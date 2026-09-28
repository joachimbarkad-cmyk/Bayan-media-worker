"""Rapport Markdown lisible, construit uniquement à partir de la base SQLite."""
from __future__ import annotations

import json
import sqlite3

METRIC_LABELS = [
    ("valeur_finale", "Valeur finale"),
    ("rendement_total_pct", "Rendement total (%)"),
    ("rendement_annualise_pct", "Rendement annualisé (%)"),
    ("volatilite_annualisee_pct", "Volatilité annualisée (%)"),
    ("baisse_max_pct", "Baisse maximale (%)"),
    ("ratio_rendement_risque_rf0", "Rendement/risque (taux sans risque = 0)"),
    ("exposition_moyenne_pct", "Exposition moyenne aux actions (%)"),
    ("nb_achats", "Achats simulés"),
    ("nb_ventes", "Ventes simulées"),
    ("frais_total", "Frais de courtage simulés"),
    ("glissement_total", "Coût de glissement simulé"),
    ("couts_total_pct_capital", "Coûts totaux (% du capital initial)"),
]


def _table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
    return "\n".join(out)


def _metrics(conn, run_id) -> dict[str, dict[str, float]]:
    m: dict[str, dict[str, float]] = {}
    for r in conn.execute("SELECT portfolio,key,value FROM metrics WHERE run_id=?", (run_id,)):
        m.setdefault(r["portfolio"], {})[r["key"]] = r["value"]
    return m


def _fmt(v) -> str:
    return f"{v:g}" if isinstance(v, float) else str(v)


def build_report(conn: sqlite3.Connection, run_id: int, sensitivity_run_ids: list[int], checks: list[tuple[str, bool, str]]) -> str:
    run = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    cfg, rs = json.loads(run["config_json"]), json.loads(run["ruleset_json"])
    cur = run["currency"]
    m = _metrics(conn, run_id)
    last_date = conn.execute("SELECT MAX(decision_date) d FROM decisions WHERE run_id=?", (run_id,)).fetchone()["d"]
    L: list[str] = []
    L.append(f"# Rapport de simulation — exécution n° {run_id}\n")
    if run["dataset_nature"] == "FICTIF":
        L.append("> **DONNÉES FICTIVES DE DÉMONSTRATION.** Sociétés, prix et états financiers inventés pour tester le logiciel. "
                 "Les chiffres ci-dessous ne disent RIEN de la rentabilité réelle de la stratégie.\n")
    L.append("> **Simulation uniquement.** Aucun courtier connecté, aucun ordre réel envoyé.\n")
    L.append("> **Pas une certification religieuse.** Le filtre applique mécaniquement le référentiel indiqué ; "
             "ADMISSIBLE ne signifie pas « 100 % halal ».\n")
    if not rs.get("validated"):
        L.append(f"> **Référentiel non validé** (`{rs['id']}`) : {rs.get('warning', '')}\n")

    L.append("## Paramètres\n")
    c = cfg["costs"]
    L.append(_table(["Paramètre", "Valeur"], [
        ["Période simulée", f"{run['start_date']} → {run['end_date']}"],
        ["Capital initial", f"{run['initial_capital']:.2f} {cur}"],
        ["Données", f"{run['dataset_name']} ({run['dataset_nature']})"],
        ["Référentiel religieux", f"{rs['id']} (validé : {'oui' if rs.get('validated') else 'NON'})"],
        ["Stratégie", f"{cfg['strategy']['name']} : détenir un titre admissible si clôture > moyenne des "
                      f"{cfg['strategy']['sma_days']} dernières clôtures ; décision en fin de mois, exécution à l'ouverture suivante"],
        ["Référence", "Achat à parts égales des titres admissibles au 1er jour de décision, puis conservation "
                      "(ventes seulement si le filtre religieux l'impose)"],
        ["Frais (fictifs)", f"{c['fixed_fee']} {cur} fixe + {c['pct_fee'] * 100:g} % (min {c['min_fee']} {cur}) par ordre ; "
                            f"glissement {c['slippage_bps']} pb ; refus si coût aller-retour > {c['max_roundtrip_cost_pct']} %"],
        ["Politique titres détenus", f"EXCLU → {cfg['holding_policy']['on_exclu']}, INCERTAIN → {cfg['holding_policy']['on_incertain']}"],
        ["Empreinte du code / des données", f"{run['code_hash'][:12]} / {json.loads(run['data_hashes'])['prices'][:12]}"],
    ]))

    L.append("\n## Résultats : stratégie contre référence\n")
    L.append(_table(["Indicateur", "Stratégie", "Référence"],
                    [[label, _fmt(m.get("strategie", {}).get(k, "")), _fmt(m.get("reference", {}).get(k, ""))]
                     for k, label in METRIC_LABELS]))
    L.append("\nLes deux portefeuilles utilisent les mêmes données, le même filtre, les mêmes frais et les mêmes règles "
             "d'exécution. Les liquidités ne sont pas rémunérées (pas d'intérêts). Dividendes non modélisés dans la V1.\n")

    if sensitivity_run_ids:
        L.append("## Sensibilité au capital (même stratégie, mêmes frais)\n")
        rows = []
        for rid in sensitivity_run_ids:
            r = conn.execute("SELECT initial_capital FROM runs WHERE run_id=?", (rid,)).fetchone()
            mm = _metrics(conn, rid)
            refused = conn.execute(
                "SELECT COUNT(*) n FROM decisions WHERE run_id=? AND portfolio='strategie' AND reason_code IN "
                "('REFUS_COUT_DISPROPORTIONNE','REFUS_CAPITAL_INSUFFISANT')", (rid,)).fetchone()["n"]
            rows.append([f"{r['initial_capital']:.0f} {cur}", _fmt(mm["strategie"]["rendement_total_pct"]),
                         _fmt(mm["reference"]["rendement_total_pct"]), _fmt(mm["strategie"]["couts_total_pct_capital"]),
                         refused])
        L.append(_table(["Capital", "Stratégie (%)", "Référence (%)", "Coûts stratégie (% capital)",
                         "Achats refusés (coût/capital)"], rows))
        L.append("\nAvec un petit capital, les frais fixes et les actions entières pèsent davantage : c'est ce que mesure ce tableau. "
                 "Un rendement de 0 avec des refus signifie qu'aucun achat n'a été jugé pertinent à ce niveau de capital "
                 "(le capital est resté en liquidités).\n")

    L.append(f"## Filtre religieux au {last_date}\n")
    rows = []
    for r in conn.execute("SELECT * FROM screenings WHERE run_id=? AND decision_date=? ORDER BY status, ticker",
                          (run_id, last_date)):
        ratios = ", ".join(f"{k}={v:.1%}" for k, v in json.loads(r["ratios_json"]).items()) or "—"
        fin = f"{r['fundamentals_period_end']} publié le {r['fundamentals_available_date']}" if r["fundamentals_period_end"] else "aucune"
        rows.append([r["ticker"], f"**{r['status']}**", "; ".join(json.loads(r["reasons_json"])), ratios, fin,
                     r["activity_codes"]])
    L.append(_table(["Titre", "Statut", "Motifs", "Ratios", "Données financières", "Activité"], rows))
    src = conn.execute("SELECT DISTINCT fundamentals_source s FROM screenings WHERE run_id=? AND s IS NOT NULL", (run_id,)).fetchall()
    L.append("\nSources des données financières : " + "; ".join(s["s"] for s in src) + "\n")

    L.append("### Changements de statut au cours de la période\n")
    prev: dict[str, str] = {}
    changes = []
    for r in conn.execute("SELECT decision_date,ticker,status,reasons_json FROM screenings WHERE run_id=? "
                          "ORDER BY decision_date, ticker", (run_id,)):
        if r["ticker"] in prev and prev[r["ticker"]] != r["status"]:
            changes.append([r["decision_date"], r["ticker"], f"{prev[r['ticker']]} → {r['status']}",
                            "; ".join(json.loads(r["reasons_json"]))])
        prev[r["ticker"]] = r["status"]
    L.append(_table(["Date", "Titre", "Changement", "Motif"], changes) if changes else "Aucun.")

    L.append(f"\n## Signaux de la stratégie au {last_date}\n")
    rows = []
    for r in conn.execute("SELECT * FROM decisions WHERE run_id=? AND portfolio='strategie' AND decision_date=? "
                          "ORDER BY final_action, ticker", (run_id, last_date)):
        inp = json.loads(r["inputs_json"])
        trend = f"clôture {inp['cloture']} / SMA {inp['sma']}" if "sma" in inp else "—"
        rows.append([r["ticker"], r["screening_status"], r["signal"], f"**{r['final_action']}**", r["reason_code"],
                     trend, r["detail"]])
    L.append(_table(["Titre", "Statut", "Signal", "Décision", "Code", "Données", "Détail"], rows))
    L.append("\nUne décision « ACHAT » ici est une proposition simulée pour le jour de bourse suivant, pas un conseil.\n")

    L.append("## Refus et ventes imposées sur toute la période (stratégie)\n")
    rows = [[r["reason_code"], r["n"]] for r in conn.execute(
        "SELECT reason_code, COUNT(*) n FROM decisions WHERE run_id=? AND portfolio='strategie' AND "
        "(reason_code LIKE 'REFUS%' OR reason_code LIKE 'VENTE_STATUT%' OR reason_code LIKE 'GEL%') "
        "GROUP BY reason_code ORDER BY n DESC", (run_id,))]
    L.append(_table(["Motif", "Nombre de décisions"], rows))
    L.append("\n### Achats refusés pour coût ou capital (10 derniers, deux portefeuilles)\n")
    rows = [[r["decision_date"], r["portfolio"], r["ticker"], r["reason_code"], r["detail"]] for r in conn.execute(
        "SELECT * FROM decisions WHERE run_id=? AND reason_code IN "
        "('REFUS_COUT_DISPROPORTIONNE','REFUS_CAPITAL_INSUFFISANT') ORDER BY decision_date DESC LIMIT 10", (run_id,))]
    L.append(_table(["Date", "Portefeuille", "Titre", "Motif", "Détail"], rows) if rows else "Aucun.")
    rows = [[r["execution_date"], r["portfolio"], r["ticker"], r["side"], r["reason"]] for r in conn.execute(
        "SELECT * FROM orders WHERE run_id=? AND status='REJETE' ORDER BY execution_date", (run_id,))]
    L.append("\n### Ordres rejetés au moment de l'exécution simulée\n")
    L.append(_table(["Date", "Portefeuille", "Titre", "Sens", "Motif"], rows) if rows else "Aucun.")

    L.append("\n## Journal des ordres simulés (15 derniers, stratégie)\n")
    rows = [[r["decision_date"], r["execution_date"], r["ticker"], r["side"], r["qty"], f"{r['ref_price']:.2f}",
             f"{r['exec_price']:.2f}", f"{r['fees']:.2f}", f"{r['slippage_cost']:.2f}", r["reason"]]
            for r in conn.execute("SELECT * FROM orders WHERE run_id=? AND portfolio='strategie' AND status='EXECUTE_SIMULE' "
                                  "ORDER BY execution_date DESC, ticker LIMIT 15", (run_id,))]
    L.append(_table(["Décision", "Exécution", "Titre", "Sens", "Qté", "Ouverture", "Prix simulé", "Frais", "Glissement", "Motif"], rows))

    L.append("\n## Vérifications automatiques de cette exécution\n")
    L.append(_table(["Contrôle", "Résultat", "Détail"], [[n, "OK" if ok else "**ÉCHEC**", d] for n, ok, d in checks]))

    L.append("\n## Limites à garder en tête\n")
    L.append("- Données fictives : aucune conclusion de rentabilité possible. Il faudra des données réelles datées.\n"
             "- Une seule période, un seul paramètre (SMA 200) : risque de sur-interprétation, même sur données réelles.\n"
             "- Dividendes, purification, fiscalité, change et jours fériés ne sont pas modélisés.\n"
             "- Frais fictifs : à remplacer par la grille réelle du courtier choisi.\n"
             "- Classement d'activité supposé constant sur la période (pas d'historique daté de l'activité).\n")
    return "\n".join(L) + "\n"


def run_checks(conn: sqlite3.Connection, run_id: int) -> list[tuple[str, bool, str]]:
    """Contrôles recalculés depuis la base, indépendamment du moteur."""
    q = lambda sql: conn.execute(sql, (run_id,)).fetchone()[0]
    bad_buys = q("SELECT COUNT(*) FROM orders WHERE run_id=? AND side='BUY' AND status='EXECUTE_SIMULE' "
                 "AND screening_status_at_decision<>'ADMISSIBLE'")
    bad_buys2 = q("SELECT COUNT(*) FROM orders o JOIN screenings s ON s.run_id=o.run_id AND s.ticker=o.ticker "
                  "AND s.decision_date=o.decision_date WHERE o.run_id=? AND o.side='BUY' AND o.status='EXECUTE_SIMULE' "
                  "AND s.status<>'ADMISSIBLE'")
    future_dec = q("SELECT COUNT(*) FROM decisions WHERE run_id=? AND max_data_date > decision_date")
    future_scr = q("SELECT COUNT(*) FROM screenings WHERE run_id=? AND max_data_date > decision_date")
    exec_order = q("SELECT COUNT(*) FROM orders WHERE run_id=? AND execution_date <= decision_date")
    n_orders = q("SELECT COUNT(*) FROM orders WHERE run_id=? AND status='EXECUTE_SIMULE'")
    neg_cash = q("SELECT COUNT(*) FROM equity WHERE run_id=? AND cash < -0.01")
    sim_only = q("SELECT simulation_only FROM runs WHERE run_id=?")
    return [
        ("Aucun achat d'un titre non ADMISSIBLE (statut enregistré)", bad_buys == 0, f"{bad_buys} cas"),
        ("Aucun achat d'un titre non ADMISSIBLE (recoupement avec le filtrage)", bad_buys2 == 0, f"{bad_buys2} cas"),
        ("Aucune décision n'a lu une donnée postérieure à sa date", future_dec == 0, f"{future_dec} cas"),
        ("Aucun filtrage n'a lu une donnée postérieure à sa date", future_scr == 0, f"{future_scr} cas"),
        ("Exécution toujours après la décision", exec_order == 0, f"{exec_order} cas sur {n_orders} ordres"),
        ("Jamais de solde de liquidités négatif (pas de marge)", neg_cash == 0, f"{neg_cash} jours"),
        ("Exécution marquée simulation uniquement", sim_only == 1, "runs.simulation_only = 1"),
        ("Aucun ordre réel", True, "Aucun module de courtage ; réseau coupé par safety.forbid_network()"),
    ]
