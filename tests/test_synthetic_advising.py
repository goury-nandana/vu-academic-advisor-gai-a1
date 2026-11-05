import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COURSE_DATA = json.loads((ROOT / "frontend/data/vu-academic-knowledge.json").read_text(encoding="utf-8"))
SYNTHETIC_DATA = json.loads((ROOT / "frontend/data/synthetic-students.json").read_text(encoding="utf-8"))
AGENT_SOURCE = (ROOT / "frontend/academic-agents.ts").read_text(encoding="utf-8")
ROUTE_SOURCE = (ROOT / "frontend/app/api/chat/route.ts").read_text(encoding="utf-8")
PAGE_SOURCE = (ROOT / "frontend/app/page.tsx").read_text(encoding="utf-8")


class SyntheticAgentWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [
            row for row in COURSE_DATA["courseRecords"]
            if str(row.get("batch")) == "2025"
            and row.get("document_type") == "semester_spread"
            and row.get("is_course_record") is not False
            and str(row.get("programme", "")).lower() == "b.tech"
        ]
        cls.record_by_code = {row["course_code"]: row for row in cls.records}
        cls.students = {row["id"]: row for row in SYNTHETIC_DATA["students"]}
        cls.target = cls.record_by_code["COMP302"]
        cls.prerequisites = [
            code.strip()
            for code in re.split(r"[,;]+", str(cls.target.get("prerequisite", "")))
            if code.strip() and code.strip().upper() not in {"NIL", "NONE", "NA"}
        ]

    def test_synthetic_records_are_explicitly_not_real_students(self):
        self.assertEqual(SYNTHETIC_DATA["dataset_type"], "synthetic_demonstration_only")
        self.assertIn("not real VU students", SYNTHETIC_DATA["warning"])
        self.assertEqual({sid for sid, row in self.students.items() if row.get("test_fixture_only")}, {"SYN-001", "SYN-002", "SYN-003"})
        account_profiles = [row for row in self.students.values() if row.get("username") and not row.get("test_fixture_only")]
        self.assertEqual(len(account_profiles), 10)
        self.assertEqual(len({row["username"] for row in account_profiles}), 10)
        self.assertTrue(all(row["programme"].startswith("B.Tech") for row in account_profiles))

    def test_all_profile_course_codes_have_batch_matched_source_rows(self):
        rows_by_batch = {}
        for row in COURSE_DATA["courseRecords"]:
            if row.get("document_type") == "semester_spread" and row.get("is_course_record") is not False and str(row.get("programme", "")).lower() == "b.tech":
                rows_by_batch.setdefault(str(row.get("batch")), {})[row["course_code"]] = row
        for student in self.students.values():
            matching_rows = rows_by_batch.get(str(student["admission_batch"]), {})
            for code in student["completed_course_codes"]:
                with self.subTest(student=student["id"], batch=student["admission_batch"], code=code):
                    self.assertIn(code, matching_rows)

    def test_prerequisite_scenarios_cover_pass_fail_and_unknown(self):
        passed = set(self.students["SYN-001"]["completed_course_codes"])
        failed = set(self.students["SYN-001"]["failed_course_codes"])
        self.assertTrue(all(code in passed for code in self.prerequisites))
        self.assertFalse(any(code in failed for code in self.prerequisites))

        passed = set(self.students["SYN-002"]["completed_course_codes"])
        failed = set(self.students["SYN-002"]["failed_course_codes"])
        self.assertEqual([code for code in self.prerequisites if code in failed], ["COMP206"])
        self.assertTrue(all(code in passed or code in failed for code in self.prerequisites))

        passed = set(self.students["SYN-003"]["completed_course_codes"])
        failed = set(self.students["SYN-003"]["failed_course_codes"])
        unknown = [code for code in self.prerequisites if code not in passed and code not in failed]
        self.assertEqual(set(unknown), {"COMP206", "COMP208"})

    def test_credit_totals_are_calculated_from_matching_workbook_rows(self):
        totals = {}
        for student_id, student in self.students.items():
            if not student.get("test_fixture_only"):
                continue
            totals[student_id] = sum(
                int(self.record_by_code[code]["credits"])
                for code in student["completed_course_codes"]
            )
        self.assertEqual(totals, {"SYN-001": 29, "SYN-002": 25, "SYN-003": 21})

    def test_specialist_agents_and_orchestrator_are_present(self):
        for symbol in (
            "studentProfileAgent", "courseRetrievalAgent", "creditCalculationAgent",
            "eligibilityAgent", "verificationAgent", "recommendationAgent",
            "runAcademicAdvisorAgentWorkflow",
        ):
            with self.subTest(symbol=symbol):
                self.assertIn("function " + symbol, AGENT_SOURCE)

    def test_workflow_is_wired_only_for_selected_synthetic_profile(self):
        self.assertIn("runAcademicAdvisorAgentWorkflow", ROUTE_SOURCE)
        self.assertIn("profile.syntheticStudentId", ROUTE_SOURCE)
        self.assertIn("syntheticStudent&&requestedSyntheticCourseCode&&asksSyntheticDecision", ROUTE_SOURCE)
        self.assertIn("synthetic demonstration", ROUTE_SOURCE.lower())

    def test_privacy_notice_and_evidence_export_are_visible_in_frontend(self):
        self.assertIn("Questions, optional profile details and uploaded files are sent to Groq", PAGE_SOURCE)
        self.assertIn("Do not enter passwords, student IDs or sensitive personal records", PAGE_SOURCE)
        self.assertIn("function exportEvidence", PAGE_SOURCE)
        self.assertIn("message.sources || []", PAGE_SOURCE)
        self.assertIn("message.model ||", PAGE_SOURCE)

    def test_chat_and_transcription_apis_check_origin_and_declared_body_size(self):
        transcription = (ROOT / "frontend/app/api/transcribe/route.ts").read_text(encoding="utf-8")
        for source in (ROUTE_SOURCE, transcription):
            self.assertIn('request.headers.get("origin")', source)
            self.assertIn('request.headers.get("content-length")', source)
            self.assertIn("Cross-origin", source)


if __name__ == "__main__":
    unittest.main()
