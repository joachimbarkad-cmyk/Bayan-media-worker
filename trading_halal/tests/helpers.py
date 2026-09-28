import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from halal_sim.backtest import run_backtest  # noqa: E402
from halal_sim.data import Dataset, load_dataset  # noqa: E402
from halal_sim.db import Store  # noqa: E402
from halal_sim.screening import load_ruleset  # noqa: E402

_DS = None


def demo_dataset() -> Dataset:
    global _DS
    if _DS is None:
        _DS = load_dataset(ROOT / "data" / "demo")
    return _DS


def fresh_copy(ds: Dataset, **overrides) -> Dataset:
    fields = dict(root=ds.root, manifest=copy.deepcopy(ds.manifest), securities=copy.deepcopy(ds.securities),
                  bars={t: list(b) for t, b in ds.bars.items()},
                  fundamentals={t: [dict(f) for f in fs] for t, fs in ds.fundamentals.items()},
                  calendar=list(ds.calendar), file_hashes=dict(ds.file_hashes))
    fields.update(overrides)
    return Dataset(**fields)


def config() -> dict:
    return json.loads((ROOT / "config" / "simulation.json").read_text(encoding="utf-8"))


def demo_ruleset() -> dict:
    return load_ruleset(ROOT / "config" / "rulesets" / "demo_fictif.json")


def template_ruleset() -> dict:
    return load_ruleset(ROOT / "config" / "rulesets" / "TEMPLATE_a_valider.json")


def run(ds=None, ruleset=None, capital=None, cfg=None):
    store = Store(":memory:")
    res = run_backtest(ds or demo_dataset(), cfg or config(), ruleset or demo_ruleset(), store, capital=capital)
    return res, store
