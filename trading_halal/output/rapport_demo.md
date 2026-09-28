# Rapport de simulation — exécution n° 1

> **DONNÉES FICTIVES DE DÉMONSTRATION.** Sociétés, prix et états financiers inventés pour tester le logiciel. Les chiffres ci-dessous ne disent RIEN de la rentabilité réelle de la stratégie.

> **Simulation uniquement.** Aucun courtier connecté, aucun ordre réel envoyé.

> **Pas une certification religieuse.** Le filtre applique mécaniquement le référentiel indiqué ; ADMISSIBLE ne signifie pas « 100 % halal ».

> **Référentiel non validé** (`DEMO_FICTIF_v1`) : RÉFÉRENTIEL DE DÉMONSTRATION. Les seuils financiers ci-dessous sont des valeurs ARBITRAIRES choisies pour tester le logiciel. Ce ne sont PAS les seuils AAOIFI ni ceux d'un indice. Interdit sur des données réelles (le moteur refuse).

## Paramètres

| Paramètre | Valeur |
|---|---|
| Période simulée | 2021-10-29 → 2025-12-31 |
| Capital initial | 2000.00 EUR |
| Données | demo_fictif_v1 (FICTIF) |
| Référentiel religieux | DEMO_FICTIF_v1 (validé : NON) |
| Stratégie | filtre_tendance_sma : détenir un titre admissible si clôture > moyenne des 200 dernières clôtures ; décision en fin de mois, exécution à l'ouverture suivante |
| Référence « achat-conservation » | Achat à parts égales des titres admissibles au 1er jour de décision, puis conservation (ventes seulement si le filtre ou une radiation l'impose) |
| Référence « réinvestie » | Chaque fin de mois : mêmes ventes imposées, puis liquidités réparties à parts cibles égales entre les titres admissibles du moment, sans moyenne mobile (docs/REFERENCES.md) |
| Frais (fictifs) | 1.0 EUR fixe + 0 % (min 1.0 EUR) par ordre ; glissement 10 pb ; refus si coût aller-retour > 1.5 % |
| Politique titres détenus | EXCLU → SELL, INCERTAIN → SELL |
| Empreinte du code / des données | c4a4b7a62f02 / 8973b58e3308 |

## Résultats : stratégie contre deux références

| Indicateur | Stratégie | Réf. achat-conservation | Réf. réinvestie |
|---|---|---|---|
| Valeur finale | 2517.29 | 1921.66 | 2282.82 |
| Rendement total (%) | 25.86 | -3.92 | 14.14 |
| Rendement annualisé (%) | 5.67 | -0.95 | 3.22 |
| Volatilité annualisée (%) | 10.03 | 10.46 | 14.25 |
| Baisse maximale (%) | -11.82 | -29.79 | -28.86 |
| Rendement/risque (taux sans risque = 0) | 0.58 | -0.04 | 0.29 |
| Exposition moyenne aux actions (%) | 44.4 | 58.1 | 81.1 |
| Achats simulés | 22 | 7 | 14 |
| Ventes simulées | 19 | 4 | 5 |
| Frais de courtage simulés | 41 | 11 | 19 |
| Coût de glissement simulé | 10.14 | 2.17 | 3.83 |
| Coûts totaux (% du capital initial) | 2.56 | 0.66 | 1.14 |

Les trois portefeuilles utilisent les mêmes données, le même univers daté, le même filtre, les mêmes frais et les mêmes règles d'exécution. Les liquidités ne sont pas rémunérées (pas d'intérêts). Dividendes non modélisés. La référence achat-conservation ne réinvestit pas le produit des ventes imposées ; la référence réinvestie, si.

## Sensibilité au capital (même stratégie, mêmes frais)

| Capital | Stratégie (%) | Réf. achat-conservation (%) | Réf. réinvestie (%) | Coûts stratégie (% capital) | Achats refusés stratégie (coût/capital) |
|---|---|---|---|---|---|
| 500 EUR | 0 | 0 | 0 | 0 | 145 |
| 2000 EUR | 25.86 | -3.92 | 14.14 | 2.56 | 0 |
| 10000 EUR | 27.94 | -6.11 | 8.54 | 0.95 | 0 |

Avec un petit capital, les frais fixes et les actions entières pèsent davantage : c'est ce que mesure ce tableau. Un rendement de 0 avec des refus signifie qu'aucun achat n'a été jugé pertinent à ce niveau de capital (le capital est resté en liquidités).

## Filtre religieux au 2025-11-28

ADMISSIBLE = aucun motif d'exclusion ni d'incertitude trouvé avec le référentiel et les données disponibles ; ce n'est pas une certification. Les documents publiés un jour J ne sont utilisés qu'à partir du jour J+1.

| Titre | Statut | Motifs | Ratios | Données financières | Activité |
|---|---|---|---|---|---|
| FXALP | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | Dette portant intérêt / capitalisation = 5.2% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 8.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | SOFTWARE (fiche du 2021-01-01) |
| FXBET | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | Dette portant intérêt / capitalisation = 12.2% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 10.0% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.5% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | HEALTHCARE (fiche du 2021-01-01) |
| FXIOT | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | Dette portant intérêt / capitalisation = 14.5% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 5.6% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | INDUSTRIALS (fiche du 2021-01-01) |
| FXNU | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | Dette portant intérêt / capitalisation = 8.0% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 5.0% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | INDUSTRIALS (fiche du 2023-02-28) |
| FXOME | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | Dette portant intérêt / capitalisation = 10.0% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 6.7% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 2.2% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | RETAIL (fiche du 2021-01-01) |
| FXDEL | **EXCLU** | Activité 'ALCOHOL' : Production ou vente principale d'alcool | Dette portant intérêt / capitalisation = 10.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 5.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | ALCOHOL (fiche du 2021-01-01) |
| FXEPS | **EXCLU** | Dette portant intérêt / capitalisation = 43.3% > seuil 20.0% | Dette portant intérêt / capitalisation = 43.3% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 4.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | INDUSTRIALS (fiche du 2021-01-01) |
| FXGAM | **EXCLU** | Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Dette portant intérêt / capitalisation = 61.3% > seuil 20.0%; Liquidités et placements à intérêt / capitalisation = 37.1% > seuil 20.0%; Revenus non conformes / chiffre d'affaires = 70.0% > seuil 3.0% | Dette portant intérêt / capitalisation = 61.3% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 37.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 70.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | CONVENTIONAL_BANKING (fiche du 2021-01-01) |
| FXKAP | **EXCLU** | Dette portant intérêt / capitalisation = 38.8% > seuil 20.0% | Dette portant intérêt / capitalisation = 38.8% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 5.8% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | TELECOM (fiche du 2021-01-01) |
| FXLAM | **EXCLU** | Activité 'GAMBLING' : Jeux de hasard | Dette portant intérêt / capitalisation = 13.4% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 5.0% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | TRANSPORT;GAMBLING (fiche du 2024-03-15) |
| FXOBL | **EXCLU** | Instrument 'OBLIGATION_CONVENTIONNELLE' hors univers : seules les actions détenues au comptant sont admises; Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Aucune donnée financière publiée avant la date de décision | — | aucune | CONVENTIONAL_BANKING (fiche du 2021-01-01) |
| FXETA | **INCERTAIN** [causes : DONNEE_MANQUANTE] | Aucune donnée financière publiée avant la date de décision | — | aucune | ENERGY (fiche du 2021-01-01) |
| FXSIG | **INCERTAIN** [causes : DONNEE_PERIMEE] | Données financières périmées : fin de période 2022-12-31 (1063 j > 200 j) | Dette portant intérêt / capitalisation = 8.0% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 4.9% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2022-12-31 publié le 2023-02-14 | CHEMICALS (fiche du 2021-01-01) |
| FXTHE | **INCERTAIN** [causes : ACTIVITE] | Activité 'TOBACCO' : Classement variable selon les référentiels : décision religieuse à trancher par l'utilisateur | Dette portant intérêt / capitalisation = 10.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Liquidités et placements à intérêt / capitalisation = 5.1% (seuil 20% — seuil de DÉMO arbitraire)<br>Revenus non conformes / chiffre d'affaires = 0.0% (seuil 3% — seuil de DÉMO arbitraire) | 2025-09-30 publié le 2025-11-14 | TOBACCO (fiche du 2021-01-01) |

Sources des données financières : DEMO_FICTIF - généré par tools/generate_demo_data.py (graine 20260928)

### Changements de statut au cours de la période

| Date | Titre | Changement | Motif |
|---|---|---|---|
| 2023-05-31 | FXIOT | ADMISSIBLE → INCERTAIN | Revenus non conformes / chiffre d'affaires : donnée manquante (non_compliant_revenue / total_revenue) |
| 2023-05-31 | FXNU | INCERTAIN → ADMISSIBLE | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' |
| 2023-07-31 | FXSIG | ADMISSIBLE → INCERTAIN | Données financières périmées : fin de période 2022-12-31 (212 j > 200 j) |
| 2023-08-31 | FXIOT | INCERTAIN → ADMISSIBLE | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' |
| 2024-03-29 | FXLAM | ADMISSIBLE → EXCLU | Activité 'GAMBLING' : Jeux de hasard |
| 2024-08-30 | FXKAP | ADMISSIBLE → EXCLU | Dette portant intérêt / capitalisation = 38.5% > seuil 20.0% |

## Signaux de la stratégie au 2025-11-28

| Titre | Statut | Décision | En clair | Données | Code et détail |
|---|---|---|---|---|---|
| FXDEL | EXCLU | **AUCUNE** | Le filtre religieux exclut ce titre : achat interdit. | clôture 51.9165 / SMA 51.3626 | `REFUS_STATUT_EXCLU` — Activité 'ALCOHOL' : Production ou vente principale d'alcool. Signal technique d'achat ignoré. |
| FXEPS | EXCLU | **AUCUNE** | Le filtre religieux exclut ce titre : achat interdit. | clôture 6.0348 / SMA 5.9668 | `REFUS_STATUT_EXCLU` — Dette portant intérêt / capitalisation = 43.3% > seuil 20.0%. Signal technique d'achat ignoré. |
| FXETA | INCERTAIN | **AUCUNE** | Le filtre religieux ne peut pas conclure (donnée ou règle manquante) : achat interdit par prudence. | clôture 19.7212 / SMA 18.7124 | `REFUS_STATUT_INCERTAIN` — Aucune donnée financière publiée avant la date de décision. Signal technique d'achat ignoré. |
| FXGAM | EXCLU | **AUCUNE** | Le filtre religieux exclut ce titre : achat interdit. | clôture 22.9042 / SMA 21.0649 | `REFUS_STATUT_EXCLU` — Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Dette portant intérêt / capitalisation = 61.3% > seuil 20.0%; Liquidités et placements à intérêt / capitalisation = 37.1% > seuil 20.0%; Revenus non conformes / chiffre d'affaires = 70.0% > seuil 3.0%. Signal technique d'achat ignoré. |
| FXIOT | ADMISSIBLE | **AUCUNE** | Admissible, mais le cours est sous sa moyenne : pas d'achat. | clôture 15.6215 / SMA 16.8582 | `REFUS_SOUS_MOYENNE` — clôture <= SMA |
| FXKAP | EXCLU | **AUCUNE** | Le filtre religieux exclut ce titre : achat interdit. | clôture 21.1656 / SMA 21.2029 | `REFUS_STATUT_EXCLU` — Dette portant intérêt / capitalisation = 38.8% > seuil 20.0%. |
| FXLAM | EXCLU | **AUCUNE** | Le filtre religieux exclut ce titre : achat interdit. | clôture 23.318 / SMA 24.49 | `REFUS_STATUT_EXCLU` — Activité 'GAMBLING' : Jeux de hasard. |
| FXNU | ADMISSIBLE | **AUCUNE** | Admissible, mais le cours est sous sa moyenne : pas d'achat. | clôture 35.3718 / SMA 36.701 | `REFUS_SOUS_MOYENNE` — clôture <= SMA |
| FXOBL | EXCLU | **AUCUNE** | Le filtre religieux exclut ce titre : achat interdit. | clôture 99.5187 / SMA 99.0543 | `REFUS_STATUT_EXCLU` — Instrument 'OBLIGATION_CONVENTIONNELLE' hors univers : seules les actions détenues au comptant sont admises; Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Aucune donnée financière publiée avant la date de décision. Signal technique d'achat ignoré. |
| FXSIG | INCERTAIN | **AUCUNE** | Le filtre religieux ne peut pas conclure (donnée ou règle manquante) : achat interdit par prudence. | clôture 181.8554 / SMA 176.2027 | `REFUS_STATUT_INCERTAIN` — Données financières périmées : fin de période 2022-12-31 (1063 j > 200 j). Signal technique d'achat ignoré. |
| FXTHE | INCERTAIN | **AUCUNE** | Le filtre religieux ne peut pas conclure (donnée ou règle manquante) : achat interdit par prudence. | clôture 61.9999 / SMA 54.3209 | `REFUS_STATUT_INCERTAIN` — Activité 'TOBACCO' : Classement variable selon les référentiels : décision religieuse à trancher par l'utilisateur. Signal technique d'achat ignoré. |
| FXALP | ADMISSIBLE | **CONSERVER** | Déjà détenu et toujours au-dessus de sa moyenne : on garde. | clôture 69.6518 / SMA 63.7557 | `CONSERVE_TENDANCE_HAUSSIERE` — clôture > SMA |
| FXBET | ADMISSIBLE | **CONSERVER** | Déjà détenu et toujours au-dessus de sa moyenne : on garde. | clôture 69.0036 / SMA 61.4405 | `CONSERVE_TENDANCE_HAUSSIERE` — clôture > SMA |
| FXOME | ADMISSIBLE | **CONSERVER** | Déjà détenu et toujours au-dessus de sa moyenne : on garde. | clôture 88.5953 / SMA 77.838 | `CONSERVE_TENDANCE_HAUSSIERE` — clôture > SMA |

Une décision « ACHAT » est une proposition simulée pour l'ouverture du jour de bourse suivant, pas un conseil. À l'exécution, la quantité peut être réduite (liquidités insuffisantes au prix d'ouverture) ou l'ordre rejeté (coût devenu disproportionné, prix manquant) : voir « Ordres rejetés au moment de l'exécution simulée ».

## Refus et ventes imposées sur toute la période (stratégie)

| Code | En clair | Nombre de décisions |
|---|---|---|
| `REFUS_STATUT_EXCLU` | Le filtre religieux exclut ce titre : achat interdit. | 236 |
| `REFUS_SOUS_MOYENNE` | Admissible, mais le cours est sous sa moyenne : pas d'achat. | 176 |
| `REFUS_STATUT_INCERTAIN` | Le filtre religieux ne peut pas conclure (donnée ou règle manquante) : achat interdit par prudence. | 132 |
| `REFUS_HISTORIQUE_INSUFFISANT` | Pas assez d'historique de prix pour appliquer la règle : pas d'achat. | 7 |
| `VENTE_STATUT_INCERTAIN` | Titre détenu devenu INCERTAIN : vente simulée selon la politique choisie. | 2 |
| `VENTE_STATUT_EXCLU` | Titre détenu devenu EXCLU : vente simulée. | 1 |

### Achats refusés pour coût ou capital (10 derniers, deux portefeuilles)

| Date | Portefeuille | Titre | Motif | Détail |
|---|---|---|---|---|
| 2022-10-31 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.99 % de 111.86 > limite 1.50 % : opération peu pertinente |
| 2022-09-30 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.92 % de 116.44 > limite 1.50 % : opération peu pertinente |
| 2022-08-31 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 2.00 % de 110.88 > limite 1.50 % : opération peu pertinente |
| 2022-07-29 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.81 % de 124.49 > limite 1.50 % : opération peu pertinente |
| 2022-06-30 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.87 % de 119.75 > limite 1.50 % : opération peu pertinente |
| 2022-05-31 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.87 % de 119.97 > limite 1.50 % : opération peu pertinente |
| 2022-04-29 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.89 % de 118.68 > limite 1.50 % : opération peu pertinente |
| 2022-03-31 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.95 % de 113.99 > limite 1.50 % : opération peu pertinente |
| 2022-02-28 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.84 % de 121.74 > limite 1.50 % : opération peu pertinente |
| 2022-01-31 | reference_reinvestie | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.61 % de 142.08 > limite 1.50 % : opération peu pertinente |

### Ordres rejetés au moment de l'exécution simulée

Aucun.

## Journal des ordres simulés (15 derniers, stratégie)

| Décision | Exécution | Titre | Sens | Qté | Ouverture | Prix simulé | Frais | Glissement | Motif |
|---|---|---|---|---|---|---|---|---|---|
| 2025-06-30 | 2025-07-01 | FXNU | SELL | 11 | 34.87 | 34.84 | 1.00 | 0.38 | SIGNAL_VENTE_TENDANCE |
| 2025-04-30 | 2025-05-01 | FXIOT | SELL | 19 | 17.77 | 17.75 | 1.00 | 0.34 | SIGNAL_VENTE_TENDANCE |
| 2024-12-31 | 2025-01-01 | FXBET | BUY | 8 | 52.74 | 52.79 | 1.00 | 0.42 | SIGNAL_ACHAT_TENDANCE |
| 2024-12-31 | 2025-01-01 | FXNU | BUY | 11 | 37.47 | 37.51 | 1.00 | 0.41 | SIGNAL_ACHAT_TENDANCE |
| 2024-10-31 | 2024-11-01 | FXOME | BUY | 6 | 63.68 | 63.75 | 1.00 | 0.38 | SIGNAL_ACHAT_TENDANCE |
| 2024-09-30 | 2024-10-01 | FXBET | SELL | 5 | 48.39 | 48.34 | 1.00 | 0.24 | SIGNAL_VENTE_TENDANCE |
| 2024-09-30 | 2024-10-01 | FXNU | SELL | 9 | 31.44 | 31.41 | 1.00 | 0.28 | SIGNAL_VENTE_TENDANCE |
| 2024-09-30 | 2024-10-01 | FXOME | SELL | 3 | 59.19 | 59.13 | 1.00 | 0.18 | SIGNAL_VENTE_TENDANCE |
| 2024-08-30 | 2024-09-02 | FXKAP | SELL | 18 | 16.36 | 16.35 | 1.00 | 0.29 | VENTE_STATUT_EXCLU |
| 2024-05-31 | 2024-06-03 | FXALP | BUY | 9 | 30.67 | 30.70 | 1.00 | 0.28 | SIGNAL_ACHAT_TENDANCE |
| 2024-04-30 | 2024-05-01 | FXALP | SELL | 8 | 28.60 | 28.57 | 1.00 | 0.23 | SIGNAL_VENTE_TENDANCE |
| 2024-03-29 | 2024-04-01 | FXALP | BUY | 8 | 32.58 | 32.61 | 1.00 | 0.26 | SIGNAL_ACHAT_TENDANCE |
| 2024-03-29 | 2024-04-01 | FXBET | BUY | 5 | 50.62 | 50.67 | 1.00 | 0.25 | SIGNAL_ACHAT_TENDANCE |
| 2024-03-29 | 2024-04-01 | FXIOT | BUY | 19 | 14.35 | 14.36 | 1.00 | 0.27 | SIGNAL_ACHAT_TENDANCE |
| 2024-02-29 | 2024-03-01 | FXKAP | BUY | 18 | 13.05 | 13.06 | 1.00 | 0.23 | SIGNAL_ACHAT_TENDANCE |

## Vérifications automatiques de cette exécution

| Contrôle | Résultat | Détail |
|---|---|---|
| Aucun achat d'un titre non ADMISSIBLE (statut enregistré) | OK | 0 cas |
| Aucun achat d'un titre non ADMISSIBLE (recoupement avec le filtrage) | OK | 0 cas |
| Aucune décision n'a lu une donnée postérieure à sa date | OK | 0 cas |
| Aucun filtrage n'a lu une donnée postérieure à sa date | OK | 0 cas |
| Exécution toujours après la décision | OK | 0 cas sur 71 ordres |
| Jamais de solde de liquidités négatif (pas de marge) | OK | 0 jours |
| Exécution marquée simulation uniquement | OK | runs.simulation_only = 1 |
| Code sans bibliothèque réseau/courtage ni lecture de clés (analyse statique à ce lancement) | OK | 11 fichiers analysés |
| Réseau effectivement coupé pendant cette exécution | OK | socket.connect / create_connection / getaddrinfo remplacés par un refus |

Ces contrôles portent sur le code Python de ce projet et sur ce processus ; ils ne remplacent pas une isolation au niveau du système. Le projet ne contient aucun connecteur de courtage.

## Limites à garder en tête

- Données fictives : aucune conclusion de rentabilité possible. Il faudra des données réelles datées.
- Une seule période, un seul paramètre (SMA 200) : risque de sur-interprétation, même sur données réelles.
- Dividendes, purification, fiscalité, change et jours fériés ne sont pas modélisés.
- Frais fictifs : à remplacer par la grille réelle du courtier choisi.
- Activités lues depuis un historique daté, mais aucune durée de validité maximale d'une fiche d'activité.
- Pas de conversion de devises : tous les titres doivent être dans la devise du portefeuille (sinon refus).
- Titre radié : liquidation supposée au dernier cours coté (en réalité : rachat, échange ou perte totale).
- Le référentiel religieux s'applique rétroactivement à toute la période simulée.

