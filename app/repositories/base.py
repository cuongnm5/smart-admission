from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.models import UniversityProfile


class UniversityRepository(ABC):
    @abstractmethod
    def list_universities(self) -> Sequence[UniversityProfile]:
        raise NotImplementedError

    @abstractmethod
    def find_by_major_and_international(self, intended_major: str) -> Sequence[UniversityProfile]:
        raise NotImplementedError
