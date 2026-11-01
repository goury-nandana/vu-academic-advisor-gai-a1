import io
import unittest

from upload_support import (
    MAX_FILE_BYTES,
    SUPPORTED_EXTENSIONS,
    extract_document_text,
)


class FakeUpload:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


class UploadSupportTests(unittest.TestCase):
    def test_plain_text_upload_is_extracted(self):
        file = FakeUpload("notes.txt", "Attendance policy notes".encode("utf-8"))
        self.assertEqual(extract_document_text(file), "Attendance policy notes")

    def test_markdown_and_csv_are_supported(self):
        self.assertIn("md", SUPPORTED_EXTENSIONS)
        self.assertIn("csv", SUPPORTED_EXTENSIONS)
        file = FakeUpload("table.csv", b"course,credits\nDATA101,4")
        self.assertIn("DATA101", extract_document_text(file))

    def test_legacy_word_document_is_rejected_with_conversion_guidance(self):
        file = FakeUpload("old.doc", b"binary")
        with self.assertRaisesRegex(ValueError, "Save as .docx or PDF"):
            extract_document_text(file)

    def test_file_size_limit_is_enforced(self):
        file = FakeUpload("large.txt", b"x" * (MAX_FILE_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "15 MB"):
            extract_document_text(file)


if __name__ == "__main__":
    unittest.main()
