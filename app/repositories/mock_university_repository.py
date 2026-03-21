from __future__ import annotations

import json
from pathlib import Path
from typing import List, Sequence

from app.domain.models import UniversityProfile
from app.repositories.base import UniversityRepository


class MockUniversityRepository(UniversityRepository):
    def __init__(self, data_file: Path | None = None) -> None:
        self._data_file = data_file or Path(__file__).resolve().parents[1] / "data" / "universities.json"
        self._universities = self._load_data()

    def _load_data(self) -> List[UniversityProfile]:
        with self._data_file.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        return [UniversityProfile.model_validate(item) for item in raw]

    def list_universities(self) -> Sequence[UniversityProfile]:
        return self._universities

    def find_by_major_and_international(self, intended_major: str) -> Sequence[UniversityProfile]:
        major_key = intended_major.strip().lower()
        return [
            university
            for university in self._universities
            if university.accepts_international_students
            and any(major.strip().lower() == major_key for major in university.majors)
        ]
