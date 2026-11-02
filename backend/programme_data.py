"""Header-driven workbook extraction for the VU API service.

Explicit course-code/title pairs become structured rows. Elective and semester
slot cells remain raw evidence with workbook/sheet/cell provenance.
"""
from __future__ import annotations
from io import BytesIO
import re
from zipfile import ZipFile
from openpyxl import load_workbook

ALIASES = {
    "course_code": {"coursecode", "courseid", "code", "subjectcode"},
    "course_title": {"coursetitle", "coursename", "subject", "subjectname", "title"},
    "credits": {"credits", "credit", "creditvalue"},
    "semester": {"semester", "sem", "semesterno", "term"},
    "prerequisite": {"prerequisite", "prerequisites", "prereq"},
    "elective_slot": {"electiveslot", "elective", "slot", "basket", "electivebasket"},
}
CODE_RE = re.compile(r"^[A-Za-z]{2,8}\s*-?\s*\d{2,5}[A-Za-z]?$")

def key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower().strip())

def field(value):
    k = key(value)
    for name, aliases in ALIASES.items():
        if k in aliases or k in {key(x) for x in aliases}:
            return name
    m = re.fullmatch(r"(?:s|semester)([1-8])", k)
    return "semester_" + m.group(1) if m else None

def extract_archive_records(raw, kind):
    records = []
    with ZipFile(BytesIO(raw)) as archive:
        for filename in archive.namelist():
            if not filename.lower().endswith(".xlsx"):
                continue
            if kind == "minor" and "minor" not in filename.lower():
                continue
            if kind == "programme" and "programme_structure" not in filename.lower():
                continue
            wb = load_workbook(BytesIO(archive.read(filename)), read_only=False, data_only=True)
            for ws in wb.worksheets:
                header_row, mapped = None, []
                for r in range(1, min(ws.max_row, 20) + 1):
                    candidate = [field(ws.cell(r, col).value) for col in range(1, ws.max_column + 1)]
                    if "course_code" in candidate and "course_title" in candidate:
                        header_row, mapped = r, candidate
                        break
                if header_row:
                    for r in range(header_row + 1, ws.max_row + 1):
                        values, coords = {}, {}
                        raw_slots = []
                        for col, name in enumerate(mapped, 1):
                            value = ws.cell(r, col).value
                            if value is None or str(value).strip() == "":
                                continue
                            value = re.sub(r"\s+", " ", str(value)).strip() if isinstance(value, str) else value
                            coord = ws.cell(r, col).coordinate
                            if name == "elective_slot" or (name and name.startswith("semester_")):
                                raw_slots.append((name, value, coord))
                            elif name:
                                values[name], coords[name] = value, coord
                        code, title = values.get("course_code"), values.get("course_title")
                        if code and title and CODE_RE.fullmatch(str(code).strip()):
                            batch_match = re.search(r"(?<!\d)(2022|2023|2024|2025|2026)(?!\d)", filename)
                            parts = [f"{str(code).strip().upper()} — {title}"]
                            for label, name in (("credits", "credits"), ("semester", "semester"), ("prerequisite", "prerequisite")):
                                if values.get(name) not in (None, ""):
                                    parts.append(f"{label}: {values[name]}")
                            records.append({"text": "; ".join(parts), "source": filename, "sheet": ws.title,
                                "cells": coords, "document_type": "minor_course" if kind == "minor" else "programme_structure_course",
                                "course_code": str(code).strip().upper(), "course_title": str(title),
                                "batch": batch_match.group(1) if batch_match else None})
                        for name, value, coord in raw_slots:
                            records.append({"text": f"Raw {name} slot: {value}. Not normalized into a course. Source: {filename}, sheet {ws.title}, cell {coord}.",
                                "source": filename, "sheet": ws.title, "cells": {name: coord},
                                "document_type": "raw_elective_slot" if name == "elective_slot" else "raw_programme_slot"})
                else:
                    slot_row, slot_cols = None, []
                    for r in range(1, min(ws.max_row, 20) + 1):
                        cols = [(col, ws.cell(r, col).value) for col in range(1, ws.max_column + 1)
                                if field(ws.cell(r, col).value) == "elective_slot"]
                        if cols:
                            slot_row, slot_cols = r, cols
                            break
                    if slot_row:
                        for r in range(slot_row + 1, ws.max_row + 1):
                            for col, header in slot_cols:
                                value = ws.cell(r, col).value
                                if value is None or str(value).strip() == "":
                                    continue
                                coord = ws.cell(r, col).coordinate
                                records.append({"text": f"Raw elective slot: {value}. Not normalized into a course. Source: {filename}, sheet {ws.title}, cell {coord}.",
                                    "source": filename, "sheet": ws.title, "cells": {"slot": coord},
                                    "document_type": "raw_elective_slot"})
            wb.close()
    return records
