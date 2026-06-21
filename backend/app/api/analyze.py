"""/analyze — run the full ML pipeline on a piece of text."""
from __future__ import annotations

from fastapi import APIRouter

from app.ml import crisis_triage, emotion, sentiment
from app.schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter(prefix="/analyze", tags=["analyze"])


def run_pipeline(text: str) -> AnalyzeResponse:
    """Shared pipeline used by /analyze, /mood and /chat."""
    sent = sentiment.analyze(text)
    emo = emotion.classify(text)
    triage = crisis_triage.assess(
        text,
        emotion_label=str(emo["label"]),
        emotion_score=float(emo["score"]),
    )
    return AnalyzeResponse(
        sentiment_label=str(sent["label"]),
        sentiment_score=float(sent["score"]),
        emotion_label=str(emo["label"]),
        emotion_score=float(emo["score"]),
        triage_level=triage.level.value,
        matched_signals=triage.matched_signals,
        resources=triage.resources,
    )


@router.post("", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    return run_pipeline(req.text)
