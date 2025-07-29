import json
from typing import Dict, Any, List
from datetime import datetime
from .logger import telemetry, EventMetrics


class TelemetryReporter:
    """Formats and outputs telemetry data"""

    @staticmethod
    def format_metrics(metrics: EventMetrics) -> Dict[str, Any]:
        """Format a single metric record"""
        return {
            "event_name": metrics.event_name,
            "task_id": metrics.task_id,
            "start_time": datetime.fromtimestamp(metrics.start_time).isoformat(),
            "end_time": (
                datetime.fromtimestamp(metrics.end_time).isoformat()
                if metrics.end_time
                else None
            ),
            "duration": f"{metrics.duration():.3f}s",
            "status": metrics.status,
            "error": metrics.error,
            "retry_count": metrics.retry_count,
            "process_id": metrics.process_id,
        }

    def get_all_metrics_json(self) -> str:
        """Get all metrics as JSON string"""
        metrics = telemetry.get_all_metrics()
        formatted = [self.format_metrics(m) for m in metrics.values()]
        return json.dumps(formatted, indent=2)

    def get_failed_events(self) -> List[Dict[str, Any]]:
        """Get metrics for all failed events"""
        metrics = telemetry.get_all_metrics()
        return [
            self.format_metrics(m) for m in metrics.values() if m.status == "failed"
        ]

    def get_slow_events(self, threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """Get metrics for events that took longer than threshold"""
        metrics = telemetry.get_all_metrics()
        return [
            self.format_metrics(m)
            for m in metrics.values()
            if m.duration() > threshold_seconds
        ]

    def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry statistics"""
        metrics = telemetry.get_all_metrics()
        total_retries = sum(m.retry_count for m in metrics.values())
        events_with_retries = sum(1 for m in metrics.values() if m.retry_count > 0)

        return {
            "total_retries": total_retries,
            "events_with_retries": events_with_retries,
            "events_by_retry_count": {
                str(i): len([m for m in metrics.values() if m.retry_count == i])
                for i in range(
                    max((m.retry_count for m in metrics.values()), default=0) + 1
                )
            },
        }


# Global reporter instance
reporter = TelemetryReporter()
