import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

from openpyxl import Workbook

from programme_data import (
    _records_from_sheet,
    load_minor_records,
    load_programme_structure_records,
)


def make_xlsx(headers, rows, title_row=None):
    wb = Workbook()
    ws = wb.active
    if title_row:
        ws.append([title_row])
    ws.append(headers)
    for row in rows:
        ws.append(row)
    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


class ProgrammeDataBuilderTests(unittest.TestCase):
    def test_header_driven_minor_course_record(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["Minor in Law"])
        ws.append(["Course Code", "Course Name", "Credits", "Semester", "Prerequisite"])
        ws.append(["LAW201", "Legal Foundations", 3, 2, "None"])
        rows = _records_from_sheet(ws, "01_Minor_Law.xlsx", "minor")
        course = next(r for r in rows if r["document_type"] == "minor_course")
        self.assertEqual(course["course_code"], "LAW201")
        self.assertEqual(course["course_title"], "Legal Foundations")
        self.assertEqual(course["credits"], 3)
        self.assertEqual(course["semester"], 2)
        self.assertEqual(course["minor_name"], "Law")
        self.assertEqual(course["cells"]["course_code"], "A3")

    def test_raw_elective_slot_is_not_split_or_guessed(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["Programme structure"])
        ws.append(["Elective Slot", "Notes"])
        ws.append(["Choose one: LAW201 / LAW202", "Either option"])
        rows = _records_from_sheet(ws, "06_Programme_Structure_BTech_2026.xlsx", "programme")
        raw = next(r for r in rows if r["document_type"] == "raw_elective_slot")
        self.assertEqual(raw["raw_value"], "Choose one: LAW201 / LAW202")
        self.assertFalse(raw["is_course_record"])
        self.assertNotIn("course_code", raw)
        self.assertEqual(raw["cells"]["slot"], "A3")

    def test_ambiguous_or_incomplete_course_rows_are_skipped(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["Course Code", "Course Name", "Credits"])
        ws.append(["LAW201", None, 3])
        ws.append(["", "A course without a code", 3])
        ws.append(["LAW/202", "Ambiguous code format", 3])
        rows = _records_from_sheet(ws, "Minor_Law.xlsx", "minor")
        self.assertFalse(any(r["document_type"] == "minor_course" for r in rows))

    def test_committed_minor_workbooks_produce_source_grounded_records(self):
        rows = load_minor_records()
        courses = [row for row in rows if row.get("document_type") == "minor_course"]
        self.assertGreater(len(courses), 0)
        self.assertEqual(
            {row["source"] for row in courses},
            {
                "01_Minor_Law.xlsx", "02_Minor_Design.xlsx", "03_Minor_Psychology.xlsx",
                "04_Minor_Economics.xlsx", "05_Minor_Finance.xlsx", "06_Minor_Marketing.xlsx",
                "07_Minor_Start-up.xlsx",
            },
        )
        self.assertTrue(all(row.get("source") and row.get("sheet") and row.get("cells") for row in courses))
        self.assertTrue(all(row.get("course_code") and row.get("course_title") for row in courses))

    def test_committed_programme_structures_are_loaded(self):
        rows = load_programme_structure_records()
        course_rows = [row for row in rows if row.get("document_type") == "programme_structure_course"]
        raw_slots = [row for row in rows if row.get("document_type") == "raw_elective_slot"]
        self.assertGreater(len(course_rows), 0)
        self.assertGreater(len(raw_slots), 0)
        self.assertTrue(all(row.get("source") and row.get("sheet") and row.get("cells") for row in rows))
        self.assertEqual({str(row["batch"]) for row in course_rows}, {"2022", "2023", "2024", "2025", "2026"})

    def test_combined_minor_workbook_keeps_explicit_batch_and_unknown_code_raw(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Psychology"
        ws.append(["2024 Batch", "Course Code", "Course Title", "L", "T", "P", "Credit", "Semester", "Pre-rq"])
        ws.append([None, "PSYC201/ PSYC103", "Biological Psychology/ Foundations of Psychology I", 3, 1, 0, 4, 3, "Nil"])
        rows = _records_from_sheet(ws, "Minor_Courses_for_BTech_Students.xlsx", "minor")
        raw = next(r for r in rows if r["document_type"] == "raw_elective_slot")
        self.assertEqual(raw["raw_value"], "PSYC201/ PSYC103 — Biological Psychology/ Foundations of Psychology I")
        self.assertEqual(raw["batch"], "2024")
        self.assertFalse(raw["is_course_record"])

    def test_second_programme_header_block_is_not_missed(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Struct_2026_DS"
        ws.append([None, "#", "Program Core - Courses", "Cr", None, "#", "Electives", "Cr"])
        ws.append([None, 1, "Data Structures", 4, None, "Probabilistic Graph Models", 4])
        ws.append([None, 2, "Operating Systems", 4, None, "Option A / Option B", 4])
        ws.append([None, None, None, None, "#", "Internship and Capstone Project - Courses", "Cr"])
        ws.append([None, None, None, None, None, "Summer Training/Internship", 2])
        rows = _records_from_sheet(ws, "Semester_Spread_Structures_Sept_2026.xlsx", "programme")
        titles = {r.get("course_title") for r in rows if r["document_type"] == "programme_structure_course"}
        self.assertIn("Data Structures", titles)
        self.assertIn("Summer Training/Internship", titles)
        self.assertTrue(any(r.get("raw_value") == "Option A / Option B" for r in rows))
        self.assertEqual({r["batch"] for r in rows if r.get("batch")}, {"2026"})

    def test_workbook_archives_load_only_matching_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            minor_path = Path(tmp) / "minor.zip"
            programme_path = Path(tmp) / "programme.zip"
            with ZipFile(minor_path, "w") as z:
                z.writestr("01_Minor_Law.xlsx", make_xlsx(
                    ["Course Code", "Course Title", "Credits"],
                    [["LAW201", "Legal Foundations", 3]],
                ))
            with ZipFile(programme_path, "w") as z:
                z.writestr("06_Programme_Structure_BTech_2026.xlsx", make_xlsx(
                    ["Course Code", "Course Title", "Semester", "Elective Slot"],
                    [["UCOR205", "Core Course", 2, "Open elective choice"]],
                ))
            minors = load_minor_records(minor_path)
            programmes = load_programme_structure_records(programme_path)
            self.assertEqual([r["course_code"] for r in minors if r["is_course_record"]], ["LAW201"])
            self.assertTrue(any(r["document_type"] == "raw_elective_slot" for r in programmes))
            self.assertEqual(next(r for r in programmes if r["is_course_record"])["batch"], "2026")


if __name__ == "__main__":
    unittest.main()
