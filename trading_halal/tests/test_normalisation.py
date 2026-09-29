"""Normalisation EDGAR en deux temps (revue n° 13) : propositions depuis companyfacts, puis normalisation et
rapprochement à partir du document XBRL en ligne. Tout hors ligne ; document FICTIF pour le rapprochement."""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from pathlib import Path

from helpers import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import edgar_collect as ec  # noqa: E402
import edgar_normalize as en  # noqa: E402

from halal_sim.audit import audit_folder  # noqa: E402
from halal_sim.selection import load_audit, select_fact  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "edgar_FICTIF"
RULES_V1 = ROOT / "config" / "normalisation" / "edgar_v1.json"
RULES_V2 = ROOT / "config" / "normalisation" / "edgar_v2.json"
RULES_V3 = ROOT / "config" / "normalisation" / "edgar_v3.json"
RULES_V4 = ROOT / "config" / "normalisation" / "edgar_v4.json"
RULES_V5 = ROOT / "config" / "normalisation" / "edgar_v5.json"
RULES_V6 = ROOT / "config" / "normalisation" / "edgar_v6.json"
RULES_V7 = ROOT / "config" / "normalisation" / "edgar_v7.json"
R1C = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
K10 = "0000000123-0000000123-25-000004"
Q10 = "0000000123-0000000123-24-000030"
REV = "us-gaap:Revenues"


def _rules(tmp: Path, extra=(), name="regles.json") -> Path:
    rules = {"version": "test_v2", "regles": [
        {"id": "T1", "source_concept": REV, "normalized_concept": "total_revenue", "source_unit": "USD",
         "period_type": "duration", "justification": "Revenu total (règle de test)."}, *extra]}
    p = tmp / name
    p.write_text(json.dumps(rules), encoding="utf-8")
    return p


def ixbrl(facts, cik="0000000123") -> str:
    """Document XBRL en ligne minimal mais conforme à la structure SEC (FICTIF).
    facts : (concept, contexte, unité, texte, échelle, decimals, signe) ; contextes prédéfinis ci-dessous."""
    ctx = {
        "c-1": ("2024-01-01", "2024-12-31", False), "c-2": ("2023-01-01", "2023-12-31", False),
        "c-3": ("2024-01-01", "2024-12-31", True), "c-4": ("", "2025-02-14", False),
    }
    contexts = []
    for cid, (start, end, seg) in ctx.items():
        period = (f"<xbrli:startDate>{start}</xbrli:startDate><xbrli:endDate>{end}</xbrli:endDate>" if start
                  else f"<xbrli:instant>{end}</xbrli:instant>")
        segment = ("<xbrli:segment><xbrldi:explicitMember dimension=\"srt:ProductOrServiceAxis\">fx:WidgetMember"
                   "</xbrldi:explicitMember></xbrli:segment>" if seg else "")
        contexts.append(f"<xbrli:context id=\"{cid}\"><xbrli:entity><xbrli:identifier scheme=\"http://www.sec.gov/CIK\">"
                        f"{cik}</xbrli:identifier>{segment}</xbrli:entity><xbrli:period>{period}</xbrli:period>"
                        "</xbrli:context>")
    body = []
    for i, (concept, cid, unit, text, scale, decimals, sign) in enumerate(facts):
        s = f' sign="-"' if sign else ""
        body.append(f'<p>{concept} : <ix:nonFraction id="f-{i}" name="{concept}" contextRef="{cid}" unitRef="{unit}" '
                    f'decimals="{decimals}" scale="{scale}" format="ixt:num-dot-decimal"{s}>{text}</ix:nonFraction></p>')
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" '
            'xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:xbrldi="http://xbrl.org/2006/xbrldi" '
            'xmlns:iso4217="http://www.xbrl.org/2003/iso4217" '
            'xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2020-02-12" '
            'xmlns:us-gaap="http://fasb.org/us-gaap/2024" xmlns:dei="http://xbrl.sec.gov/dei/2024" '
            'xmlns:srt="http://fasb.org/srt/2024" xmlns:fx="http://exemple.invalid/fictif">'
            '<head><title>FICTIF</title></head><body><div style="display:none"><ix:header><ix:resources>'
            + "".join(contexts) +
            '<xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '<xbrli:unit id="shares"><xbrli:measure>xbrli:shares</xbrli:measure></xbrli:unit>'
            '<xbrli:unit id="pure"><xbrli:measure>xbrli:pure</xbrli:measure></xbrli:unit>'
            '<xbrli:unit id="eur"><xbrli:measure>iso4217:EUR</xbrli:measure></xbrli:unit>'
            '</ix:resources></ix:header></div>' + "".join(body) + "</body></html>")


GOOD = [("us-gaap:Revenues", "c-1", "usd", "1,250", "6", "-6", False),
        ("us-gaap:Revenues", "c-2", "usd", "1,100", "6", "-6", False),
        ("us-gaap:Revenues", "c-3", "usd", "800", "6", "-6", False),          # ventilé : ignoré
        ("dei:EntityCommonStockSharesOutstanding", "c-4", "shares", "48,000,000", "0", "INF", False)]


STATEMENT = "0000004 - Statement - CONSOLIDATED STATEMENTS OF OPERATIONS"


def calc_annexes(folder: Path, parent="us-gaap:GrossProfit",
                 children=((R1C, 1.0), ("us-gaap:CostOfRevenue", -1.0)), role_def=STATEMENT,
                 arcrole="http://www.xbrl.org/2003/arcrole/summation-item", schema_url=None) -> list[Path]:
    """Schéma et fichier de calcul FICTIFS au format d'un dépôt SEC."""
    def href(c):
        prefix, local = c.split(":")
        return f"{schema_url or f'https://xbrl.fasb.org/{prefix}/2024/elts/{prefix}-2024.xsd'}#{prefix}_{local}"
    xsd = folder / "fxei-20241231.xsd"
    xsd.write_text('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:link="http://www.xbrl.org/2003/linkbase" '
                   'targetNamespace="http://exemple.invalid/fxei"><xs:annotation><xs:appinfo>'
                   '<link:roleType roleURI="http://exemple.invalid/role/Operations" id="Operations">'
                   f'<link:definition>{role_def}</link:definition></link:roleType></xs:appinfo></xs:annotation></xs:schema>',
                   encoding="utf-8")
    locs = "".join(f'<link:loc xlink:type="locator" xlink:label="l{i}" xlink:href="{href(c)}"/>'
                   for i, c in enumerate([parent] + [c for c, _ in children]))
    arcs = "".join(f'<link:calculationArc xlink:type="arc" xlink:arcrole="{arcrole}" xlink:from="l0" xlink:to="l{i}" '
                   f'weight="{w}"/>' for i, (_, w) in enumerate(children, start=1))
    cal = folder / "fxei-20241231_cal.xml"
    cal.write_text('<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink">'
                   '<link:calculationLink xlink:type="extended" xlink:role="http://exemple.invalid/role/Operations">'
                   f'{locs}{arcs}</link:calculationLink></link:linkbase>', encoding="utf-8")
    return [xsd, cal]


US_GAAP_2024 = "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-2024.xsd"
TAXO_ELEMENTS = ["RevenuesNetOfInterestExpense", "InterestIncomeExpenseNet", "NoninterestIncome", "GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss", "CostOfRevenue", "OtherIncome",
                 "RevenueFromContractWithCustomerExcludingAssessedTax", "RegulatedAndUnregulatedOperatingRevenue",
                 "GainLossOnDispositionOfAssets1", "CostsAndExpenses", "Revenues", "OtherOperatingRevenue",
                 "OperatingExpenses"]


def fake_taxonomy(cache: Path, ids: dict | None = None, extra_xml: str = "") -> Path:
    """Schéma us-gaap FICTIF (sous-ensemble) dans un cache au format de collecte/taxonomies. `ids` : nom -> id."""
    ids = ids or {}
    els = "".join(f'<xs:element id="{ids.get(n, "us-gaap_" + n)}" name="{n}" type="xs:decimal"/>'
                  for n in TAXO_ELEMENTS) + extra_xml
    rel = "xbrl.fasb.org/us-gaap/2024/elts/us-gaap-2024.xsd"
    (cache / rel).parent.mkdir(parents=True, exist_ok=True)
    (cache / rel).write_text('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" '
                             f'targetNamespace="http://fasb.org/us-gaap/2024">{els}</xs:schema>', encoding="utf-8")
    (cache / en.TAXO_MANIFEST).write_text(json.dumps([{"url": US_GAAP_2024, "fichier": rel,
                                                       "sha256": en._sha(cache / rel), "obtenu": "FICTIF"}]),
                                          encoding="utf-8")
    return cache


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.raw = self.tmp / "raw"
        self.raw.mkdir()
        self.mutate_raw(lambda cf: None)
        self.out = self.tmp / "audit"
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        self.rules = _rules(self.tmp)
        self.taxo = fake_taxonomy(self.tmp / "taxo")

    def mutate_raw(self, cf_fn):
        log = []
        for kind in ("submissions", "companyfacts"):
            name = f"{kind}_CIK0000000123.json"
            data = json.loads((FIX / name).read_text(encoding="utf-8"))
            if kind == "companyfacts":
                cf_fn(data)
            (self.raw / name).write_text(json.dumps(data), encoding="utf-8")
            log.append({"kind": kind, "cik": "0000000123", "url": f"https://data.sec.gov/{kind}", "file": name,
                        "retrieved_at": "2026-09-28T10:00:00+00:00",
                        "sha256": hashlib.sha256((self.raw / name).read_bytes()).hexdigest()})
        (self.raw / "journal_collecte.json").write_text(json.dumps(log), encoding="utf-8")

    def facts(self):
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            return {r["fact_id"]: r for r in csv.DictReader(f)}

    def fact(self, doc, end, start=""):
        return next(r for r in self.facts().values() if r["doc_id"] == doc and r["source_concept"] == REV
                    and r["period_end"] == end and (not start or r["period_start"] == start))

    def import_doc(self, content=None, annexes=None):
        src = self.tmp / "fxei-10k.htm"
        src.write_text(content or ixbrl(GOOD), encoding="utf-8")
        return en.import_filing(self.out, K10, src, "2026-09-28T14:05:00+02:00", self.raw, annexes=annexes)

    def reconcile(self, content=None, annexes=None):
        en.normalize(self.raw, self.out, self.rules)
        self.import_doc(content, annexes)
        return en.reconcile_ixbrl(self.out, K10, self.raw, self.rules, self.taxo)


class ProposalTests(Base):
    def test_normalize_only_proposes(self):
        before = (self.out / "facts.csv").read_bytes()
        rep = en.normalize(self.raw, self.out, self.rules)
        self.assertEqual(rep["propositions"], {"total_revenue": 3})
        self.assertEqual((self.out / "facts.csv").read_bytes(), before)
        self.assertFalse((self.out / ec.SAISIES_FILE).exists())
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        self.assertIn("aucun fait normalisé", audit_folder(self.out).verdict)
        with open(self.out / en.PROPOSALS_FILE, newline="", encoding="utf-8") as f:
            props = list(csv.DictReader(f))
        self.assertEqual({p["period_end"] for p in props}, {"2024-12-31", "2023-12-31", "2024-09-30"})

    def test_second_run_is_identical(self):
        en.normalize(self.raw, self.out, self.rules)
        first = (self.out / en.PROPOSALS_FILE).read_bytes()
        en.normalize(self.raw, self.out, self.rules)
        self.assertEqual((self.out / en.PROPOSALS_FILE).read_bytes(), first)

    def test_share_rules_are_refused(self):
        shares = _rules(self.tmp, [{"id": "T2", "source_concept": "dei:EntityCommonStockSharesOutstanding",
                                    "normalized_concept": "shares_outstanding", "source_unit": "shares",
                                    "period_type": "instant", "justification": "x"}], "actions.json")
        for rules in (shares, RULES_V1):
            with self.assertRaises(en.NormalizeError):
                en.normalize(self.raw, self.out, rules)

    def test_conflicting_source_concepts_are_not_proposed(self):
        def add_conflict(cf):
            cf["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
                "label": "Rev", "description": "d", "units": {"USD": [
                    {"start": "2024-01-01", "end": "2024-12-31", "val": 1240000000, "accn": "0000000123-25-000004",
                     "form": "10-K", "filed": "2025-02-20"}]}}
        self.mutate_raw(add_conflict)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"}, replace=True)
        rules = _rules(self.tmp, [{"id": "T3", "source_concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                                   "normalized_concept": "total_revenue", "source_unit": "USD",
                                   "period_type": "duration", "justification": "test"}], "conflit.json")
        rep = en.normalize(self.raw, self.out, rules)
        self.assertEqual(len(rep["conflits"]), 1)
        self.assertEqual(rep["propositions"], {"total_revenue": 2})

    def test_refuses_a_folder_that_does_not_verify(self):
        text = (self.out / "facts.csv").read_text(encoding="utf-8")
        (self.out / "facts.csv").write_text(text.replace("1250000000", "1250000001", 1), encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.normalize(self.raw, self.out, self.rules)


def _rules_v3_like(tmp: Path) -> Path:
    rules = {"version": "test_v3", "regles": [
        {"id": "R0", "source_concept": REV, "normalized_concept": "total_revenue", "source_unit": "USD",
         "period_type": "duration", "justification": "agrégat"},
        {"id": "R1", "source_concept": R1C, "normalized_concept": "revenue_from_contracts_with_customers",
         "source_unit": "USD", "period_type": "duration", "justification": "composant",
         "repli_total": {"concept": "total_revenue",
                         "si_absents_du_document": [REV, "us-gaap:RevenueNotFromContractWithCustomer"],
                         "autres_revenus": {"motifs": ["Revenue", "InterestAndDividendIncome", "NoninterestIncome"],
                                            "exclusions": ["CostOf", "IncomeTax"]},
                         "preuve_position": {"categorie": "Statement",
                                             "parents": ["us-gaap:GrossProfit", "us-gaap:OperatingIncomeLoss"]}}},
        {"id": "R0b", "source_concept": "us-gaap:RegulatedAndUnregulatedOperatingRevenue",
         "normalized_concept": "total_revenue", "source_unit": "USD", "period_type": "duration", "justification": "t",
         "preuve_position": {"categorie": "Statement", "parents": ["us-gaap:OperatingIncomeLoss"],
                             "freres_positifs_interdits": False,
                             "freres_revenus": {"motifs": ["Revenue"], "exclusions": ["CostOf"]}}}]}
    p = tmp / "v3.json"
    p.write_text(json.dumps(rules), encoding="utf-8")
    return p


def with_gross_profit(doc_facts, cost=700):
    """Ajoute coût des ventes et marge brute (contexte c-1) cohérents avec R1, pour le calcul effectif."""
    r1 = next((f for f in doc_facts if f[0] == R1C and f[1] == "c-1"), None)
    if r1 is None:
        return doc_facts
    gp = int(r1[3].replace(",", "")) - cost
    return list(doc_facts) + [("us-gaap:CostOfRevenue", "c-1", "usd", f"{cost:,}", "6", "-6", False),
                              ("us-gaap:GrossProfit", "c-1", "usd", f"{gp:,}", "6", "-6", False)]


def _add_r1(value, drop_revenues=False):
    def fn(cf):
        if drop_revenues:
            del cf["facts"]["us-gaap"]["Revenues"]
        cf["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
            "label": "R1", "description": "d", "units": {"USD": [
                {"start": "2024-01-01", "end": "2024-12-31", "val": value, "accn": "0000000123-25-000004",
                 "form": "10-K", "filed": "2025-02-20"}]}}
    return fn


class TotalAndComponentTests(Base):
    """Revue n° 14 : un composant (contrats clients) n'est jamais le total s'il existe un agrégat."""

    def run_case(self, cf_fn, doc_facts, annexes="preuve"):
        self.mutate_raw(cf_fn)
        shutil.rmtree(self.out)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        self.rules = _rules_v3_like(self.tmp)
        if annexes == "preuve":
            d = self.tmp / "annexes"
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir()
            annexes = calc_annexes(d)
            doc_facts = with_gross_profit(doc_facts)
        rep = self.reconcile(ixbrl(doc_facts), annexes)
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        self.assertEqual(audit_folder(self.out).errors, [])
        self.assertEqual(en.verify_normalisation(self.raw, self.out, self.rules, self.taxo), ([], []))
        return rep, {(r["source_concept"], r["period_end"]): r for r in self.facts().values()
                     if r["normalized_concept"] and r["period_start"] == "2024-01-01"}

    def test_aggregate_and_component_are_both_kept_without_conflict(self):
        rep, n = self.run_case(_add_r1(1240000000), GOOD + [(R1C, "c-1", "usd", "1,240", "6", "-6", False)])
        self.assertEqual(n[(REV, "2024-12-31")]["normalized_concept"], "total_revenue")
        self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertEqual(n[(R1C, "2024-12-31")]["value"], "1240000000")

    def test_component_is_total_only_by_explicit_fallback(self):
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False)])
        f = n[(R1C, "2024-12-31")]
        self.assertEqual(f["normalized_concept"], "total_revenue")
        self.assertTrue(f["normalization_justification"].startswith("REPLI :"))

    def test_fallback_is_blocked_by_revenue_outside_contracts(self):
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                ("us-gaap:RevenueNotFromContractWithCustomer", "c-1", "usd", "10", "6", "-6", False)])
        self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "revenue_from_contracts_with_customers")

    def test_fallback_is_blocked_by_an_aggregate_absent_from_companyfacts(self):
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                (REV, "c-1", "usd", "1,300", "6", "-6", False)])
        self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "revenue_from_contracts_with_customers")

    def test_fallback_is_blocked_by_any_other_revenue_concept(self):
        for other in ("us-gaap:InterestAndDividendIncomeOperating", "us-gaap:NoninterestIncome",
                      "us-gaap:RevenuesNetOfInterestExpense"):
            with self.subTest(other):
                rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                                       [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                        (other, "c-1", "usd", "300", "6", "-6", False)])
                self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "revenue_from_contracts_with_customers")
                self.assertTrue(any(other in b for b in rep["replis_bloques"]))

    def test_non_revenue_or_other_period_or_dimensional_concepts_do_not_block(self):
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                ("us-gaap:CostOfRevenue", "c-1", "usd", "700", "6", "-6", False),
                                ("us-gaap:NoninterestIncome", "c-2", "usd", "5", "6", "-6", False),
                                ("us-gaap:NoninterestIncome", "c-3", "usd", "5", "6", "-6", False)])
        self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "total_revenue")

    def test_revenue_in_any_currency_blocks_but_a_ratio_does_not(self):
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                ("us-gaap:NoninterestIncome", "c-1", "eur", "40", "6", "-6", False)])
        self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "revenue_from_contracts_with_customers")
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                ("fx:RevenueGrowthPercent", "c-1", "pure", "12", "0", "INF", False)])
        self.assertEqual(n[(R1C, "2024-12-31")]["normalized_concept"], "total_revenue")

    def _proof_case(self, doc_extra=None, facts=None, **kw):
        d = self.tmp / "annexes"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir()
        doc = facts if facts is not None else with_gross_profit([(R1C, "c-1", "usd", "1,250", "6", "-6", False)])
        rep, n = self.run_case(_add_r1(1250000000, drop_revenues=True), doc + (doc_extra or []),
                               annexes=calc_annexes(d, **kw))
        self.last_rep = rep
        return rep, n[(R1C, "2024-12-31")]

    def test_review_15_fallback_requires_positive_proof(self):
        rep, f = self._proof_case()
        self.assertEqual(f["normalized_concept"], "total_revenue")
        self.assertIn("preuve positive : rôle « Statement - CONSOLIDATED STATEMENTS OF OPERATIONS »",
                      f["normalization_justification"])
        self.assertIn("fxei-20241231_cal.xml (sha256", f["normalization_justification"])

    def test_no_calculation_files_means_no_fallback(self):
        rep, f = self.run_case(_add_r1(1250000000, drop_revenues=True),
                               [(R1C, "c-1", "usd", "1,250", "6", "-6", False)], annexes=None)
        self.assertEqual(f[(R1C, "2024-12-31")]["normalized_concept"] if False else
                         self.facts_by(R1C)["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertTrue(any("aucune preuve positive" in b for b in rep["replis_bloques"]))

    def facts_by(self, concept):
        return next(r for r in self.facts().values() if r["source_concept"] == concept
                    and r["period_start"] == "2024-01-01" and r["doc_id"] == K10)

    def test_proof_must_come_from_a_statement_with_no_other_positive_item(self):
        for kw in ({"role_def": "0000040 - Disclosure - Revenue"},
                   {"children": ((R1C, 1.0), ("us-gaap:OtherIncome", 1.0), ("us-gaap:CostOfRevenue", -1.0))},
                   {"parent": "us-gaap:NetIncomeLoss"},
                   {"children": ((R1C, -1.0), ("us-gaap:CostOfRevenue", -1.0))}):
            with self.subTest(kw):
                rep, f = self._proof_case(**kw)
                self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")

    def test_other_arcroles_and_non_fasb_schemas_prove_nothing(self):
        for kw in ({"arcrole": "http://exemple.invalid/arcrole/autre"},
                   {"schema_url": "fxei-20241231.xsd"}):
            with self.subTest(kw):
                rep, f = self._proof_case(**kw)
                self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")

    def test_review_16_misleading_absent_or_ambiguous_ids_prove_nothing(self):
        cases = {"préfixe trompeur": {"ids": {"OperatingExpenses": "us-gaap_GrossProfit",
                                              "GrossProfit": "us-gaap_GrossProfitReel"}},
                 "identifiant absent": {"ids": {"GrossProfit": "autre_id"}},
                 "identifiant en double": {"extra_xml": '<xs:element id="us-gaap_GrossProfit" name="Autre"/>'}}
        for label, kw in cases.items():
            with self.subTest(label):
                shutil.rmtree(self.tmp / "taxo")
                self.taxo = fake_taxonomy(self.tmp / "taxo", **kw)
                rep, f = self._proof_case()
                self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")

    def test_review_16_standard_schema_missing_or_altered(self):
        shutil.rmtree(self.tmp / "taxo")
        (self.tmp / "taxo").mkdir()
        rep, f = self._proof_case()  # cache vide : fail-closed
        self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertTrue(any("schémas non disponibles" in b and US_GAAP_2024 in b for b in rep["replis_bloques"]))
        self.taxo = fake_taxonomy(self.tmp / "taxo")
        schema = self.taxo / "xbrl.fasb.org/us-gaap/2024/elts/us-gaap-2024.xsd"
        schema.write_text(schema.read_text(encoding="utf-8").replace("GrossProfit", "GrossProfiT"), encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "empreinte"):
            self._proof_case()

    def test_review_16_r1_under_operating_income_with_another_positive_contributor(self):
        rep, f = self._proof_case(parent="us-gaap:OperatingIncomeLoss",
                                  children=((R1C, 1.0), ("us-gaap:OtherIncome", 1.0), ("us-gaap:CostsAndExpenses", -1.0)),
                                  facts=[(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                         ("us-gaap:OtherIncome", "c-1", "usd", "10", "6", "-6", False),
                                         ("us-gaap:CostsAndExpenses", "c-1", "usd", "1,000", "6", "-6", False),
                                         ("us-gaap:OperatingIncomeLoss", "c-1", "usd", "260", "6", "-6", False)])
        self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")

    def test_effective_calculation_must_hold_for_the_period(self):
        rep, f = self._proof_case(facts=[(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                         ("us-gaap:CostOfRevenue", "c-1", "usd", "700", "6", "-6", False),
                                         ("us-gaap:GrossProfit", "c-1", "usd", "555", "6", "-6", False)])
        # (551 serait admis : trois arrondis au million, tolérance d'intervalle de 1,5 M$, comme XBRL Calculation 1.1)
        self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertTrue(any("calcul_XBRL_coherent=non" in b for b in rep["replis_bloques"]))
        rep, f = self._proof_case(facts=[(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                         ("us-gaap:GrossProfit", "c-1", "usd", "550", "6", "-6", False)])
        self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertTrue(any("calcul_XBRL_coherent=non évaluable" in b or "preuve_complete_pour_repli=non" in b
                            for b in rep["replis_bloques"]))
        rep, f = self._proof_case()
        self.assertIn("calcul_XBRL_coherent=oui ; preuve_complete_pour_repli=oui", f["normalization_justification"])
        self.assertIn(US_GAAP_2024, f["normalization_justification"])

    def test_review_17_coherent_but_incomplete_is_not_a_proof(self):
        kids = ((R1C, 1.0), ("us-gaap:CostOfRevenue", -1.0), ("us-gaap:OperatingExpenses", -1.0))
        base = [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                ("us-gaap:CostOfRevenue", "c-1", "usd", "700", "6", "-6", False),
                ("us-gaap:GrossProfit", "c-1", "usd", "550", "6", "-6", False)]
        rep, f = self._proof_case(children=kids, facts=base)            # OperatingExpenses absent
        self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertTrue(any("calcul_XBRL_coherent=oui ; preuve_complete_pour_repli=non" in b
                            for b in rep["replis_bloques"]))

    def test_review_17_nil_contributor_does_not_participate(self):
        kids = ((R1C, 1.0), ("us-gaap:CostOfRevenue", -1.0), ("us-gaap:OperatingExpenses", -1.0))
        facts = [(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                 ("us-gaap:CostOfRevenue", "c-1", "usd", "700", "6", "-6", False),
                 ("us-gaap:GrossProfit", "c-1", "usd", "550", "6", "-6", False)]
        rep, f = self._proof_case(children=kids, facts=facts, doc_extra=[])
        # même fait, mais déclaré nil dans le document
        doc = ixbrl(facts + [("us-gaap:OperatingExpenses", "c-1", "usd", "0", "6", "-6", False)]).replace(
            'name="us-gaap:OperatingExpenses"', 'name="us-gaap:OperatingExpenses" xsi:nil="true"').replace(
            "<html ", '<html xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ', 1)
        self.mutate_raw(_add_r1(1250000000, drop_revenues=True))
        shutil.rmtree(self.out)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        d = self.tmp / "annexes"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir()
        rep = self.reconcile(doc, calc_annexes(d, children=kids))
        self.assertTrue(any("preuve_complete_pour_repli=non" in b for b in rep["replis_bloques"]))

    def test_review_17_nil_duplicate_is_ignored_and_value_counts(self):
        facts = with_gross_profit([(R1C, "c-1", "usd", "1,250", "6", "-6", False)])
        doc = ixbrl(facts + [("us-gaap:CostOfRevenue", "c-1", "usd", "0", "6", "-6", False)]).replace(
            'id="f-3" name="us-gaap:CostOfRevenue"', 'id="f-3" name="us-gaap:CostOfRevenue" xsi:nil="true"').replace(
            "<html ", '<html xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ', 1)
        self.assertIn('xsi:nil="true"', doc)
        self.mutate_raw(_add_r1(1250000000, drop_revenues=True))
        shutil.rmtree(self.out)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        self.rules = _rules_v3_like(self.tmp)
        d = self.tmp / "annexes"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir()
        self.reconcile(doc, calc_annexes(d))
        self.assertEqual(self.facts_by(R1C)["normalized_concept"], "total_revenue")

    def test_review_17_digits_beyond_declared_precision_are_refused(self):
        rep, f = self._proof_case(facts=[(R1C, "c-1", "usd", "1,250", "6", "-6", False),
                                         ("us-gaap:CostOfRevenue", "c-1", "usd", "700.4", "6", "-6", False),
                                         ("us-gaap:GrossProfit", "c-1", "usd", "550", "6", "-6", False)])
        self.assertEqual(f["normalized_concept"], "revenue_from_contracts_with_customers")
        self.assertTrue(en.within_precision(Decimal("700000000"), "-6"))
        self.assertFalse(en.within_precision(Decimal("700400000"), "-6"))
        self.assertTrue(en.within_precision(Decimal("700400000"), "INF"))

    def test_not_evaluable_is_distinct_from_incoherent(self):
        vals = {"a": (Decimal(60), "0")}
        self.assertIsNone(en.calculation_verdicts("T", [("a", 1.0)], vals)[0])          # total absent
        self.assertIsNone(en.calculation_verdicts("T", [("x", 1.0)], {"T": (Decimal(1), "0")})[0])  # aucun contributeur
        self.assertIs(en.calculation_verdicts("T", [("a", 1.0)], {"T": (Decimal(1), "0"), **vals})[0], False)

    def test_calculation_verdicts_unit(self):
        vals = {"T": (Decimal(100), "0"), "a": (Decimal(60), "0"), "b": (Decimal(40), "0")}
        self.assertEqual(en.calculation_verdicts("T", [("a", 1.0), ("b", 1.0)], vals)[:2], (True, True))
        self.assertEqual(en.calculation_verdicts("T", [("a", 1.0), ("c", 1.0)], vals)[:2], (False, False))
        self.assertEqual(en.calculation_verdicts("T", [("a", 1.0), ("b", 1.0), ("c", 1.0)], vals)[:2], (True, False))
        self.assertEqual(en.calculation_verdicts("X", [("a", 1.0)], vals)[:2], (None, False))
        # tolérance : trois montants au million près ⇒ 1,5 M
        m = {"T": (Decimal(551_000_000), "-6"), "a": (Decimal(1_250_000_000), "-6"), "b": (Decimal(700_000_000), "-6")}
        self.assertTrue(en.calculation_verdicts("T", [("a", 1.0), ("b", -1.0)], m)[0])

    def test_review_17_bank_revenue_is_typed_and_never_total(self):
        RN = "us-gaap:RevenuesNetOfInterestExpense"
        def cf(data):
            data["facts"]["us-gaap"]["RevenuesNetOfInterestExpense"] = {
                "label": "RN", "description": "d", "units": {"USD": [
                    {"start": "2024-01-01", "end": "2024-12-31", "val": 900000000, "accn": "0000000123-25-000004",
                     "form": "10-K", "filed": "2025-02-20"}]}}
            del data["facts"]["us-gaap"]["Revenues"]
        rules = json.loads(_rules_v3_like(self.tmp).read_text(encoding="utf-8"))
        rules["regles"].append({"id": "R0c", "source_concept": RN, "normalized_concept": "revenues_net_of_interest_expense",
                                "source_unit": "USD", "period_type": "duration", "justification": "banque",
                                "preuve_presence": {"categorie": "Statement"}})
        doc = [(RN, "c-1", "usd", "900", "6", "-6", False),
               ("us-gaap:InterestIncomeExpenseNet", "c-1", "usd", "500", "6", "-6", False),
               ("us-gaap:NoninterestIncome", "c-1", "usd", "400", "6", "-6", False)]
        kids = (("us-gaap:InterestIncomeExpenseNet", 1.0), ("us-gaap:NoninterestIncome", 1.0))
        for role_def, expected in ((STATEMENT, "revenues_net_of_interest_expense"),
                                   ("0000040 - Disclosure - Revenus", None), (None, None)):
            with self.subTest(role_def):
                self.mutate_raw(cf)
                shutil.rmtree(self.out)
                ec.convert(self.raw, self.out, {"10-K", "10-Q"})
                p = self.tmp / "banque.json"
                p.write_text(json.dumps(rules), encoding="utf-8")
                self.rules = p
                d = self.tmp / "annexes"
                shutil.rmtree(d, ignore_errors=True)
                d.mkdir()
                ann = calc_annexes(d, parent=RN, children=kids, role_def=role_def) if role_def else None
                self.reconcile(ixbrl(doc), ann)
                f = next(r for r in self.facts().values() if r["source_concept"] == RN)
                self.assertEqual(f["normalized_concept"] or None, expected)
                self.assertNotEqual(f["normalized_concept"], "total_revenue")
        # décision revue n° 17 (b) : le calcul de l'état doit aussi être cohérent et complet pour la période
        for label, facts in (("contributeur absent", doc[:2]),
                             ("incohérent", [doc[0], doc[1], ("us-gaap:NoninterestIncome", "c-1", "usd", "450", "6",
                                                               "-6", False)])):
            with self.subTest(label):
                self.mutate_raw(cf)
                shutil.rmtree(self.out)
                ec.convert(self.raw, self.out, {"10-K", "10-Q"})
                d = self.tmp / "annexes"
                shutil.rmtree(d, ignore_errors=True)
                d.mkdir()
                rep = self.reconcile(ixbrl(facts), calc_annexes(d, parent=RN, children=kids))
                self.assertEqual(next(r for r in self.facts().values() if r["source_concept"] == RN)
                                 ["normalized_concept"], "")
                self.assertTrue(any("preuve_complete=non" in e for e in rep["echecs"]))
        # un contributeur non résolu dans le calcul : pas de présence prouvée
        self.mutate_raw(cf)
        shutil.rmtree(self.out)
        ec.convert(self.raw, self.out, {"10-K", "10-Q"})
        d = self.tmp / "annexes"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir()
        self.reconcile(ixbrl(doc), calc_annexes(d, parent=RN, children=kids + (("us-gaap:Inconnu", 1.0),)))
        self.assertEqual(next(r for r in self.facts().values() if r["source_concept"] == RN)["normalized_concept"], "")
        bad = dict(rules)
        bad["regles"] = rules["regles"][:-1] + [dict(rules["regles"][-1], normalized_concept="total_revenue")]
        p.write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "total_revenue"):
            en.normalize(self.raw, self.out, p)

    def test_calculation_1_1_arcrole_is_accepted(self):
        rep, f = self._proof_case(arcrole="https://xbrl.org/2023/arcrole/summation-item")
        self.assertEqual(f["normalized_concept"], "total_revenue")

    def test_direct_total_needs_position_but_admits_a_positive_gain(self):
        RR = "us-gaap:RegulatedAndUnregulatedOperatingRevenue"
        def cf(data):
            data["facts"]["us-gaap"]["RegulatedAndUnregulatedOperatingRevenue"] = {
                "label": "R0b", "description": "d", "units": {"USD": [
                    {"start": "2024-01-01", "end": "2024-12-31", "val": 1300000000, "accn": "0000000123-25-000004",
                     "form": "10-K", "filed": "2025-02-20"}]}}
            del data["facts"]["us-gaap"]["Revenues"]
        doc = [(RR, "c-1", "usd", "1,300", "6", "-6", False),
               ("us-gaap:CostsAndExpenses", "c-1", "usd", "1,000", "6", "-6", False),
               ("us-gaap:GainLossOnDispositionOfAssets1", "c-1", "usd", "50", "6", "-6", False)]
        d = self.tmp / "annexes"
        for kids, oi, expected in ((((RR, 1.0), ("us-gaap:GainLossOnDispositionOfAssets1", 1.0),
                                     ("us-gaap:CostsAndExpenses", -1.0)), "350", "total_revenue"),
                                   (((RR, 1.0), ("us-gaap:CostsAndExpenses", -1.0)), "300", "total_revenue")):
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir()
            rep, n = self.run_case(cf, doc + [("us-gaap:OperatingIncomeLoss", "c-1", "usd", oi, "6", "-6", False)],
                                   annexes=calc_annexes(d, parent="us-gaap:OperatingIncomeLoss", children=kids))
            self.assertEqual(n[(RR, "2024-12-31")]["normalized_concept"], expected)
        # revue n° 16 : un second revenu au même niveau bloque R0b
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir()
        rep, n = self.run_case(cf, doc + [("us-gaap:OtherOperatingRevenue", "c-1", "usd", "20", "6", "-6", False),
                                          ("us-gaap:OperatingIncomeLoss", "c-1", "usd", "320", "6", "-6", False)],
                               annexes=calc_annexes(d, parent="us-gaap:OperatingIncomeLoss",
                                                    children=((RR, 1.0), ("us-gaap:OtherOperatingRevenue", 1.0),
                                                              ("us-gaap:CostsAndExpenses", -1.0))))
        self.assertNotIn((RR, "2024-12-31"), n)
        self.assertTrue(any("autre revenu au même niveau" in e for e in rep["echecs"]))
        rep, n = self.run_case(cf, doc, annexes=None)  # sans calculs : pas de total direct non plus
        self.assertNotIn((RR, "2024-12-31"), n)
        self.assertTrue(any("position non prouvée" in e for e in rep["echecs"]))

    def test_tampered_annex_is_refused(self):
        self._proof_case()
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            local = next(r for r in csv.DictReader(f) if r["doc_id"] == K10)["local_copy"]
        cal = (self.out / local).parent / "fxei-20241231_cal.xml"
        cal.write_text(cal.read_text(encoding="utf-8").replace('weight="-1.0"', 'weight="1.0"'), encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "annexe"):
            en.verify_normalisation(self.raw, self.out, self.rules, self.taxo)

    def test_lax_direct_total_without_revenue_sibling_block_is_refused(self):
        p = _rules_v3_like(self.tmp)
        data = json.loads(p.read_text(encoding="utf-8"))
        data["regles"][2]["preuve_position"].pop("freres_revenus")
        p.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "freres_revenus"):
            en.normalize(self.raw, self.out, p)

    def test_fallback_rules_without_strict_proof_are_refused(self):
        for mutate in (lambda r: r["repli_total"].pop("preuve_position"),
                       lambda r: r["repli_total"]["preuve_position"].update(freres_positifs_interdits=False),
                       lambda r: r["repli_total"]["preuve_position"].update(categorie="Disclosure")):
            p = _rules_v3_like(self.tmp)
            data = json.loads(p.read_text(encoding="utf-8"))
            mutate(data["regles"][1])
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(en.NormalizeError):
                en.normalize(self.raw, self.out, p)

    def test_patterns_that_miss_the_rule_concepts_are_refused(self):
        p = _rules_v3_like(self.tmp)
        data = json.loads(p.read_text(encoding="utf-8"))
        data["regles"][1]["repli_total"]["autres_revenus"]["exclusions"].append("Tax")  # écarterait R1 lui-même
        p.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "incohérents"):
            en.normalize(self.raw, self.out, p)

    def test_audit_accepts_a_mapping_exception_only_as_declared_fallback(self):
        self.run_case(_add_r1(1250000000, drop_revenues=True), [(R1C, "c-1", "usd", "1,250", "6", "-6", False)])
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        row = next(r for r in rows if r["normalization_justification"].startswith("REPLI :"))
        row["normalization_justification"] = row["normalization_justification"].replace("REPLI :", "Note :", 1)
        with open(self.out / "facts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertTrue(any("contraire au mappage" in e for e in audit_folder(self.out).errors))

    def test_malformed_fallback_rule_is_refused(self):
        p = _rules_v3_like(self.tmp)
        data = json.loads(p.read_text(encoding="utf-8"))
        data["regles"][1]["repli_total"]["concept"] = "total_assets"
        p.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.normalize(self.raw, self.out, p)


class NamespaceHardeningTests(Base):
    """Défense en profondeur (revue n° 14) : QNames par URI, devise ISO 4217, identifiant CIK SEC."""

    def reconciled(self, doc):
        return self.reconcile(doc)["rapproches"]

    def test_reference_document_reconciles(self):
        self.assertEqual(self.reconciled(ixbrl(GOOD)), 2)

    def test_prefix_bound_to_another_namespace_is_not_us_gaap(self):
        doc = ixbrl(GOOD).replace('xmlns:us-gaap="http://fasb.org/us-gaap/2024"',
                                  'xmlns:us-gaap="http://exemple.invalid/faux-us-gaap"')
        self.assertEqual(self.reconciled(doc), 0)

    def test_other_prefix_bound_to_us_gaap_is_recognized(self):
        doc = ixbrl(GOOD).replace('xmlns:us-gaap="http://fasb.org/us-gaap/2024"',
                                  'xmlns:gaap="http://fasb.org/us-gaap/2024"').replace('name="us-gaap:', 'name="gaap:')
        self.assertEqual(self.reconciled(doc), 2)

    def test_currency_outside_iso4217_is_not_usd(self):
        doc = ixbrl(GOOD).replace('xmlns:iso4217="http://www.xbrl.org/2003/iso4217"',
                                  'xmlns:iso4217="http://exemple.invalid/monnaies"')
        self.assertEqual(self.reconciled(doc), 0)

    def test_identifier_scheme_must_be_sec_cik(self):
        doc = ixbrl(GOOD).replace('scheme="http://www.sec.gov/CIK"', 'scheme="http://exemple.invalid/id"')
        self.assertEqual(self.reconciled(doc), 0)

    def test_prefix_redeclared_with_another_namespace_is_refused(self):
        doc = ixbrl(GOOD).replace("</body>", '<p xmlns:us-gaap="http://exemple.invalid/autre">x</p></body>')
        with self.assertRaisesRegex(en.NormalizeError, "plusieurs espaces de noms"):
            self.reconcile(doc)

    def test_undeclared_prefix_is_refused(self):
        doc = ixbrl(GOOD).replace('xmlns:iso4217="http://www.xbrl.org/2003/iso4217" ', "")
        with self.assertRaisesRegex(en.NormalizeError, "lecture XBRL"):
            self.reconcile(doc)


class RealDocumentEdgeCasesTests(unittest.TestCase):
    """Cas rencontrés dans le 10-K réel d'Apple : xsi:nil, faits imbriqués ; et ix:exclude (spécification)."""

    def el(self, xml):
        return ET.fromstring('<r xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" '
                             'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' + xml + "</r>")[0]

    def test_nil_value_is_refused(self):
        with self.assertRaisesRegex(ValueError, "nil"):
            en._ix_value(self.el('<ix:nonFraction name="a" xsi:nil="true"/>'))

    def test_nested_fact_text_counts_and_exclude_does_not(self):
        outer = self.el('<ix:nonFraction name="a" scale="6" format="ixt:num-dot-decimal">'
                        '<ix:nonFraction name="b" scale="6" format="ixt:num-dot-decimal">1,250</ix:nonFraction>'
                        '</ix:nonFraction>')
        self.assertEqual(en._ix_value(outer), 1250000000)
        excl = self.el('<ix:nonFraction name="a" format="ixt:num-dot-decimal">1,2<ix:exclude>(note 3)</ix:exclude>50'
                       '</ix:nonFraction>')
        self.assertEqual(en._ix_value(excl), 1250)


class FetchFilingTests(Base):
    def test_fetch_requires_identification_and_stores_none(self):
        en.normalize(self.raw, self.out, self.rules)
        d = self.tmp / "servi"
        d.mkdir()
        served = {"fxei-10k.htm": ixbrl(GOOD).encode("utf-8"),
                  "index.json": json.dumps({"directory": {"item": [
                      {"name": n} for n in ("fxei-10k.htm", "fxei-20241231.xsd", "fxei-20241231_cal.xml",
                                            "R1.htm", "FilingSummary.xml")]}}).encode("utf-8")}
        for f in calc_annexes(d):
            served[f.name] = f.read_bytes()
        calls = []

        def fake(url, ua):
            calls.append((url, ua))
            return served[url.rsplit("/", 1)[-1]]
        with self.assertRaises(SystemExit):
            en.fetch_filing(self.out, K10, None, self.raw, fetch=fake)
        self.assertEqual(calls, [])
        en.fetch_filing(self.out, K10, "Alice Martin alice@societe.fr", self.raw, fetch=fake)
        self.assertEqual([u.rsplit("/", 1)[-1] for u, _ in calls],
                         ["fxei-10k.htm", "index.json", "fxei-20241231.xsd", "fxei-20241231_cal.xml"])
        for f in self.out.rglob("*"):
            if f.is_file():
                self.assertNotIn(b"alice@societe.fr", f.read_bytes(), f.name)
        listed = json.loads(next(self.out.rglob(en.ANNEXES_FILE)).read_text(encoding="utf-8"))
        self.assertEqual({a["fichier"] for a in listed}, {"fxei-20241231.xsd", "fxei-20241231_cal.xml"})
        rep = en.reconcile_ixbrl(self.out, K10, self.raw, self.rules, self.taxo)
        self.assertEqual(rep["rapproches"], 2)
        self.assertEqual(en.verify_normalisation(self.raw, self.out, self.rules, self.taxo), ([], []))


class ResolverUnitTests(unittest.TestCase):
    """Revue n° 16 : résolution normative des localisateurs de calcul."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.cache = fake_taxonomy(self.tmp / "taxo")

    def annex(self, tns, name="fxei-20241231.xsd"):
        f = self.tmp / name
        f.write_text('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" '
                     f'targetNamespace="{tns}"><xs:element id="us-gaap_GrossProfit" name="GrossProfit"/>'
                     '<xs:element id="fx_Ventes" name="Ventes"/></xs:schema>', encoding="utf-8")
        return f

    def test_standard_and_extension_concepts(self):
        r = en.SchemaResolver([self.annex("http://exemple.invalid/fxei")], self.cache)
        self.assertEqual(r.resolve(US_GAAP_2024 + "#us-gaap_GrossProfit"), "us-gaap:GrossProfit")
        self.assertEqual(r.resolve("fxei-20241231.xsd#fx_Ventes"), "{http://exemple.invalid/fxei}Ventes")
        self.assertEqual(r.resolve("fxei-20241231.xsd#us-gaap_GrossProfit"), "{http://exemple.invalid/fxei}GrossProfit")

    def test_unresolvable_references(self):
        r = en.SchemaResolver([self.annex("http://exemple.invalid/fxei")], self.cache)
        for href in ("autre/fxei-20241231.xsd#fx_Ventes",            # chemin relatif avec dossier
                     "https://xbrl.fasb.org/us-gaap/2025/elts/us-gaap-2025.xsd#us-gaap_GrossProfit",  # hors cache
                     US_GAAP_2024 + "#element(/1/2)",                 # pointeur non « shorthand »
                     US_GAAP_2024 + "#inexistant", "fxei-20241231.xsd", ""):
            with self.subTest(href):
                self.assertIsNone(r.resolve(href))

    def test_filer_schema_cannot_claim_an_official_namespace(self):
        r = en.SchemaResolver([self.annex("http://fasb.org/us-gaap/2024")], self.cache)
        self.assertIsNone(r.resolve("fxei-20241231.xsd#us-gaap_GrossProfit"))
        self.assertTrue(r.problems_soft)

    def test_unresolved_contributor_fails_even_without_period_facts(self):
        roles = {"r": ("Statement", "Résultat")}
        arcs = [("r", "us-gaap:GrossProfit", R1C, 1.0), ("r", "us-gaap:GrossProfit", None, -1.0)]
        proof, why = en.position_proof(R1C, roles, arcs, {"categorie": "Statement", "parents": ["us-gaap:GrossProfit"]})
        self.assertIsNone(proof)
        self.assertIn("n'a pas pu être résolu", why)


class TaxonomyCacheTests(Base):
    def test_fetch_taxonomies_downloads_only_official_schemas_referenced_by_calculations(self):
        en.normalize(self.raw, self.out, self.rules)
        d = self.tmp / "ann"
        d.mkdir()
        self.import_doc(annexes=calc_annexes(d))
        cache = self.tmp / "cache"
        calls = []
        added = en.fetch_taxonomies(self.out, K10, "Alice Martin alice@societe.fr", cache,
                                    fetch=lambda url, ua: calls.append(url) or b"<xs:schema/>")
        self.assertEqual((added, calls), ([US_GAAP_2024], [US_GAAP_2024]))
        self.assertEqual(en.fetch_taxonomies(self.out, K10, "Alice Martin alice@societe.fr", cache,
                                             fetch=lambda url, ua: calls.append(url)), [])  # déjà présent
        for f in cache.rglob("*"):
            if f.is_file():
                self.assertNotIn(b"alice@societe.fr", f.read_bytes())
        with self.assertRaises(SystemExit):
            en.fetch_taxonomies(self.out, K10, None, cache, fetch=lambda url, ua: b"")

    def test_import_taxonomy_refuses_other_hosts_and_naive_times(self):
        f = self.tmp / "s.xsd"
        f.write_text("<xs:schema/>", encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.import_taxonomy("https://exemple.invalid/us-gaap-2024.xsd", f, "2026-09-29T10:00:00+00:00",
                               self.tmp / "c")
        with self.assertRaises(en.NormalizeError):
            en.import_taxonomy(US_GAAP_2024, f, "2026-09-29T10:00:00", self.tmp / "c")
        self.assertEqual(en.import_taxonomy(US_GAAP_2024, f, "2026-09-29T10:00:00+00:00", self.tmp / "c"),
                         [US_GAAP_2024])


class FetchUrlTests(Base):
    def test_non_sec_url_is_refused_before_any_request(self):
        text = (self.out / "documents.csv").read_text(encoding="utf-8")
        (self.out / "documents.csv").write_text(text.replace("https://www.sec.gov/Archives/", "https://exemple.invalid/"),
                                                encoding="utf-8")
        calls = []
        with self.assertRaisesRegex(en.NormalizeError, "URL inattendue"):
            en.fetch_filing(self.out, K10, "Alice Martin alice@societe.fr", self.raw,
                            fetch=lambda url, ua: calls.append(url) or b"")
        self.assertEqual(calls, [])


class ReconcileTests(Base):
    def test_import_filing_checks_name_and_timezone(self):
        wrong = self.tmp / "autre.htm"
        wrong.write_text("x", encoding="utf-8")
        with self.assertRaises(en.NormalizeError):
            en.import_filing(self.out, K10, wrong, "2026-09-28T14:05:00+02:00", self.raw)
        with self.assertRaises(en.NormalizeError):
            en.import_filing(self.out, K10, self.tmp / "fxei-10k.htm", "2026-09-28T14:05:00", self.raw)
        sha = self.import_doc()
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            doc = next(r for r in csv.DictReader(f) if r["doc_id"] == K10)
        self.assertEqual(doc["local_sha256"], sha)
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])

    def test_document_establishes_context_and_dimensions(self):
        rep = self.reconcile()
        self.assertEqual((rep["rapproches"], rep["echecs"]), (2, []))
        f24 = self.fact(K10, "2024-12-31")
        self.assertEqual((f24["normalized_concept"], f24["value"], f24["source_context"], f24["source_dimensions"],
                          f24["decimals"], f24["reconciled"]),
                         ("total_revenue", "1250000000", "c-1", "", "-6", "auto"))
        self.assertIn("« 1,250 »", f24["reconciled_note"])
        q = self.fact(Q10, "2024-09-30")
        self.assertEqual(q["normalized_concept"], "")
        self.assertTrue(q["normalization_justification"].startswith("NON NORMALISÉ : en attente"))
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])
        res = audit_folder(self.out)
        self.assertEqual((res.errors, res.reconciled_auto, res.to_reconcile), ([], 2, 2))
        self.assertIn("RAPPROCHEMENT AUTOMATIQUE", res.verdict)
        docs, facts = load_audit(self.out)
        s = select_fact(docs, facts, "0000000123", "total_revenue", "monnaie", "2024-01-01", "2024-12-31",
                        date(2025, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertTrue(s.usable)
        self.assertEqual(s.reconciliation, "auto")

    def test_value_mismatch_is_not_normalized(self):
        bad = [GOOD[0][:3] + ("1,249",) + GOOD[0][4:], *GOOD[1:]]
        rep = self.reconcile(ixbrl(bad))
        self.assertEqual(rep["rapproches"], 1)
        f24 = self.fact(K10, "2024-12-31")
        self.assertEqual(f24["normalized_concept"], "")
        self.assertIn("≠ companyfacts", f24["normalization_justification"])
        self.assertEqual(audit_folder(self.out).errors, [])

    def test_only_dimensional_fact_is_not_normalized(self):
        rep = self.reconcile(ixbrl([GOOD[2], GOOD[1], GOOD[3]]))
        self.assertEqual(rep["rapproches"], 1)
        self.assertIn("ventilé", self.fact(K10, "2024-12-31")["normalization_justification"])

    def test_other_entity_normalizes_nothing(self):
        rep = self.reconcile(ixbrl(GOOD, cik="0000000999"))
        self.assertEqual(rep["rapproches"], 0)
        self.assertFalse(any(r["normalized_concept"] for r in self.facts().values()))

    def test_sign_and_scale(self):
        el = ET.fromstring('<x sign="-" scale="3" format="ixt:num-dot-decimal">1,500</x>')
        self.assertEqual(en._ix_value(el), -1500000)
        with self.assertRaises(ValueError):
            en._ix_value(ET.fromstring('<x format="ixt-sec:numwordsen">five</x>'))

    def test_tampered_local_copy_is_refused(self):
        en.normalize(self.raw, self.out, self.rules)
        self.import_doc()
        with open(self.out / "documents.csv", newline="", encoding="utf-8") as f:
            doc = next(r for r in csv.DictReader(f) if r["doc_id"] == K10)
        (self.out / doc["local_copy"]).write_text(ixbrl(GOOD) + " ", encoding="utf-8")
        with self.assertRaisesRegex(en.NormalizeError, "empreinte différente de local_sha256"):
            en.reconcile_ixbrl(self.out, K10, self.raw, self.rules, self.taxo)

    def test_failed_checks_write_nothing(self):
        bad = _rules(self.tmp, name="mauvaises.json")
        data = json.loads(bad.read_text(encoding="utf-8"))
        data["regles"][0]["normalized_concept"] = "concept_inexistant"
        bad.write_text(json.dumps(data), encoding="utf-8")
        en.normalize(self.raw, self.out, bad)
        self.import_doc()
        snapshot = {p.name: p.read_bytes() for p in self.out.iterdir() if p.is_file()}
        with self.assertRaises(en.NormalizeError):
            en.reconcile_ixbrl(self.out, K10, self.raw, bad, self.taxo)
        self.assertEqual({p.name: p.read_bytes() for p in self.out.iterdir() if p.is_file()}, snapshot)

    def test_auto_reconciliation_needs_note(self):
        self.reconcile()
        with open(self.out / "facts.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        next(r for r in rows if r["reconciled"] == "auto")["reconciled_note"] = "vu"
        with open(self.out / "facts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertTrue(any("AUTOMATIQUE" in e for e in audit_folder(self.out).errors))


def _forge(audit: Path, table: str, key: str, col: str, value: str, author: str, proof: str) -> None:
    """Falsification « cohérente » : cellule modifiée ET saisie journalisée qui la justifie (passe verify-trace)."""
    with open(audit / f"{table}.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0]) if rows else None
    k = ec.ROW_KEYS[table]
    target = next(r for r in rows if "|".join(r[c] for c in k) == key)
    old = target[col]
    target[col] = value
    with open(audit / f"{table}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    journal = en._load_journal(audit)
    journal.append({"n": str(len(journal) + 1), "fichier": table, "cle": key, "colonne": col, "ancienne_valeur": old,
                    "nouvelle_valeur": value, "auteur": author, "saisi_le": journal[-1]["saisi_le"], "preuve": proof,
                    "note": ""})
    with open(audit / ec.SAISIES_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ec.SAISIES_HEADERS)
        w.writeheader()
        w.writerows(journal)


class VerifyNormalisationTests(Base):
    def setUp(self):
        super().setUp()
        self.reconcile()
        self.author = f"{en.TOOL} reconcile-ixbrl ({en.rules_tag(self.rules)}, automatique)"
        self.f24 = self.fact(K10, "2024-12-31")["fact_id"]
        self.q = self.fact(Q10, "2024-09-30")["fact_id"]

    def test_clean_folder_verifies(self):
        self.assertEqual(en.verify_normalisation(self.raw, self.out, self.rules, self.taxo), ([], []))

    def test_forged_concept_attributed_to_the_tool_is_detected(self):
        _forge(self.out, "facts", self.f24, "normalized_concept", "total_assets", self.author, "doc:" + K10)
        _forge(self.out, "concept_map", REV, "normalized_concept", "total_assets", self.author,
               "url:https://data.sec.gov/companyfacts")
        self.assertEqual(ec.verify_trace(self.raw, self.out), [])  # la forme et l'historique sont cohérents…
        problems, human = en.verify_normalisation(self.raw, self.out, self.rules, self.taxo)  # …pas le fond
        self.assertTrue(any("normalized_concept" in m and "total_assets" in m for m in problems))
        self.assertEqual(human, [])

    def test_forged_normalization_of_a_fact_without_document_is_detected(self):
        for col, val in (("normalized_concept", "total_revenue"), ("transformation", "aucune"),
                         ("value", "300000000"), ("source_context", "c-9"), ("source_dimensions", ""),
                         ("normalization_justification", "Règle T1")):
            _forge(self.out, "facts", self.q, col, val, self.author, "doc:" + Q10)
        problems, _ = en.verify_normalisation(self.raw, self.out, self.rules, self.taxo)
        self.assertTrue(any(self.q in m and "normalized_concept" in m for m in problems))

    def test_human_override_is_listed_not_hidden(self):
        _forge(self.out, "facts", self.f24, "normalization_justification", "Revu à la main : identique, page 3",
               "Relecteur B", "doc:" + K10)
        problems, human = en.verify_normalisation(self.raw, self.out, self.rules, self.taxo)
        self.assertEqual(problems, [])
        self.assertTrue(any("Relecteur B" in m for m in human))

    def test_other_rules_file_is_detected(self):
        other = self.tmp / "autres.json"
        data = json.loads(self.rules.read_text(encoding="utf-8"))
        data["regles"][0]["justification"] = "texte modifié"
        other.write_text(json.dumps(data), encoding="utf-8")
        problems, _ = en.verify_normalisation(self.raw, self.out, other, self.taxo)
        self.assertTrue(any("autres règles" in m for m in problems))

    def test_tampered_proposals_file_is_detected(self):
        p = self.out / en.PROPOSALS_FILE
        p.write_text(p.read_text(encoding="utf-8").replace("total_revenue", "total_assets", 1), encoding="utf-8")
        problems, _ = en.verify_normalisation(self.raw, self.out, self.rules, self.taxo)
        self.assertTrue(any(en.PROPOSALS_FILE in m for m in problems))


REAL = {"apple": ("0000320193", {"total_assets": 88, "total_revenue": 11,
                                 "revenue_from_contracts_with_customers": 117}, 11),
        "microsoft": ("0000789019", {"revenue_from_contracts_with_customers": 78, "total_assets": 48}, 5),
        "alphabet": ("0001652044", {"revenue_from_contracts_with_customers": 26, "total_assets": 26,
                                    "total_revenue": 17}, 5),
        "black_hills": ("0001130464", {"revenue_from_contracts_with_customers": 102, "total_assets": 91,
                                       "total_revenue": 120}, 10),
        "american_express": ("0000004962", {'revenue_from_contracts_with_customers': 91, 'revenues_net_of_interest_expense': 107, 'total_assets': 84}, 9),
        "duke_energy": ("0001326160", None, 9),
        "ford": ("0000037996", None, 6)}
REVENUE = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"


class RealIssuersTests(unittest.TestCase):
    """Dossiers réels : propositions pour tous les dépôts ; normalisation et rapprochement automatique pour les
    documents téléchargés (10-K 2025 et 10-Q T3 2025 d'Apple, derniers 10-K de Microsoft et d'Alphabet)."""

    def paths(self, name):
        audit, raw = ROOT / "data" / f"audit_edgar_{name}", ROOT / "collecte" / name
        if not (audit.exists() and raw.exists()):
            self.skipTest(f"dossier {name} absent")
        return audit, raw

    def sel(self, name, start, end, day):
        audit, _ = self.paths(name)
        docs, facts = load_audit(audit)
        return docs, select_fact(docs, facts, REAL[name][0], REVENUE, "USD", start, end, date.fromisoformat(day))

    def test_proposals_normalizations_and_all_checks_clean(self):
        for name, (_, counts, normalized) in REAL.items():
            with self.subTest(name):
                audit, raw = self.paths(name)
                rep = json.loads((audit / "rapport_normalisation.json").read_text(encoding="utf-8"))
                if counts is not None:
                    self.assertEqual(rep["propositions"], counts)
                self.assertEqual(rep["conflits"], [])
                self.assertEqual(rep["regles_sha256"], en._sha(RULES_V7))
                docs, facts = load_audit(audit)
                norm = [f for f in facts if f["normalized_concept"]]
                self.assertEqual(len(norm), normalized)
                self.assertTrue(all(f["reconciled"] == "auto" and f["source_dimensions"] == "" and
                                    docs[f["doc_id"]]["local_copy"] for f in norm))
                self.assertEqual(ec.verify_trace(raw, audit), [])
                self.assertEqual(en.verify_normalisation(raw, audit, RULES_V7), ([], []))
                res = audit_folder(audit)
                self.assertEqual((res.errors, res.reconciled_auto, res.to_reconcile), ([], normalized, normalized))
                self.assertIn("RAPPROCHEMENT AUTOMATIQUE", res.verdict)

    def test_apple_fiscal_2025_revenue_is_usable_from_its_document(self):
        audit, _ = self.paths("apple")
        docs, facts = load_audit(audit)
        s = select_fact(docs, facts, "0000320193", "total_revenue", "monnaie", "2024-09-29",
                        "2025-09-27", date(2025, 11, 1), concept_field="normalized_concept", currency="USD")
        self.assertEqual((s.fact["value"], s.usable, s.reconciliation), ("416161000000", True, "auto"))
        self.assertEqual((s.fact["source_context"], s.fact["decimals"]), ("c-1", "-6"))
        self.assertIn("« 416,161 »", s.fact["reconciled_note"])
        q = select_fact(docs, facts, "0000320193", "total_revenue", "monnaie", "2025-03-30",
                        "2025-06-28", date(2025, 8, 2), concept_field="normalized_concept", currency="USD")
        self.assertEqual((q.fact["value"], q.usable), ("94036000000", True))

    def test_known_values(self):
        for name, start, end, day, value in (
                ("apple", "2024-09-29", "2025-09-27", "2025-11-01", "416161000000"),
                ("apple", "2025-03-30", "2025-06-28", "2025-08-02", "94036000000"),
                ("microsoft", "2024-07-01", "2025-06-30", "2026-01-01", "281724000000"),
                ("alphabet", "2024-01-01", "2024-12-31", "2025-03-01", "350018000000")):
            with self.subTest(name=name, end=end):
                self.assertEqual(self.sel(name, start, end, day)[1].fact["raw_value"], value)

    def test_review_case_black_hills_component_is_never_the_total(self):
        audit, _ = self.paths("black_hills")
        docs, facts = load_audit(audit)
        for start, total, component in (("2026-04-01", "452800000", "440600000"),
                                        ("2026-01-01", "1233500000", "1200600000")):
            args = ("monnaie", start, "2026-06-30", date(2026, 8, 8))
            t_ = select_fact(docs, facts, "0001130464", "total_revenue", *args, concept_field="normalized_concept",
                             currency="USD")
            c_ = select_fact(docs, facts, "0001130464", "revenue_from_contracts_with_customers", *args,
                             concept_field="normalized_concept", currency="USD")
            self.assertEqual((t_.fact["value"], t_.fact["source_concept"], t_.usable), (total, "us-gaap:Revenues", True))
            self.assertEqual((c_.fact["value"], c_.fact["source_concept"]), (component, R1C))
        self.assertFalse(any(f["source_concept"] == R1C and f["normalized_concept"] == "total_revenue" for f in facts))

    def test_review_case_american_express_fallback_is_blocked(self):
        audit, _ = self.paths("american_express")
        docs, facts = load_audit(audit)
        s = select_fact(docs, facts, "0000004962", "total_revenue", "monnaie", "2025-01-01", "2025-12-31",
                        date(2026, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertIsNone(s.fact)  # aucun total plutôt qu'un faux total
        c = select_fact(docs, facts, "0000004962", "revenue_from_contracts_with_customers", "monnaie", "2025-01-01",
                        "2025-12-31", date(2026, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertEqual((c.fact["value"], c.usable), ("41304000000", True))

    def test_american_express_document_meets_the_v3_fallback_conditions(self):
        """Ce que v3 aurait fait : R1 déclaré, ni Revenues ni RevenueNotFromContractWithCustomer ⇒ repli (faux),
        alors que d'autres revenus sont déclarés pour l'entité entière. v3 est désormais refusée par l'outil."""
        audit, raw = self.paths("american_express")
        with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
            local = next(r for r in csv.DictReader(f) if r["doc_id"] == "0000004962-0000004962-26-000080")["local_copy"]
        contexts, _, facts = en.parse_ixbrl(audit / local)
        fy = {f["name"]: f["text"] for f in facts if f["context"] in contexts
              and not contexts[f["context"]]["segment"] and contexts[f["context"]]["start"] == "2025-01-01"
              and contexts[f["context"]]["end"] == "2025-12-31" and f["unit"] == "USD"}
        self.assertEqual(fy[R1C], "41,304")
        self.assertNotIn(REV, fy)
        self.assertNotIn("us-gaap:RevenueNotFromContractWithCustomer", fy)
        self.assertIn("us-gaap:InterestAndDividendIncomeOperating", fy)
        with self.assertRaises(en.NormalizeError):
            en.normalize(raw, audit, RULES_V3)

    def test_review_15_duke_component_including_tax_stays_distinct(self):
        audit, _ = self.paths("duke_energy")
        docs, facts = load_audit(audit)
        args = ("monnaie", "2025-01-01", "2025-12-31", date(2026, 3, 1))
        c = select_fact(docs, facts, "0001326160", "revenue_from_contracts_with_customers_including_assessed_tax",
                        *args, concept_field="normalized_concept", currency="USD")
        self.assertEqual(c.fact["value"], "31741000000")
        self.assertIsNone(select_fact(docs, facts, "0001326160", "revenue_from_contracts_with_customers", *args,
                                      concept_field="normalized_concept", currency="USD").fact)

    def test_alphabet_2025_total_comes_from_revenues(self):
        audit, _ = self.paths("alphabet")
        docs, facts = load_audit(audit)
        s = select_fact(docs, facts, "0001652044", "total_revenue", "monnaie", "2025-01-01", "2025-12-31",
                        date(2026, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertEqual((s.fact["value"], s.fact["source_concept"]), ("402836000000", "us-gaap:Revenues"))

    def test_proofs_pass_with_official_schemas(self):
        """Schémas us-gaap officiels dans collecte/taxonomies : repli prouvé (Apple, Microsoft, Ford), total direct
        réglementé (Duke), extraction bancaire typée (American Express) ; chaque preuve cite les schémas officiels."""
        cases = {"apple": ("0000320193", "2024-09-29", "2025-09-27", "416161000000", R1C),
                 "microsoft": ("0000789019", "2024-07-01", "2025-06-30", "281724000000", R1C),
                 "ford": ("0000037996", "2025-01-01", "2025-12-31", "187267000000", R1C),
                 "duke_energy": ("0001326160", "2025-01-01", "2025-12-31", "32237000000",
                                 "us-gaap:RegulatedAndUnregulatedOperatingRevenue")}
        for name, (cik, start, end, value, concept) in cases.items():
            with self.subTest(name):
                audit, _ = self.paths(name)
                docs, facts = load_audit(audit)
                s = select_fact(docs, facts, cik, "total_revenue", "monnaie", start, end, date(2026, 9, 1),
                                concept_field="normalized_concept", currency="USD")
                self.assertEqual((s.fact["value"], s.fact["source_concept"], s.usable), (value, concept, True))
                j = s.fact["normalization_justification"]
                self.assertIn("calcul_XBRL_coherent=oui ; preuve_complete_pour_repli=oui", j)
                self.assertIn("schémas officiels : https://xbrl.fasb.org/us-gaap/", j)
                if concept == R1C:
                    self.assertTrue(j.startswith("REPLI : preuve positive"))
        audit, _ = self.paths("american_express")
        docs, facts = load_audit(audit)
        b = select_fact(docs, facts, "0000004962", "revenues_net_of_interest_expense", "monnaie", "2025-01-01",
                        "2025-12-31", date(2026, 3, 1), concept_field="normalized_concept", currency="USD")
        self.assertEqual(b.fact["value"], "72229000000")
        self.assertFalse(any(f["normalized_concept"] == "total_revenue" for f in facts))

    def test_without_official_schemas_the_proofs_fail_closed(self):
        audit, raw = self.paths("ford")
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        cp = tmp / "cp"
        ec.convert(raw, cp, {"10-K", "10-Q"})
        en.normalize(raw, cp, RULES_V7)
        with open(audit / "documents.csv", newline="", encoding="utf-8") as f:
            doc = next(r for r in csv.DictReader(f) if r["local_copy"])
        src = audit / doc["local_copy"]
        en.import_filing(cp, doc["doc_id"], src, "2026-09-28T00:00:00+00:00", raw, annexes=en._annexes(src.parent))
        (tmp / "cache_vide").mkdir()
        en.reconcile_ixbrl(cp, doc["doc_id"], raw, RULES_V7, tmp / "cache_vide")
        _, facts = load_audit(cp)
        self.assertFalse(any(f["normalized_concept"] == "total_revenue" for f in facts))
        self.assertTrue(any("schémas non disponibles" in f["normalization_justification"] for f in facts))

    def test_later_comparative_never_replaces_the_filing_available_at_the_decision(self):
        docs, before = self.sel("microsoft", "2024-07-01", "2025-06-30", "2025-12-01")
        _, after = self.sel("microsoft", "2024-07-01", "2025-06-30", "2026-09-01")
        self.assertTrue(docs[before.fact["doc_id"]]["accepted_at"].startswith("2025"))
        self.assertTrue(docs[after.fact["doc_id"]]["accepted_at"].startswith("2026"))
        self.assertEqual(after.original["doc_id"], before.fact["doc_id"])
        self.assertEqual((after.fact["raw_value"], after.revised_values), (before.fact["raw_value"], []))

    def test_published_examples_match_the_data(self):
        import exemple_normalisation as ex
        doc = (ROOT / "docs" / "EXEMPLE_NORMALISATION.md").read_text(encoding="utf-8")
        for name, accn in (("apple", "0000320193-25-000079"), ("apple", "0000320193-25-000073"),
                           ("microsoft", "0001193125-26-323660"), ("alphabet", "0001652044-26-000018"),
                           ("black_hills", "0001193125-26-337444"),
                           ("american_express", "0000004962-26-000080"),
                           ("duke_energy", "0001326160-26-000014"), ("ford", "0000037996-26-000015")):
            audit, _ = self.paths(name)
            self.assertIn(ex.table(audit, accn).strip(), doc)


if __name__ == "__main__":
    unittest.main()
