# Lot 2 — IA connectée (compte Claude/ChatGPT de la personne, clé personnelle)

Critères d'acceptation :
1. Serveur MCP `/mcp` : sans jeton → 401 avec `WWW-Authenticate: Bearer resource_metadata=...` ; métadonnées RFC 9728 (`resource` = URL `/mcp` exacte) et RFC 8414 (S256, `none`, `registration_endpoint`).
2. OAuth : DCR (HTTPS ou loopback seulement), autorisation par consentement de l'utilisateur connecté, code à usage unique lié au client et à la redirection, PKCE S256 obligatoire, jetons d'accès 1 h, rotation des jetons de rafraîchissement, réutilisation ⇒ révocation de la famille, redirection inconnue jamais suivie, déconnexion depuis Réglages.
3. Outils MCP limités au compte du jeton : impossible de lire ou d'écrire dans un autre compte ; aucun outil de suppression ; contenus créés marqués `assistant:<nom>` ; sources vérifiées seulement si l'extrait est retrouvé.
4. Clé personnelle chiffrée au repos, jamais renvoyée ; sans clé ni clé serveur : message explicite, aucune simulation ; limite quotidienne ; erreurs du fournisseur traduites (clé refusée, quota, modèle inconnu).
5. « Expliquer simplement » enregistré une fois ; génération de questions = brouillon relu avant enregistrement, pages illisibles exclues, QCM à plusieurs bonnes réponses écartés.
