"""Partie II (2) — leçons 12 à 20."""

L = {}

L[12] = dict(
    objectifs=[
        "connaître les pronoms suffixes",
        "les reconnaître sur un nom, une préposition, un verbe",
        "appliquer l'harmonie vocalique (‑hu / ‑hi)",
    ],
    expose=r"""
<p>Les <b>pronoms suffixes</b> [[ٱلضَّمَائِرُ ٱلْمُتَّصِلَةُ]] se soudent à la fin d'un nom, d'une préposition, d'une particule ou d'un verbe. Ce sont les pronoms les plus fréquents du Coran.</p>
<table class="t c">
<tr><th></th><th colspan="2">singulier</th><th colspan="2">duel</th><th colspan="2">pluriel</th></tr>
<tr><td>3<sup>e</sup> m.</td><td class="ar">ـهُ</td><td>son, le, lui</td><td class="ar" rowspan="2">ـهُمَا</td><td rowspan="2">leur (à deux)</td><td class="ar">ـهُمْ</td><td>leur, les, eux</td></tr>
<tr><td>3<sup>e</sup> f.</td><td class="ar">ـهَا</td><td>son, la, elle</td><td class="ar">ـهُنَّ</td><td>leur, les (f.)</td></tr>
<tr><td>2<sup>e</sup> m.</td><td class="ar">ـكَ</td><td>ton, te, toi</td><td class="ar" rowspan="2">ـكُمَا</td><td rowspan="2">votre (à deux)</td><td class="ar">ـكُمْ</td><td>votre, vous</td></tr>
<tr><td>2<sup>e</sup> f.</td><td class="ar">ـكِ</td><td>ton, te (f.)</td><td class="ar">ـكُنَّ</td><td>votre (f.)</td></tr>
<tr><td>1<sup>re</sup></td><td class="ar">ـِي / ـنِي</td><td>mon, me, moi</td><td colspan="2">—</td><td class="ar">ـنَا</td><td>notre, nous</td></tr>
</table>
<h3><span class="pastille">1</span>Trois emplois</h3>
<ul>
<li>Sur un <b>nom</b> : possessif. Le nom devient défini (c'est une annexion, L13) : [[رَبُّكَ]] « ton Seigneur », [[صَدْرَكَ]] « ta poitrine ». À la 1<sup>re</sup> personne : [[ـِي]] — [[رَبِّي]] « mon Seigneur ».</li>
<li>Sur une <b>préposition</b> ou une particule : [[لَكَ]] « pour toi », [[عَنكَ]] « de toi », [[إِنَّهُ]] « certes il ».</li>
<li>Sur un <b>verbe</b> : complément d'objet. À la 1<sup>re</sup> personne : [[ـنِي]] — [[هَدَانِي]] « il m'a guidé ».</li>
</ul>
{{ex 93:3|hl=ودعك,ربك|com=[[وَدَّعَكَ]] « (il) t'a abandonné » : <i>-ka</i> objet du verbe ; [[رَبُّكَ]] « ton Seigneur » : <i>-ka</i> possessif.}}
{{ex 94:1|hl=لك,صدرك|com=« N'avons-Nous pas ouvert <b>pour toi</b> <b>ta</b> poitrine ? »}}
<h3><span class="pastille">2</span>Hu ou hi ?</h3>
<p>Après <b>i</b>, <b>ī</b> ou <b>ay</b>, le [[ه]] des pronoms de 3<sup>e</sup> personne prend une kasra : [[بِهِ]] <i>bihi</i>, [[فِيهِ]] <i>fīhi</i>, [[عَلَيْهِمْ]] <i>ʿalayhim</i>, [[رَبِّهِ]] <i>rabbihi</i> (au génitif). Ailleurs : [[لَهُ]], [[رَبُّهُ]], [[مِنْهُمْ]].</p>
<p>Après une voyelle brève, le muṣḥaf allonge <i>hu/hi</i> avec un petit wāw ou yāʾ : [[لَهُۥ]] <i>lahū</i>, [[بِهِۦ]] <i>bihī</i> ; pas après une voyelle longue ou un sukūn : [[فِيهِ]] <i>fīhi</i>, [[مِنْهُ]] <i>minhu</i>.</p>
<h3><span class="pastille">3</span>Petites adaptations</h3>
<ul>
<li>Devant une hamzat al-waṣl, [[ـكُمْ]] et [[ـهُمْ]] prennent une ḍamma : [[عَلَيْكُمُ ٱلصِّيَامُ]] <i>ʿalaykumu ṣ-ṣiyām</i>.</li>
<li>Un verbe en [[ـتُمْ]] devient [[ـتُمُو]] devant un pronom objet : [[فَكَرِهْتُمُوهُ]] « vous l'avez eu en horreur » (49:12).</li>
<li>Le pronom sujet du verbe ([[ـتُ]], [[ـنَا]], [[ـُوا]]…) fait partie de la conjugaison (L21) : ne pas le confondre avec le pronom objet.</li>
</ul>
{{ex 93:6|hl=يجدك|com=[[يَجِدْكَ]] « (Il) t'a trouvé » : <i>-ka</i> objet ; [[فَـَٔاوَىٰ]] « et Il a donné refuge ».}}
""",
    fiche=dict(
        titre='Les pronoms suffixes', ar='الضَّمَائِرُ الْمُتَّصِلَةُ',
        corps=r"""
<table class="t c">
<tr><th></th><th>sg.</th><th>duel</th><th>pl.</th></tr>
<tr><td>3 m.</td><td class="ar">ـهُ</td><td class="ar">ـهُمَا</td><td class="ar">ـهُمْ</td></tr>
<tr><td>3 f.</td><td class="ar">ـهَا</td><td class="ar">ـهُمَا</td><td class="ar">ـهُنَّ</td></tr>
<tr><td>2 m.</td><td class="ar">ـكَ</td><td class="ar">ـكُمَا</td><td class="ar">ـكُمْ</td></tr>
<tr><td>2 f.</td><td class="ar">ـكِ</td><td class="ar">ـكُمَا</td><td class="ar">ـكُنَّ</td></tr>
<tr><td>1</td><td class="ar">ـِي (nom) / ـنِي (verbe)</td><td>—</td><td class="ar">ـنَا</td></tr>
</table>
<ul>
<li>Sur un nom : possessif (le nom devient défini). Sur un verbe : objet. Sur une préposition : complément.</li>
<li>Après i, ī, ay : <i>hi</i>, <i>him</i> ([[فِيهِ]], [[عَلَيْهِمْ]]).</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Ajoute le pronom demandé.", items=[
            ('[[رَبّ]] + notre', '[[رَبُّنَا]]'), ('[[كِتَاب]] + mon', '[[كِتَابِي]]'), ('[[قَلْب]] + son (à lui)', '[[قَلْبُهُ]]'),
            ('[[عَلَى]] + lui', '[[عَلَيْهِ]]'), ('[[هَدَى]] + nous', '[[هَدَانَا]]'), ('[[خَلَقَ]] + vous', '[[خَلَقَكُمْ]]'),
            ('[[فِي]] + elle', '[[فِيهَا]]'), ('[[نَصَرَ]] + me', '[[نَصَرَنِي]]'),
        ]),
        dict(auto='pron', refs=[(20, 25, 35)], n=10),
    ],
    flash=[
        ("Pronom suffixe « votre » (pl.) ?", "[[ـكُمْ]]"),
        ("[[ـنِي]] ou [[ـِي]] sur un verbe ?", "[[ـنِي]] : [[هَدَانِي]]"),
        ("Pourquoi [[عَلَيْهِمْ]] et non [[عَلَيْهُمْ]] ?", "après <i>ay</i>, le h prend une kasra"),
        ("Fonction de <i>-ka</i> dans [[وَدَّعَكَ]] ?", "complément d'objet"),
        ("[[رَبُّهُمْ]] signifie… ?", "leur Seigneur"),
    ],
    notes={
        (93, 1): "[[وَٱلضُّحَىٰ]] : serment (L39) ; [[ٱلضُّحَىٰ]] se termine par un alif maqṣūra : cas invisible.",
        (93, 5): "[[وَلَسَوْفَ يُعْطِيكَ]] : <i>la-</i> d'insistance + <i>sawfa</i> (futur) : « assurément, Il te donnera ».",
        (94, 5): "[[فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا]] : le nom de <i>inna</i> ([[يُسْرًا]]) vient après le groupe [[مَعَ ٱلْعُسْرِ]] (L19).",
        (94, 7): "[[فَإِذَا فَرَغْتَ فَٱنصَبْ]] « quand tu as fini, applique-toi » : condition avec <i>idhā</i> (L38).",
    },
)

L[13] = dict(
    objectifs=[
        "construire et analyser une annexion (iḍāfa)",
        "savoir pourquoi le premier terme n'a ni article ni tanwīn",
        "reconnaître les annexions en chaîne et avec pronom",
    ],
    expose=r"""
<p>Pour dire « le Seigneur <b>des</b> mondes », « les compagnons <b>de</b> l'éléphant », l'arabe juxtapose deux noms : c'est l'<b>annexion</b> [[إِضَافَة]]. Le premier nom est l'<b>annexé</b> [[مُضَاف]], le second le <b>complément</b> [[مُضَافٌ إِلَيْهِ]].</p>
<div class="encadre"><span class="lab">Les deux règles</span>1. Le <b>premier terme</b> n'a <b>ni article ni tanwīn</b> ; son cas dépend de sa fonction dans la phrase.<br>2. Le <b>second terme</b> est toujours au <b>génitif</b>. S'il est défini, toute l'annexion est définie.</div>
{{ex 1:2|hl=رب,العالمين|com=[[رَبِّ]] (annexé, génitif car il qualifie [[لِلَّهِ]]) + [[ٱلْعَٰلَمِينَ]] (complément, génitif).}}
{{ex 105:1|hl=بأصحاب,الفيل|com=[[بِأَصْحَٰبِ ٱلْفِيلِ]] « avec les compagnons de l'éléphant ».}}
{{ex 106:2|hl=رحلة,الشتاء|com=[[رِحْلَةَ ٱلشِّتَآءِ]] « le voyage de l'hiver » : annexé à l'accusatif.}}
<h3><span class="pastille">1</span>Annexions en chaîne</h3>
<p>Le complément peut être lui-même annexé : [[مَٰلِكِ يَوْمِ ٱلدِّينِ]] « le Maître du Jour de la Rétribution » ; seul le dernier terme peut avoir l'article. [[رَبَّ هَٰذَا ٱلْبَيْتِ]] « le Seigneur de cette Maison » (106:3).</p>
<h3><span class="pastille">2</span>Annexion à un pronom</h3>
<p>Un nom suivi d'un pronom suffixe est une annexion : [[كَيْدَهُمْ]] « leur ruse » (105:2), [[رَبُّكَ]] « ton Seigneur ». Le nom est défini par le pronom.</p>
<h3><span class="pastille">3</span>Duel et pluriel : le nūn tombe</h3>
<p>Au premier terme, le duel et le pluriel masculin externe <b>perdent leur nūn</b> : [[يَدَانِ]] → [[يَدَا أَبِى لَهَبٍ]] « les deux mains d'Abū Lahab » (111:1) ; [[بَنُونَ]] → [[بَنُو إِسْرَائِيلَ]] / [[بَنِىٓ إِسْرَٰٓءِيلَ]] « les fils d'Isrāʾīl ».</p>
<h3><span class="pastille">4</span>Mots toujours annexés</h3>
<p>Certains noms se construisent presque toujours en annexion : [[كُلّ]] chaque, tout ([[كُلُّ نَفْسٍ]] « toute âme ») ; [[بَعْض]] une partie ; [[غَيْر]] autre que, non ([[غَيْرِ ٱلْمَغْضُوبِ]]) ; [[مِثْل]] semblable ; [[ذُو]] possesseur de ; les noms de lieu et de temps [[عِنْدَ]], [[بَيْنَ]], [[قَبْلَ]], [[بَعْدَ]], [[يَوْمَ]].</p>
<div class="attention"><span class="lab">Adjectif et annexion</span>On ne peut rien intercaler entre les deux termes. Un adjectif qui qualifie le premier terme se place <b>après tout le groupe</b> : [[بِرَبِّكَ ٱلْكَرِيمِ]] « ton Seigneur, le Généreux » (82:6) — voir L14.</div>
""",
    fiche=dict(
        titre="L'annexion", ar='الْإِضَافَةُ',
        corps=r"""
<ul>
<li><b>Annexé</b> (muḍāf) : ni article ni tanwīn ; cas selon sa fonction.</li>
<li><b>Complément</b> (muḍāf ilayh) : toujours au génitif ; s'il est défini, le groupe est défini.</li>
<li>Chaîne : [[مَٰلِكِ يَوْمِ ٱلدِّينِ]] ; avec pronom : [[رَبُّكَ]].</li>
<li>Duel et pluriel externe annexés perdent le nūn : [[يَدَا]], [[بَنُو]] / [[بَنِي]].</li>
<li>Rien entre les deux termes ; l'adjectif du premier terme vient après le groupe.</li>
</ul>
<table class="t"><tr><th>français</th><th class="ar">arabe</th></tr>
<tr><td>le Livre d'Allah</td><td class="ar">كِتَابُ ٱللَّهِ</td></tr>
<tr><td>un livre d'Allah (indéfini)</td><td class="ar">كِتَابُ رَبٍّ (rare)</td></tr></table>""",
    ),
    exercices=[
        dict(consigne="Traduis.", items=[
            ('[[رَبُّ ٱلنَّاسِ]]', 'le Seigneur des hommes'), ('[[كِتَابُ ٱللَّهِ]]', "le Livre d'Allah"),
            ('[[يَوْمُ ٱلْقِيَامَةِ]]', 'le Jour de la Résurrection'), ('[[أَهْلُ ٱلْكِتَابِ]]', 'les gens du Livre'),
            ('[[أَصْحَابُ ٱلْجَنَّةِ]]', 'les compagnons du Paradis'), ('[[نِعْمَةُ رَبِّكَ]]', 'le bienfait de ton Seigneur'),
        ]),
        dict(consigne="Forme l'annexion.", items=[
            ("le messager d'Allah", '[[رَسُولُ ٱللَّهِ]]'), ('la voie de ton Seigneur', '[[سَبِيلُ رَبِّكَ]]'),
            ("les deux mains d'Abū Lahab", '[[يَدَا أَبِي لَهَبٍ]]'), ('les fils de Ādam', '[[بَنُو آدَمَ]]'),
        ]),
        dict(auto='defini', refs=[(111, 1, 5)], n=8),
    ],
    flash=[
        ("Le premier terme d'une annexion porte-t-il l'article ?", "non, ni article ni tanwīn"),
        ("Cas du complément du nom ?", "génitif"),
        ("Que devient [[يَدَانِ]] en annexion ?", "[[يَدَا]] (le nūn tombe)"),
        ("Où se place l'adjectif du premier terme ?", "après tout le groupe : [[بِرَبِّكَ ٱلْكَرِيمِ]]"),
        ("[[رِحْلَةَ ٱلشِّتَآءِ]] : traduire.", "le voyage de l'hiver"),
    ],
    notes={
        (105, 1): "[[أَلَمْ تَرَ]] « n'as-tu pas vu ? » : <i>lam</i> + apocopé de [[رَأَى]] (L24, L32).",
        (105, 5): "[[كَعَصْفٍ مَّأْكُولٍۭ]] « comme de la paille mâchée » : [[كَ]] + génitif, puis adjectif (L14).",
        (106, 1): "[[لِإِيلَٰفِ قُرَيْشٍ]] : annexion ; [[إِيلَٰف]] est un nom verbal (forme IV, L29).",
        (106, 4): "[[ٱلَّذِىٓ أَطْعَمَهُم مِّن جُوعٍ]] « qui les a nourris contre la faim » : relatif (L17).",
    },
)

L[14] = dict(
    objectifs=[
        "accorder l'adjectif en cas, définition, genre et nombre",
        "appliquer l'accord au féminin singulier pour les pluriels de choses",
        "distinguer groupe nominal et phrase",
    ],
    expose=r"""
<p>L'adjectif épithète, ou <b>naʿt</b> [[نَعْت]], se place <b>après</b> le nom qu'il qualifie et s'accorde avec lui en <b>quatre points</b> : le cas, la définition, le genre et le nombre.</p>
{{ex 1:6|hl=الصراط,المستقيم|com=[[ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ]] : accusatif, défini, masculin, singulier — pour les deux mots.}}
{{ex 2:7|hl=عذاب,عظيم|from=ولهم|to=عظيم|com=[[عَذَابٌ عَظِيمٌ]] : nominatif, indéfini, masculin, singulier.}}
<p>Si le nom est défini <b>par annexion</b>, l'adjectif prend l'article : [[بِرَبِّكَ ٱلْكَرِيمِ]] « ton Seigneur le Généreux ».</p>
{{ex 82:6|hl=بربك,الكريم}}
<h3><span class="pastille">1</span>Pluriels de choses : féminin singulier</h3>
<p>Avec un pluriel de choses ou d'animaux, l'adjectif est au <b>féminin singulier</b> (L7). La sourate al-Ghāshiya en offre une série :</p>
{{ex 88:13|hl=سرر,مرفوعة}}
{{ex 88:14|hl=وأكواب,موضوعة}}
{{ex 88:16|hl=وزرابي,مبثوثة|com=[[زَرَابِىُّ]] est un diptote (pluriel [[فَعَالِيّ]]) : pas de tanwīn ; l'adjectif, lui, l'a.}}
<p>Pour des êtres humains au pluriel, l'adjectif est au pluriel : [[ٱلْمُؤْمِنُونَ ٱلصَّادِقُونَ]].</p>
<h3><span class="pastille">2</span>Plusieurs adjectifs</h3>
<p>Les adjectifs peuvent se suivre, chacun accordé : [[ٱلْمَلِكُ ٱلْقُدُّوسُ ٱلسَّلَٰمُ]] (59:23).</p>
<h3><span class="pastille">3</span>Groupe ou phrase ?</h3>
<p>Comparer :</p>
<ul>
<li>[[ٱللَّهُ ٱلْعَلِيمُ]] : même définition → <b>groupe</b> « Allah l'Omniscient » ;</li>
<li>[[ٱللَّهُ عَلِيمٌ]] : définitions différentes → <b>phrase</b> « Allah est omniscient » (L15).</li>
</ul>
<p>Ainsi [[ٱلْكِتَابُ ٱلْمُبِينُ]] « le Livre explicite » mais [[ٱلْكِتَابُ مُبِينٌ]] « le Livre est explicite ».</p>
<h3><span class="pastille">4</span>Une phrase en guise d'adjectif</h3>
<p>Après un nom <b>indéfini</b>, une phrase entière peut servir d'adjectif, sans relatif. On la traduit par « qui, où, que » :</p>
{{ex 2:48|hl=يوما,تجزي|from=واتقوا|to=شيئا|com=« craignez un jour <b>où</b> nulle âme ne suffira en rien à une autre ».}}
""",
    fiche=dict(
        titre="L'adjectif épithète", ar='النَّعْتُ',
        corps=r"""
<ul>
<li>Après le nom ; accord en <b>cas, définition, genre, nombre</b>.</li>
<li>Nom défini par annexion → adjectif avec article : [[رَبِّكَ ٱلْكَرِيمِ]].</li>
<li>Pluriel de choses → adjectif <b>féminin singulier</b> : [[سُرُرٌ مَرْفُوعَةٌ]].</li>
<li>Définitions différentes = phrase : [[ٱللَّهُ عَلِيمٌ]] « Allah est omniscient ».</li>
<li>Après un nom indéfini, une phrase peut qualifier : « un jour <b>où</b>… ».</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Accorde l'adjectif entre parenthèses.", items=[
            ('[[جَنَّةٌ]] ([[عَالٍ]])', '[[جَنَّةٌ عَالِيَةٌ]]'), ('[[ٱلْكِتَابُ]] ([[مُبِين]])', '[[ٱلْكِتَابُ ٱلْمُبِينُ]]'),
            ('[[عَذَابًا]] ([[أَلِيم]])', '[[عَذَابًا أَلِيمًا]]'), ('[[ٱلْمُؤْمِنُونَ]] ([[صَادِق]])', '[[ٱلْمُؤْمِنُونَ ٱلصَّادِقُونَ]]'),
            ('[[أَنْهَارٌ]] ([[جَارٍ]])', '[[أَنْهَارٌ جَارِيَةٌ]]'), ('[[بِرَبِّكَ]] ([[كَرِيم]])', '[[بِرَبِّكَ ٱلْكَرِيمِ]]'),
        ]),
        dict(consigne="Groupe nominal ou phrase ? Traduis.", items=[
            ('[[ٱللَّهُ ٱلْغَفُورُ]]', 'groupe : Allah le Pardonneur'), ('[[ٱللَّهُ غَفُورٌ]]', 'phrase : Allah est pardonneur'),
            ('[[ٱلرَّسُولُ ٱلْأَمِينُ]]', 'groupe : le messager digne de confiance'), ('[[ٱلْعَذَابُ شَدِيدٌ]]', 'phrase : le châtiment est dur'),
        ]),
        dict(auto='cas', refs=[(56, 10, 24)], n=10),
    ],
    flash=[
        ("Sur quels points s'accorde l'adjectif ?", "cas, définition, genre, nombre"),
        ("Adjectif d'un pluriel de choses ?", "féminin singulier"),
        ("[[ٱللَّهُ عَلِيمٌ]] : groupe ou phrase ?", "phrase : Allah est omniscient"),
        ("Traduire [[عَذَابٌ أَلِيمٌ]].", "un châtiment douloureux"),
        ("Pourquoi [[ٱلْكَرِيمِ]] a-t-il l'article dans [[بِرَبِّكَ ٱلْكَرِيمِ]] ?", "le nom est défini par annexion au pronom"),
    ],
    notes={
        (88, 8): "[[وُجُوهٌ يَوْمَئِذٍ نَّاعِمَةٌ]] « des visages, ce jour-là, seront épanouis » : phrase nominale (sujet indéfini rendu possible par le contexte).",
        (88, 11): "[[لَّا تَسْمَعُ فِيهَا لَٰغِيَةً]] « tu n'y entendras aucune parole vaine » : phrase qualifiant [[جَنَّةٍ]].",
    },
)

L[15] = dict(
    objectifs=[
        "construire la phrase nominale : mubtadaʾ et khabar",
        "reconnaître les trois sortes de khabar",
        "comprendre l'inversion avec un sujet indéfini",
    ],
    expose=r"""
<p>Une phrase qui commence par un nom est une <b>phrase nominale</b> [[جُمْلَة ٱسْمِيَّة]]. Elle a deux éléments, tous deux au <b>nominatif</b> :</p>
<ul>
<li>le <b>mubtadaʾ</b> [[مُبْتَدَأ]] (« ce dont on parle »), en général <b>défini</b> ;</li>
<li>le <b>khabar</b> [[خَبَر]] (« ce qu'on en dit »), souvent <b>indéfini</b>.</li>
</ul>
<p>Il n'y a pas de verbe « être » au présent : on l'ajoute en français.</p>
{{ex 2:173|hl=الله@2,غفور,رحيم|from=إن|to=رحيم|com=Sans <i>inna</i> on aurait [[ٱللَّهُ غَفُورٌ رَّحِيمٌ]] : « Allah <b>est</b> pardonneur, miséricordieux » (deux khabar).}}
<h3><span class="pastille">1</span>Trois sortes de khabar</h3>
<table class="t">
<tr><th>khabar</th><th>exemple</th><th>traduction</th></tr>
<tr><td>un mot (ou un groupe)</td><td class="ar">ٱللَّهُ أَحَدٌ</td><td>Allah est unique</td></tr>
<tr><td>une phrase</td><td class="ar">ٱللَّهُ يَعْلَمُ</td><td>Allah sait (litt. Allah, Il sait)</td></tr>
<tr><td>un groupe prépositionnel ou de lieu (shibh jumla)</td><td class="ar">ٱلْحَمْدُ لِلَّهِ</td><td>la louange est à Allah</td></tr>
</table>
<h3><span class="pastille">2</span>Khabar en tête</h3>
<p>Quand le mubtadaʾ est <b>indéfini</b>, le khabar (préposition ou lieu) passe <b>devant</b> : on traduit par « il y a » ou « avoir ».</p>
{{ex 2:7|hl=ولهم,عذاب|from=ولهم|to=عظيم|com=[[وَلَهُمْ عَذَابٌ عَظِيمٌ]] « et ils auront un immense châtiment » : khabar [[لَهُمْ]] + mubtadaʾ [[عَذَابٌ]].}}
{{ex 2:2|hl=فيه,هدى|com=[[فِيهِ هُدًى]] « il y a en lui une guidance » (on peut aussi lire : « en lui, nul doute ; guidance pour les pieux »).}}
<p>Le khabar peut aussi être placé en tête pour <b>insister</b> ou <b>restreindre</b> : [[لَكُمْ دِينُكُمْ وَلِىَ دِينِ]] « à vous votre religion, à moi la mienne » (109:6).</p>
<h3><span class="pastille">3</span>Plusieurs khabar</h3>
<p>Un même mubtadaʾ peut recevoir une série de khabar, très fréquente dans les passages sur les noms d'Allah :</p>
{{ex 59:24|hl=هو,الله,الخالق,البارئ,المصور|from=هو|to=المصور}}
<div class="encadre"><span class="lab">Repérer une phrase nominale</span>1. Le premier mot est-il un nom ou un pronom ? 2. Trouve le second élément au nominatif (ou un groupe prépositionnel). 3. Ajoute « est ». Les particules [[إِنَّ]] et [[كَانَ]] modifient ensuite cette phrase (L19, L20).</div>
""",
    fiche=dict(
        titre='La phrase nominale', ar='الْمُبْتَدَأُ وَالْخَبَرُ',
        corps=r"""
<ul>
<li><b>mubtadaʾ</b> (défini) + <b>khabar</b> (souvent indéfini), tous deux au <b>nominatif</b> ; pas de verbe « être ».</li>
<li>Khabar : un mot ([[ٱللَّهُ أَحَدٌ]]), une phrase ([[ٱللَّهُ يَعْلَمُ]]), un groupe prépositionnel ([[ٱلْحَمْدُ لِلَّهِ]]).</li>
<li>Mubtadaʾ indéfini → khabar en tête : [[لَهُمْ عَذَابٌ]] « ils ont un châtiment » ; [[فِيهِ هُدًى]] « il y a en lui une guidance ».</li>
<li>Plusieurs khabar possibles : [[هُوَ ٱللَّهُ ٱلْخَالِقُ ٱلْبَارِئُ]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Repère le mubtadaʾ et le khabar, puis traduis.", items=[
            ('[[ٱللَّهُ غَفُورٌ رَحِيمٌ]]', 'mubtadaʾ [[ٱللَّهُ]], khabar [[غَفُورٌ]] (et [[رَحِيمٌ]]) : Allah est pardonneur, miséricordieux'),
            ('[[ٱلْحَمْدُ لِلَّهِ]]', 'mubtadaʾ [[ٱلْحَمْدُ]], khabar [[لِلَّهِ]] : la louange est à Allah'),
            ('[[لَهُمْ عَذَابٌ أَلِيمٌ]]', 'khabar en tête [[لَهُمْ]], mubtadaʾ [[عَذَابٌ]] : ils ont un châtiment douloureux'),
            ('[[ذَٰلِكَ ٱلْفَوْزُ ٱلْعَظِيمُ]]', 'mubtadaʾ [[ذَٰلِكَ]], khabar [[ٱلْفَوْزُ]] (+ adjectif) : voilà le succès immense'),
            ('[[ٱللَّهُ يَعْلَمُ]]', 'mubtadaʾ [[ٱللَّهُ]], khabar phrase [[يَعْلَمُ]] : Allah sait'),
            ('[[وَٱللَّهُ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ]]', "mubtadaʾ [[ٱللَّهُ]], khabar [[قَدِيرٌ]] : et Allah est omnipotent sur toute chose"),
        ], une=True),
        dict(auto='cas', refs=[(59, 18, 21)], n=8),
    ],
    flash=[
        ("Cas du mubtadaʾ et du khabar ?", "nominatif tous les deux"),
        ("Pourquoi [[لَهُمْ]] est-il en tête dans [[لَهُمْ عَذَابٌ]] ?", "le mubtadaʾ est indéfini"),
        ("Traduire [[ٱلْحَمْدُ لِلَّهِ]].", "la louange est à Allah"),
        ("Trois sortes de khabar ?", "mot, phrase, groupe prépositionnel / de lieu"),
        ("Y a-t-il un verbe « être » au présent ?", "non"),
    ],
    notes={
        (59, 22): "[[لَآ إِلَٰهَ إِلَّا هُوَ]] « pas de divinité sauf Lui » : <i>lā</i> de négation absolue (L19) et exception (L37).",
        (59, 23): "[[سُبْحَٰنَ ٱللَّهِ]] « gloire à Allah » : nom verbal à l'accusatif (complément absolu, L35).",
        (59, 24): "[[لَهُ ٱلْأَسْمَآءُ ٱلْحُسْنَىٰ]] « à Lui les plus beaux noms » : khabar en tête.",
    },
)

L[16] = dict(
    objectifs=[
        "connaître les démonstratifs du proche et du lointain",
        "distinguer « ce livre » et « ceci est un livre »",
        "accorder le démonstratif",
    ],
    expose=r"""
<p>Les démonstratifs [[أَسْمَاءُ ٱلْإِشَارَةِ]] désignent ce qui est proche (« ceci ») ou lointain (« cela »). Ils sont définis et, sauf au duel, indéclinables.</p>
<table class="t c">
<tr><th></th><th>proche</th><th>lointain</th></tr>
<tr><td>m. sg.</td><td class="ar">هَٰذَا</td><td class="ar">ذَٰلِكَ</td></tr>
<tr><td>f. sg.</td><td class="ar">هَٰذِهِ</td><td class="ar">تِلْكَ</td></tr>
<tr><td>m. duel</td><td class="ar">هَٰذَانِ / هَٰذَيْنِ</td><td class="ar">ذَانِكَ</td></tr>
<tr><td>f. duel</td><td class="ar">هَٰتَانِ / هَٰتَيْنِ</td><td>—</td></tr>
<tr><td>pluriel</td><td class="ar">هَٰٓؤُلَآءِ</td><td class="ar">أُو۟لَٰٓئِكَ</td></tr>
</table>
<p>Dans [[ذَٰلِكَ]] et [[أُو۟لَٰٓئِكَ]], le [[ك]] final s'accorde parfois avec la personne à qui l'on parle : [[ذَٰلِكُمْ]] « cela, ô vous ».</p>
<h3><span class="pastille">1</span>Démonstratif + nom avec article = groupe</h3>
<p>Suivi d'un nom à l'article, le démonstratif forme un groupe : « ce… », « cet… ».</p>
{{ex 2:2|hl=ذلك,الكتاب|com=[[ذَٰلِكَ ٱلْكِتَٰبُ]] « <b>ce</b> Livre » (le lointain marque ici la grandeur).}}
{{ex 106:3|hl=هذا,البيت|com=[[رَبَّ هَٰذَا ٱلْبَيْتِ]] « le Seigneur de <b>cette</b> Maison ».}}
<h3><span class="pastille">2</span>Démonstratif + nom sans article = phrase</h3>
<p>Suivi d'un nom indéfini, il forme une phrase nominale : « ceci est… ».</p>
{{ex 14:52|hl=هذا,بلاغ|from=هذا|to=للناس|com=[[هَٰذَا بَلَٰغٌ لِّلنَّاسِ]] « <b>ceci est</b> une communication pour les gens ».}}
<p>Avec un nom défini comme attribut, on intercale souvent le pronom de séparation : [[أُو۟لَٰٓئِكَ هُمُ ٱلْمُفْلِحُونَ]] « ceux-là, ce sont eux les gagnants » (2:5).</p>
<h3><span class="pastille">3</span>Accord</h3>
<p>Le démonstratif s'accorde avec ce qu'il désigne ; pour un pluriel de choses, il est au <b>féminin singulier</b> : [[تِلْكَ ءَايَٰتُ ٱلْكِتَٰبِ]] « voici les versets du Livre » (12:1). [[أُو۟لَٰٓئِكَ]] et [[هَٰٓؤُلَآءِ]] désignent des personnes (et parfois des choses : [[كُلُّ أُو۟لَٰٓئِكَ]] 17:36).</p>
""",
    fiche=dict(
        titre='Les démonstratifs', ar='أَسْمَاءُ الْإِشَارَةِ',
        corps=r"""
<table class="t c">
<tr><th></th><th>proche</th><th>lointain</th></tr>
<tr><td>m. sg.</td><td class="ar">هَٰذَا</td><td class="ar">ذَٰلِكَ</td></tr>
<tr><td>f. sg.</td><td class="ar">هَٰذِهِ</td><td class="ar">تِلْكَ</td></tr>
<tr><td>duel</td><td class="ar">هَٰذَانِ · هَٰتَانِ</td><td class="ar">ذَانِكَ</td></tr>
<tr><td>pl.</td><td class="ar">هَٰؤُلَاءِ</td><td class="ar">أُولَٰئِكَ</td></tr>
</table>
<ul>
<li>+ nom <b>avec</b> article = groupe : [[ذَٰلِكَ ٱلْكِتَابُ]] ce Livre.</li>
<li>+ nom <b>sans</b> article = phrase : [[هَٰذَا بَلَاغٌ]] ceci est une communication.</li>
<li>Pluriel de choses → [[تِلْكَ]] / [[هَٰذِهِ]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Choisis le démonstratif (proche) qui convient.", items=[
            ('[[… ٱلْكِتَابُ]]', '[[هَٰذَا]]'), ('[[… ٱلْجَنَّةُ]]', '[[هَٰذِهِ]]'), ('[[… ٱلْمُؤْمِنُونَ]]', '[[هَٰؤُلَاءِ]]'),
            ('[[… ٱلْآيَاتُ]]', '[[هَٰذِهِ]] (pluriel de choses)'), ('[[… ٱلرَّجُلَانِ]]', '[[هَٰذَانِ]]'), ('[[… ٱلْقَرْيَةُ]]', '[[هَٰذِهِ]]'),
        ]),
        dict(consigne="Traduis (groupe ou phrase ?).", items=[
            ('[[هَٰذَا ٱلْبَيْتُ]]', 'groupe : cette maison'), ('[[هَٰذَا بَيْتٌ]]', 'phrase : ceci est une maison'),
            ('[[تِلْكَ ٱلْجَنَّةُ]]', 'groupe : ce Paradis'), ('[[ذَٰلِكَ هُوَ ٱلْفَوْزُ ٱلْعَظِيمُ]]', "phrase : c'est cela le succès immense"),
        ]),
    ],
    flash=[
        ("Démonstratif lointain féminin ?", "[[تِلْكَ]]"),
        ("[[ذَٰلِكَ ٱلْكِتَٰبُ]] : traduire.", "ce Livre"),
        ("[[هَٰذَا بَلَٰغٌ]] : groupe ou phrase ?", "phrase : ceci est une communication"),
        ("Démonstratif proche pluriel ?", "[[هَٰٓؤُلَآءِ]]"),
        ("Pour un pluriel de choses ?", "féminin singulier : [[تِلْكَ]] / [[هَٰذِهِ]]"),
    ],
    notes={
        (2, 1): "[[الٓمٓ]] <i>alif-lām-mīm</i> : lettres isolées ; leur sens est connu d'Allah seul selon de nombreux savants.",
        (2, 2): "[[لَا رَيْبَ]] : <i>lā</i> de négation absolue, nom à l'accusatif sans tanwīn (L19).",
        (2, 3): "[[ٱلَّذِينَ يُؤْمِنُونَ]] « ceux qui croient » : relatif (L17) qualifiant [[ٱلْمُتَّقِينَ]].",
        (2, 5): "[[عَلَىٰ هُدًى مِّن رَّبِّهِمْ]] « sur une guidance venant de leur Seigneur » : khabar prépositionnel (L15).",
    },
)

L[17] = dict(
    objectifs=[
        "connaître les relatifs et les accorder",
        "reconnaître la proposition relative (ṣila) et son pronom de rappel",
        "employer [[مَنْ]] et [[مَا]] relatifs",
    ],
    expose=r"""
<p>Le relatif [[ٱسْمٌ مَوْصُول]] introduit une proposition, la <b>ṣila</b> [[صِلَة]], qui complète un nom défini ou tient lieu de nom (« celui qui… »).</p>
<table class="t c">
<tr><th></th><th>masculin</th><th>féminin</th></tr>
<tr><td>singulier</td><td class="ar">ٱلَّذِي</td><td class="ar">ٱلَّتِي</td></tr>
<tr><td>duel</td><td class="ar">ٱللَّذَانِ / ٱللَّذَيْنِ</td><td class="ar">ٱللَّتَانِ / ٱللَّتَيْنِ</td></tr>
<tr><td>pluriel</td><td class="ar">ٱلَّذِينَ</td><td class="ar">ٱللَّاتِي · ٱللَّائِي</td></tr>
</table>
<p>À côté de ces formes variables, deux relatifs invariables sont très fréquents : [[مَنْ]] « celui qui, ceux qui » (personnes) et [[مَا]] « ce que, ce qui » (choses).</p>
<h3><span class="pastille">1</span>La ṣila et le pronom de rappel</h3>
<p>La ṣila contient souvent un pronom qui renvoie au relatif, le <b>ʿāʾid</b> [[عَائِد]]. Le français ne le traduit pas :</p>
{{ex 67:1|hl=الذي,بيده|com=[[ٱلَّذِى بِيَدِهِ ٱلْمُلْكُ]] « Celui dans la main <b>de qui</b> (litt. « qui dans sa main ») est la royauté ».}}
<p>Quand le relatif est sujet de la ṣila, le pronom est contenu dans le verbe :</p>
{{ex 67:2|hl=الذي,خلق|from=الذي|to=والحياة|com=[[ٱلَّذِى خَلَقَ]] « Celui qui a créé ».}}
<h3><span class="pastille">2</span>Le relatif employé seul</h3>
<p>Sans nom devant lui, le relatif signifie « celui qui, ceux qui » : [[ٱلَّذِينَ ءَامَنُوا۟]] « ceux qui ont cru » ; [[مَا فِى ٱلسَّمَٰوَٰتِ]] « ce qui est dans les cieux » ; [[مَنْ خَلَقَ]] « Celui qui a créé ».</p>
{{ex 103:3|hl=الذين|com=[[إِلَّا ٱلَّذِينَ ءَامَنُوا۟]] « sauf ceux qui ont cru ».}}
<h3><span class="pastille">3</span>Après un nom indéfini : pas de relatif</h3>
<p>Le relatif suit un nom <b>défini</b>. Après un nom indéfini, la proposition se place directement, sans relatif (L14) : [[يَوْمًا لَّا تَجْزِى نَفْسٌ]] « un jour où nulle âme ne suffira ».</p>
<div class="attention"><span class="lab">Mā et man : plusieurs rôles</span>[[مَا]] et [[مَنْ]] sont aussi interrogatifs (« quoi ? », « qui ? », L18) et conditionnels (« quiconque », L38) ; [[مَا]] est encore une négation (L25). Le contexte et la colonne d'analyse des textes tranchent.</div>
""",
    fiche=dict(
        titre='Les relatifs', ar='الْأَسْمَاءُ الْمَوْصُولَةُ',
        corps=r"""
<table class="t c">
<tr><th></th><th>m.</th><th>f.</th></tr>
<tr><td>sg.</td><td class="ar">ٱلَّذِي</td><td class="ar">ٱلَّتِي</td></tr>
<tr><td>duel</td><td class="ar">ٱللَّذَانِ</td><td class="ar">ٱللَّتَانِ</td></tr>
<tr><td>pl.</td><td class="ar">ٱلَّذِينَ</td><td class="ar">ٱللَّاتِي</td></tr>
</table>
<ul>
<li>[[مَنْ]] : celui qui (personnes) ; [[مَا]] : ce que (choses).</li>
<li>Ṣila + pronom de rappel (non traduit) : [[ٱلَّذِي بِيَدِهِ ٱلْمُلْكُ]].</li>
<li>Après un nom indéfini : pas de relatif.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Complète avec le relatif qui convient.", items=[
            ('[[ٱلرَّجُلُ … جَاءَ]]', '[[ٱلَّذِي]]'), ('[[ٱلنَّفْسُ … خَلَقَهَا ٱللَّهُ]]', '[[ٱلَّتِي]]'),
            ('[[ٱلْمُؤْمِنُونَ … يُصَلُّونَ]]', '[[ٱلَّذِينَ]]'), ('[[ٱلْجَنَّةُ … وُعِدَ ٱلْمُتَّقُونَ]]', '[[ٱلَّتِي]]'),
        ], une=True),
        dict(consigne="Traduis.", items=[
            ('[[ٱلَّذِينَ آمَنُوا]]', 'ceux qui ont cru'), ('[[مَا فِي ٱلْأَرْضِ]]', 'ce qui est sur la terre'),
            ('[[مَنْ خَلَقَ ٱلسَّمَاوَاتِ]]', 'celui qui a créé les cieux'), ('[[ٱلَّذِي أَطْعَمَهُمْ]]', 'Celui qui les a nourris'),
            ('[[مِمَّا رَزَقْنَاهُمْ]]', 'de ce que Nous leur avons attribué'), ('[[ٱلَّذِي لَهُ مُلْكُ ٱلسَّمَاوَاتِ]]', 'Celui à qui appartient la royauté des cieux'),
        ]),
    ],
    flash=[
        ("Relatif féminin singulier ?", "[[ٱلَّتِي]]"),
        ("Qu'est-ce que le ʿāʾid ?", "le pronom de rappel dans la ṣila"),
        ("Traduire [[ٱلَّذِينَ ءَامَنُوا۟]].", "ceux qui ont cru"),
        ("Met-on un relatif après un nom indéfini ?", "non"),
        ("Différence entre [[مَنْ]] et [[مَا]] relatifs ?", "<i>man</i> : personnes ; <i>mā</i> : choses"),
    ],
    notes={
        (67, 2): "[[لِيَبْلُوَكُمْ]] « afin de vous éprouver » : <i>li-</i> + subjonctif (L23). [[أَيُّكُمْ أَحْسَنُ عَمَلًا]] « lequel de vous est le meilleur en œuvre » : élatif + spécification (L36, L40).",
        (67, 3): "[[مَّا تَرَىٰ]] « tu ne vois pas » : ici <i>mā</i> est une négation (L25).",
        (67, 5): "[[بِمَصَٰبِيحَ]] : diptote, génitif en <i>-a</i> (L9).",
    },
)

L[18] = dict(
    objectifs=[
        "poser et comprendre une question",
        "reconnaître la question rhétorique",
        "construire l'apostrophe avec [[يَا]] et [[يَا أَيُّهَا]]",
    ],
    expose=r"""
<h3><span class="pastille">1</span>Questions fermées : [[أَ]] et [[هَلْ]]</h3>
<p>Ces deux particules transforment une phrase en question (« est-ce que… ? »). [[أَ]] se soude au mot suivant.</p>
{{ex 88:1|hl=هل,أتاك|com=« T'<b>est-il</b> parvenu le récit de l'Enveloppante ? »}}
{{ex 94:1|hl=ألم|com=[[أَلَمْ]] = [[أَ]] + [[لَمْ]] : « n'avons-Nous pas… ? »}}
<h3><span class="pastille">2</span>Mots interrogatifs</h3>
<table class="t">
<tr><th class="ar">mot</th><th>sens</th><th class="ar">mot</th><th>sens</th></tr>
<tr><td class="ar">مَنْ</td><td>qui ?</td><td class="ar">مَتَى</td><td>quand ?</td></tr>
<tr><td class="ar">مَا · مَاذَا</td><td>que ? quoi ?</td><td class="ar">كَيْفَ</td><td>comment ?</td></tr>
<tr><td class="ar">أَيْنَ</td><td>où ?</td><td class="ar">كَمْ</td><td>combien ?</td></tr>
<tr><td class="ar">أَيّ</td><td>quel ? lequel ?</td><td class="ar">أَنَّى</td><td>comment ? d'où ?</td></tr>
<tr><td class="ar">لِمَ · لِمَاذَا</td><td>pourquoi ?</td><td class="ar">أَيَّانَ</td><td>quand ? (pour l'Heure)</td></tr>
</table>
{{ex 88:17|hl=أفلا,كيف|com=[[أَفَلَا يَنظُرُونَ]] « ne regardent-ils donc pas… » ; [[كَيْفَ خُلِقَتْ]] « comment ils ont été créés ».}}
<h3><span class="pastille">3</span>La question rhétorique</h3>
<p>Le Coran pose souvent des questions dont la réponse est évidente : elles affirment avec force. [[أَلَمْ نَشْرَحْ لَكَ صَدْرَكَ]] = « Nous t'avons bien ouvert la poitrine ». [[أَلَيْسَ ٱللَّهُ بِأَحْكَمِ ٱلْحَٰكِمِينَ]] = « Allah est assurément le plus sage des juges ».</p>
<h3><span class="pastille">4</span>L'apostrophe (nidāʾ)</h3>
<p>On appelle avec [[يَا]] « ô ». Le nom appelé, <b>munādā</b> [[مُنَادَى]], prend :</p>
<ul>
<li>une <b>ḍamma sans tanwīn</b> s'il est un nom propre ou une personne précise : [[يَٰمُوسَىٰ]], [[يَٰنُوحُ]] ;</li>
<li>l'<b>accusatif</b> s'il est annexé : [[يَٰٓأَهْلَ ٱلْكِتَٰبِ]] « ô gens du Livre ». Le [[يَا]] tombe souvent devant [[رَبّ]] : [[رَبَّنَا]] « ô notre Seigneur », [[رَبِّ]] « ô mon Seigneur ».</li>
</ul>
<p>Devant un nom à l'article, on intercale [[أَيُّهَا]] (f. [[أَيَّتُهَا]]) ; le nom reste au <b>nominatif</b> :</p>
{{ex 82:6|hl=ياأيها,الإنسان|com=« <b>Ô</b> homme ! Qu'est-ce qui t'a trompé au sujet de ton Seigneur le Généreux ? »}}
{{ex 89:27|hl=ياأيتها,النفس}}
""",
    fiche=dict(
        titre="Interrogation et apostrophe", ar='الِاسْتِفْهَامُ وَالنِّدَاءُ',
        corps=r"""
<ul>
<li>Oui/non : [[أَ]] (soudé), [[هَلْ]] ; [[أَلَمْ]] « n'est-ce pas que… ? » ; [[أَفَلَا]] « ne… donc pas ? ».</li>
<li>[[مَنْ]] qui · [[مَا]]/[[مَاذَا]] quoi · [[أَيْنَ]] où · [[مَتَى]] quand · [[كَيْفَ]] comment · [[كَمْ]] combien · [[أَيّ]] quel · [[أَنَّى]] comment, d'où · [[لِمَ]] pourquoi.</li>
<li>Question rhétorique = affirmation forte.</li>
<li>[[يَا]] + nom propre : ḍamma sans tanwīn ([[يَا مُوسَىٰ]]) ; + annexé : accusatif ([[يَا أَهْلَ ٱلْكِتَابِ]], [[رَبَّنَا]]).</li>
<li>[[يَا أَيُّهَا]] / [[يَا أَيَّتُهَا]] + nom à l'article au nominatif.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Traduis.", items=[
            ('[[مَنْ رَبُّكَ]]', 'qui est ton Seigneur ?'), ('[[مَا هَٰذَا]]', "qu'est-ce que ceci ?"),
            ('[[أَيْنَ ٱلْمَفَرُّ]]', 'où est le refuge ? (75:10)'), ('[[كَيْفَ تَكْفُرُونَ بِٱللَّهِ]]', 'comment pouvez-vous mécroire en Allah ? (2:28)'),
            ('[[هَلْ أَتَاكَ حَدِيثُ مُوسَىٰ]]', 'le récit de Mūsā t\'est-il parvenu ? (20:9)'), ('[[يَا أَيُّهَا ٱلَّذِينَ آمَنُوا]]', 'ô vous qui avez cru'),
        ]),
        dict(consigne="Écris l'apostrophe.", items=[
            ('ô Mūsā', '[[يَا مُوسَىٰ]]'), ('ô gens du Livre', '[[يَا أَهْلَ ٱلْكِتَابِ]]'), ('ô notre Seigneur', '[[رَبَّنَا]]'),
            ('ô gens (les hommes)', '[[يَا أَيُّهَا ٱلنَّاسُ]]'), ('ô âme apaisée', '[[يَا أَيَّتُهَا ٱلنَّفْسُ ٱلْمُطْمَئِنَّةُ]]'),
        ]),
    ],
    flash=[
        ("Que signifie [[أَيْنَ]] ?", "où ?"),
        ("Cas du nom après [[يَا أَيُّهَا]] ?", "nominatif, avec l'article"),
        ("[[يَا أَهْلَ ٱلْكِتَٰبِ]] : pourquoi [[أَهْلَ]] à l'accusatif ?", "munādā annexé"),
        ("Valeur de [[أَلَمْ نَشْرَحْ]] ?", "question rhétorique : « Nous avons bien ouvert »"),
        ("Féminin de [[أَيُّهَا]] ?", "[[أَيَّتُهَا]]"),
    ],
    notes={
        (88, 18): "[[رُفِعَتْ]], [[نُصِبَتْ]], [[سُطِحَتْ]] : verbes au passif (L26), féminins pour des pluriels de choses (L7).",
        (88, 21): "[[إِنَّمَآ أَنتَ مُذَكِّرٌ]] « tu n'es qu'un rappeleur » : restriction (L37).",
        (82, 8): "[[فِىٓ أَىِّ صُورَةٍ مَّا شَآءَ رَكَّبَكَ]] « Il t'a façonné dans la forme qu'Il a voulue ».",
    },
)

L[19] = dict(
    objectifs=[
        "employer [[إِنَّ]] et ses sœurs",
        "mettre leur nom à l'accusatif et leur khabar au nominatif",
        "reconnaître le lām d'insistance et le lā de négation absolue",
    ],
    expose=r"""
<p>Six particules s'ajoutent en tête d'une phrase nominale et en modifient le sens. Elles mettent le <b>mubtadaʾ à l'accusatif</b> (il devient leur « nom », <i>ism</i>) ; le <b>khabar reste au nominatif</b>.</p>
<table class="t">
<tr><th class="ar">particule</th><th>sens</th><th class="ar">particule</th><th>sens</th></tr>
<tr><td class="ar">إِنَّ</td><td>certes, en vérité (insistance)</td><td class="ar">لَٰكِنَّ</td><td>mais</td></tr>
<tr><td class="ar">أَنَّ</td><td>que (après un verbe)</td><td class="ar">لَيْتَ</td><td>si seulement !</td></tr>
<tr><td class="ar">كَأَنَّ</td><td>comme si</td><td class="ar">لَعَلَّ</td><td>peut-être ; afin que</td></tr>
</table>
{{ex 2:173|hl=إن,الله@2,غفور|from=إن|to=رحيم|com=[[ٱللَّهُ غَفُورٌ]] devient [[إِنَّ ٱللَّهَ غَفُورٌ]] : <i>Allāha</i> à l'accusatif, <i>ghafūrun</i> reste au nominatif.}}
<h3><span class="pastille">1</span>Le lām d'insistance</h3>
<p>Après [[إِنَّ]], le khabar reçoit souvent un [[لَـ]] qui renforce encore : <i>lām al-muzaḥlaqa</i>.</p>
{{ex 100:6|hl=إن,الإنسان,لكنود|com=« L'homme est, <b>en vérité</b>, bien ingrat envers son Seigneur » : nom [[ٱلْإِنسَٰنَ]] (accusatif), khabar [[لَكَنُودٌ]] (nominatif, avec <i>la-</i>).}}
<h3><span class="pastille">2</span>Avec un pronom</h3>
<p>Le nom de <i>inna</i> est souvent un pronom suffixe : [[إِنَّهُ]] « certes il », [[إِنَّهَا]], [[إِنَّكَ]], [[إِنِّي]] / [[إِنَّنِي]] « certes je », [[إِنَّا]] / [[إِنَّنَا]] « certes nous ».</p>
<h3><span class="pastille">3</span>Khabar placé devant</h3>
<p>Si le khabar est un groupe prépositionnel, il peut précéder le nom : [[إِنَّ فِى ذَٰلِكَ لَءَايَةً]] « il y a certes en cela un signe » ; [[فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا]] (94:5).</p>
<h3><span class="pastille">4</span>Innamā</h3>
<p>[[إِنَّمَا]] (<i>inna</i> + <i>mā</i>) n'a plus d'effet sur les cas et signifie « ne… que, seulement » : [[إِنَّمَا نُطْعِمُكُمْ لِوَجْهِ ٱللَّهِ]] « nous ne vous nourrissons que pour la Face d'Allah » (76:9) — voir L37.</p>
<h3><span class="pastille">5</span>Le lā de négation absolue</h3>
<p>[[لَا]] devant un nom indéfini nie <b>toute l'espèce</b> : « aucun… ». Il agit comme <i>inna</i> : le nom est à l'accusatif, <b>sans tanwīn</b>.</p>
{{ex 2:2|hl=لا,ريب|com=[[لَا رَيْبَ فِيهِ]] « il n'y a <b>aucun</b> doute en lui ».}}
{{ex 2:255|hl=لا,إله|from=الله|to=القيوم|com=[[لَآ إِلَٰهَ إِلَّا هُوَ]] « pas de divinité sauf Lui ».}}
""",
    fiche=dict(
        titre='Inna et ses sœurs', ar='إِنَّ وَأَخَوَاتُهَا',
        corps=r"""
<ul>
<li>[[إِنَّ]] certes · [[أَنَّ]] que · [[كَأَنَّ]] comme si · [[لَٰكِنَّ]] mais · [[لَيْتَ]] si seulement · [[لَعَلَّ]] peut-être.</li>
<li><b>Nom (ism) à l'accusatif</b>, <b>khabar au nominatif</b> : [[إِنَّ ٱللَّهَ غَفُورٌ]].</li>
<li>Lām d'insistance sur le khabar : [[إِنَّ ٱلْإِنسَانَ لَكَنُودٌ]].</li>
<li>Pronoms : [[إِنَّهُ]] [[إِنِّي]] [[إِنَّا]] ; khabar prépositionnel en tête possible.</li>
<li>[[إِنَّمَا]] : « ne… que », sans effet sur les cas.</li>
<li>[[لَا]] de négation absolue + nom accusatif sans tanwīn : [[لَا رَيْبَ]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Introduis [[إِنَّ]] et fais les changements nécessaires.", items=[
            ('[[ٱللَّهُ عَلِيمٌ]]', '[[إِنَّ ٱللَّهَ عَلِيمٌ]]'), ('[[ٱلْمُتَّقُونَ فِي جَنَّاتٍ]]', '[[إِنَّ ٱلْمُتَّقِينَ فِي جَنَّاتٍ]]'),
            ('[[ٱلْإِنْسَانُ فِي خُسْرٍ]]', '[[إِنَّ ٱلْإِنْسَانَ لَفِي خُسْرٍ]] (avec lām)'), ('[[هُوَ ٱلسَّمِيعُ]]', '[[إِنَّهُ هُوَ ٱلسَّمِيعُ]]'),
            ('[[ٱلْأَبْرَارُ فِي نَعِيمٍ]]', '[[إِنَّ ٱلْأَبْرَارَ لَفِي نَعِيمٍ]]'), ('[[ٱلسَّاعَةُ آتِيَةٌ]]', '[[إِنَّ ٱلسَّاعَةَ آتِيَةٌ]] (20:15)'),
        ], une=True),
        dict(auto='cas', refs=[(2, 6, 8)], n=8),
    ],
    flash=[
        ("Cas du nom de [[إِنَّ]] ?", "accusatif"),
        ("Cas du khabar de [[إِنَّ]] ?", "nominatif"),
        ("Rôle du [[لَـ]] de [[لَكَنُودٌ]] ?", "insistance sur le khabar (lām al-muzaḥlaqa)"),
        ("[[لَا رَيْبَ]] : pourquoi pas de tanwīn ?", "lā de négation absolue"),
        ("Sens de [[لَعَلَّ]] ?", "peut-être ; afin que"),
    ],
    notes={
        (100, 1): "[[وَٱلْعَٰدِيَٰتِ ضَبْحًا]] « Par les coursiers haletants ! » : serment (L39) ; [[ضَبْحًا]] est à l'accusatif (complément de manière, L35).",
        (100, 9): "[[أَفَلَا يَعْلَمُ إِذَا بُعْثِرَ]] « ne sait-il donc pas que, lorsque sera bouleversé… » : question rhétorique (L18) et passif (L26).",
        (100, 11): "[[إِنَّ رَبَّهُم بِهِمْ يَوْمَئِذٍ لَّخَبِيرٌۢ]] : nom [[رَبَّهُم]], khabar [[لَّخَبِيرٌ]] précédé de deux compléments.",
    },
)

L[20] = dict(
    objectifs=[
        "employer [[كَانَ]] et ses sœurs",
        "mettre leur khabar à l'accusatif",
        "comprendre [[كَانَ]] + inaccompli et [[لَيْسَ]]",
    ],
    expose=r"""
<p>[[كَانَ]] « être (au passé) » et ses « sœurs » sont des verbes qui se placent devant une phrase nominale. Leur effet est l'inverse de celui de <i>inna</i> : le <b>sujet reste au nominatif</b> (il devient leur <i>ism</i>), le <b>khabar passe à l'accusatif</b>.</p>
{{ex 4:17|hl=وكان,الله,عليما,حكيما|from=وكان|to=حكيما|com=[[كَانَ ٱللَّهُ عَلِيمًا حَكِيمًا]] : <i>Allāhu</i> nominatif, <i>ʿalīman ḥakīman</i> accusatif.}}
<table class="t">
<tr><th class="ar">verbe</th><th>sens</th><th class="ar">verbe</th><th>sens</th></tr>
<tr><td class="ar">كَانَ</td><td>être, avoir été</td><td class="ar">ظَلَّ</td><td>rester, demeurer (le jour)</td></tr>
<tr><td class="ar">صَارَ</td><td>devenir</td><td class="ar">بَاتَ</td><td>passer la nuit à</td></tr>
<tr><td class="ar">أَصْبَحَ</td><td>devenir ; être au matin</td><td class="ar">لَيْسَ</td><td>ne pas être</td></tr>
<tr><td class="ar">أَمْسَى · أَضْحَى</td><td>être le soir · la matinée</td><td class="ar">مَا زَالَ</td><td>ne pas cesser d'être</td></tr>
<tr><td class="ar">مَا دَامَ</td><td>tant que</td><td class="ar">مَا بَرِحَ · مَا فَتِئَ</td><td>ne pas cesser de</td></tr>
</table>
<h3><span class="pastille">1</span>Kāna, un verbe qui se conjugue</h3>
<p>[[كَانَ]] se conjugue comme tout verbe concave (L31) : [[كَانُوا]] ils étaient, [[كُنتُمْ]] vous étiez, [[كُنتُ]] j'étais ; inaccompli [[يَكُونُ]] ; apocopé [[لَمْ يَكُنْ]] (parfois [[لَمْ يَكُ]]) ; impératif [[كُنْ]].</p>
{{ex 76:1|hl=يكن,شيئا,مذكورا|com=[[لَمْ يَكُن شَيْـًٔا مَّذْكُورًا]] « il n'était pas une chose mentionnée » : khabar [[شَيْـًٔا]] à l'accusatif.}}
<h3><span class="pastille">2</span>Kāna + inaccompli : l'habitude</h3>
<p>[[كَانَ]] suivi d'un verbe à l'inaccompli exprime un passé qui dure ou se répète : [[كَانُوا يَعْمَلُونَ]] « ils faisaient (habituellement) ». Très fréquent dans le Coran.</p>
<h3><span class="pastille">3</span>Kāna et les attributs d'Allah</h3>
<p>Dans [[كَانَ ٱللَّهُ عَلِيمًا حَكِيمًا]], <i>kāna</i> n'indique pas un passé révolu : il marque la <b>permanence</b> (« Allah est, de tout temps, omniscient et sage »).</p>
<h3><span class="pastille">4</span>Laysa</h3>
<p>[[لَيْسَ]] « ne pas être » nie la phrase nominale au présent. Il ne se conjugue qu'à l'accompli : [[لَيْسَ]], [[لَيْسَتْ]], [[لَسْتَ]], [[لَسْتُمْ]], [[لَسْتُ]]. Son khabar est souvent introduit par [[بِـ]] : [[أَلَيْسَ ٱللَّهُ بِأَحْكَمِ ٱلْحَٰكِمِينَ]] (95:8) ; [[لَسْتَ عَلَيْهِم بِمُصَيْطِرٍ]] « tu n'es pas sur eux un dominateur » (88:22).</p>
""",
    fiche=dict(
        titre='Kāna et ses sœurs', ar='كَانَ وَأَخَوَاتُهَا',
        corps=r"""
<ul>
<li>[[كَانَ]] être · [[صَارَ]] devenir · [[أَصْبَحَ]] devenir, être au matin · [[ظَلَّ]] rester · [[بَاتَ]] · [[أَمْسَى]] · [[لَيْسَ]] ne pas être · [[مَا زَالَ]] ne pas cesser · [[مَا دَامَ]] tant que.</li>
<li><b>Nom (ism) au nominatif, khabar à l'accusatif</b> : [[كَانَ ٱللَّهُ عَلِيمًا]].</li>
<li>[[كَانَ]] + inaccompli = passé habituel : [[كَانُوا يَعْمَلُونَ]].</li>
<li>Avec les attributs d'Allah : permanence.</li>
<li>[[لَيْسَ]] : khabar souvent avec [[بِـ]] : [[لَسْتَ عَلَيْهِمْ بِمُصَيْطِرٍ]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Introduis [[كَانَ]] et fais les changements nécessaires.", items=[
            ('[[ٱللَّهُ عَلِيمٌ]]', '[[كَانَ ٱللَّهُ عَلِيمًا]]'), ('[[ٱلنَّاسُ أُمَّةٌ وَاحِدَةٌ]]', '[[كَانَ ٱلنَّاسُ أُمَّةً وَاحِدَةً]] (2:213)'),
            ('[[ٱلْإِنْسَانُ عَجُولٌ]]', '[[كَانَ ٱلْإِنْسَانُ عَجُولًا]] (17:11)'), ('[[هُمْ ظَالِمُونَ]]', '[[كَانُوا ظَالِمِينَ]]'),
        ], une=True),
        dict(consigne="Traduis.", items=[
            ('[[كَانُوا يَعْمَلُونَ]]', 'ils faisaient (habituellement)'), ('[[لَيْسَ ٱلْبِرُّ]]', "la piété n'est pas…"),
            ('[[لَسْتُ بِرَبِّكُمْ]]', 'je ne suis pas votre Seigneur'), ('[[أَصْبَحُوا خَاسِرِينَ]]', 'ils sont devenus perdants'),
        ]),
        dict(auto='cas', refs=[(4, 17, 17)], n=8),
    ],
    flash=[
        ("Cas du khabar de [[كَانَ]] ?", "accusatif"),
        ("[[كَانُوا يَعْمَلُونَ]] : quelle nuance ?", "passé habituel"),
        ("Sens de [[أَصْبَحَ]] ?", "devenir ; être au matin"),
        ("Conjugue [[لَيْسَ]] à la 2e m. sg.", "[[لَسْتَ]]"),
        ("Apocopé de [[كَانَ]] (3e m. sg.) ?", "[[لَمْ يَكُنْ]] (ou [[لَمْ يَكُ]])"),
    ],
    notes={
        (76, 2): "[[نَّبْتَلِيهِ]] « pour l'éprouver » : phrase d'état (L36). [[فَجَعَلْنَٰهُ سَمِيعًۢا بَصِيرًا]] : deux compléments de [[جَعَلَ]] (L34).",
        (76, 3): "[[إِمَّا شَاكِرًا وَإِمَّا كَفُورًا]] « soit reconnaissant, soit ingrat » : état (ḥāl, L36).",
        (76, 5): "[[كَانَ مِزَاجُهَا كَافُورًا]] « dont le mélange est de camphre » : <i>kāna</i>, nom au nominatif, khabar à l'accusatif.",
        (76, 9): "[[إِنَّمَا نُطْعِمُكُمْ لِوَجْهِ ٱللَّهِ]] : restriction (L37).",
    },
)
