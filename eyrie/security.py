"""
Castle Wyvern Security Enhancements
Feature 18: Audit logging, encryption, and security hardening

Provides:
- Comprehensive audit logging
- Encryption at rest for sensitive data
- API key management
- Access control and permissions
- Security scanning
- Intrusion detection
"""

import os
import sys
import json
import hashlib
import hmac
import secrets
import threading
from typing import Dict, List, Optional, Callable, Any, Set, cast
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import re


class AuditLevel(Enum):
    """Audit log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"  # For security-specific events


@dataclass
class AuditEntry:
    """A single audit log entry."""

    timestamp: str
    level: str
    category: str
    action: str
    user: str
    details: Dict[str, Any]
    source_ip: str = "localhost"
    session_id: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "AuditEntry":
        return cls(**data)


class AuditLogger:
    """
    Comprehensive audit logging for Castle Wyvern.

    Tracks:
    - All user commands
    - Authentication events
    - Data access
    - Configuration changes
    - Security events
    """

    def __init__(self, log_dir: str = None, max_entries: int = 10000):
        if log_dir is None:
            log_dir = os.path.expanduser("~/.castle_wyvern/audit")

        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.max_entries = max_entries
        self.entries: List[AuditEntry] = []
        self._lock = threading.Lock()

        # Load existing logs
        self._load_logs()

    def _get_log_file(self) -> str:
        """Get current log file path (rotated daily)."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"audit_{date_str}.jsonl")

    def _load_logs(self):
        """Load recent audit logs."""
        log_file = self._get_log_file()
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.entries.append(AuditEntry.from_dict(data))
            except Exception:
                pass

    def log(
        self,
        level: AuditLevel,
        category: str,
        action: str,
        user: str = "system",
        details: Dict = None,
        source_ip: str = "localhost",
        session_id: str = "",
    ):
        """Log an audit event."""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            category=category,
            action=action,
            user=user,
            details=details or {},
            source_ip=source_ip,
            session_id=session_id,
        )

        with self._lock:
            self.entries.append(entry)

            # Write to file
            log_file = self._get_log_file()
            with open(log_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

            # Trim if needed
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries :]

        # Print security events to console
        if level == AuditLevel.SECURITY:
            print(f"🔒 [SECURITY] {category}: {action} by {user}")

    def log_command(self, user: str, command: str, args: str = ""):
        """Log a user command."""
        self.log(
            AuditLevel.INFO,
            "command",
            command,
            user=user,
            details={"args": args[:100]},  # Truncate long args
        )

    def log_auth(self, user: str, action: str, success: bool, details: Dict = None):
        """Log an authentication event."""
        self.log(
            AuditLevel.SECURITY if not success else AuditLevel.INFO,
            "auth",
            action,
            user=user,
            details={"success": success, **(details or {})},
        )

    def log_data_access(self, user: str, data_type: str, action: str, data_id: str = None):
        """Log data access."""
        self.log(
            AuditLevel.INFO,
            "data_access",
            action,
            user=user,
            details={"data_type": data_type, "data_id": data_id},
        )

    def log_config_change(self, user: str, config_key: str, old_value: Any, new_value: Any):
        """Log configuration changes."""
        self.log(
            AuditLevel.WARNING,
            "config",
            "change",
            user=user,
            details={"key": config_key, "old": str(old_value)[:50], "new": str(new_value)[:50]},
        )

    def log_security_event(self, event_type: str, details: Dict, severity: str = "warning"):
        """Log a security-specific event."""
        level = AuditLevel.CRITICAL if severity == "critical" else AuditLevel.SECURITY
        self.log(level, "security", event_type, details=details)

    def search(self, **filters) -> List[AuditEntry]:
        """Search audit logs."""
        results = self.entries

        if "level" in filters:
            results = [e for e in results if e.level == filters["level"]]
        if "category" in filters:
            results = [e for e in results if e.category == filters["category"]]
        if "user" in filters:
            results = [e for e in results if e.user == filters["user"]]
        if "since" in filters:
            since = filters["since"]
            results = [e for e in results if datetime.fromisoformat(e.timestamp) >= since]

        return results

    def get_stats(self) -> Dict:
        """Get audit log statistics."""
        from collections import Counter

        if not self.entries:
            return {"total": 0}

        return {
            "total": len(self.entries),
            "by_level": dict(Counter(e.level for e in self.entries)),
            "by_category": dict(Counter(e.category for e in self.entries)),
            "by_user": dict(Counter(e.user for e in self.entries)),
            "time_range": {
                "first": self.entries[0].timestamp if self.entries else None,
                "last": self.entries[-1].timestamp if self.entries else None,
            },
        }

    def export(self, output_file: str, since: datetime = None) -> bool:
        """Export audit logs to a file."""
        try:
            entries = self.entries
            if since:
                entries = [e for e in entries if datetime.fromisoformat(e.timestamp) >= since]

            with open(output_file, "w") as f:
                json.dump([e.to_dict() for e in entries], f, indent=2)

            return True
        except Exception as e:
            print(f"[Audit] Export error: {e}")
            return False


class EncryptionManager:
    """
    Simple encryption for sensitive data at rest.

    Note: This is a basic implementation. For production use,
    consider using a proper key management system.
    """

    def __init__(self, key: bytes = None):
        self.key = key or self._generate_key()

    def _generate_key(self) -> bytes:
        """Generate a new encryption key."""
        key_file = os.path.expanduser("~/.castle_wyvern/.key")

        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = secrets.token_bytes(32)
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Secure permissions
            return key

    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        # Simple XOR with key (for demonstration - use proper crypto in production)
        data_bytes = data.encode("utf-8")
        encrypted = bytes(
            a ^ b for a, b in zip(data_bytes, self.key * (len(data_bytes) // len(self.key) + 1))
        )
        return encrypted.hex()

    def decrypt(self, encrypted_hex: str) -> str:
        """Decrypt hex-encoded data."""
        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = bytes(
            a ^ b for a, b in zip(encrypted, self.key * (len(encrypted) // len(self.key) + 1))
        )
        return decrypted.decode("utf-8")

    def hash_password(self, password: str, salt: str = None) -> str:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)

        pwdhash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000  # iterations
        )
        return f"{salt}${pwdhash.hex()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, _ = hashed.split("$")
            return self.hash_password(password, salt) == hashed
        except ValueError:
            return False


class APIKeyManager:
    """
    Manages API keys for external access.
    """

    def __init__(self, keys_file: str = None):
        if keys_file is None:
            keys_file = os.path.expanduser("~/.castle_wyvern/api_keys.json")

        self.keys_file = keys_file
        self.keys: Dict[str, Dict] = {}
        self._load_keys()

    def _load_keys(self):
        """Load API keys from file."""
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, "r") as f:
                    self.keys = json.load(f)
            except Exception:
                self.keys = {}

    def _save_keys(self):
        """Save API keys to file."""
        os.makedirs(os.path.dirname(self.keys_file), exist_ok=True)
        with open(self.keys_file, "w") as f:
            json.dump(self.keys, f, indent=2)
        os.chmod(self.keys_file, 0o600)

    def generate_key(self, name: str, permissions: List[str] = None) -> str:
        """Generate a new API key."""
        key = f"cw_{secrets.token_urlsafe(32)}"

        self.keys[key] = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "permissions": permissions or ["read"],
            "enabled": True,
        }

        self._save_keys()
        return key

    def revoke_key(self, key: str) -> bool:
        """Revoke an API key."""
        if key in self.keys:
            del self.keys[key]
            self._save_keys()
            return True
        return False

    def validate_key(self, key: str, required_permission: str = None) -> bool:
        """Validate an API key and optionally check permissions."""
        if key not in self.keys:
            return False

        key_data = self.keys[key]

        if not key_data.get("enabled", True):
            return False

        if required_permission:
            if required_permission not in key_data.get("permissions", []):
                return False

        # Update last used
        self.keys[key]["last_used"] = datetime.now().isoformat()
        self._save_keys()

        return True

    def get_key_info(self, key: str) -> Optional[Dict]:
        """Get information about an API key (without revealing the key)."""
        if key in self.keys:
            info = self.keys[key].copy()
            info["key_preview"] = key[:8] + "..."
            return info
        return None

    def list_keys(self) -> List[Dict]:
        """List all API keys."""
        return [
            {
                "name": data["name"],
                "created_at": data["created_at"],
                "last_used": data.get("last_used"),
                "permissions": data["permissions"],
                "enabled": data.get("enabled", True),
            }
            for key, data in self.keys.items()
        ]


class SecurityScanner:
    """
    Scans for security issues and misconfigurations.
    """

    def __init__(self):
        self.checks: List[Dict[str, Any]] = []
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default security checks."""
        self.checks = [
            {
                "name": "default_api_keys",
                "description": "Check for default or weak API keys",
                "check": self._check_default_keys,
            },
            {
                "name": "file_permissions",
                "description": "Check for insecure file permissions",
                "check": self._check_file_permissions,
            },
            {
                "name": "env_exposure",
                "description": "Check for exposed credentials in environment",
                "check": self._check_env_exposure,
            },
            {
                "name": "open_ports",
                "description": "Check for unexpectedly open ports",
                "check": self._check_open_ports,
            },
        ]

    def _check_default_keys(self) -> List[Dict]:
        """Check for default API keys."""
        issues = []

        # Check environment variables
        sensitive_vars = ["API_KEY", "SECRET", "PASSWORD", "TOKEN"]
        for var in sensitive_vars:
            value = os.getenv(var, "")
            if value and len(value) < 20:  # Likely default/test key
                issues.append(
                    {"severity": "warning", "message": f"Potentially weak {var} detected"}
                )

        return issues

    def _check_file_permissions(self) -> List[Dict]:
        """Check file permissions."""
        issues = []

        sensitive_files = [
            os.path.expanduser("~/.castle_wyvern/.key"),
            os.path.expanduser("~/.castle_wyvern/api_keys.json"),
        ]

        for filepath in sensitive_files:
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                # Check if readable by others
                if stat.st_mode & 0o044:
                    issues.append(
                        {"severity": "error", "message": f"{filepath} is readable by others"}
                    )

        return issues

    def _check_env_exposure(self) -> List[Dict]:
        """Check for credential exposure."""
        issues = []

        # Check if .env file exists and is committed
        env_file = ".env"
        if os.path.exists(env_file):
            issues.append(
                {"severity": "warning", "message": ".env file exists - ensure it's in .gitignore"}
            )

        return issues

    def _check_open_ports(self) -> List[Dict]:
        """Check for open ports."""
        issues = []

        # This is a simplified check - in production, use proper port scanning
        try:
            import socket

            common_ports = [22, 80, 443, 18790, 18791, 18792, 18793]

            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                if result == 0 and port not in [18790, 18791, 18792, 18793]:
                    issues.append({"severity": "info", "message": f"Port {port} is open"})
                sock.close()
        except Exception:
            pass

        return issues

    def run_scan(self) -> Dict[str, Any]:
        """Run all security checks."""
        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "checks_run": len(self.checks),
            "issues": [],
            "summary": {"info": 0, "warning": 0, "error": 0, "critical": 0},
        }

        for check in self.checks:
            try:
                issues = cast(List[Dict[str, Any]], check["check"]())
                for issue in issues:
                    issue["check"] = check["name"]
                    results["issues"].append(issue)
                    results["summary"][issue["severity"]] += 1
            except Exception as e:
                results["issues"].append(
                    {
                        "check": check["name"],
                        "severity": "error",
                        "message": f"Check failed: {str(e)}",
                    }
                )

        return results


class IntrusionDetector:
    """
    Simple intrusion detection based on audit patterns.
    """

    def __init__(self, audit_logger: AuditLogger):
        self.audit = audit_logger
        self.suspicious_patterns = [
            ("brute_force", lambda e: e.category == "auth" and not e.details.get("success", True)),
            (
                "unusual_access",
                lambda e: e.category == "data_access" and e.details.get("data_type") == "sensitive",
            ),
            (
                "config_tampering",
                lambda e: e.category == "config" and e.level in ["warning", "error"],
            ),
        ]
        self.thresholds = {
            "brute_force": 5,  # 5 failed attempts
            "unusual_access": 3,
            "config_tampering": 2,
        }
        self.detections: List[Dict] = []

    def analyze(self, window_minutes: int = 60) -> List[Dict]:
        """Analyze recent audit logs for suspicious activity."""
        since = datetime.now() - timedelta(minutes=window_minutes)
        recent_entries = self.audit.search(since=since)

        detections = []

        for pattern_name, pattern_fn in self.suspicious_patterns:
            matching = [e for e in recent_entries if pattern_fn(e)]

            if len(matching) >= self.thresholds.get(pattern_name, 5):
                detections.append(
                    {
                        "pattern": pattern_name,
                        "severity": "warning" if pattern_name == "brute_force" else "info",
                        "count": len(matching),
                        "threshold": self.thresholds.get(pattern_name, 5),
                        "first_seen": matching[0].timestamp if matching else None,
                        "last_seen": matching[-1].timestamp if matching else None,
                    }
                )

        self.detections.extend(detections)
        return detections


class SecurityManager:
    """
    Central security manager for Castle Wyvern.

    Coordinates audit logging, encryption, API keys, scanning, and intrusion detection.
    """

    def __init__(self):
        # Components
        self.audit = AuditLogger()
        self.encryption = EncryptionManager()
        self.api_keys = APIKeyManager()
        self.scanner = SecurityScanner()
        self.intrusion_detector = IntrusionDetector(self.audit)

        # Security configuration
        self.config = {
            "audit_enabled": True,
            "encryption_enabled": True,
            "intrusion_detection_enabled": True,
            "max_failed_logins": 5,
            "session_timeout_minutes": 60,
        }

    def log_command(self, user: str, command: str, args: str = ""):
        """Log a command execution."""
        if self.config["audit_enabled"]:
            self.audit.log_command(user, command, args)

    def log_auth(self, user: str, action: str, success: bool, **details):
        """Log an authentication event."""
        if self.config["audit_enabled"]:
            self.audit.log_auth(user, action, success, details)

    def encrypt_sensitive(self, data: str) -> str:
        """Encrypt sensitive data."""
        if self.config["encryption_enabled"]:
            return str(self.encryption.encrypt(data))
        return data

    def decrypt_sensitive(self, encrypted: str) -> str:
        """Decrypt sensitive data."""
        if self.config["encryption_enabled"]:
            return str(self.encryption.decrypt(encrypted))
        return encrypted

    def validate_api_key(self, key: str, permission: str = None) -> bool:
        """Validate an API key."""
        valid = self.api_keys.validate_key(key, permission)

        # Log the attempt
        self.log_auth("api", "api_key_validation", valid, permission=permission)

        return bool(valid)

    def run_security_scan(self) -> Dict[str, Any]:
        """Run a security scan."""
        results = cast(Dict[str, Any], self.scanner.run_scan())

        # Log scan completion
        self.audit.log(
            AuditLevel.INFO,
            "security",
            "scan_complete",
            details={"issues_found": len(results["issues"]), "summary": results["summary"]},
        )

        return results

    def check_intrusions(self) -> List[Dict[str, Any]]:
        """Check for intrusion attempts."""
        if not self.config["intrusion_detection_enabled"]:
            return []

        detections = self.intrusion_detector.analyze()

        # Log detections
        for detection in detections:
            self.audit.log_security_event(
                "intrusion_detected",
                detection,
                severity="warning" if detection["severity"] == "warning" else "info",
            )

        return cast(List[Dict[str, Any]], detections)

    def get_status(self) -> Dict[str, Any]:
        """Get security status."""
        return {
            "audit_enabled": self.config["audit_enabled"],
            "encryption_enabled": self.config["encryption_enabled"],
            "intrusion_detection": self.config["intrusion_detection_enabled"],
            "audit_entries": len(self.audit.entries),
            "api_keys": len(self.api_keys.keys),
            "recent_intrusions": len(
                [
                    d
                    for d in self.intrusion_detector.detections
                    if datetime.fromisoformat(d.get("timestamp", "1970-01-01"))
                    > datetime.now() - timedelta(hours=24)
                ]
            ),
        }


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Security Test")
    print("=" * 50)

    # Create security manager
    security = SecurityManager()

    # Test audit logging
    print("\n1. Testing audit logging...")
    security.log_command("test_user", "ask", "test question")
    security.log_auth("test_user", "login", True)
    print(f"   Audit entries: {len(security.audit.entries)}")

    # Test encryption (demo placeholder only; never use in production)
    print("\n2. Testing encryption...")
    demo_secret = "demo_placeholder_value_12345"
    encrypted = security.encrypt_sensitive(demo_secret)
    decrypted = security.decrypt_sensitive(encrypted)
    print(f"   Original: {demo_secret[:10]}...")
    print(f"   Encrypted: {encrypted[:20]}...")
    print(f"   Decryption matches: {decrypted == demo_secret}")

    # Test API keys
    print("\n3. Testing API keys...")
    key = security.api_keys.generate_key("test_key", ["read", "write"])
    print(f"   Generated key: {key[:20]}...")
    print(f"   Valid: {security.validate_api_key(key)}")
    print(f"   Valid with permission: {security.validate_api_key(key, 'read')}")

    # Test security scan
    print("\n4. Running security scan...")
    results = security.run_security_scan()
    print(f"   Issues found: {len(results['issues'])}")
    for issue in results["issues"][:3]:
        print(f"   - [{issue['severity']}] {issue['message']}")

    print("\n✅ Security system ready!")
