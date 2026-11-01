"""Run the same VU benchmark questions against up to ten Groq-hosted models.

Uses the configured Groq API key and free-tier access only; it never requests payment.
All models receive the same question-specific source context and the same system prompt.
The rubric scores are left blank for human evaluation rather than fabricated by a second LLM.
"""
from __future__ import annotations

import argparse
import ast
import base64
import csv
import json
import os
import re
import time
import zlib
from pathlib import Path

from groq import Groq
from openpyxl import load_workbook

from course_data import load_course_records, course_records_for_question

ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "VU_LLM_Benchmark_Framework.xlsx"
OUTPUT_FILE = ROOT / "benchmark_results.csv"
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b",
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "moonshotai/kimi-k2-instruct",
    "allam-2-7b",
]
SYSTEM_PROMPT = """You are VU's academic advisor. Answer only from the supplied VU source context.
Do not invent student details, policies, course codes, credits, prerequisites, semester,
L-T-P values or eligibility rules. If evidence is missing or cohort-specific, say so and
ask one necessary clarification. If the source does not establish a fact, say that.
Use the same factual-grounding standard for every question. Do not use outside knowledge."""


def load_embedded_documents():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    match = re.search(r'^_EMBEDDED_DATA_B64\s*=\s*"([^"]+)"', source, re.M)
    if not match:
        raise RuntimeError("Could not locate the embedded VU source bundle in app.py.")
    payload = json.loads(zlib.decompress(base64.b64decode(match.group(1))).decode("utf-8"))
    return payload.get("documents", [])


def tokens(text):
    stop = {"the", "a", "an", "is", "are", "in", "on", "for", "to", "of", "what", "which", "how"}
    return [w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in stop]


def source_context(question, course_rows, documents):
    exact_rows = course_records_for_question(question, course_rows)
    if exact_rows:
        # The same batch-specific row set is provided to every model.
        return "\n".join(row["text"] + f" Source: {row['source']}; cells: {row['cells']}"
                         for row in exact_rows[:12])
    query_terms = set(tokens(question))
    scored = []
    for doc in documents:
        text = str(doc.get("text", ""))
        doc_terms = set(tokens(text))
        overlap = len(query_terms & doc_terms)
        if overlap:
            metadata = " | ".join(str(doc.get(k, "")) for k in ("source", "page", "sheet", "section"))
            scored.append((overlap / max(1, len(query_terms)), metadata, text))
    scored.sort(key=lambda item: item[0], reverse=True)
    return "\n\n".join(f"Source: {meta}\n{text}" for _, meta, text in scored[:6])


def read_questions(path, limit=None):
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["Benchmark Questions"]
    questions = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0] or not row[3]:
            continue
        questions.append({
            "id": str(row[0]), "set": str(row[1] or ""),
            "subcategory": str(row[2] or ""), "question": str(row[3]),
            "expected_behaviour": str(row[4] or ""),
            "gold_facts": str(row[5] or ""),
            "source_reference": str(row[6] or ""),
            "scoring_notes": str(row[7] or ""),
        })
    wb.close()
    return questions[:limit] if limit else questions


def available_models(client):
    try:
        listed = {getattr(item, "id", "") for item in client.models.list().data}
    except Exception as exc:
        raise RuntimeError(f"Could not list models from the configured Groq account: {exc}") from exc
    return [model for model in CANDIDATE_MODELS if model in listed]


def run_benchmark(limit=None, output_path=OUTPUT_FILE):
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set GROQ_API_KEY in the environment; do not add paid API access.")
    client = Groq(api_key=key)
    models = available_models(client)
    if len(models) < 10:
        raise RuntimeError(
            f"Only {len(models)} of the ten configured free-access candidates are currently "
            "listed for this Groq account. No results were generated; do not substitute paid access."
        )
    models = models[:10]
    questions = read_questions(QUESTIONS_FILE, limit)
    course_rows = load_course_records()
    documents = load_embedded_documents()
    output_fields = [
        "question_id", "set", "subcategory", "question", "model", "response",
        "latency_seconds", "accuracy_0_4", "grounding_0_4",
        "no_hallucination_0_4", "context_clarification_0_4",
        "input_tokens", "output_tokens", "error",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        for item in questions:
            context = source_context(item["question"], course_rows, documents)
            prompt = (
                f"Expected behaviour: {item['expected_behaviour']}\n"
                f"Authoritative source reference (for evaluator only): {item['source_reference']}\n\n"
                f"VU SOURCE CONTEXT:\n{context or '[No supporting source retrieved]'}\n\n"
                f"STUDENT QUESTION:\n{item['question']}"
            )
            for model in models:
                started = time.perf_counter()
                row = {
                    "question_id": item["id"], "set": item["set"],
                    "subcategory": item["subcategory"], "question": item["question"],
                    "model": model, "response": "", "latency_seconds": "",
                    "accuracy_0_4": "", "grounding_0_4": "",
                    "no_hallucination_0_4": "", "context_clarification_0_4": "",
                    "input_tokens": "", "output_tokens": "", "error": "",
                }
                try:
                    result = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                  {"role": "user", "content": prompt}],
                        temperature=0.1, max_tokens=800,
                    )
                    row["response"] = result.choices[0].message.content or ""
                    row["input_tokens"] = getattr(result.usage, "prompt_tokens", "")
                    row["output_tokens"] = getattr(result.usage, "completion_tokens", "")
                except Exception as exc:
                    row["error"] = f"{type(exc).__name__}: {exc}"
                row["latency_seconds"] = round(time.perf_counter() - started, 3)
                writer.writerow(row)
                handle.flush()
    return {"questions": len(questions), "models": models, "output": str(output_path)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None,
                        help="Optional question limit for a small smoke run.")
    parser.add_argument("--output", default=str(OUTPUT_FILE))
    args = parser.parse_args()
    print(json.dumps(run_benchmark(args.limit, Path(args.output)), indent=2))
