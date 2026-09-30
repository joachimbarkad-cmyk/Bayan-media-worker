# Instructions pour Claude Code

Ce dépôt contient deux produits indépendants :

- `worker.py` & co. : service vidéo Bayān (Python/FFmpeg), documenté dans `README.md`. Ne pas le modifier sans demande.
- `muraja/` : application de révision Murāja'a (Node 22 + TypeScript, React, SQLite). Voir `muraja/README.md`.

Protocole de travail et de revue avec Codex : **`docs/PROTOCOL.md`** (source unique, commune avec `AGENTS.md`).

À lire au démarrage : `docs/STATUS.md` (état de reprise), puis `docs/SPEC.md` et `docs/DECISIONS.md` selon le besoin.

Commandes : `cd muraja && npm test`, `npm run typecheck`, `npm run build`, `npm run e2e` ; revue : `make review ...` (voir le protocole).
