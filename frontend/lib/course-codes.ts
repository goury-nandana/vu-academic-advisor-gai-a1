// Course-code extraction that never confuses student identifiers with courses.
//
// Student identifiers in this app look like course codes to a naive pattern:
//   VU006, VU-SYN-106, SYN-106, SYN110
// None of these is an academic course code. Real codes (COMP302, DATA207, ...)
// are validated against the structured course records before being used.

const COURSE_SHAPE = /\b[A-Za-z]{2,6}[\s-]?\d{3,4}[A-Za-z]?\b/g;
// Order matters: the longer VU-SYN form is stripped before the bare SYN form.
const STUDENT_ID_SHAPES: RegExp[] = [
  /\bVU[\s-]?SYN[\s-]?\d{2,4}\b/gi,
  /\bSYN[\s-]?\d{2,4}\b/gi,
  /\bVU[\s-]?\d{2,4}\b/gi,
];

export type CourseCodeResolution = {
  /** Code-shaped tokens that are real course codes in the structured records. */
  valid: string[];
  /** Code-shaped tokens with a known department prefix but no matching record. */
  unknown: string[];
  /** Student identifiers found in the text (identity fields, never courses). */
  studentIds: string[];
};

export function normaliseCode(code: string): string {
  return code.replace(/[\s-]/g, "").toUpperCase();
}

export function findStudentIds(text: string): string[] {
  const found: string[] = [];
  for (const shape of STUDENT_ID_SHAPES) {
    for (const match of text.matchAll(new RegExp(shape.source, shape.flags))) found.push(normaliseCode(match[0]));
  }
  return [...new Set(found)];
}

function stripStudentIds(text: string): string {
  return STUDENT_ID_SHAPES.reduce((acc, shape) => acc.replace(new RegExp(shape.source, shape.flags), " "), text);
}

/** Shape-only candidates with student identifiers removed. Not yet validated. */
export function extractCourseCodeCandidates(text: string): string[] {
  const cleaned = stripStudentIds(text);
  return [...new Set((cleaned.match(COURSE_SHAPE) ?? []).map(normaliseCode))];
}

export function buildCourseCodeIndex(records: ReadonlyArray<{ course_code?: unknown }>): {
  codes: ReadonlySet<string>;
  prefixes: ReadonlySet<string>;
} {
  const codes = new Set<string>();
  const prefixes = new Set<string>();
  for (const record of records) {
    const code = normaliseCode(String(record.course_code ?? ""));
    if (!code) continue;
    codes.add(code);
    const prefix = code.match(/^[A-Z]+/)?.[0];
    if (prefix) prefixes.add(prefix);
  }
  return { codes, prefixes };
}

export function resolveCourseCodes(
  text: string,
  index: { codes: ReadonlySet<string>; prefixes: ReadonlySet<string> },
): CourseCodeResolution {
  const candidates = extractCourseCodeCandidates(text);
  const valid: string[] = [];
  const unknown: string[] = [];
  for (const code of candidates) {
    if (index.codes.has(code)) valid.push(code);
    else if (index.prefixes.has(code.match(/^[A-Z]+/)?.[0] ?? "")) unknown.push(code);
    // Anything else ("batch 2024", "clause 1234") is not treated as a course.
  }
  // A student id is only reported as such if it is not itself a real course code.
  const studentIds = findStudentIds(text).filter((id) => !index.codes.has(id));
  return { valid, unknown, studentIds };
}
