"""
Risk assessment and prediction service.
Implements simple ML-based or rule-based risk scoring for adverse reactions.
"""
from typing import Dict, Any, List
import numpy as np
from sklearn.preprocessing import StandardScaler
from models import Patient, RiskScore, InteractionResult


class RiskModelService:
    """Service for assessing patient risk scores."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        # Pre-fitted with reasonable defaults for demo
        self.scaler.mean_ = np.array([50, 70, 0.5, 2, 0.1, 0.1])
        self.scaler.scale_ = np.array([20, 20, 0.5, 2, 0.3, 0.3])
        
        # Weights for risk factors (can be replaced with trained model)
        self.weights = {
            'age': 0.15,
            'weight': -0.05,
            'num_medications': 0.20,
            'num_conditions': 0.15,
            'renal_impairment': 0.25,
            'hepatic_impairment': 0.20,
            'high_severity_interactions': 0.40,
            'medium_severity_interactions': 0.20,
            'allergy_concerns': 0.30
        }
    
    def calculate_patient_risk_features(self, patient: Patient, 
                                       interaction_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract risk features from patient data.
        
        Args:
            patient: Patient object
            interaction_results: Results from drug interaction service
        
        Returns:
            Dictionary of risk features
        """
        features = {
            'age': float(patient.age),
            'weight': float(patient.weight) if patient.weight else 70.0,
            'num_medications': float(len(patient.medications)),
            'num_conditions': float(len(patient.diagnoses)),
            'renal_impairment': 1.0 if patient.renal_impairment else 0.0,
            'hepatic_impairment': 1.0 if patient.hepatic_impairment else 0.0,
            'high_severity_interactions': float(interaction_results.get('high_severity_count', 0)),
            'medium_severity_interactions': float(interaction_results.get('medium_severity_count', 0)),
            'allergy_concerns': float(len(interaction_results.get('allergy_concerns', [])))
        }
        
        return features
    
    def calculate_risk_score(self, patient: Patient, 
                            interaction_results: Dict[str, Any] = None) -> RiskScore:
        """
        Calculate overall risk score for patient.
        
        Args:
            patient: Patient object
            interaction_results: Optional interaction validation results
        
        Returns:
            RiskScore object with score and contributing factors
        """
        if interaction_results is None:
            interaction_results = {
                'high_severity_count': 0,
                'medium_severity_count': 0,
                'allergy_concerns': []
            }
        
        # Extract features
        features = self.calculate_patient_risk_features(patient, interaction_results)
        
        # Calculate weighted risk score
        risk_score = 0.0
        contributing_factors = []
        
        # Age risk
        if features['age'] > 65:
            age_risk = min((features['age'] - 65) / 35 * 100, 30)  # Max 30 points
            risk_score += age_risk * self.weights['age']
            if age_risk > 10:
                contributing_factors.append({
                    'factor': 'Advanced Age',
                    'value': f"{features['age']:.0f} years",
                    'impact': 'high' if age_risk > 20 else 'medium',
                    'contribution': age_risk * self.weights['age']
                })
        
        # Polypharmacy risk
        if features['num_medications'] >= 5:
            poly_risk = min(features['num_medications'] * 10, 50)  # Max 50 points
            risk_score += poly_risk * self.weights['num_medications']
            contributing_factors.append({
                'factor': 'Polypharmacy',
                'value': f"{features['num_medications']:.0f} medications",
                'impact': 'high' if features['num_medications'] >= 10 else 'medium',
                'contribution': poly_risk * self.weights['num_medications']
            })
        
        # Organ impairment
        if features['renal_impairment'] > 0:
            renal_risk = 40.0
            risk_score += renal_risk * self.weights['renal_impairment']
            contributing_factors.append({
                'factor': 'Renal Impairment',
                'value': 'Present',
                'impact': 'high',
                'contribution': renal_risk * self.weights['renal_impairment']
            })
        
        if features['hepatic_impairment'] > 0:
            hepatic_risk = 35.0
            risk_score += hepatic_risk * self.weights['hepatic_impairment']
            contributing_factors.append({
                'factor': 'Hepatic Impairment',
                'value': 'Present',
                'impact': 'high',
                'contribution': hepatic_risk * self.weights['hepatic_impairment']
            })
        
        # Drug interactions
        if features['high_severity_interactions'] > 0:
            interaction_risk = min(features['high_severity_interactions'] * 30, 60)
            risk_score += interaction_risk * self.weights['high_severity_interactions']
            contributing_factors.append({
                'factor': 'High Severity Drug Interactions',
                'value': f"{features['high_severity_interactions']:.0f} interactions",
                'impact': 'high',
                'contribution': interaction_risk * self.weights['high_severity_interactions']
            })
        
        if features['medium_severity_interactions'] > 0:
            interaction_risk = min(features['medium_severity_interactions'] * 15, 30)
            risk_score += interaction_risk * self.weights['medium_severity_interactions']
            contributing_factors.append({
                'factor': 'Medium Severity Drug Interactions',
                'value': f"{features['medium_severity_interactions']:.0f} interactions",
                'impact': 'medium',
                'contribution': interaction_risk * self.weights['medium_severity_interactions']
            })
        
        # Allergy concerns
        if features['allergy_concerns'] > 0:
            allergy_risk = min(features['allergy_concerns'] * 25, 50)
            risk_score += allergy_risk * self.weights['allergy_concerns']
            contributing_factors.append({
                'factor': 'Allergy/Cross-Sensitivity Concerns',
                'value': f"{features['allergy_concerns']:.0f} concerns",
                'impact': 'high',
                'contribution': allergy_risk * self.weights['allergy_concerns']
            })
        
        # Normalize to 0-100
        risk_score = min(risk_score, 100.0)
        
        # Determine risk level
        if risk_score < 30:
            risk_level = "Low"
        elif risk_score < 70:
            risk_level = "Moderate"
        else:
            risk_level = "High"
        
        # Sort contributing factors by contribution
        contributing_factors.sort(key=lambda x: x['contribution'], reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, contributing_factors, patient)
        
        return RiskScore(
            overall_score=risk_score,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, risk_level: str, 
                                 factors: List[Dict[str, Any]], 
                                 patient: Patient) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if risk_level == "High":
            recommendations.append("⚠️ HIGH RISK: Immediate clinical review recommended")
            recommendations.append("Consider specialist consultation for medication optimization")
        
        # Specific recommendations based on factors
        factor_types = [f['factor'] for f in factors]
        
        if any('Drug Interaction' in f for f in factor_types):
            recommendations.append("Review all drug interactions with pharmacist")
            recommendations.append("Consider medication reconciliation and deprescribing where appropriate")
        
        if 'Polypharmacy' in factor_types:
            recommendations.append("Conduct comprehensive medication review")
            recommendations.append("Assess for potentially inappropriate medications (PIMs)")
        
        if 'Renal Impairment' in factor_types:
            recommendations.append("Verify all medication doses are adjusted for renal function")
            recommendations.append("Monitor renal function regularly")
        
        if 'Hepatic Impairment' in factor_types:
            recommendations.append("Verify hepatic dosing adjustments")
            recommendations.append("Monitor liver function tests")
        
        if 'Allergy' in ' '.join(factor_types):
            recommendations.append("Verify allergy documentation and cross-sensitivities")
            recommendations.append("Ensure allergy alerts are active in all systems")
        
        if patient.age > 75:
            recommendations.append("Apply geriatric prescribing principles (start low, go slow)")
            recommendations.append("Consider functional status and frailty in medication decisions")
        
        # General recommendations
        if risk_level in ["Moderate", "High"]:
            recommendations.append("Increase monitoring frequency for adverse effects")
            recommendations.append("Educate patient/caregiver on warning signs to report")
        
        return recommendations


# Singleton instance
_risk_service_instance = None


def get_risk_model_service() -> RiskModelService:
    """Get or create the risk model service singleton."""
    global _risk_service_instance
    if _risk_service_instance is None:
        _risk_service_instance = RiskModelService()
    return _risk_service_instance


if __name__ == "__main__":
    # Test the service
    from models import Patient
    
    service = RiskModelService()
    
    # Test patient
    patient = Patient(
        age=78,
        sex="Female",
        weight=65.0,
        allergies=["Penicillin"],
        medications=["Warfarin", "Aspirin", "Metformin", "Lisinopril", "Atorvastatin", "Furosemide"],
        diagnoses=["Atrial Fibrillation", "Heart Failure", "Type 2 Diabetes"],
        renal_impairment=True
    )
    
    # Mock interaction results
    interaction_results = {
        'high_severity_count': 2,
        'medium_severity_count': 1,
        'allergy_concerns': [{"medication": "Amoxicillin"}]
    }
    
    risk_score = service.calculate_risk_score(patient, interaction_results)
    
    print(f"Risk Score: {risk_score.overall_score:.1f}")
    print(f"Risk Level: {risk_score.risk_level}")
    print(f"\nTop Contributing Factors:")
    for factor in risk_score.contributing_factors[:5]:
        print(f"  - {factor['factor']}: {factor['value']} (Impact: {factor['impact']})")
    print(f"\nRecommendations:")
    for rec in risk_score.recommendations:
        print(f"  • {rec}")
