import unittest

from advisor_guardrails import (
    acknowledgement_reply,
    correction_reply,
    is_acknowledgement,
    is_answer_challenge,
    is_personal_knowledge_question,
    personal_knowledge_reply,
    should_retract_personal_claim,
)


class AdvisorGuardrailTests(unittest.TestCase):
    def test_personal_knowledge_question_is_recognised(self):
        self.assertTrue(is_personal_knowledge_question("what do you know abt me?"))
        self.assertTrue(is_personal_knowledge_question("Who am I?"))

    def test_personal_knowledge_does_not_invent_records(self):
        answer = personal_knowledge_reply({})
        self.assertIn("do not have access", answer)
        self.assertNotIn("Psychology", answer)
        self.assertNotIn("9.0", answer)

    def test_only_explicit_profile_values_are_repeated(self):
        answer = personal_knowledge_reply({"program": "B.Tech", "cgpa": None})
        self.assertIn("B.Tech", answer)
        self.assertNotIn("CGPA:", answer)

    def test_acknowledgements_do_not_become_new_topics(self):
        for text in ("oh", "ok", "okay", "got it", "I see"):
            self.assertTrue(is_acknowledgement(text), text)
        self.assertIn("earlier question remains", acknowledgement_reply())

    def test_challenge_retracts_unsupported_profile_claim(self):
        self.assertTrue(is_answer_challenge("no thats a lie"))
        self.assertTrue(should_retract_personal_claim(
            "You’re a second-semester B.A. Psychology student, having completed 41 credits so far and maintaining a 9.0 CGPA."
        ))
        self.assertIn("retract", correction_reply().lower())

    def test_unrelated_answer_is_not_misclassified_as_profile_claim(self):
        self.assertFalse(should_retract_personal_claim(
            "Relative grading may depend on the course and official policy."
        ))


if __name__ == "__main__":
    unittest.main()
