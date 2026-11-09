"""Partie II (1) — leçons 3 à 11."""

L = {}

L[3] = dict(
    objectifs=[
        "classer chaque mot : nom (ism), verbe (fiʿl) ou particule (ḥarf)",
        "comprendre la racine et le schème, clé du vocabulaire arabe",
        "retrouver la racine d'un mot du Coran",
    ],
    expose=r"""
<p>Les grammairiens arabes répartissent tous les mots en <b>trois espèces</b>. Savoir à laquelle appartient un mot est le premier geste de toute analyse.</p>
<table class="t">
<tr><th>espèce</th><th>définition</th><th>exemples</th></tr>
<tr><td><b>ism</b> [[ٱسْم]] — nom</td><td>désigne un être, une chose, une qualité, une idée ; comprend aussi les adjectifs, les pronoms et les démonstratifs</td><td>[[ٱللَّه]], [[إِنْسَان]], [[رَحِيم]], [[هُوَ]]</td></tr>
<tr><td><b>fiʿl</b> [[فِعْل]] — verbe</td><td>exprime une action ou un état situé dans le temps</td><td>[[خَلَقَ]] il a créé, [[يَعْلَمُ]] il sait</td></tr>
<tr><td><b>ḥarf</b> [[حَرْف]] — particule</td><td>n'a de sens qu'avec d'autres mots : prépositions, conjonctions, négations…</td><td>[[فِي]], [[وَ]], [[لَا]], [[إِنَّ]]</td></tr>
</table>
<h3><span class="pastille">1</span>Reconnaître un nom ou un verbe</h3>
<ul>
<li>Un mot est un <b>nom</b> s'il peut recevoir l'article [[ٱلْ]], le tanwīn, s'il suit une préposition ou s'il est apostrophé (« ô… »).</li>
<li>Un mot est un <b>verbe</b> s'il peut être précédé de [[قَدْ]], [[سَـ]], [[سَوْفَ]], [[لَمْ]], ou s'il porte une terminaison de personne comme [[ـتُ]] (« je ») ou [[ـتْ]] (« elle »).</li>
<li>Ce qui n'accepte aucune de ces marques est une <b>particule</b>.</li>
</ul>
{{ex 103:2|hl=الإنسان,خسر|com=[[إِنَّ]] particule · [[ٱلْإِنسَٰنَ]] nom (article) · [[لَفِى]] deux particules (<i>la-</i> + <i>fī</i>) · [[خُسْرٍ]] nom (tanwīn, après préposition).}}
{{ex 103:3|hl=آمنوا,وعملوا|com=[[ءَامَنُوا۟]] et [[عَمِلُوا۟]] sont des verbes : terminaison <i>-ū</i> « ils ».}}

<h3><span class="pastille">2</span>La racine</h3>
<p>Presque tous les noms et verbes arabes reposent sur une <b>racine</b> [[جَذْر]] de trois consonnes (parfois quatre) qui porte un sens général. On en dérive des dizaines de mots en ajoutant des voyelles et des lettres. Avec la racine <b>ع ل م</b> (idée de <i>savoir</i>) :</p>
<table class="t c">
<tr><th>mot</th><th>sens</th><th>mot</th><th>sens</th></tr>
<tr><td class="ar">عَلِمَ</td><td>il a su</td><td class="ar">عَالِمٌ</td><td>savant, qui sait</td></tr>
<tr><td class="ar">عِلْمٌ</td><td>science, savoir</td><td class="ar">عَلِيمٌ</td><td>omniscient</td></tr>
<tr><td class="ar">عَلَّمَ</td><td>il a enseigné</td><td class="ar">مَعْلُومٌ</td><td>connu</td></tr>
</table>
<p>De même <b>ك ت ب</b> (<i>écrire</i>) : [[كَتَبَ]] il a écrit, [[كِتَابٌ]] livre, écrit, [[كَاتِبٌ]] scribe, [[مَكْتُوبٌ]] écrit (participe). Les dictionnaires arabes sont classés par racine ; le lexique de ce livre aussi (annexe D).</p>

<h3><span class="pastille">3</span>Le schème</h3>
<p>Le <b>schème</b> [[وَزْن]] est le moule dans lequel on coule la racine. Les grammairiens le notent avec les trois lettres <b>ف ع ل</b>, qui représentent la 1<sup>re</sup>, la 2<sup>e</sup> et la 3<sup>e</sup> radicale. Chaque schème apporte une nuance de sens :</p>
<table class="t c">
<tr><th>schème</th><th>valeur fréquente</th><th>exemples</th></tr>
<tr><td class="ar">فَعَلَ</td><td>verbe (il a fait)</td><td class="ar">خَلَقَ، كَتَبَ</td></tr>
<tr><td class="ar">فَاعِل</td><td>celui qui fait</td><td class="ar">كَافِر، عَالِم، خَالِق</td></tr>
<tr><td class="ar">مَفْعُول</td><td>ce qui subit l'action</td><td class="ar">مَكْتُوب، مَعْلُوم</td></tr>
<tr><td class="ar">فَعِيل</td><td>qualité permanente</td><td class="ar">رَحِيم، عَلِيم، كَرِيم</td></tr>
<tr><td class="ar">فَعْلَان</td><td>qualité débordante</td><td class="ar">رَحْمَٰن</td></tr>
<tr><td class="ar">أَفْعَل</td><td>plus…, le plus…</td><td class="ar">أَكْبَر، أَعْلَم</td></tr>
</table>
<p>La racine <b>ر ح م</b> donne ainsi [[رَحِمَ]] (il a fait miséricorde), [[رَحْمَة]] (miséricorde), [[رَحِيم]] (très miséricordieux), [[رَحْمَٰن]] (le Tout-Miséricordieux), [[أَرْحَم]] (le plus miséricordieux).</p>

<h3><span class="pastille">4</span>Trouver la racine</h3>
<ol>
<li>Retirer les préfixes ([[وَ فَ بِ لِ كَ]], l'article) et les suffixes (pronoms, terminaisons de pluriel).</li>
<li>Retirer les lettres « d'augmentation », qui servent à former les schèmes. Elles tiennent dans le mot mnémotechnique [[سَأَلْتُمُونِيهَا]] : <b>س ء ل ت م و ن ي ه ا</b>.</li>
<li>Il reste trois consonnes : c'est la racine. Exemple : [[ٱلْمُسْتَقِيمَ]] → on retire [[ٱلْ]], [[مُ]], [[سْتَ]] et le yāʾ de prolongation : <b>ق و م</b> (idée de <i>se tenir debout, droit</i>).</li>
</ol>
<div class="attention"><span class="lab">Piège</span>Une lettre d'augmentation peut aussi être radicale : dans [[عَلِمَ]] le mīm est la 3<sup>e</sup> radicale. On ne retire une lettre que si elle sert au schème. Avec l'habitude, on « voit » la racine immédiatement.</div>
""",
    fiche=dict(
        titre='Nom, verbe, particule ; racine', ar='أَقْسَامُ الْكَلِمَةِ',
        corps=r"""
<table class="t">
<tr><th>espèce</th><th>se reconnaît à…</th></tr>
<tr><td><b>nom</b> (ism)</td><td>article [[ٱلْ]], tanwīn, place après une préposition, apostrophe</td></tr>
<tr><td><b>verbe</b> (fiʿl)</td><td>[[قَدْ]], [[سَـ]], [[سَوْفَ]], [[لَمْ]] devant ; terminaisons [[ـتُ]], [[ـتْ]]…</td></tr>
<tr><td><b>particule</b> (ḥarf)</td><td>aucune de ces marques ; sens seulement avec d'autres mots</td></tr>
</table>
<ul>
<li><b>Racine</b> : 3 consonnes porteuses du sens (ع ل م = savoir).</li>
<li><b>Schème</b> : moule noté avec ف ع ل : [[فَاعِل]] celui qui fait, [[مَفْعُول]] ce qui subit, [[فَعِيل]] qualité.</li>
<li><b>Lettres d'augmentation</b> : [[سَأَلْتُمُونِيهَا]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Nom, verbe ou particule ?", items=[
            ('[[قَالَ]]', 'verbe'), ('[[فِى]]', 'particule'), ('[[ٱلْكِتَٰبُ]]', 'nom (article)'), ('[[يَعْلَمُ]]', 'verbe'),
            ('[[مِنْ]]', 'particule'), ('[[رَحِيمٌ]]', 'nom (tanwīn)'), ('[[قَدْ]]', 'particule'), ('[[عَلِمْتُ]]', 'verbe (ـتُ « je »)'),
        ]),
        dict(consigne="Donne le schème de chaque mot (avec ف ع ل).", items=[
            ('[[كَاتِب]]', '[[فَاعِل]]'), ('[[مَكْتُوب]]', '[[مَفْعُول]]'), ('[[عَلِيم]]', '[[فَعِيل]]'),
            ('[[كِتَاب]]', '[[فِعَال]]'), ('[[رَحْمَٰن]]', '[[فَعْلَان]]'), ('[[أَكْبَر]]', '[[أَفْعَل]]'),
        ]),
        dict(auto='racine', refs=[(2, 21, 22)], n=10),
    ],
    flash=[
        ("Nomme les trois espèces de mots.", "nom (ism), verbe (fiʿl), particule (ḥarf)"),
        ("Racine de [[عِلْم]] ?", "ع ل م"),
        ("Schème de [[رَحِيم]] ?", "[[فَعِيل]]"),
        ("Mot qui rassemble les lettres d'augmentation ?", "[[سَأَلْتُمُونِيهَا]]"),
        ("Cite deux marques du verbe.", "[[قَدْ]], [[سَـ]], [[لَمْ]], terminaison [[ـتُ]]…"),
        ("Que signifie le schème [[فَاعِل]] ?", "celui qui fait l'action"),
    ],
    notes={
        (103, 1): "[[وَ]] introduit ici un <b>serment</b> : « Par le Temps ! » (L39).",
        (108, 1): "[[إِنَّآ]] = <i>inna</i> + <i>nā</i> « certes Nous » : Allah parle de Lui au pluriel de majesté.",
        (108, 3): "[[شَانِئَكَ]] « celui qui te hait » (schème [[فَاعِل]]) ; [[هُوَ]] renforce : c'est <b>lui</b> le privé de postérité.",
    },
)

L[4] = dict(
    objectifs=[
        "distinguer le nom défini du nom indéfini",
        "employer l'article al- devant les lettres solaires et lunaires",
        "connaître les cinq façons d'être défini",
    ],
    expose=r"""
<p>Un nom arabe est soit <b>indéfini</b> [[نَكِرَة]] (« un livre »), soit <b>défini</b> [[مَعْرِفَة]] (« le livre »). La différence ne se fait pas avec un mot séparé, comme en français, mais avec des marques sur le nom lui-même.</p>
<h3><span class="pastille">1</span>Le tanwīn : l'indéfini</h3>
<p>Le nom indéfini porte le <b>tanwīn</b> : [[كِتَابٌ]] <i>kitābun</i> « un livre », [[رَحْمَةٌ]] « une miséricorde ». Le français traduit par <i>un, une, des</i>, ou sans article : [[خَيْرٌ]] « (un) bien, meilleur ».</p>
{{ex 97:3|hl=خير,شهر|com=[[خَيْرٌ]] et [[شَهْرٍ]] portent le tanwīn : « meilleure que mille <b>mois</b> ».}}
<h3><span class="pastille">2</span>L'article : le défini</h3>
<p>L'article [[ٱلْ]] (<i>al-</i>) se soude au nom, qui <b>perd alors son tanwīn</b> : [[كِتَابٌ]] → [[ٱلْكِتَابُ]] <i>al-kitābu</i>. Un nom n'a jamais à la fois l'article et le tanwīn. L'article est invariable (masculin, féminin, singulier, pluriel).</p>
<p>Rappel (L2) : devant une <b>lettre solaire</b>, le l ne se prononce pas et la lettre est doublée : [[ٱلشَّمْسُ]] <i>ash-shamsu</i>, [[ٱلنَّاسُ]] <i>an-nāsu</i>. Devant une <b>lettre lunaire</b>, le l se prononce : [[ٱلْقَمَرُ]] <i>al-qamaru</i>, [[ٱلْكِتَابُ]].</p>
<table class="t">
<tr><th>lettres lunaires (l prononcé)</th><th>lettres solaires (l assimilé)</th></tr>
<tr><td class="ar">ء ب ج ح خ ع غ ف ق ك م ه و ي</td><td class="ar">ت ث د ذ ر ز س ش ص ض ط ظ ل ن</td></tr>
</table>
{{ex 97:1|hl=القدر|com=[[ٱلْقَدْرِ]] : nom défini par l'article (qāf lunaire : <i>al-qadr</i>).}}
<h3><span class="pastille">3</span>Les autres noms définis</h3>
<p>Sont aussi définis, sans article :</p>
<ul>
<li>les <b>noms propres</b> : [[ٱللَّه]], [[مُوسَىٰ]], [[مَكَّة]] ;</li>
<li>les <b>pronoms</b> : [[هُوَ]] « lui », [[أَنْتَ]] « toi » (L11) ;</li>
<li>les <b>démonstratifs</b> et les <b>relatifs</b> : [[هَٰذَا]], [[ٱلَّذِى]] (L16–17) ;</li>
<li>le nom <b>annexé</b> à un nom défini ou à un pronom : [[لَيْلَةُ ٱلْقَدْرِ]] « la nuit du Destin », [[رَبُّكَ]] « ton Seigneur » (L13).</li>
</ul>
{{ex 97:2|hl=ليلة,القدر|com=[[لَيْلَةُ]] n'a ni article ni tanwīn : elle est définie par le nom qui la suit.}}
<div class="encadre"><span class="lab">À retenir</span>Article ou tanwīn : jamais les deux. Un nom sans article ni tanwīn est généralement soit un nom propre, soit un nom annexé.</div>
""",
    fiche=dict(
        titre='Défini et indéfini', ar='الْمَعْرِفَةُ وَالنَّكِرَةُ',
        corps=r"""
<ul>
<li><b>Indéfini</b> : tanwīn — [[كِتَابٌ]] un livre.</li>
<li><b>Défini</b> par l'article [[ٱلْ]], qui chasse le tanwīn — [[ٱلْكِتَابُ]] le livre.</li>
<li>Autres définis : nom propre, pronom, démonstratif, relatif, nom annexé à un défini.</li>
</ul>
<table class="t">
<tr><th>lunaires : <i>al-</i> prononcé</th><th>solaires : lettre doublée</th></tr>
<tr><td class="ar">ء ب ج ح خ ع غ ف ق ك م ه و ي</td><td class="ar">ت ث د ذ ر ز س ش ص ض ط ظ ل ن</td></tr>
</table>""",
    ),
    exercices=[
        dict(consigne="Ajoute l'article et lis le mot obtenu. La lettre est-elle solaire ou lunaire ?", items=[
            ('[[كِتَابٌ]]', '[[ٱلْكِتَابُ]] <i>al-kitābu</i> — lunaire'), ('[[شَمْسٌ]]', '[[ٱلشَّمْسُ]] <i>ash-shamsu</i> — solaire'),
            ('[[قَمَرٌ]]', '[[ٱلْقَمَرُ]] <i>al-qamaru</i> — lunaire'), ('[[نُورٌ]]', '[[ٱلنُّورُ]] <i>an-nūru</i> — solaire'),
            ('[[رَحْمَةٌ]]', '[[ٱلرَّحْمَةُ]] <i>ar-raḥmatu</i> — solaire'), ('[[دِينٌ]]', '[[ٱلدِّينُ]] <i>ad-dīnu</i> — solaire'),
            ('[[أَرْضٌ]]', '[[ٱلْأَرْضُ]] <i>al-arḍu</i> — lunaire'), ('[[جَنَّةٌ]]', '[[ٱلْجَنَّةُ]] <i>al-jannatu</i> — lunaire'),
        ]),
        dict(auto='defini', refs=[(2, 21, 25)], n=10),
    ],
    flash=[
        ("Un nom peut-il porter l'article et le tanwīn ?", "non, jamais les deux"),
        ("Comment se lit [[ٱلشَّمْسُ]] ?", "<i>ash-shamsu</i> (lettre solaire)"),
        ("[[لَيْلَةُ ٱلْقَدْرِ]] : pourquoi [[لَيْلَةُ]] est-il défini ?", "il est annexé à un nom défini"),
        ("Le qāf est-il solaire ou lunaire ?", "lunaire : <i>al-qamar</i>"),
        ("Cite trois sortes de noms définis sans article.", "nom propre, pronom, nom annexé (aussi démonstratif, relatif)"),
    ],
    notes={
        (97, 1): "[[أَنزَلْنَٰهُ]] « Nous l'avons fait descendre » : le pronom <i>hu</i> désigne le Coran.",
        (97, 4): "[[تَنَزَّلُ]] = <i>tatanazzalu</i> « descendent » ; un des deux <i>ta-</i> est tombé (forme V, L28).",
        (97, 5): "[[سَلَٰمٌ هِىَ]] « elle est paix » : phrase nominale dont l'attribut est placé en tête (L15).",
    },
)

L[5] = dict(
    objectifs=[
        "reconnaître le féminin à ses marques",
        "connaître les féminins sans marque les plus fréquents",
        "former le féminin d'un adjectif",
    ],
    expose=r"""
<p>Tout nom arabe est <b>masculin</b> [[مُذَكَّر]] ou <b>féminin</b> [[مُؤَنَّث]]. Le masculin n'a pas de marque ; le féminin en a souvent une. Le genre commande l'accord des adjectifs, des pronoms et des verbes : il faut donc le repérer tout de suite.</p>
<h3><span class="pastille">1</span>Les trois marques du féminin</h3>
<table class="t">
<tr><th>marque</th><th>lecture</th><th>exemples</th></tr>
<tr><td class="ar">ـَة (tāʾ marbūṭa)</td><td>-a, -at</td><td>[[جَنَّة]] jardin, [[رَحْمَة]] miséricorde, [[نِعْمَة]] bienfait, [[صَلَوٰة]] prière</td></tr>
<tr><td class="ar">ـَى (alif maqṣūra)</td><td>-ā</td><td>[[ذِكْرَى]] rappel, [[أُنثَى]] femelle, [[ٱلْكُبْرَى]] la plus grande</td></tr>
<tr><td class="ar">ـَاء (alif mamdūda)</td><td>-āʾ</td><td>[[حَمْرَاء]] rouge (f.), [[بَيْضَاء]] blanche</td></tr>
</table>
<p>La tāʾ marbūṭa est de loin la plus fréquente. Elle se lit <i>a</i> à la pause et <i>at</i> devant un mot qui suit : [[نِعْمَةَ ٱللَّهِ]] <i>niʿmata llāhi</i>.</p>
<h3><span class="pastille">2</span>Féminins sans marque</h3>
<p>Certains noms sont féminins sans marque :</p>
<ul>
<li>par nature : [[أُمّ]] mère, [[بِنْت]] fille ;</li>
<li>par usage, à apprendre : [[أَرْض]] terre, [[شَمْس]] soleil, [[نَفْس]] âme, [[نَار]] feu, [[رِيح]] vent, [[يَد]] main, [[عَيْن]] œil, source, [[دَار]] demeure, [[سَمَاء]] ciel, [[جَهَنَّم]] la Géhenne. Les parties doubles du corps sont en général féminines.</li>
</ul>
{{ex 91:1|hl=والشمس,وضحاها|com=Le pronom [[هَا]] de [[ضُحَىٰهَا]] (« sa clarté ») renvoie au soleil : [[شَمْس]] est féminin.}}
{{ex 91:7|hl=ونفس|com=[[نَفْس]] « âme » est féminin : d'où [[سَوَّىٰهَا]] « l'a harmonisée » (pronom féminin).}}
<h3><span class="pastille">3</span>Former le féminin</h3>
<p>La plupart des adjectifs et participes forment leur féminin avec [[ـَة]] :</p>
<table class="t c">
<tr><th>masculin</th><th>féminin</th><th>sens</th></tr>
<tr><td class="ar">مُؤْمِن</td><td class="ar">مُؤْمِنَة</td><td>croyant(e)</td></tr>
<tr><td class="ar">صَالِح</td><td class="ar">صَالِحَة</td><td>vertueux, -euse</td></tr>
<tr><td class="ar">كَرِيم</td><td class="ar">كَرِيمَة</td><td>noble</td></tr>
<tr><td class="ar">عَظِيم</td><td class="ar">عَظِيمَة</td><td>immense</td></tr>
</table>
<p>Les adjectifs du schème [[أَفْعَل]] font leur féminin en [[فُعْلَى]] : [[أَكْبَر]] → [[كُبْرَى]], [[أَعْلَى]] → [[عُلْيَا]] (L40).</p>
<div class="attention"><span class="lab">Exception utile</span>Quelques noms en [[ة]] désignent des hommes et restent masculins : [[خَلِيفَة]] successeur (2:30). Inversement, certains adjectifs propres aux femmes n'ont pas de [[ة]] : [[عَاقِر]] stérile (19:5).</div>
""",
    fiche=dict(
        titre='Le genre', ar='الْمُذَكَّرُ وَالْمُؤَنَّثُ',
        corps=r"""
<ul>
<li>Masculin : sans marque. Féminin : [[ـَة]] (le plus souvent), [[ـَى]], [[ـَاء]].</li>
<li>Féminins sans marque : [[أَرْض]], [[شَمْس]], [[نَفْس]], [[نَار]], [[رِيح]], [[يَد]], [[عَيْن]], [[دَار]], [[سَمَاء]], [[جَهَنَّم]], [[أُمّ]].</li>
<li>Féminin d'un adjectif : + [[ة]] ([[صَالِح]] → [[صَالِحَة]]) ; [[أَفْعَل]] → [[فُعْلَى]].</li>
<li>Le genre commande l'accord : pronom, adjectif, verbe.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Forme le féminin.", items=[
            ('[[مُؤْمِن]]', '[[مُؤْمِنَة]]'), ('[[كَافِر]]', '[[كَافِرَة]]'), ('[[صَادِق]]', '[[صَادِقَة]]'),
            ('[[عَالِم]]', '[[عَالِمَة]]'), ('[[كَبِير]]', '[[كَبِيرَة]]'), ('[[قَرِيب]]', '[[قَرِيبَة]]'),
        ]),
        dict(consigne="Masculin ou féminin ?", items=[
            ('[[أَرْض]]', 'féminin (sans marque)'), ('[[قَلْب]]', 'masculin'), ('[[نَار]]', 'féminin (sans marque)'),
            ('[[ذِكْرَى]]', 'féminin (ـَى)'), ('[[قَمَر]]', 'masculin'), ('[[رَحْمَة]]', 'féminin (ة)'),
            ('[[نَفْس]]', 'féminin (sans marque)'), ('[[كِتَاب]]', 'masculin'),
        ]),
        dict(auto='genre_nombre', refs=[(89, 15, 20)], n=8, consigne="Donne le genre (et, si tu le peux déjà, le nombre) de chaque nom."),
    ],
    flash=[
        ("Quelle est la marque la plus fréquente du féminin ?", "la tāʾ marbūṭa [[ـَة]]"),
        ("[[شَمْس]] est-il masculin ou féminin ?", "féminin (sans marque)"),
        ("Féminin de [[صَالِح]] ?", "[[صَالِحَة]]"),
        ("Comment se lit [[ة]] devant un mot qui suit ?", "<i>-at</i> : [[نِعْمَةَ ٱللَّهِ]] <i>niʿmata llāh</i>"),
        ("Féminin de [[أَكْبَر]] ?", "[[كُبْرَى]]"),
    ],
    notes={
        (91, 5): "[[وَمَا بَنَىٰهَا]] : « et par Celui qui l'a édifié » ; [[مَا]] est ici relatif (L17).",
        (91, 9): "[[قَدْ أَفْلَحَ]] : <i>qad</i> + accompli = « a certes réussi » (L25). C'est la réponse aux serments.",
    },
)

L[6] = dict(
    objectifs=[
        "former et reconnaître le duel",
        "former le pluriel externe masculin et féminin",
        "savoir à quels noms s'appliquent ces pluriels",
    ],
    expose=r"""
<p>L'arabe a trois nombres : <b>singulier</b>, <b>duel</b> (exactement deux) et <b>pluriel</b> (trois et plus). Cette leçon présente le duel et les pluriels « externes » (ou « sains »), formés par une terminaison ajoutée au singulier sans le modifier.</p>
<h3><span class="pastille">1</span>Le duel</h3>
<p>On ajoute <b>[[ـَانِ]]</b> (<i>-āni</i>) au sujet, <b>[[ـَيْنِ]]</b> (<i>-ayni</i>) en dehors du sujet (le détail des cas est en L9). Un [[ة]] final devient [[ت]] :</p>
<table class="t c">
<tr><th>singulier</th><th>duel (sujet)</th><th>duel (autres cas)</th><th>sens</th></tr>
<tr><td class="ar">بَحْر</td><td class="ar">بَحْرَانِ</td><td class="ar">بَحْرَيْنِ</td><td>deux mers</td></tr>
<tr><td class="ar">جَنَّة</td><td class="ar">جَنَّتَانِ</td><td class="ar">جَنَّتَيْنِ</td><td>deux jardins</td></tr>
<tr><td class="ar">عَيْن</td><td class="ar">عَيْنَانِ</td><td class="ar">عَيْنَيْنِ</td><td>deux yeux</td></tr>
</table>
{{ex 55:17|hl=المشرقين,المغربين|com=« le Seigneur des deux Levants et des deux Couchants » : duel en <i>-ayn</i>.}}
<p>Le verbe et le pronom ont aussi un duel : [[يَلْتَقِيَانِ]] « (les deux mers) se rencontrent », [[بَيْنَهُمَا]] « entre les deux ».</p>
{{ex 55:19|hl=البحرين,يلتقيان}}
<h3><span class="pastille">2</span>Le pluriel externe masculin</h3>
<p>Il s'emploie pour des <b>êtres humains masculins</b> désignés par un participe ou un adjectif. On ajoute <b>[[ـُونَ]]</b> (<i>-ūna</i>) au sujet, <b>[[ـِينَ]]</b> (<i>-īna</i>) aux autres cas :</p>
<table class="t c">
<tr><th>singulier</th><th>sujet</th><th>autres cas</th><th>sens</th></tr>
<tr><td class="ar">مُؤْمِن</td><td class="ar">مُؤْمِنُونَ</td><td class="ar">مُؤْمِنِينَ</td><td>croyants</td></tr>
<tr><td class="ar">خَاشِع</td><td class="ar">خَاشِعُونَ</td><td class="ar">خَاشِعِينَ</td><td>humbles, recueillis</td></tr>
<tr><td class="ar">صَالِح</td><td class="ar">صَالِحُونَ</td><td class="ar">صَالِحِينَ</td><td>vertueux</td></tr>
</table>
{{ex 23:1|hl=المؤمنون}}
{{ex 23:2|hl=خاشعون}}
<h3><span class="pastille">3</span>Le pluriel externe féminin</h3>
<p>On remplace [[ة]] par <b>[[ـَات]]</b> (<i>-āt</i>). Ce pluriel sert pour les femmes (adjectifs, participes) mais aussi pour <b>beaucoup de noms de choses</b> :</p>
<table class="t c">
<tr><th>singulier</th><th>pluriel</th><th>sens</th><th>singulier</th><th>pluriel</th><th>sens</th></tr>
<tr><td class="ar">مُؤْمِنَة</td><td class="ar">مُؤْمِنَات</td><td>croyantes</td><td class="ar">آيَة</td><td class="ar">آيَات</td><td>signes, versets</td></tr>
<tr><td class="ar">صَالِحَة</td><td class="ar">صَالِحَات</td><td>bonnes œuvres</td><td class="ar">جَنَّة</td><td class="ar">جَنَّات</td><td>jardins</td></tr>
<tr><td class="ar">سَمَاء</td><td class="ar">سَمَاوَات</td><td>cieux</td><td class="ar">ظُلْمَة</td><td class="ar">ظُلُمَات</td><td>ténèbres</td></tr>
</table>
<p>Dans le muṣḥaf, l'alif de [[ـَات]] est souvent écrit en alif suscrit : [[ٱلصَّٰلِحَٰتِ]], [[ٱلسَّمَٰوَٰتِ]].</p>
<div class="encadre"><span class="lab">À retenir</span>Duel <i>-āni / -ayni</i> ; pluriel masculin <i>-ūna / -īna</i> (hommes) ; pluriel féminin <i>-āt</i> (femmes et nombreux noms de choses). Les autres pluriels sont « internes » : c'est la leçon suivante.</div>
""",
    fiche=dict(
        titre='Duel et pluriels externes', ar='الْمُثَنَّى وَجَمْعُ السَّلَامَةِ',
        corps=r"""
<table class="t c">
<tr><th></th><th>sujet (nominatif)</th><th>autres cas</th><th>emploi</th></tr>
<tr><td>duel</td><td class="ar">ـَانِ</td><td class="ar">ـَيْنِ</td><td>exactement deux (ة → ت)</td></tr>
<tr><td>pluriel masc.</td><td class="ar">ـُونَ</td><td class="ar">ـِينَ</td><td>hommes (participes, adjectifs)</td></tr>
<tr><td>pluriel fém.</td><td class="ar">ـَاتٌ</td><td class="ar">ـَاتٍ</td><td>femmes et beaucoup de noms de choses (ة tombe)</td></tr>
</table>
<ul><li>Le verbe et le pronom ont aussi un duel : [[يَلْتَقِيَانِ]], [[هُمَا]].</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne le duel (au nominatif puis aux autres cas).", items=[
            ('[[كِتَاب]]', '[[كِتَابَانِ]] / [[كِتَابَيْنِ]]'), ('[[جَنَّة]]', '[[جَنَّتَانِ]] / [[جَنَّتَيْنِ]]'),
            ('[[رَسُول]]', '[[رَسُولَانِ]] / [[رَسُولَيْنِ]]'), ('[[بَاب]]', '[[بَابَانِ]] / [[بَابَيْنِ]]'),
        ]),
        dict(consigne="Donne le pluriel externe (au nominatif).", items=[
            ('[[مُؤْمِن]]', '[[مُؤْمِنُونَ]]'), ('[[صَالِح]]', '[[صَالِحُونَ]]'), ('[[مُسْلِمَة]]', '[[مُسْلِمَاتٌ]]'),
            ('[[آيَة]]', '[[آيَاتٌ]]'), ('[[كَافِر]]', '[[كَافِرُونَ]]'), ('[[صَادِق]]', '[[صَادِقُونَ]]'),
        ]),
        dict(auto='genre_nombre', refs=[(36, 1, 12)], n=10),
    ],
    flash=[
        ("Duel de [[جَنَّة]] (sujet) ?", "[[جَنَّتَانِ]]"),
        ("Terminaison du pluriel masculin hors sujet ?", "[[ـِينَ]] <i>-īna</i>"),
        ("À quels noms s'applique le pluriel en [[ـُونَ]] ?", "aux êtres humains masculins (participes, adjectifs)"),
        ("Pluriel de [[آيَة]] ?", "[[آيَات]]"),
        ("Que signifie [[ٱلْمَشْرِقَيْنِ]] ?", "les deux Levants (duel)"),
    ],
    notes={
        (23, 3): "[[عَنِ ٱللَّغْوِ مُعْرِضُونَ]] : le complément [[عَنِ ٱللَّغْوِ]] est placé avant l'adjectif pour insister.",
        (23, 6): "[[مَا مَلَكَتْ أَيْمَٰنُهُمْ]] « ce que possèdent leurs mains droites » : [[أَيْمَٰن]] est le pluriel interne de [[يَمِين]] (L7).",
        (55, 16): "Ce refrain revient 31 fois dans la sourate : [[تُكَذِّبَانِ]] est un verbe au duel (« vous deux », djinns et humains).",
    },
)

L[7] = dict(
    objectifs=[
        "reconnaître les pluriels internes (brisés)",
        "connaître les schèmes de pluriel les plus fréquents",
        "accorder correctement avec un pluriel de choses",
    ],
    expose=r"""
<p>La majorité des pluriels arabes ne se forment pas par une terminaison, mais en <b>modifiant l'intérieur du mot</b> : on garde la racine et l'on change le schème. On parle de pluriel « interne » ou « brisé » [[جَمْعُ ٱلتَّكْسِيرِ]]. Il faut l'apprendre avec chaque nom ; mais une dizaine de schèmes couvrent l'essentiel.</p>
<table class="t">
<tr><th class="ar">schème</th><th>exemples (singulier → pluriel)</th></tr>
<tr><td class="ar">أَفْعَال</td><td>[[زَوْج]] → [[أَزْوَاج]] · [[مَال]] → [[أَمْوَال]] · [[عَمَل]] → [[أَعْمَال]] · [[نَهَر]] → [[أَنْهَار]] · [[وَتِد]] → [[أَوْتَاد]]</td></tr>
<tr><td class="ar">فُعُول</td><td>[[قَلْب]] → [[قُلُوب]] · [[نَجْم]] → [[نُجُوم]] · [[صَدْر]] → [[صُدُور]] · [[وَجْه]] → [[وُجُوه]] · [[بَيْت]] → [[بُيُوت]]</td></tr>
<tr><td class="ar">فِعَال</td><td>[[جَبَل]] → [[جِبَال]] · [[رَجُل]] → [[رِجَال]] · [[عَبْد]] → [[عِبَاد]] · [[ثَوْب]] → [[ثِيَاب]] · [[دَار]] → [[دِيَار]]</td></tr>
<tr><td class="ar">فُعُل</td><td>[[رَسُول]] → [[رُسُل]] · [[كِتَاب]] → [[كُتُب]] · [[سَبِيل]] → [[سُبُل]] · [[صَحِيفَة]] → [[صُحُف]]</td></tr>
<tr><td class="ar">فُعَلَاء</td><td>[[شَرِيك]] → [[شُرَكَاء]] · [[شَهِيد]] → [[شُهَدَاء]] · [[عَالِم]] → [[عُلَمَاء]]</td></tr>
<tr><td class="ar">أَفْعِلَاء</td><td>[[وَلِيّ]] → [[أَوْلِيَاء]] · [[نَبِيّ]] → [[أَنْبِيَاء]]</td></tr>
<tr><td class="ar">أَفْعُل</td><td>[[نَفْس]] → [[أَنْفُس]] · [[عَيْن]] → [[أَعْيُن]]</td></tr>
<tr><td class="ar">فِعْلَة</td><td>[[أَخ]] → [[إِخْوَة]] · [[فَتًى]] → [[فِتْيَة]]</td></tr>
<tr><td class="ar">مَفَاعِل / مَفَاعِيل</td><td>[[مَسْجِد]] → [[مَسَاجِد]] · [[مِصْبَاح]] → [[مَصَابِيح]] · [[مِيزَان]] → [[مَوَازِين]]</td></tr>
<tr><td class="ar">فَعَائِل</td><td>[[قَبِيلَة]] → [[قَبَائِل]]</td></tr>
</table>
{{ex 78:7|hl=والجبال,أوتادا|com=[[جِبَال]] (schème [[فِعَال]]) et [[أَوْتَاد]] (schème [[أَفْعَال]]).}}
{{ex 78:8|hl=أزواجا|com=« Nous vous avons créés en <b>couples</b> » : [[أَزْوَاج]], pluriel de [[زَوْج]].}}

<h3><span class="pastille">1</span>L'accord avec un pluriel de choses</h3>
<p>Règle capitale : un pluriel interne qui désigne des <b>choses ou des animaux</b> s'accorde comme un <b>féminin singulier</b>. Le verbe, le pronom et l'adjectif sont au féminin singulier.</p>
{{ex 81:3|hl=الجبال,سيرت|com=« les montagnes <b>ont été mises</b> en marche » : verbe féminin singulier ([[ـَتْ]]) pour [[ٱلْجِبَالُ]].}}
{{ex 88:13|hl=سرر,مرفوعة|com=« des lits <b>élevés</b> » : adjectif féminin singulier [[مَرْفُوعَة]] pour le pluriel [[سُرُر]] (L14).}}
<p>Pour des êtres humains, l'accord se fait au pluriel, mais le féminin singulier reste possible : [[قَالَتِ ٱلْأَعْرَابُ]] « les Bédouins ont dit » (49:14).</p>
<div class="encadre"><span class="lab">Méthode</span>Devant un mot inconnu au schème « étrange », pense au pluriel interne : cherche la racine, puis le singulier dans le lexique. Le corpus du Coran classe d'ailleurs chaque pluriel sous son singulier.</div>
""",
    fiche=dict(
        titre='Les pluriels internes', ar='جَمْعُ التَّكْسِيرِ',
        corps=r"""
<table class="t">
<tr><th class="ar">schème</th><th>exemple</th><th class="ar">schème</th><th>exemple</th></tr>
<tr><td class="ar">أَفْعَال</td><td>[[زَوْج]] → [[أَزْوَاج]]</td><td class="ar">فُعَلَاء</td><td>[[شَرِيك]] → [[شُرَكَاء]]</td></tr>
<tr><td class="ar">فُعُول</td><td>[[قَلْب]] → [[قُلُوب]]</td><td class="ar">أَفْعِلَاء</td><td>[[وَلِيّ]] → [[أَوْلِيَاء]]</td></tr>
<tr><td class="ar">فِعَال</td><td>[[جَبَل]] → [[جِبَال]]</td><td class="ar">أَفْعُل</td><td>[[نَفْس]] → [[أَنْفُس]]</td></tr>
<tr><td class="ar">فُعُل</td><td>[[رَسُول]] → [[رُسُل]]</td><td class="ar">مَفَاعِل</td><td>[[مَسْجِد]] → [[مَسَاجِد]]</td></tr>
</table>
<ul><li><b>Accord</b> : pluriel de choses ou d'animaux → <b>féminin singulier</b> (verbe, pronom, adjectif). Pluriel d'êtres humains → pluriel (ou féminin singulier).</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne le singulier et le schème du pluriel.", items=[
            ('[[قُلُوب]]', '[[قَلْب]] — [[فُعُول]]'), ('[[جِبَال]]', '[[جَبَل]] — [[فِعَال]]'), ('[[أَزْوَاج]]', '[[زَوْج]] — [[أَفْعَال]]'),
            ('[[رُسُل]]', '[[رَسُول]] — [[فُعُل]]'), ('[[أَنْفُس]]', '[[نَفْس]] — [[أَفْعُل]]'), ('[[أَوْلِيَاء]]', '[[وَلِيّ]] — [[أَفْعِلَاء]]'),
            ('[[مَسَاجِد]]', '[[مَسْجِد]] — [[مَفَاعِل]]'), ('[[عِبَاد]]', '[[عَبْد]] — [[فِعَال]]'),
        ]),
        dict(consigne="Choisis l'accord correct.", items=[
            ('[[ٱلنُّجُومُ]] (… [[ٱنكَدَرَتْ]] / [[ٱنكَدَرُوا]])', '[[ٱنكَدَرَتْ]] : choses → féminin singulier (81:2)'),
            ('[[جَنَّاتٌ]] (… [[تَجْرِي]] / [[يَجْرُونَ]]) [[مِنْ تَحْتِهَا ٱلْأَنْهَارُ]]', '[[تَجْرِي]] (« des jardins sous lesquels coulent les rivières »)'),
            ('[[قُلُوبٌ]] (… [[وَاجِفَةٌ]] / [[وَاجِفُونَ]])', '[[وَاجِفَةٌ]] (79:8)'),
        ], une=True),
        dict(auto='genre_nombre', refs=[(78, 31, 36)], n=8),
    ],
    flash=[
        ("Pluriel de [[قَلْب]] ?", "[[قُلُوب]]"),
        ("Singulier de [[رُسُل]] ?", "[[رَسُول]]"),
        ("Comment s'accorde un pluriel de choses ?", "au féminin singulier"),
        ("Schème de [[أَزْوَاج]] ?", "[[أَفْعَال]]"),
        ("Pluriel de [[نَفْس]] ?", "[[أَنْفُس]] (aussi [[نُفُوس]])"),
    ],
    notes={
        (78, 9): "[[سُبَاتًا]] « repos » : accusatif, deuxième complément de [[جَعَلْنَا]] « Nous avons fait (votre sommeil) un repos » (L34).",
        (78, 16): "[[أَلْفَافًا]] « touffus » : adjectif au pluriel accordé avec [[جَنَّٰتٍ]].",
    },
)

L[8] = dict(
    objectifs=[
        "connaître les trois cas et leurs marques de base",
        "savoir à quoi sert chaque cas",
        "distinguer les mots déclinables et indéclinables",
    ],
    expose=r"""
<p>En arabe, la fonction d'un nom dans la phrase se lit sur sa <b>terminaison</b>. C'est la flexion casuelle, ou <b>iʿrāb</b> [[إِعْرَاب]]. Il y a trois cas pour le nom :</p>
<table class="t c">
<tr><th>cas</th><th>nom arabe</th><th>marque (défini)</th><th>marque (indéfini)</th><th>exemple</th></tr>
<tr><td>nominatif</td><td>marfūʿ [[مَرْفُوع]]</td><td class="ar">ـُ</td><td class="ar">ـٌ</td><td class="ar">ٱلْكِتَابُ · كِتَابٌ</td></tr>
<tr><td>accusatif</td><td>manṣūb [[مَنْصُوب]]</td><td class="ar">ـَ</td><td class="ar">ـًا</td><td class="ar">ٱلْكِتَابَ · كِتَابًا</td></tr>
<tr><td>génitif</td><td>majrūr [[مَجْرُور]]</td><td class="ar">ـِ</td><td class="ar">ـٍ</td><td class="ar">ٱلْكِتَابِ · كِتَابٍ</td></tr>
</table>
<h3><span class="pastille">1</span>À quoi servent les cas ?</h3>
<ul>
<li><b>Nominatif</b> : le sujet du verbe (L33), le sujet et l'attribut de la phrase nominale (L15).</li>
<li><b>Accusatif</b> : le complément d'objet (L34), le nom de [[إِنَّ]] (L19), l'attribut de [[كَانَ]] (L20), les compléments de temps, de lieu, de manière, l'état (L35–36).</li>
<li><b>Génitif</b> : après une préposition (L10) et comme complément du nom dans l'annexion (L13).</li>
</ul>
{{ex 95:4|hl=الإنسان,أحسن,تقويم|com=[[ٱلْإِنسَٰنَ]] accusatif (objet de « Nous avons créé ») ; [[أَحْسَنِ]] génitif (après [[فِىٓ]]) ; [[تَقْوِيمٍ]] génitif (complément du nom).}}
{{ex 95:6|hl=أجر,غير,ممنون|com=[[أَجْرٌ]] nominatif (sujet), [[غَيْرُ]] nominatif (il qualifie [[أَجْرٌ]]), [[مَمْنُونٍ]] génitif.}}
<h3><span class="pastille">2</span>Déclinable et indéclinable</h3>
<p>Seuls les <b>noms</b> (et l'inaccompli, L22) changent de terminaison : ils sont <b>déclinables</b> [[مُعْرَب]]. Les particules, les verbes à l'accompli, les pronoms, les démonstratifs et la plupart des relatifs ont une terminaison fixe : ils sont <b>indéclinables</b> [[مَبْنِيّ]]. On dit alors qu'ils occupent la place d'un cas (« en position de nominatif », etc.).</p>
<h3><span class="pastille">3</span>Quand la marque ne se voit pas</h3>
<ul>
<li>Les noms terminés par [[ـَى]] ou [[ـًى]] (alif maqṣūra) ne montrent pas leur cas : [[هُدًى]], [[مُوسَىٰ]]. Le cas est « virtuel » (<i>muqaddar</i>).</li>
<li>À la pause, la voyelle finale tombe : le cas ne s'entend plus, mais il s'écrit.</li>
</ul>
<div class="encadre"><span class="lab">Le bon réflexe</span>Devant un nom, regarde sa dernière voyelle : <b>u</b> → nominatif, <b>a</b> → accusatif, <b>i</b> → génitif. Puis cherche pourquoi : préposition devant ? verbe dont il est sujet ou objet ? Les leçons suivantes donnent toutes les raisons.</div>
""",
    fiche=dict(
        titre='Les trois cas', ar='الْإِعْرَابُ',
        corps=r"""
<table class="t c">
<tr><th>cas</th><th>défini</th><th>indéfini</th><th>emplois principaux</th></tr>
<tr><td>nominatif (marfūʿ)</td><td class="ar">ـُ</td><td class="ar">ـٌ</td><td>sujet ; mubtadaʾ et khabar</td></tr>
<tr><td>accusatif (manṣūb)</td><td class="ar">ـَ</td><td class="ar">ـًا</td><td>objet ; nom de inna ; attribut de kāna ; compléments, état</td></tr>
<tr><td>génitif (majrūr)</td><td class="ar">ـِ</td><td class="ar">ـٍ</td><td>après préposition ; complément du nom</td></tr>
</table>
<ul><li>Indéclinables (mabnī) : particules, accompli, pronoms, démonstratifs, relatifs.</li><li>Noms en [[ـَى]] : cas invisible.</li></ul>""",
    ),
    exercices=[
        dict(consigne="Écris le nom aux trois cas, défini puis indéfini.", items=[
            ('[[كِتَاب]]', '[[ٱلْكِتَابُ / ٱلْكِتَابَ / ٱلْكِتَابِ]] — [[كِتَابٌ / كِتَابًا / كِتَابٍ]]'),
            ('[[رَسُول]]', '[[ٱلرَّسُولُ / ٱلرَّسُولَ / ٱلرَّسُولِ]] — [[رَسُولٌ / رَسُولًا / رَسُولٍ]]'),
            ('[[رَحْمَة]]', '[[ٱلرَّحْمَةُ / ٱلرَّحْمَةَ / ٱلرَّحْمَةِ]] — [[رَحْمَةٌ / رَحْمَةً / رَحْمَةٍ]]'),
        ], une=True),
        dict(auto='cas', refs=[(2, 21, 22)], n=10),
        dict(auto='cas', refs=[(96, 9, 19)], n=8, consigne="Même exercice sur la fin de la sourate al-ʿAlaq."),
    ],
    flash=[
        ("Marque du génitif indéfini ?", "[[ـٍ]] (<i>-in</i>)"),
        ("Après une préposition, quel cas ?", "le génitif"),
        ("Nom arabe de l'accusatif ?", "<i>manṣūb</i>"),
        ("Pourquoi [[هُدًى]] ne montre-t-il pas son cas ?", "il se termine par un alif maqṣūra : cas virtuel"),
        ("Un verbe à l'accompli se décline-t-il ?", "non, il est indéclinable (mabnī)"),
    ],
    notes={
        (95, 1): "[[وَٱلتِّينِ]] : génitif après le <i>wāw</i> du serment (L39).",
        (95, 8): "[[أَلَيْسَ]] = [[أَ]] interrogatif + [[لَيْسَ]] « n'est-il pas ? » (L18, L20). [[بِأَحْكَمِ]] : le [[بِ]] renforce l'attribut de <i>laysa</i>.",
    },
)

L[9] = dict(
    objectifs=[
        "reconnaître les cas au duel et aux pluriels externes",
        "connaître le diptote (nom qui refuse le tanwīn)",
        "décliner les « cinq noms » (ab, akh, dhū…)",
    ],
    expose=r"""
<p>Les marques de base (u, a, i) ont des remplaçants dans trois cas : le duel et les pluriels externes, le diptote, et les « cinq noms ». Ces marques « secondaires » sont très fréquentes dans le Coran.</p>
<h3><span class="pastille">1</span>Duel et pluriel externe masculin</h3>
<p>Ils n'ont que <b>deux formes</b> : une pour le nominatif, une pour l'accusatif et le génitif.</p>
<table class="t c">
<tr><th></th><th>nominatif</th><th>accusatif = génitif</th></tr>
<tr><td>duel</td><td class="ar">ـَانِ</td><td class="ar">ـَيْنِ</td></tr>
<tr><td>pluriel masculin</td><td class="ar">ـُونَ</td><td class="ar">ـِينَ</td></tr>
</table>
{{ex 83:28|hl=المقربون|com=[[ٱلْمُقَرَّبُونَ]] : nominatif (sujet de [[يَشْرَبُ]]).}}
{{ex 83:18|hl=عليين|com=[[عِلِّيِّينَ]] : génitif (après [[فِى]]) en <i>-īna</i>.}}
<h3><span class="pastille">2</span>Pluriel externe féminin</h3>
<p>Le pluriel en [[ـَات]] fait son accusatif <b>avec une kasra</b>, comme le génitif : [[خَلَقَ ٱلسَّمَٰوَٰتِ]] « Il a créé les cieux » (accusatif en <i>-i</i>).</p>
{{ex 6:1|hl=السماوات,الظلمات|com=[[ٱلسَّمَٰوَٰتِ]] et [[ٱلظُّلُمَٰتِ]] sont des compléments d'objet : accusatif marqué par la kasra.}}
<h3><span class="pastille">3</span>Le diptote</h3>
<p>Certains noms <b>refusent le tanwīn</b> et font leur génitif en <b>-a</b> (tant qu'ils n'ont ni article ni complément) : on les appelle diptotes [[مَمْنُوعٌ مِنَ ٱلصَّرْفِ]]. Ce sont surtout :</p>
<ul>
<li>la plupart des noms propres étrangers ou féminins : [[إِبْرَاهِيمَ]], [[مُوسَىٰ]], [[فِرْعَوْنَ]], [[مَرْيَمَ]] ;</li>
<li>les pluriels des schèmes [[مَفَاعِل]], [[مَفَاعِيل]], [[فُعَلَاء]], [[أَفْعِلَاء]] : [[مَسَاجِدَ]], [[مَصَابِيحَ]], [[أَوْلِيَاءَ]] ;</li>
<li>les adjectifs [[أَفْعَل]] et les noms en [[ـَاء]], [[ـَى]] du féminin.</li>
</ul>
{{ex 67:5|hl=بمصابيح|com=[[بِمَصَٰبِيحَ]] : génitif après [[بِ]], mais avec une fatḥa et sans tanwīn.}}
{{ex 79:17|hl=فرعون|com=[[فِرْعَوْنَ]] après [[إِلَىٰ]] : génitif en <i>-a</i>.}}
<h3><span class="pastille">4</span>Les cinq noms</h3>
<p>[[أَب]] père, [[أَخ]] frère, [[ذُو]] possesseur de, [[فُو]] bouche, [[حَم]] beau-père allongent leur voyelle quand ils sont annexés :</p>
<table class="t c">
<tr><th>nominatif</th><th>accusatif</th><th>génitif</th><th>exemple</th></tr>
<tr><td class="ar">أَبُو / ذُو</td><td class="ar">أَبَا / ذَا</td><td class="ar">أَبِي / ذِي</td><td>[[مَا كَانَ أَبُوكِ]] (19:28), [[لِأَبِيهِ]] (12:4)</td></tr>
</table>
""",
    fiche=dict(
        titre='Marques secondaires des cas', ar='الْعَلَامَاتُ الْفَرْعِيَّةُ',
        corps=r"""
<table class="t c">
<tr><th></th><th>nominatif</th><th>accusatif</th><th>génitif</th></tr>
<tr><td>duel</td><td class="ar">ـَانِ</td><td class="ar">ـَيْنِ</td><td class="ar">ـَيْنِ</td></tr>
<tr><td>pluriel masc.</td><td class="ar">ـُونَ</td><td class="ar">ـِينَ</td><td class="ar">ـِينَ</td></tr>
<tr><td>pluriel fém.</td><td class="ar">ـَاتُ / ـَاتٌ</td><td class="ar">ـَاتِ / ـَاتٍ</td><td class="ar">ـَاتِ / ـَاتٍ</td></tr>
<tr><td>diptote</td><td class="ar">ـُ</td><td class="ar">ـَ</td><td class="ar">ـَ (sans article ni annexion)</td></tr>
<tr><td>cinq noms annexés</td><td class="ar">ـُو</td><td class="ar">ـَا</td><td class="ar">ـِي</td></tr>
</table>
<ul><li>Diptotes : noms propres étrangers ou féminins, pluriels [[مَفَاعِل]]/[[مَفَاعِيل]]/[[فُعَلَاء]], adjectifs [[أَفْعَل]].</li></ul>""",
    ),
    exercices=[
        dict(consigne="Choisis la forme correcte.", items=[
            ('[[إِنَّ ٱللَّهَ يُحِبُّ]] (… [[ٱلْمُحْسِنُونَ]] / [[ٱلْمُحْسِنِينَ]])', '[[ٱلْمُحْسِنِينَ]] : objet → accusatif en <i>-īna</i>'),
            ('[[قَدْ أَفْلَحَ]] (… [[ٱلْمُؤْمِنُونَ]] / [[ٱلْمُؤْمِنِينَ]])', '[[ٱلْمُؤْمِنُونَ]] : sujet → nominatif'),
            ('[[خَلَقَ ٱللَّهُ]] (… [[ٱلسَّمَاوَاتَ]] / [[ٱلسَّمَاوَاتِ]])', '[[ٱلسَّمَاوَاتِ]] : accusatif du pluriel féminin avec kasra'),
            ('[[فِي]] (… [[مَسَاجِدٍ]] / [[مَسَاجِدَ]])', '[[مَسَاجِدَ]] : diptote, génitif en <i>-a</i> sans tanwīn'),
            ('[[قَالَ]] (… [[أَبُوهُمْ]] / [[أَبَاهُمْ]])', '[[أَبُوهُمْ]] : sujet, cinq noms → <i>-ū</i>'),
        ], une=True),
        dict(auto='cas', refs=[(55, 46, 54)], n=10, consigne="Donne le cas de chaque mot (attention aux duels)."),
    ],
    flash=[
        ("Accusatif du pluriel en [[ـَات]] ?", "avec une kasra : [[ٱلسَّمَٰوَٰتِ]]"),
        ("Qu'est-ce qu'un diptote ?", "un nom sans tanwīn, au génitif en <i>-a</i>"),
        ("Génitif de [[أَبُوهُ]] ?", "[[أَبِيهِ]]"),
        ("Duel à l'accusatif ?", "[[ـَيْنِ]]"),
        ("[[إِبْرَاهِيم]] prend-il le tanwīn ?", "non (diptote)"),
    ],
    notes={
        (83, 22): "[[إِنَّ ٱلْأَبْرَارَ لَفِى نَعِيمٍ]] : [[ٱلْأَبْرَارَ]] accusatif après [[إِنَّ]] (L19) ; c'est un pluriel interne de [[بَرّ]].",
        (83, 26): "[[فَلْيَتَنَافَسِ]] « qu'ils rivalisent » : lām d'injonction + apocopé (L24).",
    },
)

L[10] = dict(
    objectifs=[
        "connaître le sens des prépositions principales",
        "les unir aux pronoms et à [[مَا]] / [[مَنْ]]",
        "reconnaître le groupe prépositionnel (shibh jumla)",
    ],
    expose=r"""
<p>Une <b>préposition</b> [[حَرْفُ جَرٍّ]] met toujours le nom qui la suit au <b>génitif</b>. Elle a un sens propre, que le contexte précise.</p>
<table class="t">
<tr><th class="ar">préposition</th><th>sens principaux</th><th>exemple</th></tr>
<tr><td class="ar">بِـ</td><td>par, avec, au moyen de ; dans</td><td>[[بِٱلْقَلَمِ]] par le calame</td></tr>
<tr><td class="ar">لِـ</td><td>à, pour ; appartenance (« avoir »)</td><td>[[لِلَّهِ]] à Allah</td></tr>
<tr><td class="ar">كَـ</td><td>comme</td><td>[[كَٱلْفَرَاشِ]] comme des papillons</td></tr>
<tr><td class="ar">مِنْ</td><td>de, depuis ; parmi ; une partie de</td><td>[[مِنْ عَلَقٍ]] d'une adhérence</td></tr>
<tr><td class="ar">إِلَى</td><td>vers, jusqu'à</td><td>[[إِلَىٰ رَبِّكَ]] vers ton Seigneur</td></tr>
<tr><td class="ar">عَنْ</td><td>de (en s'éloignant), au sujet de</td><td>[[عَنِ ٱللَّغْوِ]] (se détourner) de la futilité</td></tr>
<tr><td class="ar">عَلَى</td><td>sur ; contre ; à la charge de</td><td>[[عَلَى ٱللَّهِ]] sur Allah</td></tr>
<tr><td class="ar">فِي</td><td>dans ; au sujet de</td><td>[[فِي ٱلْأَرْضِ]] sur la terre</td></tr>
<tr><td class="ar">حَتَّى</td><td>jusqu'à</td><td>[[حَتَّىٰ مَطْلَعِ ٱلْفَجْرِ]] jusqu'au lever de l'aube</td></tr>
</table>
<p>Les trois premières (<i>bi-</i>, <i>li-</i>, <i>ka-</i>) s'écrivent <b>soudées</b> au mot suivant.</p>
{{ex 96:1|hl=باسم|com=[[بِٱسْمِ]] : préposition [[بِ]] + [[ٱسْم]] au génitif.}}
{{ex 96:4|hl=بالقلم}}
<h3><span class="pastille">1</span>Avec les pronoms</h3>
<ul>
<li>[[إِلَى]], [[عَلَى]], [[لَدَى]] changent leur alif en yāʾ : [[إِلَيْهِ]], [[عَلَيْهِمْ]], [[لَدَيْنَا]].</li>
<li>[[لِـ]] prend une fatḥa devant les pronoms : [[لَهُ]], [[لَكَ]], [[لَنَا]] — sauf [[لِي]] « à moi ».</li>
<li>[[مِنْ]] et [[عَنْ]] doublent leur n devant [[ـِي]] : [[مِنِّي]], [[عَنِّي]] ; [[فِي]] + [[ي]] → [[فِيَّ]].</li>
<li>Le pronom [[ـهُ]] devient [[ـهِ]] après i ou y : [[بِهِ]], [[فِيهِ]], [[عَلَيْهِ]].</li>
</ul>
<h3><span class="pastille">2</span>Avec [[مَا]] et [[مَنْ]]</h3>
<p>[[مِنْ]] + [[مَا]] → [[مِمَّا]] « de ce que » ; [[مِنْ]] + [[مَنْ]] → [[مِمَّنْ]] ; [[عَنْ]] + [[مَا]] → [[عَمَّا]] ; [[فِي]] + [[مَا]] → [[فِيمَا]] ; [[بِ]] + [[مَا]] → [[بِمَا]].</p>
{{ex 2:3|hl=ومما|com=[[وَمِمَّا رَزَقْنَٰهُمْ]] « et de ce que Nous leur avons attribué ».}}
<h3><span class="pastille">3</span>Le groupe prépositionnel</h3>
<p>Préposition + nom forme un <b>shibh jumla</b> [[شِبْهُ جُمْلَة]] (« quasi-phrase »). Il peut servir d'attribut : [[ٱلْحَمْدُ لِلَّهِ]] « la louange (est) à Allah » (L15). Avec [[لِـ]], il exprime la possession : [[لَهُ ٱلْمُلْكُ]] « à Lui (appartient) la royauté », c'est-à-dire « Il a la royauté ».</p>
<div class="attention"><span class="lab">Faux amis</span>[[عِنْدَ]] « chez », [[بَيْنَ]] « entre », [[فَوْقَ]] « au-dessus », [[تَحْتَ]] « sous », [[قَبْلَ]] « avant », [[بَعْدَ]] « après », [[مَعَ]] « avec » sont des <b>noms</b> à l'accusatif suivis d'un génitif (annexion, L13 ; compléments, L35). Ils se traduisent comme des prépositions.</div>
""",
    fiche=dict(
        titre='Les prépositions', ar='حُرُوفُ الْجَرِّ',
        corps=r"""
<table class="t">
<tr><th class="ar">mot</th><th>sens</th><th class="ar">mot</th><th>sens</th></tr>
<tr><td class="ar">بِـ</td><td>par, avec</td><td class="ar">إِلَى</td><td>vers, jusqu'à</td></tr>
<tr><td class="ar">لِـ</td><td>à, pour (avoir)</td><td class="ar">عَنْ</td><td>de (éloignement), au sujet de</td></tr>
<tr><td class="ar">كَـ</td><td>comme</td><td class="ar">عَلَى</td><td>sur, contre</td></tr>
<tr><td class="ar">مِنْ</td><td>de, parmi</td><td class="ar">فِي</td><td>dans</td></tr>
</table>
<ul>
<li>Toujours suivies du <b>génitif</b>.</li>
<li>Avec pronoms : [[إِلَيْهِ]] [[عَلَيْهِ]] [[لَهُ]] [[لِي]] [[مِنِّي]] [[فِيهِ]].</li>
<li>Avec mā/man : [[مِمَّا]] [[مِمَّنْ]] [[عَمَّا]] [[فِيمَا]] [[بِمَا]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Traduis.", items=[
            ('[[فِي ٱلْأَرْضِ]]', 'sur (dans) la terre'), ('[[مِنَ ٱلسَّمَاءِ]]', 'du ciel'), ('[[عَلَى ٱللَّهِ]]', 'sur Allah (« à Allah de… »)'),
            ('[[إِلَى رَبِّكَ]]', 'vers ton Seigneur'), ('[[لِلنَّاسِ]]', 'pour les gens'), ('[[بِٱلْحَقِّ]]', 'avec la vérité'),
            ('[[عَنِ ٱلصَّلَاةِ]]', '(loin) de la prière'), ('[[كَٱلْعِهْنِ]]', 'comme de la laine'),
        ]),
        dict(consigne="Unis les deux éléments.", items=[
            ('[[مِنْ]] + [[مَا]]', '[[مِمَّا]]'), ('[[عَلَى]] + [[هُمْ]]', '[[عَلَيْهِمْ]]'), ('[[لِ]] + [[هُ]]', '[[لَهُ]]'),
            ('[[فِي]] + [[هِ]]', '[[فِيهِ]]'), ('[[مِنْ]] + [[ي]]', '[[مِنِّي]]'), ('[[إِلَى]] + [[كَ]]', '[[إِلَيْكَ]]'),
        ]),
        dict(auto='prep', refs=[(6, 1, 3)], n=8),
    ],
    flash=[
        ("Cas après une préposition ?", "génitif"),
        ("[[لَهُ]] : comment traduire [[لَهُ ٱلْمُلْكُ]] ?", "« à Lui la royauté » = Il a la royauté"),
        ("[[عَلَى]] + [[هِمْ]] ?", "[[عَلَيْهِمْ]]"),
        ("[[مِنْ]] + [[مَا]] ?", "[[مِمَّا]]"),
        ("[[عِنْدَ]] est-il une préposition ?", "non : un nom (ẓarf) à l'accusatif suivi d'un génitif"),
    ],
    notes={
        (96, 2): "[[خَلَقَ ٱلْإِنسَٰنَ مِنْ عَلَقٍ]] : [[مِنْ]] indique ici la matière (« à partir de »).",
        (96, 6): "[[لَيَطْغَىٰٓ]] : <i>la-</i> d'insistance (L19) + inaccompli : « dépasse vraiment les bornes ».",
        (96, 7): "[[أَن رَّءَاهُ ٱسْتَغْنَىٰٓ]] « dès qu'il se voit se suffire à lui-même » : <i>an</i> + accompli = « parce que » (L23).",
    },
)

L[11] = dict(
    objectifs=[
        "connaître les quatorze pronoms isolés",
        "les employer comme sujet de la phrase nominale",
        "reconnaître le pronom de séparation",
    ],
    expose=r"""
<p>Les <b>pronoms isolés</b> [[ٱلضَّمَائِرُ ٱلْمُنْفَصِلَةُ]] s'écrivent comme des mots séparés. Ils servent surtout de <b>sujet</b> (« lui, il », « toi, tu »…). Ils sont définis et indéclinables.</p>
<table class="t c">
<tr><th></th><th colspan="2">singulier</th><th colspan="2">duel</th><th colspan="2">pluriel</th></tr>
<tr><td>3<sup>e</sup> m.</td><td class="ar">هُوَ</td><td>il, lui</td><td class="ar" rowspan="2">هُمَا</td><td rowspan="2">eux deux, elles deux</td><td class="ar">هُمْ</td><td>ils, eux</td></tr>
<tr><td>3<sup>e</sup> f.</td><td class="ar">هِيَ</td><td>elle</td><td class="ar">هُنَّ</td><td>elles</td></tr>
<tr><td>2<sup>e</sup> m.</td><td class="ar">أَنْتَ</td><td>tu, toi</td><td class="ar" rowspan="2">أَنْتُمَا</td><td rowspan="2">vous deux</td><td class="ar">أَنْتُمْ</td><td>vous</td></tr>
<tr><td>2<sup>e</sup> f.</td><td class="ar">أَنْتِ</td><td>tu, toi (f.)</td><td class="ar">أَنْتُنَّ</td><td>vous (f.)</td></tr>
<tr><td>1<sup>re</sup></td><td class="ar">أَنَا</td><td>je, moi</td><td colspan="2">—</td><td class="ar">نَحْنُ</td><td>nous</td></tr>
</table>
<p>Dans le muṣḥaf, [[أَنَا]] s'écrit [[أَنَا۠]] : l'alif final ne se prononce qu'à la pause. Le [[مْ]] de [[هُمْ]], [[أَنْتُمْ]] prend une ḍamma devant une hamzat al-waṣl : [[هُمُ ٱلْمُفْلِحُونَ]] <i>humu l-mufliḥūn</i>.</p>
{{ex 112:1|hl=هو|com=[[هُوَ ٱللَّهُ أَحَدٌ]] : « <b>Il</b> est Allah, Unique ». Le pronom est sujet.}}
{{ex 109:4|hl=أنا|com=« Et <b>je</b> ne suis pas adorateur de ce que vous adorez. »}}
<h3><span class="pastille">1</span>Le « nous » de majesté</h3>
<p>Allah parle souvent de Lui-même au pluriel ([[نَحْنُ]], [[إِنَّا]], verbes en [[ـنَا]]) : c'est un pluriel de grandeur, non de nombre. Le Coran affirme partout ailleurs l'unicité divine.</p>
{{ex 15:9|hl=نحن|com=« C'est <b>Nous</b> qui avons fait descendre le Rappel. »}}
<h3><span class="pastille">2</span>Le pronom de séparation</h3>
<p>Entre un sujet défini et un attribut défini, un pronom de 3<sup>e</sup> personne peut s'intercaler pour éviter la confusion avec un adjectif et pour insister : c'est le <b>pronom de séparation</b> [[ضَمِيرُ ٱلْفَصْلِ]]. On traduit « c'est… qui ».</p>
{{ex 2:5|hl=هم|from=وأولئك|to=المفلحون|com=« et <b>ce sont eux</b> les gagnants ».}}
<div class="encadre"><span class="lab">À retenir</span>Le pronom isolé est surtout sujet. Comme complément, on emploie le pronom suffixe (leçon suivante) ; la forme isolée [[إِيَّا]] + suffixe ([[إِيَّاكَ]]) sert à mettre le complément en tête (L34).</div>
""",
    fiche=dict(
        titre='Les pronoms isolés', ar='الضَّمَائِرُ الْمُنْفَصِلَةُ',
        corps=r"""
<table class="t c">
<tr><th></th><th>sg.</th><th>duel</th><th>pl.</th></tr>
<tr><td>3 m.</td><td class="ar">هُوَ</td><td class="ar">هُمَا</td><td class="ar">هُمْ</td></tr>
<tr><td>3 f.</td><td class="ar">هِيَ</td><td class="ar">هُمَا</td><td class="ar">هُنَّ</td></tr>
<tr><td>2 m.</td><td class="ar">أَنْتَ</td><td class="ar">أَنْتُمَا</td><td class="ar">أَنْتُمْ</td></tr>
<tr><td>2 f.</td><td class="ar">أَنْتِ</td><td class="ar">أَنْتُمَا</td><td class="ar">أَنْتُنَّ</td></tr>
<tr><td>1</td><td class="ar">أَنَا</td><td>—</td><td class="ar">نَحْنُ</td></tr>
</table>
<ul><li>Emploi : sujet ; pronom de séparation ([[هُمُ ٱلْمُفْلِحُونَ]]) ; « nous » de majesté.</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne le pronom isolé.", items=[
            ('toi (m.)', '[[أَنْتَ]]'), ('nous', '[[نَحْنُ]]'), ('elles', '[[هُنَّ]]'), ('vous (m. pl.)', '[[أَنْتُمْ]]'),
            ('elle', '[[هِيَ]]'), ('eux deux', '[[هُمَا]]'), ('toi (f.)', '[[أَنْتِ]]'), ('je', '[[أَنَا]]'),
        ]),
        dict(consigne="Traduis.", items=[
            ('[[هُوَ ٱلْغَفُورُ]]', "c'est Lui le Pardonneur"), ('[[أَنْتَ ٱلسَّمِيعُ]]', "c'est Toi l'Audient"),
            ('[[نَحْنُ مُسْلِمُونَ]]', 'nous sommes soumis (musulmans)'), ('[[هُمْ فِيهَا خَالِدُونَ]]', "ils y sont éternellement"),
            ('[[أَنَا رَسُولُ رَبِّكِ]]', 'je suis le messager de ton Seigneur (19:19)'), ('[[هِيَ عَصَايَ]]', "c'est mon bâton (20:18)"),
        ]),
    ],
    flash=[
        ("Pronom « vous » (m. pl.) ?", "[[أَنْتُمْ]]"),
        ("Que signifie [[هُمَا]] ?", "eux deux / elles deux"),
        ("Comment se lit [[أَنَا۠]] en liaison ?", "<i>ana</i>"),
        ("Rôle de [[هُمْ]] dans [[وَأُو۟لَٰٓئِكَ هُمُ ٱلْمُفْلِحُونَ]] ?", "pronom de séparation : « ce sont eux les gagnants »"),
        ("Pronom « elles » ?", "[[هُنَّ]]"),
    ],
    notes={
        (109, 1): "[[قُلْ]] « dis » : impératif (L24). [[يَٰٓأَيُّهَا]] = vocatif (L18).",
        (109, 2): "[[لَآ أَعْبُدُ]] : <i>lā</i> + inaccompli = négation du présent (L25).",
        (109, 6): "[[لَكُمْ دِينُكُمْ]] « à vous votre religion » : l'attribut [[لَكُمْ]] est placé en tête (L15).",
    },
)
