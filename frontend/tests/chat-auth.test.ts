import { beforeAll, describe, expect, it, vi } from "vitest";

const SECRET = "test-secret-".padEnd(40, "x");
let POST: (request: Request) => Promise<Response>;
let auth: typeof import("../lib/demo-auth");

beforeAll(async () => {
  process.env.SESSION_SECRET = SECRET;
  delete process.env.GROQ_API_KEY;
  auth = await import("../lib/demo-auth");
  POST = (await import("../app/api/chat/route")).POST;
});

function chatRequest(question: string, opts: { profileId?: string; expected?: string } = {}) {
  const form = new FormData();
  form.append("question", question);
  const headers: Record<string, string> = {};
  if (opts.profileId) headers.cookie = auth.demoSessionCookieName + "=" + auth.createSessionToken(opts.profileId);
  if (opts.expected) headers["x-expected-profile-id"] = opts.expected;
  return new Request("http://localhost/api/chat", { method: "POST", body: form, headers });
}

describe("chat API authentication", () => {
  it("rejects unauthenticated calls with 401 BEFORE parsing the multipart body", async () => {
    const request = chatRequest("who am i");
    const spy = vi.spyOn(request, "formData");
    const response = await POST(request);
    expect(response.status).toBe(401);
    expect(spy).not.toHaveBeenCalled();
  });

  it("rejects a forged or tampered cookie", async () => {
    const token = auth.createSessionToken("SYN-106");
    const forged = token.replace(/.$/, (c) => (c === "A" ? "B" : "A"));
    const form = new FormData();
    form.append("question", "who am i");
    const response = await POST(new Request("http://localhost/api/chat", { method: "POST", body: form, headers: { cookie: auth.demoSessionCookieName + "=" + forged } }));
    expect(response.status).toBe(401);
  });

  it("answers as the session student, not anyone named in the request", async () => {
    const isha = await (await POST(chatRequest("who am i", { profileId: "SYN-106" }))).json();
    expect(isha.answer).toContain("Isha Kulkarni");
    const tara = await (await POST(chatRequest("who am i", { profileId: "SYN-110" }))).json();
    expect(tara.answer).toContain("Tara Desai");
    expect(tara.answer).not.toContain("Isha");
  });

  it("returns 409 when another tab switched accounts (expected profile mismatch)", async () => {
    const response = await POST(chatRequest("who am i", { profileId: "SYN-110", expected: "SYN-106" }));
    expect(response.status).toBe(409);
    expect((await response.json()).code).toBe("SESSION_CHANGED");
  });

  it("ignores a client-supplied profile form field", async () => {
    const form = new FormData();
    form.append("question", "who am i");
    form.append("profile", JSON.stringify({ syntheticStudentId: "SYN-110", studentName: "Tara Desai" }));
    const cookie = auth.demoSessionCookieName + "=" + auth.createSessionToken("SYN-106");
    const body = await (await POST(new Request("http://localhost/api/chat", { method: "POST", body: form, headers: { cookie } }))).json();
    expect(body.answer).toContain("Isha Kulkarni");
  });
});

describe("session secret", () => {
  it("does not fall back to GROQ_API_KEY", async () => {
    const saved = process.env.SESSION_SECRET;
    delete process.env.SESSION_SECRET;
    process.env.GROQ_API_KEY = "groq-key-should-never-sign-sessions";
    expect(() => auth.createSessionToken("SYN-106")).toThrow();
    process.env.SESSION_SECRET = saved;
    delete process.env.GROQ_API_KEY;
  });
});
