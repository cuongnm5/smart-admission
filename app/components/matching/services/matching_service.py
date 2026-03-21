from __future__ import annotations

import logging

from app.core.config import MatchingSettings
from app.domain.models import CandidateEvaluation
from app.repositories.base import UniversityRepository
from app.schemas.request import StudentMatchRequest
from app.schemas.response import MatchingResponse
from app.components.matching.services.candidate_retrieval import CandidateRetrievalService
from app.components.matching.services.consultant_payload_builder import ConsultantPayloadBuilder
from app.components.matching.services.expert_rubric import ExpertRubricService
from app.components.matching.services.feature_builder import FeatureBuilder
from app.components.matching.services.hard_filter_engine import HardFilterEngine
from app.components.matching.services.llm_scorer import LLMScorer
from app.components.matching.services.profile_normalizer import ProfileNormalizer
from app.components.matching.services.reranker import Reranker
from app.components.matching.services.university_identity import build_university_id

LOGGER = logging.getLogger(__name__)


class MatchingService:
    def __init__(
        self,
        repository: UniversityRepository,
        settings: MatchingSettings,
        profile_normalizer: ProfileNormalizer,
        rubric_service: ExpertRubricService,
        llm_scorer: LLMScorer,
        feature_builder: FeatureBuilder,
        payload_builder: ConsultantPayloadBuilder,
        reranker: Reranker,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._profile_normalizer = profile_normalizer
        self._rubric_service = rubric_service
        self._llm_scorer = llm_scorer
        self._feature_builder = feature_builder
        self._payload_builder = payload_builder
        self._reranker = reranker
        self._retrieval_service = CandidateRetrievalService(repository)
        self._hard_filter_engine = HardFilterEngine(settings.affordability_reject_ratio)

    def match(self, request: StudentMatchRequest) -> MatchingResponse:
        LOGGER.info(
            "matching_step_start_request_validation",
            extra={
                "step": "request_received",
                "student_id": request.student_id,
            },
        )

        student = self._profile_normalizer.normalize(request)
        LOGGER.info(
            "matching_step_profile_normalized",
            extra={
                "step": "profile_normalizer",
                "student_id": student.student_id,
                "normalized_gpa_4": student.normalized_gpa_4,
                "ielts": student.ielts,
                "intended_major": student.intended_major,
                "annual_budget_usd": student.annual_budget_usd,
                "leadership_score": student.leadership_score,
                "activity_score": student.activity_score,
                "honor_score": student.honor_score,
            },
        )

        rubric = self._rubric_service.get_rubric()
        LOGGER.info(
            "matching_step_rubric_loaded",
            extra={
                "step": "expert_rubric",
                "rubric_version": rubric.rubric_version,
            },
        )

        candidates = self._retrieval_service.retrieve(student)
        retrieved_count = len(candidates)
        LOGGER.info(
            "matching_step_candidates_retrieved",
            extra={
                "step": "candidate_retrieval",
                "student_id": student.student_id,
                "retrieved_count": retrieved_count,
            },
        )

        evaluations: list[CandidateEvaluation] = []
        hard_filter_pass_count = 0

        for university in candidates:
            university_id = build_university_id(university)
            hard_filter_result = self._hard_filter_engine.evaluate(student, university)
            LOGGER.info(
                "matching_step_hard_filter_evaluated",
                extra={
                    "step": "hard_filter_engine",
                    "student_id": student.student_id,
                    "university_id": university_id,
                    "passed": hard_filter_result.passed,
                    "reject_reason": hard_filter_result.reject_reason,
                    "trace": [item.model_dump(by_alias=True) for item in hard_filter_result.trace],
                },
            )
            if not hard_filter_result.passed:
                continue

            hard_filter_pass_count += 1
            features = self._feature_builder.build(student, university)
            LOGGER.info(
                "matching_step_features_built",
                extra={
                    "step": "feature_builder",
                    "student_id": student.student_id,
                    "university_id": university_id,
                    "features": features.model_dump(),
                },
            )

            score = self._llm_scorer.score(
                student,
                university,
                features,
                hard_filter_result,
                rubric,
                student_request=request,
            )
            LOGGER.info(
                "matching_step_scored",
                extra={
                    "step": "llm_scoring_engine",
                    "student_id": student.student_id,
                    "university_id": university_id,
                    "score": score.model_dump(),
                },
            )

            evaluations.append(
                CandidateEvaluation(
                    university=university,
                    hard_filter=hard_filter_result,
                    features=features,
                    score=score,
                )
            )

        ranked = self._reranker.rerank(evaluations, top_k=self._settings.top_k)
        LOGGER.info(
            "matching_step_reranked",
            extra={
                "step": "reranker",
                "student_id": student.student_id,
                "input_count": len(evaluations),
                "ranked_count": len(ranked),
                "top_k": self._settings.top_k,
                "top_university_ids": [build_university_id(item.university) for item in ranked[:5]],
            },
        )

        response = self._payload_builder.build(
            ranked_candidates=ranked,
            retrieved_count=retrieved_count,
            hard_filter_pass_count=hard_filter_pass_count,
            scored_count=len(evaluations),
            rubric_version=rubric.rubric_version,
        )
        LOGGER.info(
            "matching_step_payload_built",
            extra={
                "step": "consultant_payload_builder",
                "student_id": student.student_id,
                "returned_count": len(response.top_candidates),
            },
        )

        LOGGER.info(
            "matching_completed",
            extra={
                "student_id": request.student_id,
                "retrieved_count": retrieved_count,
                "hard_filter_pass_count": hard_filter_pass_count,
                "returned_count": len(response.top_candidates),
            },
        )

        return response
