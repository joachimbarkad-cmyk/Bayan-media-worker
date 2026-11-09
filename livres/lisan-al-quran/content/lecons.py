"""Réunit le contenu des leçons (L) et des lectures suivies (R)."""
import importlib

L = {}
R = {}
VOCAB = {}

for mod in ('lecons_p1', 'lecons_p2a', 'lecons_p2b', 'lecons_p3', 'lecons_p4', 'lectures'):
    try:
        m = importlib.import_module(mod)
    except ModuleNotFoundError as e:
        if e.name != mod:
            raise
        continue
    L.update(getattr(m, 'L', {}))
    R.update(getattr(m, 'R', {}))
    VOCAB.update(getattr(m, 'VOCAB', {}))
