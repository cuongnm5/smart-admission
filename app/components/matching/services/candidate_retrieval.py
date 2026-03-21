from __future__ import annotations

from typing import Sequence

from app.domain.models import NormalizedStudentProfile, UniversityProfile
from app.repositories.base import UniversityRepository


class CandidateRetrievalService:
    def __init__(self, repository: UniversityRepository) -> None:
        self._repository = repository

    def retrieve(self, student: NormalizedStudentProfile) -> Sequence[UniversityProfile]:
        return self._repository.find_by_major_and_international(student.intended_major)
