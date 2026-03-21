from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import CompetitivenessLevel, MatchBucket, SelectivityBand, UniversityType


class UniversityProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    admissio_rate: float = Field(ge=0.0, le=1.0)
    sat_avg: float = Field(ge=0.0)
    tution_in_state: float = Field(ge=0.0)
    tution_out_of_state: float = Field(ge=0.0)
    programs_offered: str
    top_programs: str

    @model_validator(mode="before")
    @classmethod
    def _normalize_clean_university_data(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        selectivity_fallback = {
            "high": 0.2,
            "medium": 0.5,
            "low": 0.8,
        }
        sat_fallback = {
            "high": 1400.0,
            "medium": 1200.0,
            "low": 1000.0,
        }
        selectivity_raw = str(normalized.get("selectivity_band", "medium")).lower()

        def first_non_null(*values: Any) -> Any:
            for value in values:
                if value is not None:
                    return value
            return None

        normalized["admissio_rate"] = first_non_null(
            normalized.get("admissio_rate"),
            normalized.get("admission_rate"),
            normalized.get("acceptance_rate"),
            selectivity_fallback.get(selectivity_raw, 0.5),
        )

        normalized["sat_avg"] = first_non_null(
            normalized.get("sat_avg"),
            normalized.get("sat_average"),
            normalized.get("avg_sat"),
            sat_fallback.get(selectivity_raw, 1200.0),
        )

        total_cost = first_non_null(normalized.get("total_cost_usd"), normalized.get("total_cost"), 0.0)
        normalized["tution_in_state"] = first_non_null(
            normalized.get("tution_in_state"),
            normalized.get("tuition_in_state"),
            normalized.get("in_state_tuition"),
            total_cost,
        )

        normalized["tution_out_of_state"] = first_non_null(
            normalized.get("tution_out_of_state"),
            normalized.get("tuition_out_of_state"),
            normalized.get("out_of_state_tuition"),
            total_cost,
        )

        programs_value = normalized.get("programs_offered", normalized.get("majors", ""))
        if isinstance(programs_value, list):
            normalized["programs_offered"] = ", ".join(str(item).strip() for item in programs_value if str(item).strip())
        else:
            normalized["programs_offered"] = str(programs_value or "")

        top_programs_value = normalized.get("top_programs", "")
        if not top_programs_value and normalized["programs_offered"]:
            head_programs = [part.strip() for part in normalized["programs_offered"].split(",") if part.strip()][:3]
            top_programs_value = ", ".join(head_programs)
        if isinstance(top_programs_value, list):
            normalized["top_programs"] = ", ".join(str(item).strip() for item in top_programs_value if str(item).strip())
        else:
            normalized["top_programs"] = str(top_programs_value or "")

        return normalized

    @property
    def programs_offered_list(self) -> List[str]:
        return [part.strip() for part in self.programs_offered.split(",") if part.strip()]

    @property
    def top_programs_list(self) -> List[str]:
        return [part.strip() for part in self.top_programs.split(",") if part.strip()]

    @property
    def university_id(self) -> str:
        extra = self.__pydantic_extra__ or {}
        value = extra.get("university_id")
        if isinstance(value, str) and value:
            return value
        return f"uni-{int(self.sat_avg)}-{int(self.tution_in_state)}"

    @property
    def name(self) -> str:
        extra = self.__pydantic_extra__ or {}
        value = extra.get("name")
        if isinstance(value, str) and value:
            return value
        return "Unknown University"

    @property
    def state(self) -> str:
        return "unknown"

    @property
    def region(self) -> str:
        return "unknown"

    @property
    def type(self) -> UniversityType:
        return UniversityType.PUBLIC

    @property
    def accepts_international_students(self) -> bool:
        return True

    @property
    def majors(self) -> List[str]:
        return self.programs_offered_list

    @property
    def entry_terms(self) -> List[str]:
        return ["fall"]

    @property
    def min_gpa(self) -> float:
        return 0.0

    @property
    def competitive_gpa(self) -> float:
        return 0.0

    @property
    def ielts_min(self) -> float:
        return 0.0

    @property
    def total_cost_usd(self) -> float:
        return max(self.tution_in_state, self.tution_out_of_state)

    @property
    def max_merit_usd(self) -> float:
        return 0.0

    @property
    def merit_for_internationals(self) -> bool:
        return False

    @property
    def selectivity_band(self) -> SelectivityBand:
        if self.admissio_rate <= 0.2:
            return SelectivityBand.HIGH
        if self.admissio_rate <= 0.5:
            return SelectivityBand.MEDIUM
        return SelectivityBand.LOW

    @property
    def major_competitiveness(self) -> Dict[str, CompetitivenessLevel]:
        return {major: CompetitivenessLevel.MEDIUM for major in self.majors}

    @property
    def summary_text(self) -> str:
        return f"Top programs: {self.top_programs}. Admission rate: {self.admissio_rate}"


class NormalizedStudentProfile(BaseModel):
    student_id: str
    normalized_gpa_4: float = Field(ge=0.0, le=4.0)
    raw_gpa: float = Field(ge=0.0)
    raw_gpa_scale: float = Field(gt=0.0)
    ielts: float = Field(ge=0.0, le=9.0)
    intended_major: str
    annual_budget_usd: float = Field(ge=0.0)
    profile_text: str
    leadership_score: int = Field(ge=0, le=5)
    activity_score: int = Field(ge=0, le=5)
    honor_score: int = Field(ge=0, le=5)


class RuleTrace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rule: str
    passed: bool = Field(alias="pass")
    student: Optional[float | str | bool] = None
    required: Optional[float | str | bool] = None
    detail: Optional[str] = None


class HardFilterResult(BaseModel):
    university_id: str
    passed: bool
    trace: List[RuleTrace]
    reject_reason: Optional[str] = None


class DeterministicFeaturePacket(BaseModel):
    university_id: str
    gpa_gap_to_min: float
    gpa_gap_to_competitive: float
    ielts_gap: float
    affordability_gap: float
    major_match_score: float = Field(ge=0.0, le=100.0)
    scholarship_support_score: float = Field(ge=0.0, le=100.0)
    competitiveness_penalty: float = Field(ge=0.0, le=100.0)
    profile_strength_score: float = Field(ge=0.0, le=100.0)


class RubricWeights(BaseModel):
    academic_fit: float = Field(gt=0.0)
    affordability_fit: float = Field(gt=0.0)
    profile_alignment: float = Field(gt=0.0)
    competitiveness_fit: float = Field(gt=0.0)


class RubricConfig(BaseModel):
    rubric_version: str
    weights: RubricWeights
    cs_very_high_competitiveness_penalty_multiplier: float = Field(ge=1.0)


class LLMScore(BaseModel):
    academic_fit: int = Field(ge=0, le=100)
    competitiveness_fit: int = Field(ge=0, le=100)
    affordability_fit: int = Field(ge=0, le=100)
    profile_alignment: int = Field(ge=0, le=100)
    overall_match: int = Field(ge=0, le=100)
    bucket: MatchBucket
    strengths: List[str]
    concerns: List[str]
    concise_rationale: str


class CandidateEvaluation(BaseModel):
    university: UniversityProfile
    hard_filter: HardFilterResult
    features: DeterministicFeaturePacket
    score: LLMScore
