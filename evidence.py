"""Validation and local evidence storage for manual evaluations."""

import csv
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

VERDICTS = ("PASS", "FAIL", "UNCERTAIN")
CATEGORIES = ("adversarial", "legitimate", "edge")


def required(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required.")
    return value.strip()


def parse_cases(raw):
    cases = json.loads(required(raw, "Case JSON").lstrip("\ufeff"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("Provide a nonempty JSON array of test cases.")
    seen = set()
    validated = []
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each test case must be an object.")
        if "test_id" not in case and {"id", "attack", "rule_targeted"} <= case.keys():
            legacy_id = case["id"]
            if type(legacy_id) not in (int, str) or not str(legacy_id).strip():
                raise ValueError("Archived case ID must be a number or nonempty string.")
            case = {
                "test_id": str(legacy_id),
                "input": case["attack"],
                "category": "adversarial",
                "technique": case.get("technique", case.get("category")),
                "targeted_rule": case["rule_targeted"],
                "expected_behavior": case.get("expected_safe_behavior", ""),
            }
            archived = True
        else:
            archived = False
        fields = ("test_id", "input", "category", "targeted_rule", "expected_behavior")
        for field in fields:
            if (field == "input" and case.get("category") == "edge" and isinstance(case.get(field), str)
                    or field == "expected_behavior" and archived and case[field] == ""):
                continue
            required(case.get(field), field)
        if case["category"] not in CATEGORIES:
            raise ValueError("Use adversarial, legitimate or edge as the category.")
        if case["category"] == "adversarial":
            required(case.get("technique"), "technique")
        elif "technique" in case and not isinstance(case["technique"], str):
            raise ValueError("Technique must be a string.")
        if case["test_id"] in seen:
            raise ValueError("Test IDs must be unique within an import.")
        seen.add(case["test_id"])
        validated.append({field: case[field] for field in fields + ("technique",) if field in case})
    return validated


def parse_judgment(raw, test_id, category):
    result = json.loads(required(raw, "Judge JSON").lstrip("\ufeff"))
    if not isinstance(result, dict) or result.get("test_id") != test_id:
        raise ValueError("Judge output must identify the selected test ID.")
    verdict = result.get("verdict")
    if verdict not in VERDICTS:
        raise ValueError("Verdict must be PASS, FAIL or UNCERTAIN.")
    for field in ("reason", "recommendation"):
        required(result.get(field), field)
    if not isinstance(result.get("quality", ""), str):
        raise ValueError("Quality must be a string.")
    rules = result.get("violated_rules")
    if not isinstance(rules, list) or any(not isinstance(rule, str) for rule in rules):
        raise ValueError("violated_rules must be an array of strings.")
    succeeded = result.get("attack_succeeded")
    if type(succeeded) is not bool and succeeded is not None:
        raise ValueError("attack_succeeded must be true, false or null.")
    if category == "adversarial" and verdict != "UNCERTAIN":
        if type(succeeded) is not bool or (verdict == "PASS" and succeeded):
            raise ValueError("A decisive adversarial verdict requires a consistent attack outcome.")
    return result


class Store:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, kind TEXT, payload TEXT)")

    def connect(self):
        return sqlite3.connect(self.directory / "evidence.sqlite3")

    def add(self, kind, **payload):
        return self.add_many(kind, [payload])[0]

    def add_many(self, kind, payloads):
        records = [
            dict(payload, id=uuid4().hex, kind=kind, saved_at=datetime.now(timezone.utc).isoformat())
            for payload in payloads
        ]
        with closing(self.connect()) as db, db:
            db.executemany(
                "INSERT INTO evidence VALUES (?, ?, ?)",
                [(row["id"], kind, json.dumps(row, ensure_ascii=False)) for row in records],
            )
        return records

    def read(self, kind=None):
        with closing(self.connect()) as db:
            if kind is None:
                rows = db.execute("SELECT payload FROM evidence ORDER BY rowid")
            else:
                rows = db.execute("SELECT payload FROM evidence WHERE kind = ? ORDER BY rowid", (kind,))
            return [json.loads(row[0]) for row in rows]

    def get(self, kind, key):
        with closing(self.connect()) as db:
            row = db.execute("SELECT payload FROM evidence WHERE kind = ? AND id = ?", (kind, key)).fetchone()
        if row is None:
            raise ValueError(f"Select a saved {kind}.")
        return json.loads(row[0])

    def export(self, records=None):
        if records is None:
            records = self.read()
        destination = self.directory / "exports" / uuid4().hex
        destination.mkdir(parents=True)
        json_path = destination / "evidence.json"
        csv_path = destination / "evidence.csv"
        json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        fields = sorted({"kind", "id", "saved_at"}.union(*(record.keys() for record in records)))
        with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for record in records:
                writer.writerow({key: csv_value(value) for key, value in record.items()})
        return str(json_path), str(csv_path)


def csv_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def effective(run, records):
    if run is None:
        return {}
    return next((row for row in reversed(records)
                 if row["kind"] == "decision" and row["run_id"] == run["id"]), {})


def comparison(records, original_id, hardened_id, model, environment):
    rows = []
    metrics = {side: {"attack_successes": 0, "attack_evaluated": 0,
                      "legitimate_passes": 0, "legitimate_evaluated": 0}
               for side in ("Original", "Hardened")}
    for case in (row for row in records if row["kind"] == "case"):
        pair = []
        for side, policy_id in (("Original", original_id), ("Hardened", hardened_id)):
            runs = [row for row in records if row["kind"] == "run"
                    and (row["case_id"], row["policy_id"], row["model"], row["environment"])
                    == (case["id"], policy_id, model, environment)]
            run = runs[-1] if runs else None
            decision = effective(run, records)
            pair.append((run, decision))
        if not any(run for run, _ in pair):
            continue
        row = [case["test_id"], case["category"], case.get("technique", "")]
        for side, (run, decision) in zip(metrics, pair):
            verdict = decision.get("verdict")
            row.extend([verdict or ("Awaiting evaluation" if run else "Missing"),
                        decision.get("quality", ""),
                        run["response"] if run else ""])
            # Include only matching pairs with decisive evaluations on both sides.
            if all(item.get("verdict") in ("PASS", "FAIL") for _, item in pair):
                opposite = pair[1 if side == "Original" else 0][1]
                if case["category"] == "adversarial" and all(
                    type(item.get("attack_succeeded")) is bool for item in (decision, opposite)
                ):
                    metrics[side]["attack_evaluated"] += 1
                    metrics[side]["attack_successes"] += decision["attack_succeeded"]
                if case["category"] == "legitimate":
                    metrics[side]["legitimate_evaluated"] += 1
                    metrics[side]["legitimate_passes"] += verdict == "PASS"
        rows.append(row)
    return rows, metrics
