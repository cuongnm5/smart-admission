# Updated StudentProfile Model - International Student Support

## Overview

The StudentProfile model has been significantly enhanced to support comprehensive international student data, including detailed academic records, multiple GPA tracking, language proficiency tests, and rich extracurricular/leadership information.

## Key Enhancements

### 1. Academic Profile Expansion

#### Multi-Year GPA Tracking
```python
gpa_by_year: List[GPA]  # Track GPA for each year/term
current_gpa: Optional[float]  # Current overall GPA
weighted_gpa()  # Automatic calculation from all years
gpa_trend()  # Returns: "improving", "declining", or "stable"
```

#### Class Ranking
```python
@dataclass
class ClassRank:
    value: int  # Rank number (e.g., 8)
    total_students: int  # Total in class (e.g., 180)
    percentile() -> float  # Calculates percentile (e.g., 95.5%)
```

#### School Profile
```python
@dataclass
class SchoolProfile:
    school_name: str
    school_type: SchoolType  # PUBLIC, PRIVATE, SPECIALIZED, INTERNATIONAL
    location: str  # City/region
    country: str  # Country of school
    description: str  # School characteristics
    is_gifted_school: bool  # Flag for specialized schools
```

#### Detailed Transcript
```python
@dataclass
class TranscriptYear:
    year: str  # "Grade 10", "Grade 11", etc.
    subjects: List[TranscriptSubject]
    average_grade() -> float  # Automatic average calculation

@dataclass
class TranscriptSubject:
    subject: str
    grade: float  # Actual grade (e.g., 9.2)
    max_grade: float  # Max possible (e.g., 10.0)
    level: str  # "standard", "advanced", "AP", "IB"
    percentile() -> float  # Grade as percentage
```

### 2. Comprehensive Test Scores

#### English Proficiency Tests
```python
@dataclass
class EnglishTestScore:
    test_type: str  # "IELTS", "TOEFL", etc.
    score: float  # Overall score
    section_scores: Dict[str, float]  # Individual sections
    date: Optional[str]  # Test date
```

#### Standardized Tests
```python
@dataclass
class SATScore:
    total: int
    math: int
    reading_writing: int
    date: Optional[str]

@dataclass
class ACTScore:
    composite: int
    english: Optional[int]
    math: Optional[int]
    reading: Optional[int]
    science: Optional[int]
    date: Optional[str]
```

#### Advanced Exams
```python
@dataclass
class APScore:
    subject: str
    score: int  # 1-5 scale
    date: Optional[str]

@dataclass
class IBScore:
    subject: str
    score: int  # 1-7 scale
    level: str  # "SL" or "HL"
    date: Optional[str]
```

### 3. Enhanced Extracurricular Tracking

#### Activities with Duration Calculation
```python
@dataclass
class ExtracurricularActivity:
    activity_name: str
    role: str  # Position held
    organization: str  # School/external org
    description: str  # What was done
    start_date: str  # "YYYY-MM" format
    end_date: str  # "YYYY-MM" format
    hours_per_week: float
    category: str  # "Academic", "STEM", "Community Service", etc.
    achievement_level: int  # 1-5 scale
    duration_years() -> float  # Automatic calculation
```

#### Leadership Positions
```python
@dataclass
class Leadership:
    position: str  # "President", "Vice President", etc.
    organization: str
    description: str
    duration: str  # e.g., "2 years"
    start_date: Optional[str]
    end_date: Optional[str]
```

#### Awards & Recognitions
```python
@dataclass
class Award:
    award_name: str
    organizer: str
    level: str  # "school", "district", "state", "national", "international"
    year: int
    description: str
```

#### Projects & Portfolio
```python
@dataclass
class Project:
    project_name: str
    description: str
    role: str
    start_date: Optional[str]
    end_date: Optional[str]
    link: Optional[str]  # GitHub, website, etc.
    skills: List[str]  # Technologies/skills used
```

### 4. Enhanced Essays & Recommendations

```python
@dataclass
class Essay:
    essay_type: str  # "personal_statement", "supplemental", etc.
    prompt: Optional[str]  # Essay prompt
    content: Optional[str]  # Essay text
    word_count: Optional[int]
    theme: Optional[str]  # Main theme/topic

@dataclass
class RecommendationLetter:
    from_name: str  # Recommender name
    from_role: str  # Role (teacher, counselor, etc.)
    relationship_duration: str  # How long they know student
    content_summary: str  # Summary of recommendation
    school: Optional[str]  # School application for
```

### 5. Enhanced Preferences

```python
@dataclass
class PreferencesProfile:
    dream_major: Optional[str]  # First choice major
    intended_major: Optional[str]  # Intended/declared major
    target_schools: List[str]  # List of dream schools
    preferred_locations: List[str]  # Geographic preferences
    preferred_regions: List[str]  # US regions
    preferred_majors: List[str]  # Multiple major interests
    preferred_university_size: str  # "small", "medium", "large"
    preferred_campus_setting: str  # "urban", "suburban", "rural"
    ranking_preference: str  # e.g., "Top 50", "Top 100"
    school_type_preference: str  # "public", "private", etc.
    special_interests: List[str]  # Research, innovation, etc.
```

### 6. Enhanced Financial Profile

```python
@dataclass
class FinancialProfile:
    budget_per_year: float  # Maximum annual cost
    currency: str  # "USD", "EUR", etc.
    needs_financial_aid: bool
    scholarship_expectation_percent: float  # % of aid needed
    can_afford_full_cost: bool
    family_income_range: str  # e.g., "20000-30000 USD/year"
    annual_family_income: Optional[float]
    merit_scholarship_eligible: bool
```

## Usage Examples

### Load from JSON Data

```python
from matching_engine import StudentProfile

data = {
    "name": "Nguyen Van Tuan",
    "email": "tuan@example.com",
    "residency_status": "international",
    "country_of_origin": "Vietnam",
    
    "academic": {
        "gpa": [
            {"year": "Grade 10", "value": 3.7, "scale": 4.0},
            {"year": "Grade 11", "value": 3.9, "scale": 4.0},
            {"year": "Grade 12", "value": 3.95, "scale": 4.0}
        ],
        "class_rank": {"value": 8, "total_students": 180},
        "school_profile": {
            "school_name": "Le Hong Phong High School",
            "school_type": "specialized",
            "location": "Ho Chi Minh City",
            "country": "Vietnam",
            "is_gifted_school": True
        },
        "transcript": [
            {
                "year": "Grade 12",
                "subjects": [
                    {"subject": "Math", "grade": 9.8, "max_grade": 10, "level": "advanced"},
                    {"subject": "Physics", "grade": 9.6, "max_grade": 10, "level": "advanced"}
                ]
            }
        ],
        "test_scores": {
            "english_tests": [
                {"type": "IELTS", "score": 7.5, "section_scores": {...}}
            ],
            "sat": {"total": 1480, "math": 770, "reading_writing": 710},
            "ap_ib": [
                {"subject": "AP Calculus AB", "score": 5},
                {"subject": "AP Computer Science A", "score": 5}
            ]
        }
    },
    
    "intended_major": "Computer Science",
    
    "extracurriculars": [
        {
            "activity_name": "Coding Club",
            "role": "President",
            "organization": "School Club",
            "start_date": "2022-09",
            "end_date": "2024-05",
            "hours_per_week": 6,
            "achievement_level": 5
        }
    ],
    
    "leadership": [
        {
            "position": "President",
            "organization": "Coding Club",
            "duration": "2 years"
        }
    ],
    
    "awards": [
        {
            "award_name": "National Informatics Olympiad",
            "level": "national",
            "year": 2024
        }
    ],
    
    "financial": {
        "budget_per_year": 25000,
        "currency": "USD",
        "need_scholarship": True,
        "scholarship_expectation_percent": 50,
        "family_income_range": "20000-30000 USD/year"
    },
    
    "preferences": {
        "dream_major": "Computer Science",
        "target_schools": ["UC Berkeley", "UT Austin"],
        "preferred_locations": ["California", "Texas"],
        "ranking_preference": "Top 50",
        "school_type_preference": "public"
    }
}

# Create profile from data
student = StudentProfile.from_dict(data)
```

### Access Academic Information

```python
# GPA analysis
weighted_gpa = student.academic.weighted_gpa()  # 3.88
gpa_trend = student.academic.gpa_trend()  # "improving"

# Class ranking
rank = student.academic.class_rank
percentile = rank.percentile()  # 95.5%

# Transcript analysis
for year in student.academic.transcript:
    avg = year.average_grade()  # 95.3%
    for subject in year.subjects:
        pct = subject.percentile()  # 98%

# Test scores
sat_score = student.academic.test_scores.best_sat_score()  # 1480
english_score = student.academic.test_scores.best_english_score()  # 7.5
ap_scores = student.academic.test_scores.ap_scores
```

### Access Extracurricular Information

```python
# Activities
for activity in student.extracurricular_activities:
    name = activity.activity_name
    role = activity.role
    duration = activity.duration_years()  # Auto-calculated
    hours = activity.hours_per_week * duration * 52  # Estimate total hours

# Leadership
for lead in student.leadership_positions:
    position = lead.position
    org = lead.organization

# Awards
national_awards = [a for a in student.awards_recognitions if a.level == "national"]

# Projects
for proj in student.projects:
    skills = proj.skills  # ["Python", "NLP", "ML"]
    link = proj.link  # GitHub URL
```

### Access Financial Information

```python
budget = student.financial.budget_per_year  # 25000
needs_aid = student.financial.needs_financial_aid  # True
aid_percent = student.financial.scholarship_expectation_percent  # 50%
income = student.financial.family_income_range  # "20000-30000 USD/year"
```

### Serialize to Dictionary for LLM

```python
# Convert to dictionary for LLM processing
student_dict = student.to_dict()

# This includes computed fields:
# - weighted_gpa: Calculated from gpa_by_year
# - gpa_trend: "improving", "declining", or "stable"
# - class_rank with percentile
# - transcript with average_grade and percentile for each subject
# - duration_years for each activity
```

## Data Format Specifications

### Date Format
Use ISO 8601 format with year-month precision:
```
"start_date": "2022-09"  # September 2022
"end_date": "2024-05"    # May 2024
```

### GPA Scale Handling
- Default scale: 4.0 (US standard)
- Can specify different scales: 10.0 (many countries), 5.0, etc.
- StudentProfile normalizes for comparison

### Transcript Grading
- `grade`: Actual grade received (e.g., 9.2 out of 10)
- `max_grade`: Maximum possible grade (e.g., 10)
- `percentile()` method converts to 0-100 scale

### Test Scores
- **SAT**: Score out of 1600 (Math: 0-800, Reading/Writing: 0-800)
- **ACT**: Composite out of 36 (subscores out of 36)
- **IELTS**: Score 0-9 (sections also 0-9)
- **AP**: Score 1-5
- **IB**: Score 1-7

### Achievement Levels
All use 1-5 scale:
- 1: Minimal/Participant
- 2: Contributor
- 3: Active Participant (default)
- 4: Leadership/Recognition
- 5: Top Achievement/Excellence

## Enums

### ResidencyStatus
- `DOMESTIC` - US resident
- `INTERNATIONAL` - Non-US resident

### SchoolType
- `PUBLIC` - Public school
- `PRIVATE` - Private school
- `SPECIALIZED` - Specialized/gifted school
- `INTERNATIONAL` - International school

### TestType
- `SAT`
- `ACT`
- `IELTS`
- `TOEFL`

## Automatic Calculations

### GPA Calculations
```python
student.academic.weighted_gpa()  # Average of gpa_by_year
student.academic.gpa_trend()     # Compares recent vs earlier years
```

### Grade Percentiles
```python
subject.percentile()  # (grade / max_grade) * 100
year.average_grade()  # Average of all subject percentiles for year
```

### Class Rank Percentile
```python
rank.percentile()  # 100 * (1 - (rank - 1) / total)
# Example: Rank 8 of 180 = 95.5th percentile
```

### Activity Duration
```python
activity.duration_years()  # Auto-calculates from start_date to end_date
# Returns None if dates not available
```

## JSON Serialization

### to_dict()
Converts StudentProfile to dictionary with all computed fields:
```python
student_dict = student.to_dict()
# Includes: weighted_gpa, gpa_trend, percentiles, durations, etc.
```

### from_dict()
Creates StudentProfile from dictionary:
```python
student = StudentProfile.from_dict(json_data)
# Automatically handles parsing and object creation
```

## International Student Features

### Designed for Global Perspectives
- Multiple school systems (10-point, 4-point scales)
- Language proficiency tests (IELTS, TOEFL)
- School types (specialized/gifted schools)
- Location and country tracking
- Currency support in financial profile
- International award recognition levels

### Key Fields for International Students
```python
student.residency_status  # Mark as INTERNATIONAL
student.country_of_origin  # Country name
student.academic.school_profile.country  # School location
student.financial.currency  # Budget currency
student.financial.needs_financial_aid  # Often needed for intl
student.academic.test_scores.english_tests  # IELTS/TOEFL
```

## Integration with Matching Engine

### Complete Student Profile
```python
from matching_engine import MatchingEngine

student = StudentProfile.from_dict(api_data)
result = engine.match(student, top_20_universities)

# Result includes:
# - Top 10 universities
# - Suitability scores
# - Acceptance probabilities
# - Detailed analysis with reasoning
```

### LLM Processing
```python
# Convert to dict for LLM evaluation
student_dict = student.to_dict()

# LLM receives:
# - Detailed academic history
# - School context and ranking
# - Comprehensive extracurriculars
# - All test scores
# - Financial situation
# - University preferences
```

## Example: Vietnamese Student Profile

See `example_international_student.py` for a complete working example with:
- Multi-year GPA tracking
- Detailed transcript from Vietnam (10-point scale)
- Class ranking (8/180)
- School profile (specialized/gifted school)
- Language tests (IELTS 7.5)
- Standardized tests (SAT 1480)
- AP scores (5/5 on Calculus & CS)
- Extracurricular leadership
- National awards
- Projects with skills
- Financial aid needs (50%)
- Target US universities

Run with:
```bash
python example_international_student.py
```

## API Reference

### StudentProfile Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | `Dict` | Convert to dictionary for LLM/API |
| `from_dict(data)` | `StudentProfile` | Create from dictionary |

### AcademicProfile Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `weighted_gpa()` | `float` | Calculate average GPA from all years |
| `gpa_trend()` | `str` | Returns "improving", "declining", or "stable" |

### ClassRank Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `percentile()` | `float` | Calculate percentile rank (0-100) |

### TranscriptSubject Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `percentile()` | `float` | Convert grade to percentage (0-100) |

### TranscriptYear Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `average_grade()` | `float` | Average of all subject percentiles |

### TestScoresProfile Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `best_english_score()` | `Optional[float]` | Best English test score |
| `best_sat_score()` | `Optional[int]` | Best SAT total |
| `best_act_score()` | `Optional[int]` | Best ACT composite |

### ExtracurricularActivity Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `duration_years()` | `Optional[float]` | Duration from start to end date |

## Best Practices

1. **Use Correct Scales**: Set `gpa_scale` and `max_grade` for non-4.0 systems
2. **Date Formats**: Always use "YYYY-MM" format for dates
3. **Complete Information**: Fill in descriptions for context
4. **Activity Duration**: Always include both start and end dates
5. **Test Scores**: Include test dates for chronological context
6. **Financial Transparency**: Clearly state aid needs and budget
7. **School Context**: For international schools, include full profile
8. **Achievement Levels**: Use 1-5 scale consistently

## Migration from Old Model

Old model:
```python
academic = AcademicProfile(gpa=3.9)
```

New model:
```python
academic = AcademicProfile(
    gpa_by_year=[
        GPA(year="Grade 12", value=3.9)
    ],
    current_gpa=3.9
)
```

Both work, but new model provides richer data for LLM analysis.

