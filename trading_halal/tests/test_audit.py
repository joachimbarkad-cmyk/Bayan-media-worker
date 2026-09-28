"""Dossier d'audit documentaire (revue n° 5, question 4) : provenance, chronologie, inconnues, aucun statut religieux."""
import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

from halal_sim.audit import AuditFormatError, audit_folder

EXAMPLE = ROOT / "data" / "audit_exemple_FICTIF"


class AuditTests(unittest.TestCase):
    def _copy(self):
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(EXAMPLE, tmp / "a")
        self.addCleanup(shutil.rmtree, tmp)
        return tmp / "a"

    def _edit(self, folder, name, row_id_col, row_id, **fields):
        p = folder / f"{name}.csv"
        with open(p, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            if r[row_id_col] == row_id:
                r.update(fields)
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    def _errors(self, folder):
        return " | ".join(audit_folder(folder).errors)

    def test_example_is_valid_and_reports_unknowns_without_filling_them(self):
        res = audit_folder(EXAMPLE)
        self.assertEqual(res.errors, [])
        text = " ".join(res.unknowns)
        self.assertIn("valeur inconnue", text)
        self.assertIn("classification d'activité non établie", text)

    def test_timestamps_need_timezone_and_consistent_order(self):
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D1", accepted_at="2025-02-20T16:31:05")
        self.assertIn("sans fuseau", self._errors(d))
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D1", public_available_at="2025-02-19T10:00:00-05:00")
        self.assertIn("antérieure à l'acceptation", self._errors(d))
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D1", retrieved_at="2025-01-01T00:00:00+00:00")
        self.assertIn("récupéré avant", self._errors(d))

    def test_local_copy_hash_is_checked(self):
        d = self._copy()
        (d / "copies" / "FICT-10K-2024.txt").write_text("contenu modifié", encoding="utf-8")
        self.assertIn("SHA-256", self._errors(d))

    def test_facts_must_reference_documents_and_share_counts_need_measure_date(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", doc_id="D99")
        self.assertIn("document d'origine inconnu", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F3", measure_date="", share_class="")
        self.assertIn("date de mesure et catégorie d'actions", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F2", value="nan")
        self.assertIn("non finie", self._errors(d))

    def test_amendment_must_point_to_known_document(self):
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D2", amends_doc_id="D42")
        self.assertIn("rectifie un document inconnu", self._errors(d))

    def test_real_folder_cannot_cite_demo_sources(self):
        d = self._copy()
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        m["nature"] = "REEL"
        (d / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        self._edit(d, "issuers", "issuer_id", "FICT-0001", source="DEMO_FICTIF")
        self.assertIn("sources de démonstration", self._errors(d))

    def test_religious_status_columns_are_refused(self):
        d = self._copy()
        p = d / "activities.csv"
        lines = p.read_text(encoding="utf-8").splitlines()
        lines[0] += ",statut"
        lines[1] += ",ADMISSIBLE"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(AuditFormatError):
            audit_folder(d)


if __name__ == "__main__":
    unittest.main()
