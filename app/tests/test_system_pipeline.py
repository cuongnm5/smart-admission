from fastapi.testclient import TestClient

from app.main import app


def test_system_pipeline_match_and_analyze() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/pipeline/match-and-analyze",
        json={
            "student_id": "u001",
            "academic": {
                "gpa": [
                    {"year": "Grade 10", "value": 3.7, "scale": 4.0},
                    {"year": "Grade 11", "value": 3.9, "scale": 4.0},
                    {"year": "Grade 12", "value": 3.95, "scale": 4.0},
                ]
            },
            "test_scores": {
                "english_tests": [
                    {"type": "IELTS", "score": 7.5, "section_scores": {"reading": 7.5, "writing": 7.0}}
                ]
            },
            "intended_major": "Computer Science",
            "extracurriculars": [
                {
                    "activity_name": "Coding Club",
                    "role": "President",
                    "organization": "School Club",
                    "start_date": "2022-09",
                    "end_date": "2024-05",
                    "hours_per_week": 6,
                    "description": "Led coding club and organized workshops",
                }
            ],
            "leadership": [
                {
                    "position": "President",
                    "organization": "Coding Club",
                    "description": "Managed team and events",
                    "duration": "2 years",
                }
            ],
            "awards": [
                {
                    "award_name": "National Informatics Olympiad",
                    "organizer": "Ministry of Education",
                    "level": "national",
                    "year": 2024,
                    "description": "Top 10 nationwide",
                }
            ],
            "essays": {
                "personal_statement": {
                    "content": "I want to build AI systems for education."
                }
            },
            "recommendation_letters": [
                {
                    "from": "Mr. Nguyen",
                    "role": "Math Teacher",
                    "relationship_duration": "2 years",
                    "content_summary": "Strong analytical and leadership profile",
                }
            ],
            "financial": {
                "budget_per_year": 30000,
                "currency": "USD",
                "need_scholarship": True,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert "stage_1_matching" in payload
    assert "stage_2_analysis" in payload

    top_20 = payload["stage_1_matching"]["top_20_university_ids"]
    analyzed = payload["stage_2_analysis"]["analyzed_university_ids"]
    matched = payload["stage_2_analysis"]["matched_university_id"]

    assert isinstance(top_20, list)
    assert len(top_20) <= 20
    assert len(analyzed) <= 2

    if analyzed:
        assert matched in analyzed

    assert isinstance(payload["stage_2_analysis"]["ranking_summary"], list)
    assert isinstance(payload["stage_2_analysis"]["detailed_analysis"], dict)
