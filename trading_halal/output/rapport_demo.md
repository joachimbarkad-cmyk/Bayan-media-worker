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
| Référence | Achat à parts égales des titres admissibles au 1er jour de décision, puis conservation (ventes seulement si le filtre religieux l'impose) |
| Frais (fictifs) | 1.0 EUR fixe + 0 % (min 1.0 EUR) par ordre ; glissement 10 pb ; refus si coût aller-retour > 1.5 % |
| Politique titres détenus | EXCLU → SELL, INCERTAIN → SELL |
| Empreinte du code / des données | 7ff2f189aec8 / b8549126303c |

## Résultats : stratégie contre référence

| Indicateur | Stratégie | Référence |
|---|---|---|
| Valeur finale | 2490.72 | 2063.91 |
| Rendement total (%) | 24.54 | 3.2 |
| Rendement annualisé (%) | 5.4 | 0.76 |
| Volatilité annualisée (%) | 10.46 | 11.12 |
| Baisse maximale (%) | -10.83 | -26.51 |
| Rendement/risque (taux sans risque = 0) | 0.54 | 0.12 |
| Exposition moyenne aux actions (%) | 46.7 | 63.5 |
| Achats simulés | 21 | 6 |
| Ventes simulées | 18 | 2 |
| Frais de courtage simulés | 39 | 8 |
| Coût de glissement simulé | 11.58 | 2.07 |
| Coûts totaux (% du capital initial) | 2.53 | 0.5 |

Les deux portefeuilles utilisent les mêmes données, le même filtre, les mêmes frais et les mêmes règles d'exécution. Les liquidités ne sont pas rémunérées (pas d'intérêts). Dividendes non modélisés dans la V1.

## Sensibilité au capital (même stratégie, mêmes frais)

| Capital | Stratégie (%) | Référence (%) | Coûts stratégie (% capital) | Achats refusés (coût/capital) |
|---|---|---|---|---|
| 500 EUR | 0 | 0 | 0 | 132 |
| 2000 EUR | 24.54 | 3.2 | 2.53 | 0 |
| 10000 EUR | 26.82 | 2.39 | 1 | 0 |

Avec un petit capital, les frais fixes et les actions entières pèsent davantage : c'est ce que mesure ce tableau. Un rendement de 0 avec des refus signifie qu'aucun achat n'a été jugé pertinent à ce niveau de capital (le capital est resté en liquidités).

## Filtre religieux au 2025-11-28

| Titre | Statut | Motifs | Ratios | Données financières | Activité |
|---|---|---|---|---|---|
| FXALP | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | dette_a_interet=5.2%, liquidites_a_interet=8.1%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | SOFTWARE |
| FXBET | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | dette_a_interet=12.2%, liquidites_a_interet=10.0%, revenus_non_conformes=0.5% | 2025-09-30 publié le 2025-11-14 | HEALTHCARE |
| FXIOT | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | dette_a_interet=14.5%, liquidites_a_interet=5.6%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | INDUSTRIALS |
| FXLAM | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | dette_a_interet=13.4%, liquidites_a_interet=5.0%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | TRANSPORT |
| FXOME | **ADMISSIBLE** | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' | dette_a_interet=10.0%, liquidites_a_interet=6.7%, revenus_non_conformes=2.2% | 2025-09-30 publié le 2025-11-14 | RETAIL |
| FXDEL | **EXCLU** | Activité 'ALCOHOL' : Production ou vente principale d'alcool | dette_a_interet=10.1%, liquidites_a_interet=5.1%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | ALCOHOL |
| FXEPS | **EXCLU** | Dette portant intérêt / capitalisation = 43.3% > seuil 20.0% | dette_a_interet=43.3%, liquidites_a_interet=4.1%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | INDUSTRIALS |
| FXGAM | **EXCLU** | Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Dette portant intérêt / capitalisation = 61.3% > seuil 20.0%; Liquidités et placements à intérêt / capitalisation = 37.1% > seuil 20.0%; Revenus non conformes / chiffre d'affaires = 70.0% > seuil 3.0% | dette_a_interet=61.3%, liquidites_a_interet=37.1%, revenus_non_conformes=70.0% | 2025-09-30 publié le 2025-11-14 | CONVENTIONAL_BANKING |
| FXKAP | **EXCLU** | Dette portant intérêt / capitalisation = 38.8% > seuil 20.0% | dette_a_interet=38.8%, liquidites_a_interet=5.8%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | TELECOM |
| FXOBL | **EXCLU** | Instrument 'OBLIGATION_CONVENTIONNELLE' hors univers : seules les actions détenues au comptant sont admises; Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Aucune donnée financière publiée à la date de décision | — | aucune | CONVENTIONAL_BANKING |
| FXETA | **INCERTAIN** | Aucune donnée financière publiée à la date de décision | — | aucune | ENERGY |
| FXSIG | **INCERTAIN** | Données financières périmées : fin de période 2022-12-31 (1063 j > 200 j) | dette_a_interet=8.0%, liquidites_a_interet=4.9%, revenus_non_conformes=0.0% | 2022-12-31 publié le 2023-02-14 | CHEMICALS |
| FXTHE | **INCERTAIN** | Activité 'TOBACCO' : Classement variable selon les référentiels : décision religieuse à trancher par l'utilisateur | dette_a_interet=10.1%, liquidites_a_interet=5.1%, revenus_non_conformes=0.0% | 2025-09-30 publié le 2025-11-14 | TOBACCO |

Sources des données financières : DEMO_FICTIF - généré par tools/generate_demo_data.py (graine 20260928)

### Changements de statut au cours de la période

| Date | Titre | Changement | Motif |
|---|---|---|---|
| 2023-05-31 | FXIOT | ADMISSIBLE → INCERTAIN | Revenus non conformes / chiffre d'affaires : donnée manquante (non_compliant_revenue / total_revenue) |
| 2023-07-31 | FXSIG | ADMISSIBLE → INCERTAIN | Données financières périmées : fin de période 2022-12-31 (212 j > 200 j) |
| 2023-08-31 | FXIOT | INCERTAIN → ADMISSIBLE | Aucun motif d'exclusion ou d'incertitude selon le référentiel 'DEMO_FICTIF_v1' |
| 2024-08-30 | FXKAP | ADMISSIBLE → EXCLU | Dette portant intérêt / capitalisation = 38.5% > seuil 20.0% |

## Signaux de la stratégie au 2025-11-28

| Titre | Statut | Signal | Décision | Code | Données | Détail |
|---|---|---|---|---|---|---|
| FXDEL | EXCLU | AUCUNE | **AUCUNE** | REFUS_STATUT_EXCLU | clôture 51.9165 / SMA 51.3626 | Activité 'ALCOHOL' : Production ou vente principale d'alcool. Signal technique d'achat ignoré. |
| FXEPS | EXCLU | AUCUNE | **AUCUNE** | REFUS_STATUT_EXCLU | clôture 6.0348 / SMA 5.9668 | Dette portant intérêt / capitalisation = 43.3% > seuil 20.0%. Signal technique d'achat ignoré. |
| FXETA | INCERTAIN | AUCUNE | **AUCUNE** | REFUS_STATUT_INCERTAIN | clôture 19.7212 / SMA 18.7124 | Aucune donnée financière publiée à la date de décision. Signal technique d'achat ignoré. |
| FXGAM | EXCLU | AUCUNE | **AUCUNE** | REFUS_STATUT_EXCLU | clôture 22.9042 / SMA 21.0649 | Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Dette portant intérêt / capitalisation = 61.3% > seuil 20.0%; Liquidités et placements à intérêt / capitalisation = 37.1% > seuil 20.0%; Revenus non conformes / chiffre d'affaires = 70.0% > seuil 3.0%. Signal technique d'achat ignoré. |
| FXIOT | ADMISSIBLE | AUCUNE | **AUCUNE** | REFUS_SOUS_MOYENNE | clôture 15.6215 / SMA 16.8582 | clôture <= SMA |
| FXKAP | EXCLU | AUCUNE | **AUCUNE** | REFUS_STATUT_EXCLU | clôture 21.1656 / SMA 21.2029 | Dette portant intérêt / capitalisation = 38.8% > seuil 20.0%. |
| FXLAM | ADMISSIBLE | AUCUNE | **AUCUNE** | REFUS_SOUS_MOYENNE | clôture 23.318 / SMA 24.49 | clôture <= SMA |
| FXOBL | EXCLU | AUCUNE | **AUCUNE** | REFUS_STATUT_EXCLU | clôture 99.5187 / SMA 99.0543 | Instrument 'OBLIGATION_CONVENTIONNELLE' hors univers : seules les actions détenues au comptant sont admises; Activité 'CONVENTIONAL_BANKING' : Finance conventionnelle fondée sur l'intérêt (riba); Aucune donnée financière publiée à la date de décision. Signal technique d'achat ignoré. |
| FXSIG | INCERTAIN | AUCUNE | **AUCUNE** | REFUS_STATUT_INCERTAIN | clôture 181.8554 / SMA 176.2027 | Données financières périmées : fin de période 2022-12-31 (1063 j > 200 j). Signal technique d'achat ignoré. |
| FXTHE | INCERTAIN | AUCUNE | **AUCUNE** | REFUS_STATUT_INCERTAIN | clôture 61.9999 / SMA 54.3209 | Activité 'TOBACCO' : Classement variable selon les référentiels : décision religieuse à trancher par l'utilisateur. Signal technique d'achat ignoré. |
| FXALP | ADMISSIBLE | CONSERVER | **CONSERVER** | CONSERVE_TENDANCE_HAUSSIERE | clôture 69.6518 / SMA 63.7557 | clôture > SMA |
| FXBET | ADMISSIBLE | CONSERVER | **CONSERVER** | CONSERVE_TENDANCE_HAUSSIERE | clôture 69.0036 / SMA 61.4405 | clôture > SMA |
| FXOME | ADMISSIBLE | CONSERVER | **CONSERVER** | CONSERVE_TENDANCE_HAUSSIERE | clôture 88.5953 / SMA 77.838 | clôture > SMA |

Une décision « ACHAT » ici est une proposition simulée pour le jour de bourse suivant, pas un conseil.

## Refus et ventes imposées sur toute la période (stratégie)

| Motif | Nombre de décisions |
|---|---|
| REFUS_STATUT_EXCLU | 215 |
| REFUS_SOUS_MOYENNE | 155 |
| REFUS_STATUT_INCERTAIN | 130 |
| VENTE_STATUT_INCERTAIN | 2 |
| VENTE_STATUT_EXCLU | 1 |

### Achats refusés pour coût ou capital (10 derniers, deux portefeuilles)

| Date | Portefeuille | Titre | Motif | Détail |
|---|---|---|---|---|
| 2021-10-29 | reference | FXSIG | REFUS_COUT_DISPROPORTIONNE | Coût aller-retour estimé 1.54 % de 148.86 > limite 1.50 % : opération peu pertinente |

### Ordres rejetés au moment de l'exécution simulée

Aucun.

## Journal des ordres simulés (15 derniers, stratégie)

| Décision | Exécution | Titre | Sens | Qté | Ouverture | Prix simulé | Frais | Glissement | Motif |
|---|---|---|---|---|---|---|---|---|---|
| 2025-07-31 | 2025-08-01 | FXLAM | SELL | 17 | 24.43 | 24.41 | 1.00 | 0.42 | SIGNAL_VENTE_TENDANCE |
| 2025-04-30 | 2025-05-01 | FXIOT | SELL | 21 | 17.77 | 17.75 | 1.00 | 0.37 | SIGNAL_VENTE_TENDANCE |
| 2025-04-30 | 2025-05-01 | FXLAM | BUY | 17 | 27.06 | 27.09 | 1.00 | 0.46 | SIGNAL_ACHAT_TENDANCE |
| 2025-03-31 | 2025-04-01 | FXLAM | SELL | 16 | 24.62 | 24.60 | 1.00 | 0.39 | SIGNAL_VENTE_TENDANCE |
| 2024-12-31 | 2025-01-01 | FXBET | BUY | 8 | 52.74 | 52.79 | 1.00 | 0.42 | SIGNAL_ACHAT_TENDANCE |
| 2024-10-31 | 2024-11-01 | FXLAM | BUY | 16 | 24.17 | 24.20 | 1.00 | 0.39 | SIGNAL_ACHAT_TENDANCE |
| 2024-10-31 | 2024-11-01 | FXOME | BUY | 6 | 63.68 | 63.75 | 1.00 | 0.38 | SIGNAL_ACHAT_TENDANCE |
| 2024-09-30 | 2024-10-01 | FXBET | SELL | 6 | 48.39 | 48.34 | 1.00 | 0.29 | SIGNAL_VENTE_TENDANCE |
| 2024-09-30 | 2024-10-01 | FXOME | SELL | 5 | 59.19 | 59.13 | 1.00 | 0.30 | SIGNAL_VENTE_TENDANCE |
| 2024-08-30 | 2024-09-02 | FXKAP | SELL | 23 | 16.36 | 16.35 | 1.00 | 0.38 | VENTE_STATUT_EXCLU |
| 2024-05-31 | 2024-06-03 | FXALP | BUY | 10 | 30.67 | 30.70 | 1.00 | 0.31 | SIGNAL_ACHAT_TENDANCE |
| 2024-04-30 | 2024-05-01 | FXALP | SELL | 9 | 28.60 | 28.57 | 1.00 | 0.26 | SIGNAL_VENTE_TENDANCE |
| 2024-03-29 | 2024-04-01 | FXALP | BUY | 9 | 32.58 | 32.61 | 1.00 | 0.29 | SIGNAL_ACHAT_TENDANCE |
| 2024-03-29 | 2024-04-01 | FXBET | BUY | 6 | 50.62 | 50.67 | 1.00 | 0.30 | SIGNAL_ACHAT_TENDANCE |
| 2024-03-29 | 2024-04-01 | FXIOT | BUY | 21 | 14.35 | 14.36 | 1.00 | 0.30 | SIGNAL_ACHAT_TENDANCE |

## Vérifications automatiques de cette exécution

| Contrôle | Résultat | Détail |
|---|---|---|
| Aucun achat d'un titre non ADMISSIBLE (statut enregistré) | OK | 0 cas |
| Aucun achat d'un titre non ADMISSIBLE (recoupement avec le filtrage) | OK | 0 cas |
| Aucune décision n'a lu une donnée postérieure à sa date | OK | 0 cas |
| Aucun filtrage n'a lu une donnée postérieure à sa date | OK | 0 cas |
| Exécution toujours après la décision | OK | 0 cas sur 47 ordres |
| Jamais de solde de liquidités négatif (pas de marge) | OK | 0 jours |
| Exécution marquée simulation uniquement | OK | runs.simulation_only = 1 |
| Aucun ordre réel | OK | Aucun module de courtage ; réseau coupé par safety.forbid_network() |

## Limites à garder en tête

- Données fictives : aucune conclusion de rentabilité possible. Il faudra des données réelles datées.
- Une seule période, un seul paramètre (SMA 200) : risque de sur-interprétation, même sur données réelles.
- Dividendes, purification, fiscalité, change et jours fériés ne sont pas modélisés.
- Frais fictifs : à remplacer par la grille réelle du courtier choisi.
- Classement d'activité supposé constant sur la période (pas d'historique daté de l'activité).

