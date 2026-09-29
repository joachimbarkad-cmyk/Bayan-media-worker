"""Moteur de simulation chronologique jour par jour.

Chronologie d'un jour J :
1. exécution à l'OUVERTURE de J des ordres décidés à la clôture précédente ;
2. valorisation des portefeuilles à la CLÔTURE de J ;
3. si J est le dernier jour de bourse du mois : filtrage + décisions avec les seules
   données datées <= J (via PointInTimeView) ; ordres mis en attente pour J+1.

Trois portefeuilles, mêmes données, mêmes frais, même filtre religieux, même univers daté :
- "strategie" : filtre de tendance SMA ;
- "reference" : achat à parts égales des titres ADMISSIBLES au premier jour de décision,
  puis conservation ; seules les ventes imposées par le filtre religieux sont faites ;
- "reference_reinvestie" (règles écrites avant le test, cf. docs/REFERENCES.md) : chaque fin de mois,
  ventes imposées comme ci-dessus, puis les liquidités disponibles sont réparties entre les titres
  actuellement ADMISSIBLES, à parts cibles égales, sans SMA ; aucune vente pour rééquilibrer.

Univers : à chaque date, seuls les titres dont la fiche est connue (known_from < J) et non radiés sont
filtrés. Radiation d'un titre détenu (traitée au début du jour de radiation) : aucune vente n'est simulée
faute de prix négociable. Avec une contrepartie en espèces documentée (fiche titre), elle est créditée ;
sinon la position est GELÉE à valeur inconnue ; les résultats sont donnés dans deux scénarios, à 0 (valeur
principale) et au dernier cours. Ce ne sont pas des bornes : la valeur réelle peut sortir de cet intervalle.

Compléments de lignes : une seule règle (`sizing.topup_held_positions`) pour la stratégie ET la référence
réinvestie, afin que leur écart ne mesure que l'effet du filtre de tendance.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date

from . import PROJECT_ROOT
from .broker import CostModel, Fill, PaperBroker
from .data import Dataset, PointInTimeView
from .db import Store
from .metrics import compute_metrics
from .screening import ADMISSIBLE, EXCLU, ScreeningResult, real_data_problems, screen_security, structural_problems
from .strategy import BUY, NONE, SELL, Decision, SmaTrendStrategy, incertain_action, validate_holding_policy

PORTFOLIOS = ("strategie", "reference", "reference_reinvestie")


class PolicyError(RuntimeError):
    pass


@dataclass
class PendingOrder:
    ticker: str
    side: str
    qty: int
    decision_date: date
    status: str
    reason: str


@dataclass
class BacktestResult:
    run_id: int
    start: date
    end: date
    metrics: dict[str, dict]
    brokers: dict[str, PaperBroker]
    equity: dict[str, list[tuple[date, float, float]]] = field(default_factory=dict)


def check_run_allowed(ds: Dataset, ruleset: dict, config: dict) -> None:
    """Refuse toute simulation dont le cadre n'est pas sain. Revalide le référentiel ici (et pas seulement
    au chargement) : un dictionnaire modifié en mémoire ne peut pas contourner les contrôles."""
    problems = structural_problems(ruleset)
    if ds.nature == "REEL":
        problems = real_data_problems(ruleset)
    if problems:
        raise PolicyError(f"Refus : référentiel '{ruleset.get('id')}' inutilisable sur des données {ds.nature} : "
                          + " ; ".join(problems) + " (voir docs/REFERENTIEL_ET_SOURCES.md)")
    currency = config.get("currency")
    others = sorted({s["currency"] for s in ds.securities.values()} - {currency})
    if others:
        raise PolicyError(f"Refus : titres en {others} alors que le portefeuille est en {currency}. "
                          "La conversion de devises n'est pas encore modélisée.")
    validate_holding_policy(config["holding_policy"])


def month_end_dates(calendar: list[date]) -> list[date]:
    """Derniers jours de bourse de chaque mois, sauf le tout dernier jour (pas de lendemain pour exécuter)."""
    return [d for d, nxt in zip(calendar, calendar[1:]) if nxt.month != d.month]


def code_hash() -> str:
    h = hashlib.sha256()
    for p in sorted((PROJECT_ROOT / "halal_sim").glob("*.py")):
        h.update(p.name.encode() + p.read_bytes())
    return h.hexdigest()


class Backtest:
    def __init__(self, ds: Dataset, config: dict, ruleset: dict, store: Store, *, capital: float | None = None,
                 label: str = "principal", parent_run_id: int | None = None):
        check_run_allowed(ds, ruleset, config)
        self.ds, self.cfg, self.ruleset, self.store = ds, config, ruleset, store
        self.capital = float(capital if capital is not None else config["initial_capital"])
        c = config["costs"]
        self.costs = CostModel(c["fixed_fee"], c["pct_fee"], c["min_fee"], c["slippage_bps"])
        self.max_rt = float(c["max_roundtrip_cost_pct"])
        self.policy = config["holding_policy"]
        self.strategy = SmaTrendStrategy(config["strategy"]["sma_days"])
        self.brokers = {p: PaperBroker(p, self.capital, self.costs) for p in PORTFOLIOS}
        self.run_id = store.start_run(label=label, parent_run_id=parent_run_id, ds=ds, ruleset=ruleset,
                                      config=config, code_hash=code_hash(), capital=self.capital)
        self.bench_started = False
        self.topup = bool(config.get("sizing", {}).get("topup_held_positions", False))
        # Part maximale du volume de la VEILLE (connu avant l'ouverture) qu'un ordre peut représenter.
        self.max_participation = float(config.get("execution", {}).get("max_volume_participation", 0.05))
        if not 0 < self.max_participation <= 1:
            raise PolicyError("execution.max_volume_participation doit être dans ]0 ; 1]")
        self.delistings_done: set[str] = set()
        self._open_status: dict[tuple[str, date], str] = {}

    # --- dimensionnement d'un achat, décidé avec le cours de clôture de la date de décision ---
    def _size_buy(self, close: float, budget: float) -> tuple[int, str, str]:
        price = self.costs.fill_price(close, "BUY")
        qty = int(max(budget, 0) // price)
        while qty > 0 and qty * price + self.costs.fee(qty * price) > budget:
            qty -= 1
        if qty == 0:
            return 0, "REFUS_CAPITAL_INSUFFISANT", (
                f"Budget {budget:.2f} insuffisant pour 1 action entière à ~{price:.2f} + frais {self.costs.fee(price):.2f}")
        notional = qty * price
        rt = self.costs.roundtrip_cost_pct(notional)
        if rt > self.max_rt:
            return 0, "REFUS_COUT_DISPROPORTIONNE", (
                f"Coût aller-retour estimé {rt:.2f} % de {notional:.2f} > limite {self.max_rt:.2f} % : opération peu pertinente")
        alert = " ALERTE : coûts élevés relativement au montant." if rt > self.max_rt / 2 else ""
        return qty, "", f"{qty} action(s) ~{notional:.2f}, coût aller-retour estimé {rt:.2f} %.{alert}"

    def _close(self, ticker: str, d: date) -> tuple[float | None, PointInTimeView]:
        view = PointInTimeView(self.ds, d)
        bars = view.last_bars(ticker, 1)
        return (bars[-1].close if bars else None), view

    def _equity_estimate(self, br: PaperBroker, d: date) -> float:
        return br.cash + sum(q * (self._close(t, d)[0] or 0.0) for t, q in br.positions.items())

    def _record(self, pf, d, status, dec, final, code, detail):
        self.store.add_decision(self.run_id, pf, d, status, dec, final, code, detail)

    def _sell_orders(self, pf, br, d, items) -> tuple[list[PendingOrder], float]:
        orders, proceeds = [], 0.0
        for dec, scr in items:
            qty = br.positions[dec.ticker]
            close = self._close(dec.ticker, d)[0] or 0.0
            gross = qty * self.costs.fill_price(close, "SELL")
            proceeds += gross - self.costs.fee(gross)
            orders.append(PendingOrder(dec.ticker, "SELL", qty, d, scr.status, dec.reason_code))
            self._record(pf, d, scr.status, dec, SELL, dec.reason_code, dec.detail)
        return orders, proceeds

    def _process_delistings(self, d: date) -> None:
        """Début de journée. (1) Radiation survenue ce jour : la position est toujours GELÉE (valeur inconnue).
        (2) Contrepartie en espèces documentée : créditée seulement quand sa source est publiée avant le jour
        (règle J+1) ET que sa date de paiement est passée : sans heure de paiement, rien ne garantit que les fonds
        soient disponibles à l'ouverture du jour même, d'où la séance suivante. Un échange de titres n'est pas
        modélisé : la position reste gelée."""
        for t, sec in self.ds.securities.items():
            dl = sec["delisted_date"]
            if dl is None or d < dl or t in self.delistings_done:
                continue
            self.delistings_done.add(t)
            for pf, br in self.brokers.items():
                if not br.positions.get(t):
                    continue
                last = self.ds.last_close_on_or_before(t, d)
                qty = br.freeze(t, last, d)
                src_d = sec["delisting_source_date"]
                known = sec["delisting_cash_per_share"] is not None and src_d is not None and src_d < d
                # Le journal ne mentionne une contrepartie que si elle était publiée AVANT ce jour.
                self.store.add_corporate_event(self.run_id, pf, d, t, "RADIATION_VALEUR_INCONNUE", qty, last, 0.0,
                                               f"contrepartie publiée le {src_d}, paiement annoncé le "
                                               f"{sec['delisting_cash_date']}" if known
                                               else "aucune contrepartie publiée à cette date")
        for pf, br in self.brokers.items():
            for t in sorted(br.frozen):
                sec = self.ds.securities[t]
                cash = sec["delisting_cash_per_share"]
                src_d, pay_d = sec["delisting_source_date"], sec["delisting_cash_date"]
                if cash is None or src_d is None or pay_d is None or src_d >= d or pay_d >= d:
                    continue  # non documentée, pas encore publiée, ou fonds pas encore disponibles à l'ouverture
                qty, received = br.release_frozen(t, cash)
                self.store.add_corporate_event(self.run_id, pf, d, t, "RADIATION_CONTREPARTIE_DOCUMENTEE", qty, cash,
                                               received, f"{sec['delisting_source']} (publiée le "
                                               f"{sec['delisting_source_date']}, payée le {sec['delisting_cash_date']})")

    def _volume_cap(self, ticker: str, d: date) -> int:
        prev = self.ds.last_bar_before(ticker, d)
        return int(prev.volume * self.max_participation) if prev else 0

    def _forced_sells(self, br: PaperBroker, d: date, screenings: dict[str, ScreeningResult], universe: set[str]):
        """Ventes imposées (hors univers, EXCLU, INCERTAIN selon la politique) : mêmes règles pour les références."""
        sells = []
        for t in sorted(br.positions):
            scr = screenings[t]
            if scr.status == ADMISSIBLE:
                continue
            action = self.policy["on_exclu"] if scr.status == EXCLU else incertain_action(self.policy, scr.incertain_causes)
            if action == "SELL":
                close, view = self._close(t, d)
                sells.append((Decision(t, SELL, f"VENTE_STATUT_{scr.status}", "; ".join(scr.reasons),
                                       {"cloture": close}, view.max_date_read), scr))
        return sells

    def _decide_strategy(self, d: date, screenings: dict[str, ScreeningResult], universe: set[str]) -> list[PendingOrder]:
        br = self.brokers["strategie"]
        decisions = []
        for t in sorted(screenings):
            view = PointInTimeView(self.ds, d)
            decisions.append((self.strategy.decide(view, screenings[t], br.positions.get(t, 0) > 0, self.policy),
                              screenings[t]))
        n_adm = sum(1 for s in screenings.values() if s.status == ADMISSIBLE)
        target = self._equity_estimate(br, d) / max(1, n_adm)
        orders, proceeds = self._sell_orders("strategie", br, d, [x for x in decisions if x[0].signal == SELL])
        cash_est = br.cash + proceeds
        for dec, scr in decisions:
            if dec.signal == SELL:
                continue
            if dec.signal != BUY:
                if self.topup and dec.reason_code == "CONSERVE_TENDANCE_HAUSSIERE":
                    close = dec.inputs["cloture"]
                    gap = target - br.positions[dec.ticker] * close
                    qty, _code, detail = self._size_buy(close, min(gap, cash_est)) if gap > 0 else (0, "", "")
                    if qty:
                        cash_est -= qty * self.costs.fill_price(close, "BUY") + self.costs.fee(qty * self.costs.fill_price(close, "BUY"))
                        orders.append(PendingOrder(dec.ticker, "BUY", qty, d, scr.status, "COMPLEMENT_TENDANCE"))
                        self._record("strategie", d, scr.status, dec, BUY, "COMPLEMENT_TENDANCE", f"{dec.detail} ; {detail}")
                        continue
                self._record("strategie", d, scr.status, dec, dec.signal, dec.reason_code, dec.detail)
                continue
            qty, code, detail = self._size_buy(dec.inputs["cloture"], min(target, cash_est))
            if qty == 0:
                self._record("strategie", d, scr.status, dec, NONE, code, f"{dec.detail} ; {detail}")
                continue
            cash_est -= qty * self.costs.fill_price(dec.inputs["cloture"], "BUY")
            cash_est -= self.costs.fee(qty * self.costs.fill_price(dec.inputs["cloture"], "BUY"))
            orders.append(PendingOrder(dec.ticker, "BUY", qty, d, scr.status, dec.reason_code))
            self._record("strategie", d, scr.status, dec, BUY, dec.reason_code, f"{dec.detail} ; {detail}")
        return orders

    def _decide_reference(self, d: date, screenings: dict[str, ScreeningResult], universe: set[str]) -> list[PendingOrder]:
        br = self.brokers["reference"]
        if not self.bench_started:
            self.bench_started = True
            admissible = [t for t in sorted(universe) if screenings[t].status == ADMISSIBLE]
            target, orders, cash_est = self.capital / max(1, len(admissible)), [], br.cash
            for t in admissible:
                close, view = self._close(t, d)
                dec = Decision(t, BUY, "REFERENCE_ACHAT_INITIAL", "Achat initial à parts égales des titres admissibles",
                               {"cloture": close}, view.max_date_read)
                qty, code, detail = self._size_buy(close, min(target, cash_est))
                if qty == 0:
                    self._record("reference", d, ADMISSIBLE, dec, NONE, code, detail)
                    continue
                cash_est -= qty * self.costs.fill_price(close, "BUY") + self.costs.fee(qty * self.costs.fill_price(close, "BUY"))
                orders.append(PendingOrder(t, "BUY", qty, d, ADMISSIBLE, dec.reason_code))
                self._record("reference", d, ADMISSIBLE, dec, BUY, dec.reason_code, f"{dec.detail} ; {detail}")
            return orders
        return self._sell_orders("reference", br, d, self._forced_sells(br, d, screenings, universe))[0]

    def _decide_reinvested(self, d: date, screenings: dict[str, ScreeningResult], universe: set[str]) -> list[PendingOrder]:
        """Règles fixées avant le test (docs/REFERENCES.md) :
        1. ventes imposées identiques à la référence ;
        2. cible par titre = valeur estimée du portefeuille / nombre de titres ADMISSIBLES ;
        3. pour chaque titre ADMISSIBLE (ordre alphabétique) sous sa cible : achat de l'écart, limité aux
           liquidités disponibles, en actions entières, avec le même plafond de coût ;
        4. part trop petite (capital ou coût) : pas d'achat, les liquidités restent et la règle est
           réappliquée le mois suivant ; refus enregistré seulement pour un titre non détenu ;
        5. titre redevenu ADMISSIBLE : traité comme tout autre titre admissible ;
        6. jamais de vente pour rééquilibrer, jamais de SMA."""
        pf, br = "reference_reinvestie", self.brokers["reference_reinvestie"]
        orders, proceeds = self._sell_orders(pf, br, d, self._forced_sells(br, d, screenings, universe))
        sold = {o.ticker for o in orders}
        admissible = [t for t in sorted(universe) if screenings[t].status == ADMISSIBLE]
        target = self._equity_estimate(br, d) / max(1, len(admissible))
        cash_est = br.cash + proceeds
        for t in admissible:
            if t in sold:
                continue
            close, view = self._close(t, d)
            if close is None:
                continue
            held = br.positions.get(t, 0)
            if held and not self.topup:
                continue  # même règle que la stratégie : pas de complément des lignes détenues
            gap = target - held * close
            if gap <= 0:
                continue
            code_ok = "REFERENCE_REINVESTIE_COMPLEMENT" if held else "REFERENCE_REINVESTIE_ACHAT"
            dec = Decision(t, BUY, code_ok, f"Écart à la cible {gap:.2f}", {"cloture": close, "cible": round(target, 2)},
                           view.max_date_read)
            qty, code, detail = self._size_buy(close, min(gap, cash_est))
            if qty == 0:
                if not held:
                    self._record(pf, d, ADMISSIBLE, dec, NONE, code, detail)
                continue
            cash_est -= qty * self.costs.fill_price(close, "BUY") + self.costs.fee(qty * self.costs.fill_price(close, "BUY"))
            orders.append(PendingOrder(t, "BUY", qty, d, ADMISSIBLE, code_ok))
            self._record(pf, d, ADMISSIBLE, dec, BUY, code_ok, f"{dec.detail} ; {detail}")
        return orders

    def _status_at_open(self, ticker: str, d: date) -> str:
        """Statut religieux avec les seuls documents publiés AVANT le jour d (règle J+1) : c'est ce qui est connu
        à l'ouverture. Une exclusion publiée le jour de la décision est donc prise en compte avant d'acheter."""
        key = (ticker, d)
        if key not in self._open_status:
            self._open_status[key] = screen_security(PointInTimeView(self.ds, d), ticker, self.ruleset).status
        return self._open_status[key]

    def _execute(self, pf: str, orders: list[PendingOrder], d: date, universe: set[str]) -> list[PendingOrder]:
        """Simulation de l'exécution à l'ouverture de d.

        Deux natures d'information, volontairement séparées :
        - ce que l'investisseur sait à l'ouverture (documents publiés avant d, volume de la veille) conditionne
          l'ORDRE : titre dans l'univers, statut encore ADMISSIBLE, quantité <= participation x volume de la veille ;
        - la barre du jour (prix d'ouverture, volume total du jour) sert uniquement à MODÉLISER ce que le marché a
          permis : prix d'exécution et quantité exécutable <= participation x volume du jour. Elle n'alimente
          jamais une décision de stratégie (vérifié par test_review5)."""
        br, carry = self.brokers[pf], []
        for o in sorted(orders, key=lambda o: (o.side != "SELL", o.ticker)):
            bar = self.ds.bar_on(o.ticker, d)
            if bar is None:
                delisted = self.ds.securities[o.ticker]["delisted_date"]
                gone = delisted is not None and d >= delisted
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, o.side, o.qty, o.status,
                                              "TITRE_RADIE" if gone else "PRIX_MANQUANT_A_L_EXECUTION"
                                              + (" (vente reportée)" if o.side == "SELL" else ""))
                if o.side == "SELL" and not gone:
                    carry.append(o)
                continue
            if o.side == "BUY" and o.ticker not in universe:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, "BUY", o.qty, o.status,
                                              "HORS_UNIVERS_A_L_EXECUTION")
                continue
            open_status = self._status_at_open(o.ticker, d) if o.side == "BUY" else ""
            if o.side == "BUY" and open_status != ADMISSIBLE:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, "BUY", o.qty, o.status,
                                              f"STATUT_{open_status}_A_L_OUVERTURE")
                continue
            cap_known = self._volume_cap(o.ticker, d)                      # connu à l'ouverture (veille)
            cap_market = int(bar.volume * self.max_participation)          # modèle de marché (volume du jour)
            cap = min(cap_known, cap_market)
            if cap < 1:
                reason = ("VOLUME_VEILLE_INSUFFISANT" if cap_known < 1 else "VOLUME_DU_JOUR_INSUFFISANT (modèle de marché)")
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, o.side, o.qty, o.status,
                                              reason + (" (vente reportée)" if o.side == "SELL" else ""))
                if o.side == "SELL":
                    carry.append(o)
                continue
            if o.side == "SELL":
                held = br.positions.get(o.ticker, 0)
                qty = min(held, cap)
                if qty:
                    self.store.add_fill(self.run_id, br.sell(o.ticker, qty, bar.open, o.decision_date, d, o.status, o.reason))
                if held > qty:  # reliquat au-delà du volume permis : vente poursuivie le jour suivant
                    carry.append(o)
                continue
            qty = min(o.qty, br.max_affordable_qty(bar.open), cap)
            if qty < 1:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, "BUY", o.qty, o.status,
                                              "LIQUIDITES_INSUFFISANTES_A_L_EXECUTION")
                continue
            rt = self.costs.roundtrip_cost_pct(qty * self.costs.fill_price(bar.open, "BUY"))
            if rt > self.max_rt:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, "BUY", qty, o.status,
                                              f"COUT_DISPROPORTIONNE_A_L_EXECUTION ({rt:.2f} %)")
                continue
            self.store.add_fill(self.run_id, br.buy(o.ticker, qty, bar.open, o.decision_date, d, o.status, o.reason,
                                                    status_at_execution=open_status))
        return carry

    def run(self) -> BacktestResult:
        cal = self.ds.calendar
        sma = self.strategy.sma_days
        index = {d: i for i, d in enumerate(cal)}
        decision_dates = [d for d in month_end_dates(cal) if index[d] >= sma - 1]
        if not decision_dates:
            raise PolicyError(f"Historique trop court : au moins {sma} jours de bourse requis")
        start, decision_set = decision_dates[0], set(decision_dates)
        pending: dict[str, list[PendingOrder]] = {p: [] for p in PORTFOLIOS}
        series: dict[str, list[tuple[date, float, float]]] = {p: [] for p in PORTFOLIOS}
        rows = []
        frozen_final: dict[str, float] = {}
        for d in cal:
            self._process_delistings(d)
            today_universe = set(self.ds.universe_at(d))
            for pf in PORTFOLIOS:
                pending[pf] = self._execute(pf, pending[pf], d, today_universe)
            if d >= start:
                for pf, br in self.brokers.items():
                    pv = sum(q * self.ds.last_close_on_or_before(t, d) for t, q in br.positions.items())
                    fz = br.frozen_value_at_last_close()
                    series[pf].append((d, br.cash + pv, pv))  # valeur principale : titres gelés comptés à 0
                    rows.append((pf, d, round(br.cash, 4), round(pv, 4), round(br.cash + pv, 4), round(fz, 4)))
                    frozen_final[pf] = fz
            if d in decision_set:
                universe = set(self.ds.universe_at(d))
                held = {t for br in self.brokers.values() for t in br.positions}
                if held - universe:  # impossible : les radiations sont traitées en début de journée
                    raise RuntimeError(f"Positions hors univers le {d} : {sorted(held - universe)}")
                screenings = {}
                for t in sorted(universe):
                    r = screen_security(PointInTimeView(self.ds, d), t, self.ruleset)
                    self.store.add_screening(self.run_id, r)
                    screenings[t] = r
                pending["strategie"] += self._decide_strategy(d, screenings, universe)
                pending["reference"] += self._decide_reference(d, screenings, universe)
                pending["reference_reinvestie"] += self._decide_reinvested(d, screenings, universe)
        self.store.add_equity_rows(self.run_id, rows)
        metrics = {}
        for pf, br in self.brokers.items():
            metrics[pf] = compute_metrics(series[pf], br.fills, self.capital)
            fz = frozen_final.get(pf, 0.0)
            metrics[pf]["valeur_titres_radies_au_dernier_cours"] = round(fz, 2)
            metrics[pf]["rendement_total_pct_si_radies_au_dernier_cours"] = round(
                100 * ((series[pf][-1][1] + fz) / self.capital - 1), 2)
            self.store.add_metrics(self.run_id, pf, metrics[pf])
        end = cal[-1]
        self.store.finish_run(self.run_id, start, end)
        return BacktestResult(self.run_id, start, end, metrics, self.brokers, series)


def run_backtest(ds: Dataset, config: dict, ruleset: dict, store: Store, **kw) -> BacktestResult:
    return Backtest(ds, config, ruleset, store, **kw).run()
