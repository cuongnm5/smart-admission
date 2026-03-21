from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class ResidencyStatus(Enum):
    DOMESTIC = "domestic"
    INTERNATIONAL = "international"


class TestType(Enum):
    SAT = "sat"
    ACT = "act"
    IELTS = "ielts"
    TOEFL = "toefl"


class SchoolType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SPECIALIZED = "specialized"
    INTERNATIONAL = "international"


@dataclass
class GPA:
    """Represents GPA for a specific year/term."""
    year: str
    value: float
    scale: float = 4.0


@dataclass
class ClassRank:
    """Student's class ranking."""
    value: int
    total_students: int

    def percentile(self) -> float:
        """Calculate percentile rank."""
        if self.total_students == 0:
            return 0.0
        return 100 * (1 - (self.value - 1) / self.total_students)


@dataclass
class SchoolProfile:
    """Information about the student's school."""
    school_name: str
    school_type: SchoolType = SchoolType.PUBLIC
    location: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    is_gifted_school: bool = False


@dataclass
class TranscriptSubject:
    """Individual subject grade on transcript."""
    subject: str
    grade: float
    max_grade: float = 10.0
    level: str = "standard"  # standard, advanced, AP, IB

    def percentile(self) -> float:
        """Calculate grade as percentage."""
        if self.max_grade == 0:
            return 0.0
        return 100 * (self.grade / self.max_grade)


@dataclass
class TranscriptYear:
    """Transcript for a specific year."""
    year: str
    subjects: List[TranscriptSubject] = field(default_factory=list)

    def average_grade(self) -> float:
        """Calculate average grade for the year."""
        if not self.subjects:
            return 0.0
        return sum(s.percentile() for s in self.subjects) / len(self.subjects)


@dataclass
class EnglishTestScore:
    """English proficiency test score."""
    test_type: str  # IELTS, TOEFL, etc.
    score: float
    section_scores: Dict[str, float] = field(default_factory=dict)
    date: Optional[str] = None


@dataclass
class SATScore:
    """SAT test score."""
    total: int
    math: int
    reading_writing: int
    date: Optional[str] = None


@dataclass
class ACTScore:
    """ACT test score."""
    composite: int
    english: Optional[int] = None
    math: Optional[int] = None
    reading: Optional[int] = None
    science: Optional[int] = None
    date: Optional[str] = None


@dataclass
class APScore:
    """AP exam score."""
    subject: str
    score: int  # 1-5 scale
    date: Optional[str] = None


@dataclass
class IBScore:
    """IB exam score."""
    subject: str
    score: int  # 1-7 scale
    level: str = "SL"  # SL or HL
    date: Optional[str] = None


@dataclass
class TestScoresProfile:
    """Comprehensive test scores profile."""
    english_tests: List[EnglishTestScore] = field(default_factory=list)
    sat: Optional[SATScore] = None
    act: Optional[ACTScore] = None
    ap_scores: List[APScore] = field(default_factory=list)
    ib_scores: List[IBScore] = field(default_factory=list)

    def best_english_score(self) -> Optional[float]:
        """Get best English test score."""
        if not self.english_tests:
            return None
        return max(t.score for t in self.english_tests)

    def best_sat_score(self) -> Optional[int]:
        """Get best SAT total score."""
        return self.sat.total if self.sat else None

    def best_act_score(self) -> Optional[int]:
        """Get best ACT composite score."""
        return self.act.composite if self.act else None


@dataclass
class AcademicProfile:
    """Comprehensive academic profile."""
    # GPAs by year
    gpa_by_year: List[GPA] = field(default_factory=list)

    # Single GPA (current or overall)
    current_gpa: Optional[float] = None
    gpa_scale: float = 4.0

    # Class ranking
    class_rank: Optional[ClassRank] = None

    # School information
    school_profile: Optional[SchoolProfile] = None

    # Detailed transcript
    transcript: List[TranscriptYear] = field(default_factory=list)

    # Test scores
    test_scores: TestScoresProfile = field(default_factory=TestScoresProfile)

    # Advanced courses
    ap_scores: Optional[Dict[str, int]] = None
    ib_scores: Optional[Dict[str, int]] = None
    honors_courses: Optional[int] = None

    def weighted_gpa(self) -> float:
        """Calculate weighted GPA from all years."""
        if self.current_gpa is not None:
            return self.current_gpa
        if self.gpa_by_year:
            return sum(g.value for g in self.gpa_by_year) / len(self.gpa_by_year)
        return 3.5

    def gpa_trend(self) -> str:
        """Determine GPA trend (improving, declining, stable)."""
        if len(self.gpa_by_year) < 2:
            return "stable"

        gpas = [g.value for g in self.gpa_by_year]
        recent = sum(gpas[-2:]) / len(gpas[-2:]) if len(gpas) >= 2 else gpas[-1]
        earlier = sum(gpas[:-2]) / len(gpas[:-2]) if len(gpas) > 2 else gpas[0]

        if recent > earlier + 0.1:
            return "improving"
        elif recent < earlier - 0.1:
            return "declining"
        else:
            return "stable"


@dataclass
class ExtracurricularActivity:
    """Detailed extracurricular activity."""
    activity_name: str
    role: str
    organization: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    hours_per_week: Optional[float] = None
    category: Optional[str] = None
    achievement_level: int = 3  # 1-5 scale

    def duration_years(self) -> Optional[float]:
        """Calculate duration in years."""
        if not self.start_date or not self.end_date:
            return None
        try:
            start = datetime.strptime(self.start_date, "%Y-%m")
            end = datetime.strptime(self.end_date, "%Y-%m")
            return (end - start).days / 365.25
        except:
            return None


@dataclass
class Leadership:
    """Leadership position/experience."""
    position: str
    organization: str
    description: Optional[str] = None
    duration: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class Award:
    """Award or recognition."""
    award_name: str
    organizer: str
    level: str  # school, district, state, national, international
    year: int
    description: Optional[str] = None


@dataclass
class Project:
    """Student project/portfolio item."""
    project_name: str
    description: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    link: Optional[str] = None
    skills: List[str] = field(default_factory=list)


@dataclass
class Essay:
    """Essay with content and metadata."""
    essay_type: str  # personal_statement, supplemental, short_answer
    prompt: Optional[str] = None
    content: Optional[str] = None
    word_count: Optional[int] = None
    theme: Optional[str] = None


@dataclass
class RecommendationLetter:
    """Recommendation letter information."""
    from_name: str
    from_role: str
    relationship_duration: Optional[str] = None
    content_summary: Optional[str] = None
    school: Optional[str] = None


@dataclass
class EssayProfile:
    """Essays and writing samples."""
    personal_statement: Optional[Essay] = None
    supplemental_essays: List[Essay] = field(default_factory=list)
    essays: List[Essay] = field(default_factory=list)  # Generic essays
    recommendation_letters: List[RecommendationLetter] = field(default_factory=list)


@dataclass
class PreferencesProfile:
    """University and program preferences."""
    dream_major: Optional[str] = None
    intended_major: Optional[str] = None
    target_schools: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    preferred_regions: List[str] = field(default_factory=list)
    preferred_majors: List[str] = field(default_factory=list)
    preferred_university_size: Optional[str] = None  # small, medium, large
    preferred_campus_setting: Optional[str] = None  # urban, suburban, rural
    ranking_preference: Optional[str] = None  # e.g., "Top 50", "Top 100"
    school_type_preference: Optional[str] = None  # public, private, etc.
    special_interests: List[str] = field(default_factory=list)


@dataclass
class FinancialProfile:
    """Financial information."""
    budget_per_year: Optional[float] = None
    currency: str = "USD"
    needs_financial_aid: bool = False
    scholarship_expectation_percent: float = 0.0
    can_afford_full_cost: bool = False
    family_income_range: Optional[str] = None
    annual_family_income: Optional[float] = None
    merit_scholarship_eligible: bool = True


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
    academic: AcademicProfile = field(default_factory=AcademicProfile)

    # Intended Major
    intended_major: Optional[str] = None

    # Extracurricular Activities
    extracurricular_activities: List[ExtracurricularActivity] = field(
        default_factory=list
    )
    leadership_positions: List[Leadership] = field(default_factory=list)
    awards_recognitions: List[Award] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)

    # Essay/Writing
    essay: EssayProfile = field(default_factory=EssayProfile)

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
    cv_url: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for LLM processing."""
        return {
            "name": self.name,
            "email": self.email,
            "student_id": self.student_id,
            "residency_status": self.residency_status.value,
            "country_of_origin": self.country_of_origin,
            "state_of_residence": self.state_of_residence,
            "intended_major": self.intended_major,
            "academic": {
                "gpa_by_year": [
                    {"year": g.year, "value": g.value, "scale": g.scale}
                    for g in self.academic.gpa_by_year
                ],
                "current_gpa": self.academic.current_gpa,
                "weighted_gpa": self.academic.weighted_gpa(),
                "gpa_trend": self.academic.gpa_trend(),
                "gpa_scale": self.academic.gpa_scale,
                "class_rank": {
                    "value": self.academic.class_rank.value,
                    "total": self.academic.class_rank.total_students,
                    "percentile": self.academic.class_rank.percentile(),
                } if self.academic.class_rank else None,
                "school_profile": {
                    "school_name": self.academic.school_profile.school_name,
                    "school_type": self.academic.school_profile.school_type.value,
                    "location": self.academic.school_profile.location,
                    "country": self.academic.school_profile.country,
                    "description": self.academic.school_profile.description,
                    "is_gifted_school": self.academic.school_profile.is_gifted_school,
                } if self.academic.school_profile else None,
                "transcript": [
                    {
                        "year": ty.year,
                        "average_grade": ty.average_grade(),
                        "subjects": [
                            {
                                "subject": s.subject,
                                "grade": s.grade,
                                "max_grade": s.max_grade,
                                "percentile": s.percentile(),
                                "level": s.level,
                            }
                            for s in ty.subjects
                        ],
                    }
                    for ty in self.academic.transcript
                ],
                "test_scores": {
                    "english_tests": [
                        {
                            "type": et.test_type,
                            "score": et.score,
                            "sections": et.section_scores,
                            "date": et.date,
                        }
                        for et in self.academic.test_scores.english_tests
                    ],
                    "sat": {
                        "total": self.academic.test_scores.sat.total,
                        "math": self.academic.test_scores.sat.math,
                        "reading_writing": self.academic.test_scores.sat.reading_writing,
                        "date": self.academic.test_scores.sat.date,
                    } if self.academic.test_scores.sat else None,
                    "act": {
                        "composite": self.academic.test_scores.act.composite,
                        "english": self.academic.test_scores.act.english,
                        "math": self.academic.test_scores.act.math,
                        "reading": self.academic.test_scores.act.reading,
                        "science": self.academic.test_scores.act.science,
                        "date": self.academic.test_scores.act.date,
                    } if self.academic.test_scores.act else None,
                    "ap_scores": [
                        {"subject": ap.subject, "score": ap.score, "date": ap.date}
                        for ap in self.academic.test_scores.ap_scores
                    ],
                    "ib_scores": [
                        {
                            "subject": ib.subject,
                            "score": ib.score,
                            "level": ib.level,
                            "date": ib.date,
                        }
                        for ib in self.academic.test_scores.ib_scores
                    ],
                },
                "ap_scores_legacy": self.academic.ap_scores,
                "ib_scores_legacy": self.academic.ib_scores,
                "honors_courses": self.academic.honors_courses,
            },
            "extracurricular_activities": [
                {
                    "activity_name": act.activity_name,
                    "role": act.role,
                    "organization": act.organization,
                    "description": act.description,
                    "start_date": act.start_date,
                    "end_date": act.end_date,
                    "hours_per_week": act.hours_per_week,
                    "duration_years": act.duration_years(),
                    "category": act.category,
                    "achievement_level": act.achievement_level,
                }
                for act in self.extracurricular_activities
            ],
            "leadership_positions": [
                {
                    "position": lead.position,
                    "organization": lead.organization,
                    "description": lead.description,
                    "duration": lead.duration,
                    "start_date": lead.start_date,
                    "end_date": lead.end_date,
                }
                for lead in self.leadership_positions
            ],
            "awards_recognitions": [
                {
                    "award_name": award.award_name,
                    "organizer": award.organizer,
                    "level": award.level,
                    "year": award.year,
                    "description": award.description,
                }
                for award in self.awards_recognitions
            ],
            "projects": [
                {
                    "project_name": proj.project_name,
                    "description": proj.description,
                    "role": proj.role,
                    "start_date": proj.start_date,
                    "end_date": proj.end_date,
                    "link": proj.link,
                    "skills": proj.skills,
                }
                for proj in self.projects
            ],
            "essays": {
                "personal_statement": {
                    "content": self.essay.personal_statement.content,
                    "theme": self.essay.personal_statement.theme,
                } if self.essay.personal_statement else None,
                "supplemental_essays": [
                    {
                        "school": e.prompt,
                        "theme": e.theme,
                        "content": e.content,
                    }
                    for e in self.essay.supplemental_essays
                ],
                "recommendation_letters": [
                    {
                        "from": rl.from_name,
                        "role": rl.from_role,
                        "relationship_duration": rl.relationship_duration,
                        "content_summary": rl.content_summary,
                    }
                    for rl in self.essay.recommendation_letters
                ],
            },
            "preferences": {
                "dream_major": self.preferences.dream_major,
                "intended_major": self.preferences.intended_major,
                "target_schools": self.preferences.target_schools,
                "preferred_locations": self.preferences.preferred_locations,
                "preferred_regions": self.preferences.preferred_regions,
                "preferred_majors": self.preferences.preferred_majors,
                "preferred_university_size": self.preferences.preferred_university_size,
                "preferred_campus_setting": self.preferences.preferred_campus_setting,
                "ranking_preference": self.preferences.ranking_preference,
                "school_type_preference": self.preferences.school_type_preference,
                "special_interests": self.preferences.special_interests,
            },
            "financial": {
                "budget_per_year": self.financial.budget_per_year,
                "currency": self.financial.currency,
                "needs_financial_aid": self.financial.needs_financial_aid,
                "scholarship_expectation_percent": self.financial.scholarship_expectation_percent,
                "can_afford_full_cost": self.financial.can_afford_full_cost,
                "family_income_range": self.financial.family_income_range,
                "annual_family_income": self.financial.annual_family_income,
                "merit_scholarship_eligible": self.financial.merit_scholarship_eligible,
            },
            "special_talents": self.special_talents,
            "volunteer_hours": self.volunteer_hours,
            "work_experience_years": self.work_experience_years,
            "first_generation": self.first_generation,
            "legacy_student": self.legacy_student,
            "athlete": self.athlete,
            "cv_url": self.cv_url,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StudentProfile":
        """Create StudentProfile from dictionary (e.g., from API/JSON)."""
        # Parse academic profile
        academic_data = data.get("academic", {})

        gpa_by_year = [
            GPA(year=g["year"], value=g["value"], scale=g.get("scale", 4.0))
            for g in academic_data.get("gpa", [])
        ]

        class_rank_data = academic_data.get("class_rank")
        class_rank = (
            ClassRank(
                value=class_rank_data["value"],
                total_students=class_rank_data["total_students"],
            )
            if class_rank_data
            else None
        )

        school_data = academic_data.get("school_profile")
        school_profile = (
            SchoolProfile(
                school_name=school_data["school_name"],
                school_type=SchoolType(school_data.get("school_type", "public")),
                location=school_data.get("location"),
                country=school_data.get("country"),
                description=school_data.get("description"),
                is_gifted_school=school_data.get("is_gifted_school", False),
            )
            if school_data
            else None
        )

        transcript = [
            TranscriptYear(
                year=ty["year"],
                subjects=[
                    TranscriptSubject(
                        subject=s["subject"],
                        grade=s["grade"],
                        max_grade=s.get("max_grade", 10.0),
                        level=s.get("level", "standard"),
                    )
                    for s in ty.get("subjects", [])
                ],
            )
            for ty in academic_data.get("transcript", [])
        ]

        test_scores_data = academic_data.get("test_scores", {})
        english_tests = [
            EnglishTestScore(
                test_type=et["type"],
                score=et["score"],
                section_scores=et.get("section_scores", {}),
                date=et.get("date"),
            )
            for et in test_scores_data.get("english_tests", [])
        ]

        sat_data = test_scores_data.get("sat")
        sat = (
            SATScore(
                total=sat_data["total"],
                math=sat_data["math"],
                reading_writing=sat_data["reading_writing"],
                date=sat_data.get("date"),
            )
            if sat_data
            else None
        )

        act_data = test_scores_data.get("act")
        act = (
            ACTScore(
                composite=act_data.get("composite"),
                english=act_data.get("english"),
                math=act_data.get("math"),
                reading=act_data.get("reading"),
                science=act_data.get("science"),
                date=act_data.get("date"),
            )
            if act_data
            else None
        )

        ap_scores = [
            APScore(
                subject=ap["subject"],
                score=ap["score"],
                date=ap.get("date"),
            )
            for ap in test_scores_data.get("ap_ib", [])
            if "AP" in ap.get("subject", "")
        ]

        ib_scores = [
            IBScore(
                subject=ib["subject"],
                score=ib["score"],
                level=ib.get("level", "SL"),
                date=ib.get("date"),
            )
            for ib in test_scores_data.get("ap_ib", [])
            if "IB" in ib.get("subject", "")
        ]

        test_scores = TestScoresProfile(
            english_tests=english_tests,
            sat=sat,
            act=act,
            ap_scores=ap_scores,
            ib_scores=ib_scores,
        )

        academic = AcademicProfile(
            gpa_by_year=gpa_by_year,
            current_gpa=academic_data.get("current_gpa"),
            gpa_scale=academic_data.get("gpa_scale", 4.0),
            class_rank=class_rank,
            school_profile=school_profile,
            transcript=transcript,
            test_scores=test_scores,
        )

        # Parse extracurricular activities
        extracurricular_activities = [
            ExtracurricularActivity(
                activity_name=act["activity_name"],
                role=act["role"],
                organization=act["organization"],
                description=act.get("description"),
                start_date=act.get("start_date"),
                end_date=act.get("end_date"),
                hours_per_week=act.get("hours_per_week"),
                category=act.get("category"),
                achievement_level=act.get("achievement_level", 3),
            )
            for act in data.get("extracurriculars", [])
        ]

        # Parse leadership positions
        leadership_positions = [
            Leadership(
                position=lead["position"],
                organization=lead["organization"],
                description=lead.get("description"),
                duration=lead.get("duration"),
                start_date=lead.get("start_date"),
                end_date=lead.get("end_date"),
            )
            for lead in data.get("leadership", [])
        ]

        # Parse awards
        awards_recognitions = [
            Award(
                award_name=award["award_name"],
                organizer=award["organizer"],
                level=award.get("level", "school"),
                year=award["year"],
                description=award.get("description"),
            )
            for award in data.get("awards", [])
        ]

        # Parse projects
        projects = [
            Project(
                project_name=proj["project_name"],
                description=proj["description"],
                role=proj["role"],
                start_date=proj.get("start_date"),
                end_date=proj.get("end_date"),
                link=proj.get("link"),
                skills=proj.get("skills", []),
            )
            for proj in data.get("projects", [])
        ]

        # Parse essays
        essays_data = data.get("essays", {})
        personal_statement_data = essays_data.get("personal_statement")
        personal_statement = (
            Essay(
                essay_type="personal_statement",
                content=personal_statement_data.get("content"),
            )
            if personal_statement_data
            else None
        )

        supplemental_essays = [
            Essay(
                essay_type="supplemental",
                prompt=essay.get("prompt"),
                content=essay.get("content"),
                theme=essay.get("school"),
            )
            for essay in essays_data.get("supplemental_essays", [])
        ]

        recommendation_letters = [
            RecommendationLetter(
                from_name=letter["from"],
                from_role=letter["role"],
                relationship_duration=letter.get("relationship_duration"),
                content_summary=letter.get("content_summary"),
            )
            for letter in essays_data.get("recommendation_letters", [])
        ]

        essay = EssayProfile(
            personal_statement=personal_statement,
            supplemental_essays=supplemental_essays,
            recommendation_letters=recommendation_letters,
        )

        # Parse preferences
        preferences_data = data.get("preferences", {})
        preferences = PreferencesProfile(
            dream_major=preferences_data.get("dream_major"),
            intended_major=data.get("intended_major"),
            target_schools=preferences_data.get("target_schools", []),
            preferred_locations=preferences_data.get("preferred_locations", []),
            preferred_regions=preferences_data.get("preferred_regions", []),
            preferred_majors=preferences_data.get("preferred_majors", []),
            preferred_university_size=preferences_data.get("preferred_university_size"),
            preferred_campus_setting=preferences_data.get("preferred_campus_setting"),
            ranking_preference=preferences_data.get("ranking_preference"),
            school_type_preference=preferences_data.get("school_type_preference"),
            special_interests=preferences_data.get("special_interests", []),
        )

        # Parse financial
        financial_data = data.get("financial", {})
        financial = FinancialProfile(
            budget_per_year=financial_data.get("budget_per_year"),
            currency=financial_data.get("currency", "USD"),
            needs_financial_aid=financial_data.get("need_scholarship", financial_data.get("needs_financial_aid", False)),
            scholarship_expectation_percent=financial_data.get("scholarship_expectation_percent", 0),
            family_income_range=financial_data.get("family_income_range"),
            annual_family_income=financial_data.get("annual_family_income"),
        )

        # Create student profile
        return cls(
            name=data.get("name", "Unknown"),
            email=data.get("email", ""),
            student_id=data.get("student_id"),
            residency_status=ResidencyStatus(data.get("residency_status", "domestic")),
            country_of_origin=data.get("country_of_origin"),
            state_of_residence=data.get("state_of_residence"),
            intended_major=data.get("intended_major"),
            academic=academic,
            extracurricular_activities=extracurricular_activities,
            leadership_positions=leadership_positions,
            awards_recognitions=awards_recognitions,
            projects=projects,
            essay=essay,
            preferences=preferences,
            financial=financial,
            special_talents=data.get("special_talents"),
            volunteer_hours=data.get("volunteer_hours"),
            work_experience_years=data.get("work_experience_years"),
            first_generation=data.get("first_generation", False),
            legacy_student=data.get("legacy_student", False),
            athlete=data.get("athlete", False),
            cv_url=data.get("additional", {}).get("cv"),
        )
