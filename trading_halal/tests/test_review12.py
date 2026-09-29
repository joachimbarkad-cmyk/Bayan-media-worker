"""Revue n° 12 : saisies humaines protégées par un journal (auteur, horodatage, preuve, continuité)."""
import csv
import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import edgar_collect as ec  # noqa: E402
import test_edgar_tool as te  # noqa: E402
from test_review11 import _rewrite_csv  # noqa: E402

APPLE = ROOT / "data" / "audit_edgar_apple"
APPLE_RAW = ROOT / "collecte" / "apple"
TS = "2026-09-28T12:00:00+02:00"


def _journal(folder, entries):
    with open(folder / ec.SAISIES_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ec.SAISIES_HEADERS)
        w.writeheader()
        for n, e in enumerate(entries, start=1):
            row = {"n": str(n), "ancienne_valeur": "", "auteur": "Relecteur A", "saisi_le": TS, "preuve": "",
                   "note": ""}
            row.update(e)
            w.writerow(row)


class HumanEntryJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        h = te.EdgarToolTests()
        h.tmp = self.tmp
        self.raw = h._raw()
        self.out = self.tmp / "audit"
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            self.doc = next(csv.DictReader(f))["doc_id"]
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            self.fact = next(csv.DictReader(f))
        (self.out / "copies").mkdir()
        self.proof = self.out / "copies" / "avis_diffusion.txt"
        self.proof.write_text("Diffusion constatée le 3 novembre", encoding="utf-8")
        self.proof_ref = "fichier:copies/avis_diffusion.txt#sha256=" + hashlib.sha256(self.proof.read_bytes()).hexdigest()

    def _set_public(self, value):
        def f(rows):
            for r in rows:
                if r["doc_id"] == self.doc:
                    r["public_available_at"] = value
            return rows
        _rewrite_csv(self.out / "documents.csv", f)

    def _pub_entry(self, **kw):
        e = {"fichier": "documents", "cle": self.doc, "colonne": "public_available_at",
             "nouvelle_valeur": "2025-11-03T09:00:00+00:00", "preuve": self.proof_ref}
        e.update(kw)
        return e

    def check(self):
        return ec.verify_trace(self.raw, self.out)

    def test_review_case_unjournaled_availability_date_is_flagged(self):
        self._set_public("2025-11-03T09:00:00+00:00")
        self.assertTrue(any("public_available_at" in m and "sans saisie" in m for m in self.check()))

    def test_journaled_availability_date_with_file_proof_passes(self):
        self._set_public("2025-11-03T09:00:00+00:00")
        _journal(self.out, [self._pub_entry()])
        self.assertEqual(self.check(), [])

    def test_availability_date_requires_documentary_proof(self):
        self._set_public("2025-11-03T09:00:00+00:00")
        for proof, msg in (("vu sur le site", "exige une preuve"), (f"doc:{self.doc}", "exige une preuve"),
                           ("fichier:copies/avis_diffusion.txt#sha256=" + "0" * 64, "empreinte"),
                           ("fichier:../hors.txt#sha256=" + "0" * 64, "hors du dossier")):
            _journal(self.out, [self._pub_entry(preuve=proof)])
            self.assertTrue(any(msg in m for m in self.check()), proof)
        _journal(self.out, [self._pub_entry(preuve="url:https://www.sec.gov/exemple")])
        self.assertEqual(self.check(), [])

    def test_proof_file_changed_after_entry_is_flagged(self):
        self._set_public("2025-11-03T09:00:00+00:00")
        _journal(self.out, [self._pub_entry()])
        self.proof.write_text("autre texte", encoding="utf-8")
        self.assertTrue(any("empreinte" in m for m in self.check()))

    def test_history_must_be_continuous_and_final_value_must_match(self):
        self._set_public("2025-11-05T09:00:00+00:00")
        _journal(self.out, [self._pub_entry(),
                            self._pub_entry(ancienne_valeur="2025-11-04T00:00:00+00:00",
                                            nouvelle_valeur="2025-11-05T09:00:00+00:00")])
        self.assertTrue(any("historique discontinu" in m for m in self.check()))
        _journal(self.out, [self._pub_entry(),
                            self._pub_entry(ancienne_valeur="2025-11-03T09:00:00+00:00",
                                            nouvelle_valeur="2025-11-05T09:00:00+00:00")])
        self.assertEqual(self.check(), [])
        self._set_public("2025-11-01T00:00:00+00:00")  # avancée après coup, hors journal
        self.assertTrue(any("sans saisie" in m for m in self.check()))

    def test_erasing_a_journaled_date_is_flagged(self):
        _journal(self.out, [self._pub_entry()])  # le journal dit 3 novembre, le fichier est resté vide
        self.assertTrue(any("public_available_at" in m and "sans saisie" in m for m in self.check()))

    def test_author_timezone_numbering_and_order_are_required(self):
        self._set_public("2025-11-03T09:00:00+00:00")
        for bad, msg in (({"auteur": " "}, "auteur"), ({"saisi_le": "2026-09-28T12:00:00"}, "fuseau")):
            _journal(self.out, [self._pub_entry(**bad)])
            self.assertTrue(any(msg in m for m in self.check()), msg)
        _journal(self.out, [{"fichier": "facts", "cle": self.fact["fact_id"], "colonne": "reconciled_note",
                             "nouvelle_valeur": "x", "preuve": f"doc:{self.doc}", "saisi_le": "2026-09-29T00:00:00+00:00"},
                            self._pub_entry()])
        problems = self.check()
        self.assertTrue(any("antérieur" in m for m in problems))

    def test_converter_owned_columns_cannot_be_journaled_away(self):
        _journal(self.out, [{"fichier": "documents", "cle": self.doc, "colonne": "accepted_at",
                             "nouvelle_valeur": "2000-01-01T00:00:00+00:00", "preuve": f"doc:{self.doc}"}])
        self.assertTrue(any("produit par la conversion" in m for m in self.check()))

    def test_reconciliation_and_normalization_need_entries(self):
        fid = self.fact["fact_id"]
        def norm(rows):
            for r in rows:
                if r["fact_id"] == fid:
                    r.update(normalized_concept="total_revenue", reconciled="oui", reconciled_note="page 12")
            return rows
        _rewrite_csv(self.out / "facts.csv", norm)
        self.assertEqual(len([m for m in self.check() if "sans saisie" in m]), 3)
        _journal(self.out, [{"fichier": "facts", "cle": fid, "colonne": c, "nouvelle_valeur": v,
                             "preuve": f"doc:{self.doc}"}
                            for c, v in (("normalized_concept", "total_revenue"), ("reconciled", "oui"),
                                         ("reconciled_note", "page 12"))])
        self.assertEqual(self.check(), [])

    def test_rows_of_human_tables_need_entries(self):
        with open(self.out / "concept_map.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["us-gaap:Revenues", "total_revenue", "définition identique"])
        self.assertTrue(any("concept_map.csv" in m for m in self.check()))
        _journal(self.out, [{"fichier": "concept_map", "cle": "us-gaap:Revenues", "colonne": c, "nouvelle_valeur": v,
                             "preuve": "url:https://xbrl.us/exemple"}
                            for c, v in (("source_concept", "us-gaap:Revenues"), ("normalized_concept", "total_revenue"),
                                         ("justification", "définition identique"))])
        self.assertEqual(self.check(), [])


@unittest.skipUnless(APPLE.exists() and APPLE_RAW.exists(), "dossier Apple absent")
class AppleReviewCaseTests(unittest.TestCase):
    def test_review_case_apple_public_date_without_journal(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        cp = tmp / "cp"
        shutil.copytree(APPLE, cp)
        def later(rows):
            for r in rows:
                if r["accession_number"] == "0000320193-25-000079":
                    r["public_available_at"] = "2025-11-03T09:00:00+00:00"
            return rows
        _rewrite_csv(cp / "documents.csv", later)
        self.assertTrue(any("public_available_at" in m for m in ec.verify_trace(APPLE_RAW, cp)))


if __name__ == "__main__":
    unittest.main()
