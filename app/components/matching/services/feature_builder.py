from __future__ import annotations

from app.domain.models import DeterministicFeaturePacket, NormalizedStudentProfile, UniversityProfile
from app.components.matching.services.university_identity import build_university_id


class FeatureBuilder:
    def __init__(self, affordability_feature_cap: float = 50000.0) -> None:
        self._affordability_feature_cap = affordability_feature_cap

    def build(self, student: NormalizedStudentProfile, university: UniversityProfile) -> DeterministicFeaturePacket:
        estimated_net_cost = max(0.0, university.tution_in_state, university.tution_out_of_state)
        affordability_gap = student.annual_budget_usd - estimated_net_cost

        offered_programs = [item.strip().lower() for item in university.programs_offered.split(",") if item.strip()]
        intended_major_key = student.intended_major.strip().lower()

        major_match_score = 100.0 if any(
            intended_major_key == major or intended_major_key in major or major in intended_major_key
            for major in offered_programs
        ) else 0.0

        scholarship_support_score = 50.0
        selectivity_penalty = (1.0 - min(1.0, max(0.0, university.admissio_rate))) * 60.0
        sat_penalty = max(0.0, min(40.0, (university.sat_avg - 900.0) / 700.0 * 40.0))
        competitiveness_penalty = min(100.0, selectivity_penalty + sat_penalty)

        profile_strength_score = min(
            100.0,
            (student.honor_score * 0.4 + student.leadership_score * 0.35 + student.activity_score * 0.25) * 20.0,
        )

        return DeterministicFeaturePacket(
            university_id=build_university_id(university),
            gpa_gap_to_min=0.0,
            gpa_gap_to_competitive=0.0,
            ielts_gap=0.0,
            affordability_gap=round(affordability_gap, 2),
            major_match_score=major_match_score,
            scholarship_support_score=round(scholarship_support_score, 2),
            competitiveness_penalty=round(competitiveness_penalty, 2),
            profile_strength_score=round(profile_strength_score, 2),
        )

    def affordability_fit_score(self, affordability_gap: float) -> int:
        normalized = (affordability_gap + self._affordability_feature_cap) / (2 * self._affordability_feature_cap)
        normalized = max(0.0, min(1.0, normalized))
        return int(round(normalized * 100.0))

