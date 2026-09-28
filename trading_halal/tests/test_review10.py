"""Revue n° 10 : exclusions tracées par dépôt, trace de chaque fait vers son entrée brute, sélection point dans le temps."""
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

from halal_sim.selection import available_from, load_audit, select_fact  # noqa: E402

APPLE = ROOT / "data" / "audit_edgar_apple"
APPLE_RAW = ROOT / "collecte" / "apple"
REV = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"


def _doc(doc_id, accepted, version="original", amends="", public=""):
    return {"doc_id": doc_id, "accession_number": doc_id, "accepted_at": accepted, "public_available_at": public,
            "version": version, "amends_doc_id": amends}


def _fact(doc_id, value, start, end, *, concept="c:Revenue", unit="USD", normalized="", reconciled=""):
    return {"doc_id": doc_id, "source_concept": concept, "source_unit": unit, "raw_value": value,
            "normalized_concept": normalized, "unit": "monnaie", "value": value if normalized else "",
            "period_start": start, "period_end": end, "reconciled": reconciled}


class PointInTimeSelectionTests(unittest.TestCase):
    """Cas fictifs : original, comparatif repris l'année suivante, rectificatif, trimestre contre cumul."""

    docs = {
        "K24": _doc("K24", "2024-11-01T10:01:36+00:00"),
        "K24A": _doc("K24A", "2025-02-10T21:30:00+00:00", "rectificatif", "K24"),
        "K25": _doc("K25", "2025-10-31T10:01:26+00:00"),
        "Q3": _doc("Q3", "2025-08-01T10:00:42+00:00"),
        "LATE": _doc("LATE", "2025-03-03T02:30:00+00:00"),       # 21 h 30 à New York le 2 mars
        "NOACC": _doc("NOACC", ""),
    }
    facts = [
        _fact("K24", "100", "2023-10-01", "2024-09-28"),
        _fact("K24A", "102", "2023-10-01", "2024-09-28"),         # rectificatif
        _fact("K25", "105", "2023-10-01", "2024-09-28"),          # comparatif retraité dans le dépôt suivant
        _fact("Q3", "94", "2025-03-30", "2025-06-28"),            # trimestre
        _fact("Q3", "313", "2024-09-29", "2025-06-28"),           # cumul de neuf mois, même date de fin
        _fact("NOACC", "7", "2022-10-01", "2023-09-30"),
    ]

    def sel(self, day, start="2023-10-01", end="2024-09-28"):
        return select_fact(self.docs, self.facts, "c:Revenue", "USD", start, end, date.fromisoformat(day))

    def test_nothing_before_or_on_the_filing_day(self):
        self.assertIsNone(self.sel("2024-10-31").fact)
        s = self.sel("2024-11-01")  # jour J : pas encore utilisable
        self.assertIsNone(s.fact)
        self.assertEqual(len(s.not_yet_available), 3)

    def test_original_then_amendment_then_later_comparative(self):
        self.assertEqual(self.sel("2024-11-02").fact["raw_value"], "100")
        s = self.sel("2025-02-11")
        self.assertEqual(s.fact["raw_value"], "102")
        self.assertEqual(s.revised_values, ["100 (K24)"])
        s = self.sel("2025-11-01")
        self.assertEqual(s.fact["raw_value"], "105")
        self.assertEqual(s.revised_values, ["100 (K24)", "102 (K24A)"])

    def test_future_filings_never_leak_into_an_earlier_decision(self):
        s = self.sel("2025-10-31")  # le 10-K 2025 est accepté ce jour-là
        self.assertEqual(s.fact["raw_value"], "102")
        self.assertTrue(all(f["doc_id"] != "K25" for f in s.candidates))

    def test_quarter_and_year_to_date_are_never_confused(self):
        self.assertEqual(self.sel("2025-08-02", "2025-03-30", "2025-06-28").fact["raw_value"], "94")
        self.assertEqual(self.sel("2025-08-02", "2024-09-29", "2025-06-28").fact["raw_value"], "313")
        self.assertIsNone(self.sel("2025-08-02", "", "2025-06-28").fact)  # un instant n'est pas une durée

    def test_acceptance_date_is_taken_in_utc_and_unknown_acceptance_is_never_usable(self):
        self.assertEqual(available_from(self.docs["LATE"]), date(2025, 3, 4))
        self.assertIsNone(self.sel("2030-01-01", "2022-10-01", "2023-09-30").fact)
        later_public = _doc("P", "2025-01-01T10:00:00+00:00", public="2025-01-05T09:00:00+00:00")
        self.assertEqual(available_from(later_public), date(2025, 1, 6))

    def test_same_day_conflict_is_ambiguous(self):
        docs = {"A": _doc("A", "2025-01-01T10:00:00+00:00"), "B": _doc("B", "2025-01-01T15:00:00+00:00")}
        facts = [_fact("A", "1", "", "2024-12-31"), _fact("B", "2", "", "2024-12-31")]
        s = select_fact(docs, facts, "c:Revenue", "USD", "", "2024-12-31", date(2025, 2, 1))
        self.assertIsNone(s.fact)
        self.assertIn("ambiguïté", s.reason)

    def test_only_normalized_and_reconciled_facts_are_usable(self):
        self.assertFalse(self.sel("2025-11-01").usable)
        docs = {"A": _doc("A", "2025-01-01T10:00:00+00:00")}
        f = _fact("A", "5", "2024-01-01", "2024-12-31", normalized="total_revenue", reconciled="oui")
        s = select_fact(docs, [f], "total_revenue", "monnaie", "2024-01-01", "2024-12-31", date(2025, 1, 2),
                        concept_field="normalized_concept")
        self.assertTrue(s.usable)


@unittest.skipUnless(APPLE.exists(), "dossier Apple absent")
class AppleRealDataTests(unittest.TestCase):
    """Sur le dossier réel Apple (lecture seule, aucune requête)."""

    @classmethod
    def setUpClass(cls):
        cls.docs, cls.facts = load_audit(APPLE)

    def sel(self, start, end, day):
        return select_fact(self.docs, self.facts, REV, "USD", start, end, date.fromisoformat(day))

    def test_fiscal_2025_revenue_only_after_the_10k(self):
        self.assertIsNone(self.sel("2024-09-29", "2025-09-27", "2025-10-31").fact)
        s = self.sel("2024-09-29", "2025-09-27", "2025-11-01")
        self.assertEqual(s.fact["raw_value"], "416161000000")
        self.assertFalse(s.usable)  # rien n'est encore normalisé ni rapproché

    def test_q3_2025_quarter_versus_nine_months(self):
        self.assertEqual(self.sel("2025-03-30", "2025-06-28", "2025-08-02").fact["raw_value"], "94036000000")
        self.assertEqual(self.sel("2024-09-29", "2025-06-28", "2025-08-02").fact["raw_value"], "313695000000")

    def test_comparative_in_later_10k_becomes_the_source(self):
        before = self.sel("2023-10-01", "2024-09-28", "2025-10-31").fact
        after = self.sel("2023-10-01", "2024-09-28", "2025-11-01")
        self.assertEqual(before["doc_id"], "0000320193-0000320193-24-000123")
        self.assertEqual(after.fact["doc_id"], "0000320193-0000320193-25-000079")
        self.assertEqual(after.revised_values, [])  # même valeur : pas de révision

    @unittest.skipUnless(APPLE_RAW.exists(), "fichiers bruts absents")
    def test_every_apple_fact_is_traced_to_its_raw_entry(self):
        self.assertEqual(ec.verify_trace(APPLE_RAW, APPLE), [])
        j = json.loads((APPLE / ec.JOURNAL_FILE).read_text(encoding="utf-8"))
        self.assertEqual(j["entrees_brutes_companyfacts"],
                         j["faits_retenus"] + len(j["doublons_identiques_fusionnes"]) + j["faits_ecartes"])
        self.assertEqual(sum(e["faits"] for e in j["exclusions_par_depot"]), j["faits_ecartes"])


class ConversionTraceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.helper = te.EdgarToolTests()
        self.helper.tmp = self.tmp

    def _convert(self, mutate=None):
        raw = self.helper._raw()
        if mutate:
            p = raw / "companyfacts_CIK0000000123.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            mutate(data)
            p.write_text(json.dumps(data), encoding="utf-8")
            log = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
            for e in log:
                e["sha256"] = ec.hashlib.sha256((raw / e["file"]).read_bytes()).hexdigest()
            (raw / "journal_collecte.json").write_text(json.dumps(log), encoding="utf-8")
        out = self.tmp / "audit"
        ec.convert(raw, out, {"10-K", "10-Q"})
        return raw, out

    def test_exclusions_are_logged_per_accession_with_reason(self):
        raw, out = self._convert()
        j = json.loads((out / ec.JOURNAL_FILE).read_text(encoding="utf-8"))
        for e in j["exclusions_par_depot"]:
            self.assertTrue(e["accn"] and e["motif"] and e["faits"] > 0 and e["exemple"].startswith("facts/"))
        self.assertEqual(sum(e["faits"] for e in j["exclusions_par_depot"]), j["faits_ecartes"])

    def test_trace_verifies_and_detects_tampering(self):
        raw, out = self._convert()
        self.assertEqual(ec.verify_trace(raw, out), [])
        p = out / "facts.csv"
        with open(p, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows[0]["raw_value"] = str(rows[0]["raw_value"]) + "1"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertTrue(any("valeur" in m for m in ec.verify_trace(raw, out)))

    def test_units_containing_a_slash_round_trip(self):
        ptr = ec.make_pointer("us-gaap", "EarningsPerShareBasic", "USD/shares", 3)
        self.assertEqual(ec.parse_pointer(ptr), ("us-gaap", "EarningsPerShareBasic", "USD/shares", 3))

        def add_eps(data):
            tax = next(iter(data["facts"]))
            concept = next(iter(data["facts"][tax]))
            item = dict(next(iter(data["facts"][tax][concept]["units"].values()))[0])
            item["val"] = 1.5
            data["facts"][tax]["EpsFictif"] = {"label": "EPS", "units": {"USD/shares": [item]}}
        raw, out = self._convert(add_eps)
        self.assertEqual(ec.verify_trace(raw, out), [])
        trace = (out / ec.TRACE_FILE).read_text(encoding="utf-8")
        self.assertIn("USD~1shares", trace)

    def test_missing_trace_row_is_reported(self):
        raw, out = self._convert()
        lines = (out / ec.TRACE_FILE).read_text(encoding="utf-8").splitlines()
        (out / ec.TRACE_FILE).write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        self.assertTrue(any("sans trace" in m for m in ec.verify_trace(raw, out)))


if __name__ == "__main__":
    unittest.main()
