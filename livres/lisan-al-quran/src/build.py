"""Assemble le livre Lisān al-Qurʾān en HTML (puis render.mjs produit le PDF).

Usage : python3 src/build.py [--pages build/pages.json] [--only 1,2]
"""
import html
import json
import unicodedata
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'content'))

from corpus import Q  # noqa: E402
from analyse import (lexicon, notions_of, describe, NOTIONS, bare, PERS, CASE, CASE_AR, MOOD,  # noqa: E402
                     ROMAN, gender_of, number_of, subject_suffix, is_idafa_head, ending_kind,
                     is_vocative, is_mabni_damma)
from plan import PARTS, LESSONS, READINGS, expand  # noqa: E402
import lecons  # noqa: E402
import formes  # noqa: E402
import annexes  # noqa: E402

q = Q()
LEX = lexicon()
E = html.escape

AR_DIG = '٠١٢٣٤٥٦٧٨٩'


def ar_num(n):
    return ''.join(AR_DIG[int(d)] for d in str(n))


def sura_label(s):
    return f"{q.sura_fr[s]} ({s})"


def ref_label(s, a, b=None):
    if b and b != a:
        return f"{q.sura_fr[s]} · {s} : {a}–{b}"
    return f"{q.sura_fr[s]} · {s} : {a}"


def ranges_label(rs):
    return ' ; '.join(ref_label(s, a, b) for s, a, b in rs)


PROBLEMS = []   # erreurs bloquantes
WARN = []

# ------------------------------------------------------------- markup
# Syntaxe dans les textes des leçons :
#   [[عربي]]                         arabe en ligne (police Amiri)
#   {{v S:A|hl=mot,mot}}             verset encadré (+ traduction), mots surlignés
#   {{ex S:A|hl=..|from=..|to=..|com=..}}  ligne d'exemple (extrait si from/to)
#   {{x S:A|from=..|to=..|hl=..}}    extrait en ligne
# Un mot se désigne par son orthographe courante (ex. الكتاب) ou par #n (rang).
RE_AR = re.compile(r'\[\[(.+?)\]\]')
RE_TAG = re.compile(r'\{\{(v|ex|x|q) (\d+):(\d+)((?:\|[^}]*)?)\}\}')
RE_L = re.compile(r'\{\{L(\d+)\}\}')

USED_REFS = defaultdict(set)   # (s,a) -> {contexte}
_DIAC = re.compile('[\u064b-\u065f\u0670\u06d6-\u06e4\u06e5\u06e6\u06ea-\u06ed\u0640\u06df\u06e0\u06e1\u06e2\u06e3]')


def loose(t):
    t = t.replace('\u06e7', '\u064a').replace('\u06e8', '\u0646')
    # petits yāʾ / wāw en milieu de mot = vraies lettres (إِبْرَٰهِۦمَ, دَاوُۥدَ)
    t = re.sub('\u06e6(?=[\u064b-\u065f]*[\u0621-\u064a])', '\u064a', t)
    t = re.sub('\u06e5(?=[\u064b-\u065f]*[\u0621-\u064a])', '\u0648', t)
    t = re.sub('\u0648\u0670', '', t)          # ـوٰ lu ā (ṣalāh)
    t = re.sub('\u0649\u0670(?=[\u064b-\u065f\u06d6-\u06ed]*[\u0621-\u064a])', '', t)     # ـىٰـ en milieu de mot lu ā
    t = _DIAC.sub('', t)
    t = re.sub('[\u0621\u0623\u0625\u0622\u0627\u0671\u0624\u0626]', '', t)
    t = t.replace('\u0649', '\u064a').replace('\u0629', '\u0647')
    return t


def find_word(s, a, spec, ctx='', after=0):
    ws = q.verse_words(s, a)
    spec = spec.strip()
    if spec.startswith('#'):
        k = int(spec[1:])
        if 1 <= k <= len(ws):
            return k
        PROBLEMS.append(f'{ctx}: mot #{k} hors du verset {s}:{a}')
        return None
    occ = 1
    if '@' in spec:
        spec, o = spec.split('@')
        occ = int(o)
    key = loose(spec)
    hits = [i for i, w in enumerate(ws, 1) if loose(w.text) == key and i > after]
    if len(hits) < occ:
        hits = [i for i, w in enumerate(ws, 1)
                if (loose(w.text) == key or re.sub('^[وفبلك]{1,2}', '', loose(w.text)) == key) and i > after]
    if len(hits) >= occ:
        return hits[occ - 1]
    PROBLEMS.append(f'{ctx}: « {spec} » introuvable dans {s}:{a} ({" ".join(w.text for w in ws)})')
    return None


def parse_args(argstr):
    d = {}
    for part in argstr.split('|'):
        if not part:
            continue
        if '=' in part:
            k, v = part.split('=', 1)
            d[k.strip()] = v
        else:
            d.setdefault('hl', part)
    return d


def hl_set(s, a, d, ctx):
    out = set()
    if d.get('hl'):
        for sp in d['hl'].split(','):
            k = find_word(s, a, sp, ctx)
            if k:
                out.add(k)
    return out


def verse_html(s, a, hl=(), w1=None, w2=None, ends=True):
    if (s, a) not in q.verses:
        PROBLEMS.append(f'verset inexistant {s}:{a}')
        return ''
    ws = q.verse_words(s, a)
    w1 = w1 or 1
    w2 = w2 or len(ws)
    out = []
    for i in range(w1, w2 + 1):
        w = ws[i - 1]
        t = E(w.text) + (('\u00a0' + E(w.pause)) if (w.pause and i < w2) else '')
        out.append(f'<span class="h">{t}</span>' if i in hl else t)
    txt = ' '.join(out)
    if not ends:
        return txt
    if w1 > 1:
        txt = '… ' + txt
    if w2 < len(ws):
        return txt + ' …'
    return txt + f' <span class="n">﴿{ar_num(a)}﴾</span>'


def verse_block(s, a, hl=(), fr=True, ctx='exemple'):
    USED_REFS[(s, a)].add(ctx)
    tr = q.fr[(s, a)]
    return (f'<div class="verset"><span class="q">{verse_html(s, a, hl)}</span>'
            + (f'<span class="fr">« {E(tr)} »</span>' if fr else '')
            + f'<span class="ref">{E(ref_label(s, a))}</span></div>')


def tag(kind, s, a, argstr):
    ctx = f'{{{{{kind} {s}:{a}}}}}'
    if (s, a) not in q.verses:
        PROBLEMS.append(f'verset inexistant {s}:{a}')
        return ''
    d = parse_args(argstr)
    hl = hl_set(s, a, d, ctx)
    w1 = find_word(s, a, d['from'], ctx) if d.get('from') else None
    w2 = find_word(s, a, d['to'], ctx, after=(w1 or 1) - 1) if d.get('to') else None
    if kind == 'v':
        return verse_block(s, a, hl, fr=d.get('fr') != 'non')
    USED_REFS[(s, a)].add('exemple')
    if kind == 'x':
        return f'<span class="qin">{verse_html(s, a, hl, w1, w2)}</span> <span class="gris petit">({s}:{a})</span>'
    if kind == 'q':
        return f'<span class="qin">{verse_html(s, a, hl, w1, w2, ends=False)}</span>'
    arab = verse_html(s, a, hl, w1, w2)
    fr = '' if (w1 or w2) and d.get('fr') != 'oui' else f'<span class="fr">« {E(q.fr[(s, a)])} »</span>'
    com = d.get('com', '')
    return (f'<div class="ex"><span class="q">{arab}</span>{fr}<span class="ref">{E(ref_label(s, a))}</span>'
            + (f'<span class="com">{markup(com)}</span>' if com else '') + '</div>')


def markup(t):
    if not t:
        return ''
    t = RE_TAG.sub(lambda m: tag(m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)), t)
    t = RE_AR.sub(lambda m: f'<span class="ar" lang="ar">{m.group(1)}</span>', t)
    t = RE_L.sub(lambda m: f'<a href="#L{m.group(1)}">L{m.group(1)}</a>', t)
    return t


# ---------------------------------------------------------- vocabulaire
BLACK_POS_TAGS = {'PRON', 'REL', 'DEM', 'INTG', 'COND', 'PN'}
BLACK_LEM = set('إِذا إِذ لَمّا مَع دُون عِند بَيْن قَبْل بَعْد ذُو كُلّ بَعْض غَيْر إِيّا لَدُن حَيْث أَيّ أَنَّى كَيْف لَيْسَ'.split())
_first_tags = {}
for line in open(os.path.join(ROOT, 'content', 'lemmes_index.tsv'), encoding='utf8'):
    n, lem, pos, root, tags, cnt, ex, ref = line.rstrip('\n').split('\t')
    _first_tags[lem] = (pos, set(tags.split(',')) if tags else set())


def lexical(lem):
    if lem not in LEX or lem not in _first_tags:
        return False
    pos, tags = _first_tags[lem]
    if pos not in ('N', 'V'):
        return False
    if tags & BLACK_POS_TAGS or lem in BLACK_LEM:
        return False
    return True


# formes d'inaccompli et de pluriel tirées du corpus
IMPF = {}
PLUR = {}
FINAL = re.compile('[\u064b-\u0650\u0652\u06d6-\u06ed]+$')


def _collect_forms():
    cand_i = defaultdict(list)
    cand_p = defaultdict(list)
    for w in q.words.values():
        st = w.stem
        if not st.lem:
            continue
        emph = any('EMPH' in x.tags for x in w.suffixes)
        if st.pos == 'V' and 'IMPF' in st.tags and 'PASS' not in st.tags and st.mood == 'IND' and not emph:
            f = st.form
            if len(f) > 2 and f[0] in 'يتنأ' and f[1] in '\u064e\u064f':
                score = 0 if st.pgn == '3MS' else 1 if st.pgn in ('3FS', '2MS', '1P', '1S') else 2
                if score == 2 and (not f.endswith('\u064f') or (st.root and st.root[-1] in 'وي')):
                    continue
                f = re.sub('[\u0627][\u06df\u06e0]$', '', re.sub('\u0653', '', f))   # alif muet final
                if f.endswith('\u064e'):
                    continue
                cand_i[st.lem].append((score, 'ي' + f[1:]))
        if st.pos == 'N' and number_of(st.pgn) == 'P' and not ending_kind(st) and 'PRON' not in st.tags:
            f = st.form
            b = bare(f)
            if b.endswith(('ي', 'و')) and st.pgn in ('MP', 'P') and f[-2:-1] in ('\u0650', '\u064f'):
                continue            # pluriel externe à l'état construit (‑ī, ‑ū)
            if len(f) > 1 and f[1] == '\u0651':
                f = f[0] + f[2:]    # shadda d'assimilation à l'initiale
            if w.suffixes and re.search('\u064e?\u062a[\u064b-\u0650]?$', f) and not b.endswith('ات'):
                f = re.sub('\u062a([\u064b-\u0650]?)$', '\u0629\\1', f)   # ة écrit ت devant suffixe
            score = {'NOM': 0, 'GEN': 1, 'ACC': 2}.get(st.case, 3) + (5 if w.suffixes else 0)
            cand_p[st.lem].append((score, f))
    for lem, c in cand_i.items():
        c.sort(key=lambda x: x[0])
        IMPF[lem] = c[0][1]
    for lem, c in cand_p.items():
        c.sort(key=lambda x: x[0])
        f = c[0][1]
        f = re.sub('[\u0627][\u06df\u06e0]$', '', f)
        f = re.sub('\u064b\u0627?$', '', f)    # tanwīn fatḥ + alif
        f = re.sub('\u0627\u064b$', '', f)
        f = FINAL.sub('', f)
        f = re.sub('[\u0624\u0626]$', '\u0621', f)   # support de hamza final
        PLUR[lem] = f
    nf = lambda x: unicodedata.normalize('NFC', x)
    by_nf = defaultdict(list)
    for lem in LEX:
        by_nf[nf(lem)].append(lem)
    for k, v in formes.IMPF.items():
        for lem in by_nf.get(nf(k), []):
            IMPF[lem] = v
    for k, v in formes.PLURAL.items():
        for lem in by_nf.get(nf(k), []):
            PLUR[lem] = v
    for k in formes.NO_PLURAL:
        for lem in by_nf.get(nf(k), []):
            PLUR.pop(lem, None)
    for lem in list(PLUR):
        if bare(PLUR[lem]).endswith('ت') and bare(lem).endswith('ة'):
            del PLUR[lem]            # pluriel externe féminin (ـَٰت)


_collect_forms()


def add_fatha(t):
    """Ajoute la fatḥa implicite devant un alif de prolongation (قالَ → قَالَ, جَبّار → جَبَّار)."""
    return re.sub('([\u0628-\u064a])(\u0651?)(?=\u0627)', lambda m: m.group(1) + m.group(2) + '\u064e', t)


def cmp_key(t):
    t = re.sub('[\u064b-\u065f\u06d6-\u06ed\u0640]', '', t.replace('\u0670', '\u0627'))
    t = re.sub('[\u0621\u0623\u0625\u0622\u0671\u0624\u0626]', '\u0627', t)
    t = re.sub('\u0627+', '\u0627', t).replace('\u0649', '\u064a').replace('\u0629', '\u0647')
    return t


def vocab_display(lem):
    e = LEX[lem]
    pos = _first_tags[lem][0]
    disp = add_fatha(e['disp'])
    extra = ''
    if pos == 'V' and lem in IMPF:
        extra = f' <span class="imp">– {E(IMPF[lem])}</span>'
    elif pos == 'N' and lem in PLUR and cmp_key(PLUR[lem]) != cmp_key(disp):
        extra = f' <span class="imp">ج {E(PLUR[lem])}</span>'
    return E(disp) + extra


# --------------------------------------------------- révision espacée
class Planner:
    """Suit, pour chaque notion et chaque mot de vocabulaire, la leçon d'étude
    et les révisions ; décide quand une occurrence doit être signalée."""

    def __init__(self):
        self.state = {}       # clé -> [intro, dernière, intervalle]
        self.history = defaultdict(list)   # clé -> [(lieu, étape)]

    def intro(self, key, step):
        self.state[key] = [step, step, 1]

    def mark(self, key, step, place):
        """Renvoie 'new', 'rev', 'known' ou None (pas encore étudié)."""
        st = self.state.get(key)
        if st is None:
            return None
        if st[0] == step:
            return 'new'
        if step - st[1] >= st[2]:
            st[1] = step
            st[2] = min(st[2] * 2, 8)
            self.history[key].append((place, step))
            return 'rev'
        return 'known'


PLAN = Planner()
NOTION_HISTORY = defaultdict(list)    # notion -> [(lieu, étape)] toutes occurrences
VOCAB_INTRO = {}                      # lemme -> leçon
VOCAB_BY_LESSON = {}
KNOWN_UNTIL = {}                      # étape -> set(lemmes)


def pick_vocab(n, refs):
    """Vocabulaire de la leçon n : mots fréquents du texte, puis mots fréquents du Coran."""
    spec = getattr(lecons, 'VOCAB', {}).get(n)
    chosen = []
    cnt = Counter()
    for k in refs:
        for w in q.verse_words(*k):
            lem = w.stem.lem
            if lem and lexical(lem):
                cnt[lem] += 1
    cands = sorted(cnt, key=lambda x: (-q.lem_count[x], x))
    for lem in cands:
        if lem in VOCAB_INTRO or q.lem_count[lem] < 4:
            continue
        chosen.append(lem)
        if len(chosen) >= 9:
            break
    if spec:
        for lem in spec:
            if lem not in VOCAB_INTRO and lem not in chosen:
                chosen.append(lem)
    for lem, c in q.lem_count.most_common():
        if len(chosen) >= 13:
            break
        if lem in VOCAB_INTRO or lem in chosen or not lexical(lem):
            continue
        chosen.append(lem)
    for lem in chosen:
        VOCAB_INTRO[lem] = n
        PLAN.intro(('v', lem), n)
    VOCAB_BY_LESSON[n] = chosen
    return chosen


def coverage(lems):
    tot = sum(q.lem_count.values())
    return 100.0 * sum(q.lem_count[x] for x in lems) / tot


# ------------------------------------------------------ lecture guidée
def check_note_quotes(s, a, note, place):
    """Chaque citation [[...]] d'une note doit se retrouver mot à mot dans le verset."""
    keys = [loose(w.text) for w in q.verse_words(s, a)]
    stripped = [re.sub('^[وفبلك]{1,2}', '', k) for k in keys]
    for m in RE_AR.finditer(note):
        frag = m.group(1)
        for tok in frag.split():
            k = loose(tok)
            if not k or k in keys or k in stripped or re.sub('^[وفبلك]{1,2}', '', k) in stripped:
                continue
            WARN.append(f'note {place} {s}:{a} : « {tok} » absent du verset')



def guided_text(step, place, ranges, notes=None, current_lesson=None):
    notes = notes or {}
    refs = expand(ranges)
    bad = q.verify_text(refs)
    if bad:
        WARN.append(f'texte {place}: écarts orthographiques avec QuranEnc {bad}')
    seen_items = set()
    anticip = set()
    stats = Counter()
    reviewed = Counter()
    news = Counter()
    out = []
    for (s, a) in refs:
        USED_REFS[(s, a)].add('lecture')
        words = q.verse_words(s, a)
        rows = []
        for i, w in enumerate(words):
            sense, ana = describe(words, i)
            nts = notions_of(words, i)
            marks = []
            known_word = True
            for nid in nts:
                NOTION_HISTORY[nid].append((place, step))
                key = ('n', nid)
                lesson_of, label = NOTIONS[nid]
                if key in seen_items:
                    continue
                r = PLAN.mark(key, step, place)
                if r is None:
                    if nid not in anticip and current_lesson is not None:
                        anticip.add(nid)
                        marks.append(f'<span class="m ant">→{lesson_of} {E(label)}</span>')
                    known_word = False
                elif r == 'new':
                    seen_items.add(key)
                    news[nid] += 1
                    marks.append(f'<span class="m new">★ {E(label)}</span>')
                    known_word = False
                elif r == 'rev':
                    seen_items.add(key)
                    reviewed[nid] += 1
                    marks.append(f'<span class="m rev">↺{lesson_of} {E(label)}</span>')
                    known_word = False
            lem = w.stem.lem
            vmark = ''
            stats['mots'] += 1
            if lem and lexical(lem):
                stats['lexicaux'] += 1
                key = ('v', lem)
                if lem in VOCAB_INTRO and VOCAB_INTRO[lem] <= (current_lesson or 99):
                    stats['connus'] += 1
                if key not in seen_items:
                    r = PLAN.mark(key, step, place)
                    if r == 'new':
                        vmark = '<span class="m new">★ vocabulaire</span>'
                        seen_items.add(key)
                        known_word = False
                    elif r == 'rev':
                        vmark = f'<span class="m voc">↺{VOCAB_INTRO[lem]} vocabulaire</span>'
                        seen_items.add(key)
                        stats['vocrev'] += 1
                        known_word = False
                    elif r is None:
                        known_word = False
            cls = ' class="connu"' if known_word and not marks and not vmark else ''
            rows.append(
                f'<tr{cls}><td class="i">{i + 1}</td><td class="w">{E(w.text)}</td>'
                f'<td class="s"><span class="k">{E(sense)}</span> {vmark}</td>'
                f'<td class="an">{E(ana)}{"<br>" if marks else ""}{"".join(marks)}</td></tr>')
        note = notes.get((s, a)) or notes.get(a)
        if note:
            check_note_quotes(s, a, note, place)
        out.append(
            f'<div class="bloc-verset"><div class="vv"><span class="q">{verse_html(s, a)}</span>'
            f'<div class="fr">{E(ref_label(s, a))} — « {E(q.fr[(s, a)])} »</div>'
            + (f'<div class="note"><b>Note.</b> {markup(note)}</div>' if note else '')
            + '</div>'
            f'<table class="mots">{"".join(rows)}</table></div>')
    # bilan
    pct = 100.0 * stats['connus'] / max(1, stats['lexicaux'])
    rv = ', '.join(f'{E(NOTIONS[n][1])} <span class="gris">(L{NOTIONS[n][0]})</span>'
                   for n, _ in sorted(reviewed.items(), key=lambda x: NOTIONS[x[0]][0]))
    nw = ', '.join(E(NOTIONS[n][1]) for n in news)
    late = []
    if current_lesson:
        for nid, (les, lab) in NOTIONS.items():
            if les >= min(current_lesson, step) or nid in ('racine',):
                continue
            seen_steps = [st_ for pl, st_ in NOTION_HISTORY[nid]]
            last = max(seen_steps) if seen_steps else les
            if step - max(last, les) >= 8:
                late.append((les, lab))
    bil = (f'<div class="bilan"><span class="lab">Bilan de révision</span><br>'
           f'{stats["mots"]} mots ; vocabulaire déjà étudié : <b>{pct:.0f} %</b> des mots lexicaux'
           f'<div class="jauge"><span style="width:{pct:.0f}%"></span></div>'
           + (f'<b>Nouveau ici :</b> {nw}.<br>' if nw else '')
           + (f'<b>Révisé en lisant :</b> {rv}.' if rv else '')
           + (f' {stats["vocrev"]} mots de vocabulaire revus.' if stats['vocrev'] else '')
           + ('<br><b>Fiches à relire</b> (pas rencontrées depuis longtemps) : '
              + ', '.join(f'fiche {les} ({E(lab)})' for les, lab in sorted(set(late))[:6]) + '.' if late else '')
           + '</div>')
    return ''.join(out) + bil


# --------------------------------------------------------- exercices auto
def auto_items(kind, ranges, n):
    refs = expand(ranges) if ranges and isinstance(ranges[0], tuple) and len(ranges[0]) == 3 else ranges
    cands = []
    for (s, a) in refs:
        words = q.verse_words(s, a)
        for i, w in enumerate(words):
            st = w.stem
            qa = None
            if is_vocative(w) or is_mabni_damma(w) or st.lem in ('أَيّ',):
                continue
            if kind == 'cas' and st.pos == 'N' and st.case and 'PRON' not in st.tags and 'PN' not in st.tags:
                qa = ('cas ?', f'{CASE[st.case]} ({CASE_AR[st.case]})')
            elif kind == 'defini' and st.pos == 'N' and st.case and not ({'PRON', 'REL', 'DEM', 'INTG', 'T', 'LOC'} & st.tags):
                if w.has_det():
                    r = "défini par l'article al-"
                elif 'PN' in st.tags:
                    r = 'défini (nom propre)'
                elif 'INDEF' in st.tags:
                    r = 'indéfini (tanwīn)'
                elif any('PRON' in x.tags for x in w.suffixes):
                    r = 'défini par annexion à un pronom'
                elif is_idafa_head(words, i):
                    r = 'annexé (prend la définition de son complément)'
                else:
                    continue
                qa = ('défini ou indéfini ? pourquoi ?', r)
            elif kind == 'genre_nombre' and st.pos == 'N' and st.pgn and not ({'PRON', 'REL', 'DEM', 'PN', 'INTG'} & st.tags):
                g, nb = gender_of(st.pgn), number_of(st.pgn)
                if not g or not nb or (nb == 'P' and not ending_kind(st)):
                    continue
                qa = ('genre et nombre ?', f"{'masculin' if g == 'M' else 'féminin'} {'singulier' if nb == 'S' else 'duel' if nb == 'D' else 'pluriel'}")
            elif kind == 'racine' and st.root and st.pos in ('N', 'V') and len(st.root) in (3, 4) and 'PN' not in st.tags:
                qa = ('racine ?', ' '.join(st.root))
            elif kind == 'verbe' and st.pos == 'V':
                t = 'accompli' if 'PERF' in st.tags else 'impératif' if 'IMPV' in st.tags else 'inaccompli'
                qa = ('temps et personne ?', f"{t}{' passif' if 'PASS' in st.tags else ''}, {PERS.get(st.pgn, st.pgn)}")
            elif kind == 'forme' and st.vf and st.pos in ('V', 'N') and st.root:
                qa = ('forme verbale ?', f"forme {ROMAN[st.vf]} (racine {' '.join(st.root)})")
            elif kind == 'mode' and st.pos == 'V' and 'IMPF' in st.tags and st.mood and st.pgn not in ('3FP', '2FP'):
                prev = [x for x in words[max(0, i - 2):i]]
                why = ''
                for pw in reversed(prev):
                    for sg in pw.segs:
                        if sg.lem in ('أَن', 'لَن', 'كَي', 'حَتَّى') or 'PRP' in sg.tags:
                            why = f' (après {bare(sg.form)})'
                        if sg.lem in ('لَم', 'لَمّا') or 'PRO' in sg.tags or 'COND' in sg.tags or 'IMPV' in sg.tags:
                            why = f' (après {bare(sg.form)})'
                    if why:
                        break
                for sg in w.prefixes:
                    if 'PRP' in sg.tags or 'IMPV' in sg.tags:
                        why = f' (après {bare(sg.form)}-)'
                qa = ('mode ?', f"{MOOD[st.mood]} ({ {'IND': 'marfūʿ', 'SUBJ': 'manṣūb', 'JUS': 'majzūm'}[st.mood]}){why}")
            elif kind == 'pron':
                sj = subject_suffix(w)
                for k, sg in enumerate(w.segs):
                    if 'PRON' in sg.tags and 'SUFF' in sg.tags and k != sj:
                        host = w.segs[k - 1].pos if k else 'N'
                        role = {'N': 'complément du nom', 'V': "complément d'objet", 'P': 'après particule ou préposition'}[host]
                        qa = ('pronom suffixe : personne et fonction ?', f'‑{bare(sg.form)} : {PERS.get(sg.pgn, sg.pgn)}, {role}')
                        break
            elif kind == 'prep' and any(sg.pos == 'P' and 'P' in sg.tags for sg in w.segs):
                nx = [sg for sg in w.segs if sg.pos == 'N']
                if nx and nx[0].case == 'GEN':
                    qa = ('préposition et cas du nom ?', 'préposition + génitif')
                elif i + 1 < len(words) and words[i + 1].stem.case == 'GEN' and not w.stem.pos == 'N':
                    qa = ('préposition et cas du nom suivant ?', 'préposition + génitif')
            if qa:
                cands.append(((s, a, i + 1), w.text, qa))
    if not cands:
        PROBLEMS.append(f'exercice auto {kind} sans candidat dans {ranges}')
        return []
    # répartition régulière, sans doublon de forme
    step = max(1, len(cands) // n)
    picked = []
    forms = set()
    for k in range(0, len(cands), step):
        c = cands[k]
        if c[1] in forms:
            continue
        forms.add(c[1])
        picked.append(c)
        if len(picked) >= n:
            break
    return picked


CORRIGES = defaultdict(list)    # leçon -> [(n°, consigne, [réponses])]


def exercises_html(n, exos):
    out = ['<h3><span class="pastille">✎</span>Exercices</h3>']
    for k, ex in enumerate(exos, 1):
        if 'auto' in ex:
            items = auto_items(ex['auto'], ex['refs'], ex.get('n', 8))
            cons = ex.get('consigne') or {
                'cas': 'Donne le cas de chaque mot.',
                'defini': 'Chaque nom est-il défini ou indéfini ? Dis pourquoi.',
                'genre_nombre': 'Donne le genre et le nombre de chaque nom.',
                'racine': 'Donne la racine de chaque mot.',
                'verbe': 'Donne le temps et la personne de chaque verbe.',
                'forme': 'Donne la forme verbale (I à X) de chaque mot.',
                'mode': "Donne le mode de chaque verbe à l'inaccompli et, s'il y a lieu, la particule qui le commande.",
                'pron': 'Analyse le pronom suffixe : personne et fonction.',
                'prep': 'Repère la préposition et le cas du nom qui la suit.',
            }[ex['auto']]
            lis = ''.join(f'<li><span class="qin">{E(t)}</span> <span class="gris petit">({loc[0]}:{loc[1]})</span></li>'
                          for loc, t, qa in items)
            out.append(f'<div class="exo"><div class="cons"><span class="n">{k}.</span> {markup(cons)}</div><ol>{lis}</ol></div>')
            CORRIGES[n].append((k, cons, [f'<span class="qin">{E(t)}</span> : {E(qa[1])}' for loc, t, qa in items]))
        else:
            cls = ' class="une"' if ex.get('une') else ''
            lis = ''.join(f'<li>{markup(qq)}</li>' for qq, aa in ex['items'])
            out.append(f'<div class="exo"><div class="cons"><span class="n">{k}.</span> {markup(ex["consigne"])}</div><ol{cls}>{lis}</ol></div>')
            CORRIGES[n].append((k, ex['consigne'], [markup(aa) for qq, aa in ex['items']]))
    return ''.join(out)


# ------------------------------------------------------- révision express
def revx_html(n):
    srcs = [n - d for d in (1, 2, 4, 8, 16, 32) if n - d >= 1]
    qs = []
    for s in srcs:
        cards = lecons.L.get(s, {}).get('flash', [])
        if not cards:
            continue
        k = (n * 7 + s) % len(cards)
        qs.append((s, cards[k]))
    if not qs:
        return ''
    lis = ''.join(f'<li>{markup(c[0])} <span class="gris petit">(L{s})</span></li>' for s, c in qs)
    reps = ' — '.join(f'{i}. {markup(c[1])}' for i, (s, c) in enumerate(qs, 1))
    return (f'<div class="revx"><span class="lab">Révision express — avant de commencer</span>'
            f'<ol>{lis}</ol><div class="rep"><b>Réponses :</b> {reps}</div></div>')


# --------------------------------------------------------------- fiches
FICHES = {}


def fiche_html(n, f, title):
    body = markup(f['corps'])
    foot = f.get('pied', '')
    h = (f'<div class="fiche" id="F{n}"><div class="fh"><span class="fn">Fiche {n} · {E(f.get("titre", title))}</span>'
         f'<span class="fa">{f.get("ar", "")}</span></div><div class="fb">{body}</div>'
         + (f'<div class="ff">{markup(foot)}</div>' if foot else '') + '</div>')
    FICHES[n] = h
    return h


# ------------------------------------------------------------------ leçon
def lesson_html(n, part, title, title_ar, texts):
    L = lecons.L.get(n)
    if not L:
        PROBLEMS.append(f'leçon {n} absente')
        return ''
    refs = expand(texts)
    # notions introduites
    for nid, (les, lab) in NOTIONS.items():
        if les == n:
            PLAN.intro(('n', nid), n)
    voc = pick_vocab(n, refs)
    taught = [l for l, k in VOCAB_INTRO.items() if k <= n]
    cov = coverage(taught)
    KNOWN_UNTIL[n] = set(taught)
    h = [f'<section class="lecon partie-{part}" id="L{n}">']
    h.append(f'<div class="tete"><div><div class="num">Leçon {n}</div><h2>{E(title)}</h2></div>'
             f'<div class="ar-titre">{title_ar}</div></div>')
    if L.get('objectifs'):
        h.append('<div class="objectifs"><span class="lab">Objectifs</span><ul>'
                 + ''.join(f'<li>{markup(o)}</li>' for o in L['objectifs']) + '</ul></div>')
    h.append(revx_html(n))
    h.append(f'<div class="expose">{markup(L["expose"])}</div>')
    h.append(fiche_html(n, L['fiche'], title))
    # vocabulaire
    rows = []
    for lem in voc:
        e = LEX[lem]
        root = ' '.join(e['root']) if e['root'] else ''
        rows.append(f'<tr><td class="a">{vocab_display(lem)}</td><td>{E(e["gloss"])}</td>'
                    f'<td class="r">{E(root)}</td><td class="f">×{q.lem_count[lem]}</td></tr>')
    h.append('<h3><span class="pastille">✦</span>Vocabulaire</h3>'
             f'<table class="voc">{"".join(rows)}</table>'
             f'<div class="couv">Avec le vocabulaire des leçons 1 à {n}, tu reconnais le mot principal de '
             f'<b>{cov:.0f} %</b> des mots du Coran (×N : nombre d\'occurrences dans le Coran ; ج : pluriel).</div>')
    h.append(exercises_html(n, L.get('exercices', [])))
    # texte
    for k, rg in enumerate(texts):
        lab = 'Texte de lecture' + (f' {k + 1}' if len(texts) > 1 else '')
        h.append(f'<div class="texte-titre"><span class="lab">{lab}</span><span class="ref">{E(ranges_label([rg]))}</span></div>')
        if k == 0:
            h.append('<div class="mode-emploi">Lis d\'abord le verset à voix haute, puis cache la colonne du sens. '
                     'Repères : <span class="m new">★ nouveau</span> notion ou mot de cette leçon · '
                     '<span class="m rev">↺n révision</span> notion vue en leçon n, rappelée au bon moment · '
                     '<span class="m voc">↺n vocabulaire</span> mot appris en leçon n · '
                     '<span class="m ant">→n</span> notion étudiée plus loin. Les lignes grisées ne contiennent que du déjà-acquis.</div>')
        h.append(guided_text(n, f'L{n}', [rg], L.get('notes'), current_lesson=n))
    h.append('</section>')
    return ''.join(h)


def reading_html(k, title, title_ar, ranges, step):
    R = getattr(lecons, 'R', {}).get(k, {})
    h = [f'<section class="lecon partie-V" id="T{k}">']
    h.append(f'<div class="tete"><div><div class="num">Lecture {k}</div><h2>{E(title)}</h2></div>'
             f'<div class="ar-titre">{title_ar}</div></div>')
    h.append(f'<div class="objectifs"><span class="lab">Passage</span><ul><li>{E(ranges_label(ranges))}</li></ul></div>')
    if R.get('intro'):
        h.append(f'<div class="expose">{markup(R["intro"])}</div>')
    h.append(guided_text(step, f'T{k}', ranges, R.get('notes'), current_lesson=40))
    if R.get('questions'):
        lis = ''.join(f'<li>{markup(qq)}</li>' for qq, aa in R['questions'])
        h.append(f'<h3><span class="pastille">?</span>Questions sur le texte</h3><div class="exo"><ol class="une">{lis}</ol></div>')
        CORRIGES[f'T{k}'].append((1, 'Questions sur le texte', [markup(aa) for qq, aa in R['questions']]))
    h.append('</section>')
    return ''.join(h)


# --------------------------------------------------------------- annexes
def lexique_html():
    by_root = defaultdict(list)
    for lem, n in VOCAB_INTRO.items():
        e = LEX[lem]
        by_root[e['root'] or '—'].append((lem, n))
    out = ['<div class="lexique">']
    for root in sorted(by_root, key=lambda r: bare(r)):
        items = sorted(by_root[root], key=lambda x: -q.lem_count[x[0]])
        out.append(f'<div class="rac"><div class="rh">{E(" ".join(root))}</div>')
        for lem, n in items:
            out.append(f'<div class="le"><span class="a">{vocab_display(lem)}</span><span>{E(LEX[lem]["gloss"])}</span>'
                       f'<span class="f">L{n} · ×{q.lem_count[lem]}</span></div>')
        out.append('</div>')
    out.append('</div>')
    return ''.join(out)


def index_notions_html():
    out = ['<div class="index-n">']
    for nid, (les, lab) in sorted(NOTIONS.items(), key=lambda x: (x[1][0], x[1][1])):
        places = []
        for p, st in NOTION_HISTORY[nid]:
            if p not in places:
                places.append(p)
        after = [p for p in places if (p.startswith('T') or int(p[1:]) > les)]
        out.append(f'<div><b>{E(lab)}</b> — étudié en <a href="#L{les}">L{les}</a> (fiche {les}) ; '
                   f'rencontré ensuite dans {len(after)} textes'
                   + (f' : {", ".join(after[:14])}{" …" if len(after) > 14 else ""}' if after else '') + '.</div>')
    out.append('</div>')
    return ''.join(out)


def index_passages_html():
    by_s = defaultdict(set)
    for (s, a), ctx in USED_REFS.items():
        by_s[s].add(a)
    out = ['<div class="index-n">']
    for s in sorted(by_s):
        vs = sorted(by_s[s])
        # compacter en plages
        rg = []
        for v in vs:
            if rg and v == rg[-1][1] + 1:
                rg[-1][1] = v
            else:
                rg.append([v, v])
        txt = ', '.join(f'{a}' if a == b else f'{a}–{b}' for a, b in rg)
        out.append(f'<div><b>{E(q.sura_fr[s])}</b> <span class="ar">{E(q.sura_name[s])}</span> ({s}) : {txt}</div>')
    out.append('</div>')
    return ''.join(out)


def corriges_html():
    out = ['<div class="corriges">']
    keys = [n for n, *_ in LESSONS] + [f'T{k}' for k, *_ in READINGS]
    for key in keys:
        if key not in CORRIGES:
            continue
        lab = f'Leçon {key}' if isinstance(key, int) else f'Lecture {key[1:]}'
        out.append(f'<h4>{lab}</h4>')
        for num, cons, ans in CORRIGES[key]:
            out.append(f'<div class="ce"><span class="cn">{num}.</span> <ol>'
                       + ''.join(f'<li>{a}</li>' for a in ans) + '</ol></div>')
    out.append('</div>')
    return ''.join(out)


# ------------------------------------------------------------------ toc
def toc_html(pages):
    def pg(anchor):
        return str(pages.get(anchor, '')) if pages else ''
    rows = []
    rows.append(f'<tr class="part"><td colspan="3">Avant de commencer</td><td class="p">{pg("intro")}</td></tr>')
    for p, pt, pa in PARTS:
        rows.append(f'<tr class="part"><td colspan="2">{p} · {E(pt)}</td><td class="a">{pa}</td><td class="p">{pg("P" + p)}</td></tr>')
        if p != 'V':
            for n, part, t, ta, _ in LESSONS:
                if part == p:
                    rows.append(f'<tr><td class="n">L{n}</td><td class="t"><a href="#L{n}">{E(t)}</a></td>'
                                f'<td class="a">{ta}</td><td class="p">{pg(f"L{n}")}</td></tr>')
        else:
            for k, t, ta, rg in READINGS:
                rows.append(f'<tr><td class="n">T{k}</td><td class="t"><a href="#T{k}">{E(t)}</a></td>'
                            f'<td class="a">{ta}</td><td class="p">{pg(f"T{k}")}</td></tr>')
    rows.append('<tr class="part"><td colspan="4">Annexes</td></tr>')
    for aid, at in ANNEX_TITLES:
        rows.append(f'<tr><td class="n"></td><td class="t"><a href="#{aid}">{E(at)}</a></td><td></td><td class="p">{pg(aid)}</td></tr>')
    return f'<section class="sommaire" id="sommaire"><h2>Sommaire</h2><table class="toc">{"".join(rows)}</table></section>'


ANNEX_TITLES = [
    ('A', 'A. Aide-mémoire'),
    ('B', 'B. Recueil des fiches'),
    ('C', 'C. Corrigés'),
    ('D', 'D. Lexique par racine'),
    ('E', 'E. Index des notions et de leur révision'),
    ('F', 'F. Index des passages cités'),
]


# ----------------------------------------------------------------- livre
def build(pages=None, only=None):
    body = []
    body.append(annexes.COUVERTURE)
    body.append(annexes.PAGE_TITRE)
    body.append('@@TOC@@')
    body.append(f'<section class="intro saut" id="intro">{markup(annexes.INTRO)}</section>')
    step = 0
    for p, pt, pa in PARTS:
        cls = f'partie-{p}'
        res = annexes.PARTIES.get(p, '')
        if p != 'V':
            lst = ''.join(f'<li>{E(t)}</li>' for n, part, t, ta, _ in LESSONS if part == p)
        else:
            lst = ''.join(f'<li>{E(t)}</li>' for k, t, ta, rg in READINGS)
        body.append(f'<section class="page-partie {cls}" id="P{p}"><div class="rom">Partie {p}</div><h1>{E(pt)}</h1>'
                    f'<div class="ar-grand">{pa}</div><div class="resume">{markup(res)}</div><ol>{lst}</ol></section>')
        if p != 'V':
            for n, part, t, ta, texts in LESSONS:
                if part != p:
                    continue
                if only and n not in only:
                    # garder la cohérence de la révision : on calcule mais on n'affiche pas
                    lesson_html(n, part, t, ta, texts)
                    continue
                body.append(lesson_html(n, part, t, ta, texts))
        else:
            for k, t, ta, rg in READINGS:
                st = 40 + k
                hh = reading_html(k, t, ta, rg, st)
                if not only or ('T' in only or k in only.get('T', ())) if isinstance(only, dict) else not only:
                    body.append(hh)
    # annexes
    body.append(f'<section class="annexe annexes" id="A"><div class="tete"><h2>A. Aide-mémoire</h2><div class="ar-titre">مُذَكِّرَةٌ</div></div>{markup(annexes.AIDE_MEMOIRE)}</section>')
    body.append('<section class="annexe annexes fiches-recap" id="B"><div class="tete"><h2>B. Recueil des fiches</h2><div class="ar-titre">بِطَاقَاتُ الْقَوَاعِدِ</div></div>'
                + ''.join(FICHES[n] for n in sorted(FICHES)) + '</section>')
    body.append(f'<section class="annexe annexes" id="C"><div class="tete"><h2>C. Corrigés</h2><div class="ar-titre">الْأَجْوِبَةُ</div></div>{corriges_html()}</section>')
    body.append(f'<section class="annexe annexes" id="D"><div class="tete"><h2>D. Lexique par racine</h2><div class="ar-titre">الْمُعْجَمُ</div></div>'
                f'<p class="petit">Les {len(VOCAB_INTRO)} mots des listes de vocabulaire, classés par racine. Lx : leçon où le mot est appris ; ×N : occurrences dans le Coran.</p>{lexique_html()}</section>')
    body.append(f'<section class="annexe annexes" id="E"><div class="tete"><h2>E. Index des notions</h2><div class="ar-titre">فِهْرِسُ الْمَسَائِلِ</div></div>'
                f'<p class="petit">Pour chaque notion : la leçon où elle est étudiée, puis les textes où la lecture l\'a fait réviser (L = leçon, T = lecture suivie).</p>{index_notions_html()}</section>')
    body.append(f'<section class="annexe annexes" id="F"><div class="tete"><h2>F. Index des passages</h2><div class="ar-titre">فِهْرِسُ الْآيَاتِ</div></div>{index_passages_html()}</section>')
    doc = ''.join(body).replace('@@TOC@@', toc_html(pages))
    css = open(os.path.join(HERE, 'style.css'), encoding='utf8').read()
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Lisān al-Qurʾān</title>'
            f'<style>{css}</style></head><body>{doc}</body></html>')


if __name__ == '__main__':
    pages = None
    if '--pages' in sys.argv:
        pages = json.load(open(sys.argv[sys.argv.index('--pages') + 1]))
    only = None
    out = build(pages, only)
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    path = os.path.join(ROOT, 'src', 'livre.html')
    open(path, 'w', encoding='utf8').write(out)
    for w in WARN:
        print('ATTENTION', w)
    if PROBLEMS:
        for p in PROBLEMS:
            print('ERREUR', p)
        sys.exit(1)
    print('ok', path, len(out) // 1024, 'Ko ;', len(VOCAB_INTRO), 'mots de vocabulaire')
