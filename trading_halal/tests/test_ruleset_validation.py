"""Garde-fous sur le référentiel religieux et le cadre de simulation (revue n° 1)."""
import copy
import hashlib
import json
import os
import tempfile
import unittest

from helpers import config, demo_dataset, demo_ruleset, fresh_copy, run, template_ruleset

from halal_sim.backtest import PolicyError, check_run_allowed
from halal_sim import PROJECT_ROOT
from halal_sim.screening import SHARIA_DECISIONS, RulesetError, load_ruleset, real_data_problems
from halal_sim.strategy import BUY, PolicyConfigError, incertain_action


def real_ds():
    ds = fresh_copy(demo_dataset())
    ds.manifest["nature"] = "REEL"
    return ds

SHEET = "docs/FICHE_VALIDATION_SHARIA.md"


def complete_test_ruleset():
    """Référentiel entièrement renseigné, À USAGE DE TEST UNIQUEMENT : les valeurs et les références sont
    inventées pour vérifier la mécanique de validation, elles ne proviennent d'aucun texte religieux."""
    rs = copy.deepcopy(template_ruleset())
    rs.update(id="TEST_UNIQUEMENT", validated=True, demo_only=False, validated_by="Relecteur de test",
              validated_on="2026-01-01", activity_rules_source="Texte inventé pour test unitaire, section 1",
              reference_text={"name": "Texte inventé pour test", "version": "0", "date": "2026-01-01",
                              "url_or_document": "aucun", "pages_or_sections": "1"})
    for r in rs["financial_ratios"]:
        r["max"], r["source"] = 0.5, "Texte inventé pour test unitaire, section 2"
    sheet = PROJECT_ROOT / SHEET
    rs["validation_record"] = {"document": SHEET, "sha256": hashlib.sha256(sheet.read_bytes()).hexdigest(),
                               "decisions": {k: {"reponse": "VALIDE"} for k in SHARIA_DECISIONS}}
    return rs


def load_from_dict(d):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(d, f)
    try:
        return load_ruleset(f.name)
    finally:
        os.unlink(f.name)


class RulesetValidationTests(unittest.TestCase):
    def test_review_case_empty_ratios_and_flipped_flags_is_refused(self):
        """Cas signalé en revue : booléens basculés + ratios vidés → données REEL acceptées, FXALP ADMISSIBLE."""
        rs = dict(demo_ruleset(), validated=True, demo_only=False, financial_ratios=[])
        with self.assertRaises(PolicyError):
            check_run_allowed(real_ds(), rs, config())
        with self.assertRaises(PolicyError):  # même sur données fictives : structure invalide
            check_run_allowed(demo_dataset(), rs, config())
        with self.assertRaises(RulesetError):
            load_from_dict(rs)

    def test_flipping_flags_on_demo_or_template_is_not_enough(self):
        for base in (demo_ruleset(), template_ruleset()):
            rs = dict(base, validated=True, demo_only=False)
            with self.assertRaises(PolicyError) as ctx:
                check_run_allowed(real_ds(), rs, config())
            self.assertIn("reference_text", str(ctx.exception))

    def test_complete_ruleset_is_accepted_for_real_data(self):
        rs = complete_test_ruleset()
        self.assertEqual(real_data_problems(rs), [])
        check_run_allowed(real_ds(), rs, config())  # ne lève pas

    def test_each_missing_requirement_is_detected(self):
        for key, value in [("validated_by", ""), ("validated_on", "hier"), ("activity_rules_source", None),
                           ("reference_text", {})]:
            rs = complete_test_ruleset()
            rs[key] = value
            self.assertNotEqual(real_data_problems(rs), [], key)
        rs = complete_test_ruleset()
        rs["financial_ratios"][0]["source"] = "VALEUR ARBITRAIRE DE DÉMONSTRATION"
        self.assertNotEqual(real_data_problems(rs), [])

    def test_structural_errors(self):
        cases = []
        rs = demo_ruleset(); rs = dict(rs, allowed_instrument_types=["ACTION", "OPTION"]); cases.append(rs)
        rs = copy.deepcopy(demo_ruleset()); rs["activity_rules"]["ALCOHOL"]["status"] = "ADMISSIBLE"; cases.append(rs)
        rs = copy.deepcopy(demo_ruleset()); del rs["activity_rules"]["GAMBLING"]; cases.append(rs)
        rs = copy.deepcopy(demo_ruleset()); rs["financial_ratios"][0]["max"] = 30; cases.append(rs)  # 30 au lieu de 0.30
        rs = copy.deepcopy(demo_ruleset()); rs["financial_ratios"][0]["numerator"] = "benefice"; cases.append(rs)
        rs = copy.deepcopy(demo_ruleset()); rs["financial_ratios"] = rs["financial_ratios"][:2]; cases.append(rs)
        rs = dict(demo_ruleset(), max_fundamentals_age_days=0); cases.append(rs)
        for i, rs in enumerate(cases):
            with self.assertRaises(RulesetError, msg=f"cas {i}"):
                load_from_dict(rs)
            with self.assertRaises(PolicyError, msg=f"cas {i}"):
                check_run_allowed(demo_dataset(), rs, config())

    def test_shipped_rulesets_are_structurally_valid(self):
        demo_ruleset(), template_ruleset()  # ne lèvent pas

    def test_currency_mismatch_is_refused(self):
        ds = fresh_copy(demo_dataset())
        ds.securities["FXALP"]["currency"] = "USD"
        with self.assertRaises(PolicyError) as ctx:
            check_run_allowed(ds, demo_ruleset(), config())
        self.assertIn("devises", str(ctx.exception))


class HoldingPolicyTests(unittest.TestCase):
    def test_policy_by_cause(self):
        pol = {"on_exclu": "SELL", "on_incertain": {"DONNEE_MANQUANTE": "HOLD", "DONNEE_PERIMEE": "HOLD"}}
        self.assertEqual(incertain_action(pol, ["DONNEE_MANQUANTE"]), "HOLD")
        self.assertEqual(incertain_action(pol, ["DONNEE_MANQUANTE", "ACTIVITE"]), "SELL")  # cause non listée → vente
        self.assertEqual(incertain_action(pol, []), "SELL")
        self.assertEqual(incertain_action({"on_exclu": "SELL", "on_incertain": "HOLD"}, ["ACTIVITE"]), "HOLD")

    def test_invalid_policies_refused(self):
        for pol in ({"on_exclu": "HOLD", "on_incertain": "SELL"}, {"on_exclu": "SELL", "on_incertain": "GARDER"},
                    {"on_exclu": "SELL", "on_incertain": {"CAUSE_INVENTEE": "HOLD"}}, {"on_exclu": "SELL"}):
            cfg = dict(config(), holding_policy=pol)
            with self.assertRaises(PolicyConfigError):
                check_run_allowed(demo_dataset(), demo_ruleset(), cfg)

    def test_hold_on_missing_data_keeps_position_but_never_buys_incertain(self):
        q = ("SELECT COUNT(*) FROM decisions WHERE portfolio='reference' AND ticker='FXIOT' "
             "AND reason_code='VENTE_STATUT_INCERTAIN'")
        _, default_store = run()
        self.assertEqual(default_store.conn.execute(q).fetchone()[0], 1, "précondition : vendu avec la politique SELL")
        cfg = dict(config(), holding_policy={"on_exclu": "SELL", "on_incertain": {"DONNEE_MANQUANTE": "HOLD"}})
        _, store = run(cfg=cfg)
        c = store.conn
        # FXIOT (donnée manquante en 2023) n'est plus vendu par la référence…
        self.assertEqual(c.execute("SELECT COUNT(*) FROM decisions WHERE portfolio='reference' AND ticker='FXIOT' "
                                   "AND reason_code='VENTE_STATUT_INCERTAIN'").fetchone()[0], 0)
        # …et aucun achat n'a lieu sur un statut non admissible.
        self.assertEqual(c.execute("SELECT COUNT(*) FROM decisions WHERE final_action=? AND screening_status<>'ADMISSIBLE'",
                                   (BUY,)).fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()


class DenominatorDecisionTests(unittest.TestCase):
    """Décision du 29/09/2026 (provisoire, à valider par un sharia board) : le dénominateur du ratio de revenus
    illicites est le REVENU TOTAL déclaré (document de l'utilisateur, AAOIFI SS 21 §3/4/4) ; jamais les revenus nets
    des charges d'intérêts ni les seuls revenus de contrats clients."""

    def test_only_total_revenue_is_an_allowed_denominator(self):
        from halal_sim.screening import RATIO_CATALOG
        self.assertEqual(RATIO_CATALOG["revenus_non_conformes"]["denominators"], {"total_revenue"})

    def test_user_ruleset_uses_total_revenue_and_excludes_conventional_finance(self):
        import json
        from helpers import ROOT
        r = json.loads((ROOT / "config" / "rulesets" / "AAOIFI_SS21_document_utilisateur.json").read_text(encoding="utf-8"))
        ratio = next(x for x in r["financial_ratios"] if x["id"] == "revenus_non_conformes")
        self.assertEqual(ratio["denominator"], "total_revenue")
        self.assertEqual((r["activity_rules"]["CONVENTIONAL_BANKING"]["status"],
                          r["activity_rules"]["CONVENTIONAL_INSURANCE"]["status"]), ("EXCLU", "EXCLU"))
        self.assertFalse(r["validated"])


class SignedValidationSheetTests(unittest.TestCase):
    """La validation renvoie à la fiche signée (empreinte) et reprend chaque décision (V1.24)."""

    def problems_after(self, change):
        rs = complete_test_ruleset()
        change(rs["validation_record"])
        return real_data_problems(rs)

    def test_record_is_required(self):
        rs = complete_test_ruleset()
        del rs["validation_record"]
        self.assertEqual(len(real_data_problems(rs)), 1)
        self.assertIn("validation_record absent", real_data_problems(rs)[0])

    def test_document_must_match_its_fingerprint(self):
        got = self.problems_after(lambda r: r.update(sha256="0" * 64))
        self.assertEqual(got, ["validation_record.sha256 ne correspond pas au document signé"])

    def test_document_path_must_stay_in_the_project_and_exist(self):
        for doc in ("/etc/hostname", "../README.md", "", "docs/absent.pdf"):
            with self.subTest(doc=doc):
                got = self.problems_after(lambda r: r.update(document=doc))
                self.assertEqual(len(got), 1, got)
                self.assertIn("validation_record.document", got[0])

    def test_every_decision_must_be_answered_and_none_refused(self):
        got = self.problems_after(lambda r: r["decisions"].pop("D03"))
        self.assertEqual(len(got), 1)
        self.assertIn("D03", got[0])
        for bad in ("REFUSE", "valide", None):
            with self.subTest(bad=bad):
                got = self.problems_after(lambda r: r["decisions"]["D11"].update(reponse=bad))
                self.assertEqual(len(got), 1)
                self.assertIn("D11", got[0])

    def test_a_modification_must_be_written_down(self):
        got = self.problems_after(lambda r: r["decisions"]["D12"].update(reponse="MODIFIE"))
        self.assertEqual(got, ["décision D12 modifiée sans texte de la modification"])
        got = self.problems_after(lambda r: r["decisions"]["D12"].update(reponse="MODIFIE", modification="Méthode X"))
        self.assertEqual(got, [])

    def test_the_sheet_lists_every_decision_of_the_code(self):
        text = (PROJECT_ROOT / SHEET).read_text(encoding="utf-8")
        for key in SHARIA_DECISIONS:
            self.assertIn(f"### {key}", text)
        self.assertEqual(text.count("### D"), len(SHARIA_DECISIONS))

