"""
Castle Wyvern Auto-Discovery Service
Feature 11: Automatic node discovery via mDNS/Bonjour

Allows Stone nodes to find each other on the local network
without manual configuration.
"""

import socket
import threading
import time
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, ServiceInfo

    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False


@dataclass
class DiscoveredNode:
    """A node discovered on the network via mDNS."""

    name: str
    host: str
    port: int
    node_id: str
    capabilities: List[str]
    discovered_at: str
    last_seen: str

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "DiscoveredNode":
        return cls(**data)


class CastleWyvernListener:
    """
    mDNS listener for Castle Wyvern node discovery.

    Listens for other Castle Wyvern instances on the local network
    and maintains a registry of discovered nodes.
    """

    SERVICE_TYPE = "_castlewyvern._tcp.local."

    def __init__(
        self,
        on_node_discovered: Optional[Callable] = None,
        on_node_removed: Optional[Callable] = None,
    ):
        self.zeroconf: Optional[Any] = None
        self.browser: Optional[Any] = None
        self.discovered_nodes: Dict[str, DiscoveredNode] = {}
        self.on_node_discovered = on_node_discovered
        self.on_node_removed = on_node_removed
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> bool:
        """Start the discovery listener."""
        if not ZEROCONF_AVAILABLE:
            print("[Auto-Discovery] zeroconf not installed. Run: pip install zeroconf")
            return False

        try:
            self.zeroconf = Zeroconf()
            self.browser = ServiceBrowser(
                self.zeroconf, self.SERVICE_TYPE, handlers=[self._on_service_state_change]
            )
            self._running = True
            print(f"[Auto-Discovery] Listening for nodes on {self.SERVICE_TYPE}")
            return True
        except Exception as e:
            print(f"[Auto-Discovery] Failed to start: {e}")
            return False

    def stop(self):
        """Stop the discovery listener."""
        self._running = False
        if self.browser:
            self.browser.cancel()
        if self.zeroconf:
            self.zeroconf.close()
        print("[Auto-Discovery] Stopped")

    def _on_service_state_change(
        self, zeroconf: Any, service_type: str, name: str, state_change: Any
    ):
        """Handle service state changes."""
        if state_change is ServiceStateChange.Added:
            self._add_service(zeroconf, service_type, name)
        elif state_change is ServiceStateChange.Removed:
            self._remove_service(name)

    def _add_service(self, zeroconf: Any, service_type: str, name: str):
        """Process a newly discovered service."""
        try:
            info = zeroconf.get_service_info(service_type, name)
            if not info:
                return

            # Extract node details
            node_id = name.replace(f".{service_type}", "")
            host = socket.inet_ntoa(info.addresses[0]) if info.addresses else "unknown"
            port = info.port

            # Parse capabilities from TXT records
            capabilities = []
            if info.properties:
                caps = info.properties.get(b"capabilities", b"")
                if caps:
                    capabilities = caps.decode("utf-8").split(",")

            node = DiscoveredNode(
                name=info.name or node_id,
                host=host,
                port=port,
                node_id=node_id,
                capabilities=capabilities,
                discovered_at=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
            )

            with self._lock:
                self.discovered_nodes[node_id] = node

            print(f"[Auto-Discovery] 🔍 Found node: {node.name} at {node.host}:{node.port}")

            if self.on_node_discovered:
                self.on_node_discovered(node)

        except Exception as e:
            print(f"[Auto-Discovery] Error processing service: {e}")

    def _remove_service(self, name: str):
        """Handle a service going offline."""
        node_id = name.replace(f".{self.SERVICE_TYPE}", "")

        with self._lock:
            if node_id in self.discovered_nodes:
                node = self.discovered_nodes.pop(node_id)
                print(f"[Auto-Discovery] 👋 Node offline: {node.name}")

                if self.on_node_removed:
                    self.on_node_removed(node)

    def get_nodes(self) -> List[DiscoveredNode]:
        """Get list of all discovered nodes."""
        with self._lock:
            return list(self.discovered_nodes.values())

    def get_node(self, node_id: str) -> Optional[DiscoveredNode]:
        """Get a specific node by ID."""
        with self._lock:
            return self.discovered_nodes.get(node_id)


class AutoDiscoveryService:
    """
    Full auto-discovery service that both advertises this node
    and discovers other nodes on the network.
    """

    SERVICE_TYPE = "_castlewyvern._tcp.local."

    def __init__(
        self, node_name: str, node_id: str, port: int = 18790, capabilities: List[str] = None
    ):
        self.node_name = node_name
        self.node_id = node_id
        self.port = port
        self.capabilities = capabilities or ["cpu"]
        self.zeroconf: Optional[Any] = None
        self.service_info: Optional[Any] = None
        self.listener = CastleWyvernListener()
        self._registered = False

    def start(self) -> bool:
        """Start advertising and discovery."""
        if not ZEROCONF_AVAILABLE:
            print("[Auto-Discovery] ⚠️  zeroconf not installed")
            print("[Auto-Discovery]    Run: pip install zeroconf")
            return False

        try:
            # Start listener first
            if not self.listener.start():
                return False

            # Register this node
            self.zeroconf = Zeroconf()

            # Create service info
            service_name = f"{self.node_id}.{self.SERVICE_TYPE}"
            properties = {
                b"capabilities": ",".join(self.capabilities).encode("utf-8"),
                b"version": b"0.2.0",
                b"name": self.node_name.encode("utf-8"),
            }

            self.service_info = ServiceInfo(
                type_=self.SERVICE_TYPE,
                name=service_name,
                addresses=[socket.inet_aton(self._get_ip())],
                port=self.port,
                properties=properties,
                server=f"{self.node_id}.local.",
            )

            self.zeroconf.register_service(self.service_info)
            self._registered = True

            print(f"[Auto-Discovery] 📡 Advertising as {self.node_name} on port {self.port}")
            print(f"[Auto-Discovery] ✓ Service registered: {service_name}")
            return True

        except Exception as e:
            print(f"[Auto-Discovery] Failed to start: {e}")
            return False

    def stop(self):
        """Stop advertising and discovery."""
        if self._registered and self.zeroconf and self.service_info:
            self.zeroconf.unregister_service(self.service_info)
            self._registered = False
            print("[Auto-Discovery] Unregistered from network")

        if self.zeroconf:
            self.zeroconf.close()

        self.listener.stop()

    def _get_ip(self) -> str:
        """Get the local IP address."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_discovered_nodes(self) -> List[DiscoveredNode]:
        """Get all discovered nodes."""
        return self.listener.get_nodes()

    def status(self) -> Dict:
        """Get auto-discovery status."""
        return {
            "running": self._registered,
            "advertising": self._registered,
            "service_name": f"{self.node_id}.{self.SERVICE_TYPE}" if self._registered else None,
            "discovered_nodes": len(self.listener.discovered_nodes),
            "capabilities": self.capabilities,
            "zeroconf_available": ZEROCONF_AVAILABLE,
        }


# Standalone usage
if __name__ == "__main__":
    import signal

    print("🏰 Castle Wyvern Auto-Discovery Test")
    print("=" * 50)

    if not ZEROCONF_AVAILABLE:
        print("\n⚠️  Please install zeroconf: pip install zeroconf")
        exit(1)

    # Create service
    service = AutoDiscoveryService(
        node_name="Test Node",
        node_id="test-node-001",
        port=18790,
        capabilities=["cpu", "gpu", "ollama"],
    )

    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\n\nShutting down...")
        service.stop()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start
    if service.start():
        print("\n🔍 Discovering nodes... (Ctrl+C to stop)")
        print("-" * 50)

        while True:
            time.sleep(5)
            nodes = service.get_discovered_nodes()
            if nodes:
                print(f"\n📋 Discovered {len(nodes)} node(s):")
                for node in nodes:
                    print(f"  • {node.name} ({node.host}:{node.port})")
                    print(f"    Capabilities: {', '.join(node.capabilities)}")
            else:
                print("  (no other nodes found yet...)")
