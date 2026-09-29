# Exemples vérifiables : normalisation de faits réels (règles edgar_v7)

**Statut (V1.24).** Huit documents téléchargés de `www.sec.gov` (heure et empreinte dans `documents.csv` et
`journal_saisies.csv` ; schéma et calculs du dépôt dans `copies/<doc>/annexes.json`) ; schémas us-gaap **officiels**
(2024, 2025, 2026) téléchargés de `xbrl.fasb.org` le 29/09/2026 dans `collecte/taxonomies/` (URL, empreinte, heure).
Faits normalisés et rapprochés automatiquement : même entité (schéma CIK), même période exacte, même unité (ISO 4217),
concept résolu dans son schéma, contexte sans segment ni scénario, valeur affichée égale à companyfacts. Rapprochement
automatique = concordance des chiffres ; le choix des règles reste à relire.

**Revenu total (edgar_v7).** `us-gaap:Revenues` : total direct. `RegulatedAndUnregulatedOperatingRevenue` et le repli
`RevenueFromContractWithCustomer…ExcludingAssessedTax` exigent une **preuve positive** tirée des calculs du dépôt,
chaque concept étant résolu dans son schéma (officiel ou du dépôt), avec deux verdicts écrits dans le fait :
`calcul_XBRL_coherent` et `preuve_complete_pour_repli`. Les revenus nets des charges d'intérêts (banques) sont extraits
à part, jamais comme revenu total. Sonde : `docs/SONDE_REVENUS.md`.

## Refaire et vérifier

```sh
cd trading_halal
python3 tools/edgar_collect.py verify-trace --raw collecte/ford --audit data/audit_edgar_ford
python3 tools/edgar_normalize.py verify-normalisation --raw collecte/ford --audit data/audit_edgar_ford \
    --regles config/normalisation/edgar_v7.json
python3 -m halal_sim audit-docs data/audit_edgar_ford
python3 tools/exemple_normalisation.py --audit data/audit_edgar_ford --accn 0000037996-26-000015
```

## Ford — 10-K 2025 : repli prouvé (Ford Credit compris)

Preuve : « CONSOLIDATED INCOME STATEMENTS » : résultat d'exploitation = R1 − charges ; calcul vérifié pour 2025
(−9 169 M$) ; schéma us-gaap 2025 officiel.

Dépôt 10-K 0000037996-26-000015, accepté le 2026-02-11T00:08:37.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/37996/000003799626000015/f-20251231.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-01-01 → 2023-12-31 | 176 191 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-16, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/86` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-01-01 → 2024-12-31 | 184 992 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-17, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/98` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-01-01 → 2025-12-31 | 187 267 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/105` |
| total_assets | us-gaap:Assets | au 2023-12-31 | 273 310 000 000 USD | normalisé, rapproché (auto), contexte c-31, decimals -6 | `facts/us-gaap/Assets/units/USD/181` |
| total_assets | us-gaap:Assets | au 2024-12-31 | 285 196 000 000 USD | normalisé, rapproché (auto), contexte c-18, decimals -6 | `facts/us-gaap/Assets/units/USD/192` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 289 160 000 000 USD | normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/Assets/units/USD/197` |

## Duke Energy — 10-K 2025 : total direct réglementé prouvé

Dépôt 10-K 0001326160-26-000014, accepté le 2026-02-26T18:07:42.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/1326160/000132616026000014/duk-20251231.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers_including_assessed_tax | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | 2023-01-01 → 2023-12-31 | 28 674 000 000 USD | normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/units/USD/76` |
| revenue_from_contracts_with_customers_including_assessed_tax | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | 2024-01-01 → 2024-12-31 | 30 050 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/units/USD/88` |
| revenue_from_contracts_with_customers_including_assessed_tax | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | 2025-01-01 → 2025-12-31 | 31 741 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/units/USD/95` |
| total_assets | us-gaap:Assets | au 2023-12-31 | 176 893 000 000 USD | normalisé, rapproché (auto), contexte c-34, decimals -6 | `facts/us-gaap/Assets/units/USD/138` |
| total_assets | us-gaap:Assets | au 2024-12-31 | 186 343 000 000 USD | normalisé, rapproché (auto), contexte c-29, decimals -6 | `facts/us-gaap/Assets/units/USD/148` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 195 736 000 000 USD | normalisé, rapproché (auto), contexte c-28, decimals -6 | `facts/us-gaap/Assets/units/USD/153` |
| total_revenue | us-gaap:RegulatedAndUnregulatedOperatingRevenue | 2023-01-01 → 2023-12-31 | 29 060 000 000 USD | normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/RegulatedAndUnregulatedOperatingRevenue/units/USD/148` |
| total_revenue | us-gaap:RegulatedAndUnregulatedOperatingRevenue | 2024-01-01 → 2024-12-31 | 30 357 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/RegulatedAndUnregulatedOperatingRevenue/units/USD/161` |
| total_revenue | us-gaap:RegulatedAndUnregulatedOperatingRevenue | 2025-01-01 → 2025-12-31 | 32 237 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RegulatedAndUnregulatedOperatingRevenue/units/USD/168` |

## Apple — 10-K 2025 et 10-Q T3 2025 : repli prouvé par la marge brute

Dépôt 10-K 0000320193-25-000079, accepté le 2025-10-31T10:01:26.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2022-09-25 → 2023-09-30 | 383 285 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/88` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-09-28 | 391 035 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-18, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/100` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-09-27 | 416 161 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/111` |
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 USD | normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/Assets/units/USD/135` |
| total_assets | us-gaap:Assets | au 2025-09-27 | 359 241 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/Assets/units/USD/139` |

Dépôt 10-Q 0000320193-25-000073, accepté le 2025-08-01T10:00:42.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/320193/000032019325000073/aapl-20250628.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-10-01 → 2024-06-29 | 296 105 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-21, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/96` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-03-31 → 2024-06-29 | 85 777 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/98` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-09-29 → 2025-06-28 | 313 695 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/107` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-03-30 → 2025-06-28 | 94 036 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/109` |
| total_assets | us-gaap:Assets | au 2024-09-28 | 364 980 000 000 USD | normalisé, rapproché (auto), contexte c-23, decimals -6 | `facts/us-gaap/Assets/units/USD/134` |
| total_assets | us-gaap:Assets | au 2025-06-28 | 331 495 000 000 USD | normalisé, rapproché (auto), contexte c-22, decimals -6 | `facts/us-gaap/Assets/units/USD/138` |

## Microsoft — dernier 10-K : repli prouvé

Dépôt 10-K 0001193125-26-323660, accepté le 2026-07-29T20:08:01.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-07-01 → 2024-06-30 | 245 122 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte C_7f83b284-3c69-4779-90ec-f0c89f19f47e, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/115` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-07-01 → 2025-06-30 | 281 724 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte C_7575f467-7692-4974-a3da-f27e7e8e1c47, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/127` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-07-01 → 2026-06-30 | 331 839 000 000 USD | **total_revenue par repli** ; normalisé, rapproché (auto), contexte C_29985a27-1d12-4b7e-9a06-156523f6e71e, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/133` |
| total_assets | us-gaap:Assets | au 2025-06-30 | 619 003 000 000 USD | normalisé, rapproché (auto), contexte C_528a2210-872f-4ed7-b006-dd38f90dd456, decimals -6 | `facts/us-gaap/Assets/units/USD/137` |
| total_assets | us-gaap:Assets | au 2026-06-30 | 758 376 000 000 USD | normalisé, rapproché (auto), contexte C_ca004a37-7abb-4b0e-8638-a7c6b14ebb45, decimals -6 | `facts/us-gaap/Assets/units/USD/141` |

## Alphabet — dernier 10-K : total direct `Revenues`

Dépôt 10-K 0001652044-26-000018, accepté le 2026-02-05T02:56:03.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| total_assets | us-gaap:Assets | au 2024-12-31 | 450 256 000 000 USD | normalisé, rapproché (auto), contexte c-19, decimals -6 | `facts/us-gaap/Assets/units/USD/81` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 595 281 000 000 USD | normalisé, rapproché (auto), contexte c-20, decimals -6 | `facts/us-gaap/Assets/units/USD/85` |
| total_revenue | us-gaap:Revenues | 2023-01-01 → 2023-12-31 | 307 394 000 000 USD | normalisé, rapproché (auto), contexte c-27, decimals -6 | `facts/us-gaap/Revenues/units/USD/60` |
| total_revenue | us-gaap:Revenues | 2024-01-01 → 2024-12-31 | 350 018 000 000 USD | normalisé, rapproché (auto), contexte c-28, decimals -6 | `facts/us-gaap/Revenues/units/USD/65` |
| total_revenue | us-gaap:Revenues | 2025-01-01 → 2025-12-31 | 402 836 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/Revenues/units/USD/73` |

## Black Hills — 10-Q du 30/06/2026 : le composant n'est jamais le total

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

## American Express — 10-K 2025 : pas de revenu total ; revenus nets des charges d'intérêts extraits à part

72 229 M$ en 2025, contributeur du total propre à l'émetteur (revenus nets après provisions, 66 973 M$), calcul vérifié.
Jamais `total_revenue` ; banques conventionnelles exclues par le filtre d'activité.

Dépôt 10-K 0000004962-26-000080, accepté le 2026-02-06T17:31:47.000+00:00 ; document : https://www.sec.gov/Archives/edgar/data/4962/000000496226000080/axp-20251231.htm

| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |
|---|---|---|---|---|---|
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2023-01-01 → 2023-12-31 | 37 218 000 000 USD | normalisé, rapproché (auto), contexte c-16, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/82` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2024-01-01 → 2024-12-31 | 38 825 000 000 USD | normalisé, rapproché (auto), contexte c-15, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/94` |
| revenue_from_contracts_with_customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | 2025-01-01 → 2025-12-31 | 41 304 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/units/USD/103` |
| revenues_net_of_interest_expense | us-gaap:RevenuesNetOfInterestExpense | 2023-01-01 → 2023-12-31 | 60 515 000 000 USD | normalisé, rapproché (auto), contexte c-16, decimals -6 | `facts/us-gaap/RevenuesNetOfInterestExpense/units/USD/118` |
| revenues_net_of_interest_expense | us-gaap:RevenuesNetOfInterestExpense | 2024-01-01 → 2024-12-31 | 65 949 000 000 USD | normalisé, rapproché (auto), contexte c-15, decimals -6 | `facts/us-gaap/RevenuesNetOfInterestExpense/units/USD/130` |
| revenues_net_of_interest_expense | us-gaap:RevenuesNetOfInterestExpense | 2025-01-01 → 2025-12-31 | 72 229 000 000 USD | normalisé, rapproché (auto), contexte c-1, decimals -6 | `facts/us-gaap/RevenuesNetOfInterestExpense/units/USD/139` |
| total_assets | us-gaap:Assets | au 2023-12-31 | 261 108 000 000 USD | normalisé, rapproché (auto), contexte c-40, decimals -6 | `facts/us-gaap/Assets/units/USD/158` |
| total_assets | us-gaap:Assets | au 2024-12-31 | 271 461 000 000 USD | normalisé, rapproché (auto), contexte c-29, decimals -6 | `facts/us-gaap/Assets/units/USD/169` |
| total_assets | us-gaap:Assets | au 2025-12-31 | 300 052 000 000 USD | normalisé, rapproché (auto), contexte c-28, decimals -6 | `facts/us-gaap/Assets/units/USD/175` |

## Ce qui n'est pas proposé

- Nombres d'actions : catégories d'actions ordinaires (cotées ou non) à établir sur le document, à la date du fait.
- Agrégats et postes à qualifier (dette à intérêt, placements à intérêt, revenus illicites) et capitalisation : voir
  `config/normalisation/edgar_v7.json` (`non_normalises_volontairement`).
