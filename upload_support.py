"""Safe extraction helpers for user-provided files and voice recordings."""
from __future__ import annotations

import io
import os
from pathlib import Path

MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_TEXT_CHARS_PER_FILE = 18000
SUPPORTED_EXTENSIONS = {
    "pdf", "docx", "doc", "txt", "md", "csv", "xlsx", "xls", "pptx",
    "png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff", "mp3", "wav", "m4a", "ogg", "flac",
}


def extract_document_text(uploaded_file) -> str:
    """Extract readable text from common document formats; never execute uploaded content."""
    name = getattr(uploaded_file, "name", "uploaded_file")
    ext = Path(name).suffix.lower().lstrip(".")
    data = uploaded_file.getvalue()
    if len(data) > MAX_FILE_BYTES:
        raise ValueError(f"{name}: file exceeds the 15 MB limit.")
    if ext in {"txt", "md", "csv"}:
        return data.decode("utf-8-sig", errors="replace")[:MAX_TEXT_CHARS_PER_FILE]
    if ext == "pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for index, page in enumerate(reader.pages[:40], start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {index}]\n{text}")
        return "\n\n".join(pages)[:MAX_TEXT_CHARS_PER_FILE]
    if ext == "docx":
        from docx import Document
        doc = Document(io.BytesIO(data))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(parts)[:MAX_TEXT_CHARS_PER_FILE]
    if ext == "xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        parts = []
        for ws in wb.worksheets:
            parts.append(f"[Sheet: {ws.title}]")
            for row in ws.iter_rows(values_only=True):
                values = [str(v) for v in row if v is not None]
                if values:
                    parts.append(" | ".join(values))
        wb.close()
        return "\n".join(parts)[:MAX_TEXT_CHARS_PER_FILE]
    if ext == "pptx":
        from pptx import Presentation
        prs = Presentation(io.BytesIO(data))
        parts = []
        for index, slide in enumerate(prs.slides, start=1):
            lines = [shape.text for shape in slide.shapes if getattr(shape, "has_text_frame", False) and shape.text.strip()]
            if lines:
                parts.append(f"[Slide {index}]\n" + "\n".join(lines))
        return "\n\n".join(parts)[:MAX_TEXT_CHARS_PER_FILE]
    if ext in {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"}:
        # Image content is sent to a vision-capable model separately, not treated as OCR text.
        return ""
    if ext in {"mp3", "wav", "m4a", "ogg", "flac"}:
        raise ValueError("Audio uploads are transcribed through the Groq audio endpoint.")
    if ext == "doc":
        raise ValueError("Legacy .doc files are not supported. Save as .docx or PDF.")
    if ext == "xls":
        raise ValueError("Legacy .xls files are not supported. Save as .xlsx or CSV.")
    raise ValueError(f"Unsupported file type: .{ext or 'unknown'}")


def transcribe_audio(client, audio_bytes: bytes, filename: str = "voice_input.wav") -> str:
    """Transcribe a recorded audio clip using Groq's speech-to-text endpoint."""
    if not audio_bytes:
        raise ValueError("The recording is empty.")
    if len(audio_bytes) > MAX_FILE_BYTES:
        raise ValueError("The recording exceeds the 15 MB limit.")
    result = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="text",
    )
    return str(result).strip()


def describe_image(client, image_bytes: bytes, filename: str) -> str:
    """Extract visible information from an image using a Groq vision model."""
    import base64
    import mimetypes

    if len(image_bytes) > MAX_FILE_BYTES:
        raise ValueError(f"{filename}: image exceeds the 15 MB limit.")
    mime = mimetypes.guess_type(filename)[0] or "image/jpeg"
    encoded = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{encoded}"
    errors = []
    for model in (
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.2-90b-vision-preview",
    ):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "Read and describe the useful information visible in this image. "
                            "Transcribe text accurately. Preserve numbers, labels and tables. "
                            "If something is unclear, say so; do not guess."
                        )},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }],
                temperature=0.1,
                max_tokens=1200,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            errors.append(f"{model}: {exc}")
    raise RuntimeError("Image understanding is unavailable for the configured Groq models. " + " | ".join(errors))


def uploaded_files_context(files, client) -> tuple[str, list[str]]:
    """Return extracted file context and user-readable processing notes."""
    sections, notes = [], []
    for uploaded in files or []:
        name = getattr(uploaded, "name", "uploaded file")
        ext = Path(name).suffix.lower().lstrip(".")
        try:
            if ext in {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"}:
                extracted = describe_image(client, uploaded.getvalue(), name)
            elif ext in {"mp3", "wav", "m4a", "ogg", "flac"}:
                extracted = "Voice transcript: " + transcribe_audio(client, uploaded.getvalue(), name)
            else:
                extracted = extract_document_text(uploaded)
            if extracted.strip():
                sections.append(f"USER-UPLOADED FILE: {name}\n{extracted}")
                notes.append(f"Read {name}")
            else:
                notes.append(f"No readable text found in {name}")
        except Exception as exc:
            notes.append(f"Could not read {name}: {exc}")
    return "\n\n".join(sections)[:50000], notes
