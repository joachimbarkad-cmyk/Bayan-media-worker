# Spécification — Murāja'a (application de révision)

Application web indépendante, inspirée des fonctions annoncées publiquement par Use Oria, avec un nom et une interface propres. Français d'abord ; cours pouvant contenir de l'arabe. Téléphone Android et ordinateur.

## Parcours cible

Ajouter un cours → le comprendre simplement → s'entraîner sans regarder → corriger ses erreurs → revenir au bon moment.

## Règles produit (V1)

| Sujet | Règle retenue |
|---|---|
| Comptes | Comptes séparés, données privées. Chaque requête filtre par `user_id` côté serveur ; un objet d'un autre compte répond 404. Fichiers rangés par compte. Code d'invitation optionnel (`MURAJA_INVITE_CODE`). |
| Bibliothèque | Matières → chapitres → supports (PDF, texte collé, image). |
| PDF | Texte extrait page par page (pdf.js), normalisé NFKC (formes de présentation arabes). Page « lisible » si ≥ 25 lettres/chiffres et < 20 % de caractères illisibles. Statuts : `ok`, `partial` (pages listées), `insufficient` (> 50 % illisibles : probablement scanné ; OCR non disponible, dit clairement). Limites : 30 Mo, 600 pages. |
| Fiches | Texte libre modifiable. « Expliquer simplement » appelle le fournisseur de génération ; sans fournisseur, message explicite (pas de simulation). |
| Flashcards | Une question, réponse masquée, révélation volontaire (la réponse n'est envoyée au navigateur qu'après révélation), auto-évaluation 4 niveaux FSRS. |
| QCM | Une seule bonne réponse, 2 à 8 propositions, positions mélangées côté serveur à chaque présentation, correction expliquée proposition par proposition. La justesse n'est envoyée qu'après la réponse. |
| Questions ouvertes | L'élève écrit sa réponse, puis compare avec la réponse attendue et s'évalue. |
| Calendrier | Bibliothèque `ts-fsrs` (FSRS v6). État persistant par élément (`review_state`) + journal (`review_logs`). Paramètres par compte : rétention visée, intervalle max, fuzz, nouvelles cartes/jour. |
| Évaluation QCM → FSRS | Mauvaise réponse = `Again` ; bonne avec « j'ai hésité » = `Hard` ; bonne = `Good`. Jamais `Easy` : reconnaître n'est pas rappeler. |
| Révision du jour | Journée locale de l'utilisateur (défaut `Indian/Reunion`). Cartes en révision dues avant la fin de la journée locale ; cartes en apprentissage dues seulement une fois leur pas écoulé (annoncées « plus tard aujourd'hui ») ; nouvelles cartes dans la limite du quota quotidien. Une carte ratée revient dans la séance (3 fois max). |
| Séance | Persistée côté serveur (liste + position) : reprise après fermeture. Chaque présentation a un identifiant de réponse : double clic / nouvel envoi → même résultat, pas de double enregistrement ; version d'état contrôlée (409 si déjà évaluée). |
| Progression | Distingue **activités** (réponses données) et **maîtrise** : maîtrisée = rappel libre (flashcard/ouverte), état Review, stabilité ≥ 21 j, dernière note ≥ Good. Un QCM réussi compte comme « reconnu », pas « maîtrisé ». Liste « à reprendre ». |
| Sources | Chaque fiche/question garde document, pages et extrait **quand ils sont fournis**. `verified` seulement si l'extrait (≥ 8 caractères) est retrouvé dans les pages lisibles citées d'un document du même compte (comparaison sans harakat ni ponctuation). Sinon `to_verify` (import) ou `personal` (saisie manuelle sans source). Rien n'est inventé. |
| Carte mentale | Structure de nœuds (arbre, une racine, sans cycle) éditable ; chaque nœud a une explication et des questions liées. Vue carte + vue liste accessible (rôle `tree`). Mode exercice : branches masquées à révéler. Une image téléchargée reste une image consultable, jamais convertie. |
| Imports | CSV générique avec aperçu, encodage (UTF-8/1256/1252), séparateur (auto , ; tab |), en-tête, correspondance des colonnes. JSON `muraja.v1` validé (voir `docs/IMPORT_FORMAT.md`), prévisualisation puis import transactionnel. Contenus stockés comme texte brut, jamais interprétés en HTML. |
| Glossaire | Terme, forme arabe (vocalisée), définition, par compte. |
| Export | JSON complet des données du compte (sans mot de passe). Les fichiers se téléchargent document par document. |
| Génération (clé personnelle) | `server/generation.ts` + `server/ai.ts` : Anthropic (SDK officiel, `claude-opus-5-5` par défaut, repli serveur `fallbacks: "default"`), OpenAI (Responses API), Gemini ; sortie JSON par schéma, validée par Zod. Clé chiffrée AES-256-GCM (`MURAJA_SECRET_KEY`), jamais renvoyée au navigateur. Sans clé : message explicite, rien de simulé. 40 générations/jour/compte. Explication d'une fiche stockée une fois ; questions générées = brouillon relu puis enregistré ; pages illisibles exclues ; sources vérifiées comme pour un import. Origine `ai:<fournisseur>` affichée « Généré par IA ». Les comptes Claude Code / Codex des développeurs ne sont jamais utilisés. |
| Connecteur Claude / ChatGPT | `server/oauth.ts` + `server/mcp.ts` : serveur MCP Streamable HTTP sans état sur `/mcp`, OAuth 2.1 (RFC 9728, 8414, 7591 ; PKCE S256 ; clients publics ; redirections loopback sans port ; rotation des jetons de rafraîchissement avec détection de réutilisation ; 401 + `WWW-Authenticate resource_metadata`). Écran de consentement dans l'application ; applications connectées listées et révocables. Outils : lister/lire les cours (pages réelles, texte marqué « données »), voir un chapitre, difficultés, créer un chapitre, ajouter un texte de cours, flashcards, QCM/questions ouvertes, fiche, carte mentale. Aucun outil de suppression. Origine `assistant:<nom>` affichée. |
| NotebookLM | Pas de connexion possible (pas d'API personnelle) : import CSV/JSON. |
| Sécurité | Mots de passe scrypt, cookie `HttpOnly` `SameSite=Lax`, en-tête `x-muraja` exigé pour les requêtes modifiantes (CSRF), CSP stricte, fichiers servis avec CSP `sandbox`, limitation des tentatives de connexion. |
| Interface | Accueil : « Réviser aujourd'hui » et « Ajouter un cours ». Grands boutons, navigation basse sur mobile, clavier (Espace = révéler, 1–4 = évaluer), contraste, mode sombre, texte bidirectionnel ligne par ligne, police Noto Naskh Arabic embarquée. |

## Jalons

1. Dépôt, choix techniques, revue Claude→Codex démontrée. — *mécanisme livré ; revue réelle bloquée (accès), voir STATUS.*
2. Bibliothèque → import → flashcards/quiz → révision → sauvegarde, deux comptes. — *livré.*
3. Explications, sources, cartes mentales ; mode sans API ; import NotebookLM. — *en grande partie livré (sources, carte, imports) ; génération intégrée non activée ; import NotebookLM à confirmer sur un vrai export.*
4. Démonstration, corrections, préparation du déploiement sans coût.
5. Extensions : DOCX/PPTX, OCR, audio/YouTube, Feynman enrichi, plans d'étude, annotations, podcasts.

## Hors périmètre V1 (dit explicitement dans l'interface quand c'est pertinent)

OCR, génération intégrée, partage de cours entre comptes, applications natives, audio, annotations au stylet.
