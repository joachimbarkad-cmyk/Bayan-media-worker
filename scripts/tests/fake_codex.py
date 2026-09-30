#!/usr/bin/env python3
"""Stand-in for the Codex CLI used by the tests. Mode set by FAKE_CODEX_MODE."""
import json
import os
import re
import sys
import time
from pathlib import Path

mode = os.environ.get("FAKE_CODEX_MODE", "approve")
args = sys.argv[1:]
if args == ["--version"]:
    print("codex-cli 0.0.0-fake")
    sys.exit(0)
if args[:2] == ["login", "status"]:
    if mode == "logged_out":
        print("Not logged in")
        sys.exit(1)
    print("Logged in using ChatGPT")
    sys.exit(0)
assert args[0] == "exec", args
for flag in ("--cd", "--sandbox", "--output-schema", "--output-last-message"):
    assert flag in args, f"missing {flag}"
assert args[-1] == "-", "prompt must come from stdin"
out = Path(args[args.index("--output-last-message") + 1])
workdir = Path(args[args.index("--cd") + 1])
schema = json.loads(Path(args[args.index("--output-schema") + 1]).read_text())
assert schema["title"] == "CodexReview"
prompt = sys.stdin.read()
sha = re.search(r"reviewed_sha \(commit[^)]*\) : ([0-9a-f]{40})", prompt).group(1)
# The worktree must be the reviewed commit, detached.
head = (workdir / ".git").exists() and os.popen(f"git -C '{workdir}' rev-parse HEAD").read().strip()
assert head == sha, (head, sha)
leaked = [k for k in os.environ if k.startswith("ANTHROPIC_")]
assert not leaked, leaked

if mode == "timeout":
    time.sleep(60)
if mode == "rate_limit":
    print("ERROR: You've hit your usage limit. Try again later.", file=sys.stderr)
    sys.exit(1)
if mode == "invalid_json":
    out.write_text("Voici ma revue : tout va bien")
    sys.exit(0)
review = {
    "reviewed_sha": sha, "status": "APPROVED", "summary": "RAS.",
    "findings": [], "checks_performed": [{"check": "lecture du diff", "result": "ok"}], "checks_not_run": [],
}
if mode == "wrong_sha":
    review["reviewed_sha"] = "0" * 40
if mode == "changes":
    review["status"] = "CHANGES_REQUESTED"
    review["findings"] = [{"severity": "high", "blocking": True, "file": "a.txt", "scenario": "ouvrir a.txt",
                           "expected": "b", "observed": "a", "proposed_fix": "écrire b"}]
if mode == "inconsistent":
    review["findings"] = [{"severity": "critical", "blocking": True, "file": "a.txt", "scenario": "s",
                           "expected": "e", "observed": "o", "proposed_fix": "p"}]
out.write_text(json.dumps(review))
