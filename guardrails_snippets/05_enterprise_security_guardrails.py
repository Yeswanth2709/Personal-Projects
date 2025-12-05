"""
Enterprise Security Guardrails
===============================
Security-focused guardrails for enterprise AI systems covering
data leakage prevention, access control, and cybersecurity.

Industry Use Case: Enterprise Software, SaaS, Cloud Services, Corporate IT
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from datetime import datetime, timedelta


class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


class DataLeakageGuardrail:
    """Prevent leakage of sensitive corporate data"""
    
    def __init__(self):
        self.sensitive_patterns = {
            "api_key": r'\b(?:api[_-]?key|apikey)[\s:=]+["\']?([A-Za-z0-9_\-]{20,})["\']?\b',
            "bearer_token": r'\bBearer\s+[A-Za-z0-9\-\._~\+\/]+=*\b',
            "aws_key": r'\b(?:AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\b',
            "private_key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
            "jwt_token": r'\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b',
            "database_connection": r'(?:mongodb|mysql|postgresql|redis)://[^\s]+',
            "slack_token": r'\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,}\b',
            "github_token": r'\bgh[pousr]_[A-Za-z0-9]{36,}\b',
            "password_plain": r'\b(?:password|passwd|pwd)[\s:=]+["\']?([^\s"\']{8,})["\']?\b',
            "internal_ip": r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b',
            "internal_domain": r'\b[\w-]+\.(?:local|internal|corp|private)\b',
        }
        
        self.code_snippet_patterns = [
            r'```[\s\S]*?```',
            r'`[^`]+`',
            r'\bdef\s+\w+\s*\(',
            r'\bclass\s+\w+\s*[:\(]',
            r'\bimport\s+\w+',
        ]
    
    def validate(self, text: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Detect sensitive data leakage
        
        Returns:
            Tuple[bool, Dict]: (is_safe, detected_leaks)
        """
        detected = {}
        
        for leak_type, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[leak_type] = [m if isinstance(m, str) else m[0] for m in matches]
        
        # Check for code snippets with potential secrets
        has_code = any(re.search(pattern, text) for pattern in self.code_snippet_patterns)
        if has_code:
            detected["code_snippet"] = ["Code snippet detected - review for secrets"]
        
        is_safe = len(detected) == 0
        return is_safe, detected
    
    def sanitize(self, text: str) -> str:
        """Remove sensitive data from text"""
        sanitized = text
        
        # Redact API keys
        sanitized = re.sub(
            r'\b(?:api[_-]?key|apikey)[\s:=]+["\']?[A-Za-z0-9_\-]{20,}["\']?\b',
            'api_key: [REDACTED]',
            sanitized,
            flags=re.IGNORECASE
        )
        
        # Redact tokens
        sanitized = re.sub(
            r'\bBearer\s+[A-Za-z0-9\-\._~\+\/]+=*\b',
            'Bearer [REDACTED]',
            sanitized
        )
        
        # Redact private keys
        sanitized = re.sub(
            r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC )?PRIVATE KEY-----',
            '-----BEGIN PRIVATE KEY-----\n[REDACTED]\n-----END PRIVATE KEY-----',
            sanitized
        )
        
        # Redact database connections
        sanitized = re.sub(
            r'(?:mongodb|mysql|postgresql|redis)://[^\s]+',
            '[DATABASE_URL_REDACTED]',
            sanitized,
            flags=re.IGNORECASE
        )
        
        # Redact internal IPs
        sanitized = re.sub(
            r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b',
            '[INTERNAL_IP]',
            sanitized
        )
        
        return sanitized


class AccessControlGuardrail:
    """Enforce role-based access control"""
    
    def __init__(self):
        self.roles_hierarchy = {
            "admin": ["read", "write", "delete", "manage_users", "configure"],
            "manager": ["read", "write", "delete"],
            "user": ["read", "write"],
            "viewer": ["read"],
            "guest": []
        }
        
        self.data_classifications = {
            SecurityLevel.PUBLIC: ["guest", "viewer", "user", "manager", "admin"],
            SecurityLevel.INTERNAL: ["user", "manager", "admin"],
            SecurityLevel.CONFIDENTIAL: ["manager", "admin"],
            SecurityLevel.SECRET: ["admin"]
        }
    
    def check_permission(
        self,
        user_role: str,
        required_permission: str
    ) -> Tuple[bool, str]:
        """
        Check if user role has required permission
        
        Returns:
            Tuple[bool, str]: (has_permission, error_message)
        """
        if user_role not in self.roles_hierarchy:
            return False, f"Unknown role: {user_role}"
        
        permissions = self.roles_hierarchy[user_role]
        
        if required_permission in permissions:
            return True, None
        else:
            return False, f"Role '{user_role}' lacks permission '{required_permission}'"
    
    def check_data_access(
        self,
        user_role: str,
        data_classification: SecurityLevel
    ) -> Tuple[bool, str]:
        """
        Check if user can access data based on classification
        
        Returns:
            Tuple[bool, str]: (can_access, error_message)
        """
        allowed_roles = self.data_classifications.get(data_classification, [])
        
        if user_role in allowed_roles:
            return True, None
        else:
            return False, f"Role '{user_role}' cannot access '{data_classification.value}' data"
    
    def audit_log(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str
    ) -> Dict:
        """Create audit log entry"""
        return {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "log_hash": hashlib.sha256(
                f"{user_id}{action}{resource}{result}".encode()
            ).hexdigest()[:16]
        }


class InjectionAttackGuardrail:
    """Detect various injection attacks"""
    
    def __init__(self):
        self.sql_injection_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(--\s*$)",
            r"(/\*.*\*/)",
            r"(\bOR\b.*=.*)",
            r"(;\s*\bDROP\b)",
            r"(\bEXEC\b.*\()",
            r"(\bxp_cmdshell\b)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<embed[^>]*>",
            r"<object[^>]*>",
            r"eval\s*\(",
            r"expression\s*\(",
        ]
        
        self.command_injection_patterns = [
            r"[;&|]\s*(rm|cat|ls|wget|curl|nc|bash|sh|python|perl|ruby)",
            r"\$\(.*\)",
            r"`.*`",
            r">\s*/dev/null",
            r"\|\s*tee",
            r"&&\s*\w+",
        ]
        
        self.ldap_injection_patterns = [
            r"\*\)",
            r"\(\|",
            r"\(\&",
            r"admin\*",
        ]
        
        self.nosql_injection_patterns = [
            r"\$where",
            r"\$ne",
            r"\$gt",
            r"\$regex",
        ]
    
    def validate(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect injection attacks
        
        Returns:
            Tuple[bool, List[str]]: (is_safe, detected_attacks)
        """
        detected = []
        
        # SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(f"SQL injection: {pattern}")
        
        # XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(f"XSS: {pattern}")
        
        # Command injection
        for pattern in self.command_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(f"Command injection: {pattern}")
        
        # LDAP injection
        for pattern in self.ldap_injection_patterns:
            if re.search(pattern, text):
                detected.append(f"LDAP injection: {pattern}")
        
        # NoSQL injection
        for pattern in self.nosql_injection_patterns:
            if re.search(pattern, text):
                detected.append(f"NoSQL injection: {pattern}")
        
        is_safe = len(detected) == 0
        return is_safe, detected


class IPWhitelistGuardrail:
    """IP-based access control"""
    
    def __init__(self, whitelist: Optional[List[str]] = None):
        self.whitelist = set(whitelist) if whitelist else set()
        self.whitelist_patterns = []
        
        # Add CIDR support
        for ip in self.whitelist:
            if '/' in ip:  # CIDR notation
                self.whitelist_patterns.append(self._cidr_to_regex(ip))
    
    def _cidr_to_regex(self, cidr: str) -> str:
        """Convert CIDR notation to regex pattern (simplified)"""
        base_ip, prefix = cidr.split('/')
        parts = base_ip.split('.')
        prefix_int = int(prefix)
        
        # Simplified - in production use ipaddress module
        if prefix_int >= 24:
            return rf"{parts[0]}\.{parts[1]}\.{parts[2]}\.\d+"
        elif prefix_int >= 16:
            return rf"{parts[0]}\.{parts[1]}\.\d+\.\d+"
        else:
            return rf"{parts[0]}\.\d+\.\d+\.\d+"
    
    def validate(self, ip_address: str) -> Tuple[bool, str]:
        """
        Check if IP is whitelisted
        
        Returns:
            Tuple[bool, str]: (is_allowed, error_message)
        """
        if not self.whitelist:
            return True, None  # No whitelist = allow all
        
        # Direct match
        if ip_address in self.whitelist:
            return True, None
        
        # Pattern match (CIDR)
        for pattern in self.whitelist_patterns:
            if re.match(pattern, ip_address):
                return True, None
        
        return False, f"IP {ip_address} not in whitelist"


class SessionManagementGuardrail:
    """Manage session security"""
    
    def __init__(
        self,
        session_timeout_minutes: int = 30,
        max_concurrent_sessions: int = 3
    ):
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_concurrent_sessions = max_concurrent_sessions
        self.sessions: Dict[str, List[Dict]] = {}
    
    def create_session(self, user_id: str, ip_address: str) -> Dict:
        """Create new session"""
        session = {
            "session_id": hashlib.sha256(
                f"{user_id}{datetime.now().isoformat()}{ip_address}".encode()
            ).hexdigest(),
            "user_id": user_id,
            "ip_address": ip_address,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "is_active": True
        }
        
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        
        self.sessions[user_id].append(session)
        
        # Enforce max concurrent sessions
        if len(self.sessions[user_id]) > self.max_concurrent_sessions:
            self._cleanup_old_sessions(user_id)
        
        return session
    
    def validate_session(
        self,
        user_id: str,
        session_id: str
    ) -> Tuple[bool, str]:
        """
        Validate session
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if user_id not in self.sessions:
            return False, "No active sessions"
        
        user_sessions = self.sessions[user_id]
        session = next((s for s in user_sessions if s["session_id"] == session_id), None)
        
        if not session:
            return False, "Session not found"
        
        if not session["is_active"]:
            return False, "Session expired"
        
        # Check timeout
        time_since_activity = datetime.now() - session["last_activity"]
        if time_since_activity > self.session_timeout:
            session["is_active"] = False
            return False, "Session timed out"
        
        # Update last activity
        session["last_activity"] = datetime.now()
        
        return True, None
    
    def _cleanup_old_sessions(self, user_id: str):
        """Remove oldest sessions"""
        sessions = self.sessions[user_id]
        sessions.sort(key=lambda s: s["last_activity"], reverse=True)
        
        # Keep only max_concurrent_sessions most recent
        for session in sessions[self.max_concurrent_sessions:]:
            session["is_active"] = False


class EncryptionGuardrail:
    """Ensure data encryption standards"""
    
    def __init__(self):
        self.weak_algorithms = [
            "md5", "sha1", "des", "rc4", "rc2"
        ]
        
        self.strong_algorithms = [
            "aes-256", "rsa-2048", "rsa-4096", "sha256", "sha512", "bcrypt", "scrypt"
        ]
    
    def validate_algorithm(self, algorithm: str) -> Tuple[bool, str]:
        """
        Check if encryption algorithm is secure
        
        Returns:
            Tuple[bool, str]: (is_secure, warning_message)
        """
        algorithm_lower = algorithm.lower()
        
        if any(weak in algorithm_lower for weak in self.weak_algorithms):
            return False, f"Weak encryption algorithm: {algorithm}"
        
        if any(strong in algorithm_lower for strong in self.strong_algorithms):
            return True, None
        
        return False, f"Unknown encryption algorithm: {algorithm}"
    
    def check_key_strength(
        self,
        key_length: int,
        algorithm_type: str
    ) -> Tuple[bool, str]:
        """
        Validate encryption key strength
        
        Returns:
            Tuple[bool, str]: (is_strong, warning_message)
        """
        min_lengths = {
            "symmetric": 256,
            "rsa": 2048,
            "ecc": 256,
            "hash": 256
        }
        
        min_length = min_lengths.get(algorithm_type.lower(), 256)
        
        if key_length < min_length:
            return False, f"{algorithm_type} key too short: {key_length} bits (minimum {min_length})"
        
        return True, None


class ComplianceLoggingGuardrail:
    """Ensure comprehensive audit logging"""
    
    def __init__(self):
        self.required_fields = [
            "timestamp",
            "user_id",
            "action",
            "resource",
            "result",
            "ip_address"
        ]
    
    def validate_log(self, log_entry: Dict) -> Tuple[bool, List[str]]:
        """
        Validate log entry completeness
        
        Returns:
            Tuple[bool, List[str]]: (is_complete, missing_fields)
        """
        missing = [
            field for field in self.required_fields
            if field not in log_entry or log_entry[field] is None
        ]
        
        is_complete = len(missing) == 0
        return is_complete, missing
    
    def create_audit_log(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        ip_address: str,
        additional_data: Optional[Dict] = None
    ) -> Dict:
        """Create complete audit log entry"""
        log = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "ip_address": ip_address,
            "log_id": hashlib.sha256(
                f"{user_id}{action}{datetime.now().isoformat()}".encode()
            ).hexdigest(),
        }
        
        if additional_data:
            log["additional_data"] = additional_data
        
        return log


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("DATA LEAKAGE GUARDRAIL")
    print("=" * 60)
    
    leakage_guard = DataLeakageGuardrail()
    
    text = "Here's the API key: sk_live_abc123xyz789. Connect to mongodb://user:pass@localhost/db"
    is_safe, detected = leakage_guard.validate(text)
    sanitized = leakage_guard.sanitize(text)
    
    print(f"\nOriginal: {text}")
    print(f"Safe: {is_safe}")
    print(f"Detected: {detected}")
    print(f"Sanitized: {sanitized}")
    
    print("\n" + "=" * 60)
    print("ACCESS CONTROL GUARDRAIL")
    print("=" * 60)
    
    access_guard = AccessControlGuardrail()
    
    has_perm, error = access_guard.check_permission("user", "delete")
    print(f"\nUser role can delete: {has_perm}")
    if error:
        print(f"Error: {error}")
    
    can_access, error = access_guard.check_data_access("user", SecurityLevel.SECRET)
    print(f"\nUser role can access SECRET data: {can_access}")
    if error:
        print(f"Error: {error}")
    
    print("\n" + "=" * 60)
    print("INJECTION ATTACK GUARDRAIL")
    print("=" * 60)
    
    injection_guard = InjectionAttackGuardrail()
    
    test_inputs = [
        "SELECT * FROM users WHERE id=1",
        "admin' OR '1'='1'--",
        "<script>alert('xss')</script>",
    ]
    
    for test_input in test_inputs:
        is_safe, detected = injection_guard.validate(test_input)
        print(f"\nInput: {test_input}")
        print(f"Safe: {is_safe}")
        if detected:
            print(f"Attacks detected: {len(detected)}")
    
    print("\n" + "=" * 60)
    print("SESSION MANAGEMENT GUARDRAIL")
    print("=" * 60)
    
    session_guard = SessionManagementGuardrail(session_timeout_minutes=30)
    
    session = session_guard.create_session("user123", "192.168.1.100")
    print(f"\nCreated session: {session['session_id'][:16]}...")
    
    is_valid, error = session_guard.validate_session("user123", session["session_id"])
    print(f"Session valid: {is_valid}")
