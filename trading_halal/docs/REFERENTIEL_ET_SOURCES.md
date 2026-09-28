# Référentiel religieux : sources, état de vérification, points à trancher

> Le logiciel **ne délivre aucune certification religieuse**. Il applique mécaniquement un référentiel
> écrit dans un fichier JSON, et conserve pour chaque décision la source et la date des données utilisées.
> Un statut ADMISSIBLE signifie seulement : « aucun motif d'exclusion ou d'incertitude selon le référentiel X,
> avec les données disponibles à cette date ».

## 1. Ce qui est codé aujourd'hui

| Élément | Où | Statut |
|---|---|---|
| Univers : actions ordinaires détenues au comptant uniquement (`allowed_instrument_types: ["ACTION"]`) | les deux référentiels | Règle imposée par le cahier des charges |
| Absence de marge, de vente à découvert, de levier et de fractions d'action | `halal_sim/broker.py` (le courtier simulé refuse) | Règle imposée par le cahier des charges |
| Activités EXCLUES : banque et assurance conventionnelles, alcool, porc, jeux de hasard, divertissement pour adultes | `activity_rules` | Exclusions largement partagées ; **à confirmer avec le référentiel retenu** |
| Activités INCERTAINES : tabac, armement, médias/divertissements, hôtellerie/loisirs | `activity_rules` | **Décision religieuse à prendre par vous** (les référentiels divergent) |
| Activité lue dans un **historique daté** (`activities_*.csv`) ; un document publié le jour J n'est utilisé qu'à partir de J+1 | `data.py` | Évite toute lecture d'une information future (revue n° 1) |
| Activité inconnue, absente ou sans fiche publiée → INCERTAIN | `screening.py` | Choix conservateur |
| Les activités « cœur » (banque et assurance conventionnelles, alcool, porc, jeux, divertissement pour adultes) doivent figurer dans tout référentiel et ne peuvent pas y être classées ADMISSIBLE | `structural_problems()` | Garde-fou logiciel contre un référentiel mal saisi ; si votre référentiel exige autre chose, il faudra modifier ce code en connaissance de cause |
| Trois familles de ratios obligatoires (`dette_a_interet`, `liquidites_a_interet`, `revenus_non_conformes`), seuils `null` ou dans ]0 ; 1] | `structural_problems()` | Un référentiel vidé ne peut plus laisser passer un titre sans contrôle financier (revue n° 1) |
| Chaque INCERTAIN porte sa cause (`ACTIVITE`, `DONNEE_MANQUANTE`, `DONNEE_PERIMEE`, `SEUIL_NON_DEFINI`), politique de conservation réglable par cause | `screening.py`, `holding_policy` | Mécanisme technique ; le **réglage** relève de votre référentiel (défaut : vente) |
| Données financières absentes, incomplètes ou périmées (> 200 jours après la fin de période) → INCERTAIN | `screening.py` + `max_fundamentals_age_days` | Choix conservateur ; durée de 200 j **à valider** |
| Seuils financiers | `config/rulesets/demo_fictif.json` | **Valeurs ARBITRAIRES de démonstration (20 % / 20 % / 3 %)**, volontairement différentes des chiffres cités ci-dessous. Interdites sur des données réelles (le moteur refuse). |
| Seuils financiers | `config/rulesets/TEMPLATE_a_valider.json` | `null` : aucun titre ne peut être ADMISSIBLE tant qu'ils ne sont pas renseignés depuis un texte source |

## 2. Sources à consulter (état au 2026-09-28)

| Source | Accès | Ce que j'ai pu vérifier |
|---|---|---|
| AAOIFI, *Shari'ah Standard No. 21 — Financial Paper (Shares and Bonds)*, page officielle : https://aaoifi.com/ss-21-financial-paper-shares-and-bonds/?lang=en | Bloquée depuis mon environnement (proxy réseau) | **Rien.** Texte primaire non lu. |
| Présentation « Shari'ah Screening Methodology », Dr Hamed Merah (secrétaire général de l'AAOIFI), OIC Exchanges Forum : https://www.oicexchanges.org/files/1---shari-ah-screening-in-the-islamic-capital-markets-dr-hamed-merah-secretary-general-aaoifi.pdf | Bloquée depuis mon environnement | **Rien.** |
| Sources secondaires (blogs d'outils de filtrage, article ResearchGate « Revisiting the AAOIFI Shari'ah standards' stock screening ») | Résultats de recherche seulement | Elles rapportent pour la norme n° 21 : dette portant intérêt < 30 % de la capitalisation boursière, liquidités/placements à intérêt < 30 % de la capitalisation, revenus non conformes < 5 % du revenu total, norme publiée initialement en 2004. **Non vérifié sur le texte primaire : NE PAS coder sur cette base.** |
| Méthodologies d'indices (S&P Shariah, Dow Jones Islamic Market, MSCI Islamic, FTSE Shariah) | Documents publics des fournisseurs d'indices | Non consultés. Ils diffèrent notamment sur le **dénominateur** (capitalisation moyenne sur 24 ou 36 mois ou total de l'actif) : à comparer si l'un d'eux est retenu. |

Liens de recherche ayant fourni les informations secondaires :
- https://www.researchgate.net/publication/316958451_Revisiting_the_AAOIFI_Shariah_standards'_stock_screening
- https://faithscreener.com/blog/aaoifi-standard-21-explained
- https://rafiq.money/learn/halal-stock-screening-aaoifi

## 3. Procédure pour passer du modèle à un référentiel validé

1. Choisir **un** référentiel précis et en obtenir le texte officiel **daté** (version, pages ou sections).
2. Copier `config/rulesets/TEMPLATE_a_valider.json` vers un nouveau fichier, renseigner `reference_text`,
   chaque `max` et chaque `source` (référence exacte au paragraphe), le dénominateur, et le statut des activités.
3. Faire relire par une personne qualifiée (savant ou comité charia de votre choix) ; renseigner `validated_by` et `validated_on`,
   `activity_rules_source`, puis seulement `validated: true` et `demo_only: false`.
   Le logiciel vérifie tous ces champs (`real_data_problems()`) avant d'accepter des données réelles ; une source
   contenant « DEMO » ou « ARBITRAIRE » est refusée. Il ne peut évidemment pas vérifier que la validation a réellement eu lieu.
4. Ajouter un test qui fige les valeurs validées (un changement accidentel doit faire échouer les tests).

## 4. Questions religieuses que le logiciel ne peut pas trancher

1. Quel référentiel retenir (AAOIFI n° 21, un indice précis, un comité particulier) ?
2. Dénominateur des ratios : capitalisation instantanée, moyenne glissante (sur quelle durée ?) ou total de l'actif ?
3. Classement du tabac, de l'armement, des médias/divertissements, de l'hôtellerie ?
4. Un titre détenu qui devient EXCLU ou INCERTAIN : vente immédiate (réglage actuel `SELL` pour les deux) ou délai de grâce ?
   Un INCERTAIN dû à une simple donnée manquante justifie-t-il une vente ?
5. Purification : méthode de calcul de la part des dividendes (et des plus-values ?) à donner en aumône. Non implémentée en V1.
