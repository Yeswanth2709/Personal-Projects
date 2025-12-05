"""
Healthcare Compliance Guardrails
=================================
HIPAA-compliant guardrails for healthcare AI applications covering
patient data protection, medical advice limitations, and regulatory compliance.

Industry Use Case: Healthcare, Telemedicine, EHR Systems, Medical AI
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ComplianceLevel(Enum):
    """HIPAA compliance levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


class HIPAA_ComplianceGuardrail:
    """Ensure HIPAA compliance in healthcare AI outputs"""
    
    def __init__(self):
        # Protected Health Information (PHI) identifiers
        self.phi_patterns = {
            "name": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "medical_record_number": r'\bMRN:?\s*\d+\b',
            "health_plan_number": r'\b(plan|policy)\s*#?\s*\d+\b',
            "account_number": r'\baccount\s*#?\s*\d+\b',
            "certificate_number": r'\bcert(?:ificate)?\s*#?\s*\d+\b',
            "vehicle_identifier": r'\b[A-Z0-9]{17}\b',  # VIN
            "device_identifier": r'\bdevice\s*(?:id|serial)?\s*:?\s*\S+\b',
            "biometric": r'\b(fingerprint|retina|voiceprint)\b',
            "face_photo": r'\b(photo|image|picture)\s+of\s+(patient|face)\b',
            "unique_identifier": r'\b[A-Z0-9]{10,}\b',
        }
        
        # Date patterns (dates related to individual)
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b',
        ]
        
        # Geographic identifiers (smaller than state)
        self.geo_patterns = [
            r'\b\d{5}(?:-\d{4})?\b',  # ZIP codes
            r'\b\d+\s+\w+\s+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct|boulevard|blvd)\b',
        ]
    
    def validate(self, text: str) -> Tuple[ComplianceLevel, List[Dict[str, str]]]:
        """
        Check for PHI in text
        
        Returns:
            Tuple[ComplianceLevel, List[Dict]]: (compliance_level, violations)
        """
        violations = []
        
        # Check PHI patterns
        for phi_type, pattern in self.phi_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations.append({
                    "type": "PHI",
                    "category": phi_type,
                    "matches": matches[:3],  # Limit to first 3
                    "severity": "high"
                })
        
        # Check dates
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                violations.append({
                    "type": "Date",
                    "category": "temporal_identifier",
                    "matches": matches[:3],
                    "severity": "medium"
                })
        
        # Check geographic info
        for pattern in self.geo_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations.append({
                    "type": "Geographic",
                    "category": "location_identifier",
                    "matches": matches[:3],
                    "severity": "medium"
                })
        
        # Determine compliance level
        if not violations:
            compliance_level = ComplianceLevel.COMPLIANT
        elif any(v["severity"] == "high" for v in violations):
            compliance_level = ComplianceLevel.VIOLATION
        else:
            compliance_level = ComplianceLevel.WARNING
        
        return compliance_level, violations


class MedicalDisclaimerGuardrail:
    """Ensure medical disclaimers are present when needed"""
    
    def __init__(self):
        self.medical_terms = [
            r'\b(diagnos[ei]s|treatment|medication|prescription|symptoms?|disease|condition|therapy)\b',
            r'\b(doctor|physician|nurse|hospital|clinic|medical)\b',
            r'\b(pain|fever|infection|cancer|diabetes|heart\s+disease)\b',
        ]
        
        self.disclaimer_phrases = [
            r'\bnot\s+a\s+substitute\s+for\s+professional\s+medical\s+advice\b',
            r'\bconsult\s+(?:a|your)\s+(?:doctor|physician|healthcare\s+provider)\b',
            r'\bseek\s+(?:immediate\s+)?medical\s+(?:attention|help)\b',
            r'\bthis\s+is\s+not\s+medical\s+advice\b',
            r'\bfor\s+informational\s+purposes\s+only\b',
        ]
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """
        Check if medical disclaimer is needed and present
        
        Returns:
            Tuple[bool, str]: (is_compliant, error_message)
        """
        # Check if text contains medical terms
        has_medical_content = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.medical_terms
        )
        
        if not has_medical_content:
            return True, None
        
        # Check if disclaimer is present
        has_disclaimer = any(
            re.search(phrase, text, re.IGNORECASE)
            for phrase in self.disclaimer_phrases
        )
        
        if has_disclaimer:
            return True, None
        else:
            return False, "Medical content requires appropriate disclaimer"


class PrescriptionGuardrail:
    """Prevent AI from prescribing medications"""
    
    def __init__(self):
        self.prescription_indicators = [
            r'\byou\s+should\s+take\s+\w+\s+(?:mg|ml|tablets?|pills?)\b',
            r'\bI\s+recommend\s+\w+\s+(?:mg|ml|tablets?|pills?)\b',
            r'\btake\s+\d+\s+(?:mg|ml|tablets?|pills?)\s+(?:daily|twice|once)\b',
            r'\bprescribe\s+\w+\b',
            r'\bstart\s+(?:taking|using)\s+\w+\s+medication\b',
        ]
        
        self.dosage_patterns = [
            r'\b\d+\s*(?:mg|ml|mcg|g)\b',
            r'\b\d+\s+times?\s+(?:per|a)\s+day\b',
        ]
    
    def validate(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if AI is inappropriately prescribing
        
        Returns:
            Tuple[bool, List[str]]: (is_compliant, violations)
        """
        violations = []
        
        for pattern in self.prescription_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Prescription-like statement: {pattern}")
        
        # Check for dosage instructions
        has_dosage = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.dosage_patterns
        )
        
        has_prescription = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.prescription_indicators
        )
        
        if has_dosage and has_prescription:
            violations.append("Contains specific dosage recommendations")
        
        is_compliant = len(violations) == 0
        return is_compliant, violations


class DiagnosisGuardrail:
    """Prevent AI from making medical diagnoses"""
    
    def __init__(self):
        self.diagnosis_patterns = [
            r'\byou\s+have\s+\w+\s+disease\b',
            r'\bthis\s+is\s+(?:definitely|certainly)\s+\w+\b',
            r'\bI\s+diagnose\s+you\s+with\b',
            r'\byou\s+are\s+suffering\s+from\s+\w+\b',
            r'\bmy\s+diagnosis\s+is\b',
            r'\byou\s+(?:definitely|certainly)\s+have\s+\w+\b',
        ]
        
        self.appropriate_phrases = [
            r'\bmay\s+indicate\b',
            r'\bcould\s+be\s+a\s+sign\s+of\b',
            r'\bpossible\s+\w+\b',
            r'\bsuggest(?:s|ive\s+of)\b',
            r'\bconsult\s+a\s+doctor\s+for\s+(?:proper\s+)?diagnosis\b',
        ]
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """
        Check if AI is making inappropriate diagnoses
        
        Returns:
            Tuple[bool, str]: (is_compliant, error_message)
        """
        # Check for diagnosis statements
        has_diagnosis = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.diagnosis_patterns
        )
        
        if has_diagnosis:
            # Check if appropriate hedging language is used
            has_appropriate_language = any(
                re.search(phrase, text, re.IGNORECASE)
                for phrase in self.appropriate_phrases
            )
            
            if not has_appropriate_language:
                return False, "AI appears to be making a medical diagnosis without appropriate hedging"
        
        return True, None


class EmergencyDetectionGuardrail:
    """Detect medical emergencies and provide appropriate guidance"""
    
    def __init__(self):
        self.emergency_keywords = [
            r'\bchest\s+pain\b',
            r'\bdifficulty\s+breathing\b',
            r'\bcan\'t\s+breathe\b',
            r'\bsevere\s+bleeding\b',
            r'\bunconscious\b',
            r'\bseizure\b',
            r'\bheart\s+attack\b',
            r'\bstroke\b',
            r'\bsuicid(?:e|al)\b',
            r'\bsevere\s+(?:pain|injury)\b',
            r'\bpoisoning\b',
            r'\boverdose\b',
        ]
        
        self.emergency_response = [
            r'\bcall\s+911\b',
            r'\bseek\s+immediate\s+medical\s+attention\b',
            r'\bgo\s+to\s+(?:the\s+)?emergency\s+room\b',
            r'\bthis\s+is\s+a\s+medical\s+emergency\b',
        ]
    
    def detect_emergency(self, text: str) -> bool:
        """Check if input describes a medical emergency"""
        return any(
            re.search(keyword, text, re.IGNORECASE)
            for keyword in self.emergency_keywords
        )
    
    def validate(self, user_input: str, ai_response: str) -> Tuple[bool, str]:
        """
        Check if emergency is properly handled
        
        Returns:
            Tuple[bool, str]: (is_compliant, error_message)
        """
        is_emergency = self.detect_emergency(user_input)
        
        if is_emergency:
            # Check if response contains emergency guidance
            has_emergency_response = any(
                re.search(response, ai_response, re.IGNORECASE)
                for response in self.emergency_response
            )
            
            if not has_emergency_response:
                return False, "Emergency situation not properly addressed - must direct to call 911 or seek immediate care"
        
        return True, None


class MinorProtectionGuardrail:
    """Additional protections when interacting with minors"""
    
    def __init__(self):
        self.minor_indicators = [
            r'\bI\'m\s+\d+\s+years?\s+old\b',
            r'\bI\'m\s+a\s+(?:child|kid|teenager|teen)\b',
            r'\bmy\s+age\s+is\s+\d+\b',
        ]
        
        self.inappropriate_for_minors = [
            r'\b(?:sexual|explicit|adult)\s+content\b',
            r'\balcohol\s+consumption\b',
            r'\btobacco\s+use\b',
            r'\bdrug\s+use\b',
        ]
    
    def detect_minor(self, text: str) -> Optional[int]:
        """
        Detect if user is a minor
        
        Returns:
            Optional[int]: Age if detected, None otherwise
        """
        for pattern in self.minor_indicators:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract age
                age_match = re.search(r'\d+', match.group(0))
                if age_match:
                    age = int(age_match.group(0))
                    if age < 18:
                        return age
        return None
    
    def validate(self, ai_response: str, user_age: Optional[int] = None) -> Tuple[bool, str]:
        """
        Check if content is appropriate for minors
        
        Returns:
            Tuple[bool, str]: (is_appropriate, error_message)
        """
        if user_age is None or user_age >= 18:
            return True, None
        
        # Check for inappropriate content
        for pattern in self.inappropriate_for_minors:
            if re.search(pattern, ai_response, re.IGNORECASE):
                return False, f"Content inappropriate for minor (age {user_age})"
        
        return True, None


class ConsentGuardrail:
    """Ensure proper consent for data collection and sharing"""
    
    def __init__(self):
        self.data_collection_terms = [
            r'\bcollect\s+(?:your\s+)?(?:personal\s+)?(?:data|information)\b',
            r'\bstore\s+(?:your\s+)?(?:data|information)\b',
            r'\bshare\s+(?:your\s+)?(?:data|information)\b',
            r'\bprocess\s+(?:your\s+)?(?:personal\s+)?data\b',
        ]
        
        self.consent_phrases = [
            r'\bdo\s+you\s+consent\b',
            r'\bI\s+consent\b',
            r'\bagree\s+to\s+(?:the\s+)?terms\b',
            r'\bprivacy\s+policy\b',
            r'\bopt[\s-]in\b',
        ]
    
    def validate(self, conversation: List[str]) -> Tuple[bool, str]:
        """
        Check if consent was obtained before data collection
        
        Returns:
            Tuple[bool, str]: (has_consent, error_message)
        """
        data_collection_mentioned = False
        consent_obtained = False
        
        for message in conversation:
            # Check if data collection is mentioned
            if any(re.search(term, message, re.IGNORECASE) for term in self.data_collection_terms):
                data_collection_mentioned = True
            
            # Check if consent was obtained
            if any(re.search(phrase, message, re.IGNORECASE) for phrase in self.consent_phrases):
                consent_obtained = True
        
        if data_collection_mentioned and not consent_obtained:
            return False, "Data collection mentioned without obtaining user consent"
        
        return True, None


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("HIPAA COMPLIANCE GUARDRAIL")
    print("=" * 60)
    
    hipaa_guard = HIPAA_ComplianceGuardrail()
    
    test_texts = [
        "Patient John Smith, MRN: 12345, visited on 05/15/2023",
        "The patient has hypertension and requires monitoring",
    ]
    
    for text in test_texts:
        compliance, violations = hipaa_guard.validate(text)
        print(f"\nText: {text}")
        print(f"Compliance: {compliance.value}")
        if violations:
            print(f"Violations: {violations}")
    
    print("\n" + "=" * 60)
    print("MEDICAL DISCLAIMER GUARDRAIL")
    print("=" * 60)
    
    disclaimer_guard = MedicalDisclaimerGuardrail()
    
    texts = [
        "For your symptoms, you should consult a doctor. This is not medical advice.",
        "You have a fever and should take acetaminophen.",
    ]
    
    for text in texts:
        is_compliant, error = disclaimer_guard.validate(text)
        print(f"\nText: {text}")
        print(f"Compliant: {is_compliant}")
        if error:
            print(f"Error: {error}")
    
    print("\n" + "=" * 60)
    print("PRESCRIPTION GUARDRAIL")
    print("=" * 60)
    
    prescription_guard = PrescriptionGuardrail()
    
    text = "You should take 500mg of ibuprofen twice daily."
    is_compliant, violations = prescription_guard.validate(text)
    
    print(f"\nText: {text}")
    print(f"Compliant: {is_compliant}")
    print(f"Violations: {violations}")
    
    print("\n" + "=" * 60)
    print("EMERGENCY DETECTION GUARDRAIL")
    print("=" * 60)
    
    emergency_guard = EmergencyDetectionGuardrail()
    
    user_input = "I'm having severe chest pain and difficulty breathing"
    ai_response = "That sounds serious. You should rest and drink water."
    
    is_compliant, error = emergency_guard.validate(user_input, ai_response)
    
    print(f"\nUser: {user_input}")
    print(f"AI: {ai_response}")
    print(f"Compliant: {is_compliant}")
    print(f"Error: {error}")
    
    # Proper response
    ai_response_proper = "This is a medical emergency. Call 911 immediately or go to the nearest emergency room."
    is_compliant, error = emergency_guard.validate(user_input, ai_response_proper)
    
    print(f"\nAI (Proper): {ai_response_proper}")
    print(f"Compliant: {is_compliant}")
