"use client";

import { useState } from "react";
import { ArrowUp, BookOpen, Camera, FileText, GraduationCap, Menu, Mic, Plus, RotateCcw, Sparkles, X } from "lucide-react";

type Message = { role: "assistant" | "user"; text: string };
const suggestions = ["What courses do I have this semester?", "Explain the grading policy", "How can I apply for a minor?", "Show my academic progression"];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", text: "Hello! I’m your VU Academic Advisor. I can help you navigate your curriculum, academic policies, and student procedures using official university sources. What would you like to know?" }]);
  const [draft, setDraft] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [busy, setBusy] = useState(false);

  function send(text = draft) {
    const value = text.trim();
    if (!value || busy) return;
    setMessages(prev => [...prev, { role: "user", text: value }]);
    setDraft("");
    setBusy(true);
    // Frontend preview: connect this UI to the academic retrieval API in the next integration stage.
    window.setTimeout(() => {
      setMessages(prev => [...prev, { role: "assistant", text: "The VU Academic Advisor interface is ready. The academic answer service is being connected; this preview does not yet retrieve official curriculum or policy information." }]);
      setBusy(false);
    }, 450);
  }

  return <main className="shell">
    <aside className={`sidebar ${sidebarOpen ? "" : "closed"}`}>
      <div className="brand"><img src="https://raw.githubusercontent.com/goury-nandana/vu-academic-advisor-gai-a1/main/Logo.png" alt="Vidyashilp University" /><span>VU <b>ACADEMIC</b><br/>ADVISOR</span><button className="icon-button sidebar-toggle" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar"><X size={17}/></button></div>
      <nav className="side-nav"><div className="nav-item active"><GraduationCap size={16}/> Academic Advisor</div><div className="nav-item"><BookOpen size={16}/> Academic Resources</div><div className="nav-item"><FileText size={16}/> My Profile</div></nav><div className="profile"><div className="profile-title">STUDENT PROFILE</div><div className="profile-name">Goury Nandana B.M.S.</div><div className="profile-row"><span>Programme</span><strong>Digital Business</strong></div><div className="profile-row"><span>Semester</span><strong>7</strong></div><div className="stats"><div><span>Credits</span><strong>130</strong></div><div><span>CGPA</span><strong>8.13</strong></div></div></div>
      <div className="sidebar-bottom"><div className="source-label"><BookOpen size={15}/> OFFICIAL VU SOURCES</div><p>Answers are grounded in available university documents and curriculum data.</p><button className="clear-button" onClick={() => setMessages([messages[0]])}><RotateCcw size={15}/> Clear chat</button></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><button className="icon-button" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle sidebar"><Menu size={18}/></button><div className="top-brand"><img src="https://raw.githubusercontent.com/goury-nandana/vu-academic-advisor-gai-a1/main/Logo.png" alt="VU logo"/><span>VU ACADEMIC ADVISOR</span></div><div className="status"><span/> ONLINE · ACADEMIC ASSISTANT</div></header>
      <div className="chat-area"><div className="chat-content">
        {messages.length === 1 && <div className="welcome"><div className="welcome-mark"><GraduationCap size={26}/></div><div className="eyebrow"><Sparkles size={14}/> YOUR UNIVERSITY COMPANION</div><h1>Navigate your<br/><em>academic journey.</em></h1><p>Your personal guide to curriculum, policies, and academic planning at Vidyashilp University.</p><div className="suggestions">{suggestions.map((s,i)=><button key={s} onClick={() => send(s)}><span>0{i+1}</span>{s}<ArrowUp size={14}/></button>)}</div></div>}
        <div className="messages">{messages.map((m,i)=><div className={`message ${m.role}`} key={i}>{m.role === "assistant" && <div className="avatar"><GraduationCap size={17}/></div>}<div className="bubble"><div className="message-label">{m.role === "assistant" ? "VU ADVISOR" : "YOU"}</div>{m.text}</div></div>)}</div>
      </div></div>
      <footer className="composer-wrap"><form className="composer" onSubmit={e => {e.preventDefault();send();}}><div className="composer-tools"><button type="button" className="tool" aria-label="Add file" title="Attach document"><Plus size={18}/></button><button type="button" className="tool" aria-label="Image upload" title="Attach image"><Camera size={17}/></button><button type="button" className="tool" aria-label="Document upload" title="Attach document"><FileText size={17}/></button></div><textarea value={draft} onChange={e => setDraft(e.target.value)} onKeyDown={e => {if(e.key === "Enter" && !e.shiftKey){e.preventDefault();send();}}} placeholder="Ask anything about your academics..." rows={1}/><button type="button" className="tool mic" aria-label="Voice input" title="Voice input"><Mic size={17}/></button><button type="submit" className="send" aria-label="Send" disabled={!draft.trim() || busy}><ArrowUp size={18}/></button></form><div className="disclaimer">AI can make mistakes. Verify important academic decisions with official VU sources.</div></footer>
    </section>
  </main>;
}