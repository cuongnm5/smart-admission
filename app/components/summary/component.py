from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.components.summary.dto.student_profile import StudentProfile
from app.components.summary.services.summary_service import MatchingEngine
from app.components.matching.services.university_identity import build_university_id
from app.domain.enums import SelectivityBand
from app.domain.models import UniversityProfile
from app.schemas.request import StudentMatchRequest


class _DeterministicSummaryLLMClient:
    def evaluate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        score = 7.0
        if "lead" in prompt_lower or "president" in prompt_lower:
            score += 0.6
        if "award" in prompt_lower or "olympiad" in prompt_lower:
            score += 0.6
        if "essay" in prompt_lower or "recommendation" in prompt_lower:
            score += 0.4
        score = max(0.0, min(10.0, score))
        return f"SCORE: {score:.1f}\\nREASONING: Profile signals sustained impact and alignment."


class SummaryComponent:
    def __init__(self) -> None:
        self._engine = MatchingEngine(_DeterministicSummaryLLMClient())

    def analyze(
        self,
        student_request: StudentMatchRequest,
        selected_universities: List[UniversityProfile],
    ) -> Dict[str, Any]:
        if not selected_universities:
            return {
                "matched_university_id": None,
                "ranking_summary": [],
                "detailed_analysis": {},
            }

        student_payload = self._to_summary_student_payload(student_request)
        student_profile = StudentProfile.from_dict(student_payload)
        top_20_like = [self._to_summary_university_payload(university) for university in selected_universities]

        result = self._engine.match(student_profile, top_20_like)
        name_to_id = {university.name: build_university_id(university) for university in selected_universities}

        ranking_summary: List[Dict[str, Any]] = []
        matched_university_id: Optional[str] = None

        for index, ranking in enumerate(result.top_10_universities, start=1):
            university_id = name_to_id.get(ranking.name)
            if matched_university_id is None:
                matched_university_id = university_id
            ranking_summary.append(
                {
                    "rank": index,
                    "university_id": university_id,
                    "university_name": ranking.name,
                    "combined_score": round(ranking.combined_score, 2),
                    "suitability_score": round(ranking.suitability_score, 2),
                    "acceptance_probability": round(ranking.acceptance_probability, 2),
                    "qs_rank": ranking.qs_rank,
                }
            )

        return {
            "matched_university_id": matched_university_id,
            "ranking_summary": ranking_summary,
            "detailed_analysis": result.detailed_analysis or {},
        }

    @staticmethod
    def _to_summary_student_payload(student_request: StudentMatchRequest) -> Dict[str, Any]:
        payload = deepcopy(student_request.model_dump(by_alias=True))

        payload["name"] = payload.get("name") or payload.get("student_id") or "Unknown"
        payload["email"] = payload.get("email") or "unknown@example.com"

        payload["preferences"] = payload.get("preferences") or {}

        academic = payload.get("academic") or {}
        if "test_scores" not in academic:
            academic["test_scores"] = payload.get("test_scores") or {}
        payload["academic"] = academic

        essays = payload.get("essays") or {}
        if "recommendation_letters" not in essays:
            essays["recommendation_letters"] = payload.get("recommendation_letters") or []
        payload["essays"] = essays

        return payload

    @staticmethod
    def _to_summary_university_payload(university: UniversityProfile) -> Dict[str, Any]:
        selectivity_to_acceptance = {
            SelectivityBand.HIGH: 0.12,
            SelectivityBand.MEDIUM: 0.35,
            SelectivityBand.LOW: 0.6,
        }

        major_rank_signal = 30
        if university.major_competitiveness:
            major_rank_signal = 10 + (len(university.major_competitiveness) * 2)

        return {
            "name": university.name,
            "qs_rank": major_rank_signal,
            "avg_admitted_gpa": university.competitive_gpa,
            "avg_test_score": 1400,
            "acceptance_rate": selectivity_to_acceptance[university.selectivity_band],
            "cost_of_attendance": university.total_cost_usd,
            "financial_aid_percentage": 60 if university.merit_for_internationals else 20,
            "program_ranking": {
                major: level.value for major, level in university.major_competitiveness.items()
            },
        }
