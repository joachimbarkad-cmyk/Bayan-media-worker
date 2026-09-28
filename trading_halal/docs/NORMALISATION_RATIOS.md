# Normalisation des faits pour les trois ratios : ordre de travail (Apple, exercice clos le 27/09/2025)

> V1.20 : règles `edgar_v5`. total_revenue vient de `us-gaap:Revenues` en priorité ; `RevenueFromContractWithCustomer…`
> est un composant, retenu comme total seulement par repli explicite (« REPLI : ») avec preuve positive tirée des calculs du dépôt, et si aucun autre revenu n'est déclaré. Faits normalisés et rapprochés pour
> les documents téléchargés : voir `docs/EXEMPLE_NORMALISATION.md`. shares_outstanding n'est pas proposé.

Rien ici n'est encore normalisé ni rapproché : ces chiffres sont des **faits d'origine** du dossier
`data/audit_edgar_apple/`, retrouvés avec `halal_sim.selection.select_fact` (période exacte, dépôt disponible au
1er novembre 2025). Ils doivent être comparés à la main au 10-K (0000320193-25-000079) avant toute utilisation. Aucun des
trois ratios n'est calculable de façon fiable à ce stade. L'ordre et les points de contrôle suivent la revue n° 10.

| Priorité | Ratio concerné | Faits candidats (valeur d'origine, USD) | Point de contrôle |
|---|---|---|---|
| 1 | Revenus illicites / revenu total (dénominateur) | `RevenueFromContractWithCustomerExcludingAssessedTax`, 29/09/2024 → 27/09/2025 : 416 161 000 000 | Exercice complet uniquement ; ne jamais prendre un trimestre (ex. T3 : 94 036 M) ni un cumul de neuf mois (313 695 M), qui ont la même date de fin. |
| 2 | Dette à intérêt / capitalisation (numérateur) | `LongTermDebt` au 27/09/2025 : 90 678 000 000 ; `CommercialPaper` : 7 979 000 000 | `LongTermDebt` contient déjà sa part courante (12 350 M) et non courante (78 328 M) : ne pas les rajouter. Autres emprunts et locations : à trancher selon le référentiel validé. |
| 3 | Capitalisation (dénominateur des deux premiers ratios) | `CommonStockSharesOutstanding` au 27/09/2025 : 14 773 260 000 actions ; `dei:EntityCommonStockSharesOutstanding` au 17/10/2025 : 14 776 353 000 | Deux dates différentes : la convention de date vient du référentiel (question ouverte). Les actions moyennes du bénéfice par action ne conviennent pas. EDGAR ne fournit pas le **cours** : source de prix non ajustés à trouver (coût à annoncer avant tout achat). |
| 4 | Dépôts à intérêt / capitalisation (numérateur) | Aucun tag direct. `CashAndCashEquivalentsAtCarryingValue` : 35 934 000 000 (**n'est pas** un montant de dépôts à intérêt) | Reconstituer depuis la note sur les instruments financiers (trésorerie, certificats et dépôts à terme, titres) ; la qualification de chaque ligne relève du référentiel et d'une revue humaine. |
| 5 | Revenus illicites (numérateur) | Aucun tag direct. `NonoperatingIncomeExpense` : −321 000 000 (solde net, **inutilisable** tel quel) | Détailler les intérêts perçus et les autres revenus concernés à partir des notes. Ni le solde net ni un zéro par défaut ne sont acceptables. |

## Règles de sélection (codées dans `halal_sim/selection.py`)

- Période exacte (début et fin). Un fait ponctuel n'a pas de date de début.
- Un dépôt est utilisable à partir du lendemain (UTC) de son acceptation, ou de sa diffusion publique si elle est
  connue et plus tardive. L'acceptation ne prouve pas la diffusion ; la SEC ne fournit pas d'horodatage de diffusion.
- Un chiffre repris en comparatif, ou corrigé par un rectificatif, provient du dépôt le plus récemment disponible à la
  date de décision. Les valeurs antérieures différentes sont signalées comme révisées.
- Deux dépôts du même jour avec des valeurs différentes : aucune valeur retenue.
- Un fait n'est « utilisable » que normalisé et rapproché (`reconciled = oui`).
- La clé comprend l'émetteur ; un fait monétaire normalisé exige sa devise.
- La valeur publiée à l'origine est conservée (`Selection.original`) pour mesurer l'effet des retraitements.

## Limites de companyfacts

companyfacts ne contient qu'une partie des faits (concepts standard, entité entière). L'absence d'un poste ne prouve
pas qu'il manque au rapport. Contexte XBRL, dimensions et précision (`decimals`) n'y figurent pas. Les rectificatifs
(10-K/A) ne sont pas convertis automatiquement : leurs faits sont listés dans `journal_conversion.json`.

## Capitalisation : règles à respecter (revue n° 11)

- Enregistrer pour chaque cours : sa date, sa disponibilité à la date de décision, sa devise, et s'il est ajusté ou non.
- Enregistrer pour chaque nombre d'actions : sa date de mesure et la date de disponibilité du dépôt qui le porte.
- Ne jamais associer un cours historique à un nombre d'actions publié plus tard (même règle J+1 que les autres faits).
- La convention de date (fin d'exercice, date de décision, moyenne) est une décision du référentiel, encore ouverte.

## Source de cours non ajustés : NON ÉTABLIE

Proposée par le relecteur : **Massive Stocks Basic** (gratuit ; barres journalières avec `adjusted=false` ; deux ans
d'historique ; cinq appels par minute). Elle exige la création d'un **compte** et d'une **clé API** : c'est à
l'utilisateur de décider ; rien n'a été créé. Deux ans d'historique ne couvrent pas un backtest depuis 2021. Aucune
autre source gratuite offrant à la fois la profondeur et une garantie explicite de cours non ajustés n'a été vérifiée.

Revue n° 12 : aucune source gratuite, sans compte, avec au moins cinq ans d'historique **et** une garantie explicite de
cours non ajustés n'a été vérifiée (Nasdaq : ajustement non précisé sur la page historique ; Alpha Vantage : clé API et
historique complet payant). La source de prix reste donc « non établie » : aucune série ne sera qualifiée de non
ajustée sans garantie écrite du fournisseur.
