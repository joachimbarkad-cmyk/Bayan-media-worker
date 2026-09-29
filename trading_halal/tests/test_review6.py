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

    def _cli(self, tmp, db, *extra):
        cfg = json.loads((ROOT / "config" / "simulation.json").read_text(encoding="utf-8"))
        cfg.update(db_path=str(db), report_path=str(Path(tmp) / "r.md"))
        (Path(tmp) / "c.json").write_text(json.dumps(cfg), encoding="utf-8")
        return subprocess.run([sys.executable, "-m", "halal_sim", "--config", str(Path(tmp) / "c.json"), "run",
                               "--no-sensitivity", *extra], cwd=ROOT, capture_output=True, text=True, timeout=180)

    def test_review7_old_database_refused_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._old_db(tmp)
            out = self._cli(tmp, db)
            self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
            self.assertIn("REFUS", out.stdout)
            self.assertEqual(list(Path(tmp).glob("*.bak")), [])
            con = sqlite3.connect(db)
            self.assertEqual(len(con.execute("PRAGMA table_info(orders)").fetchall()), 15)  # intacte
            con.close()
            self.assertIn("--db", out.stdout)

    def test_cli_runs_on_another_path_and_leaves_old_database_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._old_db(tmp)
            before = db.read_bytes()
            out = self._cli(tmp, db, "--db", str(Path(tmp) / "nouvelle.sqlite"))
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertEqual(db.read_bytes(), before)
            self.assertIn("modèle d'exécution rétrospectif", (Path(tmp) / "r.md").read_text(encoding="utf-8"))

    def test_review7_two_snapshots_in_the_same_second_never_overwrite(self):
        from halal_sim.db import snapshot_database
        with tempfile.TemporaryDirectory() as tmp:
            db = self._old_db(tmp)
            names = [snapshot_database(db), snapshot_database(db)]
            self.assertEqual(len(set(names)), 2)
            self.assertTrue(db.exists())

    def test_snapshot_includes_wal_content_and_never_touches_original(self):
        from halal_sim.db import snapshot_database
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "w.sqlite"
            writer = sqlite3.connect(db)
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("PRAGMA wal_autocheckpoint=0")
            writer.execute("CREATE TABLE t(v)")
            writer.execute("INSERT INTO t VALUES('dans le wal')")
            writer.commit()
            snap = snapshot_database(db)
            self.assertTrue(db.exists() and Path(str(db) + "-wal").exists())
            con = sqlite3.connect(snap)
            self.assertEqual(con.execute("SELECT v FROM t").fetchone()[0], "dans le wal")
            con.close()

    def test_review8_writer_keeps_working_after_snapshot(self):
        """Cas signalé : une connexion ouverte écrivait dans une base supprimée. L'original reste désormais en place ;
        l'instantané, lui, ne contient pas les écritures postérieures (comportement documenté)."""
        from halal_sim.db import snapshot_database
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "c.sqlite"
            writer = sqlite3.connect(db)
            writer.execute("CREATE TABLE t(v)")
            writer.execute("INSERT INTO t VALUES('avant')")
            writer.commit()
            snap = snapshot_database(db)
            writer.execute("INSERT INTO t VALUES('apres')")
            writer.commit()
            self.assertEqual([r[0] for r in writer.execute("SELECT v FROM t ORDER BY rowid")], ["avant", "apres"])
            writer.close()
            con = sqlite3.connect(snap)
            self.assertEqual([r[0] for r in con.execute("SELECT v FROM t")], ["avant"])
            con.close()

if __name__ == "__main__":
    unittest.main()
