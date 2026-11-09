"""Analyse d'un mot : description française, sens composé, notions repérées."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'content'))

from corpus import Q  # noqa: E402
import gloses  # noqa: E402
from corrections import CORR  # noqa: E402

# ---------------------------------------------------------------- lexique
_LEX = None


def lexicon():
    """lemme -> dict(id, gloss, disp)"""
    global _LEX
    if _LEX is None:
        g = gloses.load()
        _LEX = {}
        path = os.path.join(HERE, '..', 'content', 'lemmes_index.tsv')
        for line in open(path, encoding='utf8'):
            n, lem, pos, root, tags, cnt, ex, ref = line.rstrip('\n').split('\t')
            n = int(n)
            if n not in g:
                raise SystemExit(f'Glose manquante pour le lemme n° {n} ({lem})')
            gl, disp = g[n]
            _LEX[lem] = dict(id=n, gloss=gl, disp=disp or lem, root=root, pos=pos)
        missing = set(g) - set(x['id'] for x in _LEX.values())
        if missing:
            raise SystemExit(f'Gloses sans lemme : {sorted(missing)[:10]}')
    return _LEX


# --------------------------------------------------------- étiquettes FR
PERS = {
    '1S': '1re sg.', '1P': '1re pl.',
    '2MS': '2e m. sg.', '2FS': '2e f. sg.', '2D': '2e duel', '2MD': '2e m. duel', '2FD': '2e f. duel',
    '2MP': '2e m. pl.', '2FP': '2e f. pl.',
    '3MS': '3e m. sg.', '3FS': '3e f. sg.', '3D': '3e duel', '3MD': '3e m. duel', '3FD': '3e f. duel',
    '3MP': '3e m. pl.', '3FP': '3e f. pl.',
}
POSS = {'1S': 'mon', '1P': 'notre', '2MS': 'ton', '2FS': 'ton (f.)', '2D': 'votre (à deux)',
        '2MD': 'votre (à deux)', '2MP': 'votre', '2FP': 'votre (f.)', '3MS': 'son (à lui)',
        '3FS': 'son (à elle)', '3D': 'leur (à deux)', '3MD': 'leur (à deux)', '3FD': 'leur (à deux)',
        '3MP': 'leur', '3FP': 'leur (f.)'}
OBJ = {'1S': 'me', '1P': 'nous', '2MS': 'te', '2FS': 'te (f.)', '2D': 'vous deux', '2MD': 'vous deux',
       '2MP': 'vous', '2FP': 'vous (f.)', '3MS': 'le, lui', '3FS': 'la, lui (f.)', '3D': 'les deux',
       '3MD': 'les deux', '3FD': 'les deux', '3MP': 'les, leur', '3FP': 'les (f.)'}
TONIC = {'1S': 'moi', '1P': 'nous', '2MS': 'toi', '2FS': 'toi (f.)', '2D': 'vous deux', '2MD': 'vous deux',
         '2MP': 'vous', '2FP': 'vous (f.)', '3MS': 'lui', '3FS': 'elle', '3D': 'eux deux',
         '3MD': 'eux deux', '3FD': 'elles deux', '3MP': 'eux', '3FP': 'elles'}
CASE = {'NOM': 'nominatif', 'ACC': 'accusatif', 'GEN': 'génitif'}
CASE_AR = {'NOM': 'marfūʿ', 'ACC': 'manṣūb', 'GEN': 'majrūr'}
MOOD = {'IND': 'indicatif', 'SUBJ': 'subjonctif', 'JUS': 'apocopé'}
ISOL = {'1S': 'je, moi', '1P': 'nous', '2MS': 'tu, toi', '2FS': 'tu, toi (f.)', '2D': 'vous deux', '2MD': 'vous deux',
        '2MP': 'vous', '2FP': 'vous (f.)', '3MS': 'il, lui', '3FS': 'elle', '3D': 'eux deux', '3MD': 'eux deux',
        '3FD': 'elles deux', '3MP': 'ils, eux', '3FP': 'elles'}
ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}

# Sens des particules selon leur fonction (le lemme seul est ambigu).
PART = {
    ('و', 'CONJ'): 'et', ('و', 'REM'): 'et (reprise)', ('و', 'CIRC'): 'alors que',
    ('و', 'P'): 'par… ! (serment)', ('و', 'COM'): 'avec', ('و', 'SUP'): 'et',
    ('ف', 'CONJ'): 'et, puis', ('ف', 'REM'): 'alors, or', ('ف', 'RSLT'): 'alors (réponse)',
    ('ف', 'CAUS'): 'afin que', ('ف', 'SUP'): 'alors', ('ف', 'EXL'): 'alors',
    ('ل', 'P'): 'à, pour', ('ل', 'EMPH'): 'certes', ('ل', 'PRP'): 'pour que', ('ل', 'IMPV'): 'que (+ apocopé)',
    ('ل', 'IMP'): 'que (+ apocopé)',
    ('ما', 'NEG'): 'ne… pas', ('ما', 'REL'): 'ce que, ce qui', ('ما', 'INTG'): 'que ? quoi ?',
    ('ما', 'COND'): 'quoi que', ('ما', 'SUP'): '(explétif)', ('ما', 'PREV'): '(mā qui neutralise)',
    ('ما', 'SUB'): 'le fait de (mā maṣdariyya)', ('ما', 'EXH'): 'pourquoi pas ?',
    ('لا', 'NEG'): 'ne… pas, non', ('لا', 'PRO'): 'ne… pas ! (défense)', ('لا', 'SUP'): '(explétif)',
    ('مَن', 'REL'): 'celui qui', ('مَن', 'COND'): 'quiconque', ('مَن', 'INTG'): 'qui ?',
    ('إِن', 'COND'): 'si', ('إِن', 'NEG'): 'ne… (que)', ('إِن', 'SUP'): '(explétif)',
    ('أ', 'INTG'): 'est-ce que ?', ('أ', 'EQ'): '(que… ou…)',
    ('إِذا', 'T'): 'lorsque', ('إِذا', 'SUR'): 'voici que', ('إِذا', 'COND'): 'lorsque, si',
    ('لَمّا', 'NEG'): 'pas encore', ('لَمّا', 'T'): 'lorsque', ('لَمّا', 'EXP'): 'si ce n\'est',
    ('حَتَّى', 'P'): "jusqu'à", ('حَتَّى', 'SUB'): "jusqu'à ce que", ('أَن', 'SUB'): 'que',
    ('أَن', 'EXL'): 'à savoir', ('إِلّا', 'EXP'): 'excepté', ('إِلّا', 'RES'): 'ne… que',
    ('أَم', 'CONJ'): 'ou bien', ('أَم', 'EQ'): 'ou', ('ب', 'P'): 'par, avec', ('ك', 'P'): 'comme',
    ('أَيّ', 'INTG'): 'quel ?', ('أَيّ', 'COND'): 'quel que soit', ('أَيّ', 'REL'): 'lequel',
    ('أَن', 'INT'): 'à savoir', ('حَتَّى', 'INC'): 'si bien que, jusqu\'à ce que', ('إِمّا', 'COND'): 'si jamais',
    ('إِمّا', 'EXL'): 'soit… soit',
    ('ذا', 'DEM'): 'ce, cela', ('إِذ', 'T'): 'lorsque',
}

TAGLABEL = {
    'CONJ': 'conjonction', 'REM': 'particule de reprise', 'CIRC': "wāw d'état (ḥāl)",
    'RSLT': 'fā de réponse', 'CAUS': 'fā de cause', 'NEG': 'négation', 'PRO': 'défense (lā nāhiya)',
    'EMPH': "particule d'insistance", 'PRP': 'lām de but', 'IMPV': "lām d'injonction", 'IMP': "lām d'injonction",
    'INTG': 'interrogatif', 'COND': 'conditionnel', 'FUT': 'particule du futur', 'CERT': 'qad (certitude)',
    'VOC': 'vocatif', 'EXP': "particule d'exception", 'RES': 'restriction', 'SUB': 'subordonnant',
    'ATT': "particule d'attention", 'AVR': 'particule de rejet', 'RET': 'rectification (bal)',
    'AMD': 'correction (lākin)', 'ANS': 'réponse', 'INC': 'particule inceptive', 'EXH': 'incitation', 'SUR': 'surprise',
    'INT': 'an explicatif', 'DIST': 'lām de distance', 'ADDR': "kāf d'adresse",
    'EXL': 'explication / détail', 'EQ': 'égalité', 'SUP': 'explétif', 'PREV': 'mā « inhibiteur »',
    'COM': "wāw d'accompagnement", 'INL': 'lettres isolées', 'DET': 'article',
}


def _correct(word):
    """Applique les corrections manuelles d'étiquetage (content/corrections.py)."""
    c = CORR.get(word.loc)
    return c or {}


def apply_corrections():
    q = Q()
    for loc, c in CORR.items():
        if 'case' in c:
            q.words[loc].stem.case = c['case']
        if 'mood' in c:
            q.words[loc].stem.mood = c['mood']


apply_corrections()


def is_vocative(word):
    """Nom apostrophé : précédé de yā, ou رَبِّ / قَوْمِ dont le yāʾ du possessif est élidé."""
    st = word.stem
    if st.pos != 'N':
        return False
    if any('VOC' in s.tags for s in word.segs):
        return True
    for s in word.suffixes:
        if 'PRON' in s.tags and s.pgn == '1S' and bare(s.form) == '' and st.lem in ('رَبّ', 'قَوْم'):
            return True
    return False


MABNI_DAMMA = ('قَبْل', 'بَعْد', 'حَيْث')


def is_mabni_damma(word):
    st = word.stem
    return st.lem in MABNI_DAMMA and st.form.endswith('\u064f') and not word.suffixes


# --------------------------------------------------------------- helpers
def stem(word):
    return word.stem


def number_of(pgn):
    if not pgn:
        return None
    if pgn.endswith('S'):
        return 'S'
    if pgn.endswith('D') or pgn == 'D':
        return 'D'
    if pgn.endswith('P'):
        return 'P'
    return None


def gender_of(pgn):
    if not pgn:
        return None
    if 'F' in pgn:
        return 'F'
    if 'M' in pgn:
        return 'M'
    return None


AR_DIAC = re.compile('[ً-ٰٟۖ-ۭـ]')


def bare(t):
    return AR_DIAC.sub('', t or '')


def _key(t):
    t = AR_DIAC.sub('', t or '')
    t = re.sub('[\u0621\u0623\u0625\u0622\u0627\u0671\u0624\u0626]', '', t)
    return t.replace('\u0649', '\u064a').replace('\u0629', '')


def ending_kind(seg):
    """Pluriel externe ? (terminaison ajoutée au lemme sans le modifier)"""
    f = seg.form
    k = _key(f)
    lk = _key(seg.lem)
    if re.search('[\u0648\u064a]\u0646\u064e?[\u06d6-\u06ed]*$', f) and k[-2:] in ('ون', 'ين'):
        lk2 = lk[:-1] if lk.endswith('ي') else lk      # défectueux : رَاعٍ → رَاعُونَ
        if lk and (k[:-2].startswith(lk) or (lk2 and k[:-2] == lk2)):
            return 'sm'
    if k.endswith('ت') and re.search('\u062a[\u064c\u064d\u064f\u0650]?[\u06d6-\u06ed]*$', f):
        if k[:-1].startswith(lk) and lk and ('\u0670\u062a' in f or '\u0627\u062a' in f):
            return 'sf'
    return None


def subject_suffix(word):
    """Indice du segment pronom sujet suffixé au verbe (ou None)."""
    segs = word.segs
    for i, s in enumerate(segs):
        if s.pos == 'V':
            if i + 1 < len(segs):
                n = segs[i + 1]
                if 'PRON' in n.tags and n.pgn == s.pgn:
                    b = bare(n.form)
                    if b in ('وا', 'و', 'ون', 'ا', 'ان', 'ن', 'ت', 'تم', 'تما', 'تن', 'نا', 'ي', 'ين', 'تمو', ''):
                        return i + 1
            return None
    return None


def is_idafa_head(words, i):
    """Le mot i est-il le premier terme d'une annexion ?"""
    w = words[i]
    st = w.stem
    if st.pos != 'N' or 'PRON' in st.tags or 'PN' in st.tags or 'REL' in st.tags or 'DEM' in st.tags:
        return False
    if w.has_det() or 'INDEF' in st.tags or 'ADJ' in st.tags and False:
        return False
    if any('PRON' in s.tags for s in w.suffixes) and st.case:
        return 'pron'
    if st.lem in ('أَيّ',):
        return False
    if i + 1 < len(words):
        n = words[i + 1]
        ns = n.stem
        npref = [x for x in n.prefixes if 'DET' not in x.tags]
        if not npref and ns.pos == 'N' and ns.case == 'GEN' and 'ADJ' not in ns.tags and st.case \
                and 'PRON' not in ns.tags and 'REL' not in ns.tags:
            return 'nom'
        if not npref and ns.pos == 'N' and ns.case == 'GEN' and 'PN' in ns.tags and st.case:
            return 'nom'
    return False


def is_naat(words, i):
    """Adjectif s'accordant avec le nom précédent (épithète probable)."""
    w = words[i]
    st = w.stem
    if st.pos != 'N' or 'ADJ' not in st.tags or i == 0:
        return False
    p = words[i - 1]
    ps = p.stem
    if any(x.pos == 'P' and 'DET' not in x.tags for x in w.prefixes):
        return False
    if ps.pos != 'N' or not st.case or ps.case != st.case:
        return False
    d1 = w.has_det()
    d2 = p.has_det() or 'PN' in ps.tags
    i1 = 'INDEF' in st.tags
    i2 = 'INDEF' in ps.tags
    return (d1 and d2) or (i1 and i2)


ELATIFS = set('''أَكْبَر أَكْثَر أَعْلَم أَحْسَن أَشَدّ أَقْرَب أَظْلَم أَعْلَى أَبْقَى أَشْقَى أَتْقَى أَقْوَم
أَحْكَم أَكْرَم أَسْفَل أَنكَر أَقْصا أَعْظَم أَهْدَى أَوْلَى أَدْنَى أَحَقّ أَرْحَم أَحْصَى كُبْرَى حُسْنَى
يُسْرَى عُسْرَى وُثْقَى أَقْسَط أَزْكَى أَطْهَر أَفْضَل أَعَزّ أَضَلّ أَصْدَق'''.split())
NOMBRES = set('''واحِد واحِدَة اثْنَيْن اثْنَتَيْن ثَلاثَة ثَلاث أَرْبَعَة أَرْبَع خَمْسَة خَمْس سِتَّة سِتّ سَبْعَة سَبْع
ثَمانِيَة ثَمانِي تِسْعَة تِسْع عَشَرَة عَشْر عَشَر عِشْرُون ثَلاثُون أَرْبَعُون مِائَة أَلْف ثالِث رابِع خامِس
سادِس ثامِن'''.split())
WEAK = set('وي')
HAMZA = set('أءؤئ')


def root_type(root):
    if not root or len(root) != 3:
        return []
    out = []
    a, b, c = root
    if a in WEAK:
        out.append('assimile')
    if b in WEAK or b == 'ا':
        out.append('concave')
    if c in WEAK or c == 'ا':
        out.append('defectueux')
    if b == c:
        out.append('sourd')
    if a in HAMZA or b in HAMZA or c in HAMZA:
        out.append('hamze')
    return out


# ------------------------------------------------------------- notions
NOTIONS = {
    # id: (leçon, libellé)
    'wasl': (2, "hamzat al-waṣl (ٱ)"),
    'alif_suscrit': (2, 'alif suscrit (ـٰ)'),
    'racine': (3, 'racine et schème'),
    'article': (4, "article al- (défini)"),
    'solaire': (4, 'lettre solaire après al-'),
    'tanwin': (4, 'tanwīn (indéfini)'),
    'feminin': (5, 'nom féminin'),
    'duel': (6, 'duel'),
    'pl_sain_m': (6, 'pluriel externe masculin'),
    'pl_sain_f': (6, 'pluriel externe féminin'),
    'pl_brise': (7, 'pluriel interne'),
    'nominatif': (8, 'nominatif (marfūʿ)'),
    'accusatif': (8, 'accusatif (manṣūb)'),
    'genitif': (8, 'génitif (majrūr)'),
    'cas_externe': (9, 'cas au duel et au pluriel externe'),
    'prep': (10, 'préposition + génitif'),
    'pron_isole': (11, 'pronom isolé'),
    'pron_suff': (12, 'pronom suffixe'),
    'idafa': (13, 'annexion (iḍāfa)'),
    'naat': (14, 'adjectif épithète'),
    'demonstratif': (16, 'démonstratif'),
    'relatif': (17, 'relatif'),
    'interrogatif': (18, 'interrogatif'),
    'vocatif': (18, 'apostrophe (nidāʾ)'),
    'inna': (19, 'inna et ses sœurs'),
    'la_jins': (19, 'lā de négation absolue'),
    'lam_emph': (19, "lām d'insistance"),
    'kana': (20, 'kāna et ses sœurs'),
    'accompli': (21, 'verbe accompli'),
    'inaccompli': (22, 'inaccompli indicatif'),
    'subjonctif': (23, 'subjonctif (manṣūb)'),
    'apocope': (24, 'apocopé (majzūm)'),
    'imperatif': (24, 'impératif'),
    'defense': (24, 'défense (lā + apocopé)'),
    'negation': (25, 'négation'),
    'futur': (25, 'futur (sa-, sawfa)'),
    'qad': (25, 'qad'),
    'passif': (26, 'passif'),
    'forme_2_4': (27, 'forme dérivée II–IV'),
    'forme_5_10': (28, 'forme dérivée V–X'),
    'masdar': (29, 'nom verbal (maṣdar)'),
    'part_actif': (30, 'participe actif'),
    'part_passif': (30, 'participe passif'),
    'assimile': (31, 'verbe assimilé (1re radicale faible)'),
    'concave': (31, 'verbe concave (2e radicale faible)'),
    'defectueux': (32, 'verbe défectueux (3e radicale faible)'),
    'sourd': (32, 'verbe sourd (2e = 3e radicale)'),
    'hamze': (32, 'verbe hamzé'),
    'fail': (33, 'agent (fāʿil) après le verbe'),
    'objet_pron': (34, 'pronom complément du verbe'),
    'zarf': (35, 'complément de temps ou de lieu (ẓarf)'),
    'mutlaq': (35, 'complément absolu (mafʿūl muṭlaq)'),
    'hal': (36, "wāw d'état (ḥāl)"),
    'exception': (37, 'exception (illā)'),
    'restriction': (37, 'restriction (ḥaṣr)'),
    'condition': (38, 'condition'),
    'fa_reponse': (38, 'fā de réponse'),
    'serment': (39, 'serment (wa-, ta-)'),
    'nun_emph': (39, "nūn d'insistance"),
    'elatif': (40, 'élatif (afʿal)'),
    'nombre': (40, 'nombre'),
}

SOLAR = set('تثدذرزسشصضطظلن')


def notions_of(words, i):
    """Liste ordonnée des notions illustrées par le mot i du verset."""
    w = words[i]
    st = w.stem
    c = _correct(w)
    out = []
    add = out.append
    t = w.text
    if t.startswith('ٱ') or 'ٱ' in t[:6]:
        add('wasl')
    if 'ٰ' in t:
        add('alif_suscrit')
    for k, s in enumerate(w.segs):
        if 'DET' in s.tags:
            add('article')
            if k + 1 < len(w.segs):
                nxt = w.segs[k + 1].form
                if nxt and nxt[0] in SOLAR and 'ّ' in nxt[:3]:
                    add('solaire')
    if st.pos == 'N' and 'INDEF' in st.tags:
        add('tanwin')
    # nom (hors pronoms)
    if st.pos == 'N' and not ({'PRON', 'REL', 'DEM', 'INTG', 'COND', 'T', 'LOC'} & st.tags) and 'PN' not in st.tags:
        g, n = gender_of(st.pgn), number_of(st.pgn)
        if g == 'F' and n == 'S':
            add('feminin')
        if n == 'D':
            add('duel')
        if n == 'P' and st.lem not in NOMBRES and st.lem not in ('سِنِين',):
            ek = ending_kind(st)
            if ek == 'sm' and st.pgn in ('MP', 'P'):
                add('pl_sain_m')
            elif ek == 'sf' or (st.pgn == 'FP' and bare(st.form).endswith('ت')):
                add('pl_sain_f')
            else:
                add('pl_brise')
        if is_vocative(w):
            add('vocatif')
        elif st.case and not c.get('nocase') and not is_mabni_damma(w):
            add({'NOM': 'nominatif', 'ACC': 'accusatif', 'GEN': 'genitif'}[st.case])
            if n == 'D' or (n == 'P' and ending_kind(st) == 'sm'):
                add('cas_externe')
        if 'VN' in st.tags:
            add('masdar')
        if 'ACT_PCPL' in st.tags:
            add('part_actif')
        if 'PASS_PCPL' in st.tags:
            add('part_passif')
        if st.vf and st.vf in (2, 3, 4):
            add('forme_2_4')
        if st.vf and st.vf >= 5:
            add('forme_5_10')
        if st.lem in ELATIFS or (st.lem in ('خَيْر', 'شَرّ') and i + 1 < len(words)
                                 and words[i + 1].stem.lem == 'مِن'):
            add('elatif')
        if st.lem in NOMBRES:
            add('nombre')
    # prépositions
    for s in w.segs:
        if s.pos == 'P' and 'P' in s.tags and s.lem not in ('و', 'ت'):
            add('prep')
            break
        if s.pos == 'P' and 'P' in s.tags and s.lem in ('و', 'ت') and 'PREF' in s.tags:
            nxt = [x for x in w.segs if x.pos == 'N']
            if nxt and nxt[0].case == 'GEN':
                add('serment')
                break
    # pronoms
    attached = any(x.pos == 'P' and 'P' in x.tags for x in w.prefixes)
    if 'PRON' in st.tags and 'SUFF' not in st.tags and st.lem != 'إِيّا':
        add('pron_suff' if attached else 'pron_isole')
    if st.lem == 'إِيّا':
        add('objet_pron')
    sj = subject_suffix(w)
    for k, s in enumerate(w.segs):
        if 'PRON' in s.tags and 'SUFF' in s.tags:
            if k == sj:
                continue
            add('pron_suff')
            if any(x.pos == 'V' for x in w.segs[:k]):
                add('objet_pron')
    if st.pos == 'N' and 'PRON' not in st.tags:
        h = is_idafa_head(words, i)
        if h and not c.get('noidafa'):
            add('idafa')
    if is_naat(words, i) and not c.get('nonaat'):
        add('naat')
    for s in w.segs:
        if 'DEM' in s.tags:
            add('demonstratif')
        if 'REL' in s.tags:
            add('relatif')
        if 'INTG' in s.tags:
            add('interrogatif')
        if 'VOC' in s.tags and st.pos == 'N':
            add('vocatif')
        if s.fam == 'إِنّ' and 'NEG' in s.tags:
            add('la_jins')
        elif s.fam == 'إِنّ':
            add('inna')
        if 'EMPH' in s.tags and s.lem == 'ل':
            add('lam_emph')
        if 'EMPH' in s.tags and s.lem == 'ن':
            add('nun_emph')
        if s.fam in ('كَان',) or s.lem in ('لَيْسَ',):
            add('kana')
        if 'NEG' in s.tags and s.lem == 'لا' and i + 1 < len(words) and words[i + 1].stem.pos == 'V' \
                and words[i + 1].stem.mood == 'JUS':
            add('defense')
        elif 'NEG' in s.tags:
            add('negation')
        if 'PRO' in s.tags:
            add('defense')
        if 'FUT' in s.tags:
            add('futur')
        if 'CERT' in s.tags:
            add('qad')
        if 'CIRC' in s.tags:
            add('hal')
        if 'EXP' in s.tags:
            add('exception')
        if 'RES' in s.tags:
            add('restriction')
        if 'COND' in s.tags:
            add('condition')
        if 'RSLT' in s.tags:
            add('fa_reponse')
    # verbes
    for s in w.segs:
        if s.pos != 'V':
            continue
        if 'PERF' in s.tags:
            add('accompli')
        if 'IMPF' in s.tags and s.pgn not in ('3FP', '2FP'):
            if s.mood == 'IND':
                add('inaccompli')
            elif s.mood == 'SUBJ':
                add('subjonctif')
            elif s.mood == 'JUS':
                add('apocope')
        if 'IMPV' in s.tags:
            add('imperatif')
        if 'PASS' in s.tags:
            add('passif')
        if s.vf in (2, 3, 4):
            add('forme_2_4')
        if s.vf and s.vf >= 5:
            add('forme_5_10')
        for rt in root_type(s.root):
            add(rt)
        # agent nominal après le verbe
        if ('PERF' in s.tags or 'IMPF' in s.tags) and 'PASS' not in s.tags and s.fam is None \
                and s.pgn and s.pgn.startswith('3') and subject_suffix(w) is None and i + 1 < len(words):
            n = words[i + 1]
            ns = n.stem
            if ns.pos == 'N' and ns.case == 'NOM' and not n.prefixes and not ({'PRON', 'INTG', 'REL', 'DEM'} & ns.tags):
                add('fail')
        break
    # complément absolu : maṣdar à l'accusatif de même racine qu'un verbe précédent
    if st.pos == 'N' and 'VN' in st.tags and st.case == 'ACC' and not w.suffixes:
        for j in range(max(0, i - 4), i):
            vs = [s for s in words[j].segs if s.pos == 'V']
            if vs and vs[0].root == st.root:
                add('mutlaq')
                break
    if st.pos == 'N' and ({'T', 'LOC'} & st.tags) and st.case == 'ACC' and not w.prefixes:
        add('zarf')
    seen = []
    for x in out + list(c.get('add', [])):
        if x not in seen and x not in c.get('del', []):
            seen.append(x)
    return seen


# ---------------------------------------------------------- description
def seg_gloss(s, word=None):
    lex = lexicon()
    for t in ('NEG', 'REL', 'INTG', 'COND', 'SUP', 'PREV', 'SUB', 'EXH', 'PRO', 'CONJ', 'REM', 'CIRC', 'P',
              'COM', 'RSLT', 'CAUS', 'EXL', 'EMPH', 'PRP', 'IMPV', 'IMP', 'EQ', 'T', 'SUR', 'EXP', 'RES', 'DEM'):
        if t in s.tags and (s.lem, t) in PART:
            return PART[(s.lem, t)]
    if s.lem in lex:
        return lex[s.lem]['gloss']
    if 'DET' in s.tags:
        return 'le, la, les'
    return ''


def pron_gloss(s, host):
    """Sens d'un pronom suffixe selon son support."""
    p = s.pgn
    if host == 'N':
        return POSS.get(p, '')
    if host == 'V':
        return OBJ.get(p, '')
    return TONIC.get(p, '')


def describe(words, i):
    """(sens, analyse) d'un mot."""
    w = words[i]
    c = _correct(w)
    parts_sense = []
    parts_ana = []
    sj = subject_suffix(w)
    host = None
    for k, s in enumerate(w.segs):
        if 'PREF' in s.tags:
            if 'DET' in s.tags:
                continue
            g = seg_gloss(s, w)
            if g:
                parts_sense.append(g)
            lab = None
            for t in ('CONJ', 'REM', 'CIRC', 'RSLT', 'CAUS', 'EMPH', 'PRP', 'IMPV', 'IMP', 'FUT', 'INTG', 'VOC',
                      'EQ', 'SUP', 'EXL'):
                if t in s.tags:
                    lab = TAGLABEL.get(t)
                    break
            if 'P' in s.tags and s.lem in ('و', 'ت'):
                lab = 'wāw de serment' if s.lem == 'و' else 'tāʾ de serment'
            elif 'P' in s.tags:
                lab = 'préposition'
            parts_ana.append(f"{bare(s.form) or s.lem}- : {lab}" if lab else bare(s.form) + '-')
            continue
        if 'SUFF' in s.tags:
            if 'PRON' in s.tags:
                if k == sj:
                    continue
                g = pron_gloss(s, host)
                parts_sense.append(g)
                if bare(s.form) == '':
                    parts_ana.append(f"pron. {PERS.get(s.pgn, s.pgn)} (yāʾ élidé)")
                    continue
                role = {'N': 'complément du nom', 'V': "complément d'objet", 'P': 'après particule'}.get(host, '')
                if host == 'P' and words and w.stem.fam == 'إِنّ':
                    role = 'nom de ' + bare(w.stem.form)
                parts_ana.append(f"-{bare(s.form)} : pron. {PERS.get(s.pgn, s.pgn)}" + (f", {role}" if role else ''))
            elif 'EMPH' in s.tags:
                parts_ana.append("-n : nūn d'insistance")
            elif 'ATT' in s.tags:
                parts_ana.append('-hā : attention')
            continue
        # segment principal
        host = s.pos
        if s.pos == 'V':
            parts_sense.append(seg_gloss(s))
            a = []
            if 'PERF' in s.tags:
                a.append('accompli')
            elif 'IMPF' in s.tags and s.pgn in ('3FP', '2FP'):
                a.append('inaccompli (nūn du féminin pluriel, invariable)')
            elif 'IMPF' in s.tags:
                a.append('inaccompli ' + MOOD.get(s.mood, ''))
            elif 'IMPV' in s.tags:
                a.append('impératif')
            if 'PASS' in s.tags:
                a.append('passif')
            if s.pgn:
                a.append(PERS.get(s.pgn, s.pgn))
            a.append('f. ' + ROMAN.get(s.vf or 1, '?'))
            if s.root:
                a.append('rac. ' + ' '.join(s.root))
            parts_ana.insert(len([x for x in parts_ana]), 'verbe, ' + ', '.join(x for x in a if x))
        elif s.pos == 'N':
            g = seg_gloss(s)
            parts_sense.append(g)
            a = []
            tags = s.tags
            if 'PRON' in tags and any(x.pos == 'P' and 'P' in x.tags for x in w.prefixes):
                a.append('pron. ' + PERS.get(s.pgn, s.pgn or '') + ', après préposition')
                parts_sense[-1] = TONIC.get(s.pgn, '')
            elif 'PRON' in tags:
                a.append('pronom isolé ' + PERS.get(s.pgn, s.pgn or ''))
                parts_sense[-1] = ISOL.get(s.pgn, '')
                if s.lem == 'إِيّا':
                    a = ['pronom complément isolé ' + PERS.get(s.pgn, s.pgn or '')]
                    parts_sense[-1] = TONIC.get(s.pgn, '') + ' (seul)'
            elif 'REL' in tags:
                a.append('relatif')
            elif 'DEM' in tags:
                a.append('démonstratif')
            elif 'INTG' in tags:
                a.append('interrogatif')
            elif 'COND' in tags:
                a.append('nom conditionnel')
            elif 'PN' in tags:
                a.append('nom propre')
            elif 'VN' in tags:
                a.append('maṣdar' + (f' f. {ROMAN[s.vf]}' if s.vf and s.vf > 1 else ''))
            elif 'ACT_PCPL' in tags:
                a.append('part. actif' + (f' f. {ROMAN[s.vf]}' if s.vf and s.vf > 1 else ''))
            elif 'PASS_PCPL' in tags:
                a.append('part. passif' + (f' f. {ROMAN[s.vf]}' if s.vf and s.vf > 1 else ''))
            elif 'ADJ' in tags:
                a.append('adjectif')
            elif {'T', 'LOC'} & tags:
                a.append('nom de temps' if 'T' in tags else 'nom de lieu')
            else:
                a.append('nom')
            nb_ = number_of(s.pgn)
            if nb_ in ('P', 'D') and parts_sense and parts_sense[-1] and 'PRON' not in tags and 'pl.' not in parts_sense[-1] \
                    and not parts_sense[-1].endswith(('s', 'x')) and s.lem not in ('ناس', 'آباء', 'نِساء', 'أَصْحاب', 'آلاء'):
                parts_sense[-1] += ' (pl.)' if nb_ == 'P' else ' (duel)'
            if s.pgn and 'PRON' not in tags:
                g_, n_ = gender_of(s.pgn), number_of(s.pgn)
                gn = {'M': 'm.', 'F': 'f.'}.get(g_, '')
                nn = {'S': 'sg.', 'D': 'duel', 'P': 'pl.'}.get(n_, '')
                if gn or nn:
                    a.append(' '.join(x for x in (gn, nn) if x))
            if w.has_det():
                a.append('défini (al-)')
            elif 'INDEF' in tags:
                a.append('indéfini')
            if is_vocative(w):
                a.append('apostrophé (munādā)')
            elif is_mabni_damma(w):
                a.append('invariable en -u (en position de génitif)' if s.case == 'GEN' else 'invariable en -u')
            elif s.case and not c.get('nocase'):
                a.append(CASE[s.case])
            parts_ana.append(', '.join(a))
        else:  # particule autonome
            g = seg_gloss(s)
            if s.fam == 'إِنّ' and 'NEG' in s.tags:
                g = 'aucun… (négation absolue)'
            nxt = words[i + 1].stem if i + 1 < len(words) else None
            la_def = 'NEG' in s.tags and s.lem == 'لا' and nxt is not None and nxt.pos == 'V' and nxt.mood == 'JUS'
            if la_def:
                g = 'ne… pas ! (défense)'
            if 'INL' in s.tags:
                g = 'lettres isolées (sens connu d\'Allah)'
            parts_sense.append(g)
            lab = None
            if s.fam == 'إِنّ' and 'NEG' in s.tags:
                lab = 'lā de négation absolue'
            elif la_def:
                lab = 'défense (lā nāhiya)'
            elif s.fam == 'إِنّ':
                lab = 'particule de la famille de inna'
            else:
                for t in sorted(s.tags):
                    if t in TAGLABEL:
                        lab = TAGLABEL[t]
                        break
                if 'P' in s.tags:
                    lab = 'préposition'
            parts_ana.append(lab or 'particule')
    sense = ' + '.join(x for x in parts_sense if x)
    if c.get('sense'):
        sense = c['sense']
    ana = ' · '.join(x for x in parts_ana if x)
    if c.get('ana'):
        ana = c['ana']
    return sense, ana
