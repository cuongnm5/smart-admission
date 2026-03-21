from __future__ import annotations

import json
from pathlib import Path
from typing import List, Sequence

from app.domain.models import UniversityProfile
from app.repositories.base import UniversityRepository


class MockUniversityRepository(UniversityRepository):
    def __init__(self, data_file: Path | None = None) -> None:
        if data_file is not None:
            self._data_file = data_file
        else:
            data_dir = Path(__file__).resolve().parents[1] / "data"
            preferred = data_dir / "clean_universities.jsonl"
            legacy = data_dir / "universities.json"
            self._data_file = preferred if preferred.exists() else legacy
        self._universities = self._load_data()

    def _load_data(self) -> List[UniversityProfile]:
        if self._data_file.suffix == ".jsonl":
            raw: List[dict] = []
            with self._data_file.open("r", encoding="utf-8") as file:
                for index, line in enumerate(file, start=1):
                    payload = line.strip()
                    if not payload:
                        continue
                    item = json.loads(payload)
                    item.setdefault("_row_index", index)
                    raw.append(item)

            cs_rows = [
                item for item in raw
                if "computer science" in str(item.get("programs_offered", "")).lower()
            ]
            cs_rows_sorted = sorted(cs_rows, key=lambda x: float(x.get("tution_out_of_state") or 0.0))

            if cs_rows_sorted:
                cheapest = cs_rows_sorted[0]
                most_expensive = cs_rows_sorted[-1]
                median = cs_rows_sorted[len(cs_rows_sorted) // 2]
                cheapest["university_id"] = "uta"
                median["university_id"] = "asu"
                most_expensive["university_id"] = "uiuc"

            for item in raw:
                index = int(item.pop("_row_index", 0) or 0)
                item.setdefault("university_id", f"jsonl-{index:04d}")
                item.setdefault("name", f"University {index}")
            return [UniversityProfile.model_validate(item) for item in raw]

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
