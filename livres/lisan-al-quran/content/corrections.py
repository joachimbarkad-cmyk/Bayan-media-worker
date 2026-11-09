"""Corrections manuelles de l'étiquetage du corpus, par mot (sourate, verset, mot).

Chaque correction a été vérifiée sur le texte vocalisé et la grammaire classique.
Clés : case (cas corrigé), add / del (notions), sense, ana, nocase, noidafa, nonaat.
"""
CORR = {
    (55, 17, 2): dict(case='GEN', why="ٱلْمَشْرِقَيْنِ : complément du nom (رَبُّ ٱلْمَشْرِقَيْنِ) ; un duel en ‑ayni ne peut être au nominatif"),
    (55, 17, 4): dict(case='GEN', why="ٱلْمَغْرِبَيْنِ : complément du nom"),
    (36, 14, 4): dict(case='ACC', why="ٱثْنَيْنِ : complément d'objet de أَرْسَلْنَا"),
    (55, 12, 4): dict(case='NOM', why="وَٱلرَّيْحَانُ : ḍamma dans la lecture de Ḥafṣ, coordonné à ٱلْحَبُّ"),
    (80, 18, 2): dict(case='GEN', why="أَىِّ : après مِنْ"),
    (17, 26, 3): dict(case='GEN', why="ٱلْقُرْبَىٰ : complément du nom de ذَا"),
    (49, 10, 7): dict(case='GEN', why="أَخَوَيْكُمْ : complément du nom de بَيْنَ"),
    (55, 54, 7): dict(case='NOM', why="وَجَنَى : sujet de la phrase nominale (khabar دَانٍ)"),
    (55, 54, 8): dict(case='GEN', why="ٱلْجَنَّتَيْنِ : complément du nom de جَنَى"),
    (12, 5, 5): dict(case='ACC', why="رُءْيَاكَ : complément d'objet de لَا تَقْصُصْ"),
    (36, 12, 4): dict(case='ACC', why="ٱلْمَوْتَىٰ : complément d'objet de نُحْىِ"),
    (49, 13, 7): dict(case='GEN', why="وَأُنثَىٰ : coordonné à ذَكَرٍ (après مِن)"),
    (18, 1, 11): dict(case='ACC', why="عِوَجَا : complément d'objet de لَمْ يَجْعَلْ"),
    (36, 26, 6): dict(case='ACC', why="قَوْمِى : nom de لَيْتَ (sœur de inna)"),
    (20, 12, 9): dict(case='GEN', why="طُوًى : apposition à ٱلْوَادِ (génitif)"),
    # modes verbaux
    (9, 32, 7): dict(mood='IND', why="وَيَأْبَى : nouvelle proposition, indicatif"),
    (17, 25, 7): dict(mood='JUS', why="تَكُونُوا۟ : après إِن conditionnel, apocopé"),
    (36, 20, 6): dict(mood='IND', why="يَسْعَىٰ : phrase qualifiant رَجُلٌ, indicatif"),
    (49, 14, 16): dict(mood='JUS', why="تُطِيعُوا۟ : après إِن conditionnel, apocopé"),
}
