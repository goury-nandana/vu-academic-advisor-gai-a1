"""Deterministic guardrails for the VU Academic Advisor chat flow."""
from __future__ import annotations
import re

PERSONAL_KNOWLEDGE_RE = re.compile(
    r"\b(what do you know about me|tell me about myself|what do you know abt me|"
    r"who am i|describe me|what is my (?:name|cgpa|gpa|programme|program|semester))\b", re.I)
ACKNOWLEDGEMENT_RE = re.compile(
    r"^\s*(oh+|ok(?:ay)?|got it|understood|right|i see|hmm+|alright|sure|"
    r"thanks?|thank you|thx|ty|cool|nice|great)\s*[.!?]*\s*$", re.I)
CHALLENGE_RE = re.compile(
    r"\b(?:wrong|incorrect|a lie|not true|made that up|false|inaccurate)\b|"
    r"\bno,?\s+that'?s?\s+(?:a )?lie\b", re.I)
UNSUPPORTED_PROFILE_CLAIM_RE = re.compile(
    r"\b(?:you[’']?re|you are)\s+.{0,120}\b(?:student|semester|cgpa|gpa|credits?)\b|"
    r"\b(?:your|you have)\s+.{0,50}\b(?:cgpa|gpa|credits?|semester)\b", re.I)

def is_personal_knowledge_question(text: str) -> bool:
    return bool(PERSONAL_KNOWLEDGE_RE.search(str(text or "")))

def is_acknowledgement(text: str) -> bool:
    return bool(ACKNOWLEDGEMENT_RE.fullmatch(str(text or "")))

def is_answer_challenge(text: str) -> bool:
    return bool(CHALLENGE_RE.search(str(text or "")))

def should_retract_personal_claim(answer: str) -> bool:
    return bool(UNSUPPORTED_PROFILE_CLAIM_RE.search(str(answer or "")))

def personal_knowledge_reply(profile: dict | None = None) -> str:
    supplied = []
    for key, label in (("program", "programme"), ("semester", "semester"),
                       ("completed_credits", "completed credits"), ("cgpa", "CGPA")):
        value = (profile or {}).get(key)
        if value not in (None, "", "Not specified"):
            supplied.append(f"{label}: {value}")
    if supplied:
        return ("I only know the details you have explicitly entered or shared here: "
                + "; ".join(supplied)
                + ". I do not have access to your university records or private student profile.")
    return ("I only know what you explicitly share in this chat. I do not have access to your "
            "university records, identity, grades or private student profile.")

def acknowledgement_reply() -> str:
    return ("Understood. Your earlier question remains in the conversation; you can ask a "
            "follow-up whenever you are ready.")

def correction_reply() -> str:
    return ("You're right to challenge that. I cannot verify personal details from your university "
            "records, and I retract any personal or academic profile claim that you did not provide. "
            "Only details you explicitly share here or enter in the optional profile should be used.")


def wrap_untrusted_material(material: str, label: str = "retrieved sources and student attachments") -> str:
    """Wrap retrieved/uploaded content as data and escape tag-like delimiters.

    This is a deterministic prompt-hardening boundary, not a guarantee that
    a probabilistic language model will resist every prompt injection.
    """
    safe_label = re.sub(r"[^a-zA-Z0-9 _-]", "", str(label or "untrusted material"))[:80]
    safe_material = (
        str(material or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<UNTRUSTED_MATERIAL label=\"{safe_label}\">\n{safe_material}\n</UNTRUSTED_MATERIAL>"
