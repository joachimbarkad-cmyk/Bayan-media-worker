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
