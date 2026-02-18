"""
Castle Wyvern Advanced Monitoring
Feature 15: Metrics, health checks, and alerting

Provides:
- System metrics collection (CPU, memory, disk)
- Phoenix Gate performance tracking
- Custom metrics and counters
- Health check system
- Alert rules and notifications
- Metrics export (Prometheus-compatible)
"""

import os
import sys
import json
import time
import threading
import psutil
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import statistics


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
        }


@dataclass
class Alert:
    """An alert triggered by a rule."""

    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: str
    resolved: bool = False
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    last_check: str
    response_time_ms: float

    def to_dict(self) -> Dict:
        return asdict(self)


class AlertRule:
    """
    A rule that triggers alerts based on metric conditions.

    Example:
        rule = AlertRule(
            name="high_cpu",
            metric_name="system.cpu.percent",
            condition=lambda x: x > 80,
            severity=AlertSeverity.WARNING,
            message="CPU usage is above 80%"
        )
    """

    def __init__(
        self,
        name: str,
        metric_name: str,
        condition: Callable[[float], bool],
        severity: AlertSeverity,
        message: str,
        cooldown_minutes: int = 5,
    ):
        self.name = name
        self.metric_name = metric_name
        self.condition = condition
        self.severity = severity
        self.message = message
        self.cooldown_minutes = cooldown_minutes
        self._last_triggered: Optional[datetime] = None

    def check(self, value: float) -> bool:
        """Check if the rule should trigger."""
        if not self.condition(value):
            return False

        # Check cooldown
        if self._last_triggered:
            elapsed = datetime.now() - self._last_triggered
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                return False

        self._last_triggered = datetime.now()
        return True

    def create_alert(self) -> Alert:
        """Create an alert from this rule."""
        return Alert(
            id=f"{self.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            rule_name=self.name,
            severity=self.severity,
            message=self.message,
            timestamp=datetime.now().isoformat(),
        )


class MetricsCollector:
    """
    Collects and stores metrics for Castle Wyvern.

    Features:
    - System metrics (CPU, memory, disk)
    - Phoenix Gate metrics (requests, latency, errors)
    - Custom metrics
    - Time-series storage
    """

    def __init__(self, max_history: int = 10000):
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.max_history = max_history
        self._lock = threading.Lock()

    def record(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value."""
        metric = Metric(
            name=name, value=value, timestamp=datetime.now().isoformat(), labels=labels or {}
        )

        with self._lock:
            self.metrics.append(metric)
            # Trim old metrics
            if len(self.metrics) > self.max_history:
                self.metrics = self.metrics[-self.max_history :]

    def increment_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        with self._lock:
            self.counters[key] = self.counters.get(key, 0) + value
        self.record(name, self.counters[key], labels)

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value."""
        key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        with self._lock:
            self.gauges[key] = value
        self.record(name, value, labels)

    def get_metrics(
        self, name: Optional[str] = None, since: Optional[datetime] = None, limit: int = 1000
    ) -> List[Metric]:
        """Get metrics with optional filtering."""
        with self._lock:
            filtered = self.metrics

            if name:
                filtered = [m for m in filtered if m.name == name]

            if since:
                filtered = [m for m in filtered if datetime.fromisoformat(m.timestamp) >= since]

            return filtered[-limit:]

    def get_latest(self, name: str) -> Optional[Metric]:
        """Get the latest value for a metric."""
        with self._lock:
            for m in reversed(self.metrics):
                if m.name == name:
                    return m
        return None

    def get_stats(self, name: str, minutes: int = 5) -> Dict[str, float]:
        """Get statistics for a metric over time."""
        since = datetime.now() - timedelta(minutes=minutes)
        metrics = self.get_metrics(name, since)

        if not metrics:
            return {}

        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Group by name
        by_name: Dict[str, List[Metric]] = {}
        with self._lock:
            for m in self.metrics[-1000:]:  # Last 1000 only
                if m.name not in by_name:
                    by_name[m.name] = []
                by_name[m.name].append(m)

        for name, metrics in by_name.items():
            # Prometheus metric name (replace dots with underscores)
            prom_name = name.replace(".", "_").replace("-", "_")
            lines.append(f"# HELP {prom_name} Castle Wyvern metric")
            lines.append(f"# TYPE {prom_name} gauge")

            for m in metrics[-10:]:  # Last 10 per metric
                labels_str = ",".join([f'{k}="{v}"' for k, v in m.labels.items()])
                if labels_str:
                    lines.append(f"{prom_name}{{{labels_str}}} {m.value}")
                else:
                    lines.append(f"{prom_name} {m.value}")

        return "\n".join(lines)


class HealthChecker:
    """
    Performs health checks on Castle Wyvern components.
    """

    def __init__(self):
        self.checks: Dict[str, Callable[[], HealthStatus]] = {}
        self.last_results: Dict[str, HealthStatus] = {}

    def register_check(self, name: str, check_fn: Callable[[], HealthStatus]):
        """Register a health check function."""
        self.checks[name] = check_fn

    def run_check(self, name: str) -> Optional[HealthStatus]:
        """Run a single health check."""
        if name not in self.checks:
            return None

        start = time.time()
        try:
            result = self.checks[name]()
            result.response_time_ms = (time.time() - start) * 1000
            self.last_results[name] = result
            return result
        except Exception as e:
            status = HealthStatus(
                component=name,
                status="unhealthy",
                message=str(e),
                last_check=datetime.now().isoformat(),
                response_time_ms=(time.time() - start) * 1000,
            )
            self.last_results[name] = status
            return status

    def run_all_checks(self) -> Dict[str, HealthStatus]:
        """Run all registered health checks."""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results

    def get_overall_status(self) -> str:
        """Get overall system health status."""
        if not self.last_results:
            return "unknown"

        statuses = [r.status for r in self.last_results.values()]
        if "unhealthy" in statuses:
            return "unhealthy"
        if "degraded" in statuses:
            return "degraded"
        return "healthy"


class MonitoringService:
    """
    Castle Wyvern Advanced Monitoring Service.

    Combines metrics collection, health checking, and alerting
    into a unified monitoring system.
    """

    def __init__(self, phoenix_gate=None, grimoorum=None, plugins=None):
        self.phoenix_gate = phoenix_gate
        self.grimoorum = grimoorum
        self.plugins = plugins

        # Components
        self.metrics = MetricsCollector()
        self.health = HealthChecker()
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []

        # Callbacks for alert notifications
        self.alert_callbacks: List[Callable[[Alert], None]] = []

        # Monitoring state
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Setup default checks and rules
        self._setup_default_checks()
        self._setup_default_rules()

    def _setup_default_checks(self):
        """Setup default health checks."""
        # System health
        self.health.register_check("system.cpu", self._check_cpu)
        self.health.register_check("system.memory", self._check_memory)
        self.health.register_check("system.disk", self._check_disk)

        # Phoenix Gate health
        if self.phoenix_gate:
            self.health.register_check("phoenix_gate", self._check_phoenix_gate)

        # Grimoorum health
        if self.grimoorum:
            self.health.register_check("grimoorum", self._check_grimoorum)

    def _setup_default_rules(self):
        """Setup default alert rules."""
        self.alert_rules.append(
            AlertRule(
                name="high_cpu",
                metric_name="system.cpu.percent",
                condition=lambda x: x > 80,
                severity=AlertSeverity.WARNING,
                message="CPU usage is above 80%",
            )
        )

        self.alert_rules.append(
            AlertRule(
                name="critical_cpu",
                metric_name="system.cpu.percent",
                condition=lambda x: x > 95,
                severity=AlertSeverity.CRITICAL,
                message="CPU usage is above 95%!",
            )
        )

        self.alert_rules.append(
            AlertRule(
                name="high_memory",
                metric_name="system.memory.percent",
                condition=lambda x: x > 85,
                severity=AlertSeverity.WARNING,
                message="Memory usage is above 85%",
            )
        )

        self.alert_rules.append(
            AlertRule(
                name="low_disk",
                metric_name="system.disk.percent",
                condition=lambda x: x > 90,
                severity=AlertSeverity.WARNING,
                message="Disk usage is above 90%",
            )
        )

        self.alert_rules.append(
            AlertRule(
                name="phoenix_gate_errors",
                metric_name="phoenix_gate.error_rate",
                condition=lambda x: x > 0.1,  # 10% error rate
                severity=AlertSeverity.ERROR,
                message="Phoenix Gate error rate is above 10%",
            )
        )

    def _check_cpu(self) -> HealthStatus:
        """Check CPU health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.metrics.set_gauge("system.cpu.percent", cpu_percent)

            if cpu_percent > 90:
                status = "unhealthy"
                message = f"CPU usage critical: {cpu_percent:.1f}%"
            elif cpu_percent > 70:
                status = "degraded"
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = "healthy"
                message = f"CPU usage normal: {cpu_percent:.1f}%"

            return HealthStatus(
                component="system.cpu",
                status=status,
                message=message,
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )
        except Exception as e:
            return HealthStatus(
                component="system.cpu",
                status="unhealthy",
                message=str(e),
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )

    def _check_memory(self) -> HealthStatus:
        """Check memory health."""
        try:
            mem = psutil.virtual_memory()
            self.metrics.set_gauge("system.memory.percent", mem.percent)
            self.metrics.set_gauge("system.memory.available_gb", mem.available / (1024**3))

            if mem.percent > 95:
                status = "unhealthy"
                message = f"Memory critical: {mem.percent:.1f}% used"
            elif mem.percent > 80:
                status = "degraded"
                message = f"Memory high: {mem.percent:.1f}% used"
            else:
                status = "healthy"
                message = (
                    f"Memory OK: {mem.percent:.1f}% used ({mem.available / (1024**3):.1f} GB free)"
                )

            return HealthStatus(
                component="system.memory",
                status=status,
                message=message,
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )
        except Exception as e:
            return HealthStatus(
                component="system.memory",
                status="unhealthy",
                message=str(e),
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )

    def _check_disk(self) -> HealthStatus:
        """Check disk health."""
        try:
            disk = psutil.disk_usage("/")
            percent = (disk.used / disk.total) * 100
            self.metrics.set_gauge("system.disk.percent", percent)

            if percent > 95:
                status = "unhealthy"
                message = f"Disk critical: {percent:.1f}% used"
            elif percent > 85:
                status = "degraded"
                message = f"Disk high: {percent:.1f}% used"
            else:
                status = "healthy"
                message = f"Disk OK: {percent:.1f}% used"

            return HealthStatus(
                component="system.disk",
                status=status,
                message=message,
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )
        except Exception as e:
            return HealthStatus(
                component="system.disk",
                status="unhealthy",
                message=str(e),
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )

    def _check_phoenix_gate(self) -> HealthStatus:
        """Check Phoenix Gate health."""
        try:
            stats = self.phoenix_gate.get_stats()

            # Check circuit breakers
            states = [s["state"] for s in stats.values()]
            if "OPEN" in states:
                status = "degraded"
                message = "Some circuit breakers are open"
            else:
                status = "healthy"
                message = "Phoenix Gate operational"

            return HealthStatus(
                component="phoenix_gate",
                status=status,
                message=message,
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )
        except Exception as e:
            return HealthStatus(
                component="phoenix_gate",
                status="unhealthy",
                message=str(e),
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )

    def _check_grimoorum(self) -> HealthStatus:
        """Check Grimoorum health."""
        try:
            stats = self.grimoorum.get_stats()

            return HealthStatus(
                component="grimoorum",
                status="healthy",
                message=f"Grimoorum: {stats.get('total_memories', 0)} memories",
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )
        except Exception as e:
            return HealthStatus(
                component="grimoorum",
                status="unhealthy",
                message=str(e),
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
            )

    def start(self, interval_seconds: int = 30):
        """Start the monitoring service."""
        if self._running:
            return

        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval_seconds,), daemon=True
        )
        self._monitor_thread.start()
        print(f"[Monitoring] Started with {interval_seconds}s interval")

    def stop(self):
        """Stop the monitoring service."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("[Monitoring] Stopped")

    def _monitor_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        while self._running:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Run health checks
                self.health.run_all_checks()

                # Check alert rules
                self._check_alert_rules()

            except Exception as e:
                print(f"[Monitoring] Error in monitor loop: {e}")

            time.sleep(interval_seconds)

    def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # CPU
        self.metrics.set_gauge("system.cpu.percent", psutil.cpu_percent(interval=0.1))

        # Memory
        mem = psutil.virtual_memory()
        self.metrics.set_gauge("system.memory.percent", mem.percent)
        self.metrics.set_gauge("system.memory.used_gb", mem.used / (1024**3))

        # Disk
        disk = psutil.disk_usage("/")
        self.metrics.set_gauge("system.disk.percent", (disk.used / disk.total) * 100)

        # Network
        net_io = psutil.net_io_counters()
        self.metrics.set_gauge("system.network.sent_mb", net_io.bytes_sent / (1024**2))
        self.metrics.set_gauge("system.network.recv_mb", net_io.bytes_recv / (1024**2))

    def _check_alert_rules(self):
        """Check all alert rules and trigger alerts."""
        for rule in self.alert_rules:
            # Get latest metric value
            latest = self.metrics.get_latest(rule.metric_name)
            if latest is None:
                continue

            # Check rule
            if rule.check(latest.value):
                alert = rule.create_alert()
                self._trigger_alert(alert)

    def _trigger_alert(self, alert: Alert):
        """Trigger an alert."""
        self.alerts.append(alert)

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"[Monitoring] Alert callback error: {e}")

        print(f"[ALERT] [{alert.severity.value.upper()}] {alert.message}")

    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """Register a callback for alert notifications."""
        self.alert_callbacks.append(callback)

    def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule."""
        self.alert_rules.append(rule)

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                return True
        return False

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active (unresolved) alerts."""
        alerts = [a for a in self.alerts if not a.resolved]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_all_alerts(self, limit: int = 100) -> List[Alert]:
        """Get all alerts (including resolved)."""
        return sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:limit]

    def get_status(self) -> Dict:
        """Get comprehensive monitoring status."""
        return {
            "running": self._running,
            "overall_health": self.health.get_overall_status(),
            "health_checks": {
                name: status.to_dict() for name, status in self.health.last_results.items()
            },
            "active_alerts": len(self.get_active_alerts()),
            "total_alerts": len(self.alerts),
            "alert_rules": len(self.alert_rules),
            "metrics_stored": len(self.metrics.metrics),
        }


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Monitoring Test")
    print("=" * 50)

    # Create monitoring service
    monitoring = MonitoringService()

    # Run a quick health check
    print("\nRunning health checks...")
    results = monitoring.health.run_all_checks()

    for name, status in results.items():
        icon = "🟢" if status.status == "healthy" else "🟡" if status.status == "degraded" else "🔴"
        print(f"{icon} {name}: {status.status} - {status.message}")

    # Show metrics
    print("\nCollected metrics:")
    for name in ["system.cpu.percent", "system.memory.percent", "system.disk.percent"]:
        latest = monitoring.metrics.get_latest(name)
        if latest:
            print(f"  {name}: {latest.value:.1f}%")

    print("\n✅ Monitoring system ready!")
