# ============================================================
# VU AI ACADEMIC ADVISOR — Vidyashilp University
# ============================================================

import streamlit as st
from groq import Groq
from pypdf import PdfReader

import os
import re
import math
import base64
import json
import requests

from collections import Counter


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Academic Advisor — Vidyashilp University",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background-color: #f0f2f5 !important;
}

[data-testid="stSidebar"] { background-color: #ffffff !important; }

[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #ffffff !important;
    border-top: 1px solid #eaecf0 !important;
    padding: 10px 16px !important;
}

[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div {
    background: #ffffff !important;
    border: 1.5px solid #dde0e6 !important;
    border-radius: 26px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}

[data-testid="stChatInputContainer"] textarea {
    color: #1a1a2e !important;
    caret-color: #c0182a !important;
    background: transparent !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder { color: #adb5bd !important; }

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 0 !important;
}

.stChatMessage .stMarkdown p,
.stChatMessage .stMarkdown {
    font-size: 14px !important;
    line-height: 1.6 !important;
}

div[data-testid="stButton"] > button {
    background: #ffffff !important;
    border: 1px solid #eaecf0 !important;
    border-radius: 20px !important;
    color: #0a2240 !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 9px 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    transition: all 0.15s !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #c0182a !important;
    color: #c0182a !important;
    background: #fff0f1 !important;
}

.info-box {
    background-color: white;
    padding: 16px 18px;
    border-radius: 14px;
    border-left: 4px solid #c0182a;
    margin-bottom: 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}

.footer-text {
    text-align: center;
    color: #adb5bd;
    font-size: 11px;
    padding-top: 20px;
}

#MainMenu, footer { visibility: hidden; }

.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin: 6px 0;
}
.bubble-user-inner {
    background: linear-gradient(135deg, #c0182a 0%, #0a2240 100%);
    color: #ffffff;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px;
    max-width: 68%;
    font-size: 14px;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(192,24,42,0.18);
    word-wrap: break-word;
}
.bubble-bot {
    display: flex;
    justify-content: flex-start;
    margin: 6px 0;
}
.bubble-bot-inner {
    background: #ffffff;
    color: #1a1a2e;
    border-radius: 18px 18px 18px 4px;
    padding: 10px 16px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.65;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS
# ============================================================

MODEL = "llama-3.3-70b-versatile"

ACADEMIC_EXTENSIONS = (".pdf", ".txt", ".csv", ".xlsx", ".xls")

EXCLUDED_FILES = ("advisor_eval", "eval_results", "phase4", "summary_metrics", "website_sources")

DEFAULT_WEBSITE_SOURCES = [
    {"name": "VU Official Website", "url": "https://vidyashilp.edu.in/"},
    {"name": "VU Admissions", "url": "https://vidyashilp.edu.in/admissions/"},
    {"name": "VU Contact", "url": "https://vidyashilp.edu.in/contact/"},
    {"name": "VU Data Science", "url": "https://vidyashilp.edu.in/data-science/"},
    {"name": "VU AI and Machine Learning", "url": "https://vidyashilp.edu.in/schools/b_tech_ai_ml/"},
    {"name": "VU B.Tech", "url": "https://vidyashilp.edu.in/btech/"},
    {"name": "VU About", "url": "https://vidyashilp.edu.in/about/"},
    {"name": "VU Law", "url": "https://vidyashilp.edu.in/law/"},
    {"name": "VU PhD", "url": "https://vidyashilp.edu.in/phd/"},
    {"name": "VU Programmes", "url": "https://vidyashilp.edu.in/programmes/"}
]

# Greetings and social messages — handled without any document retrieval
SOCIAL_RE = re.compile(
    r"^\s*(h+i+|h+e+l+o+|hey+|hola|yo+|sup|bro|wsp|wsup|what'?s\s*up|wassup|"
    r"good\s*(morning|afternoon|evening|night)|namaste|namaskaram|"
    r"thank(s|\s*you|u)|thx|ty|ok(ay)?|got\s*it|sure|great|nice|cool|"
    r"bye|goodbye|see\s*you|take\s*care|cya)\s*[!.?]*\s*$",
    re.I
)

GREETING_REPLY = (
    "Hey! 👋 I'm VU's AI Academic Advisor. "
    "I can help with attendance, credits, prerequisites, registration, "
    "course eligibility, progression rules and more. "
    "What would you like to know?"
)

THANKS_REPLY = "Happy to help! 😊 Feel free to ask anything else about your academics at VU."


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "academic_kb" not in st.session_state:
    st.session_state.academic_kb = []
if "website_kb" not in st.session_state:
    st.session_state.website_kb = []
if "knowledge_loaded" not in st.session_state:
    st.session_state.knowledge_loaded = False
if "website_loaded" not in st.session_state:
    st.session_state.website_loaded = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# LOGO & HEADER
# ============================================================

def find_logo():
    for filename in os.listdir("."):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if lower.endswith((".png", ".jpg", ".jpeg")) and "logo" in lower:
            return filename
    for filename in os.listdir("."):
        lower = filename.lower()
        if lower.endswith((".png", ".jpg", ".jpeg")):
            return filename
    return None

logo_path = find_logo()

header_col1, header_col2 = st.columns([1, 7], vertical_alignment="center")

with header_col1:
    if logo_path:
        st.image(logo_path, width=90)
    else:
        st.markdown("🎓")

with header_col2:
    st.markdown("## Vidyashilp University")
    st.markdown("🟢 **AI Academic Advisor · Online**")

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🎓 Student Profile")
    st.markdown("Enter your details to get personalised answers.")
    st.markdown("---")

    program = st.selectbox(
        "Program",
        ["B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"]
    )

    semester = st.selectbox(
        "Current Semester",
        ["Not specified", "1st Semester", "2nd Semester", "3rd Semester",
         "4th Semester", "5th Semester", "6th Semester", "7th Semester",
         "8th Semester", "9th Semester", "10th Semester"]
    )

    completed_credits = st.number_input("Completed Credits", min_value=0, max_value=400, value=45, step=1)
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# API KEY
# ============================================================

def get_api_key():
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
        if secret_key:
            return secret_key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

api_key = get_api_key()


# ============================================================
# STUDENT PROFILE
# ============================================================

student_profile = {
    "program": program,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_pdf_text(filepath):
    pages = []
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            try:
                t = page.extract_text()
                if t:
                    pages.append(t)
            except Exception:
                continue
    except Exception:
        return ""
    return clean_text("\n".join(pages))

def extract_txt_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception:
        return ""

def extract_csv_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception:
        return ""

def extract_excel_text(filepath):
    try:
        from openpyxl import load_workbook
        wb = load_workbook(filepath, read_only=True, data_only=True)
        rows = []
        for sheet in wb.worksheets:
            rows.append(f"Sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                values = [str(v) for v in row if v is not None]
                if values:
                    rows.append(" | ".join(values))
        return clean_text("\n".join(rows))
    except Exception:
        return ""

def extract_file_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_pdf_text(filepath)
    if ext == ".txt":
        return extract_txt_text(filepath)
    if ext == ".csv":
        return extract_csv_text(filepath)
    if ext in [".xlsx", ".xls"]:
        return extract_excel_text(filepath)
    return ""


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(text, chunk_size=150, overlap=30):
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(words):
            break
        start = end - overlap
    return chunks


# ============================================================
# LOAD ACADEMIC DOCUMENTS
# ============================================================

def load_academic_documents():
    documents = []
    for filename in sorted(os.listdir(".")):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if not lower.endswith(ACADEMIC_EXTENSIONS):
            continue
        if any(ex in lower for ex in EXCLUDED_FILES):
            continue
        text = extract_file_text(os.path.join(".", filename))
        if not text:
            continue
        for i, chunk in enumerate(chunk_text(text)):
            documents.append({
                "text": chunk,
                "source": filename,
                "type": "academic",
                "chunk": i + 1
            })
    return documents


# ============================================================
# WEBSITE SOURCES
# ============================================================

def load_website_sources():
    source_file = "website_sources.json"
    if os.path.exists(source_file):
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass
    return DEFAULT_WEBSITE_SOURCES

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_webpage(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()
        return clean_text(soup.get_text(separator=" "))
    except Exception:
        return ""

def load_website_documents():
    documents = []
    for source in load_website_sources():
        name = source.get("name", "VU Website")
        url = source.get("url", "")
        if not url:
            continue
        text = fetch_webpage(url)
        if not text:
            continue
        for i, chunk in enumerate(chunk_text(text, chunk_size=180, overlap=40)):
            documents.append({
                "text": chunk,
                "source": name,
                "url": url,
                "type": "website",
                "chunk": i + 1
            })
    return documents


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

if not st.session_state.knowledge_loaded:
    with st.spinner("Loading academic documents..."):
        st.session_state.academic_kb = load_academic_documents()
        st.session_state.knowledge_loaded = True

if not st.session_state.website_loaded:
    with st.spinner("Loading official VU information..."):
        st.session_state.website_kb = load_website_documents()
        st.session_state.website_loaded = True

academic_kb = st.session_state.academic_kb
website_kb = st.session_state.website_kb


# ============================================================
# TOKENIZER & RETRIEVAL
# ============================================================

STOPWORDS = {
    "the","a","an","is","are","am","i","me","my","to","of","in","on",
    "for","and","or","can","could","would","should","do","does","did",
    "be","it","this","that","with","from","at","as","what","which",
    "how","where","when","why","you","your"
}

def tokenize(text):
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS]

def retrieve(query, documents, top_k=5, minimum_score=0.05):
    if not documents:
        return []
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    query_counter = Counter(query_tokens)
    doc_freq = Counter()
    tokenized_docs = []
    for doc in documents:
        tokens = tokenize(doc["text"])
        for t in set(tokens):
            doc_freq[t] += 1
        tokenized_docs.append(tokens)
    total = len(documents)
    scored = []
    for i, doc in enumerate(documents):
        tokens = tokenized_docs[i]
        if not tokens:
            continue
        tc = Counter(tokens)
        score = sum(
            (tc[t] / len(tokens)) *
            (math.log((total + 1) / (doc_freq.get(t, 0) + 1)) + 1) *
            qc
            for t, qc in query_counter.items() if t in tc
        )
        boost_phrases = [
            "minimum cgpa", "attendance", "eligibility", "eligible",
            "prerequisite", "minor", "semester", "admission", "course",
            "credits", "programme", "program", "transfer", "law", "phd",
            "summer", "summer term"
        ]
        ql = query.lower()
        tl = doc["text"].lower()
        for phrase in boost_phrases:
            if phrase in ql and phrase in tl:
                score += 0.15
        if score >= minimum_score:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, doc in scored[:top_k]:
        r = dict(doc)
        r["_score"] = score
        results.append(r)
    return results


# ============================================================
# CLASSIFY QUERY
# ============================================================

def classify_query(query):
    q = query.lower().strip()
    website_patterns = [
        "admission", "apply", "application", "how do i join", "join vu",
        "contact", "phone number", "email", "address", "campus", "location",
        "where is vu", "where is vidyashilp", "programmes offered",
        "about vu", "vidyashilp university", "law programme", "phd programme"
    ]
    for pattern in website_patterns:
        if pattern in q:
            return "website"
    return "academic"


# ============================================================
# PROFILE TEXT
# ============================================================

def profile_to_text():
    return (
        f"Program: {student_profile['program']}\n"
        f"Semester: {student_profile['semester']}\n"
        f"Completed credits: {student_profile['completed_credits']}\n"
        f"CGPA: {student_profile['cgpa']}"
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt():
    return f"""You are the AI Academic Advisor for Vidyashilp University (VU), Bengaluru, India.

Student profile:
{profile_to_text()}

YOUR ROLE:
Help students with academic questions — courses, credits, prerequisites, attendance,
progression rules, graduation requirements, semester planning, admissions, and programmes.

RESPONSE STYLE:
- Keep responses SHORT and conversational — like texting, not writing a report.
- NO tables, NO numbered section headers with emoji, NO "What to do next" sections.
- Max 4-5 bullet points if needed. If it can be said in 2 sentences, say it in 2 sentences.
- Friendly and warm tone always. Match the student's casual or formal style.
- NEVER guess or assume CGPA thresholds, credit requirements, or rules not explicitly
  in the documents. If the exact number isn't in the retrieved text, say you don't have
  that specific figure and ask them to verify with the academic office.

BEHAVIOUR RULES:
1. If the message is a greeting or casual opener (hi, hey, hello, bro, hiii, wsp, sup,
   in any spelling or style), respond warmly and introduce yourself as VU's AI Academic
   Advisor. Never search documents for this.
2. If asked personal questions about yourself (your family, your name, your feelings),
   explain you are an AI and redirect to academic help in a friendly way.
3. If the question is completely outside academics (weather, sports, movies, cricket,
   politics, restaurant), politely say you can only help with VU academic matters.
4. If a student mentions they are in a Summer Term, acknowledge it and say:
   "For Summer Term-specific course offerings and registration, please contact the
   academic office or registrar directly, as this information may not be in the
   available documents."
5. If a student asks about Law programmes (BA LLB, BBA LLB) — answer from website
   information if available. If documents don't have enough detail, say:
   "For detailed Law programme information, please contact the Law School office
   at Vidyashilp University directly."
6. If a student asks about PhD — answer from website information if available. If not
   enough detail, say: "For PhD admissions and programme details, please visit
   vidyashilp.edu.in or contact the research office directly."
7. Match the student's tone — informal gets a friendly response, formal gets a
   professional one. Never be robotic.
8. If a student seems stressed or mentions failing or backlogs, show empathy first.
9. For fees or financial queries, say: "Please contact the Accounts office directly."
10. For queries about specific professors or HODs, say:
    "Please contact the department office directly."
11. If a question has multiple parts, answer each part separately.
12. NUMERIC RULES: when the excerpts state a numeric threshold (e.g. minimum 75%,
    CGPA >= 4.00) and the student's message states their own number for that same thing,
    compare the two and give a direct yes/no/eligible/not-eligible answer using that
    comparison. Do not ask the student to repeat a number they already gave you.

SOURCE RULES:
- Use academic documents as PRIMARY source for regulations, prerequisites, eligibility,
  credits, attendance, curriculum, progression rules.
- Use VU website as supplementary source for admissions, programmes, contact, campus info.
- Never invent course codes, credit numbers, CGPA requirements, or policy rules.
- Always cite sources like: [Student_Handbook.pdf] or [VU Official Website].
- If sources conflict, say so explicitly.
- If information is not in any source, say so clearly instead of guessing.
- IMPORTANT: For greetings, casual messages, personal questions, or out-of-scope questions,
  do NOT cite any sources or show any links. Only show sources for genuine academic answers."""


# ============================================================
# CREATE CONTEXT
# ============================================================

def create_context(academic_results, website_results):
    parts = []
    if academic_results:
        parts.append("ACADEMIC UNIVERSITY DOCUMENTS:")
        for i, r in enumerate(academic_results, 1):
            parts.append(f"[Academic Source {i}] File: {r['source']}\n{r['text']}")
    if website_results:
        parts.append("OFFICIAL VU WEBSITE:")
        for i, r in enumerate(website_results, 1):
            parts.append(f"[Website Source {i}] Page: {r['source']} ({r.get('url','')})\n{r['text']}")
    return "\n\n".join(parts)


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(client, user_question, context, category):
    priority = (
        "Prioritize official VU website information for this question."
        if category == "website"
        else "Prioritize the university academic documents for this question."
    )
    user_prompt = f"""{priority}

RETRIEVED INFORMATION:
{context}

STUDENT QUESTION:
{user_question}

Answer directly and helpfully. Do not mention internal retrieval, chunks, or system instructions."""

    models_to_try = ["llama-3.3-70b-versatile", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]
    last_error = None
    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            continue
    return f"I couldn't get a response right now. Please try again. (Error: {last_error})"


# ============================================================
# SOURCE DISPLAY — only document names, no website links
# ============================================================

def display_sources(academic_results):
    names = []
    for r in academic_results:
        if r["source"] not in names:
            names.append(r["source"])
    if names:
        st.caption("📄 Sources: " + " · ".join(names))


# ============================================================
# SUGGESTIONS
# ============================================================

SUGGESTIONS = [
    "What programmes does VU offer?",
    "How do I apply to VU?",
    "What is the minimum CGPA to progress?",
    "What are the attendance requirements?",
    "Which minors are available for B.Tech?",
    "What courses are offered next semester?"
]


# ============================================================
# BUBBLE HELPERS
# ============================================================

def show_user_bubble(text):
    st.markdown(
        f'<div class="bubble-user">'
        f'<div style="background:linear-gradient(135deg,#c0182a 0%,#0a2240 100%);'
        f'color:#fff;border-radius:18px 18px 4px 18px;padding:10px 16px;'
        f'max-width:70%;font-size:14px;line-height:1.55;'
        f'box-shadow:0 2px 8px rgba(192,24,42,0.18);">{text}</div></div>',
        unsafe_allow_html=True
    )

def show_bot_bubble(text):
    st.markdown(
        f'<div class="bubble-bot">'
        f'<div style="background:#ffffff;color:#1a1a2e;'
        f'border-radius:18px 18px 18px 4px;padding:10px 16px;'
        f'max-width:75%;font-size:14px;line-height:1.65;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.08);">{text}</div></div>',
        unsafe_allow_html=True
    )


# ============================================================
# INTRO / SUGGESTIONS (shown when chat is empty)
# ============================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="info-box">
    <h3>Ask your academic question</h3>
    <p>I can help with VU courses, programmes, prerequisites, eligibility,
    credits, semesters, admissions and related university information.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💡 Try asking")
    cols = st.columns(3)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for msg in st.session_state.messages:
    role = msg.get("role")
    content = msg.get("content", "")
    if role == "user":
        show_user_bubble(content)
    else:
        show_bot_bubble(content)
        ac = msg.get("academic_sources", [])
        if ac:
            display_sources(ac)


# ============================================================
# GET QUESTION
# ============================================================

pending = st.session_state.pending_question
st.session_state.pending_question = None
user_question = pending or st.chat_input("Ask your academic question...")


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    st.session_state.messages.append({"role": "user", "content": user_question})
    show_user_bubble(user_question)

    # ---- Social / greeting shortcut (no retrieval, no links) ----
    is_thanks = re.search(r"\b(thank(s|\s*you|u)|thx|ty)\b", user_question, re.I)
    if SOCIAL_RE.match(user_question.strip()):
        answer = THANKS_REPLY if is_thanks else GREETING_REPLY
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    # ---- Real question — retrieval + LLM ----
    category = classify_query(user_question)

    if not api_key:
        answer = "The advisor is not configured yet. Please contact the administrator."
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
    else:
        try:
            client = Groq(api_key=api_key)

            if category == "website":
                website_results = retrieve(user_question, website_kb, top_k=6)
                academic_results = retrieve(user_question, academic_kb, top_k=3)
            else:
                academic_results = retrieve(user_question, academic_kb, top_k=6)
                website_results = retrieve(user_question, website_kb, top_k=3)

            context = create_context(academic_results, website_results)

            with st.spinner("Thinking..."):
                answer = generate_answer(client, user_question, context, category)

            show_bot_bubble(answer)

            # Show only document source names for academic questions, no links
            if category == "academic" and academic_results:
                display_sources(academic_results)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "academic_sources": academic_results,
                "website_sources": []
            })

        except Exception as error:
            answer = "I couldn't process that request right now. Please try again."
            show_bot_bubble(answer)
            st.session_state.messages.append({
                "role": "assistant", "content": answer,
                "academic_sources": [], "website_sources": []
            })


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-text">Vidyashilp University · AI Academic Advisor</div>',
    unsafe_allow_html=True
)
