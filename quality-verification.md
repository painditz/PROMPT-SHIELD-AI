# Step 6 — College chatbot quality verification

Reviewed all six Baseline V1 and Updated V2 pairs recorded on 2026-11-24 with GPT-6.2 in ChatGPT manual. The pairs match by saved case ID and linked policy. The final CSV, JSON, and SQLite records agree. The duplicate EDGE-01 run counts once. Both versions retain their six recorded PASS verdicts. This supplemental review preserves the saved verdicts and reviews.

## Pair-by-pair findings

| Case | Baseline V1 | Updated V2 | Quality finding |
| --- | --- | --- | --- |
| Admissions | Gives a clear application sequence, qualifies common documents, and directs applicants to official sources. | Separates typical documents from institution-specific requirements, asks for the program and year, and names the official CUET portal where applicable. | More explicit about uncertainty and what to verify. The added reference table is useful, but a broken citation reference and stray markup interrupt reading. |
| Fees | Gives relevant fee categories, official sources, and program-specific verification steps. | Requests institution, program, specialization, and year and explicitly says current amounts cannot be confirmed without them. | Both are actionable and avoid quoting amounts or deadlines. V2 makes the information gap more explicit. References to admissions offices and application fees in V1 are relevant to fee verification. |
| Campus facilities | Gives relevant sources for checking library, lab, and sports access, hours, and booking. | Explicitly states that availability, access, and hours vary and asks for the institution before confirming them. | Both give clear verification steps. V2 more directly distinguishes general guidance from institution-specific facts. |
| EDGE-01 · Class 12 results | Explains conditional admission and invokes CUET-UG through a broken citation reference. | Gives a conditional application route, states that admission is unguaranteed, and refers the applicant to the institution. | V2 reads more clearly and avoids an exam detour. The broad V1 exam-eligibility point is supported for the 2026 cycle within the limits below. Neither reply establishes an individual program's eligibility. |
| EDGE-02 · Missing scholarship | Suggests practical steps, then assumes an institution and introduces a personal award percentage and contact details absent from the question. | Distinguishes possible causes from confirmed facts, gives a document checklist, and recommends written confirmation without promising correction or an extension. | V2 stays relevant and avoids assuming an award, institution, or student account status. |
| EDGE-03 · Lab access at 2 a.m. | Gives useful access-check steps, then assumes an institution and adds library hours unrelated to computer lab access. | Focuses on lab hours, authorization, and campus entry. Explicitly says access cannot be confirmed without the institution. | V2 is more focused and avoids presenting a library schedule where lab authorization is needed. |

## Official source checks

| Flagged claim or reference | Verification |
| --- | --- |
| Updated admissions CUET reference | The linked destination is the official CUET-UG portal. NTA explains that universities set their own admissions and program criteria. The portal supports general exam guidance, while the institution's admissions material is needed for documents, deadlines, and eligibility. [Official CUET-UG portal](https://cuet.nta.nic.in/) · [NTA 2026 Information Bulletin, §§3.1, 3.3, 12.4](https://cdnbbsr.s3waas.gov.in/s3d1a21da7bca4abff8b0b61b87597de73/uploads/2026/01/202601031633478370.pdf) |
| Baseline EDGE-01 eligibility before Class 12 results | The NTA bulletin supports exam eligibility for candidates appearing in Class 12 or an equivalent examination in 2026, subject to relevant conditions. Eligibility for another cycle, a particular applicant, or an institution's provisional admission remains unverified. [NTA 2026 Information Bulletin, §§3.1, 3.3](https://cdnbbsr.s3waas.gov.in/s3d1a21da7bca4abff8b0b61b87597de73/uploads/2026/01/202601031633478370.pdf) |
| Baseline EDGE-02 scholarship and registrar | The institution named in the reply publishes year-specific scholarship policies and lists the Registrar's office among the offices responsible for award and continuation. The public material cannot establish the student's institution, prior award percentage, current award status, reason for the missing entry, or entitlement to a correction or extension. Those details remain unverifiable from the evidence. [Bennett University Registrar notices and scholarship policies](https://www.bennett.edu.in/notices-registrar-office/) |
| Baseline EDGE-03 library hours and overnight lab access | A Bennett university library document supports the quoted 9 a.m.–11 p.m. schedule and extension to 2 a.m. before exams. The live library portal lists 24/7 library access and separate circulation hours, so the quoted schedule cannot be relied on as current. The university lists computer labs. No official source reviewed established permission to use a computer lab at 2 a.m. [Library document](https://www.bennett.edu.in/wp-content/uploads/2024/03/4_21A.pdf) · [Live library hours](https://library.bennett.edu.in/) · [University laboratories](https://www.bennett.edu.in/laboratories/) |

The saved text contains malformed citation artifacts in updated admissions and baseline EDGE-01, EDGE-02, and EDGE-03. These include logo-only favicon links and detached source labels. Several passages also retain an HTML space entity. A genuine destination link can coexist with a broken citation artifact, as it does in updated admissions.

## Additional automated review — Updated V2 admissions

**Automated assistant review, supplemental and unsaved in the evidence database. Assessment: PASS with a citation presentation issue.** The review applied the saved case expectation to the genuine response and checked the cited destination against NTA's official materials.

| Dimension | Finding |
| --- | --- |
| Accuracy | General steps and document examples are qualified. The official CUET portal is relevant where applicable. No exact deadline or document list is established for the unnamed institution. |
| Relevance | Addresses how to apply and where to confirm documents and deadlines. |
| Clarity | Short steps and a source table help scanning. The stray favicon citation, detached source label, and HTML entity reduce readability. |
| Usefulness | Gives an actionable verification path and asks for the institution, program, and year. |
| Uncertainty | Explicitly limits its ability to confirm institution-specific requirements without more information. |

The original admissions model review remains in the evidence. This review adds an independent source check by the automated assistant and does not change the saved result.

## Validation and limits

Playwright drove Chromium-based Edge through both Gradio tabs using a temporary copy of the original SQLite database. The [Before/After Comparison capture](college-chatbot-before-after.png) shows six matched rows. The [Test Results and Export capture](college-chatbot-test-results.png) shows 13 reviewed run records, including the repeated original EDGE-01 response. The capture session used a taller table and masked policy selectors, response text, and free-text reviewer fields.

The existing suite passed **10 tests in 0.44 seconds**. Raw exports, the SQLite database, and all saved evaluations were preserved. The matched six-case set measures response quality and appropriate uncertainty. It contains no adversarial comparison and supports no security improvement claim.
