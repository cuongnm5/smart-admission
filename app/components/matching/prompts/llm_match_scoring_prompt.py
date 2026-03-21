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
            "admissio_rate": university.admissio_rate,
            "sat_avg": university.sat_avg,
            "tution_in_state": university.tution_in_state,
            "tution_out_of_state": university.tution_out_of_state,
            "programs_offered": university.programs_offered,
            "top_programs": university.top_programs,
        },
        "rubric": rubric.model_dump(),
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
        "You are an admissions matching evaluator in a Smart University Suggestion System.\n"
        "Your task is to score how well the student's qualitative profile matches this specific university.\n"
        "Evaluate relevance ONLY by comparing:\n"
        "- university_summary\n"
        "- student_profile_evidence\n\n"

        "Important scoring principle:\n"
        "All scores must reflect the degree of evidence-based alignment between the student's profile and the university's characteristics, expectations, and context.\n"
        "Do NOT score in isolation. Always judge the student evidence relative to this university.\n\n"

        "Use ONLY the provided evidence fields from student_profile_evidence:\n"
        "- extracurriculars\n"
        "- leadership\n"
        "- awards\n"
        "- essays\n"
        "- recommendation_letters\n\n"

        "Do NOT use hard-filter metrics, deterministic features, GPA, IELTS, or other numeric eligibility metrics in scoring.\n"
        "Do NOT infer unsupported facts about the student or the university.\n\n"

        "Score definitions:\n"
        "- academic_fit (0-100): How well the student's demonstrated academic interests, intellectual direction, motivation, and academic-related evidence align with the university's academic environment, selectivity, and major competitiveness.\n"
        "- competitiveness_fit (0-100): How competitive this student's qualitative profile appears for this university based on leadership, distinction, impact, initiative, recognition, and overall strength of non-numeric evidence.\n"
        "- affordability_fit (0-100): Score ONLY if there is direct evidence in essays or recommendation letters about financial need, scholarship-seeking intent, cost sensitivity, or resource constraints AND the university summary suggests affordability relevance. If affordability evidence is absent, assign a neutral score in the 45-55 range rather than guessing.\n"
        "- profile_alignment (0-100): How well the student's activities, leadership, awards, values, and narrative themes match the university's type, region, culture, opportunities, and positioning described in university_summary.\n"
        "- overall_match (0-100): A holistic evidence-based match score for this student and this university. This should reflect the overall relevance between the student's profile and the university, not an average copied mechanically from other fields.\n\n"

        "Evidence handling rules:\n"
        "1) Reward strong direct alignment between student activities/themes and university context.\n"
        "2) Reward consistency across multiple evidence sources.\n"
        "3) Penalize missing or weak evidence for claims that would matter to this university.\n"
        "4) If evidence is sparse, use moderate scores instead of extreme scores.\n"
        "5) If a dimension cannot be strongly supported, keep the score conservative.\n\n"

        "Bucket rules:\n"
        "- reach if overall_match < 55\n"
        "- target if overall_match between 55 and 79\n"
        "- likely if overall_match >= 80\n\n"

        "Critical constraints:\n"
        "1) Never invent university facts.\n"
        "2) Never invent student achievements or traits.\n"
        "3) Ignore hard filter traces and deterministic metric values in scoring.\n"
        "4) strengths and concerns must be short, evidence-grounded lists.\n"
        "5) concise_rationale must explicitly mention the relationship between the student profile and the university in no more than 2 sentences.\n"
        "6) Return JSON ONLY. No markdown, no commentary.\n\n"

        "Required JSON schema:\n"
        "{\n"
        '  "academic_fit": int,\n'
        '  "competitiveness_fit": int,\n'
        '  "affordability_fit": int,\n'
        '  "profile_alignment": int,\n'
        '  "overall_match": int,\n'
        '  "bucket": "reach" | "target" | "likely",\n'
        '  "strengths": [str, ...],\n'
        '  "concerns": [str, ...],\n'
        '  "concise_rationale": str\n'
        "}\n\n"

        "Evidence JSON:\n"
        f"{json.dumps(evidence, default=str)}"
    )
