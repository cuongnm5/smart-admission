from __future__ import annotations

from app.schemas.request import StudentMatchRequest
from app.schemas.response import MatchingResponse
from app.components.matching.services.matching_service import MatchingService


class MatchingComponent:
    def __init__(self, matching_service: MatchingService) -> None:
        self._matching_service = matching_service

    def run(self, request: StudentMatchRequest) -> MatchingResponse:
        return self._matching_service.match(request)
