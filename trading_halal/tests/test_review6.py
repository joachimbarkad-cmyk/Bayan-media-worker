"""Revue n° 6 côté simulation : base SQLite d'une version antérieure, intitulé du modèle d'exécution.
(Les cas d'audit documentaire de la même revue sont dans test_audit.Review6AuditTests.)"""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

from halal_sim.db import SCHEMA_VERSION, Store, StoreSchemaError

# Schéma des commandes tel qu'en V1.4 (15 colonnes, sans screening_status_at_execution), sans numéro de version.
V14_ORDERS = """CREATE TABLE orders(run_id INTEGER, portfolio TEXT, decision_date TEXT, execution_date TEXT, ticker TEXT,
side TEXT, qty INTEGER, ref_price REAL, exec_price REAL, notional REAL, fees REAL, slippage_cost REAL, status TEXT,
reason TEXT, screening_status_at_decision TEXT)"""


class SchemaVersionTests(unittest.TestCase):
    def _old_db(self, tmp):
        db = Path(tmp) / "s.sqlite"
        con = sqlite3.connect(db)
        con.execute(V14_ORDERS)
        con.commit()
        con.close()
        return db

    def test_review_case_old_database_is_detected_not_corrupted(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._old_db(tmp)
            with self.assertRaises(StoreSchemaError):
                Store(db)
            con = sqlite3.connect(db)  # base intacte : toujours 15 colonnes
            self.assertEqual(len(con.execute("PRAGMA table_info(orders)").fetchall()), 15)
            con.close()

    def test_new_database_gets_current_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Store(Path(tmp) / "n.sqlite")
            self.assertEqual(s.conn.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
            s.conn.close()
            Store(Path(tmp) / "n.sqlite").conn.close()  # réouverture sans erreur

    def test_cli_archives_old_database_and_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._old_db(tmp)
            cfg = json.loads((ROOT / "config" / "simulation.json").read_text(encoding="utf-8"))
            cfg.update(db_path=str(db), report_path=str(Path(tmp) / "r.md"))
            (Path(tmp) / "c.json").write_text(json.dumps(cfg), encoding="utf-8")
            out = subprocess.run([sys.executable, "-m", "halal_sim", "--config", str(Path(tmp) / "c.json"), "run",
                                  "--no-sensitivity"], cwd=ROOT, capture_output=True, text=True, timeout=180)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("archivée", out.stdout)
            backups = list(Path(tmp).glob("s.sqlite.schema-v0-*.bak"))
            self.assertEqual(len(backups), 1)
            con = sqlite3.connect(backups[0])
            self.assertEqual(len(con.execute("PRAGMA table_info(orders)").fetchall()), 15)  # ancienne base conservée
            con.close()
            report = (Path(tmp) / "r.md").read_text(encoding="utf-8")
            self.assertIn("modèle d'exécution rétrospectif", report)


if __name__ == "__main__":
    unittest.main()
