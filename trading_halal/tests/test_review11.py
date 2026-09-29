"""Revue n° 11 : émetteur dans la clé de sélection, reconversion complète, contrôle contre une copie retéléchargée."""
import csv
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
import test_edgar_tool as te  # noqa: E402

from halal_sim.selection import select_fact  # noqa: E402

APPLE = ROOT / "data" / "audit_edgar_apple"
APPLE_RAW = ROOT / "collecte" / "apple"


def _doc(doc_id, accepted, issuer):
    return {"doc_id": doc_id, "issuer_id": issuer, "accession_number": doc_id, "accepted_at": accepted,
            "public_available_at": ""}


def _fact(doc_id, value, currency="USD", normalized="", unit="USD"):
    return {"doc_id": doc_id, "source_concept": "c:Rev", "source_unit": unit, "raw_value": value,
            "normalized_concept": normalized, "unit": "monnaie", "currency": currency,
            "value": value if normalized else "", "period_start": "", "period_end": "2024-12-31", "reconciled": "oui"}


def _rewrite_csv(path, fn):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0])
    rows = fn(rows)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


class IssuerAndCurrencyKeyTests(unittest.TestCase):
    def test_review_case_other_issuer_is_never_returned(self):
        docs = {"A": _doc("A", "2025-01-01T10:00:00+00:00", "1"), "B": _doc("B", "2025-02-01T10:00:00+00:00", "2")}
        facts = [_fact("A", "1"), _fact("B", "999")]
        self.assertEqual(select_fact(docs, facts, "1", "c:Rev", "USD", "", "2024-12-31", date(2025, 3, 1))
                         .fact["raw_value"], "1")
        self.assertEqual(select_fact(docs, facts, "2", "c:Rev", "USD", "", "2024-12-31", date(2025, 3, 1))
                         .fact["raw_value"], "999")
        self.assertIsNone(select_fact(docs, facts, "3", "c:Rev", "USD", "", "2024-12-31", date(2025, 3, 1)).fact)
        with self.assertRaises(ValueError):
            select_fact(docs, facts, "", "c:Rev", "USD", "", "2024-12-31", date(2025, 3, 1))

    def test_normalized_monetary_fact_requires_matching_currency(self):
        docs = {"A": _doc("A", "2025-01-01T10:00:00+00:00", "1"), "B": _doc("B", "2025-02-01T10:00:00+00:00", "1")}
        facts = [_fact("A", "10", "USD", "total_revenue"), _fact("B", "9", "EUR", "total_revenue")]
        args = (docs, facts, "1", "total_revenue", "monnaie", "", "2024-12-31", date(2025, 3, 1))
        with self.assertRaises(ValueError):
            select_fact(*args, concept_field="normalized_concept")
        self.assertEqual(select_fact(*args, concept_field="normalized_concept", currency="USD").fact["value"], "10")
        self.assertEqual(select_fact(*args, concept_field="normalized_concept", currency="EUR").fact["value"], "9")

    def test_original_value_is_kept_next_to_the_revised_one(self):
        docs = {"A": _doc("A", "2025-01-01T10:00:00+00:00", "1"), "B": _doc("B", "2025-06-01T10:00:00+00:00", "1")}
        facts = [_fact("A", "100"), _fact("B", "105")]
        early = select_fact(docs, facts, "1", "c:Rev", "USD", "", "2024-12-31", date(2025, 3, 1))
        late = select_fact(docs, facts, "1", "c:Rev", "USD", "", "2024-12-31", date(2025, 7, 1))
        self.assertEqual((early.fact["raw_value"], early.original["raw_value"]), ("100", "100"))
        self.assertEqual((late.fact["raw_value"], late.original["raw_value"]), ("105", "100"))


class ReconversionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        h = te.EdgarToolTests()
        h.tmp = self.tmp
        self.raw = h._raw()
        self.out = self.tmp / "audit"
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})

    def test_clean_conversion_has_no_difference(self):
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])

    def test_review_case_moved_acceptance_date_is_detected(self):
        def earlier(rows):
            rows[0]["accepted_at"] = "2000-01-01T00:00:00+00:00"
            return rows
        _rewrite_csv(self.out / "documents.csv", earlier)
        self.assertTrue(any("accepted_at" in m for m in ec.verify_trace(self.raw, self.out)))

    def test_changed_form_issuer_or_removed_document_is_detected(self):
        for col, val in (("doc_type", "8-K"), ("issuer_id", "0000000999"), ("period_end", "1999-12-31")):
            ec.convert(self.raw, self.out, {"10-K", "10-Q"}, replace=True)
            def change(rows, col=col, val=val):
                rows[0][col] = val
                return rows
            _rewrite_csv(self.out / "documents.csv", change)
            self.assertTrue(any(col in m for m in ec.verify_trace(self.raw, self.out)), col)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"}, replace=True)
        _rewrite_csv(self.out / "documents.csv", lambda rows: rows[1:])
        self.assertTrue(any("absente du dossier" in m for m in ec.verify_trace(self.raw, self.out)))

    def test_human_columns_without_journal_are_flagged_since_review_12(self):
        def human(rows):
            rows[0]["public_available_at"] = "2030-01-01T00:00:00+00:00"
            rows[0]["local_copy"] = "copies/x.htm"
            return rows
        _rewrite_csv(self.out / "documents.csv", human)
        def norm(rows):
            rows[0]["normalized_concept"] = "total_revenue"
            rows[0]["reconciled"] = "oui"
            return rows
        _rewrite_csv(self.out / "facts.csv", norm)
        problems = ec.verify_trace(self.raw, self.out)
        for col in ("public_available_at", "local_copy", "normalized_concept", "reconciled"):
            self.assertTrue(any(col in m and "sans saisie" in m for m in problems), col)
        self.assertFalse(any("reconversion" in m and ("public_available_at" in m or "reconciled" in m)
                             for m in problems))


class VerifySourceTests(unittest.TestCase):
    """Contrôle indépendant des empreintes locales : comparaison avec une copie retéléchargée (simulée ici)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        h = te.EdgarToolTests()
        h.tmp = self.tmp
        self.raw = h._raw()
        self.out = self.tmp / "audit"
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        self.fresh = self.tmp / "fresh"
        shutil.copytree(self.raw, self.fresh)

    def _edit_fresh(self, name, fn):
        p = self.fresh / name
        data = json.loads(p.read_text(encoding="utf-8"))
        fn(data)
        p.write_text(json.dumps(data), encoding="utf-8")

    def test_identical_copy_has_no_difference(self):
        self.assertEqual(ec.verify_source(self.raw, self.fresh, self.out), ([], []))

    def test_local_acceptance_date_differing_from_the_sec_is_detected(self):
        def earlier(rows):
            rows[0]["accepted_at"] = "2000-01-01T00:00:00+00:00"
            return rows
        _rewrite_csv(self.out / "documents.csv", earlier)
        problems, _ = ec.verify_source(self.raw, self.fresh, self.out)
        self.assertTrue(any("accepted_at" in m for m in problems))

    def test_fact_changed_at_the_source_is_detected(self):
        def change(data):
            tax = next(iter(data["facts"]))
            for body in data["facts"][tax].values():
                for items in body["units"].values():
                    for it in items:
                        it["val"] = 123456789
        self._edit_fresh("companyfacts_CIK0000000123.json", change)
        problems, _ = ec.verify_source(self.raw, self.fresh, self.out)
        self.assertTrue(problems)

    def test_filing_no_longer_in_recent_is_unverifiable_not_ok(self):
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            accn = next(csv.DictReader(f))["accession_number"]
        def drop(data):
            rec = data["filings"]["recent"]
            i = rec["accessionNumber"].index(accn)
            for k in rec:
                rec[k] = rec[k][:i] + rec[k][i + 1:]
        self._edit_fresh("submissions_CIK0000000123.json", drop)
        problems, unverifiable = ec.verify_source(self.raw, self.fresh, self.out)
        self.assertEqual(problems, [])
        self.assertTrue(any(accn in m for m in unverifiable))


@unittest.skipUnless(APPLE.exists() and APPLE_RAW.exists(), "dossier Apple absent")
class AppleReconversionTests(unittest.TestCase):
    def test_review_case_apple_10k_acceptance_moved_one_day_earlier(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        cp = tmp / "cp"
        shutil.copytree(APPLE, cp)
        def earlier(rows):
            for r in rows:
                if r["accession_number"] == "0000320193-25-000079":
                    r["accepted_at"] = "2025-10-30T10:01:26.000+00:00"
            return rows
        _rewrite_csv(cp / "documents.csv", earlier)
        self.assertTrue(any("0000320193-25-000079" in m and "accepted_at" in m for m in ec.verify_trace(APPLE_RAW, cp)))


if __name__ == "__main__":
    unittest.main()
