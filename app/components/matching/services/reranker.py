from __future__ import annotations

from typing import Sequence

from app.domain.models import CandidateEvaluation


class Reranker:
    def rerank(self, evaluations: Sequence[CandidateEvaluation], top_k: int) -> list[CandidateEvaluation]:
        ranked = sorted(
            evaluations,
            key=lambda item: (
                item.score.overall_match,
                item.score.academic_fit,
                item.score.affordability_fit,
                item.features.gpa_gap_to_competitive,
            ),
            reverse=True,
        )
        return ranked[:top_k]
