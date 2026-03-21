"""
Example: Loading comprehensive international student profile from JSON data.

This example demonstrates how to use the updated StudentProfile model
with real-world student data from an international student (Vietnam).
"""

import json
from app.components.summary.dto.student_profile import StudentProfile

# Vietnamese student data (from your provided JSON)
VIETNAMESE_STUDENT_DATA = {
    "name": "Nguyen Van Tuan",
    "email": "tuan.nguyen@example.com",
    "student_id": "VN-2024-001",
    "residency_status": "international",
    "country_of_origin": "Vietnam",

    "academic": {
        "gpa": [
            {"year": "Grade 10", "value": 3.7, "scale": 4.0},
            {"year": "Grade 11", "value": 3.9, "scale": 4.0},
            {"year": "Grade 12", "value": 3.95, "scale": 4.0}
        ],
        "class_rank": {
            "value": 8,
            "total_students": 180
        },
        "school_profile": {
            "school_name": "Le Hong Phong High School for the Gifted",
            "school_type": "specialized",
            "location": "Ho Chi Minh City, Vietnam",
            "country": "Vietnam",
            "description": "Top specialized high school with strong STEM focus",
            "is_gifted_school": True
        },
        "transcript": [
            {
                "year": "Grade 10",
                "subjects": [
                    {"subject": "Math", "grade": 9.2, "max_grade": 10, "level": "advanced"},
                    {"subject": "Physics", "grade": 9.0, "max_grade": 10, "level": "advanced"},
                    {"subject": "English", "grade": 8.5, "max_grade": 10, "level": "standard"}
                ]
            },
            {
                "year": "Grade 11",
                "subjects": [
                    {"subject": "Math", "grade": 9.6, "max_grade": 10, "level": "advanced"},
                    {"subject": "Physics", "grade": 9.4, "max_grade": 10, "level": "advanced"},
                    {"subject": "English", "grade": 8.8, "max_grade": 10, "level": "standard"}
                ]
            },
            {
                "year": "Grade 12",
                "subjects": [
                    {"subject": "Math", "grade": 9.8, "max_grade": 10, "level": "advanced"},
                    {"subject": "Physics", "grade": 9.6, "max_grade": 10, "level": "advanced"},
                    {"subject": "English", "grade": 9.0, "max_grade": 10, "level": "standard"}
                ]
            }
        ],
        "test_scores": {
            "english_tests": [
                {
                    "type": "IELTS",
                    "score": 7.5,
                    "section_scores": {
                        "listening": 8.0,
                        "reading": 7.5,
                        "writing": 7.0,
                        "speaking": 7.0
                    }
                }
            ],
            "sat": {
                "total": 1480,
                "math": 770,
                "reading_writing": 710
            },
            "act": None,
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
            "description": "Led 40 members, organized internal hackathons and coding workshops",
            "category": "Academic",
            "achievement_level": 5
        },
        {
            "activity_name": "Volunteer Teaching",
            "role": "Tutor",
            "organization": "Local NGO",
            "start_date": "2023-01",
            "end_date": "2024-01",
            "hours_per_week": 4,
            "description": "Taught basic programming for underprivileged students",
            "category": "Community Service",
            "achievement_level": 4
        }
    ],

    "leadership": [
        {
            "position": "President",
            "organization": "Coding Club",
            "description": "Managed team, planned events, and led projects",
            "duration": "2 years",
            "start_date": "2022-09",
            "end_date": "2024-05"
        }
    ],

    "awards": [
        {
            "award_name": "National Informatics Olympiad",
            "organizer": "Ministry of Education",
            "level": "national",
            "year": 2024,
            "description": "Top 10 nationwide"
        }
    ],

    "projects": [
        {
            "project_name": "AI Chatbot for Students",
            "role": "Developer",
            "description": "Built chatbot to help students with homework using NLP",
            "link": "https://github.com/example/chatbot",
            "start_date": "2023-06",
            "end_date": "2023-12",
            "skills": ["Python", "NLP", "Machine Learning", "Flask"]
        }
    ],

    "essays": {
        "personal_statement": {
            "content": "Story about growing passion for technology and desire to use AI for education"
        },
        "supplemental_essays": [
            {
                "school": "University of California, Berkeley",
                "prompt": "Why this major?",
                "content": "Explained interest in CS and research opportunities at Berkeley"
            }
        ],
        "recommendation_letters": [
            {
                "from": "Mr. Nguyen Van A",
                "role": "Math Teacher",
                "relationship_duration": "2 years",
                "content_summary": "Strong academic performance, excellent problem-solving skills"
            },
            {
                "from": "Ms. Tran Thi B",
                "role": "Counselor",
                "relationship_duration": "3 years",
                "content_summary": "Highly motivated student with leadership qualities"
            }
        ]
    },

    "financial": {
        "budget_per_year": 25000,
        "currency": "USD",
        "need_scholarship": True,
        "scholarship_expectation_percent": 50,
        "family_income_range": "20000-30000 USD/year"
    },

    "preferences": {
        "dream_major": "Computer Science",
        "target_schools": [
            "University of California, Berkeley",
            "University of Texas at Austin",
            "San Jose State University"
        ],
        "preferred_locations": ["California", "Texas"],
        "ranking_preference": "Top 50",
        "school_type_preference": "public"
    },

    "additional": {
        "cv": "https://example.com/cv.pdf"
    }
}


def example_load_from_json():
    """Example 1: Load student profile from JSON data."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Load from JSON Data")
    print("=" * 80)

    # Create student profile from dictionary
    student = StudentProfile.from_dict(VIETNAMESE_STUDENT_DATA)

    print(f"\nStudent Name: {student.name}")
    print(f"Email: {student.email}")
    print(f"Residency: {student.residency_status.value}")
    print(f"Country of Origin: {student.country_of_origin}")
    print(f"Intended Major: {student.intended_major}")

    # Display academic information
    print("\n--- Academic Information ---")
    print(f"Weighted GPA: {student.academic.weighted_gpa():.2f}")
    print(f"GPA Trend: {student.academic.gpa_trend()}")
    print(f"Class Rank: #{student.academic.class_rank.value} out of {student.academic.class_rank.total_students}")
    print(f"Class Rank Percentile: {student.academic.class_rank.percentile():.1f}%")

    # Display school information
    print("\n--- School Information ---")
    school = student.academic.school_profile
    print(f"School: {school.school_name}")
    print(f"Type: {school.school_type.value}")
    print(f"Location: {school.location}, {school.country}")
    print(f"Gifted School: {school.is_gifted_school}")
    print(f"Description: {school.description}")

    # Display transcript
    print("\n--- Transcript Summary ---")
    for year in student.academic.transcript:
        avg_grade = year.average_grade()
        print(f"\n{year.year}: Average Grade {avg_grade:.1f}%")
        for subject in year.subjects:
            print(f"  • {subject.subject}: {subject.grade}/{subject.max_grade} ({subject.percentile():.0f}%) - {subject.level}")

    # Display test scores
    print("\n--- Test Scores ---")
    if student.academic.test_scores.english_tests:
        for test in student.academic.test_scores.english_tests:
            print(f"IELTS: {test.score}")
            print(f"  Sections: {test.section_scores}")

    if student.academic.test_scores.sat:
        sat = student.academic.test_scores.sat
        print(f"SAT: {sat.total} (Math: {sat.math}, Reading/Writing: {sat.reading_writing})")

    if student.academic.test_scores.ap_scores:
        print(f"AP Scores:")
        for ap in student.academic.test_scores.ap_scores:
            print(f"  • {ap.subject}: {ap.score}/5")

    # Display extracurricular activities
    print("\n--- Extracurricular Activities ---")
    for act in student.extracurricular_activities:
        duration = act.duration_years()
        print(f"\n{act.activity_name}")
        print(f"  Role: {act.role}")
        print(f"  Organization: {act.organization}")
        print(f"  Duration: {duration:.1f} years" if duration else "  Duration: N/A")
        print(f"  Hours/Week: {act.hours_per_week}")
        print(f"  Achievement Level: {act.achievement_level}/5")
        print(f"  Description: {act.description}")

    # Display leadership
    print("\n--- Leadership Positions ---")
    for lead in student.leadership_positions:
        print(f"\n{lead.position} - {lead.organization}")
        print(f"  Duration: {lead.duration}")
        print(f"  Description: {lead.description}")

    # Display awards
    print("\n--- Awards & Recognitions ---")
    for award in student.awards_recognitions:
        print(f"\n{award.award_name}")
        print(f"  Level: {award.level}")
        print(f"  Year: {award.year}")
        print(f"  Description: {award.description}")

    # Display projects
    print("\n--- Projects & Portfolio ---")
    for proj in student.projects:
        print(f"\n{proj.project_name}")
        print(f"  Role: {proj.role}")
        print(f"  Description: {proj.description}")
        print(f"  Link: {proj.link}")
        print(f"  Skills: {', '.join(proj.skills)}")

    # Display preferences
    print("\n--- University Preferences ---")
    print(f"Dream Major: {student.preferences.dream_major}")
    print(f"Target Schools: {', '.join(student.preferences.target_schools)}")
    print(f"Preferred Locations: {', '.join(student.preferences.preferred_locations)}")
    print(f"Ranking Preference: {student.preferences.ranking_preference}")
    print(f"School Type Preference: {student.preferences.school_type_preference}")

    # Display financial information
    print("\n--- Financial Information ---")
    print(f"Budget per Year: ${student.financial.budget_per_year} {student.financial.currency}")
    print(f"Needs Financial Aid: {student.financial.needs_financial_aid}")
    print(f"Scholarship Expectation: {student.financial.scholarship_expectation_percent}%")
    print(f"Family Income Range: {student.financial.family_income_range}")


def example_serialize_to_json():
    """Example 2: Serialize profile to JSON for LLM/API processing."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Serialize to JSON")
    print("=" * 80)

    student = StudentProfile.from_dict(VIETNAMESE_STUDENT_DATA)

    # Convert to dictionary for LLM
    student_dict = student.to_dict()

    print("\nProfile serialized to dictionary:")
    print(f"Keys: {list(student_dict.keys())}")

    print("\nAcademic section keys:")
    print(f"  {list(student_dict['academic'].keys())}")

    print("\nSample GPA data:")
    print(f"  Current GPA: {student_dict['academic']['current_gpa']}")
    print(f"  Weighted GPA: {student_dict['academic']['weighted_gpa']:.2f}")
    print(f"  GPA Trend: {student_dict['academic']['gpa_trend']}")

    # Can be serialized to JSON
    json_str = json.dumps(student_dict, indent=2)
    print(f"\nJSON serialization successful: {len(json_str)} characters")


def example_academic_analysis():
    """Example 3: Detailed academic analysis."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Academic Analysis")
    print("=" * 80)

    student = StudentProfile.from_dict(VIETNAMESE_STUDENT_DATA)

    print("\n--- GPA Analysis ---")
    print("GPA by Year:")
    for gpa in student.academic.gpa_by_year:
        print(f"  {gpa.year}: {gpa.value}/{gpa.scale}")

    weighted = student.academic.weighted_gpa()
    trend = student.academic.gpa_trend()
    print(f"\nWeighted GPA: {weighted:.2f}")
    print(f"Trend: {trend.upper()}")

    print("\n--- Transcript Analysis ---")
    for year in student.academic.transcript:
        avg = year.average_grade()
        print(f"\n{year.year}:")
        print(f"  Average Grade: {avg:.1f}%")

        # Find best and worst subjects
        if year.subjects:
            best = max(year.subjects, key=lambda s: s.percentile())
            worst = min(year.subjects, key=lambda s: s.percentile())
            print(f"  Best Subject: {best.subject} ({best.percentile():.0f}%)")
            print(f"  Challenging Subject: {worst.subject} ({worst.percentile():.0f}%)")

    print("\n--- Class Ranking Analysis ---")
    rank = student.academic.class_rank
    print(f"Rank: #{rank.value}/{rank.total_students}")
    print(f"Percentile: {rank.percentile():.1f}% (Top {100-rank.percentile():.1f}%)")

    print("\n--- Test Score Summary ---")
    sat = student.academic.test_scores.best_sat_score()
    english = student.academic.test_scores.best_english_score()
    print(f"SAT: {sat if sat else 'Not taken'}")
    print(f"Best English Test: {english if english else 'Not taken'}")
    print(f"AP Scores: {len(student.academic.test_scores.ap_scores)} exams")
    for ap in student.academic.test_scores.ap_scores:
        print(f"  • {ap.subject}: {ap.score}/5")


def example_extracurricular_analysis():
    """Example 4: Analyze extracurricular profile."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Extracurricular Analysis")
    print("=" * 80)

    student = StudentProfile.from_dict(VIETNAMESE_STUDENT_DATA)

    print("\n--- Activity Summary ---")
    print(f"Total Activities: {len(student.extracurricular_activities)}")

    total_hours = sum(
        act.hours_per_week * (act.duration_years() or 1)
        for act in student.extracurricular_activities
        if act.hours_per_week and act.duration_years()
    )
    print(f"Total Hours (estimated): {total_hours:.0f}")

    print("\n--- Activities by Category ---")
    by_category = {}
    for act in student.extracurricular_activities:
        cat = act.category or "Other"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(act)

    for category, activities in by_category.items():
        print(f"\n{category}:")
        for act in activities:
            print(f"  • {act.activity_name} ({act.role})")
            print(f"    {act.hours_per_week} hrs/week for {act.duration_years():.1f} years" if act.duration_years() else "")

    print("\n--- Leadership Analysis ---")
    print(f"Total Leadership Positions: {len(student.leadership_positions)}")
    for lead in student.leadership_positions:
        print(f"\n{lead.position} - {lead.organization}")
        print(f"  Duration: {lead.duration}")

    print("\n--- Awards Summary ---")
    awards_by_level = {}
    for award in student.awards_recognitions:
        level = award.level
        if level not in awards_by_level:
            awards_by_level[level] = []
        awards_by_level[level].append(award)

    for level in ["national", "state", "district", "school"]:
        if level in awards_by_level:
            print(f"\n{level.upper()}:")
            for award in awards_by_level[level]:
                print(f"  • {award.award_name} ({award.year})")


def example_profile_strengths():
    """Example 5: Identify profile strengths."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Profile Strengths & Competitive Analysis")
    print("=" * 80)

    student = StudentProfile.from_dict(VIETNAMESE_STUDENT_DATA)

    print("\n--- Academic Strengths ---")
    academic = student.academic

    strengths = []

    # GPA analysis
    weighted_gpa = academic.weighted_gpa()
    if weighted_gpa >= 3.8:
        strengths.append(f"✓ Excellent GPA: {weighted_gpa:.2f}/4.0")

    # GPA trend
    if academic.gpa_trend() == "improving":
        strengths.append("✓ Upward GPA trend (showing improvement)")

    # Class rank
    if academic.class_rank:
        percentile = academic.class_rank.percentile()
        if percentile >= 95:
            strengths.append(f"✓ Top class rank: {percentile:.0f}th percentile")

    # Gifted school
    if academic.school_profile and academic.school_profile.is_gifted_school:
        strengths.append("✓ Attends specialized/gifted school")

    # Test scores
    sat = academic.test_scores.best_sat_score()
    if sat and sat >= 1450:
        strengths.append(f"✓ Strong SAT: {sat}")

    english = academic.test_scores.best_english_score()
    if english and english >= 7.0:
        strengths.append(f"✓ Good English proficiency: {english}/9.0 IELTS")

    # AP/IB performance
    if academic.test_scores.ap_scores:
        perfect_aps = sum(1 for ap in academic.test_scores.ap_scores if ap.score == 5)
        if perfect_aps > 0:
            strengths.append(f"✓ Perfect AP scores: {perfect_aps} exams with 5/5")

    for strength in strengths:
        print(f"  {strength}")

    print("\n--- Extracurricular Strengths ---")
    extracurricular_strengths = []

    if any(lead.position == "President" for lead in student.leadership_positions):
        extracurricular_strengths.append("✓ Leadership experience (President)")

    if any(award.level == "national" for award in student.awards_recognitions):
        extracurricular_strengths.append("✓ National-level recognition")

    if student.projects:
        extracurricular_strengths.append(f"✓ Portfolio with {len(student.projects)} projects")

    for strength in extracurricular_strengths:
        print(f"  {strength}")

    print("\n--- International Student Advantages ---")
    if student.residency_status.value == "international":
        print("  ✓ International diversity perspective")

    if student.country_of_origin:
        print(f"  ✓ From {student.country_of_origin}")

    if student.financial.needs_financial_aid:
        print(f"  ⚠ Requires financial aid ({student.financial.scholarship_expectation_percent}% expected)")

    print("\n--- Profile Fit Analysis ---")
    print(f"Target Major: {student.intended_major}")
    print(f"Target Schools: {', '.join(student.preferences.target_schools[:2])}...")
    print(f"Budget: ${student.financial.budget_per_year}/year")
    print(f"Scholarship Needed: {student.financial.scholarship_expectation_percent}%")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("COMPREHENSIVE STUDENT PROFILE EXAMPLES")
    print("International Student Data (Vietnam)")
    print("=" * 80)

    example_load_from_json()
    example_serialize_to_json()
    example_academic_analysis()
    example_extracurricular_analysis()
    example_profile_strengths()

    print("\n" + "=" * 80)
    print("END OF EXAMPLES")
    print("=" * 80)

