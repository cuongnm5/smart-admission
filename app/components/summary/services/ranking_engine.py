from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

from ..dto.config import RankingWeightsConfig


class SortOrder(Enum):
    QS_RANK = "qs_rank"
    SUITABILITY = "suitability"
    ACCEPTANCE_PROBABILITY = "acceptance_probability"


@dataclass
class UniversityRanking:
    name: str
    qs_rank: int
    suitability_score: float
    acceptance_probability: float
    combined_score: float
    details: Dict = None  # Optional additional details about the ranking


class RankingEngine:
    """
    Ranks universities based on multiple factors: QS ranking, suitability, and acceptance probability.
    Uses weighted combination of these factors to produce final ranking.
    """

    def __init__(self, ranking_config: Optional[RankingWeightsConfig] = None):
        """
        Initialize the ranking engine.

        Args:
            ranking_config: Configuration for weights. If None, uses default.
        """
        if ranking_config is None:
            from ..dto.config import create_default_ranking_weights

            ranking_config = create_default_ranking_weights()

        ranking_config.validate_weights()
        self.ranking_config = ranking_config

    def rank_universities(
        self,
        universities: List[Dict],
        suitability_scores: Dict[str, float],
        acceptance_probabilities: Dict[str, float],
    ) -> List[UniversityRanking]:
        """
        Rank top 20 universities down to top 10.

        Args:
            universities: List of university data dicts with 'name' and 'qs_rank' fields
            suitability_scores: Dict mapping university name to suitability score (0-10)
            acceptance_probabilities: Dict mapping university name to acceptance probability (0-100)

        Returns:
            List of top 10 UniversityRanking objects sorted by combined score
        """
        rankings = []

        for uni in universities:
            uni_name = uni["name"]
            qs_rank = uni.get("qs_rank", 1000)

            suitability = suitability_scores.get(uni_name, 5.0)
            acceptance_prob = acceptance_probabilities.get(uni_name, 50.0)

            combined_score = self._calculate_combined_score(
                qs_rank, suitability, acceptance_prob
            )

            rankings.append(
                UniversityRanking(
                    name=uni_name,
                    qs_rank=qs_rank,
                    suitability_score=suitability,
                    acceptance_probability=acceptance_prob,
                    combined_score=combined_score,
                    details={
                        "qs_contribution": self.ranking_config.qs_weight
                        * max(0.0, 100.0 - (qs_rank / 10.0)),
                        "suitability_contribution": self.ranking_config.suitability_weight
                        * (suitability * 10),
                        "acceptance_contribution": self.ranking_config.acceptance_weight
                        * acceptance_prob,
                    },
                )
            )

        # Sort by combined score in descending order
        rankings.sort(key=lambda x: x.combined_score, reverse=True)

        # Return top 10
        return rankings[:10]

    def _calculate_combined_score(
        self, qs_rank: int, suitability: float, acceptance_prob: float
    ) -> float:
        """
        Combine all factors into final score (0-100 scale).

        Args:
            qs_rank: University QS ranking (lower is better)
            suitability: Suitability score (0-10 scale)
            acceptance_prob: Acceptance probability (0-100 scale)

        Returns:
            Combined score (0-100 scale)
        """
        # Convert QS rank to score (lower rank = higher score)
        # QS rank 1 = 100, QS rank 100 = 90, QS rank 1000 = 0
        qs_score = max(0.0, 100.0 - (qs_rank / 10.0))

        # Suitability is 0-10, convert to 0-100
        suitability_score = suitability * 10

        # Acceptance probability is already 0-100
        acceptance_score = acceptance_prob

        # Weighted combination
        combined = (
            self.ranking_config.qs_weight * qs_score
            + self.ranking_config.suitability_weight * suitability_score
            + self.ranking_config.acceptance_weight * acceptance_score
        )

        return combined

    def get_weights_summary(self) -> Dict:
        """Get current ranking weights configuration."""
        return self.ranking_config.to_dict()
