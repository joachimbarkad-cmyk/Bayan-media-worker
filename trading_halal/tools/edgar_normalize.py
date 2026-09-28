"""Normalisation de faits EDGAR (companyfacts) selon des règles versionnées, HORS LIGNE, par le journal des saisies.

Aucune cellule n'est modifiée directement : chaque changement devient une entrée de `journal_saisies.csv`
(auteur = cet outil, preuve = document ou URL de la source), puis les fichiers sont réécrits, et le dossier doit
repasser `verify-trace` (reconversion + rejeu du journal) et `audit-docs` sans erreur, sinon rien n'est écrit.

Usage :
  python3 tools/edgar_normalize.py normalize --raw collecte/apple --audit data/audit_edgar_apple \
      --regles config/normalisation/edgar_v1.json
  python3 tools/edgar_normalize.py import-filing --audit DOSSIER --doc-id DOC --fichier aapl-20250927.htm \
      --retrieved-at 2026-09-28T14:05:00+02:00
  python3 tools/edgar_normalize.py reconcile-ixbrl --audit DOSSIER --doc-id DOC

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
from decimal import Decimal, InvalidOperation
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


# ----------------------------------------------------------------------------------------------- normalisation
def _submissions(raw: Path, cik: str) -> dict:
    log = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
    e = next((e for e in log if e["kind"] == "submissions" and e["cik"] == cik), None)
    if e is None:
        raise NormalizeError(f"submissions de {cik} absent de {raw}")
    return json.loads((raw / e["file"]).read_text(encoding="utf-8")), e


def normalize(raw: Path, audit: Path, rules_path: Path) -> dict:
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    version = rules["version"]
    before = ec.verify_trace(raw, audit)
    if before:
        raise NormalizeError("le dossier ne passe pas verify-trace avant normalisation :\n  " + "\n  ".join(before[:10]))
    s = Session(audit, f"{TOOL} (règles {version}, automatique)")
    with open(audit / ec.TRACE_FILE, newline="", encoding="utf-8") as f:
        trace = {r["fact_id"]: r for r in csv.DictReader(f)}
    raw_cache: dict[str, dict] = {}

    def raw_entries(name):
        if name not in raw_cache:
            raw_cache[name] = json.loads((raw / name).read_text(encoding="utf-8"))
        return raw_cache[name]

    by_concept = {r["source_concept"]: r for r in rules["regles"]}
    docs = s.index["documents"]
    report = {"version": version, "normalises": defaultdict(int), "ecartes": [], "conflits": []}
    candidates, excluded = [], {}
    for fact in s.tables["facts"]:
        rule = by_concept.get(fact["source_concept"])
        if rule is None:
            continue
        fid = fact["fact_id"]
        if fact["source_unit"] != rule["source_unit"] or fact["period_type"] != rule["period_type"]:
            report["ecartes"].append(f"{fid} : unité ou type de période hors règle {rule['id']}")
            excluded[fid] = f"unité ou type de période hors règle {rule['id']}"
            continue
        t = trace.get(fid)
        if t is None:
            report["ecartes"].append(f"{fid} : sans trace brute")
            excluded[fid] = "sans trace brute"
            continue
        # D1 : une seule valeur brute pour ce concept, cette unité, cette période et ce dépôt
        tax, concept, unit, _ = ec.parse_pointer(t["source_pointer"])
        items = raw_entries(Path(t["source_file"]).name)["facts"][tax][concept]["units"][unit]
        accn = docs[fact["doc_id"]]["accession_number"]
        same = {json.dumps(it.get("val")) for it in items
                if it.get("accn") == accn and it.get("start", "") == fact["period_start"] and it.get("end") ==
                fact["period_end"]}
        if len(same) != 1:
            report["ecartes"].append(f"{fid} : {len(same)} valeurs brutes pour la même clé (dimensions probables)")
            excluded[fid] = f"D1 non satisfaite ({len(same)} valeurs brutes pour la même clé)"
            continue
        candidates.append((rule, fact, t))
    # K1 : conflits entre concepts d'origine normalisés vers le même concept
    groups = defaultdict(list)
    for rule, fact, t in candidates:
        groups[(fact["doc_id"], rule["normalized_concept"], fact["period_start"], fact["period_end"])].append(
            (rule, fact, t))
    tickers_cache: dict[str, list] = {}
    for key, members in groups.items():
        if len({m[1]["raw_value"] for m in members}) > 1:
            detail = ", ".join(f"{m[1]['source_concept']}={m[1]['raw_value']}" for m in members)
            report["conflits"].append(f"{key} : {detail}")
            for m in members:
                excluded[m[1]["fact_id"]] = f"conflit K1 ({detail})"
            continue
        for rule, fact, t in members:
            fid = fact["fact_id"]
            issuer = docs[fact["doc_id"]]["issuer_id"]
            share_class = ""
            if rule["normalized_concept"] == "shares_outstanding":
                if issuer not in tickers_cache:
                    tickers_cache[issuer] = _submissions(raw, issuer)[0].get("tickers") or []
                tk = tickers_cache[issuer]
                if len(tk) != 1:
                    report["ecartes"].append(f"{fid} : {len(tk)} titre(s) coté(s) {tk} : catégorie non établie (C1)")
                    excluded[fid] = f"catégorie d'actions non établie (C1 : {len(tk)} titre(s) coté(s))"
                    continue
                share_class = f"ordinaire (déduit C1 : titre coté unique {tk[0]})"
            _map_concept(s, rule, raw, issuer, version)
            proof = f"doc:{fact['doc_id']}"
            period = (f"{fact['period_start']}/{fact['period_end']}" if fact["period_start"]
                      else fact["period_end"])
            s.set("facts", fid, "source_context",
                  f"companyfacts;entite=CIK{issuer};periode={period};segment=aucun(deduit D1)", proof, "X1")
            s.set("facts", fid, "source_dimensions", "", proof, "D1 : une seule valeur brute pour cette clé")
            if share_class:
                s.set("facts", fid, "share_class", share_class, proof, "C1")
            s.set("facts", fid, "normalized_concept", rule["normalized_concept"], proof, rule["id"])
            s.set("facts", fid, "transformation", "aucune", proof, "T1")
            s.set("facts", fid, "value", fact["raw_value"], proof, "T1")
            s.set("facts", fid, "normalization_justification",
                  f"Règle {rule['id']} ({version}) : {rule['source_concept']} [{rule['source_unit']}, "
                  f"{rule['period_type']}] -> {rule['normalized_concept']}. Valeur reprise telle quelle (T1). "
                  f"Dimensions : aucune, déduit (D1). Entrée brute {t['source_pointer']} "
                  f"(sha256 {t['entry_sha256'][:16]}…). À confirmer sur l'instance XBRL.", proof, rule["id"])
            report["normalises"][rule["normalized_concept"]] += 1
    # Exclusion explicite de tout fait dont le concept est mappé mais qui n'a pas été normalisé.
    for fact in s.tables["facts"]:
        if fact["normalized_concept"] or not s.cell("concept_map", fact["source_concept"], "normalized_concept"):
            continue
        reason = excluded.get(fact["fact_id"], "hors règles")
        s.set("facts", fact["fact_id"], "normalization_justification", f"{EXCLUSION_PREFIX} {reason} ({version})",
              f"doc:{fact['doc_id']}", "exclusion explicite")
    s.commit(raw)
    report["saisies"] = len(s.new)
    report["normalises"] = dict(report["normalises"])
    (audit / "rapport_normalisation.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8")
    return report


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


def reconcile_ixbrl(audit: Path, doc_id: str, raw: Path | None = None) -> dict:
    """Rapproche chaque fait normalisé du document de sa copie locale XBRL en ligne (automatique, reconciled=auto)."""
    s = Session(audit, f"{TOOL} reconcile-ixbrl (automatique)")
    doc = s.index["documents"].get(doc_id)
    if doc is None or not doc["local_copy"]:
        raise NormalizeError(f"{doc_id} : aucune copie locale (utiliser import-filing)")
    path = audit / doc["local_copy"]
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != doc["local_sha256"]:
        raise NormalizeError(f"{doc['local_copy']} : empreinte différente de local_sha256")
    contexts, _, ixfacts = parse_ixbrl(path)
    cik = int(doc["issuer_id"])
    proof = f"fichier:{doc['local_copy']}#sha256={sha}"
    report = {"rapproches": 0, "echecs": []}
    for fact in s.tables["facts"]:
        if fact["doc_id"] != doc_id or not fact["normalized_concept"] or fact["reconciled"]:
            continue
        fid = fact["fact_id"]
        unit = "shares" if fact["source_unit"] == "shares" else fact["source_unit"]
        matches, refuted = [], []
        for f in ixfacts:
            ctx = contexts.get(f["context"])
            if f["name"] != fact["source_concept"] or ctx is None or f["unit"] != unit:
                continue
            if (ctx["start"], ctx["end"]) != (fact["period_start"], fact["period_end"]):
                continue
            try:
                entity_ok = int(ctx["entity"]) == cik
            except ValueError:
                entity_ok = False
            if not entity_ok:
                continue
            (refuted if ctx["segment"] else matches).append(f)
        if not matches:
            report["echecs"].append(f"{fid} : aucun fait sans segment dans le document"
                                    + (f" ({len(refuted)} fait(s) avec segment : D1 réfutée)" if refuted else ""))
            continue
        try:
            values = {_ix_value(m["el"]) for m in matches}
        except ValueError as exc:
            report["echecs"].append(f"{fid} : {exc}")
            continue
        if len(values) != 1:
            report["echecs"].append(f"{fid} : valeurs affichées incohérentes {sorted(map(str, values))}")
            continue
        (value,) = values
        if value != Decimal(fact["raw_value"]):
            report["echecs"].append(f"{fid} : document {value} ≠ companyfacts {fact['raw_value']}")
            continue
        decs = {m["decimals"] for m in matches}
        m = matches[0]
        s.set("facts", fid, "source_context", m["context"], proof, "identifiant du contexte XBRL (remplace X1)")
        if len(decs) == 1 and m["decimals"]:
            s.set("facts", fid, "decimals", m["decimals"], proof, "attribut decimals du document")
        s.set("facts", fid, "reconciled", "auto", proof, "rapprochement automatique XBRL en ligne")
        s.set("facts", fid, "reconciled_note",
              f"AUTOMATIQUE : {doc['local_copy']} (sha256 {sha[:16]}…), {len(matches)} élément(s) ix:nonFraction "
              f"{m['name']} contexte {m['context']} sans segment, id {m['id'] or '?'}, affiché « {m['text']} », "
              f"échelle {m['scale']} = {value} ; à relire par une personne.", proof, "")
        report["rapproches"] += 1
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
    r.add_argument("--raw", type=Path)
    a = p.parse_args(argv)
    try:
        if a.cmd == "normalize":
            res = normalize(a.raw, a.audit, a.regles)
            print(json.dumps({k: (v if k != "ecartes" else len(v)) for k, v in res.items()}, ensure_ascii=False,
                             indent=1))
        elif a.cmd == "import-filing":
            print("sha256", import_filing(a.audit, a.doc_id, a.fichier, a.retrieved_at, a.raw))
        else:
            print(json.dumps(reconcile_ixbrl(a.audit, a.doc_id, a.raw), ensure_ascii=False, indent=1))
    except NormalizeError as exc:
        print("REFUS :", exc)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
