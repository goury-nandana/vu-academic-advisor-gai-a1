import { NextResponse } from "next/server";
import { getAuthenticatedStudent } from "../../../lib/demo-auth";
import { createSyntheticMarksheetPdf } from "../../../lib/synthetic-marksheet-pdf";

export const runtime = "nodejs";
export async function GET(request: Request) {
  const student = getAuthenticatedStudent(request);
  if (!student) return NextResponse.json({ error: "Sign in to a synthetic student account first." }, { status: 401, headers: { "Cache-Control": "no-store" } });
  const url = new URL(request.url);
  const rawSemester = url.searchParams.get("semester");
  const semester = rawSemester === null ? undefined : Number(rawSemester);
  if (rawSemester !== null && (!Number.isInteger(semester) || Number(semester) < 1 || Number(semester) > 10)) {
    return NextResponse.json({ error: "Semester must be a whole number between 1 and 10." }, { status: 400, headers: { "Cache-Control": "no-store" } });
  }
  const pdf = createSyntheticMarksheetPdf(student, semester);
  const safeName = student.name.replace(/[^a-zA-Z0-9-]+/g, "-").replace(/^-|-$/g, "") || "Synthetic-Student";
  return new Response(new Uint8Array(pdf), {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${safeName}-Synthetic-Marksheet.pdf"`,
      "Cache-Control": "no-store, private",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
