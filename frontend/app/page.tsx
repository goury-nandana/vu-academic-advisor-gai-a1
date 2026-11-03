"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Camera, FileText, Mic, Square, X } from "lucide-react";
import { askAdvisor, type Source } from "./advisor";

type Msg = { id: number; role: "user" | "bot"; text: string; sources?: Source[]; files?: string[] };
type Presence = "off" | "typing" | "recent";

const GREETING =
  "Hi! I'm the VU Academic Advisor. Ask me about courses, programmes, prerequisites, credits, semesters and admissions.";
const CHIPS = ["What programmes does VU offer?", "How do I apply to VU?", "What are the attendance requirements?"];
const PROGRAMS = ["Not specified", "B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"];
const SEMESTERS = [
  "Not specified", "1st Semester", "2nd Semester", "3rd Semester", "4th Semester", "5th Semester",
  "6th Semester", "7th Semester", "8th Semester", "9th Semester", "10th Semester",
];
const MAX_MB = 15;
const IDLE_MS = 5000; // green ring / dot disappear after 5 seconds of inactivity

function fmt(s: number) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

function renderInline(text: string) {
  const tokens = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|\x60[^\x60]+\x60|\[[^\]]+\]\([^)]+\)|<https?:\/\/[^>]+>|<br\s*\/?\s*>)/gi);
  return tokens.map((token, index) => {
    if (token.startsWith("**") && token.endsWith("**")) return <strong key={index}>{token.slice(2, -2)}</strong>;
    if (token.startsWith("*") && token.endsWith("*")) return <em key={index}>{token.slice(1, -1)}</em>;
    if (token.startsWith("\x60") && token.endsWith("\x60")) return <code key={index}>{token.slice(1, -1)}</code>;
    const link = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
    if (link) return <a key={index} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a>;
    const angleUrl = token.match(/^<(https?:\/\/[^>]+)>$/);
    if (angleUrl) return <a key={index} href={angleUrl[1]} target="_blank" rel="noreferrer">{angleUrl[1]}</a>;
    if (/^<br\s*\/?\s*>$/i.test(token)) return <br key={index} />;
    return <span key={index}>{token}</span>;
  });
}

function splitTableRow(line: string) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function AnswerText({ text }: { text: string }) {
  const normalized = text.replace(/\\([*_])/g, "$1").replace(/\|\s+\|/g, "|\n|");
  const lines = normalized.split("\n");
  const rendered: React.ReactNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    const heading = line.match(/^#{1,3}\s+(.+)$/);
    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    const separator = index + 1 < lines.length && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[index + 1]);
    const tableStart = line.includes("|") && separator;

    if (!line.trim()) {
      rendered.push(<div className="md-gap" key={index} />);
      index++;
      continue;
    }
    if (tableStart) {
      const headers = splitTableRow(line);
      const rows: string[][] = [];
      index += 2;
      while (index < lines.length && lines[index].trim() && lines[index].includes("|")) {
        rows.push(splitTableRow(lines[index]));
        index++;
      }
      rendered.push(
        <div className="md-table-wrap" key={"table-" + index}>
          <table className="md-table">
            <thead><tr>{headers.map((cell, col) => <th key={col}>{renderInline(cell)}</th>)}</tr></thead>
            <tbody>{rows.map((row, rowIndex) => <tr key={rowIndex}>{headers.map((_, col) => <td key={col}>{renderInline(row[col] ?? "")}</td>)}</tr>)}</tbody>
          </table>
        </div>
      );
      continue;
    }
    if (heading) rendered.push(<div className="md-heading" key={index}>{renderInline(heading[1])}</div>);
    else if (bullet) rendered.push(<div className="md-list" key={index}><span aria-hidden="true">•</span><div>{renderInline(bullet[1])}</div></div>);
    else if (ordered) rendered.push(<div className="md-list" key={index}><span aria-hidden="true">{line.match(/^\s*(\d+)/)?.[1]}.</span><div>{renderInline(ordered[1])}</div></div>);
    else rendered.push(<div className="md-line" key={index}>{renderInline(line)}</div>);
    index++;
  }

  return <div className="answer-md">{rendered}</div>;
}

export default function Home() {
  const [messages, setMessages] = useState<Msg[]>([{ id: 0, role: "bot", text: GREETING }]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [presence, setPresence] = useState<Presence>("off");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [notice, setNotice] = useState("");
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [program, setProgram] = useState("Not specified");
  const [semester, setSemester] = useState("Not specified");
  const [credits, setCredits] = useState("");
  const [cgpa, setCgpa] = useState("");

  const idRef = useRef(1);
  const endRef = useRef<HTMLDivElement>(null);
  const idleTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const recRef = useRef<MediaRecorder | null>(null);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const cameraInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (window.innerWidth < 860) setSidebarOpen(false);
    return () => {
      if (idleTimer.current) clearTimeout(idleTimer.current);
      if (tickRef.current) clearInterval(tickRef.current);
    };
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  function startTyping() {
    if (idleTimer.current) clearTimeout(idleTimer.current);
    setPresence("typing");
  }
  function finishTyping() {
    setPresence("recent");
    if (idleTimer.current) clearTimeout(idleTimer.current);
    idleTimer.current = setTimeout(() => setPresence("off"), IDLE_MS);
  }

  function addFiles(list: FileList | null) {
    if (!list) return;
    const ok: File[] = [];
    Array.from(list).forEach((f) => {
      if (f.size > MAX_MB * 1024 * 1024) setNotice(`${f.name} is larger than ${MAX_MB} MB and was not attached.`);
      else ok.push(f);
    });
    if (ok.length) setAttachments((a) => [...a, ...ok]);
  }

  async function toggleMic() {
    if (recording) {
      recRef.current?.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      const chunks: Blob[] = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        if (tickRef.current) clearInterval(tickRef.current);
        const type = rec.mimeType || "audio/webm";
        const ext = type.includes("mp4") ? "m4a" : type.includes("ogg") ? "ogg" : "webm";
        setAttachments((a) => [...a, new File(chunks, `voice-note.${ext}`, { type })]);
        setRecording(false);
      };
      rec.start();
      recRef.current = rec;
      setSeconds(0);
      setRecording(true);
      tickRef.current = setInterval(() => setSeconds((s) => s + 1), 1000);
    } catch {
      setNotice("Allow microphone access in your browser to send a voice note.");
    }
  }

  async function send(text?: string) {
    const typed = (text ?? draft).trim();
    if ((!typed && attachments.length === 0) || busy || recording) return;
    const question = typed || "Please look at my attachment.";
    const files = attachments;
    const history = messages
      .slice(-8)
      .map((m) => ({ role: m.role === "bot" ? ("assistant" as const) : ("user" as const), text: m.text }));
    setMessages((m) => [...m, { id: idRef.current++, role: "user", text: question, files: files.map((f) => f.name) }]);
    setDraft("");
    setAttachments([]);
    setNotice("");
    setBusy(true);
    startTyping();
    try {
      const r = await askAdvisor({
        question,
        history,
        profile: { program, semester, completedCredits: credits, cgpa },
        files,
      });
      setMessages((m) => [...m, { id: idRef.current++, role: "bot", text: r.answer, sources: r.sources }]);
    } catch {
      setMessages((m) => [
        ...m,
        { id: idRef.current++, role: "bot", text: "I couldn't reach the advisor right now. Please try again." },
      ]);
    } finally {
      setBusy(false);
      finishTyping();
    }
  }

  function clearChat() {
    if (idleTimer.current) clearTimeout(idleTimer.current);
    setPresence("off");
    setMessages([{ id: idRef.current++, role: "bot", text: GREETING }]);
    setAttachments([]);
    setNotice("");
  }

  const lastBotId = [...messages].reverse().find((m) => m.role === "bot")?.id;
  const live = presence !== "off";

  return (
    <div className="app">
      <div className="bg" aria-hidden="true" />

      <aside className={`sidebar ${sidebarOpen ? "" : "closed"}`}>
        <button
          className="toggle"
          onClick={() => setSidebarOpen((o) => !o)}
          aria-label={sidebarOpen ? "Hide side panel" : "Show side panel"}
          aria-expanded={sidebarOpen}
        >
          ‹
        </button>
        <div className="side-body">
          <img className="logo" src="/logo.png" alt="Vidyashilp University" />
          <h2>Student profile</h2>
          <label className="field">
            <span>Program</span>
            <select value={program} onChange={(e) => setProgram(e.target.value)}>
              {PROGRAMS.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Current Semester</span>
            <select value={semester} onChange={(e) => setSemester(e.target.value)}>
              {SEMESTERS.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </label>
          <div className="row2">
            <label className="field">
              <span>Completed Credits</span>
              <input
                type="number" inputMode="numeric" min={0} max={400} placeholder="Optional"
                value={credits} onChange={(e) => setCredits(e.target.value)}
              />
            </label>
            <label className="field">
              <span>CGPA</span>
              <input
                type="number" inputMode="decimal" min={0} max={10} step={0.1} placeholder="Optional"
                value={cgpa} onChange={(e) => setCgpa(e.target.value)}
              />
            </label>
          </div>
          <button className="clear" onClick={clearChat}>Clear Chat</button>
        </div>
      </aside>

      <main className="main">
        <div className="pill-wrap">
          <div className="pill">
            <span className="av-lg">
              <span className={`ring ${live ? "on" : ""}`} />
              <span className="av-in"><img src="/symbol.jpg" alt="VU Academic Advisor" /></span>
            </span>
            <span className="pill-title">VU ACADEMIC ADVISOR</span>
          </div>
        </div>

        <div className="chat" role="log" aria-live="polite">
          <div className="chat-inner">
            {messages.map((m) =>
              m.role === "user" ? (
                <div className="row user" key={m.id}>
                  <div className="bubble user">
                    {m.text}
                    {m.files && m.files.length > 0 && <div className="files">📎 {m.files.join(", ")}</div>}
                  </div>
                </div>
              ) : (
                <div className="row bot" key={m.id}>
                  <span className="av-sm">
                    <img src="/symbol.jpg" alt="" />
                    <span className={`dot ${live && m.id === lastBotId ? "on" : ""}`} />
                  </span>
                  <div className="bubble bot">
                    <AnswerText text={m.text} />
                    {m.sources && m.sources.length > 0 && (
                      <div className="sources">
                        {m.sources.map((s, i) =>
                          s.url ? (
                            <a key={i} href={s.url} target="_blank" rel="noreferrer">{s.title}</a>
                          ) : (
                            <span key={i}>{s.title}</span>
                          ),
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ),
            )}
            {busy && (
              <div className="row bot">
                <span className="av-sm"><img src="/symbol.jpg" alt="" /><span className="dot on" /></span>
                <div className="bubble bot typing" aria-label="Advisor is typing"><i /><i /><i /></div>
              </div>
            )}
            <div ref={endRef} />
          </div>
        </div>

        <div className="dock">
          <div className="chips">
            {CHIPS.map((c) => (
              <button key={c} className="chip" onClick={() => send(c)} disabled={busy}>{c}</button>
            ))}
          </div>
          {attachments.length > 0 && (
            <div className="attached">
              {attachments.map((f, i) => (
                <span key={i} className="file-chip">
                  {f.name}
                  <button aria-label={`Remove ${f.name}`} onClick={() => setAttachments((a) => a.filter((_, j) => j !== i))}>
                    <X size={13} />
                  </button>
                </span>
              ))}
            </div>
          )}
          {notice && <div className="notice">{notice}</div>}
          <form className="composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
            <textarea
              rows={1}
              value={draft}
              placeholder={recording ? "Recording… tap the square to stop" : "Ask an academic question…"}
              onChange={(e) => {
                setDraft(e.target.value);
                e.currentTarget.style.height = "auto";
                e.currentTarget.style.height = Math.min(e.currentTarget.scrollHeight, 120) + "px";
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
              }}
            />
            <button type="button" className={`tool ${recording ? "rec" : ""}`} onClick={toggleMic}
              aria-label={recording ? "Stop recording" : "Record a voice note"}>
              {recording ? <><Square size={16} fill="currentColor" /><b>{fmt(seconds)}</b></> : <Mic size={22} />}
            </button>
            <button type="button" className="tool" onClick={() => cameraInput.current?.click()} aria-label="Take or attach a photo">
              <Camera size={22} />
            </button>
            <button type="button" className="tool" onClick={() => fileInput.current?.click()} aria-label="Attach a file">
              <FileText size={22} />
            </button>
            <button type="submit" className="send" aria-label="Send" disabled={busy || recording || (!draft.trim() && attachments.length === 0)}>
              <ArrowUp size={22} />
            </button>
            <input ref={fileInput} type="file" hidden multiple
              accept=".pdf,.docx,.txt,.md,.csv,.xlsx,.pptx,image/*,audio/*"
              onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }} />
            <input ref={cameraInput} type="file" hidden accept="image/*" capture="environment"
              onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }} />
          </form>
          <div className="disclaimer">
            This is an AI and can make mistakes. Please verify important details with official university sources.
          </div>
        </div>
      </main>
    </div>
  );
}
