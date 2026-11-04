// Frontend calls the Python API through the same Vercel origin.
// Groq credentials remain server-side in the backend service environment.
export type Source = { title: string; url?: string };
export type Profile = { program: string; semester: string; completedCredits: string; cgpa: string };
export type HistoryItem = { role: "user" | "assistant"; text: string };
const API = "/api";

export async function askAdvisor(input: {
  question: string;
  history: HistoryItem[];
  profile: Profile;
  files: File[];
}): Promise<{ answer: string; sources: Source[] }> {
  const form = new FormData();
  form.append("question", input.question);
  form.append("history", JSON.stringify(input.history));
  form.append("profile", JSON.stringify(input.profile));
  input.files.forEach((f) => form.append("files", f, f.name));
  const res = await fetch(`${API}/chat`, { method: "POST", body: form });
  if (!res.ok) {
    let detail = `Advisor API returned ${res.status}`;
    try {
      const error = (await res.json()) as { detail?: string };
      if (error.detail) detail = error.detail;
    } catch {}
    throw new Error(detail);
  }
  const data = (await res.json()) as { answer?: string; sources?: Source[] };
  return {
    answer: data.answer ?? "I couldn't find an answer to that.",
    sources: data.sources ?? [],
  };
}
