"""
Castle Wyvern Integration APIs
Feature 17: External integrations and connectors

Provides:
- Slack/Discord webhook notifications
- Email notifications (SMTP)
- Calendar integration (ICS/Google Calendar)
- Third-party API connectors
- Webhook server for incoming events
- Zapier/Make.com compatible endpoints
"""

import os
import sys
import json
import smtplib
import requests
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@dataclass
class WebhookConfig:
    """Configuration for a webhook endpoint."""
    name: str
    url: str
    headers: Dict[str, str]
    method: str = "POST"
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "WebhookConfig":
        return cls(**data)


@dataclass
class EmailConfig:
    """Configuration for email (SMTP)."""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    from_address: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "EmailConfig":
        return cls(**data)


class SlackIntegration:
    """
    Slack integration for Castle Wyvern.
    
    Features:
    - Send messages to Slack channels
    - Rich formatting with blocks
    - Alert notifications
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    
    def is_configured(self) -> bool:
        """Check if Slack is configured."""
        return bool(self.webhook_url)
    
    def send_message(self, text: str, channel: str = None, 
                     username: str = "Castle Wyvern", 
                     icon_emoji: str = ":castle:") -> bool:
        """Send a simple text message to Slack."""
        if not self.is_configured():
            return False
        
        payload = {
            "text": text,
            "username": username,
            "icon_emoji": icon_emoji
        }
        
        if channel:
            payload["channel"] = channel
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[Slack] Error sending message: {e}")
            return False
    
    def send_alert(self, title: str, message: str, 
                   severity: str = "info",
                   fields: List[Dict] = None) -> bool:
        """Send a rich alert notification."""
        if not self.is_configured():
            return False
        
        # Color based on severity
        colors = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "error": "#ff0000",
            "critical": "#990000"
        }
        
        attachment = {
            "color": colors.get(severity, "#36a64f"),
            "title": f"🏰 {title}",
            "text": message,
            "footer": "Castle Wyvern",
            "ts": int(datetime.now().timestamp())
        }
        
        if fields:
            attachment["fields"] = [
                {"title": f["name"], "value": f["value"], "short": f.get("short", True)}
                for f in fields
            ]
        
        payload = {
            "username": "Castle Wyvern",
            "icon_emoji": ":castle:",
            "attachments": [attachment]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[Slack] Error sending alert: {e}")
            return False
    
    def send_clan_message(self, member: str, message: str, 
                          emoji: str = "🦁") -> bool:
        """Send a message from a clan member."""
        text = f"{emoji} *{member}*: {message}"
        return self.send_message(text)


class DiscordIntegration:
    """
    Discord integration for Castle Wyvern.
    
    Features:
    - Send messages to Discord channels
    - Rich embeds
    - Alert notifications
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    
    def is_configured(self) -> bool:
        """Check if Discord is configured."""
        return bool(self.webhook_url)
    
    def send_message(self, content: str, username: str = "Castle Wyvern") -> bool:
        """Send a simple message to Discord."""
        if not self.is_configured():
            return False
        
        payload = {
            "content": content,
            "username": username
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"[Discord] Error sending message: {e}")
            return False
    
    def send_embed(self, title: str, description: str,
                   color: int = 0x3498db,
                   fields: List[Dict] = None,
                   footer: str = None) -> bool:
        """Send a rich embed message."""
        if not self.is_configured():
            return False
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now().isoformat()
        }
        
        if fields:
            embed["fields"] = [
                {"name": f["name"], "value": f["value"], "inline": f.get("inline", True)}
                for f in fields
            ]
        
        if footer:
            embed["footer"] = {"text": footer}
        
        payload = {
            "username": "Castle Wyvern",
            "embeds": [embed]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"[Discord] Error sending embed: {e}")
            return False
    
    def send_alert(self, title: str, message: str, 
                   severity: str = "info") -> bool:
        """Send an alert notification."""
        colors = {
            "info": 0x3498db,
            "warning": 0xf39c12,
            "error": 0xe74c3c,
            "critical": 0x990000
        }
        
        return self.send_embed(
            title=f"🚨 {title}",
            description=message,
            color=colors.get(severity, 0x3498db),
            footer="Castle Wyvern Alert System"
        )


class EmailIntegration:
    """
    Email (SMTP) integration for Castle Wyvern.
    
    Features:
    - Send email notifications
    - HTML and plain text support
    - Alert templates
    """
    
    def __init__(self, config: EmailConfig = None):
        self.config = config
        if not self.config:
            # Try to load from environment
            self.config = EmailConfig(
                smtp_server=os.getenv("SMTP_SERVER", ""),
                smtp_port=int(os.getenv("SMTP_PORT", "587")),
                username=os.getenv("SMTP_USERNAME", ""),
                password=os.getenv("SMTP_PASSWORD", ""),
                use_tls=True,
                from_address=os.getenv("SMTP_FROM", "castle-wyvern@localhost")
            )
    
    def is_configured(self) -> bool:
        """Check if email is configured."""
        return all([
            self.config.smtp_server,
            self.config.username,
            self.config.password
        ])
    
    def send_email(self, to_address: str, subject: str, 
                   body: str, html_body: str = None) -> bool:
        """Send an email."""
        if not self.is_configured():
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.config.from_address
            msg["To"] = to_address
            
            # Plain text part
            msg.attach(MIMEText(body, "plain"))
            
            # HTML part (if provided)
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            # Send
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"[Email] Error sending: {e}")
            return False
    
    def send_alert(self, to_address: str, title: str, 
                   message: str, severity: str = "info") -> bool:
        """Send an alert email."""
        subject = f"[Castle Wyvern] {severity.upper()}: {title}"
        
        body = f"""
Castle Wyvern Alert
==================

Title: {title}
Severity: {severity.upper()}
Time: {datetime.now().isoformat()}

Message:
{message}

---
This is an automated message from Castle Wyvern.
        """.strip()
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🏰 Castle Wyvern Alert</h2>
            <hr>
            <p><strong>Title:</strong> {title}</p>
            <p><strong>Severity:</strong> {severity.upper()}</p>
            <p><strong>Time:</strong> {datetime.now().isoformat()}</p>
            <hr>
            <p>{message}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated message from Castle Wyvern.
            </p>
        </body>
        </html>
        """
        
        return self.send_email(to_address, subject, body, html_body)


class CalendarIntegration:
    """
    Calendar integration for Castle Wyvern.
    
    Features:
    - Generate ICS files
    - Google Calendar integration
    - Event reminders
    """
    
    def __init__(self):
        self.events: List[Dict] = []
    
    def create_ics_event(self, title: str, start: datetime, 
                         end: datetime = None,
                         description: str = "",
                         location: str = "") -> str:
        """Create an ICS event string."""
        if end is None:
            end = start + timedelta(hours=1)
        
        uid = f"castle-wyvern-{datetime.now().timestamp()}@castle-wyvern"
        
        ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Castle Wyvern//EN
BEGIN:VEVENT
UID:{uid}
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT
END:VCALENDAR"""
        
        return ics
    
    def save_ics_event(self, filename: str, title: str, 
                       start: datetime, **kwargs) -> bool:
        """Save an ICS event to a file."""
        try:
            ics_content = self.create_ics_event(title, start, **kwargs)
            with open(filename, "w") as f:
                f.write(ics_content)
            return True
        except Exception as e:
            print(f"[Calendar] Error saving ICS: {e}")
            return False
    
    def get_google_calendar_link(self, title: str, start: datetime,
                                  end: datetime = None,
                                  description: str = "",
                                  location: str = "") -> str:
        """Generate a Google Calendar 'Add to Calendar' link."""
        if end is None:
            end = start + timedelta(hours=1)
        
        params = {
            "action": "TEMPLATE",
            "text": title,
            "dates": f"{start.strftime('%Y%m%dT%H%M%S')}/{end.strftime('%Y%m%dT%H%M%S')}",
            "details": description,
            "location": location
        }
        
        return f"https://calendar.google.com/calendar/render?{urlencode(params)}"


class WebhookServer:
    """
    Flask-based webhook server for incoming integrations.
    
    Endpoints:
    - POST /webhook/alerts - Receive alert webhooks
    - POST /webhook/commands - Receive command webhooks
    - POST /webhook/events - Receive generic events
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 18793):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask required for webhook server")
        
        self.host = host
        self.port = port
        self.app = Flask("CastleWyvernWebhooks")
        
        # Callbacks for webhook events
        self.alert_callbacks: List[Callable[[Dict], None]] = []
        self.command_callbacks: List[Callable[[Dict], None]] = []
        self.event_callbacks: List[Callable[[Dict], None]] = []
        
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes."""
        
        @self.app.route("/webhook/alerts", methods=["POST"])
        def webhook_alerts():
            """Receive alert webhooks."""
            data = request.get_json() or {}
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[Webhook] Alert callback error: {e}")
            
            return jsonify({"status": "received"}), 200
        
        @self.app.route("/webhook/commands", methods=["POST"])
        def webhook_commands():
            """Receive command webhooks."""
            data = request.get_json() or {}
            
            # Trigger callbacks
            for callback in self.command_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[Webhook] Command callback error: {e}")
            
            return jsonify({"status": "received"}), 200
        
        @self.app.route("/webhook/events", methods=["POST"])
        def webhook_events():
            """Receive generic event webhooks."""
            data = request.get_json() or {}
            
            # Trigger callbacks
            for callback in self.event_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[Webhook] Event callback error: {e}")
            
            return jsonify({"status": "received"}), 200
        
        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check."""
            return jsonify({"status": "ok"}), 200
    
    def register_alert_callback(self, callback: Callable[[Dict], None]):
        """Register a callback for alert webhooks."""
        self.alert_callbacks.append(callback)
    
    def register_command_callback(self, callback: Callable[[Dict], None]):
        """Register a callback for command webhooks."""
        self.command_callbacks.append(callback)
    
    def register_event_callback(self, callback: Callable[[Dict], None]):
        """Register a callback for event webhooks."""
        self.event_callbacks.append(callback)
    
    def run(self, debug: bool = False):
        """Start the webhook server."""
        print(f"🔗 Webhook Server starting on http://{self.host}:{self.port}")
        print(f"   Endpoints:")
        print(f"   - POST /webhook/alerts")
        print(f"   - POST /webhook/commands")
        print(f"   - POST /webhook/events")
        self.app.run(host=self.host, port=self.port, debug=debug)


class IntegrationManager:
    """
    Central manager for all Castle Wyvern integrations.
    
    Coordinates Slack, Discord, Email, Calendar, and Webhooks.
    """
    
    def __init__(self):
        # Initialize integrations
        self.slack = SlackIntegration()
        self.discord = DiscordIntegration()
        self.email = EmailIntegration()
        self.calendar = CalendarIntegration()
        self.webhook_server: Optional[WebhookServer] = None
        
        # Configuration storage
        self.config_file = os.path.expanduser("~/.castle_wyvern/integrations.json")
        self.config = self._load_config()
        
        # Apply saved config
        self._apply_config()
    
    def _load_config(self) -> Dict:
        """Load integration configuration."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_config(self):
        """Save integration configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def _apply_config(self):
        """Apply loaded configuration to integrations."""
        # Slack
        if "slack" in self.config:
            self.slack.webhook_url = self.config["slack"].get("webhook_url")
        
        # Discord
        if "discord" in self.config:
            self.discord.webhook_url = self.config["discord"].get("webhook_url")
        
        # Email
        if "email" in self.config:
            self.email.config = EmailConfig.from_dict(self.config["email"])
    
    def configure_slack(self, webhook_url: str):
        """Configure Slack integration."""
        self.slack.webhook_url = webhook_url
        self.config["slack"] = {"webhook_url": webhook_url}
        self.save_config()
    
    def configure_discord(self, webhook_url: str):
        """Configure Discord integration."""
        self.discord.webhook_url = webhook_url
        self.config["discord"] = {"webhook_url": webhook_url}
        self.save_config()
    
    def configure_email(self, **kwargs):
        """Configure email integration."""
        self.email.config = EmailConfig(**kwargs)
        self.config["email"] = self.email.config.to_dict()
        self.save_config()
    
    def send_alert(self, title: str, message: str, severity: str = "info") -> Dict[str, bool]:
        """Send an alert through all configured channels."""
        results = {}
        
        # Slack
        if self.slack.is_configured():
            results["slack"] = self.slack.send_alert(title, message, severity)
        
        # Discord
        if self.discord.is_configured():
            results["discord"] = self.discord.send_alert(title, message, severity)
        
        return results
    
    def start_webhook_server(self, host: str = "0.0.0.0", port: int = 18793) -> bool:
        """Start the webhook server."""
        if not FLASK_AVAILABLE:
            return False
        
        try:
            self.webhook_server = WebhookServer(host, port)
            
            # Start in background thread
            thread = threading.Thread(
                target=self.webhook_server.run,
                kwargs={"debug": False},
                daemon=True
            )
            thread.start()
            
            return True
        except Exception as e:
            print(f"[Integrations] Failed to start webhook server: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get integration status."""
        return {
            "slack": {
                "configured": self.slack.is_configured()
            },
            "discord": {
                "configured": self.discord.is_configured()
            },
            "email": {
                "configured": self.email.is_configured()
            },
            "webhook_server": {
                "running": self.webhook_server is not None
            }
        }


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Integration APIs Test")
    print("=" * 50)
    
    # Create integration manager
    integrations = IntegrationManager()
    
    # Show status
    status = integrations.get_status()
    print("\nIntegration Status:")
    for name, info in status.items():
        icon = "✅" if info.get("configured") or info.get("running") else "❌"
        print(f"  {icon} {name}")
    
    print("\n✅ Integration system ready!")
    print("\nTo configure integrations, set environment variables:")
    print("  - SLACK_WEBHOOK_URL")
    print("  - DISCORD_WEBHOOK_URL")
    print("  - SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD")
