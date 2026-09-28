"""Dossier d'AUDIT DOCUMENTAIRE : collecte et contrôle de documents réels, sans simulation ni statut religieux.

Distinct du jeu de simulation (data.py) : il conserve la provenance (identifiants d'émetteur, numéro d'accès,
horodatages avec fuseau, versions et rectificatifs, empreintes, concepts et contextes d'origine, unités) et signale
les inconnues au lieu de les combler.

Principes du contrôle :
- colonnes en LISTE FERMÉE : toute colonne non prévue est refusée (aucun statut religieux ne peut s'y glisser) ;
- chronologie : aucune mesure, activité ou correction ne peut être antérieure à la pièce qui la porte ;
- concept d'origine (ex. XBRL) distinct du concept normalisé du projet, reliés par un mappage explicite ;
- une heure de diffusion publique non établie reste INCONNUE (elle n'est jamais recopiée de l'heure d'acceptation) ;
- les copies locales doivent se trouver dans le dossier audité.
Le contrôle ne prouve pas que les valeurs sont exactes : la comparaison avec la source reste humaine.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

FILES = {
    "issuers": ["issuer_id", "name", "id_scheme", "source", "source_url"],
    "securities": ["security_id", "issuer_id", "ticker", "exchange", "valid_from", "valid_to", "instrument_type",
                   "currency", "source"],
    "documents": ["doc_id", "issuer_id", "doc_type", "accession_number", "url", "local_copy", "local_sha256",
                  "period_end", "accepted_at", "public_available_at", "retrieved_at", "version", "amends_doc_id"],
    # Fait d'origine (concept, contexte, dimensions, unité, valeur brute, précision) conservé tel quel ; la version
    # normalisée (valeur, unité, devise) n'existe qu'avec une transformation et une justification propres au fait.
    "facts": ["fact_id", "doc_id", "source_concept", "source_context", "source_dimensions", "source_unit", "raw_value",
              "decimals", "normalized_concept", "transformation", "normalization_justification", "definition", "value",
              "unit", "currency", "period_type", "period_start", "period_end", "measure_date", "share_class",
              "price_adjusted", "corrects_fact_id", "reconciled", "reconciled_note"],
    "concept_map": ["source_concept", "normalized_concept", "justification"],
    "activities": ["issuer_id", "proposed_code", "evidence_doc_id", "available_at", "source", "source_url",
                   "justification"],
}
# Concepts normalisés du projet (ceux qu'utiliserait un futur jeu de simulation).
PROJECT_CONCEPTS = {"market_cap", "shares_outstanding", "total_assets", "interest_bearing_debt",
                    "cash_and_interest_bearing_investments", "total_revenue", "non_compliant_revenue"}
SHARE_UNITS = {"shares", "actions"}
SHARE_CONCEPTS = {"shares_outstanding", "market_cap"}
# Nature de chaque concept normalisé : monétaire (unité « monnaie » + devise) ou nombre d'actions (sans devise).
MONETARY_CONCEPTS = PROJECT_CONCEPTS - {"shares_outstanding"}
MONETARY_UNIT = "monnaie"
UNKNOWN = "INCONNU"   # valeur explicite « non établi » (distincte du vide, qui signifie « aucune » pour les dimensions)
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


class AuditFormatError(ValueError):
    pass


@dataclass
class AuditResult:
    nature: str
    counts: dict[str, int]
    errors: list[str] = field(default_factory=list)      # bloquants
    unknowns: list[str] = field(default_factory=list)    # inconnues signalées, non comblées
    reconciled: int = 0                                  # faits normalisés rapprochés à la main de leur pièce
    to_reconcile: int = 0                                # faits normalisés au total

    @property
    def ok(self) -> bool:
        """Aucune contradiction détectée automatiquement. Ce n'est PAS un verdict d'audit : voir `verdict`."""
        return not self.errors

    @property
    def verdict(self) -> str:
        if self.errors:
            return "REJETE : contradictions détectées"
        if self.to_reconcile == 0:
            return "NON EXPLOITABLE : aucun fait normalisé"
        if self.reconciled < self.to_reconcile:
            return (f"NON EXPLOITABLE : {self.to_reconcile - self.reconciled} fait(s) normalisé(s) non rapproché(s) "
                    "de leur pièce")
        return ("RAPPROCHEMENT DECLARE : forme cohérente et chaque fait normalisé déclaré rapproché, avec une note ; "
                "le logiciel ne vérifie pas ce rapprochement, l'exactitude repose sur la personne qui l'a déclaré "
                "(à relire)")


def _read(path: Path, expected: list[str]) -> list[dict]:
    if not path.exists():
        raise AuditFormatError(f"Fichier manquant : {path.name}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        missing, extra = set(expected) - set(cols), set(cols) - set(expected)
        if missing:
            raise AuditFormatError(f"{path.name} : colonnes manquantes {sorted(missing)}")
        if extra:
            raise AuditFormatError(f"{path.name} : colonnes non prévues {sorted(extra)} (liste fermée ; aucun statut "
                                   "religieux ni champ libre n'est admis dans un dossier d'audit)")
        rows = []
        for n, row in enumerate(reader, start=2):
            if None in row:
                raise AuditFormatError(f"{path.name} ligne {n} : plus de valeurs que de colonnes")
            rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows


def _dt(value: str) -> datetime | None:
    """Horodatage ISO 8601 AVEC fuseau (ex. 2024-02-02T16:05:12-05:00). Sans fuseau : invalide."""
    try:
        d = datetime.fromisoformat(value)
    except ValueError:
        return None
    return d if d.tzinfo is not None else None


def _d(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _inside(root: Path, rel: str) -> Path | None:
    """Chemin de copie locale, seulement s'il reste dans le dossier audité (pas de chemin absolu ni de « .. »)."""
    if not rel or Path(rel).is_absolute():
        return None
    resolved = (root / rel).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def audit_folder(root: str | Path) -> AuditResult:
    root = Path(root)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise AuditFormatError("manifest.json manquant")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if set(manifest) - {"name", "nature", "warning"}:
        raise AuditFormatError(f"manifest.json : clés non prévues {sorted(set(manifest) - {'name', 'nature', 'warning'})}")
    nature = manifest.get("nature")
    if nature not in ("FICTIF", "REEL"):
        raise AuditFormatError("manifest.json : nature doit valoir FICTIF ou REEL")
    t = {name: _read(root / f"{name}.csv", cols) for name, cols in FILES.items()}
    res = AuditResult(nature, {k: len(v) for k, v in t.items()})
    E, U = res.errors.append, res.unknowns.append

    # --- émetteurs et titres ---
    issuers = {}
    for r in t["issuers"]:
        if not r["issuer_id"] or r["issuer_id"] in issuers:
            E(f"émetteur vide ou en double : {r['issuer_id']!r}")
        issuers[r["issuer_id"]] = r
        if not r["id_scheme"] or not r["source"]:
            E(f"émetteur {r['issuer_id']} : schéma d'identifiant (ex. CIK) ou source manquant")

    seen_sec = set()
    for r in t["securities"]:
        ctx = f"titre {r['security_id']}"
        if not r["security_id"] or r["security_id"] in seen_sec:
            E(f"identifiant de titre vide ou en double : {r['security_id']!r}")
        seen_sec.add(r["security_id"])
        if r["issuer_id"] not in issuers:
            E(f"{ctx} : émetteur inconnu {r['issuer_id']!r}")
        vf, vt = _d(r["valid_from"]), _d(r["valid_to"]) if r["valid_to"] else None
        if vf is None or (r["valid_to"] and vt is None):
            E(f"{ctx} : dates de validité invalides")
        elif vt and vt < vf:
            E(f"{ctx} : fin de validité antérieure au début")
        if not CURRENCY_RE.match(r["currency"]):
            E(f"{ctx} : devise invalide {r['currency']!r}")
        if not (r["ticker"] and r["exchange"] and r["instrument_type"] and r["source"]):
            E(f"{ctx} : ticker, place, type d'instrument ou source manquant")

    # --- documents ---
    docs, accessions = {}, set()
    for r in t["documents"]:
        ctx = f"document {r['doc_id']}"
        if not r["doc_id"] or r["doc_id"] in docs:
            E(f"document vide ou en double : {r['doc_id']!r}")
        docs[r["doc_id"]] = r
        if r["issuer_id"] not in issuers:
            E(f"{ctx} : émetteur inconnu {r['issuer_id']!r}")
        if not r["accession_number"] or r["accession_number"] in accessions:
            E(f"{ctx} : numéro d'accès vide ou en double")
        accessions.add(r["accession_number"])
        if not (r["doc_type"] and r["url"]):
            E(f"{ctx} : type ou URL manquant")
        acc, ret = _dt(r["accepted_at"]), _dt(r["retrieved_at"])
        pub = _dt(r["public_available_at"]) if r["public_available_at"] else None
        r["_acc"], r["_pub"], r["_pe"] = acc, pub, _d(r["period_end"])
        if acc is None or ret is None:
            E(f"{ctx} : accepted_at ou retrieved_at invalide ou sans fuseau")
        if r["public_available_at"] and pub is None:
            E(f"{ctx} : public_available_at invalide ou sans fuseau")
        if not r["public_available_at"]:
            U(f"{ctx} : heure de diffusion publique non établie (l'heure d'acceptation ne la remplace pas)")
        if acc and pub and pub < acc:
            E(f"{ctx} : disponibilité publique antérieure à l'acceptation")
        if ret and (pub or acc) and ret < (pub or acc):
            E(f"{ctx} : récupéré avant d'être accepté ou public")
        if r["_pe"] is None:
            E(f"{ctx} : fin de période invalide")
        elif acc and r["_pe"] > acc.date():
            E(f"{ctx} : fin de période postérieure à l'acceptation")
        if r["version"] not in ("original", "rectificatif"):
            E(f"{ctx} : version doit valoir original ou rectificatif")
        if (r["version"] == "rectificatif") != bool(r["amends_doc_id"]):
            E(f"{ctx} : un rectificatif (et seulement lui) doit désigner le document rectifié")
        if r["local_copy"]:
            path = _inside(root, r["local_copy"])
            if path is None:
                E(f"{ctx} : copie locale hors du dossier audité ({r['local_copy']})")
            elif not path.is_file():
                E(f"{ctx} : copie locale introuvable {r['local_copy']}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != r["local_sha256"].lower():
                E(f"{ctx} : empreinte SHA-256 de la copie locale différente")
        else:
            U(f"{ctx} : pas de copie locale (seule l'URL permet la vérification)")

    # --- rectificatifs : cible distincte, même émetteur, antérieure, même période, sans boucle ---
    for r in t["documents"]:
        target_id = r["amends_doc_id"]
        if not target_id:
            continue
        ctx = f"rectificatif {r['doc_id']}"
        target = docs.get(target_id)
        if target_id == r["doc_id"]:
            E(f"{ctx} : se rectifie lui-même")
            continue
        if target is None:
            E(f"{ctx} : rectifie un document inconnu {target_id!r}")
            continue
        if target["issuer_id"] != r["issuer_id"]:
            E(f"{ctx} : émetteur différent du document rectifié")
        if target["_acc"] and r["_acc"] and target["_acc"] >= r["_acc"]:
            E(f"{ctx} : accepté avant (ou en même temps que) le document qu'il rectifie")
        if target["_pe"] != r["_pe"]:
            E(f"{ctx} : période {r['period_end']} différente du document rectifié ({target['period_end']})")
        t_pub, r_pub = target["_pub"] or target["_acc"], r["_pub"] or r["_acc"]
        if t_pub and r_pub and r_pub <= t_pub:
            E(f"{ctx} : diffusé ({r_pub.isoformat()}) avant ou en même temps que le document qu'il rectifie "
              f"({t_pub.isoformat()})")
        chain, cur = {r["doc_id"]}, target
        while cur is not None and cur["amends_doc_id"]:
            if cur["doc_id"] in chain:
                E(f"{ctx} : boucle de rectificatifs")
                break
            chain.add(cur["doc_id"])
            cur = docs.get(cur["amends_doc_id"])

    # --- mappage des concepts ---
    cmap = {}
    for r in t["concept_map"]:
        if r["source_concept"] in cmap:
            E(f"mappage en double pour {r['source_concept']!r}")
        if r["normalized_concept"] not in PROJECT_CONCEPTS:
            E(f"mappage {r['source_concept']} : concept normalisé inconnu {r['normalized_concept']!r}")
        if not r["justification"]:
            E(f"mappage {r['source_concept']} : justification manquante")
        cmap[r["source_concept"]] = r["normalized_concept"]

    # --- faits ---
    facts = {}
    for r in t["facts"]:
        ctx = f"fait {r['fact_id']}"
        if not r["fact_id"] or r["fact_id"] in facts:
            E(f"fait vide ou en double : {r['fact_id']!r}")
        facts[r["fact_id"]] = r
        doc = docs.get(r["doc_id"])
        if doc is None:
            E(f"{ctx} : document d'origine inconnu {r['doc_id']!r}")
        if not (r["source_concept"] and r["definition"] and r["unit"]):
            E(f"{ctx} : concept d'origine, définition ou unité manquant")
        if not r["source_context"]:
            U(f"{ctx} : contexte d'origine (ex. contexte XBRL) non renseigné")
        norm = r["normalized_concept"]
        mapped = cmap.get(r["source_concept"])
        if norm:
            if mapped is None:
                E(f"{ctx} : concept normalisé {norm!r} sans mappage explicite de {r['source_concept']!r}")
            elif mapped != norm:
                E(f"{ctx} : concept normalisé {norm!r} contraire au mappage ({mapped!r})")
        elif mapped:
            E(f"{ctx} : concept {r['source_concept']!r} mappé vers {mapped!r} mais non normalisé dans le fait")
        else:
            U(f"{ctx} : concept {r['source_concept']!r} non normalisé (inutilisable par le projet en l'état)")
        if not r["source_unit"]:
            E(f"{ctx} : unité d'origine manquante")
        if r["source_dimensions"] == UNKNOWN:
            U(f"{ctx} : dimensions d'origine non établies")
            if norm:
                E(f"{ctx} : normalisation impossible tant que les dimensions d'origine ne sont pas établies")
        elif r["source_dimensions"]:
            U(f"{ctx} : fait dimensionnel ({r['source_dimensions']}) : à ne pas confondre avec le total de l'entité")
        if r["decimals"] and r["decimals"] != "INF" and not re.fullmatch(r"-?\d+", r["decimals"]):
            E(f"{ctx} : précision (decimals) invalide {r['decimals']!r}")
        if not r["decimals"]:
            U(f"{ctx} : précision (decimals) non renseignée")
        if r["raw_value"]:
            try:
                if not math.isfinite(float(r["raw_value"])):
                    raise ValueError
            except ValueError:
                E(f"{ctx} : valeur brute non numérique ou non finie {r['raw_value']!r}")
        if norm:
            res.to_reconcile += 1
            if not r["normalization_justification"]:
                E(f"{ctx} : normalisation sans justification propre au fait (le mappage général ne suffit pas)")
            if r["transformation"] == "":
                E(f"{ctx} : transformation non décrite (« aucune » si la valeur est reprise telle quelle)")
            elif r["transformation"] == "aucune" and r["value"] != r["raw_value"]:
                E(f"{ctx} : transformation « aucune » mais valeur {r['value']!r} ≠ valeur brute {r['raw_value']!r}")
            if norm in MONETARY_CONCEPTS:
                if r["unit"] != MONETARY_UNIT or not r["currency"]:
                    E(f"{ctx} : {norm} est monétaire : unité « {MONETARY_UNIT} » et devise obligatoires")
            elif r["unit"].lower() not in SHARE_UNITS or r["currency"]:
                E(f"{ctx} : {norm} est un nombre d'actions : unité « actions », sans devise")
            if r["reconciled"] == "oui":
                if not r["reconciled_note"]:
                    E(f"{ctx} : rapprochement déclaré sans note (indiquer la pièce et l'endroit vérifiés : page, "
                      "section, tableau)")
                else:
                    res.reconciled += 1
            elif r["reconciled"] not in ("", "non"):
                E(f"{ctx} : reconciled doit valoir oui, non ou rester vide")
        if r["unit"] == MONETARY_UNIT and not r["currency"]:
            E(f"{ctx} : unité monétaire sans devise")
        if r["unit"].lower() in SHARE_UNITS and r["currency"]:
            E(f"{ctx} : nombre d'actions exprimé avec une devise ({r['currency']})")
        if r["value"] == "" and r["raw_value"] == "":
            U(f"{ctx} ({r['source_concept']}) : valeur inconnue (ni brute ni normalisée)")
        elif r["value"] == "":
            U(f"{ctx} ({r['source_concept']}) : valeur brute connue ({r['raw_value']}), valeur normalisée absente")
        else:
            try:
                v = float(r["value"])
                if not math.isfinite(v):
                    raise ValueError
            except ValueError:
                E(f"{ctx} : valeur non numérique ou non finie {r['value']!r}")
        if r["currency"] and not CURRENCY_RE.match(r["currency"]):
            E(f"{ctx} : devise invalide {r['currency']!r}")
        pend, pstart = _d(r["period_end"]), _d(r["period_start"]) if r["period_start"] else None
        if r["period_type"] == "instant":
            if r["period_start"]:
                E(f"{ctx} : une valeur instantanée n'a pas de début de période")
        elif r["period_type"] == "duration":
            if pstart is None or (pend and pstart > pend):
                E(f"{ctx} : période (début/fin) invalide")
        else:
            E(f"{ctx} : period_type doit valoir instant ou duration")
        acc_date = doc["_acc"].date() if doc is not None and doc["_acc"] else None
        if pend is None:
            E(f"{ctx} : fin de période invalide")
        elif acc_date and pend > acc_date:
            E(f"{ctx} : période postérieure à l'acceptation du document")
        # Règles « actions » selon l'UNITÉ ou le concept normalisé, quel que soit le nom du concept d'origine.
        is_share = r["unit"].lower() in SHARE_UNITS or norm in SHARE_CONCEPTS
        md = _d(r["measure_date"]) if r["measure_date"] else None
        if r["measure_date"] and md is None:
            E(f"{ctx} : date de mesure invalide")
        if is_share and (md is None or not r["share_class"]):
            E(f"{ctx} ({r['source_concept']}) : date de mesure et catégorie d'actions obligatoires "
              f"(« {UNKNOWN} » si la catégorie n'est pas établie)")
        if r["share_class"] == UNKNOWN:
            U(f"{ctx} : catégorie d'actions non établie")
            if norm:
                E(f"{ctx} : normalisation impossible tant que la catégorie d'actions n'est pas établie")
        if md and acc_date and md > acc_date:
            E(f"{ctx} : mesuré le {md}, après l'acceptation de son document ({acc_date})")
        if norm == "market_cap" and r["price_adjusted"] not in ("oui", "non"):
            E(f"{ctx} : préciser si le cours utilisé est ajusté (oui/non)")

    # --- corrections de faits par un rectificatif ---
    for r in t["facts"]:
        old_id = r["corrects_fact_id"]
        if not old_id:
            continue
        ctx = f"fait {r['fact_id']}"
        old, doc = facts.get(old_id), docs.get(r["doc_id"])
        if old is None or old_id == r["fact_id"]:
            E(f"{ctx} : corrige un fait inconnu ou lui-même ({old_id!r})")
            continue
        if doc is None or doc["version"] != "rectificatif":
            E(f"{ctx} : une correction doit provenir d'un document rectificatif")
            continue
        chain, cur = set(), docs.get(doc["amends_doc_id"])
        while cur is not None and cur["doc_id"] not in chain:
            chain.add(cur["doc_id"])
            cur = docs.get(cur["amends_doc_id"])
        if old["doc_id"] not in chain:
            E(f"{ctx} : le fait corrigé n'appartient pas à un document rectifié par {r['doc_id']}")
        for k in ("source_concept", "period_type", "period_start", "period_end", "unit", "currency", "share_class"):
            if old[k] != r[k]:
                E(f"{ctx} : {k} différent du fait corrigé ({old[k]!r} ≠ {r[k]!r})")

    # --- activités : rattachées à une pièce, jamais antérieures à elle ---
    for r in t["activities"]:
        ctx = f"activité {r['issuer_id']}"
        if r["issuer_id"] not in issuers:
            E(f"{ctx} : émetteur inconnu")
        avail = _dt(r["available_at"])
        if avail is None:
            E(f"{ctx} : available_at invalide ou sans fuseau")
        if not r["source"]:
            E(f"{ctx} : source manquante")
        unknown_code = r["proposed_code"] in ("", "INCONNU")
        if unknown_code:
            U(f"{ctx} : classification d'activité non établie")
        elif not (r["justification"] and r["evidence_doc_id"]):
            E(f"{ctx} : code proposé sans justification ni pièce justificative (evidence_doc_id)")
        if r["evidence_doc_id"]:
            ev = docs.get(r["evidence_doc_id"])
            if ev is None:
                E(f"{ctx} : pièce justificative inconnue {r['evidence_doc_id']!r}")
            elif ev["issuer_id"] != r["issuer_id"]:
                E(f"{ctx} : pièce justificative d'un autre émetteur")
            elif avail:
                floor = ev["_pub"] or ev["_acc"]
                if floor and avail < floor:
                    E(f"{ctx} : disponible le {avail.isoformat()}, avant sa pièce justificative ({floor.isoformat()})")

    if nature == "REEL":
        cited = [r.get(k, "") for tab in t.values() for r in tab for k in ("source", "source_url", "url")]
        bad = sorted({c for c in cited if c and any(w in c.upper() for w in ("DEMO", "FICTIF", "TEST"))})
        if bad:
            E(f"dossier déclaré REEL citant des sources de démonstration : {bad[:3]}")
    return res
