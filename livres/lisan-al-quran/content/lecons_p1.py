"""Partie I — Lire le texte coranique (leçons 1 et 2)."""

L = {}

L[1] = dict(
    objectifs=[
        "reconnaître les 28 lettres et leur prononciation",
        "lire les voyelles brèves, les voyelles longues, le sukūn, la shadda et le tanwīn",
        "lire sans hésiter la sourate al-Fātiḥa",
    ],
    expose=r"""
<p>L'arabe s'écrit et se lit <b>de droite à gauche</b>. Son alphabet compte <b>28 lettres</b>, qui sont toutes des consonnes : les voyelles brèves ne sont pas des lettres, mais de petits signes placés au-dessus ou au-dessous des lettres. Le texte du Coran est entièrement vocalisé : chaque lettre porte son signe. C'est une chance pour l'apprenant : tout ce qu'il faut prononcer est écrit.</p>

<h3><span class="pastille">1</span>Les lettres</h3>
<p>La plupart des lettres se lient à la suivante ; elles changent alors légèrement de forme (isolée, initiale, médiane, finale), mais leur « corps » reste reconnaissable. Six lettres ne se lient jamais à la lettre qui suit : [[ا د ذ ر ز و]].</p>
<table class="t">
<tr><th class="ar">lettre</th><th>nom</th><th>transcription</th><th>prononciation</th><th class="ar">lettre</th><th>nom</th><th>transcription</th><th>prononciation</th></tr>
<tr><td class="ar">ا</td><td>alif</td><td>ā</td><td>support de ā long ou de la hamza</td><td class="ar">ض</td><td>ḍād</td><td>ḍ</td><td>d emphatique</td></tr>
<tr><td class="ar">ب</td><td>bāʾ</td><td>b</td><td>b</td><td class="ar">ط</td><td>ṭāʾ</td><td>ṭ</td><td>t emphatique</td></tr>
<tr><td class="ar">ت</td><td>tāʾ</td><td>t</td><td>t</td><td class="ar">ظ</td><td>ẓāʾ</td><td>ẓ</td><td>dh emphatique</td></tr>
<tr><td class="ar">ث</td><td>thāʾ</td><td>th</td><td>th anglais de <i>think</i></td><td class="ar">ع</td><td>ʿayn</td><td>ʿ</td><td>contraction du fond de la gorge</td></tr>
<tr><td class="ar">ج</td><td>jīm</td><td>j</td><td>dj</td><td class="ar">غ</td><td>ghayn</td><td>gh</td><td>r grasseyé (gorge)</td></tr>
<tr><td class="ar">ح</td><td>ḥāʾ</td><td>ḥ</td><td>h soufflé, gorge resserrée</td><td class="ar">ف</td><td>fāʾ</td><td>f</td><td>f</td></tr>
<tr><td class="ar">خ</td><td>khāʾ</td><td>kh</td><td>j espagnol, <i>ch</i> allemand de <i>Bach</i></td><td class="ar">ق</td><td>qāf</td><td>q</td><td>k du fond de la gorge</td></tr>
<tr><td class="ar">د</td><td>dāl</td><td>d</td><td>d</td><td class="ar">ك</td><td>kāf</td><td>k</td><td>k</td></tr>
<tr><td class="ar">ذ</td><td>dhāl</td><td>dh</td><td>th anglais de <i>this</i></td><td class="ar">ل</td><td>lām</td><td>l</td><td>l</td></tr>
<tr><td class="ar">ر</td><td>rāʾ</td><td>r</td><td>r roulé</td><td class="ar">م</td><td>mīm</td><td>m</td><td>m</td></tr>
<tr><td class="ar">ز</td><td>zāy</td><td>z</td><td>z</td><td class="ar">ن</td><td>nūn</td><td>n</td><td>n</td></tr>
<tr><td class="ar">س</td><td>sīn</td><td>s</td><td>s (toujours sourd)</td><td class="ar">ه</td><td>hāʾ</td><td>h</td><td>h expiré, léger</td></tr>
<tr><td class="ar">ش</td><td>shīn</td><td>sh</td><td>ch de <i>chat</i></td><td class="ar">و</td><td>wāw</td><td>w / ū</td><td>w, ou support de ū long</td></tr>
<tr><td class="ar">ص</td><td>ṣād</td><td>ṣ</td><td>s emphatique</td><td class="ar">ي</td><td>yāʾ</td><td>y / ī</td><td>y, ou support de ī long</td></tr>
</table>
<p>À ces 28 lettres s'ajoute la <b>hamza</b> [[ء]] (transcrite ʾ), un coup de glotte comme entre les deux <i>a</i> de « la avenue ». Elle s'écrit seule ou sur un support : [[أ إ ؤ ئ]].</p>
<p>Les <b>lettres emphatiques</b> ([[ص ض ط ظ]], et dans une moindre mesure [[ق خ غ]]) se prononcent la langue reculée et creusée ; elles « assombrissent » la voyelle voisine. Les lettres du fond de la gorge ([[ع ح غ خ ه ء]]) demandent un peu d'entraînement : écoute un récitateur et répète.</p>

<h3><span class="pastille">2</span>Les voyelles brèves</h3>
<table class="t c">
<tr><th>signe</th><th>nom</th><th>son</th><th>exemple</th><th>lecture</th></tr>
<tr><td class="ar">بَ</td><td>fatḥa</td><td>a</td><td class="ar">كَتَبَ</td><td>kataba</td></tr>
<tr><td class="ar">بِ</td><td>kasra</td><td>i</td><td class="ar">بِسْمِ</td><td>bismi</td></tr>
<tr><td class="ar">بُ</td><td>ḍamma</td><td>u</td><td class="ar">نَعْبُدُ</td><td>naʿbudu</td></tr>
</table>
<p>Le <b>sukūn</b> [[◌ْ]] indique qu'une consonne <b>n'a pas de voyelle</b> : [[بِسْمِ]] se lit <i>bis-mi</i> ; le s n'est suivi d'aucune voyelle. Une syllabe arabe commence toujours par une consonne : on ne lit jamais deux voyelles de suite.</p>

<h3><span class="pastille">3</span>Les voyelles longues</h3>
<p>Une voyelle longue s'écrit avec une lettre de prolongation précédée de la voyelle brève correspondante :</p>
<ul>
<li><b>ā</b> : fatḥa + alif — [[قَالَ]] <i>qāla</i> (il a dit) ;</li>
<li><b>ī</b> : kasra + yāʾ — [[ٱلرَّحِيمِ]] <i>ar-raḥīm</i> ;</li>
<li><b>ū</b> : ḍamma + wāw — [[نُورٌ]] <i>nūr</i> (lumière).</li>
</ul>
<p>Quand wāw et yāʾ portent un sukūn après une fatḥa, on a une <b>diphtongue</b> : [[يَوْمِ]] <i>yawmi</i> (jour), [[غَيْرِ]] <i>ghayri</i> (autre que).</p>

<h3><span class="pastille">4</span>La shadda et le tanwīn</h3>
<p>La <b>shadda</b> [[◌ّ]] double la consonne : on la prononce deux fois, en appuyant. [[رَبِّ]] se lit <i>rab-bi</i> ; [[إِيَّاكَ]] <i>iy-yāka</i>. Ne jamais l'oublier : elle change le sens (<i>ʿalima</i> « il a su » ≠ <i>ʿallama</i> « il a enseigné »).</p>
<p>Le <b>tanwīn</b> (« nunation ») est une voyelle doublée en fin de nom : elle se lit voyelle + n. Il marque un nom <b>indéfini</b> (leçon 4).</p>
<table class="t c">
<tr><th>signe</th><th>lecture</th><th>exemple</th><th>lecture</th></tr>
<tr><td class="ar">◌ٌ</td><td>-un</td><td class="ar">أَحَدٌ</td><td>aḥadun</td></tr>
<tr><td class="ar">◌ً</td><td>-an (souvent écrit avec un alif : ◌ًا)</td><td class="ar">كِتَابًا</td><td>kitāban</td></tr>
<tr><td class="ar">◌ٍ</td><td>-in</td><td class="ar">يَوْمٍ</td><td>yawmin</td></tr>
</table>

<h3><span class="pastille">5</span>Première lecture : al-Fātiḥa</h3>
<p>Voici le premier verset, lettre par lettre : <i>bi-smi llāhi r-raḥmāni r-raḥīm</i> (« Au nom d'Allah, le Tout-Miséricordieux, le Très-Miséricordieux »).</p>
{{v 1:1}}
<p>Remarque trois choses que la leçon 2 expliquera : le signe [[ٱ]] au début de [[ٱللَّهِ]] (une hamza qui tombe en liaison), le petit alif vertical de [[ٱلرَّحْمَٰنِ]] (un ā long), et la shadda sur le r de <i>ar-raḥmān</i> (le l de l'article s'assimile).</p>
{{ex 1:2|hl=الحمد|com=<i>al-ḥamdu li-llāhi rabbi l-ʿālamīn</i> : sukūn sur le l et le m de [[ٱلْحَمْدُ]], shadda sur le b de [[رَبِّ]].}}
{{ex 1:5|hl=إياك@1,إياك@2|com=<i>iyyāka naʿbudu wa-iyyāka nastaʿīn</i> : shadda sur le y, ā long, sukūn sur le ʿayn et le s.}}
<div class="encadre"><span class="lab">Conseil de méthode</span>Lis chaque verset trois fois : lentement en détachant les syllabes, puis normalement, puis en écoutant un récitateur. La lecture fluide viendra en quelques semaines ; la grammaire s'appuiera sur elle.</div>
""",
    fiche=dict(
        titre='Les signes de lecture', ar='الْحَرَكَاتُ',
        corps=r"""
<table class="t c">
<tr><th>signe</th><th>nom</th><th>valeur</th><th>signe</th><th>nom</th><th>valeur</th></tr>
<tr><td class="ar">◌َ</td><td>fatḥa</td><td>a</td><td class="ar">◌ْ</td><td>sukūn</td><td>pas de voyelle</td></tr>
<tr><td class="ar">◌ِ</td><td>kasra</td><td>i</td><td class="ar">◌ّ</td><td>shadda</td><td>consonne doublée</td></tr>
<tr><td class="ar">◌ُ</td><td>ḍamma</td><td>u</td><td class="ar">◌ٌ ◌ً ◌ٍ</td><td>tanwīn</td><td>-un, -an, -in</td></tr>
<tr><td class="ar">◌َا</td><td>fatḥa + alif</td><td>ā</td><td class="ar">◌َوْ</td><td>diphtongue</td><td>aw</td></tr>
<tr><td class="ar">◌ِي</td><td>kasra + yāʾ</td><td>ī</td><td class="ar">◌َيْ</td><td>diphtongue</td><td>ay</td></tr>
<tr><td class="ar">◌ُو</td><td>ḍamma + wāw</td><td>ū</td><td class="ar">ء</td><td>hamza</td><td>coup de glotte ʾ</td></tr>
</table>
<ul>
<li>Une syllabe commence toujours par une consonne ; deux voyelles ne se suivent jamais.</li>
<li>Six lettres ne se lient pas à gauche : [[ا د ذ ر ز و]].</li>
</ul>""",
        pied="<b>Transcription :</b> ā ī ū voyelles longues ; ʿ = ʿayn ; ʾ = hamza ; ḥ ṣ ḍ ṭ ẓ = lettres d'arrière-gorge ou emphatiques ; th dh kh sh gh = une seule lettre arabe.",
    ),
    exercices=[
        dict(consigne="Lis puis transcris en lettres latines.", items=[
            ('[[كَتَبَ]]', 'kataba'), ('[[قَلَمٌ]]', 'qalamun'), ('[[يَوْمٍ]]', 'yawmin'), ('[[رَبِّ]]', 'rabbi'),
            ('[[نُورٌ]]', 'nūrun'), ('[[كِتَابًا]]', 'kitāban'), ('[[سَمِيعٌ]]', 'samīʿun'), ('[[قُلْ]]', 'qul'),
        ]),
        dict(consigne="Quelle(s) lettre(s) porte(nt) le signe demandé ?", items=[
            ('[[ٱلرَّحْمَٰنِ]] : la shadda', 'le rāʾ (ر) : <i>ar-raḥmān</i>'),
            ('[[إِيَّاكَ]] : la shadda', 'le yāʾ (ي) : <i>iyyāka</i>'),
            ('[[نَسْتَعِينُ]] : le sukūn', 'le sīn (س) : <i>nas-taʿīnu</i>'),
            ('[[ٱلْحَمْدُ]] : le sukūn', 'le lām et le mīm : <i>al-ḥam-du</i>'),
            ('[[غَيْرِ]] : la diphtongue', 'le yāʾ avec sukūn après fatḥa : <i>ghay-ri</i>'),
            ('[[ٱلْمُسْتَقِيمَ]] : la voyelle longue', 'le yāʾ après kasra : ī (<i>al-mustaqīm</i>)'),
        ]),
        dict(consigne="Associe chaque mot de la Fātiḥa à sa lecture : <i>yawmi · ṣirāṭa · māliki · ad-dīni · naʿbudu · ʿalayhim</i>.", items=[
            ('[[مَالِكِ]]', '<i>māliki</i>'), ('[[يَوْمِ]]', '<i>yawmi</i>'), ('[[ٱلدِّينِ]]', '<i>ad-dīni</i>'),
            ('[[صِرَاطَ]]', '<i>ṣirāṭa</i>'), ('[[نَعْبُدُ]]', '<i>naʿbudu</i>'), ('[[عَلَيْهِمْ]]', '<i>ʿalayhim</i>'),
        ]),
    ],
    flash=[
        ("Quel signe indique l'absence de voyelle ?", "le sukūn [[◌ْ]]"),
        ("Que fait la shadda [[◌ّ]] ?", "elle double la consonne : [[رَبّ]] <i>rabb</i>"),
        ("Comment se lit [[أَحَدٌ]] ?", "<i>aḥadun</i> (tanwīn de ḍamma)"),
        ("Quelles lettres notent les voyelles longues ?", "ا (ā), ي (ī), و (ū)"),
        ("Comment se lit [[قَالَ]] ?", "<i>qāla</i>"),
        ("Quelles lettres ne se lient pas à la suivante ?", "[[ا د ذ ر ز و]]"),
    ],
    notes={
        (1, 1): "<i>bi-smi llāhi r-raḥmāni r-raḥīm</i>. Le premier mot réunit [[بِ]] « par » et [[ٱسْم]] « nom ».",
        (1, 5): "Le pronom [[إِيَّاكَ]] « toi » est placé en tête pour dire « toi <b>seul</b> » (voir L34 et L37).",
    },
)

L[2] = dict(
    objectifs=[
        "lire les signes propres à l'écriture du muṣḥaf (rasm ʿuthmānī)",
        "savoir quand la hamza se prononce et quand elle tombe",
        "lire correctement à la pause, en fin de verset",
    ],
    expose=r"""
<p>Le Coran est écrit selon une orthographe ancienne, celle des copies réalisées sous le califat de ʿUthmān : le <b>rasm ʿuthmānī</b>. Les signes de lecture ajoutés plus tard (voyelles, petits signes) permettent de le lire exactement comme il est récité. Cette leçon présente les signes que tu rencontreras à chaque page.</p>

<h3><span class="pastille">1</span>Hamza qui tombe, hamza qui reste</h3>
<p>Le signe [[ٱ]] (alif surmonté d'une petite tête de ṣād) est la <b>hamzat al-waṣl</b>, « hamza de liaison ». Elle ne se prononce qu'en début de lecture ; au milieu d'une phrase, elle <b>tombe</b> et l'on enchaîne avec la voyelle précédente.</p>
{{ex 112:2|hl=الله,الصمد|com=En début de verset : <i>Allāhu ṣ-ṣamad</i>. La première hamza se prononce (on commence la lecture) ; celle de [[ٱلصَّمَدُ]] tombe : on ne dit pas <i>Allāhu aṣ-ṣamad</i>.}}
<p>À l'inverse, la <b>hamzat al-qaṭʿ</b> (« hamza de coupure »), écrite [[أ]] ou [[إ]], se prononce toujours : [[أَحَدٌ]] <i>aḥad</i>, [[إِيَّاكَ]] <i>iyyāka</i>.</p>

<h3><span class="pastille">2</span>L'alif suscrit et les petites lettres</h3>
<ul>
<li>Le petit alif vertical [[◌ٰ]] (alif suscrit) se lit <b>ā</b> long : [[ذَٰلِكَ]] <i>dhālika</i>, [[هَٰذَا]] <i>hādhā</i>, [[إِلَٰهِ]] <i>ilāhi</i>.</li>
<li>Un wāw ou un yāʾ suivi d'un alif suscrit se lit <b>ā</b> : [[ٱلصَّلَوٰةَ]] <i>aṣ-ṣalāta</i>, [[ٱلزَّكَوٰةَ]] <i>az-zakāta</i>, [[عَلَىٰ]] <i>ʿalā</i>.</li>
<li>Le petit wāw [[ۥ]] et le petit yāʾ [[ۦ]] allongent le pronom <i>hu</i>/<i>hi</i> : [[لَهُۥ]] <i>lahū</i>, [[بِهِۦ]] <i>bihī</i>.</li>
</ul>
{{ex 112:4|hl=له|com=<i>wa-lam yakun lahū kufuwan aḥad</i> : petit wāw sur [[لَّهُۥ]].}}

<h3><span class="pastille">3</span>Les lettres qui ne se prononcent pas</h3>
<p>Le petit zéro arrondi [[۟]] posé sur une lettre indique qu'elle <b>ne se prononce pas</b>. C'est le cas de l'alif qui suit le wāw du pluriel : [[كَفَرُوا۟]] <i>kafarū</i>, [[ءَامَنُوا۟]] <i>āmanū</i>. Le zéro ovale de [[أَنَا۠]] indique que l'alif final ne se prononce qu'à la pause : <i>ana</i> en liaison, <i>anā</i> à la pause.</p>
{{ex 103:3|hl=آمنوا,وعملوا|com=<i>illā lladhīna āmanū wa-ʿamilu ṣ-ṣāliḥāt</i>. L'alif final des deux verbes est muet.}}

<h3><span class="pastille">4</span>Madda, nūn et tanwīn</h3>
<ul>
<li>La <b>madda</b> [[◌ٓ]] signale une prolongation plus longue (deux à six temps) : [[جَآءَ]] <i>jāʾa</i>, [[ٱلضَّآلِّينَ]] <i>aḍ-ḍāllīn</i>.</li>
<li>Un petit mīm [[ۢ]] au-dessus d'un nūn ou d'un tanwīn indique qu'il se prononce <b>m</b> devant un b : [[مِنۢ بَعْدِ]] se lit <i>mim baʿdi</i>.</li>
</ul>

<h3><span class="pastille">5</span>Lettres solaires</h3>
<p>Devant certaines lettres, le l de l'article [[ٱلْ]] s'assimile : il ne se prononce pas et la lettre suivante porte une shadda. Ce sont les <b>lettres solaires</b> : [[ت ث د ذ ر ز س ش ص ض ط ظ ل ن]]. Les autres sont <b>lunaires</b> : le l se prononce.</p>
{{ex 114:1|hl=الناس|com=<i>bi-rabbi n-nās</i> : nūn solaire, le l ne s'entend pas. Compare [[ٱلْفَلَقِ]] <i>al-falaq</i> (113:1), lettre lunaire.}}

<h3><span class="pastille">6</span>Lire à la pause</h3>
<p>En fin de verset (et à chaque arrêt), on ne prononce pas la voyelle finale brève ni le tanwīn :</p>
<ul>
<li>[[ٱلرَّحِيمِ]] → <i>ar-raḥīm</i> ; [[أَحَدٌ]] → <i>aḥad</i> ;</li>
<li>le tanwīn <i>-an</i> devient <b>ā</b> : [[كِتَابًا]] → <i>kitābā</i> ;</li>
<li>le tāʾ marbūṭa [[ة]] se lit <b>h</b> : [[رَحْمَةً]] → <i>raḥmah</i>.</li>
</ul>
<p>Les petits signes au-dessus des lignes guident les arrêts : [[ۘ]] arrêt obligatoire, [[ۗ]] arrêt préférable, [[ۚ]] arrêt permis, [[ۖ]] liaison préférable, [[ۙ]] ne pas s'arrêter, [[ۛ]] s'arrêter à l'un des deux endroits marqués. Le numéro [[﴿١﴾]] clôt chaque verset.</p>
""",
    fiche=dict(
        titre="L'écriture du muṣḥaf", ar='الرَّسْمُ',
        corps=r"""
<table class="t">
<tr><th class="ar">signe</th><th>nom</th><th>lecture</th><th class="ar">exemple</th></tr>
<tr><td class="ar">ٱ</td><td>hamzat al-waṣl</td><td>prononcée en début de lecture, muette en liaison</td><td class="ar">بِسْمِ ٱللَّهِ</td></tr>
<tr><td class="ar">أ إ</td><td>hamzat al-qaṭʿ</td><td>toujours prononcée</td><td class="ar">أَحَدٌ</td></tr>
<tr><td class="ar">◌ٰ</td><td>alif suscrit</td><td>ā long</td><td class="ar">ذَٰلِكَ</td></tr>
<tr><td class="ar">وٰ ىٰ</td><td>wāw / yāʾ + alif suscrit</td><td>ā</td><td class="ar">ٱلصَّلَوٰةَ</td></tr>
<tr><td class="ar">ۥ ۦ</td><td>petit wāw, petit yāʾ</td><td>ū, ī longs (après hu, hi)</td><td class="ar">لَهُۥ</td></tr>
<tr><td class="ar">۟</td><td>petit zéro</td><td>lettre muette</td><td class="ar">كَفَرُوا۟</td></tr>
<tr><td class="ar">◌ٓ</td><td>madda</td><td>prolongation</td><td class="ar">جَآءَ</td></tr>
<tr><td class="ar">ۢ</td><td>petit mīm</td><td>n → m devant b</td><td class="ar">مِنۢ بَعْدِ</td></tr>
</table>
<ul>
<li>Lettres solaires : [[ت ث د ذ ر ز س ش ص ض ط ظ ل ن]] — le l de l'article ne se prononce pas.</li>
<li>À la pause : pas de voyelle finale ni de tanwīn ; <i>-an</i> → ā ; [[ة]] → h.</li>
</ul>""",
    ),
    exercices=[
        dict(consigne="Lis à voix haute puis transcris.", items=[
            ('[[قُلْ هُوَ ٱللَّهُ أَحَدٌ]]', '<i>qul huwa llāhu aḥad</i>'),
            ('[[مِن شَرِّ مَا خَلَقَ]]', '<i>min sharri mā khalaq</i>'),
            ('[[مَلِكِ ٱلنَّاسِ]]', '<i>maliki n-nās</i>'),
            ('[[إِلَٰهِ ٱلنَّاسِ]]', '<i>ilāhi n-nās</i>'),
            ('[[وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ]]', '<i>wa-min sharri ḥāsidin idhā ḥasad</i>'),
            ('[[ٱلَّذِى يُوَسْوِسُ]]', '<i>alladhī yuwaswisu</i>'),
        ]),
        dict(consigne="Quel signe propre au muṣḥaf chaque mot contient-il ? Comment se lit-il ?", items=[
            ('[[ذَٰلِكَ]]', 'alif suscrit : <i>dhālika</i>'),
            ('[[كَفَرُوا۟]]', "petit zéro, l'alif est muet : <i>kafarū</i>"),
            ('[[لَهُۥ]]', 'petit wāw : <i>lahū</i>'),
            ('[[ٱلْفَلَقِ]]', 'hamzat al-waṣl (et lettre lunaire) : <i>al-falaq</i>'),
            ('[[جَآءَ]]', 'madda : <i>jāʾa</i>'),
            ('[[ٱلصَّلَوٰةَ]]', 'wāw + alif suscrit lu ā : <i>aṣ-ṣalāta</i>'),
        ]),
        dict(consigne="Comment prononce-t-on ces mots à la pause ?", items=[
            ('[[أَحَدٌ]]', '<i>aḥad</i>'), ('[[كِتَابًا]]', '<i>kitābā</i>'), ('[[ٱلرَّحِيمِ]]', '<i>ar-raḥīm</i>'),
            ('[[رَحْمَةً]]', '<i>raḥmah</i>'), ('[[ٱلنَّاسِ]]', '<i>an-nās</i>'), ('[[هُدًى]]', '<i>hudā</i>'),
        ]),
    ],
    flash=[
        ("Que signifie le signe [[ٱ]] ?", "hamzat al-waṣl : muette en liaison"),
        ("Comment lit-on [[ذَٰلِكَ]] ?", "<i>dhālika</i> (alif suscrit = ā)"),
        ("À la pause, comment se lit [[كِتَابًا]] ?", "<i>kitābā</i>"),
        ("Que note le petit wāw de [[لَهُۥ]] ?", "un ū long : <i>lahū</i>"),
        ("Comment lit-on [[ٱلصَّلَوٰةَ]] ?", "<i>aṣ-ṣalāta</i>"),
        ("Le l de [[ٱلشَّمْسِ]] se prononce-t-il ?", "non : shīn est solaire, <i>ash-shams</i>"),
    ],
    notes={
        (112, 1): "<i>qul huwa llāhu aḥad</i> : la hamza de [[ٱللَّهُ]] tombe après <i>huwa</i>.",
        (113, 1): "<i>qul aʿūdhu bi-rabbi l-falaq</i>.",
        (114, 4): "[[ٱلْوَسْوَاسِ]] <i>al-waswās</i> : racine de quatre lettres (و س و س).",
    },
)
