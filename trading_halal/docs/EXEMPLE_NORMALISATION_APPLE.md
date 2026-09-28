# Exemple vérifiable : normalisation des faits réels d'Apple (règles edgar_v1)

**Aucun de ces chiffres n'est encore rapproché du document d'origine** (colonne « Rapproché » = non) : ils ne sont
donc pas utilisables pour un ratio. Ils sont normalisés, c'est-à-dire rattachés à un concept du projet par une règle
écrite, avec leur provenance, et chaque étape est rejouable hors ligne.

## Refaire et vérifier

```sh
cd trading_halal
# 1. le dossier converti correspond aux fichiers bruts, et chaque saisie est journalisée
python3 tools/edgar_collect.py verify-trace --raw collecte/apple --audit data/audit_edgar_apple
# 2. forme, chronologie, règles de normalisation
python3 -m halal_sim audit-docs data/audit_edgar_apple
# 3. rejouer la normalisation : 0 saisie nouvelle attendue (idempotente)
cp -r data/audit_edgar_apple /tmp/copie && python3 tools/edgar_normalize.py normalize --raw collecte/apple \
    --audit /tmp/copie --regles config/normalisation/edgar_v1.json
# 4. régénérer les tableaux ci-dessous (un test vérifie qu'ils sont identiques)
python3 tools/exemple_normalisation.py --audit data/audit_edgar_apple --accn 0000320193-25-000079
```

Chaque « entrée brute » est un pointeur dans `collecte/apple/companyfacts_CIK0000320193.json` (SHA-256 dans
`collecte/apple/journal_collecte.json`). Chaque cellule normalisée a ses saisies dans
`data/audit_edgar_apple/journal_saisies.csv` (auteur : l'outil, règles edgar_v1).

## Rapport annuel 2025 (10-K)

Dépôt 10-K 0000320193-25-000079, accepté le 2025-10-31T10:01:26.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm

| Concept du projet | Concept d'origine | Période | Valeur | Unité | Rapproché | Entrée brute (collecte) |
|---|---|---|---|---|---|---|
| shares_outstanding | us-gaap:CommonStockSharesOutstanding | au 2024-09-28 | 15 116 786 000 | actions | non | `facts/us-gaap/CommonStockSharesOutstanding/units/shares/133` |
| shares_outstanding | us-gaap:CommonStockSharesOutstanding | au 2025-09-27 | 14 773 260 000 | actions | non | `facts/us-gaap/CommonStockSharesOutstanding/units/shares/137` |
| shares_outstanding | dei:EntityCommonStockSharesOutstanding | au 2025-10-17 | 14 776 353 000 | actions | non | `facts/dei/EntityCommonStockSharesOutstanding/units/shares/66` |
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 | USD | non | `facts/us-gaap/Assets/units/USD/135` |
| total_assets | us-gaap:Assets | au 2025-09-27 | 359 241 000 000 | USD | non | `facts/us-gaap/Assets/units/USD/139` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2022-09-25 → 2023-09-30 | 383 285 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/88` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-09-28 | 391 035 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/100` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-09-27 | 416 161 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/111` |
Contrôle à faire à la main sur le 10-K : le chiffre d'affaires 2025 (416 161 M$) a été confirmé par le relecteur
(revue n° 10) ; les autres lignes restent à comparer au bilan, au compte de résultat et à la page de couverture.

## Troisième trimestre 2025 (10-Q) : trimestre et cumul ne se confondent pas

Dépôt 10-Q 0000320193-25-000073, accepté le 2025-08-01T10:00:42.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000073/aapl-20250628.htm

| Concept du projet | Concept d'origine | Période | Valeur | Unité | Rapproché | Entrée brute (collecte) |
|---|---|---|---|---|---|---|
| shares_outstanding | us-gaap:CommonStockSharesOutstanding | au 2024-09-28 | 15 116 786 000 | actions | non | `facts/us-gaap/CommonStockSharesOutstanding/units/shares/132` |
| shares_outstanding | us-gaap:CommonStockSharesOutstanding | au 2025-06-28 | 14 856 722 000 | actions | non | `facts/us-gaap/CommonStockSharesOutstanding/units/shares/136` |
| shares_outstanding | dei:EntityCommonStockSharesOutstanding | au 2025-07-18 | 14 840 390 000 | actions | non | `facts/dei/EntityCommonStockSharesOutstanding/units/shares/65` |
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 | USD | non | `facts/us-gaap/Assets/units/USD/134` |
| total_assets | us-gaap:Assets | au 2025-06-28 | 331 495 000 000 | USD | non | `facts/us-gaap/Assets/units/USD/138` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-06-29 | 296 105 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/96` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-03-31 → 2024-06-29 | 85 777 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/98` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-06-28 | 313 695 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/107` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-03-30 → 2025-06-28 | 94 036 000 000 | USD | non | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/109` |
## Ce que la normalisation a décidé, et sur quelle base

| Élément | Valeur retenue | Base | Statut |
|---|---|---|---|
| Concept | 4 règles 1 → 1 (`config/normalisation/edgar_v1.json`) | Définitions de la taxonomie recopiées dans `concept_map.csv` | Proposition, à relire |
| Dimensions | aucune | D1 : une seule valeur brute par concept, unité, période et dépôt | **Inférence** |
| Contexte | décrit par son contenu (`companyfacts;entite=…;periode=…`) | X1 : l'identifiant XBRL n'est pas dans companyfacts | Provisoire |
| Catégorie d'actions | ordinaire, titre coté unique AAPL | C1 : `tickers` de submissions | **Inférence** |
| Transformation | aucune (valeur brute) | T1 | Vérifiée par l'audit |
| Précision (decimals) | inconnue | absente de companyfacts | Inconnue signalée |
