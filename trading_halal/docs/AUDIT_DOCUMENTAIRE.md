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
| `documents.csv` | `doc_id`, `issuer_id`, `doc_type`, `accession_number`, `url`, `local_copy`, `local_sha256`, `period_end`, `accepted_at`, `public_available_at`, `retrieved_at`, `version`, `amends_doc_id` | Horodatages ISO **avec fuseau** ; `public_available_at` peut rester **vide = inconnue** (jamais recopiée de l'acceptation) ; fin de période ≤ acceptation ≤ diffusion ≤ récupération ; copie locale **dans le dossier**, empreinte SHA-256 vérifiée ; rectificatif : cible distincte, même émetteur, acceptée avant, même fin de période, sans boucle |
| `facts.csv` | `fact_id`, `doc_id`, `source_concept`, `source_context`, `normalized_concept`, `definition`, `value`, `unit`, `currency`, `period_type`, `period_start`, `period_end`, `measure_date`, `share_class`, `price_adjusted`, `corrects_fact_id` | Concept et contexte **d'origine** (ex. XBRL) conservés ; `normalized_concept` seulement via `concept_map.csv` ; valeur finie ou vide ; période et **date de mesure** antérieures à l'acceptation ; unité « actions » ou concept d'actions : date de mesure et catégorie obligatoires, quel que soit le nom du concept ; une correction provient d'un rectificatif du document d'origine et garde concept, période, unité, devise et catégorie ; un rectificatif peut être partiel |
| `concept_map.csv` | `source_concept`, `normalized_concept`, `justification` | Mappage explicite et justifié vers les concepts du projet ; pas de doublon |
| `activities.csv` | `issuer_id`, `proposed_code` (ou INCONNU), `evidence_doc_id`, `available_at`, `source`, `source_url`, `justification` | Code proposé : justification **et** pièce justificative obligatoires ; pièce du même émetteur ; disponibilité jamais antérieure à celle de la pièce |

## Ce que le contrôle ne fait pas

- Il ne vérifie pas que les valeurs correspondent au document : la comparaison avec la source reste humaine.
- Il ne télécharge rien (aucun accès réseau dans le paquet). Pour EDGAR, la collecte peut être manuelle ; un
  téléchargement automatisé devra respecter les consignes d'identification et d'accès de la SEC, et reste une
  **décision de l'utilisateur** (en-tête avec nom et adresse électronique).
- Il ne convertit pas un dossier d'audit en jeu de simulation : ce passage sera une étape distincte et testée.
