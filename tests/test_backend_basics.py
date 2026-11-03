import io
import sys
import unittest
import zipfile
from openpyxl import Workbook
from pathlib import Path
from unittest.mock import Mock

_backend_path = str(Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, _backend_path)
from main import GH, NONSENSE_RE, REACTION_RE, SOCIAL_RE, extract_course_records, extract_upload, search, tok
sys.path.remove(_backend_path)
sys.modules.pop("programme_data", None)


class BackendBasicsTests(unittest.TestCase):
    def test_common_and_typo_greetings_bypass_retrieval(self):
        for message in ("hi", "hii", "hiii", "hey", "heyy", "hello", "good morning", "how are you", "thanks"):
            with self.subTest(message=message):
                self.assertIsNotNone(SOCIAL_RE.fullmatch(message))

    def test_academic_question_is_not_classified_as_small_talk(self):
        for message in ("minimum attendance?", "how do I apply to VU?", "course prerequisites"):
            with self.subTest(message=message):
                self.assertIsNone(SOCIAL_RE.fullmatch(message))

    def test_frustration_feedback_bypasses_retrieval(self):
        for message in ("wtf", "wtf is this", "are u dumb", "this makes no sense", "not what I asked"):
            with self.subTest(message=message):
                self.assertIsNotNone(REACTION_RE.fullmatch(message))

    def test_reaction_regex_does_not_capture_academic_questions(self):
        for message in ("what is the attendance policy?", "what are the prerequisites?", "how do I apply?"):
            with self.subTest(message=message):
                self.assertIsNone(REACTION_RE.fullmatch(message))

    def test_repeated_gibberish_is_detected(self):
        message = "jdhhhhhhhhhhhhhhhhhhhhhhhhhdgggggggggggggcftuj"
        self.assertIsNotNone(NONSENSE_RE.search(message))
        self.assertLessEqual(len(tok(message)), 3)

    def test_source_links_use_direct_file_host_not_github_blob_viewer(self):
        self.assertTrue(GH.startswith("https://raw.githubusercontent.com/"))
        self.assertNotIn("/blob/", GH)

    def test_min_attendance_query_retrieves_matching_evidence(self):
        docs = [
            {"text": "The minimum attendance requirement is sixty five percent.", "source": "handbook", "page": 3},
            {"text": "Students may apply for admission using the portal.", "source": "admissions", "page": 8},
        ]
        result = search("min attendance?", docs)
        self.assertTrue(result)
        self.assertEqual(result[0]["source"], "handbook")

    def test_btech_and_semester_synonyms_retrieve_matching_row(self):
        self.assertIn("btech", tok("B.Tech"))
        docs = [
            {"text": "B.Tech course entry for semester 2; prerequisite None.", "source": "curriculum"},
            {"text": "B.Tech course entry for semester 5; prerequisite None.", "source": "curriculum"},
        ]
        result = search("BTech second semester courses", docs)
        self.assertTrue(result)
        self.assertIn("semester 2", result[0]["text"])

    def test_structured_course_record_supports_space_hyphen_code_lookup(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet["D1"] = "S1"
        values = ["BASKET1", "Core", "CS 101", "Intro Programming", "None", 3, 0, 0, 4]
        for column, value in enumerate(values, start=1):
            sheet.cell(row=3, column=column, value=value)
        workbook_bytes = io.BytesIO()
        workbook.save(workbook_bytes)
        archive_bytes = io.BytesIO()
        with zipfile.ZipFile(archive_bytes, "w") as archive:
            archive.writestr("01_Semester_Spread_BTech_2022.xlsx", workbook_bytes.getvalue())

        records = extract_course_records(archive_bytes.getvalue())
        matching = search("CS-101 prerequisite credits", records)
        self.assertTrue(matching)
        self.assertEqual(matching[0]["course_code"], "CS101")
        self.assertEqual(matching[0]["semester"], 1)
        self.assertEqual(matching[0]["credits"], 4)

    def test_png_image_upload_uses_vision_model(self):
        client = Mock()
        client.chat.completions.create.return_value.choices = [Mock(message=Mock(content="The image shows an attendance table."))]
        text = extract_upload("schedule.png", b"fake-image-bytes", client)
        self.assertIn("attendance table", text)
        args = client.chat.completions.create.call_args.kwargs
        self.assertEqual(args["messages"][0]["content"][1]["type"], "image_url")

    def test_webm_voice_note_is_transcribed(self):
        client = Mock()
        client.audio.transcriptions.create.return_value = "minimum attendance is sixty five percent"
        text = extract_upload("voice-note.webm", b"audio-bytes", client)
        self.assertIn("Voice note transcript:", text)
        self.assertIn("sixty five percent", text)
        client.audio.transcriptions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
