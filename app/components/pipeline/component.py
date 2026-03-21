from __future__ import annotations

from app.domain.models import UniversityProfile
from app.repositories.base import UniversityRepository
from app.schemas.pipeline import StageOneMatchingOutput, StageTwoAnalysisOutput, UniversityPipelineResponse
from app.schemas.request import StudentMatchRequest
from app.components.matching.component import MatchingComponent
from app.components.matching.services.university_identity import build_university_id
from app.components.summary.component import SummaryComponent


class UniversityPipelineComponent:
    def __init__(
        self,
        matching_component: MatchingComponent,
        summary_component: SummaryComponent,
        repository: UniversityRepository,
    ) -> None:
        self._matching_component = matching_component
        self._summary_component = summary_component
        self._repository = repository

    def run(self, request: StudentMatchRequest) -> UniversityPipelineResponse:
        stage_1 = self._matching_component.run(request)
        top_20_ids = stage_1.top_candidates

        id_to_university: dict[str, UniversityProfile] = {
            build_university_id(university): university for university in self._repository.list_universities()
        }
        top_2_ids = top_20_ids[:2]
        top_2_universities = [id_to_university[university_id] for university_id in top_2_ids if university_id in id_to_university]

        stage_2_result = self._summary_component.analyze(request, top_2_universities)

        return UniversityPipelineResponse(
            stage_1_matching=StageOneMatchingOutput(
                top_20_university_ids=top_20_ids,
                meta=stage_1.meta,
            ),
            stage_2_analysis=StageTwoAnalysisOutput(
                analyzed_university_ids=top_2_ids,
                matched_university_id=stage_2_result.get("matched_university_id"),
                ranking_summary=stage_2_result.get("ranking_summary", []),
                detailed_analysis=stage_2_result.get("detailed_analysis", {}),
            ),
        )
