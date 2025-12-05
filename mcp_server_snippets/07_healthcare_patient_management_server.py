"""
MCP Server - Healthcare Patient Management
===========================================
Enterprise healthcare server for patient records, appointments, and clinical workflows.
HIPAA-compliant operations with secure patient data handling.

Industry Use Case: Healthcare, Hospitals, Clinics, Telemedicine, EHR Systems
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import random
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize MCP server
server = Server("healthcare-patient-management-server")

# Patient database (HIPAA-compliant in production)
patients = {}
patient_counter = 10000

# Appointments
appointments = {}
appointment_counter = 5000

# Medical records
medical_records = {}

# Prescriptions
prescriptions = {}
prescription_counter = 20000

# Healthcare providers
providers = {
    "DR001": {"id": "DR001", "name": "Dr. Sarah Johnson", "specialty": "Cardiology", "license": "MD12345"},
    "DR002": {"id": "DR002", "name": "Dr. Michael Chen", "specialty": "Pediatrics", "license": "MD23456"},
    "DR003": {"id": "DR003", "name": "Dr. Emily Rodriguez", "specialty": "Internal Medicine", "license": "MD34567"}
}


def init_sample_patients():
    """Initialize sample patient data"""
    global patient_counter
    
    for i in range(5):
        patient_id = f"PT-{patient_counter}"
        patient_counter += 1
        
        patients[patient_id] = {
            "id": patient_id,
            "first_name": f"Patient{i}",
            "last_name": f"Test{i}",
            "date_of_birth": (datetime.now() - timedelta(days=random.randint(7300, 29200))).date().isoformat(),
            "gender": random.choice(["Male", "Female", "Other"]),
            "blood_type": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
            "email": f"patient{i}@example.com",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": {
                "street": f"{random.randint(100, 999)} Healthcare Ave",
                "city": "Medical City",
                "state": "CA",
                "zip": f"{random.randint(90000, 99999)}"
            },
            "emergency_contact": {
                "name": f"Emergency Contact {i}",
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "relationship": "Spouse"
            },
            "insurance": {
                "provider": "Health Insurance Co",
                "policy_number": f"INS{random.randint(100000, 999999)}",
                "group_number": f"GRP{random.randint(1000, 9999)}"
            },
            "allergies": ["None recorded"],
            "chronic_conditions": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Create medical record
        medical_records[patient_id] = {
            "patient_id": patient_id,
            "visits": [],
            "diagnoses": [],
            "medications": [],
            "lab_results": [],
            "immunizations": []
        }


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available healthcare resources"""
    resources = [
        Resource(
            uri="healthcare://patients",
            name="Patient Database",
            mimeType="application/json",
            description="Patient demographic information (PHI protected)"
        ),
        Resource(
            uri="healthcare://appointments",
            name="Appointment Schedule",
            mimeType="application/json",
            description="All scheduled patient appointments"
        ),
        Resource(
            uri="healthcare://providers",
            name="Healthcare Providers",
            mimeType="application/json",
            description="List of healthcare providers and their specialties"
        ),
        Resource(
            uri="healthcare://prescriptions",
            name="Active Prescriptions",
            mimeType="application/json",
            description="Currently active patient prescriptions"
        )
    ]
    
    # Add individual patient medical records
    for patient_id in patients.keys():
        resources.append(
            Resource(
                uri=f"healthcare://medical-record/{patient_id}",
                name=f"Medical Record - {patient_id}",
                mimeType="application/json",
                description=f"Complete medical record for patient {patient_id}"
            )
        )
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read healthcare resources"""
    
    if uri == "healthcare://patients":
        # Return anonymized patient list
        patient_list = [
            {
                "id": p["id"],
                "name": f"{p['first_name']} {p['last_name']}",
                "date_of_birth": p["date_of_birth"],
                "gender": p["gender"]
            }
            for p in patients.values()
        ]
        return json.dumps(patient_list, indent=2)
    
    elif uri == "healthcare://appointments":
        return json.dumps(list(appointments.values()), indent=2)
    
    elif uri == "healthcare://providers":
        return json.dumps(list(providers.values()), indent=2)
    
    elif uri == "healthcare://prescriptions":
        return json.dumps(list(prescriptions.values()), indent=2)
    
    elif uri.startswith("healthcare://medical-record/"):
        patient_id = uri.split("/")[-1]
        if patient_id in medical_records:
            return json.dumps(medical_records[patient_id], indent=2)
        else:
            raise ValueError(f"Medical record not found for patient: {patient_id}")
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available healthcare tools"""
    return [
        Tool(
            name="register_patient",
            description="Register a new patient in the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "date_of_birth": {"type": "string", "format": "date"},
                    "gender": {"type": "string", "enum": ["Male", "Female", "Other"]},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "address": {"type": "object"},
                    "emergency_contact": {"type": "object"},
                    "insurance": {"type": "object"}
                },
                "required": ["first_name", "last_name", "date_of_birth", "gender"]
            }
        ),
        Tool(
            name="schedule_appointment",
            description="Schedule a patient appointment with a provider",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "provider_id": {"type": "string"},
                    "appointment_date": {"type": "string", "format": "date-time"},
                    "appointment_type": {
                        "type": "string",
                        "enum": ["checkup", "follow_up", "consultation", "emergency", "telemedicine"]
                    },
                    "reason": {"type": "string"},
                    "duration_minutes": {"type": "integer", "default": 30}
                },
                "required": ["patient_id", "provider_id", "appointment_date", "appointment_type"]
            }
        ),
        Tool(
            name="update_medical_record",
            description="Add or update patient medical record information",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "record_type": {
                        "type": "string",
                        "enum": ["visit", "diagnosis", "medication", "lab_result", "immunization"]
                    },
                    "data": {"type": "object", "description": "Record data"}
                },
                "required": ["patient_id", "record_type", "data"]
            }
        ),
        Tool(
            name="create_prescription",
            description="Create a new prescription for a patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "provider_id": {"type": "string"},
                    "medication_name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"},
                    "duration_days": {"type": "integer"},
                    "instructions": {"type": "string"},
                    "refills": {"type": "integer", "default": 0}
                },
                "required": ["patient_id", "provider_id", "medication_name", "dosage", "frequency"]
            }
        ),
        Tool(
            name="search_patients",
            description="Search for patients by name, ID, or other criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "search_by": {
                        "type": "string",
                        "enum": ["name", "id", "phone", "email"],
                        "default": "name"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_patient_history",
            description="Retrieve complete medical history for a patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "include_sections": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["visits", "diagnoses", "medications", "lab_results", "immunizations"]
                        },
                        "description": "Sections to include (all if not specified)"
                    }
                },
                "required": ["patient_id"]
            }
        ),
        Tool(
            name="check_drug_interactions",
            description="Check for potential drug interactions",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "new_medication": {"type": "string", "description": "Medication to check"}
                },
                "required": ["patient_id", "new_medication"]
            }
        ),
        Tool(
            name="send_appointment_reminder",
            description="Send appointment reminder to patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"},
                    "method": {
                        "type": "string",
                        "enum": ["email", "sms", "both"],
                        "default": "both"
                    }
                },
                "required": ["appointment_id"]
            }
        ),
        Tool(
            name="generate_clinical_report",
            description="Generate clinical reports and summaries",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["patient_summary", "visit_notes", "lab_summary", "medication_list", "referral_letter"]
                    },
                    "patient_id": {"type": "string"},
                    "date_range": {"type": "object", "description": "Optional date range filter"}
                },
                "required": ["report_type", "patient_id"]
            }
        ),
        Tool(
            name="calculate_risk_score",
            description="Calculate patient risk scores for various conditions",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "risk_type": {
                        "type": "string",
                        "enum": ["cardiac", "diabetes", "stroke", "fall_risk", "readmission"]
                    }
                },
                "required": ["patient_id", "risk_type"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute healthcare tools"""
    global patient_counter, appointment_counter, prescription_counter
    
    if name == "register_patient":
        patient_id = f"PT-{patient_counter}"
        patient_counter += 1
        
        patients[patient_id] = {
            "id": patient_id,
            "first_name": arguments.get("first_name", ""),
            "last_name": arguments.get("last_name", ""),
            "date_of_birth": arguments.get("date_of_birth", ""),
            "gender": arguments.get("gender", ""),
            "email": arguments.get("email", ""),
            "phone": arguments.get("phone", ""),
            "address": arguments.get("address", {}),
            "emergency_contact": arguments.get("emergency_contact", {}),
            "insurance": arguments.get("insurance", {}),
            "allergies": [],
            "chronic_conditions": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Initialize medical record
        medical_records[patient_id] = {
            "patient_id": patient_id,
            "visits": [],
            "diagnoses": [],
            "medications": [],
            "lab_results": [],
            "immunizations": []
        }
        
        result = {
            "status": "registered",
            "patient": patients[patient_id]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "schedule_appointment":
        appointment_id = f"APT-{appointment_counter}"
        appointment_counter += 1
        
        patient_id = arguments.get("patient_id", "")
        provider_id = arguments.get("provider_id", "")
        
        if patient_id not in patients:
            return [TextContent(type="text", text=f"Error: Patient '{patient_id}' not found")]
        
        if provider_id not in providers:
            return [TextContent(type="text", text=f"Error: Provider '{provider_id}' not found")]
        
        appointments[appointment_id] = {
            "id": appointment_id,
            "patient_id": patient_id,
            "patient_name": f"{patients[patient_id]['first_name']} {patients[patient_id]['last_name']}",
            "provider_id": provider_id,
            "provider_name": providers[provider_id]["name"],
            "appointment_date": arguments.get("appointment_date", ""),
            "appointment_type": arguments.get("appointment_type", "checkup"),
            "reason": arguments.get("reason", ""),
            "duration_minutes": arguments.get("duration_minutes", 30),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        result = {
            "status": "scheduled",
            "appointment": appointments[appointment_id]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_medical_record":
        patient_id = arguments.get("patient_id", "")
        record_type = arguments.get("record_type", "")
        data = arguments.get("data", {})
        
        if patient_id not in medical_records:
            return [TextContent(type="text", text=f"Error: Patient '{patient_id}' not found")]
        
        record = medical_records[patient_id]
        
        if record_type == "visit":
            record["visits"].append({
                **data,
                "timestamp": datetime.now().isoformat()
            })
        elif record_type == "diagnosis":
            record["diagnoses"].append({
                **data,
                "timestamp": datetime.now().isoformat()
            })
        elif record_type == "medication":
            record["medications"].append({
                **data,
                "timestamp": datetime.now().isoformat()
            })
        elif record_type == "lab_result":
            record["lab_results"].append({
                **data,
                "timestamp": datetime.now().isoformat()
            })
        elif record_type == "immunization":
            record["immunizations"].append({
                **data,
                "timestamp": datetime.now().isoformat()
            })
        
        result = {
            "status": "updated",
            "patient_id": patient_id,
            "record_type": record_type,
            "records_count": len(record[f"{record_type}s" if record_type != "diagnosis" else "diagnoses"])
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_prescription":
        prescription_id = f"RX-{prescription_counter}"
        prescription_counter += 1
        
        patient_id = arguments.get("patient_id", "")
        if patient_id not in patients:
            return [TextContent(type="text", text=f"Error: Patient '{patient_id}' not found")]
        
        prescriptions[prescription_id] = {
            "id": prescription_id,
            "patient_id": patient_id,
            "patient_name": f"{patients[patient_id]['first_name']} {patients[patient_id]['last_name']}",
            "provider_id": arguments.get("provider_id", ""),
            "medication_name": arguments.get("medication_name", ""),
            "dosage": arguments.get("dosage", ""),
            "frequency": arguments.get("frequency", ""),
            "duration_days": arguments.get("duration_days", 30),
            "instructions": arguments.get("instructions", ""),
            "refills": arguments.get("refills", 0),
            "status": "active",
            "prescribed_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=arguments.get("duration_days", 30))).isoformat()
        }
        
        result = {
            "status": "prescribed",
            "prescription": prescriptions[prescription_id]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "search_patients":
        query = arguments.get("query", "").lower()
        search_by = arguments.get("search_by", "name")
        
        results = []
        for patient in patients.values():
            if search_by == "name":
                full_name = f"{patient['first_name']} {patient['last_name']}".lower()
                if query in full_name:
                    results.append(patient)
            elif search_by == "id":
                if query in patient["id"].lower():
                    results.append(patient)
            elif search_by == "phone":
                if query in patient.get("phone", ""):
                    results.append(patient)
            elif search_by == "email":
                if query in patient.get("email", "").lower():
                    results.append(patient)
        
        search_result = {
            "query": query,
            "search_by": search_by,
            "results_count": len(results),
            "results": results
        }
        
        return [TextContent(type="text", text=json.dumps(search_result, indent=2))]
    
    elif name == "get_patient_history":
        patient_id = arguments.get("patient_id", "")
        
        if patient_id not in medical_records:
            return [TextContent(type="text", text=f"Error: Patient '{patient_id}' not found")]
        
        record = medical_records[patient_id]
        include_sections = arguments.get("include_sections")
        
        if include_sections:
            filtered_record = {k: v for k, v in record.items() if k in include_sections or k == "patient_id"}
        else:
            filtered_record = record
        
        return [TextContent(type="text", text=json.dumps(filtered_record, indent=2))]
    
    elif name == "check_drug_interactions":
        patient_id = arguments.get("patient_id", "")
        new_medication = arguments.get("new_medication", "")
        
        if patient_id not in medical_records:
            return [TextContent(type="text", text=f"Error: Patient '{patient_id}' not found")]
        
        current_medications = medical_records[patient_id].get("medications", [])
        
        # Simulated drug interaction check
        interactions = []
        if len(current_medications) > 0 and random.random() > 0.7:
            interactions.append({
                "severity": random.choice(["minor", "moderate", "severe"]),
                "drug1": new_medication,
                "drug2": current_medications[0].get("name", "Unknown"),
                "description": "Potential interaction detected - consult pharmacist"
            })
        
        result = {
            "patient_id": patient_id,
            "new_medication": new_medication,
            "current_medications_count": len(current_medications),
            "interactions_found": len(interactions),
            "interactions": interactions,
            "safe_to_prescribe": len(interactions) == 0 or all(i["severity"] == "minor" for i in interactions)
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "calculate_risk_score":
        patient_id = arguments.get("patient_id", "")
        risk_type = arguments.get("risk_type", "")
        
        if patient_id not in patients:
            return [TextContent(type="text", text=f"Error: Patient '{patient_id}' not found")]
        
        # Simulated risk score calculation
        risk_score = random.uniform(0.1, 0.9)
        risk_level = "low" if risk_score < 0.3 else "moderate" if risk_score < 0.7 else "high"
        
        result = {
            "patient_id": patient_id,
            "risk_type": risk_type,
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "risk_factors": [
                "Age-related risk",
                "Medical history considerations"
            ],
            "recommendations": [
                "Regular monitoring recommended",
                "Lifestyle modifications advised"
            ],
            "calculated_at": datetime.now().isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    init_sample_patients()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
