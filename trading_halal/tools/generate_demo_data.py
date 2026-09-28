"""Génère les fichiers de DÉMONSTRATION (entièrement FICTIFS) de data/demo/.

Aucune de ces sociétés n'existe. Les prix sont une marche aléatoire déterministe
(graine fixe) avec des phases de marché choisies pour exercer les deux branches
de la règle (hausse / baisse). Ces données ne disent RIEN sur la rentabilité réelle.

Usage : python3 tools/generate_demo_data.py
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260928
OUT = Path(__file__).resolve().parent.parent / "data" / "demo"
SOURCE = f"DEMO_FICTIF - généré par tools/generate_demo_data.py (graine {SEED})"

# ticker, nom, type d'instrument, codes d'activité, description, prix initial, dérive annuelle propre, bêta
SECURITIES = [
    ("FXALP", "Alpha Logiciels (fictif)", "ACTION", "SOFTWARE", "Éditeur de logiciels de gestion", 42.0, 0.08, 1.1),
    ("FXBET", "Beta Santé (fictif)", "ACTION", "HEALTHCARE", "Fabricant de dispositifs médicaux", 118.0, 0.04, 0.7),
    ("FXIOT", "Iota Matériaux (fictif)", "ACTION", "INDUSTRIALS", "Matériaux de construction", 23.5, 0.02, 1.0),
    ("FXLAM", "Lambda Transport (fictif)", "ACTION", "TRANSPORT", "Transport routier de marchandises", 64.0, -0.12, 1.0),
    ("FXKAP", "Kappa Télécom (fictif)", "ACTION", "TELECOM", "Opérateur de télécommunications", 15.8, 0.03, 0.8),
    ("FXOME", "Omega Distribution (fictif)", "ACTION", "RETAIL", "Grande distribution alimentaire", 88.0, 0.05, 0.9),
    ("FXSIG", "Sigma Chimie (fictif)", "ACTION", "CHEMICALS", "Chimie de spécialité", 176.0, 0.06, 1.0),
    ("FXGAM", "Banque Gamma (fictif)", "ACTION", "CONVENTIONAL_BANKING", "Banque de détail à intérêts", 31.0, 0.06, 1.2),
    ("FXDEL", "Delta Brasserie (fictif)", "ACTION", "ALCOHOL", "Production de bière", 54.0, 0.05, 0.8),
    ("FXEPS", "Epsilon Industrie (fictif)", "ACTION", "INDUSTRIALS", "Machines-outils, fortement endettée", 12.2, 0.10, 1.3),
    ("FXETA", "Eta Énergie (fictif)", "ACTION", "ENERGY", "Production d'électricité (aucune donnée financière fournie)", 27.0, 0.07, 1.1),
    ("FXTHE", "Theta Tabac (fictif)", "ACTION", "TOBACCO", "Fabrication de cigarettes", 46.0, 0.15, 0.6),
    ("FXOBL", "Obligation Omicron 2030 (fictif)", "OBLIGATION_CONVENTIONNELLE", "CONVENTIONAL_BANKING", "Obligation à coupon d'intérêt", 100.0, 0.0, 0.05),
]

# ticker -> (dette/capitalisation, liquidités+placements à intérêt/capitalisation, revenus non conformes/CA)
RATIOS = {
    "FXALP": (0.05, 0.08, 0.0),
    "FXBET": (0.12, 0.10, 0.005),
    "FXIOT": (0.15, 0.06, 0.0),
    "FXLAM": (0.14, 0.05, 0.0),
    "FXKAP": (0.12, 0.06, 0.0),   # la dette bondit à partir de la période 2024-06-30 (voir plus bas)
    "FXOME": (0.10, 0.07, 0.022),
    "FXSIG": (0.08, 0.05, 0.0),   # plus de publication après 2022-12-31 -> données périmées
    "FXGAM": (0.60, 0.40, 0.70),
    "FXDEL": (0.10, 0.05, 0.0),
    "FXEPS": (0.45, 0.04, 0.0),
    "FXTHE": (0.10, 0.05, 0.0),
    # FXETA et FXOBL : aucune donnée financière
}

# Dérive annuelle du « marché » fictif par période
REGIMES = [
    (date(2021, 1, 1), 0.15), (date(2022, 1, 1), -0.30), (date(2023, 1, 1), 0.10),
    (date(2024, 1, 1), 0.12), (date(2025, 1, 1), -0.10), (date(2025, 7, 1), 0.08),
]


def business_days(start: date, end: date):
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def regime_drift(d: date) -> float:
    drift = REGIMES[0][1]
    for start, mu in REGIMES:
        if d >= start:
            drift = mu
    return drift


def main() -> None:
    rng = random.Random(SEED)
    days = list(business_days(date(2021, 1, 4), date(2025, 12, 31)))
    market = []
    for d in days:
        mu = regime_drift(d) / 252
        market.append(mu + rng.gauss(0, 0.010))

    OUT.mkdir(parents=True, exist_ok=True)
    closes: dict[str, dict[date, float]] = {}
    with open(OUT / "prices_FICTIF.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "ticker", "open", "high", "low", "close", "volume"])
        for ticker, _n, _t, _c, _d, p0, drift, beta in SECURITIES:
            prev = p0
            closes[ticker] = {}
            for d, m in zip(days, market):
                ret = beta * m + drift / 252 + rng.gauss(0, 0.012 if beta > 0.1 else 0.002)
                opn = prev * math.exp(rng.gauss(0, 0.004))
                close = prev * math.exp(ret)
                high = max(opn, close) * (1 + abs(rng.gauss(0, 0.004)))
                low = min(opn, close) * (1 - abs(rng.gauss(0, 0.004)))
                vol = int(20000 + rng.random() * 80000)
                w.writerow([d.isoformat(), ticker, f"{opn:.4f}", f"{high:.4f}", f"{low:.4f}", f"{close:.4f}", vol])
                closes[ticker][d] = close
                prev = close

    with open(OUT / "securities_FICTIF.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "name", "instrument_type", "country", "currency", "activity_codes",
                    "activity_description", "activity_as_of", "activity_source"])
        for ticker, name, itype, codes, desc, *_ in SECURITIES:
            w.writerow([ticker, name, itype, "XX", "EUR", codes, desc, "2021-01-01", SOURCE])

    periods = []
    y, q = 2020, 3
    while (y, q) <= (2025, 3):
        month = q * 3
        end = date(y, month, 30 if month in (6, 9) else 31)
        periods.append(end)
        q += 1
        if q == 5:
            y, q = y + 1, 1

    with open(OUT / "fundamentals_FICTIF.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "period_end", "available_date", "currency", "market_cap", "total_assets",
                    "interest_bearing_debt", "cash_and_interest_bearing_investments", "total_revenue",
                    "non_compliant_revenue", "source"])
        for ticker, _n, _t, _c, _d, p0, *_ in SECURITIES:
            if ticker not in RATIOS:
                continue
            debt_r, cash_r, nc_r = RATIOS[ticker]
            for pe in periods:
                if ticker == "FXSIG" and pe > date(2022, 12, 31):
                    break
                known = [c for d, c in closes[ticker].items() if d <= pe]
                price = known[-1] if known else p0
                mcap = 1e9 * price / p0
                dr = 0.38 if (ticker == "FXKAP" and pe >= date(2024, 6, 30)) else debt_r
                noise = lambda: 1 + rng.gauss(0, 0.03)
                revenue = mcap * 0.5 * noise()
                nc = "" if (ticker == "FXIOT" and pe == date(2023, 3, 31)) else f"{revenue * nc_r:.0f}"
                w.writerow([ticker, pe.isoformat(), (pe + timedelta(days=45)).isoformat(), "EUR",
                            f"{mcap:.0f}", f"{mcap * 0.8 * noise():.0f}", f"{mcap * dr * noise():.0f}",
                            f"{mcap * cash_r * noise():.0f}", f"{revenue:.0f}", nc, SOURCE])

    manifest = {
        "name": "demo_fictif_v1",
        "nature": "FICTIF",
        "warning": "DONNÉES ENTIÈREMENT FICTIVES générées pour tester le logiciel. Aucune société réelle. "
                   "Aucun résultat obtenu sur ces données ne dit quoi que ce soit sur la rentabilité réelle.",
        "generator": "tools/generate_demo_data.py",
        "seed": SEED,
        "files": {"securities": "securities_FICTIF.csv", "prices": "prices_FICTIF.csv",
                  "fundamentals": "fundamentals_FICTIF.csv"},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Données fictives écrites dans {OUT}")


if __name__ == "__main__":
    main()
