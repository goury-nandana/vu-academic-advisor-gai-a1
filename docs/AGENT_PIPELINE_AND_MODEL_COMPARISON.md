# Advisor Pipeline and Model Comparison — A2

## Live web-answer pipeline

The Next.js frontend submits chat turns to the same-origin POST /api/chat route. The route performs these steps:

1. Validate the question, optional student profile and attachment size/type.
2. Process supported text, image and audio attachments; report unsupported file formats instead of silently claiming to read them.
3. Select and fetch a small set of allowlisted official Vidyashilp University webpages.
4. Rank fetched excerpts against the question and assign citation numbers only to pages actually fetched for that turn.
5. Escape and separate retrieved webpages and student-supplied content as untrusted data.
6. Generate an answer with the configured Groq model and explicit source-grounding, privacy and prompt-injection instructions.
7. When a visual is requested, optionally generate a structured infographic/steps/bar summary from facts already present in the answer and retrieved excerpts. The UI renders it as a visual card; it is not a general-purpose image-generation model.
8. Return the answer, clickable citations, pipeline steps, model identifier, optional visual, follow-ups and file-processing notes to the chat.

This is a sequential retrieval-and-generation pipeline. It is not a swarm of autonomous agents and does not claim independent autonomous decision-making.

## Speech and visual output

The browser chat keeps text-to-speech playback through the browser Speech Synthesis API. Voice-note uploads are transcribed through the configured Whisper endpoint. When asked for an infographic, chart, diagram or flow, the route can request a structured visual summary from the model and the client renders it as an accessible visual card. Image uploads can be interpreted by the separate vision model. This is not a raster image generator: assistant-created visuals are evidence-bounded UI infographics, not downloadable artwork.


## Model comparison: measured facts only

The live web route uses openai/gpt-oss-120b for answer generation and structured visual summaries, qwen/qwen3.8-27b for image understanding, and whisper-large-v3-turbo for voice-note transcription. The Streamlit app uses openai/gpt-oss-120b with openai/gpt-oss-20b as its fallback. The live answer UI names the answer-generation model and states that no multi-model comparison was performed for that turn. The benchmark candidate list has been refreshed to the three current documented Groq models: openai/gpt-oss-20b, openai/gpt-oss-120b and qwen/qwen3.8-27b.

The separate benchmark_runner.py script is designed to compare those three candidate Groq models against a common set of questions and source context, record latency/token usage, and leave rubric scores blank for independent human assessment. It requires VU_LLM_Benchmark_Framework.xlsx, which is not present in this repository. No benchmark run, score sheet or defensible model ranking is available. Therefore, this submission makes no claim that one model outperforms another.

## Human evaluation rubric (0–4 each)

- Factual accuracy against the source-backed gold facts.
- Grounding and correct use of actual citations.
- Absence of unsupported or hallucinated claims.
- Appropriate clarification when programme, semester or batch information is missing.

A comparison is reportable only after the missing input workbook is supplied, all available models are run against the same questions/context, unavailable models are recorded as unavailable, and responses are independently scored.
