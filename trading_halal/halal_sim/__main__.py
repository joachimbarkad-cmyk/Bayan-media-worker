"""Ligne de commande.

  python3 -m halal_sim run            # simulation complète + rapport
  python3 -m halal_sim check-data     # validation des fichiers de données
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import PROJECT_ROOT
from .safety import forbid_network


def _path(p: str) -> Path:
    p = Path(p)
    return p if p.is_absolute() else PROJECT_ROOT / p


def load_config(path: str) -> dict:
    return json.loads(_path(path).read_text(encoding="utf-8"))


def cmd_check_data(args) -> int:
    from .data import load_dataset
    cfg = load_config(args.config)
    ds = load_dataset(_path(args.dataset or cfg["dataset_dir"]))
    n_bars = sum(len(b) for b in ds.bars.values())
    print(f"Jeu de données '{ds.manifest.get('name')}' — nature : {ds.nature}")
    if ds.manifest.get("warning"):
        print(f"  ! {ds.manifest['warning']}")
    print(f"  {len(ds.securities)} titres, {n_bars} barres de prix, {ds.calendar[0]} → {ds.calendar[-1]}")
    for t in ds.tickers:
        f = ds.fundamentals[t]
        print(f"  {t:6} {ds.securities[t]['instrument_type']:28} {len(ds.bars[t]):5} prix  "
              f"{len(f):3} états financiers  {';'.join(ds.securities[t]['activity_codes'])}")
    print("Validation OK.")
    return 0


def cmd_run(args) -> int:
    from .backtest import run_backtest
    from .data import load_dataset
    from .db import Store
    from .report import build_report, run_checks
    from .screening import load_ruleset

    cfg = load_config(args.config)
    ds = load_dataset(_path(cfg["dataset_dir"]))
    ruleset = load_ruleset(_path(cfg["ruleset"]))
    store = Store(_path(cfg["db_path"]))
    capital = args.capital or cfg["initial_capital"]
    main = run_backtest(ds, cfg, ruleset, store, capital=capital, label="principal")
    sens_ids = []
    if not args.no_sensitivity:
        for c in cfg.get("sensitivity_capitals", []):
            sens_ids.append(run_backtest(ds, cfg, ruleset, store, capital=c, label=f"sensibilite_{c}",
                                         parent_run_id=main.run_id).run_id)
    store.commit()
    checks = run_checks(store.conn, main.run_id)
    report = build_report(store.conn, main.run_id, sens_ids, checks)
    out = _path(cfg["report_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    print(f"Simulation n° {main.run_id} ({ds.nature}) {main.start} → {main.end}, capital {capital} {cfg['currency']}")
    for pf, m in main.metrics.items():
        print(f"  {pf:10} rendement {m['rendement_total_pct']:7.2f} %   baisse max {m['baisse_max_pct']:7.2f} %   "
              f"coûts {m['couts_total_pct_capital']:5.2f} % du capital   ordres {m['nb_achats'] + m['nb_ventes']}")
    failed = [n for n, ok, _ in checks if not ok]
    print(f"Vérifications : {len(checks) - len(failed)}/{len(checks)} OK" + (f" — ÉCHECS : {failed}" if failed else ""))
    print(f"Rapport : {out}\nBase SQLite : {_path(cfg['db_path'])}")
    if ds.nature == "FICTIF":
        print("RAPPEL : données fictives — ces chiffres ne disent rien de la rentabilité réelle.")
    return 1 if failed else 0


def main(argv=None) -> int:
    forbid_network()
    p = argparse.ArgumentParser(prog="halal_sim", description="Simulateur de portefeuille fictif (aucun ordre réel)")
    p.add_argument("--config", default="config/simulation.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="Lancer la simulation et produire le rapport")
    r.add_argument("--capital", type=float, help="Capital initial (remplace la configuration)")
    r.add_argument("--no-sensitivity", action="store_true", help="Ne pas lancer les simulations de sensibilité au capital")
    c = sub.add_parser("check-data", help="Valider les fichiers de données")
    c.add_argument("--dataset", help="Dossier du jeu de données (défaut : celui de la configuration)")
    args = p.parse_args(argv)
    return {"run": cmd_run, "check-data": cmd_check_data}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
