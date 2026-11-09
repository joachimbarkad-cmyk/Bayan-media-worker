"""Partie V — lectures suivies : présentation, notes, questions."""

R = {}

R[1] = dict(
    intro=r"""<p>Le « verset du Trône » est, selon un hadith rapporté par Muslim, le plus grand verset du Coran. Il réunit en une phrase les attributs d'Allah : unicité, vie, subsistance, science, royauté. Les deux versets suivants en tirent la conséquence : nulle contrainte en religion, Allah est l'allié des croyants.</p>""",
    notes={
        (2, 255): "{{q 2:255|from=الله|to=القيوم}} : <i>lā</i> de négation absolue + exception (L19, L37), puis deux attributs. {{q 2:255|from=#8|to=نوم}} : le pronom objet <i>-hu</i> précède l'agent féminin [[سِنَةٌ]] (d'où [[تَأْخُذُ]]). {{q 2:255|from=من|to=بإذنه}} : question rhétorique = « personne n'intercède sans Sa permission ».",
        (2, 256): "{{q 2:256|from=لا|to=الدين}} : négation absolue. {{q 2:256|from=قد|to=الغي}} : <i>qad</i> + accompli de forme V. [[ٱلْوُثْقَىٰ]] est le féminin de l'élatif [[أَوْثَق]] (L40).",
        (2, 257): "{{q 2:257|from=الله|to=آمنوا}} : phrase nominale, annexion. {{q 2:257|from=يخرجهم|to=النور}} : forme IV, prépositions [[مِنَ]] … [[إِلَى]].",
    },
    questions=[
        ("Relève deux exemples de <i>lā</i> de négation absolue.", "[[لَآ إِلَٰهَ]] (255) et [[لَآ إِكْرَاهَ]] (256)"),
        ("Pourquoi le verbe [[تَأْخُذُهُۥ]] est-il au féminin ?", "son agent [[سِنَةٌ]] (somnolence) est féminin"),
        ("Analyse [[كُرْسِيُّهُ]].", "nom au nominatif, agent de [[وَسِعَ]], annexé au pronom <i>-hu</i>"),
        ("À quoi renvoie le duel de [[حِفْظُهُمَا]] ?", "aux cieux et à la terre"),
    ],
)

R[2] = dict(
    intro=r"""<p>Les derniers versets de la sourate al-Baqara rappellent qu'Allah connaît ce que cachent les âmes, puis rapportent la profession de foi des croyants et leur invocation, que beaucoup récitent chaque soir.</p>""",
    notes={
        (2, 284): "{{q 2:284|from=لله|to=الأرض}} : khabar en tête. {{q 2:284|from=وإن|to=الله}} : condition, deux apocopés ([[تُبْدُوا۟]], [[يُحَاسِبْكُم]]).",
        (2, 285): "{{q 2:285|from=آمن|to=ربه}} : verbe – agent. [[كُلٌّ]] « chacun » : le tanwīn remplace le complément sous-entendu. {{q 2:285|from=سمعنا|to=وأطعنا}} : accomplis 1<sup>re</sup> pl. [[غُفْرَانَكَ]] : maṣdar à l'accusatif (« [nous implorons] Ton pardon »).",
        (2, 286): "{{q 2:286|from=لا|to=وسعها}} : restriction. [[رَبَّنَا لَا تُؤَاخِذْنَآ]] : apostrophe sans <i>yā</i> + <i>lā</i> + apocopé, ici une supplication. Les impératifs [[ٱعْفُ]] (défectueux), [[ٱغْفِرْ]], [[ٱرْحَمْنَآ]], [[ٱنصُرْنَا]] sont des prières.",
    },
    questions=[
        ("Relève les impératifs du verset 286.", "[[ٱعْفُ]], [[ٱغْفِرْ]], [[ٱرْحَمْ]] (+ <i>nā</i>), [[ٱنصُرْ]] (+ <i>nā</i>)"),
        ("Analyse [[تُؤَاخِذْنَآ]].", "inaccompli apocopé après <i>lā</i>, forme III, 2<sup>e</sup> m. sg., + pronom objet <i>-nā</i>"),
        ("Pourquoi [[رَبَّنَا]] est-il à l'accusatif ?", "apostrophe d'un nom annexé"),
        ("Distingue [[كَسَبَتْ]] et [[ٱكْتَسَبَتْ]].", "forme I (acquérir, surtout le bien) / forme VIII (acquérir, ici le mal)"),
    ],
)

R[3] = dict(
    intro=r"""<p>La sourate ar-Raḥmān s'ouvre sur l'enseignement du Coran, puis énumère les bienfaits de la création. Le refrain [[فَبِأَىِّ ءَالَآءِ رَبِّكُمَا تُكَذِّبَانِ]] s'adresse aux deux espèces responsables, djinns et humains (d'où le duel).</p>""",
    notes={
        (55, 1): "[[ٱلرَّحْمَٰنُ]] est le mubtadaʾ ; son khabar est la phrase verbale du verset 2.",
        (55, 4): "{{q 55:4}} : deux compléments de la forme II [[عَلَّمَ]].",
        (55, 6): "{{q 55:6}} : verbe au duel pour deux sujets coordonnés.",
        (55, 7): "{{q 55:7|from=والسماء|to=رفعها}} : [[ٱلسَّمَآءَ]] est à l'accusatif, complément mis en tête et repris par <i>-hā</i>.",
        (55, 9): "{{q 55:9|from=ولا|to=الميزان}} : défense, forme IV ; le nūn de <i>tukhsirūna</i> est tombé.",
    },
    questions=[
        ("Pourquoi [[ٱلسَّمَآءَ]] (v. 7) est-il à l'accusatif ?", "c'est le complément de [[رَفَعَ]], placé en tête"),
        ("Personne de [[يَسْجُدَانِ]] ?", "3<sup>e</sup> duel"),
        ("Relève une défense.", "[[وَلَا تُخْسِرُوا۟ ٱلْمِيزَانَ]]"),
        ("Pourquoi [[تُكَذِّبَانِ]] est-il au duel ?", "il s'adresse aux deux espèces, djinns et humains"),
    ],
)

R[4] = dict(
    intro=r"""<p>Luqmān, homme sage que le Coran ne présente pas comme prophète, conseille son fils : unicité d'Allah, gratitude envers les parents, prière, bien commandé et mal interdit, humilité dans la démarche et la voix.</p>""",
    notes={
        (31, 12): "{{q 31:12|from=أن|to=لله}} : <i>an</i> explicatif + impératif. {{q 31:12|from=ومن|to=لنفسه}} : condition + <i>innamā</i>.",
        (31, 13): "[[يَٰبُنَىَّ]] « ô mon cher fils » : diminutif apostrophé. {{q 31:13|from=إن|to=عظيم}} : <i>inna</i> + lām d'insistance.",
        (31, 14): "{{q 31:14|from=ووصينا|to=بوالديه}} : duel annexé (le nūn tombe). [[وَهْنًا عَلَىٰ وَهْنٍ]] : état (« faiblesse sur faiblesse »).",
        (31, 15): "{{q 31:15|from=وإن|to=تطعهما}} : verbe III au duel, réponse avec <i>fa-</i> + défense.",
        (31, 16): "[[إِن تَكُ]] = <i>in takun</i> : apocopé abrégé de [[كَانَ]] (L20, L31).",
        (31, 17): "Trois impératifs : [[أَقِمِ]] (concave), [[وَأْمُرْ]] (hamzé), [[وَٱنْهَ]] (défectueux, le alif tombe).",
        (31, 19): "[[ٱغْضُضْ]] : impératif d'un verbe sourd, sans fusion. {{q 31:19|from=إن|to=الحمير}} : élatif + lām d'insistance.",
    },
    questions=[
        ("Relève les défenses (lā + apocopé) des versets 13 à 18.", "[[لَا تُشْرِكْ]], [[فَلَا تُطِعْهُمَا]], [[وَلَا تُصَعِّرْ]], [[وَلَا تَمْشِ]]"),
        ("Analyse [[ٱنْهَ]].", "impératif de [[نَهَى]] (défectueux) : la voyelle finale tombe"),
        ("Que signifie [[بِوَٰلِدَيْهِ]] et pourquoi le nūn manque-t-il ?", "« envers ses deux parents » : duel annexé au pronom"),
        ("Fonction de [[مَعْرُوفًا]] (v. 15) ?", "complément de manière : « de façon convenable »"),
    ],
)

R[5] = dict(
    intro=r"""<p>Suite du récit commencé en leçon 31 : Maryam se retire, met au monde ʿĪsā au pied d'un palmier, revient vers les siens ; l'enfant parle au berceau et se présente comme serviteur d'Allah.</p>""",
    notes={
        (19, 23): "{{q 19:23|from=ياليتني|to=هذا}} : <i>layta</i> + pronom ; [[مِتُّ]] « je serais morte » : concave devant consonne (<i>māta</i> → <i>mittu</i>).",
        (19, 24): "[[أَلَّا تَحْزَنِى]] = <i>an lā taḥzanī</i> : subjonctif 2<sup>e</sup> f. sg., le nūn est tombé.",
        (19, 25): "[[وَهُزِّىٓ]] impératif féminin d'un sourd ; [[تُسَٰقِطْ]] apocopé en réponse à l'impératif.",
        (19, 26): "[[وَقَرِّى عَيْنًا]] « et sois consolée » (litt. « rafraîchis-toi quant à l'œil ») : tamyīz. [[فَإِمَّا تَرَيِنَّ]] = <i>in</i> + <i>mā</i> + nūn d'insistance.",
        (19, 28): "{{q 19:28|from=ما|to=سوء}} : <i>kāna</i>, nom [[أَبُوكِ]] (cinq noms : <i>-ū</i>), khabar [[ٱمْرَأَ]] à l'accusatif.",
        (19, 30): "{{q 19:30|from=قال|to=الله}} : premières paroles de ʿĪsā : « je suis le serviteur d'Allah ».",
        (19, 31): "[[مَا دُمْتُ حَيًّا]] « tant que je serai vivant » : <i>mā dāma</i>, sœur de <i>kāna</i>.",
    },
    questions=[
        ("Analyse [[أَبُوكِ]] (v. 28).", "nom de <i>kāna</i> au nominatif (cinq noms) + pronom 2<sup>e</sup> f. sg."),
        ("Relève trois impératifs féminins.", "[[وَهُزِّىٓ]], [[فَكُلِى]], [[وَٱشْرَبِى]] (aussi [[وَقَرِّى]], [[فَقُولِىٓ]])"),
        ("Pourquoi [[صَبِيًّا]] (v. 29) est-il à l'accusatif ?", "khabar de <i>kāna</i>"),
        ("Que marque [[مَا دُمْتُ]] ?", "la durée : « tant que »"),
    ],
)

R[6] = dict(
    intro=r"""<p>Des jeunes gens croyants fuient leur peuple idolâtre et se réfugient dans une caverne, où Allah les fait dormir de longues années. Le récit (18:9-26) se lit ici dans sa première partie.</p>""",
    notes={
        (18, 9): "[[أَمْ حَسِبْتَ]] « ou bien as-tu pensé… ? » ; {{q 18:9|from=كانوا|to=عجبا}} : khabar de <i>kāna</i> + état.",
        (18, 10): "{{q 18:10|from=ربنا|to=رشدا}} : deux impératifs de prière ([[ءَاتِنَا]] de [[ءَاتَى]], [[وَهَيِّئْ]] forme II hamzée).",
        (18, 11): "[[فَضَرَبْنَا عَلَىٰٓ ءَاذَانِهِمْ]] « Nous avons frappé leurs oreilles » : image du sommeil profond. [[سِنِينَ عَدَدًا]] « un nombre d'années ».",
        (18, 14): "{{q 18:14|from=لن|to=إلها}} : subjonctif d'un défectueux ([[نَّدْعُوَا۟]]). [[لَّقَدْ قُلْنَآ إِذًا شَطَطًا]] « nous aurions alors dit une énormité ».",
        (18, 15): "[[لَّوْلَا يَأْتُونَ]] « que n'apportent-ils… ! » : <i>lawlā</i> d'incitation. {{q 18:15|from=فمن|to=كذبا}} : élatif interrogatif.",
    },
    questions=[
        ("Analyse [[ٱلْفِتْيَةُ]] (v. 10).", "agent de [[أَوَى]], nominatif, pluriel interne de [[فَتًى]]"),
        ("Pourquoi [[نَّدْعُوَا۟]] se termine-t-il par une fatḥa ?", "subjonctif après [[لَن]] (défectueux en <i>-ū</i>)"),
        ("Que signifie [[أَىُّ ٱلْحِزْبَيْنِ أَحْصَىٰ]] ?", "« lequel des deux groupes a mieux compté (la durée) »"),
        ("Fonction de [[عَجَبًا]] (v. 9) ?", "khabar de <i>kāna</i>, à l'accusatif (« une merveille »)"),
    ],
)

R[7] = dict(
    intro=r"""<p>Une série de commandements de la sourate al-Isrāʾ : n'adorer qu'Allah, bonté envers les parents, droits des proches, refus du gaspillage et de l'avarice.</p>""",
    notes={
        (17, 23): "{{q 17:23|from=وقضى|to=إياه}} : restriction (négation + <i>illā</i>) ; [[إِيَّاهُ]] objet isolé. [[وَبِٱلْوَٰلِدَيْنِ إِحْسَٰنًا]] : maṣdar qui remplace le verbe (« [soyez] bons »). [[إِمَّا يَبْلُغَنَّ]] : <i>in</i> + <i>mā</i> + nūn ; l'agent [[أَحَدُهُمَآ]] vient après le complément.",
        (17, 24): "{{q 17:24|from=رب|to=صغيرا}} : apostrophe, impératif + pronom duel ; [[صَغِيرًا]] état (« quand j'étais petit »).",
        (17, 26): "{{q 17:26|from=وآت|to=حقه}} : impératif de [[ءَاتَى]] ; [[ذَا]] accusatif des cinq noms. [[وَلَا تُبَذِّرْ تَبْذِيرًا]] : défense + complément absolu.",
        (17, 29): "{{q 17:29|from=ولا|to=عنقك}} : <i>jaʿala</i> à deux compléments ; image de l'avarice. [[كُلَّ ٱلْبَسْطِ]] « complètement » : complément absolu.",
    },
    questions=[
        ("Relève les défenses du passage.", "[[فَلَا تَقُل]], [[وَلَا تَنْهَرْهُمَا]], [[وَلَا تُبَذِّرْ]], [[وَلَا تَجْعَلْ]], [[وَلَا تَبْسُطْهَا]]"),
        ("Pourquoi [[ذَا]] et non [[ذُو]] au v. 26 ?", "complément d'objet : accusatif des cinq noms"),
        ("Analyse [[رَبَّيَانِى]].", "accompli forme II défectueux, 3<sup>e</sup> duel, + <i>-nī</i>"),
        ("Fonction de [[إِحْسَٰنًا]] (v. 23) ?", "maṣdar à l'accusatif remplaçant un verbe sous-entendu"),
    ],
)

R[8] = dict(
    intro=r"""<p>Portrait des « serviteurs du Tout-Miséricordieux » : humilité, prière nocturne, crainte de l'Enfer, juste mesure dans la dépense, refus du polythéisme, du meurtre et de la fornication ; le repentir sincère transforme les mauvaises actions en bonnes.</p>""",
    notes={
        (25, 63): "{{q 25:63|from=وعباد|to=هونا}} : mubtadaʾ annexé ; [[هَوْنًا]] « humblement » (manière). {{q 25:63|from=وإذا|to=سلاما}} : condition avec <i>idhā</i>.",
        (25, 64): "[[سُجَّدًا وَقِيَٰمًا]] : états ; [[سُجَّد]] est un pluriel interne de [[سَاجِد]].",
        (25, 66): "{{q 25:66}} : [[سَآءَتْ]] « quel mauvais (séjour) ! » + tamyīz [[مُسْتَقَرًّا]].",
        (25, 67): "{{q 25:67|from=والذين|to=يقتروا}} : <i>idhā</i> + accompli ; deux apocopés après <i>lam</i>.",
        (25, 68): "{{q 25:68|from=ومن|to=أثاما}} : condition ; [[يَلْقَ]] apocopé d'un défectueux.",
        (25, 70): "{{q 25:70|from=فأولئك|to=حسنات}} : <i>badala</i> à deux compléments.",
    },
    questions=[
        ("Où est le khabar de [[وَعِبَادُ ٱلرَّحْمَٰنِ]] ?", "loin, au v. 75 ([[أُو۟لَٰٓئِكَ يُجْزَوْنَ]]) ; les versets intermédiaires décrivent ces serviteurs"),
        ("Fonction de [[سُجَّدًا]] (v. 64) ?", "état (ḥāl)"),
        ("Analyse [[يَلْقَ]].", "inaccompli apocopé de [[لَقِيَ]] (réponse de condition), le yāʾ est tombé"),
        ("Pourquoi [[يُضَٰعَفْ]] est-il à l'apocopé ?", "il reprend (substitut) la réponse de la condition"),
    ],
)

R[9] = dict(
    intro=r"""<p>Fin de la sourate al-Ḥujurāt : l'égalité des humains devant Allah, la différence entre se soumettre (islām) et croire (īmān), la vraie foi prouvée par l'engagement.</p>""",
    notes={
        (49, 13): "{{q 49:13|from=إن@2|to=أتقاكم}} : nom et khabar de <i>inna</i> sont deux élatifs annexés.",
        (49, 14): "{{q 49:14|from=قالت|to=آمنا}} : verbe au féminin pour un pluriel interne. {{q 49:14|from=ولما|to=قلوبكم}} : <i>lammā</i> « pas encore ».",
        (49, 15): "{{q 49:15|from=إنما|to=يرتابوا}} : définition par restriction. {{q 49:15|from=أولئك|to=الصادقون}} : pronom de séparation.",
        (49, 17): "{{q 49:17|from=يمنون|to=أسلموا}} : <i>an</i> + accompli = « (le fait) qu'ils ont embrassé l'islam ».",
    },
    questions=[
        ("Analyse [[أَتْقَىٰكُمْ]].", "élatif de [[تَقِيّ]] annexé au pronom, khabar de <i>inna</i>"),
        ("Pourquoi [[قَالَتِ]] est-il au féminin ?", "l'agent [[ٱلْأَعْرَابُ]] est un pluriel interne"),
        ("Sens de [[لَمَّا]] + apocopé (v. 14) ?", "pas encore"),
        ("Fonction de [[شُعُوبًا]] (v. 13) ?", "second complément de [[جَعَلَ]]"),
    ],
)

R[10] = dict(
    intro=r"""<p>Mūsā aperçoit un feu dans la nuit ; il y trouve l'appel de son Seigneur, qui se présente à lui, lui ordonne la prière, lui donne deux signes (le bâton, la main) et l'envoie vers Pharaon.</p>""",
    notes={
        (20, 10): "{{q 20:10|from=امكثوا|to=نارا}} : impératif + <i>inna</i>. [[لَّعَلِّىٓ ءَاتِيكُم]] « peut-être vous en apporterai-je » : <i>laʿalla</i> + pronom.",
        (20, 11): "[[نُودِىَ]] : passif de [[نَادَى]] (forme III).",
        (20, 12): "[[فَٱخْلَعْ نَعْلَيْكَ]] : duel annexé, le nūn tombe.",
        (20, 14): "{{q 20:14|from=إنني|to=أنا@2}} : la profession d'unicité à la 1<sup>re</sup> personne.",
        (20, 15): "[[أَكَادُ أُخْفِيهَا]] « Je suis sur le point de la cacher » : <i>kāda</i> + inaccompli.",
        (20, 20): "[[فَإِذَا هِىَ حَيَّةٌ تَسْعَىٰ]] « et voici que c'était un serpent qui rampait » : <i>idhā</i> de surprise.",
        (20, 21): "[[خُذْهَا]] impératif de [[أَخَذَ]] ; [[وَلَا تَخَفْ]] défense d'un concave.",
    },
    questions=[
        ("Analyse [[نُودِىَ]].", "accompli passif, forme III défectueuse, 3<sup>e</sup> m. sg."),
        ("Pourquoi [[نَعْلَيْكَ]] n'a-t-il pas de nūn ?", "duel annexé au pronom"),
        ("Sens de [[إِذَا]] au v. 20 ?", "surprise : « et voici que »"),
        ("Relève trois impératifs de verbes faibles.", "[[أَقِمِ]] (concave), [[أَلْقِهَا]] (défectueux), [[خُذْهَا]] (hamzé)"),
    ],
)

R[11] = dict(
    intro=r"""<p>Ibrāhīm conteste l'idolâtrie de son père et de son peuple. Observant une étoile, la lune puis le soleil qui disparaissent, il montre qu'aucun astre ne peut être un seigneur, et tourne son visage vers le Créateur.</p>""",
    notes={
        (6, 74): "[[ءَازَرَ]] : nom propre diptote, apposé à [[لِأَبِيهِ]] (génitif en <i>-a</i>). {{q 6:74|from=أتتخذ|to=آلهة}} : <i>ittakhadha</i> à deux compléments.",
        (6, 75): "{{q 6:75|from=وكذلك|to=والأرض}} : forme IV de [[رَأَى]] à deux compléments.",
        (6, 76): "{{q 6:76|from=فلما|to=كوكبا}} : <i>lammā</i> « lorsque ». [[لَآ أُحِبُّ ٱلْءَافِلِينَ]] « je n'aime pas ceux qui disparaissent ».",
        (6, 77): "[[بَازِغًا]] : état. {{q 6:77|from=لئن|to=الضالين}} : serment implicite (<i>la-</i>) + condition + nūn d'insistance.",
        (6, 79): "[[حَنِيفًا]] : état (« en pur monothéiste »).",
    },
    questions=[
        ("Fonction de [[بَازِغًا]] (v. 77) ?", "état (ḥāl) de [[ٱلْقَمَرَ]]"),
        ("Pourquoi [[ءَازَرَ]] a-t-il une fatḥa après [[لِأَبِيهِ]] ?", "diptote : génitif en <i>-a</i>"),
        ("Analyse [[لَأَكُونَنَّ]].", "<i>la-</i> du serment + inaccompli de [[كَانَ]] + nūn d'insistance"),
        ("Quel est le sens de [[فَطَرَ]] ?", "créer originellement, sans modèle"),
    ],
)

R[12] = dict(
    intro=r"""<p>Le « verset de la lumière » compare la lumière d'Allah à une lampe placée dans une niche, brillant d'une huile si pure qu'elle éclaire presque sans feu. Un seul verset, une grammaire riche.</p>""",
    notes={
        (24, 35): "{{q 24:35|from=الله|to=والأرض}} : phrase nominale, annexion. {{q 24:35|from=مثل|to=مصباح}} : <i>ka-</i> + génitif, phrase qualifiant un indéfini. Les noms indéfinis ([[مِصْبَاحٌ]], [[زُجَاجَةٍ]]) sont repris ensuite avec l'article ([[ٱلْمِصْبَاحُ]], [[ٱلزُّجَاجَةُ]]). {{q 24:35|from=يكاد|to=نار}} : <i>kāda</i> + inaccompli ; <i>law</i> + <i>lam</i> = « même si… ne… pas ».",
    },
    questions=[
        ("Pourquoi [[مِصْبَاحٌ]] est-il indéfini, puis [[ٱلْمِصْبَاحُ]] défini ?", "première mention, puis reprise de ce qui est déjà connu"),
        ("Analyse [[يُوقَدُ]].", "inaccompli passif, forme IV ([[أَوْقَدَ]]), 3<sup>e</sup> m. sg."),
        ("Que signifie [[لَّا شَرْقِيَّةٍ وَلَا غَرْبِيَّةٍ]] ?", "ni orientale ni occidentale : adjectifs niés de [[شَجَرَةٍ]]"),
        ("Fonction de [[مَن يَشَآءُ]] ?", "complément d'objet de [[يَهْدِى]] (relatif)"),
    ],
)

R[13] = dict(
    intro=r"""<p>Méditation des « doués d'intelligence » sur la création, puis leur invocation : un modèle de prière coranique, construit sur des impératifs et des apostrophes [[رَبَّنَا]].</p>""",
    notes={
        (3, 190): "{{q 3:190|from=إن|to=والأرض}} : khabar de <i>inna</i> en tête, nom [[لَءَايَٰتٍ]] avec lām (pluriel féminin : accusatif en <i>-i</i>). [[لِّأُو۟لِى]] « pour ceux qui ont » : génitif pluriel de [[أُولُو]].",
        (3, 191): "[[قِيَٰمًا وَقُعُودًا]] : états. {{q 3:191|from=ربنا|to=باطلا}} : apostrophe, <i>mā</i> + accompli, [[بَٰطِلًا]] état. [[فَقِنَا]] : impératif de [[وَقَى]] (doublement faible) + <i>nā</i>.",
        (3, 193): "{{q 3:193|from=سمعنا|to=بربكم}} : participe + phrase qualifiante + <i>an</i> explicatif.",
        (3, 194): "[[وَلَا تُخْزِنَا]] : supplication (<i>lā</i> + apocopé).",
    },
    questions=[
        ("Analyse [[فَقِنَا]].", "impératif de [[وَقَى]] (1<sup>re</sup> et 3<sup>e</sup> radicales faibles) + pronom <i>-nā</i>"),
        ("Fonction de [[قِيَٰمًا]] (v. 191) ?", "état (ḥāl)"),
        ("Pourquoi [[لَءَايَٰتٍ]] a-t-il une kasra ?", "nom de <i>inna</i> au pluriel féminin : accusatif en <i>-i</i>"),
        ("Relève les impératifs du v. 193.", "[[ءَامِنُوا۟]], [[فَٱغْفِرْ]], [[وَكَفِّرْ]], [[وَتَوَفَّنَا]]"),
    ],
)

R[14] = dict(
    intro=r"""<p>Les versets du jeûne de Ramaḍān : prescription, dispenses du malade et du voyageur, mois de la descente du Coran, et cette parole qui interrompt la loi pour rassurer : « Je suis proche ».</p>""",
    notes={
        (2, 183): "{{q 2:183|from=كتب|to=الصيام}} : passif ; [[لَعَلَّكُمْ تَتَّقُونَ]] « afin que vous soyez pieux ».",
        (2, 184): "[[أَيَّامًا مَّعْدُودَٰتٍ]] : complément de temps. {{q 2:184|from=فمن|to=أخر}} : réponse nominale avec <i>fa-</i> ; [[أُخَرَ]] diptote.",
        (2, 185): "{{q 2:185|from=شهر|to=القرآن}} : khabar d'un mubtadaʾ sous-entendu ; passif IV. [[فَلْيَصُمْهُ]] : lām d'injonction + apocopé de [[صَامَ]].",
        (2, 186): "{{q 2:186|from=أجيب|to=دعان}} : le muṣḥaf n'écrit pas le yāʾ final de [[ٱلدَّاعِ]] et de [[دَعَانِ]] (= <i>daʿānī</i>).",
    },
    questions=[
        ("Analyse [[فَلْيَصُمْهُ]].", "<i>fa-</i> + lām d'injonction + apocopé de [[صَامَ]] + pronom <i>-hu</i> : « qu'il le jeûne »"),
        ("Fonction de [[أَيَّامًا]] (v. 184) ?", "complément de temps (accusatif)"),
        ("Pourquoi la réponse [[فَعِدَّةٌ]] a-t-elle <i>fa-</i> ?", "réponse nominale"),
        ("Que remplace la kasra de [[دَعَانِ]] ?", "le pronom <i>-nī</i> (« quand il M'invoque »)"),
    ],
)

R[15] = dict(
    intro=r"""<p>Un appel à ceux qui ont commis des excès contre eux-mêmes : ne pas désespérer de la miséricorde d'Allah, revenir à Lui et se soumettre avant que vienne le châtiment.</p>""",
    notes={
        (39, 53): "{{q 39:53|from=قل|to=الله}} : apostrophe + relatif + défense. {{q 39:53|from=إن|to=جميعا}} : [[جَمِيعًا]] état.",
        (39, 54): "{{q 39:54|from=من|to=العذاب}} : <i>an</i> + subjonctif après [[مِن قَبْلِ]].",
        (39, 55): "[[بَغْتَةً]] : état ou complément de manière ; [[وَأَنتُمْ لَا تَشْعُرُونَ]] : phrase d'état.",
    },
    questions=[
        ("Analyse [[لَا تَقْنَطُوا۟]].", "défense : <i>lā</i> + apocopé 2<sup>e</sup> m. pl. (nūn tombé)"),
        ("Fonction de [[جَمِيعًا]] ?", "état : « tous, sans exception »"),
        ("Relève une phrase d'état.", "[[وَأَنتُمْ لَا تَشْعُرُونَ]]"),
    ],
)

R[16] = dict(
    intro=r"""<p>Juste avant les beaux noms d'Allah (lus en leçon 15), une exhortation : que chaque âme regarde ce qu'elle a préparé pour demain, et ne pas ressembler à ceux qui ont oublié Allah.</p>""",
    notes={
        (59, 18): "[[وَلْتَنظُرْ نَفْسٌ]] : lām d'injonction + apocopé, agent indéfini (« que chaque âme regarde »).",
        (59, 19): "{{q 59:19|from=ولا|to=أنفسهم}} : défense de <i>kāna</i> ; [[فَأَنسَىٰهُمْ]] forme IV à deux compléments.",
        (59, 21): "{{q 59:21|from=لو|to=الله}} : <i>law</i> irréel, réponse avec <i>la-</i>, deux états.",
    },
    questions=[
        ("Analyse [[وَلْتَنظُرْ]].", "lām d'injonction + apocopé 3<sup>e</sup> f. sg."),
        ("[[لَا يَسْتَوِىٓ]] (v. 20) : quelle forme ?", "forme VIII de س و ي, inaccompli nié"),
        ("Fonction de [[خَٰشِعًا مُّتَصَدِّعًا]] ?", "deux états de l'objet <i>-hu</i>"),
    ],
)

R[17] = dict(
    intro=r"""<p>Une cité rejette les messagers envoyés vers elle. Un homme accourt de l'extrémité de la ville pour défendre la vérité ; tué par les siens, il entre au Paradis et regrette seulement que son peuple ne sache pas.</p>""",
    notes={
        (36, 13): "{{q 36:13|from=إذ|to=المرسلون}} : verbe au singulier devant un agent pluriel.",
        (36, 14): "[[فَعَزَّزْنَا بِثَالِثٍ]] « Nous les avons renforcés par un troisième » : ordinal.",
        (36, 15): "{{q 36:15|from=ما|to=مثلنا}} : restriction.",
        (36, 18): "{{q 36:18|from=لئن|to=لنرجمنكم}} : serment implicite + condition + nūn d'insistance.",
        (36, 20): "{{q 36:20|from=وجاء|to=يسعى}} : complément avant l'agent indéfini, qualifié par une phrase. [[يَٰقَوْمِ]] = <i>yā qawmī</i>.",
        (36, 25): "[[فَٱسْمَعُونِ]] = <i>fa-smaʿūnī</i> « écoutez-moi » : le yāʾ n'est pas écrit.",
    },
    questions=[
        ("Pourquoi [[جَآءَهَا]] est-il au singulier (v. 13) ?", "le verbe précède son agent pluriel [[ٱلْمُرْسَلُونَ]]"),
        ("Analyse [[لَنَرْجُمَنَّكُمْ]].", "<i>la-</i> + inaccompli 1<sup>re</sup> pl. + nūn d'insistance + pronom objet"),
        ("Fonction de [[يَسْعَىٰ]] (v. 20) ?", "phrase qualifiant l'indéfini [[رَجُلٌ]]"),
        ("Que signifie [[يَٰلَيْتَ قَوْمِى يَعْلَمُونَ]] ?", "« si seulement mon peuple savait ! »"),
    ],
)

R[18] = dict(
    intro=r"""<p>Les versets de la prière du vendredi : laisser le commerce à l'appel, se disperser ensuite pour rechercher la grâce d'Allah, sans délaisser le rappel pour un divertissement.</p>""",
    notes={
        (62, 9): "{{q 62:9|from=إذا|to=الجمعة}} : passif de [[نَادَى]]. [[فَٱسْعَوْا۟]] impératif pluriel d'un défectueux ; [[وَذَرُوا۟]] impératif de [[وَذَرَ]] (le wāw tombe).",
        (62, 10): "{{q 62:10|from=فإذا|to=الصلاة}} : passif de [[قَضَى]]. [[كَثِيرًا]] : complément absolu (« beaucoup »).",
        (62, 11): "[[وَتَرَكُوكَ قَآئِمًا]] « et ils t'ont laissé debout » : état du pronom objet.",
    },
    questions=[
        ("Analyse [[ٱسْعَوْا۟]].", "impératif 2<sup>e</sup> m. pl. de [[سَعَى]] (défectueux)"),
        ("Fonction de [[قَآئِمًا]] ?", "état (ḥāl) de <i>-ka</i>"),
        ("Pourquoi [[قُضِيَتِ]] a-t-il une kasra finale ?", "le sukūn de <i>-t</i> devient kasra devant la hamzat al-waṣl"),
    ],
)
