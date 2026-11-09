"""Partie III — le verbe (leçons 21 à 32)."""

L = {}

L[21] = dict(
    objectifs=[
        "conjuguer l'accompli aux quatorze personnes",
        "reconnaître la personne grâce à la terminaison",
        "connaître les valeurs de l'accompli",
    ],
    expose=r"""
<p>Le verbe arabe a deux « aspects » : l'<b>accompli</b> [[ٱلْمَاضِي]] (l'action faite) et l'<b>inaccompli</b> [[ٱلْمُضَارِع]] (l'action en cours ou à venir). On cite toujours un verbe à la 3<sup>e</sup> personne du masculin singulier de l'accompli : [[فَعَلَ]] « il a fait » sert de nom au verbe (on dit « le verbe <i>faʿala</i> »).</p>
<h3><span class="pastille">1</span>La conjugaison</h3>
<p>L'accompli se forme en ajoutant des <b>terminaisons</b> à la base [[فَعَل]] :</p>
<table class="t c">
<tr><th></th><th>singulier</th><th>duel</th><th>pluriel</th></tr>
<tr><td>3<sup>e</sup> m.</td><td class="ar">فَعَلَ <span class="gris petit">il a fait</span></td><td class="ar">فَعَلَا</td><td class="ar">فَعَلُوا</td></tr>
<tr><td>3<sup>e</sup> f.</td><td class="ar">فَعَلَتْ</td><td class="ar">فَعَلَتَا</td><td class="ar">فَعَلْنَ</td></tr>
<tr><td>2<sup>e</sup> m.</td><td class="ar">فَعَلْتَ</td><td class="ar" rowspan="2">فَعَلْتُمَا</td><td class="ar">فَعَلْتُمْ</td></tr>
<tr><td>2<sup>e</sup> f.</td><td class="ar">فَعَلْتِ</td><td class="ar">فَعَلْتُنَّ</td></tr>
<tr><td>1<sup>re</sup></td><td class="ar">فَعَلْتُ</td><td>—</td><td class="ar">فَعَلْنَا</td></tr>
</table>
<p>Devant une terminaison qui commence par une consonne (<i>-tu, -ta, -nā…</i>), la dernière radicale prend un sukūn : [[فَعَلْتُ]]. Le wāw du pluriel est suivi d'un alif muet (L2) : [[كَفَرُوا۟]] <i>kafarū</i>.</p>
{{ex 80:1|hl=عبس,وتولى|com=[[عَبَسَ]] « il a froncé les sourcils » ; [[تَوَلَّىٰٓ]] « il s'est détourné » : 3<sup>e</sup> m. sg.}}
{{ex 1:7|hl=أنعمت|com=[[أَنْعَمْتَ]] « Tu as comblé » : 2<sup>e</sup> m. sg.}}
{{ex 109:4|hl=عبدتم|com=[[عَبَدتُّمْ]] « vous avez adoré » : 2<sup>e</sup> m. pl. (le d s'assimile au t).}}
<h3><span class="pastille">2</span>Trois voyelles possibles</h3>
<p>La voyelle de la 2<sup>e</sup> radicale varie : [[فَعَلَ]] ([[خَلَقَ]] créer, [[كَتَبَ]] écrire), [[فَعِلَ]] ([[عَلِمَ]] savoir, [[عَمِلَ]] œuvrer, [[شَهِدَ]] témoigner), [[فَعُلَ]] (qualités : [[كَبُرَ]] être grand, [[ثَقُلَ]] être lourd).</p>
<h3><span class="pastille">3</span>L'accord</h3>
<p>À la 3<sup>e</sup> personne du féminin singulier, [[ـَتْ]] devient [[ـَتِ]] devant une hamzat al-waṣl : [[قَالَتِ ٱمْرَأَتُ]] <i>qālati mraʾatu</i>. Quand le sujet nominal suit le verbe, le verbe reste au <b>singulier</b> (L33).</p>
<h3><span class="pastille">4</span>Valeurs</h3>
<ul>
<li>le <b>passé</b> : [[خَلَقَ]] « Il a créé » ;</li>
<li>avec [[قَدْ]], le résultat acquis : [[قَدْ أَفْلَحَ]] « a certes réussi » (L25) ;</li>
<li>après [[إِذَا]] et dans les conditions, un <b>futur</b> : [[إِذَا جَآءَ نَصْرُ ٱللَّهِ]] « quand viendra le secours d'Allah » (110:1) ;</li>
<li>le <b>souhait</b> : [[رَضِىَ ٱللَّهُ عَنْهُمْ]] « qu'Allah les agrée » / « Allah les a agréés » (98:8).</li>
</ul>
""",
    fiche=dict(
        titre="L'accompli", ar='الْفِعْلُ الْمَاضِي',
        corps=r"""
<table class="t c">
<tr><th></th><th>sg.</th><th>duel</th><th>pl.</th></tr>
<tr><td>3 m.</td><td class="ar">فَعَلَ</td><td class="ar">فَعَلَا</td><td class="ar">فَعَلُوا</td></tr>
<tr><td>3 f.</td><td class="ar">فَعَلَتْ</td><td class="ar">فَعَلَتَا</td><td class="ar">فَعَلْنَ</td></tr>
<tr><td>2 m.</td><td class="ar">فَعَلْتَ</td><td class="ar">فَعَلْتُمَا</td><td class="ar">فَعَلْتُمْ</td></tr>
<tr><td>2 f.</td><td class="ar">فَعَلْتِ</td><td class="ar">فَعَلْتُمَا</td><td class="ar">فَعَلْتُنَّ</td></tr>
<tr><td>1</td><td class="ar">فَعَلْتُ</td><td>—</td><td class="ar">فَعَلْنَا</td></tr>
</table>
<ul><li>Types : [[فَعَلَ]] · [[فَعِلَ]] · [[فَعُلَ]]. Valeurs : passé ; avec [[قَدْ]] ; futur après [[إِذَا]] et en condition ; souhait.</li></ul>""",
    ),
    exercices=[
        dict(consigne="Conjugue à l'accompli.", items=[
            ('[[خَلَقَ]], 1<sup>re</sup> pl.', '[[خَلَقْنَا]]'), ('[[عَلِمَ]], 3<sup>e</sup> f. sg.', '[[عَلِمَتْ]]'),
            ('[[كَفَرَ]], 3<sup>e</sup> m. pl.', '[[كَفَرُوا]]'), ('[[عَبَدَ]], 2<sup>e</sup> m. pl.', '[[عَبَدْتُمْ]]'),
            ('[[ذَكَرَ]], 1<sup>re</sup> sg.', '[[ذَكَرْتُ]]'), ('[[سَمِعَ]], 2<sup>e</sup> m. sg.', '[[سَمِعْتَ]]'),
        ]),
        dict(auto='verbe', refs=[(80, 17, 32)], n=10),
    ],
    flash=[
        ("Accompli 3e f. sg. de [[فَعَلَ]] ?", "[[فَعَلَتْ]]"),
        ("Que signifie la terminaison [[ـنَا]] sur un accompli ?", "« nous » (1re pl.)"),
        ("[[عَبَدتُّمْ]] : personne ?", "2e m. pl."),
        ("Valeur de l'accompli après [[إِذَا]] ?", "futur"),
        ("Accompli 3e m. pl. de [[ءَامَنَ]] ?", "[[ءَامَنُوا۟]]"),
    ],
    notes={
        (80, 2): "[[أَن جَآءَهُ ٱلْأَعْمَىٰ]] « parce que l'aveugle est venu à lui » : <i>an</i> + accompli.",
        (80, 3): "[[يَزَّكَّىٰٓ]] = <i>yatazakkā</i> (forme V, le t assimilé, L28).",
        (80, 11): "[[كَلَّآ إِنَّهَا تَذْكِرَةٌ]] « Non ! C'est un rappel » : <i>kallā</i> rejette ce qui précède.",
    },
)

L[22] = dict(
    objectifs=[
        "conjuguer l'inaccompli (préfixes et suffixes)",
        "reconnaître l'indicatif et les « cinq verbes »",
        "connaître les valeurs de l'inaccompli",
    ],
    expose=r"""
<p>L'inaccompli se forme avec un <b>préfixe</b> (qui indique la personne) et, à certaines personnes, un <b>suffixe</b>. Les quatre préfixes tiennent dans le mot [[أَنَيْتُ]] : <b>أ</b> (je), <b>ن</b> (nous), <b>ي</b> (il, ils), <b>ت</b> (tu, vous, elle).</p>
<table class="t c">
<tr><th></th><th>singulier</th><th>duel</th><th>pluriel</th></tr>
<tr><td>3<sup>e</sup> m.</td><td class="ar">يَفْعَلُ <span class="gris petit">il fait</span></td><td class="ar">يَفْعَلَانِ</td><td class="ar">يَفْعَلُونَ</td></tr>
<tr><td>3<sup>e</sup> f.</td><td class="ar">تَفْعَلُ</td><td class="ar">تَفْعَلَانِ</td><td class="ar">يَفْعَلْنَ</td></tr>
<tr><td>2<sup>e</sup> m.</td><td class="ar">تَفْعَلُ</td><td class="ar" rowspan="2">تَفْعَلَانِ</td><td class="ar">تَفْعَلُونَ</td></tr>
<tr><td>2<sup>e</sup> f.</td><td class="ar">تَفْعَلِينَ</td><td class="ar">تَفْعَلْنَ</td></tr>
<tr><td>1<sup>re</sup></td><td class="ar">أَفْعَلُ</td><td>—</td><td class="ar">نَفْعَلُ</td></tr>
</table>
<h3><span class="pastille">1</span>La voyelle centrale</h3>
<p>La 2<sup>e</sup> radicale porte <b>a</b>, <b>i</b> ou <b>u</b> selon le verbe ; elle s'apprend avec lui (les listes de vocabulaire donnent l'inaccompli) :</p>
<ul>
<li><b>u</b> : [[كَتَبَ يَكْتُبُ]], [[عَبَدَ يَعْبُدُ]], [[خَلَقَ يَخْلُقُ]], [[نَصَرَ يَنْصُرُ]] ;</li>
<li><b>i</b> : [[ضَرَبَ يَضْرِبُ]], [[جَلَسَ يَجْلِسُ]], [[غَفَرَ يَغْفِرُ]] ;</li>
<li><b>a</b> : [[عَلِمَ يَعْلَمُ]], [[جَعَلَ يَجْعَلُ]], [[فَتَحَ يَفْتَحُ]].</li>
</ul>
<h3><span class="pastille">2</span>L'indicatif (marfūʿ)</h3>
<p>Sans particule devant lui, l'inaccompli est à l'<b>indicatif</b>. Sa marque est la <b>ḍamma</b> finale ([[يَفْعَلُ]]), ou le <b>nūn</b> final pour cinq formes, appelées les « cinq verbes » [[ٱلْأَفْعَالُ ٱلْخَمْسَةُ]] : [[يَفْعَلُونَ]], [[تَفْعَلُونَ]], [[يَفْعَلَانِ]], [[تَفْعَلَانِ]], [[تَفْعَلِينَ]]. Au subjonctif et à l'apocopé, ce nūn tombe (L23–24). Le nūn du féminin pluriel ([[يَفْعَلْنَ]]) ne tombe jamais.</p>
{{ex 87:7|hl=يعلم,يخفى|com=[[يَعْلَمُ]] « Il connaît » ; [[يَخْفَىٰ]] « (ce qui) est caché » (verbe défectueux, L32).}}
{{ex 1:5|hl=نعبد,نستعين|com=[[نَعْبُدُ]] « nous adorons » : préfixe <b>ن</b>, indicatif.}}
<h3><span class="pastille">3</span>Valeurs</h3>
<p>L'inaccompli exprime le <b>présent</b> ([[يَعْلَمُ]] « Il sait »), une vérité générale, l'<b>habitude</b>, et souvent le <b>futur</b> ; le futur est précisé par [[سَـ]] ou [[سَوْفَ]] (L25) : [[سَيَذَّكَّرُ مَن يَخْشَىٰ]] « se rappellera celui qui craint » (87:10).</p>
<div class="attention"><span class="lab">Formes dérivées</span>Aux formes II, III et IV, le préfixe prend une <b>ḍamma</b> : [[يُعَلِّمُ]], [[يُجَاهِدُ]], [[يُنْزِلُ]] (L27). [[يُ]] au lieu de [[يَ]] est donc un indice précieux.</div>
""",
    fiche=dict(
        titre="L'inaccompli", ar='الْفِعْلُ الْمُضَارِعُ',
        corps=r"""
<table class="t c">
<tr><th></th><th>sg.</th><th>duel</th><th>pl.</th></tr>
<tr><td>3 m.</td><td class="ar">يَفْعَلُ</td><td class="ar">يَفْعَلَانِ</td><td class="ar">يَفْعَلُونَ</td></tr>
<tr><td>3 f.</td><td class="ar">تَفْعَلُ</td><td class="ar">تَفْعَلَانِ</td><td class="ar">يَفْعَلْنَ</td></tr>
<tr><td>2 m.</td><td class="ar">تَفْعَلُ</td><td class="ar">تَفْعَلَانِ</td><td class="ar">تَفْعَلُونَ</td></tr>
<tr><td>2 f.</td><td class="ar">تَفْعَلِينَ</td><td class="ar">تَفْعَلَانِ</td><td class="ar">تَفْعَلْنَ</td></tr>
<tr><td>1</td><td class="ar">أَفْعَلُ</td><td>—</td><td class="ar">نَفْعَلُ</td></tr>
</table>
<ul><li>Préfixes [[أَنَيْتُ]] ; voyelle centrale a / i / u à apprendre.</li>
<li>Indicatif : ḍamma, ou nūn des « cinq verbes ». Valeurs : présent, habitude, futur.</li></ul>""",
    ),
    exercices=[
        dict(consigne="Conjugue à l'inaccompli indicatif.", items=[
            ('[[يَعْلَمُ]], 2<sup>e</sup> m. pl.', '[[تَعْلَمُونَ]]'), ('[[يَعْبُدُ]], 1<sup>re</sup> sg.', '[[أَعْبُدُ]]'),
            ('[[يَخْلُقُ]], 3<sup>e</sup> f. sg.', '[[تَخْلُقُ]]'), ('[[يَجْعَلُ]], 1<sup>re</sup> pl.', '[[نَجْعَلُ]]'),
            ('[[يَشْرَبُ]], 3<sup>e</sup> m. pl.', '[[يَشْرَبُونَ]]'), ('[[يَغْفِرُ]], 3<sup>e</sup> m. sg.', '[[يَغْفِرُ]]'),
        ]),
        dict(auto='verbe', refs=[(2, 6, 12)], n=10),
    ],
    flash=[
        ("Les quatre préfixes de l'inaccompli ?", "[[أَنَيْتُ]] : أ ن ي ت"),
        ("Inaccompli 2e m. pl. de [[فَعَلَ]] ?", "[[تَفْعَلُونَ]]"),
        ("Quels sont les « cinq verbes » ?", "les formes à nūn : يفعلون، تفعلون، يفعلان، تفعلان، تفعلين"),
        ("Marque de l'indicatif ?", "ḍamma (ou nūn des cinq verbes)"),
        ("Préfixe [[يُ]] avec ḍamma : quelles formes ?", "formes II, III, IV"),
    ],
    notes={
        (87, 6): "[[سَنُقْرِئُكَ فَلَا تَنسَىٰٓ]] « Nous te ferons réciter, et tu n'oublieras pas » : [[سَـ]] du futur ; forme IV de [[قَرَأَ]].",
        (87, 10): "[[سَيَذَّكَّرُ]] = <i>sa-yatadhakkaru</i> : futur, forme V.",
        (87, 13): "[[لَا يَمُوتُ فِيهَا وَلَا يَحْيَىٰ]] « il n'y mourra ni n'y vivra » : <i>lā</i> + inaccompli (L25).",
    },
)

L[23] = dict(
    objectifs=[
        "reconnaître le subjonctif (manṣūb) et ses particules",
        "savoir que les « cinq verbes » perdent leur nūn",
        "comprendre [[أَنْ]] + verbe = nom verbal",
    ],
    expose=r"""
<p>Après certaines particules, l'inaccompli passe au <b>subjonctif</b> [[ٱلْمُضَارِعُ ٱلْمَنْصُوبُ]]. Sa marque est la <b>fatḥa</b> finale ; les « cinq verbes » <b>perdent leur nūn</b> (et le wāw du pluriel reçoit un alif muet).</p>
<table class="t c">
<tr><th>indicatif</th><th>subjonctif</th><th>indicatif</th><th>subjonctif</th></tr>
<tr><td class="ar">يَفْعَلُ</td><td class="ar">يَفْعَلَ</td><td class="ar">يَفْعَلُونَ</td><td class="ar">يَفْعَلُوا</td></tr>
<tr><td class="ar">تَفْعَلِينَ</td><td class="ar">تَفْعَلِي</td><td class="ar">يَفْعَلَانِ</td><td class="ar">يَفْعَلَا</td></tr>
<tr><td class="ar">يَفْعَلْنَ</td><td class="ar">يَفْعَلْنَ (inchangé)</td><td class="ar">نَفْعَلُ</td><td class="ar">نَفْعَلَ</td></tr>
</table>
<h3><span class="pastille">1</span>Les particules du subjonctif</h3>
<table class="t">
<tr><th class="ar">particule</th><th>sens</th><th>exemple</th></tr>
<tr><td class="ar">أَنْ</td><td>que ; de (+ infinitif)</td><td>[[يُرِيدُونَ أَن يُطْفِـُٔوا۟]] ils veulent éteindre</td></tr>
<tr><td class="ar">لَنْ</td><td>ne… pas (futur), ne… jamais</td><td>[[لَن يَقْدِرَ]] personne ne pourra</td></tr>
<tr><td class="ar">لِـ · كَيْ · لِكَيْ</td><td>pour que, afin de</td><td>[[لِيَعْبُدُوا۟]] pour adorer</td></tr>
<tr><td class="ar">حَتَّى</td><td>jusqu'à ce que ; afin que</td><td>[[حَتَّىٰ يَرْجِعَ]] jusqu'à ce qu'il revienne</td></tr>
<tr><td class="ar">إِذَنْ</td><td>alors, en ce cas</td><td>(rare)</td></tr>
</table>
{{ex 90:5|hl=يقدر|com=[[أَيَحْسَبُ أَن لَّن يَقْدِرَ عَلَيْهِ أَحَدٌ]] « pense-t-il que nul ne pourra rien contre lui ? » : [[يَقْدِرَ]] au subjonctif après [[لَن]].}}
{{ex 9:32|hl=أن,يطفئوا|from=يريدون|to=بأفواههم|com=[[يُطْفِـُٔوا۟]] : subjonctif après [[أَن]], le nūn de <i>yuṭfiʾūna</i> est tombé.}}
{{ex 98:5|hl=ليعبدوا|from=وما|to=الدين|com=[[لِيَعْبُدُوا۟]] « pour adorer » : <i>li-</i> de but + subjonctif.}}
<h3><span class="pastille">2</span>An + verbe = un nom</h3>
<p>[[أَنْ]] + subjonctif équivaut à un <b>nom verbal</b> (maṣdar, L29). Le groupe peut être sujet ou complément :</p>
{{ex 2:184|hl=وأن,تصوموا,خير@3|from=وأن|to=لكم|com=« et <b>que vous jeûniez</b> est meilleur pour vous » = « jeûner vaut mieux pour vous ».}}
<div class="attention"><span class="lab">Ne pas confondre</span>[[أَنْ]] (sukūn, + verbe au subjonctif) et [[أَنَّ]] (shadda, sœur de <i>inna</i>, + nom à l'accusatif, L19) se traduisent tous deux par « que ».</div>
""",
    fiche=dict(
        titre='Le subjonctif', ar='الْمُضَارِعُ الْمَنْصُوبُ',
        corps=r"""
<ul>
<li>Après [[أَنْ]] que · [[لَنْ]] ne… jamais (futur) · [[لِـ]]/[[كَيْ]]/[[لِكَيْ]] pour que · [[حَتَّى]] jusqu'à ce que · [[إِذَنْ]].</li>
<li>Marque : <b>fatḥa</b> ([[يَفْعَلَ]]) ; les cinq verbes <b>perdent le nūn</b> ([[يَفْعَلُوا]], [[تَفْعَلِي]], [[يَفْعَلَا]]) ; [[يَفْعَلْنَ]] inchangé.</li>
<li>[[أَنْ]] + verbe = nom verbal : [[أَنْ تَصُومُوا]] « jeûner ».</li>
<li>[[أَنْ]] + verbe ≠ [[أَنَّ]] + nom.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Mets le verbe au subjonctif après la particule.", items=[
            ('[[لَنْ]] + [[يَعْلَمُونَ]]', '[[لَنْ يَعْلَمُوا]]'), ('[[أَنْ]] + [[يَعْبُدُ]]', '[[أَنْ يَعْبُدَ]]'),
            ('[[لِـ]] + [[تَعْلَمُونَ]]', '[[لِتَعْلَمُوا]]'), ('[[حَتَّى]] + [[يَرْجِعُ]]', '[[حَتَّى يَرْجِعَ]]'),
            ('[[لَنْ]] + [[تَفْعَلِينَ]]', '[[لَنْ تَفْعَلِي]]'), ('[[أَنْ]] + [[يَقُولَانِ]]', '[[أَنْ يَقُولَا]]'),
        ]),
        dict(auto='mode', refs=[(2, 183, 185), (9, 32, 33)], n=8),
    ],
    flash=[
        ("Marque du subjonctif ?", "fatḥa ; les cinq verbes perdent le nūn"),
        ("[[لَنْ]] + subjonctif : sens ?", "négation du futur : ne… jamais"),
        ("[[أَن تَصُومُوا۟]] équivaut à… ?", "un nom verbal : « jeûner »"),
        ("Subjonctif de [[يَعْلَمُونَ]] ?", "[[يَعْلَمُوا]]"),
        ("[[يَفْعَلْنَ]] change-t-il au subjonctif ?", "non"),
    ],
    notes={
        (90, 1): "[[لَآ أُقْسِمُ]] « non ! je jure… » : formule de serment (L39).",
        (90, 7): "[[أَن لَّمْ يَرَهُۥٓ أَحَدٌ]] : [[لَمْ]] + apocopé [[يَرَ]] (de [[رَأَى]], L24, L32).",
        (90, 8): "[[أَلَمْ نَجْعَل لَّهُۥ عَيْنَيْنِ]] : question rhétorique ; [[عَيْنَيْنِ]] duel à l'accusatif.",
    },
)

L[24] = dict(
    objectifs=[
        "reconnaître l'apocopé (majzūm) et ses particules",
        "former l'impératif",
        "exprimer la défense (« ne fais pas »)",
    ],
    expose=r"""
<h3><span class="pastille">1</span>L'apocopé</h3>
<p>L'<b>apocopé</b> [[ٱلْمُضَارِعُ ٱلْمَجْزُومُ]] se marque par un <b>sukūn</b> final ; les « cinq verbes » perdent leur nūn, comme au subjonctif. On le trouve :</p>
<ul>
<li>après [[لَمْ]] (négation du passé) et [[لَمَّا]] (« pas encore ») ;</li>
<li>après le [[لَا]] de défense ([[لَا]] <i>nāhiya</i>) : « ne fais pas » ;</li>
<li>après le [[لِـ]] d'injonction : « qu'il fasse » ;</li>
<li>dans les phrases conditionnelles (L38) et en réponse à un impératif.</li>
</ul>
{{ex 112:3|hl=يلد,يولد|com=[[لَمْ يَلِدْ]] « Il n'a pas engendré » : sukūn final.}}
{{ex 74:6|hl=ولا,تمنن|com=[[وَلَا تَمْنُن]] « et ne donne pas (en escomptant plus) » : défense ; [[تَمْنُن]] est l'apocopé d'un verbe sourd (L32).}}
{{ex 83:26|hl=فليتنافس|com=[[فَلْيَتَنَافَسِ]] « qu'ils rivalisent donc » : lām d'injonction (le sukūn devient kasra devant [[ٱلْ]]).}}
<p>Quand le verbe finit par une voyelle longue (verbes faibles), c'est elle qui tombe : [[يَدْعُو]] → [[لَمْ يَدْعُ]], [[يَخْشَى]] → [[لَمْ يَخْشَ]], [[يَقُولُ]] → [[لَمْ يَقُلْ]] (L31–32).</p>
<h3><span class="pastille">2</span>L'impératif</h3>
<p>On part de l'apocopé à la 2<sup>e</sup> personne et l'on <b>retire le préfixe</b> [[تَـ]]. Si le mot commence alors par deux consonnes, on ajoute une hamzat al-waṣl prononcée <b>u</b> si la voyelle centrale est u, <b>i</b> sinon :</p>
<table class="t c">
<tr><th>apocopé</th><th>impératif</th><th>sens</th></tr>
<tr><td class="ar">تَكْتُبْ</td><td class="ar">ٱكْتُبْ <span class="gris petit">(u)</span></td><td>écris</td></tr>
<tr><td class="ar">تَقْرَأْ</td><td class="ar">ٱقْرَأْ <span class="gris petit">(i)</span></td><td>lis, récite</td></tr>
<tr><td class="ar">تَصْبِرْ</td><td class="ar">ٱصْبِرْ <span class="gris petit">(i)</span></td><td>endure</td></tr>
<tr><td class="ar">تُنْذِرْ <span class="gris petit">(f. IV)</span></td><td class="ar">أَنْذِرْ</td><td>avertis</td></tr>
<tr><td class="ar">تُكَبِّرْ <span class="gris petit">(f. II)</span></td><td class="ar">كَبِّرْ</td><td>proclame la grandeur</td></tr>
<tr><td class="ar">تَقُمْ</td><td class="ar">قُمْ</td><td>lève-toi</td></tr>
</table>
<p>Personnes : [[ٱكْتُبْ]] (m. sg.), [[ٱكْتُبِي]] (f. sg.), [[ٱكْتُبَا]] (duel), [[ٱكْتُبُوا]] (m. pl.), [[ٱكْتُبْنَ]] (f. pl.). La forme IV garde sa hamza « de coupure » : [[أَنذِرْ]].</p>
{{ex 74:2|hl=قم,فأنذر|com=« Lève-toi et avertis ! »}}
{{ex 74:3|hl=فكبر|com=[[وَرَبَّكَ فَكَبِّرْ]] « et ton Seigneur, magnifie-Le » : complément placé en tête pour insister (L34).}}
{{ex 1:6|hl=اهدنا|com=[[ٱهْدِنَا]] « guide-nous » : impératif de [[هَدَى]] (défectueux : le yāʾ tombe) + [[نَا]].}}
""",
    fiche=dict(
        titre="L'apocopé et l'impératif", ar='الْمَجْزُومُ وَالْأَمْرُ',
        corps=r"""
<ul>
<li><b>Apocopé</b> : sukūn ; cinq verbes sans nūn ; voyelle longue finale tombe ([[لَمْ يَدْعُ]], [[لَمْ يَقُلْ]]).</li>
<li>Après [[لَمْ]] (passé nié), [[لَمَّا]] (pas encore), [[لَا]] de défense, [[لِـ]] d'injonction, conditions.</li>
<li><b>Impératif</b> : apocopé 2<sup>e</sup> pers. sans [[تَـ]] ; + [[ٱ]] (u ou i) si deux consonnes : [[ٱكْتُبْ]], [[ٱقْرَأْ]] ; forme IV [[أَنْذِرْ]] ; [[قُمْ]], [[قُلْ]].</li>
<li>Personnes : [[ٱفْعَلْ]] [[ٱفْعَلِي]] [[ٱفْعَلَا]] [[ٱفْعَلُوا]] [[ٱفْعَلْنَ]].</li>
<li>Défense : [[لَا تَفْعَلْ]] « ne fais pas ».</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Forme l'impératif (m. sg., puis m. pl.).", items=[
            ('[[تَكْتُبُ]]', '[[ٱكْتُبْ]] · [[ٱكْتُبُوا]]'), ('[[تَعْبُدُ]]', '[[ٱعْبُدْ]] · [[ٱعْبُدُوا]]'),
            ('[[تَصْبِرُ]]', '[[ٱصْبِرْ]] · [[ٱصْبِرُوا]]'), ('[[تَعْلَمُ]]', '[[ٱعْلَمْ]] · [[ٱعْلَمُوا]]'),
            ('[[تُنْذِرُ]] (IV)', '[[أَنْذِرْ]] · [[أَنْذِرُوا]]'), ('[[تَذْكُرُ]]', '[[ٱذْكُرْ]] · [[ٱذْكُرُوا]]'),
        ]),
        dict(consigne="Nie au passé avec [[لَمْ]], puis interdis avec [[لَا]].", items=[
            ('[[يَعْلَمُونَ]]', '[[لَمْ يَعْلَمُوا]] · [[لَا تَعْلَمُوا]] (à la 2e p.)'), ('[[يَكْتُبُ]]', '[[لَمْ يَكْتُبْ]] · [[لَا تَكْتُبْ]]'),
            ('[[يَقُولُ]]', '[[لَمْ يَقُلْ]] · [[لَا تَقُلْ]]'), ('[[يَدْعُو]]', '[[لَمْ يَدْعُ]] · [[لَا تَدْعُ]]'),
        ], une=True),
        dict(auto='mode', refs=[(17, 23, 26)], n=8),
    ],
    flash=[
        ("Marque de l'apocopé ?", "sukūn (cinq verbes : chute du nūn)"),
        ("Impératif de [[تَقْرَأُ]] ?", "[[ٱقْرَأْ]]"),
        ("[[لَمْ يَلِدْ]] : sens ?", "il n'a pas engendré"),
        ("Impératif m. pl. de [[تَصْبِرُ]] ?", "[[ٱصْبِرُوا]]"),
        ("[[لَا تَقُلْ]] : sens ?", "ne dis pas"),
    ],
    notes={
        (74, 1): "[[يَٰٓأَيُّهَا ٱلْمُدَّثِّرُ]] « ô toi, le revêtu d'un manteau » : participe de forme V assimilée (<i>mutadaththir</i> → <i>muddaththir</i>).",
        (74, 6): "[[تَسْتَكْثِرُ]] est à l'indicatif : phrase d'état, « en cherchant à recevoir davantage ».",
        (74, 8): "[[فَإِذَا نُقِرَ فِى ٱلنَّاقُورِ]] « quand on sonnera de la Trompe » : passif (L26).",
    },
)

L[25] = dict(
    objectifs=[
        "choisir la bonne négation selon le temps",
        "exprimer le futur avec [[سَـ]] et [[سَوْفَ]]",
        "comprendre les deux valeurs de [[قَدْ]]",
    ],
    expose=r"""
<p>L'arabe a plusieurs négations ; chacune a son temps et son mode.</p>
<table class="t">
<tr><th>négation</th><th>construction</th><th>valeur</th><th>exemple</th></tr>
<tr><td class="ar">مَا</td><td>+ accompli</td><td>passé</td><td>[[مَا وَدَّعَكَ رَبُّكَ]] ton Seigneur ne t'a pas abandonné</td></tr>
<tr><td class="ar">لَمْ</td><td>+ apocopé</td><td>passé</td><td>[[لَمْ يَلِدْ]] Il n'a pas engendré</td></tr>
<tr><td class="ar">لَمَّا</td><td>+ apocopé</td><td>pas encore</td><td>[[وَلَمَّا يَدْخُلِ ٱلْإِيمَٰنُ]] la foi n'est pas encore entrée (49:14)</td></tr>
<tr><td class="ar">لَا</td><td>+ inaccompli</td><td>présent, général</td><td>[[لَآ أَعْبُدُ مَا تَعْبُدُونَ]] je n'adore pas ce que vous adorez</td></tr>
<tr><td class="ar">لَنْ</td><td>+ subjonctif</td><td>futur</td><td>[[لَن تَنَالُوا۟ ٱلْبِرَّ]] vous n'atteindrez pas la piété (3:92)</td></tr>
<tr><td class="ar">لَيْسَ</td><td>phrase nominale</td><td>présent</td><td>[[لَسْتَ عَلَيْهِم بِمُصَيْطِرٍ]] (L20)</td></tr>
<tr><td class="ar">مَا</td><td>phrase nominale</td><td>présent</td><td>[[وَمَا هُم بِمُؤْمِنِينَ]] ils ne sont pas croyants (2:8)</td></tr>
<tr><td class="ar">إِنْ</td><td>+ إِلَّا</td><td>ne… que</td><td>[[إِن يَقُولُونَ إِلَّا كَذِبًا]] ils ne disent que mensonge (18:5)</td></tr>
<tr><td class="ar">لَا</td><td>+ nom indéfini</td><td>aucun</td><td>[[لَا رَيْبَ فِيهِ]] (L19)</td></tr>
</table>
<h3><span class="pastille">1</span>Le futur</h3>
<p>[[سَـ]] (soudé) et [[سَوْفَ]] (séparé, souvent plus lointain ou plus solennel) + inaccompli indicatif expriment le futur :</p>
{{ex 102:3|hl=سوف,تعلمون|com=« Non ! Vous saurez bientôt. »}}
{{ex 87:10|hl=سيذكر}}
<h3><span class="pastille">2</span>Qad</h3>
<ul>
<li>[[قَدْ]] + <b>accompli</b> : l'action est accomplie, le résultat certain — « déjà, certes » : [[قَدْ أَفْلَحَ ٱلْمُؤْمِنُونَ]] « les croyants ont <b>certes</b> réussi » (23:1).</li>
<li>[[قَدْ]] + <b>inaccompli</b> : « il arrive que » ; dans le Coran, souvent « certes » : [[قَدْ يَعْلَمُ ٱللَّهُ]] « Allah connaît certes » (33:18).</li>
<li>[[لَقَدْ]] renforce encore : [[لَقَدْ خَلَقْنَا ٱلْإِنسَٰنَ]] (95:4).</li>
</ul>
<div class="encadre"><span class="lab">Kallā</span>[[كَلَّا]] est une particule de rejet : « non ! certainement pas ! ». Elle annonce souvent une vérité qui suit : [[كَلَّا سَوْفَ تَعْلَمُونَ]].</div>
""",
    fiche=dict(
        titre='Négation, futur, qad', ar='النَّفْيُ وَالِاسْتِقْبَالُ',
        corps=r"""
<table class="t">
<tr><th>passé</th><th>présent</th><th>futur</th></tr>
<tr><td>[[مَا]] + accompli · [[لَمْ]] + apocopé · [[لَمَّا]] + apocopé (pas encore)</td><td>[[لَا]] + inaccompli · [[لَيْسَ]] · [[مَا]] + phrase nominale</td><td>[[لَنْ]] + subjonctif</td></tr>
</table>
<ul>
<li>[[إِنْ]] … [[إِلَّا]] : ne… que. [[لَا]] + nom indéfini : aucun.</li>
<li>Futur : [[سَـ]] / [[سَوْفَ]] + inaccompli.</li>
<li>[[قَدْ]] + accompli : déjà, certes ; + inaccompli : il arrive que, certes.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Nie la phrase en gardant le temps.", items=[
            ('[[ذَهَبَ]] (passé)', '[[مَا ذَهَبَ]] ou [[لَمْ يَذْهَبْ]]'), ('[[يَعْلَمُونَ]] (présent)', '[[لَا يَعْلَمُونَ]]'),
            ('[[سَيَفْعَلُ]] (futur)', '[[لَنْ يَفْعَلَ]]'), ('[[هُوَ ظَالِمٌ]]', '[[لَيْسَ ظَالِمًا]] / [[مَا هُوَ بِظَالِمٍ]]'),
        ], une=True),
        dict(consigne="Traduis.", items=[
            ('[[سَوْفَ تَعْلَمُونَ]]', 'vous saurez bientôt'), ('[[لَنْ نُؤْمِنَ لَكَ]]', 'nous ne te croirons pas'),
            ('[[قَدْ سَمِعَ ٱللَّهُ]]', 'Allah a certes entendu (58:1)'), ('[[لَمَّا يَأْتِهِمْ]]', 'cela ne leur est pas encore venu'),
        ]),
        dict(auto='verbe', refs=[(102, 1, 8)], n=8),
    ],
    flash=[
        ("Négation du futur ?", "[[لَنْ]] + subjonctif"),
        ("[[لَمَّا]] + apocopé : sens ?", "pas encore"),
        ("[[قَدْ]] + accompli : sens ?", "déjà, certes (résultat acquis)"),
        ("Différence [[سَـ]] / [[سَوْفَ]] ?", "même futur ; <i>sawfa</i> plus lointain ou solennel"),
        ("[[إِن يَقُولُونَ إِلَّا كَذِبًا]] : traduire.", "ils ne disent que mensonge"),
    ],
    notes={
        (102, 1): "[[أَلْهَىٰكُمُ ٱلتَّكَاثُرُ]] « la course à l'accumulation vous a distraits » : [[ٱلتَّكَاثُرُ]] maṣdar de forme VI, sujet (L29).",
        (102, 5): "[[لَوْ تَعْلَمُونَ عِلْمَ ٱلْيَقِينِ]] « si vous saviez d'une science certaine » : <i>law</i> (L38), complément absolu (L35).",
        (102, 6): "[[لَتَرَوُنَّ]] « vous verrez assurément » : <i>la-</i> + nūn d'insistance (L39).",
    },
)

L[26] = dict(
    objectifs=[
        "former et reconnaître le passif",
        "identifier le sujet du passif (nāʾib al-fāʿil)",
        "comprendre l'emploi coranique du passif",
    ],
    expose=r"""
<p>Le passif [[ٱلْمَبْنِيُّ لِلْمَجْهُولِ]] (« construit pour l'inconnu ») s'obtient en changeant <b>les voyelles</b> du verbe :</p>
<table class="t c">
<tr><th></th><th>actif</th><th>passif</th><th>schème</th></tr>
<tr><td>accompli f. I</td><td class="ar">خَلَقَ · كَتَبَ</td><td class="ar">خُلِقَ · كُتِبَ</td><td class="ar">فُعِلَ (u – i)</td></tr>
<tr><td>inaccompli f. I</td><td class="ar">يَخْلُقُ · يَكْتُبُ</td><td class="ar">يُخْلَقُ · يُكْتَبُ</td><td class="ar">يُفْعَلُ (u – a)</td></tr>
<tr><td>forme II</td><td class="ar">سَيَّرَ · يُسَيِّرُ</td><td class="ar">سُيِّرَ · يُسَيَّرُ</td><td class="ar">فُعِّلَ · يُفَعَّلُ</td></tr>
<tr><td>forme IV</td><td class="ar">أَنزَلَ · يُنزِلُ</td><td class="ar">أُنزِلَ · يُنزَلُ</td><td class="ar">أُفْعِلَ · يُفْعَلُ</td></tr>
<tr><td>concave</td><td class="ar">قَالَ · يَقُولُ</td><td class="ar">قِيلَ · يُقَالُ</td><td></td></tr>
<tr><td>défectueux</td><td class="ar">دَعَا · يَدْعُو</td><td class="ar">دُعِيَ · يُدْعَى</td><td></td></tr>
</table>
<p>Règle simple : à l'accompli, <b>u</b> sur la première consonne et <b>i</b> avant la dernière ; à l'inaccompli, <b>u</b> sur le préfixe et <b>a</b> avant la dernière.</p>
<h3><span class="pastille">1</span>Le sujet du passif</h3>
<p>L'agent n'est pas nommé ; le complément d'objet devient sujet, au <b>nominatif</b> : c'est le <b>nāʾib al-fāʿil</b> [[نَائِبُ ٱلْفَاعِلِ]] (« le remplaçant de l'agent »).</p>
{{ex 2:183|hl=كتب,الصيام|from=ياأيها|to=الصيام|com=[[كُتِبَ عَلَيْكُمُ ٱلصِّيَامُ]] « le jeûne vous a été prescrit » : [[ٱلصِّيَامُ]] nominatif.}}
{{ex 81:1|hl=الشمس,كورت|com=« Quand le soleil <b>sera obscurci</b> » ; [[ٱلشَّمْسُ]] est le sujet du passif.}}
<h3><span class="pastille">2</span>Pourquoi le passif ?</h3>
<p>Le Coran emploie le passif quand l'agent est évident (Allah), quand il importe peu, ou pour mettre en relief l'événement. Les scènes du Jour dernier en sont pleines :</p>
{{ex 81:8|hl=سئلت|com=« et quand on demandera à la fillette enterrée vivante… »}}
{{ex 81:9|hl=قتلت|com=« … pour quel péché elle <b>a été tuée</b> ».}}
{{ex 112:3|hl=يولد|com=[[وَلَمْ يُولَدْ]] « et Il n'a pas été engendré » : passif à l'apocopé.}}
<div class="attention"><span class="lab">Le muṣḥaf vocalise tout</span>Sans voyelles, [[كتب]] peut être <i>kataba</i> ou <i>kutiba</i>. Le texte vocalisé lève l'ambiguïté : regarde toujours la voyelle de la première consonne.</div>
""",
    fiche=dict(
        titre='Le passif', ar='الْمَبْنِيُّ لِلْمَجْهُولِ',
        corps=r"""
<table class="t c">
<tr><th></th><th>accompli</th><th>inaccompli</th></tr>
<tr><td>f. I</td><td class="ar">فُعِلَ</td><td class="ar">يُفْعَلُ</td></tr>
<tr><td>f. II</td><td class="ar">فُعِّلَ</td><td class="ar">يُفَعَّلُ</td></tr>
<tr><td>f. IV</td><td class="ar">أُفْعِلَ</td><td class="ar">يُفْعَلُ</td></tr>
<tr><td>concave · défectueux</td><td class="ar">قِيلَ · دُعِيَ</td><td class="ar">يُقَالُ · يُدْعَى</td></tr>
</table>
<ul><li>Accompli : u … i ; inaccompli : yu … a.</li>
<li>Le complément devient sujet au nominatif (nāʾib al-fāʿil).</li></ul>""",
    ),
    exercices=[
        dict(consigne="Mets au passif (même personne).", items=[
            ('[[خَلَقَ]]', '[[خُلِقَ]]'), ('[[يَعْلَمُ]]', '[[يُعْلَمُ]]'), ('[[أَنْزَلَ]]', '[[أُنْزِلَ]]'),
            ('[[قَالَ]]', '[[قِيلَ]]'), ('[[يَغْفِرُ]]', '[[يُغْفَرُ]]'), ('[[كَذَّبَ]]', '[[كُذِّبَ]]'),
        ]),
        dict(consigne="Traduis.", items=[
            ('[[كُتِبَ عَلَيْكُمُ ٱلْقِتَالُ]]', 'le combat vous a été prescrit (2:216)'), ('[[وَإِذَا قِيلَ لَهُمْ]]', 'et quand on leur dit (2:11)'),
            ('[[أُنزِلَ إِلَيْكَ]]', 'ce qui a été descendu vers toi'), ('[[خُلِقَ ٱلْإِنسَانُ ضَعِيفًا]]', "l'homme a été créé faible (4:28)"),
        ]),
        dict(auto='verbe', refs=[(84, 1, 6)], n=8),
    ],
    flash=[
        ("Passif de [[كَتَبَ]] ?", "[[كُتِبَ]]"),
        ("Voyelles du passif à l'inaccompli ?", "<i>yu-</i> … <i>a</i> : [[يُفْعَلُ]]"),
        ("Qu'est-ce que le nāʾib al-fāʿil ?", "le sujet du passif, au nominatif"),
        ("Passif de [[قَالَ]] ?", "[[قِيلَ]]"),
        ("[[وَلَمْ يُولَدْ]] : traduire.", "et Il n'a pas été engendré"),
    ],
    notes={
        (81, 1): "[[إِذَا]] + accompli = futur (L21). Chaque verset est une proposition « quand… » ; la réponse vient au v. 14.",
        (81, 6): "[[سُجِّرَتْ]] « seront embrasées » : forme II au passif.",
        (81, 14): "[[عَلِمَتْ نَفْسٌ مَّآ أَحْضَرَتْ]] « chaque âme saura ce qu'elle a présenté » : réponse de toute la série.",
    },
)

L[27] = dict(
    objectifs=[
        "reconnaître les formes II, III et IV",
        "connaître leurs sens habituels",
        "conjuguer et dériver chaque forme",
    ],
    expose=r"""
<p>À partir d'une racine, l'arabe forme des verbes « augmentés » [[ٱلْمَزِيد]] en ajoutant une lettre ou en doublant une radicale. Les grammairiens occidentaux les numérotent de I (verbe simple) à X. Les formes II, III et IV ajoutent <b>une</b> lettre.</p>
<table class="t c">
<tr><th>forme</th><th>accompli</th><th>inaccompli</th><th>impératif</th><th>maṣdar</th><th>part. actif</th><th>part. passif</th></tr>
<tr><td>II</td><td class="ar">فَعَّلَ</td><td class="ar">يُفَعِّلُ</td><td class="ar">فَعِّلْ</td><td class="ar">تَفْعِيل</td><td class="ar">مُفَعِّل</td><td class="ar">مُفَعَّل</td></tr>
<tr><td>III</td><td class="ar">فَاعَلَ</td><td class="ar">يُفَاعِلُ</td><td class="ar">فَاعِلْ</td><td class="ar">مُفَاعَلَة · فِعَال</td><td class="ar">مُفَاعِل</td><td class="ar">مُفَاعَل</td></tr>
<tr><td>IV</td><td class="ar">أَفْعَلَ</td><td class="ar">يُفْعِلُ</td><td class="ar">أَفْعِلْ</td><td class="ar">إِفْعَال</td><td class="ar">مُفْعِل</td><td class="ar">مُفْعَل</td></tr>
</table>
<p>Aux trois formes, l'inaccompli a un préfixe en <b>ḍamma</b> ([[يُـ]]) et une <b>kasra</b> avant la dernière radicale.</p>
<h3><span class="pastille">1</span>Forme II : doublement</h3>
<p>Elle intensifie ou rend causatif : [[عَلِمَ]] savoir → [[عَلَّمَ]] enseigner (faire savoir) ; [[نَزَلَ]] descendre → [[نَزَّلَ]] faire descendre (peu à peu) ; [[كَذَبَ]] mentir → [[كَذَّبَ]] traiter de menteur ; [[بَشَّرَ]] annoncer une bonne nouvelle ; [[سَبَّحَ]] glorifier.</p>
{{ex 96:5|hl=علم|com=[[عَلَّمَ ٱلْإِنسَٰنَ مَا لَمْ يَعْلَمْ]] « Il a enseigné à l'homme ce qu'il ne savait pas » : II face à I.}}
<h3><span class="pastille">2</span>Forme III : allongement</h3>
<p>Elle exprime l'action dirigée vers quelqu'un, souvent l'effort ou la réciprocité : [[جَاهَدَ]] lutter, faire effort ; [[قَاتَلَ]] combattre (quelqu'un) ; [[نَادَى]] appeler ; [[حَاسَبَ]] demander des comptes.</p>
<h3><span class="pastille">3</span>Forme IV : préfixe [[أَ]]</h3>
<p>Elle est surtout causative : [[خَرَجَ]] sortir → [[أَخْرَجَ]] faire sortir ; [[نَزَلَ]] → [[أَنزَلَ]] faire descendre, révéler ; [[أَرْسَلَ]] envoyer ; [[أَنذَرَ]] avertir ; [[أَسْلَمَ]] se soumettre ; [[ءَامَنَ]] croire (de <i>aʾmana</i>).</p>
{{ex 18:1|hl=أنزل|com=[[أَنزَلَ عَلَىٰ عَبْدِهِ ٱلْكِتَٰبَ]] « (Il) a fait descendre sur Son serviteur le Livre ».}}
{{ex 18:2|hl=لينذر,ويبشر|from=قيما|to=المؤمنين|com=[[لِّيُنذِرَ]] (IV) et [[يُبَشِّرَ]] (II) : subjonctifs après [[لِـ]].}}
<div class="encadre"><span class="lab">Le réflexe du lecteur</span>Préfixe [[يُ]] + kasra avant la fin → II, III ou IV. Shadda sur la 2<sup>e</sup> radicale → II ; ā après la 1<sup>re</sup> → III ; [[أَ]] / [[يُـ]] sans autre ajout → IV.</div>
""",
    fiche=dict(
        titre='Formes II, III, IV', ar='الْمَزِيدُ بِحَرْفٍ',
        corps=r"""
<table class="t c">
<tr><th></th><th>accompli</th><th>inacc.</th><th>maṣdar</th><th>part. act.</th><th>part. pass.</th><th>sens</th></tr>
<tr><td>II</td><td class="ar">فَعَّلَ</td><td class="ar">يُفَعِّلُ</td><td class="ar">تَفْعِيل</td><td class="ar">مُفَعِّل</td><td class="ar">مُفَعَّل</td><td>intensif, causatif</td></tr>
<tr><td>III</td><td class="ar">فَاعَلَ</td><td class="ar">يُفَاعِلُ</td><td class="ar">مُفَاعَلَة · فِعَال</td><td class="ar">مُفَاعِل</td><td class="ar">مُفَاعَل</td><td>action vers autrui, effort</td></tr>
<tr><td>IV</td><td class="ar">أَفْعَلَ</td><td class="ar">يُفْعِلُ</td><td class="ar">إِفْعَال</td><td class="ar">مُفْعِل</td><td class="ar">مُفْعَل</td><td>causatif</td></tr>
</table>
<ul><li>Indice : préfixe [[يُـ]] + kasra avant la dernière radicale.</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne la forme et le sens.", items=[
            ('[[عَلَّمَ]]', 'II : enseigner'), ('[[أَخْرَجَ]]', 'IV : faire sortir'), ('[[جَاهَدَ]]', 'III : lutter, faire effort'),
            ('[[نَزَّلَ]]', 'II : faire descendre (progressivement)'), ('[[أَرْسَلَ]]', 'IV : envoyer'), ('[[قَاتَلَ]]', 'III : combattre'),
        ]),
        dict(consigne="Donne l'inaccompli (3e m. sg.) et le maṣdar.", items=[
            ('[[عَلَّمَ]]', '[[يُعَلِّمُ]] · [[تَعْلِيم]]'), ('[[أَنْزَلَ]]', '[[يُنْزِلُ]] · [[إِنْزَال]]'),
            ('[[جَاهَدَ]]', '[[يُجَاهِدُ]] · [[جِهَاد]] / [[مُجَاهَدَة]]'), ('[[كَذَّبَ]]', '[[يُكَذِّبُ]] · [[تَكْذِيب]]'),
        ]),
        dict(auto='forme', refs=[(2, 2, 13)], n=10),
    ],
    flash=[
        ("Schème de la forme II à l'accompli ?", "[[فَعَّلَ]]"),
        ("Maṣdar de la forme IV ?", "[[إِفْعَال]]"),
        ("Sens habituel de la forme IV ?", "causatif : faire faire"),
        ("[[يُبَشِّرُ]] : quelle forme ?", "II"),
        ("Inaccompli de [[جَاهَدَ]] ?", "[[يُجَاهِدُ]]"),
    ],
    notes={
        (18, 1): "[[وَلَمْ يَجْعَل لَّهُۥ عِوَجَا]] « et n'y a mis aucune tortuosité » : <i>lam</i> + apocopé.",
        (18, 3): "[[مَّٰكِثِينَ فِيهِ أَبَدًا]] « où ils demeureront éternellement » : participe à l'accusatif, état (L36).",
        (18, 5): "[[كَبُرَتْ كَلِمَةً]] « quelle énorme parole ! » : verbe de qualité + spécification (L36).",
    },
)

L[28] = dict(
    objectifs=[
        "reconnaître les formes V à X",
        "connaître leurs sens habituels",
        "repérer les assimilations de la forme VIII",
    ],
    expose=r"""
<table class="t c">
<tr><th>forme</th><th>accompli</th><th>inaccompli</th><th>maṣdar</th><th>part. actif</th><th>sens habituel</th><th>exemples</th></tr>
<tr><td>V</td><td class="ar">تَفَعَّلَ</td><td class="ar">يَتَفَعَّلُ</td><td class="ar">تَفَعُّل</td><td class="ar">مُتَفَعِّل</td><td>réfléchi de II</td><td class="ar">تَذَكَّرَ، تَوَكَّلَ، تَزَكَّى</td></tr>
<tr><td>VI</td><td class="ar">تَفَاعَلَ</td><td class="ar">يَتَفَاعَلُ</td><td class="ar">تَفَاعُل</td><td class="ar">مُتَفَاعِل</td><td>réciproque</td><td class="ar">تَعَارَفَ، تَنَابَزَ، تَوَاصَى</td></tr>
<tr><td>VII</td><td class="ar">ٱنْفَعَلَ</td><td class="ar">يَنْفَعِلُ</td><td class="ar">ٱنْفِعَال</td><td class="ar">مُنْفَعِل</td><td>subir, se faire</td><td class="ar">ٱنقَلَبَ، ٱنفَطَرَ، ٱنشَقَّ</td></tr>
<tr><td>VIII</td><td class="ar">ٱفْتَعَلَ</td><td class="ar">يَفْتَعِلُ</td><td class="ar">ٱفْتِعَال</td><td class="ar">مُفْتَعِل</td><td>réfléchi, pour soi</td><td class="ar">ٱجْتَنَبَ، ٱخْتَلَفَ، ٱتَّبَعَ</td></tr>
<tr><td>IX</td><td class="ar">ٱفْعَلَّ</td><td class="ar">يَفْعَلُّ</td><td class="ar">ٱفْعِلَال</td><td class="ar">مُفْعَلّ</td><td>couleurs</td><td class="ar">ٱبْيَضَّ، ٱسْوَدَّ</td></tr>
<tr><td>X</td><td class="ar">ٱسْتَفْعَلَ</td><td class="ar">يَسْتَفْعِلُ</td><td class="ar">ٱسْتِفْعَال</td><td class="ar">مُسْتَفْعِل</td><td>demander, estimer</td><td class="ar">ٱسْتَغْفَرَ، ٱسْتَعَانَ، ٱسْتَكْبَرَ</td></tr>
</table>
<p>Les formes VII à X commencent par une hamzat al-waṣl. Leur inaccompli a un préfixe en <b>fatḥa</b>, comme la forme I.</p>
<h3><span class="pastille">1</span>Formes V et VI</h3>
<p>Elles ajoutent [[تَـ]] devant les formes II et III : [[ذَكَّرَ]] rappeler → [[تَذَكَّرَ]] se rappeler ; [[عَارَفَ]] → [[تَعَارَفَ]] se connaître mutuellement. À l'inaccompli, un des deux t tombe parfois ([[تَنَزَّلُ]] = <i>tatanazzalu</i>, 97:4) ou s'assimile ([[يَذَّكَّرُ]] = <i>yatadhakkaru</i>, [[يَزَّكَّىٰ]] = <i>yatazakkā</i>).</p>
{{ex 49:13|hl=لتعارفوا|from=وجعلناكم|to=لتعارفوا|com=[[لِتَعَارَفُوٓا۟]] « pour que vous vous connaissiez mutuellement » : VI (= <i>li-tataʿārafū</i>).}}
<h3><span class="pastille">2</span>Forme VIII et ses assimilations</h3>
<p>Le [[تـ]] infixé s'adapte aux consonnes voisines :</p>
<ul>
<li>racine en و ou ي : [[ٱتَّقَى]] (و ق ي), [[ٱتَّصَلَ]] ; aussi [[ٱتَّخَذَ]] (ء خ ذ) ;</li>
<li>après ص ض ط ظ, t → ṭ : [[ٱصْطَبَرَ]] (ص ب ر), [[ٱضْطُرَّ]] ;</li>
<li>après د ذ ز, t → d : [[ٱزْدَجَرَ]], [[ٱدَّكَرَ]].</li>
</ul>
{{ex 49:12|hl=اجتنبوا,تجسسوا,يغتب|from=ياأيها|to=بعضا|com=[[ٱجْتَنِبُوا۟]] (VIII) « évitez » ; [[تَجَسَّسُوا۟]] (V, un t tombé) « espionnez » ; [[يَغْتَب]] (VIII) « médise ».}}
<h3><span class="pastille">3</span>Forme X</h3>
<p>Elle exprime souvent la <b>demande</b> : [[غَفَرَ]] pardonner → [[ٱسْتَغْفَرَ]] demander pardon ; [[عَانَ]]/[[أَعَانَ]] aider → [[ٱسْتَعَانَ]] demander l'aide ([[نَسْتَعِينُ]], 1:5) ; ou l'estimation : [[ٱسْتَكْبَرَ]] se croire grand.</p>
{{ex 110:3|hl=واستغفره|com=« et demande-Lui pardon » : impératif X + pronom.}}
""",
    fiche=dict(
        titre='Formes V à X', ar='الْمَزِيدُ بِحَرْفَيْنِ وَثَلَاثَةٍ',
        corps=r"""
<table class="t c">
<tr><th></th><th>accompli</th><th>inacc.</th><th>maṣdar</th><th>sens</th></tr>
<tr><td>V</td><td class="ar">تَفَعَّلَ</td><td class="ar">يَتَفَعَّلُ</td><td class="ar">تَفَعُّل</td><td>réfléchi de II</td></tr>
<tr><td>VI</td><td class="ar">تَفَاعَلَ</td><td class="ar">يَتَفَاعَلُ</td><td class="ar">تَفَاعُل</td><td>réciproque</td></tr>
<tr><td>VII</td><td class="ar">ٱنْفَعَلَ</td><td class="ar">يَنْفَعِلُ</td><td class="ar">ٱنْفِعَال</td><td>subir</td></tr>
<tr><td>VIII</td><td class="ar">ٱفْتَعَلَ</td><td class="ar">يَفْتَعِلُ</td><td class="ar">ٱفْتِعَال</td><td>réfléchi</td></tr>
<tr><td>IX</td><td class="ar">ٱفْعَلَّ</td><td class="ar">يَفْعَلُّ</td><td class="ar">ٱفْعِلَال</td><td>couleur</td></tr>
<tr><td>X</td><td class="ar">ٱسْتَفْعَلَ</td><td class="ar">يَسْتَفْعِلُ</td><td class="ar">ٱسْتِفْعَال</td><td>demander</td></tr>
</table>
<ul><li>VIII : [[ٱتَّقَى]] (و), [[ٱصْطَبَرَ]] (ط), [[ٱزْدَجَرَ]] (د). V/VI : un t peut tomber ou s'assimiler ([[تَنَزَّلُ]], [[يَذَّكَّرُ]]).</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne la forme et le sens.", items=[
            ('[[تَذَكَّرَ]]', 'V : se rappeler'), ('[[ٱسْتَغْفَرَ]]', 'X : demander pardon'), ('[[ٱخْتَلَفَ]]', 'VIII : diverger'),
            ('[[تَعَارَفَ]]', 'VI : se connaître mutuellement'), ('[[ٱنْقَلَبَ]]', 'VII : se retourner'), ('[[ٱتَّقَى]]', 'VIII (و ق ي) : craindre, se prémunir'),
            ('[[تَوَكَّلَ]]', "V : s'en remettre à"), ('[[ٱسْتَكْبَرَ]]', "X : s'enorgueillir"),
        ]),
        dict(auto='forme', refs=[(3, 102, 105)], n=10),
    ],
    flash=[
        ("Schème de la forme X ?", "[[ٱسْتَفْعَلَ]] — [[يَسْتَفْعِلُ]]"),
        ("Sens habituel de la forme VI ?", "réciprocité"),
        ("Racine de [[ٱتَّقَى]] ?", "و ق ي (forme VIII)"),
        ("[[يَذَّكَّرُ]] = ?", "<i>yatadhakkaru</i> (forme V)"),
        ("Maṣdar de la forme VIII ?", "[[ٱفْتِعَال]]"),
    ],
    notes={
        (49, 10): "[[إِنَّمَا ٱلْمُؤْمِنُونَ إِخْوَةٌ]] « les croyants ne sont que des frères » : restriction (L37). [[فَأَصْلِحُوا۟]] : impératif IV.",
        (49, 11): "[[عَسَىٰٓ أَن يَكُونُوا۟ خَيْرًا مِّنْهُمْ]] « il se peut qu'ils soient meilleurs qu'eux » : <i>ʿasā</i> + <i>an</i> + subjonctif.",
        (49, 12): "[[أَيُحِبُّ أَحَدُكُمْ أَن يَأْكُلَ]] : question rhétorique ; [[مَيْتًا]] est un état (L36).",
    },
)

L[29] = dict(
    objectifs=[
        "reconnaître le maṣdar (nom verbal) à chaque forme",
        "l'employer comme nom et comme complément absolu",
        "comprendre l'annexion au maṣdar",
    ],
    expose=r"""
<p>Le <b>maṣdar</b> [[مَصْدَر]] est le nom de l'action : « le fait de… ». [[نَصَرَ]] secourir → [[نَصْر]] le secours ; [[عَلِمَ]] savoir → [[عِلْم]] le savoir.</p>
<h3><span class="pastille">1</span>Forme I : des schèmes à apprendre</h3>
<p>Le maṣdar de la forme I n'est pas prévisible ; il s'apprend avec le verbe. Schèmes fréquents :</p>
<table class="t">
<tr><th class="ar">schème</th><th>exemples</th><th class="ar">schème</th><th>exemples</th></tr>
<tr><td class="ar">فَعْل</td><td>[[نَصْر]] [[حَمْد]] [[قَتْل]] [[صَبْر]]</td><td class="ar">فُعُول</td><td>[[دُخُول]] [[خُرُوج]] [[قُعُود]]</td></tr>
<tr><td class="ar">فِعْل</td><td>[[عِلْم]] [[ذِكْر]] [[كِذْب]]</td><td class="ar">فِعَالَة</td><td>[[عِبَادَة]] [[شَهَادَة]]</td></tr>
<tr><td class="ar">فُعْل</td><td>[[شُكْر]] [[كُفْر]] [[ظُلْم]]</td><td class="ar">فَعَال</td><td>[[فَسَاد]] [[ضَلَال]]</td></tr>
<tr><td class="ar">فُعْلَان</td><td>[[غُفْرَان]] [[كُفْرَان]] [[قُرْءَان]]</td><td class="ar">فِعْلَى · فُعْلَى</td><td>[[ذِكْرَى]] [[بُشْرَى]]</td></tr>
</table>
<h3><span class="pastille">2</span>Formes dérivées : des schèmes réguliers</h3>
<table class="t c">
<tr><th>II</th><th>III</th><th>IV</th><th>V</th><th>VI</th><th>VII</th><th>VIII</th><th>X</th></tr>
<tr><td class="ar">تَفْعِيل</td><td class="ar">مُفَاعَلَة · فِعَال</td><td class="ar">إِفْعَال</td><td class="ar">تَفَعُّل</td><td class="ar">تَفَاعُل</td><td class="ar">ٱنْفِعَال</td><td class="ar">ٱفْتِعَال</td><td class="ar">ٱسْتِفْعَال</td></tr>
<tr><td class="ar">تَرْتِيل</td><td class="ar">جِهَاد</td><td class="ar">إِيمَان</td><td class="ar">تَذَكُّر</td><td class="ar">تَكَاثُر</td><td class="ar">ٱنفِصَام</td><td class="ar">ٱخْتِلَاف</td><td class="ar">ٱسْتِغْفَار</td></tr>
</table>
<h3><span class="pastille">3</span>Emplois</h3>
<ul>
<li>Comme un <b>nom</b> : sujet, complément, annexé. L'agent de l'action se met souvent au génitif : [[نَصْرُ ٱللَّهِ]] « le secours d'Allah » (= Allah secourt).</li>
<li>Comme <b>complément absolu</b> [[مَفْعُولٌ مُطْلَق]] : le maṣdar du verbe lui-même, à l'accusatif, pour insister ou préciser la manière (L35).</li>
</ul>
{{ex 110:1|hl=نصر,والفتح|com=[[نَصْرُ ٱللَّهِ]] : maṣdar annexé à son agent ; [[ٱلْفَتْحُ]] « la conquête » (maṣdar de [[فَتَحَ]]).}}
{{ex 73:4|hl=ورتل,ترتيلا|com=[[وَرَتِّلِ ٱلْقُرْءَانَ تَرْتِيلًا]] « et récite le Coran posément » : impératif II + son maṣdar.}}
{{ex 73:8|hl=وتبتل,تبتيلا|com=Verbe de forme V, maṣdar de forme II : l'usage le permet.}}
{{ex 4:164|hl=وكلم,تكليما|from=وكلم|to=تكليما|com=« et Allah a parlé à Mūsā <b>réellement</b> » : le complément absolu exclut le sens figuré.}}
""",
    fiche=dict(
        titre='Le maṣdar', ar='الْمَصْدَرُ',
        corps=r"""
<ul>
<li>Nom de l'action : [[نَصَرَ]] → [[نَصْر]] ; forme I : schème à apprendre ([[فَعْل]], [[فِعْل]], [[فُعُول]], [[فِعَالَة]]…).</li>
</ul>
<table class="t c"><tr><th>II</th><th>III</th><th>IV</th><th>V</th><th>VI</th><th>VII</th><th>VIII</th><th>X</th></tr>
<tr><td class="ar">تَفْعِيل</td><td class="ar">مُفَاعَلَة/فِعَال</td><td class="ar">إِفْعَال</td><td class="ar">تَفَعُّل</td><td class="ar">تَفَاعُل</td><td class="ar">ٱنْفِعَال</td><td class="ar">ٱفْتِعَال</td><td class="ar">ٱسْتِفْعَال</td></tr></table>
<ul><li>Agent au génitif : [[نَصْرُ ٱللَّهِ]]. Complément absolu : [[رَتِّلِ ٱلْقُرْءَانَ تَرْتِيلًا]].</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne le maṣdar.", items=[
            ('[[أَسْلَمَ]] (IV)', '[[إِسْلَام]]'), ('[[سَبَّحَ]] (II)', '[[تَسْبِيح]]'), ('[[ٱسْتَغْفَرَ]] (X)', '[[ٱسْتِغْفَار]]'),
            ('[[ٱخْتَلَفَ]] (VIII)', '[[ٱخْتِلَاف]]'), ('[[أَحْسَنَ]] (IV)', '[[إِحْسَان]]'), ('[[تَكَاثَرَ]] (VI)', '[[تَكَاثُر]]'),
            ('[[عَبَدَ]] (I)', '[[عِبَادَة]]'), ('[[شَكَرَ]] (I)', '[[شُكْر]] (aussi [[شُكُور]])'),
        ]),
        dict(auto='forme', refs=[(73, 11, 20)], n=8),
    ],
    flash=[
        ("Maṣdar de la forme II ?", "[[تَفْعِيل]]"),
        ("Maṣdar de [[آمَنَ]] ?", "[[إِيمَان]]"),
        ("[[نَصْرُ ٱللَّهِ]] : qui secourt ?", "Allah (agent au génitif)"),
        ("Qu'est-ce que le complément absolu ?", "le maṣdar du verbe à l'accusatif : [[تَرْتِيلًا]]"),
        ("Maṣdar de la forme X ?", "[[ٱسْتِفْعَال]]"),
    ],
    notes={
        (110, 2): "[[يَدْخُلُونَ فِى دِينِ ٱللَّهِ أَفْوَاجًا]] « entrer en foule dans la religion d'Allah » : [[أَفْوَاجًا]] est un état (L36).",
        (73, 2): "[[قُمِ ٱلَّيْلَ إِلَّا قَلِيلًا]] « veille la nuit, sauf un peu » : [[ٱلَّيْلَ]] complément de temps (L35), exception (L37).",
        (73, 6): "[[إِنَّ نَاشِئَةَ ٱلَّيْلِ هِىَ أَشَدُّ وَطْـًٔا]] « la veillée de la nuit est plus efficace » : élatif + spécification.",
    },
)

L[30] = dict(
    objectifs=[
        "former les participes actif et passif à toutes les formes",
        "les employer comme adjectifs, noms et « quasi-verbes »",
        "lire une série de participes",
    ],
    expose=r"""
<h3><span class="pastille">1</span>Formation</h3>
<table class="t c">
<tr><th></th><th>participe actif (celui qui fait)</th><th>participe passif (ce qui subit)</th></tr>
<tr><td>forme I</td><td class="ar">فَاعِل — كَافِر، عَالِم، خَاشِع</td><td class="ar">مَفْعُول — مَغْضُوب، مَعْلُوم</td></tr>
<tr><td>formes dérivées</td><td>[[مُـ]] + kasra avant la fin<br><span class="ar">مُؤْمِن (IV)، مُعَلِّم (II)، مُجَاهِد (III)، مُتَّقٍ (VIII)، مُسْتَقِيم (X)</span></td><td>[[مُـ]] + fatḥa avant la fin<br><span class="ar">مُنزَل (IV)، مُرْسَل (IV)، مُقَرَّب (II)، مُطَهَّر (II)</span></td></tr>
</table>
<p>À partir du schème de l'inaccompli, on remplace le préfixe par [[مُـ]] : [[يُؤْمِنُ]] → [[مُؤْمِن]] ; [[يَسْتَقِيمُ]] → [[مُسْتَقِيم]]. Kasra : actif ; fatḥa : passif ([[مُرْسِل]] qui envoie / [[مُرْسَل]] envoyé).</p>
<h3><span class="pastille">2</span>Emplois</h3>
<ul>
<li><b>adjectif</b> : [[ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ]] ;</li>
<li><b>nom</b> : [[ٱلْمُؤْمِنُ]] « le croyant », [[ٱلْكَافِرُونَ]] « les mécréants » ;</li>
<li><b>attribut</b> : [[إِنِّى جَاعِلٌ فِى ٱلْأَرْضِ خَلِيفَةً]] « Je vais établir sur la terre un successeur » (2:30) ;</li>
<li><b>avec un complément d'objet</b>, comme un verbe : [[خَلِيفَةً]] ci-dessus ; [[ءَاخِذِينَ مَآ ءَاتَىٰهُمْ رَبُّهُمْ]] « recevant ce que leur Seigneur leur a donné » (51:16).</li>
</ul>
{{ex 51:15|hl=المتقين|com=[[ٱلْمُتَّقِينَ]] : participe actif VIII (و ق ي), pluriel, nom de <i>inna</i>.}}
{{ex 51:16|hl=آخذين|com=[[ءَاخِذِينَ]] : participe actif I avec complément d'objet [[مَآ]].}}
<h3><span class="pastille">3</span>Une série célèbre</h3>
<p>Le verset 35 de la sourate al-Aḥzāb énumère dix qualités, chacune au masculin et au féminin pluriels :</p>
{{ex 33:35|hl=المسلمين,والمسلمات,والمؤمنين,والمؤمنات|from=إن|to=والقانتات|com=Participes actifs IV ([[مُسْلِم]], [[مُؤْمِن]]) et I ([[قَانِت]]) : accusatif après <i>inna</i> (<i>-īna</i>, <i>-āti</i>).}}
<div class="attention"><span class="lab">Verbes faibles</span>Le participe actif des concaves met une hamza ([[قَائِل]] de [[قَالَ]], [[صَائِم]] de [[صَامَ]]) ; celui des défectueux perd la 3<sup>e</sup> radicale au nominatif/génitif indéfinis ([[دَاعٍ]], [[بَاقٍ]], [[مُتَّقٍ]]).</div>
""",
    fiche=dict(
        titre='Les participes', ar='اسْمُ الْفَاعِلِ وَاسْمُ الْمَفْعُولِ',
        corps=r"""
<table class="t c">
<tr><th></th><th>actif</th><th>passif</th></tr>
<tr><td>forme I</td><td class="ar">فَاعِل</td><td class="ar">مَفْعُول</td></tr>
<tr><td>formes II–X</td><td>[[مُـ]] + kasra : [[مُؤْمِن]], [[مُسْتَقِيم]]</td><td>[[مُـ]] + fatḥa : [[مُرْسَل]], [[مُقَرَّب]]</td></tr>
</table>
<ul><li>Emplois : adjectif, nom, attribut, et quasi-verbe avec complément d'objet ([[آخِذِينَ مَا آتَاهُمْ]]).</li>
<li>Concaves : [[قَائِل]] ; défectueux : [[دَاعٍ]], [[مُتَّقٍ]].</li></ul>""",
    ),
    exercices=[
        dict(consigne="Donne le participe actif et le participe passif.", items=[
            ('[[نَصَرَ]] (I)', '[[نَاصِر]] · [[مَنْصُور]]'), ('[[أَرْسَلَ]] (IV)', '[[مُرْسِل]] · [[مُرْسَل]]'),
            ('[[عَلَّمَ]] (II)', '[[مُعَلِّم]] · [[مُعَلَّم]]'), ('[[غَفَرَ]] (I)', '[[غَافِر]] · [[مَغْفُور]]'),
            ('[[أَنْزَلَ]] (IV)', '[[مُنْزِل]] · [[مُنْزَل]]'), ('[[قَرَّبَ]] (II)', '[[مُقَرِّب]] · [[مُقَرَّب]]'),
        ]),
        dict(auto='forme', refs=[(33, 35, 36)], n=10),
    ],
    flash=[
        ("Participe actif de la forme I ?", "[[فَاعِل]]"),
        ("[[مُرْسِل]] ou [[مُرْسَل]] : lequel est passif ?", "[[مُرْسَل]] (fatḥa)"),
        ("Participe actif de [[ٱسْتَقَامَ]] ?", "[[مُسْتَقِيم]]"),
        ("Un participe peut-il avoir un complément d'objet ?", "oui : [[ءَاخِذِينَ مَآ ءَاتَىٰهُمْ]]"),
        ("Participe passif de [[غَضِبَ]] ?", "[[مَغْضُوب]]"),
    ],
    notes={
        (33, 35): "[[أَعَدَّ ٱللَّهُ لَهُم مَّغْفِرَةً وَأَجْرًا عَظِيمًا]] : khabar de <i>inna</i> = phrase verbale (L19).",
        (51, 17): "[[كَانُوا۟ قَلِيلًا مِّنَ ٱلَّيْلِ مَا يَهْجَعُونَ]] « ils dormaient peu la nuit » : <i>kāna</i> (L20).",
        (51, 18): "[[وَبِٱلْأَسْحَارِ هُمْ يَسْتَغْفِرُونَ]] « et aux dernières heures de la nuit, ils demandaient pardon » : complément en tête.",
    },
)

L[31] = dict(
    objectifs=[
        "conjuguer les verbes assimilés (1re radicale و)",
        "conjuguer les verbes concaves (2e radicale و/ي)",
        "reconnaître ces verbes sous leurs formes courtes",
    ],
    expose=r"""
<p>Un verbe est « faible » quand une de ses radicales est [[و]] ou [[ي]] (ou un alif qui en provient). Ces lettres se transforment ou disparaissent ; or ces verbes sont parmi les plus fréquents du Coran ([[قَالَ]] : 1 618 fois ; [[كَانَ]] : 1 358 fois).</p>
<h3><span class="pastille">1</span>L'assimilé (mithāl) : و en 1<sup>re</sup> radicale</h3>
<p>À l'accompli, rien ne change : [[وَعَدَ]], [[وَجَدَ]], [[وَضَعَ]], [[وَهَبَ]]. À l'inaccompli, le [[و]] <b>tombe</b> (surtout quand la voyelle centrale est i) :</p>
<table class="t c">
<tr><th>accompli</th><th>inaccompli</th><th>impératif</th><th>sens</th></tr>
<tr><td class="ar">وَعَدَ</td><td class="ar">يَعِدُ</td><td class="ar">عِدْ</td><td>promettre</td></tr>
<tr><td class="ar">وَجَدَ</td><td class="ar">يَجِدُ</td><td class="ar">جِدْ</td><td>trouver</td></tr>
<tr><td class="ar">وَهَبَ</td><td class="ar">يَهَبُ</td><td class="ar">هَبْ</td><td>donner</td></tr>
<tr><td class="ar">وَضَعَ</td><td class="ar">يَضَعُ</td><td class="ar">ضَعْ</td><td>poser</td></tr>
<tr><td class="ar">وَلَدَ</td><td class="ar">يَلِدُ</td><td>—</td><td>engendrer</td></tr>
</table>
{{ex 19:19|hl=لأهب|com=[[لِأَهَبَ لَكِ غُلَٰمًا]] « pour te faire don d'un garçon » : <i>ahaba</i>, de [[وَهَبَ]], au subjonctif.}}
<h3><span class="pastille">2</span>Le concave (ajwaf) : و/ي en 2<sup>e</sup> radicale</h3>
<p>À l'accompli, la 2<sup>e</sup> radicale devient <b>ā</b> : [[قَالَ]] (ق و ل), [[كَانَ]] (ك و ن), [[خَافَ]] (خ و ف), [[جَاءَ]] (ج ي ء), [[شَاءَ]] (ش ي ء). Devant une terminaison consonantique, ā devient une voyelle brève : <b>u</b> pour les verbes en و du type <i>yafʿulu</i>, <b>i</b> pour les autres.</p>
<table class="t c">
<tr><th></th><th class="ar">قَالَ (u)</th><th class="ar">كَانَ (u)</th><th class="ar">خَافَ (i)</th><th class="ar">جَاءَ (i)</th></tr>
<tr><td>il</td><td class="ar">قَالَ</td><td class="ar">كَانَ</td><td class="ar">خَافَ</td><td class="ar">جَاءَ</td></tr>
<tr><td>ils</td><td class="ar">قَالُوا</td><td class="ar">كَانُوا</td><td class="ar">خَافُوا</td><td class="ar">جَاءُوا</td></tr>
<tr><td>tu (m.)</td><td class="ar">قُلْتَ</td><td class="ar">كُنْتَ</td><td class="ar">خِفْتَ</td><td class="ar">جِئْتَ</td></tr>
<tr><td>je</td><td class="ar">قُلْتُ</td><td class="ar">كُنْتُ</td><td class="ar">خِفْتُ</td><td class="ar">جِئْتُ</td></tr>
<tr><td>inaccompli</td><td class="ar">يَقُولُ</td><td class="ar">يَكُونُ</td><td class="ar">يَخَافُ</td><td class="ar">يَجِيءُ</td></tr>
<tr><td>apocopé</td><td class="ar">لَمْ يَقُلْ</td><td class="ar">لَمْ يَكُنْ</td><td class="ar">لَمْ يَخَفْ</td><td class="ar">لَمْ يَجِئْ</td></tr>
<tr><td>impératif</td><td class="ar">قُلْ</td><td class="ar">كُنْ</td><td class="ar">خَفْ</td><td class="ar">جِئْ</td></tr>
<tr><td>passif</td><td class="ar">قِيلَ · يُقَالُ</td><td>—</td><td>—</td><td class="ar">جِيءَ</td></tr>
</table>
<p>À l'apocopé et à l'impératif, la voyelle longue s'abrège devant le sukūn : <i>yaqūlu</i> → <i>lam yaqul</i>, <i>qul</i>.</p>
{{ex 19:18|hl=قالت,أعوذ,كنت|com=[[قَالَتْ]] « elle dit » ; [[أَعُوذُ]] « je cherche refuge » ; [[كُنتَ]] « tu es » (u bref devant -ta).}}
{{ex 19:20|hl=قالت,يمسسني,أك|com=[[وَلَمْ أَكُ بَغِيًّا]] « et je n'ai pas été impudique » : apocopé de [[كَانَ]] abrégé en <i>aku</i>.}}
<h3><span class="pastille">3</span>Dans les formes dérivées</h3>
<p>Forme IV : [[أَقَامَ يُقِيمُ]] (accomplir), [[أَرَادَ يُرِيدُ]] (vouloir), [[أَصَابَ يُصِيبُ]] (atteindre) ; forme X : [[ٱسْتَقَامَ يَسْتَقِيمُ]] ; forme VIII : [[ٱخْتَارَ يَخْتَارُ]]. Participes : [[قَائِل]], [[مُقِيم]], [[مُسْتَقِيم]].</p>
""",
    fiche=dict(
        titre='Assimilés et concaves', ar='الْمِثَالُ وَالْأَجْوَفُ',
        corps=r"""
<ul>
<li><b>Assimilé</b> (و ـ ـ) : و tombe à l'inaccompli et à l'impératif : [[وَعَدَ يَعِدُ عِدْ]], [[وَهَبَ يَهَبُ هَبْ]], [[وَجَدَ يَجِدُ]].</li>
<li><b>Concave</b> (ـ و/ي ـ) : ā à l'accompli ([[قَالَ]], [[خَافَ]]) ; voyelle brève devant consonne : [[قُلْتُ]] [[كُنْتُ]] / [[خِفْتُ]] [[جِئْتُ]].</li>
<li>Inaccompli [[يَقُولُ]] [[يَخَافُ]] [[يَسِيرُ]] ; apocopé et impératif abrégés : [[لَمْ يَقُلْ]], [[قُلْ]], [[لَمْ يَكُنْ]] / [[لَمْ يَكُ]].</li>
<li>Passif : [[قِيلَ]] [[يُقَالُ]]. Dérivés : [[أَقَامَ يُقِيمُ]], [[أَرَادَ يُرِيدُ]], [[ٱسْتَقَامَ]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Conjugue.", items=[
            ('[[قَالَ]], 1<sup>re</sup> pl. accompli', '[[قُلْنَا]]'), ('[[كَانَ]], 2<sup>e</sup> m. pl. accompli', '[[كُنْتُمْ]]'),
            ('[[خَافَ]], 3<sup>e</sup> m. pl. inaccompli', '[[يَخَافُونَ]]'), ('[[وَعَدَ]], 3<sup>e</sup> m. sg. inaccompli', '[[يَعِدُ]]'),
            ('[[قَامَ]], impératif m. sg.', '[[قُمْ]]'), ('[[قَالَ]], apocopé 3<sup>e</sup> m. sg.', '[[لَمْ يَقُلْ]]'),
            ('[[أَرَادَ]], 1<sup>re</sup> pl. inaccompli', '[[نُرِيدُ]]'), ('[[وَهَبَ]], impératif m. sg.', '[[هَبْ]]'),
        ]),
        dict(auto='verbe', refs=[(19, 7, 12)], n=10),
    ],
    flash=[
        ("Inaccompli de [[وَعَدَ]] ?", "[[يَعِدُ]]"),
        ("[[قُلْتُ]] : pourquoi u et non ā ?", "concave : voyelle brève devant consonne"),
        ("Apocopé de [[يَكُونُ]] ?", "[[لَمْ يَكُنْ]] (ou [[لَمْ يَكُ]])"),
        ("Impératif de [[قَالَ]] ?", "[[قُلْ]]"),
        ("Passif de [[قَالَ]] ?", "[[قِيلَ]]"),
    ],
    notes={
        (19, 16): "[[وَٱذْكُرْ فِى ٱلْكِتَٰبِ مَرْيَمَ]] « et mentionne, dans le Livre, Maryam » : impératif ; [[مَرْيَمَ]] diptote.",
        (19, 17): "[[فَتَمَثَّلَ لَهَا بَشَرًا سَوِيًّا]] « il prit pour elle la forme d'un homme parfait » : état (L36).",
        (19, 21): "[[وَلِنَجْعَلَهُۥٓ ءَايَةً]] « et pour faire de lui un signe » : <i>li-</i> + subjonctif.",
    },
)

L[32] = dict(
    objectifs=[
        "conjuguer les verbes défectueux (3e radicale و/ي)",
        "conjuguer les verbes sourds et hamzés",
        "reconnaître les formes irrégulières de [[رَأَى]], [[أَتَى]], [[أَخَذَ]]",
    ],
    expose=r"""
<h3><span class="pastille">1</span>Le défectueux (nāqiṣ) : و/ي en 3<sup>e</sup> radicale</h3>
<table class="t c">
<tr><th></th><th class="ar">دَعَا (د ع و)</th><th class="ar">رَمَى (ر م ي)</th><th class="ar">خَشِيَ (خ ش ي)</th></tr>
<tr><td>il</td><td class="ar">دَعَا</td><td class="ar">رَمَى</td><td class="ar">خَشِيَ</td></tr>
<tr><td>elle</td><td class="ar">دَعَتْ</td><td class="ar">رَمَتْ</td><td class="ar">خَشِيَتْ</td></tr>
<tr><td>ils</td><td class="ar">دَعَوْا</td><td class="ar">رَمَوْا</td><td class="ar">خَشُوا</td></tr>
<tr><td>je</td><td class="ar">دَعَوْتُ</td><td class="ar">رَمَيْتُ</td><td class="ar">خَشِيتُ</td></tr>
<tr><td>inaccompli</td><td class="ar">يَدْعُو</td><td class="ar">يَرْمِي</td><td class="ar">يَخْشَى</td></tr>
<tr><td>ils (inacc.)</td><td class="ar">يَدْعُونَ</td><td class="ar">يَرْمُونَ</td><td class="ar">يَخْشَوْنَ</td></tr>
<tr><td>subjonctif</td><td class="ar">لَنْ يَدْعُوَ</td><td class="ar">لَنْ يَرْمِيَ</td><td class="ar">لَنْ يَخْشَى</td></tr>
<tr><td>apocopé</td><td class="ar">لَمْ يَدْعُ</td><td class="ar">لَمْ يَرْمِ</td><td class="ar">لَمْ يَخْشَ</td></tr>
<tr><td>impératif</td><td class="ar">ٱدْعُ</td><td class="ar">ٱرْمِ</td><td class="ar">ٱخْشَ</td></tr>
</table>
<p>Retenir : la voyelle longue finale <b>tombe à l'apocopé et à l'impératif</b> ([[ٱهْدِنَا]] de [[هَدَى]]). Beaucoup de formes dérivées sont défectueuses : [[أَعْطَى]] (IV), [[أَلْقَى]] (IV), [[ٱتَّقَى]] (VIII), [[تَوَلَّى]] (V), [[ٱسْتَغْنَى]] (X).</p>
{{ex 92:5|hl=أعطى,واتقى|com=[[أَعْطَىٰ]] « il a donné » (IV) ; [[ٱتَّقَىٰ]] « il a craint (Allah) » (VIII).}}
{{ex 92:8|hl=بخل,واستغنى|com=[[ٱسْتَغْنَىٰ]] « il s'est cru sans besoin » (X).}}
<h3><span class="pastille">2</span>Le sourd (muḍāʿaf) : 2<sup>e</sup> = 3<sup>e</sup> radicale</h3>
<p>Les deux lettres identiques se fondent sous une shadda : [[مَدَّ يَمُدُّ]] étendre, [[ظَنَّ يَظُنُّ]] penser, [[مَسَّ يَمَسُّ]] toucher, [[ضَلَّ يَضِلُّ]] s'égarer. Elles se séparent devant une terminaison consonantique : [[ظَنَنتُمْ]], [[ضَلَلْتُ]] ; à l'apocopé, on trouve les deux : [[لَمْ يَمْسَسْنِى]] (19:20) ou [[لَمْ يَمَسَّ]].</p>
<h3><span class="pastille">3</span>Le hamzé</h3>
<p>La hamza se comporte comme une consonne, mais change de support selon les voyelles ([[سَأَلَ]], [[يَسْأَلُ]], [[سُئِلَ]]). Trois verbes très courants ont un impératif abrégé : [[أَخَذَ]] → [[خُذْ]] « prends », [[أَكَلَ]] → [[كُلْ]] « mange », [[أَمَرَ]] → [[مُرْ]] / [[وَأْمُرْ]] « ordonne ».</p>
<h3><span class="pastille">4</span>Trois verbes à connaître par cœur</h3>
<ul>
<li>[[رَأَى]] voir : inaccompli [[يَرَى]] (la hamza disparaît), apocopé [[لَمْ يَرَ]] ([[أَلَمْ تَرَ]] « n'as-tu pas vu ? »), passif [[يُرَى]] ; forme IV [[أَرَى يُرِي]] faire voir.</li>
<li>[[أَتَى]] venir : [[يَأْتِي]], [[لَمْ يَأْتِ]], impératif [[ٱئْتِ]] ; forme IV [[ءَاتَى يُؤْتِي]] donner (de <i>aʾtā</i>).</li>
<li>[[جَاءَ]] venir (concave + hamzé) : [[يَجِيءُ]], [[جِئْتُ]].</li>
</ul>
{{ex 105:1|hl=ألم,تر|com=[[أَلَمْ تَرَ]] : apocopé de [[تَرَى]].}}
""",
    fiche=dict(
        titre='Défectueux, sourds, hamzés', ar='النَّاقِصُ وَالْمُضَعَّفُ وَالْمَهْمُوزُ',
        corps=r"""
<ul>
<li><b>Défectueux</b> : [[دَعَا يَدْعُو]] · [[رَمَى يَرْمِي]] · [[خَشِيَ يَخْشَى]] ; ils : [[دَعَوْا]] [[رَمَوْا]] [[خَشُوا]] ; je : [[دَعَوْتُ]] [[رَمَيْتُ]] [[خَشِيتُ]].</li>
<li>Apocopé et impératif : la voyelle longue tombe — [[لَمْ يَدْعُ]], [[ٱرْمِ]], [[ٱهْدِ]].</li>
<li><b>Sourd</b> : [[مَدَّ يَمُدُّ]] ; [[ظَنَنْتُمْ]] devant consonne ; apocopé [[لَمْ يَمْسَسْ]] / [[لَمْ يَمَسَّ]].</li>
<li><b>Hamzé</b> : [[خُذْ]] [[كُلْ]] [[مُرْ]].</li>
<li>[[رَأَى يَرَى]] (لَمْ يَرَ) · [[أَتَى يَأْتِي]] · [[ءَاتَى يُؤْتِي]] donner · [[جَاءَ يَجِيءُ]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Conjugue.", items=[
            ('[[دَعَا]], 3<sup>e</sup> m. pl. accompli', '[[دَعَوْا]]'), ('[[هَدَى]], impératif m. sg.', '[[ٱهْدِ]]'),
            ('[[خَشِيَ]], 3<sup>e</sup> m. sg. inaccompli', '[[يَخْشَى]]'), ('[[رَأَى]], apocopé 2<sup>e</sup> m. sg.', '[[لَمْ تَرَ]]'),
            ('[[أَخَذَ]], impératif m. sg.', '[[خُذْ]]'), ('[[ظَنَّ]], 2<sup>e</sup> m. pl. accompli', '[[ظَنَنْتُمْ]]'),
            ('[[أَعْطَى]], 1<sup>re</sup> pl. accompli', '[[أَعْطَيْنَا]]'), ('[[تَلَا]], 3<sup>e</sup> m. sg. inaccompli', '[[يَتْلُو]]'),
        ]),
        dict(auto='racine', refs=[(91, 11, 15), (92, 14, 21)], n=10),
    ],
    flash=[
        ("Apocopé de [[يَدْعُو]] ?", "[[لَمْ يَدْعُ]]"),
        ("Inaccompli de [[رَأَى]] ?", "[[يَرَى]]"),
        ("Impératif de [[أَكَلَ]] ?", "[[كُلْ]]"),
        ("[[ءَاتَى]] (IV) : sens ?", "donner"),
        ("« Ils ont craint » (de [[خَشِيَ]]) ?", "[[خَشُوا]]"),
    ],
    notes={
        (92, 1): "[[إِذَا يَغْشَىٰ]] « quand elle enveloppe (tout) » : [[يَغْشَى]] défectueux à l'inaccompli.",
        (92, 7): "[[فَسَنُيَسِّرُهُۥ لِلْيُسْرَىٰ]] « Nous lui faciliterons la voie la plus aisée » : futur + forme II.",
        (92, 12): "[[إِنَّ عَلَيْنَا لَلْهُدَىٰ]] « c'est à Nous, certes, de guider » : khabar en tête, nom de <i>inna</i> avec lām.",
    },
)
