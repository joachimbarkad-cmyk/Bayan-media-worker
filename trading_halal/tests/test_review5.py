"""Cas signalés par la revue n° 5 : volume du jour et exécution, exclusion publiée entre décision et exécution,
journal de radiation influencé par le futur, paiement en début de journée, volume négatif, faux jeu REEL."""
import json
import sqlite3
import unittest
from datetime import date

from helpers import demo_dataset, fresh_copy, run, with_activity
from test_review4 import VolumeTests, _copy_demo

from halal_sim.data import DataError, load_dataset
from halal_sim.db import Store
from halal_sim.report import run_checks

EXEC = "2021-11-01"   # premier jour d'exécution (décision du 2021-10-29)


def _set_price_field(d, row_index, column, value):
    p = d / "prices_FICTIF.csv"
    lines = p.read_text(encoding="utf-8").splitlines()
    header = lines[0].split(",")
    parts = lines[row_index].split(",")
    parts[header.index(column)] = value
    lines[row_index] = ",".join(parts)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


class ExecutionVolumeTests(unittest.TestCase):
    def test_review_case_no_fill_larger_than_day_volume(self):
        """Volume total du jour = 1 action : les références simulaient l'achat de 7 actions."""
        _, store = run(ds=VolumeTests()._with_volume("FXALP", date(2021, 11, 1), 1))
        c = store.conn
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE ticker='FXALP' AND execution_date=? AND "
                                   "status='EXECUTE_SIMULE'", (EXEC,)).fetchone()[0], 0)
        reasons = {r[0] for r in c.execute("SELECT reason FROM orders WHERE ticker='FXALP' AND execution_date=?", (EXEC,))}
        self.assertTrue(any(r.startswith("VOLUME_DU_JOUR_INSUFFISANT") for r in reasons), reasons)

    def test_decisions_never_depend_on_the_execution_day_bar(self):
        """La barre du jour d'exécution (volume) ne sert qu'au modèle de marché : les DÉCISIONS prises la veille
        et avant sont identiques, seules les exécutions changent."""
        _, base = run()
        _, alt = run(ds=VolumeTests()._with_volume("FXALP", date(2021, 11, 1), 0))
        q = ("SELECT portfolio, decision_date, ticker, signal, final_action, reason_code, detail, inputs_json "
             "FROM decisions WHERE decision_date <= '2021-10-29' ORDER BY 1, 2, 3")
        self.assertEqual([tuple(r) for r in base.conn.execute(q)], [tuple(r) for r in alt.conn.execute(q)])
        q2 = "SELECT COUNT(*) FROM orders WHERE ticker='FXALP' AND execution_date=? AND status='EXECUTE_SIMULE'"
        self.assertNotEqual(base.conn.execute(q2, (EXEC,)).fetchone()[0], alt.conn.execute(q2, (EXEC,)).fetchone()[0])

    def test_run_check_flags_fill_above_day_volume(self):
        ds = demo_dataset()
        _, store = run()
        names = {n: ok for n, ok, _ in run_checks(store.conn, 1, ds)}
        self.assertTrue(names["Quantité exécutée <= 5% du volume total du jour"])
        store.conn.execute("UPDATE orders SET qty = 10000000 WHERE rowid = (SELECT MIN(rowid) FROM orders "
                           "WHERE status='EXECUTE_SIMULE')")
        names = {n: ok for n, ok, _ in run_checks(store.conn, 1, ds)}
        self.assertFalse(names["Quantité exécutée <= 5% du volume total du jour"])


class ExclusionBetweenDecisionAndExecutionTests(unittest.TestCase):
    def test_review_case_exclusion_published_on_decision_day_blocks_next_open_buy(self):
        ds = with_activity(demo_dataset(), "FXALP", "2021-10-29", ["CONVENTIONAL_BANKING"])
        _, store = run(ds=ds)
        c = store.conn
        # Décision du 29/10 : encore ADMISSIBLE (règle J+1), achat décidé par les références...
        self.assertEqual(c.execute("SELECT COUNT(*) FROM decisions WHERE ticker='FXALP' AND decision_date='2021-10-29' "
                                   "AND final_action='ACHAT'").fetchone()[0], 2)
        # ... mais refusé à l'ouverture du 01/11, où l'exclusion est connue.
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE ticker='FXALP' AND side='BUY' AND "
                                   "status='EXECUTE_SIMULE'").fetchone()[0], 0)
        self.assertEqual({r[0] for r in c.execute("SELECT reason FROM orders WHERE ticker='FXALP' AND execution_date=?",
                                                  (EXEC,))}, {"STATUT_EXCLU_A_L_OUVERTURE"})
        checks = {n: ok for n, ok, _ in run_checks(c, 1, ds)}
        self.assertTrue(checks["Aucun achat d'un titre non ADMISSIBLE à l'ouverture d'exécution (statut recalculé)"])

    def test_database_rejects_buy_without_admissible_status_at_execution(self):
        store = Store(":memory:")
        store.conn.execute("INSERT INTO runs(run_id,created_at,label,dataset_nature) VALUES(1,'x','t','FICTIF')")
        for exec_status in ("EXCLU", None):
            with self.assertRaises(sqlite3.IntegrityError):
                store.conn.execute("INSERT INTO orders(run_id,portfolio,decision_date,execution_date,ticker,side,qty,status,"
                                   "screening_status_at_decision,screening_status_at_execution) VALUES(1,'p','2024-01-01',"
                                   "'2024-01-02','X','BUY',1,'EXECUTE_SIMULE','ADMISSIBLE',?)", (exec_status,))


class DelistingJournalTests(unittest.TestCase):
    def test_review_case_future_consideration_does_not_alter_past_journal(self):
        _, base = run()
        ds = fresh_copy(demo_dataset())
        ds.securities["FXMU"].update(delisting_cash_per_share=20.0, delisting_source="x",
                                     delisting_source_date=date(2025, 1, 1), delisting_cash_date=date(2024, 6, 28))
        _, alt = run(ds=ds)
        q = "SELECT portfolio, date, ticker, event, qty, value_per_share, cash_received, source FROM corporate_events " \
            "WHERE date < '2025-01-02' ORDER BY 1, 2"
        self.assertEqual([tuple(r) for r in base.conn.execute(q)], [tuple(r) for r in alt.conn.execute(q)])

    def test_published_consideration_is_mentioned_once_known(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXMU"].update(delisting_cash_per_share=5.0, delisting_source="x",
                                     delisting_source_date=date(2024, 6, 1), delisting_cash_date=date(2024, 7, 15))
        _, store = run(ds=ds)
        src = {r[0] for r in store.conn.execute("SELECT source FROM corporate_events WHERE date='2024-06-28'")}
        self.assertEqual(src, {"contrepartie publiée le 2024-06-01, paiement annoncé le 2024-07-15"})


class LoaderTests(unittest.TestCase):
    def test_review_case_negative_volume_rejected(self):
        for value in ("-1", "1.5", ""):
            d = _copy_demo(self)
            _set_price_field(d, 1, "volume", value)
            with self.assertRaises(DataError, msg=value):
                load_dataset(d)

    def test_review_case_real_manifest_with_demo_sources_rejected(self):
        d = _copy_demo(self)
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        m["nature"] = "REEL"
        (d / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        with self.assertRaises(DataError):
            load_dataset(d)


if __name__ == "__main__":
    unittest.main()
