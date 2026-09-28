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

from halal_sim.audit import EXCLUSION_PREFIX, FILES, audit_folder  # noqa: E402

TOOL = "edgar_normalize.py"


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


def verify_normalisation(raw: Path, audit: Path, rules_path: Path) -> tuple[list[str], list[str]]:
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
                import_filing(ref, doc["doc_id"], src, "2000-01-01T00:00:00+00:00", raw)
                reconcile_ixbrl(ref, doc["doc_id"], raw, rules_path)
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
def import_filing(audit: Path, doc_id: str, fichier: Path, retrieved_at: str, raw: Path | None = None) -> str:
    """Copie le document principal (téléchargé à la main) dans copies/ et journalise local_copy / local_sha256."""
    try:
        if datetime.fromisoformat(retrieved_at).tzinfo is None:
            raise ValueError
    except ValueError:
        raise NormalizeError("--retrieved-at doit être une date-heure avec fuseau")
    s = Session(audit, f"{TOOL} import-filing (téléchargé à la main, heure déclarée {retrieved_at})")
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
    sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    rel = dest.relative_to(audit).as_posix()
    proof = f"url:{doc['url']}"
    s.set("documents", doc_id, "local_copy", rel, proof, f"téléchargé à la main, heure déclarée {retrieved_at}")
    s.set("documents", doc_id, "local_sha256", sha, proof, "empreinte calculée à l'import")
    try:
        s.commit(raw)
    except NormalizeError:
        dest.unlink()
        raise
    return sha


IX = "http://www.xbrl.org/2013/inlineXBRL"
XBRLI = "http://www.xbrl.org/2003/instance"
SUPPORTED_FORMATS = {"num-dot-decimal", "numdotdecimal", "fixed-zero", "zerodash", "num-comma-decimal"}


def _ix_value(el) -> Decimal:
    fmt = (el.get("format") or "").split(":")[-1]
    text = "".join(el.itertext()).strip()
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


def parse_ixbrl(path: Path) -> tuple[dict, dict, list]:
    """Contextes, unités et faits numériques d'un document XBRL en ligne (XHTML bien formé)."""
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
                                 "entity": (ident.text or "").strip(), "segment": has_segment}
    for u in root.iter(f"{{{XBRLI}}}unit"):
        measures = [m.text.strip() for m in u.iter(f"{{{XBRLI}}}measure")]
        units[u.get("id")] = measures[0].split(":")[-1] if len(measures) == 1 else "/".join(measures)
    facts = []
    for el in root.iter(f"{{{IX}}}nonFraction"):
        name = el.get("name", "")
        facts.append({"name": name, "context": el.get("contextRef"), "unit": units.get(el.get("unitRef"), ""),
                      "decimals": el.get("decimals") or "", "id": el.get("id") or "", "el": el,
                      "text": "".join(el.itertext()).strip(), "scale": el.get("scale") or "0"})
    return contexts, units, facts


def reconcile_ixbrl(audit: Path, doc_id: str, raw: Path, rules_path: Path) -> dict:
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
    contexts, _, ixfacts = parse_ixbrl(path)
    cik = int(doc["issuer_id"])
    proof = f"fichier:{doc['local_copy']}#sha256={sha}"
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
            try:
                if int(ctx["entity"]) != cik:
                    continue
            except ValueError:
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
        if reason:
            report["echecs"].append(f"{fid} : {reason}")
            failures[fid] = reason
            continue
        value = next(iter(values))
        m = matches[0]
        rule = by_rule[prop["regle"]]
        _map_concept(s, rule, raw, doc["issuer_id"], rules["version"])
        decs = {x["decimals"] for x in matches}
        s.set("facts", fid, "source_context", m["context"], proof, "identifiant du contexte XBRL du document")
        s.set("facts", fid, "source_dimensions", "", proof, "établi par le document : contexte sans segment")
        if len(decs) == 1 and m["decimals"]:
            s.set("facts", fid, "decimals", m["decimals"], proof, "attribut decimals du document")
        s.set("facts", fid, "normalized_concept", rule["normalized_concept"], proof, rule["id"])
        s.set("facts", fid, "transformation", "aucune", proof, "valeur reprise telle quelle")
        s.set("facts", fid, "value", prop["raw_value"], proof, "valeur reprise telle quelle")
        s.set("facts", fid, "normalization_justification",
              f"Règle {rule['id']} ({tag}) : {rule['source_concept']} [{rule['source_unit']}, {rule['period_type']}] "
              f"-> {rule['normalized_concept']} ; valeur reprise telle quelle ; contexte {m['context']} sans segment "
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
    i.add_argument("--raw", type=Path)
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
        elif a.cmd == "import-filing":
            print("sha256", import_filing(a.audit, a.doc_id, a.fichier, a.retrieved_at, a.raw))
        else:
            print(json.dumps(reconcile_ixbrl(a.audit, a.doc_id, a.raw, a.regles), ensure_ascii=False, indent=1))
    except NormalizeError as exc:
        print("REFUS :", exc)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
