"""Filtre religieux traçable à trois statuts : ADMISSIBLE, EXCLU, INCERTAIN.

Principes :
- toute donnée manquante, périmée ou tout seuil non défini donne INCERTAIN (jamais ADMISSIBLE par défaut) ;
- l'activité et les états financiers sont lus « point dans le temps » (fiches datées par leur publication) ;
- chaque résultat conserve ses motifs, la cause de chaque incertitude, les ratios calculés, les documents
  utilisés (dates de publication, sources) et l'identifiant du référentiel appliqué ;
- le résultat est une aide au tri documentaire, PAS une certification religieuse.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .data import PRICE_STALENESS_DAYS, PointInTimeView, fundamentals_problems

ADMISSIBLE = "ADMISSIBLE"
EXCLU = "EXCLU"
INCERTAIN = "INCERTAIN"
STATUSES = (ADMISSIBLE, EXCLU, INCERTAIN)
_SEVERITY = {ADMISSIBLE: 0, INCERTAIN: 1, EXCLU: 2}

# Causes d'incertitude, pour une politique de conservation distincte par cause (config holding_policy).
CAUSE_ACTIVITE = "ACTIVITE"                    # activité classée INCERTAIN ou non classée par le référentiel
CAUSE_DONNEE_MANQUANTE = "DONNEE_MANQUANTE"    # fiche d'activité, état financier ou valeur absente
CAUSE_DONNEE_PERIMEE = "DONNEE_PERIMEE"        # état financier trop ancien
CAUSE_SEUIL_NON_DEFINI = "SEUIL_NON_DEFINI"    # référentiel incomplet
CAUSE_DONNEE_INVALIDE = "DONNEE_INVALIDE"      # valeur impossible (non finie, négative, incohérente)
INCERTAIN_CAUSES = (CAUSE_ACTIVITE, CAUSE_DONNEE_MANQUANTE, CAUSE_DONNEE_PERIMEE, CAUSE_SEUIL_NON_DEFINI,
                    CAUSE_DONNEE_INVALIDE)

# Exigences structurelles vérifiées pour TOUT référentiel (démo compris). Elles traduisent le cahier des
# charges (actions au comptant uniquement, trois familles de ratios) et empêchent qu'un référentiel
# vidé ou mal formé laisse passer un titre sans contrôle. Elles ne fixent aucune valeur de seuil.
ALLOWED_INSTRUMENT_TYPES = {"ACTION"}
# Catalogue des types de ratios : chaque identifiant est lié à SON numérateur et aux dénominateurs admis.
# Un référentiel choisit le dénominateur et le seuil, pas la signification du ratio. Ajouter un type
# (par exemple créances / actifs) exige de modifier ce catalogue, avec un test : c'est voulu.
# Seule méthode de calcul implémentée : valeurs ponctuelles du dernier état financier publié. Une méthodologie
# qui exige une moyenne glissante (ex. capitalisation moyenne sur 36 mois) ou un contrôle supplémentaire
# (ex. créances) n'est PAS reproductible en l'état : le logiciel n'implémente aucun référentiel réel complet.
SUPPORTED_CALCULATIONS = {"ponctuel_derniere_publication"}
RATIO_CATALOG = {
    "dette_a_interet": {"numerator": "interest_bearing_debt", "denominators": {"market_cap", "total_assets"}},
    "liquidites_a_interet": {"numerator": "cash_and_interest_bearing_investments",
                             "denominators": {"market_cap", "total_assets"}},
    "revenus_non_conformes": {"numerator": "non_compliant_revenue", "denominators": {"total_revenue"}},
}
# Écart toléré entre la capitalisation publiée et nombre d'actions x cours de fin de période. Contrôle de
# cohérence des DONNÉES (pas un seuil religieux) : il écarte une valeur aberrante, pas une donnée fausse mais cohérente.
MARKET_CAP_TOLERANCE = 0.05
REQUIRED_RATIO_IDS = set(RATIO_CATALOG)
CORE_EXCLUDED_ACTIVITIES = ("CONVENTIONAL_BANKING", "CONVENTIONAL_INSURANCE", "ALCOHOL", "PORK", "GAMBLING",
                            "ADULT_ENTERTAINMENT")


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
    activity_ref: dict | None = None
    incertain_causes: list[str] = field(default_factory=list)
    ruleset_id: str = ""
    max_date_read: date | None = None


def structural_problems(rs: dict) -> list[str]:
    """Problèmes rendant un référentiel inutilisable, même pour une démonstration."""
    p: list[str] = []
    for key in ("id", "validated", "allowed_instrument_types", "activity_rules", "financial_ratios",
                "max_fundamentals_age_days"):
        if key not in rs:
            p.append(f"clé '{key}' manquante")
    if p:
        return p
    types = set(rs["allowed_instrument_types"])
    if not types:
        p.append("allowed_instrument_types est vide")
    if types - ALLOWED_INSTRUMENT_TYPES:
        p.append(f"instruments hors cahier des charges : {sorted(types - ALLOWED_INSTRUMENT_TYPES)}")
    age = rs["max_fundamentals_age_days"]
    if not isinstance(age, int) or isinstance(age, bool) or age <= 0:
        p.append("max_fundamentals_age_days doit être un entier > 0")
    rules = rs["activity_rules"]
    for code, rule in rules.items():
        if not isinstance(rule, dict) or rule.get("status") not in STATUSES:
            p.append(f"activité {code} : statut invalide {rule.get('status') if isinstance(rule, dict) else rule!r}")
    for code in CORE_EXCLUDED_ACTIVITIES:
        if code not in rules:
            p.append(f"activité {code} absente du référentiel")
        elif isinstance(rules[code], dict) and rules[code].get("status") == ADMISSIBLE:
            p.append(f"activité {code} classée ADMISSIBLE : refusé par le logiciel")
    ratios = rs["financial_ratios"]
    ids = [r.get("id") for r in ratios]
    missing = REQUIRED_RATIO_IDS - set(ids)
    if missing:
        p.append(f"ratios financiers obligatoires manquants : {sorted(missing)}")
    if len(ids) != len(set(ids)):
        p.append("identifiants de ratios en double")
    for r in ratios:
        for key in ("id", "label", "numerator", "denominator", "max", "calcul"):
            if key not in r:
                p.append(f"ratio {r.get('id')} : clé '{key}' manquante")
        if "calcul" in r and r["calcul"] not in SUPPORTED_CALCULATIONS:
            p.append(f"ratio {r.get('id')} : méthode de calcul {r['calcul']!r} non implémentée "
                     f"(disponible : {sorted(SUPPORTED_CALCULATIONS)})")
        spec = RATIO_CATALOG.get(r.get("id"))
        if spec is None:
            p.append(f"ratio {r.get('id')!r} absent du catalogue RATIO_CATALOG (types permis : {sorted(RATIO_CATALOG)})")
        else:
            if r.get("numerator") != spec["numerator"]:
                p.append(f"ratio {r['id']} : numérateur {r.get('numerator')!r} au lieu de {spec['numerator']!r}")
            if r.get("denominator") not in spec["denominators"]:
                p.append(f"ratio {r['id']} : dénominateur {r.get('denominator')!r} non admis "
                         f"(permis : {sorted(spec['denominators'])})")
        mx = r.get("max")
        if mx is not None and (isinstance(mx, bool) or not isinstance(mx, (int, float)) or not 0 < mx <= 1):
            p.append(f"ratio {r.get('id')} : seuil {mx!r} invalide (null ou nombre dans ]0 ; 1])")
    return p


def real_data_problems(rs: dict) -> list[str]:
    """Conditions supplémentaires pour appliquer un référentiel à des données RÉELLES.
    Un booléen `validated` ne suffit pas : on exige le texte source, les seuils sourcés et la validation nommée."""
    p = structural_problems(rs)
    if rs.get("validated") is not True:
        p.append("validated n'est pas true")
    if rs.get("demo_only") is not False:
        p.append("demo_only doit valoir false")
    ref = rs.get("reference_text") or {}
    for key in ("name", "version", "date", "url_or_document"):
        if not str(ref.get(key) or "").strip():
            p.append(f"reference_text.{key} non renseigné")
    if not str(rs.get("validated_by") or "").strip():
        p.append("validated_by non renseigné")
    try:
        date.fromisoformat(str(rs.get("validated_on")))
    except ValueError:
        p.append("validated_on doit être une date AAAA-MM-JJ")
    if not str(rs.get("activity_rules_source") or "").strip():
        p.append("activity_rules_source non renseigné (source du classement des activités)")
    for r in rs.get("financial_ratios", []):
        if r.get("max") is None:
            p.append(f"ratio {r.get('id')} : seuil non défini")
        src = str(r.get("source") or "")
        if not src.strip() or "ARBITRAIRE" in src.upper() or "DEMO" in src.upper():
            p.append(f"ratio {r.get('id')} : source absente ou de démonstration")
    return p


def load_ruleset(path: str | Path) -> dict:
    rs = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = structural_problems(rs)
    if problems:
        raise RulesetError(f"Référentiel {path} invalide : " + " ; ".join(problems))
    return rs


def _market_cap_findings(view: PointInTimeView, ticker: str, fund: dict) -> list[tuple[str, str, str]]:
    """Vérifie la capitalisation publiée contre nombre d'actions x cours de clôture à la fin de période."""
    mcap, shares = fund.get("market_cap"), fund.get("shares_outstanding")
    if mcap is None:
        return []  # absence déjà traitée par le calcul du ratio
    if shares is None:
        return [(INCERTAIN, "Capitalisation invérifiable : nombre d'actions absent", CAUSE_DONNEE_MANQUANTE)]
    bar = view.close_on_or_before(ticker, fund["period_end"])
    if bar is None or (fund["period_end"] - bar.date).days > PRICE_STALENESS_DAYS:
        return [(INCERTAIN, f"Capitalisation invérifiable : pas de cours au {fund['period_end']}", CAUSE_DONNEE_MANQUANTE)]
    computed = shares * bar.close
    if abs(mcap / computed - 1) > MARKET_CAP_TOLERANCE:
        return [(INCERTAIN, f"Capitalisation publiée {mcap:.4g} incohérente avec actions x cours = {computed:.4g} "
                            f"(écart > {MARKET_CAP_TOLERANCE:.0%})", CAUSE_DONNEE_INVALIDE)]
    return []


def screen_security(view: PointInTimeView, ticker: str, ruleset: dict) -> ScreeningResult:
    sec = view.security(ticker)
    findings: list[tuple[str, str, str | None]] = []  # (statut, motif, cause d'incertitude)
    ratios: dict[str, float] = {}

    itype = sec["instrument_type"]
    if itype not in ruleset["allowed_instrument_types"]:
        findings.append((EXCLU, f"Instrument '{itype}' hors univers : seules les actions détenues au comptant sont admises", None))

    act = view.latest_activity(ticker)
    act_ref = None
    if act is None:
        findings.append((INCERTAIN, "Aucune fiche d'activité publiée avant la date de décision", CAUSE_DONNEE_MANQUANTE))
    else:
        act_ref = {"available_date": act["available_date"].isoformat(), "codes": act["activity_codes"],
                   "source": act["source"]}
        if not act["activity_codes"]:
            findings.append((INCERTAIN, "Activité de l'entreprise non renseignée", CAUSE_DONNEE_MANQUANTE))
        for code in act["activity_codes"]:
            rule = ruleset["activity_rules"].get(code)
            if rule is None:
                findings.append((INCERTAIN, f"Activité '{code}' non classée par le référentiel", CAUSE_ACTIVITE))
            elif rule["status"] != ADMISSIBLE:
                cause = CAUSE_ACTIVITE if rule["status"] == INCERTAIN else None
                findings.append((rule["status"], f"Activité '{code}' : {rule.get('note', '')}".strip(), cause))

    fund = view.latest_fundamentals(ticker)
    ref = None
    if fund is None:
        findings.append((INCERTAIN, "Aucune donnée financière publiée avant la date de décision", CAUSE_DONNEE_MANQUANTE))
    else:
        ref = {"period_end": fund["period_end"].isoformat(), "available_date": fund["available_date"].isoformat(),
               "source": fund["source"]}
        invalid = fundamentals_problems(fund)  # défense en profondeur : déjà refusé à l'import
        for msg in invalid:
            findings.append((INCERTAIN, f"Donnée financière invalide : {msg}", CAUSE_DONNEE_INVALIDE))
        if not invalid and any(r["denominator"] == "market_cap" for r in ruleset["financial_ratios"]):
            findings.extend(_market_cap_findings(view, ticker, fund))
        age = (view.as_of - fund["period_end"]).days
        if age > ruleset["max_fundamentals_age_days"]:
            findings.append((INCERTAIN, f"Données financières périmées : fin de période {fund['period_end']} "
                                        f"({age} j > {ruleset['max_fundamentals_age_days']} j)", CAUSE_DONNEE_PERIMEE))
        for r in ([] if invalid else ruleset["financial_ratios"]):
            num, den = fund.get(r["numerator"]), fund.get(r["denominator"])
            if num is None or den is None or den <= 0:
                findings.append((INCERTAIN, f"{r['label']} : donnée manquante ({r['numerator']} / {r['denominator']})",
                                 CAUSE_DONNEE_MANQUANTE))
                continue
            value = num / den
            if not math.isfinite(value) or value < 0:
                findings.append((INCERTAIN, f"{r['label']} : valeur calculée invalide ({value!r})", CAUSE_DONNEE_INVALIDE))
                continue
            ratios[r["id"]] = value
            if r["max"] is None:
                findings.append((INCERTAIN, f"{r['label']} = {value:.1%} : seuil non défini dans le référentiel (à valider)",
                                 CAUSE_SEUIL_NON_DEFINI))
            elif value > r["max"]:
                findings.append((EXCLU, f"{r['label']} = {value:.1%} > seuil {r['max']:.1%}", None))

    if findings:
        status = max((s for s, _, _ in findings), key=_SEVERITY.__getitem__)
        reasons = [m for _, m, _ in findings]
    else:
        status = ADMISSIBLE
        reasons = [f"Aucun motif d'exclusion ou d'incertitude selon le référentiel '{ruleset['id']}'"]
    causes = sorted({c for s, _, c in findings if s == INCERTAIN and c})
    return ScreeningResult(ticker, view.as_of, status, reasons, ratios, ref, act_ref, causes, ruleset["id"],
                           view.max_date_read)
