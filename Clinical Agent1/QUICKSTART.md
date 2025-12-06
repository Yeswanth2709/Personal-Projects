# Quick Start Guide - Clinical AI Assistant

## Step-by-Step Setup (5 minutes)

### 1. Activate Virtual Environment ✅ (Already created)

Open PowerShell in project directory:

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

This may take 2-3 minutes. You'll see packages being installed.

### 3. Get Your Gemini API Key (Free)

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### 4. Configure Your API Key

Create a new file called `.env` (copy from `.env.example`):

```powershell
copy .env.example .env
notepad .env
```

Edit the file and replace `your_gemini_api_key_here` with your actual key:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyD...your_actual_key...
GEMINI_MODEL=gemini-1.5-flash
```

Save and close Notepad.

### 5. Run the Application

```powershell
streamlit run app.py
```

The app will:

- Index the knowledge base documents (takes ~10 seconds first time)
- Launch in your browser automatically
- Be ready to use!

## Your First Demo Scenario

### Scenario: 65-year-old patient with multiple medications

1. **Go to "Patient Context" tab**

   - Age: 65
   - Sex: Male
   - Weight: 80
   - Allergies: `Penicillin`
   - Diagnoses (one per line):
     ```
     Atrial Fibrillation
     Type 2 Diabetes
     Hypertension
     ```
   - Medications (one per line):
     ```
     Warfarin
     Aspirin
     Metformin
     Lisinopril
     Simvastatin
     ```
   - Click "Save Patient Data"

2. **Go to "Drug Interactions" tab**

   - Click "Check Interactions"
   - You'll see HIGH severity warnings for Warfarin + Aspirin!

3. **Go to "Risk Assessment" tab**

   - Click "Calculate Risk Score"
   - See the risk factors and recommendations

4. **Go to "Clinical Q&A" tab**

   - Ask: "What are the side effects of warfarin?"
   - Ask: "How should I monitor a patient on warfarin?"
   - Ask: "What are alternatives to aspirin for cardiovascular protection?"

5. **Go to "Audit Logs" tab**
   - See all your interactions logged
   - Click "Export to CSV" to download

## Common Issues & Fixes

### ❌ ModuleNotFoundError

```powershell
pip install -r requirements.txt --upgrade
```

### ❌ Gemini API Error

- Double-check your API key in `.env`
- Make sure there are no extra spaces
- Verify key is active at https://makersuite.google.com

### ❌ FAISS Installation Failed

```powershell
pip install faiss-cpu --no-cache-dir
```

### ❌ Streamlit Won't Start

```powershell
streamlit cache clear
streamlit run app.py --server.port 8502
```

## Demo Tips

### Impressive Features to Show

1. **Smart Interaction Detection**

   - Show how it catches dangerous drug combinations
   - Highlight severity color coding

2. **Context-Aware Q&A**

   - Ask the same question with and without patient context
   - Show how answers adapt

3. **Risk Scoring**

   - Add more medications to increase risk score
   - Show how factors are weighted

4. **Audit Trail**
   - Demonstrate compliance logging
   - Show CSV export feature

### Good Demo Questions

- "What is the mechanism of action of metformin?"
- "When should warfarin be discontinued before surgery?"
- "What are drug interactions with aspirin?"
- "How do I manage a patient with renal impairment on lisinopril?"
- "What are the Beers Criteria medications to avoid in elderly?"

## Architecture to Highlight

1. **Abstract LLM Service**: Easy to swap Gemini for OpenAI/Claude
2. **Multi-Agent System**: Coordinator routes to specialized agents
3. **RAG Implementation**: Vector search over clinical guidelines
4. **Safety Guardrails**: Input validation, output filtering, disclaimers
5. **Compliance Logging**: Every action audited

## Switching to OpenAI (Optional)

If you have OpenAI API key instead:

1. Edit `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your_key...
OPENAI_MODEL=gpt-4
```

2. Install OpenAI:

```powershell
pip install openai
```

3. Restart app

## Next Steps

- Add more drug guidelines to `knowledge_base/`
- Customize interaction rules in `services/drug_interaction_service.py`
- Adjust risk weights in `services/risk_model_service.py`
- Try different LLM models by changing `GEMINI_MODEL` in `.env`

## Need Help?

Check the full `README.md` for detailed documentation!

---

🎉 **You're ready to demo!** The system is fully functional and production-quality for a hackathon prototype.
