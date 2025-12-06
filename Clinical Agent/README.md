# AI-Powered Clinical Q&A and Drug Interaction Validation System

A hackathon demonstration project showcasing an AI-powered clinical decision support system built with **Python** and **Streamlit**.

## ⚠️ IMPORTANT DISCLAIMER

**This is a demonstration application for educational and hackathon purposes ONLY.** This system is NOT intended for real medical use and should never be used to make actual clinical decisions. Always consult qualified healthcare professionals for medical advice, diagnosis, and treatment.

## Features

### 🔍 Core Capabilities

1. **Patient Context Management**

   - Comprehensive patient demographics
   - Medication list management
   - Allergy and condition tracking
   - Clinical flags (renal/hepatic impairment, pregnancy)

2. **Clinical Q&A Assistant**

   - Natural language question answering
   - Patient-context-aware responses
   - Chat-style interface
   - Evidence-based response formatting
   - Optional OpenAI integration (falls back to rule-based responses)

3. **Drug Interaction Checker**

   - Drug-drug interaction detection
   - Drug-allergy cross-sensitivity checking
   - Drug-condition contraindication alerts
   - Severity-based risk classification (High/Medium/Low)
   - Detailed management recommendations

4. **Risk Scoring & Prediction**

   - Multi-factor risk assessment
   - Age, polypharmacy, and comorbidity considerations
   - 0-100 scoring scale with qualitative labels
   - Contributing factor analysis
   - Clinical recommendations based on risk level

5. **Audit Logging**
   - SQLite database for activity tracking
   - Event-based logging (Q&A, interaction checks, risk scores)
   - Exportable audit trails (CSV)
   - Activity statistics and reporting

## 🏗️ Architecture

```
Clinical Agent/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and settings
├── models.py                       # Data models (Patient, InteractionResult, etc.)
├── requirements.txt                # Python dependencies
├── services/
│   ├── __init__.py
│   ├── llm_service.py             # Clinical Q&A service
│   ├── drug_interaction_service.py # Drug interaction checking
│   ├── risk_scoring_service.py    # Risk assessment algorithms
│   └── audit_service.py           # Audit logging service
└── audit_logs.db                  # SQLite database (created at runtime)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Step 1: Clone or Download

```powershell
# If using git
git clone <repository-url>
cd "Clinical Agent"

# Or download and extract the project files
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
# source venv/bin/activate
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure (Optional)

Create a `.env` file in the project root for optional API integrations:

```env
# Optional: OpenAI API for enhanced LLM responses
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo

# Optional: DrugBank API (not yet implemented)
DRUGBANK_API_KEY=your_drugbank_key_here
```

**Note:** The application works perfectly without API keys using built-in rule-based responses.

### Step 5: Run the Application

```powershell
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Patient & Medications Tab

- Enter patient demographics (age, sex, weight, height)
- Add allergies, diagnoses, and current medications
- Set clinical flags (pregnancy, renal/hepatic impairment)
- Click "Save Patient Context" to persist the data

### 2. Clinical Q&A Tab

- Ask clinical questions in natural language
- System provides evidence-based responses with patient context
- Maintains conversation history
- All responses include disclaimers and safety reminders

**Example Questions:**

- "What are the monitoring requirements for warfarin?"
- "How should I manage hypertension in this patient?"
- "What are the contraindications for NSAIDs?"

### 3. Drug Interaction Check Tab

- View current medication list from patient context
- Add additional medications to check
- Click "Check Interactions" to analyze
- Results show severity-coded interactions with management advice

**Covered Interactions:**

- Warfarin + NSAIDs (bleeding risk)
- ACE inhibitors + potassium-sparing diuretics
- Statins + macrolide antibiotics
- Metformin + contrast dye
- And many more...

### 4. Risk Prediction & Alerts Tab

- Review patient overview and active interactions
- Click "Compute Risk Score" for assessment
- View contributing factors and risk level (Low/Moderate/High)
- Receive tailored clinical recommendations

### 5. Audit & Logs Tab

- View recent system activity
- Filter by number of records
- Export audit logs to CSV
- Track usage statistics

## 🔬 Technical Details

### Data Models

- **Patient**: Comprehensive patient demographics and clinical context
- **InteractionResult**: Drug interaction findings with severity and management advice
- **RiskScore**: Numerical score (0-100) with qualitative label and factors
- **AuditEntry**: System activity tracking

### Services

- **LLMService**: Handles clinical question answering (stub + optional OpenAI)
- **DrugInteractionService**: Rule-based interaction checking with extensible API interface
- **RiskScoringService**: Multi-factor risk assessment algorithm
- **AuditService**: SQLite-based logging and reporting

### Demo Data

The system includes a built-in knowledge base with:

- 9 common drug-drug interactions
- Allergy cross-sensitivities (penicillin, sulfa, aspirin)
- Drug-condition interactions (heart failure, kidney disease, asthma)

## 🧪 Testing the System

### Quick Test Scenario

1. **Set up a test patient:**

   - Age: 72
   - Medications: warfarin, ibuprofen, metformin
   - Allergies: penicillin
   - Conditions: kidney disease
   - Flags: Renal impairment ✓

2. **Check interactions:**

   - Should detect warfarin-ibuprofen (HIGH severity)
   - Should detect metformin-kidney disease interaction

3. **Compute risk score:**

   - Expected: HIGH risk
   - Factors: elderly, polypharmacy, renal impairment, high-severity interactions

4. **Ask Q&A:**
   - "What monitoring is needed for warfarin?"
   - Should provide INR monitoring guidance with patient-specific notes

## 🔌 Extension Points

### Adding External APIs

The codebase includes TODO markers for integration with:

1. **DrugBank API** (`services/drug_interaction_service.py`)

   - Implement `ExternalInteractionAPI.fetch_interactions()`
   - Add authentication and error handling
   - Map API responses to `InteractionResult` objects

2. **OpenAI Integration** (already supported)
   - Add `OPENAI_API_KEY` to `.env`
   - Install: `pip install openai`
   - System automatically uses LLM when key is present

### Extending Interaction Database

Add entries to dictionaries in `services/drug_interaction_service.py`:

- `DRUG_DRUG_INTERACTIONS`
- `ALLERGY_INTERACTIONS`
- `CONDITION_INTERACTIONS`

### Customizing Risk Scoring

Modify weights in `services/risk_scoring_service.py`:

- `BASE_MED_WEIGHT`
- `INTERACTION_WEIGHTS`
- `AGE_PENALTY`
- etc.

## 📊 Dependencies

- **streamlit** (≥1.28.0): Web application framework
- **pydantic** (≥2.0.0): Data validation
- **requests** (≥2.31.0): HTTP client for external APIs
- **python-dotenv** (≥1.0.0): Environment variable management
- **pandas**: Data manipulation (installed with Streamlit)
- **sqlite3**: Audit logging (Python standard library)

## 🛡️ Safety Features

- Global disclaimer on every page
- Response-level disclaimers in Q&A
- Severity-based color coding (red/orange/green)
- Clear labeling of demo status
- No storage of real patient data
- Audit trail for accountability

## 📝 License

This is a hackathon demonstration project. Use at your own risk for educational purposes only.

## 🤝 Contributing

This is a demo project, but suggestions and improvements are welcome!

## 📧 Support

For questions or issues with this demonstration, please refer to the code comments and documentation.

---

**Built with ❤️ for Healthcare Innovation Hackathon | December 2025**
