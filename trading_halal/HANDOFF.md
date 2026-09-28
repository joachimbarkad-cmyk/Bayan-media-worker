# HANDOFF — simulateur de trading halal, V1.1 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire ce projet de façon critique** : cherchez surtout les lectures de données futures, les failles
qui permettraient d'acheter un titre non ADMISSIBLE, les affirmations non justifiées et les erreurs de calcul des coûts.

## 0. Suite donnée à la revue n° 1 (ChatGPT)

Les trois défauts bloquants ont été **reproduits sur l'ancien code**, puis corrigés, et chacun est couvert par un test qui rejoue le cas exact :

| Défaut signalé | Correction | Test qui rejoue le cas |
|---|---|---|
| `PointInTimeView.security()` renvoyait l'activité sans contrôler sa date : une activité datée du 2025-12-01 modifiait le filtrage du 2021-10-29 | L'activité vient désormais d'un **historique daté** (`data/demo/activities_FICTIF.csv`) lu par `PointInTimeView.latest_activity()` ; `security()` ne renvoie plus que nom, type d'instrument et devise. Le test de perturbation falsifie aussi les fiches d'activité futures. | `test_lookahead.test_activity_published_later_does_not_affect_earlier_screening`, `test_changing_the_future_does_not_change_past_decisions`, `test_screening.test_activity_change_is_dated` |
| `available_date` ne distingue pas une publication avant ou après la clôture | Règle conservatrice : un document (état financier ou fiche d'activité) publié le jour J n'est utilisé qu'à partir de la décision de J+1 | `test_lookahead.test_documents_published_on_decision_day_are_not_used`, `test_screening.test_fundamentals_are_point_in_time` |
| Référentiel aux ratios vidés + booléens basculés → données REEL acceptées, FXALP ADMISSIBLE | `structural_problems()` (toujours appliquée, au chargement **et** au lancement) : trois familles de ratios obligatoires, seuils `null` ou dans ]0 ; 1], champs connus, instruments limités à `ACTION`, activités « cœur » présentes et jamais ADMISSIBLES. `real_data_problems()` pour les données réelles : texte source daté, chaque seuil renseigné et sourcé (source « DEMO »/« ARBITRAIRE » refusée), source du classement des activités, `validated_by`, `validated_on`. | `test_ruleset_validation.test_review_case_empty_ratios_and_flipped_flags_is_refused` et 6 autres tests |
| Contrôle « Aucun ordre réel » à `True` en dur | Remplacé par deux contrôles réellement calculés à chaque lancement : analyse statique du code (`safety.scan_package()` : importations réseau/courtage, `environ`, `getenv`, importation dynamique) et état effectif de la coupure réseau (`safety.network_blocked()`) | `test_no_real_orders.test_report_network_check_is_not_hardcoded` (le contrôle échoue bien quand le réseau n'est pas coupé), `test_static_scan_detects_forbidden_code` |

Autres points de la revue traités :
- **Devises** : refus explicite si un titre n'est pas dans la devise du portefeuille (la conversion n'existe pas encore) — `test_currency_mismatch_is_refused`.
- **INCERTAIN détenu** : chaque INCERTAIN porte maintenant sa cause (`ACTIVITE`, `DONNEE_MANQUANTE`, `DONNEE_PERIMEE`, `SEUIL_NON_DEFINI`). `holding_policy.on_incertain` accepte `SELL`, `HOLD` ou une politique par cause (cause non listée = vente). Défaut inchangé : vente. `on_exclu` n'accepte que `SELL`.
- **Rapport** : colonne « En clair » pour chaque code, seuil affiché à côté de chaque ratio avec la mention « seuil de DÉMO arbitraire », causes d'incertitude, date de la fiche d'activité, rappel que ADMISSIBLE n'est pas une certification.
- **Faber** : formulation corrigée (« variante inspirée de », pas une reproduction exacte).

Point **non traité** (proposé pour la suite) : une seconde référence qui réinvestit selon des règles écrites à l'avance.

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- `python3 -m halal_sim run` tourne de bout en bout en moins d'une seconde, avec la seule bibliothèque standard de Python 3.11.
- Import et validation de 4 CSV fictifs (13 titres ; 16 939 barres quotidiennes 2021-01-04 → 2025-12-31 ; 220 états financiers
  trimestriels ; 14 fiches d'activité, dont un changement : FXLAM annonce le rachat d'un casino le 2024-03-15), plus un `manifest.json` qui déclare `nature: FICTIF`.
- Filtre religieux à 3 statuts, enregistré dans la table `screenings` avec motifs, causes, ratios, documents utilisés (dates, sources) et identifiant du référentiel.
- Stratégie SMA 200 jours appliquée aux seuls titres ADMISSIBLES ; portefeuille de référence ; frais, glissement, actions entières.
- Journal SQLite complet : `runs` (empreintes SHA-256 du code et des données, configuration et référentiel complets),
  `screenings`, `decisions` (y compris tous les refus et leur code), `orders` (exécutés ou rejetés), `equity`, `metrics`.
- Rapport Markdown `output/rapport_demo.md` généré **depuis la base**, avec 9 contrôles recalculés.
- 51 tests `unittest`, tous au vert : `python3 -m unittest discover -s tests -v` → `Ran 51 tests … OK`.

## 2. Choix et justification

| Sujet | Choix | Pourquoi |
|---|---|---|
| Langage / stockage | Python stdlib + SQLite, aucune dépendance | Coût nul, installation nulle, auditable |
| Stratégie | Détenir si clôture > SMA(200 clôtures), revue mensuelle | Variante inspirée de la règle à 10 mois de Faber (2007) ; un seul paramètre, peu d'ordres, aucune prédiction |
| Pondération | Budget par titre = valeur du portefeuille / nombre de titres ADMISSIBLES ; pas de rééquilibrage | Le capital non investi reste en liquidités (pas d'intérêts) ; moins d'ordres |
| Chronologie | Décision à la clôture du dernier jour de bourse du mois → exécution à l'**ouverture suivante** ; documents publiés le jour J utilisés à partir de J+1 | Pas d'exécution au prix de décision, pas d'ambiguïté sur l'heure de publication |
| Référence | Achat à parts égales des ADMISSIBLES au 1er jour de décision, conservation ; ventes seulement si le filtre l'impose ; mêmes frais | Isole l'apport de la règle de tendance (limite : ne réinvestit pas, voir § 5) |
| Coûts | 1 € fixe par ordre, glissement 10 pb défavorable ; refus si coût aller-retour estimé > 1,5 % ; alerte au-delà de 0,75 % | **Valeurs fictives** ; 1,5 % est une tolérance choisie, pas un seuil de rentabilité établi |
| Politique titres détenus | EXCLU → vente ; INCERTAIN → vente (réglable par cause) | Choix conservateur en attendant la décision de l'utilisateur |
| Seuils religieux | Démo : 20 % / 20 % / 3 % **arbitraires** ; modèle réel : `null` | Consigne : ne pas coder de seuils AAOIFI de mémoire |

Sources religieuses : `docs/REFERENTIEL_ET_SOURCES.md`. La page officielle de la norme AAOIFI n° 21 est identifiée mais
**inaccessible depuis mon environnement** ; les chiffres qui circulent (30 % / 30 % / 5 %) viennent de **sources secondaires non vérifiées** et ne sont pas codés.

## 3. Résultats de la démonstration (données FICTIVES : aucune valeur probante)

Période 2021-10-29 → 2025-12-31, capital 2 000 € :

| | Stratégie | Référence |
|---|---|---|
| Rendement total | +33,11 % | +2,73 % |
| Baisse maximale | −10,44 % | −26,51 % |
| Exposition moyenne | 48,1 % | 60,3 % |
| Ordres | 35 | 9 |
| Coûts (frais + glissement) | 2,28 % du capital | 0,56 % |

Sensibilité : à **500 €**, aucun achat n'est jugé pertinent (124 refus pour coût/capital, rendement 0) ; à 10 000 €, les coûts tombent à 0,91 % du capital.
L'écart avec la V1 (+24,54 %) vient surtout de FXLAM, devenu EXCLU en 2024 à cause du changement d'activité ajouté aux données.

**Pourquoi ces chiffres ne valent rien comme preuve :** les prix fictifs contiennent une phase baissière en 2022, voulue pour faire jouer
les deux branches de la règle ; un filtre de tendance est avantagé *par construction*. La référence est en outre pénalisée par trois ventes
imposées (FXIOT pour une donnée manquante, FXLAM et FXKAP devenus EXCLU) dont le produit reste en liquidités.

## 4. Vérifications (51 tests, tous passés)

| Point critique | Défenses (en couches) | Tests |
|---|---|---|
| Un INCERTAIN (ou EXCLU) ne peut pas être acheté | (1) la stratégie n'émet jamais ACHAT hors ADMISSIBLE ; (2) `PaperBroker.buy` lève `ForbiddenOrderError` ; (3) contrainte CHECK sur `decisions` et trigger SQLite sur `orders` ; (4) un référentiel incomplet ne peut rien rendre ADMISSIBLE | `test_incertain_never_bought.py` (5), `test_ruleset_validation.py` (10) |
| Aucun ordre réel | Aucun module de courtage ; analyse statique au lancement et en test ; coupure réseau vérifiée à l'exécution ; `runs.simulation_only` contraint à 1 ; données REELLES refusées sans référentiel complet | `test_no_real_orders.py` (8, dont la ligne de commande complète réseau coupé et la preuve que le contrôle réseau peut échouer) |
| Pas de lecture de données futures | Décisions uniquement via `PointInTimeView` (lève `LookaheadError`) ; activités et états financiers filtrés par date de **publication** strictement antérieure ; date maximale lue enregistrée et contrainte en base ; exécution strictement postérieure | `test_lookahead.py` (8, dont le **test de perturbation** : prix, états financiers et fiches d'activité falsifiés après le 2023-06-30 → filtrages, décisions, ordres et valeurs identiques jusqu'à cette date) |
| Filtre, coûts, données | Causes d'incertitude, fiches datées, frais minimum, glissement défavorable, actions entières, pas de découvert ; validation stricte des CSV | `test_screening.py` (11), `test_costs_and_data.py` (9) |

## 5. Limites connues

1. **Données fictives** uniquement : aucune conclusion de rentabilité possible.
2. La référence ne réinvestit pas le produit des ventes imposées : comparaison potentiellement favorable à la stratégie.
3. Pas de conversion de devises (refus explicite si les devises diffèrent) ; dividendes, purification, fiscalité, impôt de bourse non modélisés.
4. Aucune durée de validité maximale d'une fiche d'activité ; capitalisation prise à la fin de période (pas de moyenne glissante).
5. Connaissance du calendrier boursier supposée (publié à l'avance) ; pas de jours fériés dans les données fictives.
6. Biais du survivant non traité (aucune radiation dans l'univers fictif). À traiter impérativement avec des données réelles.
7. Un seul paramètre, une seule période : il faudra une évaluation hors échantillon.
8. Ordre des achats le même jour : alphabétique quand les liquidités manquent.
9. La coupure réseau et l'analyse statique protègent contre le code Python du projet ; ce n'est pas une isolation système.
10. Le logiciel vérifie que la validation du référentiel est **renseignée**, pas qu'elle a réellement eu lieu.

## 6. Prochaines décisions

**À l'utilisateur (religieux ; je ne peux pas les trancher) :** référentiel retenu, dénominateur, seuils, classement du tabac, de l'armement,
des médias et de l'hôtellerie, politique par cause pour un titre détenu devenu INCERTAIN, méthode de purification.

**À l'utilisateur (compte ou coût) :** marché visé (France/Europe ou États-Unis) et grille tarifaire réelle du courtier envisagé (uniquement pour paramétrer les frais).

**Techniques proposées pour la V2 (gratuites) :** seconde référence avec réinvestissement ; conversion de devises datée ; données réelles gratuites
(SEC EDGAR « companyfacts » avec dates de dépôt pour les États-Unis, prix quotidiens gratuits dont les conditions d'utilisation seront vérifiées) ;
traitement du biais du survivant et des dividendes ; évaluation hors échantillon.

## 7. Questions pour le relecteur

1. Reste-t-il un chemin par lequel une décision ou un filtrage pourrait lire une information postérieure à sa date (y compris via `securities` ou la configuration) ?
2. Les exigences de `structural_problems()` et `real_data_problems()` sont-elles suffisantes, ou trop rigides (activités « cœur » imposées non ADMISSIBLES) ?
3. La règle « publié le jour J → utilisable à J+1 » est-elle assez prudente pour des publications réelles (fuseaux horaires, dépôts tardifs) ?
4. Quelles règles écrites à l'avance proposez-vous pour la seconde référence avec réinvestissement ?
5. Le rapport est-il désormais compréhensible pour un débutant ?
