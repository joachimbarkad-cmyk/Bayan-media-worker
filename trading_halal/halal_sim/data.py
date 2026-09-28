"""Import, validation et accès « point dans le temps » aux données.

Les décisions (filtre et stratégie) ne reçoivent jamais le jeu de données complet :
elles passent par `PointInTimeView`, qui ne renvoie que des éléments connus à la date
de décision et lève `LookaheadError` sinon.

Règle de publication (conservatrice) : l'heure de publication n'étant pas connue, un
document (état financier, fiche d'activité) publié le jour J n'est utilisable qu'à partir
de la décision du jour J+1. Les prix du jour J, eux, sont utilisables à la clôture de J.
"""
from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


class DataError(ValueError):
    pass


class LookaheadError(RuntimeError):
    pass


@dataclass(frozen=True)
class Bar:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


SECURITY_COLS = ["ticker", "name", "instrument_type", "country", "currency", "known_from", "delisted_date",
                 "delisting_cash_per_share", "delisting_source", "delisting_source_date", "delisting_cash_date"]
# Champs de la fiche titre lisibles par une décision. delisted_date n'en fait partie qu'une fois la radiation passée.
SECURITY_PUBLIC_FIELDS = ("ticker", "name", "instrument_type", "country", "currency", "known_from")
PRICE_STALENESS_DAYS = 7
ACTIVITY_COLS = ["ticker", "available_date", "activity_codes", "activity_description", "source"]
PRICE_COLS = ["date", "ticker", "open", "high", "low", "close", "volume"]
FUND_NUMERIC = ["market_cap", "shares_outstanding", "total_assets", "interest_bearing_debt",
                "cash_and_interest_bearing_investments", "total_revenue", "non_compliant_revenue"]
FUND_COLS = ["ticker", "period_end", "available_date", "currency", *FUND_NUMERIC, "source"]
FUND_POSITIVE = ("market_cap", "shares_outstanding", "total_assets")  # strictement positifs s'ils sont renseignés
FUND_NON_NEGATIVE = ("interest_bearing_debt", "cash_and_interest_bearing_investments", "total_revenue",
                     "non_compliant_revenue")


def fundamentals_problems(rec: dict) -> list[str]:
    """Valeurs financières impossibles (non finies, négatives, incohérentes). Une valeur ABSENTE (None)
    n'est pas un problème ici : elle conduit à INCERTAIN lors du filtrage."""
    p = []
    for k in FUND_NUMERIC:
        v = rec.get(k)
        if v is None:
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            p.append(f"{k} non fini ou non numérique ({v!r})")
        elif k in FUND_POSITIVE and v <= 0:
            p.append(f"{k} doit être > 0 ({v})")
        elif k in FUND_NON_NEGATIVE and v < 0:
            p.append(f"{k} ne peut pas être négatif ({v})")
    nc, rev = rec.get("non_compliant_revenue"), rec.get("total_revenue")
    if not p and nc is not None and rev is not None and nc > rev:
        p.append("revenus non conformes supérieurs au chiffre d'affaires")
    cash, assets = rec.get("cash_and_interest_bearing_investments"), rec.get("total_assets")
    if not p and cash is not None and assets is not None and cash > assets:
        p.append("liquidités supérieures au total de l'actif")
    return p


@dataclass
class Dataset:
    root: Path
    manifest: dict
    securities: dict[str, dict]
    bars: dict[str, list[Bar]]
    fundamentals: dict[str, list[dict]]
    activities: dict[str, list[dict]]
    calendar: list[date]
    file_hashes: dict[str, str]
    _bar_dates: dict[str, list[date]] = field(default_factory=dict, repr=False)
    _fund_dates: dict[str, list[date]] = field(default_factory=dict, repr=False)
    _act_dates: dict[str, list[date]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._bar_dates = {t: [b.date for b in bs] for t, bs in self.bars.items()}
        self._fund_dates = {t: [f["available_date"] for f in fs] for t, fs in self.fundamentals.items()}
        self._act_dates = {t: [a["available_date"] for a in acts] for t, acts in self.activities.items()}

    @property
    def nature(self) -> str:
        return self.manifest["nature"]

    def universe_at(self, d: date) -> list[str]:
        """Titres connus AVANT le jour d (known_from < d) et non radiés au jour d. Évite de faire connaître
        au backtest, dès 2021, un titre introduit plus tard ; les titres radiés restent dans les fichiers."""
        return [t for t in sorted(self.securities)
                if self.securities[t]["known_from"] < d
                and (self.securities[t]["delisted_date"] is None or d < self.securities[t]["delisted_date"])]

    @property
    def tickers(self) -> list[str]:
        return sorted(self.securities)

    def bar_on(self, ticker: str, d: date) -> Bar | None:
        """Barre exacte d'un jour. Réservé au moteur pour l'exécution et la valorisation, pas aux décisions."""
        dates = self._bar_dates.get(ticker, [])
        i = bisect.bisect_left(dates, d)
        return self.bars[ticker][i] if i < len(dates) and dates[i] == d else None

    def last_bar_before(self, ticker: str, d: date) -> Bar | None:
        """Dernière barre STRICTEMENT antérieure au jour d (connue avant l'ouverture de d)."""
        dates = self._bar_dates.get(ticker, [])
        i = bisect.bisect_left(dates, d)
        return self.bars[ticker][i - 1] if i else None

    def last_close_on_or_before(self, ticker: str, d: date) -> float | None:
        dates = self._bar_dates.get(ticker, [])
        i = bisect.bisect_right(dates, d)
        return self.bars[ticker][i - 1].close if i else None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv(path: Path, required: list[str]) -> list[dict]:
    if not path.exists():
        raise DataError(f"Fichier introuvable : {path}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise DataError(f"{path.name} : colonnes manquantes {sorted(missing)}")
        return list(reader)


def _date(value: str, ctx: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError) as exc:
        raise DataError(f"{ctx} : date invalide {value!r} (format attendu AAAA-MM-JJ)") from exc


def _num(value: str, ctx: str) -> float | None:
    value = (value or "").strip()
    if value == "":
        return None  # donnée manquante : conduira à INCERTAIN, jamais à une valeur inventée
    try:
        number = float(value)
    except ValueError as exc:
        raise DataError(f"{ctx} : nombre invalide {value!r}") from exc
    if not math.isfinite(number):  # float() accepte « nan » et « inf » : on les refuse
        raise DataError(f"{ctx} : nombre non fini {value!r}")
    return number


def load_dataset(root: str | Path) -> Dataset:
    root = Path(root)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise DataError(f"manifest.json absent de {root} : la nature des données (FICTIF/REEL) doit être déclarée")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("nature") not in ("FICTIF", "REEL"):
        raise DataError("manifest.json : 'nature' doit valoir FICTIF ou REEL")
    files = manifest.get("files", {})
    paths = {k: root / files.get(k, "") for k in ("securities", "prices", "fundamentals", "activities")}

    securities: dict[str, dict] = {}
    for n, row in enumerate(_read_csv(paths["securities"], SECURITY_COLS), start=2):
        t = row["ticker"].strip()
        if not t or t in securities:
            raise DataError(f"{paths['securities'].name} ligne {n} : ticker vide ou en double ({t!r})")
        row = {k: (v or "").strip() for k, v in row.items()}
        ctx = f"{paths['securities'].name} ligne {n}"
        if not row["currency"] or not row["instrument_type"]:
            raise DataError(f"{ctx} : devise ou type d'instrument manquant pour {t}")
        if not row["known_from"]:
            raise DataError(f"{ctx} : known_from obligatoire (date à partir de laquelle la fiche est connue)")
        row["known_from"] = _date(row["known_from"], ctx)
        row["delisted_date"] = _date(row["delisted_date"], ctx) if row["delisted_date"] else None
        if row["delisted_date"] and row["delisted_date"] <= row["known_from"]:
            raise DataError(f"{ctx} : radiation antérieure à known_from")
        row["delisting_cash_per_share"] = _num(row["delisting_cash_per_share"], ctx)
        row["delisting_source_date"] = _date(row["delisting_source_date"], ctx) if row["delisting_source_date"] else None
        row["delisting_cash_date"] = _date(row["delisting_cash_date"], ctx) if row["delisting_cash_date"] else None
        if row["delisting_cash_per_share"] is not None:
            # Une contrepartie n'est utilisable que datée : publication de la source ET date de paiement.
            if (row["delisting_cash_per_share"] < 0 or not row["delisting_source"] or not row["delisted_date"]
                    or row["delisting_source_date"] is None or row["delisting_cash_date"] is None):
                raise DataError(f"{ctx} : contrepartie de radiation négative, ou sans source, date de publication "
                                "de la source, date de paiement ou date de radiation")
            if row["delisting_cash_date"] < row["delisted_date"]:
                raise DataError(f"{ctx} : paiement de la contrepartie antérieur à la radiation")
        elif row["delisting_source_date"] or row["delisting_cash_date"]:
            raise DataError(f"{ctx} : dates de contrepartie sans montant")
        securities[t] = row

    activities: dict[str, list[dict]] = {t: [] for t in securities}
    for n, row in enumerate(_read_csv(paths["activities"], ACTIVITY_COLS), start=2):
        ctx = f"{paths['activities'].name} ligne {n}"
        t = row["ticker"].strip()
        if t not in securities:
            raise DataError(f"{ctx} : ticker {t!r} absent de l'univers")
        rec = {"ticker": t, "available_date": _date(row["available_date"], ctx),
               "activity_codes": [c.strip() for c in row["activity_codes"].split(";") if c.strip()],
               "activity_description": (row["activity_description"] or "").strip(),
               "source": (row["source"] or "").strip()}
        if not rec["source"]:
            raise DataError(f"{ctx} : source manquante (traçabilité obligatoire)")
        activities[t].append(rec)
    for t in activities:
        activities[t].sort(key=lambda r: r["available_date"])
        dates = [r["available_date"] for r in activities[t]]
        if len(dates) != len(set(dates)):
            raise DataError(f"{paths['activities'].name} : deux fiches d'activité le même jour pour {t}")

    bars: dict[str, list[Bar]] = {t: [] for t in securities}
    seen: set[tuple[str, date]] = set()
    for n, row in enumerate(_read_csv(paths["prices"], PRICE_COLS), start=2):
        ctx = f"{paths['prices'].name} ligne {n}"
        t = row["ticker"].strip()
        if t not in securities:
            raise DataError(f"{ctx} : ticker {t!r} absent de l'univers")
        d = _date(row["date"], ctx)
        if (t, d) in seen:
            raise DataError(f"{ctx} : doublon {t} {d}")
        dl = securities[t]["delisted_date"]
        if dl is not None and d >= dl:
            raise DataError(f"{ctx} : cours de {t} le {d}, à partir de sa radiation du {dl} (un prix hors cote "
                            "éventuel doit être traité comme un événement documenté, pas comme une cotation)")
        seen.add((t, d))
        o, h, lo, c = (_num(row[k], ctx) for k in ("open", "high", "low", "close"))
        if None in (o, h, lo, c) or min(o, h, lo, c) <= 0:
            raise DataError(f"{ctx} : prix manquant ou non positif")
        if not (lo <= min(o, c) + 1e-9 and max(o, c) <= h + 1e-9):
            raise DataError(f"{ctx} : incohérence plus bas/ouverture/clôture/plus haut")
        bars[t].append(Bar(d, o, h, lo, c, int(float(row["volume"] or 0))))
    for t in bars:
        bars[t].sort(key=lambda b: b.date)

    fundamentals: dict[str, list[dict]] = {t: [] for t in securities}
    for n, row in enumerate(_read_csv(paths["fundamentals"], FUND_COLS), start=2):
        ctx = f"{paths['fundamentals'].name} ligne {n}"
        t = row["ticker"].strip()
        if t not in securities:
            raise DataError(f"{ctx} : ticker {t!r} absent de l'univers")
        rec = {"ticker": t, "period_end": _date(row["period_end"], ctx),
               "available_date": _date(row["available_date"], ctx),
               "currency": row["currency"].strip(), "source": row["source"].strip()}
        if rec["available_date"] < rec["period_end"]:
            raise DataError(f"{ctx} : publication antérieure à la fin de période")
        if not rec["source"]:
            raise DataError(f"{ctx} : source manquante (traçabilité obligatoire)")
        for k in FUND_NUMERIC:
            rec[k] = _num(row[k], ctx)
        problems = fundamentals_problems(rec)
        if problems:
            raise DataError(f"{ctx} : " + " ; ".join(problems))
        fundamentals[t].append(rec)
    for t in fundamentals:
        fundamentals[t].sort(key=lambda r: (r["available_date"], r["period_end"]))

    calendar = sorted({b.date for bs in bars.values() for b in bs})
    if not calendar:
        raise DataError("Aucun prix chargé")
    hashes = {k: _sha256(p) for k, p in paths.items()}
    hashes["manifest"] = _sha256(manifest_path)
    return Dataset(root, manifest, securities, bars, fundamentals, activities, calendar, hashes)


class PointInTimeView:
    """Vue des données telle qu'elle était connue à la clôture du jour `as_of`."""

    def __init__(self, ds: Dataset, as_of: date):
        self._ds = ds
        self.as_of = as_of
        self.max_date_read: date | None = None

    def _touch(self, d: date) -> None:
        if d > self.as_of:
            raise LookaheadError(f"Lecture d'une donnée du {d} pour une décision du {self.as_of}")
        if self.max_date_read is None or d > self.max_date_read:
            self.max_date_read = d

    def security(self, ticker: str) -> dict:
        """Fiche titre (nom, type d'instrument, devise), valable à partir de `known_from`. Refuse une fiche
        qui n'était pas encore connue à la date de décision (même règle J+1 que les autres documents).
        L'activité, qui peut changer dans le temps, passe par `latest_activity()`."""
        sec = self._ds.securities[ticker]
        if sec["known_from"] >= self.as_of:
            raise LookaheadError(f"Fiche {ticker} connue à partir du {sec['known_from']}, décision du {self.as_of}")
        self._touch(sec["known_from"])
        out = {k: sec[k] for k in SECURITY_PUBLIC_FIELDS}
        if sec["delisted_date"] is not None and sec["delisted_date"] < self.as_of:  # radiation déjà survenue
            self._touch(sec["delisted_date"])
            out["delisted_date"] = sec["delisted_date"]
        return out

    def close_on_or_before(self, ticker: str, d: date) -> Bar | None:
        """Dernière barre au plus tard le jour d (d <= date de décision), par exemple le cours de fin de période
        comptable pour vérifier une capitalisation."""
        if d > self.as_of:
            raise LookaheadError(f"Cours du {d} demandé pour une décision du {self.as_of}")
        dates = self._ds._bar_dates.get(ticker, [])
        i = bisect.bisect_right(dates, d)
        if not i:
            return None
        bar = self._ds.bars[ticker][i - 1]
        self._touch(bar.date)
        return bar

    def last_bars(self, ticker: str, n: int) -> list[Bar]:
        dates = self._ds._bar_dates.get(ticker, [])
        i = bisect.bisect_right(dates, self.as_of)
        out = self._ds.bars[ticker][max(0, i - n):i]
        for b in out:
            self._touch(b.date)
        return out

    def _latest_published(self, dates: list[date], records: list[dict]) -> dict | None:
        # bisect_left : seuls les documents publiés STRICTEMENT avant la date de décision sont visibles.
        i = bisect.bisect_left(dates, self.as_of)
        if not i:
            return None
        rec = records[i - 1]
        self._touch(rec["available_date"])
        return rec

    def latest_fundamentals(self, ticker: str) -> dict | None:
        """Dernier état financier publié avant le jour de décision."""
        return self._latest_published(self._ds._fund_dates.get(ticker, []), self._ds.fundamentals.get(ticker, []))

    def latest_activity(self, ticker: str) -> dict | None:
        """Dernière fiche d'activité publiée avant le jour de décision."""
        return self._latest_published(self._ds._act_dates.get(ticker, []), self._ds.activities.get(ticker, []))
