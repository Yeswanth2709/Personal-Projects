"""
AI-Powered Clinical Q&A and Drug Interaction Validation System
Streamlit Application
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import json

from config import Config
from models import Patient, ClinicalQuestion
from services.llm_service import ClinicalLLMService
from services.drug_interaction_service import DrugInteractionService
from services.risk_scoring_service import RiskScoringService
from services.audit_service import AuditService

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    layout=Config.LAYOUT,
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services (cached)."""
    return {
        'llm': ClinicalLLMService(),
        'drug_interaction': DrugInteractionService(),
        'risk_scoring': RiskScoringService(),
        'audit': AuditService()
    }

services = init_services()

# Initialize session state
if 'patient_context' not in st.session_state:
    st.session_state.patient_context = Patient()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'last_interactions' not in st.session_state:
    st.session_state.last_interactions = []

if 'last_risk_score' not in st.session_state:
    st.session_state.last_risk_score = None


# Sidebar with disclaimer and navigation
with st.sidebar:
    st.title("🏥 Clinical AI Demo")
    
    st.warning(Config.GLOBAL_DISCLAIMER)
    
    st.divider()
    
    # Show current patient context
    st.subheader("Current Patient Context")
    patient = st.session_state.patient_context
    if patient.patient_id:
        st.info(f"**Patient ID:** {patient.patient_id}")
        if patient.age:
            st.text(f"Age: {patient.age}")
        if patient.current_medications:
            st.text(f"Medications: {len(patient.current_medications)}")
        if patient.allergies:
            st.text(f"Allergies: {len(patient.allergies)}")
    else:
        st.info("No patient context loaded")


# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Patient & Medications",
    "💬 Clinical Q&A",
    "💊 Drug Interaction Check",
    "⚠️ Risk Prediction & Alerts",
    "📋 Audit & Logs"
])


# TAB 1: Patient & Medications
with tab1:
    st.header("Patient Demographics & Clinical Context")
    
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("Patient ID", value=st.session_state.patient_context.patient_id)
            age = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.patient_context.age or 0)
            sex = st.selectbox("Sex", ["", "Male", "Female", "Other"], index=0 if not st.session_state.patient_context.sex else ["", "Male", "Female", "Other"].index(st.session_state.patient_context.sex))
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=st.session_state.patient_context.weight or 0.0, step=0.1)
            height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=st.session_state.patient_context.height or 0.0, step=0.1)
        
        with col2:
            st.subheader("Clinical Flags")
            pregnancy = st.checkbox("Pregnancy", value=st.session_state.patient_context.pregnancy_status)
            renal = st.checkbox("Renal Impairment", value=st.session_state.patient_context.renal_impairment)
            hepatic = st.checkbox("Hepatic Impairment", value=st.session_state.patient_context.hepatic_impairment)
        
        st.subheader("Allergies")
        allergies_input = st.text_area(
            "Enter allergies (one per line)",
            value="\n".join(st.session_state.patient_context.allergies),
            height=100
        )
        
        st.subheader("Diagnoses / Conditions")
        diagnoses_input = st.text_area(
            "Enter diagnoses/conditions (one per line)",
            value="\n".join(st.session_state.patient_context.diagnoses),
            height=100
        )
        
        st.subheader("Current Medications")
        medications_input = st.text_area(
            "Enter current medications (one per line)",
            value="\n".join(st.session_state.patient_context.current_medications),
            height=150
        )
        
        submitted = st.form_submit_button("💾 Save Patient Context", type="primary")
        
        if submitted:
            # Parse inputs
            allergies = [a.strip() for a in allergies_input.split('\n') if a.strip()]
            diagnoses = [d.strip() for d in diagnoses_input.split('\n') if d.strip()]
            medications = [m.strip() for m in medications_input.split('\n') if m.strip()]
            
            # Update patient context
            st.session_state.patient_context = Patient(
                patient_id=patient_id,
                age=age if age > 0 else None,
                sex=sex if sex else None,
                weight=weight if weight > 0 else None,
                height=height if height > 0 else None,
                allergies=allergies,
                diagnoses=diagnoses,
                current_medications=medications,
                pregnancy_status=pregnancy,
                renal_impairment=renal,
                hepatic_impairment=hepatic
            )
            
            st.success("✅ Patient context saved successfully!")
            st.rerun()


# TAB 2: Clinical Q&A
with tab2:
    st.header("Clinical Question & Answer")
    
    st.info("Ask clinical questions and get AI-assisted responses with patient context.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a clinical question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                patient = st.session_state.patient_context
                response = services['llm'].answer_question(patient, prompt)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Log to audit
        if Config.ENABLE_AUDIT_LOGGING:
            services['audit'].log_event(
                event_type="Q&A",
                patient_id=patient.patient_id,
                payload={
                    "question": prompt,
                    "response_length": len(response),
                    "patient_summary": patient.get_summary()
                }
            )
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# TAB 3: Drug Interaction Check
with tab3:
    st.header("Drug Interaction Checker")
    
    patient = st.session_state.patient_context
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Medication List")
        if patient.current_medications:
            for med in patient.current_medications:
                st.text(f"• {med}")
        else:
            st.info("No medications in patient context. Add medications in the Patient & Medications tab.")
    
    with col2:
        st.subheader("Patient Factors")
        if patient.allergies:
            st.text(f"Allergies: {len(patient.allergies)}")
        if patient.diagnoses:
            st.text(f"Conditions: {len(patient.diagnoses)}")
        if patient.renal_impairment:
            st.text("⚠️ Renal impairment")
        if patient.hepatic_impairment:
            st.text("⚠️ Hepatic impairment")
    
    st.divider()
    
    # Additional medications to check
    st.subheader("Check Additional Medications")
    additional_meds_input = st.text_area(
        "Enter medications to add for interaction checking (one per line)",
        height=100,
        help="These medications will be checked against current medications"
    )
    
    if st.button("🔍 Check Interactions", type="primary"):
        additional_meds = [m.strip() for m in additional_meds_input.split('\n') if m.strip()]
        
        with st.spinner("Analyzing drug interactions..."):
            interactions = services['drug_interaction'].check_interactions(patient, additional_meds)
            st.session_state.last_interactions = interactions
            
            # Log to audit
            if Config.ENABLE_AUDIT_LOGGING:
                all_meds = patient.current_medications + additional_meds
                services['audit'].log_event(
                    event_type="INTERACTION_CHECK",
                    patient_id=patient.patient_id,
                    payload={
                        "medications": all_meds,
                        "num_interactions": len(interactions),
                        "high_severity": sum(1 for i in interactions if i.severity == "high")
                    },
                    risk_level=max([i.severity for i in interactions], default="low") if interactions else "low"
                )
    
    # Display results
    if st.session_state.last_interactions:
        st.divider()
        st.subheader("Interaction Results")
        
        interactions = st.session_state.last_interactions
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Interactions", len(interactions))
        with col2:
            high_count = sum(1 for i in interactions if i.severity == "high")
            st.metric("High Severity", high_count)
        with col3:
            medium_count = sum(1 for i in interactions if i.severity == "medium")
            st.metric("Medium Severity", medium_count)
        with col4:
            low_count = sum(1 for i in interactions if i.severity == "low")
            st.metric("Low Severity", low_count)
        
        st.divider()
        
        # Detailed interactions table
        if interactions:
            # Sort by severity (high first)
            severity_order = {"high": 0, "medium": 1, "low": 2}
            sorted_interactions = sorted(interactions, key=lambda x: severity_order[x.severity])
            
            for interaction in sorted_interactions:
                # Color code based on severity
                if interaction.severity == "high":
                    st.error(f"🔴 **HIGH SEVERITY** - {interaction.get_display_name()}")
                elif interaction.severity == "medium":
                    st.warning(f"🟡 **MEDIUM SEVERITY** - {interaction.get_display_name()}")
                else:
                    st.info(f"🟢 **LOW SEVERITY** - {interaction.get_display_name()}")
                
                with st.expander(f"Details: {interaction.get_display_name()}"):
                    st.write("**Summary:**")
                    st.write(interaction.summary)
                    st.write("**Management Advice:**")
                    st.write(interaction.management_advice)
                    st.write(f"**Interaction Type:** {interaction.interaction_type}")
        else:
            st.success("✅ No significant interactions detected!")
    
    elif not patient.current_medications and not additional_meds_input:
        st.info("Enter patient medications or additional medications to check for interactions.")


# TAB 4: Risk Prediction & Alerts
with tab4:
    st.header("Risk Prediction & Clinical Alerts")
    
    patient = st.session_state.patient_context
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Patient Overview")
        st.write(f"**Patient ID:** {patient.patient_id or 'Not specified'}")
        st.write(f"**Medications:** {len(patient.current_medications)}")
        st.write(f"**Active Interactions:** {len(st.session_state.last_interactions)}")
        
        if patient.age:
            st.write(f"**Age:** {patient.age}")
        if patient.renal_impairment:
            st.write("⚠️ **Renal Impairment**")
        if patient.hepatic_impairment:
            st.write("⚠️ **Hepatic Impairment**")
        if patient.pregnancy_status:
            st.write("⚠️ **Pregnancy**")
    
    with col2:
        if st.button("🎯 Compute Risk Score", type="primary"):
            with st.spinner("Calculating risk score..."):
                interactions = st.session_state.last_interactions
                risk_score = services['risk_scoring'].score_patient(patient, interactions)
                st.session_state.last_risk_score = risk_score
                
                # Log to audit
                if Config.ENABLE_AUDIT_LOGGING:
                    services['audit'].log_event(
                        event_type="RISK_SCORE",
                        patient_id=patient.patient_id,
                        payload={
                            "score": risk_score.score,
                            "label": risk_score.label,
                            "factors": risk_score.contributing_factors
                        },
                        risk_level=risk_score.label
                    )
    
    # Display risk score
    if st.session_state.last_risk_score:
        st.divider()
        
        risk_score = st.session_state.last_risk_score
        
        # Risk gauge visualization
        st.subheader("Risk Assessment")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display score with color
            if risk_score.label == "High":
                st.error(f"# {risk_score.score}/100")
                st.error(f"**Risk Level: {risk_score.label}**")
            elif risk_score.label == "Moderate":
                st.warning(f"# {risk_score.score}/100")
                st.warning(f"**Risk Level: {risk_score.label}**")
            else:
                st.success(f"# {risk_score.score}/100")
                st.success(f"**Risk Level: {risk_score.label}**")
            
            # Progress bar
            st.progress(min(risk_score.score / 100, 1.0))
        
        with col2:
            st.subheader("Contributing Factors")
            for factor in risk_score.contributing_factors:
                st.write(f"• {factor}")
        
        st.divider()
        
        # Recommendations
        st.subheader("Clinical Recommendations")
        recommendations = services['risk_scoring'].get_risk_recommendations(risk_score, patient)
        for rec in recommendations:
            if "HIGH RISK" in rec:
                st.error(rec)
            elif "MODERATE RISK" in rec:
                st.warning(rec)
            else:
                st.info(rec)
    
    else:
        st.info("Click 'Compute Risk Score' to assess patient risk level.")


# TAB 5: Audit & Logs
with tab5:
    st.header("Audit Logs & System Activity")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Recent Activity")
    
    with col2:
        num_records = st.selectbox("Records to show", [10, 25, 50, 100], index=2)
    
    # Get statistics
    stats = services['audit'].get_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Events", stats['total_events'])
    with col2:
        st.metric("Q&A Sessions", stats['by_type'].get('Q&A', 0))
    with col3:
        st.metric("Interaction Checks", stats['by_type'].get('INTERACTION_CHECK', 0))
    
    st.divider()
    
    # Fetch and display recent events
    events = services['audit'].get_recent_events(limit=num_records)
    
    if events:
        # Convert to dataframe
        data = []
        for event in events:
            data.append({
                'ID': event.id,
                'Timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Event Type': event.event_type,
                'Patient ID': event.patient_id or 'N/A',
                'Risk Level': event.risk_level or '-',
                'Summary': event.summary_text[:100] + '...' if len(event.summary_text) > 100 else event.summary_text
            })
        
        df = pd.DataFrame(data)
        
        # Style the dataframe
        def highlight_risk(row):
            if row['Risk Level'] == 'High':
                return ['background-color: #ffcccc'] * len(row)
            elif row['Risk Level'] == 'Moderate':
                return ['background-color: #fff4cc'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df.style.apply(highlight_risk, axis=1)
        st.dataframe(styled_df, width='stretch', height=400)
        
        # Export functionality
        st.divider()
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("📥 Download Logs (CSV)"):
                csv_path = "audit_export.csv"
                services['audit'].export_to_csv(csv_path, limit=num_records)
                
                with open(csv_path, 'r', encoding='utf-8') as f:
                    csv_data = f.read()
                
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No audit logs yet. Start using the system to generate activity logs.")


# Footer
st.divider()
st.caption("AI-Powered Clinical Q&A and Drug Interaction Validation System | Hackathon Demo | December 2025")
st.caption("⚠️ For demonstration purposes only - Not for clinical use")
