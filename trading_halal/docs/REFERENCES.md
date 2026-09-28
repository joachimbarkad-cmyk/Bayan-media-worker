# Portefeuilles de référence : règles fixées avant le test

Les deux références partagent avec la stratégie : les données, l'univers daté, le filtre religieux, la politique
de vente des titres EXCLUS/INCERTAINS, les frais, le glissement, les actions entières, le plafond de coût
aller-retour (1,5 % par défaut) et l'ordre d'achat alphabétique. **Aucune n'utilise la moyenne mobile.**
Ces règles ont été écrites avant la première exécution de la référence réinvestie (V1.2) et ne doivent pas être
ajustées après avoir vu les résultats.

## Référence « achat-conservation » (`reference`)

1. Au premier jour de décision : cible = capital / nombre de titres ADMISSIBLES ; achat de chaque titre admissible
   (actions entières, plafond de coût ; une part refusée reste en liquidités).
2. Ensuite, aucune nouvelle position ni aucun complément.
3. Ventes imposées uniquement : titre EXCLU, titre INCERTAIN selon la politique, titre radié.
4. Le produit des ventes reste en liquidités (non rémunérées).

Ce qu'elle mesure : un investisseur qui achète une fois et ne touche plus à rien, sauf obligation.

## Référence « réinvestie » (`reference_reinvestie`)

Chaque dernier jour de bourse du mois, avec les seules données alors disponibles :

1. **Ventes imposées**, identiques à la référence précédente (EXCLU, INCERTAIN selon la politique, radiation),
   exécutées à l'ouverture suivante.
2. **Cible** par titre = valeur estimée du portefeuille (clôture du jour) / nombre de titres ADMISSIBLES du moment.
3. Pour chaque titre ADMISSIBLE, par ordre alphabétique, dont la valeur détenue est **sous** la cible :
   achat de l'écart, limité aux liquidités disponibles (liquidités + produit estimé des ventes du jour),
   en actions entières.
4. **Part trop petite** (moins d'une action entière, ou coût aller-retour estimé au-dessus du plafond) :
   pas d'achat ; les liquidités restent et la règle est réappliquée le mois suivant. Le refus est enregistré
   pour un titre non détenu ; un simple complément refusé n'est pas enregistré (il se produirait presque tous les mois).
5. **Titre redevenu ADMISSIBLE** : traité exactement comme les autres titres admissibles (point 3).
6. **Jamais de vente pour rééquilibrer** une ligne au-dessus de sa cible.

Ce qu'elle mesure : un investisseur discipliné qui reste investi dans l'univers admissible, sans règle de tendance.
L'écart entre la stratégie et cette référence est l'estimation la plus juste de l'apport de la moyenne mobile ;
l'écart avec la référence achat-conservation inclut aussi l'effet du réinvestissement.
