"""Collecte EDGAR (SEC) -> dossier d'AUDIT documentaire. Hors du paquet halal_sim, qui reste sans réseau.

Deux étapes séparées :
  collect : télécharge les JSON bruts « submissions » et « companyfacts » d'une liste de CIK, avec journal
            (URL, horodatage UTC, SHA-256). Aucune valeur par défaut pour l'identification SEC : --user-agent
            est obligatoire à chaque lancement (la SEC demande un nom et une adresse électronique de contact).
  convert : transforme ces JSON bruts en dossier d'audit (issuers, documents, facts, ...) vérifiable par
            `python3 -m halal_sim audit-docs`. Aucune normalisation automatique : concept_map.csv reste vide,
            tous les faits sont « non normalisés » et le verdict reste NON EXPLOITABLE tant qu'un humain n'a pas
            mappé, justifié et rapproché chaque fait de sa pièce.

HYPOTHÈSES À VÉRIFIER (documentation SEC non consultable depuis l'environnement de développement) :
- URL : https://data.sec.gov/submissions/CIK##########.json et
        https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json (CIK sur 10 chiffres) ;
- submissions : filings.recent = listes parallèles accessionNumber, filingDate, reportDate, acceptanceDateTime,
  form, primaryDocument ;
- companyfacts : facts.<taxonomie>.<concept>.units.<unité> = liste de {accn, end, [start], val, form, filed, ...} ;
  pas de contexte XBRL ni de précision (decimals). Selon la SEC (rapporté par le relecteur), companyfacts n'agrège
  que certains faits de taxonomies standard s'appliquant à l'entité : ce n'est PAS l'ensemble des faits du dépôt,
  et l'absence de contexte ne prouve pas l'absence de dimensions -> dimensions et contexte laissés INCONNUS ;
- submissions : filings.recent ne couvre que les dépôts récents ; les plus anciens sont référencés dans
  filings.files (non collectés ici : signalé comme historique incomplet) ;
- chaque JSON porte le CIK de l'émetteur (champ « cik ») : il doit correspondre au CIK du journal ;
- accès équitable : au plus 10 requêtes par seconde (l'outil en fait au plus 2).
L'analyse est STRICTE : un champ attendu absent arrête la conversion avec un message explicite.

Usage :
  python3 tools/edgar_collect.py collect --cik 320193 --user-agent "Prénom Nom contact@domaine" --out DOSSIER_BRUT
  python3 tools/edgar_collect.py collect --cik 320193 --dry-run --out DOSSIER_BRUT      # aucune requête
  python3 tools/edgar_collect.py convert --raw DOSSIER_BRUT --out DOSSIER_AUDIT [--forms 10-K,10-Q]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"
MIN_INTERVAL_S = 0.5
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PLACEHOLDER_DOMAINS = re.compile(r"@(example|exemple|domaine|domain|test|invalid)\.", re.IGNORECASE)
AUDIT_HEADERS = {
    "issuers": ["issuer_id", "name", "id_scheme", "source", "source_url"],
    "securities": ["security_id", "issuer_id", "ticker", "exchange", "valid_from", "valid_to", "instrument_type",
                   "currency", "source"],
    "documents": ["doc_id", "issuer_id", "doc_type", "accession_number", "url", "local_copy", "local_sha256",
                  "period_end", "accepted_at", "public_available_at", "retrieved_at", "version", "amends_doc_id"],
    "facts": ["fact_id", "doc_id", "source_concept", "source_context", "source_dimensions", "source_unit", "raw_value",
              "decimals", "normalized_concept", "transformation", "normalization_justification", "definition", "value",
              "unit", "currency", "period_type", "period_start", "period_end", "measure_date", "share_class",
              "price_adjusted", "corrects_fact_id", "reconciled", "reconciled_note"],
    "concept_map": ["source_concept", "normalized_concept", "justification"],
    "activities": ["issuer_id", "proposed_code", "evidence_doc_id", "available_at", "source", "source_url",
                   "justification"],
}


class EdgarFormatError(ValueError):
    pass


def cik10(value: str) -> str:
    digits = value.strip().lstrip("0") or "0"
    if not digits.isdigit() or len(digits) > 10:
        raise ValueError(f"CIK invalide : {value!r}")
    return digits.zfill(10)


def check_user_agent(ua: str | None) -> str:
    if not ua or not EMAIL_RE.search(ua) or len(ua.split()) < 2:
        raise SystemExit("REFUS : --user-agent obligatoire, sous la forme « Prénom Nom adresse@domaine ». "
                         "Aucune valeur par défaut n'est fournie.")
    if PLACEHOLDER_DOMAINS.search(ua):
        raise SystemExit("REFUS : l'identification ressemble à un exemple ; indiquez un contact réel.")
    return ua


def _get(url: str, ua: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _require_fresh_dir(out: Path, replace: bool, what: str) -> None:
    """Jamais d'écrasement silencieux : un dossier existant non vide n'est réutilisé qu'avec --remplacer."""
    if out.exists() and any(out.iterdir()) and not replace:
        raise SystemExit(f"REFUS : {out} existe déjà et n'est pas vide ({what}). Choisissez un dossier neuf, ou "
                         "ajoutez --remplacer en connaissance de cause (un rapprochement humain y serait perdu).")


def import_files(cik: str, submissions: Path, companyfacts: Path, retrieved_at: str, out: Path,
                 replace: bool = False) -> list[dict]:
    """Enregistre des JSON téléchargés À LA MAIN (navigateur) : aucune requête réseau, aucune identification.
    L'heure de téléchargement est DÉCLARÉE par l'utilisateur (avec fuseau), jamais inventée."""
    try:
        when = datetime.fromisoformat(retrieved_at)
    except ValueError:
        when = None
    if when is None or when.tzinfo is None:
        raise SystemExit("REFUS : --retrieved-at doit être une date-heure avec fuseau, ex. 2026-09-28T14:05:00+02:00")
    _require_fresh_dir(out, replace, "collecte brute")
    out.mkdir(parents=True, exist_ok=True)
    c10 = cik10(cik)
    log = []
    for kind, src, url in (("submissions", submissions, SUBMISSIONS_URL.format(cik=c10)),
                           ("companyfacts", companyfacts, FACTS_URL.format(cik=c10))):
        body = Path(src).read_bytes()
        name = f"{kind}_CIK{c10}.json"
        (out / name).write_bytes(body)
        log.append({"kind": kind, "cik": c10, "url": url, "file": name, "retrieved_at": when.isoformat(),
                    "sha256": hashlib.sha256(body).hexdigest(), "method": "téléchargement manuel déclaré"})
    (out / "journal_collecte.json").write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return log


def collect(ciks: list[str], out: Path, ua: str | None, dry_run: bool = False, fetch=_get,
            replace: bool = False) -> list[dict]:
    targets = []
    for c in ciks:
        c10 = cik10(c)
        targets += [("submissions", c10, SUBMISSIONS_URL.format(cik=c10)), ("companyfacts", c10, FACTS_URL.format(cik=c10))]
    if dry_run:
        for kind, c10, url in targets:
            print(f"[simulation] {kind:12} {c10} {url}")
        return []
    ua = check_user_agent(ua)
    _require_fresh_dir(out, replace, "collecte brute")
    out.mkdir(parents=True, exist_ok=True)
    log = []
    for i, (kind, c10, url) in enumerate(targets):
        if i:
            time.sleep(MIN_INTERVAL_S)
        body = fetch(url, ua)
        path = out / f"{kind}_CIK{c10}.json"
        path.write_bytes(body)
        log.append({"kind": kind, "cik": c10, "url": url, "file": path.name,
                    "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "sha256": hashlib.sha256(body).hexdigest()})
        print(f"{kind:12} {c10} -> {path.name}")
    # L'identification SEC n'est pas enregistrée dans le journal (donnée personnelle).
    (out / "journal_collecte.json").write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return log


def _need(obj: dict, key: str, ctx: str):
    if key not in obj:
        raise EdgarFormatError(f"{ctx} : champ attendu {key!r} absent (format SEC différent de l'hypothèse)")
    return obj[key]


def convert(raw: Path, out: Path, forms: set[str], replace: bool = False) -> dict:
    _require_fresh_dir(out, replace, "dossier d'audit")
    journal = json.loads((raw / "journal_collecte.json").read_text(encoding="utf-8"))
    retrieved = {(e["kind"], e["cik"]): e for e in journal}
    for e in journal:  # intégrité des fichiers bruts depuis la collecte
        if hashlib.sha256((raw / e["file"]).read_bytes()).hexdigest() != e["sha256"]:
            raise EdgarFormatError(f"{e['file']} modifié depuis sa collecte (SHA-256 différent)")
    rows = {k: [] for k in AUDIT_HEADERS}
    amendments_to_link, skipped_facts, incomplete, merged, skipped_docs = [], 0, [], 0, []
    seen: dict[str, tuple] = {}
    for (kind, c10), entry in sorted(retrieved.items()):
        if kind != "submissions":
            continue
        sub = json.loads((raw / entry["file"]).read_text(encoding="utf-8"))
        _check_cik(sub, c10, entry["file"])
        name = _need(sub, "name", entry["file"])
        older = _need(sub, "filings", entry["file"]).get("files") or []
        if older:
            incomplete.append(f"{c10} : {len(older)} fichier(s) de dépôts plus anciens non collecté(s) "
                              f"({', '.join(str(f.get('name', '?')) for f in older[:3])}{'…' if len(older) > 3 else ''})")
        rows["issuers"].append({"issuer_id": c10, "name": name, "id_scheme": "CIK",
                                "source": "SEC EDGAR submissions API", "source_url": entry["url"]})
        recent = _need(_need(sub, "filings", entry["file"]), "recent", entry["file"])
        cols = {k: _need(recent, k, entry["file"]) for k in
                ("accessionNumber", "filingDate", "reportDate", "acceptanceDateTime", "form", "primaryDocument")}
        n = len(cols["accessionNumber"])
        if any(len(v) != n for v in cols.values()):
            raise EdgarFormatError(f"{entry['file']} : listes filings.recent de longueurs différentes")
        docs_by_accn, meta_by_accn = {}, {}
        for i in range(n):
            form = cols["form"][i]
            base = form[:-2] if form.endswith("/A") else form
            if base not in forms:
                continue
            accn = cols["accessionNumber"][i]
            if form.endswith("/A"):
                amendments_to_link.append(f"{c10} {form} {accn} (période {cols['reportDate'][i]})")
                continue  # le document rectifié doit être désigné à la main : pas d'inférence
            if not cols["reportDate"][i]:
                skipped_docs.append(f"{c10} {form} {accn} : fin de période (reportDate) absente")
                continue
            doc_id = f"{c10}-{accn}"
            docs_by_accn[accn] = doc_id
            meta_by_accn[accn] = (form, cols["filingDate"][i])
            rows["documents"].append({
                "doc_id": doc_id, "issuer_id": c10, "doc_type": form, "accession_number": accn,
                "url": ARCHIVE_URL.format(cik_int=int(c10), acc_nodash=accn.replace("-", ""),
                                          doc=cols["primaryDocument"][i]),
                "local_copy": "", "local_sha256": "", "period_end": cols["reportDate"][i],
                "accepted_at": cols["acceptanceDateTime"][i].replace("Z", "+00:00"),
                "public_available_at": "",  # non établie par l'API : laissée inconnue
                "retrieved_at": entry["retrieved_at"], "version": "original", "amends_doc_id": ""})
        facts_entry = retrieved.get(("companyfacts", c10))
        if facts_entry is None:
            continue
        cf = json.loads((raw / facts_entry["file"]).read_text(encoding="utf-8"))
        _check_cik(cf, c10, facts_entry["file"])
        for taxonomy, concepts in _need(cf, "facts", facts_entry["file"]).items():
            for concept, body in concepts.items():
                for unit, items in _need(body, "units", f"{taxonomy}:{concept}").items():
                    for it in items:
                        doc_id = docs_by_accn.get(_need(it, "accn", f"{taxonomy}:{concept}"))
                        if doc_id is None:
                            skipped_facts += 1
                            continue
                        accn = it["accn"]
                        f_form, f_filed = _need(it, "form", concept), _need(it, "filed", concept)
                        if (f_form, f_filed) != meta_by_accn[accn]:
                            raise EdgarFormatError(
                                f"{taxonomy}:{concept} : fait rattaché au dépôt {accn} ({meta_by_accn[accn][0]}, déposé le "
                                f"{meta_by_accn[accn][1]}) mais déclaré {f_form} déposé le {f_filed} ; conversion arrêtée")
                        start = it.get("start", "")
                        fid = f"{doc_id}-{taxonomy}:{concept}-{unit}-{start}-{_need(it, 'end', concept)}".replace("/", "_")
                        val = _need(it, "val", concept)
                        if fid in seen:
                            if seen[fid][0] != val:  # même dépôt, concept, unité et période, valeurs différentes
                                raise EdgarFormatError(
                                    f"Doublon contradictoire {fid} : {seen[fid][1]} contre {json.dumps(it)} ; "
                                    "conversion arrêtée, les deux entrées brutes restent dans le fichier source")
                            merged += 1
                            continue
                        seen[fid] = (val, json.dumps(it))
                        rows["facts"].append({
                            "fact_id": fid,
                            "doc_id": doc_id, "source_concept": f"{taxonomy}:{concept}",
                            "source_context": "", "source_dimensions": "INCONNU",
                            "source_unit": unit, "raw_value": str(_need(it, "val", concept)), "decimals": "",
                            "normalized_concept": "", "transformation": "", "normalization_justification": "",
                            "definition": body.get("label") or concept, "value": "",
                            "unit": "actions" if unit == "shares" else ("monnaie" if re.fullmatch(r"[A-Z]{3}", unit) else unit),
                            "currency": unit if re.fullmatch(r"[A-Z]{3}", unit) else "",
                            "period_type": "duration" if start else "instant", "period_start": start,
                            "period_end": _need(it, "end", concept),
                            "measure_date": it["end"] if unit == "shares" else "",
                            "share_class": "INCONNU" if unit == "shares" else "",
                            "price_adjusted": "", "corrects_fact_id": "", "reconciled": "", "reconciled_note": ""})
    out.mkdir(parents=True, exist_ok=True)
    warning = ("Données SEC EDGAR converties automatiquement (companyfacts : sous-ensemble des faits du dépôt). "
               "Contexte, dimensions et catégorie d'actions INCONNUS. Aucun fait normalisé ni rapproché : dossier "
               "NON EXPLOITABLE tant qu'un humain n'a pas établi, mappé, justifié et rapproché chaque fait.")
    warning += (f" PÉRIMÈTRE : dépôts récents (filings.recent) des formulaires {sorted(forms)} ; "
                f"{len(rows['documents'])} document(s) retenu(s), {len(skipped_docs)} écarté(s), "
                f"{len(amendments_to_link)} rectificatif(s) à rattacher à la main.")
    if incomplete:
        warning += " HISTORIQUE INCOMPLET : " + " ; ".join(incomplete)
    (out / "manifest.json").write_text(json.dumps({
        "name": f"edgar_{datetime.now(timezone.utc):%Y%m%d}", "nature": "REEL", "warning": warning},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, header in AUDIT_HEADERS.items():
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            w.writerows(rows[name])
    return {"documents": len(rows["documents"]), "facts": len(rows["facts"]),
            "amendments_to_link": amendments_to_link, "facts_skipped_other_documents": skipped_facts,
            "identical_duplicates_merged": merged, "incomplete_history": incomplete,
            "selected_but_skipped": skipped_docs}


def _check_cik(obj: dict, c10: str, ctx: str) -> None:
    found = _need(obj, "cik", ctx)
    try:
        same = int(str(found)) == int(c10)
    except ValueError:
        same = False
    if not same:
        raise EdgarFormatError(f"{ctx} : CIK {found!r} différent du CIK attendu {c10} (fichier d'un autre émetteur ?)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--cik", action="append", required=True)
    c.add_argument("--user-agent")
    c.add_argument("--out", required=True, type=Path)
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--remplacer", action="store_true")
    i = sub.add_parser("import-files", help="Enregistrer des JSON téléchargés à la main (aucun réseau, aucune identification)")
    i.add_argument("--cik", required=True)
    i.add_argument("--submissions", required=True, type=Path)
    i.add_argument("--companyfacts", required=True, type=Path)
    i.add_argument("--retrieved-at", required=True, help="Date-heure du téléchargement avec fuseau")
    i.add_argument("--out", required=True, type=Path)
    i.add_argument("--remplacer", action="store_true")
    v = sub.add_parser("convert")
    v.add_argument("--raw", required=True, type=Path)
    v.add_argument("--out", required=True, type=Path)
    v.add_argument("--forms", default="10-K,10-Q")
    v.add_argument("--remplacer", action="store_true")
    a = p.parse_args(argv)
    if a.cmd == "collect":
        collect(a.cik, a.out, a.user_agent, a.dry_run, replace=a.remplacer)
    elif a.cmd == "import-files":
        import_files(a.cik, a.submissions, a.companyfacts, a.retrieved_at, a.out, a.remplacer)
        print(f"Fichiers enregistrés dans {a.out}. Étape suivante : convert --raw {a.out} --out <dossier d'audit>")
    else:
        res = convert(a.raw, a.out, set(a.forms.split(",")), a.remplacer)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        print(f"Vérifiez ensuite : python3 -m halal_sim audit-docs {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
