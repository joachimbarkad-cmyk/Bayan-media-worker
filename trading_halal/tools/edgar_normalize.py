"""Normalisation de faits EDGAR selon des règles versionnées, HORS LIGNE, par le journal des saisies.

Deux temps (revue n° 13) : `normalize` PROPOSE (fichier de propositions, aucun fait modifié) ; `reconcile-ixbrl`
normalise et rapproche à partir de la copie locale du document, seule source du contexte et des dimensions.

Aucune cellule n'est modifiée directement : chaque changement devient une entrée de `journal_saisies.csv`
(auteur = cet outil, preuve = document ou URL de la source), puis les fichiers sont réécrits, et le dossier doit
repasser `verify-trace` (reconversion + rejeu du journal) et `audit-docs` sans erreur, sinon rien n'est écrit.

Usage :
  python3 tools/edgar_normalize.py normalize --raw collecte/apple --audit data/audit_edgar_apple \
      --regles config/normalisation/edgar_v1.json
  python3 tools/edgar_normalize.py import-filing --audit DOSSIER --doc-id DOC --fichier aapl-20250927.htm \
      --retrieved-at 2026-09-28T14:05:00+02:00
  python3 tools/edgar_normalize.py reconcile-ixbrl --audit DOSSIER --doc-id DOC --raw RAW --regles REGLES

La normalisation rend un fait utilisable par le projet UNIQUEMENT après rapprochement (reconcile-ixbrl ou humain).
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
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import edgar_collect as ec  # noqa: E402

from halal_sim.audit import EXCLUSION_PREFIX, FALLBACK_PREFIX, FILES, audit_folder  # noqa: E402

TOOL = "edgar_normalize.py"
# Cache des schémas officiels (FASB, SEC) : URL, empreinte et heure dans taxonomies.json (revue n° 16).
TAXO_DIR = Path(__file__).resolve().parents[1] / "collecte" / "taxonomies"
TAXO_MANIFEST = "taxonomies.json"


class NormalizeError(RuntimeError):
    pass


# ----------------------------------------------------------------------------------------------- journal et tables
def _load_tables(audit: Path) -> dict[str, list[dict]]:
    out = {}
    for name in ec.ROW_KEYS:
        with open(audit / f"{name}.csv", newline="", encoding="utf-8") as f:
            out[name] = list(csv.DictReader(f))
    return out


def _load_journal(audit: Path) -> list[dict]:
    p = audit / ec.SAISIES_FILE
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Session:
    """Accumule des saisies, les applique aux tables en mémoire, puis écrit tout ou rien."""

    def __init__(self, audit: Path, author: str):
        self.audit, self.author = audit, author
        self.tables = _load_tables(audit)
        self.index = {n: {ec._row_key(n, r): r for r in rows} for n, rows in self.tables.items()}
        self.journal = _load_journal(audit)
        self.new: list[dict] = []
        now = datetime.now(timezone.utc).replace(microsecond=0)
        last = max((datetime.fromisoformat(e["saisi_le"]) for e in self.journal), default=now)
        self.ts = max(now, last).isoformat()

    def cell(self, name: str, key: str, col: str) -> str:
        return self.index[name].get(key, {}).get(col, "")

    def set(self, name: str, key: str, col: str, value: str, proof: str, note: str = "") -> bool:
        old = self.cell(name, key, col)
        if old == value:
            return False
        row = self.index[name].get(key)
        if row is None:  # nouvelle ligne d'une table humaine
            row = {c: "" for c in FILES[name]}
            self.tables[name].append(row)
            self.index[name][key] = row
        row[col] = value
        self.new.append({"n": str(len(self.journal) + len(self.new) + 1), "fichier": name, "cle": key, "colonne": col,
                         "ancienne_valeur": old, "nouvelle_valeur": value, "auteur": self.author,
                         "saisi_le": self.ts, "preuve": proof, "note": note})
        return True

    def commit(self, raw: Path | None) -> None:
        """Écrit dans une copie, la vérifie (reconversion + journal + audit), puis remplace le dossier."""
        if not self.new:
            return
        tmp = Path(tempfile.mkdtemp(prefix="normalisation_"))
        try:
            stage = tmp / "dossier"
            shutil.copytree(self.audit, stage)
            for name, rows in self.tables.items():
                with open(stage / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=FILES[name])
                    w.writeheader()
                    w.writerows(rows)
            with open(stage / ec.SAISIES_FILE, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=ec.SAISIES_HEADERS)
                w.writeheader()
                w.writerows(self.journal + self.new)
            problems = ec.verify_trace(raw, stage) if raw is not None else []
            res = audit_folder(stage)
            problems += res.errors
            if problems:
                raise NormalizeError("contrôles en échec, rien n'a été écrit :\n  " + "\n  ".join(problems[:20]))
            for name in list(ec.ROW_KEYS) + [ec.SAISIES_FILE.removesuffix(".csv")]:
                fname = f"{name}.csv"
                shutil.copyfile(stage / fname, self.audit / fname)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ----------------------------------------------------------------------------------------------- propositions
# Revue n° 13 : companyfacts ne prouve ni l'absence de dimensions (D1 retirée) ni la catégorie d'actions (C1 retirée :
# la liste actuelle des tickers est une information future et ignore les catégories non cotées). `normalize` ne fait
# donc que PROPOSER ; la normalisation n'est écrite qu'au rapprochement avec le document (reconcile-ixbrl), qui établit
# contexte et dimensions à partir du document lui-même.
PROPOSALS_FILE = "propositions_normalisation.csv"
PROPOSAL_HEADERS = ["fact_id", "doc_id", "regle", "source_concept", "normalized_concept", "source_unit",
                    "period_start", "period_end", "raw_value", "source_pointer", "entry_sha256"]
SHARE_BASED = {"shares_outstanding", "market_cap"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rules(rules_path: Path) -> dict:
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    for r in rules["regles"]:
        if r.get("preuve_presence") is not None and (r["preuve_presence"].get("categorie") != "Statement"
                                                     or r["normalized_concept"] == "total_revenue"):
            raise NormalizeError(f"règle {r['id']} : une extraction par présence exige categorie Statement et ne peut "
                                 "pas produire total_revenue (revue n° 17)")
        fb = r.get("repli_total")
        if fb is not None and (fb.get("concept") != "total_revenue" or not fb.get("si_absents_du_document")
                               or not (fb.get("autres_revenus") or {}).get("motifs")):
            raise NormalizeError(f"règle {r['id']} : repli_total mal formé (concept total_revenue, liste "
                                 "si_absents_du_document et autres_revenus.motifs obligatoires)")
        for spec in (r.get("preuve_position"), (fb or {}).get("preuve_position") if fb else None):
            if spec is not None and (not spec.get("parents") or spec.get("categorie") != "Statement"):
                raise NormalizeError(f"règle {r['id']} : preuve_position mal formée (parents, categorie Statement)")
        spec0 = r.get("preuve_position")
        if spec0 is not None and spec0.get("freres_positifs_interdits", True) is not True and \
                not (spec0.get("freres_revenus") or {}).get("motifs"):
            raise NormalizeError(f"règle {r['id']} : des contributeurs positifs voisins ne sont admis qu'avec "
                                 "freres_revenus (motifs) pour bloquer un autre revenu au même niveau")
        if fb is not None and fb.get("preuve_position", {}).get("freres_positifs_interdits", True) is not True:
            raise NormalizeError(f"règle {r['id']} : un repli exige l'absence de tout autre élément positif")
        if fb is not None and not fb.get("preuve_position"):
            raise NormalizeError(f"règle {r['id']} : un repli exige une preuve_position (revue n° 15)")
        if fb is not None:
            missed = [c for c in [r["source_concept"], *fb["si_absents_du_document"]]
                      if not revenue_like(c, fb["autres_revenus"])]
            if missed:
                raise NormalizeError(f"règle {r['id']} : motifs/exclusions incohérents, ces concepts de revenu ne sont "
                                     f"pas reconnus comme revenus : {missed}")
        if r["normalized_concept"] in SHARE_BASED:
            raise NormalizeError(f"règle {r['id']} : {r['normalized_concept']} exige une catégorie d'actions, qui ne "
                                 "peut pas être établie automatiquement (revue n° 13) ; règle refusée")
    return rules


def rules_tag(rules_path: Path) -> str:
    return f"règles {_rules(rules_path)['version']} sha256:{_sha(rules_path)[:16]}"


def compute_proposals(raw: Path, audit: Path, rules_path: Path) -> tuple[list[dict], dict]:
    """Propositions (lecture seule) : faits dont le concept, l'unité et le type de période relèvent d'une règle, hors
    conflits K1. Aucune inférence sur les dimensions, le contexte ou la catégorie d'actions."""
    rules = _rules(rules_path)
    tables = _load_tables(audit)
    docs = {r["doc_id"]: r for r in tables["documents"]}
    with open(audit / ec.TRACE_FILE, newline="", encoding="utf-8") as f:
        trace = {r["fact_id"]: r for r in csv.DictReader(f)}
    by_concept = {r["source_concept"]: r for r in rules["regles"]}
    report = {"version": rules["version"], "regles_sha256": _sha(rules_path), "propositions": defaultdict(int),
              "ecartes": [], "conflits": []}
    groups = defaultdict(list)
    for fact in tables["facts"]:
        rule = by_concept.get(fact["source_concept"])
        if rule is None:
            continue
        fid = fact["fact_id"]
        if fact["source_unit"] != rule["source_unit"] or fact["period_type"] != rule["period_type"]:
            report["ecartes"].append(f"{fid} : unité ou type de période hors règle {rule['id']}")
            continue
        t = trace.get(fid)
        if t is None:
            report["ecartes"].append(f"{fid} : sans trace brute")
            continue
        groups[(fact["doc_id"], rule["normalized_concept"], fact["period_start"], fact["period_end"])].append(
            (rule, fact, t))
    proposals = []
    for key, members in sorted(groups.items()):
        if len({m[1]["raw_value"] for m in members}) > 1:  # K1
            report["conflits"].append(f"{key} : " + ", ".join(f"{m[1]['source_concept']}={m[1]['raw_value']}"
                                                              for m in members))
            continue
        for rule, fact, t in members:
            proposals.append({"fact_id": fact["fact_id"], "doc_id": fact["doc_id"], "regle": rule["id"],
                              "source_concept": fact["source_concept"], "normalized_concept": rule["normalized_concept"],
                              "source_unit": fact["source_unit"], "period_start": fact["period_start"],
                              "period_end": fact["period_end"], "raw_value": fact["raw_value"],
                              "source_pointer": t["source_pointer"], "entry_sha256": t["entry_sha256"]})
            report["propositions"][rule["normalized_concept"]] += 1
    proposals.sort(key=lambda p: p["fact_id"])
    report["propositions"] = dict(report["propositions"])
    return proposals, report


def normalize(raw: Path, audit: Path, rules_path: Path) -> dict:
    """Écrit les propositions et le rapport ; ne modifie aucun fait (rien n'est normalisé sans le document)."""
    before = ec.verify_trace(raw, audit)
    if before:
        raise NormalizeError("le dossier ne passe pas verify-trace :\n  " + "\n  ".join(before[:10]))
    proposals, report = compute_proposals(raw, audit, rules_path)
    with open(audit / PROPOSALS_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PROPOSAL_HEADERS)
        w.writeheader()
        w.writerows(proposals)
    (audit / "rapport_normalisation.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8")
    return report


# Colonnes écrites par reconcile-ixbrl.
NORMALIZE_FACT_COLUMNS = ["normalized_concept", "transformation", "value", "source_dimensions", "share_class",
                          "normalization_justification", "source_context", "decimals", "reconciled",
                          "reconciled_note"]


def verify_normalisation(raw: Path, audit: Path, rules_path: Path,
                         taxonomies: Path | None = TAXO_DIR) -> tuple[list[str], list[str]]:
    """Refait conversion, propositions, import et rapprochement (mêmes copies locales) avec CES règles dans un dossier
    temporaire et compare chaque cellule de normalisation, concept_map et le fichier de propositions. Renvoie (écarts,
    saisies humaines hors règles) ; une saisie humaine différente est listée, jamais masquée."""
    problems, human = [], []
    expected = f"{TOOL} reconcile-ixbrl ({rules_tag(rules_path)}, automatique)"
    journal = _load_journal(audit)
    last_author = {(e["fichier"], e["cle"], e["colonne"]): e["auteur"] for e in journal}
    for a in sorted({e["auteur"] for e in journal if e["auteur"].startswith(f"{TOOL} reconcile-ixbrl")} - {expected}):
        problems.append(f"saisies attribuées à d'autres règles que celles fournies : « {a} » (attendu « {expected} »)")
    forms = set(json.loads((audit / ec.JOURNAL_FILE).read_text(encoding="utf-8")).get("formulaires") or [])
    tmp = Path(tempfile.mkdtemp(prefix="verif_normalisation_"))
    try:
        ref = tmp / "ref"
        ec.convert(raw, ref, forms)
        normalize(raw, ref, rules_path)
        if not (audit / PROPOSALS_FILE).exists() or \
                (audit / PROPOSALS_FILE).read_bytes() != (ref / PROPOSALS_FILE).read_bytes():
            problems.append(f"{PROPOSALS_FILE} absent ou différent de ce que donnent les règles")
        mine = _load_tables(audit)
        for doc in mine["documents"]:
            if doc["local_copy"]:
                src = audit / doc["local_copy"]
                if not src.is_file() or _sha(src) != doc["local_sha256"]:
                    problems.append(f"{doc['doc_id']} : copie locale absente ou différente de local_sha256")
                    continue
                import_filing(ref, doc["doc_id"], src, "2000-01-01T00:00:00+00:00", raw,
                              annexes=_annexes(src.parent))
                reconcile_ixbrl(ref, doc["doc_id"], raw, rules_path, taxonomies)
        theirs = _load_tables(ref)
        for name, cols in (("facts", NORMALIZE_FACT_COLUMNS), ("concept_map", FILES["concept_map"])):
            m = {ec._row_key(name, r): r for r in mine[name]}
            th = {ec._row_key(name, r): r for r in theirs[name]}
            for key in sorted(m.keys() | th.keys()):
                a, b = m.get(key, {}), th.get(key, {})
                for col in cols:
                    va, vb = a.get(col, ""), b.get(col, "")
                    if va == vb:
                        continue
                    who = last_author.get((name, key, col), "")
                    if who and not who.startswith(TOOL):
                        human.append(f"{name}.csv {key} : {col} = {va!r} (règles : {vb!r}), saisi par {who}")
                    else:
                        problems.append(f"{name}.csv {key} : {col} = {va!r}, les règles donnent {vb!r}"
                                        + (f" (saisie attribuée à « {who} »)" if who else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return problems, human


def _map_concept(s: Session, rule: dict, raw: Path, issuer: str, version: str) -> None:
    src = rule["source_concept"]
    if s.cell("concept_map", src, "normalized_concept"):
        if s.cell("concept_map", src, "normalized_concept") != rule["normalized_concept"]:
            raise NormalizeError(f"concept_map : {src} déjà mappé autrement")
        return
    log = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
    cf = next(e for e in log if e["kind"] == "companyfacts" and e["cik"] == issuer)
    tax, concept = src.split(":", 1)
    body = json.loads((raw / cf["file"]).read_text(encoding="utf-8"))["facts"][tax][concept]
    proof = f"url:{cf['url']}"
    note = f"règle {rule['id']} ({version}) ; libellé taxonomie : {body.get('label', '')}"
    s.set("concept_map", src, "source_concept", src, proof, note)
    s.set("concept_map", src, "normalized_concept", rule["normalized_concept"], proof, note)
    s.set("concept_map", src, "justification",
          f"{rule['justification']} Définition ({tax}) : « {(body.get('description') or '').strip()} »", proof, note)


# ----------------------------------------------------------------------------------------------- document d'origine
ANNEXES_FILE = "annexes.json"
RECONCILE_REPORT = "rapport_rapprochement.json"


def import_filing(audit: Path, doc_id: str, fichier: Path, retrieved_at: str, raw: Path | None = None,
                  how: str = "téléchargé à la main, heure déclarée", annexes: list[Path] | None = None,
                  annex_urls: dict[str, str] | None = None) -> str:
    """Copie le document principal dans copies/ et journalise local_copy / local_sha256. Les annexes (schéma .xsd et
    calculs _cal.xml du dépôt) sont copiées à côté, avec leur empreinte, dans copies/<doc>/annexes.json."""
    try:
        if datetime.fromisoformat(retrieved_at).tzinfo is None:
            raise ValueError
    except ValueError:
        raise NormalizeError("--retrieved-at doit être une date-heure avec fuseau")
    s = Session(audit, f"{TOOL} import-filing ({how} {retrieved_at})")
    doc = s.index["documents"].get(doc_id)
    if doc is None:
        raise NormalizeError(f"document inconnu {doc_id}")
    expected_name = doc["url"].rsplit("/", 1)[-1]
    if fichier.name != expected_name:
        raise NormalizeError(f"le fichier doit être le document principal {expected_name!r} (reçu {fichier.name!r})")
    dest = audit / "copies" / doc_id / fichier.name
    if dest.exists():
        raise NormalizeError(f"{dest} existe déjà")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fichier, dest)
    listed = []
    for a in annexes or []:
        if not re.fullmatch(r"[\w.-]+(\.xsd|_cal\.xml)", a.name):
            dest.unlink()
            raise NormalizeError(f"annexe refusée {a.name!r} (seuls le schéma .xsd et le fichier _cal.xml)")
        shutil.copyfile(a, dest.parent / a.name)
        listed.append({"fichier": a.name, "sha256": _sha(dest.parent / a.name),
                       "url": (annex_urls or {}).get(a.name, ""), "obtenu": f"{how} {retrieved_at}"})
    if listed:
        (dest.parent / ANNEXES_FILE).write_text(json.dumps(listed, ensure_ascii=False, indent=1) + "\n",
                                                encoding="utf-8")
    sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    rel = dest.relative_to(audit).as_posix()
    proof = f"url:{doc['url']}"
    s.set("documents", doc_id, "local_copy", rel, proof, f"{how} {retrieved_at}")
    s.set("documents", doc_id, "local_sha256", sha, proof, "empreinte calculée à l'import")
    try:
        s.commit(raw)
    except NormalizeError:
        dest.unlink()
        raise
    return sha


def fetch_filing(audit: Path, doc_id: str, user_agent: str, raw: Path, fetch=None) -> str:
    """Télécharge le document principal depuis son URL SEC (identification obligatoire, jamais enregistrée), puis
    l'importe avec l'heure réelle du téléchargement (UTC)."""
    ua = ec.check_user_agent(user_agent)
    with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
        doc = next((r for r in csv.DictReader(f) if r["doc_id"] == doc_id), None)
    if doc is None:
        raise NormalizeError(f"document inconnu {doc_id}")
    if not doc["url"].startswith("https://www.sec.gov/Archives/"):
        raise NormalizeError(f"URL inattendue {doc['url']!r}")
    get = fetch or ec._get
    data = get(doc["url"], ua)
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    base = doc["url"].rsplit("/", 1)[0] + "/"
    try:
        names = [i["name"] for i in json.loads(get(base + "index.json", ua))["directory"]["item"]]
    except Exception:  # annexes facultatives : sans elles, aucun repli ne sera prouvé
        names = []
    wanted = [n for n in names if re.fullmatch(r"[\w.-]+(\.xsd|_cal\.xml)", n)]
    tmp = Path(tempfile.mkdtemp(prefix="document_"))
    try:
        path = tmp / doc["url"].rsplit("/", 1)[-1]
        path.write_bytes(data)
        annexes = []
        for n in wanted:
            (tmp / n).write_bytes(get(base + n, ua))
            annexes.append(tmp / n)
        return import_filing(audit, doc_id, path, retrieved_at, raw,
                             how=f"téléchargé automatiquement depuis {doc['url']}, le", annexes=annexes,
                             annex_urls={n: base + n for n in wanted})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def schema_urls(annexes: list[Path]) -> list[str]:
    """Schémas officiels (URL absolues) désignés par les localisateurs de calcul des annexes."""
    urls = set()
    for f in annexes:
        root = ET.parse(f).getroot()
        for cl in root.iter(f"{{{LINK}}}calculationLink"):
            for l in cl.iter(f"{{{LINK}}}loc"):
                url = (l.get(f"{{{XLINK}}}href") or "").partition("#")[0]
                if "://" in url:
                    urls.add(url)
    return sorted(urls)


def fetch_taxonomies(audit: Path, doc_id: str, user_agent: str, cache: Path = TAXO_DIR, fetch=None) -> list[str]:
    """Télécharge dans le cache local les schémas officiels désignés par les calculs d'un document (réseau ;
    identification obligatoire, jamais enregistrée), avec URL, empreinte et heure. Déjà présents : conservés."""
    ua = ec.check_user_agent(user_agent)
    with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
        doc = next((r for r in csv.DictReader(f) if r["doc_id"] == doc_id), None)
    if doc is None or not doc["local_copy"]:
        raise NormalizeError(f"{doc_id} : aucune copie locale")
    urls = schema_urls(_annexes((audit / doc["local_copy"]).parent))
    return _store_schemas(cache, {u: None for u in urls}, ua, fetch)


def import_taxonomy(url: str, fichier: Path, retrieved_at: str, cache: Path = TAXO_DIR) -> list[str]:
    """Ajoute au cache un schéma officiel téléchargé à la main (heure déclarée avec fuseau)."""
    try:
        if datetime.fromisoformat(retrieved_at).tzinfo is None:
            raise ValueError
    except ValueError:
        raise NormalizeError("--retrieved-at doit être une date-heure avec fuseau")
    return _store_schemas(cache, {url: (fichier.read_bytes(), f"téléchargé à la main, heure déclarée {retrieved_at}")},
                          None, None)


def _store_schemas(cache: Path, wanted: dict, ua, fetch) -> list[str]:
    cache.mkdir(parents=True, exist_ok=True)
    mpath = cache / TAXO_MANIFEST
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else []
    known = {e["url"] for e in manifest}
    added = []
    for url, given in wanted.items():
        if url in known:
            continue
        m = re.fullmatch(r"https?://(xbrl\.fasb\.org|xbrl\.sec\.gov)/([\w./-]+\.xsd)", url)
        if not m:
            raise NormalizeError(f"schéma refusé {url!r} (seuls xbrl.fasb.org et xbrl.sec.gov)")
        if given is None:
            data, how = (fetch or ec._get)(url, ua), \
                f"téléchargé automatiquement le {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}"
        else:
            data, how = given
        rel = f"{m.group(1)}/{m.group(2)}"
        (cache / rel).parent.mkdir(parents=True, exist_ok=True)
        (cache / rel).write_bytes(data)
        manifest.append({"url": url, "fichier": rel, "sha256": _sha(cache / rel), "obtenu": how})
        added.append(url)
    mpath.write_text(json.dumps(sorted(manifest, key=lambda e: e["url"]), ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    return added


IX = "http://www.xbrl.org/2013/inlineXBRL"
XBRLI = "http://www.xbrl.org/2003/instance"
SUPPORTED_FORMATS = {"num-dot-decimal", "numdotdecimal", "fixed-zero", "zerodash", "num-comma-decimal"}


XSI_NIL = "{http://www.w3.org/2001/XMLSchema-instance}nil"


def _ix_text(el) -> str:
    """Texte affiché d'un élément XBRL en ligne : descendants compris (faits imbriqués), contenu de ix:exclude exclu."""
    parts = [el.text or ""]
    for child in el:
        if child.tag != f"{{{IX}}}exclude":
            parts.append(_ix_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def _ix_value(el) -> Decimal:
    if el.get(XSI_NIL) == "true":
        raise ValueError("valeur nulle (xsi:nil) dans le document")
    fmt = (el.get("format") or "").split(":")[-1]
    text = _ix_text(el).strip()
    if fmt not in SUPPORTED_FORMATS and fmt != "":
        raise ValueError(f"format {el.get('format')!r} non pris en charge")
    if fmt in ("fixed-zero", "zerodash") or text in ("-", "—", "–"):
        number = Decimal(0)
    else:
        cleaned = text.replace(",", "").replace(" ", "") if fmt != "num-comma-decimal" else \
            text.replace(".", "").replace(" ", "").replace(",", ".")
        if not re.fullmatch(r"\d+(\.\d+)?", cleaned):
            raise ValueError(f"texte affiché non numérique {text!r}")
        number = Decimal(cleaned)
    value = number * (Decimal(10) ** int(el.get("scale") or 0))
    return -value if el.get("sign") == "-" else value


ISO4217 = "http://www.xbrl.org/2003/iso4217"
SEC_CIK_SCHEME = "http://www.sec.gov/CIK"
# Espaces de noms attendus pour les préfixes employés dans les règles (l'année de taxonomie varie).
TAXONOMY_NS = {"us-gaap": re.compile(r"^http://fasb\.org/us-gaap/\d{4}$"),
               "dei": re.compile(r"^http://xbrl\.sec\.gov/dei/\d{4}$"),
               "srt": re.compile(r"^http://fasb\.org/srt/\d{4}$")}


def revenue_like(name: str, spec: dict) -> bool:
    """Concept dont le nom local évoque un revenu (motifs), hors faux amis (exclusions). Heuristique prudente :
    un faux positif bloque seulement un repli (aucun total), jamais l'inverse."""
    local = name.rsplit("}", 1)[-1].split(":", 1)[-1]
    if any(x in local for x in spec.get("exclusions", [])):
        return False
    return any(m in local for m in spec["motifs"])


def _canonical(uri: str, local: str) -> str:
    """Nom canonique « us-gaap:Local » si l'URI est celle d'une taxonomie connue ; sinon « {uri}local »."""
    for prefix, pattern in TAXONOMY_NS.items():
        if pattern.match(uri):
            return f"{prefix}:{local}"
    return f"{{{uri}}}{local}"


LINK = "http://www.xbrl.org/2003/linkbase"
XLINK = "http://www.w3.org/1999/xlink"
SUMMATION = {"http://www.xbrl.org/2003/arcrole/summation-item", "https://xbrl.org/2023/arcrole/summation-item"}
ROLE_DEF = re.compile(r"^\s*\d+\s*-\s*(Statement|Disclosure|Document|Schedule)\s*-\s*(.*)$")
XS = "http://www.w3.org/2001/XMLSchema"


class SchemaResolver:
    """Résout un xlink:href « schéma#identifiant » vers le QName de l'xs:element qu'il désigne, dans le schéma qui le
    déclare (revue n° 16) : schéma du dépôt (annexe) pour une extension, schéma officiel du cache local (empreinte
    vérifiée) pour un concept standard. Schéma absent, identifiant absent ou ambigu, pointeur non « shorthand » ⇒ None :
    la preuve qui en dépend échoue (fail-closed). Le préfixe textuel de l'identifiant n'est jamais utilisé."""

    def __init__(self, annexes: list[Path], cache: Path | None):
        self.local = {a.name: a for a in annexes if a.suffix == ".xsd"}
        self.cache: dict[str, Path] = {}
        self.missing: set[str] = set()
        self.used: set[str] = set()
        self.problems: list[str] = []
        self.problems_soft: list[str] = []
        if cache is not None and (cache / TAXO_MANIFEST).exists():
            for e in json.loads((cache / TAXO_MANIFEST).read_text(encoding="utf-8")):
                f = cache / e["fichier"]
                if f.is_file() and _sha(f) == e["sha256"]:
                    self.cache[e["url"]] = f
                else:
                    self.problems.append(f"schéma {e['url']} absent du cache ou différent de son empreinte")
        self._maps: dict[Path, dict] = {}

    def _ids(self, path: Path) -> dict:
        if path not in self._maps:
            root = ET.parse(path).getroot()
            tns = root.get("targetNamespace") or ""
            ids = defaultdict(list)
            for el in root.iter(f"{{{XS}}}element"):
                if el.get("id"):
                    ids[el.get("id")].append((tns, el.get("name") or ""))
            self._maps[path] = ids
        return self._maps[path]

    def resolve(self, href: str) -> str | None:
        url, _, frag = (href or "").partition("#")
        if not frag or "(" in frag or not url:
            return None
        if "://" in url:
            path = self.cache.get(url)
            if path is not None:
                self.used.add(url)
        else:
            path = self.local.get(url) if "/" not in url else None
        if path is None:
            self.missing.add(url)
            return None
        found = self._ids(path).get(frag, [])
        if len(found) != 1 or not found[0][0] or not found[0][1]:
            return None
        name = _canonical(*found[0])
        if "://" not in url and not name.startswith("{"):
            # un schéma du dépôt ne peut pas définir un concept d'une taxonomie officielle (espace de noms FASB/SEC)
            self.problems_soft.append(f"{url} déclare l'espace de noms officiel de {name} : refusé")
            return None
        return name


def parse_calculations(files: list[Path], resolver: SchemaResolver) -> tuple[dict, list]:
    """Rôles (catégorie EFM Statement/Disclosure…, titre) et relations de calcul sommatoires (rôle, parent, enfant,
    poids) du dépôt. Parent ou enfant non résolu : None."""
    roles, arcs = {}, []
    for f in files:
        root = ET.parse(f).getroot()
        for rt in root.iter(f"{{{LINK}}}roleType"):
            d = rt.find(f"{{{LINK}}}definition")
            m = ROLE_DEF.match((d.text or "") if d is not None else "")
            roles[rt.get("roleURI")] = (m.group(1), m.group(2).strip()) if m else ("", (d.text or "").strip()
                                                                                    if d is not None else "")
        for cl in root.iter(f"{{{LINK}}}calculationLink"):
            role = cl.get(f"{{{XLINK}}}role")
            locs = {l.get(f"{{{XLINK}}}label"): resolver.resolve(l.get(f"{{{XLINK}}}href") or "")
                    for l in cl.iter(f"{{{LINK}}}loc")}
            for a in cl.iter(f"{{{LINK}}}calculationArc"):
                if a.get(f"{{{XLINK}}}arcrole") not in SUMMATION:
                    continue
                arcs.append((role, locs.get(a.get(f"{{{XLINK}}}from")), locs.get(a.get(f"{{{XLINK}}}to")),
                             float(a.get("weight") or "nan")))
    return roles, arcs


def within_precision(value: Decimal, decimals: str) -> bool:
    """Un fait ne doit pas porter de chiffres au-delà de sa précision déclarée (decimals) ; INF ou vide : admis."""
    if not re.fullmatch(r"-?\d+", decimals or ""):
        return True
    return value % (Decimal(10) ** (-int(decimals))) == 0


def _tolerance(decimals: list[str]) -> Decimal:
    return sum((Decimal(5) * Decimal(10) ** (-int(d) - 1) for d in decimals if re.fullmatch(r"-?\d+", d)),
               Decimal(0))


def calculation_verdicts(parent: str, contributors: list[tuple], values: dict) -> tuple[bool | None, bool, str]:
    """Deux verdicts distincts (revue n° 17) sur les faits d'une période (valeurs non nil, cohérentes avec leur
    précision ; un fait nil ou absent ne participe pas) :
    - calcul_XBRL_coherent : avec le total et les contributeurs PRÉSENTS, |total − Σ poids × contributeurs| ≤ somme
      des demi-précisions (chevauchement d'intervalles, arrondi au plus proche, un fait par concept) ; None si le total
      ou tous les contributeurs manquent. Ce n'est pas une implémentation complète de Calculation 1.1 (troncature,
      bornes ouvertes, intersection de doublons compatibles non traitées : de tels faits sont exclus, donc absents).
    - preuve_complete_pour_repli : cohérent ET chaque contributeur présent (un absent n'est pas prouvé nul)."""
    present = [(c, w) for c, w in contributors if c in values]
    absent = [c for c, _ in contributors if c not in values]
    if parent not in values or not present:
        return None, False, f"total ou contributeurs sans fait pour la période ; absents : {absent or [parent]}"
    total = sum(Decimal(str(w)) * values[c][0] for c, w in present)
    tol = _tolerance([values[parent][1]] + [values[c][1] for c, _ in present])
    coherent = abs(values[parent][0] - total) <= tol
    detail = f"{parent} = {values[parent][0]}, somme pondérée des présents = {total}, tolérance {tol}"
    if absent:
        detail += f" ; contributeurs absents ou nil : {absent}"
    return coherent, coherent and not absent, detail


def position_proof(concept: str, roles: dict, arcs: list, spec: dict,
                   values: dict | None = None) -> tuple[str | None, str]:
    """Preuve positive qu'un concept est la première ligne de revenu d'un état financier : dans un rôle de catégorie
    `spec["categorie"]`, enfant de poids +1 d'un parent de `spec["parents"]` ; tous les concepts du calcul résolus ;
    par défaut aucun autre enfant de poids positif (`freres_positifs_interdits: false` n'est admis que pour un total par
    définition, et alors aucun frère positif ne doit évoquer un revenu : `freres_revenus`) ; et, si `values` est
    fourni (faits de l'entité entière pour la période), calcul effectif : parent = Σ poids × enfants, à l'arrondi près.
    Renvoie (preuve, motif d'échec)."""
    why = f"{concept} n'est l'enfant +1 d'aucun parent {spec['parents']} dans un rôle {spec['categorie']}"
    for role, parent, child, w in arcs:
        if child != concept or w != 1.0 or parent not in spec["parents"]:
            continue
        cat, title = roles.get(role, ("", ""))
        if cat != spec["categorie"]:
            continue
        siblings = [(c, w2) for r2, p2, c, w2 in arcs if r2 == role and p2 == parent and c != concept]
        if any(c is None for c, _ in siblings):
            why = f"rôle « {title} » : un contributeur de {parent} n'a pas pu être résolu dans son schéma"
            continue
        if spec.get("freres_positifs_interdits", True) and any(w2 > 0 for _, w2 in siblings):
            why = f"rôle « {title} » : autre contributeur positif de {parent}"
            continue
        rev = [c for c, w2 in siblings if w2 > 0 and spec.get("freres_revenus")
               and revenue_like(c, spec["freres_revenus"])]
        if rev:
            why = f"rôle « {title} » : autre revenu au même niveau que {concept} : {rev}"
            continue
        text = (f"rôle « {cat} - {title} » : {parent} = {concept} (+1)"
                + "".join(f" {'+' if w2 > 0 else '−'} {c}" for c, w2 in siblings))
        if values is not None:
            coherent, complete, detail = calculation_verdicts(parent, [(concept, 1.0)] + siblings, values)
            verdicts = (f"calcul_XBRL_coherent={'oui' if coherent else 'non' if coherent is False else 'non évaluable'}"
                        f" ; preuve_complete_pour_repli={'oui' if complete else 'non'}")
            if not (coherent and complete):
                why = f"rôle « {title} » : {verdicts} ({detail})"
                continue
            text += f" ; {verdicts} ; {detail}"
        return text, ""
    return None, why


def statement_presence(concept: str, roles: dict, arcs: list, spec: dict) -> tuple[str | None, str]:
    """Présence d'un concept (résolu) dans les calculs d'un rôle de catégorie `spec["categorie"]` (état principal),
    comme total ou contributeur, avec tous les concepts de ce calcul résolus. Extraction typée directe, sans repli."""
    for role, parent, child, w in arcs:
        if concept not in (parent, child):
            continue
        cat, title = roles.get(role, ("", ""))
        if cat != spec["categorie"]:
            continue
        group = [a for a in arcs if a[0] == role and a[1] == parent]
        if any(c is None for _, _, c, _ in group) or parent is None:
            continue
        return (f"rôle « {cat} - {title} » : {parent} = "
                + " ".join(f"{'+' if w2 > 0 else '−'} {c}" for _, _, c, w2 in group)), ""
    return None, f"{concept} absent des calculs résolus de tout rôle {spec['categorie']}"


def _annexes(folder: Path) -> list[Path]:
    """Annexes du document, vérifiées contre leurs empreintes (annexes.json)."""
    listed = folder / ANNEXES_FILE
    if not listed.exists():
        return []
    out = []
    for a in json.loads(listed.read_text(encoding="utf-8")):
        f = folder / a["fichier"]
        if not f.is_file() or _sha(f) != a["sha256"]:
            raise NormalizeError(f"annexe {a['fichier']} absente ou différente de son empreinte")
        out.append(f)
    return out


def parse_ixbrl(path: Path) -> tuple[dict, dict, list]:
    """Contextes, unités et faits numériques d'un document XBRL en ligne (XHTML bien formé). Les QNames (concepts,
    mesures) sont résolus par URI d'espace de noms, jamais par la seule chaîne préfixée."""
    decl = defaultdict(set)
    for _, (prefix, uri) in ET.iterparse(path, events=["start-ns"]):
        decl[prefix].add(uri)
    ambiguous = sorted(p for p, uris in decl.items() if len(uris) > 1)
    if ambiguous:
        raise ValueError(f"préfixes liés à plusieurs espaces de noms : {ambiguous}")
    ns = {p: next(iter(u)) for p, u in decl.items()}

    def resolve(qname: str) -> tuple[str, str]:
        prefix, _, local = qname.strip().rpartition(":")
        if prefix not in ns:
            raise ValueError(f"préfixe non déclaré dans {qname!r}")
        return ns[prefix], local

    root = ET.parse(path).getroot()
    contexts, units = {}, {}
    for c in root.iter(f"{{{XBRLI}}}context"):
        period = c.find(f"{{{XBRLI}}}period")
        inst = period.find(f"{{{XBRLI}}}instant")
        start, end = period.find(f"{{{XBRLI}}}startDate"), period.find(f"{{{XBRLI}}}endDate")
        entity = c.find(f"{{{XBRLI}}}entity")
        ident = entity.find(f"{{{XBRLI}}}identifier")
        has_segment = entity.find(f"{{{XBRLI}}}segment") is not None or c.find(f"{{{XBRLI}}}scenario") is not None
        contexts[c.get("id")] = {"start": start.text.strip() if start is not None else "",
                                 "end": (inst if inst is not None else end).text.strip(),
                                 "entity": (ident.text or "").strip(), "scheme": (ident.get("scheme") or "").strip(),
                                 "segment": has_segment}
    for u in root.iter(f"{{{XBRLI}}}unit"):
        measures = [resolve(m.text) for m in u.iter(f"{{{XBRLI}}}measure")]
        if len(measures) == 1 and measures[0][0] == ISO4217:
            units[u.get("id")] = measures[0][1]                      # devise ISO 4217 (ex. USD)
        elif len(measures) == 1 and measures[0] == (XBRLI, "shares"):
            units[u.get("id")] = "shares"
        else:
            units[u.get("id")] = "/".join(f"{{{a}}}{b}" for a, b in measures)
    facts = []
    for el in root.iter(f"{{{IX}}}nonFraction"):
        try:
            name = _canonical(*resolve(el.get("name", "")))
        except ValueError:
            name = ""
        facts.append({"name": name, "context": el.get("contextRef"), "unit": units.get(el.get("unitRef"), ""),
                      "decimals": el.get("decimals") or "", "id": el.get("id") or "", "el": el,
                      "text": _ix_text(el).strip(), "scale": el.get("scale") or "0"})
    return contexts, units, facts


def reconcile_ixbrl(audit: Path, doc_id: str, raw: Path, rules_path: Path, taxonomies: Path | None = TAXO_DIR) -> dict:
    """Normalise ET rapproche les propositions d'un document à partir de sa copie locale XBRL en ligne : même entité,
    même période exacte, même unité, contexte SANS segment, valeur affichée égale à la valeur companyfacts. Le contexte
    et l'absence de dimensions sont alors établis par le document (preuve : fichier + empreinte)."""
    rules = _rules(rules_path)
    tag = rules_tag(rules_path)
    s = Session(audit, f"{TOOL} reconcile-ixbrl ({tag}, automatique)")
    doc = s.index["documents"].get(doc_id)
    if doc is None or not doc["local_copy"]:
        raise NormalizeError(f"{doc_id} : aucune copie locale (utiliser import-filing)")
    path = audit / doc["local_copy"]
    sha = _sha(path)
    if sha != doc["local_sha256"]:
        raise NormalizeError(f"{doc['local_copy']} : empreinte différente de local_sha256")
    proposals, _ = compute_proposals(raw, audit, rules_path)
    by_rule = {r["id"]: r for r in rules["regles"]}
    try:
        contexts, _, ixfacts = parse_ixbrl(path)
    except (ValueError, ET.ParseError) as exc:
        raise NormalizeError(f"{doc['local_copy']} : lecture XBRL en ligne impossible ({exc})")
    cik = int(doc["issuer_id"])

    def entity_ok(ctx) -> bool:
        if ctx["scheme"] != SEC_CIK_SCHEME:
            return False
        try:
            return int(ctx["entity"]) == cik
        except ValueError:
            return False
    # Concepts déclarés pour l'entité entière (contexte sans segment ni scénario), par période exacte.
    report_wide = {(f["name"], contexts[f["context"]]["start"], contexts[f["context"]]["end"], f["unit"])
                   for f in ixfacts if f["context"] in contexts and not contexts[f["context"]]["segment"]
                   and entity_ok(contexts[f["context"]])}
    proof = f"fichier:{doc['local_copy']}#sha256={sha}"
    annexes = _annexes(path.parent)
    resolver = SchemaResolver(annexes, taxonomies)
    try:
        roles, arcs = parse_calculations(annexes, resolver)
    except (ValueError, ET.ParseError) as exc:
        raise NormalizeError(f"annexes illisibles ({exc})")
    annex_note = ", ".join(f"{a.name} (sha256 {_sha(a)[:16]}…)" for a in annexes) or "aucune annexe"
    if resolver.used:
        annex_note += " ; schémas officiels : " + ", ".join(
            f"{u} (sha256 {_sha(resolver.cache[u])[:16]}…)" for u in sorted(resolver.used))
    if resolver.missing:
        annex_note += f" ; schémas non disponibles : {sorted(resolver.missing)}"
    if resolver.problems:
        raise NormalizeError(" ; ".join(resolver.problems))

    def period_values(start: str, end: str, unit: str) -> dict:
        """Faits de l'entité entière pour la période et l'unité : nom -> (valeur, decimals) ; ambigus exclus."""
        seen: dict[str, set] = defaultdict(set)
        for f in ixfacts:
            ctx = contexts.get(f["context"])
            if ctx is None or ctx["segment"] or not entity_ok(ctx) or f["unit"] != unit:
                continue
            if (ctx["start"], ctx["end"]) != (start, end):
                continue
            if f["el"].get(XSI_NIL) == "true":
                continue  # un fait nil ne participe pas au calcul
            try:
                v = _ix_value(f["el"])
            except ValueError:
                seen[f["name"]].add((None, ""))
                continue
            if not within_precision(v, f["decimals"]):
                seen[f["name"]].add((None, ""))  # chiffres au-delà de la précision déclarée : incohérent
                continue
            seen[f["name"]].add((v, f["decimals"]))
        return {n: next(iter(v)) for n, v in seen.items() if len({x for x, _ in v}) == 1 and None not in
                {x for x, _ in v} and len(v) == 1}
    report = {"rapproches": 0, "echecs": []}
    failures: dict[str, str] = {}
    for prop in proposals:
        fid = prop["fact_id"]
        if prop["doc_id"] != doc_id or s.cell("facts", fid, "reconciled"):
            continue
        matches, segmented = [], []
        for f in ixfacts:
            ctx = contexts.get(f["context"])
            if f["name"] != prop["source_concept"] or ctx is None or f["unit"] != prop["source_unit"]:
                continue
            if (ctx["start"], ctx["end"]) != (prop["period_start"], prop["period_end"]):
                continue
            if not entity_ok(ctx):
                continue
            (segmented if ctx["segment"] else matches).append(f)
        reason = None
        if not matches:
            reason = ("aucun fait sans segment dans le document"
                      + (f" ({len(segmented)} fait(s) ventilé(s) seulement)" if segmented else ""))
        else:
            try:
                values = {_ix_value(m["el"]) for m in matches}
            except ValueError as exc:
                values, reason = set(), str(exc)
            if reason is None and len(values) != 1:
                reason = f"valeurs affichées incohérentes {sorted(map(str, values))}"
            elif reason is None and next(iter(values)) != Decimal(prop["raw_value"]):
                reason = f"document {next(iter(values))} ≠ companyfacts {prop['raw_value']}"
        rule = by_rule[prop["regle"]]
        position = None
        pvals = period_values(prop["period_start"], prop["period_end"], prop["source_unit"])
        if reason is None and rule.get("preuve_presence"):
            position, why = statement_presence(rule["source_concept"], roles, arcs, rule["preuve_presence"])
            if position is None:
                reason = f"présence dans un état principal non prouvée ({annex_note}) : {why}"
        if reason is None and rule.get("preuve_position"):
            position, why = position_proof(rule["source_concept"], roles, arcs, rule["preuve_position"], pvals)
            if position is None:
                reason = f"position non prouvée par les calculs du dépôt ({annex_note}) : {why}"
        if reason:
            report["echecs"].append(f"{fid} : {reason}")
            failures[fid] = reason
            continue
        value = next(iter(values))
        m = matches[0]
        _map_concept(s, rule, raw, doc["issuer_id"], rules["version"])
        target, fallback_note = rule["normalized_concept"], ""
        fb = rule.get("repli_total")
        if fb:
            same = [(n, u) for (n, st, en_, u) in report_wide
                    if (st, en_) == (prop["period_start"], prop["period_end"])]
            blockers = sorted({n for n, _ in same if n in fb["si_absents_du_document"]} |
                              {n for n, u in same if re.fullmatch(r"[A-Z]{3}", u) and n != rule["source_concept"]
                               and revenue_like(n, fb["autres_revenus"])})
            proof_pos, why = position_proof(rule["source_concept"], roles, arcs, fb["preuve_position"], pvals) \
                if not blockers else (None, "")
            if not blockers and proof_pos is None:
                blockers = [f"aucune preuve positive dans les calculs du dépôt ({annex_note}) : {why}"]
            if not blockers:
                target = fb["concept"]
                fallback_note = (f"{FALLBACK_PREFIX} preuve positive : {proof_pos} [{annex_note}] ; et le document "
                                 f"ne déclare, pour l'entité entière et cette période, ni {fb['si_absents_du_document']} "
                                 f"ni aucun autre concept de revenu (motifs {fb['autres_revenus']['motifs']}) ; le "
                                 f"composant {rule['source_concept']} est retenu comme {target}. ")
            else:
                fallback_note = f"Repli vers {fb['concept']} non retenu : {'; '.join(blockers)}. "
                report.setdefault("replis_bloques", []).append(f"{fid} : {blockers}")
        decs = {x["decimals"] for x in matches}
        s.set("facts", fid, "source_context", m["context"], proof, "identifiant du contexte XBRL du document")
        s.set("facts", fid, "source_dimensions", "", proof, "établi par le document : contexte sans segment")
        if len(decs) == 1 and m["decimals"]:
            s.set("facts", fid, "decimals", m["decimals"], proof, "attribut decimals du document")
        s.set("facts", fid, "normalized_concept", target, proof,
              rule["id"] + (" (repli)" if fallback_note.startswith(FALLBACK_PREFIX) else ""))
        s.set("facts", fid, "transformation", "aucune", proof, "valeur reprise telle quelle")
        s.set("facts", fid, "value", prop["raw_value"], proof, "valeur reprise telle quelle")
        s.set("facts", fid, "normalization_justification",
              f"{fallback_note}Règle {rule['id']} ({tag}) : {rule['source_concept']} [{rule['source_unit']}, "
              f"{rule['period_type']}] -> {target} ; valeur reprise telle quelle ;"
              + (f" position : {position} [{annex_note}] ;" if position else "") + f" contexte {m['context']} sans segment "
              f"dans le document ; entrée brute {prop['source_pointer']} (sha256 {prop['entry_sha256'][:16]}…).",
              proof, rule["id"])
        s.set("facts", fid, "reconciled", "auto", proof, "rapprochement automatique XBRL en ligne")
        s.set("facts", fid, "reconciled_note",
              f"AUTOMATIQUE : {doc['local_copy']} (sha256 {sha[:16]}…), {len(matches)} élément(s) ix:nonFraction "
              f"{m['name']} contexte {m['context']} sans segment, id {m['id'] or '?'}, affiché « {m['text']} », "
              f"échelle {m['scale']} = {value} ; à relire par une personne.", proof, "")
        report["rapproches"] += 1
    # Tout fait d'un concept désormais mappé mais non normalisé porte une exclusion motivée.
    for fact in s.tables["facts"]:
        if fact["normalized_concept"] or not s.cell("concept_map", fact["source_concept"], "normalized_concept"):
            continue
        fid = fact["fact_id"]
        if fid in failures:
            why, pr = f"document : {failures[fid]}", proof
        else:
            why, pr = "en attente du rapprochement avec son document (dimensions non établies)", f"doc:{fact['doc_id']}"
        s.set("facts", fid, "normalization_justification", f"{EXCLUSION_PREFIX} {why} ({rules['version']})", pr,
              "exclusion explicite")
    s.commit(raw)
    (path.parent / RECONCILE_REPORT).write_text(json.dumps(dict(report, regles=tag, annexes=annex_note),
                                                           ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("normalize")
    n.add_argument("--raw", required=True, type=Path)
    n.add_argument("--audit", required=True, type=Path)
    n.add_argument("--regles", required=True, type=Path)
    i = sub.add_parser("import-filing")
    i.add_argument("--audit", required=True, type=Path)
    i.add_argument("--doc-id", required=True)
    i.add_argument("--fichier", required=True, type=Path)
    i.add_argument("--retrieved-at", required=True)
    i.add_argument("--annexe", action="append", type=Path, default=[], help="schéma .xsd ou fichier _cal.xml du dépôt")
    i.add_argument("--raw", type=Path)
    fx = sub.add_parser("fetch-filing", help="Télécharger le document principal depuis la SEC puis l'importer")
    fx.add_argument("--audit", required=True, type=Path)
    fx.add_argument("--doc-id", required=True)
    fx.add_argument("--user-agent")
    fx.add_argument("--raw", required=True, type=Path)
    ft = sub.add_parser("fetch-taxonomies", help="Télécharger les schémas officiels désignés par les calculs d'un document")
    ft.add_argument("--audit", required=True, type=Path)
    ft.add_argument("--doc-id", required=True)
    ft.add_argument("--user-agent")
    ft.add_argument("--cache", type=Path, default=TAXO_DIR)
    it = sub.add_parser("import-taxonomy", help="Ajouter au cache un schéma officiel téléchargé à la main")
    it.add_argument("--url", required=True)
    it.add_argument("--fichier", required=True, type=Path)
    it.add_argument("--retrieved-at", required=True)
    it.add_argument("--cache", type=Path, default=TAXO_DIR)
    r = sub.add_parser("reconcile-ixbrl")
    r.add_argument("--audit", required=True, type=Path)
    r.add_argument("--doc-id", required=True)
    r.add_argument("--raw", required=True, type=Path)
    r.add_argument("--regles", required=True, type=Path)
    v = sub.add_parser("verify-normalisation", help="Refaire la normalisation avec ces règles et comparer")
    v.add_argument("--raw", required=True, type=Path)
    v.add_argument("--audit", required=True, type=Path)
    v.add_argument("--regles", required=True, type=Path)
    a = p.parse_args(argv)
    try:
        if a.cmd == "normalize":
            res = normalize(a.raw, a.audit, a.regles)
            print(json.dumps({k: (v if k not in ("ecartes", "conflits") else len(v)) for k, v in res.items()},
                             ensure_ascii=False, indent=1))
            print(f"Propositions écrites dans {PROPOSALS_FILE} ; aucun fait n'est normalisé sans son document "
                  "(import-filing puis reconcile-ixbrl).")
        elif a.cmd == "verify-normalisation":
            problems, human = verify_normalisation(a.raw, a.audit, a.regles)
            for msg in problems[:50]:
                print("  ÉCART", msg)
            for msg in human[:50]:
                print("  SAISIE HUMAINE HORS RÈGLES (à relire)", msg)
            print(f"{len(problems)} écart(s) avec les règles ; {len(human)} saisie(s) humaine(s) hors règles.")
            return 1 if problems else 0
        elif a.cmd == "fetch-taxonomies":
            print(json.dumps(fetch_taxonomies(a.audit, a.doc_id, a.user_agent, a.cache), indent=1))
        elif a.cmd == "import-taxonomy":
            print(json.dumps(import_taxonomy(a.url, a.fichier, a.retrieved_at, a.cache), indent=1))
        elif a.cmd == "fetch-filing":
            print("sha256", fetch_filing(a.audit, a.doc_id, a.user_agent, a.raw))
        elif a.cmd == "import-filing":
            print("sha256", import_filing(a.audit, a.doc_id, a.fichier, a.retrieved_at, a.raw, annexes=a.annexe))
        else:
            print(json.dumps(reconcile_ixbrl(a.audit, a.doc_id, a.raw, a.regles), ensure_ascii=False, indent=1))
    except NormalizeError as exc:
        print("REFUS :", exc)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
