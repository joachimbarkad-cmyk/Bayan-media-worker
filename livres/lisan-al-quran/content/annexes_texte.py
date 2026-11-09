"""Couverture, page de titre, introduction et présentation des parties."""

ETOILE = '''<svg width="150" height="150" viewBox="0 0 200 200" fill="none" stroke="#8FA6EC" stroke-width="1.6" aria-hidden="true">
<rect x="40" y="40" width="120" height="120"/><rect x="40" y="40" width="120" height="120" transform="rotate(45 100 100)"/>
<rect x="60" y="60" width="80" height="80"/><rect x="60" y="60" width="80" height="80" transform="rotate(45 100 100)"/>
<circle cx="100" cy="100" r="22"/><circle cx="100" cy="100" r="96"/></svg>'''

COUVERTURE = f'''<section class="couverture"><div class="bande"></div><div class="filet"></div><div class="cadre"></div><div class="cadre2"></div>
<div class="contenu">
<div class="sous">Méthode complète d'arabe coranique</div>
<div class="titre-ar">لِسَانُ ٱلْقُرْءَانِ</div>
<div class="titre">Lisān al-Qurʾān</div>
<div class="orn">{ETOILE}</div>
<div class="desc">Quarante leçons progressives · dix-huit lectures suivies<br>plus de cinq cents versets analysés mot à mot<br>une révision intégrée à chaque lecture</div>
<div class="bas">Volume unique</div>
</div></section>'''

PAGE_TITRE = r'''<section class="page-intro" style="break-after: page; height: 250mm; display: flex; flex-direction: column; justify-content: space-between;">
<div style="text-align:center; margin-top: 30mm;">
<div style="font-family:'Amiri Quran',serif; font-size: 40pt; color:#1F3FA6; direction: rtl; line-height: 1.8;">لِسَانُ ٱلْقُرْءَانِ</div>
<h1 style="font-size: 34pt; margin-top: 4mm;">Lisān al-Qurʾān</h1>
<div style="font-family:'Cormorant SC',serif; font-weight:600; font-size: 14pt; letter-spacing: 0.14em; color:#5A6385; margin-top: 4mm;">Comprendre la langue du Coran, de la première lettre à la lecture suivie</div>
</div>
<div style="font-size: 9.4pt; color:#3A4466; border-top: 0.3mm solid #C9D2EE; padding-top: 4mm;">
<p><b>Le texte coranique</b> est reproduit dans l'écriture du muṣḥaf (rasm ʿuthmānī), selon la lecture de Ḥafṣ d'après ʿĀṣim. Il provient du <i>Quranic Arabic Corpus</i> (texte Tanzil, analyse morphologique de K. Dukes et de ses collaborateurs, version corrigée publiée sous licence libre) et a été <b>contrôlé automatiquement, lettre par lettre</b>, contre le texte de l'encyclopédie QuranEnc. Les signes de pause sont repris de ce second texte.</p>
<p><b>La traduction du sens</b> des versets est celle de Muhammad Hamidullah, dans son édition révisée diffusée par QuranEnc. Une traduction reste une approche du sens : le texte arabe seul est le Coran.</p>
<p><b>Les analyses mot à mot</b> (nature, genre, nombre, cas, temps, forme, racine) sont tirées de l'analyse morphologique du corpus ; les sens donnés sont des sens de base, à préciser par le contexte et les commentaires (tafsīr). Les règles exposées suivent la grammaire arabe classique (naḥw et ṣarf).</p>
<p class="gris">Ouvrage d'étude personnelle. Toute remarque ou correction est la bienvenue.</p>
</div></section>'''

INTRO = r'''
<h2 style="font-size: 26pt; margin-bottom: 5mm;">Comment utiliser ce livre</h2>
<p>Ce livre s'adresse à toute personne francophone qui veut <b>comprendre directement le texte du Coran</b> : débutant complet qui découvre l'alphabet, ou lecteur qui sait déchiffrer sans comprendre. Il ne demande aucun prérequis. Il ne vise pas l'arabe parlé, mais la langue du Coran, dont il présente le vocabulaire le plus fréquent et toutes les structures grammaticales essentielles.</p>

<h3><span class="pastille">1</span>L'organisation</h3>
<ul>
<li><b>Partie I</b> (leçons 1–2) : lire le texte vocalisé du muṣḥaf.</li>
<li><b>Partie II</b> (leçons 3–20) : le nom, ses marques (défini, genre, nombre, cas), les pronoms, l'annexion, l'adjectif et la phrase nominale.</li>
<li><b>Partie III</b> (leçons 21–32) : le verbe — accompli, inaccompli et ses modes, passif, formes dérivées, nom verbal, participes, verbes faibles.</li>
<li><b>Partie IV</b> (leçons 33–40) : la phrase verbale et ses compléments, l'état, l'exception, la condition, le serment, l'élatif et les nombres.</li>
<li><b>Partie V</b> : dix-huit lectures suivies de passages célèbres, analysés mot à mot.</li>
<li><b>Annexes</b> : aide-mémoire, recueil de toutes les fiches, corrigés, lexique par racine, index des notions et des versets.</li>
</ul>

<h3><span class="pastille">2</span>Le déroulé d'une leçon</h3>
<ol>
<li><b>Révision express</b> : quelques questions sur les leçons précédentes, choisies à intervalles croissants (la leçon d'avant, deux leçons avant, quatre, huit…). Les réponses sont en bas de l'encadré : cache-les.</li>
<li><b>Exposé</b> : la règle, expliquée pas à pas et illustrée par des versets.</li>
<li><b>Fiche</b> : l'essentiel de la règle sur un seul encadré. Toutes les fiches sont réunies dans l'annexe B pour les révisions.</li>
<li><b>Vocabulaire</b> : une douzaine de mots, choisis parmi les plus fréquents du Coran et, d'abord, parmi ceux du texte de la leçon. Le nombre ×N indique combien de fois le mot apparaît dans le Coran. Une jauge indique la part des mots du Coran que tu reconnais déjà.</li>
<li><b>Exercices</b> : la plupart portent sur des versets réels. Les corrigés sont dans l'annexe C.</li>
<li><b>Texte de lecture</b> : un passage du Coran, verset par verset, avec l'analyse de chaque mot.</li>
</ol>

<h3><span class="pastille">3</span>La révision intégrée à la lecture</h3>
<p>On oublie ce qu'on ne revoit pas ; on retient ce qu'on revoit <b>au bon moment</b>, c'est-à-dire juste avant de l'oublier. Ce livre applique ce principe à la lecture elle-même : chaque notion de grammaire et chaque mot de vocabulaire sont suivis d'une leçon à l'autre. Quand un texte en présente un exemple au moment où il faut le revoir, l'analyse du mot le signale :</p>
<table class="t">
<tr><th>repère</th><th>sens</th><th>que faire ?</th></tr>
<tr><td><span class="m new">★ annexion</span></td><td>notion ou mot étudié dans <b>cette</b> leçon</td><td>l'analyser avec soin : c'est l'application directe</td></tr>
<tr><td><span class="m rev">↺13 annexion</span></td><td>notion étudiée en leçon 13, <b>à revoir maintenant</b></td><td>se redire la règle ; en cas de doute, relire la fiche 13</td></tr>
<tr><td><span class="m voc">↺7 vocabulaire</span></td><td>mot appris en leçon 7, à revoir maintenant</td><td>retrouver le sens avant de lire la colonne</td></tr>
<tr><td><span class="m ant">→24 impératif</span></td><td>notion étudiée plus loin, en leçon 24</td><td>simplement la remarquer</td></tr>
</table>
<p>Après chaque rappel, l'intervalle avant le rappel suivant double (une leçon, puis deux, quatre, huit…). Les notions bien installées reviennent donc de plus en plus rarement, et les lignes qui ne contiennent que du déjà-acquis apparaissent <span style="color:#7A82A0">en gris</span> : au fil du livre, le texte s'éclaircit sous tes yeux. Le <b>bilan de révision</b> qui clôt chaque texte indique la part du vocabulaire déjà étudié, les notions revues, et les fiches à relire parce qu'elles n'ont pas été rencontrées depuis longtemps.</p>

<h3><span class="pastille">4</span>Rythme conseillé</h3>
<p>Compte deux à trois séances par leçon : (1) révision express, exposé et fiche ; (2) vocabulaire et exercices ; (3) texte de lecture, à voix haute, d'abord avec la colonne du sens puis en la cachant. À raison de deux leçons par semaine, la partie IV est achevée en cinq mois ; les lectures suivies peuvent alors être lues une par séance, puis relues.</p>
<div class="encadre"><span class="lab">Une méthode de lecture</span>Pour chaque verset : 1. lis-le à voix haute ; 2. repère les mots connus ; 3. analyse les autres à l'aide du tableau ; 4. lis la traduction et vérifie que tu retrouves chaque idée dans l'arabe ; 5. relis le verset en comprenant. Avec le temps, l'étape 3 se réduit d'elle-même.</div>

<h3><span class="pastille">5</span>Transcription et abréviations</h3>
<table class="t">
<tr><th>lettres</th><th>transcription</th><th>lettres</th><th>transcription</th><th>lettres</th><th>transcription</th></tr>
<tr><td class="ar">ء ا ب ت ث</td><td>ʾ ā b t th</td><td class="ar">ز س ش ص ض</td><td>z s sh ṣ ḍ</td><td class="ar">ق ك ل م ن</td><td>q k l m n</td></tr>
<tr><td class="ar">ج ح خ د ذ</td><td>j ḥ kh d dh</td><td class="ar">ط ظ ع غ ف</td><td>ṭ ẓ ʿ gh f</td><td class="ar">ه و ي ة</td><td>h w/ū y/ī a/at</td></tr>
</table>
<p class="petit"><b>Abréviations</b> : m. masculin · f. féminin · sg. singulier · pl. pluriel · f. I–X forme verbale · rac. racine · pron. pronom · part. participe · L13 leçon 13 · T4 lecture suivie 4 · ج pluriel (dans les listes de vocabulaire) · 2:255 sourate 2, verset 255.</p>
'''

PARTIES = {
    'I': "<p>Avant de comprendre, il faut lire. Deux leçons suffisent pour déchiffrer le texte vocalisé du muṣḥaf, avec ses signes particuliers et ses règles de pause.</p>",
    'II': "<p>Le nom porte en lui toutes les marques de la langue : définition, genre, nombre et cas. On apprend ici à les reconnaître, puis à construire les groupes du nom (annexion, adjectif) et la phrase nominale, avec les particules qui la modifient.</p>",
    'III': "<p>Le verbe arabe se construit sur une racine et un schème. On apprend sa conjugaison, ses modes, son passif, puis les formes dérivées qui multiplient le vocabulaire, et enfin les verbes « faibles », très nombreux dans le Coran.</p>",
    'IV': "<p>La phrase verbale et ses compléments : l'agent, l'objet, les compléments de temps, de but, de manière, l'état, la spécification ; puis les grandes constructions du discours coranique : exception, restriction, condition, serment.</p>",
    'V': "<p>Des passages célèbres, lus de bout en bout, avec la même analyse mot à mot. Chaque lecture fait réviser l'ensemble du livre ; le bilan final indique ce qu'il reste à revoir.</p>",
}
