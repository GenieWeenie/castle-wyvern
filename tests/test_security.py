"""
Tests for eyrie.security: AuditLogger, EncryptionManager, APIKeyManager, SecurityManager.
"""

import os
import tempfile
import pytest

from eyrie.security import (
    AuditLevel,
    AuditEntry,
    AuditLogger,
    EncryptionManager,
    APIKeyManager,
    SecurityManager,
)


class TestAuditEntry:
    def test_to_dict(self):
        entry = AuditEntry(
            timestamp="2025-01-01T00:00:00",
            level="info",
            category="command",
            action="ask",
            user="test_user",
            details={"args": "hello"},
        )
        d = entry.to_dict()
        assert d["timestamp"] == "2025-01-01T00:00:00"
        assert d["level"] == "info"
        assert d["category"] == "command"
        assert d["user"] == "test_user"
        assert d["details"]["args"] == "hello"

    def test_from_dict(self):
        d = {
            "timestamp": "2025-01-01T00:00:00",
            "level": "info",
            "category": "auth",
            "action": "login",
            "user": "u",
            "details": {},
        }
        entry = AuditEntry.from_dict(d)
        assert entry.timestamp == d["timestamp"]
        assert entry.category == "auth"


class TestAuditLogger:
    def test_log_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = AuditLogger(log_dir=tmp, max_entries=100)
            audit.log(AuditLevel.INFO, "command", "ask", user="alice", details={"q": "x"})
            audit.log(AuditLevel.SECURITY, "auth", "login", user="bob", details={"success": True})
            assert len(audit.entries) == 2
            by_user = audit.search(user="alice")
            assert len(by_user) == 1
            assert by_user[0].user == "alice"
            by_cat = audit.search(category="auth")
            assert len(by_cat) == 1
            assert by_cat[0].category == "auth"

    def test_log_command_and_auth(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = AuditLogger(log_dir=tmp)
            audit.log_command("user1", "code", "fibonacci")
            audit.log_auth("user1", "login", True)
            assert len(audit.entries) == 2
            assert audit.entries[0].category == "command"
            assert audit.entries[1].category == "auth"

    def test_get_stats_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = AuditLogger(log_dir=tmp)
            stats = audit.get_stats()
            assert stats["total"] == 0

    def test_get_stats_with_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = AuditLogger(log_dir=tmp)
            audit.log(AuditLevel.INFO, "command", "ask", user="alice")
            audit.log(AuditLevel.INFO, "command", "code", user="alice")
            stats = audit.get_stats()
            assert stats["total"] == 2
            assert stats["by_user"]["alice"] == 2


class TestEncryptionManager:
    def test_encrypt_decrypt_roundtrip(self):
        key = b"0" * 32
        em = EncryptionManager(key=key)
        plain = "sensitive_data_123"
        encrypted = em.encrypt(plain)
        assert encrypted != plain
        assert isinstance(encrypted, str)
        decrypted = em.decrypt(encrypted)
        assert decrypted == plain

    def test_hash_password_and_verify(self):
        key = b"0" * 32
        em = EncryptionManager(key=key)
        hashed = em.hash_password("mypassword")
        assert "$" in hashed
        assert em.verify_password("mypassword", hashed) is True
        assert em.verify_password("wrong", hashed) is False


class TestAPIKeyManager:
    def test_generate_and_validate_key(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            keys_file = f.name
        try:
            mgr = APIKeyManager(keys_file=keys_file)
            key = mgr.generate_key("test_key", ["read", "write"])
            assert key.startswith("cw_")
            assert mgr.validate_key(key) is True
            assert mgr.validate_key(key, "read") is True
            assert mgr.validate_key(key, "admin") is False
            assert mgr.validate_key("invalid_key") is False
        finally:
            os.unlink(keys_file)

    def test_revoke_key(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            keys_file = f.name
        try:
            mgr = APIKeyManager(keys_file=keys_file)
            key = mgr.generate_key("revoke_me", ["read"])
            assert mgr.revoke_key(key) is True
            assert mgr.validate_key(key) is False
            assert mgr.revoke_key("nonexistent") is False
        finally:
            if os.path.exists(keys_file):
                os.unlink(keys_file)


class TestSecurityManager:
    def test_encrypt_decrypt_sensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            key_file = os.path.join(tmp, ".key")
            os.makedirs(tmp, exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(b"x" * 32)
            # SecurityManager uses default paths; we need to test via public API
            # with encryption_enabled True (default)
            sec = SecurityManager()
            sec.config["encryption_enabled"] = True
            plain = "secret_value"
            enc = sec.encrypt_sensitive(plain)
            dec = sec.decrypt_sensitive(enc)
            assert dec == plain

    def test_validate_api_key_via_manager(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            keys_file = f.name
        try:
            sec = SecurityManager()
            with tempfile.TemporaryDirectory() as tmp:
                sec.audit.log_dir = tmp
                sec.api_keys = APIKeyManager(keys_file=keys_file)
                key = sec.api_keys.generate_key("sm_test", ["read"])
                assert sec.validate_api_key(key) is True
                assert sec.validate_api_key(key, "read") is True
                assert sec.validate_api_key("bad") is False
        finally:
            if os.path.exists(keys_file):
                os.unlink(keys_file)

    def test_run_security_scan_returns_structure(self):
        sec = SecurityManager()
        with tempfile.TemporaryDirectory() as tmp:
            sec.audit.log_dir = tmp
            result = sec.run_security_scan()
        assert "issues" in result
        assert "summary" in result
        assert isinstance(result["issues"], list)

    def test_get_status(self):
        sec = SecurityManager()
        status = sec.get_status()
        assert "audit_enabled" in status
        assert "encryption_enabled" in status
        assert "audit_entries" in status
        assert "api_keys" in status
