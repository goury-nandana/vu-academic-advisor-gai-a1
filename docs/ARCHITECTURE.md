# System Architecture — VU Academic Advisor A2

## System boundary

The repository contains two implementations:
- **Current web application:** Next.js 15 / React 19 / TypeScript in `frontend/`; this is the intended Assignment 2 demonstration.
- **Legacy implementation:** Streamlit/Python files at the repository root, retained for the earlier academic-data workflow. The public web application uses the Next.js routes, not the Streamlit process.

The web application is a synthetic-data academic-advising prototype. It is not connected to Digiicampus, an institutional SIS, or a real student database.

## Component map

| Layer | Location | Responsibility |
|---|---|---|
| Browser UI | `frontend/app/page.tsx`, `frontend/app/globals.css` | Student account UI, chat, uploads, microphone, Read Aloud, marksheet link, privacy panel, citations and visualisations |
| Account API | `frontend/app/api/auth/*` | Login, logout, session inspection and public demo profile information |
| Session/auth utilities | `frontend/lib/demo-auth.ts` | Server-side PBKDF2 credential verification, signed session token and authenticated profile lookup |
| Synthetic records | `frontend/data/synthetic-students.json` | Ten selectable fictional accounts plus isolated test-only fixtures |
| Credential hashes | `frontend/data/synthetic-account-credentials.json` | Server-side PBKDF2-SHA256 salts and hashes; not a client-side credential source |
| Chat orchestration | `frontend/app/api/chat/route.ts` | Session binding, file extraction, retrieval, model calls, source citations and deterministic specialist workflow integration |
| Academic retrieval | `frontend/data/vu-academic-knowledge.json`, `frontend/data/vu-website-knowledge.json` | Official university website/document excerpts and structured B.Tech workbook records |
| Specialist workflow | `frontend/academic-agents.ts` | Profile retrieval, course lookup, credit calculation, direct prerequisite check, source verification and limited recommendation |
| Marksheets | `frontend/app/api/marksheet/route.ts`, `frontend/lib/synthetic-marksheet-pdf.ts` | Session-bound PDF generation; no arbitrary student-ID parameter |
| Transcription | `frontend/app/api/transcribe/route.ts` | Server-side speech-to-text request |
| Tests | `tests/`, frontend typecheck/build | Deterministic regression checks and frontend compilation/build |
| Hosting | Vercel | Hosts the Next.js app; the repository's GitHub Actions workflow checks code but does not itself prove production deployment |

## Request and trust boundaries

### Login and profile data

1. The browser submits username and password to `POST /api/auth/login`.
2. The server verifies the supplied password against server-side PBKDF2-SHA256 credential hashes.
3. The server issues a signed session cookie with HttpOnly, SameSite=Strict and Secure in production.
4. Subsequent profile-specific chat and marksheet operations derive identity from the authenticated session. A profile ID in a prompt is not accepted as identity.
5. Logout clears the session cookie and client account/chat state.

This is a classroom demo login, not institutional identity verification. The public shared password and pre-provisioned account set are not suitable for real student information.

### Chat / RAG

1. The UI sends the question and any selected uploads to the same-origin chat route.
2. The route validates request shape, origin and upload limits.
3. Supported documents are extracted server-side; images and audio are processed by the configured model/tool paths.
4. Official VU website/document passages are retrieved using keyword-weighted retrieval. Exact B.Tech course questions can also use structured workbook rows.
5. Retrieved material and uploaded content are delimited as untrusted evidence, not executable instructions.
6. The answer model generates a grounded explanation with citations where available. A model response is not an official academic decision.

This is not a vector database / dense embedding retrieval architecture.

### Deterministic specialist workflow

For a signed-in synthetic account and an academic eligibility/credit query, the application uses deterministic code to retrieve the account, match the batch-specific course row, calculate credits from matched completed course rows, check direct prerequisites against passed/failed/unknown status, verify source rows and produce a limited recommendation. The LLM may phrase the result but does not determine the underlying credit sum or prerequisite status. See [Agent Pipeline and Model Comparison](AGENT_PIPELINE_AND_MODEL_COMPARISON.md).

### Multimodal path

- Text is processed through the chat route.
- PDF/DOCX/XLSX/PPTX/TXT/Markdown/CSV are extracted server-side with documented size/count limits.
- Images are sent to the configured vision model.
- Browser microphone recording is transcribed through the transcription API.
- Read Aloud uses browser Speech Synthesis; it is not AI audio generation.
- The course pathway visual is a typed server data structure rendered as SVG in the browser. Model-supplied markup is not executed.

See [Multimodal Extension](MULTIMODAL_EXTENSION.md).

### Marksheets

The marksheet endpoint obtains the student from the session and generates a PDF from that profile only. The document is visibly marked synthetic and not official. The route returns 401 without an authenticated session. Regression tests inspect this boundary; a deployed penetration test has not been performed.

## Models and external processing

| Task | Model/tool |
|---|---|
| General text answer | Groq-hosted `openai/gpt-oss-120b` |
| Image understanding | Groq-hosted `qwen/qwen3.8-27b` |
| Speech transcription | Groq-hosted `whisper-large-v3-turbo` |
| Read Aloud | Browser Web Speech API |
| Visual summary | Structured JSON from answer model, validated and rendered by UI |
| Course prerequisite pathway | Deterministic application logic + browser SVG renderer |

Questions, relevant synthetic profile/course context, selected document excerpts, images and audio transcription requests may be processed by Groq. Review the provider terms and account settings before any use beyond synthetic classroom data.

## Deployment configuration

- Vercel project root: `frontend/`.
- Framework: Next.js.
- Install: `npm ci`.
- Build: `npm run build`.
- Server-side secrets: `GROQ_API_KEY` and `SESSION_SECRET`; never expose them as `NEXT_PUBLIC_*`.
- GitHub Actions workflow: `.github/workflows/python-checks.yml`.

A successful GitHub Actions build does not establish that a Vercel production deployment has completed. The current release status is recorded in [Testing and Results](TESTING_AND_RESULTS.md) and the [Final Assignment 2 Report](ASSIGNMENT_2_FINAL_REPORT.md).
