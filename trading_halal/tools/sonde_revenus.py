"""Sonde (réseau, hors paquet) : pour une liste d'émetteurs, lit le dernier 10-K et liste les concepts de revenu
déclarés pour l'entité entière sur l'exercice, afin de voir ce que ferait la règle de repli edgar_v3.
N'écrit que le rapport demandé ; aucune donnée n'entre dans un dossier d'audit.

  python3 tools/sonde_revenus.py --user-agent "Prénom Nom adresse@domaine" --out docs/SONDE_REVENUS.md 726728 19617 …
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edgar_collect as ec  # noqa: E402
import edgar_normalize as en  # noqa: E402

R1 = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
BLOCKERS = ["us-gaap:Revenues", "us-gaap:RevenueNotFromContractWithCustomer"]
RULES = Path(__file__).resolve().parents[1] / "config" / "normalisation" / "edgar_v6.json"
_R = {r["id"]: r for r in json.loads(RULES.read_text(encoding="utf-8"))["regles"]}
SPEC = _R["R1"]["repli_total"]["autres_revenus"]
PROOF_R1 = _R["R1"]["repli_total"]["preuve_position"]
PROOF_R0B = _R["R0b"]["preuve_position"]
R0B = "us-gaap:RegulatedAndUnregulatedOperatingRevenue"


def revenue_like(name: str) -> bool:
    return en.revenue_like(name, SPEC)


def probe(cik: str, ua: str) -> dict:
    c10 = ec.cik10(cik)
    sub = json.loads(ec._get(f"https://data.sec.gov/submissions/CIK{c10}.json", ua))
    rec = sub["filings"]["recent"]
    i = next(k for k, f in enumerate(rec["form"]) if f == "10-K")
    accn, doc, end = rec["accessionNumber"][i], rec["primaryDocument"][i], rec["reportDate"][i]
    url = f"https://www.sec.gov/Archives/edgar/data/{int(c10)}/{accn.replace('-', '')}/{doc}"
    time.sleep(0.3)
    data = ec._get(url, ua)
    base = url.rsplit("/", 1)[0] + "/"
    names = [x["name"] for x in json.loads(ec._get(base + "index.json", ua))["directory"]["item"]]
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / doc
        p.write_bytes(data)
        contexts, _, facts = en.parse_ixbrl(p)
        annexes = []
        for n in names:
            if n.endswith(".xsd") or n.endswith("_cal.xml"):
                time.sleep(0.2)
                (Path(tmp) / n).write_bytes(ec._get(base + n, ua))
                annexes.append(Path(tmp) / n)
        resolver = en.SchemaResolver(annexes, en.TAXO_DIR)
        roles, arcs = en.parse_calculations(annexes, resolver)
        missing = sorted(resolver.missing)
    rows, vals = {}, {}
    for f in facts:
        ctx = contexts.get(f["context"])
        if ctx is None or ctx["segment"] or ctx["end"] != end or not ctx["start"] or f["unit"] != "USD":
            continue
        if ctx["scheme"] != en.SEC_CIK_SCHEME or int(ctx["entity"]) != int(c10):
            continue
        # exercice : durée la plus longue se terminant à la date du rapport (environ un an)
        rows.setdefault(f["name"], set()).add((ctx["start"], f["text"], f["scale"]))
        try:
            vals.setdefault((f["name"], ctx["start"]), set()).add((en._ix_value(f["el"]), f["decimals"]))
        except ValueError:
            pass
    starts = sorted({s for v in rows.values() for s, _, _ in v})
    fy_start = starts[0] if starts else ""
    concepts = {n: [(t, sc) for s, t, sc in v if s == fy_start] for n, v in rows.items()}
    concepts = {n: v for n, v in concepts.items() if v and revenue_like(n)}
    has_r1 = R1 in concepts
    blocked = [b for b in BLOCKERS if b in concepts]
    others = sorted(n for n in concepts if n not in BLOCKERS + [R1, R0B])
    fyvals = {n: next(iter(v)) for (n, s), v in vals.items() if s == fy_start and len(v) == 1}
    proof_r1, why_r1 = en.position_proof(R1, roles, arcs, PROOF_R1, fyvals)
    proof_r0b, why_r0b = en.position_proof(R0B, roles, arcs, PROOF_R0B, fyvals) if R0B in concepts else (None, "")
    if "us-gaap:Revenues" in concepts:
        decision = "Revenues -> total"
    elif proof_r0b:
        decision = "RegulatedAndUnregulatedOperatingRevenue -> total"
    elif has_r1 and (blocked or others):
        decision = "repli R1 bloqué (autres revenus)"
    elif has_r1 and not proof_r1:
        decision = "repli R1 bloqué (aucune preuve positive" + (" : schémas officiels non disponibles)" if missing else ")")
    elif R0B in concepts and not proof_r0b and not has_r1:
        decision = "R0b non prouvé" + (" (schémas officiels non disponibles)" if missing else "")
    elif has_r1:
        decision = "REPLI R1 -> total (preuve positive)"
    else:
        decision = "aucun total"
    return {"cik": c10, "nom": sub.get("name"), "accn": accn, "exercice": f"{fy_start} → {end}", "decision": decision,
            "autres": {n: concepts[n][0] for n in others}, "r1": concepts.get(R1, [None])[0],
            "revenues": concepts.get("us-gaap:Revenues", [None])[0],
            "r0b": concepts.get(R0B, [None])[0], "preuve": proof_r1 or proof_r0b or "",
            "motif": why_r1 if has_r1 else why_r0b, "schemas_absents": missing}


def markdown(results: list[dict]) -> str:
    lines = ["# Sonde : que ferait la règle du revenu total (edgar_v6) sur de vrais 10-K ?", "",
             "Générée par `tools/sonde_revenus.py` (dernier 10-K de chaque émetteur à la date d'exécution, faits de l'entité",
             "entière, exercice complet, USD). Données brutes : `docs/SONDE_REVENUS.json`. Ni rapprochement ni",
             "normalisation : un repérage des cas où le repli R1 → total serait juste ou faux. Montants tels qu'affichés",
             "(souvent en millions).", "",
             "| Émetteur | Dépôt | Décision edgar_v6 | Revenues | R0b (réglementé) | R1 (contrats clients) | Autres concepts de revenu déclarés |",
             "|---|---|---|---|---|---|---|"]
    for x in results:
        if "erreur" in x:
            lines.append(f"| CIK {x['cik']} | — | ERREUR : {x['erreur'][:80]} | | | | |")
            continue
        autres = ", ".join(n.split("}")[-1] for n in x["autres"]) or "—"
        lines.append(f"| {x['nom']} | {x['accn']} | {x['decision']} | {x['revenues'][0] if x['revenues'] else '—'} | "
                     f"{x['r0b'][0] if x.get('r0b') else '—'} | {x['r1'][0] if x['r1'] else '—'} | {autres} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user-agent", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("cik", nargs="+")
    a = ap.parse_args(argv)
    ua = ec.check_user_agent(a.user_agent)
    results = []
    for cik in a.cik:
        try:
            results.append(probe(cik, ua))
        except Exception as exc:  # une sonde qui échoue est rapportée, jamais masquée
            results.append({"cik": cik, "erreur": f"{type(exc).__name__}: {exc}"})
        time.sleep(0.5)
    a.out.with_suffix(".json").write_text(json.dumps(results, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    a.out.write_text(markdown(results), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
