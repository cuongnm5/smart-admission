from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends

from app.core.config import MatchingSettings, get_settings
from app.repositories.mock_university_repository import MockUniversityRepository
from app.schemas.request import StudentMatchRequest
from app.schemas.response import MatchingResponse
from app.services.consultant_payload_builder import ConsultantPayloadBuilder
from app.services.expert_rubric import ExpertRubricService
from app.services.feature_builder import FeatureBuilder
from app.services.llm_scorer import LLMScorer
from app.services.matching_service import MatchingService
from app.services.profile_normalizer import ProfileNormalizer
from app.services.reranker import Reranker

router = APIRouter(prefix="/v1/matching", tags=["matching"])


@lru_cache(maxsize=1)
def _matching_service() -> MatchingService:
    settings: MatchingSettings = get_settings()
    feature_builder = FeatureBuilder(affordability_feature_cap=settings.affordability_feature_cap)

    return MatchingService(
        repository=MockUniversityRepository(),
        settings=settings,
        profile_normalizer=ProfileNormalizer(),
        rubric_service=ExpertRubricService(),
        llm_scorer=LLMScorer(
            feature_builder=feature_builder,
            llm_client=None,
            llm_enabled=settings.llm_enabled,
        ),
        feature_builder=feature_builder,
        payload_builder=ConsultantPayloadBuilder(),
        reranker=Reranker(),
    )


def get_matching_service() -> MatchingService:
    return _matching_service()


@router.post("/universities", response_model=MatchingResponse)
def match_universities(
    request: StudentMatchRequest,
    service: MatchingService = Depends(get_matching_service),
) -> MatchingResponse:
    return service.match(request)
