"""Normalisation EDGAR par règles versionnées, journal des saisies et rapprochement XBRL en ligne (hors ligne)."""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from helpers import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import edgar_collect as ec  # noqa: E402
import edgar_normalize as en  # noqa: E402

from halal_sim.audit import audit_folder  # noqa: E402
from halal_sim.selection import load_audit, select_fact  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "edgar_FICTIF"
APPLE = ROOT / "data" / "audit_edgar_apple"
APPLE_RAW = ROOT / "collecte" / "apple"
RULES_V1 = ROOT / "config" / "normalisation" / "edgar_v1.json"
K10 = "0000000123-0000000123-25-000004"


def _rules(tmp: Path, extra=()) -> Path:
    rules = {"version": "test_v1", "regles": [
        {"id": "T1", "source_concept": "us-gaap:Revenues", "normalized_concept": "total_revenue", "source_unit": "USD",
         "period_type": "duration", "justification": "Revenu total (règle de test)."},
        {"id": "T2", "source_concept": "dei:EntityCommonStockSharesOutstanding",
         "normalized_concept": "shares_outstanding", "source_unit": "shares", "period_type": "instant",
         "justification": "Actions en circulation (règle de test)."}, *extra]}
    p = tmp / "regles.json"
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
        self.mutate_raw(lambda cf: None, lambda sub: None)
        self.out = self.tmp / "audit"
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        self.rules = _rules(self.tmp)

    def mutate_raw(self, cf_fn, sub_fn):
        log = []
        for kind, fn in (("submissions", sub_fn), ("companyfacts", cf_fn)):
            name = f"{kind}_CIK0000000123.json"
            data = json.loads((FIX / name).read_text(encoding="utf-8"))
            fn(data)
            (self.raw / name).write_text(json.dumps(data), encoding="utf-8")
            log.append({"kind": kind, "cik": "0000000123", "url": f"https://data.sec.gov/{kind}", "file": name,
                        "retrieved_at": "2026-09-28T10:00:00+00:00",
                        "sha256": hashlib.sha256((self.raw / name).read_bytes()).hexdigest()})
        (self.raw / "journal_collecte.json").write_text(json.dumps(log), encoding="utf-8")

    def facts(self):
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            return {r["fact_id"]: r for r in csv.DictReader(f)}

    def normalized(self):
        return {k: r for k, r in self.facts().items() if r["normalized_concept"]}

    def import_doc(self, content=None):
        src = self.tmp / "fxei-10k.htm"
        src.write_text(content or ixbrl(GOOD), encoding="utf-8")
        return en.import_filing(self.out, K10, src, "2026-09-28T14:05:00+02:00", self.raw)


class NormalizeTests(Base):
    def test_normalizes_through_the_journal_and_passes_all_checks(self):
        rep = en.normalize(self.raw, self.out, self.rules)
        self.assertEqual(rep["normalises"], {"total_revenue": 3, "shares_outstanding": 1})
        n = self.normalized()
        for r in n.values():
            self.assertEqual(r["value"], r["raw_value"])
            self.assertEqual(r["transformation"], "aucune")
            self.assertEqual(r["source_dimensions"], "")
            self.assertTrue(r["source_context"].startswith("companyfacts;entite=CIK0000000123"))
        shares = next(r for r in n.values() if r["normalized_concept"] == "shares_outstanding")
        self.assertIn("FXEI", shares["share_class"])
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        res = audit_folder(self.out)
        self.assertEqual(res.errors, [])
        self.assertEqual(res.to_reconcile, 4)
        self.assertIn("non rapproché", res.verdict)

    def test_second_run_adds_nothing(self):
        en.normalize(self.raw, self.out, self.rules)
        before = (self.out / ec.SAISIES_FILE).read_bytes()
        self.assertEqual(en.normalize(self.raw, self.out, self.rules)["saisies"], 0)
        self.assertEqual((self.out / ec.SAISIES_FILE).read_bytes(), before)

    def test_conflicting_source_concepts_are_not_normalized(self):
        def add_conflict(cf):
            cf["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
                "label": "Rev", "description": "d", "units": {"USD": [
                    {"start": "2024-01-01", "end": "2024-12-31", "val": 1240000000, "accn": "0000000123-25-000004",
                     "form": "10-K", "filed": "2025-02-20"}]}}
        self.mutate_raw(add_conflict, lambda s: None)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"}, replace=True)
        rules = _rules(self.tmp, [{"id": "T3", "source_concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                                   "normalized_concept": "total_revenue", "source_unit": "USD",
                                   "period_type": "duration", "justification": "test"}])
        rep = en.normalize(self.raw, self.out, rules)
        self.assertEqual(len(rep["conflits"]), 1)
        self.assertFalse(any(r["period_end"] == "2024-12-31" and r["period_start"] == "2024-01-01"
                             for r in self.normalized().values()))
        excl = [r for r in self.facts().values() if r["normalization_justification"].startswith("NON NORMALISÉ")]
        # le concept mappé (Revenues) porte l'exclusion motivée ; l'autre, sans aucun fait normalisé, n'est pas mappé
        self.assertEqual([r["source_concept"] for r in excl], ["us-gaap:Revenues"])
        self.assertIn("conflit K1", excl[0]["normalization_justification"])
        self.assertEqual(audit_folder(self.out).errors, [])

    def test_several_listed_classes_block_share_normalization(self):
        self.mutate_raw(lambda cf: None, lambda s: s.update(tickers=["FXEI", "FXEI.B"]))
        ec.convert(self.raw, self.out, {"10-K", "10-Q"}, replace=True)
        rep = en.normalize(self.raw, self.out, self.rules)
        self.assertNotIn("shares_outstanding", rep["normalises"])
        self.assertTrue(any("catégorie non établie" in e for e in rep["ecartes"]))

    def test_failed_checks_write_nothing(self):
        bad = _rules(self.tmp, [])
        data = json.loads(bad.read_text(encoding="utf-8"))
        data["regles"][0]["normalized_concept"] = "concept_inexistant"
        bad.write_text(json.dumps(data), encoding="utf-8")
        snapshot = {p.name: p.read_bytes() for p in self.out.iterdir() if p.is_file()}
        with self.assertRaises(en.NormalizeError):
            en.normalize(self.raw, self.out, bad)
        self.assertEqual({p.name: p.read_bytes() for p in self.out.iterdir() if p.is_file()}, snapshot)

    def test_refuses_a_folder_that_does_not_verify(self):
        with open(self.out / "facts.csv", encoding="utf-8") as f:
            text = f.read()
        (self.out / "facts.csv").write_text(text.replace("1250000000", "1250000001", 1), encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.normalize(self.raw, self.out, self.rules)

    def test_editing_a_normalized_value_afterwards_is_detected(self):
        en.normalize(self.raw, self.out, self.rules)
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            if r["value"]:
                r["value"] = str(int(r["value"]) + 1)
                break
        with open(self.out / "facts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertTrue(any("value" in m for m in ec.verify_trace(self.raw, self.out)))


class ImportAndReconcileTests(Base):
    def setUp(self):
        super().setUp()
        en.normalize(self.raw, self.out, self.rules)

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

    def test_reconcile_matches_non_dimensional_facts_only(self):
        self.import_doc()
        rep = en.reconcile_ixbrl(self.out, K10, self.raw)
        self.assertEqual((rep["rapproches"], rep["echecs"]), (3, []))
        rec = {r["period_end"] + r["normalized_concept"]: r for r in self.normalized().values() if r["reconciled"]}
        rev = rec["2024-12-31total_revenue"]
        self.assertEqual((rev["source_context"], rev["decimals"], rev["reconciled"]), ("c-1", "-6", "auto"))
        self.assertIn("« 1,250 »", rev["reconciled_note"])
        self.assertEqual(rec["2025-02-14shares_outstanding"]["decimals"], "INF")
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        res = audit_folder(self.out)
        self.assertEqual((res.errors, res.reconciled_auto, res.to_reconcile), ([], 3, 4))
        docs, facts = load_audit(self.out)
        s = select_fact(docs, facts, "0000000123", "total_revenue", "monnaie", "2024-01-01", "2024-12-31",
                        date(2025, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertTrue(s.usable)
        self.assertEqual(s.reconciliation, "auto")
        q = select_fact(docs, facts, "0000000123", "total_revenue", "monnaie", "2024-07-01", "2024-09-30",
                        date(2025, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertFalse(q.usable)  # 10-Q non rapproché

    def test_displayed_value_mismatch_is_not_reconciled(self):
        bad = [GOOD[0][:3] + ("1,249",) + GOOD[0][4:], *GOOD[1:]]
        self.import_doc(ixbrl(bad))
        rep = en.reconcile_ixbrl(self.out, K10, self.raw)
        self.assertEqual(rep["rapproches"], 2)
        self.assertTrue(any("≠ companyfacts" in e for e in rep["echecs"]))

    def test_only_dimensional_fact_refutes_d1(self):
        self.import_doc(ixbrl([GOOD[2], GOOD[1], GOOD[3]]))
        rep = en.reconcile_ixbrl(self.out, K10, self.raw)
        self.assertTrue(any("D1 réfutée" in e for e in rep["echecs"]))

    def test_other_entity_and_negative_sign_are_handled(self):
        self.import_doc(ixbrl(GOOD, cik="0000000999"))
        self.assertEqual(en.reconcile_ixbrl(self.out, K10, self.raw)["rapproches"], 0)
        self.assertEqual(en._ix_value(__import__("xml.etree.ElementTree").etree.ElementTree.fromstring(
            '<x sign="-" scale="3" format="ixt:num-dot-decimal">1,5</x>'.replace("1,5", "1,500"))), -1500000)

    def test_tampered_local_copy_is_refused(self):
        self.import_doc()
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            doc = next(r for r in csv.DictReader(f) if r["doc_id"] == K10)
        (self.out / doc["local_copy"]).write_text(ixbrl(GOOD) + " ", encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.reconcile_ixbrl(self.out, K10, self.raw)

    def test_auto_reconciliation_needs_note_and_local_copy(self):
        self.import_doc()
        en.reconcile_ixbrl(self.out, K10, self.raw)
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            if r["reconciled"] == "auto":
                r["reconciled_note"] = "vu"
                break
        with open(self.out / "facts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertTrue(any("AUTOMATIQUE" in e for e in audit_folder(self.out).errors))


@unittest.skipUnless(APPLE.exists() and APPLE_RAW.exists(), "dossier Apple absent")
class AppleNormalizedTests(unittest.TestCase):
    """Dossier réel Apple normalisé avec edgar_v1 (valeurs vérifiables dans docs/EXEMPLE_NORMALISATION_APPLE.md)."""

    @classmethod
    def setUpClass(cls):
        cls.docs, cls.facts = load_audit(APPLE)

    def sel(self, concept, unit, start, end, day, currency=None):
        return select_fact(self.docs, self.facts, "0000320193", concept, unit, start, end,
                           date.fromisoformat(day), concept_field="normalized_concept", currency=currency)

    def test_counts_and_audit(self):
        rep = json.loads((APPLE / "rapport_normalisation.json").read_text(encoding="utf-8"))
        self.assertEqual(rep["normalises"], {"shares_outstanding": 132, "total_assets": 88, "total_revenue": 117})
        self.assertEqual(rep["conflits"], [])
        res = audit_folder(APPLE)
        self.assertEqual((res.errors, res.to_reconcile), ([], 337))

    def test_known_values(self):
        self.assertEqual(self.sel("total_revenue", "monnaie", "2024-09-29", "2025-09-27", "2025-11-01", "USD")
                         .fact["value"], "416161000000")
        self.assertEqual(self.sel("total_revenue", "monnaie", "2025-03-30", "2025-06-28", "2025-08-02", "USD")
                         .fact["value"], "94036000000")
        self.assertEqual(self.sel("shares_outstanding", "actions", "", "2025-09-27", "2025-11-01").fact["value"],
                         "14773260000")
        self.assertEqual(self.sel("shares_outstanding", "actions", "", "2025-10-17", "2025-11-01").fact["value"],
                         "14776353000")
        self.assertIsNone(self.sel("total_revenue", "monnaie", "2024-09-29", "2025-09-27", "2025-10-31", "USD").fact)

    def test_published_example_matches_the_data(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import exemple_normalisation as ex
        doc = (ROOT / "docs" / "EXEMPLE_NORMALISATION_APPLE.md").read_text(encoding="utf-8")
        for accn in ("0000320193-25-000079", "0000320193-25-000073"):
            self.assertIn(ex.table(APPLE, accn).strip(), doc)

    def test_not_usable_until_reconciled(self):
        s = self.sel("total_revenue", "monnaie", "2024-09-29", "2025-09-27", "2025-11-01", "USD")
        self.assertFalse(s.usable)

    def test_rules_file_is_the_one_applied_and_rerun_is_a_no_op(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        cp = tmp / "cp"
        shutil.copytree(APPLE, cp)
        self.assertEqual(en.normalize(APPLE_RAW, cp, RULES_V1)["saisies"], 0)


if __name__ == "__main__":
    unittest.main()
