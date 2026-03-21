from __future__ import annotations

from app.domain.models import HardFilterResult, NormalizedStudentProfile, RuleTrace, UniversityProfile


class HardFilterEngine:
    def __init__(self, affordability_reject_ratio: float) -> None:
        self._affordability_reject_ratio = affordability_reject_ratio

    def evaluate(self, student: NormalizedStudentProfile, university: UniversityProfile) -> HardFilterResult:
        trace: list[RuleTrace] = []

        international_pass = university.accepts_international_students
        trace.append(
            RuleTrace(rule="international_allowed", **{"pass": international_pass}, student=True, required=True)
        )
        if not international_pass:
            return HardFilterResult(
                university_id=university.university_id,
                passed=False,
                trace=trace,
                reject_reason="University does not accept international students.",
            )

        major_pass = any(major.lower() == student.intended_major.lower() for major in university.majors)
        trace.append(
            RuleTrace(rule="major_available", **{"pass": major_pass}, student=student.intended_major, required=True)
        )
        if not major_pass:
            return HardFilterResult(
                university_id=university.university_id,
                passed=False,
                trace=trace,
                reject_reason="Intended major is unavailable.",
            )

        ielts_pass = student.ielts >= university.ielts_min
        trace.append(
            RuleTrace(
                rule="ielts_min",
                **{"pass": ielts_pass},
                student=student.ielts,
                required=university.ielts_min,
            )
        )
        if not ielts_pass:
            return HardFilterResult(
                university_id=university.university_id,
                passed=False,
                trace=trace,
                reject_reason="IELTS requirement not met.",
            )

        gpa_pass = student.normalized_gpa_4 >= university.min_gpa
        trace.append(
            RuleTrace(
                rule="gpa_min",
                **{"pass": gpa_pass},
                student=student.normalized_gpa_4,
                required=university.min_gpa,
            )
        )
        if not gpa_pass:
            return HardFilterResult(
                university_id=university.university_id,
                passed=False,
                trace=trace,
                reject_reason="Minimum GPA not met.",
            )

        estimated_net_cost = max(0.0, university.total_cost_usd - university.max_merit_usd)
        minimum_acceptable_budget = estimated_net_cost * self._affordability_reject_ratio
        affordability_pass = student.annual_budget_usd >= minimum_acceptable_budget
        trace.append(
            RuleTrace(
                rule="estimated_affordability",
                **{"pass": affordability_pass},
                student=student.annual_budget_usd,
                required=round(minimum_acceptable_budget, 2),
                detail=f"estimated_net_cost={estimated_net_cost}",
            )
        )
        if not affordability_pass:
            return HardFilterResult(
                university_id=university.university_id,
                passed=False,
                trace=trace,
                reject_reason="Budget is significantly below estimated net cost.",
            )

        return HardFilterResult(university_id=university.university_id, passed=True, trace=trace)
