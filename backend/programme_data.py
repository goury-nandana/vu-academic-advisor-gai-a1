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


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def _text(value):
    return re.sub(r"\s+", " ", str(value)).strip() if value is not None else ""


def _header_map(row):
    return {_norm(v): i for i, v in enumerate(row) if v is not None and _norm(v)}


def _col(mapping, *names):
    return next((mapping[n] for n in names if n in mapping), None)


def _batch(ws, row):
    for r in range(row, 0, -1):
        for c in range(1, min(ws.max_column, 4) + 1):
            match = re.search(r"\b(20\d{2})\s*batch\b", _text(ws.cell(r, c).value), re.I)
            if match:
                return match.group(1)
    return None


def _minor_records(ws, filename):
    header_row, mapping = None, {}
    for r in range(1, min(ws.max_row, 15) + 1):
        candidate = _header_map([ws.cell(r, c).value for c in range(1, ws.max_column + 1)])
        if _col(candidate, "course code", "code") is not None and _col(candidate, "course title", "course", "course name") is not None:
            header_row, mapping = r, candidate
            break
    if header_row is None:
        return []
    cols = {
        "course_code": _col(mapping, "course code", "code"),
        "course_title": _col(mapping, "course title", "course", "course name"),
        "L": _col(mapping, "l"), "T": _col(mapping, "t"), "P": _col(mapping, "p"),
        "credits": _col(mapping, "credit", "credits", "cr"),
        "semester": _col(mapping, "semester", "sem"),
        "prerequisite": _col(mapping, "pre rq", "prerequisite", "pre requisite"),
    }
    out = []
    for r in range(header_row + 1, ws.max_row + 1):
        code = ws.cell(r, cols["course_code"] + 1).value
        title = _text(ws.cell(r, cols["course_title"] + 1).value)
        if not title or key(title) in {"tbd", "to be decided"}:
            continue
        batch = _batch(ws, r)
        get = lambda name: ws.cell(r, cols[name] + 1).value if cols[name] is not None else None
        prereq = _text(get("prerequisite")) or None
        record = {
            "document_type": "minor_course",
            "programme": "B.Tech" if "btech" in filename.casefold() else None,
            "minor": ws.title.strip(), "batch": batch,
            "course_code": _text(code) or None, "course_title": title,
            "L": get("L"), "T": get("T"), "P": get("P"),
            "credits": get("credits"), "semester": get("semester"),
            "prerequisite": prereq, "source": filename, "sheet": ws.title,
            "cells": {name: ws.cell(r, idx + 1).coordinate for name, idx in cols.items() if idx is not None},
        }
        record["text"] = (
            f"{record['minor']} minor; batch {batch or 'not specified'}; "
            f"{record['course_code'] or 'course code not provided'} — {title}; "
            f"semester {record['semester'] if record['semester'] is not None else 'not specified'}; "
            f"credits {record['credits'] if record['credits'] is not None else 'not specified'}; "
            f"prerequisite {prereq or 'not specified'}; L-T-P "
            f"{record['L'] if record['L'] is not None else 'not specified'}-"
            f"{record['T'] if record['T'] is not None else 'not specified'}-"
            f"{record['P'] if record['P'] is not None else 'not specified'}."
        )
        out.append(record)
    return out


def _programme_records(ws, filename):
    out, seen = [], set()
    match = re.search(r"(?:^|[^0-9])(20\d{2})(?:$|[^0-9])", ws.title)
    batch = match.group(1) if match else None
    for header_row in range(1, min(ws.max_row, 20) + 1):
        headers = [
            (i, _text(ws.cell(header_row, i + 1).value))
            for i in range(ws.max_column)
            if ws.cell(header_row, i + 1).value is not None
            and re.search(r"\bcourses?\b|\belectives?\b", _text(ws.cell(header_row, i + 1).value), re.I)
        ]
        for title_idx, heading in headers:
            credit_idx = title_idx + 1
            if key(ws.cell(header_row, credit_idx + 1).value) not in {"cr", "credit", "credits"}:
                continue
            group = re.sub(r"\s*[-–—]\s*Courses?\s*$", "", heading, flags=re.I).strip() or "Electives"
            for r in range(header_row + 1, ws.max_row + 1):
                title = _text(ws.cell(r, title_idx + 1).value)
                credit = ws.cell(r, credit_idx + 1).value
                if title and key(credit) in {"cr", "credit", "credits"} and re.search(r"\bcourses?\b|\belectives?\b", title, re.I):
                    break
                if not title or key(title) in {"total credits", "course", "courses", "electives"}:
                    continue
                identity = (header_row, title_idx, r, title)
                if identity in seen:
                    continue
                seen.add(identity)
                summary = bool(re.match(r"^\d+\s+courses?\s+of\b", title, re.I))
                record = {
                    "document_type": "programme_structure_note" if summary else "programme_structure_course",
                    "programme": None, "track": None, "batch": batch,
                    "structure_group": group, "course_title": title, "credits": credit,
                    "source": filename, "sheet": ws.title,
                    "cells": {"course_title": ws.cell(r, title_idx + 1).coordinate,
                              "credits": ws.cell(r, credit_idx + 1).coordinate},
                }
                record["text"] = f"{ws.title}; {group}; {title}; credits {credit if credit is not None else 'not specified'}."
                out.append(record)

    for header_row in range(1, min(ws.max_row, 8) + 1):
        mapping = _header_map([ws.cell(header_row, c).value for c in range(1, ws.max_column + 1)])
        basket_idx = _col(mapping, "baskets", "basket")
        credit_idx = _col(mapping, "credits", "credit", "credit structure")
        if basket_idx is None or credit_idx is None:
            continue
        for r in range(header_row + 1, ws.max_row + 1):
            basket = _text(ws.cell(r, basket_idx + 1).value)
            credit = ws.cell(r, credit_idx + 1).value
            if basket and isinstance(credit, (int, float)):
                out.append({
                    "document_type": "programme_credit_structure", "batch": batch,
                    "basket": basket, "credits": credit, "source": filename, "sheet": ws.title,
                    "cells": {"basket": ws.cell(r, basket_idx + 1).coordinate,
                              "credits": ws.cell(r, credit_idx + 1).coordinate},
                    "text": f"{ws.title}; basket {basket}; required credits {credit}.",
                })
        break
    return out


def extract_archive_records(raw, kind):
    if kind not in {"minor", "programme"}:
        raise ValueError("kind must be 'minor' or 'programme'")
    records = []
    with ZipFile(BytesIO(raw)) as archive:
        for filename in archive.namelist():
            if not filename.lower().endswith(".xlsx"):
                continue
            if kind == "minor" and "minor" not in filename.lower():
                continue
            wb = load_workbook(BytesIO(archive.read(filename)), read_only=False, data_only=True)
            for ws in wb.worksheets:
                if kind == "minor":
                    records.extend(_minor_records(ws, filename))
                    continue
                if kind == "programme" and re.search(r"\bstruct", ws.title, re.I):
                    records.extend(_programme_records(ws, filename))
                    continue
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
                    # Programme-structure sheets use repeated (#, course title, Cr)
                    # basket groups rather than a single Course Code/Course Title header.
                    groups = []
                    basket_header_row = None
                    for candidate in range(1, min(ws.max_row, 12) + 1):
                        found = []
                        for col in range(1, ws.max_column - 1):
                            raw_marker = str(ws.cell(candidate, col).value or "").strip()
                            marker = key(raw_marker)
                            title_header = ws.cell(candidate, col + 1).value
                            credit_header = key(ws.cell(candidate, col + 2).value)
                            if ((raw_marker == "#" or marker in {"no", "sno", "number"}) and title_header
                                and ("course" in str(title_header).lower() or "elective" in str(title_header).lower())
                                and credit_header in {"cr", "credit", "credits"}):
                                found.append((col, col + 1, col + 2, str(title_header)))
                        if len(found) >= 2:
                            basket_header_row, groups = candidate, found
                            break
                    if basket_header_row:
                        for r in range(basket_header_row + 1, ws.max_row + 1):
                            for number_col, title_col, credit_col, group_title in groups:
                                title = ws.cell(r, title_col).value
                                credits = ws.cell(r, credit_col).value
                                if title is None or credits is None or str(title).strip().lower() in {"total credits", "total credit"}:
                                    continue
                                title = re.sub(r"\\s+", " ", str(title)).strip()
                                cells = {"number": ws.cell(r, number_col).coordinate,
                                         "course_title": ws.cell(r, title_col).coordinate,
                                         "credits": ws.cell(r, credit_col).coordinate}
                                if "/" in title:
                                    text_value = f"Raw programme alternative slot: {title} (credits shown: {credits}). Not split into separate courses. Basket: {group_title}. Source: {filename}, sheet {ws.title}, cells {cells}."
                                    doc_type = "raw_elective_slot"
                                else:
                                    basket = re.sub(r"\\s*-\\s*Courses?\\s*$", "", group_title, flags=re.I).strip()
                                    text_value = f"{title}; credits: {credits}; basket: {basket}. Source: {filename}, sheet {ws.title}, row {r}."
                                    doc_type = "programme_structure_course"
                                records.append({"text": text_value, "source": filename, "sheet": ws.title,
                                    "cells": cells, "document_type": doc_type, "course_code": None,
                                    "course_title": title, "credits": credits})
                    if not basket_header_row:
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
