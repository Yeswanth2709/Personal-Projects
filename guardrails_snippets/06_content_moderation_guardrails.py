"""
Content Moderation Guardrails
==============================
Advanced content moderation for social media, forums, and user-generated content
covering hate speech, misinformation, and community guidelines enforcement.

Industry Use Case: Social Media, Forums, Content Platforms, Community Management
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from datetime import datetime


class ViolationSeverity(Enum):
    """Content violation severity levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ModerationAction(Enum):
    """Actions to take on violating content"""
    ALLOW = "allow"
    FLAG = "flag"
    REMOVE = "remove"
    SHADOW_BAN = "shadow_ban"
    SUSPEND_USER = "suspend_user"
    PERMANENT_BAN = "permanent_ban"


class HateSpeechGuardrail:
    """Detect hate speech and discriminatory content"""
    
    def __init__(self):
        # Hate speech patterns (simplified for demonstration)
        self.hate_patterns = {
            ViolationSeverity.CRITICAL: [
                r'\b(kill|harm|attack)\s+all\s+\w+s?\b',
                r'\b\w+\s+should\s+(?:die|be\s+killed)\b',
                r'\bgenocide\s+(?:of|against)\b',
            ],
            ViolationSeverity.HIGH: [
                r'\bI\s+hate\s+all\s+\w+s?\b',
                r'\b\w+\s+are\s+(?:inferior|subhuman|worthless)\b',
                r'\bban\s+all\s+\w+s?\s+from\b',
            ],
            ViolationSeverity.MEDIUM: [
                r'\bgo\s+back\s+to\s+your\s+country\b',
                r'\btypical\s+\w+\s+behavior\b',
                r'\byou\s+people\s+are\b',
            ],
        }
        
        # Protected groups
        self.protected_groups = [
            "race", "ethnicity", "religion", "nationality", "gender",
            "sexual_orientation", "disability", "age"
        ]
    
    def validate(self, text: str) -> Tuple[ViolationSeverity, List[str], ModerationAction]:
        """
        Detect hate speech
        
        Returns:
            Tuple[ViolationSeverity, List[str], ModerationAction]: 
                (severity, matched_patterns, recommended_action)
        """
        matched_patterns = []
        max_severity = ViolationSeverity.NONE
        
        # Check patterns by severity
        for severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH, ViolationSeverity.MEDIUM]:
            for pattern in self.hate_patterns.get(severity, []):
                if re.search(pattern, text, re.IGNORECASE):
                    matched_patterns.append(pattern)
                    if severity.value > max_severity.value:
                        max_severity = severity
        
        # Determine action
        if max_severity == ViolationSeverity.CRITICAL:
            action = ModerationAction.PERMANENT_BAN
        elif max_severity == ViolationSeverity.HIGH:
            action = ModerationAction.SUSPEND_USER
        elif max_severity == ViolationSeverity.MEDIUM:
            action = ModerationAction.REMOVE
        else:
            action = ModerationAction.ALLOW
        
        return max_severity, matched_patterns, action


class MisinformationGuardrail:
    """Detect potential misinformation and false claims"""
    
    def __init__(self):
        self.misinformation_indicators = {
            "medical": [
                r'\b(?:cure|treatment)\s+for\s+(?:cancer|covid|aids)\s+(?:discovered|found)\b',
                r'\bvaccines?\s+cause\s+autism\b',
                r'\b5g\s+causes?\s+(?:cancer|covid)\b',
                r'\b(?:miracle|instant)\s+cure\b',
            ],
            "financial": [
                r'\bget\s+rich\s+quick\b',
                r'\bguaranteed\s+(?:profits?|returns?)\b',
                r'\b(?:1000|100)%\s+(?:return|profit)\b',
                r'\brisk[\s-]free\s+investment\b',
            ],
            "political": [
                r'\belection\s+(?:rigged|stolen|fraud)\b',
                r'\bproven\s+(?:conspiracy|hoax)\b',
                r'\b(?:definitely|certainly)\s+(?:fake|false)\s+news\b',
            ],
            "sensational": [
                r'\bshocking\s+truth\b',
                r'\bthey\s+don\'t\s+want\s+you\s+to\s+know\b',
                r'\b(?:mainstream\s+media|MSM)\s+(?:hiding|covering\s+up)\b',
                r'\bwake\s+up\s+sheeple\b',
            ]
        }
        
        self.fact_check_indicators = [
            r'\baccording\s+to\s+(?:study|research|expert)\b',
            r'\b(?:source|citation|reference):\b',
            r'\bpublished\s+in\s+\w+\s+journal\b',
            r'\bhttps?://(?:credible[\w-]+\.com|.gov|.edu)\b',
        ]
    
    def validate(self, text: str) -> Tuple[int, Dict[str, int], bool]:
        """
        Assess misinformation risk
        
        Returns:
            Tuple[int, Dict, bool]: 
                (risk_score 0-100, category_counts, has_citations)
        """
        category_counts = {}
        total_flags = 0
        
        for category, patterns in self.misinformation_indicators.items():
            count = sum(
                len(re.findall(pattern, text, re.IGNORECASE))
                for pattern in patterns
            )
            if count > 0:
                category_counts[category] = count
                total_flags += count
        
        # Check for fact-checking indicators
        has_citations = any(
            re.search(indicator, text, re.IGNORECASE)
            for indicator in self.fact_check_indicators
        )
        
        # Calculate risk score
        risk_score = min(total_flags * 20, 100)
        if has_citations:
            risk_score = max(0, risk_score - 30)
        
        return risk_score, category_counts, has_citations


class SpamDetectionGuardrail:
    """Detect spam and low-quality content"""
    
    def __init__(self):
        self.spam_patterns = [
            r'\bclick\s+here\s+now\b',
            r'\b(?:buy|order)\s+now\b',
            r'\blimited\s+time\s+offer\b',
            r'\bact\s+fast\b',
            r'\b(?:100%|totally)\s+free\b',
            r'\bno\s+(?:credit\s+card|payment)\s+required\b',
            r'\bmake\s+money\s+(?:fast|quickly|online)\b',
            r'\bwork\s+from\s+home\b',
        ]
        
        self.excessive_patterns = [
            r'!!!+',  # Multiple exclamation marks
            r'\b([A-Z]{3,}\s*){3,}\b',  # Excessive caps
            r'(.)\1{4,}',  # Repeated characters
            r'(https?://[^\s]+\s*){5,}',  # Multiple URLs
        ]
    
    def validate(self, text: str) -> Tuple[int, List[str]]:
        """
        Calculate spam score
        
        Returns:
            Tuple[int, List[str]]: (spam_score 0-100, violations)
        """
        violations = []
        score = 0
        
        # Check spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Spam pattern: {pattern}")
                score += 15
        
        # Check excessive patterns
        for pattern in self.excessive_patterns:
            matches = re.findall(pattern, text)
            if matches:
                violations.append(f"Excessive pattern: {pattern}")
                score += 10 * len(matches)
        
        # Check URL ratio
        words = text.split()
        urls = re.findall(r'https?://[^\s]+', text)
        if len(words) > 0:
            url_ratio = len(urls) / len(words)
            if url_ratio > 0.3:
                violations.append(f"High URL ratio: {url_ratio:.2%}")
                score += 25
        
        spam_score = min(score, 100)
        return spam_score, violations


class ProfanityGuardrail:
    """Detect and filter profanity"""
    
    def __init__(self, filter_level: str = "medium"):
        self.filter_level = filter_level
        
        # Profanity lists by severity (abbreviated for demonstration)
        self.profanity_lists = {
            "severe": ["f***", "s***", "b****"],  # Most offensive
            "moderate": ["damn", "hell", "crap"],  # Moderately offensive
            "mild": ["stupid", "idiot", "jerk"]  # Mild insults
        }
        
        self.filter_levels = {
            "strict": ["severe", "moderate", "mild"],
            "medium": ["severe", "moderate"],
            "lenient": ["severe"]
        }
    
    def validate(self, text: str) -> Tuple[bool, List[str], str]:
        """
        Check for profanity
        
        Returns:
            Tuple[bool, List[str], str]: (is_clean, found_words, filtered_text)
        """
        found_words = []
        filtered_text = text
        
        categories_to_check = self.filter_levels.get(self.filter_level, ["severe"])
        
        for category in categories_to_check:
            for word in self.profanity_lists.get(category, []):
                pattern = word.replace('*', r'\w')
                if re.search(rf'\b{pattern}\b', text, re.IGNORECASE):
                    found_words.append(word)
                    # Replace with asterisks
                    filtered_text = re.sub(
                        rf'\b{pattern}\b',
                        '*' * len(word),
                        filtered_text,
                        flags=re.IGNORECASE
                    )
        
        is_clean = len(found_words) == 0
        return is_clean, found_words, filtered_text


class SelfHarmGuardrail:
    """Detect self-harm and suicide-related content"""
    
    def __init__(self):
        self.self_harm_patterns = [
            r'\bI\s+(?:want\s+to|will)\s+(?:kill|harm)\s+myself\b',
            r'\bsuicid(?:e|al)\s+(?:thoughts?|ideation)\b',
            r'\bI\s+can\'t\s+(?:go\s+on|take\s+it\s+anymore)\b',
            r'\bend\s+(?:it\s+all|my\s+life)\b',
            r'\bbetter\s+off\s+dead\b',
            r'\bI\s+want\s+to\s+die\b',
        ]
        
        self.crisis_resources = {
            "US": "988 (Suicide & Crisis Lifeline)",
            "UK": "116 123 (Samaritans)",
            "Global": "https://findahelpline.com"
        }
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """
        Detect self-harm content
        
        Returns:
            Tuple[bool, str]: (needs_intervention, crisis_message)
        """
        for pattern in self.self_harm_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                crisis_message = (
                    "⚠️ If you're experiencing thoughts of self-harm, please reach out for help:\n"
                    + "\n".join(f"• {region}: {contact}" 
                               for region, contact in self.crisis_resources.items())
                )
                return True, crisis_message
        
        return False, None


class ChildSafetyGuardrail:
    """Protect children from inappropriate content"""
    
    def __init__(self):
        self.inappropriate_for_minors = [
            r'\b(?:sexual|explicit|adult)\s+content\b',
            r'\bviolent\s+(?:imagery|content)\b',
            r'\balcohol\s+(?:consumption|use)\b',
            r'\bdrug\s+use\b',
            r'\btobacco\s+products?\b',
            r'\bgambling\b',
        ]
        
        self.grooming_patterns = [
            r'\bdon\'t\s+tell\s+(?:your\s+)?parents\b',
            r'\bkeep\s+(?:this|our)\s+secret\b',
            r'\bcan\s+we\s+meet\s+in\s+person\b',
            r'\bsend\s+me\s+(?:a\s+)?(?:photo|picture)\b',
            r'\bhow\s+old\s+are\s+you\b.*(?:alone|home)\b',
        ]
    
    def validate(
        self,
        text: str,
        user_age: Optional[int] = None
    ) -> Tuple[bool, ViolationSeverity, List[str]]:
        """
        Check content safety for children
        
        Returns:
            Tuple[bool, ViolationSeverity, List[str]]: 
                (is_safe, severity, violations)
        """
        violations = []
        max_severity = ViolationSeverity.NONE
        
        # Check for grooming patterns (critical)
        for pattern in self.grooming_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Grooming indicator: {pattern}")
                max_severity = ViolationSeverity.CRITICAL
        
        # Check for inappropriate content
        if user_age and user_age < 18:
            for pattern in self.inappropriate_for_minors:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append(f"Inappropriate for minors: {pattern}")
                    if max_severity.value < ViolationSeverity.HIGH.value:
                        max_severity = ViolationSeverity.HIGH
        
        is_safe = len(violations) == 0
        return is_safe, max_severity, violations


class CopyrightGuardrail:
    """Detect potential copyright violations"""
    
    def __init__(self):
        self.copyright_indicators = [
            r'©\s*(?:19|20)\d{2}',
            r'\(c\)\s*(?:19|20)\d{2}',
            r'copyright\s+(?:19|20)\d{2}',
            r'all\s+rights\s+reserved',
        ]
        
        self.verbatim_thresholds = {
            "short": 50,  # words
            "medium": 100,
            "long": 200
        }
    
    def validate(
        self,
        text: str,
        known_sources: Optional[List[str]] = None
    ) -> Tuple[int, List[str]]:
        """
        Assess copyright risk
        
        Returns:
            Tuple[int, List[str]]: (risk_score 0-100, indicators)
        """
        indicators = []
        risk_score = 0
        
        # Check for copyright notices
        for pattern in self.copyright_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                indicators.append("Copyright notice found")
                risk_score += 30
        
        # Check text length (longer = higher risk if verbatim)
        word_count = len(text.split())
        if word_count > self.verbatim_thresholds["long"]:
            indicators.append(f"Long text ({word_count} words) - verify originality")
            risk_score += 20
        
        # Check for quotes without attribution
        quote_pattern = r'["""]([^"""]{50,})["""]'
        quotes = re.findall(quote_pattern, text)
        if quotes:
            # Check if attribution follows
            has_attribution = re.search(
                r'["""][^"""]+["""]\s*[-–—]\s*\w+',
                text
            )
            if not has_attribution:
                indicators.append(f"Unattributed quotes found ({len(quotes)})")
                risk_score += 25
        
        risk_score = min(risk_score, 100)
        return risk_score, indicators


class CommunityGuidelinesGuardrail:
    """Enforce platform-specific community guidelines"""
    
    def __init__(self, guidelines: Optional[Dict[str, List[str]]] = None):
        self.guidelines = guidelines or self._default_guidelines()
    
    def _default_guidelines(self) -> Dict[str, List[str]]:
        """Default community guidelines"""
        return {
            "harassment": [
                r'\bstupid\s+\w+\b',
                r'\bshut\s+up\b',
                r'\byou\'re\s+(?:an?\s+)?(?:idiot|moron)\b',
            ],
            "impersonation": [
                r'\bI\s+am\s+(?:the\s+)?(?:CEO|founder|president)\s+of\s+\w+\b',
                r'\bofficial\s+account\s+of\b',
            ],
            "manipulation": [
                r'\bvote\s+manipulation\b',
                r'\bupvote\s+if\s+you\s+agree\b',
                r'\blike\s+and\s+share\b',
            ],
            "doxxing": [
                r'\bhere\'s\s+(?:his|her|their)\s+(?:address|phone|email)\b',
                r'\bpersonal\s+information:\b',
            ]
        }
    
    def validate(self, text: str) -> Dict[str, List[str]]:
        """
        Check against community guidelines
        
        Returns:
            Dict[str, List[str]]: violations by category
        """
        violations = {}
        
        for category, patterns in self.guidelines.items():
            category_violations = []
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    category_violations.append(pattern)
            
            if category_violations:
                violations[category] = category_violations
        
        return violations


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("HATE SPEECH GUARDRAIL")
    print("=" * 60)
    
    hate_guard = HateSpeechGuardrail()
    
    test_texts = [
        "I disagree with this policy",
        "I hate all immigrants, they should go back",
    ]
    
    for text in test_texts:
        severity, patterns, action = hate_guard.validate(text)
        print(f"\nText: {text}")
        print(f"Severity: {severity.name}")
        print(f"Action: {action.value}")
    
    print("\n" + "=" * 60)
    print("MISINFORMATION GUARDRAIL")
    print("=" * 60)
    
    misinfo_guard = MisinformationGuardrail()
    
    text = "5G causes COVID! This is the shocking truth they don't want you to know!"
    risk_score, categories, has_citations = misinfo_guard.validate(text)
    
    print(f"\nText: {text}")
    print(f"Risk Score: {risk_score}/100")
    print(f"Categories: {categories}")
    print(f"Has Citations: {has_citations}")
    
    print("\n" + "=" * 60)
    print("SPAM DETECTION GUARDRAIL")
    print("=" * 60)
    
    spam_guard = SpamDetectionGuardrail()
    
    text = "CLICK HERE NOW!!! Buy now! Limited time offer! ACT FAST!!!"
    spam_score, violations = spam_guard.validate(text)
    
    print(f"\nText: {text}")
    print(f"Spam Score: {spam_score}/100")
    print(f"Violations: {len(violations)}")
    
    print("\n" + "=" * 60)
    print("SELF-HARM GUARDRAIL")
    print("=" * 60)
    
    self_harm_guard = SelfHarmGuardrail()
    
    text = "I want to kill myself, I can't take it anymore"
    needs_help, message = self_harm_guard.validate(text)
    
    print(f"\nText: {text}")
    print(f"Needs Intervention: {needs_help}")
    if message:
        print(f"\n{message}")
