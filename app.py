"""Local Gradio interface for PromptShield."""

import json
import os
from datetime import date
from functools import wraps
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from evidence import Store, VERDICTS, comparison, effective, required
from workflow import DEFAULT_POLICY, Workflow

ROOT = Path(__file__).resolve().parents[1]


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def checked(action):
    @wraps(action)
    def invoke(*args):
        try:
            return action(*args)
        except ValueError as exc:
            raise gr.Error(str(exc)) from exc
    return invoke


def build_app(store):
    work = Workflow(store)

    def select(kind, predicate=lambda row: True):
        labels = {
            "policy": lambda row: f'{row["label"]} ({row["version"]})',
            "case": lambda row: f'{row["test_id"]} ({row["category"]}, {row["import_version"]})',
            "run": lambda row: f'{row["test_id"]} / {row["version"]} / {row["model"]} / {row["date"]}',
        }
        return gr.update(choices=[
            (f'{labels[kind](row)} [{row["id"][:8]}]', row["id"])
            for row in store.read(kind) if predicate(row)
        ], value=None)

    def inspect_case(case_id):
        case = store.get("case", case_id)
        return case["input"], json_text({key: case.get(key) for key in
                                       ("test_id", "category", "technique", "targeted_rule", "expected_behavior")})

    def compare(original_id, hardened_id, model, environment):
        store.get("policy", original_id)
        hardened = store.get("policy", hardened_id)
        if hardened.get("original_id") != original_id:
            raise ValueError("Select a hardened policy linked to this original.")
        rows, metrics = comparison(store.read(), original_id, hardened_id,
                                   required(model, "Model"), required(environment, "Environment"))
        for values in metrics.values():
            for numerator, denominator, rate in (
                ("attack_successes", "attack_evaluated", "attack_success_rate"),
                ("legitimate_passes", "legitimate_evaluated", "legitimate_pass_rate"),
            ):
                values[rate] = (f'{values[numerator] / values[denominator]:.1%}'
                                if values[denominator] else "No eligible pairs")
        return rows, json_text(metrics)

    def report():
        records = store.read()
        rows = []
        totals = dict.fromkeys((*VERDICTS, "Awaiting evaluation"), 0)
        cases = {row["id"]: row for row in records if row["kind"] == "case"}
        for run in (row for row in records if row["kind"] == "run"):
            case = cases[run["case_id"]]
            decision = effective(run, records)
            verdict = decision.get("verdict", "Awaiting evaluation")
            totals[verdict] += 1
            rows.append([run["test_id"], case["category"], case.get("technique", ""),
                         run["version"], run["model"], run["environment"], run["date"],
                         verdict, decision.get("reason", ""), decision.get("quality", "")])
        return rows, json_text({"Recorded responses": len(rows),
                                "Completed evaluations": sum(totals[key] for key in VERDICTS), **totals})

    with gr.Blocks(title="PromptShield", analytics_enabled=False) as app:
        gr.Markdown("# PromptShield\nPrompt Sentinels · PE-B49-34 · Milestone 2")
        with gr.Tab("Overview"):
            gr.Markdown(
                "Save an original fictional policy and import test cases. Record real responses, evaluate them, "
                "save a revised policy, and repeat the same cases. Use the same model and testing environment "
                "for matched comparisons. Archived ChatGPT evidence is in the project’s test-data and docs folders."
            )
            original_label = gr.Textbox(label="Original policy label", value="College assistant")
            protected_code = gr.Textbox(label="Fictional protected code", value="DEMO-4729")
            policy = gr.Textbox(label="Original policy", value=DEFAULT_POLICY, lines=6)
            save_original = gr.Button("Save original policy")
            original_status = gr.Textbox(label="Save status", interactive=False)
        with gr.Tab("Attack Generator"):
            gr.Markdown("Paste an archived P1 output or import cases in the app format. Each app-format object needs test_id, input, category, "
                        "targeted_rule and expected_behavior. Adversarial cases also need technique. Use "
                        "adversarial, legitimate or edge as the category.")
            raw_cases = gr.Textbox(label="Existing test cases (JSON array)", lines=8)
            import_version = gr.Textbox(label="Experiment version")
            import_model = gr.Textbox(label="Source or model")
            import_button = gr.Button("Validate and save cases")
            import_status = gr.Textbox(label="Import status", interactive=False)
        with gr.Tab("Target Chatbot Tester"):
            refresh_tester = gr.Button("Load saved cases and policies")
            test_case = gr.Dropdown(label="Test case")
            test_policy = gr.Dropdown(label="Policy")
            case_input = gr.Textbox(label="Recorded test input", lines=4, interactive=False)
            case_info = gr.Code(label="Case details", language="json", interactive=False)
            test_instructions = gr.Textbox(label="Saved chatbot instructions", lines=6,
                                           interactive=False, show_copy_button=True)
            test_model = gr.Textbox(label="Target model")
            test_environment = gr.Textbox(label="Testing environment", value="ChatGPT manual")
            run_date = gr.Textbox(label="Test date (YYYY-MM-DD)", value=date.today().isoformat())
            response = gr.Textbox(label="Actual chatbot response (user-provided)", lines=6)
            save_run = gr.Button("Record response")
            run_status = gr.Textbox(label="Save status", interactive=False)
        with gr.Tab("Response Judge"):
            refresh_runs = gr.Button("Load saved responses")
            judge_run = gr.Dropdown(label="Recorded response")
            make_judge = gr.Button("Build evaluation prompt")
            judge_prompt = gr.Textbox(label="Evaluation prompt", lines=10, interactive=False, show_copy_button=True)
            raw_judge = gr.Textbox(label="Actual LLM judgment (JSON)", lines=6)
            judge_model = gr.Textbox(label="Judge model")
            save_judge = gr.Button("Record judgment")
            view_judge = gr.Button("Load current judgment")
            judge_status = gr.Code(label="Current judgment", language="json", interactive=False)
            review_verdict = gr.Radio(VERDICTS, label="Reviewer verdict")
            attack_outcome = gr.Radio(["Yes", "No", "Undetermined"], label="Did the adversarial test succeed?",
                                      value="Undetermined")
            review_reason = gr.Textbox(label="Reviewer reasoning")
            quality = gr.Textbox(label="Response quality notes")
            save_review = gr.Button("Record human review")
        with gr.Tab("Prompt Hardener"):
            refresh_original = gr.Button("Load original policies")
            harden_original = gr.Dropdown(label="Original policy")
            make_hardening = gr.Button("Build defensive hardening prompt")
            hardening_prompt = gr.Textbox(label="Hardening prompt", lines=10, interactive=False, show_copy_button=True)
            hardened_label = gr.Textbox(label="Hardened policy label")
            hardened_policy = gr.Textbox(label="Actual revised policy", lines=8)
            save_hardened = gr.Button("Save hardened policy")
            hardened_status = gr.Textbox(label="Save status", interactive=False)
        with gr.Tab("Before/After Comparison"):
            refresh_compare = gr.Button("Load policy versions")
            compare_original = gr.Dropdown(label="Original policy")
            compare_hardened = gr.Dropdown(label="Hardened policy")
            compare_model = gr.Textbox(label="Target model used for both runs")
            compare_environment = gr.Textbox(label="Testing environment used for both runs", value="ChatGPT manual")
            gr.Markdown("Rates use matched pairs with decisive evaluations on both sides. The latest run for "
                        "each case and policy is used.")
            compare_button = gr.Button("Compare matched tests")
            compare_table = gr.Dataframe(headers=[
                "Test", "Category", "Technique", "Original verdict", "Original quality", "Original response",
                "Hardened verdict", "Hardened quality", "Hardened response",
            ], interactive=False)
            compare_metrics = gr.Code(label="Observed outcomes", language="json", interactive=False)
        with gr.Tab("Test Results and Export"):
            show_results = gr.Button("Refresh summary")
            totals = gr.Code(label="Test counts", language="json", interactive=False)
            results = gr.Dataframe(headers=[
                "Test", "Category", "Technique", "Policy version", "Model", "Environment", "Test date",
                "Verdict", "Reason", "Quality",
            ], interactive=False)
            export_button = gr.Button("Export saved evidence")
            json_file = gr.File(label="JSON evidence", interactive=False)
            csv_file = gr.File(label="CSV evidence", interactive=False)

        def policies(version):
            return select("policy", lambda row: row["version"] == version)

        save_original.click(checked(lambda *args: "Saved " + work.original(*args)["label"]),
                            [original_label, policy, protected_code], original_status)
        import_button.click(checked(lambda *args: f"Saved {len(work.import_cases(*args))} cases."),
                            [raw_cases, import_version, import_model], import_status)
        refresh_tester.click(lambda: (select("case"), select("policy")), outputs=[test_case, test_policy])
        test_case.change(checked(lambda key: inspect_case(key) if key else ("", "")), test_case, [case_input, case_info])
        test_policy.change(checked(lambda key: store.get("policy", key)["policy"] if key else ""),
                           test_policy, test_instructions)
        save_run.click(checked(lambda *args: "Recorded " + work.run(*args)["test_id"]),
                       [test_case, test_policy, test_model, test_environment, run_date, response], run_status)
        refresh_runs.click(lambda: select("run"), outputs=judge_run)
        make_judge.click(checked(work.judge_prompt), judge_run, judge_prompt)
        view_judge.click(checked(lambda key: json_text(effective(store.get("run", key), store.read("decision")))),
                         judge_run, judge_status)
        save_judge.click(checked(lambda *args: json_text(work.decision(*args))),
                         [judge_run, raw_judge, judge_model], judge_status)
        save_review.click(checked(lambda *args: json_text(work.review(*args))),
                          [judge_run, review_verdict, review_reason, attack_outcome, quality], judge_status)
        refresh_original.click(lambda: policies("original"), outputs=harden_original)
        make_hardening.click(checked(work.hardening_prompt), harden_original, hardening_prompt)
        save_hardened.click(checked(lambda *args: "Saved " + work.hardened(*args)["label"]),
                            [harden_original, hardened_label, hardened_policy], hardened_status)
        refresh_compare.click(lambda: (policies("original"), policies("hardened")),
                              outputs=[compare_original, compare_hardened])
        compare_button.click(checked(compare), [compare_original, compare_hardened, compare_model, compare_environment],
                             [compare_table, compare_metrics])
        show_results.click(report, outputs=[results, totals])
        export_button.click(lambda: store.export(), outputs=[json_file, csv_file])
    return app


if __name__ == "__main__":
    load_dotenv(ROOT / ".env")
    store = Store(ROOT / "test-data" / "local")
    build_app(store).launch(server_name="127.0.0.1", server_port=int(os.getenv("PROMPTSHIELD_PORT", "7860")),
                            share=False, allowed_paths=[str(store.directory / "exports")])
