# Trading halal assisté — V1 : portefeuille FICTIF

Prototype de recherche : il filtre un univers d'actions selon un référentiel religieux traçable,
applique une stratégie simple aux seuls titres admissibles, simule un portefeuille avec frais et
glissement, enregistre tout dans SQLite et produit un rapport comparé à une référence.

**Ce que ce projet ne fait pas :**
- aucun ordre réel, aucune connexion à un courtier, aucune clé API (le réseau est même coupé au lancement) ;
- aucune certification religieuse : « ADMISSIBLE » n'est pas « 100 % halal » ;
- aucune prédiction de rendement : les propositions découlent d'une règle explicite sur des données datées ;
- les données fournies sont **FICTIVES** (sociétés inventées) : les résultats ne prouvent rien sur la rentabilité réelle.

## Prérequis

Python 3.10 ou plus récent. **Aucune installation de paquet** : bibliothèque standard uniquement (csv, sqlite3, unittest). Coût : 0 €.

## Commandes

Depuis la racine du dépôt :

```sh
cd trading_halal
python3 -m halal_sim check-data                 # valide les fichiers de données de démonstration
python3 -m halal_sim run                        # simulation complète + rapport + sensibilité au capital
python3 -m unittest discover -s tests -v        # 35 vérifications automatiques
```

Options utiles :

```sh
python3 -m halal_sim run --capital 1000         # autre capital initial
python3 -m halal_sim run --no-sensitivity       # sans les simulations à 500 / 2000 / 10000 €
python3 tools/generate_demo_data.py             # régénère les données fictives (déterministe)
```

Résultats :
- rapport lisible : `output/rapport_demo.md` ;
- base SQLite : `output/simulation.sqlite` (tables `runs`, `screenings`, `decisions`, `orders`, `equity`, `metrics`).
  Chaque lancement ajoute une exécution numérotée ; supprimer le fichier pour repartir de zéro.

## Organisation

| Chemin | Rôle |
|---|---|
| `data/demo/` | Données **FICTIVES** : `manifest.json` (nature = FICTIF), titres, prix quotidiens, états financiers datés |
| `config/simulation.json` | Capital, frais (fictifs), stratégie, politique de vente, chemins |
| `config/rulesets/demo_fictif.json` | Référentiel de **démonstration** (seuils arbitraires, interdit sur données réelles) |
| `config/rulesets/TEMPLATE_a_valider.json` | Modèle à compléter depuis un texte officiel ; seuils `null` → rien n'est admissible |
| `halal_sim/data.py` | Import, validation, accès « point dans le temps » (`PointInTimeView`) |
| `halal_sim/screening.py` | Filtre ADMISSIBLE / EXCLU / INCERTAIN avec motifs, ratios, source et date |
| `halal_sim/strategy.py` | Stratégie unique : filtre de tendance SMA 200 jours |
| `halal_sim/broker.py` | Courtier **simulé** (frais, glissement, actions entières, ni marge ni découvert) |
| `halal_sim/backtest.py` | Moteur chronologique stratégie + référence |
| `halal_sim/report.py` | Rapport Markdown et contrôles recalculés depuis SQLite |
| `halal_sim/safety.py` | Coupure du réseau au lancement |
| `docs/REFERENTIEL_ET_SOURCES.md` | Sources religieuses, état de vérification, questions à trancher |
| `HANDOFF.md` | Synthèse pour la relecture (ChatGPT, DeepSeek) |

## La stratégie en une phrase

Le dernier jour de bourse de chaque mois, on détient à parts égales les titres ADMISSIBLES dont la clôture est
au-dessus de la moyenne de leurs 200 dernières clôtures ; les autres parts restent en liquidités non rémunérées.
Les ordres sont simulés à l'ouverture du jour de bourse suivant, avec frais et glissement défavorable.
Tout achat dont le coût aller-retour estimé dépasse 1,5 % du montant est refusé comme « peu pertinent ».

## Utiliser vos propres données (plus tard)

Créer un dossier avec un `manifest.json` (`"nature": "REEL"`) et les trois CSV au même format que `data/demo/`,
chaque état financier ayant sa **date de publication** et sa **source**. Le moteur refusera de tourner tant que le
référentiel choisi n'est pas marqué `validated: true` (voir `docs/REFERENTIEL_ET_SOURCES.md`).
