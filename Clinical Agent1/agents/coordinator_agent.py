"""
Coordinator Agent - Multi-agent orchestration.
Routes requests to appropriate agents and manages workflow.
"""
from typing import Dict, Any, Literal
from models import AgentState
from agents.clinical_qa_agent import get_clinical_qa_agent
from agents.interaction_agent import get_interaction_agent
from agents.risk_agent import get_risk_agent


class CoordinatorAgent:
    """
    Coordinator agent that orchestrates multiple specialized agents.
    Routes queries and manages agent execution flow.
    """
    
    def __init__(self):
        self.qa_agent = get_clinical_qa_agent()
        self.interaction_agent = get_interaction_agent()
        self.risk_agent = get_risk_agent()
    
    def route_intent(self, query: str) -> Literal["qa", "interaction", "risk", "comprehensive"]:
        """
        Determine user intent from query.
        
        Args:
            query: User's query or request
        
        Returns:
            Intent type
        """
        query_lower = query.lower()
        
        # Interaction check keywords
        interaction_keywords = [
            "interaction", "drug interaction", "check medications", 
            "allergy", "contraindication", "compatibility"
        ]
        if any(keyword in query_lower for keyword in interaction_keywords):
            return "interaction"
        
        # Risk assessment keywords
        risk_keywords = [
            "risk", "risk score", "adverse", "safety", 
            "risk assessment", "how safe"
        ]
        if any(keyword in query_lower for keyword in risk_keywords):
            return "risk"
        
        # Comprehensive analysis keywords
        comprehensive_keywords = [
            "full analysis", "complete assessment", "evaluate everything",
            "comprehensive", "full review"
        ]
        if any(keyword in query_lower for keyword in comprehensive_keywords):
            return "comprehensive"
        
        # Default to Q&A
        return "qa"
    
    def process(self, state: AgentState, intent: str = None) -> AgentState:
        """
        Process request through appropriate agent(s).
        
        Args:
            state: Agent state with query and patient data
            intent: Optional explicit intent, otherwise auto-detected
        
        Returns:
            Updated agent state
        """
        # Determine intent if not provided
        if intent is None and state.current_query:
            intent = self.route_intent(state.current_query)
        
        # Execute appropriate workflow
        if intent == "qa":
            state = self.qa_agent.process(state)
        
        elif intent == "interaction":
            state = self.interaction_agent.process(state)
        
        elif intent == "risk":
            # Risk assessment needs interaction results first
            state = self.interaction_agent.process(state)
            state = self.risk_agent.process(state)
        
        elif intent == "comprehensive":
            # Full analysis: Q&A + Interactions + Risk
            if state.current_query:
                state = self.qa_agent.process(state)
            state = self.interaction_agent.process(state)
            state = self.risk_agent.process(state)
        
        return state
    
    def process_qa_only(self, state: AgentState) -> AgentState:
        """Process Q&A request only."""
        return self.qa_agent.process(state)
    
    def process_interaction_check(self, state: AgentState) -> AgentState:
        """Process interaction check only."""
        return self.interaction_agent.process(state)
    
    def process_risk_assessment(self, state: AgentState) -> AgentState:
        """Process risk assessment (includes interaction check)."""
        state = self.interaction_agent.process(state)
        state = self.risk_agent.process(state)
        return state
    
    def process_comprehensive(self, state: AgentState) -> AgentState:
        """
        Process comprehensive analysis.
        Runs all agents in sequence.
        """
        # Run interaction check first (needed for risk)
        state = self.interaction_agent.process(state)
        
        # Then risk assessment
        state = self.risk_agent.process(state)
        
        # Q&A if there's a query
        if state.current_query:
            state = self.qa_agent.process(state)
        
        return state


# Singleton instance
_coordinator_instance = None


def get_coordinator_agent() -> CoordinatorAgent:
    """Get or create Coordinator Agent instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = CoordinatorAgent()
    return _coordinator_instance


if __name__ == "__main__":
    # Test the coordinator
    from models import Patient, AgentState
    
    # Create test patient
    patient = Patient(
        age=65,
        sex="Male",
        weight=80.0,
        allergies=["Penicillin"],
        medications=["Warfarin", "Aspirin", "Metformin"],
        diagnoses=["Atrial Fibrillation", "Type 2 Diabetes"]
    )
    
    coordinator = CoordinatorAgent()
    
    # Test intent routing
    print("Intent routing tests:")
    print(f"'What is aspirin?' -> {coordinator.route_intent('What is aspirin?')}")
    print(f"'Check drug interactions' -> {coordinator.route_intent('Check drug interactions')}")
    print(f"'What is my risk score?' -> {coordinator.route_intent('What is my risk score?')}")
    print(f"'Full analysis' -> {coordinator.route_intent('Full analysis')}")
    
    # Test Q&A processing
    print("\n\nTesting Q&A:")
    state = AgentState(patient=patient)
    state.current_query = "What are the side effects of warfarin?"
    result = coordinator.process(state, intent="qa")
    print(f"Messages: {len(result.messages)}")
    
    # Test comprehensive analysis
    print("\n\nTesting comprehensive analysis:")
    state = AgentState(patient=patient)
    state.current_query = "Provide full analysis of my medications"
    result = coordinator.process_comprehensive(state)
    print(f"Messages: {len(result.messages)}")
    print(f"Has interaction results: {len(result.interaction_results) > 0}")
    print(f"Has risk score: {result.risk_score is not None}")
