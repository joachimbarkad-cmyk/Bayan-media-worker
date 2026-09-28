"""Rapport Markdown lisible, construit uniquement à partir de la base SQLite."""
from __future__ import annotations

import json
import sqlite3
from datetime import date

from . import PROJECT_ROOT
from .data import PointInTimeView
from .screening import screen_security
from .safety import network_blocked, scan_package

METRIC_LABELS = [
    ("valeur_finale", "Valeur finale"),
    ("rendement_total_pct", "Rendement total, scénario « radiés à zéro » (%)"),
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
    ("valeur_titres_radies_au_dernier_cours", "Titres radiés gelés, valorisés au dernier cours (exclus ci-dessus)"),
    ("rendement_total_pct_si_radies_au_dernier_cours", "Rendement total, scénario « radiés au dernier cours » (%)"),
]


# Traduction en langage simple des codes enregistrés dans la base.
REASON_TEXT = {
    "SIGNAL_ACHAT_TENDANCE": "Titre admissible dont le cours est au-dessus de sa moyenne : achat simulé.",
    "SIGNAL_VENTE_TENDANCE": "Le cours est repassé sous sa moyenne : vente simulée.",
    "CONSERVE_TENDANCE_HAUSSIERE": "Déjà détenu et toujours au-dessus de sa moyenne : on garde.",
    "CONSERVE_TENDANCE_INCALCULABLE": "Déjà détenu, mais la tendance n'est pas calculable : on garde sans renforcer.",
    "REFUS_SOUS_MOYENNE": "Admissible, mais le cours est sous sa moyenne : pas d'achat.",
    "REFUS_HISTORIQUE_INSUFFISANT": "Pas assez d'historique de prix pour appliquer la règle : pas d'achat.",
    "REFUS_STATUT_EXCLU": "Le filtre religieux exclut ce titre : achat interdit.",
    "REFUS_STATUT_INCERTAIN": "Le filtre religieux ne peut pas conclure (donnée ou règle manquante) : achat interdit par prudence.",
    "REFUS_COUT_DISPROPORTIONNE": "Les frais estimés sont trop élevés par rapport au montant investi : opération jugée peu pertinente.",
    "REFUS_CAPITAL_INSUFFISANT": "Le budget ne permet pas d'acheter une seule action entière avec ses frais.",
    "VENTE_STATUT_EXCLU": "Titre détenu devenu EXCLU : vente simulée.",
    "VENTE_STATUT_INCERTAIN": "Titre détenu devenu INCERTAIN : vente simulée selon la politique choisie.",
    "GEL_STATUT_INCERTAIN": "Titre détenu devenu INCERTAIN : conservé sans renforcement, à revoir.",
    "REFERENCE_ACHAT_INITIAL": "Achat initial du portefeuille de référence.",
    "REFERENCE_REINVESTIE_ACHAT": "Référence réinvestie : achat d'un titre admissible non détenu.",
    "REFERENCE_REINVESTIE_COMPLEMENT": "Référence réinvestie : complément d'une ligne sous sa part cible.",
    "COMPLEMENT_TENDANCE": "Stratégie : complément d'une ligne détenue sous sa part cible (option activée).",
}


PORTFOLIO_ORDER = ("strategie", "reference", "reference_reinvestie")


def _plain(code: str) -> str:
    return REASON_TEXT.get(code, code)


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
    L.append("> **Simulation avec modèle d'exécution rétrospectif.** Les ordres sont dimensionnés avec l'information "
             "connue avant l'ouverture ; leur exécution est reconstruite après coup à partir de la barre journalière "
             "(prix d'ouverture, volume du jour). Rien ne prouve qu'elles étaient possibles à ce prix et pour cette "
             "quantité : une confirmation exigerait des données horodatées de l'ouverture.\n")
    L.append("> **Pas une certification religieuse.** Le filtre applique mécaniquement le référentiel indiqué ; "
             "ADMISSIBLE ne signifie pas « 100 % halal ».\n")
    if not rs.get("validated"):
        L.append(f"> **Référentiel non validé** (`{rs['id']}`) : {rs.get('warning', '')}\n")
    if rs.get("divergence_notice"):
        L.append(f"> **Divergence entre savants.** {rs['divergence_notice']}\n")

    L.append("## Paramètres\n")
    c = cfg["costs"]
    L.append(_table(["Paramètre", "Valeur"], [
        ["Période simulée", f"{run['start_date']} → {run['end_date']}"],
        ["Capital initial", f"{run['initial_capital']:.2f} {cur}"],
        ["Données", f"{run['dataset_name']} ({run['dataset_nature']})"],
        ["Référentiel religieux", f"{rs['id']} (validé : {'oui' if rs.get('validated') else 'NON'})"],
        ["Stratégie", f"{cfg['strategy']['name']} : détenir un titre admissible si clôture > moyenne des "
                      f"{cfg['strategy']['sma_days']} dernières clôtures ; décision en fin de mois, exécution à l'ouverture suivante"],
        ["Référence « achat-conservation »", "Achat à parts égales des titres admissibles au 1er jour de décision, "
                                            "puis conservation (ventes seulement si le filtre ou une radiation l'impose)"],
        ["Référence « réinvestie »", "Chaque fin de mois : mêmes ventes imposées, puis liquidités réparties à parts cibles "
                                    "égales entre les titres admissibles du moment, sans moyenne mobile (docs/REFERENCES.md)"],
        ["Frais (fictifs)", f"{c['fixed_fee']} {cur} fixe + {c['pct_fee'] * 100:g} % (min {c['min_fee']} {cur}) par ordre ; "
                            f"glissement {c['slippage_bps']} pb ; refus si coût aller-retour > {c['max_roundtrip_cost_pct']} %"],
        ["Politique titres détenus", f"EXCLU → {cfg['holding_policy']['on_exclu']}, INCERTAIN → {cfg['holding_policy']['on_incertain']}"],
        ["Empreinte du code / des données", f"{run['code_hash'][:12]} / {json.loads(run['data_hashes'])['prices'][:12]}"],
    ]))

    L.append("\n## Résultats : stratégie contre deux références\n")
    L.append(_table(["Indicateur", "Stratégie", "Réf. achat-conservation", "Réf. réinvestie"],
                    [[label] + [_fmt(m.get(pf, {}).get(k, "")) for pf in PORTFOLIO_ORDER] for k, label in METRIC_LABELS]))
    L.append("\nLes trois portefeuilles utilisent les mêmes données, le même univers daté, le même filtre, les mêmes frais et "
             "les mêmes règles d'exécution. Les liquidités ne sont pas rémunérées (pas d'intérêts). Dividendes non modélisés. "
             "La référence achat-conservation ne réinvestit pas le produit des ventes imposées ; la référence réinvestie, si.\n")

    if sensitivity_run_ids:
        L.append("## Sensibilité au capital (même stratégie, mêmes frais)\n")
        rows = []
        for rid in sensitivity_run_ids:
            r = conn.execute("SELECT initial_capital FROM runs WHERE run_id=?", (rid,)).fetchone()
            mm = _metrics(conn, rid)
            refused = conn.execute(
                "SELECT COUNT(*) n FROM decisions WHERE run_id=? AND portfolio='strategie' AND reason_code IN "
                "('REFUS_COUT_DISPROPORTIONNE','REFUS_CAPITAL_INSUFFISANT')", (rid,)).fetchone()["n"]
            rows.append([f"{r['initial_capital']:.0f} {cur}"] +
                        [_fmt(mm[pf]["rendement_total_pct"]) for pf in PORTFOLIO_ORDER] +
                        [_fmt(mm["strategie"]["couts_total_pct_capital"]), refused])
        L.append(_table(["Capital", "Stratégie (%)", "Réf. achat-conservation (%)", "Réf. réinvestie (%)",
                         "Coûts stratégie (% capital)", "Achats refusés stratégie (coût/capital)"], rows))
        L.append("\nAvec un petit capital, les frais fixes et les actions entières pèsent davantage : c'est ce que mesure ce tableau. "
                 "Un rendement de 0 avec des refus signifie qu'aucun achat n'a été jugé pertinent à ce niveau de capital "
                 "(le capital est resté en liquidités).\n")

    L.append(f"## Filtre religieux au {last_date}\n")
    thresholds = {x["id"]: x.get("max") for x in rs["financial_ratios"]}
    labels = {x["id"]: x.get("label", x["id"]) for x in rs["financial_ratios"]}
    tag = "" if rs.get("validated") else " — seuil de DÉMO arbitraire"
    L.append("ADMISSIBLE = aucun motif d'exclusion ni d'incertitude trouvé avec le référentiel et les données disponibles ; "
             "ce n'est pas une certification. Les documents publiés un jour J ne sont utilisés qu'à partir du jour J+1.\n")
    rows = []
    for r in conn.execute("SELECT * FROM screenings WHERE run_id=? AND decision_date=? ORDER BY status, ticker",
                          (run_id, last_date)):
        ratios = "<br>".join(
            f"{labels.get(k, k)} = {v:.1%} (seuil {'non défini' if thresholds.get(k) is None else format(thresholds[k], '.0%')}{tag})"
            for k, v in json.loads(r["ratios_json"]).items()) or "—"
        fin = f"{r['fundamentals_period_end']} publié le {r['fundamentals_available_date']}" if r["fundamentals_period_end"] else "aucune"
        act = f"{r['activity_codes']} (fiche du {r['activity_available_date']})" if r["activity_available_date"] else "aucune fiche"
        causes = f" [causes : {r['incertain_causes']}]" if r["incertain_causes"] and r["status"] == "INCERTAIN" else ""
        rows.append([r["ticker"], f"**{r['status']}**{causes}", "; ".join(json.loads(r["reasons_json"])), ratios, fin, act])
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
        rows.append([r["ticker"], r["screening_status"], f"**{r['final_action']}**", _plain(r["reason_code"]),
                     trend, f"`{r['reason_code']}` — {r['detail']}"])
    L.append(_table(["Titre", "Statut", "Décision", "En clair", "Données", "Code et détail"], rows))
    L.append("\nUne décision « ACHAT » est une proposition simulée pour l'ouverture du jour de bourse suivant, pas un conseil. "
             "À l'exécution, la quantité peut être réduite (liquidités insuffisantes au prix d'ouverture) ou l'ordre rejeté "
             "(coût devenu disproportionné, prix manquant) : voir « Ordres rejetés au moment de l'exécution simulée ».\n")

    L.append("## Refus et ventes imposées sur toute la période (stratégie)\n")
    rows = [[f"`{r['reason_code']}`", _plain(r["reason_code"]), r["n"]] for r in conn.execute(
        "SELECT reason_code, COUNT(*) n FROM decisions WHERE run_id=? AND portfolio='strategie' AND "
        "(reason_code LIKE 'REFUS%' OR reason_code LIKE 'VENTE_STATUT%' OR reason_code LIKE 'GEL%') "
        "GROUP BY reason_code ORDER BY n DESC", (run_id,))]
    L.append(_table(["Code", "En clair", "Nombre de décisions"], rows))
    L.append("\n### Achats refusés pour coût ou capital (10 derniers, deux portefeuilles)\n")
    rows = [[r["decision_date"], r["portfolio"], r["ticker"], r["reason_code"], r["detail"]] for r in conn.execute(
        "SELECT * FROM decisions WHERE run_id=? AND reason_code IN "
        "('REFUS_COUT_DISPROPORTIONNE','REFUS_CAPITAL_INSUFFISANT') ORDER BY decision_date DESC LIMIT 10", (run_id,))]
    L.append(_table(["Date", "Portefeuille", "Titre", "Motif", "Détail"], rows) if rows else "Aucun.")
    rows = [[r["execution_date"], r["portfolio"], r["ticker"], r["side"], r["reason"]] for r in conn.execute(
        "SELECT * FROM orders WHERE run_id=? AND status='REJETE' ORDER BY execution_date", (run_id,))]
    L.append("\n### Ordres rejetés au moment de l'exécution simulée\n")
    L.append(_table(["Date", "Portefeuille", "Titre", "Sens", "Motif"], rows) if rows else "Aucun.")

    L.append("\n## Radiations de titres détenus\n")
    rows = [[r["date"], r["portfolio"], r["ticker"], r["event"], r["qty"],
             "—" if r["value_per_share"] is None else f"{r['value_per_share']:.2f}", f"{r['cash_received']:.2f}", r["source"]]
            for r in conn.execute("SELECT * FROM corporate_events WHERE run_id=? ORDER BY date, portfolio", (run_id,))]
    L.append("Aucune vente n'est simulée faute de prix négociable. Sans contrepartie documentée, la position est gelée "
             "à valeur **inconnue**. Deux scénarios sont affichés : « à zéro » (résultats principaux) et « au dernier "
             "cours ». Ce ne sont **pas des bornes** : une contrepartie ultérieure peut dépasser le dernier cours, et un "
             "titre radié peut encore se négocier hors cote comme ne plus rien valoir.\n")
    L.append(_table(["Date", "Portefeuille", "Titre", "Événement", "Qté", "Dernier cours / contrepartie", "Espèces reçues",
                     "Source"], rows) if rows else "Aucune.")

    L.append("\n## Journal des ordres simulés (15 derniers, stratégie)\n")
    rows = [[r["decision_date"], r["execution_date"], r["ticker"], r["side"], r["qty"], f"{r['ref_price']:.2f}",
             f"{r['exec_price']:.2f}", f"{r['fees']:.2f}", f"{r['slippage_cost']:.2f}", r["reason"]]
            for r in conn.execute("SELECT * FROM orders WHERE run_id=? AND portfolio='strategie' AND status='EXECUTE_SIMULE' "
                                  "ORDER BY execution_date DESC, ticker LIMIT 15", (run_id,))]
    L.append(_table(["Décision", "Exécution", "Titre", "Sens", "Qté", "Ouverture", "Prix simulé", "Frais", "Glissement", "Motif"], rows))

    L.append("\n## Vérifications automatiques de cette exécution\n")
    L.append(_table(["Contrôle", "Résultat", "Détail"], [[n, "OK" if ok else "**ÉCHEC**", d] for n, ok, d in checks]))
    L.append("\nCes contrôles portent sur le code Python de ce projet et sur ce processus ; ils ne remplacent pas une "
             "isolation au niveau du système. Le projet ne contient aucun connecteur de courtage.")

    L.append("\n## Limites à garder en tête\n")
    L.append("- Données fictives : aucune conclusion de rentabilité possible. Il faudra des données réelles datées.\n"
             "- Une seule période, un seul paramètre (SMA 200) : risque de sur-interprétation, même sur données réelles.\n"
             "- Dividendes, purification, fiscalité, change et jours fériés ne sont pas modélisés.\n"
             "- Frais fictifs : à remplacer par la grille réelle du courtier choisi.\n"
             "- Activités lues depuis un historique daté, mais aucune durée de validité maximale d'une fiche d'activité.\n"
             "- Pas de conversion de devises : tous les titres doivent être dans la devise du portefeuille (sinon refus).\n"
             "- Titre radié sans contrepartie publiée et payée : valeur inconnue, deux scénarios (0, dernier cours), pas des bornes.\n"
             "- Exécution : ordre borné par l'information connue à l'ouverture (statut recalculé, 5 % du volume de la veille) ; "
             "résultat modélisé avec la barre du jour (prix d'ouverture, 5 % du volume du jour). Hypothèses non validées.\n"
             "- Capitalisation vérifiée par nombre d'actions x cours : écarte une valeur aberrante, pas une donnée fausse mais cohérente.\n"
             "- Le référentiel religieux s'applique rétroactivement à toute la période simulée.\n")
    return "\n".join(L) + "\n"


def run_checks(conn: sqlite3.Connection, run_id: int, ds=None) -> list[tuple[str, bool, str]]:
    """Contrôles recalculés depuis la base, indépendamment du moteur. Avec `ds`, chaque exécution simulée est
    aussi confrontée au cours d'ouverture réel de son jour d'exécution."""
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
    violations = scan_package()
    open_check = []
    if ds is not None:
        bad = []
        fills = conn.execute("SELECT ticker, execution_date, ref_price FROM orders WHERE run_id=? AND "
                             "status='EXECUTE_SIMULE'", (run_id,)).fetchall()
        for r in fills:
            bar = ds.bar_on(r["ticker"], date.fromisoformat(r["execution_date"]))
            if bar is None or bar.volume <= 0 or abs(bar.open - r["ref_price"]) > 1e-9:
                bad.append(f"{r['ticker']} {r['execution_date']}")
        open_check = [("Chaque exécution simulée correspond à un cours d'ouverture présent dans le fichier, un jour de volume non nul", not bad,
                       ("; ".join(bad[:5]) or f"{len(fills)} exécutions vérifiées")
                       + " (ne prouve pas qu'une transaction à ce prix et cette quantité était possible)")]
        run = conn.execute("SELECT config_json, ruleset_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
        cfg, rs = json.loads(run["config_json"]), json.loads(run["ruleset_json"])
        part = float(cfg.get("execution", {}).get("max_volume_participation", 0.05))
        too_big, not_adm = [], []
        for r in conn.execute("SELECT ticker, side, qty, execution_date FROM orders WHERE run_id=? AND "
                              "status='EXECUTE_SIMULE'", (run_id,)).fetchall():
            d = date.fromisoformat(r["execution_date"])
            bar = ds.bar_on(r["ticker"], d)
            if bar is None or r["qty"] > bar.volume * part:
                too_big.append(f"{r['ticker']} {d} ({r['qty']})")
            # Recalcul indépendant du statut connu à l'ouverture (documents publiés avant le jour d'exécution).
            if r["side"] == "BUY" and screen_security(PointInTimeView(ds, d), r["ticker"], rs).status != "ADMISSIBLE":
                not_adm.append(f"{r['ticker']} {d}")
        open_check += [
            (f"Quantité exécutée <= {part:.0%} du volume total du jour", not too_big, "; ".join(too_big[:5]) or "OK"),
            ("Aucun achat d'un titre non ADMISSIBLE à l'ouverture d'exécution (statut recalculé)", not not_adm,
             "; ".join(not_adm[:5]) or "OK"),
        ]
    return open_check + [
        ("Aucun achat d'un titre non ADMISSIBLE (statut enregistré)", bad_buys == 0, f"{bad_buys} cas"),
        ("Aucun achat d'un titre non ADMISSIBLE (recoupement avec le filtrage)", bad_buys2 == 0, f"{bad_buys2} cas"),
        ("Aucune décision n'a lu une donnée postérieure à sa date", future_dec == 0, f"{future_dec} cas"),
        ("Aucun filtrage n'a lu une donnée postérieure à sa date", future_scr == 0, f"{future_scr} cas"),
        ("Exécution toujours après la décision", exec_order == 0, f"{exec_order} cas sur {n_orders} ordres"),
        ("Jamais de solde de liquidités négatif (pas de marge)", neg_cash == 0, f"{neg_cash} jours"),
        ("Exécution marquée simulation uniquement", sim_only == 1, "runs.simulation_only = 1"),
        ("Code sans bibliothèque réseau/courtage ni lecture de clés (analyse statique à ce lancement)",
         not violations, "; ".join(violations) or f"{len(list((PROJECT_ROOT / 'halal_sim').glob('*.py')))} fichiers analysés"),
        ("Réseau effectivement coupé pendant cette exécution", network_blocked(),
         "socket.connect / create_connection / getaddrinfo remplacés par un refus"),
    ]
