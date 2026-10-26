# ============================================================
# VU AI ACADEMIC ADVISOR — Vidyashilp University
# ============================================================
import streamlit as st
from groq import Groq
from pypdf import PdfReader
import os
import re
import math
import json
import html
import requests
from collections import Counter

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Academic Advisor — Vidyashilp University",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"], [data-testid="block-container"] {
    background-color: #f0f2f5 !important;
}
[data-testid="stSidebar"] { background-color: #ffffff !important; }
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #ffffff !important;
    border-top: 1px solid #eaecf0 !important;
    padding: 10px 16px !important;
}
[data-testid="stChatInputContainer"], [data-testid="stChatInputContainer"] > div {
    background: #ffffff !important;
    border: 1.5px solid #dde0e6 !important;
    border-radius: 26px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: #1a1a2e !important; caret-color: #c0182a !important; background: transparent !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: #adb5bd !important; }
div[data-testid="stButton"] > button {
    background: #ffffff !important; border: 1px solid #eaecf0 !important;
    border-radius: 20px !important; color: #0a2240 !important;
    font-size: 13px !important; font-weight: 400 !important; padding: 9px 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; transition: all 0.15s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #c0182a !important; color: #c0182a !important; background: #fff0f1 !important;
}
.info-box {
    background-color: white; padding: 16px 18px; border-radius: 14px;
    border-left: 4px solid #c0182a; margin-bottom: 18px; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.footer-text { text-align: center; color: #adb5bd; font-size: 11px; padding-top: 20px; }
#MainMenu, footer { visibility: hidden; }
/* ---- Main area: dark readable text ---- */
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] strong,
.stApp h1, .stApp h2, .stApp h3, .info-box h3, .info-box p { color: #1a1a2e !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary *,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #3a4a63 !important; }
/* ---- Sidebar: lighter VU blue, white text ---- */
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #1f4a7d !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] label { color: #ffffff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.3) !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: rgba(255,255,255,0.14) !important;
    border-color: rgba(255,255,255,0.35) !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] *,
section[data-testid="stSidebar"] [data-baseweb="input"] *,
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button { color: #ffffff !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] svg,
section[data-testid="stSidebar"] [data-testid="stNumberInput"] svg { fill: #ffffff !important; }
section[data-testid="stSidebar"] input::placeholder { color: rgba(255,255,255,0.7) !important; }
section[data-testid="stSidebar"] [data-testid="stButton"] button p { color: #0a2240 !important; }
/* ---- Chat input ---- */
[data-testid="stChatInput"] { background: #ffffff !important; border: 1.5px solid #dde0e6 !important;
    border-radius: 26px !important; overflow: hidden; }
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] [data-baseweb],
[data-testid="stChatInput"] textarea { background: transparent !important; border: none !important;
    box-shadow: none !important; color: #1a1a2e !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #8a94a6 !important; }
[data-testid="stChatInput"] button { background: #c0182a !important; border-radius: 50% !important; }
[data-testid="stChatInput"] button svg { fill: #ffffff !important; color: #ffffff !important; }
/* ---- Chat bubbles ---- */
.bubble-user { display: flex; justify-content: flex-end; margin: 6px 0; }
.bubble-bot  { display: flex; justify-content: flex-start; margin: 6px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]

ACADEMIC_EXTENSIONS = (".pdf", ".txt", ".csv", ".xlsx", ".xls")
EXCLUDED_FILES = ("advisor_eval", "eval_results", "phase4", "summary_metrics", "website_sources")

DEFAULT_WEBSITE_SOURCES = [
    {"name": "VU Official Website", "url": "https://vidyashilp.edu.in/"},
    {"name": "VU About", "url": "https://vidyashilp.edu.in/about/"},
    {"name": "VU Admissions", "url": "https://vidyashilp.edu.in/admissions/"},
    {"name": "VU Scholarship", "url": "https://vidyashilp.edu.in/scholarship/"},
    {"name": "VU Contact", "url": "https://vidyashilp.edu.in/contact/"},
    {"name": "VU B.Tech (Hons.) Data Science", "url": "https://vidyashilp.edu.in/schools/bachelor-of-technology-hons-computer-science-and-engineering-data-science/"},
    {"name": "VU B.Tech (Hons.) AI/ML", "url": "https://vidyashilp.edu.in/schools/b_tech_ai_ml/"},
    {"name": "VU B.A. (Hons.) Economics", "url": "https://vidyashilp.edu.in/schools/bachelor-of-arts-hons/"},
    {"name": "VU B.A. (Hons.) Psychology", "url": "https://vidyashilp.edu.in/schools/bachelor-of-arts-hons-with-research/"},
    {"name": "VU B.Des", "url": "https://vidyashilp.edu.in/schools/bachelor-of-design/"},
    {"name": "VU B.M.S. (Hons.)", "url": "https://vidyashilp.edu.in/schools/b-m-s-hons-hons-with-research-in-digital-business/"},
    {"name": "VU B.A., LL.B. (Hons.)", "url": "https://vidyashilp.edu.in/schools/b-a-ll-b-hons/"},
    {"name": "VU B.M.S., LL.B. (Hons.)", "url": "https://vidyashilp.edu.in/schools/bachelor-of-management-studies-bachelor-of-laws-hons/"},
    {"name": "VU PhD Programme", "url": "https://vidyashilp.edu.in/phd-program/"},
]

# Paste any extra VU pages here, one per line, e.g.:
#   {"name": "VU Anti-Ragging", "url": "https://vidyashilp.edu.in/anti-ragging-committee-3/"},
EXTRA_WEBSITE_LINKS = [
]

# If True, programme pages linked from the VU homepage (/schools/...) are added automatically
AUTO_DISCOVER_PROGRAMMES = True

SOCIAL_RE = re.compile(
    r"^\s*(h+i+|h+e+l+o+|h+l+o+|hlw|helo|hellow|hey+|hola|yo+|sup|bro|wsp|wsup|what'?s\s*up|wassup|"
    r"good\s*(morning|afternoon|evening|night)|namaste|namaskaram|"
    r"thank(s|\s*you|u)|thx|ty|ok(ay)?|got\s*it|sure|great|nice|cool|"
    r"bye|goodbye|see\s*you|take\s*care|cya)\s*[!.?]*\s*$",
    re.I,
)
GREETING_REPLY = (
    "Hey! 👋 I'm VU's AI Academic Advisor. I can help with attendance, credits, "
    "prerequisites, registration, course eligibility, progression rules and more. "
    "What would you like to know?"
)
THANKS_REPLY = "Happy to help! 😊 Feel free to ask anything else about your academics at VU."

OUT_OF_SCOPE_RE = re.compile(
    r"\b(president of|prime minister|chief minister|capital of|ipl|world cup|bollywood|weather|temperature|rain|forecast|cricket|football|soccer|match|movie|movies|"
    r"song|music|restaurant|recipe|stock market|politics|election|celebrity|"
    r"who will win|score today|bitcoin|share price)\b",
    re.I,
)
PERSONAL_RE = re.compile(
    r"\b(your mom|your mother|your dad|your father|your family|your girlfriend|"
    r"your boyfriend|are you dumb|are u dumb|are you stupid|are u stupid|"
    r"who are you|what are you)\b",
    re.I,
)
OUT_OF_SCOPE_REPLY = (
    "Sorry, I can't help with that one 😅 I only handle Vidyashilp University "
    "academics, like courses, credits, attendance, programmes and admissions. "
    "Ask me something on those!"
)
PERSONAL_REPLY = (
    "I'm an AI academic advisor, so I don't have a personal family or personal life. "
    "But I can definitely help with your VU academic questions. 😊"
)
NO_INFO_REPLY = (
    "I don't have enough information in the available VU sources to answer that accurately. "
    "Please check with the relevant academic office or programme office for the current rule."
)

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "messages": [],
    "academic_kb": [],
    "website_kb": [],
    "knowledge_loaded": False,
    "website_loaded": False,
    "pending_question": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# LOGO & HEADER
# ============================================================
def find_logo():
    files = [f for f in os.listdir(".") if not f.startswith(".")]
    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg")) and "logo" in f.lower():
            return f
    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            return f
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
        ["B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"],
        index=None, placeholder="Select if needed",
    )
    semester = st.selectbox(
        "Current Semester",
        ["1st Semester", "2nd Semester", "3rd Semester", "4th Semester", "5th Semester",
         "6th Semester", "7th Semester", "8th Semester", "9th Semester", "10th Semester"],
        index=None, placeholder="Select if needed",
    )
    completed_credits = st.number_input(
        "Completed Credits", min_value=0, max_value=400, value=None, step=1, placeholder="Optional"
    )
    cgpa = st.number_input(
        "CGPA", min_value=0.0, max_value=10.0, value=None, step=0.1, format="%.2f", placeholder="Optional"
    )
    st.markdown("---")
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# API KEY & PROFILE
# ============================================================
def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

api_key = get_api_key()

student_profile = {
    "program": program,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa,
}

# ============================================================
# TEXT EXTRACTION
# ============================================================
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()

def guess_section(raw_text):
    """Return an explicit-looking heading, otherwise blank."""
    for line in raw_text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line or len(line) > 100:
            continue
        if re.match(r"^(?:\d+(?:\.\d+)*\s+.+|[A-Z][A-Z0-9 &:/()\-]{4,})$", line):
            return line
        words = line.split()
        if 2 <= len(words) <= 10 and not re.search(r"[.!?]$", line):
            if sum(1 for w in words if w[:1].isupper()) >= max(2, len(words) // 2):
                return line
    return ""

def extract_pdf_pages(filepath):
    pages = []
    try:
        reader = PdfReader(filepath)
        for n, page in enumerate(reader.pages, start=1):
            try:
                raw = page.extract_text() or ""
                text = clean_text(raw)
                if text:
                    pages.append({"text": text, "page": n, "section": guess_section(raw)})
            except Exception:
                continue
    except Exception:
        return []
    return pages

def extract_plain_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception:
        return ""

def extract_excel_sheets(filepath):
    try:
        from openpyxl import load_workbook
        wb = load_workbook(filepath, read_only=True, data_only=True)
        sheets = []
        for sheet in wb.worksheets:
            rows = []
            for row in sheet.iter_rows(values_only=True):
                values = [str(v) for v in row if v is not None]
                if values:
                    rows.append(" | ".join(values))
            if rows:
                sheets.append({"sheet": sheet.title, "rows": rows})
        return sheets
    except Exception:
        return []

# ============================================================
# CHUNKING
# ============================================================
def chunk_text(text, chunk_size=150, overlap=30):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
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
        lower = filename.lower()
        if filename.startswith(".") or not lower.endswith(ACADEMIC_EXTENSIONS):
            continue
        if any(ex in lower for ex in EXCLUDED_FILES):
            continue
        filepath = os.path.join(".", filename)
        ext = os.path.splitext(lower)[1]
        base = {"source": filename, "type": "academic"}
        if ext == ".pdf":
            for p in extract_pdf_pages(filepath):
                for i, c in enumerate(chunk_text(p["text"]), start=1):
                    documents.append({**base, "text": c, "chunk": i,
                                      "page": p["page"], "section": p["section"]})
        elif ext in (".xlsx", ".xls"):
            for sh in extract_excel_sheets(filepath):
                rows, header, group = sh["rows"], sh["rows"][0], 12
                for i in range(0, len(rows), group):
                    block = rows[i:i + group]
                    if i > 0:
                        block = [header] + block
                    documents.append({**base, "text": "\n".join(block),
                                      "chunk": i // group + 1, "sheet": sh["sheet"]})
        else:
            for i, c in enumerate(chunk_text(extract_plain_text(filepath)), start=1):
                documents.append({**base, "text": c, "chunk": i})
    return documents

# ============================================================
# WEBSITE SOURCES
# ============================================================
USE_WEBSITE_SOURCES_JSON = False  # keep False: the verified list in code is used

SITE_ROOT = "https://vidyashilp.edu.in/"
MAX_AUTO_PAGES = 60
SKIP_URL_PARTS = ("wp-content", "preapplication", "phd-apply-now", "application.", "/blogs/",
                  "indiarising", "seru.php", "enquiryform", "javascript", "mailto", "tel:")
SKIP_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".zip", ".php", ".doc", ".docx", ".xlsx")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@st.cache_data(ttl=3600, show_spinner=False)
def discover_site_links():
    """Collect every page linked from the VU homepage menus (all the 'tabs')."""
    try:
        from urllib.parse import urljoin, urlparse
        from bs4 import BeautifulSoup
        resp = requests.get(SITE_ROOT, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        found = {}
        for a in soup.find_all("a", href=True):
            url = urljoin(SITE_ROOT, a["href"]).split("#")[0].split("?")[0]
            parsed = urlparse(url)
            if parsed.netloc != "vidyashilp.edu.in" or parsed.path in ("", "/"):
                continue
            low = url.lower()
            if any(x in low for x in SKIP_URL_PARTS) or low.endswith(SKIP_EXTENSIONS):
                continue
            url = url if url.endswith("/") else url + "/"
            slug = parsed.path.strip("/").split("/")[-1].replace("-", " ").replace("_", " ")
            found.setdefault(url, clean_text(a.get_text(" ")) or slug)
        return [{"name": ("VU " + n)[:60], "url": u} for u, n in list(found.items())[:MAX_AUTO_PAGES]]
    except Exception:
        return []

def load_website_sources():
    sources = list(DEFAULT_WEBSITE_SOURCES) + list(EXTRA_WEBSITE_LINKS)
    if USE_WEBSITE_SOURCES_JSON and os.path.exists("website_sources.json"):
        try:
            with open("website_sources.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                sources += data
        except Exception:
            pass
    if AUTO_DISCOVER_PROGRAMMES:
        sources += discover_site_links()
    unique, seen = [], set()
    for src in sources:
        key = src.get("url", "").rstrip("/")
        if key and key not in seen:
            seen.add(key)
            unique.append(src)
    return unique

def download_page(url):
    """Plain download + parse (no Streamlit calls, safe to run in threads)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
            tag.decompose()
        title = clean_text(soup.title.get_text()) if soup.title else ""
        sections, current, seen_text = [], title or "VU Official Website", set()
        for el in soup.find_all(["h1", "h2", "h3", "p", "li", "td", "th", "div"]):
            if el.name == "div" and el.find(["div", "p", "li", "h1", "h2", "h3", "table", "ul", "ol"]):
                continue
            txt = clean_text(el.get_text(" "))
            if not txt or txt in seen_text:
                continue
            seen_text.add(txt)
            if el.name in ("h1", "h2", "h3"):
                current = txt
            else:
                sections.append({"section": current, "text": txt})
        if not sections:
            sections = [{"section": title or "VU Official Website",
                         "text": clean_text(soup.get_text(separator=" "))}]
        return {"title": title, "sections": sections}
    except Exception:
        return {"title": "", "sections": []}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_pages(urls):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(download_page, urls))
    return dict(zip(urls, results))

def load_website_documents():
    sources = [src for src in load_website_sources() if src.get("url")]
    pages = fetch_all_pages(tuple(src["url"] for src in sources))
    documents = []
    for source in sources:
        url = source["url"]
        page = pages.get(url, {})
        for sec in page.get("sections", []):
            for i, c in enumerate(chunk_text(sec.get("text", ""), 180, 40), start=1):
                documents.append({
                    "text": c, "source": source.get("name", "VU Official Website"),
                    "url": url, "title": page.get("title", ""),
                    "section": sec.get("section", ""), "type": "website", "chunk": i,
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
# TOKENIZER & RETRIEVAL (TF-IDF style)
# ============================================================
STOPWORDS = {
    "the", "a", "an", "is", "are", "am", "i", "me", "my", "to", "of", "in", "on",
    "for", "and", "or", "can", "could", "would", "should", "do", "does", "did",
    "be", "it", "this", "that", "with", "from", "at", "as", "what", "which",
    "how", "where", "when", "why", "you", "your",
}
BOOST_PHRASES = [
    "minimum cgpa", "attendance", "eligibility", "eligible", "prerequisite", "minor",
    "semester", "admission", "course", "credits", "programme", "program", "transfer",
    "law", "summer", "summer term",
]

def stem(t):
    """Very light plural handling so 'minors' matches 'minor'."""
    if len(t) > 4 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t

def tokenize(text):
    text = re.sub(r"\bb\.?\s?tech\b", "btech", text.lower())
    text = re.sub(r"\bb\.?\s?des\b", "bdes", text)
    return [stem(t) for t in re.findall(r"[a-zA-Z0-9]+", text) if t not in STOPWORDS]

GENERIC_FILE_TOKENS = {"student", "sept", "2026", "aug", "final", "for", "spread", "structure", "plan"}

def retrieve(query, documents, top_k=5, minimum_score=0.05):
    if not documents:
        return []
    query_counter = Counter(tokenize(query))
    if not query_counter:
        return []
    doc_freq, tokenized_docs = Counter(), []
    for doc in documents:
        meta = f'{doc.get("source", "")} {doc.get("sheet", "")}'.replace("_", " ")
        toks = tokenize(doc["text"] + " " + meta)
        doc_freq.update(set(toks))
        tokenized_docs.append(toks)
    total, ql, scored = len(documents), query.lower(), []
    for doc, toks in zip(documents, tokenized_docs):
        if not toks:
            continue
        tc = Counter(toks)
        score = sum(
            (tc[t] / len(toks)) * (math.log((total + 1) / (doc_freq.get(t, 0) + 1)) + 1) * qc
            for t, qc in query_counter.items() if t in tc
        )
        tl = doc["text"].lower()
        score += 0.15 * sum(1 for p in BOOST_PHRASES if p in ql and p in tl)
        # A query word that appears in the FILE NAME (e.g. "minor" -> Minor_Courses_...) is a strong signal
        fname = os.path.splitext(doc.get("source", ""))[0].replace("_", " ")
        fname_tokens = set(tokenize(fname)) - GENERIC_FILE_TOKENS
        score += 0.25 * len(fname_tokens & set(query_counter))
        if score >= minimum_score:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{**d, "_score": s} for s, d in scored[:top_k]]

# ============================================================
# CLASSIFY QUERY
# ============================================================
WEBSITE_PATTERNS = [
    "admission", "apply", "application", "how do i join", "join vu", "contact",
    "phone number", "email", "address", "campus", "location", "where is vu",
    "where is vidyashilp", "programmes offered", "about vu", "vidyashilp university",
    "law programme",
]

def classify_query(query):
    q = query.lower()
    return "website" if any(p in q for p in WEBSITE_PATTERNS) else "academic"

# ============================================================
# PROFILE
# ============================================================
def profile_to_text(profile):
    lines = []
    if profile.get("program"):
        lines.append(f"Program: {profile['program']}")
    if profile.get("semester"):
        lines.append(f"Semester: {profile['semester']}")
    if profile.get("completed_credits") is not None:
        lines.append(f"Completed credits: {profile['completed_credits']}")
    if profile.get("cgpa") is not None:
        lines.append(f"CGPA: {profile['cgpa']}")
    return "\n".join(lines) if lines else "No student profile information was provided."

def effective_profile_for_question(question):
    """Let details stated in the message override the sidebar for that question."""
    profile = dict(student_profile)
    q = question.lower()
    aliases = {
        "b.tech": "B.Tech", "btech": "B.Tech", "bms llb": "BMS LLB", "ba llb": "BA LLB",
        "b.a. llb": "BA LLB", "bms": "BMS", "b.a. economics": "B.A. Economics",
        "ba economics": "B.A. Economics", "b.a. psychology": "B.A. Psychology",
        "ba psychology": "B.A. Psychology", "b.des": "B.Des", "bdes": "B.Des",
    }
    for alias, label in aliases.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", q):
            profile["program"] = label
            break
    extra = re.search(r"\b(bba|b\.arch|barch|mba|mca|bca)\b", q, re.I)
    if extra:
        profile["program"] = extra.group(1).upper().replace("BARCH", "B.ARCH")
    m = re.search(r"\b(?:cgpa|gpa)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)", q)
    if m:
        profile["cgpa"] = float(m.group(1))
    m = re.search(r"\b(\d+)\s*(?:completed\s+)?credits?\b", q) or \
        re.search(r"\bcredits?\s*(?:completed)?\s*(?:is|are|=|:)?\s*(\d+)\b", q)
    if m:
        profile["completed_credits"] = int(m.group(1))
    m = re.search(r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th)\s+semester\b", q)
    if m:
        profile["semester"] = m.group(1) + " Semester"
    return profile

# ============================================================
# CONVERSATION CONTEXT
# ============================================================
FOLLOW_UP_RE = re.compile(
    r"^\s*(which one|which ones|what about (that|this|it)|and what about|what about it|"
    r"what are the prerequisites|what is the prerequisite|what about prerequisites|"
    r"how about (that|this|it)|tell me more|more details|why|how|where|when|which)\b",
    re.I,
)
NEW_TOPIC_TERMS = {
    "attendance", "credits", "credit", "prerequisite", "prerequisites", "registration",
    "admission", "apply", "application", "fees", "fee", "programme", "program", "minor",
    "minors", "major", "majors", "semester", "course", "courses", "grading", "cgpa",
    "backlog", "progression", "graduation", "contact", "address", "law", "bms", "btech",
    "psychology", "economics", "design",
}

def get_last_user_question(skip_current=False):
    skipped = False
    for msg in reversed(st.session_state.messages):
        if msg.get("role") == "user":
            if skip_current and not skipped:
                skipped = True
                continue
            return msg.get("content", "")
    return ""

def is_follow_up_question(question, previous):
    if not previous:
        return False
    q = question.lower().strip()
    if len(q.split()) <= 5 and not any(t in q for t in NEW_TOPIC_TERMS):
        return True
    return bool(FOLLOW_UP_RE.search(q))

def conversation_context_for(question):
    previous = get_last_user_question(skip_current=True)
    if not is_follow_up_question(question, previous):
        return ""
    prev_answer = ""
    for msg in reversed(st.session_state.messages):
        if msg.get("role") == "assistant":
            prev_answer = msg.get("content", "")
            break
    return f"Previous student question: {previous}\nPrevious advisor answer: {prev_answer[:1800]}"

# ============================================================
# SYSTEM PROMPT
# ============================================================
def build_system_prompt(profile):
    return f"""You are the AI Academic Advisor for Vidyashilp University (VU), Bengaluru, India.

Student profile for this question:
{profile_to_text(profile)}

YOUR ROLE:
Help students with VU undergraduate academic questions: courses, credits, prerequisites,
attendance, progression, graduation requirements, semester planning, admissions and programmes.

RESPONSE STYLE:
- Keep responses short, clear and conversational.
- No tables and no long report-style answers.
- Use at most 4-5 bullets when useful.
- Friendly and warm, but accurate.
- Never guess a rule, number, course, eligibility condition or programme structure.

PROFILE RULES:
- Sidebar profile values are optional. Blank means unknown; never assume a value.
- If the student's message states a different programme/semester/credits/CGPA, use that
  for this question only.
- If a programme is not in the sidebar options, use the student's stated programme as
  question-specific context rather than inventing a match.

CONVERSATION RULES:
- A short follow-up ("which one?", "what are the prerequisites?") may refer to the
  immediately preceding academic topic. Use that context only when clearly connected.
- If the student starts a new topic, ignore the old topic.

BEHAVIOUR RULES:
1. Greetings and casual openers get a friendly reply without retrieval.
2. Personal questions about the AI: answer briefly and redirect to academics.
3. Completely non-academic questions: decline politely, no sources.
4. Summer Term: do not invent offerings, fees or rules. Say the available information is
   insufficient and advise checking the academic office/registrar.
5. For Law programmes, use the Law programme sources when available.
6. In VU's integrated B.A., LL.B. and B.M.S., LL.B. programmes, Law is the core legal
   education component. Do NOT tell a Law student they can simply choose "Law" as a major or
   minor. The programme has its own Liberal Discipline major/minor structure alongside Law.
7. If a BMS student asks about minors, use the BMS-specific source (it lists minors such as
   Law, Data Science, Economics, Design and Psychology).
8. Fees or financial queries: "Please contact the Accounts office directly."
9. Specific professors/HODs: "Please contact the department office directly."
10. If a question has multiple parts, answer each part separately.
11. If the sources do not contain enough information, say so clearly instead of guessing.
12. If sources disagree, explicitly mention the disagreement; do not silently pick one.
13. When a source gives a numeric threshold and the student gives their own number, compare
    them directly and state the result (eligible / not eligible). Do not ask for a number the
    student already gave.
14. ASK BEFORE ASSUMING: if a reliable answer depends on information that is missing
    (for example which courses the student has completed, their semester, programme, credits
    or CGPA), do NOT guess. But if the sources already answer the question for the student's
    whole programme (e.g. a minors list for B.Tech), just answer; do not ask for details you
    do not need. Otherwise ask ONE short, specific follow-up question naming exactly what you
    need, and mention what you can already tell them from the sources.
15. WEBSITE FIRST: the OFFICIAL VU WEBSITE excerpts are your primary source for everything.
    If they answer the question, answer from them and do not mix in the academic documents.
    ONLY if the website excerpts do not contain the answer, use the ACADEMIC DOCUMENTS
    excerpts. If neither contains it, say so.
18. LISTS (minors, majors, electives): give the complete list exactly as the source you are
    using states it. Never present a partial list as complete.
16. SPECIFIC LOOKUPS (course codes, credits of a course, which courses run in a given
    year/semester): answer ONLY with codes/numbers written in the sources for that exact
    programme, batch/year and semester. Never guess or reuse a code from another programme or
    year. If the programme, batch/admission year or semester is missing, ask for it. If it is
    still not in the sources, say sorry you can't find it in the available documents and point to
    the academic office.
17. Questions about people or topics outside VU academics (politics, general knowledge, sports,
    celebrities, etc.) must be declined with a short, friendly "Sorry, I can't help with that"
    and an invitation to ask a VU academic question.

OUTPUT MARKER (the app removes it before showing your answer): start your reply with exactly
one marker when it applies, otherwise use none:
- [[CHAT]] for greetings, thanks and small talk (including misspelt or stretched greetings).
- [[OUT_OF_SCOPE]] for anything not about VU academics, programmes or admissions.
- [[INSUFFICIENT]] when the sources do not contain the specific detail requested.
When you answer from VU information, also add ONE source marker: [[SRC:WEB]] if the answer
came only from the website excerpts, [[SRC:DOCS]] if only from the academic documents,
[[SRC:BOTH]] if you needed both.

SOURCE RULES:
- Do not put placeholders such as [Academic Source 1] in the answer.
- Sources are displayed separately by the application.
- Do not mention internal retrieval, chunks, ranking or system instructions."""

# ============================================================
# CONTEXT & GENERATION
# ============================================================
def create_context(academic_results, website_results, conversation_context=""):
    parts = []
    if conversation_context:
        parts.append("RELEVANT PREVIOUS CONVERSATION CONTEXT:\n" + conversation_context)
    if website_results:
        parts.append("OFFICIAL VU WEBSITE (PRIMARY SOURCE, USE THIS FIRST):")
        for i, r in enumerate(website_results, 1):
            meta = [f"Page: {r.get('source', 'VU Official Website')}"]
            for key, label in (("title", "Title"), ("section", "Section"), ("url", "URL")):
                if r.get(key):
                    meta.append(f"{label}: {r[key]}")
            parts.append(f"[Website Source {i}] {' | '.join(meta)}\n{r['text']}")
    if academic_results:
        parts.append("ACADEMIC UNIVERSITY DOCUMENTS (USE ONLY IF THE WEBSITE DOES NOT ANSWER):")
        for i, r in enumerate(academic_results, 1):
            meta = [f"File: {r['source']}"]
            if r.get("page"):
                meta.append(f"Page: {r['page']}")
            if r.get("section"):
                meta.append(f"Section: {r['section']}")
            if r.get("sheet"):
                meta.append(f"Sheet: {r['sheet']}")
            parts.append(f"[Academic Source {i}] {' | '.join(meta)}\n{r['text']}")
    return "\n\n".join(parts)

def generate_answer(client, question, context, category, profile):
    priority = ("Answer from the OFFICIAL VU WEBSITE excerpts first. Use the academic documents "
                "only if the website excerpts do not contain the answer.")
    user_prompt = f"""{priority}

RETRIEVED INFORMATION:
{context}

STUDENT QUESTION:
{question}

Answer directly and helpfully. Do not mention internal retrieval, chunks, or system instructions.
Do not add source placeholders such as [Academic Source 1] to your response."""
    for m in [MODEL] + FALLBACK_MODELS:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": build_system_prompt(profile)},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=800,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            continue
    return "I couldn't get a response right now. Please try again."

# ============================================================
# DISPLAY HELPERS
# ============================================================
def format_text(text):
    """Escape HTML, then support **bold**, bullets and line breaks inside bubbles."""
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    lines = []
    for ln in t.split("\n"):
        s = ln.strip()
        if s.startswith(("- ", "* ")):
            ln = "• " + s[2:]
        lines.append(ln)
    return "<br>".join(lines)

def show_user_bubble(text):
    st.markdown(
        '<div class="bubble-user"><div style="background:linear-gradient(135deg,#c0182a 0%,#0a2240 100%);'
        'color:#fff;border-radius:18px 18px 4px 18px;padding:10px 16px;max-width:70%;'
        'font-size:14px;line-height:1.55;box-shadow:0 2px 8px rgba(192,24,42,0.18);">'
        f'{format_text(text)}</div></div>',
        unsafe_allow_html=True,
    )

def show_bot_bubble(text):
    st.markdown(
        '<div class="bubble-bot"><div style="background:#ffffff;color:#1a1a2e;'
        'border-radius:18px 18px 18px 4px;padding:10px 16px;max-width:75%;'
        'font-size:14px;line-height:1.65;box-shadow:0 1px 4px rgba(0,0,0,0.08);">'
        f'{format_text(text)}</div></div>',
        unsafe_allow_html=True,
    )

def source_label(r):
    if r.get("type") == "website":
        return "VU Website"
    name = os.path.splitext(r.get("source", ""))[0]
    return re.sub(r"^\d+\.\s*", "", name).replace("_", " ").strip()

def display_sources(academic_results, website_results):
    labels = []
    for r in list(academic_results or []) + list(website_results or []):
        lab = source_label(r)
        if lab and lab not in labels:
            labels.append(lab)
    if labels:
        st.caption("Sources: " + " · ".join(labels[:3]))

def reply(answer, academic=None, website=None, show_src=False):
    """Show a bot answer (optionally with sources) and save it to history."""
    academic, website = academic or [], website or []
    show_bot_bubble(answer)
    if show_src and (academic or website):
        display_sources(academic, website)
    st.session_state.messages.append({
        "role": "assistant", "content": answer,
        "academic_sources": academic if show_src else [],
        "website_sources": website if show_src else [],
    })

# ============================================================
# SUGGESTIONS (empty chat)
# ============================================================
SUGGESTIONS = [
    "What programmes does VU offer?",
    "How do I apply to VU?",
    "What is the minimum CGPA to progress?",
    "What are the attendance requirements?",
    "Which minors are available for B.Tech?",
    "What courses are offered next semester?",
]

pending = st.session_state.pending_question
st.session_state.pending_question = None
typed_question = st.chat_input("Ask your academic question...")
user_question = pending or typed_question

if not st.session_state.messages and not user_question:
    st.markdown("""
    <div class="info-box">
    <h3>Ask your academic question</h3>
    <p>I can help with VU courses, programmes, prerequisites, eligibility,
    credits, semesters, admissions and related university information.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 💡 Try asking")
    cols = st.columns(3)
    for i, s in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = s
                st.rerun()

# ============================================================
# CHAT HISTORY
# ============================================================
for msg in st.session_state.messages:
    if msg.get("role") == "user":
        show_user_bubble(msg.get("content", ""))
    else:
        show_bot_bubble(msg.get("content", ""))
        ac, wc = msg.get("academic_sources", []), msg.get("website_sources", [])
        if ac or wc:
            display_sources(ac, wc)

# ============================================================
# GET QUESTION
# ============================================================

# ============================================================
# PROCESS QUESTION
# ============================================================
if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    show_user_bubble(user_question)

    # --- Shortcuts: greetings, personal, out-of-scope (no retrieval, no sources) ---
    if SOCIAL_RE.match(re.sub(r"(.)\1{2,}", r"\1", user_question.strip())):
        is_thanks = re.search(r"\b(thank(s|\s*you|u)|thx|ty)\b", user_question, re.I)
        reply(THANKS_REPLY if is_thanks else GREETING_REPLY)
    elif PERSONAL_RE.search(user_question):
        reply(PERSONAL_REPLY)
    elif OUT_OF_SCOPE_RE.search(user_question):
        reply(OUT_OF_SCOPE_REPLY)
    elif not api_key:
        reply("The advisor is not configured yet. Please contact the administrator.")
    else:
        # --- Academic question: retrieval + LLM ---
        try:
            category = classify_query(user_question)
            profile = effective_profile_for_question(user_question)
            conv_ctx = conversation_context_for(user_question)

            retrieval_query = user_question
            if conv_ctx:
                retrieval_query = f"{get_last_user_question(skip_current=True)} {user_question}"

            # Website first, documents as fallback (both retrieved; the prompt enforces the order)
            website_results = retrieve(retrieval_query, website_kb, top_k=8, minimum_score=0.035)
            academic_results = retrieve(retrieval_query, academic_kb, top_k=6, minimum_score=0.045)

            if not academic_results and not website_results:
                reply(NO_INFO_REPLY)
            else:
                context = create_context(academic_results, website_results, conv_ctx)
                with st.spinner("Thinking..."):
                    answer = generate_answer(Groq(api_key=api_key), user_question,
                                             context, category, profile)
                show_src = True
                for marker in ("[[CHAT]]", "[[OUT_OF_SCOPE]]", "[[INSUFFICIENT]]"):
                    if marker in answer:
                        show_src = False
                src = re.search(r"\[\[SRC:(WEB|DOCS|BOTH)\]\]", answer)
                answer = re.sub(r"\[\[[A-Z_:]+\]\]\s*", "", answer).strip()
                which = src.group(1) if src else ("WEB" if website_results else "DOCS")
                web_for_display = website_results if which in ("WEB", "BOTH") else []
                docs_for_display = academic_results if which in ("DOCS", "BOTH") else []
                reply(answer, docs_for_display, web_for_display, show_src=show_src)
        except Exception:
            reply("I couldn't process that request right now. Please try again.")

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    '<div class="footer-text">Vidyashilp University · AI Academic Advisor</div>',
    unsafe_allow_html=True,
)
