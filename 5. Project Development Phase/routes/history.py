import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import RecommendationHistory
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
def get_history(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == user.id)
        .order_by(RecommendationHistory.id.desc())
        .all()
    )

    result = []

    for record in records:
        try:
            request_data = json.loads(record.request_json)
        except Exception:
            request_data = {}

        try:
            response_data = json.loads(record.response_json)
        except Exception:
            response_data = {}

        result.append({
            "id": record.id,
            "planner": record.planner,
            "created_at": record.created_at.isoformat()
            if record.created_at else None,
            "request": request_data,
            "response": response_data,
        })

    return result


@router.get("/session-info")
def history_session_info(
    user=Depends(get_current_user),
):
    return {
        "username": user.username,
        "session_active": True,
    }


@router.get("/recommendation-details/{recommendation_id}")
def get_recommendation_details(
    recommendation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recommendation = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.id == recommendation_id,
            RecommendationHistory.user_id == user.id,
        )
        .first()
    )

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    try:
        input_data = json.loads(recommendation.request_json)
    except Exception:
        input_data = {}

    try:
        result_data = json.loads(recommendation.response_json)
    except Exception:
        result_data = {}

    return {
        "id": recommendation.id,
        "planner": recommendation.planner,
        "input": input_data,
        "result": result_data,
    }