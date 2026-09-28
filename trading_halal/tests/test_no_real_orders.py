"""Point critique n° 2 : aucun ordre réel ne peut partir."""
import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT, demo_dataset, demo_ruleset, fresh_copy, run

from halal_sim.backtest import PolicyError

FORBIDDEN = {"socket", "urllib", "http", "requests", "httpx", "aiohttp", "websocket", "websockets", "ftplib",
             "smtplib", "telnetlib", "ssl", "subprocess", "asyncio", "ccxt", "alpaca", "alpaca_trade_api",
             "ib_insync", "ibapi", "ib_async", "degiro_connector", "saxo_openapi", "oandapyV20", "MetaTrader5",
             "yfinance"}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.add(node.module.split(".")[0])
    return mods


class NoRealOrderTests(unittest.TestCase):
    def test_package_imports_no_network_or_broker_library(self):
        for py in (ROOT / "halal_sim").glob("*.py"):
            bad = _imports(py) & FORBIDDEN
            if py.name == "safety.py":
                bad -= {"socket"}  # importé uniquement pour COUPER le réseau
            self.assertEqual(bad, set(), f"{py.name} importe {bad}")

    def test_package_reads_no_credentials(self):
        for py in (ROOT / "halal_sim").glob("*.py"):
            src = py.read_text(encoding="utf-8")
            for needle in ("environ", "getenv", "api_key", "API_KEY", "secret", "token"):
                self.assertNotIn(needle, src, f"{py.name} contient {needle!r}")

    def test_network_guard_blocks_connections(self):
        code = ("import sys; sys.path.insert(0, %r)\n"
                "from halal_sim.safety import forbid_network, NetworkBlockedError\n"
                "forbid_network()\nimport socket, urllib.request\n"
                "for f in (lambda: socket.create_connection(('example.com', 443)),\n"
                "          lambda: socket.socket().connect(('93.184.216.34', 443)),\n"
                "          lambda: urllib.request.urlopen('https://example.com', timeout=2)):\n"
                "    try:\n        f(); print('CONNECTED'); sys.exit(1)\n"
                "    except NetworkBlockedError: pass\n"
                "    except Exception as e:\n"
                "        if 'Accès réseau interdit' not in repr(e): print('OTHER', e); sys.exit(2)\n"
                "print('BLOCKED')\n") % str(ROOT)
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("BLOCKED", out.stdout)

    def test_cli_end_to_end_runs_with_network_cut(self):
        cfg = json.loads((ROOT / "config" / "simulation.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            cfg["db_path"] = str(Path(tmp) / "t.sqlite")
            cfg["report_path"] = str(Path(tmp) / "r.md")
            cfg_path = Path(tmp) / "c.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            out = subprocess.run([sys.executable, "-m", "halal_sim", "--config", str(cfg_path), "run", "--no-sensitivity"],
                                 cwd=ROOT, capture_output=True, text=True, timeout=120)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            report = (Path(tmp) / "r.md").read_text(encoding="utf-8")
            self.assertIn("Aucun courtier connecté, aucun ordre réel envoyé", report)
            self.assertNotIn("ÉCHEC", report)

    def test_real_data_refused_with_demo_or_unvalidated_ruleset(self):
        ds = fresh_copy(demo_dataset())
        ds.manifest["nature"] = "REEL"
        with self.assertRaises(PolicyError):
            run(ds=ds, ruleset=demo_ruleset())
        rs = dict(demo_ruleset(), demo_only=False, validated=False)
        with self.assertRaises(PolicyError):
            run(ds=ds, ruleset=rs)

    def test_every_run_is_flagged_simulation_only(self):
        _, store = run()
        self.assertEqual(store.conn.execute("SELECT simulation_only FROM runs").fetchone()[0], 1)
        with self.assertRaises(Exception):
            store.conn.execute("UPDATE runs SET simulation_only=0")


if __name__ == "__main__":
    unittest.main()
