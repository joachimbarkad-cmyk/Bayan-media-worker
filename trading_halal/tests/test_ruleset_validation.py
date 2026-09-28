"""Garde-fous sur le référentiel religieux et le cadre de simulation (revue n° 1)."""
import copy
import json
import os
import tempfile
import unittest

from helpers import config, demo_dataset, demo_ruleset, fresh_copy, run, template_ruleset

from halal_sim.backtest import PolicyError, check_run_allowed
from halal_sim.screening import RulesetError, load_ruleset, real_data_problems
from halal_sim.strategy import BUY, PolicyConfigError, incertain_action


def real_ds():
    ds = fresh_copy(demo_dataset())
    ds.manifest["nature"] = "REEL"
    return ds


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
