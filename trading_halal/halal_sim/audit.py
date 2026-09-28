"""Dossier d'AUDIT DOCUMENTAIRE : collecte et contrôle de documents réels, sans simulation ni statut religieux.

Distinct du jeu de simulation (data.py) : il conserve la provenance que la simulation n'exige pas encore
(identifiants d'émetteur, numéro d'accès, horodatages avec fuseau, versions, empreintes, unités), et signale les
inconnues au lieu de les combler. Aucun champ de statut religieux n'y figure : ADMISSIBLE/EXCLU/INCERTAIN ne
peuvent pas être produits à partir d'un dossier d'audit.

Fichiers (CSV UTF-8) : issuers, securities, documents, facts, activities + manifest.json.
Le contrôle vérifie la forme, la cohérence chronologique et l'intégrité des copies locales. Il ne prouve pas que
les valeurs sont exactes : la comparaison avec la source reste humaine.
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
    "facts": ["fact_id", "doc_id", "concept", "definition", "value", "unit", "currency", "period_type",
              "period_start", "period_end", "measure_date", "share_class", "price_adjusted"],
    "activities": ["issuer_id", "proposed_code", "available_at", "source", "source_url", "justification"],
}
# Concepts qui exigent la date de la mesure et la catégorie d'actions (revue n° 5).
SHARE_CONCEPTS = {"shares_outstanding", "market_cap"}
FORBIDDEN_COLUMNS = {"status", "statut", "admissible", "halal", "compliant"}
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


class AuditFormatError(ValueError):
    pass


@dataclass
class AuditResult:
    nature: str
    counts: dict[str, int]
    errors: list[str] = field(default_factory=list)      # bloquants
    unknowns: list[str] = field(default_factory=list)    # inconnues signalées, non comblées

    @property
    def ok(self) -> bool:
        return not self.errors


def _read(path: Path, required: list[str]) -> list[dict]:
    if not path.exists():
        raise AuditFormatError(f"Fichier manquant : {path.name}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = set(reader.fieldnames or [])
        missing = set(required) - cols
        if missing:
            raise AuditFormatError(f"{path.name} : colonnes manquantes {sorted(missing)}")
        forbidden = {c for c in cols if c.lower() in FORBIDDEN_COLUMNS}
        if forbidden:
            raise AuditFormatError(f"{path.name} : colonnes de statut religieux interdites dans un audit {sorted(forbidden)}")
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


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


def audit_folder(root: str | Path) -> AuditResult:
    root = Path(root)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise AuditFormatError("manifest.json manquant")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    nature = manifest.get("nature")
    if nature not in ("FICTIF", "REEL"):
        raise AuditFormatError("manifest.json : nature doit valoir FICTIF ou REEL")
    t = {name: _read(root / f"{name}.csv", cols) for name, cols in FILES.items()}
    res = AuditResult(nature, {k: len(v) for k, v in t.items()})
    E, U = res.errors.append, res.unknowns.append

    issuers = {}
    for r in t["issuers"]:
        if not r["issuer_id"] or r["issuer_id"] in issuers:
            E(f"émetteur vide ou en double : {r['issuer_id']!r}")
        issuers[r["issuer_id"]] = r
        if not r["id_scheme"]:
            E(f"émetteur {r['issuer_id']} : schéma d'identifiant manquant (ex. CIK)")
        if not r["source"]:
            E(f"émetteur {r['issuer_id']} : source manquante")

    for r in t["securities"]:
        ctx = f"titre {r['security_id']}"
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
        acc, pub, ret = _dt(r["accepted_at"]), _dt(r["public_available_at"]), _dt(r["retrieved_at"])
        pe = _d(r["period_end"])
        if None in (acc, pub, ret):
            E(f"{ctx} : horodatages accepted_at / public_available_at / retrieved_at invalides ou sans fuseau")
        else:
            if pub < acc:
                E(f"{ctx} : disponibilité publique antérieure à l'acceptation")
            if ret < pub:
                E(f"{ctx} : récupéré avant d'être public")
            if pe and pe > acc.date():
                E(f"{ctx} : fin de période postérieure à l'acceptation")
        if pe is None:
            E(f"{ctx} : fin de période invalide")
        if r["version"] not in ("original", "rectificatif"):
            E(f"{ctx} : version doit valoir original ou rectificatif")
        if r["version"] == "rectificatif" and not r["amends_doc_id"]:
            E(f"{ctx} : rectificatif sans document rectifié")
        if r["local_copy"]:
            path = root / r["local_copy"]
            if not path.exists():
                E(f"{ctx} : copie locale introuvable {r['local_copy']}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != r["local_sha256"].lower():
                E(f"{ctx} : empreinte SHA-256 de la copie locale différente")
        else:
            U(f"{ctx} : pas de copie locale (seule l'URL permet la vérification)")
    for r in t["documents"]:
        if r["amends_doc_id"] and r["amends_doc_id"] not in docs:
            E(f"document {r['doc_id']} : rectifie un document inconnu {r['amends_doc_id']!r}")

    seen_facts = set()
    for r in t["facts"]:
        ctx = f"fait {r['fact_id']}"
        if not r["fact_id"] or r["fact_id"] in seen_facts:
            E(f"fait vide ou en double : {r['fact_id']!r}")
        seen_facts.add(r["fact_id"])
        doc = docs.get(r["doc_id"])
        if doc is None:
            E(f"{ctx} : document d'origine inconnu {r['doc_id']!r}")
        if not (r["concept"] and r["definition"] and r["unit"]):
            E(f"{ctx} : concept, définition ou unité manquant")
        if r["value"] == "":
            U(f"{ctx} ({r['concept']}) : valeur inconnue (null)")
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
        if pend is None:
            E(f"{ctx} : fin de période invalide")
        elif doc is not None and _dt(doc["accepted_at"]) and pend > _dt(doc["accepted_at"]).date():
            E(f"{ctx} : période postérieure à l'acceptation du document")
        if r["concept"] in SHARE_CONCEPTS:
            if _d(r["measure_date"]) is None or not r["share_class"]:
                E(f"{ctx} ({r['concept']}) : date de mesure et catégorie d'actions obligatoires")
            if r["concept"] == "market_cap" and r["price_adjusted"] not in ("oui", "non"):
                E(f"{ctx} : préciser si le cours utilisé est ajusté (oui/non)")

    for r in t["activities"]:
        ctx = f"activité {r['issuer_id']}"
        if r["issuer_id"] not in issuers:
            E(f"{ctx} : émetteur inconnu")
        if _dt(r["available_at"]) is None:
            E(f"{ctx} : available_at invalide ou sans fuseau")
        if not r["source"]:
            E(f"{ctx} : source manquante")
        if r["proposed_code"] in ("", "INCONNU"):
            U(f"{ctx} : classification d'activité non établie")
        elif not r["justification"]:
            E(f"{ctx} : code proposé sans justification")

    if nature == "REEL":
        cited = [r.get(k, "") for tab in t.values() for r in tab for k in ("source", "source_url", "url")]
        bad = sorted({c for c in cited if c and any(w in c.upper() for w in ("DEMO", "FICTIF", "TEST"))})
        if bad:
            E(f"dossier déclaré REEL citant des sources de démonstration : {bad[:3]}")
    return res
