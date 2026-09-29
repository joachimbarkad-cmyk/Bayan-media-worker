# Test du parcours complet jusqu’au MP4 — fichier de 3 minutes

Date : 28/09/2026. Aucun service payant utilisé (`costPolicy=free`, `BAYAN_ALLOW_PAID_AI=0`, pas de clé OpenAI).

## Conditions

| Élément | Valeur |
|---|---|
| Service | `worker.py` lancé directement (Python 3, FFmpeg 6.1.1), API HTTP réelle |
| Volume | tmpfs de **500 Mo**, identique au volume Railway cité dans le README |
| Fichier source | 1920×1080, 30 i/s, H.264 ~3,8 Mbit/s + AAC, **180 s, 88,8 Mo** (mire avec grain, proche d’une vidéo filmée) |
| Sous-titres | ASS de 60 segments arabe + français (un toutes les 3 s), en-tête identique à `tests/fixtures/captions.ass` |

La construction de l’image Docker n’a pas pu être testée dans cet environnement : la politique réseau du bac à sable refuse `deb.debian.org`, en HTTP comme en HTTPS (403). Le code exécuté est le même. Le parcours a aussi été rejoué sous l’utilisateur non privilégié uid 10001, comme `start.py` le fait dans le conteneur. Résultat : 2 exports de 97,7 Mo, et seul le dernier MP4 reste sur le disque.

## Parcours et résultat avant correction

| Étape | Appel | Résultat |
|---|---|---|
| 1. Santé | `GET /health` | OK |
| 2. Envoi du média | `PUT /assets/:uuid` (88,8 Mo) | OK |
| 3. Import arabe | `POST /jobs kind=import` | `blocked` : **attendu** en mode manuel ; le studio importe alors un SRT/VTT |
| 4.1 Export MP4 | `POST /jobs kind=export` | OK en 108 s, mais MP4 de **152 Mo** (1,7 × la source) |
| **4.2 Nouvel export (régénération)** | `POST /jobs kind=export` | **ÉCHEC** : `Espace vidéo insuffisant. Attendez le nettoyage des fichiers temporaires…` |

Avec une source plus granuleuse (93,3 Mo), le premier export produit **204,3 Mo**. Il passe de justesse sous le seuil d’arrêt `MAX_BYTES*2` (209,7 Mo). Avec un peu plus de grain, le rendu est interrompu par « Le MP4 est trop volumineux ».

## Étape qui échoue : l’export MP4 (`render_video`)

1. **Débit non plafonné.** FFmpeg ré-encode en `-crf 20` sans `-maxrate`. Sur une vidéo filmée (grain, mouvement), le débit monte à 6–9 Mbit/s. Le MP4 fait alors 1,7 à 2,2 fois la taille de l’upload.
2. **Anciens MP4 conservés 24 h.** Chaque export garde son `export.mp4` jusqu’au nettoyage. Sur 500 Mo, on compte : source 89 + premier MP4 152 = 241 Mo occupés, 259 Mo libres.
3. **Contrôle d’espace surdimensionné.** `ensure_space(max(MAX_BYTES, taille_source*2))` exige 178 Mo + 150 Mo de réserve = 328 Mo libres. Le second export est donc refusé, alors que la régénération est un usage prévu : on corrige un sous-titre, puis on relance.

## Correction (`worker.py`)

- `video_bitrate()` : le débit vidéo est plafonné (CRF 20 plafonné) par :
  - le débit de la source × 1,1, ajusté si on réduit la résolution, avec un minimum de 1,5 Mbit/s ;
  - un plafond par hauteur (480p 2,5 / 720p 5 / 1080p 8 Mbit/s) ;
  - un budget qui garantit un MP4 sous `MAX_BYTES*2`, quelle que soit la durée.
- `drop_superseded_exports()` : un nouvel export du **même média** supprime les MP4 précédents de ce média. Ils sont régénérables depuis le studio et renvoient 410 « expiré, relancez ». Un téléchargement déjà en cours se termine normalement, car le fichier reste ouvert.
- Le contrôle d’espace utilise la taille prévue du MP4 (durée × débit × 1,1) au lieu de 2 × la source.
- Tests ajoutés : `test_9_export_size_is_bounded` et `test_10_regeneration_replaces_previous_mp4`. Les deux échouent sur l’ancien code et passent après correction.

## Résultat après correction (même volume de 500 Mo)

| Étape | Résultat |
|---|---|
| 4.1 / 4.2 / 4.3 Export ×3 | OK, 96 s chacun, **97,7 Mo** (1,1 × la source), 1920×1080, 180,0 s |
| 5. Téléchargement | `GET /jobs/:id/file` → 200, 97,7 Mo, durée 180,0 s |
| Source granuleuse ×3 | OK, 102,7 Mo (au lieu de 204 Mo) |
| Vérification visuelle | à 1:34, le segment 32 est incrusté ; l’arabe est correctement lié |

Limite qui reste : un volume de 500 Mo ne contient pas deux médias différents de ~90 Mo avec leurs MP4 pendant 24 h. Dans ce cas, le message « Espace vidéo insuffisant » est exact. Il faut attendre le nettoyage ou utiliser un volume plus grand.

## Constat en production (Railway, logs du 21 au 28/09/2026)

- Version déployée : `main` @ `a784885`, c’est-à-dire **sans** les corrections ci-dessus. L’image est bien construite avec le Dockerfile (FFmpeg 7.1.5).
- Journaux HTTP : chaque traitement reçoit **une seule** consultation d’état, puis plus rien. **Aucun** `GET /jobs/:id/file` : aucun MP4 n’a jamais été téléchargé depuis la production.
- Journaux du service : chaque traitement lancé depuis une URL YouTube (26, 27 et 28/09, dernier le 28/09 à 15:05) échoue en ~3 s avec `ERROR: [youtube] … Sign in to confirm you’re not a bot`. YouTube refuse les adresses IP de Railway.
- Dans le code, cette erreur n’était pas gérée. Le traitement passait en `failed` avec le texte anglais brut de yt-dlp, à l’import comme à l’export d’un projet sans vidéo envoyée. Reproduit localement avec yt-dlp 2026.08.19.

**Correction :** `youtube_access()` reconnaît ces refus (vérification anti-robot, cookies, 403/429, vidéo privée ou réservée) et passe le traitement en `blocked`, avec un message en français. Ce message indique le parcours gratuit pris en charge : importer le fichier vidéo original (100 Mo maximum), puis le SRT/VTT. Les autres erreurs YouTube restent `failed`, avec un message court en français. Test : `test_11_youtube_bot_check_is_actionable`.

Le service Railway n’a pas pu être appelé depuis l’environnement de test : son domaine est refusé par la politique réseau du bac à sable.

## Test en production (29/09/2026)

`tests/e2e_parcours.py` lancé sur `https://bayan-media-worker-production.up.railway.app` (déploiement `f2a1c16`, 2 vCPU, 1 Go de RAM), vidéo de 3 min générée avec la commande ci-dessous, 2 exports.

| Étape | Résultat |
|---|---|
| 1. `GET /health` | OK, version 1.1.0 |
| 2. `PUT /assets` (88,8 Mo) | OK |
| 3. Import arabe | `blocked`, **attendu** en mode manuel |
| **4.1 Export MP4** | **ÉCHEC après 7 s** : `Échec FFmpeg : Fontconfig error: No writable cache directories` (×10) |

**Cause :** FFmpeg est tué par manque de mémoire. Les lignes Fontconfig ne sont que des avertissements : elles remplissent les 600 derniers caractères du journal, sans message d’erreur FFmpeg. Le pic mémoire relevé par Railway atteint 0,84 Go (limite 1 Go, échantillon de 30 s).

- FFmpeg crée ses threads (décodage H.264 et x264) selon les cœurs **visibles**, c’est-à-dire tous ceux de la machine Railway, pas les 2 vCPU alloués.
- Mesuré sur la même source 1080p : 2 threads 526 Mo, 4 threads 576 Mo, 16 threads 944 Mo, 32 threads 1 451 Mo.
- `HOME` reste `/root` après le passage à l’uid 10001, d’où les avertissements Fontconfig (cache non inscriptible).

**Correction :**

- `worker.py` : `cpu_quota()` lit le quota CPU du conteneur (`cpu.max`, cgroup v2 ou v1). FFmpeg reçoit `-threads` / `-filter_threads` = ce quota, 4 au maximum (réglable avec `BAYAN_FFMPEG_THREADS`).
- Un FFmpeg tué par le système renvoie désormais « Le rendu a été interrompu par le système (mémoire insuffisante probable) ». Les lignes Fontconfig sont retirées du message d’erreur.
- `start.py` : `HOME=/home/bayan` pour l’utilisateur 10001.
- Test : `test_12_ffmpeg_threads_follow_cpu_quota`.

**Vérification locale** (uid 10001, 2 threads, même vidéo, 2 exports) : 2 × OK en ~180 s, 97,8 Mo, 1920×1080, 180,0 s ; pic mémoire FFmpeg **533 Mo** ; sous-titre 32 incrusté à 1:34. La production doit être redéployée avec ce correctif puis le test relancé.

## Refaire le test

```sh
# 1. Dépendances (gratuites) : Python 3.10+, FFmpeg
sudo apt-get install -y ffmpeg

# 2. Vidéo de test de 3 min (~89 Mo), ou utilisez votre propre fichier < 100 Mo
ffmpeg -y -f lavfi -i "testsrc2=s=1920x1080:r=30:d=180,noise=alls=12:allf=t+u" \
  -f lavfi -i "sine=frequency=220:beep_factor=4:duration=180" \
  -c:v libx264 -preset veryfast -b:v 3.8M -maxrate 4M -bufsize 8M -pix_fmt yuv420p \
  -c:a aac -b:a 128k -shortest test-3min.mp4

# 3. (Optionnel, Linux root) simuler le volume Railway de 500 Mo
sudo mkdir -p /mnt/bayan500 && sudo mount -t tmpfs -o size=500m tmpfs /mnt/bayan500

# 4. Lancer le service
export BAYAN_TOKEN=$(python3 -c "import secrets;print(secrets.token_urlsafe(32))")
BAYAN_DATA=/mnt/bayan500 PORT=8080 HOST=127.0.0.1 python3 worker.py &

# 5. Parcours complet : envoi, import, 3 exports, téléchargement
BAYAN_URL=http://127.0.0.1:8080 python3 tests/e2e_parcours.py test-3min.mp4 export.mp4 original 3

# 6. Tests unitaires
python3 -m unittest tests/test_worker.py -v
```

Avec Docker : `docker compose up -d --build`, puis l’étape 5 avec le même `BAYAN_TOKEN` que dans `.env`.
