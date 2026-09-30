#!/usr/bin/env python3
"""Request an independent Codex review of one exact commit and store a validated report.

Usage (see docs/PROTOCOL.md):
  python3 scripts/request_codex_review.py --lot "Lot 1" --base <sha> [--head <sha>] \
      --criteria-file docs/lots/lot1.md --validation "npm test: 42 passed" ...

Exit codes: 0 APPROVED, 1 CHANGES_REQUESTED, 2 BLOCKED (never counts as approval).

Safety: every subprocess is launched with a list of separate arguments (never a shell),
Codex runs in a disposable detached worktree of the reviewed SHA, and nothing Codex
returns is ever executed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = Path(__file__).resolve().parent / "codex_review_schema.json"
PROMPT_PATH = Path(__file__).resolve().parent / "codex_review_prompt.md"
STATUSES = ("APPROVED", "CHANGES_REQUESTED", "BLOCKED")
SEVERITIES = ("critical", "high", "medium", "low")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
LIMIT_PATTERNS = re.compile(r"rate.?limit|usage limit|quota|429|too many requests", re.I)
AUTH_PATTERNS = re.compile(r"not logged in|unauthori[sz]ed|401|login required|invalid api key", re.I)
NETWORK_PATTERNS = re.compile(r"proxy connection failed|connect failed|waiting for network|dns|connection refused", re.I)
# Keys removed from Codex's environment so it cannot reach the Claude developer accounts.
SCRUBBED_ENV_PREFIXES = ("ANTHROPIC_", "CLAUDE_CODE_", "CLAUDE_")


def git(*args: str, cwd: Path = ROOT) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return out.stdout.strip()


def resolve_sha(ref: str) -> str:
    sha = git("rev-parse", "--verify", f"{ref}^{{commit}}")
    if not SHA_RE.match(sha):
        raise SystemExit(f"Référence invalide : {ref}")
    return sha


def slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return s[:40] or "lot"


# ---------------------------------------------------------------- validation

def validate_review(data: object, expected_sha: str) -> list[str]:
    """Return a list of problems. An empty list means the response is usable."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["la réponse n'est pas un objet JSON"]
    required = ["reviewed_sha", "status", "summary", "findings", "checks_performed", "checks_not_run"]
    for key in required:
        if key not in data:
            errors.append(f"champ manquant : {key}")
    extra = set(data) - set(required)
    if extra:
        errors.append(f"champs inattendus : {sorted(extra)}")
    if errors:
        return errors
    if data["reviewed_sha"] != expected_sha:
        errors.append(f"reviewed_sha {data['reviewed_sha']!r} ≠ SHA demandé {expected_sha}")
    if data["status"] not in STATUSES:
        errors.append(f"statut inconnu : {data['status']!r}")
    if not isinstance(data["summary"], str):
        errors.append("summary doit être une chaîne")
    finding_keys = {"severity", "blocking", "file", "scenario", "expected", "observed", "proposed_fix"}
    if not isinstance(data["findings"], list):
        errors.append("findings doit être une liste")
    else:
        for i, f in enumerate(data["findings"]):
            if not isinstance(f, dict) or set(f) != finding_keys:
                errors.append(f"finding {i} : champs attendus {sorted(finding_keys)}")
                continue
            if f["severity"] not in SEVERITIES:
                errors.append(f"finding {i} : gravité inconnue {f['severity']!r}")
            if not isinstance(f["blocking"], bool):
                errors.append(f"finding {i} : blocking doit être booléen")
            for k in finding_keys - {"severity", "blocking"}:
                if not isinstance(f[k], str) or not f[k].strip():
                    errors.append(f"finding {i} : {k} vide")
    for key, fields in (("checks_performed", {"check", "result"}), ("checks_not_run", {"check", "reason"})):
        if not isinstance(data[key], list):
            errors.append(f"{key} doit être une liste")
            continue
        for i, c in enumerate(data[key]):
            if not isinstance(c, dict) or set(c) != fields or not all(isinstance(c[k], str) for k in fields):
                errors.append(f"{key}[{i}] : champs attendus {sorted(fields)}")
    if not errors and data["status"] == "APPROVED":
        blocking = [f for f in data["findings"] if f["blocking"] or f["severity"] in ("critical", "high")]
        if blocking:
            errors.append("APPROVED incohérent : des défauts bloquants ou graves sont listés")
        if not data["checks_performed"]:
            errors.append("APPROVED sans aucune vérification effectuée")
    return errors


# ---------------------------------------------------------------- prompt

def build_prompt(lot: str, base: str, head: str, criteria: str, validations: list[str], focus: list[str]) -> str:
    rules = PROMPT_PATH.read_text(encoding="utf-8")
    stat = git("diff", "--stat", f"{base}..{head}") if base != head else "(revue du commit complet)"
    log = git("log", "--oneline", f"{base}..{head}") if base != head else git("log", "--oneline", "-1", head)
    parts = [
        rules,
        "\n## Demande de revue\n",
        f"- Lot : {lot}",
        f"- reviewed_sha (commit à examiner, déjà extrait dans le répertoire courant) : {head}",
        f"- SHA de base : {base}",
        "- Pour voir les changements : `git diff " + base + ".." + head + "` et `git log " + base + ".." + head + "`.",
    ]
    if focus:
        parts.append("- Concentre-toi d'abord sur : " + ", ".join(focus))
    parts += [
        "\n### Commits\n", "```", log or "(aucun)", "```",
        "\n### Fichiers modifiés\n", "```", stat, "```",
        "\n### Critères d'acceptation du lot\n", criteria.strip() or "(non fournis)",
        "\n### Validations déclarées par Claude (à lire APRÈS ton examen indépendant ; ne les considère pas comme prouvées)\n",
    ]
    parts += [f"- {v}" for v in validations] or ["- (aucune)"]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- codex call

def codex_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not k.startswith(SCRUBBED_ENV_PREFIXES)}


def preflight(codex_bin: str) -> tuple[str | None, str]:
    """Return (blocking_reason_or_None, version)."""
    exe = shutil.which(codex_bin)
    if not exe:
        return f"Codex CLI introuvable ({codex_bin!r}). Installer : npm install -g @openai/codex", ""
    try:
        v = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30, env=codex_env())
        version = (v.stdout or v.stderr).strip()
        st = subprocess.run([exe, "login", "status"], capture_output=True, text=True, timeout=30, env=codex_env())
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"Codex CLI inutilisable : {exc}", ""
    if st.returncode != 0:
        msg = (st.stdout + st.stderr).strip() or f"code {st.returncode}"
        return f"Codex non authentifié ({msg}). Lancer `codex login` sur la machine de développement.", version
    return None, version


def run_codex(codex_bin: str, workdir: Path, prompt: str, out_file: Path, log_file: Path,
              sandbox: str, timeout: int, model: str | None) -> tuple[int | None, str]:
    cmd = [
        shutil.which(codex_bin) or codex_bin, "exec",
        "--cd", str(workdir),
        "--sandbox", sandbox,
        "--output-schema", str(SCHEMA_PATH),
        "--output-last-message", str(out_file),
        "--color", "never",
        "--ephemeral",
    ]
    if model:
        cmd += ["--model", model]
    cmd.append("-")  # prompt read from stdin
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("$ " + " ".join(cmd) + "\n\n")
        log.flush()
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                                text=True, env=codex_env(), start_new_session=True)
        try:
            proc.communicate(prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            return None, log_file.read_text(encoding="utf-8", errors="replace")
    return proc.returncode, log_file.read_text(encoding="utf-8", errors="replace")


def classify_failure(log_text: str) -> str:
    if AUTH_PATTERNS.search(log_text):
        return "authentification refusée"
    if LIMIT_PATTERNS.search(log_text):
        return "limite d'usage atteinte"
    if NETWORK_PATTERNS.search(log_text):
        return "réseau inaccessible (api.openai.com)"
    return "échec de la commande"


# ---------------------------------------------------------------- report

def write_report(out_dir: Path, report: dict) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{report['requested_at'][:10]}-{slug(report['lot'])}-{report['reviewed_sha'][:12]}"
    jpath = out_dir / f"{stem}.json"
    n = 2
    while jpath.exists():
        jpath = out_dir / f"{stem}-{n}.json"
        n += 1
    jpath.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mpath = jpath.with_suffix(".md")
    lines = [
        f"# Revue Codex — {report['lot']}",
        "",
        f"- Statut retenu : **{report['status']}**" + (f" (réponse Codex : {report['codex_status']})" if report.get("codex_status") else ""),
        f"- reviewed_sha : `{report['reviewed_sha']}` · base : `{report['base_sha']}`",
        f"- Date : {report['requested_at']} · Codex : {report['codex']['version'] or 'n/a'} · durée : {report['codex']['duration_s']} s",
    ]
    if report["blocked_reason"]:
        lines.append(f"- Blocage : {report['blocked_reason']}")
    if report["validation_errors"]:
        lines += ["", "## Réponse rejetée", *[f"- {e}" for e in report["validation_errors"]]]
    if report.get("summary"):
        lines += ["", "## Résumé", report["summary"]]
    lines += ["", "## Défauts"]
    lines += [f"- [{f['severity']}{', bloquant' if f['blocking'] else ''}] `{f['file']}` — {f['observed']} → {f['proposed_fix']}"
              for f in report["findings"]] or ["- aucun"]
    lines += ["", "## Vérifications effectuées"]
    lines += [f"- {c['check']} : {c['result']}" for c in report["checks_performed"]] or ["- aucune"]
    lines += ["", "## Vérifications non effectuées"]
    lines += [f"- {c['check']} : {c['reason']}" for c in report["checks_not_run"]] or ["- aucune"]
    mpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return jpath, mpath


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lot", required=True, help="Nom du lot examiné")
    ap.add_argument("--base", required=True, help="SHA ou référence de base")
    ap.add_argument("--head", default="HEAD", help="SHA ou référence à examiner (défaut HEAD)")
    ap.add_argument("--criteria", default="", help="Critères d'acceptation (texte)")
    ap.add_argument("--criteria-file", type=Path, help="Fichier contenant les critères d'acceptation")
    ap.add_argument("--validation", action="append", default=[], help="Validation réalisée (répétable)")
    ap.add_argument("--focus", action="append", default=[], help="Fichier ou zone prioritaire (répétable)")
    ap.add_argument("--timeout", type=int, default=1200, help="Délai maximal en secondes")
    ap.add_argument("--sandbox", choices=["read-only", "workspace-write"], default="workspace-write",
                    help="Sandbox Codex, appliquée au worktree jetable (défaut workspace-write pour lancer les tests)")
    ap.add_argument("--model", help="Modèle Codex (défaut : configuration de Codex)")
    ap.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"))
    ap.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "REVIEWS")
    ap.add_argument("--prepare-only", action="store_true",
                    help="Écrire le dossier de revue (prompt + commande) sans appeler Codex")
    args = ap.parse_args(argv)

    head = resolve_sha(args.head)
    base = resolve_sha(args.base)
    criteria = args.criteria
    if args.criteria_file:
        criteria = (criteria + "\n" + args.criteria_file.read_text(encoding="utf-8")).strip()
    prompt = build_prompt(args.lot, base, head, criteria, args.validation, args.focus)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    report: dict = {
        "reviewed_sha": head, "base_sha": base, "lot": args.lot, "requested_at": now,
        "status": "BLOCKED", "codex_status": None, "blocked_reason": None, "summary": "",
        "findings": [], "checks_performed": [], "checks_not_run": [], "validation_errors": [],
        "criteria": criteria, "validations_declared": args.validation,
        "codex": {"version": "", "exit_code": None, "duration_s": 0, "sandbox": args.sandbox},
    }

    if args.prepare_only:
        bundle = args.out_dir / "pending" / f"{slug(args.lot)}-{head[:12]}"
        bundle.mkdir(parents=True, exist_ok=True)
        (bundle / "prompt.md").write_text(prompt, encoding="utf-8")
        cmd = ["python3", "scripts/request_codex_review.py", "--lot", args.lot, "--base", base, "--head", head]
        if args.criteria_file:
            cmd += ["--criteria-file", str(args.criteria_file)]
        for v in args.validation:
            cmd += ["--validation", v]
        (bundle / "command.json").write_text(json.dumps(cmd, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Dossier de revue préparé : {bundle.relative_to(ROOT) if bundle.is_relative_to(ROOT) else bundle}")
        return 2

    reason, version = preflight(args.codex_bin)
    report["codex"]["version"] = version
    if reason:
        report["blocked_reason"] = reason
        report["checks_not_run"] = [{"check": "revue Codex", "reason": reason}]
        j, _ = write_report(args.out_dir, report)
        print(f"BLOCKED — {reason}\nRapport : {j}")
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="codex-review-"))
    worktree = tmp / "wt"
    out_file = tmp / "last_message.json"
    log_file = tmp / "codex.log"
    started = time.monotonic()
    try:
        git("worktree", "add", "--detach", str(worktree), head)
        code, log_text = run_codex(args.codex_bin, worktree, prompt, out_file, log_file,
                                   args.sandbox, args.timeout, args.model)
        report["codex"]["exit_code"] = code
        report["codex"]["duration_s"] = round(time.monotonic() - started, 1)
        if code is None:
            report["blocked_reason"] = f"délai dépassé ({args.timeout} s) — {classify_failure(log_text)}"
        elif code != 0:
            report["blocked_reason"] = f"{classify_failure(log_text)} (code {code})"
        else:
            raw = out_file.read_text(encoding="utf-8") if out_file.exists() else ""
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                data = None
                report["validation_errors"] = [f"JSON invalide : {exc}"]
            if data is not None:
                report["validation_errors"] = validate_review(data, head)
            if report["validation_errors"]:
                report["blocked_reason"] = "réponse Codex invalide"
                report["raw_response"] = raw[:20000]
            else:
                report.update({k: data[k] for k in ("summary", "findings", "checks_performed", "checks_not_run")})
                report["codex_status"] = data["status"]
                report["status"] = data["status"]
        if report["blocked_reason"]:
            report["log_tail"] = log_text[-4000:]
            report["checks_not_run"] = report["checks_not_run"] or [{"check": "revue Codex", "reason": report["blocked_reason"]}]
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)

    j, _ = write_report(args.out_dir, report)
    print(f"{report['status']}" + (f" — {report['blocked_reason']}" if report["blocked_reason"] else "") + f"\nRapport : {j}")
    return {"APPROVED": 0, "CHANGES_REQUESTED": 1}.get(report["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
