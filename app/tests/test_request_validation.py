import pytest
from pydantic import ValidationError

from app.schemas.request import StudentMatchRequest


def test_request_validation_accepts_minimal_payload() -> None:
    payload = StudentMatchRequest(
        student_id="u001",
        academic={"gpa": [{"year": "Grade 12", "value": 3.6, "scale": 4.0}]},
        test_scores={"english_tests": [{"type": "IELTS", "score": 7.0}]},
        intended_major="Computer Science",
        extracurriculars=[
            {
                "activity_name": "Coding Club",
                "role": "President",
                "organization": "School",
                "start_date": "2023-01",
                "end_date": "2024-01",
                "hours_per_week": 3,
                "description": "leader in coding club",
            }
        ],
        financial={"budget_per_year": 30000, "currency": "USD", "need_scholarship": True},
    )

    assert payload.student_id == "u001"


def test_request_validation_rejects_invalid_ielts() -> None:
    with pytest.raises(ValidationError):
        StudentMatchRequest(
            student_id="u001",
            academic={"gpa": [{"year": "Grade 12", "value": 3.0, "scale": 4.0}]},
            test_scores={"english_tests": [{"type": "IELTS", "score": 10.0}]},
            intended_major="Computer Science",
            financial={"budget_per_year": 20000, "currency": "USD", "need_scholarship": True},
        )
