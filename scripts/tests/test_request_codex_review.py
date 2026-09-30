"""Tests of the Codex review mechanism against a fake Codex CLI (no network needed)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "request_codex_review.py"
ROOT = HERE.parent.parent
FAKE = HERE / "fake_codex.py"
sys.path.insert(0, str(HERE.parent))
import request_codex_review as rcr  # noqa: E402


class ReviewMechanismTest(unittest.TestCase):
    def run_review(self, mode, *extra, timeout="30"):
        out = Path(tempfile.mkdtemp())
        env = {**os.environ, "FAKE_CODEX_MODE": mode, "ANTHROPIC_API_KEY": "must-not-leak"}
        p = subprocess.run([sys.executable, str(SCRIPT), "--lot", "test", "--base", "HEAD~1", "--head", "HEAD",
                            "--codex-bin", str(FAKE), "--out-dir", str(out), "--timeout", timeout,
                            "--validation", "tests ok", *extra],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        reports = sorted(out.glob("*.json"))
        self.assertEqual(len(reports), 1, p.stdout + p.stderr)
        self.assertTrue(reports[0].with_suffix(".md").exists())
        return p.returncode, json.loads(reports[0].read_text())

    def head(self):
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()

    def test_approved(self):
        code, r = self.run_review("approve")
        self.assertEqual((code, r["status"], r["reviewed_sha"]), (0, "APPROVED", self.head()))
        self.assertEqual(r["validations_declared"], ["tests ok"])

    def test_changes_requested(self):
        code, r = self.run_review("changes")
        self.assertEqual((code, r["status"]), (1, "CHANGES_REQUESTED"))
        self.assertEqual(r["findings"][0]["file"], "a.txt")

    def test_wrong_sha_is_blocked(self):
        code, r = self.run_review("wrong_sha")
        self.assertEqual((code, r["status"], r["codex_status"]), (2, "BLOCKED", None))
        self.assertIn("reviewed_sha", r["validation_errors"][0])

    def test_invalid_json_is_blocked(self):
        code, r = self.run_review("invalid_json")
        self.assertEqual((code, r["status"]), (2, "BLOCKED"))

    def test_inconsistent_approval_is_blocked(self):
        code, r = self.run_review("inconsistent")
        self.assertEqual((code, r["status"]), (2, "BLOCKED"))

    def test_logged_out_is_blocked(self):
        code, r = self.run_review("logged_out")
        self.assertEqual((code, r["status"]), (2, "BLOCKED"))
        self.assertIn("non authentifié", r["blocked_reason"])

    def test_rate_limit_is_blocked(self):
        code, r = self.run_review("rate_limit")
        self.assertEqual((code, r["status"]), (2, "BLOCKED"))
        self.assertIn("limite", r["blocked_reason"])

    def test_timeout_is_blocked(self):
        code, r = self.run_review("timeout", timeout="3")
        self.assertEqual((code, r["status"]), (2, "BLOCKED"))
        self.assertIn("délai dépassé", r["blocked_reason"])

    def test_missing_binary_is_blocked(self):
        out = Path(tempfile.mkdtemp())
        p = subprocess.run([sys.executable, str(SCRIPT), "--lot", "t", "--base", "HEAD", "--codex-bin",
                            "/nonexistent/codex", "--out-dir", str(out)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(next(out.glob("*.json")).read_text())["status"], "BLOCKED")

    def test_no_worktree_left_behind(self):
        self.run_review("approve")
        wts = subprocess.run(["git", "worktree", "list"], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual(len(wts.strip().splitlines()), 1, wts)

    def test_validator_rejects_bad_severity(self):
        sha = "a" * 40
        bad = {"reviewed_sha": sha, "status": "CHANGES_REQUESTED", "summary": "", "checks_performed": [],
               "checks_not_run": [], "findings": [{"severity": "urgent", "blocking": True, "file": "f",
                                                   "scenario": "s", "expected": "e", "observed": "o",
                                                   "proposed_fix": "p"}]}
        self.assertTrue(rcr.validate_review(bad, sha))


if __name__ == "__main__":
    unittest.main()
