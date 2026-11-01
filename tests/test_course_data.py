import unittest

from course_data import load_course_records


class CourseDataFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_course_records()

    def test_all_five_supported_batches_are_loaded(self):
        self.assertEqual(
            {str(row["batch"]) for row in self.records},
            {"2022", "2023", "2024", "2025", "2026"},
        )
        self.assertGreaterEqual(len(self.records), 190)

    def test_ucor205_matches_original_batch_specific_rows(self):
        expected = {
            "2022": (3, 3, "NIL", 2, 1, 0),
            "2023": (3, 3, "NIL", 2, 1, 0),
            "2024": (3, 3, "NIL", 2, 1, 0),
            "2025": (4, 3, "Nil", 2, 1, 0),
            "2026": (4, 3, "Nil", 2, 1, 0),
        }
        for batch, (semester, credits, prereq, l_val, t_val, p_val) in expected.items():
            rows = [r for r in self.records
                    if r["course_code"] == "UCOR205" and str(r["batch"]) == batch]
            self.assertEqual(len(rows), 1, f"UCOR205 row count for {batch}")
            row = rows[0]
            self.assertEqual(row["semester"], semester)
            self.assertEqual(row["credits"], credits)
            self.assertEqual(row["prerequisite"], prereq)
            self.assertEqual((row["L"], row["T"], row["P"]), (l_val, t_val, p_val))

    def test_source_provenance_is_present(self):
        for row in self.records:
            self.assertTrue(row["source"])
            self.assertTrue(row["cells"]["code"])
            self.assertTrue(row["cells"]["title"])
            self.assertEqual(row["document_type"], "semester_spread")
            self.assertTrue(row["is_course_record"])

    def test_track_is_not_inferred_for_earlier_batches(self):
        for row in self.records:
            if str(row["batch"]) in {"2022", "2023", "2024", "2025"}:
                self.assertIsNone(row["track"])
        self.assertEqual(
            {r["track"] for r in self.records if str(r["batch"]) == "2026"},
            {"Data Science"},
        )


if __name__ == "__main__":
    unittest.main()
