"""
Enhanced Visual Automation
Polish features for OmniParser integration
"""

import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import tempfile


@dataclass
class AutomationSession:
    """Record of a visual automation session."""

    id: str
    start_time: float
    end_time: Optional[float] = None
    actions: List[Dict] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0


class SessionRecorder:
    """Record and replay visual automation sessions."""

    def __init__(self, storage_dir: str = "~/.castle_wyvern/automation_sessions"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[AutomationSession] = None

    def start_session(self) -> AutomationSession:
        """Start recording a new session."""
        session_id = f"session_{int(time.time())}"
        self.current_session = AutomationSession(id=session_id, start_time=time.time())
        return self.current_session

    def record_action(self, action_type: str, target: str, result: Dict):
        """Record an action in the current session."""
        if self.current_session:
            self.current_session.actions.append(
                {"timestamp": time.time(), "type": action_type, "target": target, "result": result}
            )

            if result.get("success"):
                self.current_session.success_count += 1
            else:
                self.current_session.failure_count += 1

    def record_screenshot(self, screenshot_path: str):
        """Record a screenshot reference."""
        if self.current_session:
            self.current_session.screenshots.append(screenshot_path)

    def end_session(self) -> AutomationSession:
        """End the current session and save it."""
        if self.current_session:
            self.current_session.end_time = time.time()

            # Save to file
            session_file = self.storage_dir / f"{self.current_session.id}.json"
            with open(session_file, "w") as f:
                json.dump(
                    {
                        "id": self.current_session.id,
                        "start_time": self.current_session.start_time,
                        "end_time": self.current_session.end_time,
                        "duration": self.current_session.end_time - self.current_session.start_time,
                        "actions": self.current_session.actions,
                        "screenshots": self.current_session.screenshots,
                        "success_count": self.current_session.success_count,
                        "failure_count": self.current_session.failure_count,
                    },
                    f,
                    indent=2,
                )

            session = self.current_session
            self.current_session = None
            return session

        return None

    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load a recorded session."""
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, "r") as f:
                return json.load(f)
        return None

    def list_sessions(self) -> List[Dict]:
        """List all recorded sessions."""
        sessions = []
        for session_file in self.storage_dir.glob("session_*.json"):
            with open(session_file, "r") as f:
                data = json.load(f)
                sessions.append(
                    {
                        "id": data["id"],
                        "start_time": data["start_time"],
                        "duration": data.get("duration", 0),
                        "actions": len(data["actions"]),
                        "success_rate": (
                            data["success_count"] / (data["success_count"] + data["failure_count"])
                            if (data["success_count"] + data["failure_count"]) > 0
                            else 0
                        ),
                    }
                )
        return sorted(sessions, key=lambda x: x["start_time"], reverse=True)

    def replay_session(self, session_id: str, visual_automation) -> Dict:
        """
        Replay a recorded session.

        Args:
            session_id: ID of session to replay
            visual_automation: VisualAutomation instance to use

        Returns:
            Replay results
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return {"success": False, "error": "Session not found"}

        results = {
            "success": True,
            "actions_replayed": 0,
            "actions_succeeded": 0,
            "actions_failed": 0,
            "details": [],
        }

        for action in session_data["actions"]:
            action_type = action["type"]
            target = action["target"]

            if action_type == "click":
                result = visual_automation.click(target)
            elif action_type == "type":
                result = visual_automation.type_text(target, "")
            else:
                continue

            results["actions_replayed"] += 1
            if result["success"]:
                results["actions_succeeded"] += 1
            else:
                results["actions_failed"] += 1

            results["details"].append(
                {"type": action_type, "target": target, "success": result["success"]}
            )

        return results


class VisualMacro:
    """Macros for common visual automation patterns."""

    def __init__(self, visual_automation):
        self.va = visual_automation
        self.recorder = SessionRecorder()

    def login_sequence(
        self,
        username: str,
        password: str,
        username_field: str = "username",
        password_field: str = "password",
        submit_button: str = "submit",
    ) -> Dict:
        """
        Complete login sequence.

        Args:
            username: Username to enter
            password: Password to enter
            username_field: Description of username field
            password_field: Description of password field
            submit_button: Description of submit button

        Returns:
            Results of each step
        """
        self.recorder.start_session()

        results = {"steps": [], "success": True}

        # Step 1: Click username field
        result = self.va.click(username_field)
        self.recorder.record_action("click", username_field, result)
        results["steps"].append({"step": 1, "action": "click_username", "result": result})
        if not result["success"]:
            results["success"] = False
            self.recorder.end_session()
            return results

        # Step 2: Type username
        result = self.va.type_text(username, username_field)
        self.recorder.record_action("type", username, result)
        results["steps"].append({"step": 2, "action": "type_username", "result": result})

        # Step 3: Click password field
        result = self.va.click(password_field)
        self.recorder.record_action("click", password_field, result)
        results["steps"].append({"step": 3, "action": "click_password", "result": result})
        if not result["success"]:
            results["success"] = False
            self.recorder.end_session()
            return results

        # Step 4: Type password
        result = self.va.type_text(password, password_field)
        self.recorder.record_action("type", password, result)
        results["steps"].append({"step": 4, "action": "type_password", "result": result})

        # Step 5: Click submit
        result = self.va.click(submit_button)
        self.recorder.record_action("click", submit_button, result)
        results["steps"].append({"step": 5, "action": "click_submit", "result": result})
        if not result["success"]:
            results["success"] = False

        self.recorder.end_session()
        return results

    def form_fill_sequence(
        self, field_values: Dict[str, str], submit_button: str = "submit"
    ) -> Dict:
        """
        Fill out a form with multiple fields.

        Args:
            field_values: Dict of {field_description: value_to_type}
            submit_button: Description of submit button

        Returns:
            Results of each step
        """
        self.recorder.start_session()

        results = {"steps": [], "success": True}

        step = 1
        for field_desc, value in field_values.items():
            # Click field
            result = self.va.click(field_desc)
            self.recorder.record_action("click", field_desc, result)
            results["steps"].append(
                {"step": step, "action": f"click_{field_desc}", "result": result}
            )
            step += 1

            if not result["success"]:
                results["success"] = False
                continue

            # Type value
            result = self.va.type_text(value, field_desc)
            self.recorder.record_action("type", value, result)
            results["steps"].append(
                {"step": step, "action": f"type_{field_desc}", "result": result}
            )
            step += 1

        # Submit form
        result = self.va.click(submit_button)
        self.recorder.record_action("click", submit_button, result)
        results["steps"].append({"step": step, "action": "click_submit", "result": result})
        if not result["success"]:
            results["success"] = False

        self.recorder.end_session()
        return results


class ElementHighlighter:
    """Highlight detected elements on screenshots."""

    @staticmethod
    def highlight_elements(screenshot_path: str, elements: List, output_path: str = None) -> str:
        """
        Draw bounding boxes around detected elements on screenshot.

        Args:
            screenshot_path: Path to original screenshot
            elements: List of UIElement objects
            output_path: Where to save highlighted image (if None, creates temp)

        Returns:
            Path to highlighted image
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Open screenshot
            img = Image.open(screenshot_path)
            draw = ImageDraw.Draw(img)

            # Draw boxes for each element
            for elem in elements:
                x, y, w, h = elem.bbox

                # Color based on element type
                color = {"button": "red", "input": "blue", "link": "green", "text": "gray"}.get(
                    elem.type, "yellow"
                )

                # Draw rectangle
                draw.rectangle([x, y, x + w, y + h], outline=color, width=2)

                # Draw label
                label = f"{elem.type}: {elem.text[:20]}"
                draw.text((x, y - 15), label, fill=color)

            # Save
            if output_path is None:
                output_path = tempfile.mktemp(suffix="_highlighted.png")

            img.save(output_path)
            return output_path

        except ImportError:
            return "Error: PIL not installed. Run: pip install Pillow"
        except Exception as e:
            return f"Error: {str(e)}"


class VisualDebugger:
    """Debug visual automation issues."""

    def __init__(self, visual_automation):
        self.va = visual_automation
        self.debug_log: List[Dict] = []

    def debug_click(self, target: str) -> Dict:
        """
        Debug a click action with detailed logging.

        Returns:
            Debug information
        """
        # Analyze screen first
        screen = self.va.analyze_screen()

        debug_info = {
            "target": target,
            "screen_analyzed": True,
            "total_elements": len(screen.elements),
            "interactive_elements": len(screen.get_interactive_elements()),
            "matching_elements": [],
            "suggestions": [],
        }

        # Find matching elements
        target_lower = target.lower()
        for elem in screen.elements:
            if target_lower in elem.text.lower() or target_lower in elem.type.lower():
                debug_info["matching_elements"].append(
                    {
                        "type": elem.type,
                        "text": elem.text,
                        "bbox": elem.bbox,
                        "center": elem.center,
                        "confidence": elem.confidence,
                    }
                )

        # Generate suggestions if no exact match
        if not debug_info["matching_elements"]:
            # Find similar elements
            for elem in screen.get_interactive_elements():
                debug_info["suggestions"].append(
                    {
                        "type": elem.type,
                        "text": elem.text,
                        "why": f"Interactive {elem.type} element",
                    }
                )

        self.debug_log.append(debug_info)
        return debug_info

    def get_debug_report(self) -> str:
        """Generate a debug report."""
        report = ["Visual Automation Debug Report", "=" * 50]

        for i, entry in enumerate(self.debug_log, 1):
            report.append(f"\nDebug #{i}:")
            report.append(f"  Target: {entry['target']}")
            report.append(f"  Elements found: {entry['total_elements']}")
            report.append(f"  Matching elements: {len(entry['matching_elements'])}")

            if entry["matching_elements"]:
                report.append("  Matches:")
                for match in entry["matching_elements"]:
                    report.append(f"    - {match['type']}: '{match['text']}' at {match['center']}")

            if entry["suggestions"]:
                report.append("  Suggestions:")
                for sugg in entry["suggestions"][:3]:
                    report.append(f"    - Try: '{sugg['text']}' ({sugg['type']})")

        return "\n".join(report)


__all__ = [
    "SessionRecorder",
    "VisualMacro",
    "ElementHighlighter",
    "VisualDebugger",
    "AutomationSession",
]
