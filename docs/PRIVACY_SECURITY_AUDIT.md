# Privacy and Security Review — VU Academic Advisor A2

**Review date:** 5 November 2026  
**Review type:** Static code review, deterministic prompt-injection tests, synthetic workflow tests and deployment-setting review. This is not a formal penetration test, independent security certification or guarantee against all attacks.

## System and data-flow boundary

- The web UI is hosted by Vercel and calls the same-origin Next.js /api/chat and /api/transcribe routes.
- Answer generation, image understanding and speech transcription requests are sent from the server to Groq. The browser does not receive the GROQ_API_KEY.
- Optional programme, semester, credits and CGPA are supplied by the student in the browser. The prototype is not connected to VU's Digiicampus or student-information database.
- Questions, uploaded content and optional profile fields may be transmitted to Groq for the requested inference. The prototype does not write chat history or uploaded content to a VU student database or its own permanent chat database.
- The browser-side Clear Chat action clears the current conversation from the page state; it cannot recall a request already sent to the provider.
- A user can explicitly export one answer's question, text, model identifier, processing steps and displayed citations to a local JSON file. Export is user-triggered and is not an automatic server archive.

## Controls implemented in the repository

- **Server-side secret:** GROQ_API_KEY is read by server routes and is not exposed through a NEXT_PUBLIC_* variable.
- **Same-origin request check:** the chat and transcription routes reject a mismatched browser Origin host. Requests with no Origin header are still accepted for non-browser clients; this check is a CSRF reduction, not user authentication.
- **Request limits:** the API checks declared request size before parsing and enforces the existing four-file / 4 MB combined upload limit after parsing. These limits do not replace infrastructure-level body limits.
- **No local persistence:** the browser keeps the chat in transient page state; no server-side transcript database is implemented.
- **Data minimisation notice:** the UI tells users that questions, optional profile details and uploads are sent to Groq and says not to enter passwords, student IDs or sensitive personal records.
- **Synthetic student data:** three invented B.Tech 2025 fixtures are explicitly labelled synthetic and used only in the demo workflow. They are not linked to a real student or university account.
- **Prompt-injection boundary:** retrieved webpages, university documents, images and attachments are treated as untrusted data. The server escapes source material before placing it in marked context blocks, and system instructions reject embedded instructions to reveal prompts, keys or private data.
- **Deterministic tests:** tests/test_prompt_injection.py checks delimiter escaping and representative attack strings. tests/test_synthetic_advising.py checks the sample student data against actual 2025 B.Tech course rows and verifies origin/body-size safeguards.
- **Dependency review:** the previous resolved frontend npm audit run reported zero known advisories at that scan time. This is not a continuous security guarantee.
- **Deployment protection:** Vercel SSO / deployment protection is preserved. It protects access to the deployment URL for authorised viewers but does not implement in-app student identity or per-student permissions.

## Synthetic data test scenarios

The new synthetic demo lets an evaluator select three fictional records and ask whether the selected student can take COMP302 (Internet of Things) while requesting the completed-course credit total. The course row and direct prerequisites are retrieved from the B.Tech 2025 semester-spread dataset.

| Synthetic fixture | Test outcome | Calculated credits |
|---|---|---:|
| SYN-001 | Direct prerequisites recorded as completed | 29 |
| SYN-002 | COMP206 recorded as failed | 25 |
| SYN-003 | Completion of COMP206 and COMP208 is not established | 21 |

The credit totals are computed from the matching 2025 workbook rows for the course codes listed in each artificial profile. The eligibility check covers only the direct prerequisites shown for that course. It does not establish official registration eligibility, timetable availability, progression, or approval by the Registrar.

## Residual risks and controls requiring university/provider action

- **No in-app authentication:** there is no student login, role-based access or verified student identity. Vercel deployment protection is not a replacement for this.
- **No Digiicampus connection:** there is no authorised VU SSO, SAML/OIDC or student-record API integration. Do not request a student's Digiicampus password in chat. Real integration needs VU/vendor approval, consent, scoped access, token security and a data-processing agreement.
- **No distributed rate limit / abuse control:** the application routes do not implement per-user quotas, distributed rate limiting, bot detection or abuse monitoring.
- **No live penetration test:** deterministic code tests are not a live red-team exercise against the deployed Groq model or a penetration test of the Vercel deployment.
- **Provider retention and region:** provider-side retention, processing region, deletion guarantees and the exact contract accepted for the configured Groq account must be checked by the account owner. Do not claim zero retention or that data never leaves the app. Groq's published agreement places responsibilities on customers for input permissions and output evaluation; account-specific settings and terms still need confirmation.
- **No cross-user isolation proof:** because there is no student login or user data store, the current prototype has no production multi-tenant student-record isolation design to certify.
- **No legal compliance certification:** the UI privacy notice is a transparency measure, not proof of compliance with the DPDP Act/Rules or any institutional policy. VU's data-protection/legal team must approve the actual purposes, notices, retention and vendor terms.
- **Source drift:** official pages and handbooks may change. A source citation identifies evidence used for an answer; it is not university endorsement of the generated answer.

## Recommended institutional controls before real student data is enabled

1. University-approved SSO and server-side session validation; roles and record-level authorisation.
2. Official vendor API access with minimum scopes; no password collection by the chatbot.
3. Approved privacy notice, purpose limitation, consent/other lawful basis, retention schedule, deletion process and vendor contract.
4. Encryption in transit and at rest for any authorised stored data; protected secrets and audited key rotation.
5. Infrastructure-level request/body limits, distributed rate limits, abuse monitoring, security logging that avoids recording unnecessary student content, and incident response.
6. Independent penetration testing, live prompt-injection red-teaming, cross-user access testing and periodic dependency scans.
7. Human escalation for eligibility, grades, progression, credit transfer, exceptions and other decisions with official academic consequences.

## Conclusion

The repository now includes practical privacy messaging, same-origin request checks, request-size checks, synthetic-only advising fixtures, source-bounded recommendations and deterministic security tests. These improvements reduce specific risks but do not make the prototype production-ready for confidential student records. An institutional security and privacy review remains necessary.
