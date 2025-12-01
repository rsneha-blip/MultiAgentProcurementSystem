"""
Span Collector - Advanced Trace Data Aggregation

Collects and analyzes spans from distributed traces to provide
insights into system performance, bottlenecks, and usage patterns.
"""
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics
import json

from .tracer import Span, Trace, SpanKind, SpanStatus
from config.settings import get_settings


class SpanMetrics:
    """Aggregated metrics for spans of the same operation."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.count = 0
        self.total_duration_ms = 0.0
        self.min_duration_ms = float('inf')
        self.max_duration_ms = 0.0
        self.error_count = 0
        self.recent_durations = deque(maxlen=100)  # Keep last 100 for percentiles
        
    def add_span(self, span: Span) -> None:
        """Add a span to the metrics calculation."""
        if span.duration_ms is None:
            return
            
        self.count += 1
        self.total_duration_ms += span.duration_ms
        self.min_duration_ms = min(self.min_duration_ms, span.duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, span.duration_ms)
        self.recent_durations.append(span.duration_ms)
        
        if span.status == SpanStatus.ERROR:
            self.error_count += 1
    
    def get_avg_duration_ms(self) -> float:
        """Get average duration."""
        return self.total_duration_ms / self.count if self.count > 0 else 0.0
    
    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        return (self.error_count / self.count * 100) if self.count > 0 else 0.0
    
    def get_percentiles(self) -> Dict[str, float]:
        """Get duration percentiles."""
        if not self.recent_durations:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        durations = sorted(self.recent_durations)
        return {
            "p50": statistics.median(durations),
            "p95": durations[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
            "p99": durations[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        percentiles = self.get_percentiles()
        return {
            "operation_name": self.operation_name,
            "count": self.count,
            "avg_duration_ms": round(self.get_avg_duration_ms(), 2),
            "min_duration_ms": round(self.min_duration_ms, 2) if self.min_duration_ms != float('inf') else 0,
            "max_duration_ms": round(self.max_duration_ms, 2),
            "error_rate_percent": round(self.get_error_rate(), 2),
            "p50_duration_ms": round(percentiles["p50"], 2),
            "p95_duration_ms": round(percentiles["p95"], 2),
            "p99_duration_ms": round(percentiles["p99"], 2)
        }


class BottleneckDetector:
    """Detects performance bottlenecks in traces."""
    
    def __init__(self, threshold_percentile: float = 95.0):
        self.threshold_percentile = threshold_percentile
        self.bottleneck_threshold_ms = 1000.0  # 1 second
        
    def analyze_trace(self, trace: Trace) -> List[Dict[str, Any]]:
        """Analyze a trace for bottlenecks."""
        bottlenecks = []
        
        if not trace.spans:
            return bottlenecks
        
        # Find spans that took longer than threshold
        slow_spans = [
            span for span in trace.spans 
            if span.duration_ms and span.duration_ms > self.bottleneck_threshold_ms
        ]
        
        for span in slow_spans:
            # Calculate what percentage of total trace time this span took
            total_trace_duration = trace.get_duration_ms()
            if total_trace_duration > 0:
                percentage = (span.duration_ms / total_trace_duration) * 100
                
                bottleneck = {
                    "span_id": span.span_id,
                    "operation_name": span.operation_name,
                    "duration_ms": span.duration_ms,
                    "percentage_of_trace": round(percentage, 1),
                    "agent_role": span.agent_role,
                    "workflow_step": span.workflow_step,
                    "kind": span.kind.value,
                    "severity": self._classify_severity(span.duration_ms)
                }
                
                bottlenecks.append(bottleneck)
        
        # Sort by duration descending
        return sorted(bottlenecks, key=lambda x: x["duration_ms"], reverse=True)
    
    def _classify_severity(self, duration_ms: float) -> str:
        """Classify bottleneck severity."""
        if duration_ms > 5000:  # 5 seconds
            return "critical"
        elif duration_ms > 2000:  # 2 seconds
            return "high"
        elif duration_ms > 1000:  # 1 second
            return "medium"
        else:
            return "low"


class SpanCollector:
    """Collects and analyzes spans from procurement traces."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Metrics storage
        self.operation_metrics: Dict[str, SpanMetrics] = {}
        self.agent_metrics: Dict[str, SpanMetrics] = {}
        self.tool_metrics: Dict[str, SpanMetrics] = {}
        
        # Raw data storage (limited retention)
        self.recent_spans: deque = deque(maxlen=1000)
        self.recent_traces: deque = deque(maxlen=100)
        
        # Analysis components
        self.bottleneck_detector = BottleneckDetector()
        
        # Session tracking
        self.session_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_spans": 0,
            "total_duration_ms": 0,
            "error_count": 0,
            "operations": set(),
            "agents_involved": set()
        })
    
    def collect_span(self, span: Span) -> None:
        """
        Collect a span for analysis.
        
        Args:
            span: The span to collect
        """
        if span.duration_ms is None:
            return
        
        # Store raw span
        self.recent_spans.append(span)
        
        # Update operation metrics
        if span.operation_name not in self.operation_metrics:
            self.operation_metrics[span.operation_name] = SpanMetrics(span.operation_name)
        self.operation_metrics[span.operation_name].add_span(span)
        
        # Update agent metrics
        if span.agent_role:
            if span.agent_role not in self.agent_metrics:
                self.agent_metrics[span.agent_role] = SpanMetrics(f"agent_{span.agent_role}")
            self.agent_metrics[span.agent_role].add_span(span)
        
        # Update tool metrics for tool spans
        if span.kind == SpanKind.TOOL:
            if span.operation_name not in self.tool_metrics:
                self.tool_metrics[span.operation_name] = SpanMetrics(f"tool_{span.operation_name}")
            self.tool_metrics[span.operation_name].add_span(span)
        
        # Update session stats
        if span.session_id:
            stats = self.session_stats[span.session_id]
            stats["total_spans"] += 1
            stats["total_duration_ms"] += span.duration_ms
            if span.status == SpanStatus.ERROR:
                stats["error_count"] += 1
            stats["operations"].add(span.operation_name)
            if span.agent_role:
                stats["agents_involved"].add(span.agent_role)
    
    def collect_trace(self, trace: Trace) -> None:
        """
        Collect an entire trace for analysis.
        
        Args:
            trace: The trace to collect
        """
        self.recent_traces.append(trace)
        
        # Collect all spans in the trace
        for span in trace.spans:
            self.collect_span(span)
        
        # Analyze for bottlenecks
        bottlenecks = self.bottleneck_detector.analyze_trace(trace)
        if bottlenecks and self.settings.debug_mode:
            print(f"🐢 Bottlenecks detected in trace {trace.trace_id[:8]}: {len(bottlenecks)} slow operations")
    
    def get_operation_metrics(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get metrics for top operations by call count."""
        metrics = sorted(
            [metric.to_dict() for metric in self.operation_metrics.values()],
            key=lambda x: x["count"],
            reverse=True
        )
        return metrics[:top_n]
    
    def get_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for each agent."""
        return {
            agent_role: metrics.to_dict() 
            for agent_role, metrics in self.agent_metrics.items()
        }
    
    def get_tool_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for MCP tools."""
        return {
            tool_name: metrics.to_dict()
            for tool_name, metrics in self.tool_metrics.items()
        }
    
    def get_slowest_operations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the slowest operations by average duration."""
        operations = [metric.to_dict() for metric in self.operation_metrics.values()]
        return sorted(operations, key=lambda x: x["avg_duration_ms"], reverse=True)[:limit]
    
    def get_error_prone_operations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get operations with highest error rates."""
        operations = [
            metric.to_dict() for metric in self.operation_metrics.values()
            if metric.error_count > 0
        ]
        return sorted(operations, key=lambda x: x["error_rate_percent"], reverse=True)[:limit]
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary statistics for a specific session."""
        if session_id not in self.session_stats:
            return None
        
        stats = self.session_stats[session_id]
        return {
            "session_id": session_id,
            "total_spans": stats["total_spans"],
            "total_duration_ms": stats["total_duration_ms"],
            "avg_span_duration_ms": (
                stats["total_duration_ms"] / stats["total_spans"] 
                if stats["total_spans"] > 0 else 0
            ),
            "error_count": stats["error_count"],
            "error_rate_percent": (
                (stats["error_count"] / stats["total_spans"]) * 100 
                if stats["total_spans"] > 0 else 0
            ),
            "unique_operations": len(stats["operations"]),
            "agents_involved": list(stats["agents_involved"]),
            "operations": list(stats["operations"])
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        total_spans = sum(metrics.count for metrics in self.operation_metrics.values())
        total_errors = sum(metrics.error_count for metrics in self.operation_metrics.values())
        
        # Calculate average response times
        avg_durations = [
            metrics.get_avg_duration_ms() 
            for metrics in self.operation_metrics.values() 
            if metrics.count > 0
        ]
        
        return {
            "total_spans_collected": total_spans,
            "total_errors": total_errors,
            "overall_error_rate_percent": (total_errors / total_spans * 100) if total_spans > 0 else 0,
            "avg_operation_duration_ms": statistics.mean(avg_durations) if avg_durations else 0,
            "unique_operations": len(self.operation_metrics),
            "active_agents": len(self.agent_metrics),
            "tools_used": len(self.tool_metrics),
            "recent_spans_count": len(self.recent_spans),
            "recent_traces_count": len(self.recent_traces)
        }
    
    def analyze_performance_trends(self, time_window_minutes: int = 30) -> Dict[str, Any]:
        """Analyze performance trends over time window."""
        cutoff_time = time.time() - (time_window_minutes * 60)
        
        # Filter recent spans within time window
        recent_spans = [
            span for span in self.recent_spans
            if span.start_time >= cutoff_time and span.duration_ms is not None
        ]
        
        if not recent_spans:
            return {"message": "No recent activity"}
        
        # Calculate trends
        durations = [span.duration_ms for span in recent_spans]
        errors = [span for span in recent_spans if span.status == SpanStatus.ERROR]
        
        # Group by operation
        operation_trends = defaultdict(list)
        for span in recent_spans:
            operation_trends[span.operation_name].append(span.duration_ms)
        
        return {
            "time_window_minutes": time_window_minutes,
            "total_spans": len(recent_spans),
            "avg_duration_ms": statistics.mean(durations),
            "median_duration_ms": statistics.median(durations),
            "error_rate_percent": (len(errors) / len(recent_spans)) * 100,
            "operation_trends": {
                op: {
                    "count": len(times),
                    "avg_duration_ms": statistics.mean(times),
                    "trend": "improving" if statistics.mean(times) < statistics.median(times) else "degrading"
                }
                for op, times in operation_trends.items()
                if len(times) >= 3  # Need at least 3 data points for trends
            }
        }
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all collected metrics for external analysis."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": self.get_system_health(),
            "operation_metrics": self.get_operation_metrics(),
            "agent_performance": self.get_agent_performance(),
            "tool_usage": self.get_tool_usage_stats(),
            "slowest_operations": self.get_slowest_operations(),
            "error_prone_operations": self.get_error_prone_operations(),
            "performance_trends": self.analyze_performance_trends()
        }
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics (useful for testing)."""
        self.operation_metrics.clear()
        self.agent_metrics.clear()
        self.tool_metrics.clear()
        self.recent_spans.clear()
        self.recent_traces.clear()
        self.session_stats.clear()


# Global collector instance
_collector_instance = None

def get_collector() -> SpanCollector:
    """Get the global span collector instance."""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = SpanCollector()
    return _collector_instance