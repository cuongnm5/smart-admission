from app.services.hard_filter_engine import HardFilterEngine
from app.services.profile_normalizer import ProfileNormalizer


def test_hard_filter_rejects_budget_constrained_candidate(budget_constrained_applicant, repository) -> None:
    student = ProfileNormalizer().normalize(budget_constrained_applicant)
    university = next(item for item in repository.list_universities() if item.university_id == "uiuc")

    result = HardFilterEngine(affordability_reject_ratio=0.7).evaluate(student, university)

    assert result.passed is False
    assert result.reject_reason is not None
    assert result.trace[-1].rule == "estimated_affordability"


def test_hard_filter_passes_eligible_candidate(strong_cs_applicant, repository) -> None:
    student = ProfileNormalizer().normalize(strong_cs_applicant)
    university = next(item for item in repository.list_universities() if item.university_id == "uta")

    result = HardFilterEngine(affordability_reject_ratio=0.7).evaluate(student, university)

    assert result.passed is True
    assert len(result.trace) >= 5
