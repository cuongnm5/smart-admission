from __future__ import annotations

import json
import logging
import os

from openai import OpenAI

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


def parse_pdf_to_request(pdf_bytes: bytes) -> StudentMatchRequest:
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

    return StudentMatchRequest.model_validate(data)
