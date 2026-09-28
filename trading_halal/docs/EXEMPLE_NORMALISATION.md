# Exemples vérifiables : normalisation de faits réels (règles edgar_v2)

**Statut (V1.17).** Les quatre documents ci-dessous ont été téléchargés de `www.sec.gov` le 28/09/2026 (heure exacte et
empreinte dans `documents.csv` et `journal_saisies.csv`). Leurs faits proposés ont été **normalisés et rapprochés
automatiquement** : même entité, même période exacte, même unité, contexte sans segment ni scénario dans le document,
valeur affichée égale à la valeur companyfacts. Les autres dépôts restent « proposés » (document non téléchargé).
Rapprochement automatique = concordance des chiffres avec la copie locale ; le choix des règles reste à relire.

## Refaire et vérifier

```sh
cd trading_halal
# fichiers bruts -> dossier converti, et journal des saisies (0 écart attendu)
python3 tools/edgar_collect.py verify-trace --raw collecte/apple --audit data/audit_edgar_apple
# propositions, normalisations et rapprochements conformes aux règles, rejoués sur les copies locales (0 écart)
python3 tools/edgar_normalize.py verify-normalisation --raw collecte/apple --audit data/audit_edgar_apple \
    --regles config/normalisation/edgar_v2.json
# forme et chronologie (verdict attendu : RAPPROCHEMENT AUTOMATIQUE)
python3 -m halal_sim audit-docs data/audit_edgar_apple
# régénérer un tableau ci-dessous (un test vérifie qu'ils sont identiques)
python3 tools/exemple_normalisation.py --audit data/audit_edgar_apple --accn 0000320193-25-000079
```

Pour un autre dépôt (identification SEC obligatoire, jamais enregistrée ; ou `import-filing` pour un fichier téléchargé
à la main, avec l'heure déclarée) :

```sh
python3 tools/edgar_normalize.py fetch-filing --audit data/audit_edgar_apple \
    --doc-id 0000320193-0000320193-24-000123 --user-agent "Prénom Nom adresse@domaine" --raw collecte/apple
python3 tools/edgar_normalize.py reconcile-ixbrl --audit data/audit_edgar_apple \
    --doc-id 0000320193-0000320193-24-000123 --raw collecte/apple --regles config/normalisation/edgar_v2.json
```

## Apple — rapport annuel 2025 (10-K)

Dépôt 10-K 0000320193-25-000079, accepté le 2025-10-31T10:01:26.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 USD | normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/Assets/units/USD/135` |
| total_assets | us-gaap:Assets | au 2025-09-27 | 359 241 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/Assets/units/USD/139` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2022-09-25 → 2023-09-30 | 383 285 000 000 USD | normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/88` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-09-28 | 391 035 000 000 USD | normalisé, rapproché (auto), contexte c-18, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/100` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-09-27 | 416 161 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/111` |

## Apple — troisième trimestre 2025 (10-Q) : trimestre et cumul ne se confondent pas

Dépôt 10-Q 0000320193-25-000073, accepté le 2025-08-01T10:00:42.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000073/aapl-20250628.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 USD | normalisé, rapproché (auto), contexte c-23, decimals -6 | `facts/us-gaap/Assets/units/USD/134` |
| total_assets | us-gaap:Assets | au 2025-06-28 | 331 495 000 000 USD | normalisé, rapproché (auto), contexte c-22, decimals -6 | `facts/us-gaap/Assets/units/USD/138` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-06-29 | 296 105 000 000 USD | normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/96` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-03-31 → 2024-06-29 | 85 777 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/98` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-06-28 | 313 695 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/107` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-03-30 → 2025-06-28 | 94 036 000 000 USD | normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/109` |

## Microsoft — dernier 10-K

Le comparatif de l'exercice 2025 dans ce 10-K 2026 ne remplace pas, pour une décision antérieure à sa publication, le
10-K 2025 déjà disponible (test `test_later_comparative_never_replaces_the_filing_available_at_the_decision`).

Dépôt 10-K 0001193125-26-323660, accepté le 2026-07-29T20:08:01.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| total_assets | us-gaap:Assets | au 2025-06-30 | 619 003 000 000 USD | normalisé, rapproché (auto), contexte C_528a2210-872f-4ed7-b006-dd38f90dd456, decimals -6 | `facts/us-gaap/Assets/units/USD/137` |
| total_assets | us-gaap:Assets | au 2026-06-30 | 758 376 000 000 USD | normalisé, rapproché (auto), contexte C_ca004a37-7abb-4b0e-8638-a7c6b14ebb45, decimals -6 | `facts/us-gaap/Assets/units/USD/141` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-07-01 → 2024-06-30 | 245 122 000 000 USD | normalisé, rapproché (auto), contexte C_7f83b284-3c69-4779-90ec-f0c89f19f47e, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/115` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-07-01 → 2025-06-30 | 281 724 000 000 USD | normalisé, rapproché (auto), contexte C_7575f467-7692-4974-a3da-f27e7e8e1c47, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/127` |
| total_revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-07-01 → 2026-06-30 | 331 839 000 000 USD | normalisé, rapproché (auto), contexte C_29985a27-1d12-4b7e-9a06-156523f6e71e, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/133` |

## Alphabet — dernier 10-K

Constat : dans ce 10-K 2025, Alphabet déclare son chiffre d'affaires total sous `us-gaap:Revenues` (qui inclut les
revenus hors contrats clients), pas sous `RevenueFromContractWithCustomerExcludingAssessedTax` : la règle R1 ne le voit
donc pas. Ajouter `Revenues` à total_revenue est un choix de sens pour le dénominateur du ratio de revenus illicites :
laissé à la relecture.

Dépôt 10-K 0001652044-26-000018, accepté le 2026-02-05T02:56:03.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| total_assets | us-gaap:Assets | au 2024-12-31 | 450 256 000 000 USD | normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/Assets/units/USD/81` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 595 281 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/Assets/units/USD/85` |

## Ce qui n'est pas proposé

- Nombres d'actions : les catégories d'actions ordinaires (cotées ou non) doivent être établies sur le document, à la
  date du fait (Alphabet : classes A, B non cotée, C ; GOOGM/GOOGN sont des depositary shares de préférentielles
  convertibles introduites en 2026). La règle C1 (liste des tickers) est retirée : information future.
- Agrégats et postes à qualifier (dette à intérêt, placements à intérêt, revenus illicites) et capitalisation : voir
  `config/normalisation/edgar_v2.json` (`non_normalises_volontairement`).
