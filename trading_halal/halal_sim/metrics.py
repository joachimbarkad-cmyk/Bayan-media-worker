"""Indicateurs de performance calculés sur la série de valeur liquidative simulée."""
from __future__ import annotations

import math
from datetime import date
from statistics import mean, pstdev

from .broker import Fill


def compute_metrics(series: list[tuple[date, float, float]], fills: list[Fill], initial: float) -> dict[str, float]:
    """`series` : (date, valeur totale, valeur des positions). Taux sans risque = 0 (liquidités non rémunérées)."""
    if not series:
        return {}
    values = [v for _, v, _ in series]
    final = values[-1]
    years = (series[-1][0] - series[0][0]).days / 365.25
    rets = [b / a - 1 for a, b in zip(values, values[1:]) if a > 0]
    vol = pstdev(rets) * math.sqrt(252) if len(rets) > 1 else 0.0
    peak, max_dd = values[0], 0.0
    for v in values:
        peak = max(peak, v)
        max_dd = min(max_dd, v / peak - 1)
    fees = sum(f.fees for f in fills)
    slip = sum(f.slippage_cost for f in fills)
    return {
        "valeur_finale": round(final, 2),
        "rendement_total_pct": round(100 * (final / initial - 1), 2),
        "rendement_annualise_pct": round(100 * ((final / initial) ** (1 / years) - 1), 2) if years > 0 and final > 0 else 0.0,
        "volatilite_annualisee_pct": round(100 * vol, 2),
        "ratio_rendement_risque_rf0": round(mean(rets) * 252 / vol, 2) if vol > 0 else 0.0,
        "baisse_max_pct": round(100 * max_dd, 2),
        "nb_achats": sum(1 for f in fills if f.side == "BUY"),
        "nb_ventes": sum(1 for f in fills if f.side == "SELL"),
        "frais_total": round(fees, 2),
        "glissement_total": round(slip, 2),
        "couts_total_pct_capital": round(100 * (fees + slip) / initial, 2),
        "exposition_moyenne_pct": round(100 * mean(p / v for _, v, p in series if v > 0), 1),
        "duree_annees": round(years, 2),
    }
