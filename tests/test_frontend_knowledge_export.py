import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_frontend_knowledge import export_knowledge


class FrontendKnowledgeExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        export_knowledge()
        data_path = ROOT / "frontend" / "data" / "vu-academic-knowledge.json"
        cls.data = json.loads(data_path.read_text(encoding="utf-8"))

    def test_allowlisted_handbook_and_student_sop_are_included(self):
        sources = {item.get("source") for item in self.data["documents"]}
        self.assertIn("4. Student Handbook Aug 2026.pdf", sources)
        self.assertIn("SOP STUDENT 17082026 - Final.pdf", sources)

    def test_attendance_threshold_and_exception_are_present_in_export(self):
        documents = self.data["documents"]
        handbook = "\n".join(
            item["text"] for item in documents
            if item.get("source") == "4. Student Handbook Aug 2026.pdf"
        )
        sop = "\n".join(
            item["text"] for item in documents
            if item.get("source") == "SOP STUDENT 17082026 - Final.pdf"
        )
        self.assertRegex(handbook, r"seventy five percent|75\s*%")
        self.assertRegex(handbook, r"sixty five percent|65\s*%")
        self.assertIn("Government Regulatory Bodies", handbook)
        self.assertRegex(handbook, r"shall not be permitted to appear for the End Term")
        self.assertRegex(handbook, r"FA.? Grade")
        self.assertRegex(sop, r"attendance recorded on Digii")
        self.assertRegex(sop, r"attendance report will be shared")
        self.assertRegex(sop, r"sixty five percent|65\s*%")
        self.assertIn("medical leave request on Digii", sop)

    def test_structured_btech_curriculum_is_exported(self):
        records = self.data["courseRecords"]
        self.assertGreater(len(records), 0)
        self.assertTrue(all(record.get("course_code") and record.get("batch") for record in records))
        self.assertTrue(all(record.get("source") and record.get("cells") for record in records))

    def test_export_contains_source_metadata_for_citations(self):
        documents = self.data["documents"]
        attendance_sources = [
            item for item in documents
            if item.get("source") == "4. Student Handbook Aug 2026.pdf"
            and "75" in item.get("text", "")
        ]
        self.assertTrue(attendance_sources)
        self.assertTrue(any(item.get("page") == 29 for item in attendance_sources))


if __name__ == "__main__":
    unittest.main()
