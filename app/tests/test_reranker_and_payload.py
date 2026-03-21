from app.domain.models import CandidateEvaluation
from app.schemas.response import MatchingResponse
from app.services.consultant_payload_builder import ConsultantPayloadBuilder
from app.services.expert_rubric import ExpertRubricService
from app.services.feature_builder import FeatureBuilder
from app.services.hard_filter_engine import HardFilterEngine
from app.services.llm_scorer import LLMScorer
from app.services.profile_normalizer import ProfileNormalizer
from app.services.reranker import Reranker


def test_reranker_and_payload_format(strong_cs_applicant, repository) -> None:
    student = ProfileNormalizer().normalize(strong_cs_applicant)
    rubric = ExpertRubricService().get_rubric()

    builder = FeatureBuilder()
    scorer = LLMScorer(feature_builder=builder, llm_enabled=False)
    hard_filter_engine = HardFilterEngine(affordability_reject_ratio=0.7)

    evaluations: list[CandidateEvaluation] = []
    for university in repository.find_by_major_and_international(student.intended_major):
        hard_filter = hard_filter_engine.evaluate(student, university)
        if not hard_filter.passed:
            continue
        features = builder.build(student, university)
        score = scorer.score(student, university, features, hard_filter, rubric)
        evaluations.append(
            CandidateEvaluation(
                university=university,
                hard_filter=hard_filter,
                features=features,
                score=score,
            )
        )

    ranked = Reranker().rerank(evaluations, top_k=20)
    response = ConsultantPayloadBuilder().build(
        ranked_candidates=ranked,
        retrieved_count=len(repository.find_by_major_and_international(student.intended_major)),
        hard_filter_pass_count=len(evaluations),
        scored_count=len(evaluations),
        rubric_version=rubric.rubric_version,
    )

    assert isinstance(response, MatchingResponse)
    assert response.meta.returned_count <= 20
    if response.top_candidates:
        assert isinstance(response.top_candidates[0], str)
        assert response.top_candidates[0]
