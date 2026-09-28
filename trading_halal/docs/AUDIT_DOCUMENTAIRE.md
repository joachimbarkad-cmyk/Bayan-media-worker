# Dossier d'audit documentaire (données réelles, sans simulation)

Objectif : rassembler et contrôler des **documents réels** (rapports déposés, faits financiers, informations sur
l'activité) en conservant leur provenance, **avant** toute simulation. Un dossier d'audit ne produit aucun statut
ADMISSIBLE / EXCLU / INCERTAIN ; une colonne de statut religieux y est refusée.

Commande : `python3 -m halal_sim audit-docs <dossier>` (sans argument : l'exemple fictif `data/audit_exemple_FICTIF`).
Code de sortie 1 s'il existe une erreur bloquante. Les **inconnues** (valeur absente, activité non établie, document
sans copie locale) sont listées, jamais comblées.

## Fichiers (colonnes en liste fermée : toute colonne non prévue est refusée)

| Fichier | Champs | Règles contrôlées |
|---|---|---|
| `manifest.json` | `name`, `nature` (FICTIF ou REEL), `warning` | Aucune autre clé ; un dossier REEL ne peut citer aucune source contenant DEMO, FICTIF ou TEST |
| `issuers.csv` | `issuer_id` (ex. CIK), `name`, `id_scheme`, `source`, `source_url` | Identifiant unique ; schéma et source obligatoires |
| `securities.csv` | `security_id`, `issuer_id`, `ticker`, `exchange`, `valid_from`, `valid_to`, `instrument_type`, `currency`, `source` | Identifiant unique ; ticker et place **datés** ; devise ISO à 3 lettres |
| `documents.csv` | `doc_id`, `issuer_id`, `doc_type`, `accession_number`, `url`, `local_copy`, `local_sha256`, `period_end`, `accepted_at`, `public_available_at`, `retrieved_at`, `version`, `amends_doc_id` | Horodatages ISO **avec fuseau** ; `public_available_at` peut rester **vide = inconnue** (jamais recopiée de l'acceptation) ; fin de période ≤ acceptation ≤ diffusion ≤ récupération ; copie locale **dans le dossier**, empreinte SHA-256 vérifiée ; rectificatif : cible distincte, même émetteur, acceptée **et diffusée** après elle, même fin de période, sans boucle |
| `facts.csv` | Fait **d'origine** : `source_concept`, `source_context`, `source_dimensions` (vide = aucune), `source_unit`, `raw_value`, `decimals` (entier, `INF` ou vide = inconnue). Version **normalisée** : `normalized_concept`, `transformation` (« aucune » ou description), `normalization_justification` (propre au fait), `value`, `unit`, `currency`. Période : `period_type`, `period_start`, `period_end`, `measure_date`, `share_class`, `price_adjusted`. Suivi : `corrects_fact_id`, `reconciled` (oui/non/vide), `reconciled_note` | Document d'origine existant ; valeurs brute et normalisée finies ou vides ; période et date de mesure antérieures à l'acceptation ; normalisation seulement via `concept_map.csv` **et** avec justification propre au fait ; « aucune » transformation ⇒ valeur = valeur brute ; concept monétaire ⇒ unité `monnaie` + devise ; nombre d'actions ⇒ unité `actions`, sans devise, date de mesure et catégorie ; toute unité `monnaie` exige une devise ; fait dimensionnel signalé ; correction rapprochée du fait corrigé |
| `concept_map.csv` | `source_concept`, `normalized_concept`, `justification` | Mappage explicite et justifié vers les concepts du projet ; pas de doublon |
| `activities.csv` | `issuer_id`, `proposed_code` (ou INCONNU), `evidence_doc_id`, `available_at`, `source`, `source_url`, `justification` | Code proposé : justification **et** pièce justificative obligatoires ; pièce du même émetteur ; disponibilité jamais antérieure à celle de la pièce |

## Ce que le contrôle ne fait pas

- Il ne vérifie pas que les valeurs correspondent au document : la comparaison avec la source reste humaine.
- Il ne télécharge rien (aucun accès réseau dans le paquet). Pour EDGAR, la collecte peut être manuelle ; un
  téléchargement automatisé devra respecter les consignes d'identification et d'accès de la SEC, et reste une
  **décision de l'utilisateur** (en-tête avec nom et adresse électronique).
- Il ne convertit pas un dossier d'audit en jeu de simulation : ce passage sera une étape distincte et testée.

## Verdict : « 0 erreur » n'est pas un audit

`audit-docs` affiche trois choses distinctes : les **erreurs** (contradictions détectées automatiquement), les
**inconnues** (signalées, jamais comblées) et le **verdict** :
- `REJETE` : au moins une contradiction ;
- `NON EXPLOITABLE` : aucune contradiction détectée, mais au moins un fait normalisé n'a pas été rapproché à la main
  de sa pièce (`reconciled=oui`) — c'est l'état normal d'un dossier fraîchement collecté ;
- `RAPPROCHEMENT DECLARE` : forme cohérente et chaque fait normalisé déclaré rapproché (`reconciled=oui`) **avec une
  note** indiquant la pièce et l'endroit vérifiés (page, section, tableau). Le logiciel enregistre cette déclaration,
  il ne la vérifie pas : elle doit être relue par une autre personne.

## Collecte EDGAR (outil séparé, avec réseau)

`tools/edgar_collect.py` est **hors** du paquet `halal_sim` (qui reste sans réseau). Il ne s'exécute pas depuis
l'environnement de développement (accès à sec.gov bloqué) : il est à lancer sur votre machine.

```sh
python3 tools/edgar_collect.py collect --cik 320193 --dry-run --out collecte_brute          # affiche les URL, aucune requête
python3 tools/edgar_collect.py collect --cik 320193 --user-agent "Prénom Nom adresse@domaine" --out collecte_brute
python3 tools/edgar_collect.py convert --raw collecte_brute --out data/audit_edgar_REEL
python3 -m halal_sim audit-docs data/audit_edgar_REEL
```

- `--user-agent` est **obligatoire à chaque lancement**, sans valeur par défaut ; il n'est pas enregistré dans le journal.
- La conversion ne normalise rien et ne rattache aucun rectificatif automatiquement (les `10-K/A`, `10-Q/A` sont listés
  à rattacher à la main) ; l'heure de diffusion publique reste inconnue.
- Les formats d'API supposés sont listés en tête du script ; l'analyse s'arrête net si un champ attendu manque.

## Valeur « INCONNU »

Dans `source_dimensions` et `share_class`, le **vide** signifie « aucune » (pas de dimension, pas de catégorie requise),
tandis que `INCONNU` signifie « non établi ». Un fait `INCONNU` est signalé ; il ne peut **pas** être normalisé tant
que l'information n'a pas été établie à partir du document. `source_context` vide signifie « non fourni ».

## Ce que la conversion EDGAR ne garantit pas (revue n° 8)

- **companyfacts n'est qu'un sous-ensemble** des faits XBRL d'un dépôt (faits de taxonomies standard s'appliquant à
  l'entité, selon la SEC d'après le relecteur) : l'absence d'un fait ne prouve pas qu'il n'existe pas.
- Contexte et dimensions ne sont pas fournis : ils restent `INCONNU` / vides.
- `filings.recent` ne couvre que les dépôts récents : si `filings.files` référence des dépôts plus anciens, la
  conversion l'indique (`HISTORIQUE INCOMPLET` dans le manifeste) ; ils ne sont pas collectés.
- Le CIK de chaque fichier doit correspondre à celui du journal ; un doublon contradictoire (même dépôt, concept,
  unité et période, valeurs différentes) arrête la conversion ; un doublon identique est regroupé et compté.

## Garde-fous ajoutés (revue n° 9)

- `form` et `filed` de chaque fait companyfacts doivent correspondre au dépôt désigné par son numéro d'accès, sinon arrêt.
- Un dépôt sélectionné mais écarté (fin de période absente) est nommé dans le résultat et compté dans le manifeste,
  qui décrit aussi le périmètre exact (formulaires, documents retenus, écartés, rectificatifs à rattacher).
- `collect`, `import-files` et `convert` refusent d'écrire dans un dossier existant non vide sans `--remplacer`.
- `import-files` enregistre des fichiers téléchargés à la main : aucune requête, aucune identification ; l'heure de
  téléchargement est déclarée (avec fuseau), jamais inventée. Guide : `docs/GUIDE_COLLECTE_EDGAR.md`.
- Dans l'audit, un fait normalisé sans contexte d'origine est refusé.

## Journal des saisies humaines (revue n° 12)

Toute cellule qu'un humain remplit ou modifie dans un dossier converti (diffusion publique, normalisation, contexte,
dimensions, catégorie d'actions, rapprochement, copie locale, rectificatif, lignes de `concept_map`, `activities`,
`securities`) doit être justifiée, dans l'ordre, par `journal_saisies.csv` :

`n, fichier, cle, colonne, ancienne_valeur, nouvelle_valeur, auteur, saisi_le, preuve, note`

- `n` continu à partir de 1 ; `saisi_le` avec fuseau, jamais antérieur à la saisie précédente ; `auteur` obligatoire ;
- `ancienne_valeur` doit être la valeur en vigueur (conversion, puis saisies précédentes) : historique continu ;
- `preuve` : `doc:<doc_id>`, `fichier:<chemin dans le dossier>#sha256=<empreinte>` ou `url:https://…` ; une **date de
  disponibilité** (`public_available_at`, `activities.available_at`, `securities.valid_from/valid_to`) exige un fichier
  ou une URL ;
- une colonne produite par la conversion (ex. `accepted_at`) ne peut pas être « saisie » ;
- `verify-trace` rejoue le journal sur la reconversion et signale toute cellule qui ne correspond pas.

Limites : le journal est **déclaratif**. Il rend les saisies traçables et cohérentes ; il ne prouve ni l'identité de
l'auteur, ni que la preuve dit ce qu'on lui fait dire, ni que le choix de normalisation est juste. L'historique git et
une contre-vérification humaine indépendante restent nécessaires.

## Normalisation et rapprochement automatique (V1.13)

- `reconciled` vaut `oui` (rapprochement humain, note obligatoire), `auto` (rapprochement par programme contre la
  copie locale du document : note commençant par « AUTOMATIQUE » et `local_copy` obligatoires), `non` ou vide.
- Verdict « RAPPROCHEMENT AUTOMATIQUE » : concordance des chiffres avec la copie locale seulement ; le choix du concept
  et les inférences restent à relire.
- Un fait dont le concept est mappé mais qui n'est pas normalisé doit porter une justification
  « NON NORMALISÉ : motif » (exclusion explicite) ; sinon, erreur bloquante.
- Outil : `tools/edgar_normalize.py` (`normalize`, `import-filing`, `reconcile-ixbrl`), règles
  `config/normalisation/edgar_v5.json` (v1 à v4 retirées), exemples `docs/EXEMPLE_NORMALISATION.md`.

## Conformité aux règles (V1.14)

`verify-trace` et `audit-docs` vérifient la forme et l'historique, pas le fond. `verify-normalisation` refait la
normalisation (et le rapprochement automatique) avec le fichier de règles fourni et compare chaque cellule : un écart
attribué à l'outil est une erreur ; une saisie humaine différente est listée pour relecture.

## Deux temps (revue n° 13)

`normalize` ne fait que proposer (`propositions_normalisation.csv`) ; aucun fait n'est normalisé sans le document du
dépôt. `reconcile-ixbrl` établit contexte et dimensions à partir de la copie locale XBRL en ligne, puis normalise et
rapproche. Les nombres d'actions ne sont pas normalisés automatiquement (catégories à établir par une personne).

## Total et composant (revue n° 14)

`revenue_from_contracts_with_customers` (composant ASC 606) s'ajoute aux concepts du projet. Un fait peut porter un
concept différent de son mappage **uniquement** pour le repli déclaré composant → total_revenue, avec une justification
commençant par « REPLI : » ; toute autre divergence reste une erreur bloquante. La lecture XBRL en ligne résout les
concepts et mesures par URI d'espace de noms, exige une devise ISO 4217 et un identifiant au schéma CIK de la SEC.

## Preuve positive par les calculs du dépôt (revue n° 15)

`fetch-filing` conserve, à côté du document, le schéma (`.xsd`) et le fichier de calcul (`_cal.xml`) du dépôt, avec
leur empreinte dans `copies/<doc>/annexes.json` (vérifiée à chaque lecture). Un composant ne devient total que s'il est
l'enfant +1 de `GrossProfit` ou `OperatingIncomeLoss` dans un rôle de catégorie EFM « Statement », sans autre élément
positif ; un concept total par définition (`RegulatedAndUnregulatedOperatingRevenue`) doit seulement y être en première
ligne. Nouveau concept : `revenue_from_contracts_with_customers_including_assessed_tax` (taxes incluses, jamais
interchangeable avec la version hors taxes).
