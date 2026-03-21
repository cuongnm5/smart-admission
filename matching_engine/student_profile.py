from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class ResidencyStatus(Enum):
    DOMESTIC = "domestic"
    INTERNATIONAL = "international"


class TestType(Enum):
    SAT = "sat"
    ACT = "act"


@dataclass
class TestScore:
    test_type: TestType
    score: int
    date: Optional[str] = None


@dataclass
class AcademicProfile:
    gpa: float
    gpa_scale: float = 4.0
    test_scores: List[TestScore] = field(default_factory=list)
    ap_scores: Optional[Dict[str, int]] = None
    ib_scores: Optional[Dict[str, int]] = None
    honors_courses: Optional[int] = None


@dataclass
class ExtracurricularActivity:
    name: str
    category: str
    role: Optional[str] = None
    hours_per_week: Optional[float] = None
    years_involved: Optional[int] = None
    achievement_level: int = 1  # 1-5 scale


@dataclass
class EssayProfile:
    essay_score: float  # 0-100 scale
    essay_strength: str = "good"  # poor, fair, good, excellent
    writing_sample_quality: Optional[int] = None


@dataclass
class PreferencesProfile:
    preferred_locations: List[str] = field(default_factory=list)
    preferred_regions: List[str] = field(default_factory=list)
    preferred_majors: List[str] = field(default_factory=list)
    preferred_university_size: Optional[str] = None  # small, medium, large
    preferred_campus_setting: Optional[str] = None  # urban, suburban, rural
    special_interests: List[str] = field(default_factory=list)


@dataclass
class FinancialProfile:
    annual_family_income: Optional[float] = None
    budget_per_year: Optional[float] = None
    needs_financial_aid: bool = False
    merit_scholarship_eligible: bool = True
    can_afford_full_cost: bool = False


@dataclass
class StudentProfile:
    """Comprehensive student profile for university matching."""

    # Basic Information
    name: str
    email: str
    student_id: Optional[str] = None

    # Demographics
    residency_status: ResidencyStatus = ResidencyStatus.DOMESTIC
    country_of_origin: Optional[str] = None
    state_of_residence: Optional[str] = None

    # Academic Profile
    academic: AcademicProfile = field(default_factory=lambda: AcademicProfile(gpa=3.5))

    # Extracurricular Activities
    extracurricular_activities: List[ExtracurricularActivity] = field(
        default_factory=list
    )
    extracurricular_score: float = 75.0  # 0-100 scale

    # Essay/Writing
    essay: EssayProfile = field(
        default_factory=lambda: EssayProfile(essay_score=75.0)
    )

    # Preferences
    preferences: PreferencesProfile = field(default_factory=PreferencesProfile)

    # Financial Information
    financial: FinancialProfile = field(default_factory=FinancialProfile)

    # Additional Information
    special_talents: Optional[List[str]] = None
    volunteer_hours: Optional[int] = None
    work_experience_years: Optional[float] = None
    first_generation: bool = False
    legacy_student: bool = False
    athlete: bool = False

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for LLM processing."""
        return {
            "name": self.name,
            "email": self.email,
            "student_id": self.student_id,
            "residency_status": self.residency_status.value,
            "country_of_origin": self.country_of_origin,
            "state_of_residence": self.state_of_residence,
            "academic": {
                "gpa": self.academic.gpa,
                "gpa_scale": self.academic.gpa_scale,
                "test_scores": [
                    {
                        "test_type": ts.test_type.value,
                        "score": ts.score,
                        "date": ts.date,
                    }
                    for ts in self.academic.test_scores
                ],
                "ap_scores": self.academic.ap_scores,
                "ib_scores": self.academic.ib_scores,
                "honors_courses": self.academic.honors_courses,
            },
            "extracurricular_activities": [
                {
                    "name": activity.name,
                    "category": activity.category,
                    "role": activity.role,
                    "hours_per_week": activity.hours_per_week,
                    "years_involved": activity.years_involved,
                    "achievement_level": activity.achievement_level,
                }
                for activity in self.extracurricular_activities
            ],
            "extracurricular_score": self.extracurricular_score,
            "essay": {
                "essay_score": self.essay.essay_score,
                "essay_strength": self.essay.essay_strength,
                "writing_sample_quality": self.essay.writing_sample_quality,
            },
            "preferences": {
                "preferred_locations": self.preferences.preferred_locations,
                "preferred_regions": self.preferences.preferred_regions,
                "preferred_majors": self.preferences.preferred_majors,
                "preferred_university_size": self.preferences.preferred_university_size,
                "preferred_campus_setting": self.preferences.preferred_campus_setting,
                "special_interests": self.preferences.special_interests,
            },
            "financial": {
                "annual_family_income": self.financial.annual_family_income,
                "budget_per_year": self.financial.budget_per_year,
                "needs_financial_aid": self.financial.needs_financial_aid,
                "merit_scholarship_eligible": self.financial.merit_scholarship_eligible,
                "can_afford_full_cost": self.financial.can_afford_full_cost,
            },
            "special_talents": self.special_talents,
            "volunteer_hours": self.volunteer_hours,
            "work_experience_years": self.work_experience_years,
            "first_generation": self.first_generation,
            "legacy_student": self.legacy_student,
            "athlete": self.athlete,
        }

