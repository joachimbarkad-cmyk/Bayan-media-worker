# Sonde : que ferait la règle du revenu total (edgar_v5) sur de vrais 10-K ?

Générée par `tools/sonde_revenus.py` (dernier 10-K de chaque émetteur à la date d'exécution, faits de l'entité
entière, exercice complet, USD). Données brutes : `docs/SONDE_REVENUS.json`. Ni rapprochement ni
normalisation : un repérage des cas où le repli R1 → total serait juste ou faux. Montants tels qu'affichés
(souvent en millions).

| Émetteur | Dépôt | Décision edgar_v5 | Revenues | R0b (réglementé) | R1 (contrats clients) | Autres concepts de revenu déclarés |
|---|---|---|---|---|---|---|
| Apple Inc. | 0000320193-25-000079 | REPLI R1 -> total (preuve positive) | — | — | 416,161 | — |
| MICROSOFT CORP | 0001193125-26-323660 | REPLI R1 -> total (preuve positive) | — | — | 331,839 | — |
| Alphabet Inc. | 0001652044-26-000018 | Revenues -> total | 402,836 | — | — | — |
| BLACK HILLS CORP /SD/ | 0001193125-26-046028 | Revenues -> total | 2,310.0 | — | 2,286.2 | — |
| REALTY INCOME CORP | 0000726728-26-000011 | Revenues -> total | 5,749,377 | — | — | us-gaap:LeaseIncome, us-gaap:OperatingLeaseVariableLeaseIncome |
| SIMON PROPERTY GROUP INC. | 0001104659-26-019419 | Revenues -> total | 6,364,505 | — | — | us-gaap:LeaseIncome, us-gaap:OperatingLeaseLeaseIncome, us-gaap:OperatingLeaseLeaseIncomeLeasePayments, us-gaap:VariableLeaseIncome, ManagementFeesAndOtherRevenues |
| Prologis, Inc. | 0001193125-26-051453 | Revenues -> total | 8,790,127 | — | — | ManagementFeesRevenue, OtherRealEstateRevenue, RentalRevenue |
| JPMORGAN CHASE & CO | 0001628280-26-008131 | Revenues -> total | 182,447 | — | — | us-gaap:BrokerageCommissionsRevenue, us-gaap:FairValueNetDerivativeAssetLiabilityMeasuredOnRecurringBasisUnobservableInputsReconciliationSales, us-gaap:InterestIncomeOperating, us-gaap:InvestmentBankingRevenue, us-gaap:NoninterestIncome, us-gaap:NoninterestIncomeOther, us-gaap:OperatingLeaseLeaseIncome, us-gaap:PrincipalTransactionsRevenue, us-gaap:RevenuesNetOfInterestExpense, AdministrativeServicesRevenue1, InvestmentBankingAdvisoryFeeRevenue |
| BANK OF AMERICA CORP /DE/ | 0000070858-26-000157 | Revenues -> total | 113,097 | — | — | us-gaap:FairValueNetDerivativeAssetLiabilityMeasuredOnRecurringBasisUnobservableInputsReconciliationSales, us-gaap:InterestAndDividendIncomeOperating, us-gaap:LeaseIncome, us-gaap:NoninterestIncome, us-gaap:NoninterestIncomeOtherOperatingIncome, us-gaap:OperatingLeaseLeaseIncome, RevenuesNetOfInterestExpenseFullTaxEquivalentBasis, SalesTypeAndDirectFinancingLeasesLeaseIncome |
| Duke Energy CORP | 0001326160-26-000014 | RegulatedAndUnregulatedOperatingRevenue -> total | — | 32,237 | — | us-gaap:RegulatedOperatingRevenueElectricNonNuclear, us-gaap:RegulatedOperatingRevenueGas, us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax, us-gaap:UnregulatedOperatingRevenue |
| AT&T INC. | 0000732717-26-000120 | Revenues -> total | 125,648 | — | — | — |
| Walmart Inc. | 0000104169-26-000055 | Revenues -> total | 713,163 | — | 706,413 | — |
| EXXON MOBIL CORP | 0000034088-26-000045 | Revenues -> total | 332,238 | — | — | AssetRetirementObligationReductionDueToPropertySales, TotalIncomeSalesBasedAndOtherTaxes |
| UNITEDHEALTH GROUP INC | 0000731766-26-000062 | Revenues -> total | 447,567 | — | — | us-gaap:PremiumsEarnedNet |
| VISA INC. | 0001403161-25-000089 | REPLI R1 -> total (preuve positive) | — | — | 40,000 | — |
| FORD MOTOR CO | 0000037996-26-000015 | REPLI R1 -> total (preuve positive) | — | — | 187,267 | — |
| CATERPILLAR INC | 0000018230-26-000008 | Revenues -> total | 67,589 | — | — | us-gaap:LeaseIncome, us-gaap:OperatingLeaseLeaseIncome, us-gaap:SalesTypeLeaseRevenue |
| BOEING CO | 0001628280-26-004357 | Revenues -> total | 89,463 | — | — | us-gaap:OperatingLeaseLeaseIncome, us-gaap:SalesTypeAndDirectFinancingLeasesProfitLoss, SalesTypeandDirectFinancingLeasesLeaseIncome |
| COCA COLA CO | 0001628280-26-010047 | Revenues -> total | 47,941 | — | — | IntersegmentRevenue, RevenueForReportableSegments |
| AMERICAN EXPRESS CO | 0000004962-26-000080 | repli R1 bloqué (autres revenus) | — | — | 41,304 | us-gaap:InterestAndDividendIncomeOperating, us-gaap:InterestAndDividendIncomeSecurities, us-gaap:NoninterestIncome, us-gaap:RevenuesNetOfInterestExpense, TotalRevenuesNetOfInterestExpenseAfterProvisionsForLosses |

## Constats (28/09/2026, edgar_v5)

- **Preuve positive (revue n° 15)** : un composant R1 ne devient total que s'il est, dans les calculs d'un rôle
  « Statement » du dépôt, l'enfant +1 de `GrossProfit` ou `OperatingIncomeLoss` sans autre élément positif. Apple et
  Microsoft (marge brute = R1 − coût des ventes), Visa et Ford (résultat d'exploitation = R1 − charges) : prouvés.
  Ford : 187 267 M$ comprennent Ford Credit (13 271 M$), vérifié par le relecteur dans le 10-K.
- **American Express** : R1 absent de tout calcul et autres revenus déclarés : aucun total (v3 aurait donné 41 304).
- **Duke Energy** : `RegulatedAndUnregulatedOperatingRevenue` (32 237) est l'enfant +1 du résultat d'exploitation dans
  le compte de résultat (à côté d'un gain de cession, admis pour un concept total par définition) ; le composant
  `…IncludingAssessedTax` (31 741) reste distinct.
- **Walmart** : `Revenues` 713 163 ≠ R1 706 413.
- Première version d'edgar_v4 : l'exclusion « Tax » écartait R1 (`…ExcludingAssessedTax`) ; corrigé, garde-fou ajouté.
