# HANDOFF — simulateur de trading halal, V1.7 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, contrôles d'audit
contournables, collecte réseau hors de son périmètre, affirmations non justifiées.

**Le logiciel n'implémente encore aucun référentiel religieux réel complet.** L'utilisateur indique que ses règles de fiqh
se trouvent dans une conversation séparée, **non accessible ici** : aucune règle n'en a été reprise (voir
`docs/REFERENTIEL_ET_SOURCES.md` § 9). Merci de ne pas en supposer le contenu.

## 0. Suite donnée à la revue n° 7

Les trois dossiers incohérents signalés (`ok=True` sur 340871e) ont été reproduits, puis corrigés ; chaque défaut
réintroduit fait échouer au moins un test (6 variantes).

| Cas signalé | Correction | Test |
|---|---|---|
| `shares_outstanding` en `monnaie`/`USD` | Nature de chaque concept normalisé : monétaire ⇒ unité `monnaie` + devise ; nombre d'actions ⇒ unité `actions`, sans devise ; toute unité `actions` avec devise refusée | `test_share_count_cannot_be_monetary` |
| `unit=monnaie` sans devise | Refusé pour tout fait | `test_monetary_fact_needs_currency` |
| Rectificatif public avant le document rectifié | Diffusion connue (ou, à défaut, acceptation) du rectificatif strictement postérieure à celle du document rectifié | `test_amendment_cannot_be_public_before_original` |
| Mappage XBRL par seul concept (question 2) | Nouveaux champs du fait d'origine : `source_dimensions`, `source_unit`, `raw_value`, `decimals` ; normalisation : `transformation` (« aucune » ⇒ valeur = valeur brute) et `normalization_justification` **propre au fait** (le mappage général ne suffit plus) ; fait dimensionnel signalé | `test_normalization_needs_fact_level_justification_and_transformation`, `test_raw_fact_fields` |
| Archivage automatique ; collision dans la même seconde ; WAL (question 3) | **Refus par défaut** (code 2, base intacte). Archivage seulement avec `--archiver-ancienne-base` : copie par l'API de sauvegarde SQLite (WAL inclus), nom réservé de façon exclusive (`open(..., "xb")` + compteur), `PRAGMA integrity_check` sur la copie, puis suppression de l'original et de ses `-wal`/`-shm` | `test_review7_old_database_refused_by_default`, `test_review7_two_archives_in_the_same_second_never_overwrite`, `test_archive_includes_wal_content`, `test_cli_archives_old_database_only_on_request` |
| « 0 erreur » pris pour un audit (question 4) | Verdict distinct : `REJETE` / `NON EXPLOITABLE` (faits normalisés non rapprochés, état normal après collecte) / `RAPPROCHE` (chaque fait normalisé marqué `reconciled=oui` par un humain) | `test_zero_errors_is_not_a_usable_verdict_without_reconciliation` |

## 1. Nouvel outil : collecte EDGAR (`tools/edgar_collect.py`)

- **Hors du paquet `halal_sim`**, qui reste sans code réseau (vérifié par `scan_package`, y compris dans les tests de l'outil).
- `collect` : télécharge les JSON bruts `submissions` et `companyfacts` ; journal avec URL, horodatage UTC et SHA-256 ;
  `--user-agent` **obligatoire à chaque lancement, sans valeur par défaut**, refusé s'il ressemble à un exemple, et
  **non enregistré** dans le journal ; au plus 2 requêtes par seconde ; `--dry-run` n'effectue aucune requête.
- `convert` : JSON bruts → dossier d'audit `REEL`. Vérifie l'empreinte des fichiers bruts ; analyse **stricte** (champ
  attendu absent ⇒ arrêt) ; aucune normalisation, aucun rattachement automatique de rectificatif (les `/A` sont listés
  pour traitement manuel) ; diffusion publique laissée inconnue ; précision (`decimals`) et contexte XBRL non fournis par
  l'API, donc signalés. Résultat attendu : 0 erreur, verdict **NON EXPLOITABLE**.
- **Non testé contre la vraie SEC** : sec.gov est bloqué depuis l'environnement de développement. Les formats d'API sont
  des **hypothèses listées en tête du script** ; les 6 tests tournent hors ligne sur un jeu fictif
  (`tests/fixtures/edgar_FICTIF/`). L'utilisateur lancera la collecte sur sa machine, avec son identification, le moment venu.

## 2. Ce qui fonctionne réellement (vérifié en lançant le code)

- Simulation de bout en bout, rapport depuis SQLite (12 contrôles), base versionnée ; `audit-docs` sur l'exemple fictif :
  0 erreur, verdict NON EXPLOITABLE (0/4 fait rapproché).
- **125 tests**, tous au vert : test_audit 23, test_costs_and_data 9, test_edgar_tool 6, test_incertain_never_bought 5,
  test_lookahead 8, test_no_real_orders 8, test_review2 10, test_review3 12, test_review4 8, test_review5 9, test_review6 6,
  test_ruleset_validation 10, test_screening 11.

## 3. Résultats de la démonstration (FICTIFS, modèle d'exécution rétrospectif, sans valeur probante)

Inchangés : stratégie +25,86 % ; référence achat-conservation −8,07 % ; référence réinvestie +4,43 %.

## 4. Limites connues

1. Données de simulation fictives ; aucun référentiel réel complet ; simulation sur données REEL refusée.
2. Exécutions reconstruites, non prouvées.
3. Collecte EDGAR non éprouvée sur l'API réelle ; formats supposés.
4. L'audit détecte des contradictions de forme et de chronologie ; l'exactitude dépend du rapprochement humain.
5. Pas de passerelle testée audit → jeu de simulation ; fiche titre de simulation non historisée.

## 5. Prochaines décisions (utilisateur)

- **Fiqh** : fournir les passages de la conversation où figurent les règles (texte, références, autorité), pour qu'ils
  soient consignés avec leur source puis codés et testés.
- **Collecte EDGAR** : choisir 2 ou 3 sociétés et lancer l'outil sur sa machine avec sa propre identification SEC
  (l'utilisateur préfère ne pas fournir son adresse avant une version définitive).

## 6. Questions pour le relecteur

1. Un dossier incohérent peut-il encore obtenir 0 erreur avec ces règles ?
2. Les hypothèses de format EDGAR listées dans `tools/edgar_collect.py` te paraissent-elles exactes (champs de
   `filings.recent`, structure `facts.<taxonomie>.<concept>.units`, absence de dimensions dans companyfacts) ?
3. La conversion laisse-t-elle passer une information qui devrait rester inconnue, ou en invente-t-elle une ?
4. L'archivage explicite (copie par l'API de sauvegarde, nom exclusif, vérification d'intégrité, puis suppression) est-il sûr ?
