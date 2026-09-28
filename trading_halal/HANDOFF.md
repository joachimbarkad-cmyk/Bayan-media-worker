# HANDOFF — V1 simulateur de trading halal (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire ce projet de façon critique** : cherchez surtout les biais d'utilisation de données futures, les failles
qui permettraient d'acheter un titre non ADMISSIBLE, les affirmations non justifiées et les erreurs de calcul des coûts.

## 1. Ce qui fonctionne réellement (vérifié en lançant le code)

- `python3 -m halal_sim run` tourne de bout en bout en moins d'une seconde, avec la seule bibliothèque standard de Python 3.11.
- Import et validation de 3 CSV fictifs (13 titres, 16 939 barres quotidiennes 2021-01-04 → 2025-12-31, 220 états financiers
  trimestriels datés par leur **date de publication**) + `manifest.json` qui déclare `nature: FICTIF`.
- Filtre religieux à 3 statuts avec motifs, ratios, période financière, date de publication, source et identifiant du référentiel,
  tout enregistré dans la table `screenings`.
- Stratégie SMA 200 jours appliquée aux seuls titres ADMISSIBLES ; portefeuille de référence ; frais, glissement, actions entières.
- Journal SQLite complet : `runs` (empreintes SHA-256 du code et des données, configuration et référentiel complets),
  `screenings`, `decisions` (y compris tous les refus et leur code), `orders` (exécutés ou rejetés), `equity`, `metrics`.
- Rapport Markdown `output/rapport_demo.md` généré **depuis la base** (signaux, refus, changements de statut, coûts, sensibilité au capital, contrôles).
- 35 tests `unittest`, tous au vert : `python3 -m unittest discover -s tests -v` → `Ran 35 tests … OK`.

## 2. Choix et justification

| Sujet | Choix | Pourquoi |
|---|---|---|
| Langage / stockage | Python stdlib + SQLite, aucune dépendance | Coût nul, installation nulle, auditable |
| Stratégie | Filtre de tendance : détenir si clôture > SMA(200 clôtures), revue mensuelle | Règle publique ancienne (Faber 2007, variante 10 mois), un seul paramètre, peu d'ordres (frais fixes), aucune prédiction |
| Pondération | Budget par titre = valeur du portefeuille / nombre de titres ADMISSIBLES ; pas de rééquilibrage des positions existantes | Le capital non investi reste en liquidités (pas d'intérêts) ; moins d'ordres |
| Chronologie | Décision à la clôture du dernier jour de bourse du mois → exécution à l'**ouverture du jour suivant** | Évite d'exécuter au prix qui a servi à décider |
| Référence | Achat à parts égales des titres ADMISSIBLES au 1er jour de décision, conservation ; ventes seulement si le filtre l'impose ; mêmes frais | Isole l'apport de la règle de tendance, avec le même univers et le même filtre |
| Coûts | 1 € fixe par ordre (min 1 €), 0 %, glissement 10 pb défavorable ; refus si coût aller-retour estimé > 1,5 % ; alerte au-delà de 0,75 % | **Valeurs fictives**, à remplacer par la grille d'un vrai courtier |
| Politique titres détenus | EXCLU → vente ; INCERTAIN → vente (réglable : `HOLD` = gel sans renfort) | Choix conservateur en attendant la décision de l'utilisateur |
| Seuils religieux | Démo : 20 % / 20 % / 3 % **arbitraires** ; modèle réel : `null` | Consigne : ne pas coder de seuils AAOIFI de mémoire |

Sources religieuses et état de vérification : `docs/REFERENTIEL_ET_SOURCES.md`. En résumé : la page officielle de la norme AAOIFI n° 21
est identifiée mais **inaccessible depuis mon environnement** ; les chiffres qui circulent (30 % / 30 % / 5 %, dénominateur = capitalisation)
viennent de **sources secondaires non vérifiées** et ne sont donc pas codés.

## 3. Résultats de la démonstration (données FICTIVES : aucune valeur probante)

Période 2021-10-29 → 2025-12-31, capital 2 000 € :

| | Stratégie | Référence |
|---|---|---|
| Rendement total | +24,54 % | +3,20 % |
| Baisse maximale | −10,83 % | −26,51 % |
| Exposition moyenne | 46,7 % | 63,5 % |
| Ordres | 39 | 8 |
| Coûts (frais + glissement) | 2,53 % du capital | 0,50 % |

Sensibilité : à **500 €**, aucun achat n'est jugé pertinent (132 refus pour coût/capital, rendement 0) ; à 10 000 €, les coûts tombent à 1 % du capital.

**Pourquoi ces chiffres ne valent rien comme preuve :** j'ai construit les prix fictifs avec une phase baissière en 2022 pour faire jouer
les deux branches de la règle ; un filtre de tendance est avantagé *par construction* sur de telles données. La référence est en outre
pénalisée par deux ventes forcées (FXIOT pour une donnée manquante, FXKAP devenu EXCLU) dont les liquidités restent inactives.

## 4. Vérifications (tests automatisés, tous passés)

| Point critique | Défenses (en couches) | Tests |
|---|---|---|
| Un INCERTAIN (ou EXCLU) ne peut pas être acheté | (1) la stratégie n'émet jamais ACHAT hors ADMISSIBLE ; (2) `PaperBroker.buy` lève `ForbiddenOrderError` ; (3) contrainte CHECK sur `decisions` et trigger SQLite sur `orders` | `test_incertain_never_bought.py` (5 tests, dont un backtest complet recoupé avec `screenings`, et le référentiel modèle sans seuils → 0 achat) |
| Aucun ordre réel | Aucun module de courtage ; analyse AST : aucune importation réseau/courtier (socket seulement dans `safety.py`) ; aucune lecture de variables d'environnement ou de clés ; `forbid_network()` coupe les sockets au lancement ; `runs.simulation_only` contraint à 1 ; données REELLES refusées avec un référentiel démo ou non validé | `test_no_real_orders.py` (6 tests, dont la ligne de commande complète lancée réseau coupé) |
| Pas de lecture de données futures | Décisions uniquement via `PointInTimeView` (lève `LookaheadError`) ; états financiers filtrés par date de **publication** ; date maximale lue enregistrée pour chaque décision et contrainte en base ; exécution strictement postérieure (contrôlée par le courtier et par la base) | `test_lookahead.py` (6 tests, dont un **test de perturbation** : toutes les données après le 2023-06-30 sont falsifiées → filtrages, décisions, ordres et valeurs jusqu'à cette date strictement identiques) |
| Coûts, données | Frais minimum, glissement défavorable, actions entières, pas de découvert, refus des petits montants ; validation stricte des CSV (source obligatoire, cohérence des prix, nature déclarée) | `test_costs_and_data.py` (9 tests), `test_screening.py` (9 tests) |

## 5. Limites connues (à ne pas sous-estimer)

1. **Données fictives** uniquement. Aucune conclusion de rentabilité n'est possible à ce stade.
2. Connaissance du calendrier : savoir qu'un jour est « le dernier du mois » suppose le calendrier boursier connu d'avance (acceptable : il est publié à l'avance). Pas de jours fériés dans les données fictives.
3. Classement d'activité supposé **constant** sur la période (pas d'historique daté de l'activité) : biais possible avec des données réelles.
4. Capitalisation prise à la fin de période de l'état financier (pas de moyenne glissante) : le dénominateur réel dépend du référentiel.
5. Dividendes, purification, fiscalité, change, impôt de bourse éventuel non modélisés. Rendement « prix seul ».
6. Biais du survivant : non traité (l'univers fictif ne contient ni radiation ni faillite). À traiter impérativement avec des données réelles.
7. Un seul jeu de paramètres, une seule période : risque de surinterprétation ; il faudra une évaluation hors échantillon.
8. Ordre des achats le même jour : alphabétique quand les liquidités manquent (arbitraire mais déterministe).
9. `forbid_network()` protège contre le code Python ; ce n'est pas une isolation système.

## 6. Prochaines décisions

**À l'utilisateur (religieux ; je ne peux pas les trancher) :** référentiel retenu, dénominateur, seuils, classement du tabac, de l'armement,
des médias et de l'hôtellerie, traitement d'un titre détenu devenu EXCLU/INCERTAIN, méthode de purification.

**À l'utilisateur (compte ou coût) :** marché visé (France/Europe ou États-Unis) et type de compte au comptant ; grille tarifaire réelle
du courtier envisagé (uniquement pour paramétrer les frais : aucune connexion).

**Techniques proposées pour la V2 (gratuites) :**
1. Données réelles gratuites : pour les actions américaines, SEC EDGAR (XBRL « companyfacts », gratuit, avec **dates de dépôt** : idéal pour le point-dans-le-temps) ; prix quotidiens gratuits (par exemple export CSV Stooq), en vérifiant leurs conditions d'utilisation. Pour l'Europe, les données financières datées gratuites sont plus difficiles : à étudier.
2. Traiter le biais du survivant (univers historique daté) et les dividendes.
3. Évaluation honnête : période d'entraînement / période de test séparées, plusieurs sous-périodes, comparaison avec un indice islamique si des données gratuites existent.
4. Purification des dividendes une fois la méthode choisie.

## 7. Questions précises pour le relecteur

1. Voyez-vous un chemin de code par lequel une décision ou un filtrage pourrait lire une donnée postérieure à sa date ?
2. La référence (achat-conservation des admissibles initiaux) est-elle juste, ou faut-il une référence rééquilibrée ?
3. Le calcul du coût aller-retour (`CostModel.roundtrip_cost_pct`) et le seuil de 1,5 % sont-ils raisonnables pour un petit capital ?
4. Le choix « INCERTAIN détenu → vente » est-il le bon réglage par défaut, sachant qu'une donnée manquante suffit à le déclencher ?
5. Les motifs affichés dans le rapport sont-ils assez clairs pour un débutant ?
