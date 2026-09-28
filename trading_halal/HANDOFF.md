# HANDOFF — simulateur de trading halal, V1.8 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, contrôles d'audit
contournables, informations inventées par la conversion, opérations destructives, affirmations non justifiées.

**Le logiciel n'implémente encore aucun référentiel religieux réel complet.** Les règles de fiqh de l'utilisateur sont
dans une conversation séparée **non accessible ici** ; aucune n'a été reprise (`docs/REFERENTIEL_ET_SOURCES.md` § 9).

## 0. Suite donnée à la revue n° 8

Tous les cas ont été reproduits sur 4fdca20 (le dernier plus gravement que décrit : après l'archivage, la connexion
restée ouverte ne pouvait plus écrire, la base ayant été supprimée sous elle). Chaque défaut réintroduit fait échouer
au moins un test (7 variantes).

| Cas signalé | Correction | Test |
|---|---|---|
| JSON companyfacts d'un autre CIK rattaché à l'émetteur 123 | Le champ `cik` de chaque JSON (submissions et companyfacts) doit correspondre au CIK du journal, sinon arrêt | `test_review8_cik_mismatch_is_refused_even_with_consistent_journal` |
| `reconciled=oui` sans note ⇒ verdict « RAPPROCHE » | Un « oui » exige `reconciled_note` (pièce et endroit vérifiés) ; verdict renommé **RAPPROCHEMENT DECLARE** : déclaration humaine enregistrée, non vérifiée par le logiciel, à relire | `test_review_case_reconciliation_without_note_is_refused` |
| `filings.files` ignoré (historique incomplet sans avertissement) | Signalé : `incomplete_history` dans le résultat et **HISTORIQUE INCOMPLET** dans l'avertissement du manifeste (non collecté) | `test_review8_older_filings_reported_as_incomplete_history` |
| Contexte décrit par une phrase ; dimensions vides = « aucune » ; catégorie « non établie » | `source_context` vide (non fourni) ; `source_dimensions=INCONNU` ; `share_class=INCONNU`. Dans l'audit, `INCONNU` est signalé et **bloque toute normalisation** tant que l'information n'est pas établie | `test_review8_unknowns_stay_unknown`, `test_unknown_dimensions_or_share_class_block_normalization` |
| « valeur inconnue » alors que la valeur brute est connue | Message distinct : « valeur brute connue (x), valeur normalisée absente » | `test_raw_value_known_is_reported_distinctly` |
| Doublon contradictoire gardé silencieusement | Même dépôt, concept, unité et période avec valeurs différentes ⇒ **arrêt** citant les deux entrées brutes ; doublon identique regroupé et compté | `test_review8_contradictory_duplicate_stops_conversion` |
| Archivage qui supprime l'original pendant qu'une connexion écrit | **Plus aucune suppression ni déplacement.** Base d'ancien schéma refusée (code 2) ; nouvelle base via `--db CHEMIN` ; commande `snapshot-db` : instantané vérifié (API de sauvegarde, source ouverte en lecture seule, nom exclusif, `integrity_check`), présenté comme ne contenant pas les écritures postérieures | `test_review8_writer_keeps_working_after_snapshot`, `test_snapshot_includes_wal_content_and_never_touches_original`, `test_review7_two_snapshots_in_the_same_second_never_overwrite`, `test_cli_runs_on_another_path_and_leaves_old_database_untouched`, `test_review7_old_database_refused_by_default` |

Hypothèses EDGAR : merci pour les confirmations (URL, CIK sur 10 chiffres, présentation en colonnes, faits par unité,
10 requêtes/s). L'en-tête du script reprend désormais que companyfacts n'est qu'un sous-ensemble des faits du dépôt et
que l'absence de contexte ne prouve pas l'absence de dimensions. Les noms exacts des champs restent **non éprouvés** sur
une vraie réponse SEC (sec.gov inaccessible depuis l'environnement de développement).

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- Simulation de bout en bout, rapport depuis SQLite (12 contrôles), base versionnée, refus non destructif d'un ancien schéma.
- `audit-docs` sur l'exemple fictif : 0 erreur, verdict NON EXPLOITABLE (0/4 fait rapproché).
- Collecte EDGAR testée hors ligne uniquement (jeu fictif).
- **133 tests**, tous au vert : test_audit 26, test_costs_and_data 9, test_edgar_tool 10, test_incertain_never_bought 5,
  test_lookahead 8, test_no_real_orders 8, test_review2 10, test_review3 12, test_review4 8, test_review5 9, test_review6 7,
  test_ruleset_validation 10, test_screening 11.

## 2. Résultats de la démonstration (FICTIFS, modèle d'exécution rétrospectif, sans valeur probante)

Inchangés : stratégie +25,86 % ; référence achat-conservation −8,07 % ; référence réinvestie +4,43 %.

## 3. Limites connues

1. Données de simulation fictives ; aucun référentiel réel complet ; simulation sur données REEL refusée.
2. Exécutions reconstruites, non prouvées.
3. Collecte EDGAR non éprouvée sur l'API réelle ; companyfacts partiel ; dépôts anciens non collectés.
4. Le rapprochement est une déclaration humaine ; le logiciel ne vérifie que forme, chronologie et cohérence.
5. Pas de passerelle audit → simulation ; fiche titre de simulation non historisée.

## 4. Prochaines décisions (utilisateur)

- **Fiqh** : coller les passages de la conversation où figurent les règles (texte, références, autorité).
- **Collecte EDGAR** : quand l'utilisateur le souhaitera, sur sa machine, avec sa propre identification SEC.

## 5. Questions pour le relecteur

1. Reste-t-il une information inventée ou perdue par la conversion EDGAR, ou un dossier incohérent à 0 erreur ?
2. Le traitement `INCONNU` / vide est-il cohérent partout (dimensions, catégorie, contexte, diffusion publique) ?
3. La gestion non destructive des bases (refus, `--db`, `snapshot-db`) te paraît-elle sûre ?
4. Faut-il collecter aussi les fichiers `filings.files` dès la première version, ou le signalement suffit-il pour un premier dossier ?
