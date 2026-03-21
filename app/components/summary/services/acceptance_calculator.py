from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ApplicationScores:
    """Breakdown of application component scores (0-100 scale)."""

    gpa_score: float
    test_score: float
    essay_score: float
    extracurricular_score: float
    overall_strength: float

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "gpa_score": self.gpa_score,
            "test_score": self.test_score,
            "essay_score": self.essay_score,
            "extracurricular_score": self.extracurricular_score,
            "overall_strength": self.overall_strength,
        }


class AcceptanceCalculator:
    """
    Calculate probability of acceptance based on student application strength.
    Uses data-driven approach combining GPA, test scores, essays, and extracurriculars.
    """

    # Weighting for different application components
    DEFAULT_WEIGHTS = {
        "gpa": 0.35,
        "test": 0.35,
        "essay": 0.20,
        "extracurricular": 0.10,
    }

    def __init__(
        self,
        base_acceptance_rate: Optional[float] = None,
        component_weights: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize the acceptance calculator.

        Args:
            base_acceptance_rate: Default acceptance rate if not provided by university (default: 0.25)
            component_weights: Custom weights for application components. If None, uses DEFAULT_WEIGHTS.
        """
        self.base_acceptance_rate = base_acceptance_rate or 0.25
        self.component_weights = component_weights or self.DEFAULT_WEIGHTS

        # Validate weights sum to 1.0
        total_weight = sum(self.component_weights.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(
                f"Component weights must sum to 1.0, got {total_weight}"
            )

    def calculate_acceptance_probability(
        self, student_profile: Dict, university_data: Dict
    ) -> tuple[float, ApplicationScores]:
        """
        Calculate probability of acceptance based on application strength.

        Args:
            student_profile: Student profile dictionary (from StudentProfile.to_dict())
            university_data: University data dictionary

        Returns:
            Tuple of (acceptance_probability: float (0-100), application_scores: ApplicationScores)
        """
        app_scores = self._score_application(student_profile, university_data)
        acceptance_prob = self._calculate_probability(app_scores, university_data)

        return acceptance_prob, app_scores

    def _score_application(
        self, student: Dict, university: Dict
    ) -> ApplicationScores:
        """
        Score individual components of the application.

        Args:
            student: Student profile dictionary
            university: University data dictionary

        Returns:
            ApplicationScores with all component scores (0-100 scale)
        """
        # Extract student academic data
        academic = student.get("academic", {})
        essay = student.get("essay", {})

        student_gpa = academic.get("gpa", 3.0)
        student_test_score = self._extract_best_test_score(academic)
        essay_score = essay.get("essay_score", 75.0)
        extracurricular_score = student.get("extracurricular_score", 75.0)

        # Score each component
        gpa_score = self._score_gpa(
            student_gpa, university.get("avg_admitted_gpa", 3.8)
        )
        test_score = self._score_test(
            student_test_score, university.get("avg_test_score", 1450)
        )

        # Calculate overall strength using weighted average
        overall_strength = (
            gpa_score * self.component_weights["gpa"]
            + test_score * self.component_weights["test"]
            + essay_score * self.component_weights["essay"]
            + extracurricular_score * self.component_weights["extracurricular"]
        )

        return ApplicationScores(
            gpa_score=gpa_score,
            test_score=test_score,
            essay_score=essay_score,
            extracurricular_score=extracurricular_score,
            overall_strength=overall_strength,
        )

    def _extract_best_test_score(self, academic: Dict) -> int:
        """Extract the best test score from student's academic profile."""
        test_scores = academic.get("test_scores", [])
        if not test_scores:
            return 0

        if isinstance(test_scores, list):
            return max((ts.get("score", 0) for ts in test_scores), default=0)

        if isinstance(test_scores, dict):
            english_scores = [
                item.get("score", 0)
                for item in test_scores.get("english_tests", [])
                if isinstance(item, dict)
            ]
            sat_total = 0
            sat_data = test_scores.get("sat")
            if isinstance(sat_data, dict):
                sat_total = sat_data.get("total", 0) or 0

            act_composite = 0
            act_data = test_scores.get("act")
            if isinstance(act_data, dict):
                act_composite = act_data.get("composite", 0) or 0

            return int(max(english_scores + [sat_total, act_composite], default=0))

        return 0

    def _score_gpa(self, student_gpa: float, avg_admitted_gpa: float) -> float:
        """
        Convert GPA to 0-100 scale based on comparison to university average.

        Args:
            student_gpa: Student's GPA
            avg_admitted_gpa: Average GPA of admitted students

        Returns:
            Score on 0-100 scale
        """
        if avg_admitted_gpa == 0:
            return 50.0

        # Percentile comparison
        percentile = min(student_gpa / avg_admitted_gpa, 1.0)
        return percentile * 100

    def _score_test(self, student_score: int, avg_score: int) -> float:
        """
        Convert test score to 0-100 scale based on comparison to university average.

        Args:
            student_score: Student's test score (SAT or ACT equivalent)
            avg_score: Average test score of admitted students

        Returns:
            Score on 0-100 scale
        """
        if avg_score == 0 or student_score == 0:
            return 50.0

        # Percentile comparison
        percentile = min(student_score / avg_score, 1.0)
        return percentile * 100

    def _calculate_probability(
        self, app_scores: ApplicationScores, university: Dict
    ) -> float:
        """
        Calculate acceptance probability using logistic model.

        The model considers:
        1. University's base acceptance rate (selectivity)
        2. Student's overall application strength relative to average admitted student

        Args:
            app_scores: ApplicationScores object with component scores
            university: University data dictionary

        Returns:
            Acceptance probability (0-100 scale)
        """
        # Get university acceptance rate (lower rate = more selective)
        base_rate = university.get("acceptance_rate", self.base_acceptance_rate)

        # University selectivity: 1.0 - acceptance_rate
        # More selective universities have lower acceptance rates
        selectivity = 1.0 - base_rate

        # Normalize student strength to 0-1 scale
        strength_factor = app_scores.overall_strength / 100.0

        # Logistic adjustment:
        # - If student strength = 100%, increase acceptance prob by 50% of selectivity
        # - If student strength = 50%, acceptance prob stays at base rate
        # - If student strength < 50%, acceptance prob decreases
        adjusted_probability = base_rate + (strength_factor - 0.5) * selectivity * 0.5

        # Clamp to reasonable bounds (0.1% to 99%)
        return max(0.1, min(adjusted_probability * 100, 99.0))

    def get_component_weights(self) -> Dict[str, float]:
        """Get current component weight configuration."""
        return self.component_weights.copy()
