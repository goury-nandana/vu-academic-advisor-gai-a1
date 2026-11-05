import { NextResponse } from "next/server";
import studentData from "../../../../data/synthetic-students.json";

export const runtime = "nodejs";
export async function GET() {
  const profiles = studentData.students
    .filter((student) => typeof student.username === "string" && student.username.trim())
    .map((student) => ({
      username: student.username,
      profileId: student.id,
      name: student.name,
      persona: student.persona,
      programme: student.programme,
      currentSemester: student.current_semester,
      academicStatus: student.academic_status,
    }));
  return NextResponse.json({ profiles }, { headers: { "Cache-Control": "no-store" } });
}
