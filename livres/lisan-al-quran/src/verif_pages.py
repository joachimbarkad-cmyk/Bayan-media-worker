"""Vérifie que chaque titre du sommaire se trouve bien à la page annoncée."""
import json
import re
import sys
from pypdf import PdfReader

sys.path.insert(0, 'content')
from plan import LESSONS, READINGS  # noqa: E402

pdf, pages = sys.argv[1], json.load(open(sys.argv[2]))
r = PdfReader(pdf)
norm = lambda t: re.sub(r'[\s­‐-]+', '', t).lower()
errs = 0
items = [(f'L{n}', t) for n, _, t, _, _ in LESSONS] + [(f'T{k}', t) for k, t, _, _ in READINGS]
for key, title in items:
    p = pages.get(key)
    txt = norm(r.pages[p - 1].extract_text()) if p else ''
    if norm(title)[:25] not in txt:
        errs += 1
        print('page incorrecte :', key, title, p)
print('vérification des pages :', 'OK' if not errs else f'{errs} erreurs', f'({len(items)} titres)')
sys.exit(1 if errs else 0)
