import ast
import re
import unittest
from pathlib import Path
from types import SimpleNamespace


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
TREE = ast.parse(APP_PATH.read_text(encoding="utf-8"))

NEEDED_FUNCTIONS = {
    "extract_batch_years",
    "batch_from_question",
    "normalize_course_code",
    "course_records_for_code",
    "course_records_for_semester",
    "latest_assistant_message",
    "assistant_is_asking_batch_clarification",
    "is_clarification_reply",
    "get_context_anchor_question",
    "is_follow_up_question",
    "conversation_context_for",
}
NEEDED_ASSIGNMENTS = {"FOLLOW_UP_RE", "NEW_TOPIC_TERMS"}
selected = []
for node in TREE.body:
    if isinstance(node, ast.FunctionDef) and node.name in NEEDED_FUNCTIONS:
        selected.append(node)
    elif isinstance(node, ast.Assign):
        names = {target.id for target in node.targets if isinstance(target, ast.Name)}
        if names & NEEDED_ASSIGNMENTS:
            selected.append(node)

namespace = {
    "re": re,
    "st": SimpleNamespace(session_state=SimpleNamespace(messages=[])),
}
exec(compile(ast.Module(body=selected, type_ignores=[]), str(APP_PATH), "exec"), namespace)


class ConversationLogicTests(unittest.TestCase):
    def setUp(self):
        namespace["st"].session_state.messages = [
            {"role": "user", "content": "What are the credits and prerequisites for UCOR205 in B.Tech?"},
            {
                "role": "assistant",
                "content": (
                    "Which admission batch are you asking about: 2022, 2023, 2024, 2025 or 2026? "
                    "The course structure can differ by batch, so I need that detail before giving the curriculum answer."
                ),
            },
        ]

    def test_extracts_multiple_years(self):
        self.assertEqual(
            namespace["extract_batch_years"]("for 2021 and 2026 you give"),
            ["2021", "2026"],
        )

    def test_recognises_multi_year_clarification_reply(self):
        self.assertTrue(namespace["is_clarification_reply"]("for 2021 and 2026 you give"))

    def test_keeps_original_course_question_as_context_anchor(self):
        namespace["st"].session_state.messages.append(
            {"role": "user", "content": "for 2021 and 2026 you give"}
        )
        self.assertEqual(
            namespace["get_context_anchor_question"](),
            "What are the credits and prerequisites for UCOR205 in B.Tech?",
        )

    def test_pending_batch_question_keeps_context(self):
        namespace["st"].session_state.messages.append(
            {"role": "user", "content": "for 2021 and 2026 you give"}
        )
        context = namespace["conversation_context_for"]("for 2021 and 2026 you give")
        self.assertIn("UCOR205", context)
        self.assertIn("Which admission batch", context)

    def test_all_batches_is_a_clarification_reply(self):
        self.assertTrue(namespace["is_clarification_reply"]("for all"))

    def test_semester_lookup_keeps_every_supported_requested_batch(self):
        records = [
            {
                "is_course_record": True, "semester": "3", "programme": "B.Tech",
                "source": "Semester_Spread_Structures_Sept_2026.xlsx", "batch": "2025",
                "course_code": "MATH209",
            },
            {
                "is_course_record": True, "semester": "3", "programme": "B.Tech",
                "source": "Semester_Spread_Structures_Sept_2026.xlsx", "batch": "2026",
                "course_code": "MATH210",
            },
            {
                "is_course_record": True, "semester": "3", "programme": "B.Tech",
                "source": "Semester_Spread_Structures_Sept_2026.xlsx", "batch": "2024",
                "course_code": "MATH208",
            },
        ]
        found = namespace["course_records_for_semester"](
            "B.Tech semester 3 for 2021 and 2026", records
        )
        self.assertEqual({row["batch"] for row in found}, {"2026"})

    def test_course_code_lookup_does_not_change_code_normalisation(self):
        records = [{"course_code": "UCOR205", "batch": "2026"}]
        found = namespace["course_records_for_code"]("UCOR-205", records)
        self.assertEqual(len(found), 1)


if __name__ == "__main__":
    unittest.main()
