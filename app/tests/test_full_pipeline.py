from fastapi.testclient import TestClient

from app.main import app


def test_full_pipeline_end_to_end_contract_and_ranking() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/matching/universities",
        json={
            "student_id": "u001",
            "academic": {
                "gpa": [
                    {"year": "Grade 10", "value": 3.7, "scale": 4.0},
                    {"year": "Grade 11", "value": 3.9, "scale": 4.0},
                    {"year": "Grade 12", "value": 3.95, "scale": 4.0}
                ]
            },
            "test_scores": {
                "english_tests": [
                    {"type": "IELTS", "score": 7.5, "section_scores": {"listening": 8.0, "reading": 7.5}}
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
                    "description": "Led coding club and organized workshops"
                }
            ],
            "leadership": [
                {
                    "position": "President",
                    "organization": "Coding Club",
                    "description": "Managed team and events",
                    "duration": "2 years"
                }
            ],
            "awards": [
                {
                    "award_name": "National Informatics Olympiad",
                    "organizer": "Ministry of Education",
                    "level": "national",
                    "year": 2024,
                    "description": "Top 10 nationwide"
                }
            ],
            "financial": {
                "budget_per_year": 30000,
                "currency": "USD",
                "need_scholarship": True
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert set(payload.keys()) == {"top_candidates", "meta"}

    top_candidates = payload["top_candidates"]
    meta = payload["meta"]

    assert meta["rubric_version"] == "v1"
    assert meta["retrieved_count"] >= meta["hard_filter_pass_count"] >= meta["scored_count"] >= meta["returned_count"]
    assert meta["returned_count"] == len(top_candidates)
    assert len(top_candidates) <= 20

    if top_candidates:
        assert all(isinstance(candidate_id, str) and candidate_id for candidate_id in top_candidates)
        assert len(set(top_candidates)) == len(top_candidates)
