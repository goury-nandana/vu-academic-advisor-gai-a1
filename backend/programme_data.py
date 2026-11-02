"""Header-driven loaders for minor and programme-structure workbooks.

Only explicit header/value pairs become course records. Unmapped or ambiguous
cells are retained as raw elective-slot records with provenance; they are never
split into guessed course codes, titles, credits, or semesters.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
from zipfile import ZipFile

from openpyxl import load_workbook

MINOR_ARCHIVE = Path(__file__).resolve().parent / "VU_Minor_Data_Split.zip"
PROGRAMME_ARCHIVE = Path(__file__).resolve().parent / "VU_Semester_Data_Split.zip"

ALIASES = {
    "course_code": {"coursecode", "courseid", "code", "subjectcode", "paper code"},
    "course_title": {"coursetitle", "coursename", "subject", "subjectname", "title", "papername"},
    "credits": {"credits", "credit", "creditvalue", "noofcredits"},
    "semester": {"semester", "sem", "semestername", "semesterno", "term"},
    "prerequisite": {"prerequisite", "prerequisites", "prereq", "pre requisite"},
    "programme": {"programme", "program", "programmename", "programname", "degree"},
    "minor_name": {"minor", "minorname", "minorarea", "specialisation", "specialization"},
    "elective_slot": {"electiveslot", "elective", "slot", "basket", "electivebasket", "electivegroup"},
    "course_type": {"coursetype", "type", "category", "coursecategory", "basketname"},
    "ltp": {"ltp", "l-t-p", "lecturetutorialpractical"},
}
CODE_RE = re.compile(r"^[A-Za-z]{2,8}\s*-?\s*\d{2,5}[A-Za-z]?$")


def _header_key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def _field_for_header(value):
    key = _header_key(value)
    for field, aliases in ALIASES.items():
        if key in {_header_key(alias) for alias in aliases}:
            return field
    # Explicit semester headers such as S1/S2 are safe numeric labels.
    match = re.fullmatch(r"s([1-8])", key)
    if match:
        return "semester_" + match.group(1)
    match = re.fullmatch(r"semester([1-8])", key)
    if match:
        return "semester_" + match.group(1)
    return None


def _metadata_from_filename(filename, sheet_name=None):
    name = Path(sheet_name).stem if sheet_name else Path(filename).stem
    batch_match = re.search(r"(?<!\d)(2022|2023|2024|2025|2026)(?!\d)", name)
    programme = "B.Tech" if re.search(r"btech", name, re.I) else None
    return {
        "batch": batch_match.group(1) if batch_match else None,
        "programme": programme,
    }


def _cell_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = re.sub(r"\s+", " ", value).strip()
        return value or None
    return value


def _header_row(ws, max_scan=20):
    for row_idx in range(1, min(ws.max_row, max_scan) + 1):
        mapped = [_field_for_header(ws.cell(row_idx, col).value) for col in range(1, ws.max_column + 1)]
        if "course_code" in mapped and "course_title" in mapped:
            return row_idx, mapped
    return None, []


def _basket_header_groups(ws, max_scan=20):
    """Find every explicit (#, course-list title, credits) header group."""
    result = []
    for row_idx in range(1, min(ws.max_row, max_scan) + 1):
        groups = []
        for col_idx in range(1, ws.max_column - 1):
            raw_marker = str(ws.cell(row_idx, col_idx).value or "").strip()
            marker = _header_key(raw_marker)
            title_header = _cell_value(ws.cell(row_idx, col_idx + 1).value)
            credit_header = _header_key(ws.cell(row_idx, col_idx + 2).value)
            if (
                (raw_marker == "#" or marker in {"no", "sno", "number"})
                and title_header
                and ("course" in str(title_header).lower() or "elective" in str(title_header).lower())
                and credit_header in {"cr", "credit", "credits"}
            ):
                groups.append((col_idx, col_idx + 1, col_idx + 2, str(title_header)))
        if groups:
            result.append((row_idx, groups))
    return result


def _records_from_basket_layout(ws, filename, metadata):
    header_blocks = _basket_header_groups(ws)
    records = []
    for header_idx, groups in header_blocks:
        for number_col, title_col, credit_col, group_title in groups:
            for row_idx in range(header_idx + 1, ws.max_row + 1):
                title = _cell_value(ws.cell(row_idx, title_col).value)
                credits = _cell_value(ws.cell(row_idx, credit_col).value)
                # A later header in the same columns starts a new table, not a course row.
                if title and _header_key(credits) in {"cr", "credit", "credits"} and (
                    "course" in title.lower() or "elective" in title.lower()
                ):
                    break
                if title is None or credits is None or str(title).strip().lower() in {"total credits", "total credit"}:
                    continue
                title = str(title).strip()
                cells = {
                    "number": ws.cell(row_idx, number_col).coordinate,
                    "course_title": ws.cell(row_idx, title_col).coordinate,
                    "credits": ws.cell(row_idx, credit_col).coordinate,
                }
                if re.match(r"^\d+\s+courses?\s+of\b", title, re.I):
                    records.append({
                        "is_course_record": False,
                        "document_type": "programme_structure_note",
                        "raw_value": title,
                        "raw_credits": credits,
                        "programme": metadata["programme"],
                        "batch": metadata["batch"],
                        "source": filename,
                        "sheet": ws.title,
                        "cells": cells,
                        "text": f"Programme structure note: {title}; credits shown: {credits}. Source: {filename}, sheet {ws.title}, cells {cells}.",
                    })
                    continue
                if "/" in title:
                    records.append({
                        "is_course_record": False,
                        "document_type": "raw_elective_slot",
                        "slot_header": group_title,
                        "raw_value": title,
                        "raw_credits": credits,
                        "programme": metadata["programme"],
                        "batch": metadata["batch"],
                        "source": filename,
                        "sheet": ws.title,
                        "cells": cells,
                        "text": f"Raw programme alternative slot: {title} (credits shown: {credits}). Not split into separate courses. Basket: {group_title}. Source: {filename}, sheet {ws.title}, cells {cells}.",
                    })
                    continue
                basket = re.sub(r"\s*-\s*Courses?\s*$", "", group_title, flags=re.I).strip()
                record = {
                    "is_course_record": False,
                    "document_type": "programme_structure_course",
                    "course_code": None,
                    "course_title": title,
                    "credits": credits,
                    "semester": None,
                    "programme": metadata["programme"],
                    "batch": metadata["batch"],
                    "course_type": basket,
                    "source": filename,
                    "sheet": ws.title,
                    "cells": cells,
                }
                parts = [title, f"credits: {credits}", f"basket: {basket}"]
                if record["programme"]:
                    parts.append(f"programme: {record['programme']}")
                if record["batch"]:
                    parts.append(f"admission batch: {record['batch']}")
                record["text"] = "; ".join(parts) + f". Source: {filename}, sheet {ws.title}, row {row_idx}."
                records.append(record)

    # Read basket credit requirements from an explicit Baskets/Credits header pair.
    for header_row in range(1, min(ws.max_row, 8) + 1):
        header = {_header_key(ws.cell(header_row, col).value): col for col in range(1, ws.max_column + 1)
                  if ws.cell(header_row, col).value is not None}
        basket_col = next((header[k] for k in ("baskets", "basket") if k in header), None)
        credit_col = next((header[k] for k in ("credits", "credit", "creditstructure") if k in header), None)
        if basket_col and credit_col:
            for row_idx in range(header_row + 1, ws.max_row + 1):
                basket = _cell_value(ws.cell(row_idx, basket_col).value)
                credits = ws.cell(row_idx, credit_col).value
                if basket and isinstance(credits, (int, float)):
                    records.append({
                        "is_course_record": False,
                        "document_type": "programme_credit_structure",
                        "basket": basket,
                        "credits": credits,
                        "programme": metadata["programme"],
                        "batch": metadata["batch"],
                        "source": filename,
                        "sheet": ws.title,
                        "cells": {"basket": ws.cell(row_idx, basket_col).coordinate,
                                  "credits": ws.cell(row_idx, credit_col).coordinate},
                        "text": f"{ws.title}; basket {basket}; required credits {credits}. Source: {filename}, row {row_idx}.",
                    })
            break
    return records


def _records_from_sheet(ws, filename, kind):
    header_idx, mapped = _header_row(ws)
    metadata = _metadata_from_filename(filename, ws.title)
    records = []
    if not header_idx and kind == "programme":
        basket_records = _records_from_basket_layout(ws, filename, metadata)
        if basket_records:
            return basket_records
    if header_idx:
        for row_idx in range(header_idx + 1, ws.max_row + 1):
            row_batch = _explicit_batch_from_sheet(ws, row_idx) or metadata["batch"]
            values = {}
            cells = {}
            raw_slots = []
            for col_idx, field in enumerate(mapped, start=1):
                value = _cell_value(ws.cell(row_idx, col_idx).value)
                if value is None:
                    continue
                coord = ws.cell(row_idx, col_idx).coordinate
                if field == "elective_slot" or (field and field.startswith("semester_")):
                    raw_slots.append((field, value, coord))
                elif field:
                    values[field] = value
                    cells[field] = coord
            code = values.get("course_code")
            title = values.get("course_title")
            if code and title and CODE_RE.fullmatch(str(code).strip()):
                semester = values.get("semester")
                if semester is None:
                    explicit_semesters = [f"semester_{i}" for i in range(1, 9) if f"semester_{i}" in values]
                    if len(explicit_semesters) == 1:
                        semester = int(explicit_semesters[0].split("_")[1])
                record = {
                    "is_course_record": True,
                    "document_type": "minor_course" if kind == "minor" else "programme_structure_course",
                    "course_code": re.sub(r"\s+", "", str(code)).upper(),
                    "course_title": str(title),
                    "credits": values.get("credits"),
                    "semester": semester,
                    "prerequisite": values.get("prerequisite"),
                    "programme": values.get("programme") or metadata["programme"],
                    "minor_name": values.get("minor_name") or (ws.title if kind == "minor" else None),
                    "batch": row_batch,
                    "course_type": values.get("course_type"),
                    "ltp": values.get("ltp"),
                    "source": filename,
                    "sheet": ws.title,
                    "cells": cells,
                }
                parts = [f"{record['course_code']} — {record['course_title']}"]
                for label, key in (("credits", "credits"), ("semester", "semester"), ("prerequisite", "prerequisite"), ("course type", "course_type"), ("L-T-P", "ltp")):
                    if record.get(key) not in (None, ""):
                        parts.append(f"{label}: {record[key]}")
                if record.get("minor_name"):
                    parts.append(f"minor: {record['minor_name']}")
                if record.get("programme"):
                    parts.append(f"programme: {record['programme']}")
                if record.get("batch"):
                    parts.append(f"admission batch: {record['batch']}")
                record["text"] = "; ".join(parts) + f". Source: {filename}, sheet {ws.title}, row {row_idx}."
                records.append(record)
            if title and (not code or not CODE_RE.fullmatch(str(code).strip())) and str(title).strip().lower() not in {"tbd", "to be decided"}:
                raw_value = f"{code or 'Course code not provided'} — {title}"
                records.append({
                    "is_course_record": False,
                    "document_type": "raw_elective_slot",
                    "slot_header": "unresolved course row",
                    "raw_value": raw_value,
                    "programme": values.get("programme") or metadata["programme"],
                    "minor_name": values.get("minor_name") or (ws.title if kind == "minor" else None),
                    "batch": row_batch,
                    "source": filename,
                    "sheet": ws.title,
                    "cells": {"course_code": cells.get("course_code", ws.cell(row_idx, 1).coordinate),
                              "course_title": cells.get("course_title", ws.cell(row_idx, 1).coordinate)},
                    "text": f"Unresolved source row: {raw_value}. Code/title pair is not normalized into a course. Source: {filename}, sheet {ws.title}, row {row_idx}.",
                })
            # Preserve slot values separately. Do not infer course details from them.
            for field, value, coord in raw_slots:
                records.append({
                    "is_course_record": False,
                    "document_type": "raw_elective_slot" if field == "elective_slot" else "raw_programme_slot",
                    "slot_header": field,
                    "raw_value": value,
                    "programme": values.get("programme") or metadata["programme"],
                    "minor_name": values.get("minor_name"),
                    "batch": row_batch,
                    "source": filename,
                    "sheet": ws.title,
                    "cells": {field: coord},
                    "text": f"Raw {('elective' if field == 'elective_slot' else 'programme semester')} slot ({field}): {value}. Not normalized into a course. Source: {filename}, sheet {ws.title}, cell {coord}.",
                })
        return records

    # No course-code/title header pair: retain explicit elective/slot columns as raw values.
    # Search for the header row rather than assuming it is the first row.
    slot_header_row = None
    slot_columns = []
    for candidate in range(1, min(ws.max_row, 20) + 1):
        cols = [(col, ws.cell(candidate, col).value) for col in range(1, ws.max_column + 1)
                if _field_for_header(ws.cell(candidate, col).value) == "elective_slot"]
        if cols:
            slot_header_row, slot_columns = candidate, cols
            break
    if slot_header_row:
        for row_idx in range(slot_header_row + 1, ws.max_row + 1):
            for col_idx, header_value in slot_columns:
                value = _cell_value(ws.cell(row_idx, col_idx).value)
                if value is None:
                    continue
                coord = ws.cell(row_idx, col_idx).coordinate
                records.append({
                    "is_course_record": False,
                    "document_type": "raw_elective_slot",
                    "slot_header": str(header_value),
                    "raw_value": value,
                    "programme": metadata["programme"],
                    "batch": metadata["batch"],
                    "source": filename,
                    "sheet": ws.title,
                    "cells": {"slot": coord},
                    "text": f"Raw elective slot: {value}. Not normalized into a course. Source: {filename}, sheet {ws.title}, cell {coord}.",
                })
    return records


def _load_archive(archive_path, filename_filter, kind):
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise FileNotFoundError(f"Required workbook archive not found: {archive_path.name}")
    records = []
    with ZipFile(archive_path) as archive:
        for filename in archive.namelist():
            if not filename.lower().endswith(".xlsx") or not filename_filter(filename):
                continue
            wb = load_workbook(BytesIO(archive.read(filename)), read_only=False, data_only=True)
            for ws in wb.worksheets:
                records.extend(_records_from_sheet(ws, filename, kind))
            wb.close()
    return _dedupe(records)


def _dedupe(records):
    unique, seen = [], set()
    for record in records:
        cells = record.get("cells") or {}
        identity = (record.get("document_type"), record.get("source"), record.get("sheet"), tuple(sorted(cells.items())))
        if identity not in seen:
            seen.add(identity)
            unique.append(record)
    return unique


def load_minor_records(archive_path=MINOR_ARCHIVE):
    """Load minor courses and preserve ambiguous elective slots as raw records."""
    return _load_archive(archive_path, lambda name: "minor" in name.lower(), "minor")


def load_programme_structure_records(archive_path=PROGRAMME_ARCHIVE):
    """Load programme-structure course rows and raw elective slots by explicit headers."""
    return _load_archive(
        archive_path,
        lambda name: any(token in name.lower() for token in ("programme_structure", "semester_spread_structures", "semester_data_split")),
        "programme",
    )


def load_minor_and_programme_records(minor_archive=MINOR_ARCHIVE, programme_archive=PROGRAMME_ARCHIVE):
    return load_minor_records(minor_archive) + load_programme_structure_records(programme_archive)


def extract_archive_records(raw, kind):
    """API-service adapter: parse uploaded ZIP bytes with the canonical workbook builders."""
    if kind not in {"minor", "programme"}:
        raise ValueError("kind must be 'minor' or 'programme'")
    records = []
    with ZipFile(BytesIO(raw)) as archive:
        for filename in archive.namelist():
            if not filename.lower().endswith(".xlsx"):
                continue
            if kind == "minor" and "minor" not in filename.lower():
                continue
            workbook = load_workbook(BytesIO(archive.read(filename)), read_only=False, data_only=True)
            try:
                for ws in workbook.worksheets:
                    records.extend(_records_from_sheet(ws, filename, kind))
            finally:
                workbook.close()
    return _dedupe(records)
