#!/usr/bin/env python3
"""Export the same allowlisted VU source material used by Streamlit for Next.js.

The source PDFs and curriculum workbooks remain in the repository. This script
extracts their already-curated text from app.py's embedded payload and the
validated semester-spread archive into a JSON file inside frontend/.
"""
from __future__ import annotations

import base64
import json
import re
import zlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APP_FILE = ROOT / "app.py"
OUTPUT = ROOT / "frontend" / "data" / "vu-academic-knowledge.json"
ALLOWED_SOURCES = {
    "4. Student Handbook Aug 2026.pdf",
    "SOP STUDENT 17082026 - Final.pdf",
    "Course_Plans.txt",
    "Minor_Courses_for_BTech_Students.xlsx",
}


def load_embedded_payload() -> dict[str, Any]:
    source = APP_FILE.read_text(encoding="utf-8")
    match = re.search(r'^_EMBEDDED_DATA_B64\s*=\s*"([^"]+)"', source, re.M)
    if not match:
        raise RuntimeError("The embedded VU academic knowledge base was not found in app.py.")
    try:
        payload = json.loads(zlib.decompress(base64.b64decode(match.group(1))).decode("utf-8"))
    except Exception as exc:
        raise RuntimeError("Could not decode the embedded VU academic knowledge base.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("The embedded VU academic knowledge base has an unexpected format.")
    return payload


def split_text(value: str, size: int = 160, overlap: int = 30) -> list[str]:
    words = str(value or "").split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + size)
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(start + 1, end - overlap)
    return chunks


def export_knowledge() -> dict[str, Any]:
    payload = load_embedded_payload()
    raw_documents = payload.get("documents", [])
    if not isinstance(raw_documents, list):
        raise RuntimeError("Embedded VU documents are not a list.")

    documents: list[dict[str, Any]] = []
    matching_source_names: set[str] = set()
    attendance_hits: list[dict[str, Any]] = []
    for item in raw_documents:
        if not isinstance(item, dict):
            continue
        source_name = str(item.get("source") or item.get("filename") or "").strip()
        if source_name not in ALLOWED_SOURCES:
            continue
        matching_source_names.add(source_name)
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        metadata = {
            key: item[key]
            for key in ("title", "source", "page", "sheet", "section", "url", "type", "document_type")
            if item.get(key) not in (None, "")
        }
        for chunk_number, chunk in enumerate(split_text(text), start=1):
            documents.append({
                **metadata,
                "chunk": chunk_number,
                "text": chunk,
            })
            if re.search(r"\b(attendance|attend|absence|absent|condonation|shortage)\b", chunk, re.I):
                if len(attendance_hits) < 30:
                    attendance_hits.append({
                        "source": source_name,
                        "page": metadata.get("page"),
                        "section": metadata.get("section"),
                        "excerpt": chunk[:700],
                    })

    if not documents:
        raise RuntimeError(
            "No allowlisted academic text was exported. Refusing to build a web advisor with an empty corpus."
        )

    # Keep the original workbook loader as the source of truth for B.Tech semester rows.
    course_records: list[dict[str, Any]] = []
    archive_path = ROOT / "VU_Semester_Data_Split.zip"
    if archive_path.is_file():
        from course_data import load_course_records
        course_records = load_course_records(archive_path)

    output = {
        "schemaVersion": 1,
        "generatedFrom": "app.py embedded allowlisted VU sources + VU_Semester_Data_Split.zip",
        "documents": documents,
        "courseRecords": course_records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return {
        "path": str(OUTPUT.relative_to(ROOT)),
        "documentChunks": len(documents),
        "courseRecords": len(course_records),
        "sources": sorted(matching_source_names),
        "bytes": OUTPUT.stat().st_size,
        "attendanceMatches": attendance_hits,
    }


if __name__ == "__main__":
    summary = export_knowledge()
    print("VU WEB KNOWLEDGE EXPORT")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
