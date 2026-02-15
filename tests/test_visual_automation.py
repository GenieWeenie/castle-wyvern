"""
Unit tests for Visual Automation functionality.
"""

import pytest
from unittest.mock import Mock, patch
from eyrie.omni_parser import VisualAutomation, UIElement, ScreenAnalysis


class TestVisualAutomation:
    """Test suite for Visual Automation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.va = VisualAutomation()
    
    def test_get_status(self):
        """Test getting automation status."""
        status = self.va.get_status()
        
        assert "omni_parser_version" in status
        assert "screen_capture_available" in status
        assert "element_detection_ready" in status
    
    def test_uielement_creation(self):
        """Test UI element data structure."""
        element = UIElement(
            type="button",
            bbox=(100, 200, 50, 30),
            text="Submit",
            confidence=0.95
        )
        
        assert element.type == "button"
        assert element.bbox == (100, 200, 50, 30)
        assert element.text == "Submit"
        assert element.confidence == 0.95
        assert element.center == (125, 215)
    
    def test_screen_analysis_empty(self):
        """Test screen analysis with no elements."""
        analysis = ScreenAnalysis(elements=[])
        
        assert len(analysis.elements) == 0
        assert len(analysis.get_interactive_elements()) == 0
    
    def test_screen_analysis_with_elements(self):
        """Test screen analysis with various elements."""
        elements = [
            UIElement("button", (0, 0, 10, 10), "Click me", 0.9),
            UIElement("text", (10, 10, 20, 20), "Some text", 0.8),
            UIElement("input", (30, 30, 15, 15), "", 0.85),
        ]
        
        analysis = ScreenAnalysis(elements=elements)
        
        assert len(analysis.elements) == 3
        # Should find interactive elements (button, input)
        interactive = analysis.get_interactive_elements()
        assert len(interactive) == 2


class TestVisualMacros:
    """Test visual automation macros."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from eyrie.visual_automation_utils import VisualMacro, SessionRecorder
        self.va = Mock(spec=VisualAutomation)
        self.macro = VisualMacro(self.va)
        self.recorder = SessionRecorder()
    
    def test_login_sequence_success(self):
        """Test successful login macro."""
        self.va.click.return_value = {"success": True}
        self.va.type_text.return_value = {"success": True}
        
        result = self.macro.login_sequence("user", "pass")
        
        assert result["success"] is True
        assert len(result["steps"]) == 5  # username field, username, password field, password, submit
    
    def test_login_sequence_failure(self):
        """Test login macro when click fails."""
        self.va.click.return_value = {"success": False, "error": "Element not found"}
        
        result = self.macro.login_sequence("user", "pass")
        
        assert result["success"] is False


class TestSessionRecorder:
    """Test session recording functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from eyrie.visual_automation_utils import SessionRecorder
        import tempfile
        self.recorder = SessionRecorder(storage_dir=tempfile.mkdtemp())
    
    def test_start_session(self):
        """Test starting a recording session."""
        session = self.recorder.start_session()
        
        assert session.id.startswith("session_")
        assert session.start_time is not None
        assert len(session.actions) == 0
    
    def test_record_action(self):
        """Test recording an action."""
        self.recorder.start_session()
        
        self.recorder.record_action("click", "button", {"success": True})
        
        assert len(self.recorder.current_session.actions) == 1
        assert self.recorder.current_session.success_count == 1
    
    def test_end_session(self):
        """Test ending and saving a session."""
        self.recorder.start_session()
        self.recorder.record_action("click", "button", {"success": True})
        
        session = self.recorder.end_session()
        
        assert session.end_time is not None
        assert session.duration == session.end_time - session.start_time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
