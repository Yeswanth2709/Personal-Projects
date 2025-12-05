# Guardrails Code Snippets

Comprehensive collection of production-ready guardrails for AI systems covering input validation, output safety, industry-specific compliance, and security across all major use cases.

## 🛡️ Overview

These guardrails provide essential safety and compliance layers for AI applications across multiple industries. Each guardrail module is independently usable and can be integrated into existing systems.

## 📂 Guardrail Modules

### 1. **Input Validation Guardrails** (`01_input_validation_guardrails.py`)

**Purpose:** Validate and sanitize user inputs before processing

**Guardrails:**

- **InputValidationGuardrail** - SQL injection, XSS, command injection detection
- **PII_DetectionGuardrail** - Detect and mask personally identifiable information
- **ContentTypeGuardrail** - Validate input format (JSON, URL, email, etc.)
- **PromptInjectionGuardrail** - Detect prompt injection attacks
- **RateLimitGuardrail** - Rate limiting and throttling

**Use Cases:** All AI applications, chatbots, API endpoints

**Example:**

```python
from guardrails_snippets.input_validation_guardrails import InputValidationGuardrail

validator = InputValidationGuardrail({
    "max_length": 1000,
    "allow_html": False
})

is_valid, sanitized, error = validator.validate(user_input)
if not is_valid:
    print(f"Input rejected: {error}")
```

---

### 2. **Output Safety Guardrails** (`02_output_safety_guardrails.py`)

**Purpose:** Ensure AI outputs are safe, unbiased, and appropriate

**Guardrails:**

- **ToxicityGuardrail** - Detect toxic, offensive, or harmful content (5 severity levels)
- **BiasDetectionGuardrail** - Identify biased or discriminatory statements
- **ProfessionalismGuardrail** - Ensure appropriate tone and language
- **FactualityGuardrail** - Check for overconfident claims and hallucinations
- **PrivacyGuardrail** - Prevent leakage of sensitive information
- **ContentLengthGuardrail** - Validate response completeness
- **JSONOutputGuardrail** - Validate structured outputs
- **RefusalGuardrail** - Ensure proper refusal of inappropriate requests

**Use Cases:** Content generation, customer service, chatbots

**Example:**

```python
from guardrails_snippets.output_safety_guardrails import ToxicityGuardrail, ToxicityLevel

toxicity_guard = ToxicityGuardrail(threshold=ToxicityLevel.MEDIUM)
is_safe, level, patterns = toxicity_guard.validate(ai_response)
```

---

### 3. **Healthcare Compliance Guardrails** (`03_healthcare_compliance_guardrails.py`)

**Purpose:** HIPAA compliance for healthcare AI applications

**Guardrails:**

- **HIPAA_ComplianceGuardrail** - Detect PHI (Protected Health Information) in 18 identifier categories
- **MedicalDisclaimerGuardrail** - Ensure medical disclaimers are present
- **PrescriptionGuardrail** - Prevent AI from prescribing medications
- **DiagnosisGuardrail** - Prevent inappropriate medical diagnoses
- **EmergencyDetectionGuardrail** - Detect medical emergencies and provide proper guidance
- **MinorProtectionGuardrail** - Additional protections for children
- **ConsentGuardrail** - Ensure proper consent for data collection

**Use Cases:** Telemedicine, EHR systems, health chatbots, medical AI

**Example:**

```python
from guardrails_snippets.healthcare_compliance_guardrails import HIPAA_ComplianceGuardrail

hipaa_guard = HIPAA_ComplianceGuardrail()
compliance, violations = hipaa_guard.validate(patient_data)

if compliance != ComplianceLevel.COMPLIANT:
    print(f"HIPAA violation detected: {violations}")
```

---

### 4. **Financial Compliance Guardrails** (`04_financial_compliance_guardrails.py`)

**Purpose:** Regulatory compliance for financial services

**Guardrails:**

- **InvestmentAdviceGuardrail** - Prevent unlicensed investment advice (SEC/FINRA compliance)
- **FinancialDataProtectionGuardrail** - Protect credit cards, account numbers, SSN (PCI-DSS)
- **FraudDetectionGuardrail** - Detect fraud attempts and social engineering
- **KYC_ComplianceGuardrail** - Know Your Customer validation
- **AML_ComplianceGuardrail** - Anti-Money Laundering compliance and transaction structuring detection
- **CreditScoringBiasGuardrail** - Fair lending practices (80% rule for disparate impact)
- **DisclaimerGuardrail** - Financial disclaimers for investment/insurance/lending

**Use Cases:** Banking, fintech, investment platforms, lending

**Example:**

```python
from guardrails_snippets.financial_compliance_guardrails import AML_ComplianceGuardrail

aml_guard = AML_ComplianceGuardrail(threshold_amount=10000)
is_compliant, flags = aml_guard.validate_transaction(
    amount=15000,
    purpose="gift",
    sender_country="USA",
    recipient_country="Iran"
)
```

---

### 5. **Enterprise Security Guardrails** (`05_enterprise_security_guardrails.py`)

**Purpose:** Security controls for enterprise AI systems

**Guardrails:**

- **DataLeakageGuardrail** - Prevent leakage of API keys, tokens, passwords, secrets
- **AccessControlGuardrail** - Role-based access control (RBAC) with 4 security levels
- **InjectionAttackGuardrail** - Detect SQL, XSS, command, LDAP, NoSQL injections
- **IPWhitelistGuardrail** - IP-based access control with CIDR support
- **SessionManagementGuardrail** - Session timeout and concurrent session limits
- **EncryptionGuardrail** - Validate encryption algorithms and key strength
- **ComplianceLoggingGuardrail** - Comprehensive audit logging

**Use Cases:** Enterprise SaaS, cloud services, corporate IT, B2B platforms

**Example:**

```python
from guardrails_snippets.enterprise_security_guardrails import DataLeakageGuardrail

leakage_guard = DataLeakageGuardrail()
is_safe, detected = leakage_guard.validate(text)
sanitized = leakage_guard.sanitize(text)
```

---

### 6. **Content Moderation Guardrails** (`06_content_moderation_guardrails.py`)

**Purpose:** Moderate user-generated content for social platforms

**Guardrails:**

- **HateSpeechGuardrail** - Detect hate speech with 3 severity levels and moderation actions
- **MisinformationGuardrail** - Identify misinformation across medical/financial/political domains
- **SpamDetectionGuardrail** - Spam scoring with URL ratio analysis
- **ProfanityGuardrail** - Profanity filtering with 3 strictness levels
- **SelfHarmGuardrail** - Detect self-harm content and provide crisis resources
- **ChildSafetyGuardrail** - Protect children from inappropriate content and grooming
- **CopyrightGuardrail** - Detect potential copyright violations
- **CommunityGuidelinesGuardrail** - Enforce platform-specific rules

**Use Cases:** Social media, forums, content platforms, community management

**Example:**

```python
from guardrails_snippets.content_moderation_guardrails import HateSpeechGuardrail

hate_guard = HateSpeechGuardrail()
severity, patterns, action = hate_guard.validate(user_comment)

if action == ModerationAction.REMOVE:
    # Remove content
    pass
```

---

## 🚀 Quick Start

### Installation

```bash
# No external dependencies required - uses only Python standard library
# For production use, consider adding:
pip install regex  # Better regex performance
```

### Basic Usage Pattern

```python
# 1. Import the guardrail
from guardrails_snippets.input_validation_guardrails import InputValidationGuardrail

# 2. Initialize with configuration
guardrail = InputValidationGuardrail({
    "max_length": 1000,
    "allow_html": False,
    "blocked_patterns": [r'custom_pattern']
})

# 3. Validate input
is_valid, result, error = guardrail.validate(user_input)

# 4. Handle result
if not is_valid:
    return {"error": error}
else:
    process(result)
```

### Combining Multiple Guardrails

```python
class GuardrailPipeline:
    def __init__(self):
        self.input_guard = InputValidationGuardrail()
        self.pii_guard = PII_DetectionGuardrail(mask_pii=True)
        self.injection_guard = PromptInjectionGuardrail()

    def validate_input(self, text: str) -> Tuple[bool, str, str]:
        # Step 1: Input validation
        is_valid, sanitized, error = self.input_guard.validate(text)
        if not is_valid:
            return False, text, error

        # Step 2: PII detection
        has_no_pii, masked, detected = self.pii_guard.validate(sanitized)
        if not has_no_pii:
            return False, sanitized, f"PII detected: {list(detected.keys())}"

        # Step 3: Prompt injection check
        is_safe, error = self.injection_guard.validate(masked)
        if not is_safe:
            return False, masked, error

        return True, masked, None
```

## 🏗️ Architecture

### Guardrail Design Pattern

All guardrails follow a consistent pattern:

```python
class GuardrailName:
    def __init__(self, config: Optional[Dict] = None):
        """Initialize with configuration"""
        pass

    def validate(self, input_data: Any) -> Tuple[bool, ...]:
        """
        Validate input/output
        Returns: (is_valid, additional_data...)
        """
        pass
```

### Return Value Conventions

- **Boolean first**: Always return validation result as first element
- **Processed data**: Return sanitized/processed data when applicable
- **Error messages**: Return descriptive error messages for failures
- **Metadata**: Return detection details, scores, or categories

## 🔧 Configuration

### Environment-Specific Settings

```python
# Development
config = {
    "strict_mode": False,
    "log_violations": True,
    "auto_sanitize": True
}

# Production
config = {
    "strict_mode": True,
    "log_violations": True,
    "auto_sanitize": False,  # Manual review
    "alert_on_violation": True
}
```

### Industry-Specific Presets

```python
# Healthcare
from guardrails_snippets.healthcare_compliance_guardrails import *
guardrails = [
    HIPAA_ComplianceGuardrail(),
    MedicalDisclaimerGuardrail(),
    EmergencyDetectionGuardrail()
]

# Finance
from guardrails_snippets.financial_compliance_guardrails import *
guardrails = [
    InvestmentAdviceGuardrail(is_registered_advisor=False),
    FinancialDataProtectionGuardrail(),
    AML_ComplianceGuardrail(threshold_amount=10000)
]
```

## 📊 Performance Considerations

### Optimization Tips

1. **Precompile Regex Patterns**: For high-throughput systems

```python
import re
self.pattern = re.compile(r'pattern', re.IGNORECASE)
```

2. **Parallel Processing**: Validate multiple guardrails concurrently

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    results = list(executor.map(validate, guardrails))
```

3. **Caching**: Cache validation results for identical inputs

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def validate(text: str) -> Tuple[bool, str]:
    # Validation logic
    pass
```

4. **Early Exit**: Order guardrails by failure likelihood

## 🧪 Testing

### Unit Testing Example

```python
import unittest
from guardrails_snippets.input_validation_guardrails import InputValidationGuardrail

class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.validator = InputValidationGuardrail()

    def test_sql_injection_detection(self):
        malicious = "SELECT * FROM users WHERE 1=1 OR 1=1--"
        is_valid, _, error = self.validator.validate(malicious)
        self.assertFalse(is_valid)
        self.assertIn("SQL injection", error)

    def test_normal_input(self):
        normal = "Hello, how can I help you?"
        is_valid, sanitized, error = self.validator.validate(normal)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
```

### Integration Testing

```python
def test_guardrail_pipeline():
    pipeline = GuardrailPipeline()

    # Test case 1: Clean input
    result = pipeline.validate_input("What's the weather?")
    assert result[0] == True

    # Test case 2: SQL injection
    result = pipeline.validate_input("DROP TABLE users;")
    assert result[0] == False
    assert "SQL injection" in result[2]
```

## 🔐 Security Best Practices

### 1. Defense in Depth

Use multiple complementary guardrails:

```python
guardrails = [
    InputValidationGuardrail(),      # First line
    PII_DetectionGuardrail(),        # Second line
    PromptInjectionGuardrail(),      # Third line
    ToxicityGuardrail()              # Fourth line
]
```

### 2. Fail Secure

Default to denying access when uncertain:

```python
if not is_valid or error:
    return reject_request()  # Fail secure
```

### 3. Audit Everything

Log all guardrail violations:

```python
if not is_valid:
    audit_log.record({
        "timestamp": datetime.now(),
        "violation": error,
        "input": masked_input,
        "user_id": user_id
    })
```

### 4. Regular Updates

Update patterns and rules regularly:

```python
# Schedule pattern updates
def update_patterns():
    fetch_latest_patterns()
    reload_guardrails()
```

## 📈 Metrics & Monitoring

### Key Metrics to Track

```python
class GuardrailMetrics:
    def __init__(self):
        self.total_validations = 0
        self.violations = 0
        self.false_positives = 0
        self.latency = []

    def record(self, is_valid: bool, duration: float):
        self.total_validations += 1
        if not is_valid:
            self.violations += 1
        self.latency.append(duration)

    def get_stats(self):
        return {
            "violation_rate": self.violations / self.total_validations,
            "avg_latency_ms": sum(self.latency) / len(self.latency) * 1000,
            "p95_latency_ms": sorted(self.latency)[int(len(self.latency) * 0.95)] * 1000
        }
```

## 🌍 Real-World Examples

### Example 1: Healthcare Chatbot

```python
from guardrails_snippets.healthcare_compliance_guardrails import *
from guardrails_snippets.output_safety_guardrails import *

class HealthcareChatbot:
    def __init__(self):
        self.hipaa_guard = HIPAA_ComplianceGuardrail()
        self.disclaimer_guard = MedicalDisclaimerGuardrail()
        self.emergency_guard = EmergencyDetectionGuardrail()

    def process_message(self, user_input: str, ai_response: str):
        # Check for emergency
        is_emergency, msg = self.emergency_guard.detect_emergency(user_input)
        if is_emergency:
            return self.handle_emergency()

        # Validate AI response
        compliance, violations = self.hipaa_guard.validate(ai_response)
        if compliance != ComplianceLevel.COMPLIANT:
            return "I cannot share that information."

        # Check disclaimer
        needs_disclaimer, error = self.disclaimer_guard.validate(ai_response)
        if not needs_disclaimer:
            ai_response += "\n\nThis is not medical advice. Consult your doctor."

        return ai_response
```

### Example 2: Financial Advisory Platform

```python
from guardrails_snippets.financial_compliance_guardrails import *

class FinancialAdvisor:
    def __init__(self, is_licensed: bool):
        self.investment_guard = InvestmentAdviceGuardrail(
            is_registered_advisor=is_licensed
        )
        self.data_guard = FinancialDataProtectionGuardrail()
        self.fraud_guard = FraudDetectionGuardrail()

    def validate_response(self, response: str):
        # Check investment advice compliance
        is_compliant, violations = self.investment_guard.validate(response)
        if not is_compliant:
            response += "\n\nNot financial advice. Consult a licensed advisor."

        # Mask sensitive financial data
        response = self.data_guard.mask_sensitive_data(response)

        return response
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Too many false positives

```python
# Solution: Adjust thresholds
validator = InputValidationGuardrail({
    "max_length": 5000,  # Increase limit
    "blocked_patterns": []  # Reduce restrictions
})
```

**Issue**: Performance degradation

```python
# Solution: Use compiled patterns and caching
import re
self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
```

**Issue**: Missing edge cases

```python
# Solution: Add custom patterns
custom_patterns = [
    r'your_specific_pattern',
    r'another_edge_case'
]
validator.blocked_patterns.extend(custom_patterns)
```

## 📚 Additional Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **HIPAA Compliance**: https://www.hhs.gov/hipaa/
- **PCI DSS Standards**: https://www.pcisecuritystandards.org/
- **AI Safety Guidelines**: https://www.nist.gov/itl/ai-risk-management-framework

## 🤝 Contributing

To add new guardrails:

1. Follow the standard guardrail pattern
2. Include comprehensive docstrings
3. Add example usage in `__main__`
4. Update this README

## 📄 License

These code snippets are provided as examples for educational and reference purposes.

---

**Version**: 1.0.0  
**Last Updated**: December 2024
