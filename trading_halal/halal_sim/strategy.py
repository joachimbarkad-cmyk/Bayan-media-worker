"""Stratégie unique de la V1 : filtre de tendance sur moyenne mobile simple (SMA).

Règle (évaluée à la clôture du dernier jour de bourse de chaque mois, exécutée à
l'ouverture du jour de bourse suivant) :
- titre ADMISSIBLE dont la clôture > SMA(N clôtures) -> détenir (ACHAT s'il n'est pas détenu) ;
- titre ADMISSIBLE dont la clôture <= SMA -> ne pas détenir (VENTE s'il est détenu) ;
- titre EXCLU ou INCERTAIN -> jamais d'achat ; vente s'il est détenu, selon la politique configurée.

Pourquoi celle-ci : variante (200 jours de bourse, titres individuels) de la règle de moyenne
mobile sur 10 mois décrite par M. Faber, « A Quantitative Approach to Tactical Asset
Allocation », 2007 — inspirée de cette approche, pas sa reproduction exacte. Un seul paramètre, peu de
transactions (important quand les frais fixes pèsent sur un petit capital), et en
dehors des tendances haussières le capital reste en liquidités non rémunérées.
Elle ne prédit rien : elle réagit à des prix déjà observés.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from .data import PointInTimeView
from .screening import ADMISSIBLE, EXCLU, INCERTAIN, INCERTAIN_CAUSES, ScreeningResult

BUY, SELL, HOLD, NONE = "ACHAT", "VENTE", "CONSERVER", "AUCUNE"
MAX_PRICE_STALENESS = timedelta(days=7)


class PolicyConfigError(ValueError):
    pass


def validate_holding_policy(policy: dict) -> None:
    """on_exclu : SELL uniquement. on_incertain : SELL/HOLD, ou un dictionnaire {cause: SELL/HOLD}."""
    if policy.get("on_exclu") != "SELL":
        raise PolicyConfigError("holding_policy.on_exclu doit valoir SELL (un titre EXCLU détenu est vendu)")
    inc = policy.get("on_incertain")
    if isinstance(inc, str):
        if inc not in ("SELL", "HOLD"):
            raise PolicyConfigError("holding_policy.on_incertain doit valoir SELL ou HOLD")
    elif isinstance(inc, dict):
        unknown = set(inc) - set(INCERTAIN_CAUSES)
        if unknown or any(v not in ("SELL", "HOLD") for v in inc.values()):
            raise PolicyConfigError(f"holding_policy.on_incertain invalide ; causes permises : {INCERTAIN_CAUSES}")
    else:
        raise PolicyConfigError("holding_policy.on_incertain manquant")


def incertain_action(policy: dict, causes: list[str]) -> str:
    """Vente dès qu'UNE cause d'incertitude est réglée sur SELL ; cause non listée = SELL (prudence)."""
    inc = policy["on_incertain"]
    if isinstance(inc, str):
        return inc
    return "SELL" if any(inc.get(c, "SELL") == "SELL" for c in (causes or ["INCONNUE"])) else "HOLD"


@dataclass
class Decision:
    ticker: str
    signal: str
    reason_code: str
    detail: str
    inputs: dict = field(default_factory=dict)
    max_date_read: date | None = None


class SmaTrendStrategy:
    name = "filtre_tendance_sma"

    def __init__(self, sma_days: int = 200):
        if sma_days < 2:
            raise ValueError("sma_days doit être >= 2")
        self.sma_days = sma_days

    def trend(self, view: PointInTimeView, ticker: str) -> tuple[bool | None, dict]:
        bars = view.last_bars(ticker, self.sma_days)
        if len(bars) < self.sma_days:
            return None, {"nb_clotures": len(bars), "sma_jours": self.sma_days}
        last = bars[-1]
        sma = sum(b.close for b in bars) / len(bars)
        inputs = {"cloture": round(last.close, 4), "date_cloture": last.date.isoformat(), "sma": round(sma, 4),
                  "sma_jours": self.sma_days, "premiere_date_sma": bars[0].date.isoformat()}
        if view.as_of - last.date > MAX_PRICE_STALENESS:
            inputs["prix_perime"] = True
            return None, inputs
        return last.close > sma, inputs

    def decide(self, view: PointInTimeView, screening: ScreeningResult, held: bool, policy: dict) -> Decision:
        t = screening.ticker
        up, inputs = self.trend(view, t)
        trend_txt = {True: "clôture > SMA", False: "clôture <= SMA", None: "tendance non calculable"}[up]

        if screening.status in (EXCLU, INCERTAIN):
            motif = "; ".join(screening.reasons)
            if held:
                action = (policy["on_exclu"] if screening.status == EXCLU
                          else incertain_action(policy, screening.incertain_causes))
                if action == "SELL":
                    d = Decision(t, SELL, f"VENTE_STATUT_{screening.status}", motif, inputs)
                else:
                    d = Decision(t, HOLD, f"GEL_STATUT_{screening.status}",
                                 f"Conservé sans renforcement (politique HOLD) ; à revoir : {motif}", inputs)
            else:
                ignored = " Signal technique d'achat ignoré." if up else ""
                d = Decision(t, NONE, f"REFUS_STATUT_{screening.status}", motif + "." + ignored, inputs)
        elif screening.status == ADMISSIBLE:
            if up is None:
                d = Decision(t, HOLD if held else NONE,
                             "CONSERVE_TENDANCE_INCALCULABLE" if held else "REFUS_HISTORIQUE_INSUFFISANT",
                             f"{trend_txt} (historique de prix insuffisant ou périmé)", inputs)
            elif up:
                d = Decision(t, HOLD if held else BUY,
                             "CONSERVE_TENDANCE_HAUSSIERE" if held else "SIGNAL_ACHAT_TENDANCE", trend_txt, inputs)
            else:
                d = Decision(t, SELL if held else NONE,
                             "SIGNAL_VENTE_TENDANCE" if held else "REFUS_SOUS_MOYENNE", trend_txt, inputs)
        else:
            raise ValueError(f"Statut inconnu {screening.status!r}")
        d.max_date_read = view.max_date_read
        return d
