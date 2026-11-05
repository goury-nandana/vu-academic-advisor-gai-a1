import { createHmac, pbkdf2 as pbkdf2Callback, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";
import accountData from "../data/synthetic-account-credentials.json";
import studentData from "../data/synthetic-students.json";

const pbkdf2 = promisify(pbkdf2Callback);
const SESSION_COOKIE = "vu_demo_session";
const SESSION_TTL_SECONDS = 8 * 60 * 60;
type Account = { username: string; profileId: string; salt: string; hash: string };
export type SyntheticStudentProfile = { id: string; username: string; name: string; synthetic_student_id: string; programme: string; admission_batch: string; current_semester: number | null; academic_status: string; synthetic_cgpa: number | null; academic_records: Array<{ course_code: string; course_title: string; semester: number; credits: number; grade: string | null; status: string; attempts?: Array<{ semester: number; grade: string; status: string }> }>; completed_course_codes: string[]; failed_course_codes: string[]; unknown_course_codes: string[]; declared_minor: string };
const accounts = accountData.accounts as Account[];
const students = studentData.students as unknown as SyntheticStudentProfile[];

function sessionSecret(): string {
  // SESSION_SECRET is preferred. GROQ_API_KEY is a server-only fallback so an
  // existing deployment can function without exposing a signing key to clients.
  return process.env.SESSION_SECRET?.trim() || process.env.GROQ_API_KEY?.trim() || "";
}
function signature(payload: string): string {
  const secret = sessionSecret();
  if (!secret) throw new Error("Authentication requires SESSION_SECRET or GROQ_API_KEY.");
  return createHmac("sha256", secret).update(payload).digest("base64url");
}
export function createSessionToken(profileId: string): string {
  const payload = Buffer.from(JSON.stringify({ profileId, exp: Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS })).toString("base64url");
  return payload + "." + signature(payload);
}
export async function verifyDemoCredentials(usernameInput: string, passwordInput: string): Promise<string | undefined> {
  const username = usernameInput.trim().toLowerCase();
  const account = accounts.find((item) => item.username.toLowerCase() === username);
  if (!account || !passwordInput || passwordInput.length > 128) return undefined;
  const actual = await pbkdf2(passwordInput, Buffer.from(account.salt, "hex"), accountData.iterations, 32, "sha256");
  const expected = Buffer.from(account.hash, "hex");
  if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) return undefined;
  return account.profileId;
}
export function getStudentById(profileId: string): SyntheticStudentProfile | undefined {
  return students.find((student) => student.id === profileId);
}
export function getAuthenticatedStudent(request: Request): SyntheticStudentProfile | undefined {
  const cookieHeader = request.headers.get("cookie") || "";
  const token = cookieHeader.split(";").map((part) => part.trim()).find((part) => part.startsWith(SESSION_COOKIE + "="))?.slice(SESSION_COOKIE.length + 1);
  if (!token) return undefined;
  const [payload, providedSignature] = token.split(".");
  if (!payload || !providedSignature) return undefined;
  let expectedSignature: string;
  try { expectedSignature = signature(payload); } catch { return undefined; }
  const provided = Buffer.from(providedSignature);
  const expected = Buffer.from(expectedSignature);
  if (provided.length !== expected.length || !timingSafeEqual(provided, expected)) return undefined;
  try {
    const decoded = JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as { profileId?: string; exp?: number };
    if (typeof decoded.profileId !== "string" || typeof decoded.exp !== "number" || decoded.exp <= Math.floor(Date.now() / 1000)) return undefined;
    return getStudentById(decoded.profileId);
  } catch { return undefined; }
}
export const demoSessionCookieName = SESSION_COOKIE;
export const demoSessionTtlSeconds = SESSION_TTL_SECONDS;
