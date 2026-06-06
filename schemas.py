from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class ShotType(str, Enum):
    """Shot type categories."""
    DRIVING = "driving"
    CUTTING = "cutting"
    PULLING = "pulling"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"


# ========================
# API 3A - Input Schema (Derived Variables)
# ========================
class ShotInput(BaseModel):
    """Primary shot-level input for API 3A."""
    shot_id: str = Field(..., description="Unique shot identifier")
    shot_type: ShotType = Field(..., description="Type of shot played")
    runs_gained: int = Field(..., ge=0, le=6, description="Runs scored from this shot")
    is_dismissal: bool = Field(..., description="Whether batter was dismissed on this shot")
    is_boundary: bool = Field(..., description="Whether shot resulted in boundary (4 or 6)")
    ball_outcome: str = Field(..., description="Outcome of the ball")


class ShotRiskInputs(BaseModel):
    """Primary inputs for API 3A: shot-level data."""
    shots: List[ShotInput] = Field(
        ..., 
        description="List of shot-level inputs",
        min_items=5,
        max_items=200
    )


# ========================
# API 3A - Output Schema (Derived Variables)
# ========================
class DerivedVariable(BaseModel):
    """Single derived variable with explanation."""
    name: str
    value: float
    formula: str
    explanation: str


class ShotRiskResponse(BaseModel):
    """Output for API 3A: 6 derived variables."""
    total_shots_count: int
    shot_type_analyzed: str
    shot_type: str = Field(..., description="Shot type category")
    shot_frequency: float = Field(..., description="Frequency of this shot")
    expected_runs_per_shot: float = Field(..., description="Expected runs per shot (shot value)")
    dismissal_probability: float = Field(..., description="Dismissal probability (shot risk)")
    boundary_probability: float = Field(..., description="Boundary probability")
    risk_reward_ratio: float = Field(..., description="Risk-reward ratio")
    total_shots_of_type: int = Field(..., description="Total shots of this type")
    total_runs_from_type: int = Field(..., description="Total runs from this shot type")
    total_dismissals: int = Field(..., description="Total dismissals on this shot type")
    total_boundaries: int = Field(..., description="Total boundaries from this shot type")
    shot_value: float = Field(..., description="Shot value = expected_runs_per_shot")
    shot_risk: float = Field(..., description="Shot risk = dismissal_probability")
    shot_efficiency: float = Field(..., description="Shot efficiency = shot_value / (shot_risk + 0.01)")
    derived_variables: List[DerivedVariable]
    formula_documentation: str = Field(..., description="Complete formula documentation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_shots_count": 50,
                "shot_type_analyzed": "driving",
                "shot_type": "driving",
                "shot_frequency": 0.32,
                "expected_runs_per_shot": 3.44,
                "dismissal_probability": 0.0625,
                "boundary_probability": 0.375,
                "risk_reward_ratio": 0.182,
                "shot_value": 3.44,
                "shot_risk": 0.0625,
                "shot_efficiency": 54.6
            }
        }


# ========================
# API 3B - Input Schema (Final Output)
# ========================
class ShotRiskFinalInput(BaseModel):
    """Primary input for API 3B: derived variables from API 3A."""
    shot_type: str = Field(..., description="Shot type category")
    shot_frequency: float = Field(..., ge=0, le=1, description="Frequency of this shot")
    expected_runs_per_shot: float = Field(..., ge=0, description="Expected runs per shot (shot value)")
    dismissal_probability: float = Field(..., ge=0, le=1, description="Dismissal probability (shot risk)")
    boundary_probability: float = Field(..., ge=0, le=1, description="Boundary probability")
    risk_reward_ratio: float = Field(..., ge=0, description="Risk-reward ratio")


# ========================
# API 3B - Output Schema (Final Output)
# ========================
class ShotRiskFinalResponse(BaseModel):
    """Output for API 3B: Final score + label + recommendation."""
    shot_risk_efficiency_score: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Final Shot Risk Efficiency Score (0-100)"
    )
    best_shot_recommendation: str = Field(..., description="Actionable recommendation")
    risk_label: str = Field(..., description="Masterful/Strong/Moderate/High-Risk")
    derived_variables_used: list[str] = Field(..., description="List of variables used")
    explanation: str = Field(..., description="Contextual explanation")
    shot_type_out: str = Field(..., description="Shot type analyzed")
    expected_runs_per_shot_out: float = Field(..., description="Shot value")
    dismissal_probability_out: float = Field(..., description="Shot risk")
    boundary_probability_out: float = Field(..., description="Boundary probability")
    value_component_score: float = Field(..., description="Scoring value component (50%)")
    risk_component_score: float = Field(..., description="Risk component (20%)")
    boundary_component_score: float = Field(..., description="Boundary component (30%)")
    formula_used: str = Field(..., description="Formula used")
    threshold_breakdown: str = Field(..., description="Label thresholds")
    value_risk_balance_note: str = Field(..., description="Value-risk balance explanation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "shot_risk_efficiency_score": 72.45,
                "best_shot_recommendation": "Your Strong efficiency shows good balance.",
                "risk_label": "Strong",
                "derived_variables_used": ["shot_type", "expected_runs_per_shot", "dismissal_probability", "boundary_probability"],
                "explanation": "Shot Risk Efficiency Score of 72.45 indicates Strong risk level.",
                "shot_type_out": "driving",
                "expected_runs_per_shot_out": 3.44,
                "dismissal_probability_out": 0.0625,
                "boundary_probability_out": 0.375,
                "value_component_score": 34.4,
                "risk_component_score": 18.75,
                "boundary_component_score": 19.29,
                "formula_used": "SRE = (expected_runs × 10 × 0.5) + ((1 - dismissal_prob) × 100 × 0.2) + (boundary_prob × 25 × 0.3)",
                "threshold_breakdown": "Masterful: ≥80 | Strong: 65-79 | Moderate: 50-64 | High-Risk: <50",
                "value_risk_balance_note": "Score balances scoring value (50%) with dismissal risk (20%) and boundary (30%)."
            }
        }
