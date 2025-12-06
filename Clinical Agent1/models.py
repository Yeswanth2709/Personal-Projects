"""
Data models for Clinical AI Assistant.
Defines structured data types using Pydantic for type safety and validation.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Patient(BaseModel):
    """Patient context information."""
    patient_id: str = Field(default="demo-patient", description="Patient identifier")
    age: int = Field(ge=0, le=120, description="Patient age in years")
    sex: Literal["Male", "Female", "Other"] = Field(description="Patient sex")
    weight: Optional[float] = Field(None, ge=0, description="Weight in kg")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    diagnoses: List[str] = Field(default_factory=list, description="Current diagnoses")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    pregnancy_status: Optional[bool] = Field(None, description="Pregnancy status if applicable")
    renal_impairment: bool = Field(False, description="Renal impairment flag")
    hepatic_impairment: bool = Field(False, description="Hepatic impairment flag")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "demo-001",
                "age": 45,
                "sex": "Female",
                "weight": 70.0,
                "allergies": ["Penicillin"],
                "diagnoses": ["Hypertension", "Type 2 Diabetes"],
                "medications": ["Metformin", "Lisinopril"],
                "pregnancy_status": False,
                "renal_impairment": False,
                "hepatic_impairment": False
            }
        }


class Medication(BaseModel):
    """Medication information."""
    name: str = Field(description="Medication name")
    dose: Optional[str] = Field(None, description="Dose and frequency")
    route: Optional[str] = Field(None, description="Route of administration")
    indication: Optional[str] = Field(None, description="Indication for use")


class InteractionResult(BaseModel):
    """Drug interaction validation result."""
    drug1: str = Field(description="First drug in interaction")
    drug2: str = Field(description="Second drug in interaction")
    severity: Literal["low", "medium", "high"] = Field(description="Interaction severity")
    interaction_type: str = Field(description="Type of interaction")
    explanation: str = Field(description="Explanation of the interaction")
    management: str = Field(description="Management recommendations")
    references: List[str] = Field(default_factory=list, description="Reference sources")


class AllergyCheck(BaseModel):
    """Allergy check result."""
    medication: str = Field(description="Medication being checked")
    allergy: str = Field(description="Known allergy")
    severity: Literal["low", "medium", "high"] = Field(description="Risk severity")
    explanation: str = Field(description="Explanation of the allergy concern")
    alternative_medications: List[str] = Field(default_factory=list)


class RiskScore(BaseModel):
    """Risk assessment result."""
    overall_score: float = Field(ge=0, le=100, description="Overall risk score 0-100")
    risk_level: Literal["Low", "Moderate", "High"] = Field(description="Risk category")
    contributing_factors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Factors contributing to risk"
    )
    recommendations: List[str] = Field(default_factory=list, description="Risk mitigation recommendations")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """Chat message in conversation."""
    role: Literal["user", "assistant", "system"] = Field(description="Message role")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class AgentState:
    """Shared state for multi-agent orchestration."""
    patient: Optional[Patient] = None
    messages: List[ChatMessage] = field(default_factory=list)
    current_query: str = ""
    retrieved_context: List[str] = field(default_factory=list)
    interaction_results: List[InteractionResult] = field(default_factory=list)
    allergy_results: List[AllergyCheck] = field(default_factory=list)
    risk_score: Optional[RiskScore] = None
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation history."""
        msg = ChatMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        return msg


class AuditLog(BaseModel):
    """Audit log entry."""
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str = Field(default="demo-user", description="User identifier")
    event_type: Literal["qa", "interaction_check", "risk_assessment", "error"] = Field(
        description="Type of event"
    )
    risk_level: Optional[str] = Field(None, description="Risk level if applicable")
    summary: str = Field(description="Brief summary of the event")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed event data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-12-06T10:30:00",
                "user_id": "demo-user",
                "event_type": "qa",
                "summary": "Clinical question about drug dosage",
                "details": {"question": "What is the correct dose?", "answer": "Consult guidelines"}
            }
        }
