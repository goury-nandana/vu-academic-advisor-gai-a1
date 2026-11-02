// The ONLY place the page talks to the advisor backend.
// Set NEXT_PUBLIC_ADVISOR_API_URL (a public URL, never a secret) to your backend, e.g. https://my-advisor.onrender.com
// Expected: POST {API}/chat  (multipart/form-data)
//   question: string | history: JSON [{role:"user"|"assistant", text}] | profile: JSON {program, semester, completedCredits, cgpa}
//   files: File[] (documents, images, voice notes)
// Response (JSON): { answer: string, sources?: [{ title: string, url?: string }] }

export type Source = { title: string; url?: string };
export type Profile = { program: string; semester: string; completedCredits: string; cgpa: string };
export type HistoryItem = { role: "user" | "assistant"; text: string };

const API = process.env.NEXT_PUBLIC_ADVISOR_API_URL?.replace(/\/$/, "");

export async function askAdvisor(input: {
  question: string;
  history: HistoryItem[];
  profile: Profile;
  files: File[];
}): Promise<{ answer: string; sources: Source[] }> {
  if (!API) {
    return {
      answer:
        "The advisor service is not connected to this page yet, so I can't answer academic questions here. Please check official university sources for now.",
      sources: [],
    };
  }
  const form = new FormData();
  form.append("question", input.question);
  form.append("history", JSON.stringify(input.history));
  form.append("profile", JSON.stringify(input.profile));
  input.files.forEach((f) => form.append("files", f, f.name));
  const res = await fetch(`${API}/chat`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Advisor API returned ${res.status}`);
  const data = (await res.json()) as { answer?: string; sources?: Source[] };
  return { answer: data.answer ?? "I couldn't find an answer to that.", sources: data.sources ?? [] };
}
