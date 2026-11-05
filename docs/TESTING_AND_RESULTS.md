# Testing, CI Evidence and Release Status

## Latest verified source commit at the start of Task 7

- Branch: `main`
- Commit: `c714edcb4bcc1838d6f862f2132cf12ad3ffb2f9`
- GitHub Actions: [run 42123342501](https://github.com/goury-nandana/vu-academic-advisor-gai-a2/actions/runs/42123342501)
- Workflow: `.github/workflows/python-checks.yml`
- Run conclusion: **success** (5 November 2026 UTC).

## Automated checks in that run

| Check | Result | Evidence / boundary |
|---|---|---|
| Python syntax compilation | Passed | Workflow step |
| Python unit/regression suite | **73 tests passed** | Log ends with `Ran 73 tests` and `OK` |
| Synthetic account and password-hash regression checks | Passed | PBKDF2 hash verification, ten unique selectable accounts, session/logout and marksheet-route assertions |
| Privacy/security regression suite | Passed | Ten requested scenarios are checked with source-level assertions; not ten live attacks |
| Prompt-injection boundary tests | Passed | Escaping and untrusted-content boundary assertions |
| Synthetic advising tests | Passed | All ten account credit totals, batch matching and direct prerequisite fixtures |
| Multimodal regression tests | 4 passed | Authenticated batch workflow, status mapping, accessible SVG and preservation of existing multimodal wiring |
| Frontend TypeScript | Passed | `npm run typecheck` |
| Next.js production build | Passed | `npm run build` |

The GitHub Actions run validates repository tests and the frontend build. It does not call the deployed model for a full end-to-end conversation, execute browser-based accessibility testing, perform an independent penetration test, or prove a successful Vercel deployment.

## Functional coverage represented in automated tests

- Authenticated account lookup, hashed demo credentials and session/logout binding.
- Profile data kept server-side and derived from the session rather than a client-selected student ID.
- Marksheets are session-bound; the route has no arbitrary student profile selector and rejects unauthenticated access.
- Ten fictional student profiles map to exact batch/semester source rows where records are available.
- Credit totals use matching structured workbook rows for completed-course codes.
- Direct prerequisites distinguish passed, failed and unknown.
- Graduated profile handling is represented.
- Missing information is not inferred in deterministic workflow fixtures.
- Privacy notice and prompt-injection untrusted boundary source checks.
- Document/image/voice/Read Aloud feature wiring and SVG pathway rendering.

## What has not been independently verified

- A live browser login/logout and cross-account attack against the deployed production endpoints.
- A live unauthorized marksheet download attempt against Vercel.
- A full prompt-injection red-team exercise against the remote Groq model.
- Provider-side data retention, region, deletion and contract settings.
- Actual image/OCR/voice quality across diverse user uploads and browsers.
- A completed scored multi-model benchmark; the expected benchmark workbook is absent.
- Independent legal review or institutional approval.
- A successful production deployment of the latest source commit.

## Vercel release status

A Vercel production deployment is verified:

- Deployment: `dpl_DR61rbmBqambRvN665GxgtLYqRVv`
- State: **READY**
- Deployment commit: `36605c53ba5557cc3c7e7822f184b7466933f21a`
- Production aliases assigned: `vu-academic-advisor-gai-a1.vercel.app`, `vu-academic-advisor-gai-a1-goury2.vercel.app`, and the main-branch alias.
- The deployed commit is a documentation-only commit after the Task 6 implementation commit; the application source code is unchanged from the tested Task 6 implementation.

A direct attempt to deploy the newest Task 7 documentation commit `328b5203a59dbf2347199b07503267312a189737` was rejected by Vercel with HTTP 402, code `api-deployments-free-per-day`, because the team exceeded 100 deployments in the daily window. Vercel reported a retry period of 24 hours. Since Task 7 changes are documentation-only, the runtime application is already deployed; the latest documentation commit itself is not the deployment's source SHA.

A successful GitHub Actions run does not by itself prove deployment. The READY deployment state and production aliases above were checked separately. A direct protected-page fetch may require an active Vercel share link / authentication; deployment metadata verifies the alias assignment but is not a browser-based user acceptance test.
