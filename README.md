# VU Academic Advisor — DATA308 Generative AI Assignment 2

A multimodal academic-advising prototype for Vidyashilp University. The production-facing app is a Next.js web chat hosted on Vercel. A legacy Streamlit implementation is also retained in the repository for the original academic-data workflow.

**Production web chat:** https://vu-academic-advisor-gai-a1.vercel.app/  
**Repository:** https://github.com/goury-nandana/vu-academic-advisor-gai-a2

## Production web architecture

- **Frontend:** Next.js 15, React 19 and TypeScript.
- **Hosting:** Vercel; project root is frontend/.
- **Backend:** same-origin Next.js API routes at POST /api/chat and POST /api/transcribe.
- **LLM provider:** Groq API. The GROQ_API_KEY is read server-side and must never be exposed via NEXT_PUBLIC_*.
- **Answer model:** openai/gpt-oss-120b.
- **Image model:** qwen/qwen3.8-27b.
- **Audio transcription:** whisper-large-v3-turbo.
- **Read Aloud:** browser Speech Synthesis API.
- **Retrieval:** keyword-weighted official-website/document retrieval plus exact structured B.Tech course-record lookup. The web route is not a dense-vector embedding database.

Configure Vercel with Framework = Next.js, Root Directory = frontend, Install Command = npm ci, Build Command = npm run build. Add GROQ_API_KEY as a server-side Production and Preview environment variable.

## Academic knowledge and retrieval

The web route imports two data exports:

- frontend/data/vu-academic-knowledge.json — Student Handbook, Student SOP, course-plan and minor-workbook passages, plus 205 structured B.Tech semester-spread course records.
- frontend/data/vu-website-knowledge.json — chunked official VU webpage content used for programme, admissions, faculty and campus questions.

Structured course records retain course code, title, L-T-P, credits, prerequisite, semester, admission batch, track where present, source workbook and cell coordinates. Detailed B.Tech semester-spread coverage is for admission batches 2022–2026. The 2022–2025 files do not identify a named track in their source metadata; the application does not infer one. Some non-B.Tech programme curriculum and minor offerings are not available in the supplied structured records, so the advisor must say when it cannot verify them.

Minor-course data is batch-specific. A minor listed in a workbook is not a promise that the course will run in a particular semester. When the answer states the Handbook's minimum-registration threshold, the web route now includes a separate Handbook citation.

## Multimodal features

The web chat supports:

- Text questions and conversational follow-ups.
- PDF, DOCX, XLSX, PPTX, TXT, Markdown and CSV document uploads.
- Image upload and image understanding.
- Audio recording and voice-note transcription.
- Read Aloud using browser Speech Synthesis.
- Structured charts, steps and visual summary cards derived from retrieved answer evidence.

The web API limit is four files and 4 MB combined. Extraction is in memory. Scanned or encrypted files may not yield readable text; the app should disclose this rather than guess.

## Synthetic B.Tech student accounts (Assignment 2 demo)

The app now requires a pre-provisioned synthetic student login. Account data and PBKDF2-SHA256 password hashes are server-side; the browser receives an HttpOnly, SameSite=Strict session cookie. Student identity and academic context used by /api/chat are derived from that signed session, not from a profile ID submitted by the browser.

Demo credentials (fictional accounts only):

| Username | Password | Demonstration case |
|---|---|---|
| demo-sem1 | DemoPass!001 | Semester 1, high-performing starting profile |
| demo-sem2 | DemoPass!002 | Semester 2, clean progression |
| demo-sem3 | DemoPass!003 | Semester 3, backlog |
| demo-sem4 | DemoPass!004 | Semester 4, missing result data |
| demo-sem5 | DemoPass!005 | Semester 5, strong progression |
| demo-sem6 | DemoPass!006 | Semester 6, failed prerequisite |
| demo-sem7 | DemoPass!007 | Semester 7, repeated course |
| demo-sem8 | DemoPass!008 | Semester 8, pending final-semester data |
| demo-grad | DemoPass!009 | Graduated student |
| demo-complex | DemoPass!010 | Mixed backlog and unknown result |

These are public classroom-demo credentials and must not be reused for real accounts. Self-service signup is not enabled: this deployment has no persistent account database. All ten fictional female student profiles are in frontend/data/synthetic-students.json. Academic course codes, titles, semesters, credits and batch are selected from the existing structured B.Tech dataset; grades, CGPAs and result statuses are synthetic.

After login, try “What is my name?”, “What courses did I have in Semester 1?”, “Which courses did I fail?”, or “Can I take COMP302?”. A graduated profile should be treated as completed rather than as a current registration candidate.

The deterministic workflow in frontend/academic-agents.ts runs six specialist stages: synthetic student profile, course retrieval, credit calculation, direct prerequisite check, source verification and limited recommendation. This is a controlled specialist-stage workflow, not six independent autonomous LLM agents. It does not connect to real student records, register a course, approve eligibility or replace a Faculty Advisor/Registrar.

## Privacy and security

- The prototype is not connected to Digiicampus or VU student records.
- Student profile fields are optional and are provided by the person using the chat.
- Questions, profile details and uploaded files are sent to Groq for the requested inference. Do not enter passwords, student IDs or sensitive personal records.
- The prototype does not save chat history in a VU student database or its own permanent server-side chat database. Clear Chat clears the current browser conversation only; it cannot undo data already processed by the provider.
- Users can explicitly export an answer's question, answer, model identifier, processing steps and displayed citations as a local JSON evidence file. Redact personal details before sharing it.
- Chat and transcription routes reject mismatched browser Origin hosts and check declared request sizes. These are useful safeguards, not user authentication or distributed abuse protection.
- Retrieved documents and webpages are treated as untrusted evidence, not instructions.
- Vercel SSO deployment protection is preserved. It is not a substitute for institutional student authentication.

The privacy/security review is in docs/PRIVACY_SECURITY_AUDIT.md. It is a source-code review plus deterministic checks, not a live penetration test or legal compliance certification. Provider retention/region/contract terms, per-student authentication, rate limiting, abuse controls and independent testing require further institutional action.

## Copyright / legal review evidence

docs/LEGAL_COPYRIGHT_OUTPUT_REVIEW.md evaluates three actual saved advisor outputs captured on 4 November 2026: an undergraduate programme list, a Calculus course-code lookup and a B.Tech 2022 minor-options answer. The saved transcript did not preserve original model identifiers or timestamps per response. The review records that evidence gap and identifies a missing Handbook citation in the older minor response; the current route has been corrected to cite that policy separately.

The document is an educational risk review, not legal advice or blanket permission to reproduce university material. VU approval is required before commercial use of university content, student data or third-party materials.

## Model benchmark status

benchmark_runner.py supports a three-model comparison:
- openai/gpt-oss-20b
- openai/gpt-oss-120b
- qwen/qwen3.8-27b

It expects VU_LLM_Benchmark_Framework.xlsx, which is not in the repository. No complete scored model comparison or model ranking is claimed. The benchmark also requires a configured GROQ_API_KEY and must be run where that secret is authorised. The model displayed in an individual chat turn is the model used for that turn, not a model-comparison result.

## Local development and tests

Python checks from the repository root:

    python -m py_compile app.py course_data.py advisor_guardrails.py upload_support.py benchmark_runner.py
    python -m unittest discover -s tests -v

Next.js checks from frontend/:

    npm ci
    npm run typecheck
    npm run build
    npm run dev

GitHub Actions runs Python and frontend checks on pushes and pull requests to main.

## Remaining production requirements

Before real students' confidential records are enabled, VU must approve the purpose, privacy notice, provider agreement, identity integration and data-retention rules. A production integration would require authorised VU/vendor SSO or APIs, minimum data scopes, server-side authorisation, deletion and retention controls, distributed rate limits, security logging, incident response, cross-user isolation tests and independent penetration testing.

The current system is a working educational prototype, not a production-authorised student-record system.
