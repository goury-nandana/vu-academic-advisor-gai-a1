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

The repository now contains a controlled specialist-stage workflow in frontend/academic-agents.ts. It is explicitly selected from the sidebar and uses only the invented profiles in frontend/data/synthetic-students.json. It does not read or imitate a real student's VU account.

The six stages are:

1. **Student-profile stage:** load one explicitly selected synthetic fixture (SYN-001, SYN-002 or SYN-003).
2. **Course-retrieval stage:** retrieve the requested B.Tech course row for the fixture's admission batch.
3. **Credit-calculation stage:** sum credit values only for the fixture's listed completed courses that have matching rows in the same batch's structured source data.
4. **Eligibility stage:** compare the course's direct prerequisites with the fixture's passed and failed course lists. Unknown prerequisites remain unknown.
5. **Verification stage:** check that the target course and prerequisite rows exist in the matching batch's source workbook records and retain provenance.
6. **Recommendation stage:** return a limited prerequisite-check recommendation, or refuse to recommend when the source evidence is incomplete.

The orchestration is deterministic code with specialist modules, not six independent LLM agents. It does not autonomously change student records, register courses, approve credit transfers or replace a Faculty Advisor/Registrar.

### Demonstration cases

The selected course is B.Tech 2025 COMP302 — Internet of Things (2 credits). Its source row lists direct prerequisites COMP132, COMP201, COMP206, COMP208 and COMP301.

| Synthetic profile | Designed scenario | Direct prerequisite result | Completed-course credit sum |
|---|---|---|---:|
| SYN-001 | All five direct prerequisites are listed as completed | Prerequisites recorded as met | 29 |
| SYN-002 | COMP206 is listed as failed | Prerequisite not met | 25 |
| SYN-003 | COMP206 and COMP208 are neither completed nor listed as failed | Insufficient information | 21 |

The credit sums are calculated from matching 2025 B.Tech semester-spread rows for the completed course codes in each artificial profile. These are fixture calculations, not real student credit totals. The direct check does not establish overall academic eligibility, timetable availability, credit-category compliance or official registration approval.

### How to demonstrate in the UI

1. In the Student profile sidebar, select **SYN-001 — prerequisites met**.
2. Ask: **“Can I take COMP302? Check prerequisites and calculate my completed credits.”**
3. Repeat with SYN-002 and SYN-003. Compare the failed and unknown prerequisite outcomes.
4. Point to the displayed model label and open **Processing steps** to show the stages used. The answer label says this is a deterministic specialist-agent workflow using a synthetic demonstration.
5. Clear the synthetic profile selection before any ordinary student-facing question.

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
