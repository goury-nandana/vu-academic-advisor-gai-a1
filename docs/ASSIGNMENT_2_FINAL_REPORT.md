# DATA308 Generative AI — Assignment 2 Final Report

**Project:** VU Academic Advisor  
**Repository:** [goury-nandana/vu-academic-advisor-gai-a2](https://github.com/goury-nandana/vu-academic-advisor-gai-a2)  
**Web application:** [VU Academic Advisor](https://vu-academic-advisor-gai-a1.vercel.app/)  
**Report status:** Evidence-based implementation report. This is not a claim of full rubric compliance or institutional approval.

## 1. Project overview

VU Academic Advisor is a Next.js academic question-answering prototype for university programme and course information. It combines keyword-weighted retrieval of official VU website/document passages with exact structured B.Tech workbook course lookup. The Assignment 2 web app adds ten synthetic student accounts, session-bound profile-aware advising, deterministic course eligibility and credit stages, downloadable synthetic marksheets, privacy information, document/image/voice input and visual summaries.

A legacy Streamlit implementation remains in the repository; the current web demo is the Next.js application under `frontend/`.

## 2. Technology and models

- Next.js 15, React 19 and TypeScript.
- Vercel hosting, with GitHub Actions for Python regression tests, TypeScript and Next.js build.
- Groq-hosted text model: `openai/gpt-oss-120b`.
- Groq-hosted image understanding model: `qwen/qwen3.8-27b`.
- Groq-hosted speech transcription: `whisper-large-v3-turbo`.
- Browser Speech Synthesis for Read Aloud.
- `officeparser` for supported office document extraction.
- Keyword-weighted retrieval and exact structured workbook lookup; not dense-vector retrieval.

## 3. Assignment 2 feature summary

### Phase 8 — Multimodal Extension (12 marks)

Implemented capabilities include text chat; PDF/DOCX/XLSX/PPTX/TXT/Markdown/CSV upload extraction; image understanding; microphone audio transcription; audio-file transcription; browser Read Aloud; model-produced structured visual summaries; and a new authenticated, source-grounded course-prerequisite SVG infographic.

The course infographic is assembled deterministically from the signed-in synthetic profile and the exact batch-matched course/prerequisite rows. It labels passed, failed, unknown or not-required direct prerequisites. It is a browser-rendered SVG, not a generated raster image. Read Aloud is browser speech synthesis, not AI-generated audio. Feature wiring and regression checks passed, but this repository evidence is not a comprehensive live multimodal quality evaluation across devices, image types and browsers.

See [Multimodal Extension](MULTIMODAL_EXTENSION.md).

### Phase 9 — Agentic Extension (10 marks)

Implemented a six-stage deterministic specialist workflow: authenticated profile retrieval, batch-specific course retrieval, completed-credit calculation, direct prerequisite check, source verification and limited recommendation. The system checks all ten synthetic account scenarios in regression tests and exposes the stages in the UI. The LLM can explain the verified outcome but does not decide the underlying credit sum or direct prerequisite status.

The workflow is not six independent autonomous LLM agents and does not execute enrolment actions. The RAG-only path retrieves passages/course context and asks the answer model to formulate a response; it does not calculate against a structured student history by default. No measured accuracy or latency improvement is claimed.

See [Agent Pipeline and Model Comparison](AGENT_PIPELINE_AND_MODEL_COMPARISON.md).

### Phase 10 — Privacy & Security Audit (10 marks)

Implemented safeguards include PBKDF2-SHA256 server-side demo credential hashes, signed HttpOnly session cookies (Secure in production, SameSite=Strict), session-derived student identity for profile-specific chat and marksheets, logout, same-origin checks on relevant API requests, request-size limits, no arbitrary profile ID for marksheet downloads, and an in-UI privacy/security notice.

The ten requested privacy scenarios are represented by deterministic source-level regression tests. They are not ten live attacks. There has been no independent penetration test, deployed cross-account attack exercise, remote-model prompt-injection red team, or provider-retention audit. Demo credentials are intentionally public and shared; these accounts are only for fictional classroom data.

See [Privacy and Security Audit](PRIVACY_SECURITY_AUDIT.md).

### Phase 11 — Synthetic Media, Copyright & Legal Analysis (8 marks)

The repository review evaluates three actual saved text-answer outputs: a programme directory, a Calculus course-code lookup and a B.Tech minor-options answer. It considers copyright in source material and output, attribution, ownership uncertainty for computer-generated work under Indian law, licensing, misuse and practical controls. It distinguishes these three text outputs from prospective risk analysis for generated images, speech and video.

The evidence transcript did not preserve per-answer model identifiers, timestamps or canonical citation URLs. The review leaves those fields unspecified rather than reconstructing them. It is an educational risk analysis, not legal advice, proof of licensing or VU clearance.

See [Legal/Copyright Output Review](LEGAL_COPYRIGHT_OUTPUT_REVIEW.md).

### Phase 12 — Deploy, Demonstrate, Document & Present (10 marks)

The repository includes the README, system architecture, multimodal guide, agentic workflow comparison, privacy audit, legal review, synthetic-account data, viva demo guide, and test/release evidence. GitHub Actions passed on the source commit recorded in [Testing and Results](TESTING_AND_RESULTS.md).

The production release must be treated separately from source CI. The Task 6 production deployment was blocked by Vercel's daily Hobby deployment limit; the production alias was still serving an older commit at the last verified check. This report does not claim the latest source is deployed. Recheck Vercel's deployment by commit SHA after the documentation update.

## 4. Synthetic student account design

Ten selectable fictional female B.Tech accounts are pre-provisioned. All use the shared classroom password `1234`, which is intentionally public for demonstration only. Student names, IDs, grades, CGPAs and outcomes are synthetic; course codes, titles, credits, semesters and batch-specific curriculum mappings are drawn from the repository's structured workbook records.

| Username | Fictional student | Scenario |
|---|---|---|
| VU001 | Aarohi Menon | First-semester / high-performing in-progress |
| VU002 | Ananya Rao | Clean progression |
| VU003 | Meera Nair | Backlog |
| VU004 | Kavya Iyer | Incomplete results |
| VU005 | Diya Sharma | High performer |
| VU006 | Isha Kulkarni | Borderline prerequisite |
| VU007 | Nandita Bose | Repeated course |
| VU008 | Rhea Pillai | Pending final-semester course |
| VU009 | Saanvi Krishnan | Graduated |
| VU010 | Tara Desai | Complex progression / multiple backlogs |

Three additional legacy fixture records (SYN-001–SYN-003) are test-only and are not selectable accounts.

## 5. Tests and evidence

At the Task 6 source commit, GitHub Actions run 42123342501 completed successfully: 73 Python tests passed; frontend TypeScript check and Next.js production build passed. The test suite includes account/session and marksheet assertions, ten privacy-scenario source checks, prompt-injection boundary checks, synthetic course/credit/prerequisite checks, and four multimodal extension checks.

The test suite is deterministic and largely source/fixture-level. It should not be described as a full end-to-end, live model, penetration, legal or accessibility test. The exact current commit's CI run and release state are tracked in [Testing and Results](TESTING_AND_RESULTS.md).

## 6. Known limitations and outstanding work

1. **Production deployment:** Vercel's daily Hobby deployment cap previously blocked release of the Task 6 commit. Confirm the current documentation commit is deployed by exact SHA before claiming it is live.
2. **Authentication:** shared demo password, pre-provisioned accounts and no institutional SSO or durable student account database.
3. **Privacy/security:** no independent penetration test, deployed cross-account red team or formal provider-retention audit.
4. **Model benchmark:** `VU_LLM_Benchmark_Framework.xlsx` is absent; no complete scored multi-model comparison or model ranking.
5. **Retrieval:** keyword-weighted retrieval rather than dense-vector embeddings; coverage depends on supplied official documents and workbook exports.
6. **Academic decisions:** direct prerequisite logic is not a full graduation audit, timetable/seat check, registration approval or substitute for an authorised advisor.
7. **Multimodal quality:** OCR, vision and transcription can fail on poor-quality or ambiguous inputs; Read Aloud depends on browser voices.
8. **Legal:** output review is educational; source permissions, provider terms and VU authorisation require independent confirmation.

## 7. Final assessment

The repository contains substantive implementations and passing automated checks across the assignment's five phases. The strongest evidence is the functioning source-code pathways, synthetic account fixtures, deterministic specialist workflow, multimodal wiring, SVG infographic renderer, privacy controls and repeatable CI build.

The main evidence gaps are live production deployment of the latest commit, end-to-end browser and adversarial testing, a scored model benchmark, and institutional/legal approval. Accordingly, this is a developed and tested educational prototype, not a fully validated production student-information service and not a defensible claim of 50/50 marks.
