# Configuration Examples

This file provides example configurations for different use cases.

## Example 1: Default Configuration

The most straightforward approach - use all default settings:

```python
from matching_engine import MatchingEngine, create_default_matching_engine_config

config = create_default_matching_engine_config()
engine = MatchingEngine(llm_client, config)
```

**Default Weights:**
- GPA Fit: 0.25
- Test Score Alignment: 0.20
- Major Ranking: 0.25
- Budget Alignment: 0.15
- Location Fit: 0.10
- Student Preferences: 0.05

**Ranking Weights:**
- Suitability: 50%
- Acceptance Probability: 30%
- QS Ranking: 20%

---

## Example 2: STEM Focus Configuration

For students pursuing Science, Technology, Engineering, Mathematics with emphasis on program quality:

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    create_default_prompt_config,
)

stem_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.35,  # Highest priority
        importance=1.0,
        description="How highly ranked is the student's STEM major?",
    ),
    CriterionConfig(
        name="Test Score Alignment",
        criterion_type=CriterionType.TEST_SCORES,
        weight=0.25,
        importance=1.0,
        description="Strong test scores are critical for STEM programs",
    ),
    CriterionConfig(
        name="GPA Fit",
        criterion_type=CriterionType.GPA,
        weight=0.20,
        importance=1.0,
    ),
    CriterionConfig(
        name="Budget Alignment",
        criterion_type=CriterionType.BUDGET,
        weight=0.15,
        importance=0.8,
    ),
    CriterionConfig(
        name="Location Fit",
        criterion_type=CriterionType.LOCATION,
        weight=0.05,
        importance=0.5,  # Less important for STEM students
    ),
])

stem_ranking = RankingWeightsConfig(
    suitability_weight=0.6,   # Emphasize fit
    acceptance_weight=0.2,
    qs_weight=0.2,
)

stem_config = MatchingEngineConfig(
    criteria_weights=stem_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=stem_ranking,
)

engine = MatchingEngine(llm_client, stem_config)
```

---

## Example 3: International Student Configuration

For international students with different priorities:

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    create_default_prompt_config,
)

international_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Budget Alignment",
        criterion_type=CriterionType.BUDGET,
        weight=0.30,  # Critical for international students
        importance=1.0,
        description="Does the university offer sufficient financial aid for international students?",
    ),
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.25,
        importance=1.0,
    ),
    CriterionConfig(
        name="GPA Fit",
        criterion_type=CriterionType.GPA,
        weight=0.20,
        importance=1.0,
    ),
    CriterionConfig(
        name="Test Score Alignment",
        criterion_type=CriterionType.TEST_SCORES,
        weight=0.15,
        importance=1.0,
    ),
    CriterionConfig(
        name="Location Fit",
        criterion_type=CriterionType.LOCATION,
        weight=0.10,
        importance=1.0,  # Important for international students
        description="Does the location have a welcoming international student community?",
    ),
])

international_ranking = RankingWeightsConfig(
    suitability_weight=0.5,
    acceptance_weight=0.25,  # Slightly lower
    qs_weight=0.25,          # Higher emphasis on prestige
)

international_config = MatchingEngineConfig(
    criteria_weights=international_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=international_ranking,
)

engine = MatchingEngine(llm_client, international_config)
```

---

## Example 4: Acceptance-Focused Configuration

When a student wants to maximize their chances of getting into a good university:

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    create_default_prompt_config,
)

acceptance_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="GPA Fit",
        criterion_type=CriterionType.GPA,
        weight=0.35,
        importance=1.0,
        description="GPA is a key determinant of admission success",
    ),
    CriterionConfig(
        name="Test Score Alignment",
        criterion_type=CriterionType.TEST_SCORES,
        weight=0.35,
        importance=1.0,
        description="Test scores significantly impact acceptance probability",
    ),
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.15,
        importance=0.8,
    ),
    CriterionConfig(
        name="Budget Alignment",
        criterion_type=CriterionType.BUDGET,
        weight=0.10,
        importance=0.7,
    ),
    CriterionConfig(
        name="Location Fit",
        criterion_type=CriterionType.LOCATION,
        weight=0.05,
        importance=0.5,
    ),
])

acceptance_ranking = RankingWeightsConfig(
    suitability_weight=0.3,
    acceptance_weight=0.5,   # Heavily weight acceptance probability
    qs_weight=0.2,
)

acceptance_config = MatchingEngineConfig(
    criteria_weights=acceptance_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=acceptance_ranking,
)

engine = MatchingEngine(llm_client, acceptance_config)
```

---

## Example 5: Prestige-Focused Configuration

When a student prioritizes university ranking and prestige:

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    create_default_prompt_config,
)

prestige_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.30,
        importance=1.0,
        description="Program reputation and national ranking",
    ),
    CriterionConfig(
        name="GPA Fit",
        criterion_type=CriterionType.GPA,
        weight=0.25,
        importance=1.0,
    ),
    CriterionConfig(
        name="Test Score Alignment",
        criterion_type=CriterionType.TEST_SCORES,
        weight=0.20,
        importance=1.0,
    ),
    CriterionConfig(
        name="Budget Alignment",
        criterion_type=CriterionType.BUDGET,
        weight=0.15,
        importance=0.9,
    ),
    CriterionConfig(
        name="Location Fit",
        criterion_type=CriterionType.LOCATION,
        weight=0.10,
        importance=0.6,
    ),
])

prestige_ranking = RankingWeightsConfig(
    suitability_weight=0.4,
    acceptance_weight=0.2,
    qs_weight=0.4,           # Heavy weight on QS ranking
)

prestige_config = MatchingEngineConfig(
    criteria_weights=prestige_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=prestige_ranking,
)

engine = MatchingEngine(llm_client, prestige_config)
```

---

## Example 6: Budget-Conscious Configuration

For families with strict budget constraints:

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    create_default_prompt_config,
)

budget_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Budget Alignment",
        criterion_type=CriterionType.BUDGET,
        weight=0.40,  # Primary concern
        importance=1.0,
        description="Cost must fit within family budget",
    ),
    CriterionConfig(
        name="GPA Fit",
        criterion_type=CriterionType.GPA,
        weight=0.25,
        importance=1.0,
    ),
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.20,
        importance=0.9,
    ),
    CriterionConfig(
        name="Test Score Alignment",
        criterion_type=CriterionType.TEST_SCORES,
        weight=0.10,
        importance=0.8,
    ),
    CriterionConfig(
        name="Location Fit",
        criterion_type=CriterionType.LOCATION,
        weight=0.05,
        importance=0.7,
    ),
])

budget_ranking = RankingWeightsConfig(
    suitability_weight=0.5,
    acceptance_weight=0.3,
    qs_weight=0.2,
)

budget_config = MatchingEngineConfig(
    criteria_weights=budget_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=budget_ranking,
)

engine = MatchingEngine(llm_client, budget_config)
```

---

## Example 7: Location-First Configuration

For students with strong location preferences (e.g., staying in home region):

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
    create_default_prompt_config,
)

location_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Location Fit",
        criterion_type=CriterionType.LOCATION,
        weight=0.30,  # Significantly increased
        importance=1.0,
        description="Location must match student and family preferences",
    ),
    CriterionConfig(
        name="GPA Fit",
        criterion_type=CriterionType.GPA,
        weight=0.25,
        importance=1.0,
    ),
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.25,
        importance=1.0,
    ),
    CriterionConfig(
        name="Budget Alignment",
        criterion_type=CriterionType.BUDGET,
        weight=0.15,
        importance=0.9,
    ),
    CriterionConfig(
        name="Test Score Alignment",
        criterion_type=CriterionType.TEST_SCORES,
        weight=0.05,
        importance=0.8,
    ),
])

location_ranking = RankingWeightsConfig(
    suitability_weight=0.6,   # Higher suitability weight
    acceptance_weight=0.2,
    qs_weight=0.2,
)

location_config = MatchingEngineConfig(
    criteria_weights=location_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=location_ranking,
)

engine = MatchingEngine(llm_client, location_config)
```

---

## Example 8: Custom LLM Prompts

Customize prompts for specific evaluation criteria:

```python
from matching_engine import (
    MatchingEngineConfig,
    LLMPromptConfig,
    EvaluationCriterionPrompt,
    create_default_criteria_config,
    create_default_ranking_weights,
)

custom_prompt_config = LLMPromptConfig(
    system_instruction="You are an expert in American university admissions with 20 years of experience.",
    criterion_prompts={
        "GPA Fit": EvaluationCriterionPrompt(
            criterion_name="GPA Fit",
            system_prompt="You are an expert admissions counselor...",
            evaluation_prompt="""Evaluate GPA fit for this student and university.

Consider:
- Upward/downward trend in grades
- Course rigor (AP, honors, IB courses)
- Unweighted vs weighted GPA
- High school GPA scale

Student GPA: {student_gpa}
University Average: {university_avg_gpa}
GPA Scale: {gpa_scale}

Provide score 0-10.""",
            scoring_guidelines="""
- 9-10: Student significantly exceeds university average
- 7-8: Student meets or slightly exceeds average
- 5-6: Student aligns with average
- 3-4: Student below average
- 0-2: Student significantly below average
""",
        ),
        "Major Ranking": EvaluationCriterionPrompt(
            criterion_name="Major Ranking",
            system_prompt="You are an expert in university program rankings...",
            evaluation_prompt="""Evaluate how well the university's program matches the student's major interest.

Student's Major: {preferred_major}
Program Rank: {program_ranking}
Program Notes: {program_notes}

Provide score 0-10 based on program quality and fit.""",
            scoring_guidelines="""
- 9-10: Top 5 nationally, excellent fit
- 7-8: Top 20 nationally, good fit
- 5-6: Top 50 nationally, adequate fit
- 3-4: Top 100 nationally, acceptable
- 0-2: Not ranked or weak program
""",
        ),
    },
)

custom_config = MatchingEngineConfig(
    criteria_weights=create_default_criteria_config(),
    prompt_config=custom_prompt_config,
    ranking_weights=create_default_ranking_weights(),
)

engine = MatchingEngine(llm_client, custom_config)
```

---

## Configuration Templates by Goal

| Goal | Primary Weight | Secondary | Tertiary | Config Example |
|------|---|---|---|---|
| Get into *any* good school | Acceptance 50% | Suitability 35% | QS 15% | Acceptance-Focused |
| Best program for major | Suitability 60% | QS 25% | Acceptance 15% | STEM Focus |
| Prestige matters most | QS 40% | Suitability 40% | Acceptance 20% | Prestige-Focused |
| Budget is primary concern | Suitability 50% | Acceptance 30% | QS 20% | Budget-Conscious |
| Must stay in region | Suitability 65% | Acceptance 25% | QS 10% | Location-First |

---

## Saving and Loading Configurations

```python
import json

# Save configuration
config_dict = engine.config.to_dict()
with open("my_config.json", "w") as f:
    json.dump(config_dict, f, indent=2)

# Load configuration
from matching_engine import MatchingEngineConfig
with open("my_config.json", "r") as f:
    loaded_config = MatchingEngineConfig.from_dict(json.load(f))

engine = MatchingEngine(llm_client, loaded_config)
```

---

## Dynamic Configuration Adjustments

```python
# Start with one config, adjust on the fly
engine = MatchingEngine(llm_client, create_default_matching_engine_config())

# Adjust ranking weights
engine.update_ranking_weights(
    suitability=0.4,
    acceptance=0.4,
    qs=0.2,
)

# Adjust criterion weights
engine.update_criteria_weights({
    "GPA Fit": 0.30,
    "Major Ranking": 0.35,
    "Budget Alignment": 0.20,
    "Test Score Alignment": 0.10,
    "Location Fit": 0.05,
})

# Disable certain criteria
engine.enable_criterion("Location Fit", False)
```

