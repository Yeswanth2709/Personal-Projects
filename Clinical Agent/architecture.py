"""
System Architecture Visualization
Run this to see the architecture diagram
"""

def print_architecture():
    diagram = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                   CLINICAL Q&A SYSTEM ARCHITECTURE                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT UI LAYER (app.py)                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Tab 1: Patient    │  Tab 2: Clinical  │  Tab 3: Drug      │  Tab 4:   │
│  & Medications     │  Q&A              │  Interactions     │  Risk     │
│                    │                   │                   │  Score    │
│  • Demographics    │  • Chat UI        │  • Med List       │  • Gauge  │
│  • Allergies       │  • History        │  • Checks         │  • Factors│
│  • Diagnoses       │  • Context        │  • Severity       │  • Advice │
│  • Medications     │  • Disclaimer     │  • Details        │           │
└────────┬──────────────────┬─────────────────┬────────────────┬──────────┘
         │                  │                 │                │
         │                  │                 │                │
┌────────▼──────────────────▼─────────────────▼────────────────▼──────────┐
│                         SESSION STATE LAYER                              │
├──────────────────────────────────────────────────────────────────────────┤
│  • patient_context (Patient object)                                      │
│  • messages (Chat history)                                               │
│  • last_interactions (InteractionResult[])                               │
│  • last_risk_score (RiskScore)                                           │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                         SERVICE LAYER                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────┐  ┌──────────────────────┐  ┌─────────────────┐│
│  │  LLM Service        │  │ Drug Interaction     │  │ Risk Scoring    ││
│  │  (llm_service.py)   │  │ Service              │  │ Service         ││
│  │                     │  │ (drug_interaction_   │  │ (risk_scoring_  ││
│  │ • answer_question() │  │  service.py)         │  │  service.py)    ││
│  │ • summarize()       │  │                      │  │                 ││
│  │ • stub responses    │  │ • check_drug_drug()  │  │ • score_patient ││
│  │ • OpenAI optional   │  │ • check_allergy()    │  │ • get_risks()   ││
│  │                     │  │ • check_condition()  │  │ • weights       ││
│  └─────────────────────┘  └──────────────────────┘  └─────────────────┘│
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────────┤
│  │  Audit Service (audit_service.py)                                    │
│  │  • log_event()                                                       │
│  │  • get_recent_events()                                               │
│  │  • export_to_csv()                                                   │
│  └──────────────────────────────────────────────────────────────────────┤
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                         DATA MODEL LAYER (models.py)                     │
├──────────────────────────────────────────────────────────────────────────┤
│  @dataclass Patient              @dataclass InteractionResult            │
│  • patient_id                    • interaction_type                      │
│  • age, sex, weight, height      • drug1, drug2                          │
│  • allergies[]                   • severity (high/medium/low)            │
│  • diagnoses[]                   • summary, management_advice            │
│  • current_medications[]                                                 │
│  • flags (renal, hepatic, etc)   @dataclass RiskScore                    │
│                                  • score (0-100)                         │
│  @dataclass ClinicalQuestion     • label (Low/Moderate/High)             │
│  • question_text                 • contributing_factors[]                │
│  • language                                                              │
│                                  @dataclass AuditEntry                   │
│                                  • timestamp, event_type                 │
│                                  • patient_id, risk_level                │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                         DATA STORAGE LAYER                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────┐         ┌───────────────────────────┐       │
│  │   Knowledge Base       │         │   SQLite Database         │       │
│  │   (In-Memory Dicts)    │         │   (audit_logs.db)         │       │
│  │                        │         │                           │       │
│  │ • DRUG_DRUG_           │         │ Table: audit_logs         │       │
│  │   INTERACTIONS         │         │ • id (PRIMARY KEY)        │       │
│  │   (9 interactions)     │         │ • timestamp               │       │
│  │                        │         │ • event_type              │       │
│  │ • ALLERGY_             │         │ • patient_id              │       │
│  │   INTERACTIONS         │         │ • risk_level              │       │
│  │   (3 groups)           │         │ • summary_text            │       │
│  │                        │         │ • raw_json                │       │
│  │ • CONDITION_           │         │                           │       │
│  │   INTERACTIONS         │         │ Indexes: timestamp DESC   │       │
│  │   (3 conditions)       │         │                           │       │
│  └────────────────────────┘         └───────────────────────────┘       │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL INTEGRATIONS (Optional)                  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────┐              ┌──────────────────────┐              │
│  │  OpenAI API      │              │  DrugBank API        │              │
│  │  (gpt-3.5-turbo) │              │  (Future/TODO)       │              │
│  │                  │              │                      │              │
│  │  • Chat          │              │  • Drug interactions │              │
│  │    completions   │              │  • Drug info         │              │
│  │  • Optional      │              │  • Not implemented   │              │
│  │  • Fallback to   │              │  • Interface ready   │              │
│  │    stub          │              │                      │              │
│  └──────────────────┘              └──────────────────────┘              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════╗
║                            DATA FLOW EXAMPLES                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. DRUG INTERACTION CHECK FLOW:
   ────────────────────────────────
   User Input (Tab 3) 
      → Patient meds: ["warfarin", "ibuprofen"]
      → DrugInteractionService.check_interactions()
         → normalize_med_name() for each med
         → check_drug_drug() - finds warfarin+ibuprofen HIGH
         → check_drug_allergy() with patient allergies
         → check_drug_condition() with patient diagnoses
      → Returns InteractionResult[] with severity & advice
      → AuditService.log_event("INTERACTION_CHECK")
      → Display color-coded results in UI
      → Store in session_state.last_interactions

2. RISK SCORE COMPUTATION FLOW:
   ─────────────────────────────
   User clicks "Compute Risk" (Tab 4)
      → RiskScoringService.score_patient(patient, interactions)
         → Base score: num_meds × 5
         → Add age penalty if ≥65
         → Add polypharmacy penalty if ≥5 meds
         → Add organ impairment penalties
         → Add interaction severity weights
         → Cap at 100
         → Map to label (Low/Moderate/High)
      → Returns RiskScore with factors
      → AuditService.log_event("RISK_SCORE")
      → Display gauge and recommendations
      → Store in session_state.last_risk_score

3. CLINICAL Q&A FLOW:
   ──────────────────
   User asks question (Tab 2)
      → LLMService.answer_question(patient, question)
         → If OpenAI key exists:
            → Build context prompt with patient data
            → Call OpenAI API
            → Format response with disclaimer
         → Else (stub mode):
            → Analyze question keywords
            → Select appropriate template response
            → Add patient-specific considerations
            → Format with disclaimer
      → Returns answer text
      → AuditService.log_event("Q&A")
      → Display in chat UI
      → Store in session_state.messages

4. AUDIT LOGGING FLOW:
   ───────────────────
   Any user action
      → AuditService.log_event(type, patient_id, payload, risk)
         → Create AuditEntry object
         → Generate summary text
         → Serialize payload to JSON
         → INSERT into SQLite audit_logs table
      → User views Tab 5
         → AuditService.get_recent_events(limit)
         → SELECT from audit_logs ORDER BY timestamp DESC
         → Convert to Pandas DataFrame
         → Display with color coding by risk_level
      → User clicks "Download CSV"
         → AuditService.export_to_csv(filepath)
         → CSV file created
         → Streamlit download button

╔═══════════════════════════════════════════════════════════════════════════╗
║                         TECHNOLOGY STACK                                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

Frontend:           Streamlit 1.28+
                    ├─ Multi-tab layout
                    ├─ Chat components
                    ├─ Forms and inputs
                    ├─ Data display (tables, metrics)
                    └─ Download buttons

Backend:            Python 3.10+
                    ├─ Dataclasses for models
                    ├─ Type hints throughout
                    └─ Modular services

Data Storage:       SQLite3 (built-in)
                    └─ Single-file database

Optional APIs:      OpenAI GPT (via openai package)
                    DrugBank (future, stub ready)

Dependencies:       streamlit, pydantic, requests, python-dotenv
                    pandas (via streamlit), sqlite3 (built-in)

Development:        Virtual environment (venv)
                    Python 3.13.5.final.0

╔═══════════════════════════════════════════════════════════════════════════╗
║                    KEY DESIGN PATTERNS USED                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. Service Layer Pattern
   - Business logic separated into dedicated service classes
   - Each service has single responsibility
   - Stateless operations (except audit)

2. Data Transfer Objects (DTO)
   - Dataclasses for clean data structures
   - Type-safe with hints
   - Methods for serialization

3. Session State Management
   - Streamlit session_state for UI state
   - Persistent across reruns
   - No global variables

4. Strategy Pattern
   - LLMService: stub vs. OpenAI strategy
   - Determined by configuration

5. Repository Pattern
   - AuditService encapsulates data access
   - SQLite operations abstracted

6. Factory Pattern
   - Demo data generators create sample patients

"""
    print(diagram)

if __name__ == "__main__":
    print_architecture()
