"""The scenario script must reproduce the outcomes reported in Table 4."""
from experiments.scenarios import SCENARIOS, run_scenario


def test_scenario_outcomes_match_the_report():
    outcomes = {sid: run_scenario(sid, name, query, expect)["outcome"] for sid, name, query, expect in SCENARIOS}
    assert outcomes == {
        "S1": "Pass", "S2": "Pass", "S3": "Pass", "S4": "Pass", "S5": "Partial", "S6": "Fail", "S7": "Pass",
        "S8": "Pass", "S9": "Fail", "S10": "Pass", "S11": "Pass", "S12": "Pass", "S13": "Pass", "S14": "Pass",
    }
