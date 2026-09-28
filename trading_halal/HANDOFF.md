# HANDOFF — simulateur de trading halal, V1.9 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, contrôles d'audit
contournables, informations inventées ou perdues par la conversion, opérations destructives, **fidélité du référentiel
au document de fiqh fourni par l'utilisateur**.

## 0. Nouveau : référentiel tiré du document de fiqh de l'utilisateur

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

## 1. Suite donnée à la revue n° 9

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

## 2. Collecte EDGAR sans identification : `import-files`

L'utilisateur préfère ne pas donner son adresse électronique, et sec.gov est inaccessible depuis l'environnement de
développement. Nouvelle voie : l'utilisateur télécharge les deux JSON dans son navigateur et les transmet ;
`import-files` les enregistre avec empreinte SHA-256 et heure de téléchargement **déclarée** (avec fuseau, jamais
inventée), sans aucune requête ; `convert` et `audit-docs` s'appliquent ensuite. Guide débutant : `docs/GUIDE_COLLECTE_EDGAR.md`.

## 3. Ce qui fonctionne réellement (vérifié en lançant le code)

- Simulation de bout en bout (12 contrôles), avec `--ruleset` pour choisir le référentiel et `--db` pour la base.
- `audit-docs` sur l'exemple fictif : 0 erreur, verdict NON EXPLOITABLE.
- **142 tests**, tous au vert : test_audit 26, test_costs_and_data 9, test_edgar_tool 10, test_incertain_never_bought 5,
  test_lookahead 8, test_no_real_orders 8, test_review2 10, test_review3 12, test_review4 8, test_review5 9, test_review6 7,
  test_review9 9, test_ruleset_validation 10, test_screening 11.

## 4. Limites connues

1. Données de simulation fictives ; référentiel réel non validé ; simulation sur données REEL refusée.
2. Exécutions reconstruites, non prouvées.
3. Collecte EDGAR non éprouvée sur de vraies réponses SEC ; companyfacts partiel ; dépôts récents seulement.
4. Le numérateur « dépôts à intérêt » doit exclure la trésorerie non rémunérée : à vérifier sur chaque donnée réelle.
5. Purification, zakāt, filtre mālikite des actifs monétaires : non codés (décisions du board).

## 5. Questions pour le relecteur

1. Le référentiel `AAOIFI_SS21_document_utilisateur.json` reflète-t-il fidèlement le § 5.1 du document (seuils,
   dénominateurs, comparateur « ≤ », sources) ? Y manque-t-il une règle que le document présente comme consensuelle ?
2. La conversion EDGAR peut-elle encore perdre ou inventer une information, ou produire un dossier incohérent à 0 erreur ?
3. `import-files` (heure déclarée, empreinte, aucune requête) est-il une base honnête pour un premier dossier réel ?
