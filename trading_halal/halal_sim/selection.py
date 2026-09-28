"""Sélection « point dans le temps » d'un fait d'un dossier d'audit : période exacte + dépôt disponible à la décision.

Règles (aucune inférence) :
- la période doit correspondre EXACTEMENT (début et fin) : un trimestre, un cumul de neuf mois et un exercice partagent
  souvent la même date de fin et ne sont jamais interchangeables ; un fait ponctuel (instant) n'a pas de début ;
- un dépôt n'est utilisable qu'à partir du lendemain de son acceptation (date UTC, règle J+1 du projet), ou du
  lendemain de sa diffusion publique si elle est connue et plus tardive ; l'acceptation ne prouve pas la diffusion ;
- un même chiffre est souvent repris en comparatif dans des dépôts ultérieurs, ou corrigé par un rectificatif : parmi
  les dépôts disponibles, on retient le PLUS RÉCEMMENT disponible (dernière information connue à la date de décision),
  et les valeurs divergentes plus anciennes sont signalées comme révisées ;
- deux dépôts disponibles le même jour avec des valeurs différentes : aucune valeur n'est choisie (ambiguïté) ;
- la clé comprend l'ÉMETTEUR (via le document porteur) ; un fait monétaire normalisé exige en plus sa devise ;
- la valeur publiée à l'origine (premier dépôt disponible) est conservée à côté de la valeur retenue, pour mesurer
  l'effet des retraitements ; une publication ultérieure ne modifie jamais une décision antérieure à sa disponibilité.
La sélection ne rend un fait « utilisable » que s'il est normalisé et rapproché de sa pièce (reconciled = oui).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta, timezone
from pathlib import Path

from .audit import FILES, _d, _dt, _read

_UTC = timezone.utc


@dataclass
class Selection:
    fact: dict | None
    candidates: list[dict] = field(default_factory=list)   # faits de la bonne période, dépôts déjà disponibles
    not_yet_available: list[dict] = field(default_factory=list)
    revised_values: list[str] = field(default_factory=list)
    original: dict | None = None      # fait du premier dépôt disponible (valeur publiée à l'origine)
    reason: str = ""
    usable: bool = False


def load_audit(root: str | Path) -> tuple[dict[str, dict], list[dict]]:
    root = Path(root)
    docs = {r["doc_id"]: r for r in _read(root / "documents.csv", FILES["documents"])}
    return docs, _read(root / "facts.csv", FILES["facts"])


def available_from(doc: dict) -> date | None:
    """Premier jour de décision où le dépôt peut servir ; None si l'heure d'acceptation n'est pas établie."""
    acc = _dt(doc.get("accepted_at", ""))
    if acc is None:
        return None
    day = acc.astimezone(_UTC).date()
    pub = _dt(doc.get("public_available_at", ""))
    if pub is not None:
        day = max(day, pub.astimezone(_UTC).date())
    return day + timedelta(days=1)


def select_fact(docs: dict[str, dict], facts: list[dict], issuer_id: str, concept: str, unit: str, period_start: str,
                period_end: str, decision: date, *, concept_field: str = "source_concept",
                currency: str | None = None) -> Selection:
    if concept_field not in ("source_concept", "normalized_concept"):
        raise ValueError(concept_field)
    if not issuer_id:
        raise ValueError("émetteur obligatoire")
    if concept_field == "normalized_concept" and unit == "monnaie" and not currency:
        raise ValueError("devise obligatoire pour un fait monétaire normalisé")
    if _d(period_end) is None or (period_start and _d(period_start) is None):
        raise ValueError("période invalide")
    unit_field = "source_unit" if concept_field == "source_concept" else "unit"
    same_period, pending = [], []
    for f in facts:
        if (f[concept_field], f[unit_field], f["period_start"], f["period_end"]) != (concept, unit, period_start,
                                                                                    period_end):
            continue
        doc = docs.get(f["doc_id"], {})
        if doc.get("issuer_id") != issuer_id:
            continue
        if currency is not None and f.get("currency") != currency:
            continue
        avail = available_from(doc)
        if avail is None:
            pending.append(f)          # heure d'acceptation inconnue : jamais utilisable
        elif avail <= decision:
            same_period.append((avail, f))
        else:
            pending.append(f)
    sel = Selection(fact=None, candidates=[f for _, f in same_period], not_yet_available=pending)
    if not same_period:
        sel.reason = ("aucun dépôt disponible à cette date pour cette période exacte"
                      + (f" ({len(pending)} fait(s) publiés plus tard)" if pending else ""))
        return sel
    latest = max(a for a, _ in same_period)
    newest = [f for a, f in same_period if a == latest]
    val_field = "raw_value" if concept_field == "source_concept" else "value"
    if len({f[val_field] for f in newest}) > 1:
        sel.reason = "valeurs différentes dans des dépôts disponibles le même jour : ambiguïté, aucune valeur retenue"
        return sel
    chosen = newest[0]
    sel.fact = chosen
    first = min(a for a, _ in same_period)
    firsts = [f for a, f in same_period if a == first]
    sel.original = firsts[0] if len({f[val_field] for f in firsts}) == 1 else None
    sel.revised_values = sorted({f"{f[val_field]} ({docs[f['doc_id']]['accession_number']})"
                                 for _, f in same_period if f[val_field] != chosen[val_field]})
    if chosen["reconciled"] != "oui" or not chosen["normalized_concept"]:
        sel.reason = "fait trouvé mais non normalisé ou non rapproché de sa pièce : inutilisable pour un ratio"
    else:
        sel.usable = True
        sel.reason = "fait normalisé et rapproché"
    return sel

