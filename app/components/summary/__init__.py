from .dto.config import (
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    EvaluationCriterionPrompt,
    LLMPromptConfig,
    MatchingEngineConfig,
    RankingWeightsConfig,
    create_default_criteria_config,
    create_default_matching_engine_config,
    create_default_prompt_config,
    create_default_ranking_weights,
)
from .dto.student_profile import (
    APScore,
    ACTScore,
    AcademicProfile,
    Award,
    ClassRank,
    EnglishTestScore,
    Essay,
    EssayProfile,
    ExtracurricularActivity,
    FinancialProfile,
    GPA,
    IBScore,
    Leadership,
    PreferencesProfile,
    Project,
    RecommendationLetter,
    ResidencyStatus,
    SATScore,
    SchoolProfile,
    SchoolType,
    StudentProfile,
    TestScoresProfile,
    TestType,
    TranscriptSubject,
    TranscriptYear,
)
from .services.acceptance_calculator import AcceptanceCalculator, ApplicationScores
from .services.ranking_engine import RankingEngine, UniversityRanking
from .services.suitability_calculator import SuitabilityCalculator, SuitabilityScore


def __getattr__(name):
    if name == "MatchingEngine":
        from .services.summary_service import MatchingEngine

        return MatchingEngine
    if name == "MatchResult":
        from .services.summary_service import MatchResult

        return MatchResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "StudentProfile",
    "AcademicProfile",
    "GPA",
    "ClassRank",
    "SchoolProfile",
    "SchoolType",
    "TranscriptSubject",
    "TranscriptYear",
    "EnglishTestScore",
    "SATScore",
    "ACTScore",
    "APScore",
    "IBScore",
    "TestScoresProfile",
    "EssayProfile",
    "Essay",
    "RecommendationLetter",
    "PreferencesProfile",
    "FinancialProfile",
    "ExtracurricularActivity",
    "Leadership",
    "Award",
    "Project",
    "ResidencyStatus",
    "TestType",
    "MatchingEngineConfig",
    "CriteriaWeightsConfig",
    "CriterionConfig",
    "CriterionType",
    "RankingWeightsConfig",
    "LLMPromptConfig",
    "EvaluationCriterionPrompt",
    "create_default_matching_engine_config",
    "create_default_criteria_config",
    "create_default_prompt_config",
    "create_default_ranking_weights",
    "SuitabilityCalculator",
    "SuitabilityScore",
    "AcceptanceCalculator",
    "ApplicationScores",
    "RankingEngine",
    "UniversityRanking",
    "MatchingEngine",
    "MatchResult",
]
