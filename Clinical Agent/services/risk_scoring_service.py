"""Risk scoring service for adverse reaction prediction."""

from typing import List, Tuple
from models import Patient, InteractionResult, RiskScore


class RiskScoringService:
    """Service for computing patient risk scores."""
    
    # Scoring weights
    BASE_MED_WEIGHT = 5  # Points per medication
    INTERACTION_WEIGHTS = {
        "high": 20,
        "medium": 10,
        "low": 5
    }
    AGE_THRESHOLD = 65
    AGE_PENALTY = 10
    POLYPHARMACY_THRESHOLD = 5
    POLYPHARMACY_PENALTY = 15
    RENAL_PENALTY = 15
    HEPATIC_PENALTY = 10
    PREGNANCY_PENALTY = 12
    
    @staticmethod
    def score_patient(patient: Patient, interactions: List[InteractionResult]) -> RiskScore:
        """
        Calculate risk score for a patient based on multiple factors.
        
        Args:
            patient: Patient context
            interactions: List of detected interactions
            
        Returns:
            RiskScore with numerical score, label, and contributing factors
        """
        score = 0
        factors = []
        
        # Base score from number of medications
        num_meds = len(patient.current_medications)
        if num_meds > 0:
            med_score = num_meds * RiskScoringService.BASE_MED_WEIGHT
            score += med_score
            factors.append(f"Taking {num_meds} medication(s) (+{med_score} points)")
        
        # Polypharmacy penalty
        if num_meds >= RiskScoringService.POLYPHARMACY_THRESHOLD:
            score += RiskScoringService.POLYPHARMACY_PENALTY
            factors.append(f"Polypharmacy (≥{RiskScoringService.POLYPHARMACY_THRESHOLD} meds) (+{RiskScoringService.POLYPHARMACY_PENALTY} points)")
        
        # Age factor
        if patient.age and patient.age >= RiskScoringService.AGE_THRESHOLD:
            score += RiskScoringService.AGE_PENALTY
            factors.append(f"Age ≥{RiskScoringService.AGE_THRESHOLD} years (+{RiskScoringService.AGE_PENALTY} points)")
        
        # Renal impairment
        if patient.renal_impairment:
            score += RiskScoringService.RENAL_PENALTY
            factors.append(f"Renal impairment (+{RiskScoringService.RENAL_PENALTY} points)")
        
        # Hepatic impairment
        if patient.hepatic_impairment:
            score += RiskScoringService.HEPATIC_PENALTY
            factors.append(f"Hepatic impairment (+{RiskScoringService.HEPATIC_PENALTY} points)")
        
        # Pregnancy
        if patient.pregnancy_status:
            score += RiskScoringService.PREGNANCY_PENALTY
            factors.append(f"Pregnancy status (+{RiskScoringService.PREGNANCY_PENALTY} points)")
        
        # Interaction severity scoring
        interaction_counts = {"high": 0, "medium": 0, "low": 0}
        for interaction in interactions:
            severity = interaction.severity
            interaction_counts[severity] += 1
            score += RiskScoringService.INTERACTION_WEIGHTS[severity]
        
        # Add interaction factors
        if interaction_counts["high"] > 0:
            points = interaction_counts["high"] * RiskScoringService.INTERACTION_WEIGHTS["high"]
            factors.append(f"{interaction_counts['high']} high-severity interaction(s) (+{points} points)")
        if interaction_counts["medium"] > 0:
            points = interaction_counts["medium"] * RiskScoringService.INTERACTION_WEIGHTS["medium"]
            factors.append(f"{interaction_counts['medium']} medium-severity interaction(s) (+{points} points)")
        if interaction_counts["low"] > 0:
            points = interaction_counts["low"] * RiskScoringService.INTERACTION_WEIGHTS["low"]
            factors.append(f"{interaction_counts['low']} low-severity interaction(s) (+{points} points)")
        
        # Cap at 100
        score = min(score, 100)
        
        # Determine label
        label = RiskScoringService._get_risk_label(score)
        
        # Add no risk factors message if score is 0
        if score == 0:
            factors.append("No significant risk factors identified")
        
        return RiskScore(
            score=score,
            label=label,
            contributing_factors=factors
        )
    
    @staticmethod
    def _get_risk_label(score: int) -> str:
        """Map numerical score to risk label."""
        if score >= 60:
            return "High"
        elif score >= 30:
            return "Moderate"
        else:
            return "Low"
    
    @staticmethod
    def get_risk_recommendations(risk_score: RiskScore, patient: Patient) -> List[str]:
        """
        Generate recommendations based on risk score.
        
        Args:
            risk_score: Computed risk score
            patient: Patient context
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if risk_score.label == "High":
            recommendations.append("⚠️ HIGH RISK: Urgent clinical review recommended")
            recommendations.append("Consider medication reconciliation with pharmacist")
            recommendations.append("Schedule close follow-up appointments")
        elif risk_score.label == "Moderate":
            recommendations.append("⚠️ MODERATE RISK: Clinical review advised")
            recommendations.append("Monitor for adverse effects closely")
        else:
            recommendations.append("✓ LOW RISK: Continue routine monitoring")
        
        # Specific recommendations
        if patient.renal_impairment:
            recommendations.append("Check renal function and adjust medication doses accordingly")
        
        if patient.hepatic_impairment:
            recommendations.append("Review hepatically-cleared medications")
        
        if len(patient.current_medications) >= RiskScoringService.POLYPHARMACY_THRESHOLD:
            recommendations.append("Consider deprescribing review - can any medications be discontinued?")
        
        if patient.age and patient.age >= RiskScoringService.AGE_THRESHOLD:
            recommendations.append("Apply BEERS criteria for potentially inappropriate medications in elderly")
        
        return recommendations
