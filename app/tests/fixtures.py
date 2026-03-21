from app.schemas.request import StudentMatchRequest

STRONG_CS_APPLICANT = StudentMatchRequest(
    student_id="u001",
    academic={
        "gpa": [
            {"year": "Grade 10", "value": 3.7, "scale": 4.0},
            {"year": "Grade 11", "value": 3.9, "scale": 4.0},
            {"year": "Grade 12", "value": 3.95, "scale": 4.0},
        ]
    },
    test_scores={"english_tests": [{"type": "IELTS", "score": 7.5}]},
    intended_major="Computer Science",
    extracurriculars=[
        {
            "activity_name": "Coding Club",
            "role": "President",
            "organization": "School Club",
            "start_date": "2022-09",
            "end_date": "2024-05",
            "hours_per_week": 6,
            "description": "Won a provincial math prize, leader of coding club, volunteer teaching children.",
        }
    ],
    financial={"budget_per_year": 30000, "currency": "USD", "need_scholarship": True},
)

BUDGET_CONSTRAINED_APPLICANT = StudentMatchRequest(
    student_id="u002",
    academic={
        "gpa": [
            {"year": "Grade 10", "value": 3.2, "scale": 4.0},
            {"year": "Grade 11", "value": 3.4, "scale": 4.0},
            {"year": "Grade 12", "value": 3.6, "scale": 4.0},
        ]
    },
    test_scores={"english_tests": [{"type": "IELTS", "score": 6.5}]},
    intended_major="Computer Science",
    extracurriculars=[
        {
            "activity_name": "Coding Club",
            "role": "Member",
            "organization": "School Club",
            "start_date": "2023-01",
            "end_date": "2024-05",
            "hours_per_week": 3,
            "description": "Active in coding club and community teaching.",
        }
    ],
    financial={"budget_per_year": 14000, "currency": "USD", "need_scholarship": True},
)
