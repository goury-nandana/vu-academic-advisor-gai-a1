import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "frontend/data/synthetic-students.json").read_text(encoding="utf-8"))
CREDENTIALS = json.loads((ROOT / "frontend/data/synthetic-account-credentials.json").read_text(encoding="utf-8"))
COURSES = json.loads((ROOT / "frontend/data/vu-academic-knowledge.json").read_text(encoding="utf-8"))["courseRecords"]
AUTH_SOURCE = (ROOT / "frontend/lib/demo-auth.ts").read_text(encoding="utf-8")
LOGIN_ROUTE = (ROOT / "frontend/app/api/auth/login/route.ts").read_text(encoding="utf-8")
SIGNUP_ROUTE = (ROOT / "frontend/app/api/auth/signup/route.ts").read_text(encoding="utf-8")
DEMO_PROFILES_ROUTE = (ROOT / "frontend/app/api/auth/demo-profiles/route.ts").read_text(encoding="utf-8")
MARKSHEET_ROUTE = (ROOT / "frontend/app/api/marksheet/route.ts").read_text(encoding="utf-8")
MARKSHEET_PDF = (ROOT / "frontend/lib/synthetic-marksheet-pdf.ts").read_text(encoding="utf-8")
FRONTEND_PAGE = (ROOT / "frontend/app/page.tsx").read_text(encoding="utf-8")
SESSION_ROUTE = (ROOT / "frontend/app/api/auth/session/route.ts").read_text(encoding="utf-8")
LOGOUT_ROUTE = (ROOT / "frontend/app/api/auth/logout/route.ts").read_text(encoding="utf-8")
CHAT_ROUTE = (ROOT / "frontend/app/api/chat/route.ts").read_text(encoding="utf-8")


class SyntheticAccountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounts = CREDENTIALS["accounts"]
        cls.students = {student["id"]: student for student in PROFILES["students"]}
        cls.source_rows = {
            (str(row.get("batch")), row.get("course_code"), row.get("semester")): row
            for row in COURSES
            if row.get("document_type") == "semester_spread"
            and row.get("is_course_record") is not False
            and str(row.get("programme", "")).lower() == "b.tech"
        }

    def test_ten_accounts_have_unique_credentials_and_profile_links(self):
        self.assertEqual(len(self.accounts), 10)
        self.assertEqual(len({account["username"] for account in self.accounts}), 10)
        self.assertEqual(len({account["profileId"] for account in self.accounts}), 10)
        for account in self.accounts:
            with self.subTest(username=account["username"]):
                profile = self.students[account["profileId"]]
                self.assertEqual(profile["username"], account["username"])
                self.assertEqual(profile["user_id"], profile["name"])
                self.assertEqual(account["username"], profile["name"])
                self.assertTrue(profile["name"])
                self.assertTrue(profile["synthetic_student_id"].startswith("VU-SYN-"))
                self.assertTrue(profile["programme"].startswith("B.Tech"))

    def test_demo_passwords_match_server_side_pbkdf2_hashes(self):
        self.assertEqual(CREDENTIALS["algorithm"], "PBKDF2-SHA256")
        iterations = CREDENTIALS["iterations"]
        self.assertGreaterEqual(iterations, 120000)
        for index, account in enumerate(self.accounts, start=1):
            password = b"1234"
            actual = hashlib.pbkdf2_hmac("sha256", password, bytes.fromhex(account["salt"]), iterations)
            with self.subTest(username=account["username"]):
                self.assertEqual(actual.hex(), account["hash"])
                self.assertNotIn(password.decode(), json.dumps(account))
                self.assertNotIn("password", account)

    def test_account_course_history_matches_exact_batch_semester_source_rows(self):
        for account in self.accounts:
            student = self.students[account["profileId"]]
            batch = str(student["admission_batch"])
            for record in student["academic_records"]:
                key = (batch, record["course_code"], record["semester"])
                source = self.source_rows.get(key)
                with self.subTest(student=student["id"], course=record["course_code"], semester=record["semester"]):
                    self.assertIsNotNone(source)
                    self.assertEqual(record["course_title"], source["course_title"])
                    self.assertEqual(record["credits"], int(source["credits"]))
                    self.assertTrue(record["synthetic_result"])

    def test_auth_uses_hashed_passwords_and_secure_session_cookie_flags(self):
        self.assertIn("pbkdf2", AUTH_SOURCE.lower())
        self.assertIn("timingSafeEqual", AUTH_SOURCE)
        self.assertIn("createHmac", AUTH_SOURCE)
        self.assertIn("httpOnly: true", LOGIN_ROUTE)
        self.assertIn('sameSite: "strict"', LOGIN_ROUTE)
        self.assertIn('secure: process.env.NODE_ENV === "production"', LOGIN_ROUTE)
        self.assertIn("maxAge: demoSessionTtlSeconds", LOGIN_ROUTE)
        self.assertIn("verifyDemoCredentials", LOGIN_ROUTE)

    def test_session_logout_and_chat_are_bound_to_authenticated_student(self):
        self.assertIn("getAuthenticatedStudent(request)", SESSION_ROUTE)
        self.assertIn("maxAge: 0", LOGOUT_ROUTE)
        self.assertIn("getAuthenticatedStudent(request)", CHAT_ROUTE)
        self.assertIn("status:401", CHAT_ROUTE.replace(" ", ""))
        self.assertNotIn('form.get("profile")', CHAT_ROUTE)
        self.assertIn("authenticatedStudent.id", CHAT_ROUTE)
        self.assertIn("authenticatedStudent.academic_records.map", CHAT_ROUTE)

    def test_signup_activates_only_a_preprovisioned_synthetic_profile(self):
        self.assertIn("verifyDemoCredentials", SIGNUP_ROUTE)
        self.assertIn("pre-provisioned fictional scenarios", SIGNUP_ROUTE)
        self.assertIn("createSessionToken", SIGNUP_ROUTE)
        self.assertIn("student.username", SIGNUP_ROUTE)
        self.assertIn("studentData.students", DEMO_PROFILES_ROUTE)
        self.assertIn("persona", DEMO_PROFILES_ROUTE)
        self.assertIn('"/api/auth/signup"', FRONTEND_PAGE)
        self.assertIn("shared demo password: 1234", FRONTEND_PAGE)

    def test_authenticated_marksheet_pdf_generation_and_download_route(self):
        self.assertIn("getAuthenticatedStudent(request)", MARKSHEET_ROUTE)
        self.assertIn("application/pdf", MARKSHEET_ROUTE)
        self.assertIn("Content-Disposition", MARKSHEET_ROUTE)
        self.assertIn("createSyntheticMarksheetPdf(student)", MARKSHEET_ROUTE)
        self.assertIn("SYNTHETIC DEMONSTRATION RECORD - NOT AN OFFICIAL MARKSHEET", MARKSHEET_PDF)
        self.assertIn("academic_records", MARKSHEET_PDF)
        self.assertIn("createSyntheticMarksheetPdf", MARKSHEET_PDF)
        self.assertIn("/api/marksheet", FRONTEND_PAGE)
        self.assertIn("Download Synthetic Marksheet (PDF)", FRONTEND_PAGE)


if __name__ == "__main__":
    unittest.main()
