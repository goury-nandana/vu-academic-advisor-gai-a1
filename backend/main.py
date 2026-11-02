"""FastAPI academic advisor service deployed as a Vercel Service."""
from __future__ import annotations
import io, os, re, urllib.request, urllib.parse, zipfile
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Request
from groq import Groq
from pypdf import PdfReader

app=FastAPI(title="VU Academic Advisor API")
RAW="https://raw.githubusercontent.com/goury-nandana/vu-academic-advisor-gai-a2/main/"
GH="https://github.com/goury-nandana/vu-academic-advisor-gai-a2/blob/main/"
def get(path):
    req=urllib.request.Request(RAW+urllib.parse.quote(path),headers={"User-Agent":"VU-Academic-Advisor"})
    with urllib.request.urlopen(req,timeout=25) as r:return r.read()
def pdf(path):
    try:
        reader=PdfReader(io.BytesIO(get(path)))
        return [{"text":re.sub(r"\\s+"," ",p.extract_text() or "").strip(),"source":path,"page":i+1,"url":GH+urllib.parse.quote(path)} for i,p in enumerate(reader.pages) if (p.extract_text() or "").strip()]
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
SYS="""You are the AI Academic Advisor for Vidyashilp University, Bengaluru. Respond concisely and only from retrieved evidence. Never invent course codes, policy thresholds, eligibility, credits, or student-record facts. Never claim access to private university records; use profile only if explicitly supplied. For B.Tech minor questions, published Data Science and AI/ML tracks list Economics, Marketing, Psychology, Finance, Design, and Law; do not mix programmes' lists. If sources are insufficient, state that and suggest Digicampus or relevant office. Fees: Accounts; professors/HODs: department office; records/exams: Registrar. Specific course codes: advise Digicampus for details."""
@app.get("/api")
@app.get("/api/")
async def health():return {"status":"ok","service":"VU Academic Advisor API"}
@app.post("/api/chat")
async def chat(req:Request):
    key=os.getenv("GROQ_API_KEY","").strip()
    if not key:raise HTTPException(503,"Set GROQ_API_KEY in Vercel backend environment variables.")
    form=await req.form(); question=str(form.get("question","")).strip()
    if not question:raise HTTPException(400,"question is required")
    try:history=json.loads(str(form.get("history","[]")))
    except Exception:history=[]
    try:profile=json.loads(str(form.get("profile","{}")))
    except Exception:profile={}
    rows=search(question,load_docs())
    ctx="\n\n".join("Source: "+r["source"]+(f", page {r['page']}" if r.get("page") else "")+"\n"+r["text"] for r in rows)
    hist="\n".join(f"{m.get('role')}: {str(m.get('text',''))[:500]}" for m in history[-5:] if isinstance(m,dict))
    prof=json.dumps({k:v for k,v in profile.items() if v not in ("",None)})
    prompt=f"Explicit student details: {prof}\nPrevious chat: {hist}\nEvidence:\n{ctx or 'No matching evidence.'}\nQuestion: {question}\nAnswer grounded in the evidence."
    client=Groq(api_key=key);answer=""
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
