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
        f, acts = ds.fundamentals[t], ds.activities[t]
        hist = " → ".join(f"{a['available_date']}:{';'.join(a['activity_codes']) or '?'}" for a in acts) or "aucune fiche"
        print(f"  {t:6} {ds.securities[t]['instrument_type']:28} {ds.securities[t]['currency']}  {len(ds.bars[t]):5} prix  "
              f"{len(f):3} états financiers  activité {hist}")
    print("Contrôles de format et de cohérence réussis. Cela ne prouve ni l'authenticité, ni l'exactitude, ni "
          "l'exhaustivité des données : leur provenance reste à auditer.")
    return 0


def cmd_audit_docs(args) -> int:
    from .audit import audit_folder
    res = audit_folder(_path(args.folder))
    print(f"Dossier d'audit documentaire — nature : {res.nature}")
    print("  " + ", ".join(f"{k} : {v}" for k, v in res.counts.items()))
    for e in res.errors:
        print(f"  ERREUR   {e}")
    for u in res.unknowns:
        print(f"  INCONNUE {u}")
    print(f"{len(res.errors)} erreur(s) bloquante(s), {len(res.unknowns)} inconnue(s) signalée(s), "
          f"{res.reconciled} rapproché(s) à la main et {res.reconciled_auto} automatiquement, sur {res.to_reconcile} fait(s) normalisé(s).")
    print(f"VERDICT : {res.verdict}")
    print("Ce contrôle vérifie la forme, la chronologie et l'intégrité des copies locales ; il ne prouve pas l'exactitude "
          "des valeurs et ne produit aucun statut religieux.")
    return 0 if res.ok else 1


class IncompatibleDatabase(SystemExit):
    pass


def _open_store(path: Path):
    """Ouvre la base. Une base d'un autre schéma est REFUSÉE et laissée intacte (jamais déplacée ni supprimée)."""
    from .db import Store, StoreSchemaError
    try:
        return Store(path)
    except StoreSchemaError as exc:
        print(f"REFUS : la base {path} est au schéma v{exc.found}, incompatible avec cette version. Rien n'a été "
              "modifié. Choisissez un autre fichier : --db CHEMIN (ou db_path dans la configuration). Pour garder une "
              f"copie de l'ancienne base : python3 -m halal_sim snapshot-db {path}")
        raise IncompatibleDatabase(2)


def cmd_snapshot_db(args) -> int:
    from .db import snapshot_database
    target = snapshot_database(_path(args.path))
    print(f"Instantané vérifié : {target}. L'original n'a pas été modifié. Si un autre programme écrivait encore dans "
          "la base, ses écritures postérieures ne figurent pas dans cet instantané.")
    return 0


def cmd_run(args) -> int:
    from .backtest import run_backtest
    from .data import load_dataset
    from .db import Store
    from .report import build_report, run_checks
    from .screening import load_ruleset

    cfg = load_config(args.config)
    ds = load_dataset(_path(cfg["dataset_dir"]))
    ruleset = load_ruleset(_path(args.ruleset or cfg["ruleset"]))
    db_path = _path(args.db) if args.db else _path(cfg["db_path"])
    store = _open_store(db_path)
    capital = args.capital or cfg["initial_capital"]
    main = run_backtest(ds, cfg, ruleset, store, capital=capital, label="principal")
    sens_ids = []
    if not args.no_sensitivity:
        for c in cfg.get("sensitivity_capitals", []):
            sens_ids.append(run_backtest(ds, cfg, ruleset, store, capital=c, label=f"sensibilite_{c}",
                                         parent_run_id=main.run_id).run_id)
    store.commit()
    checks = run_checks(store.conn, main.run_id, ds)
    report = build_report(store.conn, main.run_id, sens_ids, checks)
    out = _path(cfg["report_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    print(f"Simulation n° {main.run_id} ({ds.nature}) {main.start} → {main.end}, capital {capital} {cfg['currency']}")
    for pf, m in main.metrics.items():
        print(f"  {pf:20} rendement {m['rendement_total_pct']:7.2f} %   baisse max {m['baisse_max_pct']:7.2f} %   "
              f"coûts {m['couts_total_pct_capital']:5.2f} % du capital   ordres {m['nb_achats'] + m['nb_ventes']}")
    failed = [n for n, ok, _ in checks if not ok]
    print(f"Vérifications : {len(checks) - len(failed)}/{len(checks)} OK" + (f" — ÉCHECS : {failed}" if failed else ""))
    print(f"Rapport : {out}\nBase SQLite : {db_path}")
    print("Modèle d'exécution rétrospectif : exécutions reconstruites à partir des barres journalières, non prouvées.")
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
    r.add_argument("--db", help="Base SQLite à utiliser (remplace db_path de la configuration)")
    r.add_argument("--ruleset", help="Référentiel à appliquer (remplace ruleset de la configuration)")
    c = sub.add_parser("check-data", help="Valider les fichiers de données")
    c.add_argument("--dataset", help="Dossier du jeu de données (défaut : celui de la configuration)")
    s = sub.add_parser("snapshot-db", help="Instantané vérifié d'une base SQLite (l'original n'est jamais modifié)")
    s.add_argument("path")
    a = sub.add_parser("audit-docs", help="Contrôler un dossier d'audit documentaire (sans simulation)")
    a.add_argument("folder", nargs="?", default="data/audit_exemple_FICTIF")
    args = p.parse_args(argv)
    return {"run": cmd_run, "check-data": cmd_check_data, "audit-docs": cmd_audit_docs, "snapshot-db": cmd_snapshot_db}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
