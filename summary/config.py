from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json


class CriterionType(Enum):
    GPA = "gpa"
    BUDGET = "budget"
    MAJOR_RANKING = "major_ranking"
    LOCATION = "location"
    PREFERENCES = "preferences"
    TEST_SCORES = "test_scores"
    EXTRACURRICULAR = "extracurricular"
    ESSAY = "essay"


@dataclass
class CriterionConfig:
    """Configuration for a single criterion."""

    name: str
    criterion_type: CriterionType
    weight: float
    importance: float = 1.0
    description: str = ""
    enabled: bool = True


@dataclass
class CriteriaWeightsConfig:
    """Configuration for all criteria and their weights."""

    criteria: List[CriterionConfig] = field(default_factory=list)

    def validate_weights(self) -> bool:
        """Validate that weights sum to 1.0."""
        enabled_criteria = [c for c in self.criteria if c.enabled]
        total_weight = sum(c.weight for c in enabled_criteria)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(
                f"Enabled criteria weights must sum to 1.0, got {total_weight}"
            )
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "criteria": [
                {
                    "name": c.name,
                    "criterion_type": c.criterion_type.value,
                    "weight": c.weight,
                    "importance": c.importance,
                    "description": c.description,
                    "enabled": c.enabled,
                }
                for c in self.criteria
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CriteriaWeightsConfig":
        """Create from dictionary."""
        criteria = [
            CriterionConfig(
                name=c["name"],
                criterion_type=CriterionType[c["criterion_type"].upper()],
                weight=c["weight"],
                importance=c.get("importance", 1.0),
                description=c.get("description", ""),
                enabled=c.get("enabled", True),
            )
            for c in data.get("criteria", [])
        ]
        return cls(criteria=criteria)


@dataclass
class EvaluationCriterionPrompt:
    """Template for evaluating a single criterion via LLM."""

    criterion_name: str
    system_prompt: str
    evaluation_prompt: str
    scoring_guidelines: str
    response_format: str = "SCORE: [0-10]\nREASONING: [explanation]"


@dataclass
class LLMPromptConfig:
    """Configuration for LLM prompts used in suitability evaluation."""

    system_instruction: str
    criterion_prompts: Dict[str, EvaluationCriterionPrompt] = field(
        default_factory=dict
    )
    default_criterion_prompt: Optional[EvaluationCriterionPrompt] = None

    def get_criterion_prompt(
        self, criterion_name: str
    ) -> Optional[EvaluationCriterionPrompt]:
        """Get prompt template for a criterion."""
        return self.criterion_prompts.get(
            criterion_name, self.default_criterion_prompt
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "system_instruction": self.system_instruction,
            "criterion_prompts": {
                name: {
                    "criterion_name": prompt.criterion_name,
                    "system_prompt": prompt.system_prompt,
                    "evaluation_prompt": prompt.evaluation_prompt,
                    "scoring_guidelines": prompt.scoring_guidelines,
                    "response_format": prompt.response_format,
                }
                for name, prompt in self.criterion_prompts.items()
            },
            "default_criterion_prompt": {
                "criterion_name": self.default_criterion_prompt.criterion_name,
                "system_prompt": self.default_criterion_prompt.system_prompt,
                "evaluation_prompt": self.default_criterion_prompt.evaluation_prompt,
                "scoring_guidelines": self.default_criterion_prompt.scoring_guidelines,
                "response_format": self.default_criterion_prompt.response_format,
            }
            if self.default_criterion_prompt
            else None,
        }


@dataclass
class RankingWeightsConfig:
    """Configuration for ranking weights."""

    suitability_weight: float = 0.5
    acceptance_weight: float = 0.3
    qs_weight: float = 0.2

    def validate_weights(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = self.suitability_weight + self.acceptance_weight + self.qs_weight
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"Ranking weights must sum to 1.0, got {total}"
            )
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "suitability_weight": self.suitability_weight,
            "acceptance_weight": self.acceptance_weight,
            "qs_weight": self.qs_weight,
        }


@dataclass
class MatchingEngineConfig:
    """Complete configuration for the matching engine."""

    criteria_weights: CriteriaWeightsConfig
    prompt_config: LLMPromptConfig
    ranking_weights: RankingWeightsConfig

    def validate(self) -> bool:
        """Validate all configurations."""
        self.criteria_weights.validate_weights()
        self.ranking_weights.validate_weights()
        return True

    def to_dict(self) -> Dict:
        """Convert entire config to dictionary."""
        return {
            "criteria_weights": self.criteria_weights.to_dict(),
            "prompt_config": self.prompt_config.to_dict(),
            "ranking_weights": self.ranking_weights.to_dict(),
        }

    def to_json(self) -> str:
        """Convert entire config to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> "MatchingEngineConfig":
        """Create config from dictionary."""
        criteria_weights = CriteriaWeightsConfig.from_dict(
            data.get("criteria_weights", {})
        )
        ranking_weights = RankingWeightsConfig(
            **data.get("ranking_weights", {})
        )
        prompt_config = LLMPromptConfig(
            system_instruction=data.get("prompt_config", {}).get(
                "system_instruction", ""
            )
        )
        return cls(
            criteria_weights=criteria_weights,
            prompt_config=prompt_config,
            ranking_weights=ranking_weights,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MatchingEngineConfig":
        """Create config from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


def create_default_criteria_config() -> CriteriaWeightsConfig:
    """Create a default criteria configuration."""
    return CriteriaWeightsConfig(
        criteria=[
            CriterionConfig(
                name="GPA Fit",
                criterion_type=CriterionType.GPA,
                weight=0.25,
                importance=1.0,
                description="How well does the student's GPA align with the university's admitted student profile?",
            ),
            CriterionConfig(
                name="Test Score Alignment",
                criterion_type=CriterionType.TEST_SCORES,
                weight=0.20,
                importance=1.0,
                description="How do the student's test scores compare to the university's average admitted student?",
            ),
            CriterionConfig(
                name="Major Ranking",
                criterion_type=CriterionType.MAJOR_RANKING,
                weight=0.25,
                importance=1.0,
                description="How highly ranked is the student's preferred major at this university?",
            ),
            CriterionConfig(
                name="Budget Alignment",
                criterion_type=CriterionType.BUDGET,
                weight=0.15,
                importance=0.9,
                description="Does the university's cost align with the student's budget?",
            ),
            CriterionConfig(
                name="Location Fit",
                criterion_type=CriterionType.LOCATION,
                weight=0.10,
                importance=0.7,
                description="Does the university's location match the student's preferences?",
            ),
            CriterionConfig(
                name="Student Preferences",
                criterion_type=CriterionType.PREFERENCES,
                weight=0.05,
                importance=0.8,
                description="How well does the university align with the student's stated preferences?",
            ),
        ]
    )


def create_default_prompt_config() -> LLMPromptConfig:
    """Create default LLM prompt configuration."""
    system_instruction = """You are an expert university admissions counselor with deep knowledge of American higher education institutions. 
Your task is to evaluate how well a student fits with specific universities based on various criteria.
Provide objective, data-driven assessments based on the student profile and university information provided.
Be concise but comprehensive in your reasoning."""

    gpa_prompt = EvaluationCriterionPrompt(
        criterion_name="GPA Fit",
        system_prompt=system_instruction,
        evaluation_prompt="""Evaluate the GPA fit between this student and university.

Consider:
1. The student's current GPA relative to the university's average admitted GPA
2. Trend in grades (improving vs. declining)
3. Course difficulty and rigor
4. GPA scale used by the student's school vs. 4.0 scale

Student GPA: {student_gpa}
University Average Admitted GPA: {university_avg_gpa}
Student's GPA Scale: {gpa_scale}

Provide a fit score from 0-10 where:
- 10: Student's GPA significantly exceeds university average
- 5: Student's GPA matches university average
- 0: Student's GPA is well below university average""",
        scoring_guidelines="""Score based on percentile comparison:
- 90-100th percentile: 9-10
- 75-90th percentile: 7-8
- 50-75th percentile: 5-6
- 25-50th percentile: 3-4
- Below 25th percentile: 0-2""",
    )

    major_ranking_prompt = EvaluationCriterionPrompt(
        criterion_name="Major Ranking",
        system_prompt=system_instruction,
        evaluation_prompt="""Evaluate how well the university's program ranks for the student's preferred major.

Consider:
1. National ranking of the program
2. Program reputation and recognition
3. Available resources and facilities
4. Faculty expertise in student's area of interest
5. Career outcomes for graduates

Student's Preferred Major: {preferred_major}
University Program Ranking: {program_ranking}
Program Notes: {program_notes}

Provide a fit score from 0-10 where:
- 10: Top-tier program, excellent fit for student's interests
- 5: Solid program, adequate for student's goals
- 0: Weak program, poor match for student's interests""",
        scoring_guidelines="""Score based on program quality:
- Top 10 nationally: 9-10
- Top 25 nationally: 7-8
- Top 50 nationally: 5-6
- Top 100 nationally: 3-4
- Not ranked/emerging: 0-2""",
    )

    budget_prompt = EvaluationCriterionPrompt(
        criterion_name="Budget Alignment",
        system_prompt=system_instruction,
        evaluation_prompt="""Evaluate the financial fit between the university and student's budget.

Consider:
1. Total cost of attendance (tuition + fees + room & board)
2. Student's stated budget and financial constraints
3. Financial aid availability and merit scholarship likelihood
4. Cost of attendance relative to similar institutions

Student's Budget: ${student_budget}
University Cost of Attendance: ${university_cost}
Financial Aid Available: {financial_aid_percent}%
Merit Scholarship Likelihood: {merit_scholarship_likelihood}

Provide a fit score from 0-10 where:
- 10: Cost is very affordable within student's budget
- 5: Cost requires some financial aid/scholarships
- 0: Cost is prohibitive for student's financial situation""",
        scoring_guidelines="""Score based on affordability:
- Cost < Student Budget: 8-10
- Cost within 10% of budget: 6-7
- Cost 10-25% above budget: 4-5
- Cost 25-50% above budget: 2-3
- Cost > 50% above budget: 0-1""",
    )

    default_prompt = EvaluationCriterionPrompt(
        criterion_name="Default Criterion",
        system_prompt=system_instruction,
        evaluation_prompt="""Evaluate how well the student fits this university for the criterion: {criterion_name}

Student Profile Summary:
{student_summary}

University Information:
{university_summary}

Based on this criterion, provide a fit score from 0-10 and brief reasoning.""",
        scoring_guidelines="""Use a 0-10 scale where:
- 9-10: Excellent fit
- 7-8: Good fit
- 5-6: Moderate fit
- 3-4: Weak fit
- 0-2: Poor fit""",
    )

    config = LLMPromptConfig(
        system_instruction=system_instruction,
        criterion_prompts={
            "GPA Fit": gpa_prompt,
            "Major Ranking": major_ranking_prompt,
            "Budget Alignment": budget_prompt,
        },
        default_criterion_prompt=default_prompt,
    )

    return config


def create_default_ranking_weights() -> RankingWeightsConfig:
    """Create default ranking weights configuration."""
    return RankingWeightsConfig(
        suitability_weight=0.5,
        acceptance_weight=0.3,
        qs_weight=0.2,
    )


def create_default_matching_engine_config() -> MatchingEngineConfig:
    """Create a complete default configuration for the matching engine."""
    return MatchingEngineConfig(
        criteria_weights=create_default_criteria_config(),
        prompt_config=create_default_prompt_config(),
        ranking_weights=create_default_ranking_weights(),
    )

