from __future__ import annotations

from app.domain.models import HardFilterResult, NormalizedStudentProfile, RuleTrace, UniversityProfile
from app.components.matching.services.university_identity import build_university_id


class HardFilterEngine:
    def __init__(self, affordability_reject_ratio: float) -> None:
        self._affordability_reject_ratio = affordability_reject_ratio

    def evaluate(self, student: NormalizedStudentProfile, university: UniversityProfile) -> HardFilterResult:
        trace: list[RuleTrace] = []
        university_id = build_university_id(university)

        offered_programs = [item.strip().lower() for item in university.programs_offered.split(",") if item.strip()]
        intended_major_key = student.intended_major.strip().lower()
        major_pass = any(
            intended_major_key == major or intended_major_key in major or major in intended_major_key
            for major in offered_programs
        )
        trace.append(
            RuleTrace(rule="major_available", **{"pass": major_pass}, student=student.intended_major, required=True)
        )
        if not major_pass:
            return HardFilterResult(
                university_id=university_id,
                passed=False,
                trace=trace,
                reject_reason="Intended major is unavailable.",
            )

        trace.append(
            RuleTrace(
                rule="tuition_in_state_present",
                **{"pass": university.tution_in_state >= 0},
                student=university.tution_in_state,
                required=0,
            )
        )

        trace.append(
            RuleTrace(
                rule="tuition_out_of_state_present",
                **{"pass": university.tution_out_of_state >= 0},
                student=university.tution_out_of_state,
                required=0,
            )
        )

        trace.append(
            RuleTrace(
                rule="admission_rate_signal",
                **{"pass": True},
                student=university.admissio_rate,
                required="[0,1]",
            )
        )

        estimated_net_cost = max(0.0, university.tution_in_state, university.tution_out_of_state)
        minimum_acceptable_budget = estimated_net_cost * self._affordability_reject_ratio
        affordability_pass = student.annual_budget_usd >= minimum_acceptable_budget
        trace.append(
            RuleTrace(
                rule="estimated_affordability",
                **{"pass": affordability_pass},
                student=student.annual_budget_usd,
                required=round(minimum_acceptable_budget, 2),
                detail=f"estimated_net_cost_from_tuition={estimated_net_cost}",
            )
        )
        if not affordability_pass:
            return HardFilterResult(
                university_id=university_id,
                passed=False,
                trace=trace,
                reject_reason="Budget is significantly below estimated net cost.",
            )

        return HardFilterResult(university_id=university_id, passed=True, trace=trace)
