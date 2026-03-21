from __future__ import annotations

from app.domain.enums import CompetitivenessLevel, SelectivityBand
from app.domain.models import DeterministicFeaturePacket, NormalizedStudentProfile, UniversityProfile


class FeatureBuilder:
    def __init__(self, affordability_feature_cap: float = 50000.0) -> None:
        self._affordability_feature_cap = affordability_feature_cap

    def build(self, student: NormalizedStudentProfile, university: UniversityProfile) -> DeterministicFeaturePacket:
        estimated_net_cost = max(0.0, university.total_cost_usd - university.max_merit_usd)
        affordability_gap = student.annual_budget_usd - estimated_net_cost

        major_match_score = 100.0 if any(
            major.lower() == student.intended_major.lower() for major in university.majors
        ) else 0.0

        scholarship_support_score = 100.0 if university.merit_for_internationals and university.max_merit_usd > 0 else 40.0
        scholarship_support_score = min(100.0, scholarship_support_score + min(40.0, university.max_merit_usd / 500.0))

        major_competitiveness = university.major_competitiveness.get(
            student.intended_major,
            CompetitivenessLevel.MEDIUM,
        )
        competitiveness_penalty = self._competitiveness_penalty(university.selectivity_band, major_competitiveness)

        profile_strength_score = min(
            100.0,
            (student.honor_score * 0.4 + student.leadership_score * 0.35 + student.activity_score * 0.25) * 20.0,
        )

        return DeterministicFeaturePacket(
            university_id=university.university_id,
            gpa_gap_to_min=round(student.normalized_gpa_4 - university.min_gpa, 3),
            gpa_gap_to_competitive=round(student.normalized_gpa_4 - university.competitive_gpa, 3),
            ielts_gap=round(student.ielts - university.ielts_min, 3),
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

    @staticmethod
    def _competitiveness_penalty(
        selectivity_band: SelectivityBand,
        major_competitiveness: CompetitivenessLevel,
    ) -> float:
        selectivity_weight = {
            SelectivityBand.HIGH: 30.0,
            SelectivityBand.MEDIUM: 20.0,
            SelectivityBand.LOW: 10.0,
        }[selectivity_band]

        major_weight = {
            CompetitivenessLevel.VERY_HIGH: 35.0,
            CompetitivenessLevel.HIGH: 25.0,
            CompetitivenessLevel.MEDIUM: 15.0,
            CompetitivenessLevel.LOW: 5.0,
        }[major_competitiveness]

        return min(100.0, selectivity_weight + major_weight)
