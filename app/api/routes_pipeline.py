from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends

from app.api.routes_matching import get_matching_service
from app.components.matching.component import MatchingComponent
from app.components.pipeline.component import UniversityPipelineComponent
from app.components.summary.component import SummaryComponent
from app.repositories.mock_university_repository import MockUniversityRepository
from app.schemas.pipeline import UniversityPipelineResponse
from app.schemas.request import StudentMatchRequest

router = APIRouter(prefix="/v1/pipeline", tags=["pipeline"])


@lru_cache(maxsize=1)
def _pipeline_service() -> UniversityPipelineComponent:
    repository = MockUniversityRepository()
    return UniversityPipelineComponent(
        matching_component=MatchingComponent(get_matching_service()),
        summary_component=SummaryComponent(),
        repository=repository,
    )


def get_pipeline_service() -> UniversityPipelineComponent:
    return _pipeline_service()


@router.post("/match-and-analyze", response_model=UniversityPipelineResponse)
def match_and_analyze(
    request: StudentMatchRequest,
    service: UniversityPipelineComponent = Depends(get_pipeline_service),
) -> UniversityPipelineResponse:
    return service.run(request)
