"""Moteur de simulation chronologique jour par jour.

Chronologie d'un jour J :
1. exécution à l'OUVERTURE de J des ordres décidés à la clôture précédente ;
2. valorisation des portefeuilles à la CLÔTURE de J ;
3. si J est le dernier jour de bourse du mois : filtrage + décisions avec les seules
   données datées <= J (via PointInTimeView) ; ordres mis en attente pour J+1.

Deux portefeuilles, mêmes données, mêmes frais, même filtre religieux :
- "strategie" : filtre de tendance SMA ;
- "reference" : achat à parts égales des titres ADMISSIBLES au premier jour de décision,
  puis conservation ; seules les ventes imposées par le filtre religieux sont faites.
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

PORTFOLIOS = ("strategie", "reference")


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

    def _decide_strategy(self, d: date, screenings: dict[str, ScreeningResult]) -> list[PendingOrder]:
        br = self.brokers["strategie"]
        decisions = []
        for t in self.ds.tickers:
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

    def _decide_reference(self, d: date, screenings: dict[str, ScreeningResult]) -> list[PendingOrder]:
        br = self.brokers["reference"]
        if not self.bench_started:
            self.bench_started = True
            admissible = [t for t in self.ds.tickers if screenings[t].status == ADMISSIBLE]
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
        sells = []
        for t in list(br.positions):
            scr = screenings[t]
            if scr.status == ADMISSIBLE:
                continue
            action = self.policy["on_exclu"] if scr.status == EXCLU else incertain_action(self.policy, scr.incertain_causes)
            if action == "SELL":
                close, view = self._close(t, d)
                sells.append((Decision(t, SELL, f"VENTE_STATUT_{scr.status}", "; ".join(scr.reasons),
                                       {"cloture": close}, view.max_date_read), scr))
        return self._sell_orders("reference", br, d, sells)[0]

    def _execute(self, pf: str, orders: list[PendingOrder], d: date) -> list[PendingOrder]:
        br, carry = self.brokers[pf], []
        for o in sorted(orders, key=lambda o: (o.side != "SELL", o.ticker)):
            bar = self.ds.bar_on(o.ticker, d)
            if bar is None:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, o.side, o.qty, o.status,
                                              "PRIX_MANQUANT_A_L_EXECUTION" + (" (vente reportée)" if o.side == "SELL" else ""))
                if o.side == "SELL":
                    carry.append(o)
                continue
            if o.side == "SELL":
                qty = br.positions.get(o.ticker, 0)
                if qty:
                    self.store.add_fill(self.run_id, br.sell(o.ticker, qty, bar.open, o.decision_date, d, o.status, o.reason))
                continue
            qty = min(o.qty, br.max_affordable_qty(bar.open))
            if qty < 1:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, "BUY", o.qty, o.status,
                                              "LIQUIDITES_INSUFFISANTES_A_L_EXECUTION")
                continue
            rt = self.costs.roundtrip_cost_pct(qty * self.costs.fill_price(bar.open, "BUY"))
            if rt > self.max_rt:
                self.store.add_rejected_order(self.run_id, pf, o.decision_date, d, o.ticker, "BUY", qty, o.status,
                                              f"COUT_DISPROPORTIONNE_A_L_EXECUTION ({rt:.2f} %)")
                continue
            self.store.add_fill(self.run_id, br.buy(o.ticker, qty, bar.open, o.decision_date, d, o.status, o.reason))
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
        for d in cal:
            for pf in PORTFOLIOS:
                pending[pf] = self._execute(pf, pending[pf], d)
            if d >= start:
                for pf, br in self.brokers.items():
                    pv = sum(q * self.ds.last_close_on_or_before(t, d) for t, q in br.positions.items())
                    series[pf].append((d, br.cash + pv, pv))
                    rows.append((pf, d, round(br.cash, 4), round(pv, 4), round(br.cash + pv, 4)))
            if d in decision_set:
                screenings = {}
                for t in self.ds.tickers:
                    r = screen_security(PointInTimeView(self.ds, d), t, self.ruleset)
                    self.store.add_screening(self.run_id, r)
                    screenings[t] = r
                pending["strategie"] += self._decide_strategy(d, screenings)
                pending["reference"] += self._decide_reference(d, screenings)
        self.store.add_equity_rows(self.run_id, rows)
        metrics = {}
        for pf, br in self.brokers.items():
            metrics[pf] = compute_metrics(series[pf], br.fills, self.capital)
            self.store.add_metrics(self.run_id, pf, metrics[pf])
        end = cal[-1]
        self.store.finish_run(self.run_id, start, end)
        return BacktestResult(self.run_id, start, end, metrics, self.brokers, series)


def run_backtest(ds: Dataset, config: dict, ruleset: dict, store: Store, **kw) -> BacktestResult:
    return Backtest(ds, config, ruleset, store, **kw).run()
