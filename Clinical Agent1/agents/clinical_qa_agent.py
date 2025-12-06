"""
Clinical Q&A Agent.
Handles clinical question answering with RAG and guardrails.
"""
from typing import Dict, Any, Optional
from models import AgentState, ChatMessage
from services.llm_service import get_llm_service
from services.rag_service import get_rag_service
from services.guardrails_service import get_guardrails_service
from services.audit_service import get_audit_service
from config import MEDICAL_DISCLAIMER


class ClinicalQAAgent:
    """Agent for answering clinical questions using RAG and LLM."""
    
    def __init__(self):
        self.llm = get_llm_service()
        self.rag = get_rag_service()
        self.guardrails = get_guardrails_service()
        self.audit = get_audit_service()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process a clinical question through the full pipeline.
        
        Pipeline:
        1. Validate and sanitize input (guardrails)
        2. Retrieve relevant context (RAG)
        3. Generate answer (LLM)
        4. Validate output (guardrails)
        5. Add disclaimer
        6. Log to audit
        
        Args:
            state: Current agent state with query
        
        Returns:
            Updated agent state with answer
        """
        query = state.current_query
        
        # Step 1: Validate input
        validation = self.guardrails.validate_input_query(query)
        if not validation["is_valid"]:
            error_msg = f"Invalid query: {', '.join(validation['blocked_reasons'])}"
            state.errors.append(error_msg)
            state.add_message("assistant", error_msg)
            return state
        
        if validation["warnings"]:
            for warning in validation["warnings"]:
                state.errors.append(f"Warning: {warning}")
        
        sanitized_query = validation["sanitized_query"]
        
        # Step 2: Retrieve relevant context
        retrieved_chunks = self.rag.retrieve_relevant_chunks(sanitized_query, top_k=3)
        state.retrieved_context = [chunk["content"] for chunk in retrieved_chunks]
        
        context_text = self.rag.format_context_for_prompt(retrieved_chunks)
        
        # Step 3: Build prompt and generate answer
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(sanitized_query, context_text, state.patient)
        
        try:
            answer = self.llm.generate(user_prompt, system_prompt)
        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            state.errors.append(error_msg)
            state.add_message("assistant", error_msg)
            self.audit.log_error(error_msg, "llm_generation")
            return state
        
        # Step 4: Validate output
        output_validation = self.guardrails.validate_clinical_response(answer)
        if output_validation["warnings"]:
            for warning in output_validation["warnings"]:
                state.errors.append(f"Output warning: {warning}")
        
        # Step 5: Add disclaimer if needed
        if output_validation["requires_disclaimer"]:
            answer = self.guardrails.add_disclaimer_to_response(answer)
        
        # Step 6: Log to audit
        patient_context = state.patient.model_dump() if state.patient else None
        sources = [chunk["source"] for chunk in retrieved_chunks]
        self.audit.log_qa_event(
            question=sanitized_query,
            answer=answer,
            patient_context=patient_context,
            retrieved_docs=sources
        )
        
        # Update state
        state.add_message("assistant", answer, metadata={
            "retrieved_sources": sources,
            "validation_warnings": output_validation["warnings"]
        })
        state.agent_outputs["qa_agent"] = {
            "answer": answer,
            "sources": sources,
            "validation": output_validation
        }
        
        return state
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the LLM."""
        return f"""You are a clinical information assistant helping healthcare professionals.

IMPORTANT GUIDELINES:
- Provide accurate, evidence-based clinical information
- Always recommend consulting qualified healthcare professionals for medical decisions
- Include appropriate medical disclaimers in your responses
- Do NOT provide definitive diagnoses or treatment prescriptions
- Acknowledge uncertainty when information is limited
- Base answers on provided context when available
- Use professional medical terminology but explain complex concepts

{MEDICAL_DISCLAIMER}
"""
    
    def _build_user_prompt(self, query: str, context: str, patient: Optional[Any]) -> str:
        """Build user prompt with query, context, and patient information."""
        prompt_parts = []
        
        # Add patient context if available
        if patient:
            prompt_parts.append(f"""PATIENT CONTEXT:
- Age: {patient.age} years, Sex: {patient.sex}
- Allergies: {', '.join(patient.allergies) if patient.allergies else 'None documented'}
- Current Diagnoses: {', '.join(patient.diagnoses) if patient.diagnoses else 'None documented'}
- Current Medications: {', '.join(patient.medications) if patient.medications else 'None'}
- Renal Impairment: {'Yes' if patient.renal_impairment else 'No'}
- Hepatic Impairment: {'Yes' if patient.hepatic_impairment else 'No'}
""")
        
        # Add retrieved context
        if context and "No relevant information" not in context:
            prompt_parts.append(f"""RELEVANT CLINICAL INFORMATION:
{context}
""")
        
        # Add the question
        prompt_parts.append(f"""CLINICAL QUESTION:
{query}

Please provide a comprehensive answer based on the information above. Remember to include appropriate disclaimers and recommendations to consult healthcare professionals.""")
        
        return "\n\n".join(prompt_parts)
    
    def stream_answer(self, state: AgentState):
        """
        Stream answer generation for real-time UI updates.
        
        Args:
            state: Agent state
        
        Yields:
            Chunks of generated text
        """
        query = state.current_query
        
        # Validate and retrieve (same as process)
        validation = self.guardrails.validate_input_query(query)
        if not validation["is_valid"]:
            yield f"Invalid query: {', '.join(validation['blocked_reasons'])}"
            return
        
        sanitized_query = validation["sanitized_query"]
        retrieved_chunks = self.rag.retrieve_relevant_chunks(sanitized_query, top_k=3)
        context_text = self.rag.format_context_for_prompt(retrieved_chunks)
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(sanitized_query, context_text, state.patient)
        
        # Add disclaimer first
        yield MEDICAL_DISCLAIMER + "\n\n"
        
        # Stream answer
        try:
            for chunk in self.llm.generate_stream(user_prompt, system_prompt):
                yield chunk
        except Exception as e:
            yield f"\n\nError: {str(e)}"


def get_clinical_qa_agent() -> ClinicalQAAgent:
    """Get or create Clinical Q&A Agent instance."""
    return ClinicalQAAgent()


if __name__ == "__main__":
    # Test the agent
    from models import Patient, AgentState
    
    # Create test patient
    patient = Patient(
        age=65,
        sex="Male",
        weight=80.0,
        allergies=["Penicillin"],
        medications=["Metformin", "Lisinopril"],
        diagnoses=["Type 2 Diabetes", "Hypertension"]
    )
    
    # Create agent state
    state = AgentState(patient=patient)
    state.current_query = "What are the side effects of metformin?"
    
    # Process query
    agent = ClinicalQAAgent()
    result_state = agent.process(state)
    
    print("Query:", state.current_query)
    print("\nAnswer:", result_state.messages[-1].content if result_state.messages else "No answer")
    print("\nErrors:", result_state.errors)
