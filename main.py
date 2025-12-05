from typing import Optional, Dict, Any, List
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import httpx
import json

from clinical_data import ClinicalDataStore
from graph_workflow import run_workflow

# OpenAI client (uses OPENAI_API_KEY env variable)
#client = OpenAI()


# -------------------------------------------------------------
# WORKFLOW EXECUTION (unchanged)
# -------------------------------------------------------------
def run_clinical_workflow(query: str, patient_id: Optional[str]) -> str:
    """
    Runs the LangGraph workflow and returns the clinician-facing summary.
    """
    if not query.strip():
        return "Please enter a clinical question."

    state: Dict[str, Any] = run_workflow(query, patient_id or None)
    return state.get(
        "final_answer",
        "No final answer produced. Please check backend / logs.",
    )


# -------------------------------------------------------------
# VOICE → TEXT (OpenAI Whisper / gpt-4o-transcribe)
# -------------------------------------------------------------


# Re-use the same style you already have for DeepSeek
http_client = httpx.Client(verify=False)

client = OpenAI(
    base_url="https://genailab.tcs.in",   # NOTE: no /v1 here to start with
    api_key="xxxxxxxxxxxxxxxxxx",
    http_client=http_client,
)

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    import tempfile
    try:
        # Save bytes -> temp wav file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            # This will call POST https://genailab.tcs.in/audio/transcriptions
            transcript = client.audio.transcriptions.create(
                model="azure/genailab-maas-whisper",  # use the exact model id they gave
                file=f,
            )

        text = getattr(transcript, "text", None) or transcript.get("text", "")
        return text.strip()
    except Exception as e:
        print("Transcription error:", e)
        return ""

# -------------------------------------------------------------
# PATIENT FORM HELPERS (unchanged)
# -------------------------------------------------------------
def load_patient_for_edit(selected_id: Optional[str]) -> List[str]:
    """
    Load an existing patient into the edit form.
    Returns 6 fields in order:
    [patient_id, age, gender, allergies, conditions, medications]
    """
    if not selected_id:
        return ["", "", "", "", "", ""]

    row = ClinicalDataStore.get_patient_row(selected_id) or {}

    return [
        row.get("patient_id", selected_id),
        str(row.get("age", "")),
        row.get("gender", ""),
        row.get("allergies", ""),
        row.get("conditions", ""),
        row.get("medications", ""),
    ]


def on_patient_dropdown_change(selected_id: Optional[str]):
    """
    When user selects a patient:
    - load details into the form
    - update current patient badges
    - keep the original id for rename cascade
    - Returns blank string to clear the analysis output.
    """
    (
        pid,
        age,
        gender,
        allergies,
        conditions,
        meds,
    ) = load_patient_for_edit(selected_id)

    if selected_id:
        badge_main = f"Demo Patient: **{selected_id}**"
        badge_workspace = f"Current Patient: **{selected_id}**"
    else:
        badge_main = "Demo Patient: –"
        badge_workspace = "Current Patient: –"

    original_id = selected_id or ""

    # 6 form fields + header badge + workspace badge + hidden original id + CLEAR OUTPUT
    return (
        pid,
        age,
        gender,
        allergies,
        conditions,
        meds,
        badge_main,
        badge_workspace,
        original_id,
        "",  # Clear final_answer
    )


def save_patient(
    original_patient_id: str,
    patient_id: str,
    age: str,
    gender: str,
    allergies: str,
    conditions: str,
    medications: str,
):
    """
    Upsert patient into patients.csv.
    Returns blank string to clear the analysis summary.
    """
    if not patient_id.strip():
        return (
            "❌ Patient ID is required.",
            ClinicalDataStore.list_patient_ids(),  # dropdown choices unchanged
            "Demo Patient: –",
            "Current Patient: –",
            original_patient_id,
            "",  # Clear output on error
        )

    new_id = patient_id.strip()
    orig_id = (original_patient_id or "").strip()

    # 1) Rename cascade if needed
    if orig_id and orig_id != new_id:
        ClinicalDataStore.rename_patient_id(orig_id, new_id)

    # 2) Upsert patient row
    ClinicalDataStore.upsert_patient(
        {
            "patient_id": new_id,
            "age": age.strip(),
            "gender": gender.strip(),
            "allergies": allergies.strip(),
            "conditions": conditions.strip(),
            "medications": medications.strip(),
        }
    )

    # 3) Refresh dropdown
    ids = ClinicalDataStore.list_patient_ids()

    badge_main = f"Demo Patient: **{new_id}**"
    badge_workspace = f"Current Patient: **{new_id}**"

    # status, ids (for dropdown), badges, new original id, cleared output
    return (
        "✅ Patient saved/updated.",
        ids,
        badge_main,
        badge_workspace,
        new_id,  # new original id
        "",  # Clear output on save
    )


def clear_query_and_output():
    """Returns empty strings to clear the query box and the output box."""
    return "", ""


# -------------------------------------------------------------
# STREAMLIT APP
# -------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Clinical AI Assistant",
        page_icon="🧠",
        layout="wide",
    )

    # Simple global styling (light, clinical, compact inputs)
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f4f6f9;
        }
        /* Shrink text inputs a bit */
        div[data-testid="stTextInput"] input {
            height: 32px;
            padding: 4px 8px;
            font-size: 0.9rem;
        }
        div[data-testid="stSelectbox"] select {
            height: 32px;
            padding: 2px 6px;
            font-size: 0.9rem;
        }
        div[data-testid="stTextArea"] textarea {
            font-size: 0.9rem;
        }
        .subtle-card {
            background: #ffffff;
            padding: 1rem 1.25rem;
            border-radius: 0.75rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 10px rgba(15,23,42,0.05);
        }
        .pill {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.8rem;
            background: #e0f2fe;
            color: #0369a1;
            border: 1px solid #bae6fd;
            margin-right: 0.35rem;
            margin-bottom: 0.25rem;
        }
        .pill-warn {
            background: #fef3c7;
            color: #92400e;
            border-color: #fde68a;
        }
        .pill-safe {
            background: #dcfce7;
            color: #166534;
            border-color: #bbf7d0;
        }
        .page-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            color: #111827;
        }
        .page-subtitle {
            color: #4b5563;
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Always fetch latest patient IDs (so new saves show up)
    patient_ids = ClinicalDataStore.list_patient_ids()

    # Sidebar navigation
    st.sidebar.title("🧠 Clinical AI")
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Welcome", "🧑‍⚕️ Clinical Assistant"],
        index=0,
    )

    # ------------- SESSION STATE INIT -------------
    if "selected_patient_id" not in st.session_state:
        st.session_state.selected_patient_id = patient_ids[0] if patient_ids else ""
    if "last_selected_patient_id" not in st.session_state:
        st.session_state.last_selected_patient_id = st.session_state.selected_patient_id

    if "patient_id" not in st.session_state:
        (
            pid,
            age,
            gender,
            allergies,
            conditions,
            meds,
            badge_main,
            badge_workspace,
            original_id,
            cleared,
        ) = on_patient_dropdown_change(st.session_state.selected_patient_id or None)

        st.session_state.patient_id = pid
        st.session_state.age = age
        st.session_state.gender = gender
        st.session_state.allergies = allergies
        st.session_state.conditions = conditions
        st.session_state.medications = meds
        st.session_state.original_patient_id = original_id
        st.session_state.demo_patient_badge = badge_main
        st.session_state.current_patient_badge = badge_workspace
        st.session_state.final_answer = cleared
        st.session_state.save_status = ""

    if "query" not in st.session_state:
        st.session_state.query = ""
    if "final_answer" not in st.session_state:
        st.session_state.final_answer = ""
    if "save_status" not in st.session_state:
        st.session_state.save_status = ""
    if "demo_patient_badge" not in st.session_state:
        st.session_state.demo_patient_badge = "Demo Patient: –"
    if "current_patient_badge" not in st.session_state:
        st.session_state.current_patient_badge = "Current Patient: –"

    # ---------------------------------------------------------
    # PAGE 1: WELCOME / OVERVIEW
    # ---------------------------------------------------------
    if page == "🏠 Welcome":
        st.markdown('<div class="page-title">🏥 Clinical AI Assistant</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">AI-powered clinical Q&A, drug interaction validation, and guideline alignment.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        col_top_left, col_top_right = st.columns([2, 1])

        with col_top_left:
            st.markdown(
                """
                ### 👋 Welcome

                This dashboard demonstrates a **LangGraph-based multi-agent AI system** that supports:

                - **Clinical Q&A** using patient context  
                - **Drug interaction validation** using medication lists  
                - **Guideline-style reasoning** with multi-step agents  

                Everything here runs on **synthetic data** and **LLM-generated reasoning** — it's a safe playground for designing clinical agents.
                """
            )

            st.info(
                "⚠️ This is **not** a medical device. Do **not** use it for real patients or clinical decisions."
            )

        with col_top_right:
            st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
            st.markdown("#### Snapshot")
            st.metric("Registered Patients", len(patient_ids))
            st.metric("Active Agents", 3)
            st.metric("Mode", "Simulation")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("🧩 How the multi-agent workflow works")

        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            st.markdown("#### 1️⃣ Clinical Query Agent")
            st.write(
                "- Parses the clinician’s free-text question\n"
                "- Extracts drugs, conditions, and intent\n"
                "- Normalizes terms into structured state"
            )
        with col_w2:
            st.markdown("#### 2️⃣ Safety & Interaction Agent")
            st.write(
                "- Checks current medications\n"
                "- Flags high-risk interactions\n"
                "- Suggests monitoring and alternatives"
            )
        with col_w3:
            st.markdown("#### 3️⃣ Guideline Agent")
            st.write(
                "- Aligns reasoning with guidelines\n"
                "- Produces clinician-facing summary\n"
                "- Adds caveats and follow-ups"
            )

        st.markdown("---")

        st.subheader("💡 Try questions like")

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.code('Can I combine warfarin and aspirin for this patient?', language=None)
            st.code('How should I monitor for bleeding risk on dual therapy?', language=None)
        with col_q2:
            st.code('Is ibuprofen safe with this patient’s medications?', language=None)
            st.code('What guidelines apply for anticoagulation in AF with diabetes?', language=None)

        st.markdown("---")
        st.success("Ready? Switch to **🧑‍⚕️ Clinical Assistant** in the sidebar to start using the tool.")

    # ---------------------------------------------------------
    # PAGE 2: CLINICAL ASSISTANT
    # ---------------------------------------------------------
    else:
        st.markdown('<div class="page-title">🧑‍⚕️ Clinical Assistant</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Work with patient context, ask clinical questions (by text or voice), and review AI reasoning.</div>',
            unsafe_allow_html=True,
        )

        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown('<span class="pill">🟡 Simulation Mode (No Backend)</span>', unsafe_allow_html=True)
        with b2:
            st.markdown(f'<span class="pill">{st.session_state.demo_patient_badge}</span>', unsafe_allow_html=True)
        with b3:
            st.markdown('<span class="pill">🤖 Agents Available: 3</span>', unsafe_allow_html=True)

        st.markdown("---")

        left_col, right_col = st.columns([1, 2])

        # LEFT: Patient Context
        with left_col:
            st.markdown("### 👤 Patient Context")

            st.session_state.selected_patient_id = st.selectbox(
                "Select Patient",
                options=patient_ids if patient_ids else [""],
                index=patient_ids.index(st.session_state.selected_patient_id)
                if st.session_state.selected_patient_id in patient_ids and patient_ids
                else 0,
            )

            # If the selected patient changed, reload form fields
            if st.session_state.selected_patient_id != st.session_state.last_selected_patient_id:
                (
                    pid,
                    age,
                    gender,
                    allergies,
                    conditions,
                    meds,
                    badge_main,
                    badge_workspace,
                    original_id,
                    cleared,
                ) = on_patient_dropdown_change(st.session_state.selected_patient_id or None)

                st.session_state.patient_id = pid
                st.session_state.age = age
                st.session_state.gender = gender
                st.session_state.allergies = allergies
                st.session_state.conditions = conditions
                st.session_state.medications = meds
                st.session_state.original_patient_id = original_id
                st.session_state.demo_patient_badge = badge_main
                st.session_state.current_patient_badge = badge_workspace
                st.session_state.final_answer = cleared
                st.session_state.save_status = ""
                st.session_state.last_selected_patient_id = st.session_state.selected_patient_id

            with st.container():
                st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
                st.markdown("#### Patient Details")

                col_pid, col_age = st.columns(2)
                with col_pid:
                    st.session_state.patient_id = st.text_input(
                        "Patient ID", value=st.session_state.patient_id
                    )
                with col_age:
                    st.session_state.age = st.text_input(
                        "Age", value=st.session_state.age
                    )

                st.session_state.gender = st.selectbox(
                    "Gender",
                    options=["Male", "Female", "Other"],
                    index=(
                        ["Male", "Female", "Other"].index(st.session_state.gender)
                        if st.session_state.gender in ["Male", "Female", "Other"]
                        else 0
                    ),
                )

                st.markdown("#### Clinical Overview")
                st.session_state.allergies = st.text_input(
                    "Known Allergies",
                    value=st.session_state.allergies,
                    placeholder="e.g., Penicillin, Sulfa",
                )
                st.session_state.conditions = st.text_input(
                    "Medical Conditions",
                    value=st.session_state.conditions,
                    placeholder="e.g., Hypertension, Diabetes",
                )
                st.session_state.medications = st.text_input(
                    "Current Medications",
                    value=st.session_state.medications,
                    placeholder="e.g., Aspirin, Metformin",
                )

                if st.button("Save / Update Patient", use_container_width=True):
                    (
                        status_msg,
                        ids_after,
                        badge_main,
                        badge_workspace,
                        new_orig_id,
                        cleared,
                    ) = save_patient(
                        st.session_state.original_patient_id,
                        st.session_state.patient_id,
                        st.session_state.age,
                        st.session_state.gender,
                        st.session_state.allergies,
                        st.session_state.conditions,
                        st.session_state.medications,
                    )
                    st.session_state.save_status = status_msg
                    # Update state to reflect new ID
                    st.session_state.selected_patient_id = new_orig_id
                    st.session_state.last_selected_patient_id = new_orig_id
                    st.session_state.original_patient_id = new_orig_id
                    st.session_state.demo_patient_badge = badge_main
                    st.session_state.current_patient_badge = badge_workspace
                    st.session_state.final_answer = cleared
                    st.experimental_rerun()

                if st.session_state.save_status:
                    st.markdown(st.session_state.save_status)

                st.markdown("</div>", unsafe_allow_html=True)

        # RIGHT: Clinical Reasoning Workspace
        with right_col:
            st.markdown("### 🩺 Clinical Reasoning Workspace")
            st.markdown(st.session_state.current_patient_badge)

            st.markdown(
                "You can either **type** your question or use **voice input**. "
                "The LangGraph workflow will use the active patient's context and synthetic data."
            )

            # --- Voice + Text input section ---
            st.markdown("#### Clinical Question")

            vcol1, vcol2 = st.columns([2, 1])

            with vcol1:
                st.session_state.query = st.text_area(
                    "Type your question",
                    value=st.session_state.query,
                    placeholder='e.g., "Can I safely combine warfarin and aspirin for this patient?"',
                    height=140,
                )

            with vcol2:
                st.markdown("**Or use voice:**")
                audio = mic_recorder(
                    key="mic",
                    start_prompt="🎙️ Start recording",
                    stop_prompt="⏹️ Stop",
                    just_once=False,
                    use_container_width=True,
                )

                if audio is not None:
                    st.success("Audio captured.")
                    if st.button("Transcribe Voice", use_container_width=True):
                        text = transcribe_audio_bytes(audio["bytes"])
                        if text:
                            st.session_state.query = text
                            st.success("✅ Voice converted to text and filled into the question box.")
                        else:
                            st.error("❌ Could not transcribe audio. Please try again.")

            # --- Existing buttons (logic unchanged) ---
            rcol1, rcol2 = st.columns(2)
            with rcol1:
                if st.button("Analyze Query", use_container_width=True):
                    answer = run_clinical_workflow(
                        st.session_state.query,
                        st.session_state.selected_patient_id or None,
                    )
                    st.session_state.final_answer = answer
            with rcol2:
                if st.button("Clear", use_container_width=True):
                    q, out = clear_query_and_output()
                    st.session_state.query = q
                    st.session_state.final_answer = out

        st.markdown("---")

        # ------------- BOTTOM: ANALYSIS RESULT -------------
        st.subheader("📋 Clinical Analysis Result")

        if st.session_state.final_answer:
            st.markdown(st.session_state.final_answer)
        else:
            st.info(
                "Analysis results will appear here after clicking **Analyze Query**."
            )


# -------------------------------------------------------------
# LAUNCH
# -------------------------------------------------------------
if __name__ == "__main__":
    main()