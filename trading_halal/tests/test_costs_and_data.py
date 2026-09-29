import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from helpers import ROOT, run

from halal_sim.broker import CostModel, ForbiddenOrderError, PaperBroker
from halal_sim.data import DataError, load_dataset
from halal_sim.screening import ADMISSIBLE


class CostTests(unittest.TestCase):
    def test_fee_and_slippage_are_adverse(self):
        c = CostModel(fixed_fee=1.0, pct_fee=0.001, min_fee=2.0, slippage_bps=10)
        self.assertEqual(c.fee(100), 2.0)                     # minimum appliqué
        self.assertAlmostEqual(c.fee(10_000), 11.0)
        self.assertAlmostEqual(c.fill_price(100, "BUY"), 100.1)
        self.assertAlmostEqual(c.fill_price(100, "SELL"), 99.9)
        self.assertAlmostEqual(CostModel(1, 0, 1, 10).roundtrip_cost_pct(200), 1.2)

    def test_whole_shares_no_margin_no_short(self):
        br = PaperBroker("t", 100.0, CostModel(1, 0, 1, 0))
        self.assertEqual(br.max_affordable_qty(33.5), 2)       # 3 x 33.5 + 1 > 100
        with self.assertRaises(ForbiddenOrderError):
            br.buy("X", 3, 33.5, date(2024, 1, 1), date(2024, 1, 2), ADMISSIBLE, "t", status_at_execution=ADMISSIBLE)
        with self.assertRaises(ValueError):
            br.buy("X", 0, 33.0, date(2024, 1, 1), date(2024, 1, 2), ADMISSIBLE, "t", status_at_execution=ADMISSIBLE)
        with self.assertRaises(ForbiddenOrderError):
            br.sell("X", 1, 33.0, date(2024, 1, 1), date(2024, 1, 2), ADMISSIBLE, "t")

    def test_small_capital_trades_are_refused_as_not_worth_it(self):
        res, store = run(capital=500)
        c = store.conn
        n = c.execute("SELECT COUNT(*) FROM decisions WHERE portfolio='strategie' AND reason_code IN "
                      "('REFUS_COUT_DISPROPORTIONNE','REFUS_CAPITAL_INSUFFISANT')").fetchone()[0]
        self.assertGreater(n, 0)
        detail = c.execute("SELECT detail FROM decisions WHERE reason_code='REFUS_COUT_DISPROPORTIONNE' LIMIT 1").fetchone()[0]
        self.assertIn("peu pertinente", detail)

    def test_costs_are_recorded_for_every_fill(self):
        _, store = run()
        rows = store.conn.execute("SELECT fees, slippage_cost FROM orders WHERE status='EXECUTE_SIMULE'").fetchall()
        self.assertTrue(rows)
        self.assertTrue(all(r[0] >= 1.0 and r[1] > 0 for r in rows))


class DataValidationTests(unittest.TestCase):
    def _copy(self):
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT / "data" / "demo", tmp / "d")
        self.addCleanup(shutil.rmtree, tmp)
        return tmp / "d"

    def test_demo_dataset_is_declared_fictitious(self):
        ds = load_dataset(ROOT / "data" / "demo")
        self.assertEqual(ds.nature, "FICTIF")
        self.assertTrue(all("(fictif)" in s["name"] for s in ds.securities.values()))

    def test_missing_manifest_rejected(self):
        d = self._copy()
        (d / "manifest.json").unlink()
        with self.assertRaises(DataError):
            load_dataset(d)

    def test_inconsistent_price_rejected(self):
        d = self._copy()
        p = d / "prices_FICTIF.csv"
        lines = p.read_text(encoding="utf-8").splitlines()
        parts = lines[1].split(",")
        parts[4] = str(float(parts[5]) * 2)  # plus bas > clôture
        lines[1] = ",".join(parts)
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(DataError):
            load_dataset(d)

    def test_fundamentals_without_source_rejected(self):
        d = self._copy()
        p = d / "fundamentals_FICTIF.csv"
        lines = p.read_text(encoding="utf-8").splitlines()
        lines[1] = lines[1].rsplit(",", 1)[0] + ","
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(DataError):
            load_dataset(d)

    def test_invalid_nature_rejected(self):
        d = self._copy()
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        m["nature"] = "PEUT_ETRE"
        (d / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        with self.assertRaises(DataError):
            load_dataset(d)


if __name__ == "__main__":
    unittest.main()
