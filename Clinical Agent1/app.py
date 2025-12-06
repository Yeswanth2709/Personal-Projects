"""
Streamlit UI for Clinical AI Assistant.
Main application entry point with multi-tab interface.
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Any
import pandas as pd

from config import APP_TITLE, MEDICAL_DISCLAIMER, SEVERITY_COLORS
from models import Patient, AgentState
from agents import get_coordinator_agent
from services.audit_service import get_audit_service
from services.rag_service import get_rag_service


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services (cached)."""
    rag = get_rag_service()
    coordinator = get_coordinator_agent()
    audit = get_audit_service()
    return rag, coordinator, audit

rag_service, coordinator, audit_service = init_services()


# Initialize session state
if "patient" not in st.session_state:
    st.session_state.patient = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "interaction_results" not in st.session_state:
    st.session_state.interaction_results = None

if "risk_score" not in st.session_state:
    st.session_state.risk_score = None


def render_disclaimer():
    """Render medical disclaimer banner."""
    st.warning(MEDICAL_DISCLAIMER)


def render_sidebar():
    """Render sidebar with app info and patient summary."""
    with st.sidebar:
        st.title("🏥 " + APP_TITLE)
        st.markdown("*TCS AI Fridays Hackathon Demo*")
        st.markdown("---")
        
        # Patient summary
        if st.session_state.patient:
            st.subheader("Current Patient")
            patient = st.session_state.patient
            st.info(f"""
**Age:** {patient.age} years  
**Sex:** {patient.sex}  
**Medications:** {len(patient.medications)}  
**Allergies:** {len(patient.allergies)}  
**Diagnoses:** {len(patient.diagnoses)}
            """)
            
            if st.button("Clear Patient Data", type="secondary"):
                st.session_state.patient = None
                st.rerun()
        else:
            st.info("👤 No patient data loaded\n\nGo to 'Patient Context' tab to enter patient information.")
        
        st.markdown("---")
        st.caption("v1.0.0 | Demo Only")


def tab_patient_context():
    """Patient context capture tab."""
    st.header("👤 Patient Context")
    render_disclaimer()
    
    st.markdown("### Enter Patient Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age (years)", min_value=0, max_value=120, value=65)
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
        
    with col2:
        pregnancy_status = None
        if sex == "Female":
            pregnancy_status = st.checkbox("Pregnant")
        
        renal_impairment = st.checkbox("Renal Impairment")
        hepatic_impairment = st.checkbox("Hepatic Impairment")
    
    st.markdown("---")
    
    # Allergies
    st.subheader("Allergies")
    allergies_input = st.text_area(
        "Enter allergies (one per line)",
        help="List known drug allergies",
        height=100
    )
    allergies = [a.strip() for a in allergies_input.split("\n") if a.strip()]
    
    # Diagnoses
    st.subheader("Current Diagnoses")
    diagnoses_input = st.text_area(
        "Enter diagnoses (one per line)",
        help="List current medical conditions",
        height=100
    )
    diagnoses = [d.strip() for d in diagnoses_input.split("\n") if d.strip()]
    
    # Medications
    st.subheader("Current Medications")
    medications_input = st.text_area(
        "Enter medications (one per line)",
        help="List current medications",
        height=150
    )
    medications = [m.strip() for m in medications_input.split("\n") if m.strip()]
    
    # Save patient data
    if st.button("💾 Save Patient Data", type="primary"):
        patient = Patient(
            age=age,
            sex=sex,
            weight=weight,
            allergies=allergies,
            diagnoses=diagnoses,
            medications=medications,
            pregnancy_status=pregnancy_status,
            renal_impairment=renal_impairment,
            hepatic_impairment=hepatic_impairment
        )
        st.session_state.patient = patient
        st.success("✅ Patient data saved successfully!")
        st.rerun()


def tab_clinical_qa():
    """Clinical Q&A chat tab."""
    st.header("💬 Clinical Q&A Chat")
    render_disclaimer()
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a clinical question..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Create agent state
                state = AgentState(patient=st.session_state.patient)
                state.current_query = prompt
                
                # Process through coordinator
                result_state = coordinator.process_qa_only(state)
                
                # Get response
                if result_state.messages:
                    response = result_state.messages[-1].content
                else:
                    response = "I'm sorry, I couldn't generate a response. Please try again."
                
                st.markdown(response)
                
                # Add to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


def tab_drug_interaction():
    """Drug interaction validation tab."""
    st.header("💊 Drug Interaction Validation")
    render_disclaimer()
    
    if not st.session_state.patient:
        st.warning("⚠️ Please enter patient information in the 'Patient Context' tab first.")
        return
    
    patient = st.session_state.patient
    
    st.markdown(f"""
### Current Patient
- **Medications:** {', '.join(patient.medications) if patient.medications else 'None'}
- **Allergies:** {', '.join(patient.allergies) if patient.allergies else 'None'}
    """)
    
    if not patient.medications:
        st.info("No medications to check. Please add medications in the Patient Context tab.")
        return
    
    if st.button("🔍 Check Interactions", type="primary"):
        with st.spinner("Analyzing drug interactions..."):
            # Create agent state and run interaction check
            state = AgentState(patient=patient)
            result_state = coordinator.process_interaction_check(state)
            
            # Store results
            st.session_state.interaction_results = result_state.agent_outputs.get("interaction_agent", {})
    
    # Display results
    if st.session_state.interaction_results:
        results = st.session_state.interaction_results
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Issues", results['total_issues'])
        with col2:
            st.metric("High Severity", results['high_severity_count'])
        with col3:
            st.metric("Medium Severity", results['medium_severity_count'])
        with col4:
            st.metric("Low Severity", results['low_severity_count'])
        
        st.markdown("---")
        
        # Drug-Drug Interactions
        if results['drug_interactions']:
            st.subheader(f"🔄 Drug-Drug Interactions ({len(results['drug_interactions'])})")
            
            for interaction in results['drug_interactions']:
                severity = interaction.severity
                color = SEVERITY_COLORS.get(severity, "#FFFFFF")
                
                with st.expander(f"{'🔴' if severity=='high' else '🟡' if severity=='medium' else '🟢'} {interaction.drug1} + {interaction.drug2}", expanded=(severity=="high")):
                    st.markdown(f"""
**Severity:** <span style="background-color: {color}; padding: 2px 8px; border-radius: 4px;">{severity.upper()}</span>

**Interaction Type:** {interaction.interaction_type}

**Explanation:**  
{interaction.explanation}

**Management:**  
{interaction.management}
                    """, unsafe_allow_html=True)
        
        # Allergy Concerns
        if results['allergy_concerns']:
            st.markdown("---")
            st.subheader(f"⚠️ Allergy Concerns ({len(results['allergy_concerns'])})")
            
            for concern in results['allergy_concerns']:
                severity = concern.severity
                color = SEVERITY_COLORS.get(severity, "#FFFFFF")
                
                with st.expander(f"{'🔴' if severity=='high' else '🟡' if severity=='medium' else '🟢'} {concern.medication}", expanded=(severity=="high")):
                    st.markdown(f"""
**Severity:** <span style="background-color: {color}; padding: 2px 8px; border-radius: 4px;">{severity.upper()}</span>

**Known Allergy:** {concern.allergy}

**Explanation:**  
{concern.explanation}

**Alternative Medications:**  
{', '.join(concern.alternative_medications)}
                    """, unsafe_allow_html=True)


def tab_risk_assessment():
    """Risk assessment tab."""
    st.header("📊 Adverse Reaction Risk Assessment")
    render_disclaimer()
    
    if not st.session_state.patient:
        st.warning("⚠️ Please enter patient information in the 'Patient Context' tab first.")
        return
    
    patient = st.session_state.patient
    
    if st.button("📈 Calculate Risk Score", type="primary"):
        with st.spinner("Calculating risk score..."):
            # Create agent state and run risk assessment
            state = AgentState(patient=patient)
            result_state = coordinator.process_risk_assessment(state)
            
            # Store results
            st.session_state.risk_score = result_state.risk_score
            st.session_state.interaction_results = result_state.agent_outputs.get("interaction_agent", {})
    
    # Display risk score
    if st.session_state.risk_score:
        risk_score = st.session_state.risk_score
        
        # Risk score gauge
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
### Overall Risk Score
<h1 style="color: {'#FF6B6B' if risk_score.risk_level=='High' else '#FFD700' if risk_score.risk_level=='Moderate' else '#90EE90'};">
{risk_score.overall_score:.1f}/100
</h1>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Risk Level", risk_score.risk_level)
        
        with col3:
            st.metric("Factors", len(risk_score.contributing_factors))
        
        # Progress bar
        st.progress(risk_score.overall_score / 100)
        
        st.markdown("---")
        
        # Contributing factors
        if risk_score.contributing_factors:
            st.subheader("📋 Contributing Factors")
            
            # Create dataframe
            factors_data = []
            for factor in risk_score.contributing_factors:
                factors_data.append({
                    "Factor": factor['factor'],
                    "Value": factor['value'],
                    "Impact": factor['impact'].upper(),
                    "Contribution": f"{factor['contribution']:.1f}"
                })
            
            df = pd.DataFrame(factors_data)
            st.dataframe(df, use_container_width=True)
        
        # Recommendations
        if risk_score.recommendations:
            st.markdown("---")
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(risk_score.recommendations, 1):
                st.markdown(f"{i}. {rec}")


def tab_audit_logs():
    """Audit logs tab."""
    st.header("📝 Audit Logs")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        event_filter = st.selectbox("Event Type", ["All", "qa", "interaction_check", "risk_assessment", "error"])
    with col2:
        limit = st.number_input("Number of Records", min_value=10, max_value=500, value=50)
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get logs
    event_type = None if event_filter == "All" else event_filter
    logs = audit_service.get_recent_logs(limit=limit, event_type=event_type)
    
    # Statistics
    stats = audit_service.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", stats['total_events'])
    with col2:
        st.metric("High Risk Events", stats['high_risk_events'])
    with col3:
        st.metric("Last 24h Activity", stats['recent_activity_24h'])
    with col4:
        qa_count = stats['events_by_type'].get('qa', 0)
        st.metric("Q&A Events", qa_count)
    
    st.markdown("---")
    
    # Display logs
    if logs:
        for log in logs:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            risk_badge = ""
            if log['risk_level']:
                color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(log['risk_level'], "⚪")
                risk_badge = f" {color}"
            
            with st.expander(f"{timestamp} | {log['event_type']}{risk_badge} | {log['summary']}"):
                st.json(log['details'])
    else:
        st.info("No audit logs found.")
    
    # Export button
    st.markdown("---")
    if st.button("📥 Export to CSV"):
        from pathlib import Path
        export_path = Path("audit_logs_export.csv")
        audit_service.export_to_csv(export_path, event_type=event_type)
        st.success(f"✅ Exported to {export_path}")


# Main app
def main():
    render_sidebar()
    
    # Create tabs
    tabs = st.tabs([
        "👤 Patient Context",
        "💬 Clinical Q&A",
        "💊 Drug Interactions",
        "📊 Risk Assessment",
        "📝 Audit Logs"
    ])
    
    with tabs[0]:
        tab_patient_context()
    
    with tabs[1]:
        tab_clinical_qa()
    
    with tabs[2]:
        tab_drug_interaction()
    
    with tabs[3]:
        tab_risk_assessment()
    
    with tabs[4]:
        tab_audit_logs()


if __name__ == "__main__":
    main()
