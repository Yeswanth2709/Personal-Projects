"""
Drug Interaction Agent.
Validates drug interactions, allergies, and contraindications.
"""
from typing import Dict, Any
from models import AgentState, Patient
from services.drug_interaction_service import get_drug_interaction_service
from services.audit_service import get_audit_service


class InteractionAgent:
    """Agent for drug interaction validation."""
    
    def __init__(self):
        self.drug_service = get_drug_interaction_service()
        self.audit = get_audit_service()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process drug interaction validation.
        
        Args:
            state: Current agent state with patient data
        
        Returns:
            Updated agent state with interaction results
        """
        if not state.patient:
            state.errors.append("No patient data available for interaction check")
            return state
        
        patient = state.patient
        
        # Validate medications
        if not patient.medications:
            state.add_message("assistant", "No medications to check for interactions.")
            return state
        
        # Run comprehensive validation
        try:
            results = self.drug_service.validate_patient_medications(patient)
            
            state.interaction_results = results["drug_interactions"]
            state.allergy_results = results["allergy_concerns"]
            
            # Store in agent outputs
            state.agent_outputs["interaction_agent"] = results
            
            # Log to audit
            self.audit.log_interaction_check(
                medications=patient.medications,
                interactions_found=results["total_issues"],
                high_severity=results["high_severity_count"],
                patient_id=patient.patient_id
            )
            
            # Generate summary message
            summary = self._generate_summary(results)
            state.add_message("assistant", summary, metadata={"results": results})
            
        except Exception as e:
            error_msg = f"Error checking interactions: {str(e)}"
            state.errors.append(error_msg)
            self.audit.log_error(error_msg, "interaction_check")
        
        return state
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary of interaction results."""
        parts = []
        
        parts.append(f"**Drug Interaction Analysis Complete**\n")
        parts.append(f"Total Issues Found: {results['total_issues']}")
        
        if results['total_issues'] == 0:
            parts.append("\n✅ No significant drug interactions or allergy concerns detected.")
            return "\n".join(parts)
        
        # Severity breakdown
        parts.append(f"\n**Severity Breakdown:**")
        if results['high_severity_count'] > 0:
            parts.append(f"- 🔴 High Severity: {results['high_severity_count']}")
        if results['medium_severity_count'] > 0:
            parts.append(f"- 🟡 Medium Severity: {results['medium_severity_count']}")
        if results['low_severity_count'] > 0:
            parts.append(f"- 🟢 Low Severity: {results['low_severity_count']}")
        
        # Drug interactions
        if results['drug_interactions']:
            parts.append(f"\n**Drug-Drug Interactions ({len(results['drug_interactions'])}):**")
            for interaction in results['drug_interactions'][:5]:  # Show first 5
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(interaction.severity, "⚪")
                parts.append(f"{severity_emoji} {interaction.drug1} + {interaction.drug2}")
                parts.append(f"   Type: {interaction.interaction_type}")
        
        # Allergy concerns
        if results['allergy_concerns']:
            parts.append(f"\n**Allergy Concerns ({len(results['allergy_concerns'])}):**")
            for concern in results['allergy_concerns'][:5]:  # Show first 5
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(concern.severity, "⚪")
                parts.append(f"{severity_emoji} {concern.medication} (Allergy: {concern.allergy})")
        
        parts.append("\n⚠️ **Action Required:** Review detailed results and consult with clinical pharmacist.")
        
        return "\n".join(parts)


def get_interaction_agent() -> InteractionAgent:
    """Get or create Interaction Agent instance."""
    return InteractionAgent()


if __name__ == "__main__":
    # Test the agent
    from models import Patient, AgentState
    
    # Create test patient with interactions
    patient = Patient(
        age=70,
        sex="Female",
        weight=65.0,
        allergies=["Penicillin"],
        medications=["Warfarin", "Aspirin", "Amoxicillin", "Simvastatin", "Clarithromycin"],
        diagnoses=["Atrial Fibrillation", "Hypertension", "Hyperlipidemia"]
    )
    
    # Create agent state
    state = AgentState(patient=patient)
    
    # Process
    agent = InteractionAgent()
    result_state = agent.process(state)
    
    print("Summary:", result_state.messages[-1].content if result_state.messages else "No summary")
    print(f"\nFound {len(result_state.interaction_results)} drug interactions")
    print(f"Found {len(result_state.allergy_results)} allergy concerns")
