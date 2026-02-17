"""
Smoke tests for Castle Wyvern REST API (eyrie.api_server).
Requires Flask; skipped if Flask not installed.
"""

import os
import pytest

# Avoid loading env that might override test keys
os.environ.setdefault("AI_API_KEY", "test_key_for_ci")

try:
    from eyrie.api_server import CastleWyvernAPI, FLASK_AVAILABLE
except ImportError:
    FLASK_AVAILABLE = False


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not installed")
class TestCastleWyvernAPI:
    def test_health_returns_200_and_json(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.get("/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data.get("version") == "0.2.0"
        assert "services" in data
        assert "phoenix_gate" in data["services"]
        assert data["services"]["grimoorum"] == "active"

    def test_clan_list_returns_200_and_members(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.get("/clan")
        assert r.status_code == 200
        data = r.get_json()
        assert data["clan"] == "Manhattan Clan"
        assert "members" in data
        assert len(data["members"]) >= 9
        names = [m["name"] for m in data["members"]]
        assert "Goliath" in names
        assert "Lexington" in names
