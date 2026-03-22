from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

# Maps student major (lowercase) to the oedb_rank_* column name
_MAJOR_TO_OEDB_COL: Dict[str, str] = {
    "computer science": "oedb_rank_computer_science",
    "information technology": "oedb_rank_it",
    "software engineering": "oedb_rank_computer_science",
    "computer engineering": "oedb_rank_computer_science",
    "data science": "oedb_rank_computer_science",
    "artificial intelligence": "oedb_rank_computer_science",
    "machine learning": "oedb_rank_computer_science",
    "cybersecurity": "oedb_rank_computer_science",
    "network engineering": "oedb_rank_it",
    "electrical engineering": "oedb_rank_engineering",
    "mechanical engineering": "oedb_rank_engineering",
    "civil engineering": "oedb_rank_engineering",
    "biomedical engineering": "oedb_rank_engineering",
    "chemical engineering": "oedb_rank_engineering",
    "industrial engineering": "oedb_rank_engineering",
    "engineering": "oedb_rank_engineering",
    "business administration": "oedb_rank_business_administration",
    "mba": "oedb_rank_mba",
    "marketing": "oedb_rank_marketing",
    "accounting": "oedb_rank_accounting",
    "nursing": "oedb_rank_nursing",
    "psychology": "oedb_rank_psychology",
    "education": "oedb_rank_education",
    "criminal justice": "oedb_rank_criminal_justice",
    "graphic design": "oedb_rank_graphic_design",
    "paralegal": "oedb_rank_paralegal",
}

_OEDB_COL_TO_LABEL: Dict[str, str] = {
    "oedb_rank_computer_science": "CS",
    "oedb_rank_it": "IT",
    "oedb_rank_engineering": "Engineering",
    "oedb_rank_business_administration": "Business",
    "oedb_rank_mba": "MBA",
    "oedb_rank_marketing": "Marketing",
    "oedb_rank_accounting": "Accounting",
    "oedb_rank_nursing": "Nursing",
    "oedb_rank_psychology": "Psychology",
    "oedb_rank_education": "Education",
    "oedb_rank_criminal_justice": "Criminal Justice",
    "oedb_rank_graphic_design": "Graphic Design",
    "oedb_rank_paralegal": "Paralegal",
    "oedb_rank_phd": "PhD Programs",
}


def _resolve_oedb_col(intended_major: str) -> Optional[str]:
    key = intended_major.strip().lower()
    if key in _MAJOR_TO_OEDB_COL:
        return _MAJOR_TO_OEDB_COL[key]
    for alias, col in _MAJOR_TO_OEDB_COL.items():
        if alias in key or key in alias:
            return col
    return None

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
        name_to_university = {university.name: university for university in selected_universities}

        # Resolve which oedb_rank_* column applies to the student's major
        rank_col = _resolve_oedb_col(student_request.intended_major or "")
        subject_label = _OEDB_COL_TO_LABEL.get(rank_col, "") if rank_col else ""

        ranking_summary: List[Dict[str, Any]] = []
        matched_university_id: Optional[str] = None

        for index, ranking in enumerate(result.top_10_universities, start=1):
            university_id = name_to_id.get(ranking.name)
            if matched_university_id is None:
                matched_university_id = university_id

            uni = name_to_university.get(ranking.name)
            extras: Dict[str, Any] = (uni.__pydantic_extra__ or {}) if uni else {}

            entry: Dict[str, Any] = {
                "rank": index,
                "university_id": university_id,
                "university_name": ranking.name,
                "combined_score": round(ranking.combined_score, 2),
                "suitability_score": round(ranking.suitability_score, 2),
                "acceptance_probability": round(ranking.acceptance_probability, 2),
                "qs_rank": ranking.qs_rank,
                # Location
                "city": extras.get("city", ""),
                "state": extras.get("state", ""),
                # University stats
                "sat_avg": int(uni.sat_avg) if uni and uni.sat_avg else 0,
                "admission_rate": round(uni.admissio_rate * 100, 1) if uni else 0,
                "tuition_per_year": int(uni.tution_out_of_state) if uni and uni.tution_out_of_state else 0,
            }

            # Subject-specific rank (e.g. oedb_rank_computer_science)
            if rank_col:
                raw_rank = extras.get(rank_col)
                if raw_rank is not None:
                    entry["subject_rank"] = int(raw_rank)
                    entry["subject_label"] = subject_label

            ranking_summary.append(entry)

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
