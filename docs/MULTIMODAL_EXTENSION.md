# Multimodal extension — implementation and viva guide

## What is implemented

The Next.js application supports several input and output modalities. These are existing application capabilities, with the course-pathway infographic added as the Task 6 extension.

| Modality | Implementation / model | Demonstration | Quality and limitations |
|---|---|---|---|
| Text chat | Next.js chat UI; Groq `openai/gpt-oss-120b` for general answer generation | Ask a B.Tech policy or course question and inspect citations | Grounding depends on retrieved passages; a model answer is not an official academic decision |
| PDF and office documents | Server-side `officeparser` extraction for PDF, DOCX, XLSX and PPTX; PDF OCR retry when selectable text is absent | Upload a course-plan PDF and ask for a specific course or prerequisite | Four files / 4 MB combined; encrypted, damaged, complex-layout or low-quality scans may fail or lose layout |
| Text files | Server-side extraction for TXT, Markdown and CSV | Upload a small course list or notes file | Extracted excerpts are capped and selected against the question |
| Images | Groq vision model `qwen/qwen3.8-27b`; image descriptions and visible text are returned as structured analysis | Upload a screenshot of a course table or timetable and ask what it shows | OCR and interpretation can misread small text, handwriting, low resolution or ambiguous diagrams; verify against the cited official source |
| Voice input | Browser `MediaRecorder` captures audio; Groq `whisper-large-v3-turbo` transcribes it to text | Use the microphone button, speak a course question, then review the transcript before sending | Browser microphone permission is required; transcription may mishear names and course codes |
| Audio-file transcription | Server-side Groq `whisper-large-v3-turbo` | Attach a supported audio recording | File size and supported-format limits apply; transcription is not speaker verification |
| Read Aloud | Browser Web Speech `SpeechSynthesisUtterance` | Select **Read aloud** under an assistant response | Depends on browser and installed voices; it is local speech synthesis, not generated audio returned by an AI audio model |
| General visual summaries | Groq answer model returns constrained JSON for bars, steps or cards; UI renders the validated structure | Ask “Create a visual summary” with a sourced policy/process answer | Only uses facts/numbers in the answer and retrieved evidence; if generation fails, the text answer remains |
| Course prerequisite infographic | Deterministic server-side data assembly from the authenticated synthetic profile and exact batch-matched structured course workbook rows; React renders an accessible SVG | Log in to a synthetic B.Tech account and ask “Visualise the prerequisites for COMP302” or “Create an infographic for COMP302 eligibility” | Shows direct prerequisites only; missing profile outcomes remain unknown; it does not infer indirect dependencies, course offering, timetable, credit rules or enrolment approval |

## Course-pathway infographic behaviour

When a course code and a visual/diagram/infographic request are present, the API first uses the existing deterministic specialist workflow. It resolves the course against the student's admission batch, then labels each direct prerequisite as:

- **Passed** — listed in the synthetic profile's completed-course codes.
- **Failed** — listed in the synthetic profile's failed-course codes.
- **Unknown** — neither passed nor failed is established by the profile, or the prerequisite row cannot be verified.
- **Not required** — the batch-specific course row lists no direct prerequisite.

The server returns a small typed data object, not arbitrary SVG or HTML. The browser renders that object as SVG with accessible text. Course codes, titles and prerequisite data come from the repository's structured VU workbook export; the synthetic student's outcomes remain fictional demonstration values. The graphic is therefore reproducible and cannot execute model-supplied markup.

## Recommended viva sequence

1. Log in to one of the synthetic B.Tech student accounts.
2. Ask “Can I take COMP302?” and inspect the answer, citations and specialist workflow.
3. Ask “Create an infographic for COMP302 eligibility” and inspect the course-pathway SVG and its Passed / Failed / Unknown states.
4. Upload a course-plan PDF or a screenshot of a course table and ask the advisor to read a specific item.
5. Use the microphone to dictate a short question; check the transcription before sending.
6. Use **Read aloud** on an answer.

## Boundaries

- The app does not generate or edit images, video or AI-generated audio.
- The SVG pathway is a data-driven diagram rendered by the frontend, not a generated image file.
- Browser Read Aloud is not a voice-cloning or audio-generation feature.
- No modality establishes official VU approval, student identity outside the synthetic login, or correctness beyond its source evidence.
- Do not upload real student records, passwords or confidential university data.
