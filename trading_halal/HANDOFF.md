# HANDOFF — simulateur de trading halal, V1.4 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, achats non ADMISSIBLES,
valeurs encaissées ou exécutions sans fondement vérifiable, affirmations non justifiées, erreurs de calcul.

**Le logiciel n'implémente encore aucun référentiel religieux réel complet** : il teste une mécanique de filtrage
avec des seuils de démonstration arbitraires, sur des données inventées.

## 0. Suite donnée à la revue n° 4

Chaque cas a été reproduit sur le commit 9c4bbec, corrigé et couvert par `tests/test_review4.py`. J'ai ensuite
réintroduit chaque défaut (6 variantes) : à chaque fois, au moins un test échoue.

| Cas signalé | Correction | Test |
|---|---|---|
| Contrepartie de 20 € dont la « source » est publiée le 2025-01-01, créditée dès le 2024-06-28 | Une contrepartie exige désormais `delisting_source_date` (publication) et `delisting_cash_date` (paiement), refusées à l'import si absentes ou si le paiement précède la radiation. À la radiation, la position est **toujours gelée** ; elle n'est convertie en espèces qu'au premier jour où la source est publiée depuis la veille (J+1) **et** le paiement effectué. Le moteur ignore aussi une contrepartie sans dates construite en mémoire. | `test_review_case_consideration_published_later_is_not_credited_early` (crédit le 2025-01-02 ; valeurs de portefeuille identiques au scénario sans contrepartie jusqu'au 2025-01-01), `test_payment_date_after_publication_is_respected`, `test_loader_requires_dated_consideration` |
| Achat de FXALP à l'ouverture de son jour de radiation, puis erreur au mois suivant | Import : aucun cours accepté à partir de la date de radiation. Exécution : un achat est refusé si le titre n'est pas dans l'univers **le jour d'exécution** (`HORS_UNIVERS_A_L_EXECUTION`), même si un prix figure dans les données. | `test_review_case_loader_refuses_bar_on_delisting_day`, `test_review_case_engine_refuses_buy_on_delisting_day_even_with_a_price` |
| États financiers en JPY comparés à une cotation en EUR → ADMISSIBLE | Devise de l'état financier différente de la devise de cotation → INCERTAIN (`DONNEE_INVALIDE`), ratios non calculés. Aucune conversion n'est tentée. | `test_review_case_fundamentals_in_other_currency_are_not_admissible` |
| Vente exécutée un jour de volume nul | Exécution refusée si le volume du jour est nul (vente reportée) ; quantité plafonnée à 5 % du volume de la **veille** (connu avant l'ouverture ; paramètre `execution.max_volume_participation`, hypothèse arbitraire). Contrôle du rapport reformulé : il prouve un cours d'ouverture présent et un volume non nul, **pas** qu'une transaction à ce prix et cette quantité était possible. | `test_review_case_no_fill_on_zero_volume_day`, `test_quantity_capped_by_previous_day_volume` |
| « Borne haute » au dernier cours | Deux **scénarios** nommés « radiés à zéro » (résultats principaux) et « radiés au dernier cours », explicitement présentés comme ne bornant pas la valeur réelle (contrepartie supérieure possible, négociation hors cote possible). | libellés du rapport |
| Attribution de l'écart stratégie / référence réinvestie | Reformulé partout : l'écart mesure l'ensemble de la politique de tendance, pas un effet isolé de la formule SMA. | `docs/REFERENCES.md` |
| Faux INCERTAIN possibles du contrôle de capitalisation | Documentés (suspension, catégories d'actions, variation du nombre d'actions, cours ajustés) ; datation du nombre d'actions requise avant données réelles. | `docs/REFERENTIEL_ET_SOURCES.md` § 8 |

Revues n° 1 à 3 : corrections toujours en place et testées (activités et fiches titres datées, règle J → J+1,
validation et catalogue du référentiel, nombres non finis, capitalisation vérifiée, gel des radiés, contrôle réseau).

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- `python3 -m halal_sim run` de bout en bout, bibliothèque standard de Python 3.11 uniquement, aucun réseau.
- Données fictives : 15 titres (FXNU introduit en 2023 ; FXMU radié en 2024 sans contrepartie documentée),
  18 589 barres, 244 états financiers et 16 fiches d'activité datés.
- Filtre à 3 statuts sur l'univers daté ; stratégie SMA 200 ; deux références ; frais, glissement, actions entières,
  volume ; journal SQLite complet ; rapport généré depuis la base avec **10 contrôles**.
- **81 tests**, tous au vert.

## 2. Choix et justification

| Sujet | Choix | Pourquoi |
|---|---|---|
| Stratégie | Détenir si clôture > SMA(200), revue mensuelle, pas de complément | Variante inspirée de Faber (2007) ; un paramètre, peu d'ordres |
| Chronologie | Décision à la clôture de fin de mois → ouverture suivante ; documents publiés le jour J utilisés à J+1 ; radiation connue le jour où elle survient ; contrepartie connue à J+1 de sa publication et encaissée à son paiement | Aucune anticipation |
| Exécution | Cours d'ouverture, glissement 10 pb, volume du jour > 0, ≤ 5 % du volume de la veille | Hypothèses simples et prudentes, à confronter à des données réelles |
| Radiation | Gel à valeur inconnue ; scénarios 0 et dernier cours | Ni l'un ni l'autre n'est une valeur fiable |
| Coûts | 1 € par ordre ; refus si coût aller-retour estimé > 1,5 % | **Fictifs** ; tolérance, pas seuil de rentabilité |
| Seuils religieux | Démo 20 % / 20 % / 3 % **arbitraires** ; modèle réel `null` | Aucun seuil codé de mémoire |

## 3. Résultats de la démonstration (données FICTIVES : aucune valeur probante)

Identiques à la V1.3 : les nouveaux contrôles ne modifient aucun ordre sur ces données (volumes fictifs élevés,
aucune contrepartie documentée). Capital 2 000 €, 2021-10-29 → 2025-12-31.

| | Stratégie | Réf. achat-conservation | Réf. réinvestie |
|---|---|---|---|
| Rendement total, radiés à zéro | +25,86 % | −8,07 % | +4,43 % |
| Rendement total, radiés au dernier cours | +25,86 % | −3,86 % | +8,64 % |
| Baisse maximale | −11,82 % | −29,79 % | −28,86 % |
| Ordres | 41 | 10 | 14 |

**Sans valeur de preuve** : prix inventés, phase baissière voulue, titre radié après une forte baisse.

## 4. Vérifications (81 tests)

`test_costs_and_data` (9), `test_incertain_never_bought` (5), `test_lookahead` (8), `test_no_real_orders` (8),
`test_review2` (10), `test_review3` (12), `test_review4` (8), `test_ruleset_validation` (10), `test_screening` (11).

## 5. Limites connues

1. Données fictives ; aucun référentiel réel complet.
2. Pas de conversion de devises (INCERTAIN ou refus) ; dividendes, purification, fiscalité non modélisés.
3. Exécution : un cours d'ouverture et un volume non nul ne prouvent pas qu'une transaction était possible à ce prix.
4. Radiation sans contrepartie publiée et payée : valeur inconnue (scénarios seulement).
5. Capitalisation contrôlée par cohérence interne ; faux INCERTAIN possibles (§ 8 du document de sources).
6. Référentiel appliqué rétroactivement ; pas d'horodatage ni de fuseau des publications.
7. Un seul paramètre, une seule période, pas d'évaluation hors échantillon.

## 6. Données réelles d'essai : où nous en sommes

Suivant la revue n° 4 : **oui pour l'import et l'audit documentaire, non pour une simulation**.
- `python3 -m halal_sim check-data --dataset <dossier>` charge et valide un jeu sans appliquer de référentiel ni simuler.
- `run` sur des données `REEL` reste **refusé** tant qu'aucun référentiel complet et validé n'existe (`check_run_allowed`).
- Prochaine étape proposée : un petit jeu réel (quelques actions américaines), pour éprouver l'import, les dates de
  disponibilité (SEC EDGAR : date de dépôt et heure d'acceptation), les devises, les opérations sur titres et la
  qualité des prix. EDGAR est gratuit ; la SEC demande un en-tête d'identification (nom et adresse électronique) :
  **décision de l'utilisateur**.

## 7. Questions pour le relecteur

1. Reste-t-il un chemin par lequel une donnée datée après la décision (ou après l'exécution) influence un résultat ?
2. La règle d'encaissement d'une contrepartie (publication J+1 et paiement) est-elle suffisante, y compris pour un échange de titres (non modélisé : quelle conduite par défaut ?) ?
3. Le plafond de 5 % du volume de la veille et le refus sur volume nul sont-ils des hypothèses raisonnables pour un très petit capital ?
4. Quels champs minimaux exiges-tu pour un premier jeu réel d'audit (sans simulation) ?
5. Voyez-vous encore un préalable bloquant avant cet audit de données réelles ?
