# Exemples vérifiables : normalisation de faits réels (règles edgar_v3)

**Statut (V1.18).** Cinq documents ont été téléchargés de `www.sec.gov` le 28/09/2026 (heure exacte et empreinte dans
`documents.csv` et `journal_saisies.csv`). Leurs faits proposés ont été **normalisés et rapprochés automatiquement** :
même entité (identifiant au schéma CIK de la SEC), même période exacte, même unité (devise ISO 4217), concept résolu par
espace de noms, contexte sans segment ni scénario, valeur affichée égale à la valeur companyfacts. Les autres dépôts
restent « proposés ». Rapprochement automatique = concordance des chiffres ; le choix des règles reste à relire.

**Revenu total (revue n° 14).** `us-gaap:Revenues` est le total prioritaire. `RevenueFromContractWithCustomer…`
(contrats clients, ASC 606) est un **composant** (`revenue_from_contracts_with_customers`) ; il n'est retenu comme
total que **par repli**, marqué « REPLI : » dans le fait, si le document ne déclare pour la même période ni
`Revenues` ni `RevenueNotFromContractWithCustomer` (cas d'Apple et de Microsoft ci-dessous).

## Refaire et vérifier

```sh
cd trading_halal
python3 tools/edgar_collect.py verify-trace --raw collecte/apple --audit data/audit_edgar_apple
python3 tools/edgar_normalize.py verify-normalisation --raw collecte/apple --audit data/audit_edgar_apple \
    --regles config/normalisation/edgar_v3.json
python3 -m halal_sim audit-docs data/audit_edgar_apple
python3 tools/exemple_normalisation.py --audit data/audit_edgar_apple --accn 0000320193-25-000079
```

Pour un autre dépôt (identification SEC obligatoire, jamais enregistrée ; ou `import-filing` pour un fichier téléchargé
à la main, avec l'heure déclarée) :

```sh
python3 tools/edgar_normalize.py fetch-filing --audit data/audit_edgar_apple \
    --doc-id 0000320193-0000320193-24-000123 --user-agent "Prénom Nom adresse@domaine" --raw collecte/apple
python3 tools/edgar_normalize.py reconcile-ixbrl --audit data/audit_edgar_apple \
    --doc-id 0000320193-0000320193-24-000123 --raw collecte/apple --regles config/normalisation/edgar_v3.json
```

## Black Hills — 10-Q du 30/06/2026 : le cas qui a motivé la V1.18

Revenus des contrats clients 440,6 M$ (trimestre) et 1 200,6 M$ (six mois) ; revenu total (`Revenues`) 452,8 M$ et
1 233,5 M$. En V1.17, 440,6 M$ aurait été retenu comme revenu total ; désormais le total vient de `Revenues` et le
composant reste distinct (test `test_review_case_black_hills_component_is_never_the_total`).

Dépôt 10-Q 0001193125-26-337444, accepté le 2026-08-06T17:21:32.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/1130464/000119312526337444/bkh-20260630.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-01-01 → 2025-06-30 | 1 236 100 000 USD | normalisé, rapproché (auto), contexte C_1b57cd3b-dc2e-4455-b09b-fc63998e50dd, decimals -5 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/93` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-04-01 → 2025-06-30 | 435 700 000 USD | normalisé, rapproché (auto), contexte C_4da4795c-6e11-4a95-aa2f-81ff384e8fc7, decimals -5 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/95` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2026-01-01 → 2026-06-30 | 1 200 600 000 USD | normalisé, rapproché (auto), contexte C_d003b75b-e028-4192-b97d-b43705b994a2, decimals -5 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/100` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2026-04-01 → 2026-06-30 | 440 600 000 USD | normalisé, rapproché (auto), contexte C_60aa3aac-d2f4-454b-b5a9-3d06732acba7, decimals -5 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/101` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 10 869 800 000 USD | normalisé, rapproché (auto), contexte C_68930964-0821-425e-b0e0-e776b684f0ef, decimals -5 | `facts/us-gaap/Assets/units/USD/159` |
| total_assets | us-gaap:Assets | au 2026-06-30 | 11 038 100 000 USD | normalisé, rapproché (auto), contexte C_9e9e861a-5895-4fe4-b076-cf884a691eb2, decimals -5 | `facts/us-gaap/Assets/units/USD/161` |
| total_revenue | us-gaap:Revenues | 2025-01-01 → 2025-06-30 | 1 244 200 000 USD | normalisé, rapproché (auto), contexte C_1b57cd3b-dc2e-4455-b09b-fc63998e50dd, decimals -5 | `facts/us-gaap/Revenues/units/USD/122` |
| total_revenue | us-gaap:Revenues | 2025-04-01 → 2025-06-30 | 439 000 000 USD | normalisé, rapproché (auto), contexte C_4da4795c-6e11-4a95-aa2f-81ff384e8fc7, decimals -5 | `facts/us-gaap/Revenues/units/USD/124` |
| total_revenue | us-gaap:Revenues | 2026-01-01 → 2026-06-30 | 1 233 500 000 USD | normalisé, rapproché (auto), contexte C_d003b75b-e028-4192-b97d-b43705b994a2, decimals -5 | `facts/us-gaap/Revenues/units/USD/129` |
| total_revenue | us-gaap:Revenues | 2026-04-01 → 2026-06-30 | 452 800 000 USD | normalisé, rapproché (auto), contexte C_60aa3aac-d2f4-454b-b5a9-3d06732acba7, decimals -5 | `facts/us-gaap/Revenues/units/USD/130` |

## Apple — rapport annuel 2025 (10-K)

Dépôt 10-K 0000320193-25-000079, accepté le 2025-10-31T10:01:26.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2022-09-25 → 2023-09-30 | 383 285 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/88` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-09-28 | 391 035 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-18, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/100` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-09-27 | 416 161 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/111` |
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 USD | normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/Assets/units/USD/135` |
| total_assets | us-gaap:Assets | au 2025-09-27 | 359 241 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/Assets/units/USD/139` |

## Apple — troisième trimestre 2025 (10-Q) : trimestre et cumul ne se confondent pas

Dépôt 10-Q 0000320193-25-000073, accepté le 2025-08-01T10:00:42.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000073/aapl-20250628.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-06-29 | 296 105 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/96` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-03-31 → 2024-06-29 | 85 777 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/98` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-06-28 | 313 695 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/107` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-03-30 → 2025-06-28 | 94 036 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/109` |
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 USD | normalisé, rapproché (auto), contexte c-23, decimals -6 | `facts/us-gaap/Assets/units/USD/134` |
| total_assets | us-gaap:Assets | au 2025-06-28 | 331 495 000 000 USD | normalisé, rapproché (auto), contexte c-22, decimals -6 | `facts/us-gaap/Assets/units/USD/138` |

## Microsoft — dernier 10-K

Le comparatif de l'exercice 2025 dans ce 10-K 2026 ne remplace pas, pour une décision antérieure à sa publication, le
10-K 2025 déjà disponible (test `test_later_comparative_never_replaces_the_filing_available_at_the_decision`).

Dépôt 10-K 0001193125-26-323660, accepté le 2026-07-29T20:08:01.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-07-01 → 2024-06-30 | 245 122 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte C_7f83b284-3c69-4779-90ec-f0c89f19f47e, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/115` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-07-01 → 2025-06-30 | 281 724 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte C_7575f467-7692-4974-a3da-f27e7e8e1c47, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/127` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-07-01 → 2026-06-30 | 331 839 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte C_29985a27-1d12-4b7e-9a06-156523f6e71e, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/133` |
| total_assets | us-gaap:Assets | au 2025-06-30 | 619 003 000 000 USD | normalisé, rapproché (auto), contexte C_528a2210-872f-4ed7-b006-dd38f90dd456, decimals -6 | `facts/us-gaap/Assets/units/USD/137` |
| total_assets | us-gaap:Assets | au 2026-06-30 | 758 376 000 000 USD | normalisé, rapproché (auto), contexte C_ca004a37-7abb-4b0e-8638-a7c6b14ebb45, decimals -6 | `facts/us-gaap/Assets/units/USD/141` |

## Alphabet — dernier 10-K

Total 2025 = 402 836 M$ sous `us-gaap:Revenues` (revenus hors contrats clients compris).

Dépôt 10-K 0001652044-26-000018, accepté le 2026-02-05T02:56:03.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| total_assets | us-gaap:Assets | au 2024-12-31 | 450 256 000 000 USD | normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/Assets/units/USD/81` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 595 281 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/Assets/units/USD/85` |
| total_revenue | us-gaap:Revenues | 2023-01-01 → 2023-12-31 | 307 394 000 000 USD | normalisé, rapproché (auto), contexte c-27, decimals -6 | `facts/us-gaap/Revenues/units/USD/60` |
| total_revenue | us-gaap:Revenues | 2024-01-01 → 2024-12-31 | 350 018 000 000 USD | normalisé, rapproché (auto), contexte c-28, decimals -6 | `facts/us-gaap/Revenues/units/USD/65` |
| total_revenue | us-gaap:Revenues | 2025-01-01 → 2025-12-31 | 402 836 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/Revenues/units/USD/73` |

## Ce qui n'est pas proposé

- Nombres d'actions : catégories d'actions ordinaires (cotées ou non) à établir sur le document, à la date du fait.
- Agrégats et postes à qualifier (dette à intérêt, placements à intérêt, revenus illicites) et capitalisation : voir
  `config/normalisation/edgar_v3.json` (`non_normalises_volontairement`).
