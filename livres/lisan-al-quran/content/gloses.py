"""Gloses françaises des lemmes (numérotés comme content/lemmes_index.tsv).

Format d'une ligne : numéro|glose[|forme de dictionnaire]
La forme de dictionnaire remplace la forme du corpus quand celle-ci est
atypique (verbe cité à l'inaccompli, forme tronquée...).
"""

RAW = r"""
1|par, avec, au moyen de
2|nom
3|Allah
4|le, la, les (article)
5|le Tout-Miséricordieux (ar-Raḥmān)|رَحْمَٰن
6|très miséricordieux
7|louange
8|à, pour ; certes (devant le khabar)
9|seigneur, maître
10|monde (pl. : les mondes, l'univers)|عَالَم
11|maître, possesseur|مَالِك
12|jour
13|rétribution ; religion
14|support du pronom complément isolé (iyyā-)|إِيَّا
15|adorer
16|et
17|demander l'aide|اسْتَعَانَ
18|guider
19|chemin, voie
20|droit
21|celui qui, ce que (relatif)
22|combler de bienfaits
23|sur, contre, à la charge de
24|autre que, non
25|objet de la colère
26|ne… pas ; non
27|égaré
28|dire
29|un, unique ; quelqu'un
30|le Seul à être imploré (aṣ-Ṣamad)
31|ne… pas (passé, + apocopé)
32|engendrer
33|être
34|égal, équivalent|كُفُو
35|chercher refuge (auprès de)|عَاذَ
36|aube (naissante)
37|de, depuis, parmi
38|mal
39|ce que ; ce qui (relatif)
40|créer
41|ténèbres (de la nuit)
42|lorsque, quand (futur)
43|s'étendre, se répandre
44|souffleuse (de sortilèges)|نَفَّاثَة
45|dans
46|nœud
47|envieux
48|envier
49|gens, hommes
50|roi
51|divinité
52|le Tentateur, le chuchoteur|وَسْوَاس
53|celui qui se dérobe
54|souffler le mal, chuchoter
55|poitrine
56|djinns
57|temps (al-ʿaṣr)
58|certes (particule d'insistance)
59|être humain
60|perte
61|sauf, excepté
62|croire, avoir la foi
63|faire, œuvrer
64|bonne œuvre
65|se recommander mutuellement|تَوَاصَى
66|vérité ; droit
67|endurance, patience
68|donner, accorder
69|al-Kawthar (abondance)
70|alors, donc
71|prier, accomplir la prière
72|sacrifier (une bête)|نَحَرَ
73|qui hait
74|privé de postérité
75|faire descendre, révéler
76|nuit (une)
77|destin ; valeur (al-qadr)
78|faire connaître
79|bien ; meilleur
80|mille
81|mois
82|descendre peu à peu|تَنَزَّلَ
83|ange|مَلَك
84|esprit ; l'Esprit (Jibrīl)
85|permission
86|chaque, tout
87|ordre ; affaire
88|paix
89|jusqu'à
90|lever (de l'aube)
91|aube
92|soleil
93|clarté du jour, matinée
94|lune
95|suivre ; réciter
96|jour (opposé à la nuit)
97|faire apparaître
98|nuit
99|couvrir, envelopper
100|ciel
101|bâtir, édifier
102|terre
103|étendre
104|âme, personne
105|harmoniser, former parfaitement
106|inspirer
107|perversité
108|piété
109|déjà (+ accompli) ; parfois (+ inaccompli)
110|réussir, être heureux
111|celui qui, quiconque
112|purifier
113|échouer, être déçu
114|corrompre, étouffer
115|croyant
116|prière (rituelle)
117|humble, recueilli
118|de (loin de), au sujet de
119|futilité, parole vaine
120|qui se détourne
121|aumône purificatrice (zakāt)
122|qui fait, agissant
123|parties intimes
124|qui préserve, gardien
125|époux, épouse ; couple
126|ou
127|posséder|مَلَكَ
128|main droite ; serment
129|blâmé
130|chercher, désirer
131|derrière ; au-delà de
132|ce, celui-ci (démonstratif)
133|transgresseur|عَادٍ
134|dépôt confié
135|engagement, pacte
136|qui veille sur|رَاعٍ
137|veiller sur, observer|حَافَظَ
138|héritier
139|hériter
140|le Firdaws (le Paradis le plus haut)
141|éternel, qui demeure à jamais
142|argile sonore
143|comme (préposition)
144|poterie
145|djinn (premier ancêtre)
146|flamme pure
147|feu
148|quel ? lequel ?
149|bienfaits
150|traiter de mensonge, démentir
151|levant, orient
152|couchant, occident
153|laisser se joindre (deux mers)
154|mer
155|se rencontrer
156|entre
157|barrière, isthme
158|transgresser, empiéter
159|sortir
160|perle
161|corail
162|est-ce que ? (interrogation)
163|faire, rendre ; placer
164|lit, couche
165|montagne
166|piquets, pieux
167|sommeil
168|repos
169|vêtement
170|subsistance (moyen de vivre)
171|au-dessus de
172|sept
173|fort, dur, intense
174|lampe
175|ardent, éclatant
176|nuées chargées de pluie
177|eau
178|abondant (en flots)
179|faire sortir
180|grain
181|plantes, végétation
182|jardin ; le Paradis
183|touffus, entrelacés
184|figue
185|olive, olivier
186|mont
187|Sīnīn (le Sinaï)
188|particule d'attention (hā-)
189|pays, cité
190|sûr ; digne de confiance
191|plus beau, meilleur
192|forme, constitution
193|puis, ensuite
194|renvoyer, ramener
195|le plus bas
196|plus bas, inférieur
197|salaire, récompense
198|reproché ; interrompu (ghayr mamnūn : sans fin)
199|après
200|ne pas être
201|le plus sage, le meilleur (juge)
202|juge
203|non ! pas du tout !
204|livre, écrit
205|pieux, bienfaisant
206|ʿIlliyyūn (le registre des élus)
207|marqué, inscrit
208|témoigner ; être présent
209|rapproché (d'Allah)
210|délice
211|divans, lits ornés
212|regarder
213|reconnaître, connaître
214|visage
215|éclat, fraîcheur
216|abreuver (passif : recevoir à boire)|سَقَى
217|nectar
218|cacheté, scellé
219|cachet, sceau
220|musc
221|rivaliser|تَنَافَسَ
222|qui rivalise
223|mélange
224|Tasnīm (source du Paradis)
225|œil ; source
226|boire
227|lire, réciter
228|adhérence (caillot)
229|le plus noble, le très généreux
230|enseigner
231|calame, plume
232|savoir
233|dépasser les bornes
234|que (+ subjonctif), de (+ infinitif)
235|voir
236|se suffire à soi-même
237|vers, jusqu'à
238|retour
239|ô (vocatif)
240|mécréant
241|adorateur
242|s'étendre, se calmer (la nuit)
243|abandonner, faire ses adieux
244|détester
245|dernier ; l'au-delà (al-ākhira)
246|premier
247|bientôt, plus tard (futur)
248|agréer, être satisfait
249|trouver
250|orphelin
251|donner refuge, abriter
252|pauvre, dans le besoin
253|enrichir
254|quant à
255|opprimer|قَهَرَ
256|mendiant, qui demande
257|repousser durement|نَهَرَ
258|bienfait, grâce
259|parler de, raconter|حَدَّثَ
260|ouvrir, dilater
261|poser, déposer
262|fardeau (du péché)
263|accabler, faire ployer
264|dos
265|élever
266|rappel, mention ; renommée
267|avec
268|difficulté
269|facilité
270|finir, se libérer|فَرَغَ
271|s'appliquer avec effort|نَصِبَ
272|aspirer, désirer ardemment|رَغِبَ
273|comment ?
274|faire, agir
275|compagnons, gens de
276|éléphant
277|ruse, stratagème
278|égarement (fī taḍlīl : voué à l'échec)
279|envoyer
280|oiseaux
281|par volées
282|lancer, jeter
283|pierres
284|argile cuite
285|paille, feuilles (de céréales)
286|mangé, dévoré
287|pacte, habitude sécurisée
288|Quraysh
289|voyage
290|hiver
291|été
292|maison
293|nourrir
294|faim
295|peur
296|lorsque ; (yawma-idhin) ce jour-là
297|épanoui, heureux
298|effort
299|satisfait, agréé
300|élevé
301|entendre
302|parole futile
303|qui coule
304|lits
305|élevé, surélevé
306|coupes
307|posé, disposé
308|coussins
309|alignés, rangés
310|tapis
311|étendus, répandus
312|qui sait, connaisseur
313|l'invisible, le mystère
314|témoignage ; le visible
315|le Pur, le Saint (al-Quddūs)
316|le Prédominant, le Préservateur
317|puissant
318|le Contraignant (al-Jabbār)
319|le Superbe (al-Mutakabbir)
320|gloire à… ! (subḥāna)
321|associer (à Allah)
322|créateur
323|le Producteur (al-Bāriʾ)
324|le Formateur (al-Muṣawwir)
325|très beau, meilleur (fém.)
326|glorifier
327|sage
328|doute
329|guidée, bonne direction
330|pieux, qui craint Allah|مُتَّقٍ
331|accomplir (la prière), établir
332|pourvoir, attribuer (une subsistance)
333|dépenser (dans le bien)
334|avant
335|croire avec certitude|أَيْقَنَ
336|qui réussit
337|être béni, plein de bénédiction
338|main
339|royauté, royaume
340|chose
341|omnipotent
342|mort
343|vie
344|éprouver, mettre à l'épreuve|بَلَا
345|œuvre, action
346|pardonneur
347|superposés (en étages)
348|création
349|disproportion, défaut
350|revenir, retourner
351|vue, regard
352|est-ce que ? y a-t-il ?
353|fissure
354|fois, reprise
355|se retourner, revenir
356|humilié, bredouille
357|épuisé
358|embellir, orner
359|proche ; (ad-dunyā) ce bas monde
360|lampe
361|projectiles
362|diable, démon
363|préparer|أَعْتَدَ
364|châtiment
365|brasier
366|chameaux
367|étendre à plat|سَطَحَ
368|rappeler, exhorter|ذَكَّرَ
369|qui rappelle, exhortateur
370|qui exerce une autorité absolue
371|se détourner
372|mécroire, être ingrat
373|châtier
374|plus grand
375|retour
376|compte, jugement
377|tromper, leurrer
378|noble, généreux
379|équilibrer, rendre harmonieux
380|forme, image
381|vouloir
382|assembler, composer
383|mais plutôt, bien au contraire
384|scribe
385|coursière (cavale lancée)
386|halètement
387|qui fait jaillir des étincelles
388|frappement (des sabots)
389|qui lance l'assaut
390|matin
391|soulever|أَثَارَ
392|poussière
393|pénétrer au milieu|وَسَطَ
394|groupe, foule
395|ingrat
396|témoin
397|amour
398|être bouleversé (passif)|بَعْثَرَ
399|tombe
400|mettre au jour (passif : être dévoilé)|حَصَّلَ
401|parfaitement informé
402|venir ; apporter
403|temps, moment
404|temps (ad-dahr)
405|mentionné, digne de mention
406|goutte (de sperme)
407|mélangé
408|éprouver, mettre à l'épreuve
409|entendant (as-Samīʿ)
410|voyant (al-Baṣīr)
411|chemin, voie
412|soit… soit
413|reconnaissant
414|très ingrat
415|chaîne
416|carcan
417|coupe
418|camphre
419|serviteur, esclave
420|faire jaillir|فَجَّرَ
421|jaillissement
422|accomplir pleinement, tenir (un vœu)
423|vœu
424|craindre
425|qui se répand largement
426|nourriture
427|pauvre, indigent
428|captif
429|vouloir
430|rétribution, récompense
431|remerciement
432|sombre, renfrogné
433|terrible
434|froncer les sourcils
435|venir
436|aveugle
437|peut-être, afin que
438|se purifier
439|se souvenir, réfléchir
440|être utile, profiter
441|rappel, exhortation
442|s'empresser auprès de
443|courir ; s'efforcer
444|redouter, craindre
445|se désintéresser, se distraire
446|rappel
447|mentionner, se souvenir de
448|feuillets
449|honoré, vénéré
450|purifié
451|scribes (anges)
452|le Très-Haut
453|décréter, mesurer
454|pâturage
455|débris, herbe sèche
456|noirâtre
457|bientôt (préfixe du futur)
458|faire réciter|أَقْرَأَ
459|oublier
460|ce qui est dit à haute voix, le manifeste
461|être caché|خَفِيَ
462|faciliter
463|la voie la plus facile
464|si (condition) ; ne… que (négation, avec illā)
465|s'écarter de, éviter|تَجَنَّبَ
466|le plus misérable
467|brûler dans (le feu)|صَلِيَ
468|plus grand (fém.)
469|mourir
470|vivre|حَيِيَ
471|jurer|أَقْسَمَ
472|résidant ; licite
473|père, géniteur
474|peine
475|penser, croire, s'imaginer
476|ne… pas (futur, + subjonctif)
477|pouvoir, avoir pouvoir sur
478|anéantir ; dilapider
479|biens, richesse
480|abondant
481|langue
482|lèvre|شَفَة
483|voie (élevée)|نَجْد
484|revêtu d'un manteau
485|se lever, se tenir debout
486|avertir
487|proclamer la grandeur|كَبَّرَ
488|vêtements
489|purifier
490|souillure (des idoles)
491|délaisser, fuir|هَجَرَ
492|faire un don (en le rappelant)
493|chercher à obtenir davantage|اسْتَكْثَرَ
494|endurer, patienter
495|retentir, être sonné (passif)|نَقَرَ
496|trompe (du Jugement)
497|difficile, pénible
498|facile
499|distraire
500|course à l'accumulation
501|visiter|زَارَ
502|tombes
503|si (irréel)
504|savoir, science
505|certitude
506|nūn d'insistance
507|la Fournaise
508|demander, interroger
509|être enroulé, s'obscurcir (passif)|كَوَّرَ
510|étoile
511|s'éteindre, se ternir|انْكَدَرَ
512|être mis en marche (passif)|سَيَّرَ
513|chamelles pleines
514|être délaissé (passif)|عَطَّلَ
515|bêtes sauvages
516|rassembler
517|être embrasé (passif)|سَجَّرَ
518|être apparié (passif)|زَوَّجَ
519|fillette enterrée vivante
520|péché|ذَنْب
521|tuer
522|être déployé (passif)|نَشَرَ
523|être arraché (passif)|كَشَطَ
524|être attisé (passif)|سَعَّرَ
525|être rapproché (passif)|أَزْلَفَ
526|présenter, faire venir
527|tortuosité
528|droit, qui redresse
529|rigueur ; malheur
530|auprès de
531|annoncer une bonne nouvelle|بَشَّرَ
532|que (particule, comme inna)
533|beau, bon
534|demeurant
535|à jamais
536|prendre (pour), adopter
537|enfant
538|ancêtres, pères
539|être grave, énorme
540|parole, mot
541|bouches
542|mensonge
543|frères
544|réconcilier ; réformer
545|frère
546|craindre (Allah), se prémunir
547|faire miséricorde
548|se moquer
549|peuple, groupe d'hommes
550|il se peut que
551|femmes
552|dénigrer|لَمَزَ
553|s'affubler de sobriquets|تَنَابَزَ
554|sobriquets
555|quel mauvais… !
556|perversion
557|foi
558|se repentir
559|injuste
560|éviter|اجْتَنَبَ
561|beaucoup, nombreux
562|soupçon, conjecture
563|une partie, certains
564|péché
565|espionner|تَجَسَّسَ
566|médire (en l'absence)|اغْتَابَ
567|aimer|أَحَبَّ
568|manger
569|chair, viande
570|mort
571|détester
572|qui accueille sans cesse le repentir
573|secours, victoire
574|ouverture, conquête
575|entrer
576|groupe, foule
577|demander pardon
578|enveloppé (dans un manteau)
579|peu
580|moitié
581|diminuer|نَقَصَ
582|augmenter, ajouter
583|réciter posément|رَتَّلَ
584|Coran, récitation
585|récitation posée
586|jeter ; transmettre
587|parole
588|lourd
589|veillée nocturne
590|plus fort, plus intense
591|efficacité, emprise
592|plus droit
593|parole
594|occupations, va-et-vient
595|long
596|se consacrer entièrement|تَبَتَّلَ
597|consécration totale
598|garant, protecteur
599|délaissement
600|beau
601|musulman, soumis
602|musulmane
603|croyante
604|dévot, obéissant
605|dévote
606|véridique, sincère
607|véridique (fém.)
608|endurant
609|endurante
610|qui fait l'aumône
611|qui fait l'aumône (fém.)
612|jeûneur
613|jeûneuse
614|qui préserve (fém.)
615|qui invoque, qui se souvient
616|qui invoque (fém.)
617|préparer
618|pardon
619|immense
620|qui prend, recevant
621|donner, accorder
622|bienfaisant
623|dormir (la nuit)|هَجَعَ
624|dernières heures de la nuit
625|démuni
626|Maryam
627|se retirer à l'écart|انْتَبَذَ
628|famille, gens
629|lieu
630|oriental
631|en deçà, en dehors de
632|voile
633|prendre l'apparence de
634|être humain
635|bien proportionné
636|pieux
637|messager
638|donner, faire don
639|garçon
640|pur
641|comment ? d'où ?
642|toucher
643|impudique
644|facile
645|signe ; verset
646|miséricorde
647|décrété
648|apparaître dans sa clarté
649|mâle
650|femelle
651|divers
652|confirmer, croire vrai
653|être avare
654|la voie la plus difficile
655|servir à, être utile|أَغْنَى
656|tomber, périr
657|être secoué (passif)|زَلْزَلَ
658|secousse
659|fardeau
660|nouvelles, informations
661|révéler, inspirer
662|sortir, revenir|صَدَرَ
663|par groupes dispersés
664|faire voir (passif : être montré)|أَرَى
665|poids
666|atome, grain infime
667|repousser brutalement|دَعَّ
668|inciter, encourager|حَضَّ
669|malheur !
670|qui prie
671|négligent, distrait
672|agir par ostentation|رَاءَى
673|refuser, empêcher
674|ustensiles, menue aide
675|déclin (du soleil)
676|obscurité (de la nuit)
677|attesté
678|veiller en prière|تَهَجَّدَ
679|œuvre surérogatoire
680|ressusciter ; envoyer
681|station, rang
682|digne de louange
683|faire entrer|أَدْخَلَ
684|entrée
685|vérité, sincérité
686|sortie
687|pouvoir, preuve
688|secoureur
689|disparaître
690|faux, vain
691|voué à disparaître
692|apaisé
693|agréé
694|Zakariyyā
695|appeler
696|appel
697|discret
698|s'affaiblir
699|os
700|s'embraser (de blancheur)
701|tête
702|cheveux blancs
703|invocation
704|malheureux
705|proches (héritiers)
706|femme, épouse|ٱمْرَأَة
707|stérile
708|allié, protecteur ; héritier
709|famille
710|Yaʿqūb
711|agréé
712|ordonner
713|sincère, exclusif (dans le culte)
714|monothéiste pur
715|droite (la religion droite)
716|associateur
717|l'Enfer (Jahannam)
718|créatures
719|auprès de, chez
720|ʿAdn (séjour éternel)
721|couler|جَرَى
722|sous
723|rivière, fleuve
724|atteindre
725|terme, délai
726|retenir
727|convenable, ce qui est reconnu bon
728|se séparer de|فَارَقَ
729|prendre à témoin
730|doué de, possesseur de
731|justice ; juste
732|exhorter|وَعَظَ
733|issue
734|là où, d'où
735|escompter, s'attendre à|احْتَسَبَ
736|s'en remettre à|تَوَكَّلَ
737|ce qui suffit
738|qui atteint, qui accomplit
739|le Fracas (al-Qāriʿa)
740|papillons
741|dispersés
742|laine
743|cardée
744|être lourd|ثَقُلَ
745|balance
746|vie
747|être léger|خَفَّ
748|mère
749|abîme
750|ardent
751|dix
752|pair
753|impair
754|s'écouler (la nuit)|سَرَى
755|serment
756|raison, intelligence
757|Iram
758|colonnes
759|semblable, pareil
760|Thamūd
761|creuser, tailler|جَابَ
762|rocher
763|vallée
764|Firʿawn (Pharaon)
765|multiplier|أَكْثَرَ
766|corruption, désordre
767|déverser
768|fouet
769|aux aguets (lieu d'observation)
770|préférer
771|plus durable
772|Ibrāhīm
773|Mūsā
774|Yūsuf
775|père
776|dix (dans 11 à 19)
777|astre, étoile
778|prosterné
779|mon cher fils (diminutif)|بُنَيّ
780|raconter
781|rêve, vision
782|ruser contre|كَادَ
783|ennemi
784|clair, évident
785|élire, choisir
786|interprétation
787|récit, parole
788|parachever
789|les deux parents
790|Isḥāq
791|omniscient
792|vivant
793|subsistant par Lui-même
794|prendre, saisir
795|somnolence
796|intercéder|شَفَعَ
797|derrière
798|cerner, embrasser
799|contenir, embrasser
800|Trône (Kursī)
801|peser à, fatiguer|آدَ
802|garde, préservation
803|le Très-Haut
804|contrainte
805|devenir clair
806|droiture
807|égarement
808|ṭāghūt (fausses divinités)
809|saisir fermement
810|anse
811|la plus solide
812|rupture
813|ténèbres
814|lumière
815|montrer, divulguer|أَبْدَى
816|cacher|أَخْفَى
817|demander compte|حَاسَبَ
818|pardonner
819|faire distinction, séparer|فَرَّقَ
820|obéir
821|pardon
822|devenir, destination
823|imposer (une charge)|كَلَّفَ
824|capacité
825|acquérir, mériter
826|acquérir (le mal)
827|tenir rigueur, punir|آخَذَ
828|se tromper|أَخْطَأَ
829|porter
830|lourd fardeau
831|charger de|حَمَّلَ
832|force, capacité
833|effacer (les fautes)
834|maître, protecteur
835|secourir
836|expression claire
837|calcul précis
838|arbres, végétation
839|se prosterner
840|pesée
841|équité
842|fausser (la pesée), léser|أَخْسَرَ
843|créatures
844|fruit(s)
845|palmiers
846|spathes
847|plantes odoriférantes
848|Luqmān
849|sagesse
850|remercier
851|riche, qui se suffit
852|digne de louange
853|fils
854|association (polythéisme)
855|injustice
856|recommander
857|père et mère|وَالِدَانِ
858|faiblesse
859|sevrage
860|année
861|lutter, s'efforcer
862|côtoyer, accompagner|صَاحَبَ
863|suivre
864|revenir (repentant)
865|retour
866|informer
867|grain
868|moutarde (graine)
869|rocher
870|subtil, bienveillant
871|interdire
872|blâmable
873|atteindre, frapper
874|résolution
875|détourner (la joue) avec mépris|صَعَّرَ
876|joue
877|marcher|مَشَى
878|insolence
879|orgueilleux
880|vantard
881|être modéré|قَصَدَ
882|démarche
883|baisser (la voix, le regard)|غَضَّ
884|voix
885|le plus détestable
886|âne
887|éloigné
888|douleurs de l'enfantement
889|tronc
890|palmier
891|si seulement !
892|chose oubliée
893|totalement oublié
894|attrister|حَزَنَ
895|ruisseau
896|secouer|هَزَّ
897|faire tomber|سَاقَطَ
898|dattes fraîches
899|mûres, à cueillir
900|se réjouir, être consolé|قَرَّ
901|vouer, faire vœu|نَذَرَ
902|jeûne (abstinence)
903|parler à
904|humain
905|inouï, monstrueux
906|sœur
907|Hārūn
908|homme|ٱمْرُؤ
909|mal
910|faire signe|أَشَارَ
911|berceau
912|enfant, nourrisson
913|prophète
914|béni
915|où ? où que
916|recommander, prescrire|أَوْصَى
917|durer, demeurer|دَامَ
918|ou bien
919|caverne
920|ar-Raqīm (l'inscription)
921|merveille
922|se réfugier
923|jeunes gens
924|préparer, disposer|هَيَّأَ
925|droiture
926|frapper ; proposer (un exemple)
927|oreille
928|année|سَنَة
929|nombre
930|groupe, parti
931|plus exact à dénombrer
932|demeurer
933|durée
934|nouvelle, récit
935|lier, raffermir|رَبَطَ
936|cœur
937|appeler, invoquer
938|alors, dans ce cas
939|outrance
940|pourquoi ne… pas ? ; n'eût été
941|clair
942|plus injuste
943|inventer (un mensonge)
944|se tenir à l'écart
945|commodité
946|décréter
947|bienfaisance
948|vieillesse
949|tous deux
950|fi ! (agacement)
951|abaisser|خَفَضَ
952|aile
953|humilité
954|élever (un enfant)|رَبَّى
955|petit
956|plus savant, mieux informé
957|vertueux
958|qui revient sans cesse (à Allah)
959|proches parents
960|gaspiller|بَذَّرَ
961|gaspillage
962|gaspilleur
963|se détourner
964|recherche
965|espérer|رَجَا
966|aimable, facile
967|enchaînée, liée
968|cou
969|étendre
970|extension
971|s'asseoir, rester
972|démuni, épuisé
973|humilité, douceur
974|adresser la parole
975|ignorant
976|passer la nuit|بَاتَ
977|debout
978|détourner, écarter
979|implacable, permanent
980|être mauvais
981|demeure, séjour
982|lieu de séjour
983|dépasser la mesure
984|lésiner|قَتَرَ
985|juste milieu
986|autre
987|rendre sacré, interdire
988|forniquer|زَنَى
989|rencontrer|لَقِيَ
990|sanction (du péché)
991|doubler, multiplier|ضَاعَفَ
992|résurrection
993|demeurer éternellement|خَلَدَ
994|humilié
995|changer, remplacer
996|mauvaise action
997|bonne action
998|peuples
999|tribus
1000|se connaître mutuellement|تَعَارَفَ
1001|le plus pieux
1002|bédouins
1003|mais
1004|se soumettre (à Allah)
1005|pas encore ; lorsque
1006|diminuer, faire perdre|لَاتَ
1007|douter
1008|islam, soumission
1009|demeurer, attendre
1010|apercevoir
1011|tison
1012|ôter|خَلَعَ
1013|sandale|نَعْل
1014|sacré
1015|Ṭuwā
1016|choisir
1017|écouter
1018|l'Heure
1019|qui vient
1020|faillir, être sur le point de
1021|rétribuer
1022|détourner
1023|passion, désir
1024|périr|رَدِيَ
1025|bâton
1026|s'appuyer|تَوَكَّأَ
1027|abattre (des feuilles)|هَشَّ
1028|moutons
1029|usages
1030|serpent
1031|ramener, restituer|أَعَادَ
1032|état (premier)
1033|serrer, joindre|ضَمَّ
1034|blanc
1035|mal
1036|aller, s'en aller
1037|Āzar
1038|idoles
1039|égarement
1040|royaume
1041|convaincu
1042|couvrir (de ténèbres)
1043|disparaître (astre)
1044|qui disparaît
1045|qui se lève (astre)
1046|qui se lève (fém.)
1047|innocent ; qui désavoue
1048|tourner (le visage)|وَجَّهَ
1049|créer (originellement)
1050|exemple, parabole
1051|niche
1052|verre
1053|comme si
1054|brillant
1055|allumer|أَوْقَدَ
1056|arbre
1057|bénie
1058|olivier
1059|orientale
1060|occidentale
1061|huile
1062|éclairer
1063|alternance, divergence
1064|esprits, intelligences
1065|assis
1066|côté, flanc|جَنْب
1067|méditer|تَفَكَّرَ
1068|préserver
1069|couvrir d'opprobre|أَخْزَى
1070|crieur, appelant
1071|effacer (les péchés)
1072|rappeler à soi (faire mourir)
1073|promettre
1074|manquer (à une promesse)|أَخْلَفَ
1075|promesse, rendez-vous
1076|écrire ; prescrire
1077|jeûne
1078|comptés
1079|malade
1080|voyage
1081|nombre
1082|pouvoir supporter|أَطَاقَ
1083|compensation
1084|faire volontairement
1085|jeûner|صَامَ
1086|Ramaḍān
1087|preuve évidente
1088|discernement
1089|compléter|أَكْمَلَ
1090|proche
1091|répondre|أَجَابَ
1092|appel, prière
1093|celui qui invoque
1094|répondre (à un appel)
1095|être bien guidé|رَشَدَ
1096|désespérer|قَنَطَ
1097|tous ensemble
1098|soudainement
1099|se rendre compte|شَعَرَ
1100|avancer, présenter
1101|demain
1102|faire oublier
1103|pervers
1104|être égal ; s'établir
1105|triomphant
1106|qui se fend
1107|crainte
1108|cité
1109|envoyé
1110|deux|اثْنَانِ
1111|renforcer|عَزَّزَ
1112|troisième
1113|mentir
1114|transmission (du message)
1115|voir un mauvais présage|تَطَيَّرَ
1116|cesser
1117|lapider|رَجَمَ
1118|douloureux
1119|présage, sort
1120|outrancier
1121|extrémité
1122|ville
1123|homme
1124|bien guidé
1125|mal, préjudice
1126|intercession
1127|sauver
1128|honoré
1129|vendredi (jour du rassemblement)
1130|laisser|وَذَرَ
1131|commerce, vente
1132|se disperser|انْتَشَرَ
1133|grâce, faveur
1134|commerce
1135|divertissement
1136|se disperser|انْفَضَّ
1137|laisser, abandonner
1138|pourvoyeur
1139|être injuste, léser
1140|plus nombreux, la plupart
1141|mais (particule, comme inna)
1142|égarer
1143|communauté
1144|faire descendre (progressivement)
1145|avertisseur
1146|subsistance
1147|combattre
1148|s'égarer
1149|criminel
1150|faire vivre, ressusciter
1151|raisonner, comprendre|عَقَلَ
1152|promesse
1153|demeure
1154|penser, supposer
1155|juger
1156|Isrāʾīl
1157|Nūḥ
1158|pouvoir
1159|s'enorgueillir
1160|être guidé
1161|grand
1162|associé
1163|certes ! (attention)
1164|mort
1165|sauver
1166|mécréance
1167|bestiaux
1168|goûter|ذَاقَ
1169|jouissance (passagère)
1170|exposer clairement|بَيَّنَ
1171|diverger
1172|épreuve, tentation
1173|groupe
1174|sacré ; interdit
1175|perdant
1176|descendance
1177|suffire
1178|menteur
1179|issue, fin
1180|une (seule)
1181|bonne, pure
1182|un (seul)
1183|force
1184|tourner le dos
1185|notables
1186|jugement, sagesse
1187|voir, percevoir
1188|vent
1189|armée|جُنْد
1190|trône
1191|magie
1192|mosquée
1193|hommes
1194|devenir (au matin)
1195|égal
1196|porte
1197|inattentif
1198|hypocrite
1199|Lūṭ
1200|quoi ? qu'est-ce que ?
1201|tous
1202|passer, s'écouler
1203|engagement solennel
1204|Ādam
1205|ʿĪsā
1206|faute, grief
1207|lointain
1208|disputer|جَادَلَ
1209|groupe
1210|rencontre
1211|sauver
1212|maudire
1213|navire(s)
1214|permettre
1215|éprouver, tenter|فَتَنَ
1216|génération
1217|ouïe
1218|mais si ! (réponse affirmative)
"""


def load():
    out = {}
    for line in RAW.strip().splitlines():
        parts = line.split('|')
        n = int(parts[0])
        out[n] = (parts[1], parts[2] if len(parts) > 2 else None)
    return out
