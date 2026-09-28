"""Garde-fous : le simulateur ne doit jamais accéder au réseau ni à un courtier.

Le code du paquet n'importe aucune bibliothèque réseau ou de courtage (vérifié par
tests/test_safety.py). En complément, `forbid_network()` coupe les sockets du
processus au démarrage de la ligne de commande : même une dépendance future qui
tenterait une connexion échouerait.
"""
from __future__ import annotations

import socket


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
