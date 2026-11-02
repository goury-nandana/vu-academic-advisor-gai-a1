import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

_backend_path = str(Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, _backend_path)
from main import GH, SOCIAL_RE, extract_upload
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

    def test_webm_voice_note_is_transcribed(self):
        client = Mock()
        client.audio.transcriptions.create.return_value = "minimum attendance is sixty five percent"
        text = extract_upload("voice-note.webm", b"audio-bytes", client)
        self.assertIn("Voice note transcript:", text)
        self.assertIn("sixty five percent", text)
        client.audio.transcriptions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
