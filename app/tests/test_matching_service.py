from app.schemas.response import MatchingResponse


def test_matching_service_returns_consultant_payload(strong_cs_applicant, matching_service) -> None:
    response = matching_service.match(strong_cs_applicant)

    assert isinstance(response, MatchingResponse)
    assert response.meta.returned_count <= 20
    assert response.meta.retrieved_count >= response.meta.hard_filter_pass_count
    if response.top_candidates:
        assert isinstance(response.top_candidates[0], str)
        assert response.top_candidates[0]
