# Dossier d'audit documentaire (données réelles, sans simulation)

Objectif : rassembler et contrôler des **documents réels** (rapports déposés, faits financiers, informations sur
l'activité) en conservant leur provenance, **avant** toute simulation. Un dossier d'audit ne produit aucun statut
ADMISSIBLE / EXCLU / INCERTAIN ; une colonne de statut religieux y est refusée.

Commande : `python3 -m halal_sim audit-docs <dossier>` (sans argument : l'exemple fictif `data/audit_exemple_FICTIF`).
Code de sortie 1 s'il existe une erreur bloquante. Les **inconnues** (valeur absente, activité non établie, document
sans copie locale) sont listées, jamais comblées.

## Fichiers

| Fichier | Champs | Règles contrôlées |
|---|---|---|
| `manifest.json` | `name`, `nature` (FICTIF ou REEL), `warning` | Un dossier REEL ne peut citer aucune source contenant DEMO, FICTIF ou TEST |
| `issuers.csv` | `issuer_id` (ex. CIK pour EDGAR), `name`, `id_scheme`, `source`, `source_url` | Identifiant unique, schéma et source obligatoires |
| `securities.csv` | `security_id`, `issuer_id`, `ticker`, `exchange`, `valid_from`, `valid_to`, `instrument_type`, `currency`, `source` | Ticker et place **datés** ; devise ISO à 3 lettres |
| `documents.csv` | `doc_id`, `issuer_id`, `doc_type`, `accession_number`, `url`, `local_copy`, `local_sha256`, `period_end`, `accepted_at`, `public_available_at`, `retrieved_at`, `version` (original / rectificatif), `amends_doc_id` | Horodatages ISO **avec fuseau** ; fin de période ≤ acceptation ≤ disponibilité publique ≤ récupération ; numéro d'accès unique ; empreinte SHA-256 de la copie locale vérifiée ; rectificatif relié au document rectifié |
| `facts.csv` | `fact_id`, `doc_id`, `concept`, `definition`, `value` (vide = inconnu), `unit`, `currency`, `period_type` (instant / duration), `period_start`, `period_end`, `measure_date`, `share_class`, `price_adjusted` | Document d'origine existant ; valeur finie ou vide ; période cohérente et antérieure à l'acceptation ; nombre d'actions et capitalisation : date de mesure et catégorie d'actions obligatoires ; capitalisation : cours ajusté ou non |
| `activities.csv` | `issuer_id`, `proposed_code` (ou INCONNU), `available_at`, `source`, `source_url`, `justification` | Code proposé toujours justifié ; INCONNU signalé comme inconnue |

## Ce que le contrôle ne fait pas

- Il ne vérifie pas que les valeurs correspondent au document : la comparaison avec la source reste humaine.
- Il ne télécharge rien (aucun accès réseau dans le paquet). Pour EDGAR, la collecte peut être manuelle ; un
  téléchargement automatisé devra respecter les consignes d'identification et d'accès de la SEC, et reste une
  **décision de l'utilisateur** (en-tête avec nom et adresse électronique).
- Il ne convertit pas un dossier d'audit en jeu de simulation : ce passage sera une étape distincte et testée.
