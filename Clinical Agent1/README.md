# Clinical AI Assistant - TCS AI Fridays Hackathon

A multi-agent AI-powered clinical Q&A and drug interaction validation system built with Python, Streamlit, and Gemini AI.

⚠️ **DISCLAIMER**: This is a demo prototype for educational and hackathon purposes only. This system does NOT provide medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

## Features

### 🤖 Multi-Agent AI Architecture

- **Clinical Q&A Agent**: Answers clinical questions using RAG and LLM
- **Drug Interaction Agent**: Validates drug-drug and drug-allergy interactions
- **Risk Assessment Agent**: Calculates patient risk scores with ML-based prediction
- **Coordinator Agent**: Routes requests and orchestrates agent workflows

### 💊 Core Capabilities

1. **Patient Context Management**: Capture comprehensive patient information
2. **Clinical Q&A Chat**: Real-time question answering with medical knowledge base
3. **Drug Interaction Validation**: Check for drug-drug and drug-allergy interactions
4. **Risk Assessment**: Predictive adverse reaction risk scoring
5. **Audit Logging**: Complete compliance tracking with SQLite database

### 🛡️ Safety Features

- Input validation and sanitization
- Output guardrails with content filtering
- Medical disclaimers on all responses
- Comprehensive audit trail

## Tech Stack

- **UI Framework**: Streamlit
- **LLM Provider**: Google Gemini AI (abstracted for easy switching)
- **Vector Store**: FAISS for document retrieval
- **Embeddings**: Sentence Transformers
- **ML Framework**: Scikit-learn for risk modeling
- **Database**: SQLite for audit logs
- **Data Validation**: Pydantic

## Project Structure

```
Clinical Agent1/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and settings
├── models.py                       # Data models (Patient, RiskScore, etc.)
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
├── agents/                         # Multi-agent orchestration
│   ├── __init__.py
│   ├── clinical_qa_agent.py       # Q&A with RAG
│   ├── interaction_agent.py       # Drug interaction validation
│   ├── risk_agent.py              # Risk assessment
│   └── coordinator_agent.py       # Agent orchestration
│
├── services/                       # Core services
│   ├── llm_service.py             # Abstract LLM with Gemini/OpenAI support
│   ├── rag_service.py             # Retrieval-Augmented Generation
│   ├── drug_interaction_service.py # Interaction checking
│   ├── risk_model_service.py      # Risk scoring
│   ├── guardrails_service.py      # Safety validation
│   └── audit_service.py           # Logging and compliance
│
├── knowledge_base/                 # Medical guidelines (markdown/text)
│   ├── aspirin_guidelines.md
│   ├── metformin_guidelines.md
│   ├── warfarin_guidelines.md
│   ├── lisinopril_guidelines.md
│   └── polypharmacy_elderly.md
│
└── data/                           # Vector store and databases
    └── vector_store/               # FAISS index (auto-generated)
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Gemini API key (free tier available at https://makersuite.google.com/app/apikey)

### 1. Clone or Navigate to Project Directory

```powershell
cd "d:\Python Projects\Clinical Agent1"
```

### 2. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If you encounter execution policy errors, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install all required packages including:

- streamlit
- google-generativeai
- langchain
- faiss-cpu
- sentence-transformers
- scikit-learn
- pydantic
- And more...

### 4. Configure Environment Variables

Create a `.env` file from the example:

```powershell
copy .env.example .env
```

Edit `.env` and add your Gemini API key:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
TEMPERATURE=0.7
MAX_TOKENS=2048
```

### 5. Run the Application

```powershell
streamlit run app.py
```

The application will:

- Initialize the RAG service and index documents from `knowledge_base/`
- Start the Streamlit server
- Open in your default browser at `http://localhost:8501`

## Usage Guide

### 1. Patient Context Tab

- Enter patient demographics (age, sex, weight)
- Add known allergies
- List current diagnoses
- Input current medications
- Mark any organ impairments
- Click "Save Patient Data"

### 2. Clinical Q&A Tab

- Ask clinical questions in the chat interface
- System retrieves relevant knowledge and generates answers
- All responses include medical disclaimers
- Considers patient context if available

### 3. Drug Interactions Tab

- Requires patient data with medications
- Click "Check Interactions" to analyze
- View color-coded severity levels:
  - 🔴 High Severity
  - 🟡 Medium Severity
  - 🟢 Low Severity
- Expand interactions for detailed explanations and management advice

### 4. Risk Assessment Tab

- Calculates overall risk score (0-100)
- Shows risk level (Low/Moderate/High)
- Lists contributing factors
- Provides clinical recommendations

### 5. Audit Logs Tab

- View all system activity
- Filter by event type
- Export logs to CSV
- View statistics

## Customization

### Using Different LLM Providers

The system supports multiple LLM providers through an abstract interface:

#### Switch to OpenAI:

1. Update `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4
```

2. Install OpenAI package:

```powershell
pip install openai
```

#### Add New Provider:

Extend `BaseLLMService` in `services/llm_service.py`:

```python
class MyCustomLLMService(BaseLLMService):
    def generate(self, prompt, system_prompt=None):
        # Implement your provider
        pass
```

### Adding Medical Knowledge

Add new documents to `knowledge_base/`:

1. Create `.md` or `.txt` files with medical guidelines
2. Restart the application (RAG will re-index)

### Customizing Drug Interactions

Edit `services/drug_interaction_service.py`:

- Add entries to `_initialize_interactions()`
- Update `drug_allergies` dictionary

## Testing

Test individual components:

```powershell
# Test LLM service
python services/llm_service.py

# Test RAG service
python services/rag_service.py

# Test drug interaction service
python services/drug_interaction_service.py

# Test agents
python agents/clinical_qa_agent.py
```

## Architecture Highlights

### Multi-Agent Workflow

1. **Input Validation**: Guardrails check user input
2. **Intent Routing**: Coordinator determines appropriate agent
3. **RAG Retrieval**: Relevant documents fetched from knowledge base
4. **LLM Generation**: Answer generated with context
5. **Output Validation**: Response validated for safety
6. **Audit Logging**: All actions logged for compliance

### RAG Pipeline

- Documents chunked into 500-character segments
- Embeddings generated with Sentence Transformers
- FAISS index for fast similarity search
- Top-3 relevant chunks retrieved per query

### Risk Scoring

- Rule-based + ML hybrid approach
- Considers: age, polypharmacy, organ function, interactions
- Weighted scoring with interpretable factors
- Evidence-based recommendations

## Performance Optimization

- RAG service and embeddings cached with `@st.cache_resource`
- Vector index persisted to disk
- Singleton pattern for service instances
- Efficient FAISS indexing

## Security & Compliance

- Input sanitization against injection attacks
- Content safety checks on all responses
- PII redaction in audit logs
- Medical disclaimers enforced
- Comprehensive audit trail

## Limitations & Future Enhancements

### Current Limitations

- Demo data only (not production medical database)
- Limited drug interaction database
- Rule-based risk model (not trained on real data)
- No EHR integration
- Single-user (no authentication)

### Potential Enhancements

- Integration with clinical drug databases (e.g., Lexicomp, Micromedex)
- Real ML model trained on clinical data
- Multi-user support with RBAC
- EHR/FHIR integration
- Real-time monitoring dashboards
- Advanced NLP for clinical note extraction
- Voice interface for hands-free operation

## Troubleshooting

### Import Errors

```powershell
pip install --upgrade -r requirements.txt
```

### FAISS Installation Issues on Windows

```powershell
pip install faiss-cpu --no-cache-dir
```

### Gemini API Errors

- Verify API key in `.env`
- Check API quota at Google AI Studio
- Ensure internet connectivity

### Streamlit Won't Start

```powershell
# Clear cache
streamlit cache clear
# Try different port
streamlit run app.py --server.port 8502
```

## Contributing

This is a hackathon demo project. For production use:

1. Replace stub data with real medical databases
2. Implement proper authentication and authorization
3. Add comprehensive error handling
4. Conduct security audit
5. Validate with medical professionals
6. Ensure regulatory compliance (HIPAA, GDPR, etc.)

## License

MIT License - This is a demo/educational project.

## Acknowledgments

- TCS AI Fridays Hackathon
- Google Gemini AI
- Streamlit community
- Open-source medical guidelines

## Contact

For questions about this demo, please refer to the TCS AI Fridays Hackathon documentation.

---

**Remember**: This is NOT a medical device. Always consult qualified healthcare professionals for medical advice, diagnosis, and treatment.
