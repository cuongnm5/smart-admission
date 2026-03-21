from __future__ import annotations

import json
import logging
from typing import Protocol

from pydantic import ValidationError

from app.domain.enums import CompetitivenessLevel, MatchBucket
from app.domain.models import DeterministicFeaturePacket, HardFilterResult, LLMScore, NormalizedStudentProfile, RubricConfig, UniversityProfile
from app.prompts.llm_match_scoring_prompt import build_match_scoring_prompt
from app.schemas.request import StudentMatchRequest
from app.services.feature_builder import FeatureBuilder

LOGGER = logging.getLogger(__name__)


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class LLMScorer:
    def __init__(self, feature_builder: FeatureBuilder, llm_client: LLMClient | None = None, llm_enabled: bool = False) -> None:
        self._feature_builder = feature_builder
        self._llm_client = llm_client
        self._llm_enabled = llm_enabled

    def score(
        self,
        student: NormalizedStudentProfile,
        university: UniversityProfile,
        features: DeterministicFeaturePacket,
        hard_filter: HardFilterResult,
        rubric: RubricConfig,
        student_request: StudentMatchRequest | None = None,
    ) -> LLMScore:
        if not self._llm_enabled or self._llm_client is None:
            return self._deterministic_fallback(student, university, features, rubric)

        prompt = build_match_scoring_prompt(
            student,
            university,
            features,
            hard_filter,
            rubric,
            student_request=student_request,
        )

        try:
            raw = self._llm_client.generate(prompt)
            parsed = self._parse_json(raw)
            return LLMScore.model_validate(parsed)
        except (ValidationError, ValueError, json.JSONDecodeError) as error:
            LOGGER.warning("llm_scoring_failed_using_fallback", extra={"error": str(error)})
            return self._deterministic_fallback(student, university, features, rubric)

    @staticmethod
    def _parse_json(raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0].strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end < 0 or end <= start:
            raise ValueError("No JSON object found in LLM response")
        return json.loads(raw[start : end + 1])

    def _deterministic_fallback(
        self,
        student: NormalizedStudentProfile,
        university: UniversityProfile,
        features: DeterministicFeaturePacket,
        rubric: RubricConfig,
    ) -> LLMScore:
        academic_fit = self._compute_academic_fit(features)
        affordability_fit = self._feature_builder.affordability_fit_score(features.affordability_gap)
        profile_alignment = int(round(features.profile_strength_score))
        competitiveness_fit = max(0, int(round(100.0 - features.competitiveness_penalty)))

        if (
            student.intended_major.lower() == "computer science"
            and university.major_competitiveness.get(student.intended_major) == CompetitivenessLevel.VERY_HIGH
        ):
            competitiveness_fit = max(
                0,
                int(round(competitiveness_fit / rubric.cs_very_high_competitiveness_penalty_multiplier)),
            )

        overall = int(
            round(
                academic_fit * rubric.weights.academic_fit
                + affordability_fit * rubric.weights.affordability_fit
                + profile_alignment * rubric.weights.profile_alignment
                + competitiveness_fit * rubric.weights.competitiveness_fit
            )
        )
        overall = max(0, min(100, overall))

        bucket = MatchBucket.REACH
        if overall >= 80:
            bucket = MatchBucket.LIKELY
        elif overall >= 55:
            bucket = MatchBucket.TARGET

        strengths, concerns = self._build_reasons(features, affordability_fit, competitiveness_fit)

        return LLMScore(
            academic_fit=academic_fit,
            competitiveness_fit=competitiveness_fit,
            affordability_fit=affordability_fit,
            profile_alignment=profile_alignment,
            overall_match=overall,
            bucket=bucket,
            strengths=strengths,
            concerns=concerns,
            concise_rationale="Deterministic fallback scoring used due to unavailable or invalid LLM output.",
        )

    @staticmethod
    def _compute_academic_fit(features: DeterministicFeaturePacket) -> int:
        gpa_component = max(0.0, min(1.0, (features.gpa_gap_to_competitive + 1.5) / 2.5))
        ielts_component = max(0.0, min(1.0, (features.ielts_gap + 1.0) / 2.0))
        return int(round((gpa_component * 0.7 + ielts_component * 0.3) * 100.0))

    @staticmethod
    def _build_reasons(
        features: DeterministicFeaturePacket,
        affordability_fit: int,
        competitiveness_fit: int,
    ) -> tuple[list[str], list[str]]:
        strengths: list[str] = []
        concerns: list[str] = []

        if features.gpa_gap_to_min >= 0:
            strengths.append("Student meets academic threshold for the university")
        if features.profile_strength_score >= 60:
            strengths.append("Profile shows leadership and sustained extracurricular engagement")
        if affordability_fit >= 60:
            strengths.append("Estimated affordability is within a manageable range")

        if affordability_fit < 50:
            concerns.append("Affordability may remain difficult even with merit aid")
        if competitiveness_fit < 50:
            concerns.append("Program competitiveness creates significant admission uncertainty")
        if features.gpa_gap_to_competitive < 0:
            concerns.append("GPA is below the competitive benchmark for this program")

        if not strengths:
            strengths.append("Major availability and baseline eligibility requirements are satisfied")
        if not concerns:
            concerns.append("No major deterministic concern beyond routine admission uncertainty")

        return strengths[:3], concerns[:3]
