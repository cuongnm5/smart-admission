from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field


class MatchingSettings(BaseModel):
    top_k: int = 20
    affordability_reject_ratio: float = Field(default=0.7, ge=0.0, le=1.0)
    affordability_feature_cap: float = 50000.0
    llm_enabled: bool = False


@lru_cache(maxsize=1)
def get_settings() -> MatchingSettings:
    return MatchingSettings()
