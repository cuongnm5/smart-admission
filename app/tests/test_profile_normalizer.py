from app.services.profile_normalizer import ProfileNormalizer


def test_profile_normalization(strong_cs_applicant) -> None:
    normalizer = ProfileNormalizer()

    normalized = normalizer.normalize(strong_cs_applicant)

    assert normalized.normalized_gpa_4 == 3.85
    assert normalized.intended_major == "Computer Science"
    assert normalized.leadership_score >= 1
    assert normalized.activity_score >= 1
    assert normalized.honor_score >= 1
