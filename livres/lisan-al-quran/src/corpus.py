"""Accès au texte coranique et à son analyse morphologique.

Sources (téléchargées dans cache/ par fetch_data.sh) :
- quran-morphology.txt : Quranic Arabic Corpus (K. Dukes), version corrigée
  publiée par mustafa0x/quran-morphology (licence GPL). Texte uthmani Tanzil,
  segmenté et analysé (racine, lemme, cas, mode, forme verbale...).
- quranenc-uthmani.json / quranenc-fr.json : texte uthmani et traduction
  française de M. Hamidullah (révisée), via QuranEnc (paquet npm quran-json).

Le texte affiché vient du corpus ; il est contrôlé lettre à lettre contre
QuranEnc (verify_text). Les signes de pause sont repris de QuranEnc.
"""
import json
import os
import re
import unicodedata
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, '..', 'cache')

PAUSE = re.compile('[ۖ-ۜ]')


class Segment:
    __slots__ = ('form', 'pos', 'tags', 'root', 'lem', 'fam', 'vf', 'mood',
                 'pgn', 'case')

    def __init__(self, form, pos, feats):
        self.form = form
        self.pos = pos
        self.tags = set()
        self.root = self.lem = self.fam = self.vf = self.mood = None
        self.pgn = None   # personne/genre/nombre (ex. 3MP, MS, FP)
        self.case = None
        for x in feats.split('|'):
            if not x:
                continue
            if x.startswith('ROOT:'):
                self.root = x[5:]
            elif x.startswith('LEM:'):
                self.lem = x[4:]
            elif x.startswith('FAM:'):
                self.fam = x[4:]
            elif x.startswith('VF:'):
                self.vf = int(x[3:])
            elif x.startswith('MOOD:'):
                self.mood = x[5:]
            elif x in ('NOM', 'ACC', 'GEN'):
                self.case = x
            elif x == 'P' and pos == 'N':
                self.pgn = 'P'        # pluriel (sans genre)
            elif re.fullmatch(r'[123]?(M|F)?(S|D|P)?', x) and x not in ('', 'P') and any(c in x for c in 'MFSD123'):
                self.pgn = x
            else:
                self.tags.add(x)
        # 'P' seul est l'étiquette « préposition » ; 'MP', '3MP'... sont des pgn.

    def is_(self, t):
        return t in self.tags

    def __repr__(self):
        return f'<{self.form} {self.pos} {sorted(self.tags)} {self.lem} {self.pgn} {self.case}>'


class Word:
    __slots__ = ('loc', 'segs', 'text', 'pause')

    def __init__(self, loc):
        self.loc = loc
        self.segs = []
        self.text = ''
        self.pause = ''

    @property
    def stem(self):
        """Segment principal (nom ou verbe hors préfixes et suffixes)."""
        for s in self.segs:
            if s.pos in ('N', 'V') and 'PREF' not in s.tags and 'SUFF' not in s.tags:
                return s
        for s in self.segs:
            if 'PREF' not in s.tags and 'SUFF' not in s.tags:
                return s
        return self.segs[-1]

    @property
    def prefixes(self):
        return [s for s in self.segs if 'PREF' in s.tags]

    @property
    def suffixes(self):
        return [s for s in self.segs if 'SUFF' in s.tags]

    def has_det(self):
        return any('DET' in s.tags for s in self.segs)


class Quran:
    def __init__(self):
        self.words = {}            # (s,a,w) -> Word
        self.verses = defaultdict(list)   # (s,a) -> [Word]
        self.lem_count = Counter()
        self.lem_root = {}
        self.lem_pos = {}
        self.root_count = Counter()
        self.tokens = 0
        self._load()
        enc = json.load(open(os.path.join(CACHE, 'quranenc-uthmani.json'), encoding='utf8'))
        fr = json.load(open(os.path.join(CACHE, 'quranenc-fr.json'), encoding='utf8'))
        self.enc = {(su['id'], v['id']): v['text'] for su in enc for v in su['verses']}
        self.fr = {(su['id'], v['id']): v['translation'] for su in fr for v in su['verses']}
        self.sura_name = {su['id']: su['name'] for su in enc}
        self.sura_fr = {su['id']: su['transliteration'] for su in fr}
        self.sura_len = {su['id']: su['total_verses'] for su in enc}
        self._pauses()

    def _load(self):
        path = os.path.join(CACHE, 'quran-morphology.txt')
        for line in open(path, encoding='utf8'):
            loc, form, pos, feats = line.rstrip('\n').split('\t')
            s, a, w, g = map(int, loc.split(':'))
            key = (s, a, w)
            if key not in self.words:
                self.words[key] = Word(key)
                self.verses[(s, a)].append(self.words[key])
            seg = Segment(form, pos, feats)
            self.words[key].segs.append(seg)
        for wd in self.words.values():
            wd.text = ''.join(s.form for s in wd.segs)
            self.tokens += 1
            st = wd.stem
            if st.lem:
                self.lem_count[st.lem] += 1
                if st.root:
                    self.lem_root[st.lem] = st.root
                self.lem_pos.setdefault(st.lem, st.pos)
            for sg in wd.segs:
                if sg.root:
                    self.root_count[sg.root] += 1
                    break

    @staticmethod
    def skeleton(t):
        LET = re.compile('[ء-يٱ]')
        t = t.replace('ـ', '')
        t = re.sub('[ٱأإآ]', 'ا', t)
        t = re.sub('[ءؤئ]', 'ء', t)
        t = ''.join(c for c in t if LET.match(c) or c == ' ')
        t = t.replace('ى', 'ي')
        t = t.replace('ءا', 'ا').replace('اء', 'ا')
        return ' '.join(t.split())

    def _pauses(self):
        """Reprend les signes de pause de QuranEnc quand les mots s'alignent."""
        for key, wl in self.verses.items():
            ew = self.enc[key].split()
            if len(ew) != len(wl):
                continue
            for w, e in zip(wl, ew):
                p = ''.join(PAUSE.findall(e))
                if p:
                    w.pause = p

    def verify_text(self, keys):
        """Vérifie, verset par verset, l'accord des deux sources (squelette consonantique)."""
        bad = []
        for k in keys:
            a = self.skeleton(' '.join(w.text for w in self.verses[k]))
            b = self.skeleton(self.enc[k])
            if a != b:
                # différences d'orthographe connues (mots soudés, hamza)
                if a.replace(' ', '') != b.replace(' ', ''):
                    bad.append(k)
        return bad

    def verse_words(self, s, a):
        return self.verses[(s, a)]

    def verse_text(self, s, a, pauses=True):
        out = []
        for w in self.verses[(s, a)]:
            out.append(w.text + ((' ' + w.pause) if (pauses and w.pause) else ''))
        return ' '.join(out)

    def range(self, s, a1, a2):
        return [(s, a) for a in range(a1, a2 + 1)]


_Q = None


def Q():
    global _Q
    if _Q is None:
        _Q = Quran()
    return _Q


if __name__ == '__main__':
    q = Q()
    print(q.tokens, len(q.lem_count))
    print(q.verse_text(2, 2))
    for w in q.verse_words(1, 5):
        print(w.text, w.segs)
    print('vérif :', q.verify_text(list(q.verses.keys()))[:30])
