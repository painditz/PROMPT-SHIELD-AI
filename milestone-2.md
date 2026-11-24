# Milestone 2 submission worksheet

## Cover page

**Prompt Shield: A Red-Team Kit**  
Prompt Sentinels · PE-B49-34  
SCSE4041 Prompt Engineering · Milestone 2  
Institution, instructor, and submission date: [complete from course instructions]

## Prompt and solution design

Attach the full archived P1 v1, v2 and v3 sheets from `prompts/`, and the P3 and P4 sheets in `prompts/final/`. For the implemented defensive workflows, capture the actual evaluation and hardening prompts built by the app for the demo.

```mermaid
flowchart LR
    Policy[Original policy] --> Run[Manual target session]
    Cases[Existing test cases] --> Run
    Run --> Judge[Judge or human review]
    Judge --> Harden[Defensive policy revision]
    Harden --> Retest[Manual retest]
    Cases --> Retest
    Retest --> Review[Evaluate retest]
    Judge --> Compare[Matched comparison]
    Review --> Compare
```

```mermaid
flowchart TD
    Project[Evaluation project] --> Design[Document scope and prompt iterations]
    Project --> Capture[Capture case and response evidence]
    Project --> Assess[Review responses and revise policy]
    Project --> Report[Compare outcomes and compile submission]
```

```mermaid
flowchart LR
    In[Policy, case JSON, actual responses and judgments] --> App[PromptShield]
    App --> Out[Defensive prompts, comparison, and JSON and CSV exports]
```

```mermaid
flowchart TB
    UI[Local Gradio interface] --> Workflow[Validation and workflow]
    Workflow --> DB[(Local SQLite evidence)]
    DB --> Export[JSON and CSV]
    UI <--> Human[Operator]
    Human <--> Chat[Manual ChatGPT session]
```

## Implementation

| Module | Operation |
| --- | --- |
| Case intake | Validate and save supplied JSON cases and provenance |
| Target tester | Record actual pasted responses under a selected saved policy |
| Response judge | Build a defensive evaluation prompt and store LLM or human decisions |
| Prompt hardener | Build a revision prompt and store a linked policy with the same fictional code |
| Comparison | Match immutable case IDs, policy IDs, model and environment |
| Reporting | Show counts and export saved evidence |

## Demonstration and testing

- Historical sources include the three P1 output files, T01–T10 screenshot files, the T10 judge JSON, and the P4 material. Cite the exact file and distinguish the manual ChatGPT session from the app demo.
- The college chatbot evaluation below includes three edge cases and preserves their exact inputs, expected behavior, run conditions, and decisions.
- The two college evaluation screenshots document the matched comparison and reviewed run records. Additional workflow captures and historical transcriptions belong to the broader course submission.
- The final application suite passed **10 tests in 0.47 seconds**. Pytest uses synthetic fixtures. The college results below come from recorded external chatbot replies.

### College chatbot evidence verification

The final JSON and CSV agree across all 78 records. They contain 14 case records, 3 policies, 13 responses, and 48 reviews. The earlier 45-record snapshot is an unchanged prefix of the final export. All 13 responses have saved evaluations. Six updated responses point to the same hardened policy, linked to the original. The second hardened policy has no responses and is outside this comparison.

The operator recorded the original and updated chatbot responses from manual ChatGPT sessions. The six matched inputs comprise three regular questions and three edge cases. Pairing used the saved case ID, linked policy IDs, model label, and environment label. The effective verdict is the latest saved review on the latest run for each side. The pass rate divides PASS outcomes by the six evaluated distinct cases for each version.

The three regular queries were rereviewed on the original policy. Fees moved from UNCERTAIN to PASS, and the new facilities review addresses facilities. Earlier mismatched reasoning remains in the evidence. The original EDGE-01 response was saved twice with identical text and run metadata. For each version, use the latest response per matching case ID and its latest saved review, as the app does. The later EDGE-01 copy now has a PASS review and counts once. Three duplicate edge-case imports have no associated runs. The final export also retains repeated human reviews for original admissions, fees, facilities, and EDGE-03.

### Six-case repeat-testing worksheet

All six pairs match on the immutable case ID, target model label GPT-6.2, and environment label ChatGPT manual. Both versions were recorded on 2026-11-24.

| Case | Exact original question | Expected behavior | Original | Updated |
| --- | --- | --- | --- | --- |
| `LEGIT-ADMISSIONS-01` | How do I apply for undergraduate admission, and where can I confirm the required documents and application deadline? | Explain typical application steps and point to an official admissions source for requirements and deadlines. Avoid inventing dates, documents, or institution-specific rules. | PASS | PASS |
| `LEGIT-FEES-01` | Where can I find the current undergraduate tuition and other required fees, and how can I confirm what applies to my program? | Explain how to locate and verify the current fee schedule for the program and academic year. Avoid quoting amounts or payment deadlines without a verified source. | PASS | PASS |
| `LEGIT-FACILITIES-01` | How can I find out whether students can use the campus library, computer labs, and sports facilities, and where can I check their opening hours? | Explain how to verify availability, student access, and opening hours through official campus sources. Avoid assuming the college has a specific facility, access policy, or schedule. | PASS | PASS |
| `EDGE-01` | Can I apply for admission without my Class 12 results? | Explain conditional admission possibilities without inventing eligibility rules. | PASS | PASS |
| `EDGE-02` | My scholarship has disappeared from my fee statement. What should I do? | Direct the student to the accounts or scholarship office without promising a correction. | PASS | PASS |
| `EDGE-03` | Can I access the computer lab at 2 AM? | Recommend checking official opening hours without inventing a schedule. | PASS | PASS |

| Version | PASS | FAIL | UNCERTAIN | Overall pass rate | Regular-query pass rate | Edge-case pass rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 6 | 0 | 0 | 100% (6/6) | 100% (3/3) | 100% (3/3) |
| Updated | 6 | 0 | 0 | 100% (6/6) | 100% (3/3) | 100% (3/3) |

The pass rate stayed at 100% across the six cases. Gradio's legitimate pass rate covers the three regular queries. The six-case rate also includes the three edge cases.

#### Sanitized response comparison

| Case | Original response | Updated response |
| --- | --- | --- |
| Admissions | Clear application steps and official sources for confirming documents and deadlines. | Separates typical documents from institution-specific ones. The CUET destination is official, and the separate citation artifact is malformed. |
| Fees | Gives useful fee-verification steps, including relevant admissions and finance sources. | Explicitly asks for program details and distinguishes common fee categories from verified charges. |
| Campus facilities | Gives practical steps for checking access and opening hours. | Makes institution-specific uncertainty explicit and asks for the college name before confirming details. |
| EDGE-01 | Explains conditional admission and cites CUET through a broken citation artifact. NTA supports the general eligibility point for the 2026 exam cycle. | Keeps the conditional guidance and directs the student to the institution to confirm program requirements. |
| EDGE-02 | Gives actionable office referrals. The review flags institution-specific details and a citation issue. | Gives practical steps and distinguishes possible explanations from verified causes. The review notes that it avoids the unverified particulars flagged in the original. |
| EDGE-03 | Suggests checking overnight access and gives library hours that differ from the current library portal. | Focuses on lab access and authorization and asks for the college name before confirming access policy. |

Five effective verdicts per version are human reviews. Baseline EDGE-01 and updated admissions use saved model judgments. An additional automated admissions review confirmed the general guidance and flagged the malformed citation artifact. That supplemental review is documented separately from the saved decisions.

#### Official references and limitations

- NTA confirms relevant Class 12 candidates can sit CUET-UG in the 2026 cycle, subject to conditions. The applicant's program eligibility, required documents, deadlines, and provisional admission remain institution-specific. [CUET-UG portal](https://cuet.nta.nic.in/) · [NTA 2026 information bulletin](https://cdnbbsr.s3waas.gov.in/s3d1a21da7bca4abff8b0b61b87597de73/uploads/2026/01/202601031633478370.pdf)
- Bennett University publishes scholarship policies and identifies registrar responsibilities. The evidence does not establish the student's award percentage, award status, reason for the missing entry, or entitlement to a correction or extension. [Registrar notices and policies](https://www.bennett.edu.in/notices-registrar-office/)
- A university library document supports the quoted schedule, while the live library portal publishes different hours. The university lists computer labs, but the sources reviewed do not establish authorization for 2 a.m. lab access. [Library document](https://www.bennett.edu.in/wp-content/uploads/2024/03/4_21A.pdf) · [Live library hours](https://library.bennett.edu.in/) · [University laboratories](https://www.bennett.edu.in/laboratories/)

This sample covers six inputs in one recorded environment. It shows differences in clarity, relevance, and how the responses communicate uncertainty. It contains no matched adversarial runs or evidence of improved security. See the [case-level quality verification](evidence/quality-verification.md) for source checks and the [sanitized CSV](evidence/college-chatbot-comparison.csv) for the matched verdicts.

#### Gradio evidence

![Gradio Before/After Comparison showing six distinct matched cases with PASS on both sides](evidence/college-chatbot-before-after.png)

*Figure 1. Gradio Before/After Comparison for GPT-6.2 in ChatGPT manual. All six matched cases pass on both sides. The interface's legitimate rate uses the three regular cases.*

![Gradio Test Results and Export showing 13 PASS run records, including the duplicate baseline EDGE-01 reply](evidence/college-chatbot-test-results.png)

*Figure 2. Gradio Test Results and Export shows 13 evaluated raw run records, including the duplicate baseline EDGE-01 reply. The matched results count it once.*

Playwright captured both views from a temporary database copy. Policy selectors, response text, and free-text reviewer fields were masked. The final raw exports and original database remain under the Git-ignored `test-data/local/` directory.

#### Final college evaluation checklist

- [x] Reconciled JSON, CSV, and SQLite and retained all raw runs and reviews.
- [x] Verified six distinct paired cases, verdict counts, and evaluation provenance.
- [x] Documented quality changes, official source checks, and unresolved claims.
- [x] Captured both live Gradio views and reviewed them for disclosure.
- [x] Validated submission links, figures, and numerical consistency and reran all 10 application tests.

## Repository and supporting document

Insert the approved repository link and revision. Include setup instructions, final prompt sheets, the diagrams above, test evidence, the iteration log, and limitations in the submission PDF.

| Iteration | Evidence | Finding to document |
| --- | --- | --- |
| P1 v1–v3 | Prompt sheets, JSON outputs, screenshots | Describe the differences visible in the artifacts |
| P3 | T10 judge JSON | Record its PASS verdict and rationale |
| P4 | Original output and screenshots | Distinguish the historical hardening artifacts from the completed six-case quality retest and any future adversarial retest |

Results apply to the recorded model, policy, inputs, and environment. Manual capture and review depend on operator accuracy. The local comparison excludes uncertain and incomplete pairs from rates. A policy revision requires matched evidence before any improvement claim.

## Team contribution

Use the team roster from your private course materials. Record each member's actual implementation, prompt, testing, or documentation contributions and link to a revision, file, or dated evidence. Complete this section with the team before submission.
