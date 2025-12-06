"""Drug interaction checking service."""

from typing import List, Dict, Tuple
from models import Patient, InteractionResult


class DrugInteractionService:
    """Service for checking drug interactions."""
    
    # Demo knowledge base of known interactions
    DRUG_DRUG_INTERACTIONS: Dict[Tuple[str, str], Dict] = {
        ("warfarin", "ibuprofen"): {
            "severity": "high",
            "summary": "Increased risk of bleeding when NSAIDs are combined with warfarin",
            "management": "Avoid concurrent use if possible. If necessary, monitor INR closely and watch for signs of bleeding."
        },
        ("warfarin", "aspirin"): {
            "severity": "high",
            "summary": "Significantly increased bleeding risk with anticoagulant + antiplatelet combination",
            "management": "Use only when benefit outweighs risk. Close monitoring of INR and bleeding signs required."
        },
        ("metformin", "contrast dye"): {
            "severity": "high",
            "summary": "Risk of contrast-induced nephropathy and lactic acidosis",
            "management": "Hold metformin 48 hours before and after contrast administration. Check renal function."
        },
        ("lisinopril", "spironolactone"): {
            "severity": "medium",
            "summary": "Risk of hyperkalemia when ACE inhibitors are combined with potassium-sparing diuretics",
            "management": "Monitor serum potassium levels regularly. Limit dietary potassium intake."
        },
        ("simvastatin", "clarithromycin"): {
            "severity": "high",
            "summary": "Increased statin levels and risk of rhabdomyolysis",
            "management": "Avoid combination. Consider alternative antibiotic or temporarily hold statin."
        },
        ("levothyroxine", "calcium"): {
            "severity": "medium",
            "summary": "Calcium can reduce absorption of thyroid hormone",
            "management": "Separate administration by at least 4 hours."
        },
        ("digoxin", "furosemide"): {
            "severity": "medium",
            "summary": "Diuretic-induced hypokalemia increases risk of digoxin toxicity",
            "management": "Monitor potassium and digoxin levels. Consider potassium supplementation."
        },
        ("methotrexate", "ibuprofen"): {
            "severity": "medium",
            "summary": "NSAIDs may reduce methotrexate clearance and increase toxicity",
            "management": "Monitor methotrexate levels and watch for signs of toxicity. Use lowest NSAID dose."
        },
        ("clopidogrel", "omeprazole"): {
            "severity": "medium",
            "summary": "PPI may reduce effectiveness of clopidogrel",
            "management": "Consider alternative PPI (pantoprazole) or H2 blocker."
        },
    }
    
    # Known drug-allergy cross-sensitivities
    ALLERGY_INTERACTIONS: Dict[str, List[str]] = {
        "penicillin": ["amoxicillin", "ampicillin", "penicillin", "augmentin"],
        "sulfa": ["sulfamethoxazole", "trimethoprim", "bactrim"],
        "aspirin": ["aspirin", "ibuprofen", "naproxen", "nsaid"],
    }
    
    # Drug-condition interactions
    CONDITION_INTERACTIONS: Dict[str, Dict] = {
        "heart failure": {
            "drugs": ["ibuprofen", "naproxen", "nsaid"],
            "severity": "medium",
            "summary": "NSAIDs can worsen heart failure by causing fluid retention",
            "management": "Avoid NSAIDs in heart failure. Use acetaminophen for pain relief."
        },
        "kidney disease": {
            "drugs": ["ibuprofen", "naproxen", "nsaid", "metformin"],
            "severity": "high",
            "summary": "Risk of acute kidney injury and drug accumulation",
            "management": "Avoid NSAIDs. Adjust doses based on renal function."
        },
        "asthma": {
            "drugs": ["aspirin", "ibuprofen", "beta blocker"],
            "severity": "medium",
            "summary": "May trigger bronchospasm in sensitive patients",
            "management": "Use with caution. Monitor respiratory status."
        },
    }
    
    @staticmethod
    def normalize_med_name(name: str) -> str:
        """Normalize medication name for matching."""
        # Simple normalization: lowercase and strip
        normalized = name.lower().strip()
        
        # Basic alias mapping
        aliases = {
            "motrin": "ibuprofen",
            "advil": "ibuprofen",
            "tylenol": "acetaminophen",
            "coumadin": "warfarin",
            "lasix": "furosemide",
            "zocor": "simvastatin",
            "prilosec": "omeprazole",
            "plavix": "clopidogrel",
            "glucophage": "metformin",
        }
        
        return aliases.get(normalized, normalized)
    
    @staticmethod
    def check_drug_drug(meds: List[str]) -> List[InteractionResult]:
        """Check for drug-drug interactions."""
        interactions = []
        normalized_meds = [DrugInteractionService.normalize_med_name(m) for m in meds]
        
        # Check all pairs
        for i in range(len(normalized_meds)):
            for j in range(i + 1, len(normalized_meds)):
                drug1, drug2 = normalized_meds[i], normalized_meds[j]
                
                # Check both orderings
                key = (drug1, drug2) if (drug1, drug2) in DrugInteractionService.DRUG_DRUG_INTERACTIONS else (drug2, drug1)
                
                if key in DrugInteractionService.DRUG_DRUG_INTERACTIONS:
                    interaction_data = DrugInteractionService.DRUG_DRUG_INTERACTIONS[key]
                    interactions.append(InteractionResult(
                        interaction_type="drug-drug",
                        drug1=meds[i],
                        drug2=meds[j],
                        severity=interaction_data["severity"],
                        summary=interaction_data["summary"],
                        management_advice=interaction_data["management"]
                    ))
        
        return interactions
    
    @staticmethod
    def check_drug_allergy(meds: List[str], allergies: List[str]) -> List[InteractionResult]:
        """Check for drug-allergy interactions."""
        interactions = []
        normalized_meds = [DrugInteractionService.normalize_med_name(m) for m in meds]
        normalized_allergies = [a.lower().strip() for a in allergies]
        
        for allergy in normalized_allergies:
            if allergy in DrugInteractionService.ALLERGY_INTERACTIONS:
                contraindicated = DrugInteractionService.ALLERGY_INTERACTIONS[allergy]
                for med, norm_med in zip(meds, normalized_meds):
                    if norm_med in contraindicated:
                        interactions.append(InteractionResult(
                            interaction_type="drug-allergy",
                            drug1=med,
                            allergen=allergy,
                            severity="high",
                            summary=f"Patient has documented {allergy} allergy. {med} may cause cross-sensitivity reaction.",
                            management_advice="CONTRAINDICATED. Do not administer. Consider alternative medication from different class."
                        ))
        
        return interactions
    
    @staticmethod
    def check_drug_condition(meds: List[str], conditions: List[str]) -> List[InteractionResult]:
        """Check for drug-condition interactions."""
        interactions = []
        normalized_meds = [DrugInteractionService.normalize_med_name(m) for m in meds]
        normalized_conditions = [c.lower().strip() for c in conditions]
        
        for condition in normalized_conditions:
            if condition in DrugInteractionService.CONDITION_INTERACTIONS:
                interaction_data = DrugInteractionService.CONDITION_INTERACTIONS[condition]
                contraindicated = interaction_data["drugs"]
                
                for med, norm_med in zip(meds, normalized_meds):
                    if norm_med in contraindicated:
                        interactions.append(InteractionResult(
                            interaction_type="drug-condition",
                            drug1=med,
                            condition=condition,
                            severity=interaction_data["severity"],
                            summary=interaction_data["summary"],
                            management_advice=interaction_data["management"]
                        ))
        
        return interactions
    
    @staticmethod
    def check_interactions(patient: Patient, additional_meds: List[str] = None) -> List[InteractionResult]:
        """
        Orchestrator to check all types of interactions.
        
        Args:
            patient: Patient context with medications, allergies, and conditions
            additional_meds: Additional medications to check (optional)
        
        Returns:
            List of all detected interactions
        """
        # Combine current meds with any additional ones being checked
        all_meds = patient.current_medications.copy()
        if additional_meds:
            all_meds.extend(additional_meds)
        
        if not all_meds:
            return []
        
        interactions = []
        
        # Check drug-drug interactions
        interactions.extend(DrugInteractionService.check_drug_drug(all_meds))
        
        # Check drug-allergy interactions
        if patient.allergies:
            interactions.extend(DrugInteractionService.check_drug_allergy(all_meds, patient.allergies))
        
        # Check drug-condition interactions
        if patient.diagnoses:
            interactions.extend(DrugInteractionService.check_drug_condition(all_meds, patient.diagnoses))
        
        return interactions


class ExternalInteractionAPI:
    """
    Interface for external drug interaction APIs.
    
    TODO: Implement integration with real APIs like:
    - DrugBank API (https://drugbank.com/api)
    - FDA Drug Interaction API
    - RxNorm / RxNav APIs
    """
    
    def fetch_interactions(self, drug_list: List[str]) -> List[InteractionResult]:
        """
        Fetch interactions from external API.
        
        Args:
            drug_list: List of drug names
            
        Returns:
            List of interaction results
            
        TODO: Implement actual API calls with proper authentication and error handling.
        """
        # Placeholder for future implementation
        raise NotImplementedError("External API integration not yet implemented")
