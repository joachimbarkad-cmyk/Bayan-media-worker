"""Couverture, pages liminaires, introduction, présentation des parties, aide-mémoire."""
from annexes_texte import COUVERTURE, PAGE_TITRE, INTRO, PARTIES  # noqa: F401
try:
    from aide_memoire import AIDE_MEMOIRE  # noqa: F401
except ModuleNotFoundError:
    AIDE_MEMOIRE = '<p>(à venir)</p>'
