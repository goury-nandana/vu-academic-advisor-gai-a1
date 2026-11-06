import { describe, expect, it } from "vitest";
import academic from "../data/vu-academic-knowledge.json";
import { buildCourseCodeIndex, extractCourseCodeCandidates, resolveCourseCodes } from "../lib/course-codes";

const index = buildCourseCodeIndex((academic as { courseRecords: Array<{ course_code?: unknown }> }).courseRecords);

describe("student IDs are never course codes", () => {
  it.each(["SYN-106", "SYN110", "VU-SYN-106", "VU006", "vu 010", "syn 106"])("%s is excluded", (id) => {
    expect(extractCourseCodeCandidates("what about " + id + "?")).toEqual([]);
  });

  it("keeps COMP302 and drops the student id in a mixed question", () => {
    const r = resolveCourseCodes("I am VU-SYN-106 (SYN110). Can I take COMP302?", index);
    expect(r.valid).toEqual(["COMP302"]);
    expect(r.unknown).toEqual([]);
    expect(r.studentIds).toEqual(expect.arrayContaining(["VUSYN106", "SYN110"]));
  });
});

describe("validation against the structured course records", () => {
  it("accepts real codes in any spacing/case", () => {
    expect(resolveCourseCodes("comp 302 and DATA-207", index).valid).toEqual(["COMP302", "DATA207"]);
  });
  it("flags a known-prefix code that has no record instead of silently accepting it", () => {
    expect(resolveCourseCodes("tell me about COMP999", index)).toMatchObject({ valid: [], unknown: ["COMP999"] });
  });
  it("ignores non-course tokens like 'batch 2024'", () => {
    const r = resolveCourseCodes("2024 batch or batch 2024, clause 1234", index);
    expect(r.valid).toEqual([]);
    expect(r.unknown).toEqual([]);
  });
});
