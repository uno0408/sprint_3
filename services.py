from typing import List
from schemas import ShotRiskInputs, ShotRiskFinalInput, ShotInput, ShotType, DerivedVariable


class ShotRiskDerivedService:
    """Service for API 3A: Calculate derived variables from shot-level data."""
    
    EPSILON = 0.01
    
    def filter_shots_by_type(self, shots: List[ShotInput], shot_type: ShotType) -> List[ShotInput]:
        """Filter shots by shot type."""
        return [shot for shot in shots if shot.shot_type == shot_type]
    
    def compute_derived_variables(self, inputs: ShotRiskInputs, shot_type: ShotType = ShotType.DRIVING):
        """API 3A: Compute 6 derived variables."""
        total_shots = len(inputs.shots)
        shots_of_type = self.filter_shots_by_type(inputs.shots, shot_type)
        total_shots_of_type = len(shots_of_type)
        
        if total_shots_of_type == 0:
            return {
                "total_shots_count": total_shots,
                "shot_type_analyzed": shot_type.value,
                "shot_type": shot_type.value,
                "shot_frequency": 0.0,
                "expected_runs_per_shot": 0.0,
                "dismissal_probability": 0.0,
                "boundary_probability": 0.0,
                "risk_reward_ratio": 0.0,
                "total_shots_of_type": 0,
                "total_runs_from_type": 0,
                "total_dismissals": 0,
                "total_boundaries": 0,
                "shot_value": 0.0,
                "shot_risk": 0.0,
                "shot_efficiency": 0.0,
                "derived_variables": [],
                "formula_documentation": "No shots of this type found"
            }
        
        # shot_frequency
        shot_frequency = total_shots_of_type / total_shots
        
        # expected_runs_per_shot (SHOT VALUE)
        total_runs = sum(shot.runs_gained for shot in shots_of_type)
        expected_runs = total_runs / total_shots_of_type
        
        # dismissal_probability (SHOT RISK)
        dismissals = sum(1 for shot in shots_of_type if shot.is_dismissal)
        dismissal_prob = dismissals / total_shots_of_type
        
        # boundary_probability
        boundaries = sum(1 for shot in shots_of_type if shot.is_boundary)
        boundary_prob = boundaries / total_shots_of_type
        
        # risk_reward_ratio
        denominator = boundary_prob * expected_runs
        risk_reward = dismissal_prob / denominator if denominator > 0 else 0.0
        
        # shot_efficiency (uses shot_value and shot_risk SEPARATELY)
        shot_value = expected_runs
        shot_risk = dismissal_prob
        shot_efficiency = shot_value / (shot_risk + self.EPSILON)
        
        return {
            "total_shots_count": total_shots,
            "shot_type_analyzed": shot_type.value,
            "shot_type": shot_type.value,
            "shot_frequency": round(shot_frequency, 4),
            "expected_runs_per_shot": round(expected_runs, 4),
            "dismissal_probability": round(dismissal_prob, 4),
            "boundary_probability": round(boundary_prob, 4),
            "risk_reward_ratio": round(risk_reward, 4),
            "total_shots_of_type": total_shots_of_type,
            "total_runs_from_type": total_runs,
            "total_dismissals": dismissals,
            "total_boundaries": boundaries,
            "shot_value": round(shot_value, 4),
            "shot_risk": round(shot_risk, 4),
            "shot_efficiency": round(shot_efficiency, 4),
            "derived_variables": [
                DerivedVariable(name="shot_type", value=1.0, formula="categorical", explanation="Shot category"),
                DerivedVariable(name="shot_frequency", value=round(shot_frequency, 4), formula=f"{total_shots_of_type}/{total_shots}", explanation="Proportion of shots"),
                DerivedVariable(name="expected_runs_per_shot", value=round(expected_runs, 4), formula=f"{total_runs}/{total_shots_of_type}", explanation="SHOT VALUE"),
                DerivedVariable(name="dismissal_probability", value=round(dismissal_prob, 4), formula=f"{dismissals}/{total_shots_of_type}", explanation="SHOT RISK"),
                DerivedVariable(name="boundary_probability", value=round(boundary_prob, 4), formula=f"{boundaries}/{total_shots_of_type}", explanation="Boundary rate"),
                DerivedVariable(name="risk_reward_ratio", value=round(risk_reward, 4), formula="dismissal/(boundary×runs)", explanation="Risk-reward")
            ],
            "formula_documentation": f"Shot Value = {expected_runs:.2f}, Shot Risk = {dismissal_prob:.2f}, Efficiency = {shot_efficiency:.2f}"
        }


class ShotRiskFinalService:
    """Service for API 3B: Calculate final score from derived variables."""
    
    @staticmethod
    def calculate_sre(expected_runs: float, dismissal_prob: float, boundary_prob: float) -> tuple:
        """API 3B: Calculate SRE formula (balances value and risk)."""
        value_component = expected_runs * 10 * 0.5
        risk_component = (1 - dismissal_prob) * 100 * 0.2
        boundary_component = boundary_prob * 25 * 0.3
        sre = value_component + risk_component + boundary_component
        return round(min(100, sre), 2), round(value_component, 2), round(risk_component, 2), round(boundary_component, 2)
    
    @staticmethod
    def get_risk_label(sre: float) -> str:
        """API 3B: Get label based on SRE threshold."""
        if sre >= 80:
            return "Masterful"
        elif sre >= 65:
            return "Strong"
        elif sre >= 50:
            return "Moderate"
        else:
            return "High-Risk"
    
    async def get_shot_risk_efficiency_final(self, inputs: ShotRiskFinalInput):
        """API 3B: Main method to produce final output."""
        # Calculate SRE (balances value and risk)
        sre, value_score, risk_score, boundary_score = self.calculate_sre(
            inputs.expected_runs_per_shot,
            inputs.dismissal_probability,
            inputs.boundary_probability
        )
        
        # Get label
        label = self.get_risk_label(sre)
        
        return {
            "shot_risk_efficiency_score": sre,
            "best_shot_recommendation": f"Your {label} efficiency shows good balance. Expected runs: {inputs.expected_runs_per_shot}, Dismissal: {inputs.dismissal_probability:.1%}, Boundary: {inputs.boundary_probability:.1%}",
            "risk_label": label,
            "derived_variables_used": ["shot_type", "shot_frequency", "expected_runs_per_shot", "dismissal_probability", "boundary_probability", "risk_reward_ratio"],
            "explanation": f"Shot Risk Efficiency Score of {sre} indicates {label} risk level. Player scores {inputs.expected_runs_per_shot} runs per shot with {inputs.dismissal_probability:.1%} dismissal probability and {inputs.boundary_probability:.1%} boundary rate, balancing value and risk effectively.",
            "shot_type_out": inputs.shot_type,
            "expected_runs_per_shot_out": inputs.expected_runs_per_shot,
            "dismissal_probability_out": inputs.dismissal_probability,
            "boundary_probability_out": inputs.boundary_probability,
            "value_component_score": value_score,
            "risk_component_score": risk_score,
            "boundary_component_score": boundary_score,
            "formula_used": "SRE = (expected_runs × 10 × 0.5) + ((1 - dismissal_prob) × 100 × 0.2) + (boundary_prob × 25 × 0.3)",
            "threshold_breakdown": "Masterful: ≥80 | Strong: 65-79 | Moderate: 50-64 | High-Risk: <50",
            "value_risk_balance_note": "Score balances scoring value (50%) with dismissal risk (20%) and boundary aggression (30%)."
        }
