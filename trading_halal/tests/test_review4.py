"""Cas signalés par la revue n° 4 : contrepartie de radiation publiée ou payée plus tard, achat le jour de la
radiation, devises des états financiers, exécution sans volume."""
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from helpers import ROOT, demo_dataset, demo_ruleset, fresh_copy, run

from halal_sim.data import Bar, DataError, PointInTimeView, load_dataset
from halal_sim.screening import INCERTAIN, screen_security


def _copy_demo(test):
    tmp = Path(tempfile.mkdtemp())
    shutil.copytree(ROOT / "data" / "demo", tmp / "d")
    test.addCleanup(shutil.rmtree, tmp)
    return tmp / "d"


def _set_security_fields(d, ticker, **fields):
    p = d / "securities_FICTIF.csv"
    lines = p.read_text(encoding="utf-8").splitlines()
    header = lines[0].split(",")
    for i, line in enumerate(lines[1:], start=1):
        parts = line.split(",")
        if parts[0] == ticker:
            for k, v in fields.items():
                parts[header.index(k)] = v
            lines[i] = ",".join(parts)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


class DelistingConsiderationTimingTests(unittest.TestCase):
    def test_review_case_consideration_published_later_is_not_credited_early(self):
        base_res, base = run()
        ds = fresh_copy(demo_dataset())
        ds.securities["FXMU"].update(delisting_cash_per_share=20.0, delisting_source="Document fictif (test)",
                                     delisting_source_date=date(2025, 1, 1), delisting_cash_date=date(2024, 6, 28))
        res, store = run(ds=ds)
        c = store.conn
        credited = c.execute("SELECT portfolio, date, cash_received FROM corporate_events "
                             "WHERE event='RADIATION_CONTREPARTIE_DOCUMENTEE'").fetchall()
        self.assertTrue(credited)
        for pf, d, cash in credited:
            self.assertEqual(d, "2025-01-02")  # premier jour de bourse APRÈS la publication (règle J+1)
            self.assertAlmostEqual(cash, 200.0)
        q = "SELECT portfolio, date, equity FROM equity WHERE date < '2025-01-02' ORDER BY 1, 2"
        self.assertEqual([tuple(r) for r in c.execute(q)], [tuple(r) for r in base.conn.execute(q)])

    def test_payment_date_after_publication_is_respected(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXMU"].update(delisting_cash_per_share=5.0, delisting_source="Offre fictive (test)",
                                     delisting_source_date=date(2024, 5, 1), delisting_cash_date=date(2024, 9, 30))
        _, store = run(ds=ds)
        dates = {r[0] for r in store.conn.execute(
            "SELECT date FROM corporate_events WHERE event='RADIATION_CONTREPARTIE_DOCUMENTEE'")}
        self.assertEqual(dates, {"2024-09-30"})

    def test_loader_requires_dated_consideration(self):
        for fields in ({"delisting_cash_per_share": "5", "delisting_source": "x"},
                       {"delisting_cash_per_share": "5", "delisting_source": "x", "delisting_source_date": "2024-05-01"},
                       {"delisting_cash_per_share": "5", "delisting_source": "x", "delisting_source_date": "2024-05-01",
                        "delisting_cash_date": "2024-06-01"},  # paiement avant la radiation
                       {"delisting_source_date": "2024-05-01"}):
            d = _copy_demo(self)
            _set_security_fields(d, "FXMU", **fields)
            with self.assertRaises(DataError, msg=str(fields)):
                load_dataset(d)


class NoTradeOnOrAfterDelistingTests(unittest.TestCase):
    def test_review_case_loader_refuses_bar_on_delisting_day(self):
        d = _copy_demo(self)
        _set_security_fields(d, "FXALP", delisted_date="2021-11-01")
        with self.assertRaises(DataError):
            load_dataset(d)

    def test_review_case_engine_refuses_buy_on_delisting_day_even_with_a_price(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXALP"]["delisted_date"] = date(2021, 11, 1)  # construit en mémoire : barre du jour conservée
        _, store = run(ds=ds)  # ne doit plus lever d'erreur
        c = store.conn
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE ticker='FXALP' AND status='EXECUTE_SIMULE'")
                         .fetchone()[0], 0)
        self.assertGreater(c.execute("SELECT COUNT(*) FROM orders WHERE ticker='FXALP' AND "
                                     "reason='HORS_UNIVERS_A_L_EXECUTION'").fetchone()[0], 0)


class CurrencyTests(unittest.TestCase):
    def test_review_case_fundamentals_in_other_currency_are_not_admissible(self):
        ds = fresh_copy(demo_dataset())
        ds.fundamentals["FXALP"][-1]["currency"] = "JPY"
        r = screen_security(PointInTimeView(ds, date(2025, 11, 28)), "FXALP", demo_ruleset())
        self.assertEqual(r.status, INCERTAIN)
        self.assertIn("DONNEE_INVALIDE", r.incertain_causes)
        self.assertTrue(any("devise" in m for m in r.reasons))


class VolumeTests(unittest.TestCase):
    def _with_volume(self, ticker, d, volume):
        ds = fresh_copy(demo_dataset())
        ds.bars[ticker] = [Bar(b.date, b.open, b.high, b.low, b.close, volume) if b.date == d else b
                           for b in ds.bars[ticker]]
        return fresh_copy(ds)

    def test_review_case_no_fill_on_zero_volume_day(self):
        _, base = run()
        row = base.conn.execute("SELECT ticker, execution_date, side FROM orders WHERE status='EXECUTE_SIMULE' "
                                "AND portfolio='strategie' AND side='SELL' ORDER BY execution_date LIMIT 1").fetchone()
        t, day = row[0], date.fromisoformat(row[1])
        _, store = run(ds=self._with_volume(t, day, 0))
        c = store.conn
        self.assertEqual(c.execute("SELECT COUNT(*) FROM orders WHERE ticker=? AND execution_date=? AND "
                                   "status='EXECUTE_SIMULE' AND portfolio='strategie'", (t, row[1])).fetchone()[0], 0)
        later = c.execute("SELECT MIN(execution_date) FROM orders WHERE ticker=? AND side='SELL' AND "
                          "status='EXECUTE_SIMULE' AND portfolio='strategie' AND execution_date > ?", (t, row[1])).fetchone()[0]
        self.assertIsNotNone(later)  # vente reportée au jour suivant

    def test_quantity_capped_by_previous_day_volume(self):
        _, base = run()
        t, ex, qty = base.conn.execute("SELECT ticker, execution_date, qty FROM orders WHERE status='EXECUTE_SIMULE' "
                                       "AND portfolio='strategie' AND side='BUY' AND qty >= 4 LIMIT 1").fetchone()
        prev = demo_dataset().last_bar_before(t, date.fromisoformat(ex)).date
        q = ("SELECT status, qty, reason FROM orders WHERE ticker=? AND execution_date=? AND side='BUY' AND "
             "portfolio='strategie'")
        _, store = run(ds=self._with_volume(t, prev, 120))  # 5 % de 120 = 6 actions au plus
        self.assertEqual(tuple(store.conn.execute(q, (t, ex)).fetchone())[:2], ("EXECUTE_SIMULE", 6))
        _, store = run(ds=self._with_volume(t, prev, 40))   # 2 actions : plafonné, puis refusé pour coût
        status, qty, reason = store.conn.execute(q, (t, ex)).fetchone()
        self.assertEqual((status, qty), ("REJETE", 2))
        self.assertIn("COUT_DISPROPORTIONNE", reason)


if __name__ == "__main__":
    unittest.main()
