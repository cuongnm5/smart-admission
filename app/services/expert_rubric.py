from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.domain.models import RubricConfig


class ExpertRubricService:
    def __init__(self, rubric_file: Path | None = None) -> None:
        self._rubric_file = rubric_file or Path(__file__).resolve().parents[1] / "data" / "expert_rubric_v1.json"

    @lru_cache(maxsize=1)
    def get_rubric(self) -> RubricConfig:
        with self._rubric_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return RubricConfig.model_validate(payload)
