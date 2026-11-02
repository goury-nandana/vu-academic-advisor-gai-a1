import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

_backend_path = str(Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, _backend_path)
from main import GH, SOCIAL_RE, extract_upload, search
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

    def test_png_image_upload_uses_vision_model(self):
        client = Mock()
        client.chat.completions.create.return_value.choices[0].message.content = "The image shows an attendance table."
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
