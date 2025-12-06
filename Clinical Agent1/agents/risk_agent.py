"""
Risk Assessment Agent.
Calculates patient risk scores and provides recommendations.
"""
from typing import Dict, Any
from models import AgentState
from services.risk_model_service import get_risk_model_service
from services.audit_service import get_audit_service


class RiskAgent:
    """Agent for patient risk assessment."""
    
    def __init__(self):
        self.risk_service = get_risk_model_service()
        self.audit = get_audit_service()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process risk assessment.
        
        Args:
            state: Current agent state with patient data
        
        Returns:
            Updated agent state with risk score
        """
        if not state.patient:
            state.errors.append("No patient data available for risk assessment")
            return state
        
        patient = state.patient
        
        # Get interaction results if available
        interaction_results = state.agent_outputs.get("interaction_agent", {})
        
        # Calculate risk
        try:
            risk_score = self.risk_service.calculate_risk_score(patient, interaction_results)
            state.risk_score = risk_score
            
            # Store in agent outputs
            state.agent_outputs["risk_agent"] = {
                "risk_score": risk_score.overall_score,
                "risk_level": risk_score.risk_level,
                "contributing_factors": risk_score.contributing_factors,
                "recommendations": risk_score.recommendations
            }
            
            # Log to audit
            self.audit.log_risk_assessment(
                risk_score=risk_score.overall_score,
                risk_level=risk_score.risk_level,
                patient_id=patient.patient_id,
                contributing_factors=risk_score.contributing_factors
            )
            
            # Generate summary message
            summary = self._generate_summary(risk_score)
            state.add_message("assistant", summary, metadata={"risk_score": risk_score.model_dump()})
            
        except Exception as e:
            error_msg = f"Error calculating risk: {str(e)}"
            state.errors.append(error_msg)
            self.audit.log_error(error_msg, "risk_assessment")
        
        return state
    
    def _generate_summary(self, risk_score) -> str:
        """Generate human-readable summary of risk assessment."""
        parts = []
        
        parts.append(f"**Risk Assessment Complete**\n")
        parts.append(f"Overall Risk Score: **{risk_score.overall_score:.1f}/100**")
        parts.append(f"Risk Level: **{risk_score.risk_level}**")
        
        # Risk level indicator
        if risk_score.risk_level == "Low":
            parts.append("\n🟢 Low risk - Standard monitoring appropriate")
        elif risk_score.risk_level == "Moderate":
            parts.append("\n🟡 Moderate risk - Enhanced monitoring recommended")
        else:
            parts.append("\n🔴 High risk - Immediate review and intervention may be needed")
        
        # Top contributing factors
        if risk_score.contributing_factors:
            parts.append(f"\n**Top Contributing Factors:**")
            for i, factor in enumerate(risk_score.contributing_factors[:5], 1):
                impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(factor['impact'], "⚪")
                parts.append(f"{i}. {impact_emoji} {factor['factor']}: {factor['value']}")
        
        # Key recommendations
        if risk_score.recommendations:
            parts.append(f"\n**Key Recommendations:**")
            for i, rec in enumerate(risk_score.recommendations[:5], 1):
                parts.append(f"{i}. {rec}")
        
        return "\n".join(parts)


def get_risk_agent() -> RiskAgent:
    """Get or create Risk Agent instance."""
    return RiskAgent()


if __name__ == "__main__":
    # Test the agent
    from models import Patient, AgentState
    
    # Create test patient
    patient = Patient(
        age=78,
        sex="Female",
        weight=65.0,
        allergies=["Penicillin", "Sulfa"],
        medications=["Warfarin", "Aspirin", "Metformin", "Lisinopril", "Atorvastatin", "Furosemide"],
        diagnoses=["Atrial Fibrillation", "Heart Failure", "Type 2 Diabetes", "Hypertension"],
        renal_impairment=True,
        hepatic_impairment=False
    )
    
    # Create agent state with mock interaction results
    state = AgentState(patient=patient)
    state.agent_outputs["interaction_agent"] = {
        "high_severity_count": 2,
        "medium_severity_count": 1,
        "low_severity_count": 0,
        "allergy_concerns": [{"medication": "Amoxicillin"}]
    }
    
    # Process
    agent = RiskAgent()
    result_state = agent.process(state)
    
    print("Summary:", result_state.messages[-1].content if result_state.messages else "No summary")
    if result_state.risk_score:
        print(f"\nRisk Score: {result_state.risk_score.overall_score:.1f}")
        print(f"Risk Level: {result_state.risk_score.risk_level}")
