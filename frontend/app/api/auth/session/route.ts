import { NextResponse } from "next/server";
import { getAuthenticatedStudent } from "../../../lib/demo-auth";

export const runtime = "nodejs";
export async function GET(request: Request) {
  const student = getAuthenticatedStudent(request);
  if (!student) return NextResponse.json({ student: null }, { status: 401, headers: { "Cache-Control": "no-store" } });
  return NextResponse.json({ student: { id: student.id, username: student.username, name: student.name, synthetic_student_id: student.synthetic_student_id, programme: student.programme, admission_batch: student.admission_batch, current_semester: student.current_semester, academic_status: student.academic_status, synthetic_cgpa: student.synthetic_cgpa } }, { headers: { "Cache-Control": "no-store" } });
}
