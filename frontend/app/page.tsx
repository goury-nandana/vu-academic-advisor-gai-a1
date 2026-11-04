"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Camera, Check, Copy, FileText, Mic, Square, X, Volume2, VolumeX } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { askAdvisor, type Source, type Visualization } from "./advisor";

type Msg = { id: number; role: "user" | "bot"; text: string; sources?: Source[]; files?: string[]; pipeline?: string[]; model?: string; visualization?: Visualization; followUps?: string[]; fileNotes?: string[] };
type Presence = "off" | "typing" | "recent";

function splitPipeCells(value: string) {
  return value.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function repairFlattenedMarkdownTables(value: string) {
  const lines = value.split("\n");
  for (let dividerLine = 0; dividerLine < lines.length; dividerLine += 1) {
    const divider = /(?:\|\s*:?-{3,}:?\s*){2,}\|?/.exec(lines[dividerLine]);
    if (!divider) continue;

    let headerStart = dividerLine;
    while (headerStart > 0 && lines[headerStart - 1].trim() && lines[headerStart - 1].includes("|")) {
      headerStart -= 1;
    }
    const headerText = lines.slice(headerStart, dividerLine).join(" ") + " " + lines[dividerLine].slice(0, divider.index);
    const headers = headerText.split("|").map((cell) => cell.trim()).filter(Boolean);
    const columnCount = (divider[0].match(/:?-{3,}:?/g) || []).length;
    if (columnCount < 2 || headers.length !== columnCount) continue;

    const bodyParts = [lines[dividerLine].slice(divider.index + divider[0].length)];
    let bodyEnd = dividerLine + 1;
    while (bodyEnd < lines.length && lines[bodyEnd].trim() && lines[bodyEnd].includes("|")) {
      bodyParts.push(lines[bodyEnd]);
      bodyEnd += 1;
    }
    const body = bodyParts.join(" ").trim();
    if (!body.startsWith("|") || !/\|\s*\|\s*\|/.test(body)) continue;

    const flattenedRows = body.split(/\|\s*\|\s*\|/);
    const rows: string[][] = [];
    let valid = true;
    for (let rowIndex = 0; rowIndex < flattenedRows.length; rowIndex += 1) {
      const fragment = flattenedRows[rowIndex].trim();
      if (!fragment) continue;
      const cells = splitPipeCells(fragment);
      if (cells.length === columnCount - 1 && rowIndex > 0) cells.unshift("");
      if (cells.length !== columnCount) { valid = false; break; }
      rows.push(cells);
    }
    if (!valid || rows.length === 0) continue;

    const table = [
      "| " + headers.join(" | ") + " |",
      "| " + headers.map(() => "---").join(" | ") + " |",
      ...rows.map((cells) => "| " + cells.join(" | ") + " |"),
    ].join("\n");
    return [...lines.slice(0, headerStart), table, ...lines.slice(bodyEnd)].join("\n");
  }
  return value;
}

function normalizeAnswerMarkdown(input: string) {
  let markdown = String(input || "")
    .replace(/\r\n?/g, "\n")
    .replace(/\\\*\\\*/g, "**")
    .replace(/\\\*/g, "*")
    .replace(/\\_/g, "_")
    .replace(/\\\|/g, "|")
    .replace(/\\?<br\s*\/?>/gi, " / ")
    .replace(/<br\s*\/?>/gi, " / ")
    .replace(/^\s*Sources consulted\s*:\s*.*$/gim, "")
    .replace(/!\[[^\]]*\]\(\s*https?:\/\/[^)]*\)/gi, "")
    .replace(/\[(?:image|svg)\]\(\s*https?:\/\/[^)]*\)/gi, "")
    .replace(/\[[^\]]*\]\(\s*https?:\/\/[^\s)]*\.(?:png|jpe?g|gif|webp|svg)(?:[?#][^)]*)?\)/gi, "")
    .replace(/^\s*svg\s*$/gim, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  markdown = repairFlattenedMarkdownTables(markdown);
  return markdown;
}
function renderAnswer(text: string) {
  return (
    <div className="answer-markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => {
            if (!href || !/^https?:\/\//i.test(href)) return <span>{children}</span>;
            // Never render model-supplied links as avatar/infographic images.
            if (/\.(?:png|jpe?g|gif|webp|svg)(?:[?#].*)?$/i.test(href)) return null;
            return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>;
          },
          img: () => null,
          table: ({ children }) => (
            <div className="markdown-table-wrap">
              <table>{children}</table>
            </div>
          ),
        }}
      >
        {normalizeAnswerMarkdown(text)}
      </ReactMarkdown>
    </div>
  );
}

function renderVisualization(visual?: Visualization) {
  if (!visual) return null;
  const max = Math.max(1, ...visual.items.map((item) => item.value ?? 0));
  return (
    <section className="visual-card" aria-label={"Visual summary: " + visual.title}>
      <h3>{visual.title}</h3>
      {visual.items.map((item, index) => (
        <div className={"visual-item " + visual.kind} key={item.label + "-" + index}>
          <div className="visual-item-heading">
            <strong>{item.label}</strong>
            {item.valueLabel && <span>{item.valueLabel}</span>}
            {item.value !== undefined && !item.valueLabel && <span>{item.value.toLocaleString()}</span>}
          </div>
          {visual.kind === "bars" && item.value !== undefined && (
            <div className="visual-track" aria-hidden="true">
              <span style={{ width: (Math.max(0, Math.min(100, item.value / max * 100))) + "%" }} />
            </div>
          )}
          {item.detail && <p>{item.detail}</p>}
        </div>
      ))}
      <p className="visual-note">Visual summary generated from the cited response. Verify the underlying source before relying on it.</p>
    </section>
  );
}

const GREETING =
  "Hi! I'm the VU Academic Advisor. Ask me about courses, programmes, prerequisites, credits, semesters and admissions.";
const CHIPS = ["What programmes does VU offer?", "How do I apply to VU?", "What are the attendance requirements?"];
const PROGRAMS = ["Not specified", "B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"];
const SEMESTERS = [
  "Not specified", "1st Semester", "2nd Semester", "3rd Semester", "4th Semester", "5th Semester",
  "6th Semester", "7th Semester", "8th Semester", "9th Semester", "10th Semester",
];
const MAX_MB = 4;
const IDLE_MS = 5000; // green ring / dot disappear after 5 seconds of inactivity

function fmt(s: number) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export default function Home() {
  const [messages, setMessages] = useState<Msg[]>([{ id: 0, role: "bot", text: GREETING }]);
  const [busy, setBusy] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [presence, setPresence] = useState<Presence>("off");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [notice, setNotice] = useState("");
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [speakingId, setSpeakingId] = useState<number | null>(null);
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [program, setProgram] = useState("Not specified");
  const [semester, setSemester] = useState("Not specified");
  const [credits, setCredits] = useState("");
  const [cgpa, setCgpa] = useState("");

  const idRef = useRef(1);
  const endRef = useRef<HTMLDivElement>(null);
  const draftRef = useRef<HTMLTextAreaElement>(null);
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
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
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
    if (ok.length) setAttachments((a) => {
      const combined = [...a, ...ok];
      const total = combined.reduce((sum, file) => sum + file.size, 0);
      if (total > MAX_MB * 1024 * 1024) {
        setNotice(`Attachments exceed the ${MAX_MB} MB total web limit. Remove a file and try again.`);
        return a;
      }
      return combined;
    });
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
    const typed = (text ?? draftRef.current?.value ?? "").trim();
    if ((!typed && attachments.length === 0) || busy || recording) return;
    const question = typed || "Please look at my attachment.";
    const files = attachments;
    const history = messages
      .slice(-8)
      .map((m) => ({ role: m.role === "bot" ? ("assistant" as const) : ("user" as const), text: m.text }));
    setMessages((m) => [...m, { id: idRef.current++, role: "user", text: question, files: files.map((f) => f.name) }]);
    if (draftRef.current) { draftRef.current.value = ""; draftRef.current.style.height = ""; }
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
      setMessages((m) => [...m, { id: idRef.current++, role: "bot", text: r.answer, ...r }]);
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

  function toggleSpeech(id: number, text: string) {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setNotice("Text-to-speech is not supported in this browser.");
      return;
    }
    if (speakingId === id) {
      window.speechSynthesis.cancel();
      setSpeakingId(null);
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => setSpeakingId(null);
    utterance.onerror = () => setSpeakingId(null);
    setSpeakingId(id);
    window.speechSynthesis.speak(utterance);
  }

  async function copyAnswer(id: number, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
    } catch {
      setNotice("Clipboard access is unavailable. Check your browser permissions and try again.");
    }
  }

  function clearChat() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    setSpeakingId(null);
    setCopiedId(null);
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
          <p className="profile-help">Profile details are optional. Blank values remain unknown; the advisor asks one clarification when programme information is needed.</p>
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
                    <div className="answer-text">{renderAnswer(m.text)}</div>
                    {renderVisualization(m.visualization)}
                    {m.fileNotes && m.fileNotes.length > 0 && <div className="file-notes">{m.fileNotes.map((note, i) => <p key={i}>{note}</p>)}</div>}
                    {m.followUps && m.followUps.length > 0 && <div className="follow-ups">{m.followUps.map((followUp) => <button key={followUp} type="button" onClick={() => send(followUp)} disabled={busy}>{followUp}</button>)}</div>}

                    <button type="button" className="speak" onClick={() => void copyAnswer(m.id, m.text)} aria-label={copiedId === m.id ? "Response copied" : "Copy response"} title={copiedId === m.id ? "Copied" : "Copy response"}>
                      {copiedId === m.id ? <Check size={16} /> : <Copy size={16} />}
                    </button>
                    <button type="button" className="speak" onClick={() => toggleSpeech(m.id, m.text)} aria-label={speakingId === m.id ? "Stop speaking" : "Read answer aloud"} title={speakingId === m.id ? "Stop speaking" : "Read answer aloud"}>
                      {speakingId === m.id ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </button>
                    {m.sources && m.sources.length > 0 && (
                      <div className="sources">
                        {m.sources
                          .filter((source, index, all) =>
                            all.findIndex((item) => (item.url || item.title) === (source.url || source.title)) === index
                          )
                          .map((s, i) =>
                            s.url ? (
                              <a key={s.url} href={s.url} target="_blank" rel="noreferrer">{s.title}</a>
                            ) : (
                              <span key={s.title + "-" + i}>{s.title}</span>
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
              ref={draftRef}
              rows={1}
              placeholder={recording ? "Recording… tap the square to stop" : "Ask an academic question…"}
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
            <button type="submit" className="send" aria-label="Send" disabled={busy || recording}>
              <ArrowUp size={22} />
            </button>
            <input ref={fileInput} type="file" hidden multiple
              accept=".pdf,.docx,.txt,.md,.csv,.xlsx,.pptx,image/*,audio/*"
              onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }} />
            <input ref={cameraInput} type="file" hidden accept="image/*" capture="environment"
              onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }} />
          </form>
          <div className="disclaimer">
            Academic information only. This AI is not the Registrar and cannot confirm enrolment, eligibility, credit transfer, grades, fees, deadlines, exceptions or approvals. Rules can change; verify course codes, credits and requirements against the current VU Handbook, Digicampus and the responsible university office. Written confirmation from VU is authoritative.
          </div>
        </div>
      </main>
    </div>
  );
}
