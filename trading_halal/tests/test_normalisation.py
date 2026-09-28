"""Normalisation EDGAR en deux temps (revue n° 13) : propositions depuis companyfacts, puis normalisation et
rapprochement à partir du document XBRL en ligne. Tout hors ligne ; document FICTIF pour le rapprochement."""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from helpers import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import edgar_collect as ec  # noqa: E402
import edgar_normalize as en  # noqa: E402

from halal_sim.audit import audit_folder  # noqa: E402
from halal_sim.selection import load_audit, select_fact  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "edgar_FICTIF"
RULES_V1 = ROOT / "config" / "normalisation" / "edgar_v1.json"
RULES_V2 = ROOT / "config" / "normalisation" / "edgar_v2.json"
K10 = "0000000123-0000000123-25-000004"
Q10 = "0000000123-0000000123-24-000030"
REV = "us-gaap:Revenues"


def _rules(tmp: Path, extra=(), name="regles.json") -> Path:
    rules = {"version": "test_v2", "regles": [
        {"id": "T1", "source_concept": REV, "normalized_concept": "total_revenue", "source_unit": "USD",
         "period_type": "duration", "justification": "Revenu total (règle de test)."}, *extra]}
    p = tmp / name
    p.write_text(json.dumps(rules), encoding="utf-8")
    return p


def ixbrl(facts, cik="0000000123") -> str:
    """Document XBRL en ligne minimal mais conforme à la structure SEC (FICTIF).
    facts : (concept, contexte, unité, texte, échelle, decimals, signe) ; contextes prédéfinis ci-dessous."""
    ctx = {
        "c-1": ("2024-01-01", "2024-12-31", False), "c-2": ("2023-01-01", "2023-12-31", False),
        "c-3": ("2024-01-01", "2024-12-31", True), "c-4": ("", "2025-02-14", False),
    }
    contexts = []
    for cid, (start, end, seg) in ctx.items():
        period = (f"<xbrli:startDate>{start}</xbrli:startDate><xbrli:endDate>{end}</xbrli:endDate>" if start
                  else f"<xbrli:instant>{end}</xbrli:instant>")
        segment = ("<xbrli:segment><xbrldi:explicitMember dimension=\"srt:ProductOrServiceAxis\">fx:WidgetMember"
                   "</xbrldi:explicitMember></xbrli:segment>" if seg else "")
        contexts.append(f"<xbrli:context id=\"{cid}\"><xbrli:entity><xbrli:identifier scheme=\"http://www.sec.gov/CIK\">"
                        f"{cik}</xbrli:identifier>{segment}</xbrli:entity><xbrli:period>{period}</xbrli:period>"
                        "</xbrli:context>")
    body = []
    for i, (concept, cid, unit, text, scale, decimals, sign) in enumerate(facts):
        s = f' sign="-"' if sign else ""
        body.append(f'<p>{concept} : <ix:nonFraction id="f-{i}" name="{concept}" contextRef="{cid}" unitRef="{unit}" '
                    f'decimals="{decimals}" scale="{scale}" format="ixt:num-dot-decimal"{s}>{text}</ix:nonFraction></p>')
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" '
            'xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:xbrldi="http://xbrl.org/2006/xbrldi" '
            'xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2020-02-12" '
            'xmlns:us-gaap="http://fasb.org/us-gaap/2024" xmlns:dei="http://xbrl.sec.gov/dei/2024" '
            'xmlns:srt="http://fasb.org/srt/2024" xmlns:fx="http://exemple.invalid/fictif">'
            '<head><title>FICTIF</title></head><body><div style="display:none"><ix:header><ix:resources>'
            + "".join(contexts) +
            '<xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '<xbrli:unit id="shares"><xbrli:measure>xbrli:shares</xbrli:measure></xbrli:unit>'
            '</ix:resources></ix:header></div>' + "".join(body) + "</body></html>")


GOOD = [("us-gaap:Revenues", "c-1", "usd", "1,250", "6", "-6", False),
        ("us-gaap:Revenues", "c-2", "usd", "1,100", "6", "-6", False),
        ("us-gaap:Revenues", "c-3", "usd", "800", "6", "-6", False),          # ventilé : ignoré
        ("dei:EntityCommonStockSharesOutstanding", "c-4", "shares", "48,000,000", "0", "INF", False)]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.raw = self.tmp / "raw"
        self.raw.mkdir()
        self.mutate_raw(lambda cf: None)
        self.out = self.tmp / "audit"
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        self.rules = _rules(self.tmp)

    def mutate_raw(self, cf_fn):
        log = []
        for kind in ("submissions", "companyfacts"):
            name = f"{kind}_CIK0000000123.json"
            data = json.loads((FIX / name).read_text(encoding="utf-8"))
            if kind == "companyfacts":
                cf_fn(data)
            (self.raw / name).write_text(json.dumps(data), encoding="utf-8")
            log.append({"kind": kind, "cik": "0000000123", "url": f"https://data.sec.gov/{kind}", "file": name,
                        "retrieved_at": "2026-09-28T10:00:00+00:00",
                        "sha256": hashlib.sha256((self.raw / name).read_bytes()).hexdigest()})
        (self.raw / "journal_collecte.json").write_text(json.dumps(log), encoding="utf-8")

    def facts(self):
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            return {r["fact_id"]: r for r in csv.DictReader(f)}

    def fact(self, doc, end, start=""):
        return next(r for r in self.facts().values() if r["doc_id"] == doc and r["source_concept"] == REV
                    and r["period_end"] == end and (not start or r["period_start"] == start))

    def import_doc(self, content=None):
        src = self.tmp / "fxei-10k.htm"
        src.write_text(content or ixbrl(GOOD), encoding="utf-8")
        return en.import_filing(self.out, K10, src, "2026-09-28T14:05:00+02:00", self.raw)

    def reconcile(self, content=None):
        en.normalize(self.raw, self.out, self.rules)
        self.import_doc(content)
        return en.reconcile_ixbrl(self.out, K10, self.raw, self.rules)


class ProposalTests(Base):
    def test_normalize_only_proposes(self):
        before = (self.out / "facts.csv").read_bytes()
        rep = en.normalize(self.raw, self.out, self.rules)
        self.assertEqual(rep["propositions"], {"total_revenue": 3})
        self.assertEqual((self.out / "facts.csv").read_bytes(), before)
        self.assertFalse((self.out / ec.SAISIES_FILE).exists())
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        self.assertIn("aucun fait normalisé", audit_folder(self.out).verdict)
        with open(self.out / en.PROPOSALS_FILE, newline="", encoding="utf-8") as f:
            props = list(csv.DictReader(f))
        self.assertEqual({p["period_end"] for p in props}, {"2024-12-31", "2023-12-31", "2024-09-30"})

    def test_second_run_is_identical(self):
        en.normalize(self.raw, self.out, self.rules)
        first = (self.out / en.PROPOSALS_FILE).read_bytes()
        en.normalize(self.raw, self.out, self.rules)
        self.assertEqual((self.out / en.PROPOSALS_FILE).read_bytes(), first)

    def test_share_rules_are_refused(self):
        shares = _rules(self.tmp, [{"id": "T2", "source_concept": "dei:EntityCommonStockSharesOutstanding",
                                    "normalized_concept": "shares_outstanding", "source_unit": "shares",
                                    "period_type": "instant", "justification": "x"}], "actions.json")
        for rules in (shares, RULES_V1):
            with self.assertRaises(en.NormalizeError):
                en.normalize(self.raw, self.out, rules)

    def test_conflicting_source_concepts_are_not_proposed(self):
        def add_conflict(cf):
            cf["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
                "label": "Rev", "description": "d", "units": {"USD": [
                    {"start": "2024-01-01", "end": "2024-12-31", "val": 1240000000, "accn": "0000000123-25-000004",
                     "form": "10-K", "filed": "2025-02-20"}]}}
        self.mutate_raw(add_conflict)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"}, replace=True)
        rules = _rules(self.tmp, [{"id": "T3", "source_concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                                   "normalized_concept": "total_revenue", "source_unit": "USD",
                                   "period_type": "duration", "justification": "test"}], "conflit.json")
        rep = en.normalize(self.raw, self.out, rules)
        self.assertEqual(len(rep["conflits"]), 1)
        self.assertEqual(rep["propositions"], {"total_revenue": 2})

    def test_refuses_a_folder_that_does_not_verify(self):
        text = (self.out / "facts.csv").read_text(encoding="utf-8")
        (self.out / "facts.csv").write_text(text.replace("1250000000", "1250000001", 1), encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.normalize(self.raw, self.out, self.rules)


class ReconcileTests(Base):
    def test_import_filing_checks_name_and_timezone(self):
        wrong = self.tmp / "autre.htm"
        wrong.write_text("x", encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.import_filing(self.out, K10, wrong, "2026-09-28T14:05:00+02:00", self.raw)
        with self.assertRaises(en.NormalizeError):
            en.import_filing(self.out, K10, self.tmp / "fxei-10k.htm", "2026-09-28T14:05:00", self.raw)
        sha = self.import_doc()
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            doc = next(r for r in csv.DictReader(f) if r["doc_id"] == K10)
        self.assertEqual(doc["local_sha256"], sha)
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])

    def test_document_establishes_context_and_dimensions(self):
        rep = self.reconcile()
        self.assertEqual((rep["rapproches"], rep["echecs"]), (2, []))
        f24 = self.fact(K10, "2024-12-31")
        self.assertEqual((f24["normalized_concept"], f24["value"], f24["source_context"], f24["source_dimensions"],
                          f24["decimals"], f24["reconciled"]),
                         ("total_revenue", "1250000000", "c-1", "", "-6", "auto"))
        self.assertIn("« 1,250 »", f24["reconciled_note"])
        q = self.fact(Q10, "2024-09-30")
        self.assertEqual(q["normalized_concept"], "")
        self.assertTrue(q["normalization_justification"].startswith("NON NORMALISÉ : en attente"))
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        res = audit_folder(self.out)
        self.assertEqual((res.errors, res.reconciled_auto, res.to_reconcile), ([], 2, 2))
        self.assertIn("RAPPROCHEMENT AUTOMATIQUE", res.verdict)
        docs, facts = load_audit(self.out)
        s = select_fact(docs, facts, "0000000123", "total_revenue", "monnaie", "2024-01-01", "2024-12-31",
                        date(2025, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertTrue(s.usable)
        self.assertEqual(s.reconciliation, "auto")

    def test_value_mismatch_is_not_normalized(self):
        bad = [GOOD[0][:3] + ("1,249",) + GOOD[0][4:], *GOOD[1:]]
        rep = self.reconcile(ixbrl(bad))
        self.assertEqual(rep["rapproches"], 1)
        f24 = self.fact(K10, "2024-12-31")
        self.assertEqual(f24["normalized_concept"], "")
        self.assertIn("≠ companyfacts", f24["normalization_justification"])
        self.assertEqual(audit_folder(self.out).errors, [])

    def test_only_dimensional_fact_is_not_normalized(self):
        rep = self.reconcile(ixbrl([GOOD[2], GOOD[1], GOOD[3]]))
        self.assertEqual(rep["rapproches"], 1)
        self.assertIn("ventilé", self.fact(K10, "2024-12-31")["normalization_justification"])

    def test_other_entity_normalizes_nothing(self):
        rep = self.reconcile(ixbrl(GOOD, cik="0000000999"))
        self.assertEqual(rep["rapproches"], 0)
        self.assertFalse(any(r["normalized_concept"] for r in self.facts().values()))

    def test_sign_and_scale(self):
        el = ET.fromstring('<x sign="-" scale="3" format="ixt:num-dot-decimal">1,500</x>')
        self.assertEqual(en._ix_value(el), -1500000)
        with self.assertRaises(ValueError):
            en._ix_value(ET.fromstring('<x format="ixt-sec:numwordsen">five</x>'))

    def test_tampered_local_copy_is_refused(self):
        en.normalize(self.raw, self.out, self.rules)
        self.import_doc()
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            doc = next(r for r in csv.DictReader(f) if r["doc_id"] == K10)
        (self.out / doc["local_copy"]).write_text(ixbrl(GOOD) + " ", encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "empreinte différente de local_sha256"):
            en.reconcile_ixbrl(self.out, K10, self.raw, self.rules)

    def test_failed_checks_write_nothing(self):
        bad = _rules(self.tmp, name="mauvaises.json")
        data = json.loads(bad.read_text(encoding="utf-8"))
        data["regles"][0]["normalized_concept"] = "concept_inexistant"
        bad.write_text(json.dumps(data), encoding="utf-8")
        en.normalize(self.raw, self.out, bad)
        self.import_doc()
        snapshot = {p.name: p.read_bytes() for p in self.out.iterdir() if p.is_file()}
        with self.assertRaises(en.NormalizeError):
            en.reconcile_ixbrl(self.out, K10, self.raw, bad)
        self.assertEqual({p.name: p.read_bytes() for p in self.out.iterdir() if p.is_file()}, snapshot)

    def test_auto_reconciliation_needs_note(self):
        self.reconcile()
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        next(r for r in rows if r["reconciled"] == "auto")["reconciled_note"] = "vu"
        with open(self.out / "facts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertTrue(any("AUTOMATIQUE" in e for e in audit_folder(self.out).errors))


def _forge(audit: Path, table: str, key: str, col: str, value: str, author: str, proof: str) -> None:
    """Falsification « cohérente » : cellule modifiée ET saisie journalisée qui la justifie (passe verify-trace)."""
    with open(audit / f"{table}.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0]) if rows else None
    k = ec.ROW_KEYS[table]
    target = next(r for r in rows if "|".join(r[c] for c in k) == key)
    old = target[col]
    target[col] = value
    with open(audit / f"{table}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    journal = en._load_journal(audit)
    journal.append({"n": str(len(journal) + 1), "fichier": table, "cle": key, "colonne": col, "ancienne_valeur": old,
                    "nouvelle_valeur": value, "auteur": author, "saisi_le": journal[-1]["saisi_le"], "preuve": proof,
                    "note": ""})
    with open(audit / ec.SAISIES_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ec.SAISIES_HEADERS)
        w.writeheader()
        w.writerows(journal)


class VerifyNormalisationTests(Base):
    def setUp(self):
        super().setUp()
        self.reconcile()
        self.author = f"{en.TOOL} reconcile-ixbrl ({en.rules_tag(self.rules)}, automatique)"
        self.f24 = self.fact(K10, "2024-12-31")["fact_id"]
        self.q = self.fact(Q10, "2024-09-30")["fact_id"]

    def test_clean_folder_verifies(self):
        self.assertEqual(en.verify_normalisation(self.raw, self.out, self.rules), ([], []))

    def test_forged_concept_attributed_to_the_tool_is_detected(self):
        _forge(self.out, "facts", self.f24, "normalized_concept", "total_assets", self.author, "doc:" + K10)
        _forge(self.out, "concept_map", REV, "normalized_concept", "total_assets", self.author,
               "url:https://data.sec.gov/companyfacts")
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])  # la forme et l'historique sont cohérents…
        problems, human = en.verify_normalisation(self.raw, self.out, self.rules)  # …pas le fond
        self.assertTrue(any("normalized_concept" in m and "total_assets" in m for m in problems))
        self.assertEqual(human, [])

    def test_forged_normalization_of_a_fact_without_document_is_detected(self):
        for col, val in (("normalized_concept", "total_revenue"), ("transformation", "aucune"),
                         ("value", "300000000"), ("source_context", "c-9"), ("source_dimensions", ""),
                         ("normalization_justification", "Règle T1")):
            _forge(self.out, "facts", self.q, col, val, self.author, "doc:" + Q10)
        problems, _ = en.verify_normalisation(self.raw, self.out, self.rules)
        self.assertTrue(any(self.q in m and "normalized_concept" in m for m in problems))

    def test_human_override_is_listed_not_hidden(self):
        _forge(self.out, "facts", self.f24, "normalization_justification", "Revu à la main : identique, page 3",
               "Relecteur B", "doc:" + K10)
        problems, human = en.verify_normalisation(self.raw, self.out, self.rules)
        self.assertEqual(problems, [])
        self.assertTrue(any("Relecteur B" in m for m in human))

    def test_other_rules_file_is_detected(self):
        other = self.tmp / "autres.json"
        data = json.loads(self.rules.read_text(encoding="utf-8"))
        data["regles"][0]["justification"] = "texte modifié"
        other.write_text(json.dumps(data), encoding="utf-8")
        problems, _ = en.verify_normalisation(self.raw, self.out, other)
        self.assertTrue(any("autres règles" in m for m in problems))

    def test_tampered_proposals_file_is_detected(self):
        p = self.out / en.PROPOSALS_FILE
        p.write_text(p.read_text(encoding="utf-8").replace("total_revenue", "total_assets", 1), encoding="utf-8")
        problems, _ = en.verify_normalisation(self.raw, self.out, self.rules)
        self.assertTrue(any(en.PROPOSALS_FILE in m for m in problems))


REAL = {"apple": ("0000320193", {"total_assets": 88, "total_revenue": 117}),
        "microsoft": ("0000789019", {"total_assets": 48, "total_revenue": 78}),
        "alphabet": ("0001652044", {"total_assets": 26, "total_revenue": 26})}
REVENUE = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"


class RealIssuersTests(unittest.TestCase):
    """Dossiers réels : propositions seulement (documents inaccessibles d'ici), contrôles à 0."""

    def paths(self, name):
        audit, raw = ROOT / "data" / f"audit_edgar_{name}", ROOT / "collecte" / name
        if not (audit.exists() and raw.exists()):
            self.skipTest(f"dossier {name} absent")
        return audit, raw

    def sel(self, name, start, end, day):
        audit, _ = self.paths(name)
        docs, facts = load_audit(audit)
        return docs, select_fact(docs, facts, REAL[name][0], REVENUE, "USD", start, end, date.fromisoformat(day))

    def test_proposals_only_and_all_checks_clean(self):
        for name, (_, counts) in REAL.items():
            with self.subTest(name):
                audit, raw = self.paths(name)
                rep = json.loads((audit / "rapport_normalisation.json").read_text(encoding="utf-8"))
                self.assertEqual((rep["propositions"], rep["conflits"]), (counts, []))
                self.assertEqual(rep["regles_sha256"], en._sha(RULES_V2))
                docs, facts = load_audit(audit)
                self.assertFalse(any(f["normalized_concept"] for f in facts))
                self.assertEqual(ec.verify_trace(raw, audit), [])
                self.assertEqual(en.verify_normalisation(raw, audit, RULES_V2), ([], []))
                res = audit_folder(audit)
                self.assertEqual(res.errors, [])
                self.assertIn("aucun fait normalisé", res.verdict)

    def test_known_values(self):
        for name, start, end, day, value in (
                ("apple", "2024-09-29", "2025-09-27", "2025-11-01", "416161000000"),
                ("apple", "2025-03-30", "2025-06-28", "2025-08-02", "94036000000"),
                ("microsoft", "2024-07-01", "2025-06-30", "2026-01-01", "281724000000"),
                ("alphabet", "2024-01-01", "2024-12-31", "2025-03-01", "350018000000")):
            with self.subTest(name=name, end=end):
                self.assertEqual(self.sel(name, start, end, day)[1].fact["raw_value"], value)

    def test_later_comparative_never_replaces_the_filing_available_at_the_decision(self):
        docs, before = self.sel("microsoft", "2024-07-01", "2025-06-30", "2025-12-01")
        _, after = self.sel("microsoft", "2024-07-01", "2025-06-30", "2026-09-01")
        self.assertTrue(docs[before.fact["doc_id"]]["accepted_at"].startswith("2025"))
        self.assertTrue(docs[after.fact["doc_id"]]["accepted_at"].startswith("2026"))
        self.assertEqual(after.original["doc_id"], before.fact["doc_id"])
        self.assertEqual((after.fact["raw_value"], after.revised_values), (before.fact["raw_value"], []))

    def test_published_examples_match_the_data(self):
        import exemple_normalisation as ex
        doc = (ROOT / "docs" / "EXEMPLE_NORMALISATION.md").read_text(encoding="utf-8")
        for name, accn in (("apple", "0000320193-25-000079"), ("apple", "0000320193-25-000073"),
                           ("microsoft", "0001193125-26-323660"), ("alphabet", "0001652044-26-000018")):
            audit, _ = self.paths(name)
            self.assertIn(ex.table(audit, accn).strip(), doc)


if __name__ == "__main__":
    unittest.main()
