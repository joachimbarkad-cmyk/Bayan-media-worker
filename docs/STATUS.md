# État de reprise

_Mis à jour le 2026-09-30._

## Dernier jalon démontré

**Jalon 3 (IA connectée)** au-dessus du jalon 2, commit `484d2d1` sur `claude/codex-review-workflow-1br66x`.

- IA : connecteur MCP + OAuth pour le Claude/ChatGPT de chaque personne ; clé API personnelle chiffrée (Anthropic/OpenAI/Gemini). 29 tests API (OAuth complet, client MCP officiel, fausse clé rejetée par la vraie API Anthropic), E2E 17 étapes. Captures `docs/demo/desktop-08..10`.

- Mécanisme de revue Claude → Codex : `552379c` (11 tests avec faux Codex).
- Application `muraja/` : 21 tests API/CSV, typage OK, parcours E2E Chromium en 14 étapes (bureau + mobile, deux comptes). Captures : `docs/demo/`.
- Démonstration : données **fictives** (« Fiqh (démo) », PDF généré), aucune génération IA.

## Revue Codex

| Lot | SHA | Statut | Rapport |
|---|---|---|---|
| Lot 0 — revue Codex | `552379c` | **BLOCKED** (Codex non authentifié) | `docs/REVIEWS/2026-09-30-lot-0-revue-codex-552379c1aa89.md` |
| Lot 1 — parcours | `96d11d9` | **BLOCKED** (Codex non authentifié) | `docs/REVIEWS/2026-09-30-lot-1-parcours-96d11d942b62.md` |
| Lot 2 — IA connectée | `484d2d1` | **BLOCKED** (Codex non authentifié) | `docs/REVIEWS/2026-09-30-lot-2-ia-connectee-484d2d1c5bb3.md` |

Aucun lot n'est approuvé par Codex. Ne pas fusionner avant une revue `APPROVED` du SHA à livrer. Les commandes exactes à rejouer sont dans `docs/REVIEWS/pending/*/command.json`.

Relecture critique faite par Claude à défaut : deux défauts trouvés et corrigés avant `96d11d9` (une modification partielle d'une question ou des réglages réinjectait des valeurs par défaut Zod ; tests de non-régression ajoutés).

## Blocages

1. **Codex non exécutable dans l'environnement cloud** : Codex CLI 0.159.2 s'installe (`npm i -g @openai/codex`), mais
   - la politique réseau refuse `api.openai.com` et `auth.openai.com` (CONNECT 403) ;
   - aucune authentification Codex (`codex login status` → « Not logged in »).
   Voies possibles, au choix du propriétaire :
   - **Machine personnelle (recommandé par le document de cadrage)** : `npm i -g @openai/codex`, `codex login` (compte ChatGPT existant), puis `make review LOT=... BASE=... CRITERIA=...` dans ce dépôt.
   - **Environnement cloud** : autoriser `api.openai.com` et `auth.openai.com` (probablement aussi `chatgpt.com`, non vérifié) dans l'accès réseau de l'environnement, puis connexion `codex login --device-auth` à chaque nouveau conteneur. Une clé d'API OpenAI serait une facturation séparée : exclue sans accord (budget 0 €).
2. **Image Docker non construite** : pas de démon Docker ici. Le serveur de production (`npm start`) a été lancé et vérifié (index, routes SPA, 404 API, CSP).
3. **Tests du service vidéo** (`tests/test_worker.py`) non exécutables ici : FFmpeg absent. Code non modifié.
4. **Connexion Claude/ChatGPT non essayée en réel** : il faut une adresse HTTPS publique (`MURAJA_PUBLIC_URL`). Testée avec le client MCP officiel et un parcours OAuth simulé dans le navigateur. ChatGPT : offres et menus à confirmer (documentation OpenAI inaccessible ici).
5. **Génération réelle non essayée** : aucune clé API disponible (budget 0 €) ; seules la gestion d'une clé refusée (Anthropic) et un fournisseur simulé ont été testés. OpenAI et Gemini : code écrit d'après les types des SDK, non exécuté.
6. **Import NotebookLM** : CSV générique seulement ; il faut un vrai fichier de flashcards exporté pour tester la compatibilité.

## Prochaines actions

1. Dès que Codex est joignable : rejouer les revues des lots 0 et 1 ; corriger (2 cycles max) ; consigner.
2. Publier le site en HTTPS sans coût, puis connecter un vrai compte Claude (gratuit : 1 connecteur) pour valider le parcours de bout en bout.
3. Jalon 3 (suite) : mode Feynman (explication libre, puis comparaison guidée avec la fiche et les extraits), fiche générée depuis la sélection de pages, recherche dans la bibliothèque, « reformuler sans les choix » après un QCM réussi.
4. Jalon 4 : choisir un hébergement sans coût (machine personnelle + tunnel gratuit, ou offre gratuite vérifiée) ; ne rien activer de payant.
5. Tester l'import avec un vrai CSV NotebookLM et un vrai PDF arabe (texte, et scanné).
