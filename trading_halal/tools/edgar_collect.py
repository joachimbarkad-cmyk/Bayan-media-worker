"""Collecte EDGAR (SEC) -> dossier d'AUDIT documentaire. Hors du paquet halal_sim, qui reste sans réseau.

Deux étapes séparées :
  collect : télécharge les JSON bruts « submissions » et « companyfacts » d'une liste de CIK, avec journal
            (URL, horodatage UTC, SHA-256). Aucune valeur par défaut pour l'identification SEC : --user-agent
            est obligatoire à chaque lancement (la SEC demande un nom et une adresse électronique de contact).
  convert : transforme ces JSON bruts en dossier d'audit (issuers, documents, facts, ...) vérifiable par
            `python3 -m halal_sim audit-docs`. Aucune normalisation automatique : concept_map.csv reste vide,
            tous les faits sont « non normalisés » et le verdict reste NON EXPLOITABLE tant qu'un humain n'a pas
            mappé, justifié et rapproché chaque fait de sa pièce.

HYPOTHÈSES À VÉRIFIER (documentation SEC non consultable depuis l'environnement de développement) :
- URL : https://data.sec.gov/submissions/CIK##########.json et
        https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json (CIK sur 10 chiffres) ;
- submissions : filings.recent = listes parallèles accessionNumber, filingDate, reportDate, acceptanceDateTime,
  form, primaryDocument ;
- companyfacts : facts.<taxonomie>.<concept>.units.<unité> = liste de {accn, end, [start], val, form, filed, ...} ;
  pas de contexte XBRL ni de précision (decimals). Selon la SEC (rapporté par le relecteur), companyfacts n'agrège
  que certains faits de taxonomies standard s'appliquant à l'entité : ce n'est PAS l'ensemble des faits du dépôt,
  et l'absence de contexte ne prouve pas l'absence de dimensions -> dimensions et contexte laissés INCONNUS ;
- submissions : filings.recent ne couvre que les dépôts récents ; les plus anciens sont référencés dans
  filings.files (non collectés ici : signalé comme historique incomplet) ;
- chaque JSON porte le CIK de l'émetteur (champ « cik ») : il doit correspondre au CIK du journal ;
- accès équitable : au plus 10 requêtes par seconde (l'outil en fait au plus 2).
L'analyse est STRICTE : un champ attendu absent arrête la conversion avec un message explicite.

Usage :
  python3 tools/edgar_collect.py collect --cik 320193 --user-agent "Prénom Nom contact@domaine" --out DOSSIER_BRUT
  python3 tools/edgar_collect.py collect --cik 320193 --dry-run --out DOSSIER_BRUT      # aucune requête
  python3 tools/edgar_collect.py convert --raw DOSSIER_BRUT --out DOSSIER_AUDIT [--forms 10-K,10-Q]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"
MIN_INTERVAL_S = 0.5
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PLACEHOLDER_DOMAINS = re.compile(r"@(example|exemple|domaine|domain|test|invalid)\.", re.IGNORECASE)
AUDIT_HEADERS = {
    "issuers": ["issuer_id", "name", "id_scheme", "source", "source_url"],
    "securities": ["security_id", "issuer_id", "ticker", "exchange", "valid_from", "valid_to", "instrument_type",
                   "currency", "source"],
    "documents": ["doc_id", "issuer_id", "doc_type", "accession_number", "url", "local_copy", "local_sha256",
                  "period_end", "accepted_at", "public_available_at", "retrieved_at", "version", "amends_doc_id"],
    "facts": ["fact_id", "doc_id", "source_concept", "source_context", "source_dimensions", "source_unit", "raw_value",
              "decimals", "normalized_concept", "transformation", "normalization_justification", "definition", "value",
              "unit", "currency", "period_type", "period_start", "period_end", "measure_date", "share_class",
              "price_adjusted", "corrects_fact_id", "reconciled", "reconciled_note"],
    "concept_map": ["source_concept", "normalized_concept", "justification"],
    "activities": ["issuer_id", "proposed_code", "evidence_doc_id", "available_at", "source", "source_url",
                   "justification"],
}


class EdgarFormatError(ValueError):
    pass


TRACE_FILE = "trace_source.csv"
TRACE_HEADERS = ["fact_id", "source_file", "source_pointer", "entry_sha256", "fy", "fp", "frame"]
JOURNAL_FILE = "journal_conversion.json"


def cik10(value: str) -> str:
    digits = value.strip().lstrip("0") or "0"
    if not digits.isdigit() or len(digits) > 10:
        raise ValueError(f"CIK invalide : {value!r}")
    return digits.zfill(10)


def check_user_agent(ua: str | None) -> str:
    if not ua or not EMAIL_RE.search(ua) or len(ua.split()) < 2:
        raise SystemExit("REFUS : --user-agent obligatoire, sous la forme « Prénom Nom adresse@domaine ». "
                         "Aucune valeur par défaut n'est fournie.")
    if PLACEHOLDER_DOMAINS.search(ua):
        raise SystemExit("REFUS : l'identification ressemble à un exemple ; indiquez un contact réel.")
    return ua


def _get(url: str, ua: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _require_fresh_dir(out: Path, replace: bool, what: str) -> None:
    """Jamais d'écrasement silencieux : un dossier existant non vide n'est réutilisé qu'avec --remplacer."""
    if out.exists() and any(out.iterdir()) and not replace:
        raise SystemExit(f"REFUS : {out} existe déjà et n'est pas vide ({what}). Choisissez un dossier neuf, ou "
                         "ajoutez --remplacer en connaissance de cause (un rapprochement humain y serait perdu).")


def import_files(cik: str, submissions: Path, companyfacts: Path, retrieved_at: str, out: Path,
                 replace: bool = False) -> list[dict]:
    """Enregistre des JSON téléchargés À LA MAIN (navigateur) : aucune requête réseau, aucune identification.
    L'heure de téléchargement est DÉCLARÉE par l'utilisateur (avec fuseau), jamais inventée."""
    try:
        when = datetime.fromisoformat(retrieved_at)
    except ValueError:
        when = None
    if when is None or when.tzinfo is None:
        raise SystemExit("REFUS : --retrieved-at doit être une date-heure avec fuseau, ex. 2026-09-28T14:05:00+02:00")
    _require_fresh_dir(out, replace, "collecte brute")
    out.mkdir(parents=True, exist_ok=True)
    c10 = cik10(cik)
    log = []
    for kind, src, url in (("submissions", submissions, SUBMISSIONS_URL.format(cik=c10)),
                           ("companyfacts", companyfacts, FACTS_URL.format(cik=c10))):
        body = Path(src).read_bytes()
        name = f"{kind}_CIK{c10}.json"
        (out / name).write_bytes(body)
        log.append({"kind": kind, "cik": c10, "url": url, "file": name, "retrieved_at": when.isoformat(),
                    "sha256": hashlib.sha256(body).hexdigest(), "method": "téléchargement manuel déclaré"})
    (out / "journal_collecte.json").write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return log


def collect(ciks: list[str], out: Path, ua: str | None, dry_run: bool = False, fetch=_get,
            replace: bool = False) -> list[dict]:
    targets = []
    for c in ciks:
        c10 = cik10(c)
        targets += [("submissions", c10, SUBMISSIONS_URL.format(cik=c10)), ("companyfacts", c10, FACTS_URL.format(cik=c10))]
    if dry_run:
        for kind, c10, url in targets:
            print(f"[simulation] {kind:12} {c10} {url}")
        return []
    ua = check_user_agent(ua)
    _require_fresh_dir(out, replace, "collecte brute")
    out.mkdir(parents=True, exist_ok=True)
    log = []
    for i, (kind, c10, url) in enumerate(targets):
        if i:
            time.sleep(MIN_INTERVAL_S)
        body = fetch(url, ua)
        path = out / f"{kind}_CIK{c10}.json"
        path.write_bytes(body)
        log.append({"kind": kind, "cik": c10, "url": url, "file": path.name,
                    "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "sha256": hashlib.sha256(body).hexdigest()})
        print(f"{kind:12} {c10} -> {path.name}")
    # L'identification SEC n'est pas enregistrée dans le journal (donnée personnelle).
    (out / "journal_collecte.json").write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return log


def _need(obj: dict, key: str, ctx: str):
    if key not in obj:
        raise EdgarFormatError(f"{ctx} : champ attendu {key!r} absent (format SEC différent de l'hypothèse)")
    return obj[key]


def convert(raw: Path, out: Path, forms: set[str], replace: bool = False) -> dict:
    _require_fresh_dir(out, replace, "dossier d'audit")
    journal = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
    retrieved = {(e["kind"], e["cik"]): e for e in journal}
    for e in journal:  # intégrité des fichiers bruts depuis la collecte
        if hashlib.sha256((raw / e["file"]).read_bytes()).hexdigest() != e["sha256"]:
            raise EdgarFormatError(f"{e['file']} modifié depuis sa collecte (SHA-256 différent)")
    rows = {k: [] for k in AUDIT_HEADERS}
    amendments_to_link, skipped_facts, incomplete, merged, skipped_docs = [], 0, [], 0, []
    seen: dict[str, tuple] = {}
    # Journal des exclusions (par numéro d'accès et motif) et trace de chaque fait vers son entrée JSON brute.
    excluded: dict[tuple, dict] = {}
    trace, merged_trace, total_items = [], [], 0
    for (kind, c10), entry in sorted(retrieved.items()):
        if kind != "submissions":
            continue
        sub = json.loads((raw / entry["file"]).read_text(encoding="utf-8"))
        _check_cik(sub, c10, entry["file"])
        name = _need(sub, "name", entry["file"])
        older = _need(sub, "filings", entry["file"]).get("files") or []
        if older:
            incomplete.append(f"{c10} : {len(older)} fichier(s) de dépôts plus anciens non collecté(s) "
                              f"({', '.join(str(f.get('name', '?')) for f in older[:3])}{'…' if len(older) > 3 else ''})")
        rows["issuers"].append({"issuer_id": c10, "name": name, "id_scheme": "CIK",
                                "source": "SEC EDGAR submissions API", "source_url": entry["url"]})
        recent = _need(_need(sub, "filings", entry["file"]), "recent", entry["file"])
        cols = {k: _need(recent, k, entry["file"]) for k in
                ("accessionNumber", "filingDate", "reportDate", "acceptanceDateTime", "form", "primaryDocument")}
        n = len(cols["accessionNumber"])
        if any(len(v) != n for v in cols.values()):
            raise EdgarFormatError(f"{entry['file']} : listes filings.recent de longueurs différentes")
        docs_by_accn, meta_by_accn, why_not = {}, {}, {}
        for i in range(n):
            form = cols["form"][i]
            base = form[:-2] if form.endswith("/A") else form
            accn = cols["accessionNumber"][i]
            if base not in forms:
                why_not[accn] = f"formulaire non retenu ({form})"
                continue
            if form.endswith("/A"):
                amendments_to_link.append(f"{c10} {form} {accn} (période {cols['reportDate'][i]})")
                why_not[accn] = f"rectificatif ({form}) non rattaché : document rectifié à désigner à la main"
                continue  # le document rectifié doit être désigné à la main : pas d'inférence
            if not cols["reportDate"][i]:
                skipped_docs.append(f"{c10} {form} {accn} : fin de période (reportDate) absente")
                why_not[accn] = f"dépôt {form} retenu puis écarté : fin de période (reportDate) absente"
                continue
            doc_id = f"{c10}-{accn}"
            docs_by_accn[accn] = doc_id
            meta_by_accn[accn] = (form, cols["filingDate"][i])
            rows["documents"].append({
                "doc_id": doc_id, "issuer_id": c10, "doc_type": form, "accession_number": accn,
                "url": ARCHIVE_URL.format(cik_int=int(c10), acc_nodash=accn.replace("-", ""),
                                          doc=cols["primaryDocument"][i]),
                "local_copy": "", "local_sha256": "", "period_end": cols["reportDate"][i],
                "accepted_at": cols["acceptanceDateTime"][i].replace("Z", "+00:00"),
                "public_available_at": "",  # non établie par l'API : laissée inconnue
                "retrieved_at": entry["retrieved_at"], "version": "original", "amends_doc_id": ""})
        facts_entry = retrieved.get(("companyfacts", c10))
        if facts_entry is None:
            continue
        cf = json.loads((raw / facts_entry["file"]).read_text(encoding="utf-8"))
        _check_cik(cf, c10, facts_entry["file"])
        for taxonomy, concepts in _need(cf, "facts", facts_entry["file"]).items():
            for concept, body in concepts.items():
                for unit, items in _need(body, "units", f"{taxonomy}:{concept}").items():
                    for idx, it in enumerate(items):
                        total_items += 1
                        pointer = make_pointer(taxonomy, concept, unit, idx)
                        doc_id = docs_by_accn.get(_need(it, "accn", f"{taxonomy}:{concept}"))
                        if doc_id is None:
                            skipped_facts += 1
                            reason = why_not.get(it["accn"], "dépôt absent de filings.recent (historique non collecté)")
                            ex = excluded.setdefault((c10, it["accn"]), {
                                "cik": c10, "accn": it["accn"], "form": it.get("form", ""), "filed": it.get("filed", ""),
                                "motif": reason, "faits": 0, "exemple": pointer})
                            ex["faits"] += 1
                            continue
                        accn = it["accn"]
                        f_form, f_filed = _need(it, "form", concept), _need(it, "filed", concept)
                        if (f_form, f_filed) != meta_by_accn[accn]:
                            raise EdgarFormatError(
                                f"{taxonomy}:{concept} : fait rattaché au dépôt {accn} ({meta_by_accn[accn][0]}, déposé le "
                                f"{meta_by_accn[accn][1]}) mais déclaré {f_form} déposé le {f_filed} ; conversion arrêtée")
                        start = it.get("start", "")
                        fid = f"{doc_id}-{taxonomy}:{concept}-{unit}-{start}-{_need(it, 'end', concept)}".replace("/", "_")
                        val = _need(it, "val", concept)
                        if fid in seen:
                            if seen[fid][0] != val:  # même dépôt, concept, unité et période, valeurs différentes
                                raise EdgarFormatError(
                                    f"Doublon contradictoire {fid} : {seen[fid][1]} contre {json.dumps(it)} ; "
                                    "conversion arrêtée, les deux entrées brutes restent dans le fichier source")
                            merged += 1
                            merged_trace.append({"fact_id": fid, "source_pointer": pointer})
                            continue
                        seen[fid] = (val, json.dumps(it))
                        trace.append({"fact_id": fid, "source_file": facts_entry["file"], "source_pointer": pointer,
                                      "entry_sha256": entry_sha256(it), "fy": str(it.get("fy", "")),
                                      "fp": str(it.get("fp", "")), "frame": str(it.get("frame", ""))})
                        rows["facts"].append({
                            "fact_id": fid,
                            "doc_id": doc_id, "source_concept": f"{taxonomy}:{concept}",
                            "source_context": "", "source_dimensions": "INCONNU",
                            "source_unit": unit, "raw_value": str(_need(it, "val", concept)), "decimals": "",
                            "normalized_concept": "", "transformation": "", "normalization_justification": "",
                            "definition": body.get("label") or concept, "value": "",
                            "unit": "actions" if unit == "shares" else ("monnaie" if re.fullmatch(r"[A-Z]{3}", unit) else unit),
                            "currency": unit if re.fullmatch(r"[A-Z]{3}", unit) else "",
                            "period_type": "duration" if start else "instant", "period_start": start,
                            "period_end": _need(it, "end", concept),
                            "measure_date": it["end"] if unit == "shares" else "",
                            "share_class": "INCONNU" if unit == "shares" else "",
                            "price_adjusted": "", "corrects_fact_id": "", "reconciled": "", "reconciled_note": ""})
    out.mkdir(parents=True, exist_ok=True)
    warning = ("Données SEC EDGAR converties automatiquement (companyfacts : sous-ensemble des faits du dépôt). "
               "Contexte, dimensions et catégorie d'actions INCONNUS. Aucun fait normalisé ni rapproché : dossier "
               "NON EXPLOITABLE tant qu'un humain n'a pas établi, mappé, justifié et rapproché chaque fait.")
    warning += (f" PÉRIMÈTRE : dépôts récents (filings.recent) des formulaires {sorted(forms)} ; "
                f"{len(rows['documents'])} document(s) retenu(s), {len(skipped_docs)} écarté(s), "
                f"{len(amendments_to_link)} rectificatif(s) à rattacher à la main.")
    if incomplete:
        warning += " HISTORIQUE INCOMPLET : " + " ; ".join(incomplete)
    (out / "manifest.json").write_text(json.dumps({
        "name": f"edgar_{datetime.now(timezone.utc):%Y%m%d}", "nature": "REEL", "warning": warning},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, header in AUDIT_HEADERS.items():
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            w.writerows(rows[name])
    with open(out / TRACE_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TRACE_HEADERS)
        w.writeheader()
        w.writerows(trace)
    exclusions = sorted(excluded.values(), key=lambda e: (e["cik"], e["filed"], e["accn"]))
    (out / JOURNAL_FILE).write_text(json.dumps({
        "formulaires": sorted(forms),
        "entrees_brutes_companyfacts": total_items, "faits_retenus": len(trace),
        "doublons_identiques_fusionnes": merged_trace,
        "faits_ecartes": skipped_facts, "exclusions_par_depot": exclusions,
        "depots_retenus_puis_ecartes": skipped_docs, "rectificatifs_a_rattacher": amendments_to_link,
        "historique_incomplet": incomplete}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if total_items != len(trace) + merged + skipped_facts:  # aucune entrée brute ne disparaît sans être comptée
        raise EdgarFormatError("comptage incohérent des entrées companyfacts ; conversion à reprendre")
    return {"documents": len(rows["documents"]), "facts": len(rows["facts"]),
            "amendments_to_link": amendments_to_link, "facts_skipped_other_documents": skipped_facts,
            "identical_duplicates_merged": merged, "incomplete_history": incomplete,
            "selected_but_skipped": skipped_docs, "excluded_filings": len(excluded),
            "journal": str(out / JOURNAL_FILE)}


def entry_sha256(item: dict) -> str:
    return hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _esc(s: str) -> str:  # échappement des pointeurs JSON (RFC 6901) : les unités peuvent contenir « / »
    return s.replace("~", "~0").replace("/", "~1")


def make_pointer(taxonomy: str, concept: str, unit: str, idx: int) -> str:
    return f"facts/{_esc(taxonomy)}/{_esc(concept)}/units/{_esc(unit)}/{idx}"


def parse_pointer(pointer: str) -> tuple[str, str, str, int]:
    parts = pointer.split("/")
    if len(parts) != 6 or parts[0] != "facts" or parts[3] != "units" or not parts[5].isdigit():
        raise EdgarFormatError(f"pointeur de trace invalide : {pointer!r}")
    un = [x.replace("~1", "/").replace("~0", "~") for x in parts]
    return un[1], un[2], un[4], int(un[5])


def _resolve_pointer(doc: dict, pointer: str):
    taxonomy, concept, unit, idx = parse_pointer(pointer)
    return doc["facts"][taxonomy][concept]["units"][unit][idx]


def verify_trace(raw: Path, audit: Path) -> list[str]:
    """Recalcule chaque fait converti depuis son entrée JSON brute : aucune valeur, date ou attribution modifiée."""
    problems: list[str] = []
    journal = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
    for e in journal:
        if hashlib.sha256((raw / e["file"]).read_bytes()).hexdigest() != e["sha256"]:
            problems.append(f"{e['file']} modifié depuis sa collecte")
    if problems:
        return problems
    with open(audit / "facts.csv", newline="", encoding="utf-8") as f:
        facts = {r["fact_id"]: r for r in csv.DictReader(f)}
    with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
        docs = {r["doc_id"]: r for r in csv.DictReader(f)}
    with open(audit / TRACE_FILE, newline="", encoding="utf-8") as f:
        trace = list(csv.DictReader(f))
    cache: dict[str, dict] = {}
    traced = set()
    for t in trace:
        fid = t["fact_id"]
        if fid in traced:
            problems.append(f"{fid} : tracé deux fois")
        traced.add(fid)
        fact = facts.get(fid)
        if fact is None:
            problems.append(f"{fid} : présent dans la trace, absent de facts.csv")
            continue
        src = raw / Path(t["source_file"]).name
        if src.name not in cache:
            cache[src.name] = json.loads(src.read_text(encoding="utf-8"))
        try:
            it = _resolve_pointer(cache[src.name], t["source_pointer"])
        except (KeyError, IndexError, ValueError, EdgarFormatError):
            problems.append(f"{fid} : entrée brute introuvable ({t['source_pointer']})")
            continue
        tax, concept, unit, _ = parse_pointer(t["source_pointer"])
        doc = docs.get(fact["doc_id"], {})
        checks = {
            "empreinte de l'entrée": (entry_sha256(it), t["entry_sha256"]),
            "valeur": (str(it.get("val")), fact["raw_value"]),
            "numéro d'accès": (it.get("accn"), doc.get("accession_number")),
            "concept": (f"{tax}:{concept}", fact["source_concept"]),
            "unité": (unit, fact["source_unit"]),
            "début de période": (it.get("start", ""), fact["period_start"]),
            "fin de période": (it.get("end"), fact["period_end"]),
            "formulaire": (it.get("form"), doc.get("doc_type")),
            "fy/fp/frame": ((str(it.get("fy", "")), str(it.get("fp", "")), str(it.get("frame", ""))),
                            (t["fy"], t["fp"], t["frame"])),
        }
        for label, (a, b) in checks.items():
            if a != b:
                problems.append(f"{fid} : {label} différent(e) de l'entrée brute ({a!r} contre {b!r})")
    for fid in facts.keys() - traced:
        problems.append(f"{fid} : fait sans trace vers une entrée brute")
    problems += _compare_with_reconversion(raw, audit)
    return problems


# Colonnes produites par la conversion. Les autres (normalisation, rapprochement, copie locale, diffusion publique,
# rectificatif désigné à la main) relèvent du travail humain et ne sont pas comparées.
CONVERTER_OWNED = {
    "issuers": ("issuer_id", ["issuer_id", "name", "id_scheme", "source", "source_url"]),
    "documents": ("doc_id", ["doc_id", "issuer_id", "doc_type", "accession_number", "url", "period_end", "accepted_at",
                             "retrieved_at"]),
    "facts": ("fact_id", ["fact_id", "doc_id", "source_concept", "source_unit", "raw_value", "definition",
                          "period_type", "period_start", "period_end", "measure_date"]),
}


def _compare_with_reconversion(raw: Path, audit: Path) -> list[str]:
    """Refait la conversion depuis les fichiers bruts et compare chaque colonne produite par la conversion : une date
    d'acceptation, un formulaire, un émetteur ou une ligne modifiés, ajoutés ou supprimés sont signalés."""
    problems: list[str] = []
    jpath = audit / JOURNAL_FILE
    if not jpath.exists():
        return [f"{JOURNAL_FILE} absent : reconversion impossible"]
    forms = set(json.loads(jpath.read_text(encoding="utf-8")).get("formulaires") or [])
    if not forms:
        return [f"{JOURNAL_FILE} : formulaires retenus non indiqués ; reconversion impossible"]
    tmp = Path(tempfile.mkdtemp(prefix="reconversion_"))
    try:
        ref = tmp / "ref"
        convert(raw, ref, forms)
        for name, (key, cols) in CONVERTER_OWNED.items():
            def load(folder):
                with open(folder / f"{name}.csv", newline="", encoding="utf-8") as f:
                    return {r[key]: r for r in csv.DictReader(f)}
            mine, theirs = load(audit), load(ref)
            for k in sorted(mine.keys() - theirs.keys()):
                problems.append(f"{name}.csv : ligne {k} absente de la reconversion (ajoutée à la main ?)")
            for k in sorted(theirs.keys() - mine.keys()):
                problems.append(f"{name}.csv : ligne {k} de la reconversion absente du dossier")
            for k in sorted(mine.keys() & theirs.keys()):
                for c in cols:
                    if mine[k].get(c, "") != theirs[k].get(c, ""):
                        problems.append(f"{name}.csv {k} : {c} = {mine[k].get(c, '')!r}, reconversion "
                                        f"{theirs[k].get(c, '')!r}")
        for fname in (TRACE_FILE, JOURNAL_FILE):
            if (audit / fname).read_bytes() != (ref / fname).read_bytes():
                problems.append(f"{fname} différent de la reconversion")
        mine_w = json.loads((audit / "manifest.json").read_text(encoding="utf-8")).get("warning")
        if mine_w != json.loads((ref / "manifest.json").read_text(encoding="utf-8")).get("warning"):
            problems.append("manifest.json : avertissement différent de la reconversion")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return problems


def verify_source(raw: Path, fresh: Path, audit: Path) -> tuple[list[str], list[str]]:
    """Contrôle INDÉPENDANT des empreintes locales : compare le dossier à une copie retéléchargée de la SEC.
    Renvoie (écarts, invérifiables). Les métadonnées d'un dépôt et les faits déjà publiés ne devraient pas changer ;
    un dépôt sorti de filings.recent dans la nouvelle copie est seulement « invérifiable »."""
    problems, unverifiable = [], []
    with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
        docs = list(csv.DictReader(f))
    new_log = {(e["kind"], e["cik"]): e for e in json.loads((fresh / "journal_collecte.json").read_text("utf-8"))}
    for d in docs:
        entry = new_log.get(("submissions", d["issuer_id"]))
        if entry is None:
            unverifiable.append(f"{d['doc_id']} : submissions absent de la nouvelle copie")
            continue
        rec = _need(_need(json.loads((fresh / entry["file"]).read_text("utf-8")), "filings", entry["file"]), "recent",
                    entry["file"])
        try:
            i = rec["accessionNumber"].index(d["accession_number"])
        except ValueError:
            unverifiable.append(f"{d['doc_id']} : dépôt absent de filings.recent dans la nouvelle copie")
            continue
        fresh_vals = {"accepted_at": rec["acceptanceDateTime"][i].replace("Z", "+00:00"), "doc_type": rec["form"][i],
                      "period_end": rec["reportDate"][i]}
        for c, v in fresh_vals.items():
            if d[c] != v:
                problems.append(f"{d['doc_id']} : {c} = {d[c]!r}, SEC (nouvelle copie) {v!r}")
    with open(audit / TRACE_FILE, newline="", encoding="utf-8") as f:
        trace = list(csv.DictReader(f))
    old_cache, new_index = {}, {}
    for t in trace:
        name = Path(t["source_file"]).name
        if name not in old_cache:
            old_cache[name] = json.loads((raw / name).read_text(encoding="utf-8"))
            new_index[name] = None
            if any(e["kind"] == "companyfacts" and e["file"] == name for e in new_log.values()):
                cf = json.loads((fresh / name).read_text(encoding="utf-8"))
                new_index[name] = {_fact_key(tax, concept, unit, it)
                                   for tax, concepts in cf["facts"].items()
                                   for concept, body in concepts.items()
                                   for unit, items in body["units"].items() for it in items}
        tax, concept, unit, _ = parse_pointer(t["source_pointer"])
        it = _resolve_pointer(old_cache[name], t["source_pointer"])
        if new_index[name] is None:
            unverifiable.append(f"{t['fact_id']} : companyfacts absent de la nouvelle copie")
        elif _fact_key(tax, concept, unit, it) not in new_index[name]:
            problems.append(f"{t['fact_id']} : entrée absente ou différente dans la copie retéléchargée")
    return problems, unverifiable


def _fact_key(tax: str, concept: str, unit: str, it: dict) -> tuple:
    return (tax, concept, unit, it.get("accn"), it.get("start", ""), it.get("end"), json.dumps(it.get("val")),
            it.get("form"), it.get("filed"))


def _check_cik(obj: dict, c10: str, ctx: str) -> None:
    found = _need(obj, "cik", ctx)
    try:
        same = int(str(found)) == int(c10)
    except ValueError:
        same = False
    if not same:
        raise EdgarFormatError(f"{ctx} : CIK {found!r} différent du CIK attendu {c10} (fichier d'un autre émetteur ?)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--cik", action="append", required=True)
    c.add_argument("--user-agent")
    c.add_argument("--out", required=True, type=Path)
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--remplacer", action="store_true")
    i = sub.add_parser("import-files", help="Enregistrer des JSON téléchargés à la main (aucun réseau, aucune identification)")
    i.add_argument("--cik", required=True)
    i.add_argument("--submissions", required=True, type=Path)
    i.add_argument("--companyfacts", required=True, type=Path)
    i.add_argument("--retrieved-at", required=True, help="Date-heure du téléchargement avec fuseau")
    i.add_argument("--out", required=True, type=Path)
    i.add_argument("--remplacer", action="store_true")
    v = sub.add_parser("convert")
    v.add_argument("--raw", required=True, type=Path)
    v.add_argument("--out", required=True, type=Path)
    v.add_argument("--forms", default="10-K,10-Q")
    v.add_argument("--remplacer", action="store_true")
    r = sub.add_parser("verify-trace", help="Recalculer chaque fait converti depuis son entrée JSON brute")
    r.add_argument("--raw", required=True, type=Path)
    r.add_argument("--audit", required=True, type=Path)
    s = sub.add_parser("verify-source", help="Comparer le dossier à une copie retéléchargée de la SEC (collect)")
    s.add_argument("--raw", required=True, type=Path)
    s.add_argument("--fresh", required=True, type=Path, help="dossier produit par un nouveau collect")
    s.add_argument("--audit", required=True, type=Path)
    a = p.parse_args(argv)
    if a.cmd == "collect":
        collect(a.cik, a.out, a.user_agent, a.dry_run, replace=a.remplacer)
    elif a.cmd == "import-files":
        import_files(a.cik, a.submissions, a.companyfacts, a.retrieved_at, a.out, a.remplacer)
        print(f"Fichiers enregistrés dans {a.out}. Étape suivante : convert --raw {a.out} --out <dossier d'audit>")
    elif a.cmd == "verify-trace":
        problems = verify_trace(a.raw, a.audit)
        for msg in problems[:50]:
            print("  ÉCART", msg)
        print(f"{len(problems)} écart(s) entre le dossier converti et les entrées brutes.")
        return 1 if problems else 0
    elif a.cmd == "verify-source":
        problems, unverifiable = verify_source(a.raw, a.fresh, a.audit)
        for msg in problems[:50]:
            print("  ÉCART", msg)
        print(f"{len(problems)} écart(s) avec la copie retéléchargée ; {len(unverifiable)} élément(s) invérifiable(s).")
        return 1 if problems else 0
    else:
        res = convert(a.raw, a.out, set(a.forms.split(",")), a.remplacer)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        print(f"Vérifiez ensuite : python3 -m halal_sim audit-docs {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
