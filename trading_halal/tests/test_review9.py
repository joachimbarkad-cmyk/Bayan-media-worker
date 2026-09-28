"""Revue n° 9 et intégration du document de fiqh fourni par l'utilisateur."""
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT, config, demo_dataset, fresh_copy

sys.path.insert(0, str(ROOT / "tools"))
import edgar_collect as ec  # noqa: E402
import test_edgar_tool as te  # noqa: E402
import test_audit as ta  # noqa: E402  (fonctions utilitaires seulement)

from halal_sim.audit import audit_folder  # noqa: E402
from halal_sim.backtest import PolicyError, check_run_allowed, run_backtest  # noqa: E402
from halal_sim.db import Store, snapshot_database  # noqa: E402
from halal_sim.report import build_report, run_checks  # noqa: E402
from halal_sim.screening import load_ruleset, real_data_problems  # noqa: E402

USER_RULESET = ROOT / "config" / "rulesets" / "AAOIFI_SS21_document_utilisateur.json"


class UserFiqhRulesetTests(unittest.TestCase):
    def setUp(self):
        self.rs = load_ruleset(USER_RULESET)

    def test_thresholds_are_those_cited_by_the_user_document_with_sources(self):
        got = {r["id"]: (r["max"], r["denominator"]) for r in self.rs["financial_ratios"]}
        self.assertEqual(got, {"dette_a_interet": (0.30, "market_cap"), "liquidites_a_interet": (0.30, "market_cap"),
                               "revenus_non_conformes": (0.05, "total_revenue")})
        for r in self.rs["financial_ratios"]:
            self.assertIn("Document fourni par l'utilisateur", r["source"])
            self.assertIn("3/4/", r["source"])

    def test_not_usable_on_real_data_until_named_board_validates(self):
        self.assertFalse(self.rs["validated"])
        self.assertEqual(sorted(real_data_problems(self.rs)), sorted([
            "validated n'est pas true", "validated_by non renseigné", "validated_on doit être une date AAAA-MM-JJ"]))
        ds = fresh_copy(demo_dataset())
        ds.manifest["nature"] = "REEL"
        with self.assertRaises(PolicyError):
            check_run_allowed(ds, self.rs, config())

    def test_divergence_is_disclosed_in_report(self):
        store = Store(":memory:")
        res = run_backtest(demo_dataset(), config(), self.rs, store)
        report = build_report(store.conn, res.run_id, [], run_checks(store.conn, res.run_id))
        self.assertIn("Divergence entre savants", report)
        self.assertIn("rés. 63 (1/7)", report)


class SnapshotPathTests(unittest.TestCase):
    def test_review_case_reserved_characters_in_path(self):
        for name in ("old?name.sqlite", "a#b.sqlite", "c%41d.sqlite", "espace et é.sqlite"):
            with tempfile.TemporaryDirectory() as tmp:
                db = Path(tmp) / name
                con = sqlite3.connect(db)
                con.execute("CREATE TABLE t(v)")
                con.execute("INSERT INTO t VALUES(1)")
                con.commit()
                con.close()
                snap = snapshot_database(db)
                c = sqlite3.connect(snap)
                self.assertEqual(c.execute("SELECT COUNT(*) FROM t").fetchone()[0], 1, name)
                c.close()
                self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), sorted([name, snap.name]), name)


class ContextRequiredTests(unittest.TestCase):
    _copy, _edit, _errors = ta.AuditTests._copy, ta.AuditTests._edit, ta.AuditTests._errors

    def test_review_case_normalized_fact_without_context_is_refused(self):
        d = self._copy()
        self._edit(d, "facts", "fact_id", "F1", source_context="")
        self.assertIn("normalisation impossible sans contexte d'origine", self._errors(d))


class EdgarReview9Tests(unittest.TestCase):
    _raw, _rehash, _patch_facts, _raw_in = (te.EdgarToolTests._raw, te.EdgarToolTests._rehash,
                                            te.EdgarToolTests._patch_facts, te.EdgarToolTests._raw_in)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_review_case_fact_form_or_filing_date_must_match_its_filing(self):
        raw = self._raw()
        self._patch_facts(raw, lambda cf: cf["facts"]["us-gaap"]["Revenues"]["units"]["USD"][0].update(
            form="10-K/A", filed="2026-01-01"))
        with self.assertRaises(ec.EdgarFormatError):
            ec.convert(raw, self.tmp / "a", {"10-K", "10-Q"})

    def test_review_case_selected_filing_without_report_date_is_named(self):
        raw = self._raw()
        p = raw / "submissions_CIK0000000123.json"
        sub = json.loads(p.read_text(encoding="utf-8"))
        sub["filings"]["recent"]["reportDate"][1] = ""
        p.write_text(json.dumps(sub), encoding="utf-8")
        self._rehash(raw)
        res = ec.convert(raw, self.tmp / "a", {"10-K", "10-Q"})
        self.assertEqual(len(res["selected_but_skipped"]), 1)
        self.assertIn("reportDate", res["selected_but_skipped"][0])
        self.assertIn("1 écarté(s)", json.loads((self.tmp / "a" / "manifest.json").read_text(encoding="utf-8"))["warning"])

    def test_review_case_no_silent_overwrite(self):
        raw = self._raw()
        ec.convert(raw, self.tmp / "audit", {"10-K", "10-Q"})
        with self.assertRaises(SystemExit):
            ec.convert(raw, self.tmp / "audit", {"10-K", "10-Q"})
        ec.convert(raw, self.tmp / "audit", {"10-K", "10-Q"}, replace=True)  # explicite
        ec.MIN_INTERVAL_S = 0
        with self.assertRaises(SystemExit):
            ec.collect(["123"], raw, "Alice Martin alice@societe.fr", fetch=te._no_network)

    def test_manual_import_needs_declared_time_and_no_network(self):
        src = self.tmp / "telechargements"
        src.mkdir()
        for kind in ("submissions", "companyfacts"):
            shutil.copy(te.FIX / f"{kind}_CIK0000000123.json", src / f"{kind}.json")
        with self.assertRaises(SystemExit):
            ec.import_files("123", src / "submissions.json", src / "companyfacts.json", "2026-09-28 14:05", self.tmp / "r")
        log = ec.import_files("123", src / "submissions.json", src / "companyfacts.json",
                              "2026-09-28T14:05:00+02:00", self.tmp / "r")
        self.assertEqual(log[0]["method"], "téléchargement manuel déclaré")
        self.assertEqual(log[0]["sha256"], hashlib.sha256((src / "submissions.json").read_bytes()).hexdigest())
        ec.convert(self.tmp / "r", self.tmp / "audit", {"10-K", "10-Q"})
        self.assertEqual(audit_folder(self.tmp / "audit").errors, [])


if __name__ == "__main__":
    unittest.main()
