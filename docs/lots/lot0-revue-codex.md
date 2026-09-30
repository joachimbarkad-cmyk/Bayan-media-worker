# Lot 0 — Mécanisme de revue Claude → Codex

Critères d'acceptation :
1. `scripts/request_codex_review.py` appelle `codex exec` avec des arguments séparés (pas de shell), `--output-schema`, `--output-last-message`, une sandbox, dans un worktree détaché du SHA examiné, et retire les variables `ANTHROPIC_*`/`CLAUDE_*` de son environnement.
2. Le rapport contient `reviewed_sha`, `status`, `findings`, `checks_performed`, `checks_not_run` et est conservé dans `docs/REVIEWS/` avec le SHA exact.
3. Réponse invalide, échec de commande, authentification absente, limite atteinte, délai dépassé ou SHA différent ⇒ `BLOCKED`, jamais `APPROVED`. Une approbation listant un défaut bloquant/grave est rejetée.
4. Le worktree temporaire est supprimé après la revue ; le checkout principal n'est pas modifié.
5. Tests automatisés couvrant ces cas avec un faux binaire Codex.
