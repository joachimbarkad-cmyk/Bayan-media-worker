"""Courtier SIMULÉ : met à jour un portefeuille en mémoire, rien d'autre.

Il n'existe dans ce projet aucun autre courtier, aucune clé API et aucun appel réseau.
Le courtier simulé refuse lui-même tout achat d'un titre non ADMISSIBLE et toute
exécution qui ne serait pas strictement postérieure à la date de décision.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

from .data import LookaheadError
from .screening import ADMISSIBLE


class ForbiddenOrderError(RuntimeError):
    pass


@dataclass(frozen=True)
class CostModel:
    fixed_fee: float = 1.0
    pct_fee: float = 0.0
    min_fee: float = 1.0
    slippage_bps: float = 10.0

    def fee(self, notional: float) -> float:
        return max(self.min_fee, self.fixed_fee + self.pct_fee * notional)

    def fill_price(self, reference: float, side: str) -> float:
        """Prix d'exécution défavorable : écart (glissement) ajouté à l'achat, retranché à la vente."""
        s = self.slippage_bps / 10_000
        return reference * (1 + s) if side == "BUY" else reference * (1 - s)

    def roundtrip_cost_pct(self, notional: float) -> float:
        """Coût estimé aller-retour (frais achat + vente + glissement x2) en % du montant."""
        if notional <= 0:
            return math.inf
        return 100 * (2 * self.fee(notional) + 2 * notional * self.slippage_bps / 10_000) / notional


@dataclass
class Fill:
    portfolio: str
    ticker: str
    side: str
    qty: int
    decision_date: date
    execution_date: date
    ref_price: float
    exec_price: float
    notional: float
    fees: float
    slippage_cost: float
    screening_status: str
    reason: str
    screening_status_exec: str = ""  # statut recalculé à l'ouverture d'exécution (achats)


@dataclass
class PaperBroker:
    name: str
    cash: float
    costs: CostModel
    positions: dict[str, int] = field(default_factory=dict)
    fills: list[Fill] = field(default_factory=list)
    # Titres radiés sans contrepartie documentée : ni vendables ni valorisables avec certitude.
    # ticker -> {"qty", "last_close", "date"} ; le rapport donne deux scénarios (à 0 et au dernier cours), pas des bornes.
    frozen: dict[str, dict] = field(default_factory=dict)

    def freeze(self, ticker: str, last_close: float, d: date) -> int:
        qty = self.positions.pop(ticker)
        prev = self.frozen.get(ticker, {"qty": 0})
        self.frozen[ticker] = {"qty": prev["qty"] + qty, "last_close": last_close, "date": d}
        return qty

    def release_frozen(self, ticker: str, cash_per_share: float) -> tuple[int, float]:
        """Contrepartie en espèces DOCUMENTÉE, publiée et payée, d'un titre radié gelé : pas de frais ni de glissement."""
        qty = self.frozen.pop(ticker)["qty"]
        self.cash += qty * cash_per_share
        return qty, qty * cash_per_share

    def frozen_value_at_last_close(self) -> float:
        return sum(v["qty"] * v["last_close"] for v in self.frozen.values())

    def max_affordable_qty(self, ref_price: float) -> int:
        price = self.costs.fill_price(ref_price, "BUY")
        qty = int(self.cash // price)
        while qty > 0 and qty * price + self.costs.fee(qty * price) > self.cash + 1e-9:
            qty -= 1
        return qty

    def _check(self, qty: int, decision_date: date, execution_date: date) -> None:
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantité entière strictement positive requise (pas de fractions d'action)")
        if execution_date <= decision_date:
            raise LookaheadError("L'exécution doit être strictement postérieure à la décision")

    def buy(self, ticker: str, qty: int, ref_price: float, decision_date: date, execution_date: date,
            screening_status: str, reason: str, *, status_at_execution: str) -> Fill:
        """Achat simulé. Le statut doit être ADMISSIBLE à la décision ET à l'ouverture d'exécution (une exclusion
        publiée entre les deux, donc connue à l'ouverture selon la règle J+1, bloque l'achat)."""
        for label, st in (("à la décision", screening_status), ("à l'exécution", status_at_execution)):
            if st != ADMISSIBLE:
                raise ForbiddenOrderError(f"Achat de {ticker} interdit : statut {st} {label} (seul ADMISSIBLE est achetable)")
        self._check(qty, decision_date, execution_date)
        price = self.costs.fill_price(ref_price, "BUY")
        notional = qty * price
        fees = self.costs.fee(notional)
        if notional + fees > self.cash + 1e-9:
            raise ForbiddenOrderError("Liquidités insuffisantes : pas de marge, pas d'emprunt")
        self.cash -= notional + fees
        self.positions[ticker] = self.positions.get(ticker, 0) + qty
        fill = Fill(self.name, ticker, "BUY", qty, decision_date, execution_date, ref_price, price, notional, fees,
                    qty * (price - ref_price), screening_status, reason, status_at_execution)
        self.fills.append(fill)
        return fill

    def sell(self, ticker: str, qty: int, ref_price: float, decision_date: date, execution_date: date,
             screening_status: str, reason: str) -> Fill:
        self._check(qty, decision_date, execution_date)
        if qty > self.positions.get(ticker, 0):
            raise ForbiddenOrderError("Vente supérieure à la position détenue : vente à découvert interdite")
        price = self.costs.fill_price(ref_price, "SELL")
        notional = qty * price
        fees = self.costs.fee(notional)
        self.cash += notional - fees
        self.positions[ticker] -= qty
        if not self.positions[ticker]:
            del self.positions[ticker]
        fill = Fill(self.name, ticker, "SELL", qty, decision_date, execution_date, ref_price, price, notional, fees,
                    qty * (ref_price - price), screening_status, reason)
        self.fills.append(fill)
        return fill
