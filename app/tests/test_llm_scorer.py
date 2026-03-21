from app.components.matching.services.expert_rubric import ExpertRubricService
from app.components.matching.services.feature_builder import FeatureBuilder
from app.components.matching.services.hard_filter_engine import HardFilterEngine
from app.components.matching.services.llm_scorer import LLMScorer
from app.components.matching.services.profile_normalizer import ProfileNormalizer


class FakeLLMClient:
    def __init__(self, payload: str) -> None:
        self._payload = payload
        self.last_prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self._payload


def test_llm_scorer_parses_valid_json(strong_cs_applicant, repository) -> None:
    student = ProfileNormalizer().normalize(strong_cs_applicant)
    university = next(item for item in repository.list_universities() if item.university_id == "asu")
    hard_filter = HardFilterEngine(0.7).evaluate(student, university)
    features = FeatureBuilder().build(student, university)
    rubric = ExpertRubricService().get_rubric()

    client = FakeLLMClient(
        '{"academic_fit":80,"competitiveness_fit":70,"affordability_fit":75,'
        '"profile_alignment":78,"overall_match":76,"bucket":"target",'
        '"strengths":["Good academic baseline"],"concerns":["Competitive program"],'
        '"concise_rationale":"Strong baseline with manageable constraints."}'
    )
    scorer = LLMScorer(feature_builder=FeatureBuilder(), llm_client=client, llm_enabled=True)

    score = scorer.score(student, university, features, hard_filter, rubric, student_request=strong_cs_applicant)

    assert score.overall_match == 76
    assert score.bucket.value == "target"
    assert client.last_prompt is not None
    assert "student_profile_evidence" in client.last_prompt
    assert "extracurriculars" in client.last_prompt
    assert "leadership" in client.last_prompt
    assert "awards" in client.last_prompt
    assert "essays" in client.last_prompt
    assert "recommendation_letters" in client.last_prompt


def test_llm_scorer_falls_back_when_invalid_json(strong_cs_applicant, repository) -> None:
    student = ProfileNormalizer().normalize(strong_cs_applicant)
    university = next(item for item in repository.list_universities() if item.university_id == "asu")
    hard_filter = HardFilterEngine(0.7).evaluate(student, university)
    features = FeatureBuilder().build(student, university)
    rubric = ExpertRubricService().get_rubric()

    client = FakeLLMClient("not a json payload")
    scorer = LLMScorer(feature_builder=FeatureBuilder(), llm_client=client, llm_enabled=True)

    score = scorer.score(student, university, features, hard_filter, rubric)

    assert score.concise_rationale.startswith("Deterministic fallback")
