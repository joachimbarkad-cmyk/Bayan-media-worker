"""Journal SQLite : chaque exécution, filtrage, décision, ordre simulé et résultat."""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  label TEXT NOT NULL,
  parent_run_id INTEGER,
  simulation_only INTEGER NOT NULL DEFAULT 1 CHECK (simulation_only = 1),
  dataset_name TEXT, dataset_nature TEXT NOT NULL,
  data_hashes TEXT, code_hash TEXT,
  ruleset_id TEXT, ruleset_validated INTEGER, ruleset_json TEXT,
  config_json TEXT, initial_capital REAL, currency TEXT,
  start_date TEXT, end_date TEXT
);
CREATE TABLE IF NOT EXISTS screenings(
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  decision_date TEXT NOT NULL, ticker TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('ADMISSIBLE','EXCLU','INCERTAIN')),
  reasons_json TEXT NOT NULL, ratios_json TEXT,
  fundamentals_period_end TEXT, fundamentals_available_date TEXT, fundamentals_source TEXT,
  activity_codes TEXT, activity_available_date TEXT, activity_source TEXT, incertain_causes TEXT,
  ruleset_id TEXT NOT NULL, max_data_date TEXT,
  CHECK (max_data_date IS NULL OR max_data_date <= decision_date)
);
CREATE TABLE IF NOT EXISTS decisions(
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  portfolio TEXT NOT NULL, decision_date TEXT NOT NULL, ticker TEXT NOT NULL,
  screening_status TEXT NOT NULL, signal TEXT NOT NULL, final_action TEXT NOT NULL,
  reason_code TEXT NOT NULL, detail TEXT, inputs_json TEXT, max_data_date TEXT,
  CHECK (max_data_date IS NULL OR max_data_date <= decision_date),
  CHECK (NOT (final_action = 'ACHAT' AND screening_status <> 'ADMISSIBLE'))
);
CREATE TABLE IF NOT EXISTS orders(
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  portfolio TEXT NOT NULL, decision_date TEXT NOT NULL, execution_date TEXT,
  ticker TEXT NOT NULL, side TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
  qty INTEGER, ref_price REAL, exec_price REAL, notional REAL, fees REAL, slippage_cost REAL,
  status TEXT NOT NULL CHECK (status IN ('EXECUTE_SIMULE','REJETE')),
  reason TEXT, screening_status_at_decision TEXT NOT NULL, screening_status_at_execution TEXT,
  CHECK (execution_date IS NULL OR execution_date > decision_date)
);
CREATE TRIGGER IF NOT EXISTS buy_requires_admissible BEFORE INSERT ON orders
WHEN NEW.side = 'BUY' AND NEW.status = 'EXECUTE_SIMULE' AND (NEW.screening_status_at_decision <> 'ADMISSIBLE'
     OR NEW.screening_status_at_execution IS NULL OR NEW.screening_status_at_execution <> 'ADMISSIBLE')
BEGIN SELECT RAISE(ABORT, 'Achat interdit : statut non ADMISSIBLE à la décision ou à l''exécution'); END;
CREATE TABLE IF NOT EXISTS equity(
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  portfolio TEXT NOT NULL, date TEXT NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, equity REAL NOT NULL,
  frozen_value_last_close REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS corporate_events(
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  portfolio TEXT NOT NULL, date TEXT NOT NULL, ticker TEXT NOT NULL,
  event TEXT NOT NULL CHECK (event IN ('RADIATION_VALEUR_INCONNUE','RADIATION_CONTREPARTIE_DOCUMENTEE')),
  qty INTEGER NOT NULL, value_per_share REAL, cash_received REAL NOT NULL DEFAULT 0, source TEXT
);
CREATE TABLE IF NOT EXISTS metrics(
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  portfolio TEXT NOT NULL, key TEXT NOT NULL, value REAL
);
CREATE INDEX IF NOT EXISTS idx_dec ON decisions(run_id, portfolio, decision_date);
CREATE INDEX IF NOT EXISTS idx_scr ON screenings(run_id, decision_date);
"""


def _s(v):
    return v.isoformat() if isinstance(v, date) else v


# Version du schéma, enregistrée dans PRAGMA user_version. À incrémenter à chaque changement de SCHEMA.
# Une base d'une autre version n'est jamais modifiée, déplacée ni supprimée : StoreSchemaError est levée ; la ligne
# de commande indique d'utiliser un autre chemin (--db) et propose un instantané (snapshot-db).
SCHEMA_VERSION = 6


class StoreSchemaError(RuntimeError):
    def __init__(self, path, found):
        super().__init__(f"Base {path} au schéma v{found}, incompatible avec le schéma v{SCHEMA_VERSION} de cette version")
        self.path, self.found = path, found


def snapshot_database(path: Path) -> Path:
    """INSTANTANÉ vérifié d'une base : copie cohérente par l'API de sauvegarde SQLite (elle intègre un éventuel journal
    WAL) vers un nom réservé de façon exclusive (jamais d'écrasement). L'original et ses fichiers -wal / -shm ne sont
    JAMAIS modifiés ni supprimés. Si d'autres connexions écrivent encore dans la base, leurs écritures postérieures ne
    figurent pas dans l'instantané : fermer les autres programmes avant de s'y fier comme copie complète."""
    from datetime import datetime
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    # URI construite à partir du chemin ENCODÉ (?, #, % et espaces), sinon « old?name » serait lu comme « old ».
    src = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    version = src.execute("PRAGMA user_version").fetchone()[0]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    n = 0
    while True:
        target = path.with_name(f"{path.name}.instantane-v{version}-{stamp}-{n}.sqlite")
        try:
            with open(target, "xb"):  # réservation exclusive du nom
                break
        except FileExistsError:
            n += 1
    dst = sqlite3.connect(str(target))
    try:
        src.backup(dst)
        if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError(f"Instantané {target} invalide")
    finally:
        dst.close()
        src.close()
    return target


class Store:
    def __init__(self, path: str | Path):
        path = Path(path)
        if str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        has_tables = self.conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0] > 0
        found = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if has_tables and found != SCHEMA_VERSION:
            self.conn.close()
            raise StoreSchemaError(path, found)
        self.conn.executescript(SCHEMA)
        self.conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def start_run(self, *, label, parent_run_id, ds, ruleset, config, code_hash, capital) -> int:
        cur = self.conn.execute(
            "INSERT INTO runs(created_at,label,parent_run_id,dataset_name,dataset_nature,data_hashes,code_hash,"
            "ruleset_id,ruleset_validated,ruleset_json,config_json,initial_capital,currency) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), label, parent_run_id,
             ds.manifest.get("name"), ds.nature, json.dumps(ds.file_hashes), code_hash, ruleset["id"],
             int(bool(ruleset["validated"])), json.dumps(ruleset, ensure_ascii=False),
             json.dumps(config, ensure_ascii=False), capital, config.get("currency", "")))
        return cur.lastrowid

    def finish_run(self, run_id, start, end):
        self.conn.execute("UPDATE runs SET start_date=?, end_date=? WHERE run_id=?", (_s(start), _s(end), run_id))
        self.conn.commit()

    def add_screening(self, run_id, r):
        ref, act = r.fundamentals_ref or {}, r.activity_ref or {}
        self.conn.execute(
            "INSERT INTO screenings VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, _s(r.as_of), r.ticker, r.status, json.dumps(r.reasons, ensure_ascii=False),
             json.dumps({k: round(v, 6) for k, v in r.ratios.items()}), ref.get("period_end"),
             ref.get("available_date"), ref.get("source"), ";".join(act.get("codes", [])),
             act.get("available_date"), act.get("source"), ";".join(r.incertain_causes), r.ruleset_id,
             _s(r.max_date_read)))

    def add_decision(self, run_id, portfolio, decision_date, status, dec, final_action, reason_code, detail):
        self.conn.execute(
            "INSERT INTO decisions VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, portfolio, _s(decision_date), dec.ticker, status, dec.signal, final_action, reason_code, detail,
             json.dumps(dec.inputs, ensure_ascii=False), _s(dec.max_date_read)))

    def add_fill(self, run_id, f):
        self.conn.execute(
            "INSERT INTO orders VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, f.portfolio, _s(f.decision_date), _s(f.execution_date), f.ticker, f.side, f.qty, f.ref_price,
             f.exec_price, f.notional, f.fees, f.slippage_cost, "EXECUTE_SIMULE", f.reason, f.screening_status,
             f.screening_status_exec or None))

    def add_rejected_order(self, run_id, portfolio, decision_date, execution_date, ticker, side, qty, status, reason):
        self.conn.execute(
            "INSERT INTO orders(run_id,portfolio,decision_date,execution_date,ticker,side,qty,status,reason,"
            "screening_status_at_decision) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (run_id, portfolio, _s(decision_date), _s(execution_date), ticker, side, qty, "REJETE", reason, status))

    def add_equity_rows(self, run_id, rows):
        self.conn.executemany("INSERT INTO equity VALUES(?,?,?,?,?,?,?)",
                              [(run_id, p, _s(d), c, pv, e, fz) for p, d, c, pv, e, fz in rows])

    def add_corporate_event(self, run_id, portfolio, d, ticker, event, qty, value_per_share, cash, source):
        self.conn.execute("INSERT INTO corporate_events VALUES(?,?,?,?,?,?,?,?,?)",
                          (run_id, portfolio, _s(d), ticker, event, qty, value_per_share, cash, source))

    def add_metrics(self, run_id, portfolio, metrics: dict):
        self.conn.executemany("INSERT INTO metrics VALUES(?,?,?,?)",
                              [(run_id, portfolio, k, v) for k, v in metrics.items()])

    def commit(self):
        self.conn.commit()
