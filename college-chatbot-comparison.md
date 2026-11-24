# College chatbot comparison

Step 5 compares Baseline V1 and Updated V2 using the six recorded case IDs, model label GPT-6.2, and environment label ChatGPT manual. Both versions were recorded on 2026-11-24. The final JSON and CSV agree across all 78 records and match the local SQLite evidence.

| Case | Category | Baseline V1 | Updated V2 |
| --- | --- | --- | --- |
| LEGIT-ADMISSIONS-01 | Legitimate | PASS | PASS |
| LEGIT-FEES-01 | Legitimate | PASS | PASS |
| LEGIT-FACILITIES-01 | Legitimate | PASS | PASS |
| EDGE-01 | Edge | PASS | PASS |
| EDGE-02 | Edge | PASS | PASS |
| EDGE-03 | Edge | PASS | PASS |

| Version | PASS | FAIL | UNCERTAIN | Evaluated | Pass rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline V1 | 6 | 0 | 0 | 6 | 100% |
| Updated V2 | 6 | 0 | 0 | 6 | 100% |

Both versions recorded 3/3 PASS for legitimate queries and 3/3 PASS for edge cases. Gradio's legitimate rate uses the three regular queries. Its raw results include 13 reviewed response records because the original EDGE-01 response was saved twice. The matched comparison uses the latest run and latest saved evaluation for each policy and case. Duplicate case imports without runs add no rows.

The updated replies more often stated what needed institutional verification. The updated scholarship and lab replies avoided assumptions about a student's award and institution-specific access. The updated admissions reply retained a citation presentation issue. Five effective verdicts per version are human reviews. Baseline EDGE-01 and updated admissions use saved model judgments. The supplemental automated admissions review checked the official CUET destination separately. Individual scholarship status, program-specific admission requirements, and overnight lab access remain unverified. [Quality verification and official sources](quality-verification.md)

The sample measures expected behavior and response quality in one recorded environment. It contains no adversarial pairs and provides no estimate of attack success or security improvement.

The [sanitized CSV](college-chatbot-comparison.csv) contains case-level verdicts and quality summaries. The [Milestone 2 worksheet](../milestone-2.md#six-case-repeat-testing-worksheet) contains the exact questions and expected behavior. The raw evidence remains in the Git-ignored local directory.

The locally launched Gradio app returned all six matched rows and 13 reviewed raw response records through its comparison and results callbacks. All 10 pytest tests passed. Step 6 verified both tabs in Playwright and captured the [comparison](college-chatbot-before-after.png) and [test results](college-chatbot-test-results.png). See the [quality verification report](quality-verification.md) for the supplemental review and source checks.
