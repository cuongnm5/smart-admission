from typing import List

from pydantic import BaseModel


class MatchingMeta(BaseModel):
    retrieved_count: int
    hard_filter_pass_count: int
    scored_count: int
    returned_count: int
    rubric_version: str


class MatchingResponse(BaseModel):
    top_candidates: List[str]
    meta: MatchingMeta
