"""/crisis — standalone safety triage endpoint.

Lets the frontend check arbitrary text (e.g. while typing) and always returns
the canonical crisis resources when escalated.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.ml import crisis_triage
from app.schemas import CrisisCheckRequest, CrisisCheckResponse

router = APIRouter(prefix="/crisis", tags=["crisis"])


@router.post("/check", response_model=CrisisCheckResponse)
def check(req: CrisisCheckRequest) -> CrisisCheckResponse:
    result = crisis_triage.assess(req.text)
    return CrisisCheckResponse(
        level=result.level.value,
        matched_signals=result.matched_signals,
        resources=result.resources,
    )
