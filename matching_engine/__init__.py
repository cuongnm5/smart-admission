# Student Profile
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

# Configuration
from .config import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    LLMPromptConfig,
    EvaluationCriterionPrompt,
    create_default_matching_engine_config,
    create_default_criteria_config,
    create_default_prompt_config,
    create_default_ranking_weights,
)

# Calculators
from .suitability_calculator import SuitabilityCalculator, SuitabilityScore
from .acceptance_calculator import AcceptanceCalculator, ApplicationScores

# Ranking
from .ranking_engine import RankingEngine, UniversityRanking

# Import MatchingEngine and MatchResult after other modules to avoid circular imports
def __getattr__(name):
    if name == "MatchingEngine":
        from .matching_engine import MatchingEngine
        return MatchingEngine
    elif name == "MatchResult":
        from .matching_engine import MatchResult
        return MatchResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Student Profile
    "StudentProfile",
    "AcademicProfile",
    "TestScore",
    "TestType",
    "EssayProfile",
    "PreferencesProfile",
    "FinancialProfile",
    "ExtracurricularActivity",
    "ResidencyStatus",
    # Configuration
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
    # Calculators
    "SuitabilityCalculator",
    "SuitabilityScore",
    "AcceptanceCalculator",
    "ApplicationScores",
    # Ranking
    "RankingEngine",
    "UniversityRanking",
    # Main Engine
    "MatchingEngine",
    "MatchResult",
]
