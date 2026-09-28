"""Outil de collecte EDGAR (hors du paquet halal_sim) : testé HORS LIGNE sur des fichiers fictifs."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from helpers import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import edgar_collect as ec  # noqa: E402

from halal_sim.audit import audit_folder  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "edgar_FICTIF"


def _no_network(url, ua):
    raise AssertionError(f"requête inattendue vers {url}")


class EdgarToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def _raw(self):
        raw = self.tmp / "raw"
        raw.mkdir()
        log = []
        for kind in ("submissions", "companyfacts"):
            name = f"{kind}_CIK0000000123.json"
            shutil.copy(FIX / name, raw / name)
            log.append({"kind": kind, "cik": "0000000123", "url": f"https://data.sec.gov/{kind}", "file": name,
                        "retrieved_at": "2026-09-28T10:00:00+00:00",
                        "sha256": hashlib.sha256((raw / name).read_bytes()).hexdigest()})
        (raw / "journal_collecte.json").write_text(json.dumps(log), encoding="utf-8")
        return raw

    def test_user_agent_is_mandatory_and_never_defaulted(self):
        for ua in (None, "", "sans_adresse", "Prénom Nom nom@exemple.com", "x@y.z"):
            with self.assertRaises(SystemExit, msg=ua):
                ec.collect(["123"], self.tmp / "o", ua, fetch=_no_network)
        self.assertEqual(ec.check_user_agent("Jean Testard jean.testard@societe.fr"),
                         "Jean Testard jean.testard@societe.fr")  # un vrai nom contenant « test » est accepté

    def test_dry_run_makes_no_request(self):
        self.assertEqual(ec.collect(["123"], self.tmp / "o", None, dry_run=True, fetch=_no_network), [])
        self.assertFalse((self.tmp / "o").exists())

    def test_collect_logs_hash_without_personal_identifier(self):
        calls = []
        def fake(url, ua):
            calls.append((url, ua))
            return b'{"ok": true}'
        ec.MIN_INTERVAL_S = 0
        ec.collect(["123"], self.tmp / "o", "Alice Martin alice@societe.fr", fetch=fake)
        self.assertEqual([u for u, _ in calls], ["https://data.sec.gov/submissions/CIK0000000123.json",
                                                 "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000123.json"])
        journal = (self.tmp / "o" / "journal_collecte.json").read_text(encoding="utf-8")
        self.assertNotIn("alice", journal.lower())
        self.assertEqual(json.loads(journal)[0]["sha256"], hashlib.sha256(b'{"ok": true}').hexdigest())

    def test_convert_produces_consistent_audit_folder_that_is_not_yet_usable(self):
        res = ec.convert(self._raw(), self.tmp / "audit", {"10-K", "10-Q"})
        self.assertEqual(res["documents"], 2)                      # 10-K et 10-Q ; 8-K exclu
        self.assertEqual(len(res["amendments_to_link"]), 1)        # 10-K/A à rattacher à la main
        self.assertEqual(res["facts_skipped_other_documents"], 1)  # fait du 10-K/A non repris
        audit = audit_folder(self.tmp / "audit")
        self.assertEqual(audit.errors, [])
        self.assertEqual(audit.nature, "REEL")
        self.assertTrue(audit.verdict.startswith("NON EXPLOITABLE"))
        self.assertTrue(any("diffusion publique non établie" in u for u in audit.unknowns))

    def test_convert_is_strict_about_format_and_integrity(self):
        raw = self._raw()
        sub = json.loads((raw / "submissions_CIK0000000123.json").read_text(encoding="utf-8"))
        del sub["filings"]["recent"]["acceptanceDateTime"]
        (raw / "submissions_CIK0000000123.json").write_text(json.dumps(sub), encoding="utf-8")
        with self.assertRaises(ec.EdgarFormatError):   # empreinte modifiée
            ec.convert(raw, self.tmp / "a1", {"10-K"})
        journal = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
        journal[0]["sha256"] = hashlib.sha256((raw / "submissions_CIK0000000123.json").read_bytes()).hexdigest()
        (raw / "journal_collecte.json").write_text(json.dumps(journal), encoding="utf-8")
        with self.assertRaises(ec.EdgarFormatError):   # champ attendu absent
            ec.convert(raw, self.tmp / "a2", {"10-K"})

    def test_simulator_package_still_has_no_network_code(self):
        from halal_sim.safety import scan_package
        self.assertEqual(scan_package(), [])


if __name__ == "__main__":
    unittest.main()
