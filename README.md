# Service vidéo Bayān

Ce service complète le studio hébergé : yt-dlp récupère les sous-titres YouTube (arabe manuel avant automatique), Whisper transcrit les fichiers qui en ont besoin, l’API Responses traduit avec contexte et glossaire, FFmpeg incruste les sous-titres dans un MP4 H.264/AAC.

## Installation

1. Installer Docker et Docker Compose sur un serveur Linux avec une adresse HTTPS. Pour des vidéos longues, prévoir au moins 2 cœurs, 4 Go de RAM et assez de disque pour les originaux et rendus. Les frais de serveur et d’API sont à la charge de l’utilisateur.
2. Dans ce dossier, copier `.env.example` en `.env`. Générer un jeton aléatoire avec `python -c "import secrets; print(secrets.token_urlsafe(32))"`, puis renseigner `BAYAN_TOKEN` et `OPENAI_API_KEY` dans `.env`. Ne pas publier ce fichier. Le jeton du service doit avoir au moins 24 caractères.
3. Exécuter `docker compose up -d --build`. Le port 8080 est lié à 127.0.0.1 ; le conteneur tourne sous un utilisateur non privilégié.
4. Placer un reverse proxy HTTPS devant `127.0.0.1:8080`. Autoriser les envois vidéo jusqu’à 8 Go, désactiver le buffering des requêtes et prévoir un timeout de 10 minutes pour le transfert. Les jobs sont asynchrones : leur calcul continue après la réponse HTTP.
5. Dans Bayān → Réglages, renseigner l’adresse HTTPS et le `BAYAN_TOKEN`, puis cliquer sur « Enregistrer et tester ». La clé OpenAI reste sur le service vidéo ; elle n’est pas envoyée au navigateur.

Exemple de configuration Nginx, à compléter avec la configuration TLS de votre domaine :

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_http_version 1.1;
    proxy_request_buffering off;
    proxy_buffering off;
    client_max_body_size 8G;
    proxy_read_timeout 600s;
    proxy_send_timeout 600s;
}
```

## Fonctionnement et protection

- Une file SQLite sur le volume `bayan-data` conserve les tâches et les résultats partiels. Un seul calcul vidéo à la fois limite la pression sur le serveur.
- Les uploads sont écrits par blocs sur disque ; les vidéos ne sont pas chargées intégralement en mémoire.
- Une tâche interrompue par un redémarrage devient « Échec » ; elle n’est pas relancée à votre insu avec des frais d’API supplémentaires.
- L’application présente les nouvelles traductions comme des propositions. Une confirmation protège les corrections humaines et les projets modifiés pendant le traitement.
- Les sous-titres YouTube récupérés, les réponses de transcription et les rendus sont conservés dans le volume. Sauvegarder ce volume et surveiller son occupation. La suppression d’un projet dans le studio supprime ses données D1/R2 ; les copies du service doivent être supprimées séparément par son administrateur.
- `TRANSLATION_MODEL` est configurable ; valeur initiale : `gpt-4.1`. Transcription : `whisper-1` avec timestamps de segments et mots. Les audios sont traités par tranches de 8 minutes ; les jonctions méritent une relecture.
- Il n’y a pas de contournement des vidéos privées ou des contrôles de YouTube. Si YouTube refuse la récupération, importer votre fichier vidéo ou SRT. `YOUTUBE_COOKIES_FILE` peut pointer vers un fichier de cookies de votre compte autorisé sur le service ; ne jamais le fournir dans le studio ni le versionner.
- L’export conserve la résolution (ou la réduit à 1080p/720p maximum), la cadence et le contenu audio. H.264/AAC impliquent un réencodage. Le poids du rendu est fourni après calcul ; il n’est pas estimé arbitrairement avant.
- L’aperçu CSS approche le rendu ASS, mais des différences de police ou de disposition peuvent exister. Le MP4 est le résultat de référence.

## Vérification après connexion

Importer une courte vidéo arabe que vous êtes autorisé à traiter. Vérifier les étapes de récupération/transcription, la traduction, la correction d’un segment, la sauvegarde après rechargement et les deux exports SRT et MP4. Le test local inclus vérifie un vrai rendu vidéo et les réponses d’erreur ; il ne remplace pas ce test avec les services externes actifs.

## Références d’implémentation

- [Transcription et timestamps OpenAI](https://developers.openai.com/api/docs/guides/speech-to-text)
- [Sorties structurées OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Filtre subtitles/ASS de FFmpeg](https://ffmpeg.org/ffmpeg-filters.html#ass)


## Déploiement Railway

Un volume persistant doit être monté sur `/data`. Le démarrage prépare ses droits puis exécute le service avec l’utilisateur non privilégié `bayan` (UID 10001). La sonde `/ready` ne révèle aucune configuration. Toutes les routes métier, y compris `/health`, exigent la clé de connexion. Configurer `BAYAN_TOKEN` et `OPENAI_API_KEY` uniquement dans les variables du service, jamais dans GitHub.
