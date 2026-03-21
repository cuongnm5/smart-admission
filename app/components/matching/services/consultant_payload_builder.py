from __future__ import annotations

from typing import Sequence

from app.domain.models import CandidateEvaluation
from app.schemas.response import MatchingMeta, MatchingResponse
from app.components.matching.services.university_identity import build_university_id


class ConsultantPayloadBuilder:
    def build(
        self,
        ranked_candidates: Sequence[CandidateEvaluation],
        retrieved_count: int,
        hard_filter_pass_count: int,
        scored_count: int,
        rubric_version: str,
    ) -> MatchingResponse:
        top_candidates = [build_university_id(evaluation.university) for evaluation in ranked_candidates]

        meta = MatchingMeta(
            retrieved_count=retrieved_count,
            hard_filter_pass_count=hard_filter_pass_count,
            scored_count=scored_count,
            returned_count=len(top_candidates),
            rubric_version=rubric_version,
        )

        return MatchingResponse(top_candidates=top_candidates, meta=meta)
