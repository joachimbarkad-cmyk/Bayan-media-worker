"""Extrait du PDF (signets) le numéro de page de chaque partie, leçon, lecture et annexe."""
import json
import sys
from pypdf import PdfReader

sys.path.insert(0, 'content')
from plan import PARTS, LESSONS, READINGS  # noqa: E402

reader = PdfReader(sys.argv[1])
found = {}


def walk(items):
    for it in items:
        if isinstance(it, list):
            walk(it)
        else:
            t = ''.join(str(it.title).replace('\u2010', '').replace('\u00ad', '').split())
            try:
                p = reader.get_destination_page_number(it) + 1
            except Exception:
                continue
            found.setdefault(t, p)


walk(reader.outline)
pages = {}
for p, pt, pa in PARTS:
    for t, n in found.items():
        if t == ''.join(pt.split()):
            pages['P' + p] = n
for n, part, t, ta, _ in LESSONS:
    if ''.join(t.split()) in found:
        pages[f'L{n}'] = found[''.join(t.split())]
for k, t, ta, rg in READINGS:
    if ''.join(t.split()) in found:
        pages[f'T{k}'] = found[''.join(t.split())]
for t, n in found.items():
    if t.startswith('Commentutiliser'):
        pages['intro'] = n
    for letter in 'ABCDEF':
        if t.startswith(letter + '.'):
            pages[letter] = n
missing = [f'L{n}' for n, *_ in LESSONS if f'L{n}' not in pages] + [f'T{k}' for k, *_ in READINGS if f'T{k}' not in pages]
json.dump(pages, open(sys.argv[2], 'w'), indent=1)
print(len(pages), 'repères ; manquants :', missing[:20], '; pages :', len(reader.pages))
