# Bayān — Service vidéo gratuit par défaut

Service Python/FFmpeg du studio Bayān. Il récupère les sous-titres arabes YouTube, conserve les timecodes et produit des MP4 sous-titrés. L’import se termine **sans appeler une API de traduction**. La traduction gratuite passe par le bouton **Traduire avec ChatGPT** du studio : copier la demande, coller la réponse JSON, appliquer et relire.

## Utilisation du studio

1. Importer une URL YouTube autorisée ou une vidéo de moins de 100 Mo.
2. Récupérer l’arabe. Si YouTube ne fournit pas de sous-titres exploitables, importer un fichier SRT/VTT (par exemple exporté de Soniox), ou utiliser le moteur local ci-dessous.
3. Traduire avec ChatGPT par lots. Aucun envoi automatique et aucune clé API ; les limites de votre abonnement ChatGPT restent applicables.
4. Relire puis exporter SRT, VTT, ASS ou lancer le rendu MP4. Télécharger le MP4 dans les 24 h ; on peut le régénérer depuis le projet.

YouTube peut refuser les téléchargements depuis certains hébergements. Importer le fichier original constitue alors le parcours pris en charge. Un essai d’hébergement n’est pas une garantie d’hébergement gratuit permanent.

## Démarrage Docker

Créer `.env` depuis `.env.example`, définir un `BAYAN_TOKEN` aléatoire d’au moins 24 caractères, puis :

```sh
docker compose up -d --build
```

Le port 8080 est exposé sur la boucle locale uniquement. Pour le studio hébergé, utiliser une adresse HTTPS existante avec un reverse proxy prenant en charge les uploads de 100 Mo et les réponses vidéo longues. Renseigner l’URL et le jeton dans Réglages. Ne jamais publier le jeton. Aucun service payant n’est nécessaire au fonctionnement du code, mais il faut disposer d’une machine et d’un accès réseau adaptés.

## Transcription locale gratuite (option ordinateur)

```sh
docker compose -f compose.local.yaml up -d --build
```

Cette variante installe `faster-whisper`. Prévoir de la mémoire et du disque pour le modèle (quelques Go disponibles conseillés), ainsi que du temps CPU. Le premier traitement télécharge le modèle open source ; les traitements suivants réutilisent le cache `/models`. `BAYAN_WHISPER_MODEL=small` est la valeur par défaut. Aucune API payante n’est appelée. Cette variante n’est pas destinée au volume Railway de 500 Mo. La vitesse et la précision en arabe dépendent de la machine, du modèle et de la qualité audio ; la relecture reste nécessaire.

## Stockage et sécurité des coûts

- `BAYAN_ALLOW_PAID_AI=0` par défaut. La présence d’une clé OpenAI n’active jamais la facturation. Un appel API historique n’est possible que si le serveur autorise explicitement le payant **et** si le job porte `costPolicy=paid`. Le studio transmet toujours `free` et refuse les anciens appels directs de traduction.
- Maximum 100 Mo par upload, marge disque de 150 Mo, vérification de capacité avant téléchargement/rendu.
- Les copies YouTube téléchargées et les fragments audio sont supprimés après traitement. Les MP4 temporaires et les médias inutilisés de plus de 24 h sont supprimés lors des nouvelles tâches ou des nouveaux uploads ; les jobs actifs sont protégés.
- Les projets et leurs sous-titres restent dans le studio. Les vidéos sont renvoyées au service depuis le studio si nécessaire.
- SQLite conserve la file et les états réels ; les jobs interrompus ne sont pas relancés silencieusement.

## Endpoints

`GET /ready` vérifie le processus. Tous les autres endpoints exigent `Authorization: Bearer <BAYAN_TOKEN>` : `GET /health`, `POST /jobs`, `GET /jobs/:id`, `GET /jobs/:id/file`, `PUT /assets/:uuid`. `/health` expose les capacités et la limite réelle. Le rendu est H.264/AAC avec FFmpeg ; pas de recadrage vertical automatique.
