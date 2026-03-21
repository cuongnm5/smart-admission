from typing import List, Dict, Optional
from dataclasses import dataclass

from .student_profile import StudentProfile
from .suitability_calculator import SuitabilityCalculator
from .acceptance_calculator import AcceptanceCalculator
from .ranking_engine import RankingEngine, UniversityRanking
from .config import (
    MatchingEngineConfig,
    create_default_matching_engine_config,
)


@dataclass
class MatchResult:
    """Complete matching result for a student."""

    student_name: str
    top_10_universities: List[UniversityRanking]
    detailed_analysis: Dict = None


class MatchingEngine:
    """
    Main matching engine that combines suitability, acceptance probability,
    and QS ranking to match students with universities.

    Integrates:
    - StudentProfile: Comprehensive student data
    - SuitabilityCalculator: LLM-based criterion evaluation with weighted scores
    - AcceptanceCalculator: Data-driven acceptance probability estimation
    - RankingEngine: Final ranking combining all factors
    """

    def __init__(
        self,
        llm_client,
        config: Optional[MatchingEngineConfig] = None,
    ):
        """
        Initialize the matching engine.

        Args:
            llm_client: LLM client for suitability evaluation
            config: MatchingEngineConfig. If None, uses default configuration.
        """
        if config is None:
            config = create_default_matching_engine_config()

        # Validate configuration
        config.validate()

        self.config = config
        self.suitability_calc = SuitabilityCalculator(
            llm_client,
            criteria_config=config.criteria_weights,
            prompt_config=config.prompt_config,
        )
        self.acceptance_calc = AcceptanceCalculator()
        self.ranking_engine = RankingEngine(config.ranking_weights)

    def match(
        self,
        student: StudentProfile,
        top_20_universities: List[Dict],
    ) -> MatchResult:
        """
        Main entry point: match student to universities.

        Args:
            student: StudentProfile object with complete student data
            top_20_universities: List of pre-filtered universities (from hard filters)
                               Each dict should have: name, qs_rank, avg_admitted_gpa, etc.

        Returns:
            MatchResult with top 10 ranked universities
        """
        # Convert student profile to dict for calculations
        student_dict = student.to_dict()

        suitability_scores = {}
        acceptance_probabilities = {}
        detailed_scores = {}

        # Calculate suitability and acceptance for each university
        for university in top_20_universities:
            uni_name = university["name"]

            # Calculate suitability score using LLM
            suitability, detailed = self.suitability_calc.calculate_suitability(
                student_dict, university
            )
            suitability_scores[uni_name] = suitability
            detailed_scores[uni_name] = detailed

            # Calculate acceptance probability
            acceptance_prob, app_scores = (
                self.acceptance_calc.calculate_acceptance_probability(
                    student_dict, university
                )
            )
            acceptance_probabilities[uni_name] = acceptance_prob

        # Rank universities
        final_rankings = self.ranking_engine.rank_universities(
            top_20_universities,
            suitability_scores,
            acceptance_probabilities,
        )

        # Build detailed analysis
        analysis = self._build_analysis(
            student, final_rankings, detailed_scores, acceptance_probabilities
        )

        return MatchResult(
            student_name=student.name,
            top_10_universities=final_rankings,
            detailed_analysis=analysis,
        )

    def _build_analysis(
        self,
        student: StudentProfile,
        rankings: List[UniversityRanking],
        suitability_details: Dict,
        acceptance_probs: Dict,
    ) -> Dict:
        """Build detailed analysis for matched universities."""
        analysis = {
            "student": {
                "name": student.name,
                "gpa": student.academic.gpa,
                "test_scores": [
                    {
                        "type": ts.test_type.value,
                        "score": ts.score,
                    }
                    for ts in student.academic.test_scores
                ],
                "preferred_majors": student.preferences.preferred_majors,
            },
            "criteria_config": self.config.criteria_weights.to_dict(),
            "ranking_config": self.config.ranking_weights.to_dict(),
            "universities": [],
        }

        for idx, ranking in enumerate(rankings, 1):
            uni_details = {
                "rank": idx,
                "name": ranking.name,
                "qs_rank": ranking.qs_rank,
                "suitability_score": ranking.suitability_score,
                "acceptance_probability": ranking.acceptance_probability,
                "combined_score": ranking.combined_score,
                "score_breakdown": ranking.details,
                "criterion_analysis": [
                    {
                        "criterion": score.criterion_name,
                        "score": score.score,
                        "weight": score.weight,
                        "importance": score.importance,
                        "reasoning": score.reasoning,
                    }
                    for score in suitability_details.get(ranking.name, [])
                ],
            }
            analysis["universities"].append(uni_details)

        return analysis

    def get_config(self) -> Dict:
        """Get current engine configuration."""
        return self.config.to_dict()

    def update_criteria_weights(self, new_weights: Dict[str, float]) -> None:
        """
        Update criterion weights dynamically.

        Args:
            new_weights: Dict mapping criterion names to new weights
        """
        for criterion in self.config.criteria_weights.criteria:
            if criterion.name in new_weights:
                criterion.weight = new_weights[criterion.name]

        self.config.criteria_weights.validate_weights()
        self.suitability_calc.criteria_config = self.config.criteria_weights

    def update_ranking_weights(
        self, suitability: float, acceptance: float, qs: float
    ) -> None:
        """
        Update ranking weights dynamically.

        Args:
            suitability: Weight for suitability factor (0-1)
            acceptance: Weight for acceptance probability factor (0-1)
            qs: Weight for QS ranking factor (0-1)
        """
        self.config.ranking_weights.suitability_weight = suitability
        self.config.ranking_weights.acceptance_weight = acceptance
        self.config.ranking_weights.qs_weight = qs

        self.config.ranking_weights.validate_weights()
        self.ranking_engine.ranking_config = self.config.ranking_weights

    def enable_criterion(self, criterion_name: str, enabled: bool) -> None:
        """Enable or disable a specific criterion."""
        for criterion in self.config.criteria_weights.criteria:
            if criterion.name == criterion_name:
                criterion.enabled = enabled
                break
