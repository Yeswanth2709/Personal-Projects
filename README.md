# Healthcare Compliance AI System

## 🎯 Executive Summary

A comprehensive, production-grade healthcare compliance enforcement system that automatically ensures regulatory compliance (HIPAA, GDPR, PCI-DSS, AI Act) for AI-powered healthcare applications. The system uses **LangGraph** for orchestration, **policy knowledge graphs** for regulation mapping, and **multi-agent architecture** to enforce privacy, security, and governance requirements in real-time.

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                              │
│  ┌──────────────────┐        ┌──────────────────────────────────┐  │
│  │  Streamlit UI    │   OR   │  HTML/JavaScript Frontend        │  │
│  │  (ui/app.py)     │        │  (ui/index.html)                 │  │
│  └────────┬─────────┘        └────────────┬─────────────────────┘  │
└───────────┼──────────────────────────────┼────────────────────────┘
            │                               │
            └───────────┬───────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────────┐
│                    COMPLIANCE ORCHESTRATION                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  LangGraph Agent (frontend/healthcare_compliance_agent.py)  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐   │   │
│  │  │ Get Plan │→ │Check     │→ │Mask PII │→ │Sanitize  │   │   │
│  │  │          │  │Access    │  │         │  │Output    │   │   │
│  │  └──────────┘  └──────────┘  └─────────┘  └──────────┘   │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────┬────────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────────┐
│                    FASTAPI BACKEND                                  │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints (app/main_langgraph.py)                 │   │
│  │  • GET  /api/enforcement-plan                               │   │
│  │  • POST /api/check-access                                   │   │
│  │  • POST /api/mask-pii                                       │   │
│  │  • POST /api/sanitize-output                                │   │
│  │  • GET  /api/audit-logs                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────┬────────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────────┐
│                  COMPLIANCE ENFORCEMENT ENGINE                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  LangGraph Workflow (agent_graph/graph.py)                  │   │
│  │                                                              │   │
│  │  Router → Agent Pipeline → Audit                            │   │
│  │                                                              │   │
│  │  Agents (agent_graph/nodes.py):                             │   │
│  │  ├─ AccessControlAgent  (role-based authorization)          │   │
│  │  ├─ PrivacyAgent        (PII detection & masking)           │   │
│  │  ├─ EncryptionAgent     (data encryption)                   │   │
│  │  ├─ OutputGuardAgent    (output sanitization)               │   │
│  │  ├─ RetentionAgent      (data retention policies)           │   │
│  │  ├─ MonitoringAgent     (compliance monitoring)             │   │
│  │  └─ AuditAgent          (audit logging)                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────┬────────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────────┐
│              POLICY KNOWLEDGE GRAPH SYSTEM                          │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Policy Graph (policy_generator/policy_graph/)              │   │
│  │                                                              │   │
│  │  RequestType → Regulation → PolicyRule → AI_Scope → Agent   │   │
│  │                                                              │   │
│  │  Components:                                                 │   │
│  │  ├─ build_policy_graph.py  (NetworkX graph builder)        │   │
│  │  ├─ resolver.py            (policy resolution engine)       │   │
│  │  ├─ loader.py              (graph persistence)              │   │
│  │  └─ actions.py             (AI scope → action mapping)      │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────┬────────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────────┐
│                    SECURITY & DATA LAYER                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  PII Detection   │  │  Encryption      │  │  Audit Logging  │ │
│  │  (security/pii.py)│  │(security/       │  │ (security/      │ │
│  │  • Names         │  │ encryption.py)   │  │  audit.py)      │ │
│  │  • SSN/Email     │  │  • Fernet cipher │  │  • HMAC pseudo  │ │
│  │  • Phone numbers │  │  • Field encrypt │  │  • Event trace  │ │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Core Components

### 1. **Policy Knowledge Graph** (`policy_generator/`)

The foundation of the system - a **NetworkX-based graph** that encodes regulatory requirements from multiple sources (HIPAA, GDPR, PCI-DSS, AI Act) and maps them to specific agents and actions.

#### How It Works:

1. **PDF Ingestion** (`pdf_to_policy_json.py`):
   - Extracts text from regulation PDFs
   - Uses GPT-4 to convert regulations into structured JSON
   - Categorizes policies by AI scope (Privacy, Access Control, Governance, etc.)
   - Output: JSON files in `output_policies_AI/`

2. **Graph Construction** (`build_policy_graph.py`):
   ```
   RequestType → Regulation → PolicyRule → AI_Scope → Agent
   ```
   - **RequestType nodes**: Healthcare operations (patient_triage, appointment_scheduling, etc.)
   - **Regulation nodes**: HIPAA, GDPR, PCI-DSS, AI Act
   - **PolicyRule nodes**: Individual articles/requirements from regulations
   - **AI_Scope nodes**: Privacy, Access Control, Governance, Explainability
   - **Agent nodes**: AccessControlAgent, PrivacyAgent, OutputGuardAgent, etc.

3. **Policy Resolution** (`resolver.py`):
   - Given a request type, traverses the graph to find applicable policies
   - Returns enforcement plan: which regulations apply, which agents to invoke, which actions to take

#### Request Types (`request_types.py`):
- `patient_triage`: Emergency/routine patient assessment
- `patient_lookup`: Medical record retrieval
- `appointment_scheduling`: Calendar management
- `prescription`: Medication orders
- `lab_results`: Test result access
- `billing`: Payment processing
- `clinical_decision`: Diagnostic/treatment recommendations

---

### 2. **LangGraph Compliance Engine** (`agent_graph/`)

A **state machine workflow** that enforces compliance policies using specialized agents.

#### Workflow (`graph.py`):

```python
Router → [Agent Pipeline] → Audit → END
```

**Routing Logic**:
1. **Router Node**: Determines execution order based on enforcement plan
2. **Agent Execution**: Each agent processes the state and updates audit trail
3. **Conditional Routing**: Loops back to router until all agents complete
4. **Audit Finalization**: AuditAgent logs final compliance record

#### State Management (`state.py`):

```python
AgentState = {
    # Request Context
    "request_type": str,
    "user_role": str,
    "input_text": str,
    "regulations": List[str],
    
    # Enforcement
    "enforcement_plan": dict,
    "execution_queue": List[str],
    "policy_trace_map": dict,
    
    # Data Flow
    "masked_input": str,
    "llm_output": str,
    "final_output": str,
    "pii_detected": List[dict],
    
    # Audit
    "audit_log": List[dict]
}
```

#### Agents (`nodes.py`):

1. **AccessControlAgent**:
   - Validates user role and permissions
   - Checks consent requirements
   - Enforces least-privilege access

2. **PrivacyAgent**:
   - Detects PII/PHI using regex patterns and NLP
   - Masks sensitive data: names, SSN, emails, phone numbers
   - Applies data minimization (truncates to 500 chars)
   - Optional: tokenization, pseudonymization, encryption

3. **OutputGuardAgent**:
   - Scans LLM outputs for leaked PII
   - Redacts sensitive information before user display
   - Ensures public output safety

4. **EncryptionAgent**:
   - Encrypts sensitive fields using Fernet (AES-128)
   - Key management via environment variables

5. **RetentionAgent**:
   - Enforces data retention policies
   - Schedules automatic deletion

6. **MonitoringAgent**:
   - Real-time compliance monitoring
   - Anomaly detection

7. **AuditAgent**:
   - Creates immutable audit trail
   - HMAC-based pseudonymization for identifiers
   - Records: agent, action, timestamp, policy_trace_ids

---

### 3. **FastAPI Backend** (`app/`)

RESTful API server that exposes compliance middleware endpoints.

#### Main Endpoints (`main_langgraph.py`):

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/compliance/status` | GET | Get compliance toggle state |
| `/api/compliance/enable` | POST | Enable compliance enforcement |
| `/api/compliance/disable` | POST | Bypass compliance (testing mode) |
| `/api/enforcement-plan` | GET | Get applicable policies for request type |
| `/api/check-access` | POST | Validate user access |
| `/api/mask-pii` | POST | Detect and mask PII |
| `/api/sanitize-output` | POST | Clean LLM output |
| `/api/audit-logs` | GET | Retrieve audit trail |

#### Request Processing Flow:

```python
# Example: Triage Request
POST /api/process
{
    "input_text": "Patient John Doe (SSN: 123-45-6789) has chest pain",
    "request_type": "patient_triage",
    "user_role": "clinician"
}

# Internal Flow:
1. Get enforcement plan from policy graph
2. Build LangGraph with agent pipeline
3. Execute workflow:
   - AccessControl: Check clinician can triage
   - Privacy: Mask "John Doe" → [NAME], "123-45-6789" → [SSN]
   - Task: LLM processes masked input
   - OutputGuard: Sanitize output
   - Audit: Log all actions with policy trace
4. Return sanitized output + audit record
```

#### Compliance Toggle (`compliance_state.py`):

The system supports **on/off switching** for compliance enforcement:
- **Enabled**: All requests go through full compliance pipeline
- **Disabled**: Direct pass-through for testing/development

---

### 4. **Security Layer** (`security/`)

Production-grade security implementations:

#### PII Detection (`pii.py`):

Regex-based deterministic detection:
- **SSN**: `\d{3}-\d{2}-\d{4}`
- **Email**: RFC-compliant email pattern
- **Phone**: US/international formats
- **Names**: Title + capitalized tokens (Patient John Doe, Dr. Smith)

Returns structured PII entities:
```python
{
    "type": "SSN",
    "value": "123-45-6789",
    "masked": "[SSN]",
    "start": 15,
    "end": 26
}
```

#### Encryption (`encryption.py`):

- **Algorithm**: Fernet (symmetric AES-128-CBC + HMAC)
- **Key Management**: Environment variable `APP_ENCRYPTION_KEY`
- **Use Cases**: 
  - Sensitive field encryption before storage
  - At-rest data protection

#### Audit Trail (`audit.py`):

- **Event Structure**:
  ```python
  {
      "agent": "PrivacyAgent",
      "action": "mask_phi",
      "timestamp": "2025-12-18T10:30:00Z",
      "status": "COMPLETED",
      "policy_trace_ids": ["HIPAA_164.502", "GDPR_Article_6"],
      "pii_count": 3
  }
  ```
- **Pseudonymization**: HMAC-SHA256 for user/patient IDs
- **PII Protection**: Never stores raw PII in audit logs

#### Access Control (`access_control.py`):

Role-based permissions defined in `config/compliance_config.py`:
```python
request_type_permissions = {
    "patient_triage": ["admin", "clinician", "doctor", "nurse"],
    "prescription": ["admin", "doctor", "pharmacist"],
    "billing": ["admin", "billing_staff"]
}
```

---

### 5. **Frontend Orchestration** (`frontend/`)

#### Compliance Agent (`healthcare_compliance_agent.py`):

A **LangGraph-based orchestration layer** that runs on the frontend and coordinates backend calls:

**Workflow Nodes**:
1. **Get Enforcement Plan**: Query policy graph for applicable regulations
2. **Check Access**: Validate user permissions
3. **Mask PII**: Anonymize input before LLM processing
4. **Call LLM**: Process masked data (clinical decision/triage)
5. **Sanitize Output**: Remove any PII from LLM response
6. **Store Audit**: Persist full compliance trail

**State Management**:
```python
HealthcareComplianceState = {
    "user_id": str,
    "user_role": str,
    "patient_id": str,
    "input_text": str,
    "enforcement_plan": dict,
    "masked_text": str,
    "llm_output": str,
    "sanitized_output": str,
    "audit_record": dict,
    "violations": List[str]
}
```

#### Backend Client (`backend_client.py`):

HTTP client wrapper for FastAPI backend:
```python
client = BackendClient("http://localhost:8000")

# Get enforcement plan
plan = client.get_enforcement_plan("patient_triage")

# Check access
result = client.check_access(
    user_id="clinician_001",
    user_role="clinician",
    patient_id="patient_123"
)

# Mask PII
masked = client.mask_pii("Patient John Doe has diabetes")
```

---

### 6. **User Interface** (`ui/`)

#### Streamlit App (`app.py`):

Interactive healthcare compliance dashboard:

**Pages**:
1. **Clinical Triage**: 
   - Patient symptom input
   - Real-time compliance checking
   - Triage level determination (Emergency/Urgent/Routine)
   - Masked data display

2. **Compliance Dashboard**:
   - Active regulations display
   - Enforcement plan visualization
   - System status monitoring

3. **Audit Trail**:
   - Searchable compliance logs
   - Policy trace visualization
   - Regulation mapping

4. **Settings**:
   - Compliance toggle (enable/disable)
   - User role configuration
   - Request type selection

#### HTML Frontend (`index.html`):

Standalone JavaScript frontend with same capabilities as Streamlit.

---

## 🚀 Getting Started

### Prerequisites

```bash
# Python 3.10+
python --version

# OpenAI API Key
export OPENAI_API_KEY="sk-..."

# Encryption Keys
export APP_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
export AUDIT_HMAC_SECRET="your-secret-key"
```

### Installation

```bash
# Clone repository
git clone <repository-url>
cd COMPLIANCE_AI_SYSTEM

# Install dependencies
pip install -r requirements.txt

# Download spaCy medical model (for NLP-based PII detection)
python -m spacy download en_core_web_sm
```

### Configuration

1. **OpenAI Configuration** (`config/openai_config.py`):
   ```python
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   MODEL = "gpt-4"
   MINI_MODEL = "gpt-4o-mini"
   ```

2. **Compliance Configuration** (`config/config.json`):
   ```json
   {
     "access_control": {
       "allowed_roles": ["clinician", "doctor", "nurse"],
       "denied_roles": ["guest", "anonymous"]
     },
     "active_regulations": ["GDPR", "HIPAA", "PCI-DSS", "AI Act"]
   }
   ```

3. **Request Types** (`policy_generator/request_types.py`):
   - Define healthcare operations
   - Map to required roles and regulations
   - Specify keywords for classification

### Build Policy Graph

```bash
# Generate policy JSONs from regulation PDFs
python policy_generator/pdf_to_policy_json.py

# Build policy knowledge graph
python policy_generator/policy_graph/build_policy_graph.py

# Verify graph
python policy_generator/policy_graph/visualize_policy_graph.py
```

### Run Backend

```bash
# Start FastAPI server
uvicorn app.main_langgraph:app --host 0.0.0.0 --port 8000 --reload

# API docs available at:
# http://localhost:8000/api/docs
```

### Run Frontend

#### Option 1: Enhanced Streamlit UI (Recommended)

The new enhanced UI demonstrates all privacy and compliance features with automatic mock data fallback:

```bash
# Windows
run_ui.bat

# Linux/Mac
chmod +x run_ui.sh
./run_ui.sh

# Or direct command
streamlit run streamlit_app.py
```

**Features:**
- 🩺 Patient Triage with PII masking
- 🔒 Privacy Dashboard with real-time PII detection
- 📊 Audit Trail with policy traceability
- ⚙️ Compliance Settings and enforcement plans
- ✅ **Works offline with mock data when backend unavailable**

See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed walkthrough.

#### Option 2: Original Streamlit UI

```bash
streamlit run ui/app.py
```

#### Option 3: HTML Frontend

Open `ui/index.html` in browser for standalone JavaScript frontend.

---

## 📊 Data Flow Example

### Scenario: Patient Triage

**Input**:
```python
{
    "user_role": "clinician",
    "user_id": "dr_smith_001",
    "patient_id": "patient_12345",
    "request_type": "patient_triage",
    "input_text": "Patient John Doe (DOB: 1985-03-15, SSN: 123-45-6789) reports severe chest pain and shortness of breath"
}
```

**Processing Steps**:

1. **Enforcement Plan Resolution**:
   ```python
   GET /api/enforcement-plan?request_type=patient_triage
   
   Response:
   {
       "regulations": ["HIPAA", "GDPR"],
       "agents": ["AccessControlAgent", "PrivacyAgent", "OutputGuardAgent", "AuditAgent"],
       "actions": ["check_role_permissions", "mask_phi", "redact_pii", "log_event"],
       "policies": [
           {
               "rule_id": "HIPAA_164.502_a",
               "article": "§164.502(a)",
               "principle": "Privacy",
               "requirement": "Minimum necessary use and disclosure",
               "ai_scope": "AI_Privacy_Control"
           }
       ]
   }
   ```

2. **Access Control**:
   ```python
   POST /api/check-access
   
   Request:
   {
       "user_role": "clinician",
       "user_id": "dr_smith_001",
       "patient_id": "patient_12345",
       "resource_type": "patient_data"
   }
   
   Response:
   {
       "access_granted": true,
       "reason": "Role 'clinician' is authorized for patient_triage",
       "audit_id": "audit_abc123"
   }
   ```

3. **PII Masking**:
   ```python
   POST /api/mask-pii
   
   Request:
   {
       "input_text": "Patient John Doe (DOB: 1985-03-15, SSN: 123-45-6789) reports severe chest pain..."
   }
   
   Response:
   {
       "masked_text": "Patient [NAME] (DOB: 1985-03-15, SSN: [SSN]) reports severe chest pain...",
       "pii_detected": [
           {"type": "NAME", "value": "John Doe", "masked": "[NAME]"},
           {"type": "SSN", "value": "123-45-6789", "masked": "[SSN]"}
       ],
       "pii_count": 2
   }
   ```

4. **LLM Processing** (Frontend):
   ```python
   # Frontend calls OpenAI with MASKED text
   llm_output = openai.chat.completions.create(
       model="gpt-4o-mini",
       messages=[{
           "role": "system",
           "content": "You are a triage nurse. Assess urgency."
       }, {
           "role": "user",
           "content": "Patient [NAME] (DOB: 1985-03-15, SSN: [SSN]) reports severe chest pain..."
       }]
   )
   
   # LLM Response:
   {
       "level": "Emergency",
       "reason": "Severe chest pain indicates potential cardiac event",
       "action": "Call emergency services immediately"
   }
   ```

5. **Output Sanitization**:
   ```python
   POST /api/sanitize-output
   
   Request:
   {
       "output_text": "Emergency - Call 911 for patient..."
   }
   
   Response:
   {
       "sanitized_output": "Emergency - Call 911 for patient...",
       "pii_in_output": [],
       "safe_to_store": true
   }
   ```

6. **Audit Trail**:
   ```python
   GET /api/audit-logs?patient_id=patient_12345
   
   Response:
   {
       "logs": [
           {
               "agent": "AccessControlAgent",
               "action": "check_role_permissions",
               "timestamp": "2025-12-18T10:30:00Z",
               "status": "COMPLETED",
               "policy_trace_ids": ["HIPAA_164.502_a"],
               "user_role": "clinician"
           },
           {
               "agent": "PrivacyAgent",
               "action": "mask_phi",
               "timestamp": "2025-12-18T10:30:01Z",
               "status": "COMPLETED",
               "policy_trace_ids": ["HIPAA_164.514", "GDPR_Article_5"],
               "pii_count": 2
           },
           {
               "agent": "OutputGuardAgent",
               "action": "redact_pii",
               "timestamp": "2025-12-18T10:30:05Z",
               "status": "COMPLETED",
               "policy_trace_ids": ["HIPAA_164.502_b"]
           }
       ]
   }
   ```

**Final Output**:
```python
{
    "triage": {
        "level": "Emergency",
        "reason": "Severe chest pain indicates potential cardiac event",
        "recommended_action": "Call emergency services immediately"
    },
    "compliance_status": "PASSED",
    "regulations_applied": ["HIPAA", "GDPR"],
    "pii_protected": true,
    "audit_id": "audit_abc123"
}
```

---

## 🔧 Configuration & Customization

### Adding New Regulations

1. **Place PDF in `policy_generator/input_pdfs/`**

2. **Run PDF-to-JSON converter**:
   ```bash
   python policy_generator/pdf_to_policy_json.py
   ```

3. **Rebuild policy graph**:
   ```bash
   python policy_generator/policy_graph/build_policy_graph.py
   ```

### Adding New Request Types

Edit `policy_generator/request_types.py`:

```python
REQUEST_TYPES["telemedicine_consultation"] = {
    "name": "Telemedicine Consultation",
    "description": "Remote patient consultation via video",
    "regulations": ["HIPAA", "GDPR", "Telemedicine Act"],
    "principles": ["Privacy", "Access Control", "Informed Consent"],
    "required_roles": ["doctor", "telemedicine_provider"],
    "keywords": ["video call", "remote consultation", "telehealth"]
}
```

### Customizing Agents

Modify agent behavior in `agent_graph/nodes.py`:

```python
def privacy_node(state):
    # Add custom PII detection logic
    custom_pii = detect_custom_identifiers(state["input_text"])
    
    # Apply custom masking
    masked = custom_mask_function(state["input_text"], custom_pii)
    
    state["masked_input"] = masked
    return state
```

---

## 🧪 Testing

### Unit Tests

```bash
# Test individual agents
python -m pytest agent_graph/test_privacy.py
python -m pytest agent_graph/test_router.py

# Test policy resolution
python -m pytest policy_generator/policy_graph/test.py

# Test PII detection
python -m pytest security/test_pii.py
```

### Integration Tests

```bash
# Test full compliance workflow
python agent_graph/test_run.py

# Test API endpoints
python app/test_main.py
```

### Manual Testing

```bash
# Test enforcement plan
curl http://localhost:8000/api/enforcement-plan?request_type=patient_triage

# Test PII masking
curl -X POST http://localhost:8000/api/mask-pii \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Patient John Doe (SSN: 123-45-6789)"}'
```

---

## 📈 Monitoring & Observability

### Audit Logs

All compliance actions are logged with:
- **Agent name** (which component performed the action)
- **Action type** (what was done)
- **Policy trace** (which regulations/articles applied)
- **Timestamp** (when it occurred)
- **Status** (success/failure)

### Compliance Metrics

Track:
- **PII detection rate**: How much sensitive data is caught
- **Access denial rate**: How often unauthorized access is blocked
- **Regulation coverage**: Which regulations are most frequently triggered
- **Agent execution time**: Performance bottlenecks

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Compliance status
curl http://localhost:8000/api/compliance/status
```

---

## 🔒 Security Best Practices

1. **Never log raw PII**: All audit logs use masked/pseudonymized data
2. **Encrypt at rest**: Sensitive fields encrypted before storage
3. **HMAC for identifiers**: User/patient IDs pseudonymized in logs
4. **Role-based access**: Strict permission enforcement
5. **Least privilege**: Agents only access necessary data
6. **Immutable audit trail**: Logs cannot be modified post-creation

---

## 🌐 Deployment

### Production Checklist

- [ ] Set environment variables (API keys, encryption keys)
- [ ] Build policy graph from latest regulations
- [ ] Configure allowed roles in `config/config.json`
- [ ] Enable HTTPS for FastAPI backend
- [ ] Set up secure database for audit logs
- [ ] Configure log retention policies
- [ ] Set up monitoring/alerting
- [ ] Test compliance enforcement end-to-end
- [ ] Document incident response procedures

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."
export APP_ENCRYPTION_KEY="<fernet-key>"
export AUDIT_HMAC_SECRET="<secret>"

# Optional
export COMPLIANCE_ENABLED="true"
export LOG_LEVEL="INFO"
export DATABASE_URL="postgresql://..."
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main_langgraph:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📚 Architecture Patterns

### 1. **Policy-as-Code**
Regulations are versioned, testable code (JSON + graph) rather than documentation.

### 2. **Multi-Agent Orchestration**
LangGraph coordinates specialized agents (privacy, access control, audit) rather than monolithic processing.

### 3. **Knowledge Graph Resolution**
Graph traversal determines applicable policies at runtime, supporting new regulations without code changes.

### 4. **Separation of Concerns**
- **Frontend**: User interaction + orchestration
- **Backend**: Compliance middleware + enforcement
- **Policy Layer**: Regulation definitions + resolution
- **Security Layer**: Cryptography + PII detection

### 5. **Audit-First Design**
Every action is logged with policy traceability for regulatory compliance proof.

---

## 🎓 Key Concepts

### Enforcement Plan

A **data structure** returned by the policy graph that specifies:
- Which regulations apply to a request type
- Which agents should be invoked
- Which actions each agent should perform
- Policy trace (regulation article IDs)

### Policy Trace

A **list of regulation IDs** (e.g., `["HIPAA_164.502", "GDPR_Article_6"]`) that justifies why an action was taken. Provides **explainability** and **audit trail**.

### AI Scope

A **categorization** of policy rules:
- **AI_Privacy_Control**: Data minimization, anonymization
- **AI_Access_Control**: Role-based permissions, consent
- **AI_Governance**: Audit, retention, transparency
- **AI_Explainability**: Output explanation, decision rationale

### Masked vs. Sanitized

- **Masked**: Input data with PII removed/tokenized before LLM processing
- **Sanitized**: LLM output with any leaked PII redacted before user display

---

## 🐛 Troubleshooting

### Issue: "Policy graph not found"

**Solution**: Build the graph:
```bash
python policy_generator/policy_graph/build_policy_graph.py
```

### Issue: "Access denied for clinician"

**Solution**: Check role permissions in `config/config.json`:
```json
{
  "access_control": {
    "request_type_permissions": {
      "patient_triage": ["clinician", "doctor", "nurse"]
    }
  }
}
```

### Issue: "PII not detected"

**Solution**: Review regex patterns in `security/pii.py` or enable NLP-based detection with spaCy/medspacy.

### Issue: "Backend connection failed"

**Solution**: Verify backend is running:
```bash
curl http://localhost:8000/api/health
```

---

## 📖 Further Reading

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **HIPAA Compliance**: https://www.hhs.gov/hipaa/
- **GDPR Overview**: https://gdpr.eu/
- **PCI-DSS Standards**: https://www.pcisecuritystandards.org/
- **AI Act (EU)**: https://artificialintelligenceact.eu/

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-regulation`)
3. Commit changes (`git commit -m 'Add CCPA support'`)
4. Push to branch (`git push origin feature/new-regulation`)
5. Open Pull Request

---

## 📄 License

[Your License Here]

---

## 👥 Support

For questions or issues:
- Open GitHub issue
- Contact: [Your Contact Info]

---

## 🎯 Roadmap

- [ ] Add more NLP models for PII detection (BERT-based)
- [ ] Support for additional regulations (CCPA, SOC 2)
- [ ] Real-time monitoring dashboard
- [ ] Automated compliance report generation
- [ ] Integration with EHR systems (FHIR)
- [ ] Multi-tenant support
- [ ] Advanced anonymization techniques (differential privacy)

---

**Built with ❤️ for healthcare compliance automation**
