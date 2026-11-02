"""Vercel serverless academic advisor API. Groq key is server-side only."""
from __future__ import annotations
import io, json, os, re, urllib.request, zipfile
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Request
from groq import Groq
from pypdf import PdfReader

app = FastAPI(title="VU Academic Advisor API")
RAW = "https://raw.githubusercontent.com/goury-nandana/vu-academic-advisor-gai-a2/main/"
GH = "https://github.com/goury-nandana/vu-academic-advisor-gai-a2/blob/main/"
def download(path):
    req=urllib.request.Request(RAW+urllib.parse.quote(path), headers={"User-Agent":"VU-Academic-Advisor"})
    with urllib.request.urlopen(req, timeout=25) as r: return r.read()

def pdf_text(path):
    try:
        reader=PdfReader(io.BytesIO(download(path)))
        return [{"text": re.sub(r"\\s+"," ",p.extract_text() or "").strip(),
                 "source":path, "page":i+1, "url":GH+urllib.parse.quote(path)}
                for i,p in enumerate(reader.pages) if (p.extract_text() or "").strip()]
    except Exception: return []

@lru_cache(maxsize=1)
def knowledge():
    docs=pdf_text("4. Student Handbook Aug 2026.pdf")+pdf_text("SOP STUDENT 17082026 - Final.pdf")
    try:
        text=download("Course_Plans.txt").decode("utf-8",errors="ignore")
        docs += [{"text":text,"source":"Course_Plans.txt","url":GH+"Course_Plans.txt"}]
    except Exception: pass
    try:
        archive=zipfile.ZipFile(io.BytesIO(download("VU_Semester_Data_Split.zip")))
        for fn in archive.namelist():
            if not fn.lower().endswith(".xlsx"): continue
            from openpyxl import load_workbook
            wb=load_workbook(io.BytesIO(archive.read(fn)),read_only=True,data_only=True)
            ws=wb.active
            for row in ws.iter_rows(min_row=3,values_only=True):
                line=" | ".join(str(v) for v in row if v is not None)
                if line: docs.append({"text":line,"source":fn,"url":GH+"VU_Semester_Data_Split.zip"})
            wb.close()
    except Exception: pass
    # Chunk source passages into retrieval-sized pieces.
    out=[]
    for d in docs:
        words=d["text"].split()
        for i in range(0,len(words),180):
            piece=" ".join(words[max(0,i-30):i+180])
            if piece: out.append({**d,"text":piece})
    return out

STOP=set("the a an is are am i me my to of in on for and or can could would should do does did be it this that with from at as what which how where when why you your".split())
def tokens(s): return [w for w in re.findall(r"[a-z0-9]+",s.lower()) if w not in STOP]
def retrieve(q, docs, k=7):
    qt=set(tokens(q))
    if not qt:return []
    scored=[]
    for d in docs:
        dt=tokens(d["text"]); overlap=sum(1 for w in qt if w in dt)
        if overlap: scored.append((overlap/(len(set(dt))**0.45),d))
    scored.sort(key=lambda x:x[0],reverse=True)
    return [d for _,d in scored[:k]]

SYSTEM="""You are the AI Academic Advisor for Vidyashilp University, Bengaluru.
Answer university academic questions clearly and briefly using only the retrieved source evidence.
Never invent course codes, policy thresholds, eligibility, credits, semesters, student records or profile facts.
For B.Tech minors, the two official tracks (Data Science and AI & ML) publish Economics, Marketing, Psychology, Finance, Design and Law. Never mix minor lists across programmes.
You have no access to university records. Use profile details only if explicitly supplied in the request.
For unsupported facts, say the sources do not establish the answer and direct the student to the relevant office or Digicampus.
For fees contact Accounts; specific professors/HODs contact department office; records/examinations contact Registrar.
If student asks about course codes, refer to Digicampus for further detail. Avoid source placeholders."""

@app.get("/")
async def health(): return {"status":"ok","service":"VU Academic Advisor API"}

@app.post("/chat")
async def chat(request: Request):
    key=os.getenv("GROQ_API_KEY","").strip()
    if not key: raise HTTPException(503,"GROQ_API_KEY is not configured in Vercel.")
    form=await request.form()
    question=str(form.get("question","")).strip()
    if not question: raise HTTPException(400,"question is required")
    try: history=json.loads(str(form.get("history","[]")))
    except Exception: history=[]
    try: profile=json.loads(str(form.get("profile","{}")))
    except Exception: profile={}
    docs=knowledge()
    found=retrieve(question,docs)
    context="\\n\\n".join(f"Source: {d['source']}"+(f", page {d['page']}" if d.get("page") else "")+"\\n"+d["text"] for d in found)
    recent="\\n".join(f"{m.get('role','')}: {str(m.get('text',''))[:700]}" for m in history[-6:] if isinstance(m,dict))
    prof="Student details explicitly supplied: "+json.dumps({k:v for k,v in profile.items() if v not in ("",None)},ensure_ascii=False)
    prompt=f"{prof}\\nConversation: {recent}\\nRetrieved evidence:\\n{context or 'No relevant passages found.'}\\n\\nStudent question: {question}\\nAnswer grounded in evidence. If evidence is insufficient, say so."
    client=Groq(api_key=key)
    answer=None
    for model in [os.getenv("GROQ_MODEL","llama-3.3-70b-versatile"),"openai/gpt-oss-20b","openai/gpt-oss-120b"]:
        try:
            res=client.chat.completions.create(model=model,messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],temperature=0.1,max_tokens=800)
            answer=res.choices[0].message.content.strip(); break
        except Exception: continue
    if answer is None: raise HTTPException(502,"Groq could not generate an answer; check model availability and API limits.")
    seen=set(); sources=[]
    for d in found:
        title=d["source"]+(f" · p. {d['page']}" if d.get("page") else "")
        if title not in seen: seen.add(title); sources.append({"title":title,"url":d.get("url")})
    return {"answer":answer,"sources":sources}
