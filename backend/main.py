"""FastAPI academic advisor service deployed as a Vercel Service."""
from __future__ import annotations
import io, json, os, re, urllib.request, urllib.parse, zipfile
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Request
from groq import Groq
from pypdf import PdfReader
from programme_data import extract_archive_records

app=FastAPI(title="VU Academic Advisor API")
RAW="https://raw.githubusercontent.com/goury-nandana/vu-academic-advisor-gai-a2/main/"
GH="https://raw.githubusercontent.com/goury-nandana/vu-academic-advisor-gai-a2/main/"
def get(path):
    req=urllib.request.Request(RAW+urllib.parse.quote(path),headers={"User-Agent":"VU-Academic-Advisor"})
    with urllib.request.urlopen(req,timeout=25) as r:return r.read()
def pdf(path):
    try:
        reader=PdfReader(io.BytesIO(get(path)))
        return [{"text":re.sub(r"\s+"," ",p.extract_text() or "").strip(),"source":path,"page":i+1,"url":GH+urllib.parse.quote(path)} for i,p in enumerate(reader.pages) if (p.extract_text() or "").strip()]
    except Exception:return []
@lru_cache(maxsize=1)
def load_docs():
    docs=pdf("4. Student Handbook Aug 2026.pdf")+pdf("SOP STUDENT 17082026 - Final.pdf")
    try:docs.append({"text":get("Course_Plans.txt").decode("utf-8",errors="ignore"),"source":"Course_Plans.txt","url":GH+"Course_Plans.txt"})
    except Exception:pass
    try:
        from openpyxl import load_workbook
        z=zipfile.ZipFile(io.BytesIO(get("VU_Semester_Data_Split.zip")))
        for filename in z.namelist():
            if not filename.endswith(".xlsx"):continue
            wb=load_workbook(io.BytesIO(z.read(filename)),read_only=True,data_only=True); ws=wb.active
            for row in ws.iter_rows(min_row=3,values_only=True):
                s=" | ".join(str(v) for v in row if v is not None)
                if s:docs.append({"text":s,"source":filename,"url":GH+"VU_Semester_Data_Split.zip"})
            wb.close()
    except Exception:pass
    # Minor workbooks are a separate source archive. Keep explicit course rows
    # structured and ambiguous elective cells raw; never split or infer values.
    try:
        minor_raw = get("VU_Minor_Data_Split.zip")
        for record in extract_archive_records(minor_raw, "minor"):
            docs.append({**record, "url": GH + "VU_Minor_Data_Split.zip"})
    except Exception:
        pass
    # Programme structures live beside semester spreads in the same archive.
    try:
        programme_raw = get("VU_Semester_Data_Split.zip")
        for record in extract_archive_records(programme_raw, "programme"):
            docs.append({**record, "url": GH + "VU_Semester_Data_Split.zip"})
    except Exception:
        pass
    chunks=[]
    for d in docs:
        words=d["text"].split()
        for i in range(0,len(words),180):
            txt=" ".join(words[max(0,i-30):i+180])
            if txt:chunks.append({**d,"text":txt})
    return chunks
STOP=set("the a an is are am i me my to of in on for and or can could would should do does did be it this that with from at as what which how where when why you your".split())
def tok(s):return [x for x in re.findall(r"[a-z0-9]+",s.lower()) if x not in STOP]
def search(q,docs):
    qset=set(tok(q)); scores=[]
    for d in docs:
        terms=set(tok(d["text"])); n=len(qset&terms)
        if n:scores.append((n/(len(terms)**.45),d))
    scores.sort(key=lambda x:x[0],reverse=True)
    return [d for _,d in scores[:7]]
SYS="""You are the AI Academic Advisor for Vidyashilp University, Bengaluru. Respond concisely and only from retrieved evidence. Never invent course codes, policy thresholds, eligibility, credits, or student-record facts. Never claim access to private university records; use profile only if explicitly supplied. For B.Tech minor questions, published Data Science and AI/ML tracks list Economics, Marketing, Psychology, Finance, Design, and Law; do not mix programmes' lists. If sources are insufficient, state that and suggest Digicampus or relevant office. Fees: Accounts; professors/HODs: department office; records/exams: Registrar. Specific course codes: advise Digicampus for details. For minor and programme-structure questions, use only rows explicitly matching the requested programme, minor, batch and named structure group. Never transfer a minor list or structure between programmes or batches. A raw elective slot or slash-delimited alternative is source text, not multiple confirmed course records: preserve it verbatim and state that the source does not resolve it into separate courses. If a code is missing or marked DON’T KNOW, report it as unavailable rather than guessing."""
SOCIAL_RE = re.compile(
    r"^(?:h(?:i|e?y|ello|i{2,}|e{2,}y)|yo|sup|"
    r"good\s+(?:morning|afternoon|evening|night)|"
    r"how\s+(?:are\\s+you|r\\s+you|is\s+it\s+going|do\s+you\s+do)|"
    r"what'?s\s+up|thanks?|thank\\s+you(?:\\s+so\\s+much)?)[!.?, ]*$",
    re.I,
)

SOCIAL_REPLY = (
    "I’m working normally and ready to help with Vidyashilp University. "
    "What academic question can I help you with?"
)

def extract_upload(filename, raw, client=None):
    ext=filename.lower().rsplit(".",1)[-1] if "." in filename else ""
    if ext in {"webm","mp3","wav","m4a","ogg","flac","mp4","mpeg","mpga"}:
        if client is None:
            return ""
        try:
            transcription=client.audio.transcriptions.create(
                file=(filename, raw),
                model=os.getenv("GROQ_TRANSCRIPTION_MODEL","whisper-large-v3-turbo"),
                response_format="text",
                prompt="Vidyashilp University, academic courses, attendance, semester, credits, admissions.",
            )
            text=str(transcription).strip()
            return "Voice note transcript: " + text if text else ""
        except Exception as exc:
            return f"Voice-note transcription failed: {exc}"
    try:
        if ext=="pdf":
            return "\\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(raw)).pages)
        if ext in {"txt","md","csv"}:return raw.decode("utf-8",errors="ignore")
        if ext=="docx":
            from docx import Document
            return "\\n".join(p.text for p in Document(io.BytesIO(raw)).paragraphs)
        if ext=="xlsx":
            from openpyxl import load_workbook
            wb=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
            return "\\n".join(" | ".join(str(v) for v in row if v is not None) for ws in wb.worksheets for row in ws.iter_rows(values_only=True))
        if ext=="pptx":
            from pptx import Presentation
            prs=Presentation(io.BytesIO(raw))
            return "\\n".join(sh.text for slide in prs.slides for sh in slide.shapes if hasattr(sh,"text"))
    except Exception:return ""
    return ""

@app.get("/api")
@app.get("/api/")
async def health():return {"status":"ok","service":"VU Academic Advisor API"}
@app.post("/api/chat")
async def chat(req:Request):
    key=os.getenv("GROQ_API_KEY","").strip()
    if not key:raise HTTPException(503,"Set GROQ_API_KEY in Vercel backend environment variables.")
    client=Groq(api_key=key)
    form=await req.form(); question=str(form.get("question","")).strip()
    if not question:raise HTTPException(400,"question is required")
    if SOCIAL_RE.fullmatch(question):
        return {"answer": SOCIAL_REPLY, "sources": []}
    try:history=json.loads(str(form.get("history","[]")))
    except Exception:history=[]
    try:profile=json.loads(str(form.get("profile","{}")))
    except Exception:profile={}
    uploaded=[]
    upload_errors=[]
    for item in form.getlist("files"):
        if not hasattr(item,"filename") or not item.filename:continue
        raw=await item.read()
        if len(raw)>15*1024*1024:continue
        extracted=extract_upload(item.filename,raw,client)[:12000]
        if extracted.startswith("Voice-note transcription failed:"):
            upload_errors.append(item.filename)
        elif extracted.strip():
            uploaded.append({"text":extracted,"source":"Student upload: "+item.filename})
        else:
            upload_errors.append(item.filename)
    if upload_errors and not uploaded:
        return {"answer":"I couldn't read/transcribe "+", ".join(upload_errors)+". Please attach a readable PDF, DOCX, TXT, XLSX, PPTX, or a supported audio recording (WEBM, MP3, WAV, M4A, OGG, FLAC).", "sources":[]}
    rows=uploaded[:4] + search(question,load_docs())[:7]
    ctx="\n\n".join("Source: "+r["source"]+(f", page {r['page']}" if r.get("page") else "")+"\n"+r["text"] for r in rows)
    hist="\n".join(f"{m.get('role')}: {str(m.get('text',''))[:500]}" for m in history[-5:] if isinstance(m,dict))
    prof=json.dumps({k:v for k,v in profile.items() if v not in ("",None)})
    upload_instruction=("The student attached file(s). Read the uploaded-file evidence first and answer the request about its contents. If the prompt is generic (for example, 'look at my attachment'), briefly describe what the attachment contains and ask what they want to know. Do not say you cannot view attachments when extracted content is provided. " if uploaded else "")
    prompt=f"{upload_instruction}Explicit student details: {prof}\nPrevious chat: {hist}\nEvidence:\n{ctx or 'No matching evidence.'}\nQuestion: {question}\nAnswer grounded in the evidence."
    answer=""
    for model in [os.getenv("GROQ_MODEL","llama-3.3-70b-versatile"),"openai/gpt-oss-20b","openai/gpt-oss-120b"]:
        try:
            out=client.chat.completions.create(model=model,messages=[{"role":"system","content":SYS},{"role":"user","content":prompt}],temperature=.1,max_tokens=800)
            answer=out.choices[0].message.content.strip();break
        except Exception:continue
    if not answer:raise HTTPException(502,"Groq answer generation failed; check key, model access, and rate limits.")
    sources=[];seen=set()
    for r in rows:
        label=r["source"]+(f" · page {r['page']}" if r.get("page") else "")
        if label not in seen:seen.add(label);sources.append({"title":label,"url":r.get("url")})
    return {"answer":answer,"sources":sources}
