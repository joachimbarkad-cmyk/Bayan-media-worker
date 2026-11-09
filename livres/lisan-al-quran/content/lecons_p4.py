"""Partie IV — la phrase verbale et ses compléments (leçons 33 à 40)."""

L = {}

L[33] = dict(
    objectifs=[
        "construire la phrase verbale : verbe, agent, complément",
        "accorder le verbe avec un agent placé après lui",
        "comprendre les changements d'ordre des mots",
    ],
    expose=r"""
<p>La <b>phrase verbale</b> [[جُمْلَة فِعْلِيَّة]] commence par un verbe. Son ordre habituel est : <b>verbe – agent – complément</b>. L'agent, ou <b>fāʿil</b> [[فَاعِل]], est au <b>nominatif</b>.</p>
{{ex 99:2|hl=وأخرجت,الأرض,أثقالها|com=[[أَخْرَجَتِ]] verbe · [[ٱلْأَرْضُ]] agent (nominatif) · [[أَثْقَالَهَا]] complément (accusatif).}}
<h3><span class="pastille">1</span>L'accord du verbe placé en tête</h3>
<ul>
<li>Le verbe reste au <b>singulier</b>, même si l'agent est duel ou pluriel : [[إِذَا جَآءَكَ ٱلْمُنَٰفِقُونَ]] « quand les hypocrites viennent à toi » (63:1).</li>
<li>Il s'accorde en <b>genre</b> : agent féminin → [[ـَتْ]] / [[تَـ]]. C'est obligatoire pour un vrai féminin placé juste après ([[قَالَتِ ٱمْرَأَتُ]]), facultatif pour un pluriel interne ([[قَالَتِ ٱلْأَعْرَابُ]] 49:14).</li>
</ul>
{{ex 99:3|hl=وقال,الإنسان|com=[[وَقَالَ ٱلْإِنسَٰنُ مَا لَهَا]] « et l'homme dira : “Qu'a-t-elle ?” »}}
<h3><span class="pastille">2</span>Agent contenu dans le verbe</h3>
<p>Si l'agent n'est pas exprimé par un nom, il est contenu dans la terminaison : [[قَالُوا]] « ils ont dit », [[نَعْبُدُ]] « nous adorons ». Quand l'agent précède le verbe, la phrase devient nominale et le verbe s'accorde entièrement : [[ٱلْمُؤْمِنُونَ يَقُولُونَ]] « les croyants disent ».</p>
<h3><span class="pastille">3</span>Ordre libre, sens précis</h3>
<p>Grâce aux cas, l'ordre peut changer sans ambiguïté ; le mot avancé est mis en relief :</p>
{{ex 2:124|hl=إبراهيم,ربه|from=وإذ|to=بكلمات|com=Complément [[إِبْرَٰهِـۧمَ]] (accusatif) avant l'agent [[رَبُّهُۥ]] (nominatif) : « et quand son Seigneur éprouva Ibrāhīm ».}}
{{ex 35:28|hl=الله,العلماء|from=إنما|to=العلماء|com=« Seuls les savants, parmi Ses serviteurs, craignent Allah » : l'agent [[ٱلْعُلَمَٰٓؤُا۟]] rejeté à la fin porte la restriction.}}
<div class="encadre"><span class="lab">Analyser une phrase verbale</span>1. Trouve le verbe et sa personne. 2. Cherche un nom au nominatif après lui : c'est l'agent ; sinon l'agent est dans le verbe. 3. Les accusatifs sont des compléments (leçons suivantes).</div>
""",
    fiche=dict(
        titre='La phrase verbale', ar='الْفِعْلُ وَالْفَاعِلُ',
        corps=r"""
<ul>
<li>Ordre : verbe – <b>agent (nominatif)</b> – complément (accusatif).</li>
<li>Verbe en tête : toujours <b>singulier</b> ; accord en genre ([[قَالَتِ ٱمْرَأَةٌ]]), facultatif avec un pluriel interne.</li>
<li>Agent pronom : dans la terminaison ([[قَالُوا]]). Agent avant le verbe : phrase nominale, accord complet.</li>
<li>Mot avancé = mot mis en relief.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Choisis la forme du verbe.", items=[
            ('(… [[قَالَ]] / [[قَالُوا]]) [[ٱلْمُؤْمِنُونَ]]', '[[قَالَ ٱلْمُؤْمِنُونَ]] : verbe en tête au singulier'),
            ('[[ٱلْمُؤْمِنُونَ]] (… [[قَالَ]] / [[قَالُوا]])', '[[ٱلْمُؤْمِنُونَ قَالُوا]] : agent avant, accord complet'),
            ('(… [[جَاءَ]] / [[جَاءَتْ]]) [[ٱمْرَأَةٌ]]', '[[جَاءَتْ ٱمْرَأَةٌ]] : vrai féminin'),
            ('(… [[يَشْهَدُ]] / [[يَشْهَدُونَ]]) [[ٱلْمُقَرَّبُونَ]]', '[[يَشْهَدُ]] (83:21)'),
        ], une=True),
        dict(auto='cas', refs=[(19, 22, 26)], n=10),
    ],
    flash=[
        ("Cas de l'agent (fāʿil) ?", "nominatif"),
        ("Verbe placé avant un agent pluriel ?", "singulier"),
        ("[[إِذَا جَآءَكَ ٱلْمُنَٰفِقُونَ]] : pourquoi [[جَآءَ]] au singulier ?", "le verbe précède l'agent"),
        ("Où est l'agent dans [[قَالُوا]] ?", "dans la terminaison <i>-ū</i>"),
        ("Pourquoi [[إِبْرَٰهِيمَ]] avant [[رَبُّهُ]] en 2:124 ?", "mise en relief du complément"),
    ],
    notes={
        (99, 1): "[[إِذَا زُلْزِلَتِ ٱلْأَرْضُ زِلْزَالَهَا]] : passif + complément absolu « secouée de sa secousse » (L35).",
        (99, 4): "[[يَوْمَئِذٍ تُحَدِّثُ أَخْبَارَهَا]] « ce jour-là, elle racontera ses nouvelles » : complément de temps en tête.",
        (99, 7): "[[فَمَن يَعْمَلْ … يَرَهُۥ]] : condition, deux verbes à l'apocopé (L38).",
    },
)

L[34] = dict(
    objectifs=[
        "reconnaître le complément d'objet (mafʿūl bihi)",
        "connaître les verbes à deux compléments",
        "comprendre l'objet placé en tête et [[إِيَّا]]",
    ],
    expose=r"""
<p>Le <b>complément d'objet</b> [[مَفْعُولٌ بِهِ]] est le nom sur lequel porte l'action. Il est à l'<b>accusatif</b>. Ce peut être un pronom suffixé au verbe.</p>
{{ex 107:2|hl=يدع,اليتيم|com=[[يَدُعُّ ٱلْيَتِيمَ]] « (il) repousse l'orphelin ».}}
{{ex 107:7|hl=ويمنعون,الماعون|com=« et refusent l'ustensile (le moindre service) ».}}
<h3><span class="pastille">1</span>Verbes à deux compléments</h3>
<p>Plusieurs verbes fréquents ont deux compléments à l'accusatif : [[أَعْطَى]] / [[ءَاتَى]] donner (qqn, qqch), [[جَعَلَ]] faire de X un Y, [[هَدَى]] guider (qqn sur qqch), [[زَادَ]] augmenter, [[عَلَّمَ]] enseigner, et les verbes de jugement [[ظَنَّ]], [[حَسِبَ]], [[رَأَى]].</p>
{{ex 90:10|hl=وهديناه,النجدين|com=[[هَدَيْنَٰهُ]] (1<sup>er</sup> complément : <i>-hu</i>) [[ٱلنَّجْدَيْنِ]] (2<sup>e</sup> complément) : « Nous lui avons montré les deux voies ».}}
{{ex 78:9|hl=وجعلنا,نومكم,سباتا|com=« Nous avons fait de votre sommeil un repos ».}}
<h3><span class="pastille">2</span>Verbes construits avec une préposition</h3>
<p>Certains verbes introduisent leur objet par une préposition : [[ءَامَنَ بِـ]] croire en, [[كَذَّبَ بِـ]] démentir, [[نَظَرَ إِلَى]] regarder, [[رَغِبَ إِلَى]] aspirer à, [[تَوَكَّلَ عَلَى]] s'en remettre à. Apprends le verbe avec sa préposition.</p>
{{ex 107:1|hl=يكذب,بالدين|com=[[يُكَذِّبُ بِٱلدِّينِ]] « dément la Rétribution ».}}
<h3><span class="pastille">3</span>L'objet en tête</h3>
<p>Placer l'objet <b>avant</b> le verbe le met en relief, souvent avec une valeur d'exclusivité :</p>
<ul>
<li>[[إِيَّاكَ نَعْبُدُ]] « c'est <b>Toi</b> (seul) que nous adorons ». Un pronom objet placé en tête prend le support [[إِيَّا]] : [[إِيَّاكَ]], [[إِيَّاهُ]], [[إِيَّانَا]], [[إِيَّاكُمْ]].</li>
<li>[[فَأَمَّا ٱلْيَتِيمَ فَلَا تَقْهَرْ]] « quant à l'orphelin, ne l'opprime pas » (93:9).</li>
<li>[[وَرَبَّكَ فَكَبِّرْ]] « et ton Seigneur, magnifie-Le » (74:3).</li>
</ul>
""",
    fiche=dict(
        titre="Le complément d'objet", ar='الْمَفْعُولُ بِهِ',
        corps=r"""
<ul>
<li><b>Accusatif</b> ; souvent pronom suffixe sur le verbe ([[هَدَانَا]]).</li>
<li>Deux compléments : [[أَعْطَى]] [[ءَاتَى]] [[جَعَلَ]] [[هَدَى]] [[زَادَ]] [[عَلَّمَ]] [[ظَنَّ]] [[حَسِبَ]].</li>
<li>Verbe + préposition : [[ءَامَنَ بِـ]] [[كَذَّبَ بِـ]] [[نَظَرَ إِلَى]] [[تَوَكَّلَ عَلَى]].</li>
<li>Objet en tête = relief, exclusivité : [[إِيَّاكَ نَعْبُدُ]] (pronom → [[إِيَّا]] + suffixe).</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Repère le(s) complément(s) d'objet.", items=[
            ('[[خَلَقَ ٱلْإِنسَٰنَ مِنْ عَلَقٍ]]', '[[ٱلْإِنسَٰنَ]]'), ('[[أَطْعَمَهُم مِّن جُوعٍ]]', '<i>-hum</i>'),
            ('[[إِنَّآ أَعْطَيْنَٰكَ ٱلْكَوْثَرَ]]', '<i>-ka</i> et [[ٱلْكَوْثَرَ]] (deux compléments)'), ('[[وَيُطْعِمُونَ ٱلطَّعَامَ]]', '[[ٱلطَّعَامَ]]'),
            ('[[وَجَعَلْنَا ٱلَّيْلَ لِبَاسًا]]', '[[ٱلَّيْلَ]] et [[لِبَاسًا]]'), ('[[إِيَّاكَ نَسْتَعِينُ]]', '[[إِيَّاكَ]] (en tête)'),
        ], une=True),
        dict(auto='pron', refs=[(93, 6, 11), (2, 255, 255)], n=8),
    ],
    flash=[
        ("Cas du complément d'objet ?", "accusatif"),
        ("[[هَدَيْنَٰهُ ٱلنَّجْدَيْنِ]] : combien de compléments ?", "deux"),
        ("Pourquoi [[إِيَّاكَ]] et non [[ـكَ]] dans [[إِيَّاكَ نَعْبُدُ]] ?", "pronom objet placé avant le verbe"),
        ("Préposition de [[ءَامَنَ]] ?", "[[بِـ]] : croire en"),
        ("Valeur de l'objet en tête ?", "mise en relief, exclusivité"),
    ],
    notes={
        (107, 1): "[[أَرَءَيْتَ]] « as-tu vu ? » : question (L18) ; la hamza de [[رَأَى]] est notée par [[ءَ]].",
        (107, 4): "[[فَوَيْلٌ لِّلْمُصَلِّينَ]] « malheur donc à ceux qui prient (ainsi) » : phrase nominale, sujet indéfini en tête (formule d'imprécation).",
        (107, 5): "[[عَن صَلَاتِهِمْ سَاهُونَ]] : complément prépositionnel avant le participe [[سَاهُونَ]].",
    },
)

L[35] = dict(
    objectifs=[
        "reconnaître le complément de temps et de lieu (mafʿūl fīhi)",
        "reconnaître le complément de but (mafʿūl li-ajlihi)",
        "employer le complément absolu (mafʿūl muṭlaq)",
    ],
    expose=r"""
<p>Outre l'objet, plusieurs compléments se mettent à l'<b>accusatif</b>. Ils répondent à des questions différentes.</p>
<table class="t">
<tr><th>complément</th><th>question</th><th>exemple</th></tr>
<tr><td>de temps ou de lieu (<i>mafʿūl fīhi</i>, ẓarf)</td><td>quand ? où ?</td><td>[[لَيْلًا]] de nuit · [[يَوْمَ ٱلْقِيَٰمَةِ]] le Jour de la Résurrection · [[عِندَ رَبِّهِمْ]] auprès de leur Seigneur</td></tr>
<tr><td>de but (<i>mafʿūl li-ajlihi</i>)</td><td>pourquoi ?</td><td>[[ٱبْتِغَآءَ مَرْضَاتِ ٱللَّهِ]] en recherchant l'agrément d'Allah</td></tr>
<tr><td>absolu (<i>mafʿūl muṭlaq</i>)</td><td>comment ? combien ?</td><td>[[تَرْتِيلًا]] · [[هَجْرًا جَمِيلًا]] · [[دَكَّةً وَٰحِدَةً]]</td></tr>
</table>
<h3><span class="pastille">1</span>Le temps et le lieu</h3>
<p>Les noms de temps ([[يَوْم]], [[لَيْل]], [[حِين]], [[يَوْمَئِذٍ]]) et de lieu ([[عِندَ]], [[فَوْقَ]], [[تَحْتَ]], [[بَيْنَ]], [[خَلْفَ]], [[أَمَامَ]], [[قَبْلَ]], [[بَعْدَ]]) se mettent à l'accusatif sans préposition :</p>
{{ex 17:1|hl=ليلا|from=سبحان|to=الأقصا|com=« Gloire à Celui qui a fait voyager Son serviteur <b>de nuit</b> ».}}
<h3><span class="pastille">2</span>Le but</h3>
<p>Un maṣdar à l'accusatif peut exprimer le motif de l'action :</p>
{{ex 2:207|hl=ابتغاء|com=[[ٱبْتِغَآءَ]] « par recherche (de l'agrément d'Allah) ».}}
{{ex 17:31|hl=خشية|from=ولا|to=إملاق|com=« ne tuez pas vos enfants <b>par crainte</b> de la pauvreté ».}}
<h3><span class="pastille">3</span>Le complément absolu</h3>
<p>C'est le maṣdar du verbe lui-même (L29). Seul, il <b>renforce</b> ([[تَكْلِيمًا]]) ; avec un adjectif, il indique la <b>manière</b> ([[صَبْرًا جَمِيلًا]] « une belle patience ») ; avec un nombre, la <b>fréquence</b> ([[دَكَّةً وَٰحِدَةً]] « d'un seul coup », 69:14). [[سُبْحَٰنَ ٱللَّهِ]] est aussi un maṣdar de ce type, le verbe étant sous-entendu.</p>
{{ex 73:10|hl=واهجرهم,هجرا,جميلا}}
<div class="attention"><span class="lab">Le cas d'un même mot</span>[[يَوْمَ]] est accusatif comme complément de temps ([[يَوْمَ يَقُومُ ٱلنَّاسُ]]), mais nominatif comme sujet ([[ٱلْيَوْمُ]]) ou génitif après préposition ([[فِى يَوْمٍ]]). Toujours se demander : quelle fonction ?</div>
""",
    fiche=dict(
        titre='Les autres compléments', ar='الْمَفْعُولُ فِيهِ وَلَهُ وَالْمُطْلَقُ',
        corps=r"""
<ul>
<li>Tous à l'<b>accusatif</b>.</li>
<li><b>Temps / lieu</b> (quand ? où ?) : [[لَيْلًا]], [[يَوْمَ]], [[عِنْدَ]], [[فَوْقَ]], [[بَيْنَ]], [[قَبْلَ]], [[بَعْدَ]].</li>
<li><b>But</b> (pourquoi ?) : maṣdar — [[ٱبْتِغَاءَ مَرْضَاتِ ٱللَّهِ]], [[خَشْيَةَ إِمْلَاقٍ]].</li>
<li><b>Absolu</b> (comment ?) : maṣdar du verbe — [[تَكْلِيمًا]] (insistance), [[هَجْرًا جَمِيلًا]] (manière), [[دَكَّةً وَاحِدَةً]] (nombre).</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Nomme le complément souligné (temps/lieu, but, absolu).", items=[
            ('[[وَسَبِّحُوهُ بُكْرَةً وَأَصِيلًا]] — <i>bukratan</i>', 'temps (« matin et soir », 33:42)'),
            ('[[وَكَلَّمَ ٱللَّهُ مُوسَىٰ تَكْلِيمًا]] — <i>taklīman</i>', 'absolu (insistance)'),
            ('[[يُنفِقُونَ أَمْوَالَهُمُ ٱبْتِغَاءَ مَرْضَاتِ ٱللَّهِ]] — <i>ibtighāʾa</i>', 'but (2:265)'),
            ('[[فَصَبْرٌ جَمِيلٌ]] / [[فَٱصْبِرْ صَبْرًا جَمِيلًا]] — <i>ṣabran</i>', 'absolu de manière (70:5)'),
            ('[[عِندَ رَبِّهِمْ]] — <i>ʿinda</i>', 'lieu (ẓarf) annexé'),
        ], une=True),
        dict(auto='cas', refs=[(17, 82, 84)], n=8),
    ],
    flash=[
        ("Question du complément de but ?", "pourquoi ?"),
        ("[[لَيْلًا]] dans [[أَسْرَىٰ بِعَبْدِهِۦ لَيْلًا]] ?", "complément de temps (de nuit)"),
        ("Complément absolu de manière : exemple ?", "[[هَجْرًا جَمِيلًا]]"),
        ("Cas de ces compléments ?", "accusatif"),
        ("[[سُبْحَٰنَ ٱللَّهِ]] : quel complément ?", "absolu (verbe sous-entendu)"),
    ],
    notes={
        (17, 78): "[[وَقُرْءَانَ ٱلْفَجْرِ]] « et (accomplis) la récitation de l'aube » : objet d'un verbe sous-entendu, coordonné à [[ٱلصَّلَوٰةَ]].",
        (17, 79): "[[نَافِلَةً لَّكَ]] « en surérogation pour toi » : état ou complément ; [[مَقَامًا مَّحْمُودًا]] « à une station louable » : complément de lieu.",
        (17, 81): "[[إِنَّ ٱلْبَٰطِلَ كَانَ زَهُوقًا]] « le faux est voué à disparaître » : <i>inna</i> + <i>kāna</i>.",
    },
)

L[36] = dict(
    objectifs=[
        "reconnaître l'état (ḥāl) et sa construction",
        "employer la phrase d'état introduite par [[وَ]]",
        "reconnaître la spécification (tamyīz)",
    ],
    expose=r"""
<h3><span class="pastille">1</span>Le ḥāl : dans quel état ?</h3>
<p>Le <b>ḥāl</b> [[حَال]] décrit l'<b>état</b> d'un être (agent ou objet) au moment de l'action. Il est à l'<b>accusatif</b>, généralement <b>indéfini</b>, alors que l'être qu'il décrit est défini. Il répond à la question « comment ? dans quel état ? ».</p>
{{ex 89:28|hl=راضية,مرضية|com=« Retourne vers ton Seigneur, <b>satisfaite et agréée</b> » : deux ḥāl de l'âme (agent de [[ٱرْجِعِىٓ]]).}}
{{ex 12:4|hl=ساجدين|from=رأيتهم|to=ساجدين|com=« je les ai vus <b>prosternés</b> devant moi » : ḥāl de l'objet <i>-hum</i>.}}
{{ex 110:2|hl=أفواجا|com=« les gens entrer <b>en foule</b> dans la religion d'Allah ».}}
<p>Comparer l'adjectif et le ḥāl : [[رَأَيْتُ ٱلرَّجُلَ ٱلرَّاكِبَ]] « j'ai vu l'homme qui chevauche » (adjectif, défini comme le nom) ; [[رَأَيْتُ ٱلرَّجُلَ رَاكِبًا]] « j'ai vu l'homme <b>à cheval</b> » (ḥāl, indéfini).</p>
<h3><span class="pastille">2</span>La phrase d'état</h3>
<p>Le ḥāl peut être une phrase, souvent introduite par [[وَ]] (« alors que ») et un pronom :</p>
{{ex 4:43|hl=وأنتم,سكارى|from=ياأيها|to=سكارى|com=« n'approchez pas la prière <b>alors que vous êtes</b> ivres ».}}
<p>Sans wāw, une phrase verbale à l'inaccompli peut aussi exprimer l'état : [[جَآءُوٓ أَبَاهُمْ عِشَآءً يَبْكُونَ]] « ils vinrent à leur père le soir, <b>en pleurant</b> » (12:16).</p>
<h3><span class="pastille">3</span>Le tamyīz : sous quel rapport ?</h3>
<p>Le <b>tamyīz</b> [[تَمْيِيز]] (« spécification ») est un nom <b>indéfini à l'accusatif</b> qui précise sous quel rapport une chose est dite. Il suit les comparatifs, les nombres de 11 à 99 et certains verbes :</p>
{{ex 19:4|hl=واشتعل,الرأس,شيبا|com=[[وَٱشْتَعَلَ ٱلرَّأْسُ شَيْبًا]] « et la tête s'est embrasée <b>de cheveux blancs</b> ».}}
{{ex 18:34|hl=أكثر,مالا,وأعز,نفرا|from=أنا|to=نفرا|com=« je suis plus riche que toi <b>en biens</b> et plus puissant <b>en hommes</b> ».}}
{{ex 67:2|hl=أحسن,عملا|from=ليبلوكم|to=عملا|com=[[أَحْسَنُ عَمَلًا]] « le meilleur <b>en œuvre</b> ».}}
""",
    fiche=dict(
        titre='État et spécification', ar='الْحَالُ وَالتَّمْيِيزُ',
        corps=r"""
<ul>
<li><b>Ḥāl</b> : accusatif, indéfini ; état de l'agent ou de l'objet pendant l'action — [[ٱرْجِعِي إِلَىٰ رَبِّكِ رَاضِيَةً]].</li>
<li>Phrase d'état : [[وَ]] + pronom (« alors que ») — [[وَأَنْتُمْ سُكَارَىٰ]] ; ou inaccompli sans wāw — [[يَبْكُونَ]].</li>
<li>Adjectif (défini comme le nom) ≠ ḥāl (indéfini) : [[ٱلرَّجُلَ ٱلرَّاكِبَ]] / [[ٱلرَّجُلَ رَاكِبًا]].</li>
<li><b>Tamyīz</b> : accusatif, indéfini ; « sous quel rapport ? » — [[ٱشْتَعَلَ ٱلرَّأْسُ شَيْبًا]], [[أَكْثَرُ مَالًا]], [[أَحَدَ عَشَرَ كَوْكَبًا]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Ḥāl ou tamyīz ? Traduis.", items=[
            ('[[ٱدْخُلُوهَا خَالِدِينَ]]', 'ḥāl : entrez-y pour l\'éternité (39:73)'), ('[[أَنَا أَكْثَرُ مِنْكَ مَالًا]]', 'tamyīz : je suis plus riche que toi'),
            ('[[وَخُلِقَ ٱلْإِنسَانُ ضَعِيفًا]]', "ḥāl : l'homme a été créé faible"), ('[[أَحَدَ عَشَرَ كَوْكَبًا]]', 'tamyīz : onze astres'),
            ('[[كَبُرَتْ كَلِمَةً]]', 'tamyīz : quelle énorme parole !'), ('[[فَتَمَثَّلَ لَهَا بَشَرًا سَوِيًّا]]', 'ḥāl : il prit pour elle la forme d\'un homme parfait'),
        ]),
        dict(auto='cas', refs=[(39, 73, 75)], n=8),
    ],
    flash=[
        ("Cas et définition du ḥāl ?", "accusatif, généralement indéfini"),
        ("[[رَاضِيَةً مَّرْضِيَّةً]] : fonction ?", "ḥāl (état de l'âme)"),
        ("Question à laquelle répond le tamyīz ?", "sous quel rapport ?"),
        ("[[ٱشْتَعَلَ ٱلرَّأْسُ شَيْبًا]] : rôle de [[شَيْبًا]] ?", "tamyīz"),
        ("Comment introduit-on une phrase d'état ?", "par [[وَ]] + pronom (« alors que »)"),
    ],
    notes={
        (89, 29): "[[فَٱدْخُلِى فِى عِبَٰدِى]] « entre donc parmi Mes serviteurs » : impératif féminin.",
        (19, 3): "[[إِذْ نَادَىٰ رَبَّهُۥ نِدَآءً خَفِيًّا]] : complément absolu de manière (L35).",
        (19, 5): "[[فَهَبْ لِى مِن لَّدُنكَ وَلِيًّا]] : impératif de [[وَهَبَ]] (L31).",
        (19, 6): "[[وَٱجْعَلْهُ رَبِّ رَضِيًّا]] : deux compléments de [[جَعَلَ]] ; [[رَبِّ]] = « ô mon Seigneur ».",
    },
)

L[37] = dict(
    objectifs=[
        "analyser l'exception avec [[إِلَّا]]",
        "employer [[غَيْر]] et [[سِوَى]]",
        "reconnaître les procédés de restriction",
    ],
    expose=r"""
<p>L'exception [[ٱسْتِثْنَاء]] retire un élément d'un ensemble : « tous… sauf ». Elle se construit surtout avec [[إِلَّا]]. Le cas du mot qui suit [[إِلَّا]] (le <i>mustathnā</i>) dépend de la phrase.</p>
<table class="t">
<tr><th>phrase</th><th>cas après illā</th><th>exemple</th></tr>
<tr><td>affirmative, ensemble exprimé</td><td><b>accusatif</b></td><td>[[فَشَرِبُوا۟ مِنْهُ إِلَّا قَلِيلًا]] ils en burent, sauf un petit nombre (2:249)</td></tr>
<tr><td>négative, ensemble exprimé</td><td>accusatif, ou même cas que l'ensemble</td><td>[[مَّا فَعَلُوهُ إِلَّا قَلِيلٌ مِّنْهُمْ]] peu d'entre eux l'auraient fait (4:66)</td></tr>
<tr><td>négative, ensemble <b>non</b> exprimé</td><td>cas normal de la fonction (= restriction)</td><td>[[وَمَا مُحَمَّدٌ إِلَّا رَسُولٌ]] Muḥammad n'est qu'un messager (3:144)</td></tr>
</table>
{{ex 103:3|hl=إلا,الذين|com=Phrase affirmative (« l'homme est en perdition ») : [[ٱلَّذِينَ]] est en position d'accusatif.}}
<h3><span class="pastille">1</span>Lā ilāha illā Allāh</h3>
<p>Dans [[لَآ إِلَٰهَ إِلَّا ٱللَّهُ]], la phrase est négative et l'ensemble (« divinité ») est exprimé : [[ٱللَّه]] est au <b>nominatif</b>, comme substitut du khabar sous-entendu (« pas de divinité [véritable], sauf Allah »).</p>
<h3><span class="pastille">2</span>Ghayr et siwā</h3>
<p>[[غَيْر]] et [[سِوَى]] « autre que, sauf » sont des noms suivis du <b>génitif</b> ; [[غَيْر]] prend lui-même le cas que prendrait le mot après [[إِلَّا]] : [[غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ]] (1:7) ; [[مَا لَكُم مِّنْ إِلَٰهٍ غَيْرُهُۥ]] « vous n'avez pas d'autre divinité que Lui » (7:59).</p>
<h3><span class="pastille">3</span>La restriction (ḥaṣr)</h3>
<p>Pour dire « ne… que, seul », le Coran emploie :</p>
<ul>
<li>négation + [[إِلَّا]] : [[وَمَآ أُمِرُوٓا۟ إِلَّا لِيَعْبُدُوا۟ ٱللَّهَ]] « il ne leur a été ordonné que d'adorer Allah » (98:5) ;</li>
<li>[[إِنَّمَا]] : [[إِنَّمَا ٱلْمُؤْمِنُونَ إِخْوَةٌ]] « les croyants ne sont que des frères » (49:10) ;</li>
<li>l'antéposition : [[إِيَّاكَ نَعْبُدُ]] (L34) ;</li>
<li>le pronom de séparation : [[هُمُ ٱلْمُفْلِحُونَ]] (L11).</li>
</ul>
{{ex 98:5|hl=وما,إلا,ليعبدوا|from=وما|to=الدين}}
""",
    fiche=dict(
        titre='Exception et restriction', ar='الِاسْتِثْنَاءُ وَالْحَصْرُ',
        corps=r"""
<table class="t">
<tr><th>phrase</th><th>après [[إِلَّا]]</th></tr>
<tr><td>affirmative complète</td><td>accusatif : [[إِلَّا قَلِيلًا]]</td></tr>
<tr><td>négative complète</td><td>accusatif ou même cas : [[إِلَّا قَلِيلٌ]]</td></tr>
<tr><td>négative incomplète</td><td>cas de la fonction = restriction : [[مَا مُحَمَّدٌ إِلَّا رَسُولٌ]]</td></tr>
</table>
<ul><li>[[غَيْر]] / [[سِوَى]] + génitif.</li>
<li>Restriction : négation + [[إِلَّا]] · [[إِنَّمَا]] · antéposition · pronom de séparation.</li></ul>""",
    ),
    exercices=[
        dict(consigne="Traduis en marquant l'exception ou la restriction.", items=[
            ('[[إِنْ هُوَ إِلَّا ذِكْرٌ لِلْعَالَمِينَ]]', "ce n'est qu'un rappel pour les mondes (81:27)"),
            ('[[إِنَّمَا أَنْتَ مُذَكِّرٌ]]', "tu n'es qu'un rappeleur (88:21)"), ('[[لَا إِلَٰهَ إِلَّا هُوَ]]', 'pas de divinité sauf Lui'),
            ('[[فَسَجَدُوا إِلَّا إِبْلِيسَ]]', "ils se prosternèrent, sauf Iblīs (2:34)"), ('[[مَا لَكُمْ مِنْ إِلَٰهٍ غَيْرُهُ]]', "vous n'avez pas d'autre divinité que Lui"),
            ('[[وَمَا تَوْفِيقِي إِلَّا بِٱللَّهِ]]', "ma réussite ne dépend que d'Allah (11:88)"),
        ], une=True),
        dict(auto='cas', refs=[(98, 1, 4)], n=8),
    ],
    flash=[
        ("Cas après [[إِلَّا]] dans une phrase affirmative complète ?", "accusatif"),
        ("[[وَمَا مُحَمَّدٌ إِلَّا رَسُولٌ]] : pourquoi [[رَسُولٌ]] au nominatif ?", "restriction : c'est le khabar"),
        ("Cas après [[غَيْر]] ?", "génitif"),
        ("Trois procédés de restriction ?", "négation + illā, innamā, antéposition (aussi pronom de séparation)"),
        ("Cas de [[ٱللَّه]] dans [[لَآ إِلَٰهَ إِلَّا ٱللَّهُ]] ?", "nominatif"),
    ],
    notes={
        (98, 6): "[[أُو۟لَٰٓئِكَ هُمْ شَرُّ ٱلْبَرِيَّةِ]] « ceux-là sont les pires des créatures » : pronom de séparation, élatif sans <i>a-</i> (L40).",
        (98, 7): "[[أُو۟لَٰٓئِكَ هُمْ خَيْرُ ٱلْبَرِيَّةِ]] : même construction avec [[خَيْر]].",
        (98, 8): "[[رَّضِىَ ٱللَّهُ عَنْهُمْ وَرَضُوا۟ عَنْهُ]] « Allah les agrée et ils L'agréent » : accomplis de [[رَضِيَ]] (défectueux).",
    },
)

L[38] = dict(
    objectifs=[
        "construire la phrase conditionnelle avec les particules qui régissent l'apocopé",
        "savoir quand la réponse prend [[فَـ]]",
        "employer [[إِذَا]], [[لَوْ]], [[لَوْلَا]] et [[أَمَّا… فَـ]]",
    ],
    expose=r"""
<p>Une phrase conditionnelle a deux parties : la <b>condition</b> [[ٱلشَّرْط]] et la <b>réponse</b> [[ٱلْجَوَاب]].</p>
<h3><span class="pastille">1</span>Les particules qui régissent l'apocopé</h3>
<p>[[إِنْ]] si · [[مَنْ]] quiconque · [[مَا]] / [[مَهْمَا]] quoi que · [[أَيْنَمَا]] où que · [[حَيْثُمَا]] partout où · [[مَتَى]] chaque fois que · [[أَيّ]] quel que. Les deux verbes sont à l'<b>apocopé</b> (ou à l'accompli, au sens du futur) :</p>
{{ex 99:7|hl=فمن,يعمل,يره|com=[[يَعْمَلْ]] (condition) et [[يَرَهُۥ]] (réponse, apocopé de [[يَرَى]]) : « quiconque fait le poids d'un atome de bien le verra ».}}
{{ex 65:2|hl=ومن,يتق,يجعل|from=ومن|to=مخرجا|com=[[يَتَّقِ]] (apocopé de [[يَتَّقِي]], le yāʾ tombe) ; [[يَجْعَل]] (apocopé).}}
<h3><span class="pastille">2</span>Quand la réponse prend fa-</h3>
<p>Si la réponse ne peut pas être un verbe à l'apocopé — phrase nominale, impératif, défense, réponse avec [[قَدْ]], [[لَنْ]], [[مَا]], [[سَـ]], [[سَوْفَ]] —, elle est introduite par [[فَـ]] :</p>
{{ex 65:3|hl=ومن,يتوكل,فهو,حسبه|from=ومن|to=حسبه|com=« et quiconque s'en remet à Allah, <b>Il</b> lui suffit » : réponse nominale avec [[فَـ]].}}
<h3><span class="pastille">3</span>Idhā, law, lawlā</h3>
<ul>
<li>[[إِذَا]] « lorsque » : condition réalisable, verbe à l'accompli (sens futur) ; pas d'apocopé : [[فَإِذَا فَرَغْتَ فَٱنصَبْ]] (94:7).</li>
<li>[[لَوْ]] : condition <b>irréelle</b> (« si… avait / aurait ») ; réponse souvent avec [[لَـ]] : [[وَلَوْ شَآءَ ٱللَّهُ لَجَعَلَكُمْ أُمَّةً وَٰحِدَةً]] « si Allah l'avait voulu, Il aurait fait de vous une seule communauté » (5:48).</li>
<li>[[لَوْلَا]] « n'eût été, sans » + nom : [[وَلَوْلَا فَضْلُ ٱللَّهِ عَلَيْكُمْ]] « n'eût été la grâce d'Allah sur vous » (24:10).</li>
</ul>
<h3><span class="pastille">4</span>Ammā… fa-</h3>
<p>[[أَمَّا]] « quant à » détaille ; la suite commence obligatoirement par [[فَـ]] :</p>
{{ex 101:6|hl=فأما,ثقلت}}
{{ex 101:7|hl=فهو|com=« … <b>il</b> sera dans une vie agréable » : réponse avec [[فَـ]].}}
""",
    fiche=dict(
        titre='La condition', ar='الشَّرْطُ',
        corps=r"""
<ul>
<li>Apocopé dans les deux parties après [[إِنْ]] [[مَنْ]] [[مَا]] [[مَهْمَا]] [[أَيْنَمَا]] [[حَيْثُمَا]] [[مَتَى]] [[أَيّ]] (ou accompli).</li>
<li>Réponse avec [[فَـ]] : phrase nominale, impératif, défense, [[قَدْ]] [[لَنْ]] [[مَا]] [[سَـ]] [[سَوْفَ]].</li>
<li>[[إِذَا]] + accompli (futur), sans apocopé. [[لَوْ]] irréel, réponse en [[لَـ]]. [[لَوْلَا]] + nom : n'eût été.</li>
<li>[[أَمَّا]] … [[فَـ]] : quant à… (alors).</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Repère la condition et la réponse ; dis pourquoi la réponse a (ou n'a pas) [[فَـ]].", items=[
            ('[[وَمَنْ يَتَّقِ ٱللَّهَ يَجْعَلْ لَهُ مَخْرَجًا]]', 'condition [[يَتَّقِ]], réponse [[يَجْعَلْ]] : verbe à l\'apocopé, pas de fa-'),
            ('[[وَمَنْ يَتَوَكَّلْ عَلَى ٱللَّهِ فَهُوَ حَسْبُهُ]]', 'réponse nominale → [[فَهُوَ]]'),
            ('[[إِنْ تَنْصُرُوا ٱللَّهَ يَنْصُرْكُمْ]]', 'deux apocopés : « si vous secourez Allah, Il vous secourra » (47:7)'),
            ('[[فَإِذَا قَرَأْتَ ٱلْقُرْآنَ فَٱسْتَعِذْ بِٱللَّهِ]]', 'idhā + accompli ; réponse impérative → fa- (16:98)'),
            ('[[لَوْ أَنْزَلْنَا هَٰذَا ٱلْقُرْآنَ عَلَىٰ جَبَلٍ لَرَأَيْتَهُ خَاشِعًا]]', 'law irréel, réponse avec la- (59:21)'),
        ], une=True),
        dict(auto='mode', refs=[(47, 7, 7), (65, 4, 5)], n=8),
    ],
    flash=[
        ("Mode des deux verbes après [[إِنْ]] ?", "apocopé (ou accompli)"),
        ("Quand la réponse prend-elle [[فَـ]] ?", "réponse nominale, impérative, avec qad, lan, mā, sa-, sawfa…"),
        ("[[لَوْ]] exprime… ?", "une condition irréelle"),
        ("[[لَوْلَا]] + nom : sens ?", "n'eût été"),
        ("Après [[أَمَّا]], la suite commence par… ?", "[[فَـ]]"),
    ],
    notes={
        (65, 2): "Début du verset : il s'agit des femmes divorcées arrivées au terme de leur délai.",
        (101, 1): "[[ٱلْقَارِعَةُ مَا ٱلْقَارِعَةُ]] « le Fracas ! Qu'est-ce que le Fracas ? » : question qui exprime la grandeur (L18).",
        (101, 9): "[[فَأُمُّهُۥ هَاوِيَةٌ]] « sa mère (son refuge) sera un abîme ».",
        (101, 10): "[[وَمَآ أَدْرَىٰكَ مَا هِيَهْ]] : [[هِيَهْ]] = <i>hiya</i> + hāʾ de pause.",
    },
)

L[39] = dict(
    objectifs=[
        "reconnaître les particules du serment et la réponse au serment",
        "reconnaître le nūn d'insistance",
        "récapituler les moyens d'insister",
    ],
    expose=r"""
<h3><span class="pastille">1</span>Les particules du serment</h3>
<p>Le serment [[قَسَم]] se fait avec une particule suivie du <b>génitif</b> :</p>
<ul>
<li>[[وَ]] : la plus fréquente — [[وَٱلْعَصْرِ]], [[وَٱلشَّمْسِ]], [[وَٱلْفَجْرِ]] ;</li>
<li>[[تَ]] : seulement avec Allah — [[تَٱللَّهِ]] « par Allah ! » (12:85) ;</li>
<li>[[بِـ]] après le verbe [[أُقْسِمُ]] « je jure » : [[لَآ أُقْسِمُ بِيَوْمِ ٱلْقِيَٰمَةِ]] « non ! je jure par le Jour de la Résurrection » (75:1). Le [[لَا]] initial renforce le serment.</li>
</ul>
{{ex 89:1|hl=والفجر|com=« Par l'aube ! »}}
<h3><span class="pastille">2</span>La réponse au serment</h3>
<p>Ce que l'on jure (la « réponse ») est marqué par :</p>
<ul>
<li>[[لَقَدْ]] / [[قَدْ]] + accompli : [[قَدْ أَفْلَحَ مَن زَكَّىٰهَا]] (91:9), [[لَقَدْ خَلَقْنَا]] (95:4) ;</li>
<li>[[إِنَّ]] … [[لَـ]] : [[إِنَّ ٱلْإِنسَٰنَ لَفِى خُسْرٍ]] (103:2) ;</li>
<li>[[لَـ]] + inaccompli + nūn d'insistance : [[لَتَرَوُنَّ ٱلْجَحِيمَ]] « vous verrez assurément la Fournaise » (102:6) ;</li>
<li>une négation : [[مَا وَدَّعَكَ رَبُّكَ]] (93:3).</li>
</ul>
<p>La réponse peut être sous-entendue ou éloignée : dans al-Fajr, beaucoup y voient [[إِنَّ رَبَّكَ لَبِٱلْمِرْصَادِ]] (89:14).</p>
{{ex 89:14|hl=إن,ربك,لبالمرصاد}}
<h3><span class="pastille">3</span>Le nūn d'insistance</h3>
<p>Ajouté à l'inaccompli (ou à l'impératif), il renforce fortement : nūn « lourd » [[ـَنَّ]] ([[لَتُسْـَٔلُنَّ]] « vous serez assurément interrogés », 102:8) ou « léger » [[ـَنْ]], écrit comme un tanwīn dans [[لَنَسْفَعًۢا]] (96:15) et [[وَلَيَكُونًا]] (12:32).</p>
<h3><span class="pastille">4</span>Les moyens d'insister</h3>
<table class="t">
<tr><th>moyen</th><th>exemple</th></tr>
<tr><td>[[إِنَّ]], [[أَنَّ]]</td><td>[[إِنَّ ٱللَّهَ غَفُورٌ]]</td></tr>
<tr><td>lām [[لَـ]]</td><td>[[لَكَنُودٌ]], [[لَقَدْ]]</td></tr>
<tr><td>[[قَدْ]] + accompli</td><td>[[قَدْ أَفْلَحَ]]</td></tr>
<tr><td>nūn d'insistance</td><td>[[لَتَرَوُنَّ]]</td></tr>
<tr><td>pronom de séparation</td><td>[[هُمُ ٱلْمُفْلِحُونَ]]</td></tr>
<tr><td>complément absolu</td><td>[[تَكْلِيمًا]]</td></tr>
<tr><td>répétition</td><td>[[كَلَّا سَوْفَ تَعْلَمُونَ ثُمَّ كَلَّا سَوْفَ تَعْلَمُونَ]]</td></tr>
<tr><td>[[أَلَا]] « certes ! »</td><td>[[أَلَآ إِنَّ أَوْلِيَآءَ ٱللَّهِ]] (10:62)</td></tr>
</table>
""",
    fiche=dict(
        titre="Le serment et l'insistance", ar='الْقَسَمُ وَالتَّوْكِيدُ',
        corps=r"""
<ul>
<li>Serment : [[وَ]] / [[تَ]] (avec Allah) / [[أُقْسِمُ بِـ]] + génitif ; [[لَا أُقْسِمُ]] renforcé.</li>
<li>Réponse : [[لَقَدْ]]/[[قَدْ]] + accompli · [[إِنَّ]] … [[لَـ]] · [[لَـ]] + inaccompli + [[نَّ]] · négation ; parfois sous-entendue.</li>
<li>Nūn d'insistance : lourd [[ـَنَّ]] ([[لَتَرَوُنَّ]]), léger [[ـًا]] ([[لَنَسْفَعًا]]).</li>
<li>Autres moyens : [[إِنَّ]], [[لَـ]], [[قَدْ]], pronom de séparation, complément absolu, répétition, [[أَلَا]].</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Repère la particule du serment et la réponse.", items=[
            ('[[وَٱلْعَصْرِ إِنَّ ٱلْإِنْسَانَ لَفِي خُسْرٍ]]', '[[وَ]] ; réponse [[إِنَّ … لَـ]]'),
            ('[[وَٱلتِّينِ … لَقَدْ خَلَقْنَا ٱلْإِنْسَانَ]]', '[[وَ]] ; réponse [[لَقَدْ]] + accompli'),
            ('[[وَٱلضُّحَىٰ … مَا وَدَّعَكَ رَبُّكَ]]', '[[وَ]] ; réponse négative [[مَا]]'),
            ('[[تَٱللَّهِ لَأَكِيدَنَّ أَصْنَامَكُمْ]]', "[[تَ]] ; réponse [[لَـ]] + nūn : « par Allah, je ruserai contre vos idoles » (21:57)"),
        ], une=True),
        dict(auto='verbe', refs=[(89, 15, 20)], n=8),
    ],
    flash=[
        ("Particule de serment réservée à Allah ?", "[[تَ]] : [[تَٱللَّهِ]]"),
        ("Cas du nom après le wāw du serment ?", "génitif"),
        ("[[لَتَرَوُنَّ]] : qu'ajoute le [[نَّ]] ?", "une forte insistance (nūn lourd)"),
        ("Trois formes de réponse au serment ?", "laqad + accompli ; inna … la- ; la- + inaccompli + nūn (ou négation)"),
        ("[[لَآ أُقْسِمُ]] : nie-t-il le serment ?", "non, il le renforce"),
    ],
    notes={
        (89, 2): "[[وَلَيَالٍ عَشْرٍ]] « et par dix nuits » : [[لَيَالٍ]] (pluriel de [[لَيْلَة]]) au génitif ; le yāʾ final tombe devant le tanwīn.",
        (89, 6): "[[أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِعَادٍ]] : question rhétorique (L18).",
        (89, 13): "[[فَصَبَّ عَلَيْهِمْ رَبُّكَ سَوْطَ عَذَابٍ]] « ton Seigneur abattit sur eux un fouet de châtiment » : annexion.",
    },
)

L[40] = dict(
    objectifs=[
        "former et employer l'élatif (comparatif et superlatif)",
        "accorder les nombres de 1 à 10, 11 à 19, et les dizaines",
        "lire les nombres du Coran",
    ],
    expose=r"""
<h3><span class="pastille">1</span>L'élatif</h3>
<p>L'élatif [[ٱسْمُ ٱلتَّفْضِيلِ]] se forme sur le schème [[أَفْعَل]] (féminin [[فُعْلَى]]) : [[كَبِير]] grand → [[أَكْبَر]] plus grand ; [[حَسَن]] beau → [[أَحْسَن]] ; [[عَظِيم]] → [[أَعْظَم]] ; racine sourde [[شَدِيد]] → [[أَشَدّ]] ; défectueuse [[عَلِيّ]] → [[أَعْلَى]]. [[خَيْر]] « meilleur » et [[شَرّ]] « pire » sont des élatifs sans [[أَ]]. L'élatif est diptote.</p>
<ul>
<li><b>Comparatif</b> avec [[مِنْ]] (invariable) : [[أَنَا۠ أَكْثَرُ مِنكَ مَالًا]] (18:34) ; [[خَيْرٌ مِّنْ أَلْفِ شَهْرٍ]] (97:3).</li>
<li><b>Superlatif</b> par annexion : [[أَحْسَنُ ٱلْخَٰلِقِينَ]] « le meilleur des créateurs » (23:14) ; ou avec l'article : [[رَبِّكَ ٱلْأَعْلَى]] « ton Seigneur le Très-Haut » (87:1), [[ٱلْأَكْرَمُ]] (96:3).</li>
<li>Sans complément, il garde souvent la valeur comparative : [[وَٱلْءَاخِرَةُ خَيْرٌ وَأَبْقَىٰٓ]] « l'au-delà est meilleur et plus durable ».</li>
</ul>
{{ex 87:17|hl=خير,وأبقى}}
<h3><span class="pastille">2</span>Un et deux</h3>
<p>Ils se placent <b>après</b> le nom, comme des adjectifs, et s'accordent : [[إِلَٰهٌ وَٰحِدٌ]] « une divinité unique » (2:163), [[إِلَٰهَيْنِ ٱثْنَيْنِ]] « deux divinités » (16:51).</p>
<h3><span class="pastille">3</span>De trois à dix : la polarité</h3>
<p>Le nombre précède le nom compté, qui est au <b>pluriel génitif</b>. Le nombre prend le genre <b>inverse</b> de celui du singulier compté : avec un nom masculin, le nombre a [[ة]] ; avec un nom féminin, il n'en a pas.</p>
<table class="t c">
<tr><th>nom masculin</th><th>nom féminin</th></tr>
<tr><td>[[ثَلَٰثَةِ أَيَّامٍ]] trois jours (2:196)</td><td>[[سَبْعَ سَمَٰوَٰتٍ]] sept cieux (67:3)</td></tr>
<tr><td>[[ثَمَٰنِيَةَ أَيَّامٍ]] huit jours (69:7)</td><td>[[سَبْعَ لَيَالٍ]] sept nuits (69:7)</td></tr>
</table>
<h3><span class="pastille">4</span>Onze à dix-neuf, dizaines, cent, mille</h3>
<ul>
<li>11–19 : deux mots en fatḥa, nom compté au <b>singulier accusatif</b> (tamyīz) : [[أَحَدَ عَشَرَ كَوْكَبًا]] (12:4), [[تِسْعَةَ عَشَرَ]] (74:30).</li>
<li>20–90 ([[عِشْرُونَ]], [[ثَلَٰثُونَ]]…) : nom au singulier accusatif : [[ثَلَٰثِينَ لَيْلَةً]] « trente nuits » (7:142).</li>
<li>100 [[مِائَة]] et 1000 [[أَلْف]] : nom au singulier génitif : [[مِا۟ئَةَ عَامٍ]] (2:259), [[أَلْفِ شَهْرٍ]] (97:3).</li>
<li>Ordinaux sur le schème [[فَاعِل]] : [[ثَانِي]], [[ثَالِث]], [[رَابِع]] : [[رَّابِعُهُمْ كَلْبُهُمْ]] « le quatrième d'entre eux était leur chien » (18:22).</li>
</ul>
{{ex 12:4|hl=أحد,عشر,كوكبا|from=إذ|to=والقمر}}
""",
    fiche=dict(
        titre="L'élatif et les nombres", ar='التَّفْضِيلُ وَالْعَدَدُ',
        corps=r"""
<ul>
<li>Élatif [[أَفْعَل]] (f. [[فُعْلَى]]), diptote ; [[خَيْر]], [[شَرّ]]. Comparatif + [[مِنْ]] ; superlatif par annexion ([[أَحْسَنُ ٱلْخَالِقِينَ]]) ou article ([[ٱلْأَعْلَى]]).</li>
<li>1, 2 : après le nom, accordés ([[إِلَٰهٌ وَاحِدٌ]]).</li>
<li>3–10 : pluriel génitif, <b>genre inverse</b> : [[ثَلَاثَةُ أَيَّامٍ]] / [[سَبْعُ سَمَاوَاتٍ]].</li>
<li>11–19 et 20–99 : singulier <b>accusatif</b> ([[أَحَدَ عَشَرَ كَوْكَبًا]], [[ثَلَاثِينَ لَيْلَةً]]).</li>
<li>100, 1000 : singulier <b>génitif</b> ([[أَلْفِ شَهْرٍ]]). Ordinaux : [[فَاعِل]] ([[ثَالِث]]).</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Forme l'élatif.", items=[
            ('[[كَبِير]]', '[[أَكْبَر]]'), ('[[عَظِيم]]', '[[أَعْظَم]]'), ('[[قَرِيب]]', '[[أَقْرَب]]'),
            ('[[شَدِيد]]', '[[أَشَدّ]]'), ('[[كَرِيم]]', '[[أَكْرَم]]'), ('[[عَلِيم]]', '[[أَعْلَم]]'),
        ]),
        dict(consigne="Écris en arabe (nombre + nom).", items=[
            ('trois jours ([[يَوْم]], pl. [[أَيَّام]])', '[[ثَلَاثَةُ أَيَّامٍ]]'), ('sept cieux ([[سَمَاء]] f.)', '[[سَبْعُ سَمَاوَاتٍ]]'),
            ('onze astres', '[[أَحَدَ عَشَرَ كَوْكَبًا]]'), ('mille mois', '[[أَلْفُ شَهْرٍ]]'),
            ('trente nuits', '[[ثَلَاثُونَ لَيْلَةً]]'), ('cent ans ([[عَام]])', '[[مِائَةُ عَامٍ]]'),
        ]),
        dict(auto='cas', refs=[(18, 22, 22)], n=8),
    ],
    flash=[
        ("Élatif de [[كَبِير]] ?", "[[أَكْبَر]]"),
        ("Féminin de [[أَعْلَى]] ?", "[[عُلْيَا]]"),
        ("Pourquoi [[ثَلَٰثَةِ]] a-t-il un [[ة]] dans [[ثَلَٰثَةِ أَيَّامٍ]] ?", "polarité : nom compté masculin"),
        ("Cas du nom compté après 11–19 ?", "singulier accusatif"),
        ("Cas du nom après [[أَلْف]] ?", "singulier génitif"),
    ],
    notes={
        (87, 14): "[[قَدْ أَفْلَحَ مَن تَزَكَّىٰ]] « a réussi celui qui s'est purifié » : forme V.",
        (87, 16): "[[بَلْ تُؤْثِرُونَ ٱلْحَيَوٰةَ ٱلدُّنْيَا]] « mais vous préférez la vie d'ici-bas » : [[بَلْ]] rectifie.",
        (12, 5): "[[فَيَكِيدُوا۟ لَكَ كَيْدًا]] « de peur qu'ils ne trament contre toi une ruse » : <i>fa-</i> + subjonctif, complément absolu.",
        (12, 6): "[[وَكَذَٰلِكَ يَجْتَبِيكَ رَبُّكَ]] « et ainsi ton Seigneur te choisira » : forme VIII défectueuse.",
    },
)
