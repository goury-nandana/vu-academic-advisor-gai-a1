# Advisor Pipeline, Specialist-Agent Demonstration and Model Comparison — A2

## Existing RAG answer pipeline

The Next.js frontend submits chat turns to the same-origin POST /api/chat route. The route:

1. Validates the question, optional profile and attachment limits.
2. Processes supported text, image and audio attachments, and reports unsupported files rather than claiming to have read them.
3. Selects relevant allowlisted official VU webpages and local academic documents.
4. Ranks retrieved passages using keyword-weighted matching and uses structured B.Tech course records for exact course lookups.
5. Escapes and separates retrieved webpages and student-supplied content as untrusted evidence.
6. Generates an answer through the configured Groq-hosted model, with explicit source-grounding, privacy and prompt-injection instructions.
7. Optionally asks the model for a structured visual summary based only on facts already present in the answer and retrieved excerpts.
8. Returns the answer, citations, model identifier, processing steps, optional visual and follow-up questions to the UI.

This is a retrieval-augmented, sequential answer pipeline. It is not a swarm of autonomous agents.

## Assignment 2 specialist-workflow extension

The controlled specialist workflow in frontend/academic-agents.ts is integrated with the authenticated synthetic demo account. The server obtains the student ID from the signed HttpOnly session via getAuthenticatedStudent; it does not trust a student ID supplied in the chat request. The profile is loaded from frontend/data/synthetic-students.json. All ten login accounts (SYN-101 through SYN-110 / VU001 through VU010) can use the workflow. Three older SYN-001 through SYN-003 records remain isolated test fixtures and are not selectable login accounts.

The six deterministic specialist stages are:

1. **Student-profile stage:** load the signed-in synthetic account's programme, admission batch, semester, completed courses and failed courses.
2. **Course-retrieval stage:** retrieve the requested B.Tech course row for that account's exact admission batch. The matcher accepts the workbook degree label B.Tech for account programme labels such as B.Tech CSE; it does not equate unrelated degree programmes.
3. **Credit-calculation stage:** sum credit values only for the account's listed completed courses that have matching semester-spread rows for the same batch and degree family. Missing rows are reported and excluded rather than guessed.
4. **Eligibility stage:** compare the course's direct prerequisites with the profile's passed and failed course lists. Missing status remains unknown; a failed prerequisite is not treated as passed.
5. **Verification stage:** check that the target course and every stated prerequisite row exist in the matching batch's source workbook records and retain source workbook/cell provenance.
6. **Recommendation stage:** return a limited prerequisite-check recommendation, or refuse to recommend when source evidence is incomplete.

The orchestration is deterministic code with six specialist modules, not six independent LLM agents. The LLM is not used to calculate the credit total or decide the prerequisite status. The chat response now exposes the six actual stages in a collapsible **Agent workflow — 6 specialist stages** panel. It does not autonomously change student records, register courses, approve credit transfers or replace a Faculty Advisor/Registrar.

### Account-integrated demonstration

Use **MTSC211 — Sustainable Smart Materials** as the example. The matching semester-spread row lists MTSC111 as its direct prerequisite. The workflow checks each logged-in synthetic profile against the course row for that profile's admission batch.

| Login ID | Synthetic profile | Admission batch | Direct prerequisite result | Completed-course credits calculated |
|---|---|---:|---|---:|
| VU001 | SYN-101 | 2026 | Insufficient information (MTSC111 is in progress) | 0 |
| VU002 | SYN-102 | 2026 | Met | 21 |
| VU003 | SYN-103 | 2025 | Met | 42 |
| VU004 | SYN-104 | 2025 | Met | 62 |
| VU005 | SYN-105 | 2024 | Met | 88 |
| VU006 | SYN-106 | 2024 | Met | 84 |
| VU007 | SYN-107 | 2023 | Met | 117 |
| VU008 | SYN-108 | 2023 | Met | 121 |
| VU009 | SYN-109 | 2022 | Met (graduated profile; not a registration recommendation) | 141 |
| VU010 | SYN-110 | 2025 | Met | 93 |

The totals are deterministic sums of the synthetic profiles' completed course codes using matching batch-specific workbook rows. They are not actual student credit totals. The direct check covers only the listed prerequisite; it does not establish overall academic eligibility, timetable availability, credit-category compliance or official registration approval.

### How to demonstrate in the UI

1. Sign in with any of the ten demo accounts (VU001–VU010).
2. Ask: **“Can I take MTSC211? Check prerequisites and calculate my completed credits.”**
3. Inspect the answer for the direct prerequisite outcome, calculated credits, recommendation and cited course evidence.
4. Expand **Agent workflow — 6 specialist stages** to show the profile, course retrieval, credit calculation, eligibility, verification and recommendation stages.
5. Repeat with VU001 and VU002 to contrast unknown/in-progress with met. Use VU009 to demonstrate that a graduated profile is not an instruction to register for another course.

### Qualitative comparison with the RAG-only path

| Capability | RAG-only answer path | Synthetic specialist workflow |
|---|---|---|
| Course information | Retrieves relevant structured rows and documents | Retrieves the exact batch-specific course row |
| Student-specific state | Uses only voluntarily supplied optional fields; no transcript database | Uses an explicitly selected synthetic course history |
| Credit total | Does not calculate from a verified transcript by default | Sums course credits from matching rows for fixture-listed completed courses |
| Direct prerequisite check | Provides source context to the answer model | Explicitly checks passed / failed / unknown prerequisite sets |
| Evidence verification | Displays retrieved sources where cited | Checks target and prerequisite rows against matching batch records |
| Recommendation | Model-generated guidance with constraints | Deterministic, limited prerequisite outcome and caveat |

This is a design/functional comparison, not a measured accuracy or latency benchmark between independent models. The synthetic test suite verifies the three fixture outcomes and credit sums against the JSON source records.

## Multimodal models and tools

- **Text generation:** openai/gpt-oss-120b via Groq.
- **Image understanding:** qwen/qwen3.8-27b via Groq.
- **Speech transcription:** whisper-large-v3-turbo via Groq.
- **Read Aloud:** browser Speech Synthesis API.
- **Visual summaries:** structured JSON from the main model rendered as accessible UI cards. This is not a general-purpose raster image or video generator.

## Model comparison — measured facts only

The benchmark harness in benchmark_runner.py is configured for three documented Groq model candidates:

- openai/gpt-oss-20b
- openai/gpt-oss-120b
- qwen/qwen3.8-27b

It is designed to send common questions and source context, record responses, latency and token usage, and leave rubric scoring to human evaluators. Its expected input workbook, VU_LLM_Benchmark_Framework.xlsx, is not present in this repository. No completed run, scored result sheet or defensible model ranking is available. No claim is made that one model outperforms another.

## Human evaluation rubric (0–4 each)

- Factual accuracy against source-backed expected outcomes.
- Grounding and correct use of actual citations.
- Absence of unsupported or hallucinated claims.
- Appropriate clarification when programme, semester or batch information is missing.

A quantitative model comparison should only be reported after the same benchmark questions and source context have been run for every available model, unavailable models have been recorded, and responses have been independently scored.
