"""Produit, depuis un dossier d'audit normalisé, le tableau d'exemples vérifiables d'un dépôt (Markdown, hors ligne).

  python3 tools/exemple_normalisation.py --audit data/audit_edgar_apple --accn 0000320193-25-000079
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def table(audit: Path, accn: str) -> str:
    with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
        doc = next(r for r in csv.DictReader(f) if r["accession_number"] == accn)
    with open(audit / "trace_source.csv", newline="", encoding="utf-8") as f:
        trace = {r["fact_id"]: r for r in csv.DictReader(f)}
    with open(audit / "facts.csv", newline="", encoding="utf-8") as f:
        facts = [r for r in csv.DictReader(f) if r["doc_id"] == doc["doc_id"] and r["normalized_concept"]]
    facts.sort(key=lambda r: (r["normalized_concept"], r["period_end"], r["period_start"]))
    lines = [f"Dépôt {doc['doc_type']} {accn}, accepté le {doc['accepted_at']} ; document : {doc['url']}", "",
             "| Concept du projet | Concept d'origine | Période | Valeur | Unité | Rapproché | Entrée brute (collecte) |",
             "|---|---|---|---|---|---|---|"]
    for r in facts:
        period = f"{r['period_start']} → {r['period_end']}" if r["period_start"] else f"au {r['period_end']}"
        unit = r["currency"] or r["unit"]
        lines.append(f"| {r['normalized_concept']} | {r['source_concept']} | {period} | {int(r['value']):,} | {unit} | "
                     f"{r['reconciled'] or 'non'} | `{trace[r['fact_id']]['source_pointer']}` |".replace(",", " "))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--audit", required=True, type=Path)
    p.add_argument("--accn", required=True)
    a = p.parse_args(argv)
    sys.stdout.write(table(a.audit, a.accn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
