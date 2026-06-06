from fastapi import FastAPI, HTTPException, status
from schemas import (
    ShotRiskInputs,
    ShotRiskResponse,
    ShotRiskFinalInput,
    ShotRiskFinalResponse,
    ShotType
)
from services import ShotRiskDerivedService, ShotRiskFinalService

app = FastAPI(
    title="Shot Risk Efficiency API",
    description="API with 2 endpoints: (3A) Derived Variables and (3B) Final Output",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

derived_service = ShotRiskDerivedService()
final_service = ShotRiskFinalService()


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Shot Risk Efficiency API",
        "version": "1.0.0",
        "endpoints": [
            "/api/shot-risk-efficiency (3A - Derived Variables)",
            "/api/shot-risk-efficiency/final (3B - Final Output)"
        ]
    }


# ========================
# API 3A - Derived Variables Endpoint
# ========================
@app.post(
    "/api/shot-risk-efficiency",
    response_model=ShotRiskResponse,
    tags=["Shot Risk Efficiency 3A - Derived Variables"]
)
async def get_shot_risk_efficiency_derived(inputs: ShotRiskInputs):
    """
    API 3A: Convert shot-level inputs into Shot Risk Efficiency derived variables.
    
    **6 Required Output Fields:**
    - shot_type: Shot category
    - shot_frequency: Frequency of this shot
    - expected_runs_per_shot: Shot VALUE
    - dismissal_probability: Shot RISK
    - boundary_probability: Boundary rate
    - risk_reward_ratio: Risk-reward tradeoff
    """
    try:
        result = derived_service.compute_derived_variables(inputs)
        return ShotRiskResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to compute shot risk efficiency", "details": str(e)}
        )


# ========================
# API 3B - Final Output Endpoint
# ========================
@app.post(
    "/api/shot-risk-efficiency/final",
    response_model=ShotRiskFinalResponse,
    tags=["Shot Risk Efficiency 3B - Final Output"]
)
async def get_shot_risk_efficiency_final(inputs: ShotRiskFinalInput):
    """
    API 3B: Produce final Shot Risk Efficiency score from derived variables.
    
    **5 Required Output Fields:**
    - shot_risk_efficiency_score: Final score (0-100)
    - best_shot_recommendation: Actionable advice
    - risk_label: Masterful/Strong/Moderate/High-Risk
    - derived_variables_used: List of variables used
    - explanation: Contextual explanation
    """
    try:
        result = await final_service.get_shot_risk_efficiency_final(inputs)
        return ShotRiskFinalResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to compute Shot Risk Efficiency Score", "details": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
