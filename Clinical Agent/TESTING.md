# Testing Guide for Clinical Q&A System

## Quick Test Scenarios

### Scenario 1: High-Risk Patient with Multiple Interactions

**Setup Patient:**

```
Patient ID: TEST-001
Age: 72
Sex: Male
Allergies: penicillin, sulfa
Diagnoses: heart failure, kidney disease, diabetes
Current Medications:
  - warfarin
  - ibuprofen
  - metformin
  - lisinopril
  - spironolactone
Renal Impairment: ✓
```

**Expected Results:**

- Drug Interaction Check:
  - warfarin + ibuprofen → HIGH severity (bleeding risk)
  - lisinopril + spironolactone → MEDIUM severity (hyperkalemia)
  - ibuprofen + heart failure → MEDIUM severity (fluid retention)
  - ibuprofen + kidney disease → HIGH severity (AKI risk)
- Risk Score:
  - Expected: HIGH (score ~70-85)
  - Factors: Age ≥65, polypharmacy (5 meds), renal impairment, high-severity interactions

**Test Actions:**

1. Enter patient data in tab 1, save
2. Go to tab 3, click "Check Interactions"
3. Verify 4+ interactions detected
4. Go to tab 4, click "Compute Risk Score"
5. Verify HIGH risk with appropriate factors
6. Go to tab 2, ask: "What monitoring is needed for warfarin?"
7. Check tab 5 for audit logs

---

### Scenario 2: Moderate Risk with Drug-Allergy Conflict

**Setup Patient:**

```
Patient ID: TEST-002
Age: 45
Sex: Female
Allergies: penicillin
Diagnoses: pneumonia
Current Medications:
  - lisinopril
  - levothyroxine
```

**Additional Medications to Check:**

```
amoxicillin
```

**Expected Results:**

- Drug Interaction Check:
  - amoxicillin + penicillin allergy → HIGH severity (CONTRAINDICATED)
- Risk Score:
  - Expected: LOW-MODERATE (score ~20-30)

**Test Actions:**

1. Enter patient with penicillin allergy
2. In tab 3, add "amoxicillin" to additional medications
3. Click "Check Interactions"
4. Verify HIGH severity drug-allergy interaction
5. Ask in Q&A: "What antibiotics are safe in penicillin allergy?"

---

### Scenario 3: Polypharmacy with Multiple Interactions

**Setup Patient:**

```
Patient ID: TEST-003
Age: 68
Sex: Male
Current Medications:
  - simvastatin
  - clarithromycin
  - digoxin
  - furosemide
  - clopidogrel
  - omeprazole
Hepatic Impairment: ✓
```

**Expected Results:**

- Interactions:
  - simvastatin + clarithromycin → HIGH (rhabdomyolysis risk)
  - digoxin + furosemide → MEDIUM (digoxin toxicity risk)
  - clopidogrel + omeprazole → MEDIUM (reduced effectiveness)
- Risk Score:
  - Expected: HIGH (score ~65-80)
  - Factors: Age ≥65, polypharmacy (6 meds), hepatic impairment, multiple interactions

---

### Scenario 4: Low Risk Young Patient

**Setup Patient:**

```
Patient ID: TEST-004
Age: 28
Sex: Female
Current Medications:
  - levothyroxine
Pregnancy: ✓
```

**Expected Results:**

- No interactions detected
- Risk Score: LOW (score ~12-17)
- Factors: Pregnancy status, minimal medications

---

## Feature Testing Checklist

### Tab 1: Patient & Medications

- [ ] Enter all patient fields
- [ ] Add multiple allergies (one per line)
- [ ] Add multiple diagnoses (one per line)
- [ ] Add multiple medications (one per line)
- [ ] Toggle clinical flags
- [ ] Save context
- [ ] Verify saved in sidebar
- [ ] Clear and re-enter data

### Tab 2: Clinical Q&A

- [ ] Ask a question about warfarin
- [ ] Ask a question about diabetes
- [ ] Ask a question about hypertension
- [ ] Verify patient context is mentioned in response
- [ ] Verify disclaimer appears
- [ ] Check conversation history maintained
- [ ] Clear chat history

### Tab 3: Drug Interaction Check

- [ ] Check interactions with current meds only
- [ ] Add additional medications to check
- [ ] Verify high-severity interactions show as red/error
- [ ] Verify medium-severity as orange/warning
- [ ] Verify low-severity as blue/info
- [ ] Expand details for each interaction
- [ ] Check management advice provided

### Tab 4: Risk Prediction

- [ ] Compute risk score
- [ ] Verify score 0-100 displayed
- [ ] Verify label (Low/Moderate/High) matches score
- [ ] Check contributing factors listed
- [ ] Verify recommendations provided
- [ ] Test with different patient profiles

### Tab 5: Audit & Logs

- [ ] View recent events
- [ ] Change number of records shown
- [ ] Verify events from previous tabs appear
- [ ] Check timestamps are correct
- [ ] Download CSV export
- [ ] Open CSV and verify format

---

## Edge Cases to Test

### Empty States

- [ ] No patient context - tabs should handle gracefully
- [ ] No medications - should show "No interactions"
- [ ] No interactions found - should display success message
- [ ] No audit logs - should show informational message

### Validation

- [ ] Age = 0 or negative (should handle gracefully)
- [ ] Empty medication list with interaction check
- [ ] Special characters in medication names
- [ ] Very long patient ID

### Normalization

- [ ] Test drug aliases: "Motrin" should match "ibuprofen"
- [ ] Test case variations: "WARFARIN" vs "warfarin"
- [ ] Test with extra spaces in medication names

---

## Performance Tests

- [ ] Add 10+ medications - check interaction calculation speed
- [ ] Add 100+ audit log entries - check display performance
- [ ] Multiple rapid Q&A queries
- [ ] Large text input in Q&A

---

## Integration Tests (with OpenAI)

If `OPENAI_API_KEY` is configured:

- [ ] Verify LLM responses are different from stub responses
- [ ] Check response quality and format
- [ ] Verify disclaimers still appear
- [ ] Test error handling if API fails

---

## User Experience Tests

- [ ] Clear visual hierarchy
- [ ] Appropriate color coding (red/orange/green)
- [ ] Disclaimer visible and prominent
- [ ] Tooltips and help text present
- [ ] Responsive layout on different screen sizes
- [ ] Loading spinners appear during processing
- [ ] Success/error messages clear

---

## Data Integrity Tests

- [ ] Patient context persists across tabs
- [ ] Interaction results saved in session state
- [ ] Risk score saved and accessible
- [ ] Audit logs persist in database
- [ ] Exported CSV matches displayed data

---

## Test Results Template

```
Test Date: ___________
Tester: ___________

| Scenario | Status | Notes |
|----------|--------|-------|
| Scenario 1: High Risk | ✓/✗ | |
| Scenario 2: Allergy Check | ✓/✗ | |
| Scenario 3: Polypharmacy | ✓/✗ | |
| Scenario 4: Low Risk | ✓/✗ | |

Issues Found:
1.
2.
3.

Recommendations:
1.
2.
3.
```

---

## Automated Testing (Future)

To add automated tests, create `test_services.py`:

```python
import pytest
from models import Patient
from services.drug_interaction_service import DrugInteractionService
from services.risk_scoring_service import RiskScoringService

def test_warfarin_ibuprofen_interaction():
    patient = Patient(current_medications=["warfarin", "ibuprofen"])
    interactions = DrugInteractionService.check_interactions(patient)
    assert len(interactions) == 1
    assert interactions[0].severity == "high"

def test_risk_score_high_risk_patient():
    patient = Patient(
        age=75,
        current_medications=["med1", "med2", "med3", "med4", "med5", "med6"],
        renal_impairment=True
    )
    score = RiskScoringService.score_patient(patient, [])
    assert score.label == "High"
    assert score.score >= 60
```

Run with: `pytest test_services.py`
