# Matching Engine Documentation

## Overview

The Matching Engine is a comprehensive system for matching students with suitable American universities. It combines:

1. **Student Profile Model** - Comprehensive representation of student data
2. **Suitability Calculator** - LLM-based evaluation of student-university fit
3. **Acceptance Calculator** - Data-driven estimation of acceptance probability
4. **Ranking Engine** - Combines all factors for final ranking
5. **Configuration System** - Flexible, configurable criteria and weights

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MatchingEngine                            │
│                  (Main Entry Point)                          │
└────────┬────────────────────────────────────────────────┬───┘
         │                                                │
    ┌────▼──────────────┐                      ┌────────▼──────┐
    │ StudentProfile    │                      │ Configuration │
    │                   │                      │                │
    │ • Academic        │                      │ • Criteria     │
    │ • Extracurricular │                      │ • Weights      │
    │ • Essay           │                      │ • Prompts      │
    │ • Preferences     │                      │                │
    │ • Financial       │                      └────────────────┘
    └───────────────────┘

         ┌──────────────────────────────────────────┐
         │         Calculation Pipeline             │
         ├──────────────────────────────────────────┤
         │  For each of 20 universities:            │
         │  1. SuitabilityCalculator                │
         │     └─ LLM evaluates criteria            │
         │  2. AcceptanceCalculator                 │
         │     └─ Estimates acceptance prob.        │
         │  3. RankingEngine                        │
         │     └─ Combines all factors              │
         └──────────────────────────────────────────┘

         ┌──────────────────────────────────────────┐
         │         Output: Top 10 Universities      │
         └──────────────────────────────────────────┘
```

## Components

### 1. StudentProfile (`student_profile.py`)

Comprehensive dataclass representing a student with multiple nested profiles:

```python
from matching_engine import StudentProfile, AcademicProfile, TestScore, TestType

student = StudentProfile(
    name="Jane Doe",
    email="jane@example.com",
    academic=AcademicProfile(
        gpa=3.85,
        test_scores=[
            TestScore(test_type=TestType.SAT, score=1520),
        ]
    ),
    preferences=PreferencesProfile(
        preferred_majors=["Computer Science", "Engineering"],
        preferred_locations=["California", "Massachusetts"],
    ),
    financial=FinancialProfile(
        budget_per_year=60000,
        needs_financial_aid=True,
    )
)
```

**Key Features:**
- Multiple sub-profiles: Academic, Essay, Extracurricular, Preferences, Financial
- Easy conversion to dictionary for LLM processing: `student.to_dict()`
- Type-safe with enums (ResidencyStatus, TestType)
- Support for detailed academic records (AP, IB scores)

### 2. Configuration System (`config.py`)

Highly flexible configuration management:

#### CriteriaWeightsConfig
Define evaluation criteria with individual weights and importance scores:

```python
from matching_engine import CriteriaWeightsConfig, CriterionConfig, CriterionType

criteria_config = CriteriaWeightsConfig(
    criteria=[
        CriterionConfig(
            name="GPA Fit",
            criterion_type=CriterionType.GPA,
            weight=0.25,           # Must sum to 1.0 with other weights
            importance=1.0,        # Multiplier for this criterion
            description="How well does the student's GPA align with the university?"
        ),
        # ... more criteria
    ]
)
```

#### LLMPromptConfig
Customize LLM prompts for each criterion:

```python
from matching_engine import LLMPromptConfig, EvaluationCriterionPrompt

prompt_config = LLMPromptConfig(
    system_instruction="You are an expert admissions counselor...",
    criterion_prompts={
        "GPA Fit": EvaluationCriterionPrompt(
            criterion_name="GPA Fit",
            system_prompt="...",
            evaluation_prompt="...",
            scoring_guidelines="...",
            response_format="SCORE: [0-10]\nREASONING: [explanation]"
        ),
        # ... more criteria
    }
)
```

#### RankingWeightsConfig
Configure how to combine suitability, acceptance, and QS ranking:

```python
from matching_engine import RankingWeightsConfig

ranking_config = RankingWeightsConfig(
    suitability_weight=0.5,    # 50%
    acceptance_weight=0.3,     # 30%
    qs_weight=0.2,             # 20%
)
```

#### Complete Configuration
Combine all sub-configurations:

```python
from matching_engine import MatchingEngineConfig

config = MatchingEngineConfig(
    criteria_weights=criteria_config,
    prompt_config=prompt_config,
    ranking_weights=ranking_config,
)

# Or use defaults
from matching_engine import create_default_matching_engine_config
config = create_default_matching_engine_config()
```

### 3. SuitabilityCalculator (`suitability_calculator.py`)

Evaluates student-university fit using LLM and configurable criteria:

```python
from matching_engine import SuitabilityCalculator

calculator = SuitabilityCalculator(
    llm_client=your_llm_client,
    criteria_config=criteria_config,
    prompt_config=prompt_config,
)

score, detailed_scores = calculator.calculate_suitability(
    student_profile=student.to_dict(),
    university_data={
        "name": "MIT",
        "avg_admitted_gpa": 3.97,
        "avg_test_score": 1550,
        # ...
    }
)

# score: float (0-10)
# detailed_scores: List[SuitabilityScore]
#   - criterion_name: str
#   - score: float (0-10)
#   - reasoning: str
#   - weight: float
#   - importance: float
```

**Features:**
- Criterion-specific LLM prompts if configured
- Falls back to generic prompt if specific one not found
- Proper weight and importance multipliers
- Detailed reasoning for each criterion

### 4. AcceptanceCalculator (`acceptance_calculator.py`)

Data-driven estimation of acceptance probability:

```python
from matching_engine import AcceptanceCalculator

calculator = AcceptanceCalculator(
    base_acceptance_rate=0.25,  # Default if not in university data
    component_weights={
        "gpa": 0.35,
        "test": 0.35,
        "essay": 0.20,
        "extracurricular": 0.10,
    }
)

acceptance_prob, app_scores = calculator.calculate_acceptance_probability(
    student_profile=student.to_dict(),
    university_data={"acceptance_rate": 0.03, ...}
)

# acceptance_prob: float (0-100)
# app_scores: ApplicationScores
#   - gpa_score: float (0-100)
#   - test_score: float (0-100)
#   - essay_score: float (0-100)
#   - extracurricular_score: float (0-100)
#   - overall_strength: float (0-100)
```

**Algorithm:**
- Scores each component as percentile of university's admitted students
- Uses logistic model: `base_rate + (strength_factor - 0.5) * selectivity * 0.5`
- More selective universities penalize weak applications more

### 5. RankingEngine (`ranking_engine.py`)

Combines all factors into final ranking:

```python
from matching_engine import RankingEngine

engine = RankingEngine(ranking_config=ranking_config)

rankings = engine.rank_universities(
    universities=top_20_universities,
    suitability_scores={"MIT": 8.5, "Stanford": 8.2, ...},
    acceptance_probabilities={"MIT": 5.2, "Stanford": 7.1, ...}
)

# Returns top 10 UniversityRanking objects:
# - name: str
# - qs_rank: int
# - suitability_score: float (0-10)
# - acceptance_probability: float (0-100)
# - combined_score: float (0-100)
# - details: Dict (breakdown by factor)
```

**Scoring Formula:**
```
combined_score = (
    qs_weight * qs_score +
    suitability_weight * (suitability * 10) +
    acceptance_weight * acceptance_prob
)
```

### 6. MatchingEngine (`matching_engine.py`)

Main orchestrator combining all components:

```python
from matching_engine import MatchingEngine

engine = MatchingEngine(
    llm_client=your_llm_client,
    config=matching_config  # Optional, uses default if not provided
)

result = engine.match(
    student=student_profile,
    top_20_universities=universities
)

# Returns MatchResult:
# - student_name: str
# - top_10_universities: List[UniversityRanking]
# - detailed_analysis: Dict
```

## Usage Examples

### Basic Usage

```python
from matching_engine import MatchingEngine, StudentProfile, create_default_matching_engine_config

# Create LLM client (example with OpenAI)
from openai import OpenAI
llm_client = OpenAI(api_key="your-key")

# Create engine with default config
engine = MatchingEngine(llm_client)

# Create student
student = StudentProfile(name="John Doe", email="john@example.com", ...)

# Match to universities
result = engine.match(student, top_20_universities)

# View results
for ranking in result.top_10_universities:
    print(f"{ranking.name}: {ranking.combined_score:.2f}")
```

### Custom Configuration

```python
from matching_engine import (
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
)

# Emphasize major ranking for STEM student
custom_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.40,  # Increased
        importance=1.0,
    ),
    # ... other criteria
])

custom_config = MatchingEngineConfig(
    criteria_weights=custom_criteria,
    prompt_config=default_config.prompt_config,
    ranking_weights=RankingWeightsConfig(
        suitability_weight=0.6,
        acceptance_weight=0.2,
        qs_weight=0.2,
    ),
)

engine = MatchingEngine(llm_client, custom_config)
```

### Dynamic Configuration

```python
# Adjust weights dynamically
engine.update_ranking_weights(
    suitability=0.4,
    acceptance=0.4,
    qs=0.2,
)

# Enable/disable criteria
engine.enable_criterion("Location Fit", False)

# Update criterion weights
engine.update_criteria_weights({
    "GPA Fit": 0.30,
    "Major Ranking": 0.35,
})
```

## LLM Integration

### Prompt Structure

The system uses a hierarchical prompt structure:

1. **System Instruction** - Context and role
2. **Criterion-specific Prompt** - Detailed evaluation instruction
3. **Scoring Guidelines** - How to score on 0-10 scale
4. **Response Format** - Expected output format

### LLM Client Requirements

Your LLM client must implement:

```python
class YourLLMClient:
    def evaluate(self, prompt: str) -> str:
        """
        Evaluate a prompt and return response.
        
        Args:
            prompt: Full prompt with system instruction, task, and format
            
        Returns:
            Response in format: "SCORE: [0-10]\nREASONING: [text]"
        """
        # Call your LLM API
        response = your_llm_api.call(prompt)
        return response
```

### Example with OpenAI

```python
from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def evaluate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistency
        )
        return response.choices[0].message.content

llm_client = OpenAIClient(api_key="your-key")
engine = MatchingEngine(llm_client)
```

## Configuration File Format

Save/load configurations as JSON:

```python
# Save
config_json = engine.config.to_json()
with open("matching_config.json", "w") as f:
    f.write(config_json)

# Load
with open("matching_config.json", "r") as f:
    from matching_engine import MatchingEngineConfig
    config = MatchingEngineConfig.from_json(f.read())
```

## Performance Considerations

1. **LLM Calls**: Each university requires LLM evaluations for each enabled criterion
   - 20 universities × 5 criteria ≈ 100 LLM calls
   - Consider batch processing or caching for repeated students

2. **Weights Validation**: Automatically validates on initialization
   - Prevents invalid configurations early
   - Clear error messages

3. **Memory**: Student profiles and results stored in memory
   - For large batches, consider streaming or database integration

## Error Handling

```python
from matching_engine import CriteriaWeightsConfig

try:
    config = CriteriaWeightsConfig(criteria=[...])
    config.validate_weights()  # Raises ValueError if weights don't sum to 1.0
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Extending the System

### Adding New Criteria

```python
from matching_engine import CriterionType

# 1. Add to CriterionType enum (if new category)
class CriterionType(Enum):
    # ... existing types
    SPECIAL_TALENTS = "special_talents"

# 2. Create criterion config
criterion = CriterionConfig(
    name="Special Talents",
    criterion_type=CriterionType.SPECIAL_TALENTS,
    weight=0.05,
    description="How well do the student's talents align with university resources?"
)

# 3. Add prompt template if needed
prompt = EvaluationCriterionPrompt(
    criterion_name="Special Talents",
    # ... prompt details
)
```

### Custom Acceptance Calculator Weights

```python
calculator = AcceptanceCalculator(
    base_acceptance_rate=0.20,
    component_weights={
        "gpa": 0.40,      # Increased
        "test": 0.30,     # Decreased
        "essay": 0.20,
        "extracurricular": 0.10,
    }
)
```

## Best Practices

1. **Validate Early**: Call `config.validate()` after creating configurations
2. **Use Defaults**: Start with `create_default_matching_engine_config()` and customize
3. **Document Weights**: Add descriptions to explain why criteria have specific weights
4. **Test LLM Prompts**: Validate prompt formatting before large-scale runs
5. **Cache Results**: Store suitability/acceptance scores to avoid redundant LLM calls
6. **Monitor Quality**: Review LLM outputs for consistency and accuracy
7. **Version Configs**: Keep version history of configuration changes

## Troubleshooting

**Issue**: "Weights must sum to 1.0"
- **Solution**: Check that all enabled criteria weights sum to exactly 1.0
- Use: `sum(c.weight for c in criteria if c.enabled)`

**Issue**: LLM not returning expected format
- **Solution**: Verify `response_format` in prompt config
- Ensure LLM returns "SCORE: X" and "REASONING: Y" format

**Issue**: Unexpected acceptance probabilities
- **Solution**: Check university data has `acceptance_rate` field
- Verify test scores are in correct scale (SAT 1600, ACT 36)

**Issue**: Strange ranking results
- **Solution**: Check `ranking_weights` sum to 1.0
- Verify suitability scores are on 0-10 scale
- Verify acceptance probabilities are on 0-100 scale

