from __future__ import annotations

import json

from app.domain.models import DeterministicFeaturePacket, HardFilterResult, NormalizedStudentProfile, RubricConfig, UniversityProfile
from app.schemas.request import StudentMatchRequest


def build_match_scoring_prompt(
    student: NormalizedStudentProfile,
    university: UniversityProfile,
    features: DeterministicFeaturePacket,
    hard_filter: HardFilterResult,
    rubric: RubricConfig,
    student_request: StudentMatchRequest | None = None,
) -> str:
    _ = student
    _ = features
    _ = hard_filter

    evidence = {
        "university_summary": {
            "admission_rate": university.admissio_rate,
            "sat_avg": university.sat_avg,
            "tuition_in_state": university.tution_in_state,
            "tuition_out_of_state": university.tution_out_of_state,
            "programs_offered": university.programs_offered,
            "top_programs": university.top_programs,
        },
        "rubric": rubric.model_dump(),
        "student_profile_evidence": {
            "extracurriculars": [],
            "leadership": [],
            "awards": [],
            "essays": {},
            "recommendation_letters": [],
        },
    }

    if student_request is not None:
        evidence["student_profile_evidence"] = {
            "extracurriculars": [
                {
                    "activity_name": item.activity_name,
                    "role": item.role,
                    "organization": item.organization,
                    "hours_per_week": item.hours_per_week,
                    "description": item.description,
                }
                for item in student_request.extracurriculars
            ],
            "leadership": [
                {
                    "position": item.position,
                    "organization": item.organization,
                    "description": item.description,
                    "duration": item.duration,
                }
                for item in student_request.leadership
            ],
            "awards": [
                {
                    "award_name": item.award_name,
                    "organizer": item.organizer,
                    "level": item.level,
                    "year": item.year,
                    "description": item.description,
                }
                for item in student_request.awards
            ],
            "essays": student_request.essays.model_dump(by_alias=True),
            "recommendation_letters": [
                item.model_dump(by_alias=True)
                for item in student_request.recommendation_letters
            ],
        }

    return (
    "You are an admissions matching evaluator.\n"
    "Your task is to score how well this student's qualitative profile matches this university.\n\n"

    "Use ONLY the provided evidence:\n"
    "- university_summary\n"
    "- student_profile_evidence\n\n"

    "Do NOT use GPA, IELTS, SAT, hard-filter results, deterministic features, or any other numeric eligibility data.\n"
    "Do NOT invent facts about the student or the university.\n\n"

    "Scoring rule:\n"
    "- Give one overall match score from 0 to 100.\n"
    "- The score must reflect university-specific fit, not generic student quality.\n"
    "- A strong student is not automatically a strong match for every university.\n"
    "- Reward direct alignment between the student's activities, leadership, awards, essays, and the university's programs, strengths, and context.\n"
    "- If evidence is limited or unclear, give a moderate score instead of an extreme score.\n\n"

    "Score interpretation:\n"
    "- 0-39: weak match\n"
    "- 40-59: below average match\n"
    "- 60-74: moderate match\n"
    "- 75-89: strong match\n"
    "- 90-100: exceptional match\n\n"

    "Return ONLY the integer score. No explanation. No markdown.\n\n"

    "Evidence JSON:\n"
    f"{json.dumps(evidence, default=str, ensure_ascii=False)}"
)
