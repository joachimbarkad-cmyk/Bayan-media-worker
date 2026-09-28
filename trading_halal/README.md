# Trading halal assisté — V1 : portefeuille FICTIF

Prototype de recherche : il filtre un univers d'actions selon un référentiel religieux traçable,
applique une stratégie simple aux seuls titres admissibles, simule un portefeuille avec frais et
glissement, enregistre tout dans SQLite et produit un rapport comparé à une référence.

**Ce que ce projet ne fait pas :**
- il n'implémente encore **aucun référentiel religieux réel complet** (voir `docs/REFERENTIEL_ET_SOURCES.md`) ;
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
python3 -m unittest discover -s tests -v        # 180 vérifications automatiques
python3 -m halal_sim audit-docs                  # contrôle du dossier d'audit documentaire d'exemple (FICTIF)
python3 -m halal_sim run --ruleset config/rulesets/AAOIFI_SS21_document_utilisateur.json --no-sensitivity   # référentiel tiré de votre document (non validé)
python3 tools/edgar_collect.py collect --cik 320193 --dry-run --out collecte_brute   # collecte EDGAR (voir docs/AUDIT_DOCUMENTAIRE.md)
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
| `data/demo/` | Données **FICTIVES** : `manifest.json` (nature = FICTIF), fiches titres datées (entrée en cote, radiation), prix quotidiens, états financiers et fiches d'activité datés par leur publication |
| `config/simulation.json` | Capital, frais (fictifs), stratégie, politique de vente, chemins |
| `config/rulesets/demo_fictif.json` | Référentiel de **démonstration** (seuils arbitraires, interdit sur données réelles) |
| `config/rulesets/TEMPLATE_a_valider.json` | Modèle à compléter depuis un texte officiel ; seuils `null` → rien n'est admissible |
| `halal_sim/data.py` | Import, validation, accès « point dans le temps » (`PointInTimeView`) |
| `halal_sim/screening.py` | Filtre ADMISSIBLE / EXCLU / INCERTAIN avec motifs, ratios, source et date |
| `halal_sim/strategy.py` | Stratégie unique : filtre de tendance SMA 200 jours |
| `halal_sim/broker.py` | Courtier **simulé** (frais, glissement, actions entières, ni marge ni découvert) |
| `halal_sim/backtest.py` | Moteur chronologique : stratégie + deux références |
| `halal_sim/audit.py`, `docs/AUDIT_DOCUMENTAIRE.md`, `data/audit_exemple_FICTIF/` | Format et contrôle d'un dossier d'audit de documents réels, sans simulation ni statut religieux |
| `docs/REFERENCES.md` | Règles des deux portefeuilles de référence, fixées avant le test |
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

Créer un dossier avec un `manifest.json` (`"nature": "REEL"`) et les quatre CSV au même format que `data/demo/`
(titres, prix, états financiers, fiches d'activité), chaque document ayant sa **date de publication** et sa **source**.
Chaque fiche titre porte `known_from` (date à partir de laquelle son type d'instrument et sa devise sont connus)
et, s'il y a lieu, `delisted_date` : inclure les titres **radiés** pour limiter le biais du survivant. Aucun cours n'est
accepté à partir de la date de radiation. Une contrepartie en espèces se documente par `delisting_cash_per_share`,
`delisting_source`, `delisting_source_date` (publication) et `delisting_cash_date` (paiement) ; elle n'est créditée
qu'une fois publiée et payée. D'ici là, ou sans elle, la position est gelée à valeur inconnue (deux scénarios : 0 et
dernier cours, qui ne sont pas des bornes). La devise des états financiers doit être celle de la cotation, sinon le
titre est INCERTAIN.
Les états financiers portent `shares_outstanding` : la capitalisation publiée est vérifiée contre nombre d'actions
x cours de fin de période quand un ratio l'utilise.
Les valeurs non finies (`nan`, `inf`), négatives ou incohérentes sont refusées à l'import.
Un document publié le jour J n'est utilisé qu'à partir de la décision du jour J+1 (l'heure de publication n'est pas connue).
Tous les titres doivent être dans la devise du portefeuille (pas encore de conversion).

Le moteur refusera de tourner tant que le référentiel choisi n'est pas **complet** : texte source daté, chaque seuil
renseigné et sourcé, source du classement des activités, nom et date de la validation, `validated: true` et
`demo_only: false`. Basculer les booléens ne suffit pas (voir `docs/REFERENTIEL_ET_SOURCES.md`).

## Base SQLite d'une version antérieure

Le schéma de la base est versionné. Une base créée par une version antérieure du code est **refusée et laissée
intacte** (jamais déplacée ni supprimée). Pour continuer : `python3 -m halal_sim run --db output/nouvelle.sqlite`.
Pour garder une copie : `python3 -m halal_sim snapshot-db output/simulation.sqlite` (instantané vérifié ; l'original
n'est pas modifié ; fermez les autres programmes qui l'utilisent pour que la copie soit complète).

## Référentiels disponibles

- `config/rulesets/demo_fictif.json` : seuils arbitraires de démonstration (par défaut).
- `config/rulesets/AAOIFI_SS21_document_utilisateur.json` : seuils AAOIFI SS 21 tels que cités par le document de
  fiqh fourni par l'utilisateur ; **non validé** (refusé sur données réelles jusqu'à validation par un sharia board).
- `config/rulesets/TEMPLATE_a_valider.json` : modèle vide.

Collecte de données réelles : voir `docs/GUIDE_COLLECTE_EDGAR.md`. Premier dossier réel (Apple, non exploitable en l'état) :
`python3 -m halal_sim audit-docs data/audit_edgar_apple` ;
`python3 tools/edgar_collect.py verify-trace --raw collecte/apple --audit data/audit_edgar_apple` (chaque fait recalculé
depuis le JSON brut, et toute la conversion refaite et comparée). Contrôle indépendant contre une copie retéléchargée :
`python3 tools/edgar_collect.py collect --cik 320193 --user-agent "…" --out /tmp/copie` puis
`python3 tools/edgar_collect.py verify-source --raw collecte/apple --fresh /tmp/copie --audit data/audit_edgar_apple`. Ordre de normalisation des ratios : `docs/NORMALISATION_RATIOS.md`.
