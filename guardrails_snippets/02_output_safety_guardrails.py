"""
Output Safety Guardrails
=========================
Comprehensive output validation for AI responses covering toxicity,
bias detection, factuality, and content filtering.

Industry Use Case: All AI Applications, Content Generation, Customer Service
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ToxicityLevel(Enum):
    """Toxicity severity levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    SEVERE = 4


class ToxicityGuardrail:
    """Detect toxic, offensive, or harmful content in AI outputs"""
    
    def __init__(self, threshold: ToxicityLevel = ToxicityLevel.MEDIUM):
        self.threshold = threshold
        
        # Toxic content patterns (simplified for demonstration)
        self.toxic_patterns = {
            ToxicityLevel.SEVERE: [
                r'\b(kill|murder|assassinate)\s+(yourself|themselves|him|her)\b',
                r'\bhate\s+(all|every)\s+\w+s?\b',
                r'\b(kys|kms)\b',  # internet slang for self-harm
            ],
            ToxicityLevel.HIGH: [
                r'\b(idiot|moron|stupid|dumb)\s+(person|people)\b',
                r'\b(f[\*u]ck|sh[\*i]t|b[\*i]tch)\s+(you|off)\b',
                r'\b(hate|despise|loathe)\s+(you|them)\b',
            ],
            ToxicityLevel.MEDIUM: [
                r'\b(dumb|stupid|idiotic|moronic)\b',
                r'\b(suck|terrible|awful|horrible)\s+at\b',
                r'\byou\s+are\s+(useless|worthless)\b',
            ],
            ToxicityLevel.LOW: [
                r'\b(annoying|irritating|frustrating)\b',
                r'\bnot\s+smart\b',
            ]
        }
    
    def validate(self, text: str) -> Tuple[bool, ToxicityLevel, List[str]]:
        """
        Check for toxic content
        
        Returns:
            Tuple[bool, ToxicityLevel, List[str]]: (is_safe, toxicity_level, matched_patterns)
        """
        detected_patterns = []
        max_toxicity = ToxicityLevel.NONE
        
        # Check patterns from most severe to least
        for level in [ToxicityLevel.SEVERE, ToxicityLevel.HIGH, ToxicityLevel.MEDIUM, ToxicityLevel.LOW]:
            for pattern in self.toxic_patterns.get(level, []):
                if re.search(pattern, text, re.IGNORECASE):
                    detected_patterns.append(pattern)
                    if level.value > max_toxicity.value:
                        max_toxicity = level
        
        is_safe = max_toxicity.value <= self.threshold.value
        return is_safe, max_toxicity, detected_patterns


class BiasDetectionGuardrail:
    """Detect biased or discriminatory content"""
    
    def __init__(self):
        # Protected attributes
        self.protected_groups = {
            "gender": ["male", "female", "men", "women", "man", "woman", "boy", "girl"],
            "race": ["black", "white", "asian", "hispanic", "latino", "african"],
            "religion": ["muslim", "christian", "jewish", "hindu", "buddhist", "atheist"],
            "age": ["young", "old", "elderly", "senior", "teenager", "millennial"],
            "disability": ["disabled", "handicapped", "blind", "deaf"],
            "nationality": ["american", "chinese", "indian", "mexican", "european"],
        }
        
        # Biased statement patterns
        self.bias_patterns = [
            r'\b(\w+)\s+are\s+(always|never|all|naturally|inherently)\s+(\w+)\b',
            r'\b(all|every|no)\s+(\w+)\s+(are|is|can\'t|cannot)\b',
            r'\b(\w+)\s+can\'t\s+(\w+)\s+because\s+they\'re\s+(\w+)\b',
            r'\btypical\s+(\w+)\b',
            r'\b(\w+)\s+tend\s+to\s+be\s+(\w+)\b',
        ]
    
    def validate(self, text: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Check for biased content
        
        Returns:
            Tuple[bool, List[Dict]]: (is_unbiased, detected_biases)
        """
        detected_biases = []
        text_lower = text.lower()
        
        # Check for bias patterns mentioning protected groups
        for pattern in self.bias_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                
                # Check if any protected group is mentioned
                for category, groups in self.protected_groups.items():
                    for group in groups:
                        if group in matched_text:
                            detected_biases.append({
                                "category": category,
                                "group": group,
                                "text": matched_text,
                                "pattern": pattern
                            })
                            break
        
        is_unbiased = len(detected_biases) == 0
        return is_unbiased, detected_biases


class ProfessionalismGuardrail:
    """Ensure professional and appropriate tone"""
    
    def __init__(self, allow_casual: bool = False):
        self.allow_casual = allow_casual
        
        self.unprofessional_patterns = [
            r'\b(lol|lmao|rofl|omg|wtf|bruh)\b',
            r'\b(gonna|wanna|gotta|kinda|sorta)\b',
            r'\byeah\s+right\b',
            r'\bwhatever\b',
            r'\bnot\s+my\s+problem\b',
        ]
        
        self.inappropriate_patterns = [
            r'\b(shut\s+up|shut\s+it)\b',
            r'\bdon\'t\s+care\b',
            r'\bnot\s+interested\b',
            r'\bleave\s+me\s+alone\b',
        ]
    
    def validate(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check for professional tone
        
        Returns:
            Tuple[bool, List[str]]: (is_professional, violations)
        """
        violations = []
        
        if not self.allow_casual:
            for pattern in self.unprofessional_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append(f"Casual language: {pattern}")
        
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Inappropriate language: {pattern}")
        
        is_professional = len(violations) == 0
        return is_professional, violations


class FactualityGuardrail:
    """Check for potential factual inconsistencies or hallucinations"""
    
    def __init__(self):
        # Hedge words that indicate uncertainty
        self.uncertainty_indicators = [
            r'\b(might|may|could|possibly|perhaps|maybe)\b',
            r'\b(seems|appears|looks like|sounds like)\b',
            r'\b(probably|likely|unlikely)\b',
            r'\bI\s+(think|believe|assume|guess)\b',
        ]
        
        # Overconfident statements without evidence
        self.overconfident_patterns = [
            r'\b(definitely|certainly|absolutely|always|never)\b',
            r'\beveryone\s+knows\b',
            r'\bit\s+is\s+a\s+fact\s+that\b',
            r'\bwithout\s+a\s+doubt\b',
        ]
        
        # Numeric claims that should be verified
        self.numeric_claim_patterns = [
            r'\b\d+%\b',
            r'\b\d+\s+(million|billion|trillion)\b',
            r'\bin\s+\d{4}\b',  # years
        ]
    
    def validate(self, text: str) -> Dict[str, Any]:
        """
        Analyze factual claims in text
        
        Returns:
            Dict with uncertainty score, claims, and warnings
        """
        uncertainty_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in self.uncertainty_indicators
        )
        
        overconfident_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in self.overconfident_patterns
        )
        
        numeric_claims = []
        for pattern in self.numeric_claim_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            numeric_claims.extend(matches)
        
        # Calculate uncertainty score (0-1)
        total_claims = uncertainty_count + overconfident_count
        uncertainty_score = uncertainty_count / total_claims if total_claims > 0 else 0.5
        
        result = {
            "uncertainty_score": uncertainty_score,
            "uncertainty_indicators": uncertainty_count,
            "overconfident_statements": overconfident_count,
            "numeric_claims": numeric_claims,
            "requires_verification": len(numeric_claims) > 0 or overconfident_count > 2
        }
        
        return result


class PrivacyGuardrail:
    """Ensure AI doesn't leak sensitive information"""
    
    def __init__(self):
        self.sensitive_patterns = {
            "api_key": r'\b[A-Za-z0-9]{32,}\b',
            "password": r'\b(password|passwd|pwd)\s*[:=]\s*\S+\b',
            "token": r'\btoken\s*[:=]\s*[A-Za-z0-9_\-\.]+\b',
            "secret": r'\b(secret|key)\s*[:=]\s*\S+\b',
            "internal_url": r'https?://(localhost|127\.0\.0\.1|192\.168\.|10\.)',
            "file_path": r'[A-Za-z]:\\[\w\\\-\. ]+|/(?:home|root|etc|var)/[\w/\-\.]+',
        }
    
    def validate(self, text: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Check for sensitive information leakage
        
        Returns:
            Tuple[bool, Dict]: (is_safe, detected_sensitive_info)
        """
        detected = {}
        
        for info_type, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[info_type] = matches
        
        is_safe = len(detected) == 0
        return is_safe, detected


class ContentLengthGuardrail:
    """Validate output length and completeness"""
    
    def __init__(self, min_length: int = 10, max_length: int = 5000):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """
        Check if output has appropriate length
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        length = len(text)
        
        if length < self.min_length:
            return False, f"Output too short: {length} chars (minimum {self.min_length})"
        
        if length > self.max_length:
            return False, f"Output too long: {length} chars (maximum {self.max_length})"
        
        # Check for incomplete responses
        incomplete_indicators = [
            r'\.\.\.$',  # trailing ellipsis
            r'\[.*\]$',  # trailing placeholder
            r'\bto\s+be\s+continued\b',
        ]
        
        for pattern in incomplete_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Output appears incomplete"
        
        return True, None


class JSONOutputGuardrail:
    """Validate JSON output structure"""
    
    def __init__(self, required_fields: Optional[List[str]] = None):
        self.required_fields = required_fields or []
    
    def validate(self, text: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate JSON output
        
        Returns:
            Tuple[bool, str, Optional[Dict]]: (is_valid, error_message, parsed_json)
        """
        import json
        
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_text = text
        
        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}", None
        
        # Check required fields
        if isinstance(parsed, dict):
            missing_fields = [field for field in self.required_fields if field not in parsed]
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}", parsed
        
        return True, None, parsed


class RefusalGuardrail:
    """Detect if AI properly refuses inappropriate requests"""
    
    def __init__(self):
        self.refusal_phrases = [
            r'\bI\s+cannot\b',
            r'\bI\s+can\'t\b',
            r'\bI\'m\s+not\s+able\s+to\b',
            r'\bI\'m\s+unable\s+to\b',
            r'\bI\s+must\s+decline\b',
            r'\bI\s+cannot\s+assist\b',
            r'\bSorry,?\s+I\s+can\'t\b',
            r'\bI\'m\s+sorry,?\s+but\s+I\s+cannot\b',
        ]
    
    def should_refuse(self, user_input: str) -> bool:
        """
        Check if user input should be refused
        
        This is a simplified check - in production, use more sophisticated methods
        """
        harmful_indicators = [
            r'\bhow\s+to\s+(hack|crack|break\s+into)\b',
            r'\bcreate\s+(virus|malware|exploit)\b',
            r'\b(illegal|unlawful)\s+(activity|activities)\b',
            r'\bharm\s+(yourself|themselves|others)\b',
        ]
        
        for pattern in harmful_indicators:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True
        
        return False
    
    def validate(self, output: str, user_input: str) -> Tuple[bool, str]:
        """
        Check if AI properly refused inappropriate request
        
        Returns:
            Tuple[bool, str]: (properly_handled, error_message)
        """
        should_refuse = self.should_refuse(user_input)
        
        if should_refuse:
            # Check if output contains refusal
            has_refusal = any(
                re.search(phrase, output, re.IGNORECASE)
                for phrase in self.refusal_phrases
            )
            
            if not has_refusal:
                return False, "AI should have refused this request but didn't"
        
        return True, None


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("TOXICITY GUARDRAIL")
    print("=" * 60)
    
    toxicity_guard = ToxicityGuardrail(threshold=ToxicityLevel.MEDIUM)
    
    test_outputs = [
        "I'd be happy to help you with that!",
        "You're being annoying with these questions.",
        "That's a stupid question.",
    ]
    
    for output in test_outputs:
        is_safe, level, patterns = toxicity_guard.validate(output)
        print(f"\nOutput: {output}")
        print(f"Safe: {is_safe}, Level: {level.name}")
    
    print("\n" + "=" * 60)
    print("BIAS DETECTION GUARDRAIL")
    print("=" * 60)
    
    bias_guard = BiasDetectionGuardrail()
    
    test_texts = [
        "Women are naturally better at multitasking.",
        "The candidate has excellent qualifications.",
    ]
    
    for text in test_texts:
        is_unbiased, biases = bias_guard.validate(text)
        print(f"\nText: {text}")
        print(f"Unbiased: {is_unbiased}")
        if biases:
            print(f"Detected biases: {biases}")
    
    print("\n" + "=" * 60)
    print("FACTUALITY GUARDRAIL")
    print("=" * 60)
    
    factuality_guard = FactualityGuardrail()
    
    text = "The market definitely grew by 150% in 2020. Everyone knows this is absolutely true."
    result = factuality_guard.validate(text)
    
    print(f"\nText: {text}")
    print(f"Analysis: {result}")
    
    print("\n" + "=" * 60)
    print("PRIVACY GUARDRAIL")
    print("=" * 60)
    
    privacy_guard = PrivacyGuardrail()
    
    text_with_secrets = "Your API key is abc123def456 and password is: secret123"
    is_safe, detected = privacy_guard.validate(text_with_secrets)
    
    print(f"\nText: {text_with_secrets}")
    print(f"Safe: {is_safe}")
    print(f"Detected: {detected}")
