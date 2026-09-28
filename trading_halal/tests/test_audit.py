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


class Review6AuditTests(unittest.TestCase):
    """Cas signalés par la revue n° 6 ; chacun passait (ok=True) avec la V1.5."""
    _copy, _edit, _errors = AuditTests._copy, AuditTests._edit, AuditTests._errors

    def test_measure_date_after_document_acceptance_is_refused(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F3", measure_date="2026-01-01")
        self.assertIn("après l'acceptation de son document", self._errors(d))

    def test_activity_cannot_predate_its_evidence(self):
        d = self._copy()
        self._edit(d, "activities", "issuer_id", "FICT-0001", available_at="2024-01-01T00:00:00+00:00")
        self.assertIn("avant sa pièce justificative", self._errors(d))
        d = self._copy()
        self._edit(d, "activities", "issuer_id", "FICT-0001", proposed_code="SOFTWARE", evidence_doc_id="",
                   justification="")
        self.assertIn("sans justification ni pièce justificative", self._errors(d))

    def test_amendment_rules(self):
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D2", amends_doc_id="D2")
        self.assertIn("se rectifie lui-même", self._errors(d))
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D2", period_end="2023-12-31")
        self.assertIn("différente du document rectifié", self._errors(d))
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D2", accepted_at="2025-01-02T09:00:00-05:00",
                   public_available_at="2025-01-02T09:00:00-05:00")
        self.assertIn("accepté avant", self._errors(d))
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D1", version="rectificatif", amends_doc_id="D2")
        self.assertIn("boucle de rectificatifs", self._errors(d))

    def test_fact_correction_must_match_corrected_fact(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F5", period_end="2024-06-30")
        self.assertIn("period_end différent du fait corrigé", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F5", corrects_fact_id="F5")
        self.assertIn("corrige un fait inconnu ou lui-même", self._errors(d))

    def test_any_unexpected_column_is_refused(self):
        for col in ("screening_status", "note_libre"):
            d = self._copy()
            p = d / "activities.csv"
            lines = p.read_text(encoding="utf-8").splitlines()
            lines[0] += f",{col}"
            lines[1] += ",ADMISSIBLE"
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(AuditFormatError, msg=col):
                audit_folder(d)

    def test_duplicate_security_id_is_refused(self):
        d = self._copy()
        p = d / "securities.csv"
        lines = p.read_text(encoding="utf-8").splitlines()
        lines.append(lines[1].replace("USD", "EUR"))
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertIn("identifiant de titre vide ou en double", self._errors(d))

    def test_local_copy_must_stay_inside_folder(self):
        import hashlib
        d = self._copy()
        (d.parent / "external_source.txt").write_text("x", encoding="utf-8")
        self._edit(d, "documents", "doc_id", "D1", local_copy="../external_source.txt",
                   local_sha256=hashlib.sha256(b"x").hexdigest())
        self.assertIn("hors du dossier audité", self._errors(d))

    def test_share_rules_follow_unit_not_concept_name(self):
        """Concept XBRL réel non mappé, sans date de mesure : refusé parce que l'unité est « actions »."""
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F3", source_concept="dei:EntityCommonStockSharesOutstanding",
                   normalized_concept="", measure_date="", share_class="")
        self.assertIn("date de mesure et catégorie d'actions obligatoires", self._errors(d))

    def test_normalized_concept_requires_explicit_mapping(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F4", normalized_concept="non_compliant_revenue")
        self.assertIn("sans mappage explicite", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", normalized_concept="interest_bearing_debt")
        self.assertIn("contraire au mappage", self._errors(d))

    def test_unknown_public_availability_is_reported_not_copied(self):
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D1", public_available_at="")
        res = audit_folder(d)
        self.assertEqual(res.errors, [])
        self.assertTrue(any("diffusion publique non établie" in u for u in res.unknowns))


class Review7AuditTests(unittest.TestCase):
    """Cas signalés par la revue n° 7 ; chacun passait (ok=True) avec la V1.6."""
    _copy, _edit, _errors = AuditTests._copy, AuditTests._edit, AuditTests._errors

    def test_share_count_cannot_be_monetary(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F3", unit="monnaie", currency="USD")
        self.assertIn("nombre d'actions : unité « actions », sans devise", self._errors(d))

    def test_monetary_fact_needs_currency(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", currency="")
        self.assertIn("unité monétaire sans devise", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", unit="actions", currency="")
        self.assertIn("est monétaire", self._errors(d))

    def test_amendment_cannot_be_public_before_original(self):
        d = self._copy()
        self._edit(d, "documents", "doc_id", "D1", public_available_at="2025-05-01T09:00:00-04:00")
        self._edit(d, "activities", "issuer_id", "FICT-0001", available_at="2025-05-02T09:00:00-04:00")
        self.assertIn("avant ou en même temps que le document qu'il rectifie", self._errors(d))

    def test_normalization_needs_fact_level_justification_and_transformation(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", normalization_justification="")
        self.assertIn("justification propre au fait", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", value="1250")
        self.assertIn("transformation « aucune » mais valeur", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", value="1250", transformation="division par 1 000 000 (millions)")
        self.assertEqual(self._errors(d), "")

    def test_raw_fact_fields(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", source_unit="")
        self.assertIn("unité d'origine manquante", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", decimals="environ")
        self.assertIn("précision (decimals) invalide", self._errors(d))
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", source_dimensions="srt:SegmentsAxis=exemple:EuropeMember")
        self.assertTrue(any("fait dimensionnel" in u for u in audit_folder(d).unknowns))

    def test_zero_errors_is_not_a_usable_verdict_without_reconciliation(self):
        res = audit_folder(EXAMPLE)
        self.assertTrue(res.ok)
        self.assertTrue(res.verdict.startswith("NON EXPLOITABLE"))
        d = self._copy()
        for fid in ("F1", "F2", "F3", "F5"):
            self._edit(d, "facts", "fact_id", fid, reconciled="oui")
        self.assertTrue(audit_folder(d).verdict.startswith("RAPPROCHE"))


if __name__ == "__main__":
    unittest.main()
