"""Tests for VisualAutomation and visual automation utilities."""

import pytest
from unittest.mock import MagicMock, patch
import tempfile
import time

from eyrie.omni_parser import VisualAutomation, UIElement, ParsedScreen
from eyrie.visual_automation_utils import VisualMacro, SessionRecorder, AutomationSession

# --- Fixtures ---


@pytest.fixture
def mock_visual_automation():
    """Create a VisualAutomation with mocked internals."""
    with patch("eyrie.omni_parser.OmniParserClient"):
        va = VisualAutomation()
        va.parser.available = True
        va.current_screen = None
        va.history = []
        return va


@pytest.fixture
def sample_elements():
    """Sample UIElements for testing."""
    return [
        UIElement(
            id="btn1",
            type="button",
            bbox=(10, 20, 100, 40),
            text="Submit",
            confidence=0.95,
            interactive=True,
        ),
        UIElement(
            id="inp1",
            type="input",
            bbox=(10, 60, 200, 30),
            text="username",
            confidence=0.90,
            interactive=True,
        ),
        UIElement(
            id="txt1",
            type="text",
            bbox=(10, 100, 150, 20),
            text="Welcome",
            confidence=0.85,
            interactive=False,
        ),
        UIElement(
            id="btn2",
            type="button",
            bbox=(10, 140, 100, 40),
            text="Cancel",
            confidence=0.88,
            interactive=True,
        ),
    ]


@pytest.fixture
def sample_screen(sample_elements):
    """A ParsedScreen with sample elements."""
    return ParsedScreen(elements=sample_elements, width=1920, height=1080, timestamp=time.time())


@pytest.fixture
def session_recorder(tmp_path):
    """SessionRecorder using a temporary directory."""
    return SessionRecorder(storage_dir=str(tmp_path / "sessions"))


# --- VisualAutomation.get_status() ---


class TestVisualAutomationStatus:

    def test_get_status_no_screen(self, mock_visual_automation):
        status = mock_visual_automation.get_status()
        assert isinstance(status, dict)
        assert status["available"] is True
        assert status["current_screen"] is False
        assert status["elements_on_screen"] == 0
        assert status["action_history"] == 0

    def test_get_status_with_screen(self, mock_visual_automation, sample_screen):
        mock_visual_automation.current_screen = sample_screen
        mock_visual_automation.history = [{"action": "click"}]

        status = mock_visual_automation.get_status()
        assert status["current_screen"] is True
        assert status["elements_on_screen"] == 4
        assert status["action_history"] == 1


# --- UIElement ---


class TestUIElement:

    def test_creation_and_properties(self):
        elem = UIElement(
            id="btn1",
            type="button",
            bbox=(10, 20, 100, 40),
            text="OK",
            confidence=0.95,
            interactive=True,
        )
        assert elem.type == "button"
        assert elem.bbox == (10, 20, 100, 40)
        assert elem.text == "OK"
        assert elem.confidence == 0.95
        assert elem.interactive is True

    def test_defaults(self):
        elem = UIElement(id="e1", type="text", bbox=(0, 0, 50, 50))
        assert elem.text == ""
        assert elem.confidence == 0.0
        assert elem.interactive is False

    def test_center_property(self):
        elem = UIElement(id="e1", type="button", bbox=(10, 20, 100, 40))
        assert elem.center == (60, 40)


# --- ParsedScreen.get_interactive_elements() ---


class TestScreenAnalysis:

    def test_get_interactive_elements(self, sample_screen):
        interactive = sample_screen.get_interactive_elements()
        assert len(interactive) == 3
        assert all(e.interactive for e in interactive)

    def test_get_interactive_elements_empty(self):
        screen = ParsedScreen(elements=[], width=1920, height=1080, timestamp=time.time())
        assert screen.get_interactive_elements() == []

    def test_no_interactive_elements(self):
        elements = [
            UIElement(id="t1", type="text", bbox=(0, 0, 10, 10), interactive=False),
            UIElement(id="t2", type="text", bbox=(20, 0, 10, 10), interactive=False),
        ]
        screen = ParsedScreen(elements=elements, width=800, height=600, timestamp=time.time())
        assert screen.get_interactive_elements() == []


# --- VisualMacro ---


class TestVisualMacro:

    def _make_macro(self, click_results, type_results, tmp_path):
        """Helper to build a VisualMacro with controlled mock responses."""
        va = MagicMock()
        va.click = MagicMock(side_effect=click_results)
        va.type_text = MagicMock(side_effect=type_results)

        macro = VisualMacro(va)
        macro.recorder = SessionRecorder(storage_dir=str(tmp_path / "macro_sessions"))
        return macro

    def test_login_sequence_success(self, tmp_path):
        success = {"success": True}
        macro = self._make_macro(
            click_results=[success, success, success],  # username field, password field, submit
            type_results=[success, success],  # type username, type password
            tmp_path=tmp_path,
        )

        result = macro.login_sequence("user1", "pass1")
        assert result["success"] is True
        assert len(result["steps"]) == 5

    def test_login_sequence_fail_username_click(self, tmp_path):
        fail = {"success": False, "error": "not found"}
        success = {"success": True}
        macro = self._make_macro(
            click_results=[fail],
            type_results=[],
            tmp_path=tmp_path,
        )

        result = macro.login_sequence("user1", "pass1")
        assert result["success"] is False
        assert len(result["steps"]) == 1
        assert result["steps"][0]["action"] == "click_username"

    def test_login_sequence_fail_submit(self, tmp_path):
        success = {"success": True}
        fail = {"success": False, "error": "submit not found"}
        macro = self._make_macro(
            click_results=[success, success, fail],  # username ok, password ok, submit fail
            type_results=[success, success],
            tmp_path=tmp_path,
        )

        result = macro.login_sequence("user1", "pass1")
        assert result["success"] is False
        assert len(result["steps"]) == 5

    def test_login_sequence_fail_password_click(self, tmp_path):
        success = {"success": True}
        fail = {"success": False, "error": "not found"}
        macro = self._make_macro(
            click_results=[success, fail],
            type_results=[success],
            tmp_path=tmp_path,
        )

        result = macro.login_sequence("user1", "pass1")
        assert result["success"] is False
        assert result["steps"][-1]["action"] == "click_password"


# --- SessionRecorder ---


class TestSessionRecorder:

    def test_start_session(self, session_recorder):
        session = session_recorder.start_session()
        assert isinstance(session, AutomationSession)
        assert session.id.startswith("session_")
        assert session.actions == []
        assert session_recorder.current_session is session

    def test_record_action_success(self, session_recorder):
        session_recorder.start_session()
        session_recorder.record_action("click", "button", {"success": True})

        assert len(session_recorder.current_session.actions) == 1
        assert session_recorder.current_session.success_count == 1
        assert session_recorder.current_session.failure_count == 0

    def test_record_action_failure(self, session_recorder):
        session_recorder.start_session()
        session_recorder.record_action("click", "button", {"success": False})

        assert session_recorder.current_session.failure_count == 1
        assert session_recorder.current_session.success_count == 0

    def test_record_action_without_session(self, session_recorder):
        # Should not raise
        session_recorder.record_action("click", "btn", {"success": True})

    def test_end_session(self, session_recorder):
        session_recorder.start_session()
        session_recorder.record_action("click", "btn", {"success": True})
        session = session_recorder.end_session()

        assert session.end_time is not None
        assert session.end_time >= session.start_time
        assert session_recorder.current_session is None

    def test_end_session_saves_file(self, session_recorder):
        session_recorder.start_session()
        session = session_recorder.end_session()

        session_file = session_recorder.storage_dir / f"{session.id}.json"
        assert session_file.exists()

    def test_end_session_without_start(self, session_recorder):
        result = session_recorder.end_session()
        assert result is None
