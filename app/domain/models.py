from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import CompetitivenessLevel, MatchBucket, SelectivityBand, UniversityType


class UniversityProfile(BaseModel):
    university_id: str
    name: str
    state: str
    region: str
    type: UniversityType
    accepts_international_students: bool
    majors: List[str]
    entry_terms: List[str]
    min_gpa: float = Field(ge=0.0)
    competitive_gpa: float = Field(ge=0.0)
    ielts_min: float = Field(ge=0.0)
    total_cost_usd: float = Field(ge=0.0)
    max_merit_usd: float = Field(ge=0.0)
    merit_for_internationals: bool
    selectivity_band: SelectivityBand
    major_competitiveness: Dict[str, CompetitivenessLevel]
    summary_text: str


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
