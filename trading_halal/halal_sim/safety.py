"""Garde-fous : le simulateur ne doit jamais accéder au réseau ni à un courtier.

Le code du paquet n'importe aucune bibliothèque réseau ou de courtage (vérifié par
tests/test_no_real_orders.py et recontrôlé à chaque lancement par scan_package()). En complément, `forbid_network()` coupe les sockets du
processus au démarrage de la ligne de commande : même une dépendance future qui
tenterait une connexion échouerait.
"""
from __future__ import annotations

import ast
import socket
from pathlib import Path

# Bibliothèques réseau et connecteurs de courtage connus : aucune ne doit être importée par le paquet.
FORBIDDEN_IMPORTS = {
    "socket", "urllib", "http", "requests", "httpx", "aiohttp", "websocket", "websockets", "ftplib", "smtplib",
    "telnetlib", "ssl", "subprocess", "asyncio", "multiprocessing", "ctypes", "ccxt", "alpaca", "alpaca_trade_api",
    "ib_insync", "ibapi", "ib_async", "degiro_connector", "saxo_openapi", "oandapyV20", "MetaTrader5", "yfinance",
}
FORBIDDEN_NAMES = ("environ", "getenv", "__import__", "importlib")


class NetworkBlockedError(RuntimeError):
    pass


def _blocked(*_args, **_kwargs):
    raise NetworkBlockedError(
        "Accès réseau interdit : ce simulateur ne se connecte à aucun courtier et n'envoie aucun ordre réel."
    )


def forbid_network() -> None:
    socket.socket.connect = _blocked  # type: ignore[method-assign]
    socket.socket.connect_ex = _blocked  # type: ignore[method-assign]
    socket.create_connection = _blocked  # type: ignore[assignment]
    socket.getaddrinfo = _blocked  # type: ignore[assignment]


def network_blocked() -> bool:
    """Vrai si la coupure réseau est effectivement en place dans ce processus."""
    return (socket.socket.connect is _blocked and socket.socket.connect_ex is _blocked
            and socket.create_connection is _blocked and socket.getaddrinfo is _blocked)


def scan_package(package_dir: str | Path | None = None) -> list[str]:
    """Analyse statique du code du paquet : importations réseau/courtage, lecture de variables
    d'environnement (clés) ou importation dynamique. Renvoie la liste des violations."""
    package_dir = Path(package_dir) if package_dir else Path(__file__).resolve().parent
    violations = []
    for py in sorted(package_dir.glob("*.py")):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                mods = [node.module.split(".")[0]]
            for m in mods:
                if m in FORBIDDEN_IMPORTS and not (py.name == "safety.py" and m == "socket"):
                    violations.append(f"{py.name}:{node.lineno} importe {m}")
            name = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else None
            if name in FORBIDDEN_NAMES:
                violations.append(f"{py.name}:{node.lineno} utilise {name}")
    return violations
