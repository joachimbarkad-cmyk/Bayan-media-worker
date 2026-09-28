# HANDOFF — simulateur de trading halal, V1.3 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, chemins vers un ADMISSIBLE erroné ou un
achat non ADMISSIBLE, valeurs encaissées sans prix négociable, affirmations non justifiées, erreurs de calcul.

**Le logiciel n'implémente encore aucun référentiel religieux réel complet** : il teste une mécanique de filtrage
avec des seuils de démonstration arbitraires, sur des données inventées.

## 0. Suite donnée à la revue n° 3

Chaque cas a été reproduit sur le commit 0e830bc, corrigé et couvert par `tests/test_review3.py`. J'ai ensuite
réintroduit chaque défaut dans le code : à chaque fois, au moins un test échoue.

| Cas signalé | Correction | Test |
|---|---|---|
| `PointInTimeView.security()` révélait au 31/01/2022 la radiation de FXMU du 28/06/2024 | La vue ne renvoie que les champs publics (`SECURITY_PUBLIC_FIELDS`) ; `delisted_date` n'apparaît qu'une fois la radiation passée (règle J+1) et sa lecture est tracée. Test de perturbation : repousser la radiation ne change aucune décision antérieure. | `test_review_case_future_delisting_not_exposed_by_view`, `test_changing_future_delisting_date_does_not_change_earlier_decisions` |
| Capitalisation de 1e300 → FXEPS ADMISSIBLE | Nouveau champ `shares_outstanding`. Quand un ratio utilise la capitalisation, elle est confrontée à nombre d'actions x cours de clôture de fin de période (écart toléré 5 %, contrôle de données et non seuil religieux) ; sinon INCERTAIN (`DONNEE_INVALIDE` ou `DONNEE_MANQUANTE`). Nouvelle incohérence refusée : liquidités > total de l'actif. | `test_review_case_absurd_market_cap_is_not_admissible` et 3 autres |
| Vente fictivement encaissée au dernier cours lors d'une radiation (260,83 € pour la référence réinvestie) | Aucune vente sans prix d'ouverture négociable. Radiation traitée au début du jour où elle survient : contrepartie en espèces créditée **seulement** si elle est documentée dans la fiche (`delisting_cash_per_share` + `delisting_source`) ; sinon position **gelée à valeur inconnue**, table `corporate_events`. Résultats principaux : titres gelés à 0 (borne basse) ; ligne séparée au dernier cours (borne haute). Nouveau contrôle indépendant : chaque exécution simulée correspond à un cours d'ouverture réellement coté ce jour-là. | `test_review_case_no_cash_credited_without_documented_consideration`, `test_documented_cash_consideration_is_credited`, `test_every_fill_matches_a_real_opening_price` |
| La référence réinvestie complétait ses lignes, pas la stratégie | Règle unique `sizing.topup_held_positions` (défaut `false`) pour les deux portefeuilles ; avec `true`, les deux complètent. Révision datée et justifiée dans `docs/REFERENCES.md` (les résultats V1.2 étaient connus : je le signale). | `test_default_no_topup_in_either_portfolio`, `test_topup_enabled_applies_to_both` |
| `RATIO_CATALOG` ne lie pas le dénominateur à une méthode datée ; FTSE/S&P non reproductibles | Chaque ratio déclare sa méthode `calcul` ; seule `ponctuel_derniere_publication` est implémentée, toute autre est refusée. Documentation explicite des référentiels non reproductibles (`docs/REFERENTIEL_ET_SOURCES.md` § 7 ; points rapportés par le relecteur, non vérifiés par moi). | `test_unsupported_or_missing_calculation_method_refused` |

Non traité (documenté) : lien formel entre chaque combinaison de champs et un texte daté (possible seulement une
fois un référentiel choisi) ; contrôle des créances ; moyennes glissantes ; annonce de radiation distincte de sa
prise d'effet ; provenance des données.

Rappels : revue n° 1 (activités datées, règle J → J+1, validation du référentiel, contrôle réseau réel, devises,
causes d'incertitude) et revue n° 2 (catalogue de ratios, nombres non finis, fiches titres et univers datés,
référence réinvestie) restent corrigées et testées.

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- `python3 -m halal_sim run` tourne de bout en bout en quelques secondes, bibliothèque standard de Python 3.11 uniquement.
- Données fictives : 15 titres (FXNU introduit en 2023, FXMU radié en 2024 sans contrepartie documentée),
  18 589 barres quotidiennes, 244 états financiers et 16 fiches d'activité datés par leur publication.
- Filtre à 3 statuts sur l'univers daté ; stratégie SMA 200 ; deux références ; frais, glissement, actions entières.
- SQLite : `runs`, `screenings`, `decisions`, `orders`, `equity` (avec valeur gelée), `corporate_events`, `metrics`.
- Rapport généré depuis la base, **10 contrôles** recalculés (dont le nouveau contrôle des cours d'ouverture).
- **73 tests** `unittest`, tous au vert.

## 2. Choix et justification

| Sujet | Choix | Pourquoi |
|---|---|---|
| Stratégie | Détenir si clôture > SMA(200), revue mensuelle, pas de complément | Variante inspirée de Faber (2007) ; un paramètre, peu d'ordres |
| Chronologie | Décision à la clôture de fin de mois → ouverture suivante ; documents publiés le jour J utilisés à J+1 ; radiation connue le jour où elle survient | Aucune anticipation |
| Références | Achat-conservation ; réinvestie avec la même règle de complément que la stratégie | La réinvestie isole au mieux l'effet de la SMA |
| Radiation | Gel à valeur inconnue sauf contrepartie documentée ; bornes 0 / dernier cours | Ni le dernier cours ni zéro ne sont une valeur par défaut fiable |
| Coûts | 1 € par ordre, glissement 10 pb ; refus si coût aller-retour estimé > 1,5 % | **Fictifs** ; 1,5 % est une tolérance, pas un seuil de rentabilité |
| Seuils religieux | Démo 20 % / 20 % / 3 % **arbitraires** ; modèle réel `null` | Aucun seuil codé de mémoire ; texte AAOIFI primaire non consulté |

## 3. Résultats de la démonstration (données FICTIVES : aucune valeur probante)

Période 2021-10-29 → 2025-12-31, capital 2 000 €. Titres radiés comptés à 0 ; entre parenthèses, au dernier cours.

| | Stratégie | Réf. achat-conservation | Réf. réinvestie |
|---|---|---|---|
| Rendement total | +25,86 % | −8,07 % (−3,86 %) | +4,43 % (+8,64 %) |
| Baisse maximale | −11,82 % | −29,79 % | −28,86 % |
| Exposition moyenne | 44,4 % | 58,8 % | 74,8 % |
| Ordres | 41 | 10 | 14 |
| Coûts (% du capital) | 2,56 % | 0,60 % | 0,84 % |

La stratégie avait vendu FXMU en 2023 (tendance baissière) et n'est pas touchée par sa radiation. À 500 € : aucun achat
jugé pertinent (145 refus). À 10 000 € : stratégie +27,94 %, réinvestie −1,11 %.

**Sans valeur de preuve :** prix inventés avec une phase baissière voulue en 2022 et un titre radié après une forte
baisse — deux situations qui avantagent *par construction* un filtre de tendance.

## 4. Vérifications (73 tests, tous passés)

| Point critique | Tests |
|---|---|
| Aucun achat non ADMISSIBLE, aucun ADMISSIBLE erroné | `test_incertain_never_bought.py` (5), `test_ruleset_validation.py` (10), `test_screening.py` (11), `test_review2.py` (10), `test_review3.py` (12) |
| Aucun ordre réel | `test_no_real_orders.py` (8) |
| Pas d'information future (prix, états financiers, activités, fiches titres, radiations) | `test_lookahead.py` (8), `test_review2.py`, `test_review3.py` |
| Coûts, import | `test_costs_and_data.py` (9) |

## 5. Limites connues

1. Données fictives uniquement ; aucun référentiel réel complet.
2. Radiation sans contrepartie documentée : valeur inconnue, seulement bornée (0 / dernier cours).
3. Capitalisation contrôlée par cohérence interne, pas par provenance ; total de l'actif non vérifiable au-delà de « liquidités ≤ actif ».
4. Pas de conversion de devises (refus) ; dividendes, purification, fiscalité non modélisés.
5. Référentiel appliqué rétroactivement ; pas d'horodatage ni de fuseau des publications.
6. Un seul paramètre, une seule période, pas d'évaluation hors échantillon.
7. Analyse statique et coupure réseau ≠ isolation système ; validation religieuse vérifiée dans sa forme seulement.

## 6. Prochaines décisions

**Religieuses (à l'utilisateur) :** référentiel, dénominateur, seuils, contrôles supplémentaires éventuels (créances),
classement du tabac, de l'armement, des médias et de l'hôtellerie, politique pour un titre devenu INCERTAIN, purification.

**Compte ou coût (à l'utilisateur) :** marché visé ; grille tarifaire réelle d'un courtier envisagé (paramétrage seulement).

**Techniques proposées (gratuites) :** horodatage et version des documents ; événements de radiation datés (annonce,
prise d'effet, contrepartie) ; données réelles gratuites avec provenance ; dividendes ; évaluation hors échantillon.

## 7. Questions pour le relecteur

1. Reste-t-il un champ ou une méthode de `PointInTimeView` ou du moteur qui expose une information future ?
2. Le gel à valeur inconnue et ses deux bornes sont-ils présentés honnêtement dans le rapport ?
3. Le contrôle de capitalisation (actions x cours, 5 %) crée-t-il de nouveaux faux INCERTAIN problématiques, par exemple autour des dates de fin de période non ouvrées ?
4. Avec la même règle de complément, l'écart stratégie / référence réinvestie isole-t-il désormais l'effet de la SMA, ou voyez-vous une autre différence de traitement ?
5. Faut-il passer maintenant aux données réelles d'essai (sans aucun ordre), ou reste-t-il un préalable bloquant ?
