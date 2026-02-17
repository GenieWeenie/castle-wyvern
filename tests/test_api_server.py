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

    def test_kg_status_returns_200_and_stats(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.get("/kg/status")
        assert r.status_code == 200
        data = r.get_json()
        assert "knowledge_graph" in data
        kg = data["knowledge_graph"]
        assert "total_entities" in kg or "entity_types" in kg

    def test_kg_reason_400_when_query_missing(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.post("/kg/reason", json={}, content_type="application/json")
        assert r.status_code == 400
        data = r.get_json()
        assert "error" in data
        assert data.get("code") == "missing_field"

    def test_kg_reason_200_with_query(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.post(
            "/kg/reason",
            json={"query": "What facts do we have?"},
            content_type="application/json",
        )
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, dict)

    def test_coord_status_returns_200_and_stats(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.get("/coord/status")
        assert r.status_code == 200
        data = r.get_json()
        assert "coordination" in data
        coord = data["coordination"]
        assert "registered_agents" in coord

    def test_coord_team_400_when_task_missing(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.post("/coord/team", json={"requirements": ["coding"]}, content_type="application/json")
        assert r.status_code == 400
        data = r.get_json()
        assert "error" in data
        assert data.get("code") == "missing_field"

    def test_coord_team_200_with_task(self):
        api = CastleWyvernAPI()
        client = api.app.test_client()
        r = client.post(
            "/coord/team",
            json={"task": "Implement a small API", "requirements": ["coding", "documentation"]},
            content_type="application/json",
        )
        assert r.status_code == 200
        data = r.get_json()
        assert "team" in data
        assert data["task"] == "Implement a small API"
        assert "requirements" in data
        assert isinstance(data["team"], list)
