"""
Financial Services Guardrails
==============================
Compliance guardrails for financial AI applications covering
regulatory compliance, investment advice limitations, and fraud detection.

Industry Use Case: Banking, Fintech, Investment Platforms, Financial Advisory
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class RegulatoryCompliance(Enum):
    """Financial regulatory compliance standards"""
    SEC = "SEC"  # Securities and Exchange Commission
    FINRA = "FINRA"  # Financial Industry Regulatory Authority
    CFPB = "CFPB"  # Consumer Financial Protection Bureau
    GDPR = "GDPR"  # General Data Protection Regulation (EU)
    PCI_DSS = "PCI_DSS"  # Payment Card Industry Data Security Standard


class InvestmentAdviceGuardrail:
    """Prevent unlicensed investment advice"""
    
    def __init__(self, is_registered_advisor: bool = False):
        self.is_registered_advisor = is_registered_advisor
        
        self.investment_advice_patterns = [
            r'\byou\s+should\s+(?:buy|sell|invest\s+in)\s+\w+\s+(?:stock|bond|fund|security)\b',
            r'\bI\s+recommend\s+(?:buying|selling|investing\s+in)\b',
            r'\bnow\s+is\s+(?:a\s+)?good\s+time\s+to\s+(?:buy|sell)\b',
            r'\bthis\s+(?:stock|security)\s+will\s+(?:rise|fall|increase|decrease)\b',
            r'\bguaranteed\s+returns?\b',
            r'\brisk[\s-]free\s+investment\b',
        ]
        
        self.educational_phrases = [
            r'\bfor\s+educational\s+purposes\s+only\b',
            r'\bnot\s+(?:financial|investment)\s+advice\b',
            r'\bconsult\s+(?:a|your)\s+(?:financial\s+advisor|professional)\b',
            r'\bthis\s+is\s+general\s+information\b',
        ]
    
    def validate(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check for unlicensed investment advice
        
        Returns:
            Tuple[bool, List[str]]: (is_compliant, violations)
        """
        violations = []
        
        # Check for investment advice patterns
        has_advice = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.investment_advice_patterns
        )
        
        if has_advice and not self.is_registered_advisor:
            # Check for proper disclaimers
            has_disclaimer = any(
                re.search(phrase, text, re.IGNORECASE)
                for phrase in self.educational_phrases
            )
            
            if not has_disclaimer:
                violations.append("Investment advice without proper disclaimer or licensing")
        
        # Check for guarantee claims
        if re.search(r'\bguarantee', text, re.IGNORECASE):
            violations.append("Inappropriate guarantee claims in financial context")
        
        is_compliant = len(violations) == 0
        return is_compliant, violations


class FinancialDataProtectionGuardrail:
    """Protect sensitive financial information"""
    
    def __init__(self):
        self.sensitive_patterns = {
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "cvv": r'\bCVV:?\s*\d{3,4}\b',
            "account_number": r'\baccount\s*#?:?\s*\d{8,17}\b',
            "routing_number": r'\brouting\s*#?:?\s*\d{9}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "pin": r'\bPIN:?\s*\d{4,6}\b',
            "bank_account": r'\b\d{10,17}\b',
        }
    
    def validate(self, text: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Detect sensitive financial information
        
        Returns:
            Tuple[bool, Dict]: (is_safe, detected_info)
        """
        detected = {}
        
        for info_type, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[info_type] = matches
        
        is_safe = len(detected) == 0
        return is_safe, detected
    
    def mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive financial data"""
        masked = text
        
        # Mask credit card
        masked = re.sub(
            r'\b(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})\b',
            r'\1-XXXX-XXXX-\4',
            masked
        )
        
        # Mask account numbers
        masked = re.sub(
            r'\baccount\s*#?:?\s*(\d{4})\d+(\d{4})\b',
            r'account: \1XXXX\2',
            masked,
            flags=re.IGNORECASE
        )
        
        # Mask SSN
        masked = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX', masked)
        
        # Mask CVV
        masked = re.sub(r'\bCVV:?\s*\d{3,4}\b', 'CVV: XXX', masked, flags=re.IGNORECASE)
        
        return masked


class FraudDetectionGuardrail:
    """Detect potential fraud attempts"""
    
    def __init__(self):
        self.fraud_indicators = [
            r'\burgent(?:ly)?\s+(?:send|transfer|wire)\s+money\b',
            r'\blimited\s+time\s+offer\b',
            r'\bact\s+now\s+(?:or|before)\b',
            r'\bunclaimed\s+(?:money|funds|prize)\b',
            r'\bverify\s+your\s+(?:account|identity)\s+(?:immediately|now)\b',
            r'\bsuspicious\s+activity\s+on\s+your\s+account\b',
            r'\byou\'ve\s+won\s+(?:a\s+)?(?:prize|lottery)\b',
            r'\bforeign\s+(?:prince|official|lottery)\b',
            r'\binheritance\s+(?:money|funds)\b',
            r'\b(?:click|open)\s+(?:this\s+)?link\s+(?:immediately|now)\b',
        ]
        
        self.social_engineering_patterns = [
            r'\bdon\'t\s+tell\s+anyone\b',
            r'\bkeep\s+this\s+(?:secret|confidential)\b',
            r'\bdelete\s+this\s+message\s+after\b',
            r'\bif\s+you\s+don\'t\s+(?:act|respond)\b',
            r'\byour\s+account\s+will\s+be\s+(?:closed|suspended)\b',
        ]
    
    def validate(self, text: str) -> Tuple[int, List[str]]:
        """
        Calculate fraud risk score
        
        Returns:
            Tuple[int, List[str]]: (risk_score 0-100, matched_indicators)
        """
        matched_indicators = []
        
        for pattern in self.fraud_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                matched_indicators.append(pattern)
        
        for pattern in self.social_engineering_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matched_indicators.append(pattern)
        
        # Calculate risk score
        risk_score = min(len(matched_indicators) * 15, 100)
        
        return risk_score, matched_indicators


class KYC_ComplianceGuardrail:
    """Know Your Customer (KYC) compliance checks"""
    
    def __init__(self):
        self.required_fields = [
            "full_name",
            "date_of_birth",
            "address",
            "identification_number",
            "nationality"
        ]
        
        self.high_risk_countries = [
            "north korea", "iran", "syria", "crimea"
        ]
    
    def validate_kyc_data(self, kyc_data: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate KYC data completeness
        
        Returns:
            Tuple[bool, List[str]]: (is_complete, missing_fields)
        """
        missing_fields = [
            field for field in self.required_fields
            if field not in kyc_data or not kyc_data[field]
        ]
        
        is_complete = len(missing_fields) == 0
        return is_complete, missing_fields
    
    def check_sanctions(self, nationality: str, name: str) -> Tuple[bool, str]:
        """
        Check against sanctions lists (simplified)
        
        Returns:
            Tuple[bool, str]: (is_clear, warning_message)
        """
        # Check high-risk countries
        if any(country in nationality.lower() for country in self.high_risk_countries):
            return False, f"High-risk country detected: Enhanced due diligence required"
        
        # In production, check against OFAC, UN, EU sanctions lists
        return True, None


class AML_ComplianceGuardrail:
    """Anti-Money Laundering (AML) compliance"""
    
    def __init__(self, threshold_amount: float = 10000.0):
        self.threshold_amount = threshold_amount
        self.structuring_window_hours = 24
    
    def detect_structuring(self, transactions: List[Dict]) -> Tuple[bool, str]:
        """
        Detect transaction structuring (smurfing)
        
        Returns:
            Tuple[bool, str]: (is_suspicious, reason)
        """
        if not transactions:
            return False, None
        
        # Check for multiple transactions just below threshold
        suspicious_transactions = [
            t for t in transactions
            if 0.8 * self.threshold_amount <= t["amount"] < self.threshold_amount
        ]
        
        if len(suspicious_transactions) >= 3:
            total = sum(t["amount"] for t in suspicious_transactions)
            return True, f"Possible structuring: {len(suspicious_transactions)} transactions totaling ${total:.2f}"
        
        # Check for rapid succession
        if len(transactions) >= 5:
            time_span = (
                max(t["timestamp"] for t in transactions) -
                min(t["timestamp"] for t in transactions)
            ).total_seconds() / 3600
            
            if time_span < self.structuring_window_hours:
                return True, f"{len(transactions)} transactions within {time_span:.1f} hours"
        
        return False, None
    
    def validate_transaction(
        self,
        amount: float,
        purpose: str,
        sender_country: str,
        recipient_country: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate transaction for AML compliance
        
        Returns:
            Tuple[bool, List[str]]: (is_compliant, flags)
        """
        flags = []
        
        # Check amount threshold
        if amount >= self.threshold_amount:
            flags.append(f"Large transaction (${amount:.2f}) - reporting required")
        
        # Check vague purpose
        vague_purposes = ["gift", "loan", "personal", "other"]
        if purpose.lower() in vague_purposes and amount > 5000:
            flags.append("Vague transaction purpose for large amount")
        
        # Check high-risk countries
        high_risk = ["afghanistan", "iran", "north korea", "syria"]
        if sender_country.lower() in high_risk or recipient_country.lower() in high_risk:
            flags.append(f"High-risk country involved: {sender_country} or {recipient_country}")
        
        is_compliant = len(flags) == 0
        return is_compliant, flags


class CreditScoringBiasGuardrail:
    """Ensure fair lending practices and prevent discriminatory credit decisions"""
    
    def __init__(self):
        # Protected classes under Fair Lending Act
        self.protected_attributes = [
            "race", "color", "religion", "national_origin", "sex",
            "marital_status", "age", "income_source"
        ]
    
    def validate_features(self, features: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if credit scoring features are compliant
        
        Returns:
            Tuple[bool, List[str]]: (is_compliant, prohibited_features)
        """
        prohibited = []
        
        for feature in features:
            feature_lower = feature.lower()
            for protected in self.protected_attributes:
                if protected in feature_lower:
                    prohibited.append(feature)
                    break
        
        is_compliant = len(prohibited) == 0
        return is_compliant, prohibited
    
    def check_disparate_impact(
        self,
        approval_rate_group_a: float,
        approval_rate_group_b: float
    ) -> Tuple[bool, float]:
        """
        Check for disparate impact using 80% rule
        
        Returns:
            Tuple[bool, float]: (passes_80_rule, impact_ratio)
        """
        if approval_rate_group_a == 0:
            return False, 0.0
        
        impact_ratio = approval_rate_group_b / approval_rate_group_a
        passes_80_rule = impact_ratio >= 0.8
        
        return passes_80_rule, impact_ratio


class DisclaimerGuardrail:
    """Ensure proper financial disclaimers"""
    
    def __init__(self):
        self.required_disclaimers = {
            "investment": [
                r'\bnot\s+(?:financial|investment)\s+advice\b',
                r'\bpast\s+performance\s+(?:is\s+)?not\s+(?:indicative|guarantee)\s+of\s+future\s+results\b',
                r'\binvestments\s+(?:carry|involve)\s+risk\b',
            ],
            "insurance": [
                r'\bterms\s+and\s+conditions\s+apply\b',
                r'\bnot\s+all\s+(?:coverages|policies)\s+available\b',
            ],
            "lending": [
                r'\bsubject\s+to\s+(?:credit\s+)?approval\b',
                r'\bterms\s+and\s+conditions\s+apply\b',
                r'\bAPR\s+varies\s+based\s+on\s+creditworthiness\b',
            ]
        }
    
    def validate(self, text: str, context: str) -> Tuple[bool, str]:
        """
        Check if appropriate disclaimers are present
        
        Returns:
            Tuple[bool, str]: (has_disclaimer, error_message)
        """
        if context not in self.required_disclaimers:
            return True, None
        
        disclaimers = self.required_disclaimers[context]
        has_disclaimer = any(
            re.search(disclaimer, text, re.IGNORECASE)
            for disclaimer in disclaimers
        )
        
        if not has_disclaimer:
            return False, f"Missing required {context} disclaimer"
        
        return True, None


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("INVESTMENT ADVICE GUARDRAIL")
    print("=" * 60)
    
    investment_guard = InvestmentAdviceGuardrail(is_registered_advisor=False)
    
    texts = [
        "You should buy Tesla stock now - guaranteed returns!",
        "Here's some general information about index funds. Not financial advice.",
    ]
    
    for text in texts:
        is_compliant, violations = investment_guard.validate(text)
        print(f"\nText: {text}")
        print(f"Compliant: {is_compliant}")
        if violations:
            print(f"Violations: {violations}")
    
    print("\n" + "=" * 60)
    print("FINANCIAL DATA PROTECTION GUARDRAIL")
    print("=" * 60)
    
    data_guard = FinancialDataProtectionGuardrail()
    
    text = "My credit card is 4532-1234-5678-9010 and CVV is 123"
    is_safe, detected = data_guard.validate(text)
    masked = data_guard.mask_sensitive_data(text)
    
    print(f"\nOriginal: {text}")
    print(f"Safe: {is_safe}")
    print(f"Detected: {detected}")
    print(f"Masked: {masked}")
    
    print("\n" + "=" * 60)
    print("FRAUD DETECTION GUARDRAIL")
    print("=" * 60)
    
    fraud_guard = FraudDetectionGuardrail()
    
    text = "Urgent! Verify your account now or it will be suspended. Limited time offer!"
    risk_score, indicators = fraud_guard.validate(text)
    
    print(f"\nText: {text}")
    print(f"Risk Score: {risk_score}/100")
    print(f"Indicators: {len(indicators)} fraud patterns detected")
    
    print("\n" + "=" * 60)
    print("AML COMPLIANCE GUARDRAIL")
    print("=" * 60)
    
    aml_guard = AML_ComplianceGuardrail(threshold_amount=10000)
    
    is_compliant, flags = aml_guard.validate_transaction(
        amount=15000,
        purpose="gift",
        sender_country="USA",
        recipient_country="Iran"
    )
    
    print(f"\nTransaction: $15,000 gift to Iran")
    print(f"Compliant: {is_compliant}")
    print(f"Flags: {flags}")
