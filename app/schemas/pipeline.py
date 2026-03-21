from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.schemas.response import MatchingMeta


class StageOneMatchingOutput(BaseModel):
    top_20_university_ids: List[str]
    meta: MatchingMeta


class StageTwoAnalysisOutput(BaseModel):
    analyzed_university_ids: List[str]
    matched_university_id: Optional[str] = None
    ranking_summary: List[Dict[str, Any]]
    detailed_analysis: Dict[str, Any]


class UniversityPipelineResponse(BaseModel):
    stage_1_matching: StageOneMatchingOutput
    stage_2_analysis: StageTwoAnalysisOutput
