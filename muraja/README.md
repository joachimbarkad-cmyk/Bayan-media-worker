# Murāja'a — application de révision

Bibliothèque de cours (PDF, texte), fiches, flashcards, QCM, questions ouvertes, révision espacée FSRS, cartes mentales, glossaire, imports CSV/JSON et export. Fonctionne sans aucune API payante : la génération automatique est désactivée par défaut et le site le dit.

## Lancer en local

Prérequis : Node.js ≥ 22.18.

```sh
cd muraja
npm ci
npm run build          # construit l'interface dans dist/
npm start              # http://127.0.0.1:8787
```

Développement : `npm run dev:server` et `npm run dev:web` (Vite, proxy vers l'API).

Variables : `MURAJA_DATA` (dossier des données, défaut `muraja/data`), `PORT`, `HOST`, `MURAJA_INVITE_CODE` (exigé à l'inscription si défini — recommandé dès que le site est accessible depuis Internet), `MURAJA_SECURE_COOKIES=1` derrière HTTPS.

Sauvegarde : copier le dossier `MURAJA_DATA` (base SQLite + fichiers). Chaque utilisateur peut aussi exporter ses données depuis Réglages.

## Docker

```sh
docker build -t muraja muraja/
docker run -p 127.0.0.1:8787:8787 -v muraja-data:/data -e MURAJA_INVITE_CODE=... muraja
```

## Vérifications

```sh
npm test            # tests API : isolation de deux comptes, PDF, imports, FSRS, fuseau, double clic, reprise
npm run typecheck
npm run build && npm run e2e   # parcours complet dans Chromium (bureau + mobile), captures dans e2e/screenshots
```

Spécification : `../docs/SPEC.md`. Format d'import : `../docs/IMPORT_FORMAT.md`. Protocole de revue : `../docs/PROTOCOL.md`.
