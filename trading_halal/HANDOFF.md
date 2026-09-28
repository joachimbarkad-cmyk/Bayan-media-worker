# HANDOFF — simulateur de trading halal, V1.16 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, contrôles d'audit
contournables, informations inventées ou perdues par la conversion, opérations destructives, **fidélité du référentiel
au document de fiqh fourni par l'utilisateur**.

## V1.16 — Revue n° 13 : plus aucune normalisation sans le document

La revue n° 13 a montré que deux inférences des V1.13–V1.15 n'étaient pas fondées ; **les normalisations publiées dans
ces versions sont retirées** (dossiers régénérés depuis une conversion neuve) :

- **C1 (catégorie d'actions par la liste des tickers) : fausse et lookahead.** La liste `tickers` de submissions est
  l'état actuel (GOOGM/GOOGN introduits en 2026 : depositary shares de préférentielles convertibles, pas des actions
  ordinaires) ; elle ignore les catégories non cotées (Alphabet classe B) ; un ticker n'identifie pas le type de titre
  (notes cotées sous MSFT). ⇒ C1 retirée ; **les règles visant shares_outstanding ou market_cap sont refusées** par
  l'outil ; les catégories d'actions ordinaires, cotées ou non, à la date du fait, relèvent d'une personne.
- **D1 (aucune dimension si une seule valeur dans companyfacts) : non prouvée.** La SEC dit que ses API agrègent des
  faits applicables à l'entité entière, pas que tout fait présent est sans dimension. ⇒ D1 et X1 retirées.

Nouvelle conception (`config/normalisation/edgar_v2.json`, `tools/edgar_normalize.py`) :

1. `normalize` ne fait que **proposer** : `propositions_normalisation.csv` (règle, période exacte, valeur brute, pointeur
   et empreinte de l'entrée brute), conflits K1 exclus ; **aucun fait modifié**, aucun journal.
2. `reconcile-ixbrl --raw --regles` recalcule les propositions (sans se fier au fichier), lit la copie locale du
   document, et normalise un fait seulement s'il y trouve la même entité, la même période exacte, la même unité, un
   contexte **sans segment ni scénario**, et une valeur affichée égale : contexte réel, « aucune dimension » établie par
   le document (preuve = fichier + SHA-256), `decimals`, `reconciled = auto`. Échec ⇒ fait non normalisé, motif écrit
   (« NON NORMALISÉ : document : … ») ; faits du même concept sans document ⇒ « NON NORMALISÉ : en attente … ».
3. `verify-normalisation` refait propositions, import et rapprochement et compare cellules, concept_map et fichier de
   propositions ; auteur des saisies = outil + empreinte des règles.

État réel : Apple 205, Microsoft 126, Alphabet 52 propositions (chiffre d'affaires et total des actifs) ; **0 fait
normalisé** (documents inaccessibles : `www.sec.gov` bloqué) ; verify-trace, verify-normalisation et audit à 0 ; verdict
« aucun fait normalisé ». Montants principaux recoupés par le relecteur avec les dépôts (concordance, pas
rapprochement).

Autre point de la revue : un comparatif repris dans un dépôt ultérieur ne remplace jamais le dépôt disponible à la date
de décision — déjà garanti par la sélection, désormais testé sur Microsoft (`test_later_comparative_never_replaces_…`).

Tests : `tests/test_normalisation.py` réécrit (24 tests : propositions, rapprochement sur document FICTIF, falsifications,
3 émetteurs réels). Mutations : 15, toutes détectées (dont une après avoir rendu un test plus précis : le refus pour
copie altérée était aussi obtenu, plus tard, par l'audit ; le test exige désormais le bon motif). **204 tests.**

Points nécessitant une revue indépendante : règles R1/R2 d'edgar_v2 ; `parse_ixbrl`/`_ix_value` sur un vrai 10-K dès
qu'un document est disponible ; méthode d'établissement des catégories d'actions (humaine) pour réintroduire
shares_outstanding.

> Les sections V1.13 à V1.15 ci-dessous décrivent des normalisations **retirées** ; elles restent pour l'historique.

## V1.15 — Normalisation éprouvée sur trois émetteurs réels

Même règles edgar_v1, sans aucune adaptation : Microsoft (CIK 789019) et Alphabet (CIK 1652044) collectés le
28/09/2026 sur data.sec.gov, convertis puis normalisés.

| Émetteur | Documents | Faits convertis | Normalisés | Exclus | Contrôles (verify-trace, verify-normalisation, audit) |
|---|---|---|---|---|---|
| Apple | 44 | 15 068 | 337 | 0 | 0 / 0 / 0 |
| Microsoft | 24 | 11 179 | 210 | 0 | 0 / 0 / 0 |
| Alphabet | 13 | 6 333 | 52 | 26 (C1 : 4 titres cotés) | 0 / 0 / 0 |

- Chiffres d'affaires annuels sélectionnés : Microsoft exercice clos le 30/06/2025 = 281 724 M$, Alphabet 2024 =
  350 018 M$ (à comparer aux 10-K) ; tests `OtherRealIssuersTests`.
- **Indice pour D1** : Alphabet déclare ses actions de couverture par catégorie (fait ventilé) et ce concept est absent
  de son companyfacts ; cela suggère que companyfacts ne contient que des faits non ventilés (à confirmer dans la
  documentation SEC, inaccessible d'ici).
- C1 est prudente, peut-être trop : GOOGM et GOOGN sont vraisemblablement des titres de dette cotés, pas des actions ;
  la règle compte tout titre coté. Point de revue.
- Exemple d'application de la règle UTC : le 10-K d'Alphabet est accepté le 05/02/2026 à 02:56 UTC (04/02 au soir à
  New York) ; il n'est utilisable qu'à partir du 06/02.
- Exemples vérifiables regroupés dans `docs/EXEMPLE_NORMALISATION.md` (4 dépôts ; un test vérifie les tableaux).
- Décision : pas de chaînage du journal des saisies par empreintes (un auteur malveillant pourrait recalculer la
  chaîne) ; l'ancrage est l'historique git. Un horodatage externe serait nécessaire pour mieux faire.
- **209 tests.**

## V1.14 — Un fait normalisé faux ne passe plus inaperçu

Constat (auto-relecture) : sur la V1.13, un fait normalisé faux accompagné d'une saisie journalisée « cohérente »
(ex. chiffre d'affaires reclassé en total_assets, mappage modifié en conséquence, ou valeur multipliée avec une
transformation décrite) passait `verify-trace` et `audit-docs` à 0 : ces contrôles vérifient la forme et l'historique,
pas la conformité aux règles.

Correction : `tools/edgar_normalize.py verify-normalisation --raw … --audit … --regles …` refait, dans un dossier
temporaire, la conversion puis la normalisation avec **ces** règles, rejoue l'import et le rapprochement automatique
sur les mêmes copies locales, et compare chaque cellule de normalisation et de rapprochement ainsi que `concept_map`.
- cellule attribuée à l'outil mais différente des règles ⇒ **écart** ;
- cellule dont la dernière saisie est humaine ⇒ listée « saisie humaine hors règles (à relire) », jamais masquée ;
- l'auteur des saisies porte désormais l'empreinte du fichier de règles (`règles edgar_v1 sha256:f95d7e2287bb49a3`) :
  des règles modifiées sous le même nom de version sont détectées.

Le dossier Apple a été régénéré depuis une conversion neuve (mêmes 337 faits ; seul l'auteur des saisies change) :
`verify-normalisation` ⇒ 0 écart, 0 saisie humaine. Tests : 7 nouveaux (falsification du concept, de la valeur, d'un
rapprochement automatique, autre fichier de règles, saisie humaine listée, dossier Apple conforme). Mutations : 6,
toutes détectées. **206 tests.**

Limite : une saisie **humaine** fausse reste possible (elle est seulement listée) ; c'est le rôle de la relecture
indépendante. `www.sec.gov` reste bloqué (vérifié à nouveau) : aucun rapprochement réel.

## V1.13 — Normalisation EDGAR sur données réelles (travail autonome demandé par l'utilisateur)

Objectif : que la normalisation fonctionne sur les faits réels d'Apple, avec tests et exemples vérifiables, en restant
en simulation (aucun ordre, aucun courtier, aucun service payant). **Atteint pour la normalisation ; le rapprochement
avec le document d'origine est prêt et testé, mais n'a pas pu être exécuté sur un vrai document** (voir « Bloquant »).

### Ce qui a été fait

| Élément | Fichier | Résultat vérifiable |
|---|---|---|
| Règles versionnées (4 règles 1 → 1, inférences D1, X1, C1, T1, K1, liste de ce qui n'est volontairement pas normalisé) | `config/normalisation/edgar_v1.json` | — |
| Outil hors ligne `normalize` : chaque cellule passe par le journal des saisies ; écriture « tout ou rien » après `verify-trace` + `audit-docs` sur une copie ; précondition : dossier déjà vérifié ; idempotent | `tools/edgar_normalize.py` | Apple : **337 faits normalisés** (total_revenue 117, total_assets 88, shares_outstanding 132), 0 conflit, 0 écarté, 2 166 saisies ; relance : 0 saisie |
| Exclusion explicite `NON NORMALISÉ : motif` pour un fait d'un concept mappé non normalisé (conflit, catégorie…) ; l'audit l'accepte comme inconnue signalée, jamais en silence | `halal_sim/audit.py` | test du conflit K1 |
| `import-filing` : copie locale du document principal téléchargé à la main (nom vérifié, heure déclarée avec fuseau, SHA-256, journalisé) | `tools/edgar_normalize.py` | tests fixture |
| `reconcile-ixbrl` : lit le XBRL en ligne de la copie locale (contextes, unités, `ix:nonFraction`, échelle, signe, formats courants), ne retient que les faits de la même entité, même période, **sans segment**, compare à la valeur companyfacts ; remplace le contexte X1 par l'identifiant réel et renseigne `decimals` ; `reconciled = auto` avec note « AUTOMATIQUE … » | `tools/edgar_normalize.py` | 7 tests sur document XBRL en ligne FICTIF (concordance, écart de valeur, seul fait ventilé ⇒ D1 réfutée, autre entité, signe, copie altérée) |
| Audit : `reconciled = auto` exige une note « AUTOMATIQUE » et une copie locale ; verdict distinct « RAPPROCHEMENT AUTOMATIQUE … à relire » | `halal_sim/audit.py` | test |
| Sélection : utilisable si rapproché (`oui` ou `auto`), avec `Selection.reconciliation` | `halal_sim/selection.py` | tests |
| Exemples vérifiables (10-K 2025 et 10-Q T3 2025), régénérables ; un test vérifie qu'ils correspondent aux données | `docs/EXEMPLE_NORMALISATION.md`, `tools/exemple_normalisation.py` | test |

Tests : `tests/test_normalisation.py` (19, dont 5 sur le dossier Apple réel). **199 tests** au total. Mutations :
15 défauts réintroduits dans le nouveau code (K1, C1, D1, tout ou rien, précondition, segment, valeur, période,
entité, empreinte, signe, nom du document, note automatique, exclusion motivée, sélection), **tous détectés**.

### Décisions prises (réversibles, à relire)

1. **Correspondance 1 → 1 uniquement** : aucun agrégat ni calcul. `interest_bearing_debt`,
   `cash_and_interest_bearing_investments`, `non_compliant_revenue` et `market_cap` ne sont **pas** normalisés : leur
   périmètre est une décision du référentiel religieux (locations, qualification des placements, revenus illicites) ou
   exige un cours (source non établie).
2. `us-gaap:Revenues` (2018) et `us-gaap:SalesRevenueNet` (avant 2018) **non mappés** vers total_revenue : équivalence
   avec ASC 606 non établie. Conséquence : pas de chiffre d'affaires normalisé avant l'exercice 2018 d'Apple.
3. Deux concepts d'actions mappés vers `shares_outstanding` (page de couverture et bilan) : dates de mesure différentes,
   distinguées par la sélection à date exacte ; la convention de date pour la capitalisation reste ouverte.
4. **Inférences** faute d'accès au document : D1 (aucune dimension si une seule valeur brute par clé), X1 (contexte
   décrit par son contenu), C1 (catégorie unique si un seul titre coté). Elles sont écrites dans chaque justification
   et sont vérifiées ou réfutées par `reconcile-ixbrl` dès qu'une copie du document existe.
5. Rapprochement automatique distinct du rapprochement humain (`auto` ≠ `oui`) ; il prouve la **concordance des
   chiffres** avec la copie locale, pas le bon choix de concept.
6. L'auteur des saisies automatiques est l'outil (« edgar_normalize.py (règles edgar_v1, automatique) »), jamais une
   personne.

### Limites

- **Bloquant pour le rapprochement réel** : `www.sec.gov` (où sont les documents) reste bloqué par le réseau de
  l'environnement ; seul `data.sec.gov` est autorisé. Deux voies : ajouter `www.sec.gov` aux domaines autorisés, ou
  télécharger le document principal dans un navigateur (ex. `aapl-20250927.htm`) puis `import-filing`.
- `reconcile-ixbrl` n'a jamais tourné sur un vrai document SEC : formats `ixt` rares, `ix:continuation`,
  `xsi:nil`, faits imbriqués, grands documents (mémoire) non éprouvés. Les formats non pris en charge produisent un
  échec explicite, jamais une valeur.
- `decimals` reste inconnu tant que le document n'est pas rapproché.
- Un changement de version des règles ne « dé-normalise » pas les faits déjà normalisés : repartir d'une conversion
  neuve (`convert --remplacer`) pour appliquer une nouvelle version.
- Le journal est déclaratif ; l'empreinte d'une preuve ne prouve pas ce qu'elle dit.
- Rien n'est « utilisable » pour un ratio aujourd'hui : 0 fait rapproché ; et le référentiel n'est pas validé.

### Points nécessitant une revue indépendante

1. Les 4 règles et leurs justifications (`concept_map.csv`) : le concept choisi est-il le bon total pour le projet ?
2. L'inférence D1 : un fait companyfacts unique par clé est-il bien le total non ventilé ? (Réfutable par
   `reconcile-ixbrl`.)
3. L'inférence C1 pour Apple (une seule catégorie d'actions) et son usage pour d'autres émetteurs.
4. Décision 2 (concepts de revenu antérieurs à 2018) et décision 3 (deux mesures d'actions).
5. La lecture XBRL en ligne (`parse_ixbrl`, `_ix_value`) sur un vrai 10-K dès qu'il est disponible.
6. Comparer à la main les lignes de `docs/EXEMPLE_NORMALISATION.md` au 10-K 2025 (bilan, compte de résultat,
   page de couverture).

## Historique — revue n° 12

- **Cas reproduit** sur b86400b : `public_available_at` du 10-K 2025 fixée au 03/11/2025 sans preuve ⇒ fait retiré de la
  sélection du 01/11, mais 0 écart à `verify-trace` et 0 erreur à `audit-docs`.
- **Correction** : `journal_saisies.csv` (format dans `docs/AUDIT_DOCUMENTAIRE.md`). `verify-trace` rejoue le journal
  sur la reconversion : toute cellule humaine qui diffère de la conversion doit résulter d'une saisie journalisée
  (numérotation continue, auteur, horodatage avec fuseau et ordonné, ancienne valeur = valeur en vigueur, preuve).
  Une date de disponibilité exige un fichier du dossier avec empreinte SHA-256 vérifiée, ou une URL. Effacer, avancer
  ou modifier après coup une valeur journalisée est signalé. Les colonnes produites par la conversion ne se
  « saisissent » pas. Les lignes de `concept_map`, `activities` et `securities` sont couvertes.
- **Limite dite** : journal déclaratif (identité de l'auteur non prouvée ; contenu de la preuve non interprété).
- **verify-source rejouable** : la seconde copie SEC est dans `collecte/apple_controle/` (téléchargée le 28/09/2026 à
  11:22 UTC) : `verify-source --raw collecte/apple --fresh collecte/apple_controle --audit data/audit_edgar_apple`
  ⇒ 0 écart, 0 invérifiable.
- **Prix** : source « non établie » (`docs/NORMALISATION_RATIOS.md`).
- Tests `tests/test_review12.py` (11) ; le test de la V1.11 qui laissait passer les colonnes humaines est inversé.
  Mutations : 9 défauts réintroduits, tous détectés. **180 tests.**

## Historique — revue n° 11

Les deux défauts signalés ont été reproduits sur c48d19d (chiffre de l'émetteur 2 renvoyé pour l'émetteur 1 ; date
d'acceptation du 10-K 2025 avancée au 30/10 : 0 écart à `verify-trace`, 0 erreur à `audit-docs`), puis corrigés.

| Point | Correction | Test |
|---|---|---|
| Sélection sans émetteur | `select_fact(docs, facts, issuer_id, …)` : émetteur obligatoire (via le document porteur) ; devise obligatoire pour un fait monétaire normalisé | `test_review_case_other_issuer_is_never_returned`, `test_normalized_monetary_fact_requires_matching_currency` |
| Valeur publiée à l'origine | `Selection.original` (premier dépôt disponible) à côté de la valeur retenue ; une décision antérieure à une révision n'en voit jamais l'effet | `test_original_value_is_kept_next_to_the_revised_one` |
| `accepted_at` non contrôlé | `verify-trace` refait toute la conversion depuis les fichiers bruts et compare chaque colonne produite par la conversion (émetteurs, documents, faits), la trace et le journal ; lignes ajoutées ou supprimées signalées ; colonnes du travail humain (normalisation, rapprochement, copie locale, diffusion publique, rectificatif) non comparées | `test_review_case_moved_acceptance_date_is_detected`, `test_review_case_apple_10k_acceptance_moved_one_day_earlier`, `test_changed_form_issuer_or_removed_document_is_detected`, `test_human_columns_are_not_flagged` |
| Empreintes locales non indépendantes | `verify-source` compare le dossier à une copie **retéléchargée de la SEC** (`collect` vers un autre dossier) : dates d'acceptation, formulaires, fins de période, et présence identique de chaque fait tracé ; dépôt sorti de `filings.recent` = « invérifiable », jamais « conforme ». Exécuté pour de vrai sur Apple : 0 écart, 0 invérifiable ; la copie altérée est détectée | `VerifySourceTests` (4 cas, hors ligne) |

Limite restante : `verify-source` suppose que la SEC ne réécrit pas un dépôt passé ; il prouve la concordance avec la
SEC à la date du second téléchargement, pas l'exactitude économique des chiffres. Mutations : 9 défauts réintroduits,
tous détectés. **169 tests.**

Source de cours (question c) : Massive Stocks Basic (gratuit, `adjusted=false`, 2 ans d'historique, 5 appels/min)
demande un **compte et une clé API** : décision laissée à l'utilisateur ; rien n'a été créé. Règles de capitalisation
ajoutées à `docs/NORMALISATION_RATIOS.md`.

## Historique — revue n° 10 (collecte Apple)

| Recommandation | Fait | Test |
|---|---|---|
| `acceptanceDateTime` en UTC | Confirmé par le relecteur ; conservé en `+00:00`, `public_available_at` reste vide | — |
| Journal des exclusions par numéro d'accès et motif | `journal_conversion.json` : 28 dépôts, 10 067 faits (10-Q 5 737, 10-K 3 002, 8-K 1 118, 10-K/A 210 ; tous hors `filings.recent`), un pointeur d'exemple par dépôt ; comptage entrées brutes = retenus + fusionnés + écartés, sinon arrêt | `test_exclusions_are_logged_per_accession_with_reason`, `test_every_apple_fact_is_traced_to_its_raw_entry` |
| Conserver l'entrée JSON source | `trace_source.csv` : pointeur JSON (RFC 6901) vers l'entrée brute, empreinte SHA-256 de l'entrée, `fy`, `fp`, `frame` ; `verify-trace` recalcule valeur, accn, concept, unité, dates, formulaire | `test_trace_verifies_and_detects_tampering`, `test_units_containing_a_slash_round_trip`, `test_missing_trace_row_is_reported` |
| Sélection « période + dépôt disponible à la décision », avec rectificatif et comparatif | `halal_sim/selection.py` (règles dans `docs/NORMALISATION_RATIOS.md`) | 7 cas fictifs + 4 sur Apple dans `tests/test_review10.py` |
| Ordre de normalisation des ratios | `docs/NORMALISATION_RATIOS.md` ; les chiffres cités par le relecteur sont retrouvés dans les données (LongTermDebt 90 678 M = 12 350 + 78 328 ; CommercialPaper 7 979 M ; trésorerie 35 934 M ; actions 14 773 260 000 au 27/09 et 14 776 353 000 au 17/10 ; NonoperatingIncomeExpense −321 M) | — |

Défaut trouvé en chemin : la première version de la trace coupait les unités contenant « / » (`USD/shares`) ;
`verify-trace` l'a détecté (675 écarts), corrigé par l'échappement RFC 6901. Sur Apple : 15 068 faits, 0 écart.
Mutations : 9 défauts réintroduits (J+1, plus récent, début de période, UTC, ambiguïté, échappement, contrôle de
valeur, compte des exclusions, fait sans trace), tous détectés. **157 tests.**

## Historique — première collecte EDGAR réelle (Apple, CIK 320193)

Collecte faite le 2026-09-28 à 10:50 UTC par `collect` (accès à `data.sec.gov` ouvert par l'utilisateur ; l'identification
envoyée à la SEC n'est écrite nulle part dans le dépôt). Fichiers bruts et empreintes : `collecte/apple/` ; dossier converti :
`data/audit_edgar_apple/`.

- `convert` : 44 documents (10-K et 10-Q récents), 15 068 faits, 10 067 faits d'autres documents écartés, 0 doublon,
  0 dépôt retenu puis écarté ; historique incomplet signalé (1 fichier de dépôts anciens non collecté).
- `audit-docs` : **0 erreur bloquante**, 76 245 inconnues signalées, verdict **NON EXPLOITABLE** (aucun fait normalisé),
  comme prévu.
- Contrôle ponctuel : chiffre d'affaires exercice 2025 (10-K 0000320193-25-000079) = 416 161 000 000 USD, à rapprocher
  à la main du rapport d'origine.
- À vérifier par le relecteur : `acceptanceDateTime` de la SEC porte le suffixe `Z` ; est-ce vraiment de l'UTC ou de
  l'heure de New York mal étiquetée ? (valeurs observées : 10:01Z, soit 6 h 01 à New York.)

## Historique — référentiel tiré du document de fiqh de l'utilisateur

L'utilisateur a fourni son document « Actions, bourse et produits financiers en Islam : vérification et annotation de vos
notes de cours » (PDF, 19 p.). J'en ai tiré `config/rulesets/AAOIFI_SS21_document_utilisateur.json` :

- dette à intérêt ≤ 30 % de la capitalisation (AAOIFI SS 21 §3/4/2), dépôts à intérêt ≤ 30 % de la capitalisation
  (§3/4/3), revenus illicites ≤ 5 % du revenu total (§3/4/4), **tels que cités au § 5.1 du document** ; chaque seuil
  renvoie au paragraphe du document ;
- activités exclues par consensus selon le document (Synthèse A.1) ; tabac, armement, médias, hôtellerie : INCERTAIN
  (non traités par le document) ;
- avertissement de divergence affiché dans chaque rapport (Synthèse C.1 : l'OCI, Makka et la Lajna Dāʾima interdisent
  les sociétés « mêlées ») ;
- **non validé** : le document exige une validation par un sharia board nommé et signale des copies secondaires ; le
  moteur refuse donc les données réelles (seuls manquent `validated`, `validated_by`, `validated_on`) ;
- points ouverts listés dans `open_questions` et `docs/REFERENTIEL_ET_SOURCES.md` § 9 (états « vérifiés » §3/4/5,
  date de la capitalisation, filtre mālikite des actifs monétaires, purification, délai de cession, etc.).

Sur les données fictives, ce référentiel donne les mêmes résultats que la démo (aucun titre fictif entre les seuils 20/20/3 %
et 30/30/5 %).

## Historique — revue n° 9

Les 5 cas ont été reproduits sur 5751e76, corrigés et couverts par `tests/test_review9.py` ; chaque défaut réintroduit fait
échouer au moins un test (6 variantes, dont l'avertissement de divergence).

| Cas signalé | Correction | Test |
|---|---|---|
| Fait marqué `10-K/A`, déposé en 2026, attribué au 10-K de 2025 | `form` et `filed` de chaque fait doivent correspondre au dépôt de son numéro d'accès, sinon arrêt | `test_review_case_fact_form_or_filing_date_must_match_its_filing` |
| 10-K sans `reportDate` écarté en silence | Dépôt écarté nommé dans `selected_but_skipped` ; manifeste : périmètre exact (formulaires, retenus, écartés, rectificatifs à rattacher) | `test_review_case_selected_filing_without_report_date_is_named` |
| `collect` et `convert` écrasent sans prévenir | Refus d'écrire dans un dossier existant non vide sans `--remplacer` | `test_review_case_no_silent_overwrite` |
| Fait normalisé avec contexte vide ⇒ 0 erreur | Normalisation refusée sans contexte d'origine | `test_review_case_normalized_fact_without_context_is_refused` |
| `snapshot-db` sur `old?name.sqlite` : instantané vide et fichier `old` créé | URI construite depuis le chemin encodé (`Path.as_uri()`) ; testé avec `?`, `#`, `%`, espace et accent | `test_review_case_reserved_characters_in_path` |

Question 4 (historique) : le premier dossier est explicitement limité aux dépôts récents ; le manifeste le dit.

## Historique — collecte EDGAR sans identification : `import-files`

L'utilisateur préfère ne pas donner son adresse électronique, et sec.gov est inaccessible depuis l'environnement de
développement. Nouvelle voie : l'utilisateur télécharge les deux JSON dans son navigateur et les transmet ;
`import-files` les enregistre avec empreinte SHA-256 et heure de téléchargement **déclarée** (avec fuseau, jamais
inventée), sans aucune requête ; `convert` et `audit-docs` s'appliquent ensuite. Guide débutant : `docs/GUIDE_COLLECTE_EDGAR.md`.

## Ce qui fonctionne réellement (vérifié en lançant le code)

- Simulation de bout en bout (12 contrôles), avec `--ruleset` pour choisir le référentiel et `--db` pour la base.
- `audit-docs` sur l'exemple fictif : 0 erreur, verdict NON EXPLOITABLE.
- **204 tests**, tous au vert : test_audit 26, test_costs_and_data 9, test_edgar_tool 10, test_incertain_never_bought 5,
  test_lookahead 8, test_no_real_orders 8, test_review2 10, test_review3 12, test_review4 8, test_review5 9, test_review6 7,
  test_review9 9, test_review10 15, test_review11 12, test_review12 11, test_normalisation 24, test_ruleset_validation 10, test_screening 11.

## Limites connues (générales)

1. Données de simulation fictives ; référentiel réel non validé ; simulation sur données REEL refusée.
2. Exécutions reconstruites, non prouvées.
3. Collecte EDGAR éprouvée sur une seule société (Apple) ; companyfacts partiel ; dépôts récents seulement.
4. Le numérateur « dépôts à intérêt » doit exclure la trésorerie non rémunérée : à vérifier sur chaque donnée réelle.
5. Purification, zakāt, filtre mālikite des actifs monétaires : non codés (décisions du board).

## Questions pour le relecteur (anciennes)

0. (V1.10) La règle « dépôt le plus récemment disponible » est-elle la bonne pour un backtest, ou faut-il garder la
   valeur telle que publiée à l'origine pour certains usages ? `verify-trace` laisse-t-il passer une altération ?

1. Le référentiel `AAOIFI_SS21_document_utilisateur.json` reflète-t-il fidèlement le § 5.1 du document (seuils,
   dénominateurs, comparateur « ≤ », sources) ? Y manque-t-il une règle que le document présente comme consensuelle ?
2. La conversion EDGAR peut-elle encore perdre ou inventer une information, ou produire un dossier incohérent à 0 erreur ?
3. `import-files` (heure déclarée, empreinte, aucune requête) est-il une base honnête pour un premier dossier réel ?
