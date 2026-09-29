# Fiche de validation du filtrage religieux (à faire relire et signer)

Projet : simulateur de trading halal, **en simulation uniquement** (aucun courtier, aucun ordre réel).
Référentiel concerné : `config/rulesets/AAOIFI_SS21_document_utilisateur.json` (état : **NON VALIDÉ**).
Version de la fiche : V1.24, 29/09/2026.

## À qui s'adresse cette fiche

À une personne qualifiée en fiqh des transactions (muʿāmalāt) : un sharia board, un comité chariatique ou un mufti.
Le document de fiqh de l'utilisateur recommande un avis écrit (Synthèse D) et, pour le filtre des actifs monétaires, un
mufti mālikite (§ 7). **L'assistant qui a écrit le logiciel n'a aucune qualité pour valider ces points** : les
réglages actuels sont des propositions tirées du document de l'utilisateur, pas des avis religieux.

Pour chaque décision : lire la source et le comportement actuel, cocher **une** case, et écrire la modification si
la case « Modifié » est cochée. Une décision « Refusé » bloque l'usage du référentiel tant que le logiciel n'a pas été
corrigé selon l'avis donné (la décision passe alors à « Modifié »).

Sources citées :
- « Document » : le document de l'utilisateur, *Actions, bourse et produits financiers en Islam : vérification et
  annotation de vos notes de cours* (PDF, 19 pages, reçu le 28/09/2026). Il cite lui-même des copies secondaires de la
  norme AAOIFI n° 21. **Le texte officiel de la norme n'a pas été lu** (site de l'AAOIFI inaccessible) : le
  relecteur est invité à vérifier les paragraphes sur l'édition imprimée.
- Les numéros « 3/4/x » renvoient à la norme AAOIFI n° 21 (*Financial Paper — Shares and Bonds*) telle que citée par
  le document.

---

## Critères financiers

### D01 — Seuils 30 % / 30 % / 5 %

- **Source** : Document § 5.1, citant AAOIFI SS 21 §3/4/2, 3/4/3 et 3/4/4. Divergence sur le seuil (30 % ou 33 %) :
  Document, Synthèse C.2.
- **Comportement actuel** : un titre est EXCLU si une des trois limites est dépassée : emprunts à intérêt ≤ 30 % ;
  dépôts à intérêt ≤ 30 % ; revenus illicites ≤ 5 %.
- [ ] Validé  [ ] Modifié  [ ] Refusé — Modification / commentaire : ……………………………………

### D02 — Base des deux premiers ratios : capitalisation boursière

- **Source** : Document § 5.1 (« market capitalization ») ; divergence capitalisation / total de l'actif : Synthèse C.2.
- **Comportement actuel** : la capitalisation boursière ponctuelle (pas de moyenne sur 24 ou 36 mois).
- [ ] Validé  [ ] Modifié  [ ] Refusé — Modification / commentaire : ……………………………………

### D03 — Dénominateur du ratio de revenus illicites : revenu total déclaré

- **Source** : Document, lignes 270-271 (« 5 % du revenu total, quelle que soit leur source ») ; AAOIFI §3/4/4.
- **Comportement actuel** (décision **provisoire** de l'assistant, 29/09/2026) : le revenu total déclaré par la
  société, toutes sources confondues. Si ce total n'est pas établi de façon prouvée, le titre est INCERTAIN (donc
  jamais acheté). Les revenus nets des charges d'intérêts ne sont jamais utilisés.
- [ ] Validé  [ ] Modifié  [ ] Refusé — Modification / commentaire : ……………………………………

### D04 — Périmètre des emprunts à intérêt

- **Source** : AAOIFI §3/4/2 (Document § 5.1) ; le document ne détaille pas le périmètre.
- **Comportement actuel** : **non codé**. Question : faut-il compter les dettes de location (leasing), les billets
  de trésorerie, les emprunts à taux zéro, les dettes d'une filiale financière (ex. Ford Credit) ?
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D05 — Périmètre des dépôts et placements à intérêt

- **Source** : AAOIFI §3/4/3 (Document § 5.1).
- **Comportement actuel** : **non codé**. Le logiciel refuse de prendre toute la trésorerie comme dépôts à intérêt.
  Question : quels postes comptent (comptes rémunérés, dépôts à terme, obligations, fonds monétaires) ?
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D06 — Revenus illicites : ce qui est compté

- **Source** : AAOIFI §3/4/4 (« intérêts perçus compris », Document § 5.1).
- **Comportement actuel** : **non codé**. Ni le solde financier net, ni un zéro par défaut ne sont acceptés.
  Question : intérêts perçus, et quelles autres sources (ventes d'alcool marginales, etc.) ?
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D07 — Date de la capitalisation boursière

- **Source** : non précisée par le Document.
- **Comportement actuel** : question ouverte. Le logiciel interdit seulement d'utiliser une information publiée
  après la date de décision.
- Proposition : [ ] fin de l'exercice des comptes  [ ] date de décision  [ ] moyenne sur …… mois
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D10 — États financiers vérifiés, âge maximal de 200 jours

- **Source** : AAOIFI §3/4/5 (« dernier bilan ou état financier vérifié », Document § 5.1). Les 200 jours sont un
  **choix technique** du projet, pas une règle de l'AAOIFI.
- **Comportement actuel** : les derniers chiffres publiés avant la date de décision, audités ou non (trimestriels
  non audités compris) ; au-delà de 200 jours, le titre est INCERTAIN.
- Question : faut-il n'utiliser que les comptes annuels audités ?
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D13 — Filtre mālikite des actifs monétaires

- **Source** : Document § 7 (règle de l'accessoire au tiers, tabaʿ ; « à faire valider par un mufti mālikite ») ;
  Synthèse C.3.
- **Comportement actuel** : **non codé**.
- Proposition : [ ] liquidités + créances ≤ ⅔ du total de l'actif  [ ] actifs réels > 50 %  [ ] pas de filtre
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D17 — Sociétés à dominante de liquidités

- **Source** : Document, page sur le qabḍ (AAOIFI 3/17, règles du ṣarf).
- **Comportement actuel** : **non traité** (lié à D13).
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

## Activités

### D08 — Classement des activités

- **Source** : Document, Synthèse A.1 et § 3.1 (OCI 63 (1/7), Makka 1415 H, AAOIFI §3/4/1).
- **Comportement actuel** : EXCLU pour la banque et l'assurance conventionnelles, l'alcool, le porc, les jeux de
  hasard et le divertissement pour adultes. ADMISSIBLE a priori pour logiciel, santé, industrie, transport,
  télécoms, distribution, énergie et chimie (sous réserve des ratios). Toute activité non classée donne INCERTAIN.
- [ ] Validé  [ ] Modifié  [ ] Refusé — Modification / commentaire : ……………………………………

### D09 — Tabac, armement, médias et divertissement, hôtellerie et loisirs

- **Source** : non traités par le Document.
- **Comportement actuel** : INCERTAIN (jamais acheté ; vendu s'il est détenu).
- Tabac : [ ] EXCLU  [ ] ADMISSIBLE sous ratios  [ ] INCERTAIN
- Armement : [ ] EXCLU  [ ] ADMISSIBLE sous ratios  [ ] INCERTAIN
- Médias et divertissement : [ ] EXCLU  [ ] ADMISSIBLE sous ratios  [ ] INCERTAIN
- Hôtellerie et loisirs : [ ] EXCLU  [ ] ADMISSIBLE sous ratios  [ ] INCERTAIN
- [ ] Validé  [ ] Modifié  [ ] Refusé — Commentaire : ……………………………………

## Principe et pratique

### D14 — Avis permissif retenu

- **Source** : Document § 3.3 et Synthèse C.1. Les Académies de fiqh de l'OCI (rés. 63 (1/7), 1992) et de Makka
  (14e session, 1415 H) ainsi que la Lajna Dāʾima interdisent en principe les sociétés « mêlées » ; l'AAOIFI, l'ECFR
  et les comités chariatiques les permettent sous conditions.
- **Comportement actuel** : le projet suit l'avis permissif et l'annonce dans chaque rapport.
- [ ] Validé  [ ] Modifié  [ ] Refusé — Commentaire : ……………………………………

### D11 — Titre détenu qui devient EXCLU ou INCERTAIN

- **Source** : Document, Synthèse D (« règles de sortie… délai de cession »).
- **Comportement actuel** : vente à la décision suivante dans les deux cas (`on_exclu: SELL`,
  `on_incertain: SELL`). Un INCERTAIN dû à une simple donnée manquante entraîne aussi une vente.
- Délai de cession accepté : …………  INCERTAIN pour donnée manquante : [ ] vendre  [ ] conserver sans renforcer
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D12 — Purification

- **Source** : Document § 8 : méthode AAOIFI 3/4/6/4 ; détenteur en fin de période (3/4/6/1) ou prorata des jours
  de détention (FCNA) ; plus-values : divergence (Taqī ʿUthmānī, ISRA-Bloomberg). Synthèse C.4 et D.
- **Comportement actuel** : **non codée**.
- Méthode : [ ] AAOIFI, détenteur en fin de période  [ ] prorata FCNA  [ ] autre : …………
- Plus-values : [ ] à purifier  [ ] non   —   Destination des sommes : ……………………
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D15 — Revente avant règlement-livraison

- **Source** : Document, page sur le qabḍ (OCI 53 (4/6) ; AAOIFI 3/2) : zone grise signalée.
- **Comportement actuel** : la simulation décide une fois par mois ; elle ne revend jamais un titre avant son
  règlement.
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

### D16 — Fréquence du filtrage

- **Source** : Document, Synthèse D (« fréquence »).
- **Comportement actuel** : filtrage à chaque décision mensuelle (fin de mois), avec les derniers chiffres publiés
  avant cette date.
- [ ] Validé  [ ] Modifié  [ ] Refusé — Réponse : ……………………………………

---

## Hors périmètre de la V1 (pour information)

Choix du courtier (prêt de titres, intérêts sur les liquidités, compte sans marge), ETF, ṣukūk, cryptomonnaies,
zakāt : Document, Synthèse D. Le projet ne se connecte à aucun courtier et ne traite que des actions.

## Signature

| Nom | Qualification (formation, institution, madhhab) | Date | Signature |
|---|---|---|---|
| | | | |

Avis général : ……………………………………………………………………………………

---

## Après la signature (partie technique, à faire par l'utilisateur ou l'assistant)

1. Numériser la fiche signée et l'enregistrer dans le projet, par exemple `docs/validation/fiche_signee.pdf`.
2. Reporter **fidèlement** chaque réponse dans le référentiel et corriger le logiciel selon les « Modifié ».
3. Remplir dans le référentiel : `validated_by`, `validated_on`, puis `validation_record` :

   ```json
   "validation_record": {
     "document": "docs/validation/fiche_signee.pdf",
     "sha256": "<empreinte du fichier>",
     "decisions": {"D01": {"reponse": "VALIDE"}, "D03": {"reponse": "MODIFIE", "modification": "…"}}
   }
   ```

   Seulement ensuite : `validated: true`.
4. Le logiciel refuse les données réelles si : la fiche est absente ou modifiée après coup (empreinte différente) ;
   une décision D01 à D17 manque ou est « Refusé » ; une modification n'est pas écrite. Il **ne peut pas** vérifier
   que la signature est authentique, ni que les réponses ont été correctement reportées : cette relecture reste
   humaine.
