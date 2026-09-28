"""Filtre religieux traçable à trois statuts : ADMISSIBLE, EXCLU, INCERTAIN.

Principes :
- toute donnée manquante, périmée ou tout seuil non défini donne INCERTAIN (jamais ADMISSIBLE par défaut) ;
- chaque résultat conserve ses motifs, les ratios calculés, la période financière utilisée,
  sa date de publication, sa source et l'identifiant du référentiel appliqué ;
- le résultat est une aide au tri documentaire, PAS une certification religieuse.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .data import PointInTimeView

ADMISSIBLE = "ADMISSIBLE"
EXCLU = "EXCLU"
INCERTAIN = "INCERTAIN"
STATUSES = (ADMISSIBLE, EXCLU, INCERTAIN)
_SEVERITY = {ADMISSIBLE: 0, INCERTAIN: 1, EXCLU: 2}


class RulesetError(ValueError):
    pass


@dataclass
class ScreeningResult:
    ticker: str
    as_of: date
    status: str
    reasons: list[str]
    ratios: dict[str, float] = field(default_factory=dict)
    fundamentals_ref: dict | None = None
    ruleset_id: str = ""
    max_date_read: date | None = None


def load_ruleset(path: str | Path) -> dict:
    rs = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("id", "validated", "allowed_instrument_types", "activity_rules",
                "financial_ratios", "max_fundamentals_age_days"):
        if key not in rs:
            raise RulesetError(f"Référentiel {path} : clé '{key}' manquante")
    for code, rule in rs["activity_rules"].items():
        if rule.get("status") not in STATUSES:
            raise RulesetError(f"Activité {code} : statut invalide {rule.get('status')!r}")
    for r in rs["financial_ratios"]:
        for key in ("id", "label", "numerator", "denominator", "max"):
            if key not in r:
                raise RulesetError(f"Ratio {r.get('id')} : clé '{key}' manquante")
    return rs


def screen_security(view: PointInTimeView, ticker: str, ruleset: dict) -> ScreeningResult:
    sec = view.security(ticker)
    findings: list[tuple[str, str]] = []
    ratios: dict[str, float] = {}

    itype = sec["instrument_type"]
    if itype not in ruleset["allowed_instrument_types"]:
        findings.append((EXCLU, f"Instrument '{itype}' hors univers : seules les actions détenues au comptant sont admises"))

    if not sec["activity_codes"]:
        findings.append((INCERTAIN, "Activité de l'entreprise non renseignée"))
    for code in sec["activity_codes"]:
        rule = ruleset["activity_rules"].get(code)
        if rule is None:
            findings.append((INCERTAIN, f"Activité '{code}' non classée par le référentiel"))
        elif rule["status"] != ADMISSIBLE:
            findings.append((rule["status"], f"Activité '{code}' : {rule.get('note', '')}".strip()))

    fund = view.latest_fundamentals(ticker)
    ref = None
    if fund is None:
        findings.append((INCERTAIN, "Aucune donnée financière publiée à la date de décision"))
    else:
        ref = {"period_end": fund["period_end"].isoformat(), "available_date": fund["available_date"].isoformat(),
               "source": fund["source"]}
        age = (view.as_of - fund["period_end"]).days
        if age > ruleset["max_fundamentals_age_days"]:
            findings.append((INCERTAIN, f"Données financières périmées : fin de période {fund['period_end']} "
                                        f"({age} j > {ruleset['max_fundamentals_age_days']} j)"))
        for r in ruleset["financial_ratios"]:
            num, den = fund.get(r["numerator"]), fund.get(r["denominator"])
            if num is None or den is None or den <= 0:
                findings.append((INCERTAIN, f"{r['label']} : donnée manquante ({r['numerator']} / {r['denominator']})"))
                continue
            value = num / den
            ratios[r["id"]] = value
            if r["max"] is None:
                findings.append((INCERTAIN, f"{r['label']} = {value:.1%} : seuil non défini dans le référentiel (à valider)"))
            elif value > r["max"]:
                findings.append((EXCLU, f"{r['label']} = {value:.1%} > seuil {r['max']:.1%}"))

    if findings:
        status = max((s for s, _ in findings), key=_SEVERITY.__getitem__)
        reasons = [m for s, m in findings]
    else:
        status = ADMISSIBLE
        reasons = [f"Aucun motif d'exclusion ou d'incertitude selon le référentiel '{ruleset['id']}'"]
    return ScreeningResult(ticker, view.as_of, status, reasons, ratios, ref, ruleset["id"], view.max_date_read)
