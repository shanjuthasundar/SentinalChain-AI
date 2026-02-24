from fastapi import APIRouter

from app.models.schemas import FraudEvaluationRequest, FraudEvaluationResponse
from app.services.fraud_engine import FraudEngine


router = APIRouter()
engine = FraudEngine()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "SentinelChain AI", "model_ready": True}


@router.get("/network/summary")
def network_summary() -> dict:
    return engine.network_summary()


@router.post("/fraud/evaluate", response_model=FraudEvaluationResponse)
def evaluate_fraud(payload: FraudEvaluationRequest) -> FraudEvaluationResponse:
    result = engine.evaluate(payload)
    return FraudEvaluationResponse(**result)


@router.post("/fraud/simulate")
def simulate() -> dict:
    return {"samples": [engine.random_assessment() for _ in range(5)]}
