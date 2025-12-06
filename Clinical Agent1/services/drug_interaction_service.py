"""
Drug interaction validation service.
Checks for drug-drug, drug-allergy, and drug-condition interactions.
"""
from typing import List, Dict, Any
from models import InteractionResult, AllergyCheck, Patient


class DrugInteractionService:
    """Service for validating drug interactions."""
    
    def __init__(self):
        # In-memory interaction database (small realistic examples)
        self.drug_interactions = self._initialize_interactions()
        self.drug_allergies = self._initialize_allergy_data()
    
    def _initialize_interactions(self) -> List[Dict[str, Any]]:
        """Initialize drug-drug interaction database."""
        return [
            {
                "drug1": "warfarin",
                "drug2": "aspirin",
                "severity": "high",
                "type": "Bleeding Risk",
                "explanation": "Both warfarin and aspirin increase bleeding risk. Concurrent use significantly increases risk of major bleeding events.",
                "management": "Avoid combination if possible. If necessary, use lowest effective doses and monitor INR closely. Consider gastroprotection with PPI."
            },
            {
                "drug1": "warfarin",
                "drug2": "ibuprofen",
                "severity": "high",
                "type": "Bleeding Risk",
                "explanation": "NSAIDs like ibuprofen increase bleeding risk when combined with warfarin. Also increases risk of GI bleeding.",
                "management": "Avoid NSAIDs in patients on warfarin. Use alternative analgesics like acetaminophen. If NSAID necessary, use lowest dose with PPI and monitor INR."
            },
            {
                "drug1": "metformin",
                "drug2": "contrast dye",
                "severity": "high",
                "type": "Lactic Acidosis Risk",
                "explanation": "Metformin with iodinated contrast media increases risk of contrast-induced nephropathy and lactic acidosis.",
                "management": "Discontinue metformin before or at the time of contrast procedure. May restart 48 hours after if renal function is stable."
            },
            {
                "drug1": "lisinopril",
                "drug2": "spironolactone",
                "severity": "medium",
                "type": "Hyperkalemia Risk",
                "explanation": "ACE inhibitors and potassium-sparing diuretics both increase potassium levels, increasing hyperkalemia risk.",
                "management": "Monitor serum potassium regularly. Consider potassium supplementation restriction. Watch for signs of hyperkalemia."
            },
            {
                "drug1": "simvastatin",
                "drug2": "clarithromycin",
                "severity": "high",
                "type": "Myopathy/Rhabdomyolysis Risk",
                "explanation": "Clarithromycin inhibits CYP3A4, significantly increasing simvastatin levels and risk of muscle toxicity.",
                "management": "Avoid combination. Consider holding statin during clarithromycin course or use alternative antibiotic. If unavoidable, use lowest statin dose and monitor for muscle symptoms."
            },
            {
                "drug1": "methotrexate",
                "drug2": "trimethoprim",
                "severity": "high",
                "type": "Bone Marrow Suppression",
                "explanation": "Both drugs are folate antagonists. Combined use increases risk of severe bone marrow suppression.",
                "management": "Avoid combination. If necessary, increase folic acid supplementation and monitor CBC closely."
            },
            {
                "drug1": "digoxin",
                "drug2": "furosemide",
                "severity": "medium",
                "type": "Digoxin Toxicity Risk",
                "explanation": "Loop diuretics can cause hypokalemia, which increases sensitivity to digoxin and risk of toxicity.",
                "management": "Monitor potassium levels and digoxin levels. Supplement potassium as needed. Watch for signs of digoxin toxicity."
            },
            {
                "drug1": "amiodarone",
                "drug2": "warfarin",
                "severity": "high",
                "type": "Increased Anticoagulation",
                "explanation": "Amiodarone inhibits warfarin metabolism, significantly increasing INR and bleeding risk.",
                "management": "Reduce warfarin dose by 30-50% when starting amiodarone. Monitor INR frequently (weekly x 4-6 weeks)."
            },
            {
                "drug1": "levothyroxine",
                "drug2": "calcium",
                "severity": "medium",
                "type": "Decreased Absorption",
                "explanation": "Calcium supplements can bind to levothyroxine in the GI tract, reducing its absorption and effectiveness.",
                "management": "Separate administration by at least 4 hours. Take levothyroxine on empty stomach, calcium with meals."
            },
            {
                "drug1": "ssri",
                "drug2": "tramadol",
                "severity": "medium",
                "type": "Serotonin Syndrome Risk",
                "explanation": "Combination increases risk of serotonin syndrome, a potentially life-threatening condition.",
                "management": "Use caution. Monitor for serotonin syndrome symptoms (agitation, confusion, tremor, hyperthermia). Consider alternative analgesic."
            }
        ]
    
    def _initialize_allergy_data(self) -> Dict[str, List[str]]:
        """Initialize drug allergy cross-sensitivity data."""
        return {
            "penicillin": ["amoxicillin", "ampicillin", "piperacillin", "cephalosporins"],
            "sulfa": ["sulfamethoxazole", "sulfasalazine", "furosemide", "thiazides"],
            "aspirin": ["nsaids", "ibuprofen", "naproxen", "celecoxib"],
            "codeine": ["morphine", "hydrocodone", "oxycodone", "hydromorphone"]
        }
    
    def normalize_drug_name(self, drug_name: str) -> str:
        """Normalize drug name for matching."""
        return drug_name.lower().strip()
    
    def check_drug_drug_interactions(self, medications: List[str]) -> List[InteractionResult]:
        """
        Check for interactions between multiple medications.
        
        Args:
            medications: List of medication names
        
        Returns:
            List of interaction results
        """
        if len(medications) < 2:
            return []
        
        interactions = []
        normalized_meds = [self.normalize_drug_name(med) for med in medications]
        
        # Check each pair of medications
        for i, med1 in enumerate(normalized_meds):
            for med2 in normalized_meds[i+1:]:
                # Check in both directions
                for interaction in self.drug_interactions:
                    drug1_norm = self.normalize_drug_name(interaction["drug1"])
                    drug2_norm = self.normalize_drug_name(interaction["drug2"])
                    
                    # Check if drugs match (in either order)
                    if (med1 in drug1_norm or drug1_norm in med1) and \
                       (med2 in drug2_norm or drug2_norm in med2):
                        interactions.append(InteractionResult(
                            drug1=medications[i],
                            drug2=medications[normalized_meds.index(med2)],
                            severity=interaction["severity"],
                            interaction_type=interaction["type"],
                            explanation=interaction["explanation"],
                            management=interaction["management"],
                            references=["Internal Database"]
                        ))
                    elif (med2 in drug1_norm or drug1_norm in med2) and \
                         (med1 in drug2_norm or drug2_norm in med1):
                        interactions.append(InteractionResult(
                            drug1=medications[normalized_meds.index(med2)],
                            drug2=medications[i],
                            severity=interaction["severity"],
                            interaction_type=interaction["type"],
                            explanation=interaction["explanation"],
                            management=interaction["management"],
                            references=["Internal Database"]
                        ))
        
        return interactions
    
    def check_allergies(self, medications: List[str], allergies: List[str]) -> List[AllergyCheck]:
        """
        Check medications against known allergies.
        
        Args:
            medications: List of medication names
            allergies: List of known allergies
        
        Returns:
            List of allergy concerns
        """
        if not allergies:
            return []
        
        concerns = []
        normalized_allergies = [self.normalize_drug_name(a) for a in allergies]
        
        for med in medications:
            med_norm = self.normalize_drug_name(med)
            
            for allergy in normalized_allergies:
                # Direct match
                if allergy in med_norm or med_norm in allergy:
                    concerns.append(AllergyCheck(
                        medication=med,
                        allergy=allergies[normalized_allergies.index(allergy)],
                        severity="high",
                        explanation=f"Patient has documented allergy to {allergy}. Direct contraindication.",
                        alternative_medications=self._suggest_alternatives(med)
                    ))
                
                # Check cross-sensitivity
                if allergy in self.drug_allergies:
                    cross_sensitive = self.drug_allergies[allergy]
                    for cross_med in cross_sensitive:
                        if cross_med in med_norm or med_norm in cross_med:
                            concerns.append(AllergyCheck(
                                medication=med,
                                allergy=allergies[normalized_allergies.index(allergy)],
                                severity="medium",
                                explanation=f"Potential cross-sensitivity with {allergy} allergy. {med} belongs to related drug class.",
                                alternative_medications=self._suggest_alternatives(med)
                            ))
        
        return concerns
    
    def _suggest_alternatives(self, medication: str) -> List[str]:
        """Suggest alternative medications (stub implementation)."""
        # Simple stub - in real system would use drug database
        alternatives_map = {
            "penicillin": ["azithromycin", "levofloxacin"],
            "amoxicillin": ["azithromycin", "levofloxacin"],
            "aspirin": ["acetaminophen", "celecoxib (if no NSAID allergy)"],
            "ibuprofen": ["acetaminophen", "naproxen"],
            "warfarin": ["apixaban", "rivaroxaban"]
        }
        
        med_norm = self.normalize_drug_name(medication)
        for key, alts in alternatives_map.items():
            if key in med_norm:
                return alts
        
        return ["Consult clinical guidelines for alternatives"]
    
    def validate_patient_medications(self, patient: Patient) -> Dict[str, Any]:
        """
        Comprehensive medication validation for a patient.
        
        Args:
            patient: Patient object with medications and allergies
        
        Returns:
            Dictionary with interaction and allergy results
        """
        results = {
            "drug_interactions": self.check_drug_drug_interactions(patient.medications),
            "allergy_concerns": self.check_allergies(patient.medications, patient.allergies),
            "total_issues": 0,
            "high_severity_count": 0,
            "medium_severity_count": 0,
            "low_severity_count": 0
        }
        
        # Count issues by severity
        for interaction in results["drug_interactions"]:
            if interaction.severity == "high":
                results["high_severity_count"] += 1
            elif interaction.severity == "medium":
                results["medium_severity_count"] += 1
            else:
                results["low_severity_count"] += 1
        
        for concern in results["allergy_concerns"]:
            if concern.severity == "high":
                results["high_severity_count"] += 1
            elif concern.severity == "medium":
                results["medium_severity_count"] += 1
            else:
                results["low_severity_count"] += 1
        
        results["total_issues"] = (
            results["high_severity_count"] + 
            results["medium_severity_count"] + 
            results["low_severity_count"]
        )
        
        return results


# Singleton instance
_drug_service_instance = None


def get_drug_interaction_service() -> DrugInteractionService:
    """Get or create the drug interaction service singleton."""
    global _drug_service_instance
    if _drug_service_instance is None:
        _drug_service_instance = DrugInteractionService()
    return _drug_service_instance


if __name__ == "__main__":
    # Test the service
    from models import Patient
    
    service = DrugInteractionService()
    
    # Test patient
    patient = Patient(
        age=65,
        sex="Male",
        weight=80.0,
        allergies=["Penicillin"],
        medications=["Warfarin", "Aspirin", "Lisinopril", "Amoxicillin"],
        diagnoses=["Atrial Fibrillation", "Hypertension"]
    )
    
    results = service.validate_patient_medications(patient)
    print(f"Total issues: {results['total_issues']}")
    print(f"High severity: {results['high_severity_count']}")
    print(f"\nDrug interactions:")
    for interaction in results["drug_interactions"]:
        print(f"  - {interaction.drug1} + {interaction.drug2}: {interaction.severity}")
    print(f"\nAllergy concerns:")
    for concern in results["allergy_concerns"]:
        print(f"  - {concern.medication} (allergy: {concern.allergy}): {concern.severity}")
