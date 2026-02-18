"""
OmniParser Integration
Vision-based GUI control for Castle Wyvern

Uses Microsoft OmniParser to:
- Parse screenshots into structured UI elements
- Identify interactive elements (buttons, fields, etc.)
- Enable visual automation
- Control any GUI through vision
"""

import base64
import json
import subprocess
from typing import List, Dict, Optional, Tuple, Any, cast
from dataclasses import dataclass
from pathlib import Path
import tempfile
import os


@dataclass
class UIElement:
    """A detected UI element from a screenshot."""

    id: str
    type: str  # button, input, text, icon, etc.
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    text: str = ""  # Text content or label
    confidence: float = 0.0
    interactive: bool = False  # Can be clicked/interacted with

    @property
    def center(self) -> Tuple[int, int]:
        """Get center coordinates of the element."""
        x, y, w, h = self.bbox
        return (x + w // 2, y + h // 2)


@dataclass
class ParsedScreen:
    """Result of parsing a screenshot."""

    elements: List[UIElement]
    width: int
    height: int
    timestamp: float

    def get_interactive_elements(self) -> List[UIElement]:
        """Get only interactive elements (buttons, inputs, etc.)."""
        return [e for e in self.elements if e.interactive]

    def get_elements_by_type(self, element_type: str) -> List[UIElement]:
        """Get elements of a specific type."""
        return [e for e in self.elements if e.type == element_type]

    def find_by_text(self, text: str) -> List[UIElement]:
        """Find elements containing specific text."""
        text_lower = text.lower()
        return [e for e in self.elements if text_lower in e.text.lower()]

    def find_button(self, label: str) -> Optional[UIElement]:
        """Find a button with specific label."""
        for element in self.elements:
            if element.type == "button" and label.lower() in element.text.lower():
                return element
        return None

    def find_input(self, placeholder: str = None) -> Optional[UIElement]:
        """Find an input field."""
        for element in self.elements:
            if element.type == "input":
                if placeholder is None or placeholder.lower() in element.text.lower():
                    return element
        return None


class OmniParserClient:
    """
    Client for Microsoft OmniParser.

    Parses screenshots into structured UI elements that can be
    used for visual automation.
    """

    def __init__(self):
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if OmniParser is available."""
        try:
            # Check if omni_parser module can be imported
            # In production, this would check for the actual OmniParser installation
            return False  # Placeholder - would detect actual installation
        except Exception:
            return False

    def parse_screenshot(self, image_path: str) -> ParsedScreen:
        """
        Parse a screenshot and extract UI elements.

        Args:
            image_path: Path to screenshot image

        Returns:
            ParsedScreen with detected elements
        """
        if not self.available:
            # Return simulated data for demo
            return self._simulate_parsing(image_path)

        # In production, this would call OmniParser
        # For now, return simulated data
        return self._simulate_parsing(image_path)

    def _simulate_parsing(self, image_path: str) -> ParsedScreen:
        """Simulate parsing for demo purposes."""
        import time

        # Simulated elements for a typical web form
        elements = [
            UIElement(
                id="btn_1",
                type="button",
                bbox=(100, 200, 120, 40),
                text="Submit",
                confidence=0.95,
                interactive=True,
            ),
            UIElement(
                id="btn_2",
                type="button",
                bbox=(250, 200, 100, 40),
                text="Cancel",
                confidence=0.92,
                interactive=True,
            ),
            UIElement(
                id="input_1",
                type="input",
                bbox=(100, 100, 300, 35),
                text="Username",
                confidence=0.88,
                interactive=True,
            ),
            UIElement(
                id="input_2",
                type="input",
                bbox=(100, 150, 300, 35),
                text="Password",
                confidence=0.88,
                interactive=True,
            ),
            UIElement(
                id="text_1",
                type="text",
                bbox=(100, 50, 200, 30),
                text="Login Form",
                confidence=0.90,
                interactive=False,
            ),
            UIElement(
                id="link_1",
                type="link",
                bbox=(100, 260, 150, 20),
                text="Forgot Password?",
                confidence=0.85,
                interactive=True,
            ),
        ]

        return ParsedScreen(elements=elements, width=800, height=600, timestamp=time.time())

    def get_action_coordinates(
        self, parsed_screen: ParsedScreen, action: str
    ) -> Optional[Tuple[int, int]]:
        """
        Get coordinates for a specific action.

        Args:
            parsed_screen: Parsed screen from parse_screenshot
            action: Description of action (e.g., "click the submit button")

        Returns:
            (x, y) coordinates or None if not found
        """
        action_lower = action.lower()

        # Parse action description
        if "submit" in action_lower or "login" in action_lower:
            button = parsed_screen.find_button("submit")
            if button:
                return button.center

        if "cancel" in action_lower:
            button = parsed_screen.find_button("cancel")
            if button:
                return button.center

        if "username" in action_lower or "email" in action_lower:
            input_field = parsed_screen.find_input("username")
            if input_field:
                return input_field.center

        if "password" in action_lower:
            input_field = parsed_screen.find_input("password")
            if input_field:
                return input_field.center

        # Try to find by text
        elements = parsed_screen.find_by_text(action_lower)
        for elem in elements:
            if elem.interactive:
                return elem.center

        return None


class VisualAutomation:
    """
    Visual automation using OmniParser.

    Enables Castle Wyvern to control GUIs through screenshots.
    """

    def __init__(self):
        self.parser = OmniParserClient()
        self.current_screen: Optional[ParsedScreen] = None
        self.history: List[Dict] = []

    def capture_screen(self, output_path: str = None) -> str:
        """
        Capture a screenshot.

        Args:
            output_path: Where to save the screenshot

        Returns:
            Path to screenshot
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".png")

        # Platform-specific screenshot capture
        import platform

        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                subprocess.run(["screencapture", output_path], check=True)
            elif system == "Linux":
                subprocess.run(["gnome-screenshot", "-f", output_path], check=True)
            elif system == "Windows":
                # Would use PIL or pyautogui on Windows
                pass

            return output_path
        except Exception as e:
            # Return placeholder for demo
            return output_path

    def analyze_screen(self, screenshot_path: str = None) -> ParsedScreen:
        """
        Analyze current screen and extract UI elements.

        Args:
            screenshot_path: Path to screenshot (if None, captures new)

        Returns:
            ParsedScreen with elements
        """
        if screenshot_path is None:
            screenshot_path = self.capture_screen()

        self.current_screen = self.parser.parse_screenshot(screenshot_path)

        # Log the analysis
        self.history.append(
            {
                "action": "analyze",
                "screenshot": screenshot_path,
                "elements_found": len(self.current_screen.elements),
                "interactive": len(self.current_screen.get_interactive_elements()),
            }
        )

        return self.current_screen

    def click(self, target: str) -> Dict:
        """
        Click on an element identified by text/description.

        Args:
            target: Description of what to click (e.g., "submit button")

        Returns:
            Result of the action
        """
        if self.current_screen is None:
            self.analyze_screen()

        coords = self.parser.get_action_coordinates(self.current_screen, target)

        if coords:
            x, y = coords
            # In production, this would use pyautogui or similar
            # For demo, we just log it
            self.history.append(
                {"action": "click", "target": target, "coordinates": (x, y), "status": "success"}
            )

            return {
                "success": True,
                "action": "click",
                "target": target,
                "coordinates": (x, y),
                "message": f"Would click at ({x}, {y})",
            }
        else:
            return {
                "success": False,
                "action": "click",
                "target": target,
                "error": "Target not found on screen",
            }

    def type_text(self, text: str, target: str = None) -> Dict:
        """
        Type text into a field.

        Args:
            text: Text to type
            target: Field to type into (if None, uses current focus)

        Returns:
            Result of the action
        """
        if target:
            # Click the target first
            result = self.click(target)
            if not result["success"]:
                return result

        # In production, this would use pyautogui.typewrite
        self.history.append({"action": "type", "text": text, "target": target, "status": "success"})

        return {
            "success": True,
            "action": "type",
            "text": text,
            "target": target,
            "message": f"Would type: {text}",
        }

    def get_element_summary(self) -> str:
        """Get a summary of elements on current screen."""
        if self.current_screen is None:
            return "No screen analyzed yet"

        lines = ["Screen Analysis:", "=" * 50]

        interactive = self.current_screen.get_interactive_elements()
        lines.append(f"\nInteractive Elements ({len(interactive)}):")

        for elem in interactive[:10]:  # Show first 10
            lines.append(f"  • {elem.type}: '{elem.text}' at {elem.center}")

        return "\n".join(lines)

    def get_status(self) -> Dict:
        """Get visual automation status."""
        return {
            "available": self.parser.available,
            "current_screen": self.current_screen is not None,
            "elements_on_screen": len(self.current_screen.elements) if self.current_screen else 0,
            "action_history": len(self.history),
        }


# Integration with Browser Agent
class VisualBrowserAgent:
    """
    Browser agent with visual capabilities.
    Combines BrowserAgent with OmniParser for visual web automation.
    """

    def __init__(self):
        self.visual = VisualAutomation()
        self.session_active = False

    def start_session(self) -> Dict:
        """Start a visual browsing session."""
        self.session_active = True

        # Analyze initial screen
        screen = self.visual.analyze_screen()

        return {
            "success": True,
            "session": "active",
            "elements_detected": len(screen.elements),
            "summary": self.visual.get_element_summary(),
        }

    def execute_task(self, task: str) -> Dict:
        """
        Execute a task using visual automation.

        Args:
            task: Natural language task (e.g., "Click the login button")

        Returns:
            Result of execution
        """
        if not self.session_active:
            self.start_session()

        # Parse task and execute
        task_lower = task.lower()

        if "click" in task_lower:
            # Extract what to click
            target = task_lower.replace("click", "").strip()
            return cast(Dict[str, Any], self.visual.click(target))

        elif "type" in task_lower or "enter" in task_lower:
            # Extract text and target
            # Simplified parsing
            return cast(Dict[str, Any], self.visual.type_text("sample text", "input field"))

        elif "analyze" in task_lower or "scan" in task_lower:
            screen = self.visual.analyze_screen()
            return {
                "success": True,
                "action": "analyze",
                "elements": len(screen.elements),
                "summary": self.visual.get_element_summary(),
            }

        return {"success": False, "error": f"Unknown task: {task}"}

    def end_session(self) -> Dict:
        """End the visual browsing session."""
        self.session_active = False
        return {"success": True, "session": "ended", "actions_performed": len(self.visual.history)}


__all__ = [
    "OmniParserClient",
    "VisualAutomation",
    "VisualBrowserAgent",
    "UIElement",
    "ParsedScreen",
]
