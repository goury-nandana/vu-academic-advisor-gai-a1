import syntheticStudentData from "./data/synthetic-students.json";

export type AgentCourseRecord = {
  course_code: string;
  course_title: string;
  prerequisite?: string;
  credits?: string | number;
  batch?: string;
  semester?: number;
  source?: string;
  cells?: Record<string, string>;
  document_type?: string;
  is_course_record?: boolean;
  programme?: string;
};

export type SyntheticStudent = {
  id: string;
  programme: string;
  admission_batch: string;
  current_semester: number;
  completed_course_codes: string[];
  failed_course_codes: string[];
  declared_minor: string;
};

export type AgentWorkflowResult = {
  student: SyntheticStudent;
  course: AgentCourseRecord;
  prerequisites: string[];
  eligibility: "prerequisites_met" | "prerequisite_failed" | "insufficient_information";
  failedPrerequisites: string[];
  unverifiedPrerequisites: string[];
  calculatedCredits: number;
  creditCourseCodes: string[];
  missingCreditRecords: string[];
  evidenceRecords: AgentCourseRecord[];
  evidenceVerified: boolean;
  recommendation: string;
  stages: string[];
};

const students = syntheticStudentData.students as SyntheticStudent[];

export function getSyntheticStudent(id: string): SyntheticStudent | undefined {
  return students.find((student) => student.id.toUpperCase() === id.trim().toUpperCase());
}

function normalizeCode(value: unknown): string {
  return String(value || "").replace(/[\\s-]/g, "").toUpperCase();
}

/** Agent 1: retrieves the synthetic student record selected for the demo. */
export function studentProfileAgent(id: string): SyntheticStudent | undefined {
  return getSyntheticStudent(id);
}

/** Agent 2: retrieves the exact course row for the student's admission batch. */
export function courseRetrievalAgent(
  code: string,
  student: SyntheticStudent,
  records: AgentCourseRecord[],
): AgentCourseRecord | undefined {
  const target = normalizeCode(code);
  return records.find((record) =>
    normalizeCode(record.course_code) === target &&
    String(record.batch || "") === student.admission_batch &&
    record.document_type === "semester_spread" &&
    record.is_course_record !== false &&
    String(record.programme || "").toLowerCase() === student.programme.toLowerCase()
  );
}

/** Agent 3: calculates credits only from passed courses with matching batch records. */
export function creditCalculationAgent(
  student: SyntheticStudent,
  records: AgentCourseRecord[],
): { total: number; courseCodes: string[]; missing: string[]; evidence: AgentCourseRecord[] } {
  const uniqueCodes = [...new Set(student.completed_course_codes.map(normalizeCode))];
  const evidence: AgentCourseRecord[] = [];
  const missing: string[] = [];
  let total = 0;
  for (const code of uniqueCodes) {
    const row = records.find((record) =>
      normalizeCode(record.course_code) === code &&
      String(record.batch || "") === student.admission_batch &&
      record.document_type === "semester_spread" &&
      record.is_course_record !== false &&
      String(record.programme || "").toLowerCase() === student.programme.toLowerCase()
    );
    const credits = Number(row?.credits);
    if (!row || !Number.isFinite(credits) || credits < 0) {
      missing.push(code);
      continue;
    }
    evidence.push(row);
    total += credits;
  }
  return { total, courseCodes: evidence.map((row) => normalizeCode(row.course_code)), missing, evidence };
}

/** Agent 4: checks direct prerequisites against the synthetic passed/failed course lists. */
export function eligibilityAgent(
  student: SyntheticStudent,
  course: AgentCourseRecord,
  records: AgentCourseRecord[],
): { status: AgentWorkflowResult["eligibility"]; prerequisites: string[]; failed: string[]; unverified: string[]; evidence: AgentCourseRecord[] } {
  const raw = String(course.prerequisite || "").trim();
  const prerequisites = raw && !/^(?:nil|none|na|n\/a|-)$/i.test(raw)
    ? raw.split(/[,;]+/).map(normalizeCode).filter(Boolean)
    : [];
  const completed = new Set(student.completed_course_codes.map(normalizeCode));
  const failedCourses = new Set(student.failed_course_codes.map(normalizeCode));
  const failed = prerequisites.filter((code) => failedCourses.has(code));
  const unverified = prerequisites.filter((code) => !completed.has(code) && !failedCourses.has(code));
  const evidence = prerequisites.flatMap((code) => {
    const row = records.find((record) =>
      normalizeCode(record.course_code) === code &&
      String(record.batch || "") === student.admission_batch &&
      record.document_type === "semester_spread" &&
      record.is_course_record !== false &&
      String(record.programme || "").toLowerCase() === student.programme.toLowerCase()
    );
    return row ? [row] : [];
  });
  const status = failed.length
    ? "prerequisite_failed"
    : unverified.length
      ? "insufficient_information"
      : "prerequisites_met";
  return { status, prerequisites, failed, unverified, evidence };
}

/** Agent 5: verifies that the target and all stated prerequisite rows exist in the source dataset. */
export function verificationAgent(
  course: AgentCourseRecord,
  prerequisites: string[],
  records: AgentCourseRecord[],
  student: SyntheticStudent,
): { verified: boolean; evidence: AgentCourseRecord[] } {
  const required = [normalizeCode(course.course_code), ...prerequisites];
  const evidence = required.flatMap((code) => {
    const row = records.find((record) =>
      normalizeCode(record.course_code) === code &&
      String(record.batch || "") === student.admission_batch &&
      record.document_type === "semester_spread" &&
      record.is_course_record !== false &&
      String(record.programme || "").toLowerCase() === student.programme.toLowerCase() &&
      Boolean(record.source) && Boolean(record.cells)
    );
    return row ? [row] : [];
  });
  return { verified: evidence.length === required.length, evidence };
}

/** Agent 6: gives a limited recommendation; it does not decide university enrolment. */
export function recommendationAgent(
  status: AgentWorkflowResult["eligibility"],
  failed: string[],
  unverified: string[],
): string {
  if (status === "prerequisites_met") {
    return "The listed direct prerequisites are recorded as completed in this synthetic profile. This is only a prerequisite check, not confirmation of registration or overall university eligibility.";
  }
  if (status === "prerequisite_failed") {
    return "The synthetic profile records a failed direct prerequisite (" + failed.join(", ") + "). The prerequisite check is not met; consult the Faculty Advisor before planning registration.";
  }
  return "The available synthetic profile does not establish completion of every direct prerequisite (" + unverified.join(", ") + "). More verified student information is required before advising.";
}

/** Orchestrator: runs the specialist stages in a controlled sequence. */
export function runAcademicAdvisorAgentWorkflow(
  studentId: string,
  courseCode: string,
  records: AgentCourseRecord[],
): AgentWorkflowResult | undefined {
  const student = studentProfileAgent(studentId);
  if (!student) return undefined;
  const course = courseRetrievalAgent(courseCode, student, records);
  if (!course) return undefined;
  const credit = creditCalculationAgent(student, records);
  const eligibility = eligibilityAgent(student, course, records);
  const verification = verificationAgent(course, eligibility.prerequisites, records, student);
  const recommendation = verification.verified
    ? recommendationAgent(eligibility.status, eligibility.failed, eligibility.unverified)
    : "Source verification is incomplete. Do not make an eligibility recommendation from this record.";
  return {
    student, course, prerequisites: eligibility.prerequisites,
    eligibility: verification.verified ? eligibility.status : "insufficient_information",
    failedPrerequisites: eligibility.failed,
    unverifiedPrerequisites: eligibility.unverified,
    calculatedCredits: credit.total,
    creditCourseCodes: credit.courseCodes,
    missingCreditRecords: credit.missing,
    evidenceRecords: [...new Map([...verification.evidence, ...credit.evidence].map((row) => [normalizeCode(row.course_code), row])).values()],
    evidenceVerified: verification.verified,
    recommendation,
    stages: [
      "Student-profile agent: loaded the selected synthetic student record",
      "Course-retrieval agent: retrieved the exact admission-batch course row",
      "Credit-calculation agent: summed credits from completed-course rows with matching source records",
      "Eligibility agent: checked each direct prerequisite against passed and failed course lists",
      "Verification agent: checked course and prerequisite evidence against source workbook rows",
      "Recommendation agent: produced a limited, non-authoritative prerequisite recommendation",
    ],
  };
}
