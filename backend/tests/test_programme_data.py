import io
import sys
import unittest
import zipfile
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from programme_data import extract_archive_records


def _archive(filename, workbook):
    xlsx = io.BytesIO()
    workbook.save(xlsx)
    zipped = io.BytesIO()
    with zipfile.ZipFile(zipped, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(filename, xlsx.getvalue())
    return zipped.getvalue()


class MinorWorkbookTests(unittest.TestCase):
    def test_header_driven_rows_preserve_alternatives_and_source_cells(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Psychology"
        ws.append(["2024 Batch", "Course Code", "Course Title", "L", "T", "P", "Credit", "Semester", "Pre-rq"])
        ws.append([None, "PSYC201/ PSYC103", "Biological Psychology/ Foundations of Psychology I", 3, 1, 0, 4, 3, "Nil"])
        ws.append([None, None, "TBD", None, None, None, 12, None, None])

        rows = extract_archive_records(_archive("Minor_Courses_for_BTech_Students.xlsx", wb), "minor")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["document_type"], "minor_course")
        self.assertEqual(row["batch"], "2024")
        self.assertEqual(row["course_code"], "PSYC201/ PSYC103")
        self.assertEqual(row["course_title"], "Biological Psychology/ Foundations of Psychology I")
        self.assertEqual(row["cells"]["course_code"], "B2")
        self.assertEqual(row["semester"], 3)

    def test_unknown_code_is_retained_not_guessed(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Marketing"
        ws.append(["2022 Batch", "Course Code", "Course Title", "L", "T", "P", "Credit", "Semester", "Pre-rq"])
        ws.append([None, "DON’T KNOW", "Marketing Management", 2, 1, 0, 3, 3, "Nil"])
        rows = extract_archive_records(_archive("Minor_Courses_for_BTech_Students.xlsx", wb), "minor")
        self.assertEqual(rows[0]["course_code"], "DON’T KNOW")
        self.assertEqual(rows[0]["batch"], "2022")


class ProgrammeStructureTests(unittest.TestCase):
    def test_repeated_header_blocks_electives_and_credit_baskets(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Struct_2026_DS"
        ws.append([None, None, None, None, None, None, None, None, None])
        ws.append([None, "#", "Program Core - Courses", "Cr", None, "Electives", "Cr", "Baskets", "Credits"])
        ws.append([None, 1, "Data Structures", 4, None, "Probabilistic Graph Models", 4, "University Core", 18])
        ws.append([None, 2, "Operating Systems", 4, None, "Option A / Option B", 3, "Total Credits", 180])
        ws.append([None, None, None, None, None, "Internship and Capstone Project - Courses", "Cr", None, None])
        ws.append([None, None, None, None, None, "Summer Training/Internship", 2, None, None])

        rows = extract_archive_records(_archive("Semester_Spread_Structures.xlsx", wb), "programme")
        courses = [r for r in rows if r["document_type"] == "programme_structure_course"]
        self.assertTrue(any(r["course_title"] == "Option A / Option B" and r["structure_group"] == "Electives" for r in courses))
        self.assertTrue(any(r["course_title"] == "Summer Training/Internship" and r["structure_group"] == "Internship and Capstone Project" for r in courses))
        self.assertEqual(next(r for r in courses if r["course_title"] == "Data Structures")["batch"], "2026")
        baskets = [r for r in rows if r["document_type"] == "programme_credit_structure"]
        self.assertEqual([(r["basket"], r["credits"]) for r in baskets], [("University Core", 18), ("Total Credits", 180)])

    def test_invalid_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_archive_records(b"", "other")


if __name__ == "__main__":
    unittest.main()
