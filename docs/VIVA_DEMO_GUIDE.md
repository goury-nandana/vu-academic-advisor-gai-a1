# DATA308 Assignment 2 — Viva Demonstration Guide

## Before the demonstration

1. Open the [VU Academic Advisor web application](https://vu-academic-advisor-gai-a1.vercel.app/).
2. If Vercel Deployment Protection appears, use the authorised evaluator access flow configured for the project. Do not share or paste Vercel bypass secrets into chat or screenshots.
3. Use the Student Account login. These are fictional classroom accounts, not Digiicampus accounts.
4. The ten selectable demo accounts use usernames `VU001`–`VU010`. The shared classroom demo password is `1234`. It is deliberately public and weak; it must never be reused for any real account.

## Synthetic account scenarios

| Username | Fictional student | Batch | Semester / status | Demonstration purpose |
|---|---|---:|---|---|
| VU001 | Aarohi Menon | 2026 | Semester 1 | High-performing/in-progress first-semester profile; current CGPA not yet supplied |
| VU002 | Ananya Rao | 2026 | Semester 2 | Clean progression |
| VU003 | Meera Nair | 2025 | Semester 3 | Backlog in DATA103 |
| VU004 | Kavya Iyer | 2025 | Semester 4 | Incomplete academic results; missing values must remain unknown |
| VU005 | Diya Sharma | 2024 | Semester 5 | High-performing profile |
| VU006 | Isha Kulkarni | 2024 | Semester 6 | Failed prerequisite / borderline eligibility |
| VU007 | Nandita Bose | 2023 | Semester 7 | Repeated-course scenario |
| VU008 | Rhea Pillai | 2023 | Semester 8 | Pending final-semester courses and backlog |
| VU009 | Saanvi Krishnan | 2022 | Graduated | Completed academic record; should not be advised to register for a current semester |
| VU010 | Tara Desai | 2025 | Semester 6 | Multiple backlogs / complex progression |

All names, synthetic IDs, grades, CGPAs and outcomes are fictional. Course codes, titles, credits, semester and batch mappings are taken from the repository's structured VU B.Tech workbook export. The app has ten selectable synthetic accounts; the three legacy SYN-001–SYN-003 entries are test-only fixtures, not login accounts.

## Suggested 8–10 minute viva flow

### 1. Login and profile isolation

- Sign in as VU003.
- Ask **“What is my name, batch and current semester?”**
- Ask **“Which courses did I fail?”**
- Log out and sign in as VU004.
- Ask **“What is my CGPA and how many credits have I completed?”**
- Observe that missing values are reported as unavailable rather than inferred.

### 2. Account-aware academic advising

- Sign in as VU006 or VU010.
- Ask **“Can I take COMP302? Check my prerequisites and explain what is missing.”**
- Expand **Agent workflow — 6 specialist stages**.
- Explain that profile retrieval, batch-matched course lookup, credit calculation, prerequisite checking, source verification and limited recommendation are deterministic application stages. They are not six autonomous LLM agents.

### 3. Multimodal demonstration

- Ask a normal text question about a B.Tech course or policy and inspect the citations.
- Upload a course-plan PDF or an image/screenshot of a course table; ask the advisor to extract a specific code or prerequisite.
- Use the microphone to dictate a short question; review the transcription.
- Use **Read aloud** on the assistant response.
- Ask **“Create an infographic for COMP302 eligibility”** while signed in. Inspect the SVG pathway's Passed / Failed / Unknown states. The diagram uses the logged-in profile and batch-matched source row.

### 4. Marksheet and privacy

- Use **Download Synthetic Marksheet PDF** from the authenticated account.
- Confirm the PDF says **SYNTHETIC DEMONSTRATION RECORD — NOT AN OFFICIAL MARKSHEET**.
- Open **Privacy & Security** and explain the data sent to the model provider, prohibited information, synthetic-only boundary and limitations.
- Log out; explain that the marksheet route and profile-aware chat require the authenticated session.

## Questions to prepare for

**Is this connected to Digiicampus?** No. It is an independent synthetic classroom login. No real university student record is queried.

**Are the grades real?** No. The student outcomes, grades and CGPAs are fictional. Curriculum metadata is sourced from the repository's VU workbook exports.

**Are the six specialist stages six autonomous agents?** No. They are deterministic specialist modules orchestrated in application code. The LLM explains the verified result; it does not decide the credit sum or prerequisite status.

**Is the RAG system a vector database?** No. The current web implementation uses keyword-weighted retrieval and exact structured B.Tech course-row lookup.

**Does the SVG infographic mean the app generates images?** No. It assembles a typed data object from verified profile/course facts and renders it as SVG. It is not a raster image-generation model.

**Is voice output AI-generated?** No. Voice input uses Whisper transcription; Read Aloud uses browser Speech Synthesis.

**Is the application production-ready for real student records?** No. It lacks institutional SSO, an approved data-processing arrangement, persistent institutional account storage, independent penetration testing and a full deployed security assessment.

**Was the three-model benchmark completed?** No. The benchmark harness exists, but the expected `VU_LLM_Benchmark_Framework.xlsx` is not present. No measured ranking or accuracy improvement is claimed.

## Presentation integrity

- Do not show real student data, real credentials or personal documents.
- Do not describe a synthetic recommendation as official course registration approval.
- Do not claim a live production release for a commit until Vercel shows that exact commit as READY and assigned to the production alias.
- If the production alias is still serving an older deployment, present the latest verified GitHub commit/CI separately and disclose the deployment block.
