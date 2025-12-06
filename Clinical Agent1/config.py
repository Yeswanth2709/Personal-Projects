"""
Configuration module for Clinical AI Assistant.
Loads environment variables and provides centralized config access.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
DATA_DIR = BASE_DIR / "data"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Settings
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# Application Settings
APP_TITLE = os.getenv("APP_TITLE", "Clinical AI Assistant")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///audit.db")

# Embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_STORE_PATH = DATA_DIR / "vector_store"

# Disclaimer Text
MEDICAL_DISCLAIMER = """
⚠️ **DISCLAIMER**: This is a demo prototype for educational and hackathon purposes only. 
This system does NOT provide medical advice, diagnosis, or treatment. Always consult 
qualified healthcare professionals for medical decisions.
"""

# Risk Thresholds
RISK_THRESHOLDS = {
    "low": (0, 30),
    "moderate": (30, 70),
    "high": (70, 100)
}

# Drug Interaction Severity Colors
SEVERITY_COLORS = {
    "low": "#90EE90",      # Light green
    "medium": "#FFD700",    # Gold
    "high": "#FF6B6B"       # Red
}
