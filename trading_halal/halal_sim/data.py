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


SECURITY_COLS = ["ticker", "name", "instrument_type", "country", "currency"]
ACTIVITY_COLS = ["ticker", "available_date", "activity_codes", "activity_description", "source"]
PRICE_COLS = ["date", "ticker", "open", "high", "low", "close", "volume"]
FUND_NUMERIC = ["market_cap", "total_assets", "interest_bearing_debt",
                "cash_and_interest_bearing_investments", "total_revenue", "non_compliant_revenue"]
FUND_COLS = ["ticker", "period_end", "available_date", "currency", *FUND_NUMERIC, "source"]


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

    @property
    def tickers(self) -> list[str]:
        return sorted(self.securities)

    def bar_on(self, ticker: str, d: date) -> Bar | None:
        """Barre exacte d'un jour. Réservé au moteur pour l'exécution et la valorisation, pas aux décisions."""
        dates = self._bar_dates.get(ticker, [])
        i = bisect.bisect_left(dates, d)
        return self.bars[ticker][i] if i < len(dates) and dates[i] == d else None

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
        return float(value)
    except ValueError as exc:
        raise DataError(f"{ctx} : nombre invalide {value!r}") from exc


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
        if not row["currency"]:
            raise DataError(f"{paths['securities'].name} ligne {n} : devise manquante pour {t}")
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
        """Identifiants statiques uniquement (nom, type d'instrument, devise). L'activité, qui peut
        changer dans le temps, passe par `latest_activity()`."""
        return self._ds.securities[ticker]

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
