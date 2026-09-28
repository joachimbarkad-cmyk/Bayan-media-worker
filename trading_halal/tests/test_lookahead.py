"""Point critique n° 3 : aucune décision ne lit une donnée postérieure à sa date."""
import random
import sqlite3
import unittest
from datetime import date

from helpers import demo_dataset, fresh_copy, run

from halal_sim.broker import CostModel, PaperBroker
from halal_sim.data import Bar, LookaheadError, PointInTimeView
from halal_sim.db import Store
from halal_sim.screening import ADMISSIBLE

CUTOFF = date(2023, 6, 30)  # dernier jour de bourse de juin 2023 dans le calendrier fictif


def _rows(store, sql):
    return [tuple(r) for r in store.conn.execute(sql, (CUTOFF.isoformat(),))]


class LookaheadTests(unittest.TestCase):
    def test_view_never_returns_future_data(self):
        ds = demo_dataset()
        for d in (date(2021, 3, 15), date(2023, 6, 30), date(2024, 8, 13)):
            v = PointInTimeView(ds, d)
            for t in ds.tickers:
                self.assertTrue(all(b.date <= d for b in v.last_bars(t, 10_000)))
                f = v.latest_fundamentals(t)
                self.assertTrue(f is None or f["available_date"] <= d)
            self.assertLessEqual(v.max_date_read, d)

    def test_view_raises_on_future_touch(self):
        v = PointInTimeView(demo_dataset(), date(2023, 1, 2))
        with self.assertRaises(LookaheadError):
            v._touch(date(2023, 1, 3))

    def test_changing_the_future_does_not_change_past_decisions(self):
        """Test de perturbation : on falsifie toutes les données postérieures à CUTOFF.
        Les filtrages, décisions et exécutions jusqu'à CUTOFF doivent être strictement identiques."""
        base = demo_dataset()
        rng = random.Random(1)
        bars = {}
        for t, bs in base.bars.items():
            bars[t] = [b if b.date <= CUTOFF else
                       Bar(b.date, *(x * f for x, f in zip((b.open, b.high, b.low, b.close), [rng.uniform(0.3, 3)] * 4)),
                           b.volume) for b in bs]
        funds = {t: [dict(f, interest_bearing_debt=f["market_cap"] * 5) if f["available_date"] > CUTOFF else f
                     for f in fs] for t, fs in base.fundamentals.items()}
        altered = fresh_copy(base, bars=bars, fundamentals=funds)

        _, s1 = run(ds=base)
        _, s2 = run(ds=altered)
        q_scr = "SELECT decision_date,ticker,status,reasons_json,ratios_json FROM screenings WHERE decision_date<=? ORDER BY 1,2"
        q_dec = ("SELECT portfolio,decision_date,ticker,signal,final_action,reason_code,detail,inputs_json FROM decisions "
                 "WHERE decision_date<=? ORDER BY 1,2,3")
        q_ord = ("SELECT portfolio,decision_date,execution_date,ticker,side,qty,exec_price,fees FROM orders "
                 "WHERE execution_date<=? ORDER BY 1,3,4")
        q_eq = "SELECT portfolio,date,equity FROM equity WHERE date<=? ORDER BY 1,2"
        for q in (q_scr, q_dec, q_ord, q_eq):
            a, b = _rows(s1, q), _rows(s2, q)
            self.assertTrue(a, q)
            self.assertEqual(a, b, q)
        # Et la falsification a bien un effet après CUTOFF (sinon le test ne prouverait rien)
        self.assertNotEqual(_rows(s1, q_scr.replace("<=", ">")), _rows(s2, q_scr.replace("<=", ">")))

    def test_recorded_read_dates_never_exceed_decision_dates(self):
        _, store = run()
        c = store.conn
        self.assertEqual(c.execute("SELECT COUNT(*) FROM decisions WHERE max_data_date IS NULL AND portfolio='strategie' "
                                   "AND screening_status='ADMISSIBLE'").fetchone()[0], 0)
        for table in ("decisions", "screenings"):
            self.assertEqual(c.execute(f"SELECT COUNT(*) FROM {table} WHERE max_data_date > decision_date").fetchone()[0], 0)
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE execution_date <= decision_date").fetchone()[0], 0)

    def test_database_rejects_future_reads_and_same_day_execution(self):
        store = Store(":memory:")
        store.conn.execute("INSERT INTO runs(run_id,created_at,label,dataset_nature) VALUES(1,'x','t','FICTIF')")
        with self.assertRaises(sqlite3.IntegrityError):
            store.conn.execute("INSERT INTO screenings(run_id,decision_date,ticker,status,reasons_json,ruleset_id,"
                               "max_data_date) VALUES(1,'2024-01-01','X','ADMISSIBLE','[]','r','2024-01-02')")
        with self.assertRaises(sqlite3.IntegrityError):
            store.conn.execute("INSERT INTO orders(run_id,portfolio,decision_date,execution_date,ticker,side,qty,status,"
                               "screening_status_at_decision) VALUES(1,'p','2024-01-01','2024-01-01','X','SELL',1,"
                               "'EXECUTE_SIMULE','ADMISSIBLE')")

    def test_broker_refuses_execution_not_after_decision(self):
        br = PaperBroker("t", 1000, CostModel())
        with self.assertRaises(LookaheadError):
            br.buy("X", 1, 10.0, date(2024, 1, 2), date(2024, 1, 2), ADMISSIBLE, "t")


if __name__ == "__main__":
    unittest.main()
