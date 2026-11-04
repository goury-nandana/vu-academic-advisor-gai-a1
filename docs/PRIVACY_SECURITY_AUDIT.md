# Privacy and Security Review — VU Academic Advisor A2

**Review type:** Static source-code review plus deterministic prompt-injection boundary tests. This is not a formal penetration test, independent security certification, or proof of resistance to every prompt injection.

**Reviewed:** 4 November 2026  
**Scope:** Next.js chat client and /api/chat route, Streamlit app.py, advisor_guardrails.py, upload_support.py, GitHub Actions workflow, and accessible Vercel project settings.

## Findings and implemented controls

- **Optional profile:** Programme, semester, credits and CGPA are optional. Blank values are represented as unknown, not inferred. The assistant asks one clarification for programme-specific questions when the programme is not supplied.
- **Server-side secret:** The Vercel project has a sensitive GROQ_API_KEY environment-variable entry for Production and Preview. Its value was not decrypted or printed. The Next.js route reads the key only on the server; no NEXT_PUBLIC key is used.
- **Same-origin API:** The web client calls POST /api/chat on its own origin by default. No cross-origin API allowance is required for this route. An external API URL remains an optional override.
- **Request/file limits:** The web API permits at most four attachments and 4 MB combined, caps extracted text, and does not write chat/file content to an application database. Submitted material is still transmitted to Groq for transcription, image description or answer generation.
- **Supported formats:** The web route processes TXT, Markdown, CSV, images and audio. PDF, DOCX, XLSX and PPTX extraction remains in the separate Streamlit implementation; the web route reports those formats as unsupported rather than pretending to process them.
- **Prompt-injection boundary:** The Streamlit path identifies retrieved webpages, university documents and attachments as untrusted data and escapes delimiter characters before wrapping them. The web API serializes and escapes fetched sources and student-file content before adding them to a marked untrusted context block. The model instructions explicitly reject embedded commands that try to override the academic role or extract secrets.
- **Privacy boundary:** Both model prompts state that the application has no access to private VU student records and must not disclose system prompts, credentials, hidden application data or another student's information.
- **Dependency audit:** CI ran `npm audit --json` after pinning Next.js 15.5.29, PostCSS 8.5.32 and minimatch 11.0.1. The resulting audit reported 0 info, 0 low, 0 moderate, 0 high and 0 critical advisories for the resolved frontend lockfile. That is a point-in-time package audit, not a guarantee against newly disclosed issues.
- **Domain protection:** The existing Vercel SSO deployment-protection configuration was preserved while correcting the build framework/root. No protection bypass or secret value was changed.

## Deterministic prompt-injection tests added

tests/test_prompt_injection.py includes six representative adversarial prompts and a forged closing-delimiter attack. It tests escaped content boundaries, malicious-label sanitization, and whether the Streamlit model prompt uses the wrapper. These are deterministic code-boundary tests. They are not six live attacks against Groq and do not demonstrate model-level immunity. The actual test result is established by the GitHub Actions run for the commit, not by this description alone.

## Residual risks and unverified controls

- No independent penetration test or live six-case red-team run against the production Groq model was completed. Model-level prompt-injection resistance remains unverified.
- Provider-side retention, processing region, deletion guarantees and contractual privacy terms were not accessible from repository/Vercel settings and must be checked against Groq's account terms.
- The sensitive GROQ_API_KEY entry was observed, but its value was not decrypted. A real authenticated API smoke test is required to prove that the configured value is valid.
- Vercel SSO protection is enabled for deployment URLs and was intentionally preserved. A grader may need authorized access. Do not remove protection without the project owner's explicit decision.
- Distributed rate limiting, abuse detection and per-user authentication are not implemented in the application route. Vercel deployment protection is not a substitute for production-grade abuse controls.
- Source pages are fetched on demand; availability and content can change. A citation means that page was fetched for that request, not that the university endorsed the generated response.
- Full independent penetration testing, a complete response-header review, cross-user isolation tests, distributed rate limiting and provider-retention verification remain outstanding. Dependency scanning was executed; the resolved frontend dependency audit reported zero known advisories at the scan time.

## Status interpretation

A passing deterministic test suite shows that the tested payloads are escaped and remain in the intended wrapper. It does not establish legal compliance, secure hosting, immunity to prompt injection or the absence of other vulnerabilities. Do not label this review a completed penetration test.
