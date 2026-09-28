import unittest
from datetime import date

from helpers import demo_dataset, demo_ruleset, fresh_copy, template_ruleset

from halal_sim.data import PointInTimeView
from halal_sim.screening import ADMISSIBLE, EXCLU, INCERTAIN, RulesetError, load_ruleset, screen_security


def status(ticker, d, ds=None, rs=None):
    return screen_security(PointInTimeView(ds or demo_dataset(), d), ticker, rs or demo_ruleset())


class ScreeningTests(unittest.TestCase):
    def test_expected_statuses_on_demo_data(self):
        d = date(2025, 11, 28)
        expected = {"FXALP": ADMISSIBLE, "FXBET": ADMISSIBLE, "FXOME": ADMISSIBLE,
                    "FXDEL": EXCLU, "FXGAM": EXCLU, "FXEPS": EXCLU, "FXKAP": EXCLU, "FXOBL": EXCLU,
                    "FXETA": INCERTAIN, "FXTHE": INCERTAIN, "FXSIG": INCERTAIN}
        for t, st in expected.items():
            self.assertEqual(status(t, d).status, st, t)

    def test_result_is_traceable(self):
        r = status("FXEPS", date(2025, 11, 28))
        self.assertEqual(r.ruleset_id, "DEMO_FICTIF_v1")
        self.assertTrue(r.fundamentals_ref["source"])
        self.assertEqual(r.fundamentals_ref["period_end"], "2025-09-30")
        self.assertIn("dette_a_interet", r.ratios)
        self.assertTrue(any("Dette" in m for m in r.reasons))

    def test_fundamentals_are_point_in_time(self):
        # Le rapport FXKAP à dette élevée est publié le 2024-08-14 : invisible la veille.
        self.assertEqual(status("FXKAP", date(2024, 8, 13)).status, ADMISSIBLE)
        self.assertEqual(status("FXKAP", date(2024, 8, 14)).status, EXCLU)

    def test_missing_value_gives_incertain(self):
        r = status("FXIOT", date(2023, 5, 31))
        self.assertEqual(r.status, INCERTAIN)
        self.assertTrue(any("donnée manquante" in m for m in r.reasons))

    def test_stale_fundamentals_give_incertain(self):
        self.assertEqual(status("FXSIG", date(2023, 1, 31)).status, ADMISSIBLE)
        self.assertEqual(status("FXSIG", date(2023, 7, 31)).status, INCERTAIN)

    def test_unknown_activity_gives_incertain(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXALP"]["activity_codes"] = ["CODE_INCONNU"]
        self.assertEqual(status("FXALP", date(2025, 11, 28), ds=ds).status, INCERTAIN)
        ds.securities["FXALP"]["activity_codes"] = []
        self.assertEqual(status("FXALP", date(2025, 11, 28), ds=ds).status, INCERTAIN)

    def test_exclu_takes_precedence_over_incertain(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXDEL"]["activity_codes"] = ["ALCOHOL", "CODE_INCONNU"]
        self.assertEqual(status("FXDEL", date(2025, 11, 28), ds=ds).status, EXCLU)

    def test_template_without_thresholds_admits_nothing(self):
        rs = template_ruleset()
        for t in demo_dataset().tickers:
            self.assertNotEqual(status(t, date(2025, 11, 28), rs=rs).status, ADMISSIBLE, t)

    def test_invalid_ruleset_rejected(self):
        import json, tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"id": "x", "validated": False, "allowed_instrument_types": [], "financial_ratios": [],
                       "max_fundamentals_age_days": 1, "activity_rules": {"A": {"status": "HALAL_100"}}}, f)
        try:
            with self.assertRaises(RulesetError):
                load_ruleset(f.name)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
