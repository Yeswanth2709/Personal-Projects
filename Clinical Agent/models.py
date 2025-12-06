"""Data models for the Clinical Q&A and Drug Interaction System."""

from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime


@dataclass
class Patient:
    """Represents patient context and clinical information."""
    
    patient_id: str = ""
    age: Optional[int] = None
    sex: Optional[str] = None
    weight: Optional[float] = None  # in kg
    height: Optional[float] = None  # in cm
    allergies: List[str] = field(default_factory=list)
    diagnoses: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    pregnancy_status: bool = False
    renal_impairment: bool = False
    hepatic_impairment: bool = False
    
    def to_dict(self) -> dict:
        """Convert patient to dictionary."""
        return {
            "patient_id": self.patient_id,
            "age": self.age,
            "sex": self.sex,
            "weight": self.weight,
            "height": self.height,
            "allergies": self.allergies,
            "diagnoses": self.diagnoses,
            "current_medications": self.current_medications,
            "pregnancy_status": self.pregnancy_status,
            "renal_impairment": self.renal_impairment,
            "hepatic_impairment": self.hepatic_impairment,
        }
    
    def get_summary(self) -> str:
        """Get a text summary of patient information."""
        parts = []
        if self.age:
            parts.append(f"Age: {self.age}")
        if self.sex:
            parts.append(f"Sex: {self.sex}")
        if self.current_medications:
            parts.append(f"Medications: {', '.join(self.current_medications)}")
        if self.allergies:
            parts.append(f"Allergies: {', '.join(self.allergies)}")
        if self.diagnoses:
            parts.append(f"Conditions: {', '.join(self.diagnoses)}")
        
        return " | ".join(parts) if parts else "No patient data"


@dataclass
class Medication:
    """Represents a medication."""
    
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None


@dataclass
class InteractionResult:
    """Represents a drug interaction finding."""
    
    interaction_type: Literal["drug-drug", "drug-allergy", "drug-condition"]
    drug1: str
    drug2: Optional[str] = None
    allergen: Optional[str] = None
    condition: Optional[str] = None
    severity: Literal["high", "medium", "low"] = "low"
    summary: str = ""
    management_advice: str = ""
    
    def get_display_name(self) -> str:
        """Get a display name for the interaction."""
        if self.interaction_type == "drug-drug":
            return f"{self.drug1} ↔ {self.drug2}"
        elif self.interaction_type == "drug-allergy":
            return f"{self.drug1} (Allergy: {self.allergen})"
        else:
            return f"{self.drug1} (Condition: {self.condition})"


@dataclass
class RiskScore:
    """Represents a patient risk score."""
    
    score: int  # 0-100
    label: Literal["Low", "Moderate", "High"]
    contributing_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_color(self) -> str:
        """Get color code for risk level."""
        if self.label == "High":
            return "red"
        elif self.label == "Moderate":
            return "orange"
        else:
            return "green"


@dataclass
class AuditEntry:
    """Represents an audit log entry."""
    
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: Literal["Q&A", "INTERACTION_CHECK", "RISK_SCORE"] = "Q&A"
    patient_id: str = ""
    risk_level: Optional[str] = None
    summary_text: str = ""
    raw_json: str = ""
    
    def to_tuple(self) -> tuple:
        """Convert to tuple for database insertion."""
        return (
            self.timestamp.isoformat(),
            self.event_type,
            self.patient_id,
            self.risk_level,
            self.summary_text,
            self.raw_json,
        )


@dataclass
class ClinicalQuestion:
    """Represents a clinical question."""
    
    question_text: str
    language: str = "en"
    timestamp: datetime = field(default_factory=datetime.now)
