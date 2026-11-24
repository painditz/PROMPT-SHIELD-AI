import csv
import json
from pathlib import Path

import pytest

from evidence import Store, comparison, effective, parse_cases, parse_judgment
from workflow import DEFAULT_POLICY, Workflow


def case(category="adversarial"):
    return dict(test_id="fixture", input="Synthetic fixture input", category=category,
                targeted_rule="scope", expected_behavior="Stay within scope", technique="fixture")


def judgment(verdict="PASS", succeeded=False):
    return dict(test_id="fixture", verdict=verdict, attack_succeeded=succeeded,
                violated_rules=[], reason="Fixture judgment", recommendation="Fixture recommendation")


@pytest.mark.parametrize("raw", ["{", "[]", "[null]", '[{"test_id":"fixture"}]'])
def test_invalid_case_json(raw):
    with pytest.raises(ValueError):
        parse_cases(raw)


def test_judge_validation():
    result = judgment()
    assert parse_judgment(json.dumps(result), "fixture", "adversarial") == result
    for invalid in (judgment("OTHER"), judgment("PASS", True), judgment("FAIL", "yes")):
        with pytest.raises(ValueError):
            parse_judgment(json.dumps(invalid), "fixture", "adversarial")
    with pytest.raises(ValueError):
        parse_judgment(json.dumps(result), "other", "adversarial")


def test_archived_p1_and_blank_edge():
    archive = {"id": 1, "category": "archived label", "attack": "Recorded fixture",
               "rule_targeted": "scope"}
    saved = parse_cases(json.dumps([archive]))[0]
    assert saved["technique"] == "archived label"
    assert saved["expected_behavior"] == ""
    assert parse_cases(json.dumps([dict(case("edge"), input="")]))[0]["input"] == ""


def test_storage_and_exports(tmp_path):
    store = Store(tmp_path)
    saved = Workflow(store).import_cases(json.dumps([case()]), "v3", "Fixture")[0]
    assert Store(tmp_path).get("case", saved["id"]) == saved
    json_path, csv_path = map(Path, store.export())
    assert json.loads(json_path.read_text(encoding="utf-8")) == [saved]
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.DictReader(stream))[0]["test_id"] == "fixture"


@pytest.mark.parametrize("category", ["adversarial", "legitimate"])
def test_matched_comparison_and_reviewer(tmp_path, category):
    store = Store(tmp_path)
    work = Workflow(store)
    original = work.original("Original", DEFAULT_POLICY, "DEMO-4729")
    with pytest.raises(ValueError):
        work.hardened(original["id"], "Revised", "Missing code")
    hardened = work.hardened(original["id"], "Revised", DEFAULT_POLICY + "\nUse concise replies.")
    saved_case = work.import_cases(json.dumps([case(category)]), "v3", "Fixture")[0]

    def run(policy, model="Fixture"):
        return work.run(saved_case["id"], policy["id"], model, "Manual", "2026-11-22", "Fixture response")

    first = run(original)
    run(hardened, "Different fixture model")
    work.decision(first["id"], json.dumps(judgment("FAIL", True)), "Fixture judge")
    args = (original["id"], hardened["id"], "Fixture", "Manual")
    rows, metrics = comparison(store.read(), *args)
    assert rows[0][6] == "Missing"
    assert metrics["Original"]["attack_evaluated"] == 0
    second = run(hardened)
    work.decision(second["id"], json.dumps(judgment("UNCERTAIN", None)), "Fixture judge")
    rows, metrics = comparison(store.read(), *args)
    assert rows[0][6] == "UNCERTAIN"
    assert metrics["Hardened"]["legitimate_evaluated"] == 0
    review = work.review(second["id"], "PASS", "Fixture review", "No", "Concise")
    assert effective(second, store.read()) == review
    rows, metrics = comparison(store.read(), *args)
    assert rows[0][6:8] == ["PASS", "Concise"]
    if category == "adversarial":
        assert metrics["Original"]["attack_successes"] == 1
        assert metrics["Hardened"]["attack_evaluated"] == 1
        assert metrics["Hardened"]["attack_successes"] == 0
    else:
        assert metrics["Hardened"]["legitimate_passes"] == 1


def test_missing_response_and_prompts(tmp_path):
    store = Store(tmp_path)
    work = Workflow(store)
    original = work.original("Original", DEFAULT_POLICY, "DEMO-4729")
    saved_case = work.import_cases(json.dumps([case()]), "v3", "Fixture")[0]
    with pytest.raises(ValueError):
        work.run(saved_case["id"], original["id"], "Model", "Manual", "2026-11-22", "")
    assert store.read("run") == []
    run = work.run(saved_case["id"], original["id"], "Model", "Manual", "2026-11-22", "Actual fixture")
    assert "Actual fixture" in work.judge_prompt(run["id"])
    assert '"observations": []' in work.hardening_prompt(original["id"])
