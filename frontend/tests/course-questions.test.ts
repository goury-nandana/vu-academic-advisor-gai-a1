import { beforeAll, describe, expect, it } from "vitest";

let POST: (request: Request) => Promise<Response>;
let auth: typeof import("../lib/demo-auth");

beforeAll(async () => {
  process.env.SESSION_SECRET = "test-secret-".padEnd(40, "x");
  delete process.env.GROQ_API_KEY;
  auth = await import("../lib/demo-auth");
  POST = (await import("../app/api/chat/route")).POST;
});

async function ask(profileId: string, question: string, history: unknown[] = []) {
  const form = new FormData();
  form.append("question", question);
  form.append("history", JSON.stringify(history));
  const cookie = auth.demoSessionCookieName + "=" + auth.createSessionToken(profileId);
  const response = await POST(new Request("http://localhost/api/chat", { method: "POST", body: form, headers: { cookie } }));
  const body = await response.json();
  return { status: response.status, answer: String(body.answer ?? body.error ?? ""), model: String(body.model ?? "") };
}

describe("L-T-P question about a course title", () => {
  it.each(["SYN-101", "SYN-106"])("is answered from the structured records for %s (not refused, not 'not included')", async (id) => {
    const r = await ask(id, "l-t-p structure of calculus");
    expect(r.status).toBe(200);
    expect(r.answer).not.toMatch(/limited to B\.Tech academic advising/i);
    expect(r.answer).not.toMatch(/do not include the detailed/i);
    // Values come from the workbook rows: MATH201 Calculus 2-1-0 and MATH208 Multivariate Calculus 3-1-0.
    expect(r.answer).toContain("MATH201");
    expect(r.answer).toContain("MATH208");
    expect(r.answer).toMatch(/2-1-0/);
    expect(r.answer).toMatch(/3-1-0/);
    // Each row names its own course so MATH208 is not mislabelled as plain "Calculus".
    expect(r.answer).toMatch(/MATH208 Multivariate Calculus/);
    expect(r.answer).toMatch(/MATH201 Calculus/);
  });
});

describe("minor vs specialisation", () => {
  it.each([
    "difference between specialisation and minor",
    "difference between specialisationa nd minor",
  ])("%s is labelled as a general explanation, not an official definition, and does not ask for a batch", async (q) => {
    const r = await ask("SYN-101", q);
    expect(r.status).toBe(200);
    expect(r.answer).toMatch(/not an official VU definition/i);
    expect(r.answer).not.toMatch(/Which admission year/i);
    expect(r.answer).not.toMatch(/^At VU,/);
  });

  it("uses the signed-in admission batch for minor options instead of asking for it", async () => {
    const r = await ask("SYN-106", "what minors can i take");
    expect(r.answer).not.toMatch(/Which admission year/i);
  });
});
