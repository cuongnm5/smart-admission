from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.components.pdf_parser.service import parse_pdf_to_request
from app.schemas.request import StudentMatchRequest

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/profile", tags=["profile"])

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

_REQUIRED_FIELDS = [
    "intended_major",
    "academic.gpa",
    "financial.budget_per_year",
]


class ParsePDFResponse(BaseModel):
    data: Optional[Dict[str, Any]] = None
    missing_fields: List[str] = []
    error: Optional[str] = None


def _find_missing(req: StudentMatchRequest) -> List[str]:
    missing: List[str] = []
    if not req.intended_major or req.intended_major == "Undecided":
        missing.append("intended_major")
    if not req.academic.gpa or req.academic.gpa[0].value == 0:
        missing.append("academic.gpa")
    if req.financial.budget_per_year == 0:
        missing.append("financial.budget_per_year")
    has_test = (
        req.test_scores.sat is not None
        or bool(req.test_scores.english_tests)
        or req.test_scores.act is not None
    )
    if not has_test:
        missing.append("test_scores")
    return missing


@router.post("/parse-pdf", response_model=ParsePDFResponse)
async def parse_pdf(file: UploadFile) -> ParsePDFResponse:
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10 MB.")

    try:
        request = parse_pdf_to_request(pdf_bytes)
    except EnvironmentError as exc:
        LOGGER.error("pdf_parse_env_error", extra={"error": str(exc)})
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        LOGGER.warning("pdf_parse_value_error", extra={"error": str(exc)})
        return ParsePDFResponse(error=str(exc))
    except Exception as exc:
        LOGGER.exception("pdf_parse_unexpected_error")
        return ParsePDFResponse(error=f"Failed to parse PDF: {exc}")

    missing = _find_missing(request)
    return ParsePDFResponse(
        data=request.model_dump(by_alias=True),
        missing_fields=missing,
    )
