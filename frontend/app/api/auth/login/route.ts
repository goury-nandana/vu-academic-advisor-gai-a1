import { NextResponse } from "next/server";
import { createSessionToken, demoSessionCookieName, demoSessionTtlSeconds, getStudentById, verifyDemoCredentials } from "../../../../lib/demo-auth";

export const runtime = "nodejs";
export async function POST(request: Request) {
  const origin = request.headers.get("origin");
  const host = request.headers.get("host");
  if (origin && host) {
    try { if (new URL(origin).host !== host) return NextResponse.json({ error: "Request origin rejected." }, { status: 403 }); }
    catch { return NextResponse.json({ error: "Request origin rejected." }, { status: 403 }); }
  }
  let body: { username?: unknown; password?: unknown };
  try { body = await request.json(); } catch { return NextResponse.json({ error: "Enter a username and password." }, { status: 400 }); }
  const username = typeof body.username === "string" ? body.username.slice(0, 80) : "";
  const password = typeof body.password === "string" ? body.password : "";
  if (!username.trim() || !password || password.length > 128) return NextResponse.json({ error: "Enter a valid username and password." }, { status: 400 });
  const profileId = await verifyDemoCredentials(username, password);
  if (!profileId) return NextResponse.json({ error: "Username or password is incorrect." }, { status: 401 });
  const student = getStudentById(profileId);
  if (!student) return NextResponse.json({ error: "Synthetic account record is unavailable." }, { status: 500 });
  let token: string;
  try { token = createSessionToken(profileId); } catch { return NextResponse.json({ error: "Session signing is not configured. Set SESSION_SECRET in Vercel environment variables." }, { status: 503 }); }
  const response = NextResponse.json({ student: { id: student.id, username: student.username, name: student.name, synthetic_student_id: student.synthetic_student_id, programme: student.programme, admission_batch: student.admission_batch, current_semester: student.current_semester, academic_status: student.academic_status, synthetic_cgpa: student.synthetic_cgpa } });
  response.cookies.set(demoSessionCookieName, token, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "strict", path: "/", maxAge: demoSessionTtlSeconds });
  return response;
}