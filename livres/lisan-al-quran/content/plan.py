"""Plan du livre : parties, leçons, textes de lecture.

Chaque texte est une liste de plages (sourate, premier verset, dernier verset).
"""

PARTS = [
    ('I', 'Lire le texte coranique', 'قِرَاءَةُ النَّصِّ'),
    ('II', 'Le nom et la phrase nominale', 'الاسْمُ وَالْجُمْلَةُ الاسْمِيَّةُ'),
    ('III', 'Le verbe', 'الْفِعْلُ'),
    ('IV', 'La phrase verbale et ses compléments', 'الْجُمْلَةُ الْفِعْلِيَّةُ وَمُتَعَلَّقَاتُهَا'),
    ('V', 'Lectures suivies', 'نُصُوصٌ لِلْقِرَاءَةِ'),
]

# (numéro, partie, titre FR, titre AR, textes)
LESSONS = [
    (1, 'I', "Lettres, voyelles et signes", 'الْحُرُوفُ وَالْحَرَكَاتُ', [(1, 1, 7)]),
    (2, 'I', "L'écriture du muṣḥaf", 'الرَّسْمُ الْعُثْمَانِيُّ', [(112, 1, 4), (113, 1, 5), (114, 1, 6)]),
    (3, 'II', "Nom, verbe, particule ; racine et schème", 'الاسْمُ وَالْفِعْلُ وَالْحَرْفُ', [(103, 1, 3), (108, 1, 3)]),
    (4, 'II', "Défini et indéfini", 'الْمَعْرِفَةُ وَالنَّكِرَةُ', [(97, 1, 5)]),
    (5, 'II', "Le genre", 'الْمُذَكَّرُ وَالْمُؤَنَّثُ', [(91, 1, 10)]),
    (6, 'II', "Le duel et les pluriels réguliers", 'الْمُثَنَّى وَجَمْعُ السَّلَامَةِ', [(23, 1, 11), (55, 14, 23)]),
    (7, 'II', "Les pluriels internes", 'جَمْعُ التَّكْسِيرِ', [(78, 6, 16)]),
    (8, 'II', "Les trois cas", 'الْإِعْرَابُ', [(95, 1, 8)]),
    (9, 'II', "Les cas au duel, au pluriel et chez le diptote", 'عَلَامَاتُ الْإِعْرَابِ الْفَرْعِيَّةُ', [(83, 18, 28)]),
    (10, 'II', "Les prépositions", 'حُرُوفُ الْجَرِّ', [(96, 1, 8)]),
    (11, 'II', "Les pronoms isolés", 'الضَّمَائِرُ الْمُنْفَصِلَةُ', [(109, 1, 6)]),
    (12, 'II', "Les pronoms suffixes", 'الضَّمَائِرُ الْمُتَّصِلَةُ', [(93, 1, 11), (94, 1, 8)]),
    (13, 'II', "L'annexion", 'الْإِضَافَةُ', [(105, 1, 5), (106, 1, 4)]),
    (14, 'II', "L'adjectif épithète", 'النَّعْتُ', [(88, 8, 16)]),
    (15, 'II', "La phrase nominale", 'الْمُبْتَدَأُ وَالْخَبَرُ', [(59, 22, 24)]),
    (16, 'II', "Les démonstratifs", 'أَسْمَاءُ الْإِشَارَةِ', [(2, 1, 5)]),
    (17, 'II', "Les relatifs", 'الْأَسْمَاءُ الْمَوْصُولَةُ', [(67, 1, 5)]),
    (18, 'II', "L'interrogation et l'apostrophe", 'الِاسْتِفْهَامُ وَالنِّدَاءُ', [(88, 17, 26), (82, 6, 12)]),
    (19, 'II', "Inna et ses sœurs", 'إِنَّ وَأَخَوَاتُهَا', [(100, 1, 11)]),
    (20, 'II', "Kāna et ses sœurs", 'كَانَ وَأَخَوَاتُهَا', [(76, 1, 10)]),
    (21, 'III', "L'accompli", 'الْفِعْلُ الْمَاضِي', [(80, 1, 16)]),
    (22, 'III', "L'inaccompli", 'الْفِعْلُ الْمُضَارِعُ', [(87, 1, 13)]),
    (23, 'III', "Le subjonctif", 'الْمُضَارِعُ الْمَنْصُوبُ', [(90, 1, 10)]),
    (24, 'III', "L'apocopé et l'impératif", 'الْمَجْزُومُ وَالْأَمْرُ', [(74, 1, 10)]),
    (25, 'III', "Négation, futur et certitude", 'النَّفْيُ وَالِاسْتِقْبَالُ وَقَدْ', [(102, 1, 8)]),
    (26, 'III', "Le passif", 'الْمَبْنِيُّ لِلْمَجْهُولِ', [(81, 1, 14)]),
    (27, 'III', "Les formes dérivées II, III et IV", 'الْمَزِيدُ بِحَرْفٍ', [(18, 1, 5)]),
    (28, 'III', "Les formes dérivées V à X", 'الْمَزِيدُ بِحَرْفَيْنِ وَثَلَاثَةٍ', [(49, 10, 12)]),
    (29, 'III', "Le nom verbal (maṣdar)", 'الْمَصْدَرُ', [(110, 1, 3), (73, 1, 10)]),
    (30, 'III', "Les participes", 'اسْمُ الْفَاعِلِ وَاسْمُ الْمَفْعُولِ', [(33, 35, 35), (51, 15, 19)]),
    (31, 'III', "Verbes faibles (1) : assimilés et concaves", 'الْمِثَالُ وَالْأَجْوَفُ', [(19, 16, 21)]),
    (32, 'III', "Verbes faibles (2) : défectueux, sourds, hamzés", 'النَّاقِصُ وَالْمُضَعَّفُ وَالْمَهْمُوزُ', [(92, 1, 13)]),
    (33, 'IV', "La phrase verbale et l'agent", 'الْفِعْلُ وَالْفَاعِلُ', [(99, 1, 8)]),
    (34, 'IV', "Le complément d'objet", 'الْمَفْعُولُ بِهِ', [(107, 1, 7)]),
    (35, 'IV', "Les autres compléments", 'الْمَفْعُولُ فِيهِ وَلَهُ وَالْمُطْلَقُ', [(17, 78, 81)]),
    (36, 'IV', "L'état (ḥāl) et la spécification (tamyīz)", 'الْحَالُ وَالتَّمْيِيزُ', [(89, 27, 30), (19, 2, 6)]),
    (37, 'IV', "Exception et restriction", 'الِاسْتِثْنَاءُ وَالْحَصْرُ', [(98, 5, 8)]),
    (38, 'IV', "La condition", 'الشَّرْطُ', [(65, 2, 3), (101, 1, 11)]),
    (39, 'IV', "Le serment et l'insistance", 'الْقَسَمُ وَالتَّوْكِيدُ', [(89, 1, 14)]),
    (40, 'IV', "L'élatif et les nombres", 'اسْمُ التَّفْضِيلِ وَالْعَدَدُ', [(87, 14, 19), (12, 4, 6)]),
]

# Lectures suivies (partie V) : (numéro, titre, titre AR, plages)
READINGS = [
    (1, "Le Trône (Āyat al-Kursī)", 'آيَةُ الْكُرْسِيِّ', [(2, 255, 257)]),
    (2, "La fin d'al-Baqara", 'خَوَاتِيمُ الْبَقَرَةِ', [(2, 284, 286)]),
    (3, "Le Tout-Miséricordieux enseigne", 'الرَّحْمَٰنُ عَلَّمَ الْقُرْآنَ', [(55, 1, 13)]),
    (4, "Les conseils de Luqmān", 'وَصَايَا لُقْمَانَ', [(31, 12, 19)]),
    (5, "Maryam et la naissance de ʿĪsā", 'مَرْيَمُ وَمِيلَادُ عِيسَى', [(19, 22, 33)]),
    (6, "Les gens de la caverne", 'أَصْحَابُ الْكَهْفِ', [(18, 9, 16)]),
    (7, "Les recommandations d'al-Isrāʾ", 'وَصَايَا سُورَةِ الْإِسْرَاءِ', [(17, 23, 29)]),
    (8, "Les serviteurs du Tout-Miséricordieux", 'عِبَادُ الرَّحْمَٰنِ', [(25, 63, 70)]),
    (9, "Fraternité et piété", 'الْأُخُوَّةُ وَالتَّقْوَى', [(49, 13, 18)]),
    (10, "Mūsā au mont Ṭūr", 'مُوسَى عِنْدَ الطُّورِ', [(20, 9, 24)]),
    (11, "Ibrāhīm et les astres", 'إِبْرَاهِيمُ وَالْكَوَاكِبُ', [(6, 74, 79)]),
    (12, "Le verset de la lumière", 'آيَةُ النُّورِ', [(24, 35, 35)]),
    (13, "Les doués d'intelligence", 'أُولُو الْأَلْبَابِ', [(3, 190, 194)]),
    (14, "Le jeûne et l'invocation", 'الصِّيَامُ وَالدُّعَاءُ', [(2, 183, 186)]),
    (15, "Ne désespérez pas", 'لَا تَقْنَطُوا', [(39, 53, 55)]),
    (16, "Ce que chaque âme a préparé", 'وَلْتَنْظُرْ نَفْسٌ', [(59, 18, 21)]),
    (17, "Le messager de la cité", 'رَجُلٌ يَسْعَى', [(36, 13, 27)]),
    (18, "Le vendredi", 'الْجُمُعَةُ', [(62, 9, 11)]),
]


def expand(ranges):
    out = []
    for s, a, b in ranges:
        out.extend((s, x) for x in range(a, b + 1))
    return out
