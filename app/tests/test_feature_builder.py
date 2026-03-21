from app.components.matching.services.feature_builder import FeatureBuilder
from app.components.matching.services.profile_normalizer import ProfileNormalizer


def test_feature_builder_outputs_expected_fields(strong_cs_applicant, repository) -> None:
    student = ProfileNormalizer().normalize(strong_cs_applicant)
    university = next(item for item in repository.list_universities() if item.university_id == "asu")

    features = FeatureBuilder().build(student, university)

    assert isinstance(features.gpa_gap_to_min, float)
    assert isinstance(features.gpa_gap_to_competitive, float)
    assert 0 <= features.profile_strength_score <= 100
    assert 0 <= features.scholarship_support_score <= 100
