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
| Chaque type de ratio est lié à **son** numérateur et à des dénominateurs admis (`RATIO_CATALOG`) : dette → dette portant intérêt / (capitalisation ou total de l'actif) ; liquidités → liquidités et placements à intérêt / (capitalisation ou total de l'actif) ; revenus non conformes → revenus non conformes / chiffre d'affaires | `screening.py` | Empêche de détourner un ratio vers d'autres champs (revue n° 2). Ajouter un type (ex. créances) = modification du catalogue + test |
| Valeur financière non finie, négative ou incohérente (revenus non conformes > chiffre d'affaires) : refusée à l'import ; si elle apparaît malgré tout, INCERTAIN (cause `DONNEE_INVALIDE`) | `data.py`, `screening.py` | Revue n° 2 : `nan` et une dette négative rendaient un titre ADMISSIBLE |
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

## 5. Rigidité assumée du moteur (réponse à la revue n° 2)

La revue n° 2 juge trop rigide d'imposer à tout référentiel trois types de ratios et six activités « cœur ».
Je conserve ces exigences **volontairement** : les assouplir rouvrirait la faille de la revue n° 1 (un référentiel
vidé qui laisse tout passer). Elles sont regroupées dans `REQUIRED_RATIO_IDS`, `RATIO_CATALOG` et
`CORE_EXCLUDED_ACTIVITIES` (`halal_sim/screening.py`) : si le référentiel que vous choisissez l'exige, on les
modifiera explicitement, avec un test et une relecture, plutôt que par un simple fichier de configuration.

Le logiciel vérifie la **forme** d'un référentiel (champs, sources, noms) ; il ne peut pas vérifier que la source
citée dit bien ce qui est codé, ni que la validation a réellement eu lieu. Cette vérification reste humaine.

## 6. Exigences de datation pour les données réelles

- `available_date` doit être la date à laquelle **le public** a pu accéder au document, dans le calendrier du marché
  concerné — pas la fin de période comptable. Pour les dépôts EDGAR, la SEC distingue la date officielle de dépôt
  et l'heure d'acceptation, et ses API publient les données avec un délai de traitement : il faudra conserver
  l'horodatage, le fuseau et la version de chaque document pour rendre la règle « J → J+1 » vérifiable.
- Le référentiel s'applique **rétroactivement** à toute la période simulée. C'est acceptable pour tester une règle
  fixée à l'avance ; cela ne reconstruit pas les décisions religieuses réellement disponibles à chaque date passée.
- Une fiche titre modifiée sans mise à jour de `known_from` ne peut pas être détectée par le logiciel : pour un
  changement de type d'instrument ou de devise, il faudra un historique daté (comme pour les activités).

## 7. Ce que le catalogue de ratios ne sait pas encore reproduire (revue n° 3)

**Le logiciel n'implémente aucun référentiel réel complet.** Chaque ratio déclare sa méthode de calcul (`calcul`) ;
seule `ponctuel_derniere_publication` est implémentée (valeurs du dernier état financier publié). D'après le
relecteur — points **non vérifiés par moi** sur les textes :
- les règles FTSE SGX utiliseraient le total de l'actif pour la dette et les liquidités, exigeraient un contrôle des
  créances et prévoiraient des règles de suivi entre deux examens ;
- une méthodologie S&P utiliserait une capitalisation moyenne sur 36 mois.
Aucun de ces deux référentiels n'est donc reproductible en l'état. Pour en adopter un, il faudra : le texte daté,
de nouveaux champs (créances, historique de capitalisation), de nouvelles méthodes de calcul dans le code, et des
tests propres à ce référentiel. Le total de l'actif n'est pas interchangeable avec la capitalisation : le choix
du dénominateur doit venir du texte retenu.

La capitalisation publiée est confrontée à nombre d'actions x cours de clôture à la fin de période (écart toléré
5 %, contrôle de cohérence des données et non seuil religieux). Cela écarte une valeur aberrante isolée, pas une
série de données fausses mais cohérentes entre elles : la provenance des données reste à contrôler.

## 8. Limites du contrôle de capitalisation (revue n° 4)

Le contrôle « nombre d'actions x cours de fin de période » peut produire de **faux INCERTAIN** : suspension ou
longue fermeture (pas de cours à moins de 7 jours de la fin de période), variation du nombre d'actions entre la date
du chiffre et la fin de période, plusieurs catégories d'actions, cours ajustés des divisions. Avant des données
réelles, il faudra dater le nombre d'actions et préciser la définition de capitalisation du référentiel retenu.
La devise de chaque état financier est comparée à celle de la cotation : sans conversion datée, une différence
donne INCERTAIN.

## 9. Règles de fiqh fournies par l'utilisateur

**Source** : document fourni par l'utilisateur le 2026-09-28, « Actions, bourse et produits financiers en Islam :
vérification et annotation de vos notes de cours » (PDF, 19 pages). Ce document est lui-même une synthèse de recherche ;
il signale que plusieurs textes ont été lus dans des **copies secondaires** (notamment une copie de la norme AAOIFI 21
publiée par la Bourse des Philippines) et demande de vérifier chaque citation sur l'édition imprimée.

**Ce qui en a été codé** : `config/rulesets/AAOIFI_SS21_document_utilisateur.json`, **non validé**.

| Règle | Valeur | Référence dans le document |
|---|---|---|
| Emprunts à intérêt / capitalisation boursière | ≤ 30 % | § 5.1, AAOIFI SS 21 §3/4/2 (« does not exceed 30% of the market capitalization ») |
| Dépôts à intérêt / capitalisation boursière | ≤ 30 % | § 5.1, AAOIFI SS 21 §3/4/3 |
| Revenus illicites / revenu total | ≤ 5 % | § 5.1, AAOIFI SS 21 §3/4/4 (toute source, intérêts perçus compris) |
| Activité principale illicite (banque et assurance conventionnelles, alcool, porc, jeux…) | EXCLU | Synthèse A.1, § 3.1 |
| Vente à découvert, marge à intérêt, options, futures, CFD, indices, Forex à levier, obligations à intérêt | interdits | Synthèse A.2-A.3, § 9 — déjà exclus par le périmètre du logiciel |
| Liquidités non investies non rémunérées | — | § 9 — déjà le cas dans la simulation |

Le comparateur « ≤ » suit la formulation « does not exceed » citée. Le choix de l'AAOIFI suit la recommandation du
document (« le plus strict et le plus documenté »), sans prendre le verdict le plus favorable titre par titre (§ 5.3).

**Divergence affichée dans chaque rapport** (document, Synthèse C.1) : le projet suit l'avis permissif sous conditions ;
les Académies de l'OCI (rés. 63 (1/7)) et de Makka, ainsi que la Lajna Dāʾima, interdisent les sociétés « mêlées ».

**Pourquoi le référentiel reste non validé** : le document demande lui-même une validation écrite par un sharia board
nommé (Synthèse D). Le logiciel refuse donc toute simulation sur données réelles tant que `validated_by` et
`validated_on` sont vides.

**Points ouverts tirés du document (non codés)** : états financiers « vérifiés » (§3/4/5) non distingués des autres ;
date de la capitalisation retenue ; filtre mālikite des actifs monétaires (liquidités + créances ≤ ⅔, à valider par un
mufti mālikite, § 7) ; tabac, armement, médias, hôtellerie (non traités) ; délai de cession d'un titre devenu non
conforme ; purification (méthode AAOIFI 3/4/6/4, détenteur en fin de période ou prorata FCNA, plus-values) ; revente
avant règlement-livraison ; zakāt (mudīr / muḥtakir). La liste complète figure dans `open_questions` du référentiel.
