"""Configuration for the Clinical Q&A and Drug Interaction System."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # LLM Service Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    USE_EXTERNAL_LLM = bool(OPENAI_API_KEY)
    
    # Drug Interaction API Configuration
    DRUGBANK_API_KEY = os.getenv("DRUGBANK_API_KEY", "")
    USE_EXTERNAL_DRUG_API = bool(DRUGBANK_API_KEY)
    
    # Database Configuration
    AUDIT_DB_PATH = "audit_logs.db"
    
    # Feature Flags
    ENABLE_RISK_SCORING = True
    ENABLE_AUDIT_LOGGING = True
    
    # UI Configuration
    PAGE_TITLE = "AI Clinical Q&A & DDI Demo"
    LAYOUT = "wide"
    
    # Disclaimers
    GLOBAL_DISCLAIMER = """
    ⚠️ **IMPORTANT DISCLAIMER**: This is a demonstration application only and is NOT intended 
    for real medical use. All outputs are for educational and hackathon purposes. 
    Always consult qualified healthcare professionals for actual medical decisions.
    """
