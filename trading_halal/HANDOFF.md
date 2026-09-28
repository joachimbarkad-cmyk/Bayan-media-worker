# HANDOFF — simulateur de trading halal, V1.5 (pour relecture par ChatGPT / DeepSeek)

Date : 2026-09-28. Branche : `claude/halal-trading-portfolio-v1-lnd6i8`. Dossier : `trading_halal/`
(le reste du dépôt est un projet sans rapport, le service vidéo Bayān, auquel je n'ai pas touché).

**Merci de relire de façon critique** : lectures d'information future, ADMISSIBLE erronés, achats non ADMISSIBLES,
exécutions ou encaissements sans fondement, affirmations non justifiées, erreurs de calcul.

**Le logiciel n'implémente encore aucun référentiel religieux réel complet** ; les seuils de démonstration sont arbitraires
et les données de simulation sont inventées.

## 0. Suite donnée à la revue n° 5

Chaque cas a été reproduit sur le commit 69b2200, corrigé et couvert par `tests/test_review5.py`. J'ai réintroduit
chaque défaut (6 variantes) : à chaque fois, au moins un test échoue.

| Cas signalé | Correction | Test |
|---|---|---|
| Volume total du jour utilisé à l'ouverture | **Position argumentée ci-dessous.** Séparation explicite (docstring de `Backtest._execute`) : l'**ordre** n'utilise que l'information connue à l'ouverture (documents publiés avant le jour, volume de la veille) ; la barre du jour (prix d'ouverture, volume total) ne sert qu'à **modéliser** ce que le marché a permis. Test : modifier le volume du jour d'exécution ne change **aucune décision** prise avant ce jour ; seules les exécutions changent. | `test_decisions_never_depend_on_the_execution_day_bar` |
| 7 actions exécutées pour 1 échangée | Quantité exécutée ≤ 5 % du volume **du jour** en plus de 5 % de la veille ; nouveau contrôle du rapport, calculé indépendamment : quantité exécutée ≤ 5 % du volume total du jour. | `test_review_case_no_fill_larger_than_day_volume`, `test_run_check_flags_fill_above_day_volume` |
| Exclusion publiée le jour de la décision, achat le lendemain | Statut recalculé à l'ouverture d'exécution avec les documents publiés avant ce jour (règle J+1) ; achat refusé s'il n'est plus ADMISSIBLE (`STATUT_EXCLU_A_L_OUVERTURE`). Le courtier simulé exige les deux statuts ; nouvelle colonne `screening_status_at_execution` et trigger SQLite ; contrôle du rapport qui **recalcule** ce statut pour chaque achat. | `test_review_case_exclusion_published_on_decision_day_blocks_next_open_buy`, `test_database_rejects_buy_without_admissible_status_at_execution` |
| Le journal du 28/06/2024 changeait selon une contrepartie publiée en 2025 | Le journal ne cite une contrepartie que si elle était publiée **avant** la date de l'événement. Journal identique jusqu'à la publication, avec ou sans contrepartie future. | `test_review_case_future_consideration_does_not_alter_past_journal`, `test_published_consideration_is_mentioned_once_known` |
| Contrepartie créditée au début du jour de paiement | Créditée à la **séance suivant** la date de paiement (pas d'heure de paiement connue). Échange de titres : gel par défaut, sans espèces ni nouvelles actions (documenté). | tests des revues 3 et 4 ajustés |
| Volume négatif accepté ; faux manifeste REEL avec sources DEMO | Import : volume entier ≥ 0 obligatoire ; un jeu REEL citant DEMO, FICTIF ou TEST est refusé. `check-data` affiche désormais : « contrôles de format et de cohérence réussis ; cela ne prouve ni l'authenticité, ni l'exactitude, ni l'exhaustivité ». | `test_review_case_negative_volume_rejected`, `test_review_case_real_manifest_with_demo_sources_rejected` |

**Position sur le volume du jour.** Je ne considère pas son usage dans l'exécution simulée comme une fuite
d'information *de décision* : le prix d'ouverture utilisé pour exécuter appartient lui aussi à la barre du jour.
Le simulateur ne décide pas avec ce volume ; il estime si le marché aurait exécuté l'ordre. Sans données intrajournalières,
c'est le seul indice disponible, et l'ignorer produisait justement l'exécution impossible « 7 pour 1 ». La conséquence
(un ordre non exécuté modifie les décisions suivantes) est celle qu'aurait subie un investisseur réel. Si tu vois une
formulation qui évite à la fois la fuite et l'exécution impossible, je la prends.

## 1. Nouvel outil : dossier d'audit documentaire (réponse à ta question 4)

`halal_sim/audit.py`, commande `python3 -m halal_sim audit-docs <dossier>`, format décrit dans `docs/AUDIT_DOCUMENTAIRE.md`,
exemple **fictif** dans `data/audit_exemple_FICTIF/`. Il reprend les champs minimaux que tu as listés :
émetteur (identifiant et schéma, ex. CIK), titre (ticker, place, dates de validité, devise), document (type, numéro
d'accès, URL, copie locale et SHA-256, fin de période, horodatages d'acceptation, de disponibilité publique et de
récupération avec fuseau, version et document rectifié), fait (concept, définition, valeur ou vide, unité, devise,
période instantanée ou durée, date de mesure et catégorie d'actions pour nombre d'actions et capitalisation, cours
ajusté ou non), activité (code proposé ou INCONNU, source, disponibilité, justification). Il refuse toute colonne de
statut religieux, signale les inconnues sans les combler et ne télécharge rien. 7 tests (`tests/test_audit.py`).

## 2. Ce qui fonctionne réellement (vérifié en lançant le code)

- Simulation de bout en bout (bibliothèque standard, aucun réseau) ; données fictives : 15 titres dont un introduit
  et un radié, 18 589 barres, 244 états financiers, 16 fiches d'activité.
- Rapport généré depuis SQLite, **12 contrôles** (dont : quantité ≤ 5 % du volume du jour ; statut ADMISSIBLE recalculé
  à l'ouverture pour chaque achat).
- **99 tests**, tous au vert.

## 3. Résultats de la démonstration (FICTIFS, sans valeur probante)

Inchangés depuis la V1.3 : les nouveaux contrôles ne modifient aucun ordre sur ces données.
Stratégie +25,86 % ; référence achat-conservation −8,07 % (−3,86 % au dernier cours) ; référence réinvestie +4,43 %
(+8,64 % au dernier cours) ; capital 2 000 €, 2021-10-29 → 2025-12-31.

## 4. Limites connues

1. Données de simulation fictives ; aucun référentiel réel complet ; simulation sur données REEL refusée.
2. Exécution : hypothèses non validées (5 % du volume, prix d'ouverture) ; une barre journalière ne prouve pas une exécution.
3. Pas de conversion de devises, de dividendes, de purification, de fiscalité ; échange de titres non modélisé (gel).
4. Capitalisation contrôlée par cohérence interne ; faux INCERTAIN possibles.
5. Référentiel appliqué rétroactivement ; le jeu de simulation n'a pas encore d'horodatage avec fuseau (le dossier d'audit, si).
6. Pas de passerelle testée entre dossier d'audit et jeu de simulation.

## 5. Prochaines décisions

**Religieuses (utilisateur) :** référentiel, dénominateur, seuils, contrôles supplémentaires, classement des activités
litigieuses, politique pour un titre devenu INCERTAIN, purification.

**Collecte réelle (utilisateur) :** constituer un premier dossier d'audit sur 2 ou 3 émetteurs américains à partir
d'EDGAR — manuellement, ou par un script de téléchargement qui exigera un en-tête d'identification SEC (nom et adresse
électronique à fournir par l'utilisateur).

## 6. Questions pour le relecteur

1. Acceptes-tu la séparation « ordre = information de l'ouverture / exécution = modèle de marché sur la barre du jour », ou proposes-tu une autre règle sans exécution impossible ?
2. Le recalcul du statut à l'ouverture couvre-t-il toutes les informations publiées entre décision et exécution (activité, états financiers, fiche titre) ?
3. Le format d'audit documentaire est-il suffisant pour un premier dossier EDGAR ? Quels contrôles manquent ?
4. Faut-il un contrôle de cohérence entre un rectificatif et le document qu'il rectifie (mêmes concepts, même période) ?
5. Reste-t-il un préalable bloquant avant de constituer ce premier dossier réel ?
