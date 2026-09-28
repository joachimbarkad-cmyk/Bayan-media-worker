"""Cas signalés par la revue n° 3 : radiation future exposée, capitalisation aberrante, vente fictive à la
radiation, règle de complément différente entre stratégie et référence, méthode de calcul des ratios."""
import copy
import unittest
from datetime import date

from helpers import config, demo_dataset, demo_ruleset, fresh_copy, run

from halal_sim.data import PointInTimeView, fundamentals_problems
from halal_sim.report import run_checks
from halal_sim.screening import EXCLU, INCERTAIN, screen_security, structural_problems

D = date(2025, 11, 28)


class DelistingNotRevealedTests(unittest.TestCase):
    def test_review_case_future_delisting_not_exposed_by_view(self):
        v = PointInTimeView(demo_dataset(), date(2022, 1, 31))
        sec = v.security("FXMU")
        self.assertNotIn("delisted_date", sec)
        self.assertLessEqual(v.max_date_read, date(2022, 1, 31))
        after = PointInTimeView(demo_dataset(), date(2024, 7, 1)).security("FXMU")
        self.assertEqual(after["delisted_date"], date(2024, 6, 28))

    def test_changing_future_delisting_date_does_not_change_earlier_decisions(self):
        base = demo_dataset()
        altered = fresh_copy(base)
        altered.securities["FXMU"]["delisted_date"] = date(2025, 6, 30)  # radiation plus tardive
        _, s1 = run(ds=base)
        _, s2 = run(ds=altered)
        for q in ("SELECT portfolio,decision_date,ticker,final_action,reason_code,detail FROM decisions "
                  "WHERE decision_date < '2024-06-28' ORDER BY 1,2,3",
                  "SELECT decision_date,ticker,status,reasons_json FROM screenings WHERE decision_date < '2024-06-28' ORDER BY 1,2"):
            self.assertEqual([tuple(r) for r in s1.conn.execute(q)], [tuple(r) for r in s2.conn.execute(q)])


class MarketCapConsistencyTests(unittest.TestCase):
    def _status(self, ds, t="FXEPS", rs=None):
        return screen_security(PointInTimeView(ds, D), t, rs or demo_ruleset())

    def test_review_case_absurd_market_cap_is_not_admissible(self):
        ds = fresh_copy(demo_dataset())
        for f in ds.fundamentals["FXEPS"]:
            f["market_cap"] = 1e300
        r = self._status(ds)
        self.assertEqual(r.status, INCERTAIN)
        self.assertIn("DONNEE_INVALIDE", r.incertain_causes)

    def test_missing_share_count_makes_market_cap_unverifiable(self):
        ds = fresh_copy(demo_dataset())
        for f in ds.fundamentals["FXALP"]:
            f["shares_outstanding"] = None
        r = self._status(ds, "FXALP")
        self.assertEqual((r.status, r.incertain_causes), (INCERTAIN, ["DONNEE_MANQUANTE"]))

    def test_check_not_required_when_no_ratio_uses_market_cap(self):
        rs = copy.deepcopy(demo_ruleset())
        for r in rs["financial_ratios"][:2]:
            r["denominator"] = "total_assets"
        ds = fresh_copy(demo_dataset())
        for f in ds.fundamentals["FXEPS"]:
            f["market_cap"], f["shares_outstanding"] = 1e300, None
        self.assertEqual(self._status(ds, rs=rs).status, EXCLU)  # dette / actif toujours au-dessus du seuil démo

    def test_cash_above_total_assets_is_invalid(self):
        rec = dict(demo_dataset().fundamentals["FXALP"][-1])
        rec["cash_and_interest_bearing_investments"] = rec["total_assets"] * 2
        self.assertTrue(fundamentals_problems(rec))


class DelistingValuationTests(unittest.TestCase):
    def test_review_case_no_cash_credited_without_documented_consideration(self):
        res, store = run()
        c = store.conn
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE ticker='FXMU' AND side='SELL' "
                                   "AND execution_date >= '2024-06-28' AND status='EXECUTE_SIMULE'").fetchone()[0], 0)
        ev = c.execute("SELECT portfolio, event, cash_received FROM corporate_events WHERE ticker='FXMU'").fetchall()
        self.assertEqual({(r[0], r[1], r[2]) for r in ev},
                         {("reference", "RADIATION_VALEUR_INCONNUE", 0.0),
                          ("reference_reinvestie", "RADIATION_VALEUR_INCONNUE", 0.0)})
        for pf in ("reference", "reference_reinvestie"):
            m = res.metrics[pf]
            self.assertIn("FXMU", res.brokers[pf].frozen)
            self.assertGreater(m["valeur_titres_radies_au_dernier_cours"], 0)
            self.assertGreater(m["rendement_total_pct_si_radies_au_dernier_cours"], m["rendement_total_pct"])

    def test_documented_cash_consideration_is_credited(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXMU"].update(delisting_cash_per_share=5.0, delisting_source="Offre de rachat fictive (test)",
                                     delisting_source_date=date(2024, 6, 10), delisting_cash_date=date(2024, 7, 15))
        res, store = run(ds=ds)
        rows = store.conn.execute("SELECT portfolio, event, qty, cash_received, date FROM corporate_events "
                                  "WHERE event='RADIATION_CONTREPARTIE_DOCUMENTEE'").fetchall()
        self.assertTrue(rows)
        for r in rows:
            self.assertAlmostEqual(r[3], r[2] * 5.0)
            self.assertEqual(r[4], "2024-07-16")  # séance suivant le paiement (revue n° 5), pas à la radiation
        for br in res.brokers.values():
            self.assertEqual(br.frozen, {})

    def test_every_fill_matches_a_real_opening_price(self):
        _, store = run()
        checks = {n: ok for n, ok, _ in run_checks(store.conn, 1, demo_dataset())}
        self.assertTrue(checks["Chaque exécution simulée correspond à un cours d'ouverture présent dans le fichier, un jour de volume non nul"])
        store.conn.execute("UPDATE orders SET ref_price = ref_price * 1.01 WHERE rowid = "
                           "(SELECT MIN(rowid) FROM orders WHERE status='EXECUTE_SIMULE')")
        checks = {n: ok for n, ok, _ in run_checks(store.conn, 1, demo_dataset())}
        self.assertFalse(checks["Chaque exécution simulée correspond à un cours d'ouverture présent dans le fichier, un jour de volume non nul"])


class SameTopUpRuleTests(unittest.TestCase):
    def _complements(self, store):
        return dict(store.conn.execute(
            "SELECT portfolio, COUNT(*) FROM orders WHERE status='EXECUTE_SIMULE' AND reason IN "
            "('COMPLEMENT_TENDANCE','REFERENCE_REINVESTIE_COMPLEMENT') GROUP BY portfolio").fetchall())

    def test_default_no_topup_in_either_portfolio(self):
        _, store = run()
        self.assertEqual(self._complements(store), {})

    def test_topup_enabled_applies_to_both(self):
        cfg = dict(config(), sizing={"topup_held_positions": True})
        _, store = run(cfg=cfg)
        comp = self._complements(store)
        self.assertGreater(comp.get("strategie", 0), 0)
        self.assertGreater(comp.get("reference_reinvestie", 0), 0)


class CalculationMethodTests(unittest.TestCase):
    def test_unsupported_or_missing_calculation_method_refused(self):
        rs = copy.deepcopy(demo_ruleset())
        rs["financial_ratios"][0]["calcul"] = "moyenne_capitalisation_36_mois"
        self.assertTrue(any("non implémentée" in p for p in structural_problems(rs)))
        rs = copy.deepcopy(demo_ruleset())
        del rs["financial_ratios"][1]["calcul"]
        self.assertTrue(structural_problems(rs))


if __name__ == "__main__":
    unittest.main()
