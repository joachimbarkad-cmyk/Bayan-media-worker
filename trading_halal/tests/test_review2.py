"""Cas signalés par la revue n° 2 et comportements ajoutés en réponse (univers daté, référence réinvestie)."""
import copy
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from helpers import ROOT, config, demo_dataset, demo_ruleset, fresh_copy, run

from halal_sim.backtest import PolicyError, check_run_allowed
from halal_sim.data import DataError, LookaheadError, PointInTimeView, load_dataset
from halal_sim.screening import ADMISSIBLE, EXCLU, INCERTAIN, RulesetError, real_data_problems, screen_security, \
    structural_problems
from test_ruleset_validation import complete_test_ruleset, load_from_dict

D = date(2025, 11, 28)


def _status(ds, ticker, d=D, rs=None):
    return screen_security(PointInTimeView(ds, d), ticker, rs or demo_ruleset())


class RatioFieldBindingTests(unittest.TestCase):
    def test_review_case_all_ratios_pointing_to_revenue_fields_is_refused(self):
        rs = copy.deepcopy(demo_ruleset())
        for r in rs["financial_ratios"]:
            r["numerator"], r["denominator"] = "non_compliant_revenue", "total_revenue"
        self.assertTrue(structural_problems(rs))
        with self.assertRaises(RulesetError):
            load_from_dict(rs)
        with self.assertRaises(PolicyError):
            check_run_allowed(demo_dataset(), rs, config())
        real = complete_test_ruleset()
        for r in real["financial_ratios"]:
            r["numerator"], r["denominator"] = "non_compliant_revenue", "total_revenue"
        self.assertTrue(real_data_problems(real))

    def test_allowed_and_refused_denominators(self):
        rs = copy.deepcopy(demo_ruleset())
        rs["financial_ratios"][0]["denominator"] = "total_assets"      # dette / total de l'actif : admis
        self.assertEqual(structural_problems(rs), [])
        rs["financial_ratios"][2]["denominator"] = "market_cap"        # revenus non conformes / capitalisation : refusé
        self.assertTrue(structural_problems(rs))
        rs = copy.deepcopy(demo_ruleset())
        rs["financial_ratios"].append(dict(rs["financial_ratios"][0], id="creances"))  # type absent du catalogue
        self.assertTrue(structural_problems(rs))

    def test_debt_ratio_still_excludes_fxeps_with_valid_ruleset(self):
        self.assertEqual(_status(demo_dataset(), "FXEPS").status, EXCLU)


class InvalidNumberTests(unittest.TestCase):
    def test_review_case_nan_or_negative_debt_is_never_admissible(self):
        for bad in (float("nan"), float("inf"), -1e9):
            ds = fresh_copy(demo_dataset())
            for f in ds.fundamentals["FXEPS"]:
                f["interest_bearing_debt"] = bad
            r = _status(ds, "FXEPS")
            self.assertEqual(r.status, INCERTAIN, bad)
            self.assertIn("DONNEE_INVALIDE", r.incertain_causes)

    def test_non_compliant_revenue_above_revenue_is_invalid(self):
        ds = fresh_copy(demo_dataset())
        for f in ds.fundamentals["FXALP"]:
            f["non_compliant_revenue"] = f["total_revenue"] * 2
        self.assertEqual(_status(ds, "FXALP").incertain_causes, ["DONNEE_INVALIDE"])

    def _copy(self):
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT / "data" / "demo", tmp / "d")
        self.addCleanup(shutil.rmtree, tmp)
        return tmp / "d"

    def _patch_first_row(self, d, filename, column, value):
        p = d / filename
        lines = p.read_text(encoding="utf-8").splitlines()
        header = lines[0].split(",")
        parts = lines[1].split(",")
        parts[header.index(column)] = value
        lines[1] = ",".join(parts)
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_loader_rejects_non_finite_and_impossible_values(self):
        cases = [("prices_FICTIF.csv", "close", "nan"), ("prices_FICTIF.csv", "open", "inf"),
                 ("fundamentals_FICTIF.csv", "interest_bearing_debt", "nan"),
                 ("fundamentals_FICTIF.csv", "interest_bearing_debt", "-5"),
                 ("fundamentals_FICTIF.csv", "market_cap", "0"),
                 ("fundamentals_FICTIF.csv", "non_compliant_revenue", "9e99")]
        for filename, column, value in cases:
            d = self._copy()
            self._patch_first_row(d, filename, column, value)
            with self.assertRaises(DataError, msg=f"{filename}:{column}={value}"):
                load_dataset(d)


class DatedUniverseTests(unittest.TestCase):
    def test_review_case_security_record_known_later_is_not_used_earlier(self):
        """Une fiche titre modifiée (type d'instrument) doit porter sa date : avant, elle n'est pas lisible."""
        ds = fresh_copy(demo_dataset())
        ds.securities["FXALP"].update(instrument_type="OPTION", known_from=date(2025, 12, 1))
        self.assertNotIn("FXALP", ds.universe_at(date(2021, 10, 29)))
        with self.assertRaises(LookaheadError):
            PointInTimeView(ds, date(2021, 10, 29)).security("FXALP")
        self.assertEqual(_status(ds, "FXALP", date(2025, 12, 2)).status, EXCLU)
        _, store = run(ds=ds)
        self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM screenings WHERE ticker='FXALP'").fetchone()[0], 0)

    def test_listed_late_and_delisted_securities(self):
        ds = demo_dataset()
        self.assertNotIn("FXNU", ds.universe_at(date(2023, 2, 28)))
        self.assertIn("FXNU", ds.universe_at(date(2023, 3, 31)))
        self.assertIn("FXMU", ds.universe_at(date(2024, 5, 31)))
        self.assertNotIn("FXMU", ds.universe_at(date(2024, 6, 28)))
        _, store = run()
        c = store.conn
        first_nu = c.execute("SELECT MIN(decision_date) FROM screenings WHERE ticker='FXNU'").fetchone()[0]
        last_mu = c.execute("SELECT MAX(decision_date) FROM screenings WHERE ticker='FXMU'").fetchone()[0]
        self.assertEqual((first_nu, last_mu), ("2023-03-31", "2024-05-31"))
        # Revue n° 3 : plus de vente encaissée à la radiation ; la position est gelée (voir test_review3).
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE ticker='FXMU' AND status='EXECUTE_SIMULE' "
                                   "AND execution_date >= '2024-06-28'").fetchone()[0], 0)
        for br in run()[0].brokers.values():
            self.assertNotIn("FXMU", br.positions)


class ReinvestedReferenceTests(unittest.TestCase):
    def test_reinvested_reference_rebuys_title_that_becomes_admissible_again(self):
        _, store = run()
        c = store.conn
        rows = c.execute("SELECT decision_date, final_action, reason_code FROM decisions "
                         "WHERE portfolio='reference_reinvestie' AND ticker='FXIOT' ORDER BY decision_date").fetchall()
        sold = [r[0] for r in rows if r[2] == "VENTE_STATUT_INCERTAIN"]
        rebought = [r[0] for r in rows if r[1] == "ACHAT" and sold and r[0] > sold[0]]
        self.assertEqual(sold, ["2023-05-31"])
        self.assertTrue(rebought and rebought[0] >= "2023-08-31")

    def test_reinvested_reference_never_sells_to_rebalance_and_never_uses_sma(self):
        _, store = run()
        reasons = {r[0] for r in store.conn.execute(
            "SELECT DISTINCT reason FROM orders WHERE portfolio='reference_reinvestie' AND side='SELL'")}
        self.assertTrue(reasons <= {"VENTE_STATUT_EXCLU", "VENTE_STATUT_INCERTAIN", "VENTE_HORS_UNIVERS",
                                    "LIQUIDATION_RADIATION_AU_DERNIER_COURS"}, reasons)
        inputs = [r[0] for r in store.conn.execute(
            "SELECT inputs_json FROM decisions WHERE portfolio='reference_reinvestie'")]
        self.assertFalse(any('"sma"' in i for i in inputs))


if __name__ == "__main__":
    unittest.main()
