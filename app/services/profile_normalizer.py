from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.models import NormalizedStudentProfile
from app.schemas.request import StudentMatchRequest


@dataclass(frozen=True)
class ProfileHeuristicLexicon:
    leadership_keywords: tuple[str, ...] = (
        "leader",
        "captain",
        "president",
        "founded",
        "organized",
        "mentored",
    )
    activity_keywords: tuple[str, ...] = (
        "club",
        "volunteer",
        "community",
        "project",
        "competition",
        "hackathon",
        "teaching",
    )
    honor_keywords: tuple[str, ...] = (
        "award",
        "prize",
        "honor",
        "scholarship",
        "distinction",
        "medal",
    )


class ProfileNormalizer:
    def __init__(self, lexicon: ProfileHeuristicLexicon | None = None) -> None:
        self._lexicon = lexicon or ProfileHeuristicLexicon()

    def normalize(self, request: StudentMatchRequest) -> NormalizedStudentProfile:
        raw_gpa, raw_gpa_scale = self._derive_gpa(request)
        normalized_gpa = round((raw_gpa / raw_gpa_scale) * 4.0, 2)
        normalized_gpa = max(0.0, min(4.0, normalized_gpa))

        ielts = self._derive_ielts(request)
        profile_text = self._build_profile_text(request)

        major = self._normalize_major(request.intended_major)
        leadership_score = self._keyword_score(profile_text, self._lexicon.leadership_keywords)
        activity_score = self._keyword_score(profile_text, self._lexicon.activity_keywords)
        honor_score = self._keyword_score(profile_text, self._lexicon.honor_keywords)

        return NormalizedStudentProfile(
            student_id=request.student_id,
            normalized_gpa_4=normalized_gpa,
            raw_gpa=raw_gpa,
            raw_gpa_scale=raw_gpa_scale,
            ielts=ielts,
            intended_major=major,
            annual_budget_usd=request.financial.budget_per_year,
            profile_text=profile_text,
            leadership_score=leadership_score,
            activity_score=activity_score,
            honor_score=honor_score,
        )

    @staticmethod
    def _derive_gpa(request: StudentMatchRequest) -> tuple[float, float]:
        if not request.academic.gpa:
            return 0.0, 4.0

        total_value = sum(record.value for record in request.academic.gpa)
        total_scale = sum(record.scale for record in request.academic.gpa)
        average_value = total_value / len(request.academic.gpa)
        average_scale = total_scale / len(request.academic.gpa)
        return average_value, average_scale

    @staticmethod
    def _derive_ielts(request: StudentMatchRequest) -> float:
        ielts_scores = [
            test.score
            for test in request.test_scores.english_tests
            if test.type.strip().lower() == "ielts"
        ]
        if not ielts_scores:
            return 0.0
        return max(ielts_scores)

    @staticmethod
    def _build_profile_text(request: StudentMatchRequest) -> str:
        chunks: list[str] = []

        chunks.extend(activity.description for activity in request.extracurriculars if activity.description)
        chunks.extend(lead.description for lead in request.leadership if lead.description)
        chunks.extend(award.description for award in request.awards if award.description)
        chunks.extend(project.description for project in request.projects if project.description)

        if request.essays.personal_statement and request.essays.personal_statement.content:
            chunks.append(request.essays.personal_statement.content)

        chunks.extend(
            letter.content_summary
            for letter in request.recommendation_letters
            if letter.content_summary
        )

        compact = " ".join(chunks)
        return re.sub(r"\s+", " ", compact).strip()

    @staticmethod
    def _normalize_major(major: str) -> str:
        compact = re.sub(r"\s+", " ", major).strip()
        return compact.title()

    @staticmethod
    def _keyword_score(profile_text: str, keywords: tuple[str, ...]) -> int:
        text = profile_text.lower()
        hits = sum(1 for keyword in keywords if keyword in text)
        return min(5, hits)
