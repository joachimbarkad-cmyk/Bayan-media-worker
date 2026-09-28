# HANDOFF — simulateur de trading halal, V1.2 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : cherchez les lectures d'information future, les chemins vers un statut
ADMISSIBLE erroné ou un achat non ADMISSIBLE, les affirmations non justifiées et les erreurs de calcul.

## 0. Suite donnée à la revue n° 2

Chaque cas a été **reproduit sur le commit 1d980c0**, corrigé, puis couvert par un test (`tests/test_review2.py`).
J'ai ensuite réintroduit chaque défaut un par un dans le code : à chaque fois, au moins un test échoue.

| Cas signalé | Correction | Test |
|---|---|---|
| Les trois ratios pointés vers `non_compliant_revenue / total_revenue` passaient la validation (y compris en référentiel « réel » complet) ; FXEPS devenait ADMISSIBLE | `RATIO_CATALOG` lie chaque type de ratio à **son** numérateur et à ses dénominateurs admis (dette et liquidités : capitalisation ou total de l'actif ; revenus non conformes : chiffre d'affaires). Tout identifiant hors catalogue est refusé. | `test_review_case_all_ratios_pointing_to_revenue_fields_is_refused`, `test_allowed_and_refused_denominators` |
| `data._num()` acceptait `nan` et `inf` ; une dette négative passait sous le plafond ; `value > max` ne détecte pas `nan` | Import : nombres non finis refusés (prix compris : `nan <= 0` valait `False`), valeurs négatives ou nulles impossibles refusées, revenus non conformes > chiffre d'affaires refusés. Filtre (défense en profondeur si les données sont construites en mémoire) : cause `DONNEE_INVALIDE` → INCERTAIN, ratio non fini ou négatif → INCERTAIN. | `test_review_case_nan_or_negative_debt_is_never_admissible`, `test_loader_rejects_non_finite_and_impossible_values`, `test_non_compliant_revenue_above_revenue_is_invalid` |
| `PointInTimeView.security()` renvoyait type d'instrument et devise sans date ; la liste des titres était connue dès le début | Fiche titre datée : `known_from` (obligatoire) et `delisted_date`. `security()` lève `LookaheadError` pour une fiche pas encore connue (règle J+1). `Dataset.universe_at(d)` : seuls les titres connus et non radiés sont filtrés à la date d. Titre détenu radié → vente, liquidation supposée au dernier cours coté. Données de démo : FXNU introduit en mars 2023, FXMU radié en juin 2024. | `test_review_case_security_record_known_later_is_not_used_earlier`, `test_listed_late_and_delisted_securities` |
| Seconde référence avec réinvestissement (règles proposées par le relecteur) | `reference_reinvestie`, règles écrites dans `docs/REFERENCES.md` et dans la docstring **avant** sa première exécution ; la référence achat-conservation est conservée | `test_reinvested_reference_rebuys_title_that_becomes_admissible_again`, `test_reinvested_reference_never_sells_to_rebalance_and_never_uses_sma` |
| Rapport | Libellés français des ratios à la place des identifiants ; phrase précisant qu'un ACHAT peut être réduit ou rejeté à l'ouverture ; trois colonnes de résultats | — |

**Point où je ne suis pas la revue :** elle juge trop rigide d'imposer trois types de ratios et six activités « cœur ».
Je les conserve volontairement : les assouplir rouvrirait la faille de la revue n° 1. Ils sont regroupés dans trois
constantes de `screening.py` et se modifient par le code, avec un test, si le référentiel choisi l'exige
(`docs/REFERENTIEL_ET_SOURCES.md` § 5).

**Documenté mais non codé :** horodatage, fuseau et version des publications (EDGAR distingue la date de dépôt et
l'heure d'acceptation) ; application rétroactive d'un référentiel unique ; changement de type d'instrument sans
historique daté (indétectable si `known_from` n'est pas mis à jour).

Rappel de la revue n° 1 (déjà corrigé en V1.1) : activités datées, règle J → J+1, validation du référentiel pour
données réelles, contrôle réseau réellement calculé, refus des devises mixtes, causes d'incertitude.

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- `python3 -m halal_sim run` tourne de bout en bout en environ une seconde, avec la seule bibliothèque standard de Python 3.11.
- Données fictives : 15 titres (dont 1 introduit et 1 radié en cours de période), 18 589 barres quotidiennes
  2021-01-04 → 2025-12-31, 244 états financiers trimestriels et 16 fiches d'activité datés par leur publication.
- Filtre à 3 statuts sur l'univers daté ; stratégie SMA 200 ; deux références ; frais, glissement, actions entières.
- Journal SQLite complet (`runs`, `screenings`, `decisions`, `orders`, `equity`, `metrics`) et rapport Markdown
  généré depuis la base, avec 9 contrôles recalculés.
- **61 tests** `unittest`, tous au vert : `python3 -m unittest discover -s tests -v`.

## 2. Choix et justification

| Sujet | Choix | Pourquoi |
|---|---|---|
| Langage / stockage | Python stdlib + SQLite, aucune dépendance | Coût nul, auditable |
| Stratégie | Détenir si clôture > SMA(200), revue mensuelle | Variante inspirée de la règle à 10 mois de Faber (2007) ; un paramètre, peu d'ordres |
| Chronologie | Décision à la clôture de fin de mois → exécution à l'ouverture suivante ; documents publiés le jour J utilisés à J+1 | Ni exécution au prix de décision ni ambiguïté sur l'heure de publication |
| Références | Achat-conservation et réinvestie (`docs/REFERENCES.md`) | La réinvestie isole l'apport de la SMA ; l'autre mesure le « ne rien faire » |
| Coûts | 1 € par ordre, glissement 10 pb ; refus si coût aller-retour estimé > 1,5 % | **Valeurs fictives** ; 1,5 % est une tolérance, pas un seuil de rentabilité établi |
| Politique titres détenus | EXCLU → vente ; INCERTAIN → vente (réglable par cause) ; radié → vente | Conservateur en attendant la décision de l'utilisateur |
| Seuils religieux | Démo : 20 % / 20 % / 3 % **arbitraires** ; modèle réel : `null` | Aucun seuil AAOIFI codé de mémoire ; texte primaire non consulté (accès bloqué) |

## 3. Résultats de la démonstration (données FICTIVES : aucune valeur probante)

Période 2021-10-29 → 2025-12-31, capital 2 000 € :

| | Stratégie | Réf. achat-conservation | Réf. réinvestie |
|---|---|---|---|
| Rendement total | +25,86 % | −3,92 % | +14,14 % |
| Baisse maximale | −11,82 % | −29,79 % | −28,86 % |
| Exposition moyenne | 44,4 % | 58,1 % | 81,1 % |
| Ordres | 41 | 11 | 19 |
| Coûts (% du capital) | 2,56 % | 0,66 % | 1,14 % |

À 500 € : aucun achat jugé pertinent (145 refus). À 10 000 € : stratégie +27,94 %, réinvestie +8,54 %.
Les chiffres changent par rapport à la V1.1 parce que l'univers contient maintenant FXNU et FXMU (ce dernier radié après une forte baisse).

**Sans valeur de preuve :** les prix fictifs contiennent une phase baissière en 2022 voulue pour faire jouer la règle,
ce qui avantage *par construction* un filtre de tendance. La référence réinvestie réduit l'écart dû au non-réinvestissement,
mais la conclusion reste impossible sur des données inventées.

## 4. Vérifications (61 tests, tous passés)

| Point critique | Défenses | Tests |
|---|---|---|
| Aucun achat non ADMISSIBLE, aucun ADMISSIBLE erroné | Stratégie, courtier simulé, contraintes et trigger SQLite ; référentiel structurellement validé (catalogue de ratios) ; données invalides refusées puis INCERTAIN | `test_incertain_never_bought.py` (5), `test_ruleset_validation.py` (10), `test_review2.py` (10), `test_screening.py` (11) |
| Aucun ordre réel | Aucun module de courtage ; analyse statique au lancement ; coupure réseau vérifiée ; `simulation_only` = 1 | `test_no_real_orders.py` (8) |
| Pas d'information future | `PointInTimeView` pour prix, états financiers, activités **et fiches titres** ; univers daté ; test de perturbation ; dates lues contraintes en base | `test_lookahead.py` (8), `test_review2.py` |
| Coûts et import | Frais, glissement, actions entières, pas de découvert ; import strict | `test_costs_and_data.py` (9) |

## 5. Limites connues

1. Données fictives uniquement.
2. Radiation : liquidation supposée au dernier cours coté (en réalité rachat, échange ou perte totale).
3. Pas de conversion de devises (refus si les devises diffèrent) ; dividendes, purification, fiscalité non modélisés.
4. Référentiel appliqué rétroactivement ; fiche titre modifiée sans `known_from` à jour indétectable.
5. Pas d'horodatage ni de fuseau des publications (indispensable avant des données réelles).
6. Capitalisation prise en fin de période (pas de moyenne glissante) ; aucune durée de validité d'une fiche d'activité.
7. Un seul paramètre, une seule période ; pas encore d'évaluation hors échantillon.
8. L'analyse statique et la coupure réseau ne remplacent pas une isolation système.
9. Le logiciel vérifie qu'une validation religieuse est **renseignée**, pas qu'elle a eu lieu ni que la source dit ce qui est codé.

## 6. Prochaines décisions

**Religieuses (à l'utilisateur) :** référentiel, dénominateur, seuils, classement du tabac, de l'armement, des médias et
de l'hôtellerie, politique par cause pour un titre détenu devenu INCERTAIN, purification.

**Compte ou coût (à l'utilisateur) :** marché visé ; grille tarifaire réelle d'un courtier envisagé (paramétrage seulement).

**Techniques proposées (gratuites) :** horodatage et version des documents ; historique daté des fiches titres ;
données réelles gratuites (SEC EDGAR avec heure d'acceptation, prix quotidiens dont les conditions seront vérifiées) ;
dividendes ; évaluation hors échantillon.

## 7. Questions pour le relecteur

1. Le catalogue `RATIO_CATALOG` est-il correct (en particulier : total de l'actif admis comme dénominateur de la dette et des liquidités) ?
2. Reste-t-il un chemin vers un ADMISSIBLE erroné, par exemple une combinaison de valeurs valides mais absurdes ?
3. La liquidation au dernier cours lors d'une radiation est-elle la bonne hypothèse par défaut, ou faut-il une valeur nulle par prudence ?
4. Les règles de la référence réinvestie (`docs/REFERENCES.md`) correspondent-elles à ta proposition ?
5. Les exigences structurelles rigides (§ 0) te paraissent-elles acceptables avec leur justification ?
