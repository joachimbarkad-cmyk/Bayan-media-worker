"""Point critique n° 1 : un titre INCERTAIN (ou EXCLU) ne peut jamais être acheté."""
import sqlite3
import unittest
from datetime import date

from helpers import demo_dataset, demo_ruleset, run, template_ruleset

from halal_sim.broker import CostModel, ForbiddenOrderError, PaperBroker
from halal_sim.data import PointInTimeView
from halal_sim.db import Store
from halal_sim.screening import ADMISSIBLE, EXCLU, INCERTAIN, screen_security
from halal_sim.strategy import BUY, NONE, SmaTrendStrategy


class IncertainNeverBoughtTests(unittest.TestCase):
    def test_paper_broker_refuses_non_admissible(self):
        br = PaperBroker("t", 10_000, CostModel())
        for st in (INCERTAIN, EXCLU, "", None):
            with self.assertRaises(ForbiddenOrderError):
                br.buy("X", 1, 10.0, date(2024, 1, 1), date(2024, 1, 2), st, "test", status_at_execution=st)
            with self.assertRaises(ForbiddenOrderError):  # admissible à la décision, plus à l'ouverture
                br.buy("X", 1, 10.0, date(2024, 1, 1), date(2024, 1, 2), ADMISSIBLE, "test", status_at_execution=st)
        self.assertEqual(br.positions, {})
        br.buy("X", 1, 10.0, date(2024, 1, 1), date(2024, 1, 2), ADMISSIBLE, "test", status_at_execution=ADMISSIBLE)
        self.assertEqual(br.positions, {"X": 1})

    def test_strategy_never_emits_buy_for_incertain_even_with_uptrend(self):
        d = date(2025, 11, 28)
        view = PointInTimeView(demo_dataset(), d)
        scr = screen_security(view, "FXTHE", demo_ruleset())
        self.assertEqual(scr.status, INCERTAIN)
        strat = SmaTrendStrategy(200)
        up, _ = strat.trend(PointInTimeView(demo_dataset(), d), "FXTHE")
        self.assertTrue(up, "précondition : tendance haussière")
        dec = strat.decide(PointInTimeView(demo_dataset(), d), scr, held=False,
                           policy={"on_exclu": "SELL", "on_incertain": "SELL"})
        self.assertEqual(dec.signal, NONE)
        self.assertEqual(dec.reason_code, "REFUS_STATUT_INCERTAIN")

    def test_full_backtest_buys_only_admissible(self):
        res, store = run()
        c = store.conn
        n_buys = c.execute("SELECT COUNT(*) FROM orders WHERE side='BUY' AND status='EXECUTE_SIMULE'").fetchone()[0]
        self.assertGreater(n_buys, 0)
        bad = c.execute(
            "SELECT COUNT(*) FROM orders o JOIN screenings s ON s.run_id=o.run_id AND s.ticker=o.ticker "
            "AND s.decision_date=o.decision_date WHERE o.side='BUY' AND o.status='EXECUTE_SIMULE' "
            "AND s.status<>'ADMISSIBLE'").fetchone()[0]
        self.assertEqual(bad, 0)
        bought = {r[0] for r in c.execute("SELECT DISTINCT ticker FROM orders WHERE side='BUY'")}
        self.assertTrue(bought.isdisjoint({"FXTHE", "FXETA", "FXDEL", "FXGAM", "FXEPS", "FXOBL"}))
        # Aucune décision finale d'achat sur un statut non admissible
        self.assertEqual(c.execute("SELECT COUNT(*) FROM decisions WHERE final_action=? AND screening_status<>?",
                                   (BUY, ADMISSIBLE)).fetchone()[0], 0)

    def test_unvalidated_template_ruleset_produces_no_buy(self):
        res, store = run(ruleset=template_ruleset())
        for br in res.brokers.values():
            self.assertEqual([f for f in br.fills if f.side == "BUY"], [])

    def test_database_rejects_buy_of_non_admissible(self):
        store = Store(":memory:")
        store.conn.execute("INSERT INTO runs(run_id,created_at,label,dataset_nature) VALUES(1,'x','t','FICTIF')")
        with self.assertRaises(sqlite3.IntegrityError):
            store.conn.execute("INSERT INTO orders(run_id,portfolio,decision_date,execution_date,ticker,side,qty,status,"
                               "screening_status_at_decision) VALUES(1,'p','2024-01-01','2024-01-02','X','BUY',1,"
                               "'EXECUTE_SIMULE','INCERTAIN')")
        with self.assertRaises(sqlite3.IntegrityError):
            store.conn.execute("INSERT INTO decisions(run_id,portfolio,decision_date,ticker,screening_status,signal,"
                               "final_action,reason_code) VALUES(1,'p','2024-01-01','X','INCERTAIN','ACHAT','ACHAT','x')")


if __name__ == "__main__":
    unittest.main()
