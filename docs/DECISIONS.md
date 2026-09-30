# Décisions techniques

| Date | Décision | Raison / conséquence |
|---|---|---|
| 2026-09-30 | L'application de révision vit dans `muraja/`, à côté du service vidéo Bayān, sans le modifier. | Un seul dépôt accessible ; les deux produits restent indépendants (dépendances, Docker, tests). |
| 2026-09-30 | Node 22 (≥ 22.18) + TypeScript exécuté directement par Node (effacement des types), sans étape de compilation serveur. | Moins d'outillage. Contrainte : syntaxe TS « effaçable » uniquement (`erasableSyntaxOnly`). |
| 2026-09-30 | Fastify 5, `@fastify/multipart`, `@fastify/cookie`, `@fastify/static` ; validation Zod 4. | Bibliothèques maintenues ; validation stricte aux frontières. |
| 2026-09-30 | SQLite via `node:sqlite` (intégré à Node), fichier unique dans `MURAJA_DATA`. | Aucune dépendance native, sauvegarde = copie d'un dossier. Risque : module marqué expérimental par Node ; l'accès est concentré dans `server/db.ts` pour pouvoir passer à `better-sqlite3` si besoin. |
| 2026-09-30 | FSRS via `ts-fsrs` 5.x (FSRS v6), paramètres par compte ; aucun calendrier maison. | Exigence du cahier des charges. |
| 2026-09-30 | Extraction PDF via `pdfjs-dist` 6 (build legacy) côté serveur, page par page. | Numéros de page fiables ; détection des scans. |
| 2026-09-30 | React 19 + Vite 8 ; routeur par hash écrit à la main (≈ 20 lignes) au lieu de React Router 8. | Éviter de dépendre d'une API majeure récente non vérifiée ; routes simples. |
| 2026-09-30 | CSV parsé côté navigateur (PapaParse) pour l'aperçu et la correspondance ; lignes validées côté serveur. | Aperçu immédiat ; le serveur reste l'autorité. |
| 2026-09-30 | Comptes locaux (e-mail + mot de passe scrypt), pas de fournisseur d'identité externe. | Budget nul, pas de service tiers. |
| 2026-09-30 | Revue Codex : `codex exec` dans un worktree détaché, `--output-schema`, `--output-last-message`, sandbox `workspace-write` limitée au worktree jetable, environnement Claude retiré. | Revue du SHA exact sans toucher au checkout principal. |
| 2026-09-30 | Nom de travail « Murāja'a » (مراجعة, « révision »). | Identité propre ; modifiable. |
| 2026-09-30 | « IA intégrée » sans coût pour le site = connecteur MCP + OAuth que chaque personne ajoute à SON Claude (toutes offres, 1 connecteur en gratuit) ou ChatGPT (mode développeur, offres payantes, non testé). | Seule voie officielle pour utiliser un abonnement personnel : un abonnement Claude.ai/ChatGPT ne peut pas être appelé par un site tiers ; NotebookLM n'a pas d'API personnelle. |
| 2026-09-30 | OAuth : enregistrement dynamique (DCR) seulement, pas de Client ID Metadata Document. | Claude revient à DCR si CIMD n'est pas annoncé (documentation Claude « Authentication for connectors »). CIMD possible plus tard. |
| 2026-09-30 | Clés API personnelles facultatives, chiffrées (AES-256-GCM, clé serveur `MURAJA_SECRET_KEY`), 40 générations/jour. | Boutons intégrés sans facturer le site ; budget de la personne protégé. |
| 2026-09-30 | Modèle Anthropic par défaut `claude-opus-5-5` (choix modifiable : Sonnet 5.5, Haiku 4.5) ; OpenAI/Gemini : modèle choisi dans la liste renvoyée par la clé. | Pas de nom de modèle OpenAI/Gemini deviné : documentation de ces fournisseurs inaccessible depuis l'environnement. |
