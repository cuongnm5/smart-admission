from __future__ import annotations

import json
import logging
import os
from typing import List, Tuple

from openai import OpenAI
from pydantic import ValidationError

from app.schemas.request import StudentMatchRequest

LOGGER = logging.getLogger(__name__)

PARSE_PROMPT = """\
You are an expert university admissions data extractor.

The attached file is a student's CV / resume / academic profile.
Parse it and return a single JSON object that strictly matches the schema below.
If a field is not found in the document, use sensible defaults (empty lists, null, or 0 where appropriate).
Always include every required field.

SCHEMA:
{
  "student_id": "<student name slug, lowercase, underscores>",
  "academic": {
    "gpa": [{ "year": "<e.g. 2024>", "value": <float 0-4>, "scale": 4.0 }],
    "class_rank": null | { "value": <int>, "total_students": <int> },
    "school_profile": null | { "school_name": "<str>", "school_type": "<str>", "location": "<str>", "description": "<str>" },
    "transcript": []
  },
  "test_scores": {
    "english_tests": [{ "type": "IELTS|TOEFL|Duolingo", "score": <float>, "section_scores": {} }],
    "sat": null | { "total": <int 0-1600>, "math": null, "reading_writing": null },
    "act": null | { "composite": <float 0-36>, "sections": {} },
    "ap_ib": [{ "subject": "<str>", "score": <float> }]
  },
  "intended_major": "<str>",
  "extracurriculars": [
    { "activity_name": "<str>", "role": "<str>", "organization": "<str>",
      "start_date": "<YYYY-MM>", "end_date": "<YYYY-MM>",
      "hours_per_week": <float>, "description": "<str>" }
  ],
  "leadership": [
    { "position": "<str>", "organization": "<str>", "description": "<str>", "duration": "<str>" }
  ],
  "awards": [
    { "award_name": "<str>", "organizer": "<str>", "level": "<str>", "year": <int>, "description": "<str>" }
  ],
  "projects": [
    { "project_name": "<str>", "role": "<str>", "description": "<str>",
      "link": null | "<str>", "start_date": "<YYYY-MM>", "end_date": "<YYYY-MM>" }
  ],
  "essays": { "personal_statement": null, "supplemental_essays": [] },
  "recommendation_letters": [],
  "financial": {
    "budget_per_year": 60000,
    "currency": "USD",
    "need_scholarship": false,
    "scholarship_expectation_percent": null,
    "family_income_range": null
  },
  "preferences": {
    "dream_major": null,
    "target_schools": [],
    "preferred_locations": [],
    "ranking_preference": null,
    "school_type_preference": null
  }
}

Return ONLY the JSON object — no markdown, no explanation, no code fences.
"""


def _sanitize_data(data: dict) -> None:
    """Replace None with '' for required string fields that the LLM may return as null."""
    str_list_fields = {
        "projects": ["start_date", "end_date", "role", "description"],
        "extracurriculars": ["start_date", "end_date", "role", "organization", "description"],
        "leadership": ["position", "organization", "description", "duration"],
        "awards": ["award_name", "organizer", "level", "description"],
    }
    for key, fields in str_list_fields.items():
        for item in data.get(key) or []:
            if isinstance(item, dict):
                for field in fields:
                    if item.get(field) is None:
                        item[field] = ""


def parse_pdf_to_request(pdf_bytes: bytes) -> Tuple[StudentMatchRequest, List[str]]:
    """
    Returns (validated_request, extra_missing_fields).

    extra_missing_fields contains dot-path strings for fields that failed
    validation and were replaced with defaults so that the UI can highlight
    them in the manual-input form.

    Raises EnvironmentError if the OpenAI key is missing.
    Raises ValueError only if the LLM response is not parseable JSON at all.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    # Upload the PDF to OpenAI Files API, then delete after use
    uploaded = client.files.create(
        file=("resume.pdf", pdf_bytes, "application/pdf"),
        purpose="user_data",
    )
    LOGGER.info("pdf_uploaded_to_openai", extra={"file_id": uploaded.id})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a structured data extractor. Always respond with valid JSON only.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "file", "file": {"file_id": uploaded.id}},
                        {"type": "text", "text": PARSE_PROMPT},
                    ],
                },
            ],
        )
    finally:
        client.files.delete(uploaded.id)
        LOGGER.info("pdf_deleted_from_openai", extra={"file_id": uploaded.id})

    raw = (response.choices[0].message.content or "").strip()
    LOGGER.info("pdf_parse_llm_response", extra={"raw": raw, "raw_length": len(raw)})

    data = json.loads(raw)

    if not data.get("intended_major"):
        data["intended_major"] = "Undecided"
    if not data.get("financial"):
        data["financial"] = {"budget_per_year": 60000, "currency": "USD", "need_scholarship": False}

    _sanitize_data(data)

    try:
        return StudentMatchRequest.model_validate(data), []
    except ValidationError as exc:
        # Collect paths that failed so the UI can ask the user to fill them in
        extra_missing = [".".join(str(x) for x in err["loc"]) for err in exc.errors()]
        LOGGER.warning(
            "pdf_parse_validation_partial",
            extra={"missing": extra_missing, "error": str(exc)},
        )
        # Drop items that cannot be validated (e.g. entire list entries with bad fields)
        # and retry with a cleaned-up version rather than failing completely.
        for key in ("projects", "extracurriculars", "leadership", "awards"):
            if any(p.startswith(key) for p in extra_missing):
                data[key] = []
        try:
            return StudentMatchRequest.model_validate(data), extra_missing
        except ValidationError as exc2:
            raise ValueError(f"Could not build a valid profile from this PDF: {exc2}") from exc2
