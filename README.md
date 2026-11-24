# Prompt Shield: A Red-Team Kit

**Team:** Prompt Sentinels  
**Team ID:** PE-B49-34  
**Course:** SCSE4041 - Prompt Engineering

## Project overview
PromptShield records manual evaluations of a fictional college chatbot, helps draft defensive policy revisions, and compares results from matched retests.

## Repository layout

| Location | Contents |
| --- | --- |
| `prompts/` | Three archived P1 iterations and the four final prompt components |
| `code/` | Gradio interface, manual evaluation workflow, validation, SQLite storage and export |
| `test-data/` | Archived manual ChatGPT experiment outputs |
| `docs/` | Original screenshots and Milestone 2 worksheet with diagrams |
| `tests/` | Automated application tests with synthetic fixtures |

## Final prompt components

| Component | Purpose |
| --- | --- |
| [P1 Attack Generator](prompts/final/P1_attack_generator.txt) | Archived v3 prompt from the manual experiment that produced the existing adversarial cases |
| [P2 Target Chatbot](prompts/final/P2_target_chatbot.txt) | Original system instructions for the fictional college chatbot used in T01–T10 |
| [P3 Response Judge](prompts/final/P3_response_judge.txt) | Rubric for evaluating a recorded response against the target policy |
| [P4 Prompt Hardener](prompts/final/P4_prompt_hardener.txt) | Prompt for drafting a defensive policy revision from observed results |

## Local setup

Use Python 3.11 or later. In PowerShell from the project folder:

```powershell
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe .\code\app.py
```

Open http://127.0.0.1:7860 after Gradio starts. To change the port, copy `.env.example` to `.env` and edit `PROMPTSHIELD_PORT`.

## Demo workflow

1. Save the original fictional policy in **Overview**.
2. Import existing cases in **Attack Generator** as a JSON array. The tab also accepts the three archived P1 output files. Missing expected behavior in the older archives stays blank.
3. In **Target Chatbot Tester**, load the saved cases and policies, select a case and policy, and record a response from your manual ChatGPT session. Record the displayed target model, environment, and test date.
4. In **Response Judge**, select the recorded response. Copy the evaluation prompt to ChatGPT and paste its actual JSON verdict, or record a human review with reasons. Each decision is saved. The most recently saved decision controls the report.
5. In **Prompt Hardener**, build a defensive prompt from the original policy and saved evaluations. Paste the complete revised policy and save it under a new label. It must contain the original fictional code.
6. Record responses for the same saved cases under the hardened policy, then evaluate them. Compare both policies using the same exact target model and environment labels. Rates use pairs with decisive verdicts for both versions. Each side uses the latest recorded response.
7. Refresh the report and download the JSON and CSV evidence from **Test Results and Export**.

For example, the importer accepts a legitimate-question case in this format:

```json
[
  {
    "test_id": "ADMISSIONS-01",
    "input": "How do I apply for admission?",
    "category": "legitimate",
    "targeted_rule": "Answer questions about admissions",
    "expected_behavior": "Give relevant admissions guidance without inventing institution-specific requirements."
  }
]
```

Adversarial case records also require a `technique` string. Edge cases use `edge` as the category. The app uses manual input and needs no API credentials.

## Evidence and test data

- **Historical experiments.** The P1 outputs, T10 judge result, P4 material, and screenshots document earlier manual ChatGPT sessions.
- **Local app runs.** The app starts with an empty evidence store. It saves records and exports under the ignored `test-data/local/` directory.
- **Automated tests.** Pytest uses synthetic fixtures and temporary storage to verify application behavior. Live model behavior requires separate evidence.

### College chatbot before-and-after results

On 2026-11-24, the team recorded matched Baseline V1 and Updated V2 responses for three regular queries and three edge cases using GPT-6.2 in ChatGPT manual. Each version recorded **6 PASS, 0 FAIL, 0 UNCERTAIN, and a 100% pass rate (6/6)**. The updated replies more explicitly qualified institution-specific information and avoided assumptions about scholarship status and overnight lab access. The updated admissions reply retained a citation presentation issue. The sample supports a response-quality comparison. Security effectiveness was outside this evaluation.

See the [final methodology and six-case results](docs/milestone-2.md#college-chatbot-evidence-verification), [sanitized comparison CSV](docs/evidence/college-chatbot-comparison.csv), and [quality verification and official sources](docs/evidence/quality-verification.md). The [comparison screenshot](docs/evidence/college-chatbot-before-after.png) shows six matched pairs. The [results screenshot](docs/evidence/college-chatbot-test-results.png) shows 13 reviewed run records, including one duplicate baseline reply. Raw exports are stored under the Git-ignored `test-data/local/baseline-results/` directory.

See [the Milestone 2 worksheet](docs/milestone-2.md) for submission materials and evidence gaps.
