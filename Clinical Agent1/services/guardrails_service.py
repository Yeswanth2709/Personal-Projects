"""
Guardrails service for validation and safety checks.
Ensures LLM outputs are safe, compliant, and properly formatted.
"""
from typing import Dict, Any, Optional, List
import json
import re
from config import MEDICAL_DISCLAIMER


class GuardrailsService:
    """Service for validating and enforcing safety guardrails."""
    
    def __init__(self):
        self.disclaimer = MEDICAL_DISCLAIMER
        self.required_phrases = [
            "consult", "healthcare professional", "medical advice", 
            "physician", "clinician", "qualified"
        ]
        self.blocked_keywords = [
            "guaranteed cure", "definitely works", "medical diagnosis",
            "prescribed medication", "cancel appointment"
        ]
    
    def validate_input_query(self, query: str) -> Dict[str, Any]:
        """
        Validate user input query for safety and appropriateness.
        
        Args:
            query: User's input question
        
        Returns:
            Validation result with is_valid flag and sanitized query
        """
        result = {
            "is_valid": True,
            "sanitized_query": query.strip(),
            "warnings": [],
            "blocked_reasons": []
        }
        
        # Check for empty query
        if not query.strip():
            result["is_valid"] = False
            result["blocked_reasons"].append("Empty query")
            return result
        
        # Check for excessively long queries
        if len(query) > 2000:
            result["warnings"].append("Query is very long, may be truncated")
            result["sanitized_query"] = query[:2000]
        
        # Check for blocked keywords (case-insensitive)
        query_lower = query.lower()
        for keyword in self.blocked_keywords:
            if keyword in query_lower:
                result["warnings"].append(f"Query contains sensitive phrase: '{keyword}'")
        
        # Check for injection attempts
        suspicious_patterns = [
            r"ignore previous instructions",
            r"disregard.*above",
            r"you are now",
            r"system prompt",
            r"<script",
            r"javascript:"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query_lower):
                result["warnings"].append("Query contains potentially unsafe content")
                break
        
        return result
    
    def validate_clinical_response(self, response: str) -> Dict[str, Any]:
        """
        Validate LLM response for clinical appropriateness.
        
        Args:
            response: LLM generated response
        
        Returns:
            Validation result
        """
        result = {
            "is_valid": True,
            "requires_disclaimer": True,
            "warnings": [],
            "blocked_reasons": []
        }
        
        response_lower = response.lower()
        
        # Check if response contains appropriate disclaimers/qualifiers
        has_qualifier = any(phrase in response_lower for phrase in self.required_phrases)
        
        if not has_qualifier and len(response) > 100:
            result["warnings"].append(
                "Response lacks appropriate medical disclaimer language"
            )
            result["requires_disclaimer"] = True
        
        # Check for absolute medical claims
        absolute_patterns = [
            r"\b(always|never|definitely|guaranteed|certainly)\s+(cure|treat|fix|heal)",
            r"\byou (should|must|need to) (take|stop|start)",
            r"\bI (prescribe|diagnose|recommend taking)"
        ]
        
        for pattern in absolute_patterns:
            if re.search(pattern, response_lower):
                result["warnings"].append(
                    "Response contains absolute medical claims or directive language"
                )
                break
        
        # Check for diagnostic language
        diagnostic_patterns = [
            r"you (have|are suffering from|definitely have)",
            r"this is (a|an)\s+\w+\s+(diagnosis|disease|condition)",
            r"based on.*symptoms.*you have"
        ]
        
        for pattern in diagnostic_patterns:
            if re.search(pattern, response_lower):
                result["warnings"].append(
                    "Response appears to provide diagnosis"
                )
                result["requires_disclaimer"] = True
                break
        
        return result
    
    def add_disclaimer_to_response(self, response: str) -> str:
        """
        Add medical disclaimer to response if needed.
        
        Args:
            response: Original response
        
        Returns:
            Response with disclaimer prepended
        """
        return f"{self.disclaimer}\n\n{response}"
    
    def validate_json_structure(self, data: Any, expected_fields: List[str]) -> Dict[str, Any]:
        """
        Validate that JSON data contains expected fields.
        
        Args:
            data: Data to validate (dict or JSON string)
            expected_fields: List of required field names
        
        Returns:
            Validation result
        """
        result = {
            "is_valid": True,
            "missing_fields": [],
            "errors": []
        }
        
        # Parse JSON if string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                result["is_valid"] = False
                result["errors"].append(f"Invalid JSON: {str(e)}")
                return result
        
        # Check for expected fields
        if not isinstance(data, dict):
            result["is_valid"] = False
            result["errors"].append("Data is not a dictionary")
            return result
        
        for field in expected_fields:
            if field not in data:
                result["missing_fields"].append(field)
        
        if result["missing_fields"]:
            result["is_valid"] = False
            result["errors"].append(
                f"Missing required fields: {', '.join(result['missing_fields'])}"
            )
        
        return result
    
    def validate_severity_value(self, severity: str) -> Dict[str, Any]:
        """
        Validate that severity is one of allowed values.
        
        Args:
            severity: Severity value to check
        
        Returns:
            Validation result
        """
        allowed_values = ["low", "medium", "high"]
        severity_lower = severity.lower().strip()
        
        result = {
            "is_valid": severity_lower in allowed_values,
            "normalized_value": severity_lower if severity_lower in allowed_values else None,
            "error": None
        }
        
        if not result["is_valid"]:
            result["error"] = (
                f"Invalid severity '{severity}'. Must be one of: {', '.join(allowed_values)}"
            )
        
        return result
    
    def sanitize_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize patient data for logging (remove PII).
        
        Args:
            patient_data: Raw patient data
        
        Returns:
            Sanitized data safe for logging
        """
        sanitized = patient_data.copy()
        
        # Fields to redact or anonymize
        pii_fields = ["patient_id", "name", "email", "phone", "ssn", "mrn"]
        
        for field in pii_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"
        
        # Keep only aggregate/non-identifying information
        safe_fields = [
            "age", "sex", "weight", "allergies", "diagnoses", 
            "medications", "renal_impairment", "hepatic_impairment"
        ]
        
        return {k: v for k, v in sanitized.items() if k in safe_fields}
    
    def check_content_safety(self, text: str) -> Dict[str, Any]:
        """
        Check text for unsafe or inappropriate content.
        
        Args:
            text: Text to check
        
        Returns:
            Safety check result
        """
        result = {
            "is_safe": True,
            "flags": [],
            "severity": "none"
        }
        
        text_lower = text.lower()
        
        # Check for harmful content
        harmful_patterns = {
            "self_harm": [r"\b(suicide|kill myself|end my life|self harm)\b"],
            "violence": [r"\b(hurt|harm|kill|attack)\s+(someone|others|people)\b"],
            "illegal": [r"\b(illegal drugs|buy prescription|fake prescription)\b"]
        }
        
        for category, patterns in harmful_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    result["is_safe"] = False
                    result["flags"].append(category)
                    result["severity"] = "high"
        
        return result


# Singleton instance
_guardrails_service_instance = None


def get_guardrails_service() -> GuardrailsService:
    """Get or create the guardrails service singleton."""
    global _guardrails_service_instance
    if _guardrails_service_instance is None:
        _guardrails_service_instance = GuardrailsService()
    return _guardrails_service_instance


if __name__ == "__main__":
    # Test the service
    service = GuardrailsService()
    
    # Test input validation
    query = "What is the dosage for aspirin?"
    result = service.validate_input_query(query)
    print(f"Input validation: {result}")
    
    # Test response validation
    response = "You should take 100mg aspirin daily for your heart."
    result = service.validate_clinical_response(response)
    print(f"\nResponse validation: {result}")
    
    # Test adding disclaimer
    safe_response = service.add_disclaimer_to_response(response)
    print(f"\nWith disclaimer:\n{safe_response}")
    
    # Test severity validation
    result = service.validate_severity_value("high")
    print(f"\nSeverity validation: {result}")
