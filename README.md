# VU Academic Advisor — DATA308 Generative AI Assignment 2

Streamlit-based academic advising chatbot for Vidyashilp University (VU). It uses Groq for answer generation, structured retrieval from the original B.Tech semester-spread workbooks, and a separate official-website knowledge source.

**Live app:** https://vu-academic-advisor-gai-a1-hzdbiixzivwbjb3dvbfvka.streamlit.app/

## Current scope

- Detailed B.Tech curriculum lookups for admission batches 2022–2026, using the batch-specific semester-spread workbook.
- Course code, title, prerequisite, L-T-P, credits, semester, basket, workbook name and cell coordinates are retained from source data.
- Course and batch context is carried across relevant follow-up questions.
- Explicit multi-batch questions return the requested supported batches; unsupported cohorts are not fabricated.
- Student Handbook and SOP material are kept as academic-document sources.
- Official VU website retrieval is kept separate from academic-document retrieval.
- Other VU programmes can be asked about, but detailed curriculum answers are limited to what the loaded official sources actually support.

The 2026 semester-spread source is identified as the B.Tech Data Science track. The 2022–2025 semester-spread files do not explicitly identify a track in the source metadata, so the application does not infer one.

## Assignment 2 reliability safeguards

- Personal-profile questions are answered from explicitly supplied sidebar/chat details only; the chatbot does not claim access to university student records.
- Unsupported personal or academic profile claims are retracted when challenged.
- Short acknowledgements such as "oh" and "ok" do not replace the active conversation topic.
- French greetings (including "bonjour") are handled as social openers without document retrieval.
- Numeric policy thresholds, including grading cut-offs, require explicit source evidence.

## Ten-model benchmark

`benchmark_runner.py` runs the same benchmark questions, source context, and grounding prompt against ten Groq model candidates available to the configured account. It uses the configured `GROQ_API_KEY` only; it does not require paid API access. Unavailable models are not silently replaced. The script records responses, latency and token usage; the four rubric scores are intentionally left blank for consistent human evaluation.

Place `VU_LLM_Benchmark_Framework.xlsx` in the repository root, then run:

```bash
python benchmark_runner.py --limit 3
python benchmark_runner.py
```

The first command is a small smoke run; the second runs the full question set. The workbook is an evaluation input and is not currently committed to this repository. A benchmark run has not yet been performed from the deployment environment. Groq model availability and free-tier rate limits depend on the account at run time.

## Run locally

Python 3.11+ is recommended.

```bash
git clone https://github.com/goury-nandana/vu-academic-advisor-gai-a1.git
cd vu-academic-advisor-gai-a1
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Set the Groq key as an environment variable, or configure it in Streamlit Secrets:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

Optional debug access requires a separate token:

```toml
DEBUG_TOKEN = "a-long-random-secret"
```

Debug output is disabled unless the token is configured and supplied as the `debug` query parameter. Do not share debug URLs.

Start the app:

```bash
streamlit run app.py
```

## Streamlit Community Cloud

1. Connect this GitHub repository to Streamlit Community Cloud.
2. Set the app entry point to `app.py`.
3. Add `GROQ_API_KEY` under App settings → Secrets.
4. Optionally add `DEBUG_TOKEN`; leave it unset in normal use.
5. Deploy from `main`.

Do not commit API keys, `.env` files or `.streamlit/secrets.toml`.

## Data sources and retrieval

| Source | Intended use |
|---|---|
| `VU_Semester_Data_Split.zip` | Batch-specific B.Tech semester spread, course details and L-T-P |
| Embedded Student Handbook | University regulations and academic policies |
| Embedded SOP | Student-facing procedures |
| `Course_Plans.txt` | Academic course-plan context |
| `Minor_Courses_for_BTech_Students.xlsx` (legacy embedded extract) | Minor-course context |
| Official VU website sources | Admissions, programmes, faculty, placements and campus information |

The structured loader reads only the five semester-spread workbooks in the archive. It does not infer missing values or treat programme-structure sheets as semester-spread rows. Each structured row includes source workbook and cell coordinates.

## Tests

Run:

```bash
python -m unittest discover -s tests -v
python -m py_compile app.py course_data.py
```

GitHub Actions runs the syntax check and unittest suite on pushes and pull requests to `main`.

## Known limitations

- Structured semester-spread curriculum coverage is B.Tech batches 2022–2026. Do not assume a different cohort is covered.
- The 2022–2025 workbook metadata does not establish a named track; the application leaves track unspecified.
- Ambiguous elective cells, TBA placeholders, and combined alternative-course cells (for example, slash-separated codes with multiple titles or L-T-P values) are not converted into single course records. They require a separate source-aware treatment; the loader does not guess how to split them.
- Minor-workbook extraction and non-B.Tech programme semester structures are not yet fully normalized into the structured course-record loader.
- Website information depends on the official pages being reachable when the website knowledge base is refreshed.
- Real Groq API behaviour and the deployed Streamlit instance must be smoke-tested with the configured deployment secret; automated tests do not validate external API credentials.
