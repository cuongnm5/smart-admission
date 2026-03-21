from __future__ import annotations

import pytest

from app.core.config import MatchingSettings
from app.repositories.mock_university_repository import MockUniversityRepository
from app.schemas.request import StudentMatchRequest
from app.services.consultant_payload_builder import ConsultantPayloadBuilder
from app.services.expert_rubric import ExpertRubricService
from app.services.feature_builder import FeatureBuilder
from app.services.llm_scorer import LLMScorer
from app.services.matching_service import MatchingService
from app.services.profile_normalizer import ProfileNormalizer
from app.services.reranker import Reranker


@pytest.fixture
def strong_cs_applicant() -> StudentMatchRequest:
    return StudentMatchRequest(
        student_id="u001",
        academic={
            "gpa": [
                {"year": "Grade 10", "value": 3.7, "scale": 4.0},
                {"year": "Grade 11", "value": 3.9, "scale": 4.0},
                {"year": "Grade 12", "value": 3.95, "scale": 4.0},
            ]
        },
        test_scores={
            "english_tests": [
                {"type": "IELTS", "score": 7.5, "section_scores": {"reading": 7.5, "writing": 7.0}}
            ]
        },
        intended_major="Computer Science",
        extracurriculars=[
            {
                "activity_name": "Coding Club",
                "role": "President",
                "organization": "School Club",
                "start_date": "2022-09",
                "end_date": "2024-05",
                "hours_per_week": 6,
                "description": "Leader of coding club, organized hackathon and workshops",
            },
            {
                "activity_name": "Volunteer Teaching",
                "role": "Tutor",
                "organization": "Local NGO",
                "start_date": "2023-01",
                "end_date": "2024-01",
                "hours_per_week": 4,
                "description": "Volunteer teaching children in community",
            },
        ],
        leadership=[
            {
                "position": "President",
                "organization": "Coding Club",
                "description": "Led team and mentored peers",
                "duration": "2 years",
            }
        ],
        awards=[
            {
                "award_name": "Math Prize",
                "organizer": "Province",
                "level": "provincial",
                "year": 2024,
                "description": "Won provincial math prize",
            }
        ],
        financial={
            "budget_per_year": 30000,
            "currency": "USD",
            "need_scholarship": True,
        },
    )


@pytest.fixture
def budget_constrained_applicant() -> StudentMatchRequest:
    return StudentMatchRequest(
        student_id="u002",
        academic={
            "gpa": [
                {"year": "Grade 10", "value": 3.2, "scale": 4.0},
                {"year": "Grade 11", "value": 3.4, "scale": 4.0},
                {"year": "Grade 12", "value": 3.6, "scale": 4.0},
            ]
        },
        test_scores={
            "english_tests": [
                {"type": "IELTS", "score": 6.5, "section_scores": {"reading": 6.5, "writing": 6.0}}
            ]
        },
        intended_major="Computer Science",
        extracurriculars=[
            {
                "activity_name": "Coding Club",
                "role": "Member",
                "organization": "School Club",
                "start_date": "2023-01",
                "end_date": "2024-05",
                "hours_per_week": 3,
                "description": "Active in coding club and community teaching",
            }
        ],
        financial={
            "budget_per_year": 14000,
            "currency": "USD",
            "need_scholarship": True,
        },
    )


@pytest.fixture
def repository() -> MockUniversityRepository:
    return MockUniversityRepository()


@pytest.fixture
def feature_builder() -> FeatureBuilder:
    return FeatureBuilder(affordability_feature_cap=50000)


@pytest.fixture
def matching_service(repository: MockUniversityRepository, feature_builder: FeatureBuilder) -> MatchingService:
    settings = MatchingSettings(top_k=20, affordability_reject_ratio=0.7, llm_enabled=False)
    return MatchingService(
        repository=repository,
        settings=settings,
        profile_normalizer=ProfileNormalizer(),
        rubric_service=ExpertRubricService(),
        llm_scorer=LLMScorer(feature_builder=feature_builder, llm_client=None, llm_enabled=False),
        feature_builder=feature_builder,
        payload_builder=ConsultantPayloadBuilder(),
        reranker=Reranker(),
    )
