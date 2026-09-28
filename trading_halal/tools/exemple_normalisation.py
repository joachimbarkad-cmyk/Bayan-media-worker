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
    with open(audit / "facts.csv", newline="", encoding="utf-8") as f:
        facts = {r["fact_id"]: r for r in csv.DictReader(f)}
    with open(audit / "propositions_normalisation.csv", newline="", encoding="utf-8") as f:
        props = [r for r in csv.DictReader(f) if r["doc_id"] == doc["doc_id"]]
    props.sort(key=lambda r: (r["normalized_concept"], r["period_end"], r["period_start"]))
    lines = [f"Dépôt {doc['doc_type']} {accn}, accepté le {doc['accepted_at']} ; document : {doc['url']}", "",
             "| Concept du projet | Concept d'origine | Période | Valeur | Statut | Entrée brute (collecte) |",
             "|---|---|---|---|---|---|"]
    for r in props:
        period = f"{r['period_start']} → {r['period_end']}" if r["period_start"] else f"au {r['period_end']}"
        fact = facts[r["fact_id"]]
        if fact["reconciled"] == "auto" and fact["normalized_concept"]:
            status = f"normalisé, rapproché (auto), contexte {fact['source_context']}, decimals {fact['decimals']}"
            if fact["normalized_concept"] != r["normalized_concept"]:
                status = f"**{fact['normalized_concept']} par repli** ; " + status
        else:
            status = "proposé (document non lu)"
        value = f"{int(r['raw_value']):,}".replace(",", " ")
        lines.append(f"| {r['normalized_concept']} | {r['source_concept']} | {period} | {value} {r['source_unit']} | "
                     f"{status} | `{r['source_pointer']}` |")
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
