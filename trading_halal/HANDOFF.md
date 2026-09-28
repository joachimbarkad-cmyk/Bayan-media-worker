# HANDOFF — simulateur de trading halal, V1.6 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, achats non ADMISSIBLES,
contrôles d'audit contournables, affirmations non justifiées, erreurs de calcul.

**Le logiciel n'implémente encore aucun référentiel religieux réel complet** ; les seuils de démonstration sont arbitraires
et les données de simulation sont inventées.

## 0. Suite donnée à la revue n° 6

Chaque cas a été reproduit sur le commit c271241 (8 cas d'audit donnaient `ok=True`), corrigé et couvert par un test.
J'ai réintroduit chaque défaut (8 variantes) : à chaque fois, au moins un test échoue.

| Cas signalé | Correction | Test |
|---|---|---|
| Fait mesuré après l'acceptation de son document | `measure_date` doit être ≤ date d'acceptation du document | `test_measure_date_after_document_acceptance_is_refused` |
| Activité antidatée par rapport à sa source | Nouvelle colonne `evidence_doc_id` : un code proposé exige justification **et** pièce justificative du même émetteur ; `available_at` ≥ diffusion publique (ou, si inconnue, acceptation) de la pièce | `test_activity_cannot_predate_its_evidence` |
| Rectificatif de lui-même ou d'une autre période | Cible distincte, même émetteur, acceptée avant, même fin de période, pas de boucle ; un rectificatif (et lui seul) désigne sa cible | `test_amendment_rules` |
| Correction de fait non rapprochée | `corrects_fact_id` : le fait corrigé appartient à un document rectifié par ce document ; concept d'origine, période, unité, devise et catégorie d'actions identiques ; rectificatif partiel admis ; ancienne et nouvelle valeurs conservées avec leurs dates | `test_fact_correction_must_match_corrected_fact` |
| Colonne `screening_status=ADMISSIBLE` acceptée | **Liste fermée** : toute colonne non prévue est refusée, quel que soit son nom (idem pour les clés du manifeste) | `test_any_unexpected_column_is_refused` |
| `security_id` en double avec deux devises | Identifiant de titre unique | `test_duplicate_security_id_is_refused` |
| Copie locale `../external_source.txt` | Chemin absolu ou sortant du dossier refusé (résolution du chemin) | `test_local_copy_must_stay_inside_folder` |
| `EntityCommonStockSharesOutstanding` sans date de mesure | Concept **d'origine** (`source_concept`, `source_context`) distinct du concept **normalisé** (`normalized_concept`), relié seulement par `concept_map.csv` justifié ; les règles « actions » s'appliquent selon l'**unité** (actions) ou le concept normalisé, pas selon un nom littéral | `test_share_rules_follow_unit_not_concept_name`, `test_normalized_concept_requires_explicit_mapping` |
| Heure de diffusion publique recopiée de l'acceptation | `public_available_at` peut rester vide : **inconnue** signalée, jamais inventée | `test_unknown_public_availability_is_reported_not_copied` |
| Base SQLite V1.4 → `OperationalError` en V1.5 | Version de schéma dans `PRAGMA user_version` (v6) ; base d'une autre version jamais modifiée en place (`StoreSchemaError`) ; la ligne de commande l'**archive** (renommée `*.schema-vN-date.bak`, pas supprimée) et crée une base neuve | `tests/test_review6.py` (3 tests, dont une base au schéma V1.4 réel) |

**Modèle d'exécution : j'adopte ta formulation.** Tu as raison : le volume de la séance ne dit pas ce qui était disponible
à l'ouverture, et le résultat dépend rétroactivement de ce volume. Faute de données horodatées de l'ouverture, les résultats
sont désormais intitulés, dans le rapport et la ligne de commande, « **simulation avec modèle d'exécution rétrospectif** » :
ordres dimensionnés avec l'information antérieure, exécutions reconstruites à partir de la barre journalière et **non prouvées**.
Le mode causal (exécution confirmée par une donnée horodatée, sinon « indéterminée ») n'est pas implémenté : il exige des
données que nous n'avons pas.

**Non traité (documenté) :** historique daté des fiches titres dans le jeu de simulation (type d'instrument, devise, identité) ;
heures de publication dans le jeu de simulation (le dossier d'audit les a) ; passerelle audit → simulation.

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- Simulation de bout en bout (bibliothèque standard, aucun réseau), rapport depuis SQLite avec **12 contrôles**, base versionnée.
- `audit-docs` sur l'exemple fictif : 0 erreur, 5 inconnues signalées (copie absente, contexte absent, concept non normalisé,
  valeur nulle, activité non établie).
- **112 tests**, tous au vert : test_audit 17, test_costs_and_data 9, test_incertain_never_bought 5, test_lookahead 8,
  test_no_real_orders 8, test_review2 10, test_review3 12, test_review4 8, test_review5 9, test_review6 3,
  test_ruleset_validation 10, test_screening 11.

## 2. Résultats de la démonstration (FICTIFS, modèle d'exécution rétrospectif, sans valeur probante)

Inchangés : stratégie +25,86 % ; référence achat-conservation −8,07 % (−3,86 % au dernier cours) ; référence réinvestie
+4,43 % (+8,64 % au dernier cours) ; capital 2 000 €, 2021-10-29 → 2025-12-31.

## 3. Limites connues

1. Données de simulation fictives ; aucun référentiel réel complet ; simulation sur données REEL refusée.
2. Exécutions reconstruites, non prouvées (5 % du volume, prix d'ouverture : hypothèses).
3. Pas de conversion de devises, de dividendes, de purification, de fiscalité ; échange de titres non modélisé (gel).
4. Fiche titre de simulation non historisée ; référentiel appliqué rétroactivement.
5. L'audit vérifie forme, chronologie, cohérence des rectificatifs et intégrité des copies, pas l'exactitude des valeurs.

## 4. Prochaines décisions

**Religieuses (utilisateur) :** référentiel, dénominateur, seuils, contrôles supplémentaires, activités litigieuses,
politique pour un titre devenu INCERTAIN, purification.

**Collecte réelle (utilisateur) :** premier dossier d'audit sur 2 ou 3 émetteurs américains (EDGAR), manuellement ou par un
script qui exigera un en-tête d'identification SEC (nom et adresse électronique à fournir par l'utilisateur).

## 5. Questions pour le relecteur

1. Les nouvelles règles d'audit laissent-elles encore un dossier incohérent obtenir 0 erreur ?
2. La séparation concept d'origine / concept normalisé / mappage suffit-elle pour des faits XBRL réels (dimensions, échelles, signes) ?
3. L'archivage automatique d'une base d'ancien schéma est-il la bonne conduite, ou faut-il refuser et laisser l'utilisateur agir ?
4. Quel contrôle manque avant de considérer « 0 erreur » comme un résultat d'audit utilisable pour un premier dossier réel ?
