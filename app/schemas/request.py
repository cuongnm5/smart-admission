from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GPARecord(BaseModel):
    year: str
    value: float = Field(ge=0.0)
    scale: float = Field(gt=0.0)


class ClassRank(BaseModel):
    value: int = Field(ge=1)
    total_students: int = Field(ge=1)


class SchoolProfile(BaseModel):
    school_name: str
    school_type: str
    location: str
    description: str


class TranscriptSubject(BaseModel):
    subject: str
    grade: float = Field(ge=0.0)
    max_grade: float = Field(gt=0.0)
    level: str


class TranscriptYear(BaseModel):
    year: str
    subjects: List[TranscriptSubject] = Field(default_factory=list)


class AcademicProfile(BaseModel):
    gpa: List[GPARecord] = Field(default_factory=list)
    class_rank: Optional[ClassRank] = None
    school_profile: Optional[SchoolProfile] = None
    transcript: List[TranscriptYear] = Field(default_factory=list)


class EnglishTest(BaseModel):
    type: str
    score: float = Field(ge=0.0, le=9.0)
    section_scores: Dict[str, float] = Field(default_factory=dict)


class SATScore(BaseModel):
    total: Optional[int] = Field(default=None, ge=0, le=1600)
    math: Optional[int] = Field(default=None, ge=0, le=800)
    reading_writing: Optional[int] = Field(default=None, ge=0, le=800)


class ACTScore(BaseModel):
    composite: Optional[float] = Field(default=None, ge=0.0, le=36.0)
    sections: Dict[str, float] = Field(default_factory=dict)


class APIBScore(BaseModel):
    subject: str
    score: float = Field(ge=0.0)


class TestScores(BaseModel):
    english_tests: List[EnglishTest] = Field(default_factory=list)
    sat: Optional[SATScore] = None
    act: Optional[ACTScore] = None
    ap_ib: List[APIBScore] = Field(default_factory=list)


class ExtracurricularActivity(BaseModel):
    activity_name: str
    role: str
    organization: str
    start_date: str
    end_date: str
    hours_per_week: float = Field(ge=0.0)
    description: str


class LeadershipExperience(BaseModel):
    position: str
    organization: str
    description: str
    duration: str


class AwardRecord(BaseModel):
    award_name: str
    organizer: str
    level: str
    year: int = Field(ge=1900)
    description: str


class ProjectRecord(BaseModel):
    project_name: str
    role: str
    description: str
    link: Optional[str] = None
    start_date: str
    end_date: str


class PersonalStatement(BaseModel):
    content: str


class SupplementalEssay(BaseModel):
    school: str
    prompt: str
    content: str


class Essays(BaseModel):
    personal_statement: Optional[PersonalStatement] = None
    supplemental_essays: List[SupplementalEssay] = Field(default_factory=list)


class RecommendationLetter(BaseModel):
    from_: str = Field(alias="from")
    role: str
    relationship_duration: str
    content_summary: str


class FinancialProfile(BaseModel):
    budget_per_year: float = Field(ge=0.0)
    currency: str
    need_scholarship: bool
    scholarship_expectation_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    family_income_range: Optional[str] = None


class PreferenceProfile(BaseModel):
    dream_major: Optional[str] = None
    target_schools: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    ranking_preference: Optional[str] = None
    school_type_preference: Optional[str] = None


class StudentMatchRequest(BaseModel):
    student_id: str = Field(default="unknown", min_length=1)
    academic: AcademicProfile
    test_scores: TestScores
    intended_major: str = Field(min_length=1)
    extracurriculars: List[ExtracurricularActivity] = Field(default_factory=list)
    leadership: List[LeadershipExperience] = Field(default_factory=list)
    awards: List[AwardRecord] = Field(default_factory=list)
    projects: List[ProjectRecord] = Field(default_factory=list)
    essays: Essays = Field(default_factory=Essays)
    recommendation_letters: List[RecommendationLetter] = Field(default_factory=list)
    financial: FinancialProfile
    preferences: Optional[PreferenceProfile] = None
