from dataclasses import dataclass
from typing import Dict, List, Optional
import json

from ..dto.config import (
    CriteriaWeightsConfig,
    LLMPromptConfig,
    CriterionConfig,
)


@dataclass
class SuitabilityScore:
    criterion_name: str
    score: float
    reasoning: str
    weight: float
    importance: float


class SuitabilityCalculator:
    """
    Calculate university suitability scores for students using LLM evaluation.
    Uses configuration-based approach for criteria, weights, and prompts.
    """

    def __init__(
        self,
        llm_client,
        criteria_config: CriteriaWeightsConfig,
        prompt_config: Optional[LLMPromptConfig] = None,
    ):
        """
        Initialize the suitability calculator.

        Args:
            llm_client: LLM client for evaluation (must have evaluate(prompt) method)
            criteria_config: Configuration for criteria and their weights
            prompt_config: Configuration for LLM prompts
        """
        self.llm_client = llm_client
        self.criteria_config = criteria_config
        self.prompt_config = prompt_config

        # Validate weights on initialization
        self.criteria_config.validate_weights()

    def calculate_suitability(
        self, student_profile: Dict, university_data: Dict
    ) -> tuple[float, List[SuitabilityScore]]:
        """
        Calculate suitability score for a student-university pair.

        Args:
            student_profile: Student profile dictionary or StudentProfile object converted to dict
            university_data: University data dictionary

        Returns:
            Tuple of (overall_score: float, detailed_scores: List[SuitabilityScore])
            overall_score is on a 0-10 scale
        """
        detailed_scores = []
        weighted_sum = 0.0

        # Only evaluate enabled criteria
        enabled_criteria = [c for c in self.criteria_config.criteria if c.enabled]

        for criterion in enabled_criteria:
            score_obj = self._evaluate_criterion(
                criterion, student_profile, university_data
            )
            detailed_scores.append(score_obj)

            # Apply weight and importance multiplier
            weighted_contribution = (
                score_obj.score * criterion.weight * criterion.importance
            )
            weighted_sum += weighted_contribution

        overall_score = min(weighted_sum, 10.0)
        return overall_score, detailed_scores

    def _evaluate_criterion(
        self,
        criterion: CriterionConfig,
        student: Dict,
        university: Dict,
    ) -> SuitabilityScore:
        """
        Use LLM to evaluate a single criterion.

        Args:
            criterion: The criterion configuration to evaluate
            student: Student profile data
            university: University data

        Returns:
            SuitabilityScore object with score and reasoning
        """
        prompt = self._build_evaluation_prompt(criterion, student, university)

        # Call LLM for evaluation
        response = self.llm_client.evaluate(prompt)
        score, reasoning = self._parse_llm_response(response)

        return SuitabilityScore(
            criterion_name=criterion.name,
            score=score,
            reasoning=reasoning,
            weight=criterion.weight,
            importance=criterion.importance,
        )

    def _build_evaluation_prompt(
        self,
        criterion: CriterionConfig,
        student: Dict,
        university: Dict,
    ) -> str:
        """
        Build LLM prompt for criterion evaluation using config templates.

        If prompt_config exists and has a specific template for this criterion,
        use that. Otherwise, use the default template with criterion information.

        Args:
            criterion: The criterion to evaluate
            student: Student profile data
            university: University data

        Returns:
            Formatted prompt string for LLM
        """
        # Try to get criterion-specific prompt from config
        if self.prompt_config:
            criterion_prompt = self.prompt_config.get_criterion_prompt(criterion.name)
            if criterion_prompt:
                return self._format_criterion_prompt(
                    criterion_prompt, student, university
                )

        # Fall back to generic prompt
        prompt = f"""
Evaluate the fit between a student and university for the criterion: {criterion.name}

Criterion Description: {criterion.description}

Student Profile:
{json.dumps(student, indent=2)}

University Data:
{json.dumps(university, indent=2)}

Task: Evaluate how well this student matches this university on the '{criterion.name}' criterion.
Consider the criterion description and provide an objective assessment.

Provide:
1. A score from 0-10 (where 10 is excellent fit, 0 is poor fit)
2. Brief reasoning (2-3 sentences explaining the score)

Format your response exactly as:
SCORE: [number]
REASONING: [explanation]
"""
        return prompt

    def _format_criterion_prompt(
        self, criterion_prompt, student: Dict, university: Dict
    ) -> str:
        """Format a specific criterion prompt template with actual data."""
        # Extract relevant fields from student and university
        prompt_text = criterion_prompt.evaluation_prompt

        # Build formatting dict with common fields
        format_dict = {
            "criterion_name": criterion_prompt.criterion_name,
            "student_summary": json.dumps(student, indent=2),
            "university_summary": json.dumps(university, indent=2),
        }

        # Add criterion-specific fields
        if "gpa" in criterion_prompt.criterion_name.lower():
            format_dict.update({
                "student_gpa": student.get("academic", {}).get("gpa", "N/A"),
                "university_avg_gpa": university.get("avg_admitted_gpa", "N/A"),
                "gpa_scale": student.get("academic", {}).get("gpa_scale", 4.0),
            })

        if "major" in criterion_prompt.criterion_name.lower():
            preferred_majors = student.get("preferences", {}).get("preferred_majors", [])
            preferred_major = preferred_majors[0] if preferred_majors else student.get("intended_major", "Not specified")
            format_dict.update({
                "preferred_major": preferred_major,
                "program_ranking": university.get("program_ranking", "N/A"),
                "program_notes": university.get("program_notes", ""),
            })

        if "budget" in criterion_prompt.criterion_name.lower():
            format_dict.update({
                "student_budget": (
                    student.get("financial", {}).get("budget_per_year", "Not specified")
                ),
                "university_cost": university.get("cost_of_attendance", "N/A"),
                "financial_aid_percent": university.get(
                    "financial_aid_percentage", 0
                ),
                "merit_scholarship_likelihood": university.get(
                    "merit_scholarship_likelihood", "Unknown"
                ),
            })

        # Format the prompt with available fields
        try:
            formatted = prompt_text.format(**format_dict)
        except KeyError:
            # If formatting fails, return as is
            formatted = prompt_text

        # Add system context and scoring guidelines
        final_prompt = f"""{criterion_prompt.system_prompt}

{formatted}

Scoring Guidelines:
{criterion_prompt.scoring_guidelines}

Response Format:
{criterion_prompt.response_format}
"""
        return final_prompt

    def _parse_llm_response(self, response: str) -> tuple[float, str]:
        """
        Parse LLM response to extract score and reasoning.

        Args:
            response: Raw response from LLM

        Returns:
            Tuple of (score: float, reasoning: str)
        """
        lines = response.strip().split("\n")
        score = 5.0
        reasoning = ""

        for line in lines:
            if line.startswith("SCORE:"):
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    score = float(score_str)
                    score = max(0.0, min(10.0, score))
                except ValueError:
                    pass
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()

        return score, reasoning
