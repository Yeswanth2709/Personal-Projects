"""LLM service for clinical question answering."""

import os
from typing import List, Optional
from models import Patient, InteractionResult
from config import Config


class ClinicalLLMService:
    """Service for answering clinical questions using LLM or rule-based responses."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.use_external = Config.USE_EXTERNAL_LLM
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.LLM_MODEL
        
        if self.use_external and self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Falling back to stub responses.")
                self.use_external = False
        else:
            self.use_external = False
    
    def answer_question(self, patient: Optional[Patient], question: str) -> str:
        """
        Answer a clinical question with patient context.
        
        Args:
            patient: Patient context (optional)
            question: Clinical question text
            
        Returns:
            Formatted answer with disclaimer
        """
        if self.use_external:
            return self._answer_with_llm(patient, question)
        else:
            return self._answer_with_stub(patient, question)
    
    def _answer_with_llm(self, patient: Optional[Patient], question: str) -> str:
        """Answer using external LLM API."""
        try:
            # Build system prompt
            system_prompt = """You are a clinical decision support assistant. Provide evidence-based, 
            concise answers to clinical questions. Always structure your response with:
            1. A brief summary (2-3 sentences)
            2. Key recommendations as bullet points
            3. A reminder that this is for educational purposes only
            
            Keep responses professional and cite general medical knowledge."""
            
            # Build user prompt with patient context
            user_prompt = f"Question: {question}\n\n"
            if patient:
                context = patient.get_summary()
                if context != "No patient data":
                    user_prompt += f"Patient Context: {context}\n\n"
            
            user_prompt += "Please provide a concise, evidence-based response."
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Add disclaimer
            return self._format_response(answer)
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return self._answer_with_stub(patient, question)
    
    def _answer_with_stub(self, patient: Optional[Patient], question: str) -> str:
        """Answer using rule-based stub responses."""
        # Analyze question for keywords
        q_lower = question.lower()
        
        # Generate response based on keywords
        if any(word in q_lower for word in ["warfarin", "coumadin", "anticoagulant", "inr"]):
            answer = self._get_warfarin_response()
        elif any(word in q_lower for word in ["diabetes", "metformin", "blood sugar", "glucose"]):
            answer = self._get_diabetes_response()
        elif any(word in q_lower for word in ["hypertension", "blood pressure", "bp"]):
            answer = self._get_hypertension_response()
        elif any(word in q_lower for word in ["pain", "analgesic", "nsaid"]):
            answer = self._get_pain_management_response()
        elif any(word in q_lower for word in ["antibiotic", "infection"]):
            answer = self._get_antibiotic_response()
        else:
            answer = self._get_general_response(question)
        
        # Add patient-specific notes if available
        if patient:
            answer += self._add_patient_considerations(patient)
        
        return self._format_response(answer)
    
    def _format_response(self, answer: str) -> str:
        """Format response with disclaimer."""
        disclaimer = "\n\n---\n\n⚠️ **DEMO DISCLAIMER**: This is a demonstration response for educational purposes only. This is NOT medical advice. All clinical decisions must be made by qualified healthcare professionals based on complete patient assessment.\n"
        return answer + disclaimer
    
    def _get_warfarin_response(self) -> str:
        """Response for warfarin-related questions."""
        return """**Warfarin Management Summary:**

Warfarin is a vitamin K antagonist requiring careful monitoring and dose adjustment.

**Key Recommendations:**
• Monitor INR regularly (target range typically 2.0-3.0 for most indications)
• Check for drug interactions - many medications affect warfarin levels
• Counsel on consistent vitamin K intake
• Watch for bleeding signs (bruising, blood in stool/urine, etc.)
• Bridging may be needed for procedures

**Important Interactions:**
NSAIDs, antibiotics, and many other drugs can significantly affect INR."""
    
    def _get_diabetes_response(self) -> str:
        """Response for diabetes-related questions."""
        return """**Diabetes Management Summary:**

Type 2 diabetes management focuses on glycemic control and cardiovascular risk reduction.

**Key Recommendations:**
• Target HbA1c typically <7% (individualize based on patient)
• Metformin is first-line unless contraindicated
• Monitor renal function before initiating/continuing metformin
• Screen for and manage cardiovascular risk factors
• Patient education on diet, exercise, and glucose monitoring

**Medication Considerations:**
Consider SGLT2 inhibitors or GLP-1 agonists for patients with cardiovascular disease."""
    
    def _get_hypertension_response(self) -> str:
        """Response for hypertension-related questions."""
        return """**Hypertension Management Summary:**

Blood pressure control reduces cardiovascular events and end-organ damage.

**Key Recommendations:**
• Target BP typically <130/80 mmHg (individualize based on comorbidities)
• First-line agents: ACE-I/ARB, CCB, or thiazide diuretic
• Lifestyle modifications are essential (diet, exercise, weight loss)
• Monitor electrolytes, renal function
• Screen for secondary causes if resistant hypertension

**Monitoring:**
Home BP monitoring can help assess control and white coat effect."""
    
    def _get_pain_management_response(self) -> str:
        """Response for pain management questions."""
        return """**Pain Management Summary:**

Multimodal approach to pain control with consideration of risks and benefits.

**Key Recommendations:**
• Start with acetaminophen for mild-moderate pain
• NSAIDs effective but have GI, renal, and CV risks
• Avoid NSAIDs in elderly, renal impairment, heart failure
• Consider topical agents for localized pain
• Opioids reserved for severe pain with careful monitoring

**Safety Considerations:**
Always check for contraindications and drug interactions before prescribing."""
    
    def _get_antibiotic_response(self) -> str:
        """Response for antibiotic questions."""
        return """**Antibiotic Use Summary:**

Appropriate antibiotic selection requires consideration of infection type, resistance patterns, and patient factors.

**Key Recommendations:**
• Narrow spectrum when possible to reduce resistance
• Check allergies before prescribing
• Consider local resistance patterns (antibiogram)
• Adjust for renal/hepatic impairment
• Complete prescribed course for most infections

**Stewardship:**
Avoid antibiotics for viral infections. Culture before treatment when appropriate."""
    
    def _get_general_response(self, question: str) -> str:
        """General response for unrecognized questions."""
        return f"""**Clinical Question Analysis:**

Thank you for your question: "{question}"

**General Approach:**
• Review current evidence-based guidelines
• Consider patient-specific factors (age, comorbidities, medications)
• Assess benefits vs. risks
• Involve patient in shared decision-making
• Document clinical reasoning

**Recommendations:**
For specific clinical scenarios, consult:
• Relevant specialty guidelines
• Pharmacist for medication questions
• Literature databases (PubMed, UpToDate, etc.)
• Specialist consultation when appropriate"""
    
    def _add_patient_considerations(self, patient: Patient) -> str:
        """Add patient-specific considerations to response."""
        notes = "\n\n**Patient-Specific Considerations:**"
        considerations = []
        
        if patient.age and patient.age >= 65:
            considerations.append("Elderly patient - consider dose adjustments and fall risk")
        
        if patient.renal_impairment:
            considerations.append("Renal impairment - verify dosing adjustments needed")
        
        if patient.hepatic_impairment:
            considerations.append("Hepatic impairment - check for metabolism concerns")
        
        if patient.pregnancy_status:
            considerations.append("Pregnancy - verify medication safety category")
        
        if len(patient.current_medications) >= 5:
            considerations.append("Polypharmacy - review for potential interactions and deprescribing")
        
        if patient.allergies:
            considerations.append(f"Known allergies: {', '.join(patient.allergies)}")
        
        if considerations:
            for note in considerations:
                notes += f"\n• {note}"
            return notes
        
        return ""
    
    def summarize_interactions(self, patient: Patient, interactions: List[InteractionResult]) -> str:
        """
        Generate a natural language summary of drug interactions.
        
        Args:
            patient: Patient context
            interactions: List of detected interactions
            
        Returns:
            Formatted summary text
        """
        if not interactions:
            return "No significant drug interactions detected based on the current medication list."
        
        # Count by severity
        high = sum(1 for i in interactions if i.severity == "high")
        medium = sum(1 for i in interactions if i.severity == "medium")
        low = sum(1 for i in interactions if i.severity == "low")
        
        summary = f"**Interaction Check Summary for {patient.patient_id or 'Patient'}:**\n\n"
        summary += f"Found {len(interactions)} potential interaction(s):\n"
        
        if high > 0:
            summary += f"• {high} HIGH severity (requires immediate attention)\n"
        if medium > 0:
            summary += f"• {medium} MEDIUM severity (clinical monitoring needed)\n"
        if low > 0:
            summary += f"• {low} LOW severity (awareness recommended)\n"
        
        summary += "\n**Priority Actions:**\n"
        
        # High severity interactions first
        high_interactions = [i for i in interactions if i.severity == "high"]
        if high_interactions:
            summary += "\n🔴 **HIGH PRIORITY:**\n"
            for interaction in high_interactions[:3]:  # Limit to top 3
                summary += f"• {interaction.get_display_name()}: {interaction.summary}\n"
        
        summary += "\n\n⚠️ **Reminder:** This is a demo system. All findings must be reviewed by a licensed clinician.\n"
        
        return summary
