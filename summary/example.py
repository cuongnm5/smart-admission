"""
Example usage of the matching engine with student profiles and configurations.

This example demonstrates:
1. Creating student profiles
2. Setting up matching engine configuration
3. Using the matching engine to rank universities
4. Customizing criteria and weights
"""

from .student_profile import (
    StudentProfile,
    AcademicProfile,
    TestScore,
    TestType,
    EssayProfile,
    PreferencesProfile,
    FinancialProfile,
    ExtracurricularActivity,
    ResidencyStatus,
)
from .config import (
    create_default_matching_engine_config,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    MatchingEngineConfig,
)
from .summary_service import MatchingEngine


class MockLLMClient:
    """Mock LLM client for testing (replace with actual LLM API in production)."""

    def evaluate(self, prompt: str) -> str:
        """Mock LLM evaluation."""
        # In production, this would call OpenAI, Claude, or other LLM APIs
        return "SCORE: 7.5\nREASONING: Good fit based on academic profile and program strength."


def create_sample_student() -> StudentProfile:
    """Create a sample student profile for demonstration."""
    student = StudentProfile(
        name="John Smith",
        email="john.smith@example.com",
        student_id="STU001",
        residency_status=ResidencyStatus.DOMESTIC,
        state_of_residence="California",
        # Academic Profile
        academic=AcademicProfile(
            gpa=3.85,
            gpa_scale=4.0,
            test_scores=[
                TestScore(test_type=TestType.SAT, score=1520, date="2024-11-01"),
            ],
            ap_scores={"Calculus AB": 5, "Physics C": 4, "Chemistry": 4},
            honors_courses=8,
        ),
        # Extracurricular Activities
        extracurricular_activities=[
            ExtracurricularActivity(
                name="Science Olympiad",
                category="Academic Competition",
                role="Team Captain",
                hours_per_week=8,
                years_involved=3,
                achievement_level=5,
            ),
            ExtracurricularActivity(
                name="Robotics Club",
                category="STEM",
                role="Lead Programmer",
                hours_per_week=10,
                years_involved=2,
                achievement_level=5,
            ),
            ExtracurricularActivity(
                name="Volunteer Tutoring",
                category="Community Service",
                role="Tutor",
                hours_per_week=5,
                years_involved=2,
                achievement_level=4,
            ),
        ],
        extracurricular_score=88.0,
        # Essay/Writing
        essay=EssayProfile(
            essay_score=92.0,
            essay_strength="excellent",
            writing_sample_quality=9,
        ),
        # Preferences
        preferences=PreferencesProfile(
            preferred_locations=["Boston", "San Francisco", "New York"],
            preferred_regions=["Northeast", "West Coast"],
            preferred_majors=["Computer Science", "Engineering", "Physics"],
            preferred_university_size="Large",
            preferred_campus_setting="Urban",
            special_interests=["AI/ML", "Robotics", "Renewable Energy"],
        ),
        # Financial Profile
        financial=FinancialProfile(
            annual_family_income=150000,
            budget_per_year=50000,
            needs_financial_aid=False,
            merit_scholarship_eligible=True,
            can_afford_full_cost=True,
        ),
        # Additional Info
        special_talents=["Programming", "Mathematics"],
        volunteer_hours=120,
        work_experience_years=0.5,
        first_generation=False,
        legacy_student=False,
        athlete=False,
    )
    return student


def create_sample_universities() -> list:
    """Create sample university data for demonstration."""
    universities = [
        {
            "name": "MIT",
            "qs_rank": 1,
            "avg_admitted_gpa": 3.97,
            "avg_test_score": 1550,
            "acceptance_rate": 0.03,
            "cost_of_attendance": 80000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Computer Science": 1, "Engineering": 1},
        },
        {
            "name": "Stanford",
            "qs_rank": 3,
            "avg_admitted_gpa": 3.96,
            "avg_test_score": 1545,
            "acceptance_rate": 0.04,
            "cost_of_attendance": 82000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Computer Science": 2, "Engineering": 2},
        },
        {
            "name": "Harvard",
            "qs_rank": 4,
            "avg_admitted_gpa": 3.99,
            "avg_test_score": 1540,
            "acceptance_rate": 0.04,
            "cost_of_attendance": 80000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Computer Science": 10, "Engineering": 15},
        },
        {
            "name": "Berkeley",
            "qs_rank": 10,
            "avg_admitted_gpa": 3.94,
            "avg_test_score": 1535,
            "acceptance_rate": 0.09,
            "cost_of_attendance": 45000,
            "financial_aid_percentage": 80,
            "program_ranking": {"Computer Science": 3, "Engineering": 5},
        },
        {
            "name": "Carnegie Mellon",
            "qs_rank": 25,
            "avg_admitted_gpa": 3.93,
            "avg_test_score": 1530,
            "acceptance_rate": 0.07,
            "cost_of_attendance": 80000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Computer Science": 1, "Engineering": 8},
        },
        {
            "name": "Princeton",
            "qs_rank": 15,
            "avg_admitted_gpa": 3.98,
            "avg_test_score": 1535,
            "acceptance_rate": 0.04,
            "cost_of_attendance": 78000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Computer Science": 12, "Engineering": 10},
        },
        {
            "name": "Caltech",
            "qs_rank": 6,
            "avg_admitted_gpa": 3.95,
            "avg_test_score": 1560,
            "acceptance_rate": 0.03,
            "cost_of_attendance": 82000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Physics": 1, "Engineering": 3},
        },
        {
            "name": "UChicago",
            "qs_rank": 12,
            "avg_admitted_gpa": 3.95,
            "avg_test_score": 1510,
            "acceptance_rate": 0.06,
            "cost_of_attendance": 82000,
            "financial_aid_percentage": 100,
            "program_ranking": {"Computer Science": 15, "Engineering": 20},
        },
        {
            "name": "Northwestern",
            "qs_rank": 32,
            "avg_admitted_gpa": 3.90,
            "avg_test_score": 1500,
            "acceptance_rate": 0.08,
            "cost_of_attendance": 80000,
            "financial_aid_percentage": 95,
            "program_ranking": {"Computer Science": 20, "Engineering": 12},
        },
        {
            "name": "Georgia Tech",
            "qs_rank": 35,
            "avg_admitted_gpa": 3.92,
            "avg_test_score": 1520,
            "acceptance_rate": 0.15,
            "cost_of_attendance": 35000,
            "financial_aid_percentage": 70,
            "program_ranking": {"Computer Science": 7, "Engineering": 1},
        },
    ]
    return universities


def example_basic_usage():
    """Example 1: Basic usage with default configuration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Usage with Default Configuration")
    print("=" * 80)

    # Create matching engine with default configuration
    llm_client = MockLLMClient()
    engine = MatchingEngine(llm_client)

    # Create student profile
    student = create_sample_student()
    print(f"\nStudent: {student.name}")
    print(f"GPA: {student.academic.gpa}")
    print(f"Preferred Majors: {student.preferences.preferred_majors}")

    # Get universities
    universities = create_sample_universities()

    # Run matching
    result = engine.match(student, universities)

    # Display results
    print(f"\nTop 10 Matched Universities for {result.student_name}:")
    print("-" * 80)
    for ranking in result.top_10_universities:
        print(f"\n{ranking.name}")
        print(f"  QS Rank: {ranking.qs_rank}")
        print(f"  Suitability: {ranking.suitability_score:.2f}/10")
        print(f"  Acceptance Probability: {ranking.acceptance_probability:.1f}%")
        print(f"  Combined Score: {ranking.combined_score:.2f}")


def example_custom_criteria():
    """Example 2: Custom criteria configuration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Custom Criteria Configuration")
    print("=" * 80)

    # Create custom criteria config emphasizing STEM programs
    custom_criteria = CriteriaWeightsConfig(
        criteria=[
            CriterionConfig(
                name="GPA Fit",
                criterion_type=CriterionType.GPA,
                weight=0.20,
                importance=1.0,
                description="How well does the student's GPA align with the university?",
            ),
            CriterionConfig(
                name="Major Ranking",
                criterion_type=CriterionType.MAJOR_RANKING,
                weight=0.40,  # Increased weight for major ranking
                importance=1.0,
                description="How highly ranked is the student's preferred major?",
            ),
            CriterionConfig(
                name="Test Score Alignment",
                criterion_type=CriterionType.TEST_SCORES,
                weight=0.20,
                importance=1.0,
                description="How do the student's test scores compare?",
            ),
            CriterionConfig(
                name="Location Fit",
                criterion_type=CriterionType.LOCATION,
                weight=0.20,
                importance=0.9,
                description="Does location match student preferences?",
            ),
        ]
    )

    # Create custom config
    default_config = create_default_matching_engine_config()
    custom_config = MatchingEngineConfig(
        criteria_weights=custom_criteria,
        prompt_config=default_config.prompt_config,
        ranking_weights=default_config.ranking_weights,
    )

    print("\nCustom Criteria Configuration:")
    print("-" * 80)
    for criterion in custom_criteria.criteria:
        print(f"{criterion.name}: weight={criterion.weight}, importance={criterion.importance}")

    # Create engine with custom config
    llm_client = MockLLMClient()
    engine = MatchingEngine(llm_client, custom_config)

    student = create_sample_student()
    universities = create_sample_universities()

    result = engine.match(student, universities)

    print(f"\nTop 5 Matched Universities (Custom Criteria):")
    print("-" * 80)
    for ranking in result.top_10_universities[:5]:
        print(f"{ranking.name}: {ranking.combined_score:.2f}")


def example_dynamic_weight_adjustment():
    """Example 3: Dynamically adjusting weights after creation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Dynamic Weight Adjustment")
    print("=" * 80)

    llm_client = MockLLMClient()
    engine = MatchingEngine(llm_client)

    # Update ranking weights to prioritize acceptance probability
    print("\nAdjusting ranking weights to prioritize acceptance probability...")
    engine.update_ranking_weights(
        suitability=0.3,
        acceptance=0.5,  # Increased from 0.3 to 0.5
        qs=0.2,
    )

    print(f"New ranking weights: {engine.get_config()['ranking_weights']}")

    student = create_sample_student()
    universities = create_sample_universities()

    result = engine.match(student, universities)

    print(f"\nTop 5 Universities (Acceptance Probability Prioritized):")
    print("-" * 80)
    for ranking in result.top_10_universities[:5]:
        print(f"{ranking.name}")
        print(f"  Acceptance: {ranking.acceptance_probability:.1f}%")
        print(f"  Combined Score: {ranking.combined_score:.2f}")


def example_enable_disable_criteria():
    """Example 4: Enable/disable specific criteria."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Enable/Disable Specific Criteria")
    print("=" * 80)

    llm_client = MockLLMClient()
    engine = MatchingEngine(llm_client)

    print("\nDisabling location criterion...")
    engine.enable_criterion("Location Fit", False)

    print(f"Enabled criteria: {[c.name for c in engine.config.criteria_weights.criteria if c.enabled]}")

    student = create_sample_student()
    universities = create_sample_universities()

    result = engine.match(student, universities)

    print(f"\nTop 5 Universities (Without Location Criterion):")
    print("-" * 80)
    for ranking in result.top_10_universities[:5]:
        print(f"{ranking.name}: {ranking.combined_score:.2f}")


def example_detailed_analysis():
    """Example 5: Viewing detailed analysis."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Detailed Analysis")
    print("=" * 80)

    llm_client = MockLLMClient()
    engine = MatchingEngine(llm_client)

    student = create_sample_student()
    universities = create_sample_universities()[:3]  # Just 3 for brevity

    result = engine.match(student, universities)

    # Display top university with full analysis
    if result.detailed_analysis["universities"]:
        top_uni = result.detailed_analysis["universities"][0]
        print(f"\nDetailed Analysis for: {top_uni['name']}")
        print("-" * 80)
        print(f"QS Rank: {top_uni['qs_rank']}")
        print(f"Combined Score: {top_uni['combined_score']:.2f}")
        print(f"Acceptance Probability: {top_uni['acceptance_probability']:.1f}%")
        print("\nScore Breakdown:")
        for key, value in top_uni["score_breakdown"].items():
            print(f"  {key}: {value:.2f}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MATCHING ENGINE EXAMPLES")
    print("=" * 80)

    example_basic_usage()
    example_custom_criteria()
    example_dynamic_weight_adjustment()
    example_enable_disable_criteria()
    example_detailed_analysis()

    print("\n" + "=" * 80)
    print("END OF EXAMPLES")
    print("=" * 80)

