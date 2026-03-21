# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install dataclasses-json  # If needed for your Python version
```

### 2. Create Your First Matching Engine

```python
from matching_engine import (
    MatchingEngine,
    StudentProfile,
    AcademicProfile,
    TestScore,
    TestType,
    create_default_matching_engine_config,
)

# Step 1: Create an LLM client (example with mock)
class SimpleLLMClient:
    def evaluate(self, prompt: str) -> str:
        # In production, call your actual LLM API
        return "SCORE: 7.5\nREASONING: Good fit based on profile."

llm_client = SimpleLLMClient()

# Step 2: Initialize the matching engine
engine = MatchingEngine(llm_client)

# Step 3: Create a student profile
student = StudentProfile(
    name="Alice Johnson",
    email="alice@example.com",
    academic=AcademicProfile(
        gpa=3.9,
        test_scores=[TestScore(test_type=TestType.SAT, score=1520)],
    ),
)

# Step 4: Define universities to match
universities = [
    {
        "name": "MIT",
        "qs_rank": 1,
        "avg_admitted_gpa": 3.97,
        "avg_test_score": 1550,
        "acceptance_rate": 0.03,
    },
    {
        "name": "Stanford",
        "qs_rank": 3,
        "avg_admitted_gpa": 3.96,
        "avg_test_score": 1545,
        "acceptance_rate": 0.04,
    },
    # ... more universities
]

# Step 5: Run the matching
result = engine.match(student, universities)

# Step 6: View results
for rank, university in enumerate(result.top_10_universities, 1):
    print(f"{rank}. {university.name}")
    print(f"   Combined Score: {university.combined_score:.2f}")
```

## Key Classes

### StudentProfile

Complete student information:

```python
from matching_engine import (
    StudentProfile,
    AcademicProfile,
    TestScore,
    TestType,
    EssayProfile,
    PreferencesProfile,
    FinancialProfile,
    ExtracurricularActivity,
)

student = StudentProfile(
    # Basic info
    name="John Doe",
    email="john@example.com",
    
    # Academic
    academic=AcademicProfile(
        gpa=3.85,
        test_scores=[
            TestScore(test_type=TestType.SAT, score=1520),
            TestScore(test_type=TestType.ACT, score=34),
        ],
    ),
    
    # Activities
    extracurricular_activities=[
        ExtracurricularActivity(
            name="Robotics Club",
            category="STEM",
            role="Lead",
            years_involved=2,
        ),
    ],
    
    # Essay
    essay=EssayProfile(essay_score=90.0),
    
    # Preferences
    preferences=PreferencesProfile(
        preferred_majors=["Computer Science"],
        preferred_locations=["California"],
    ),
    
    # Financial
    financial=FinancialProfile(
        budget_per_year=50000,
        needs_financial_aid=True,
    ),
)
```

### Configuration

Use default or customize:

```python
from matching_engine import (
    MatchingEngine,
    create_default_matching_engine_config,
)

# Option 1: Use defaults
engine = MatchingEngine(llm_client)

# Option 2: Customize
from matching_engine import MatchingEngineConfig, CriteriaWeightsConfig, CriterionConfig, CriterionType

custom_criteria = CriteriaWeightsConfig(criteria=[
    CriterionConfig(
        name="Major Ranking",
        criterion_type=CriterionType.MAJOR_RANKING,
        weight=0.40,  # 40% weight
        importance=1.0,
    ),
    # ... more criteria
])

config = MatchingEngineConfig(
    criteria_weights=custom_criteria,
    prompt_config=create_default_prompt_config(),
    ranking_weights=create_default_ranking_weights(),
)

engine = MatchingEngine(llm_client, config)
```

### Dynamic Adjustments

Change settings after creating the engine:

```python
# Update ranking priorities
engine.update_ranking_weights(
    suitability=0.6,
    acceptance=0.2,
    qs=0.2,
)

# Update criterion weights
engine.update_criteria_weights({
    "GPA Fit": 0.30,
    "Major Ranking": 0.40,
})

# Enable/disable criteria
engine.enable_criterion("Location Fit", False)
```

## University Data Format

Each university dict should contain:

```python
university = {
    # Required
    "name": "MIT",
    "qs_rank": 1,
    
    # Academic stats
    "avg_admitted_gpa": 3.97,
    "avg_test_score": 1550,
    
    # Admissions
    "acceptance_rate": 0.03,  # 3%
    
    # Financial
    "cost_of_attendance": 80000,
    "financial_aid_percentage": 100,
    
    # Program info
    "program_ranking": {
        "Computer Science": 1,
        "Engineering": 1,
    },
}
```

## Results

The `match()` method returns a `MatchResult`:

```python
result = engine.match(student, universities)

# Access top 10 universities
for ranking in result.top_10_universities:
    print(f"Name: {ranking.name}")
    print(f"QS Rank: {ranking.qs_rank}")
    print(f"Suitability (0-10): {ranking.suitability_score}")
    print(f"Acceptance Prob (0-100): {ranking.acceptance_probability}")
    print(f"Combined Score (0-100): {ranking.combined_score}")
    
    # Score breakdown
    print(f"Details: {ranking.details}")

# Access detailed analysis
analysis = result.detailed_analysis
for uni in analysis["universities"]:
    print(f"{uni['name']}: {uni['combined_score']}")
    for criterion in uni["criterion_analysis"]:
        print(f"  {criterion['criterion']}: {criterion['score']}/10")
```

## Common Scenarios

### Scenario 1: STEM Student

```python
from matching_engine import (
    MatchingEngine,
    MatchingEngineConfig,
    CriteriaWeightsConfig,
    CriterionConfig,
    CriterionType,
    RankingWeightsConfig,
)

stem_config = MatchingEngineConfig(
    criteria_weights=CriteriaWeightsConfig(criteria=[
        CriterionConfig(
            name="Major Ranking",
            criterion_type=CriterionType.MAJOR_RANKING,
            weight=0.40,
            importance=1.0,
        ),
        CriterionConfig(
            name="Test Score Alignment",
            criterion_type=CriterionType.TEST_SCORES,
            weight=0.30,
            importance=1.0,
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
            weight=0.10,
            importance=0.9,
        ),
    ]),
    prompt_config=create_default_prompt_config(),
    ranking_weights=RankingWeightsConfig(
        suitability_weight=0.6,
        acceptance_weight=0.2,
        qs_weight=0.2,
    ),
)

engine = MatchingEngine(llm_client, stem_config)
```

### Scenario 2: Budget-Conscious Student

```python
# Create engine with budget emphasis
engine = MatchingEngine(llm_client)

engine.update_criteria_weights({
    "Budget Alignment": 0.40,
    "GPA Fit": 0.25,
    "Major Ranking": 0.20,
    "Test Score Alignment": 0.10,
    "Location Fit": 0.05,
})

# Run matching
result = engine.match(student, universities)
```

### Scenario 3: International Student

```python
from matching_engine import ResidencyStatus

# Create student with international status
student = StudentProfile(
    name="Carlos Rodriguez",
    email="carlos@example.com",
    residency_status=ResidencyStatus.INTERNATIONAL,
    country_of_origin="Mexico",
    academic=AcademicProfile(gpa=3.8),
)

# Use configuration that prioritizes financial aid
engine = MatchingEngine(llm_client)
engine.update_criteria_weights({
    "Budget Alignment": 0.35,
    "Location Fit": 0.20,
    "Major Ranking": 0.25,
    "GPA Fit": 0.15,
    "Test Score Alignment": 0.05,
})

result = engine.match(student, universities)
```

## Production LLM Integration

### OpenAI

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
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content

llm_client = OpenAIClient(api_key="sk-...")
engine = MatchingEngine(llm_client)
```

### Anthropic Claude

```python
import anthropic

class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def evaluate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

llm_client = ClaudeClient(api_key="sk-ant-...")
engine = MatchingEngine(llm_client)
```

### Google Gemini

```python
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")
    
    def evaluate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

llm_client = GeminiClient(api_key="AIzaSy...")
engine = MatchingEngine(llm_client)
```

## Troubleshooting

**Q: Getting "Weights must sum to 1.0" error**
```python
# Check your weights sum to 1.0
total = sum(c.weight for c in engine.config.criteria_weights.criteria)
print(f"Total weight: {total}")  # Should be 1.0
```

**Q: LLM responses not being parsed**
```python
# Ensure your LLM returns correct format
response = """SCORE: 7.5
REASONING: Good fit based on major and GPA."""
# Format must be exactly: SCORE: [number]\nREASONING: [text]
```

**Q: Results seem biased toward certain universities**
```python
# Check your ranking weights
print(engine.get_config()["ranking_weights"])
# Verify suitability_weight + acceptance_weight + qs_weight == 1.0
```

**Q: How do I cache LLM results?**
```python
from functools import lru_cache

class CachedLLMClient:
    def __init__(self, base_client):
        self.base_client = base_client
    
    @lru_cache(maxsize=1000)
    def evaluate(self, prompt: str) -> str:
        return self.base_client.evaluate(prompt)

llm_client = CachedLLMClient(OpenAIClient(...))
```

## Next Steps

1. Read [DOCUMENTATION.md](./DOCUMENTATION.md) for detailed API documentation
2. Check [CONFIGURATION_EXAMPLES.md](./CONFIGURATION_EXAMPLES.md) for different use cases
3. Run [example.py](./example.py) to see all features in action
4. Integrate with your hard filter component to get top 20 universities
5. Deploy with your chosen LLM provider

## File Structure

```
matching_engine/
├── __init__.py                    # Public API exports
├── student_profile.py             # StudentProfile class
├── config.py                      # Configuration classes
├── suitability_calculator.py      # LLM-based evaluation
├── acceptance_calculator.py       # Probability calculation
├── ranking_engine.py              # Final ranking
├── matching_engine.py             # Main orchestrator
├── example.py                     # Usage examples
├── DOCUMENTATION.md               # Full documentation
├── CONFIGURATION_EXAMPLES.md      # Configuration examples
└── QUICK_START.md                 # This file
```

## API Summary

### MatchingEngine

```python
engine = MatchingEngine(llm_client, config=None)
result = engine.match(student, universities)
engine.update_ranking_weights(suitability, acceptance, qs)
engine.update_criteria_weights(weights_dict)
engine.enable_criterion(name, enabled)
engine.get_config()
```

### StudentProfile

```python
student = StudentProfile(name, email, academic=..., preferences=..., ...)
student_dict = student.to_dict()
```

### Configuration

```python
config = create_default_matching_engine_config()
config = MatchingEngineConfig(criteria_weights, prompt_config, ranking_weights)
config.validate()
config.to_dict()
config.to_json()
```

## Support

For detailed information, see:
- **API Reference**: DOCUMENTATION.md
- **Configuration Guide**: CONFIGURATION_EXAMPLES.md
- **Working Examples**: example.py

