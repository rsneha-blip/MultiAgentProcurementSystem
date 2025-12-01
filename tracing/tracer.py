"""
Procurement Tracer - Distributed Tracing for Multi-Agent Systems

Implements OpenTelemetry-style distributed tracing specifically designed
for procurement workflows and agent interactions.
"""
import time
import uuid
from typing import Dict, Any, List, Optional, ContextManager
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import contextmanager
from enum import Enum
import json
import logging

from config.settings import get_settings


class SpanKind(Enum):
    """Types of spans in the procurement system."""
    REQUEST = "request"              # User request -> system response
    WORKFLOW = "workflow"            # Workflow step execution  
    AGENT = "agent"                 # Agent processing
    TOOL = "tool"                   # MCP tool execution
    COMMUNICATION = "communication"  # Agent-to-agent messages
    HUMAN = "human"                 # Human-in-the-loop interactions
    DECISION = "decision"           # Decision points and rationale


class SpanStatus(Enum):
    """Span execution status."""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TraceAttribute:
    """Individual trace attribute with metadata."""
    key: str
    value: Any
    type: str = field(default="string")
    sensitive: bool = field(default=False)  # For PII data


@dataclass
class Span:
    """Individual span in a distributed trace."""
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trace_id: str = ""
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    kind: SpanKind = SpanKind.REQUEST
    status: SpanStatus = SpanStatus.OK
    
    # Timing
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    
    # Metadata
    attributes: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Procurement-specific
    agent_role: Optional[str] = None
    session_id: Optional[str] = None
    workflow_step: Optional[str] = None
    
    # Error tracking
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    def finish(self) -> None:
        """Mark span as finished and calculate duration."""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def set_attribute(self, key: str, value: Any, sensitive: bool = False) -> None:
        """Set a span attribute."""
        self.attributes[key] = {
            "value": value,
            "type": type(value).__name__,
            "sensitive": sensitive
        }
    
    def set_tag(self, key: str, value: str) -> None:
        """Set a span tag."""
        self.tags[key] = value
    
    def log_event(self, event: str, attributes: Dict[str, Any] = None) -> None:
        """Log an event within the span."""
        log_entry = {
            "timestamp": time.time(),
            "event": event,
            "attributes": attributes or {}
        }
        self.logs.append(log_entry)
    
    def set_error(self, error: Exception = None, message: str = None) -> None:
        """Mark span as having an error."""
        self.status = SpanStatus.ERROR
        
        if error:
            self.error_type = type(error).__name__
            self.error_message = str(error)
        elif message:
            self.error_message = message
        
        self.set_attribute("error", True)
        if self.error_type:
            self.set_attribute("error.type", self.error_type)
        if self.error_message:
            self.set_attribute("error.message", self.error_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary for serialization."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "kind": self.kind.value,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "tags": self.tags,
            "logs": self.logs,
            "agent_role": self.agent_role,
            "session_id": self.session_id,
            "workflow_step": self.workflow_step,
            "error_message": self.error_message,
            "error_type": self.error_type
        }


@dataclass
class Trace:
    """Complete trace containing multiple spans."""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    root_span_id: Optional[str] = None
    spans: List[Span] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Procurement context
    session_id: Optional[str] = None
    procurement_request_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Metadata
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def add_span(self, span: Span) -> None:
        """Add a span to this trace."""
        span.trace_id = self.trace_id
        if not self.root_span_id:
            self.root_span_id = span.span_id
        self.spans.append(span)
    
    def get_span(self, span_id: str) -> Optional[Span]:
        """Get a span by ID."""
        return next((span for span in self.spans if span.span_id == span_id), None)
    
    def finish(self) -> None:
        """Mark trace as finished."""
        if self.end_time is None:
            self.end_time = time.time()
    
    def get_duration_ms(self) -> float:
        """Get total trace duration."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary."""
        return {
            "trace_id": self.trace_id,
            "root_span_id": self.root_span_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.get_duration_ms(),
            "session_id": self.session_id,
            "procurement_request_id": self.procurement_request_id,
            "user_id": self.user_id,
            "attributes": self.attributes,
            "spans": [span.to_dict() for span in self.spans],
            "span_count": len(self.spans)
        }


class ProcurementTracer:
    """Main tracer for procurement workflows."""
    
    def __init__(self):
        """Initialize the procurement tracer."""
        self.settings = get_settings()
        self.logger = logging.getLogger("tracer.procurement")
        
        # Active traces and spans
        self.active_traces: Dict[str, Trace] = {}
        self.active_spans: Dict[str, Span] = {}
        self.completed_traces: List[Trace] = []
        
        # Performance tracking
        self.performance_stats = {
            "total_traces": 0,
            "total_spans": 0,
            "avg_trace_duration_ms": 0,
            "error_rate": 0
        }
    
    def start_trace(self, operation_name: str, session_id: str = None, 
                   user_id: str = None, attributes: Dict[str, Any] = None) -> Trace:
        """
        Start a new distributed trace.
        
        Args:
            operation_name: Name of the root operation
            session_id: Associated session ID
            user_id: User who initiated the request
            attributes: Initial trace attributes
            
        Returns:
            Trace: The new trace object
        """
        trace = Trace(
            session_id=session_id,
            user_id=user_id,
            attributes=attributes or {}
        )
        
        # Create root span
        root_span = Span(
            trace_id=trace.trace_id,
            operation_name=operation_name,
            kind=SpanKind.REQUEST,
            session_id=session_id
        )
        
        trace.add_span(root_span)
        self.active_traces[trace.trace_id] = trace
        self.active_spans[root_span.span_id] = root_span
        
        if self.settings.debug_mode:
            self.logger.info(f"Started trace {trace.trace_id[:8]} for {operation_name}")
        
        return trace
    
    def start_span(self, operation_name: str, parent_span_id: str = None,
                  trace_id: str = None, kind: SpanKind = SpanKind.AGENT,
                  agent_role: str = None, workflow_step: str = None) -> Span:
        """
        Start a new span within a trace.
        
        Args:
            operation_name: Name of the operation
            parent_span_id: Parent span ID for nesting
            trace_id: Trace to add span to
            kind: Type of span
            agent_role: Which agent is performing this operation
            workflow_step: Current workflow step
            
        Returns:
            Span: The new span object
        """
        span = Span(
            operation_name=operation_name,
            parent_span_id=parent_span_id,
            kind=kind,
            agent_role=agent_role,
            workflow_step=workflow_step
        )
        
        # Associate with trace
        if trace_id and trace_id in self.active_traces:
            trace = self.active_traces[trace_id]
            trace.add_span(span)
            span.session_id = trace.session_id
        
        self.active_spans[span.span_id] = span
        
        if self.settings.debug_mode:
            self.logger.info(f"Started span {span.span_id} for {operation_name}")
        
        return span
    
    def finish_span(self, span_id: str) -> Optional[Span]:
        """Finish a span."""
        span = self.active_spans.pop(span_id, None)
        if span:
            span.finish()
            if self.settings.debug_mode:
                self.logger.info(f"Finished span {span_id} ({span.duration_ms:.2f}ms)")
        return span
    
    def finish_trace(self, trace_id: str) -> Optional[Trace]:
        """Finish a trace and move it to completed traces."""
        trace = self.active_traces.pop(trace_id, None)
        if trace:
            trace.finish()
            self.completed_traces.append(trace)
            
            # Update performance stats
            self._update_performance_stats(trace)
            
            if self.settings.debug_mode:
                self.logger.info(f"Finished trace {trace_id[:8]} ({trace.get_duration_ms():.2f}ms)")
        
        return trace
    
    @contextmanager
    def span(self, operation_name: str, parent_span_id: str = None,
            trace_id: str = None, kind: SpanKind = SpanKind.AGENT,
            agent_role: str = None, workflow_step: str = None) -> ContextManager[Span]:
        """
        Context manager for automatic span lifecycle management.
        
        Usage:
            with tracer.span("supplier_search", kind=SpanKind.TOOL) as span:
                span.set_attribute("supplier_count", 5)
                # ... do work ...
                # span automatically finished
        """
        span = self.start_span(
            operation_name=operation_name,
            parent_span_id=parent_span_id,
            trace_id=trace_id,
            kind=kind,
            agent_role=agent_role,
            workflow_step=workflow_step
        )
        
        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            self.finish_span(span.span_id)
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID (active or completed)."""
        if trace_id in self.active_traces:
            return self.active_traces[trace_id]
        
        return next((trace for trace in self.completed_traces 
                    if trace.trace_id == trace_id), None)
    
    def get_traces_for_session(self, session_id: str) -> List[Trace]:
        """Get all traces for a session."""
        traces = []
        
        # Check active traces
        for trace in self.active_traces.values():
            if trace.session_id == session_id:
                traces.append(trace)
        
        # Check completed traces  
        for trace in self.completed_traces:
            if trace.session_id == session_id:
                traces.append(trace)
        
        return traces
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance statistics summary."""
        return self.performance_stats.copy()
    
    def export_traces(self, session_id: str = None, 
                     since: datetime = None) -> List[Dict[str, Any]]:
        """
        Export traces for analysis or visualization.
        
        Args:
            session_id: Filter by session ID
            since: Only traces after this time
            
        Returns:
            List of trace dictionaries
        """
        traces_to_export = []
        
        all_traces = list(self.active_traces.values()) + self.completed_traces
        
        for trace in all_traces:
            # Apply filters
            if session_id and trace.session_id != session_id:
                continue
            
            if since and trace.start_time < since.timestamp():
                continue
            
            traces_to_export.append(trace.to_dict())
        
        return traces_to_export
    
    def cleanup_old_traces(self, max_age_hours: int = 24) -> int:
        """Clean up old completed traces."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        before_count = len(self.completed_traces)
        self.completed_traces = [
            trace for trace in self.completed_traces
            if trace.start_time > cutoff_time
        ]
        
        cleaned_count = before_count - len(self.completed_traces)
        
        if cleaned_count > 0 and self.settings.debug_mode:
            self.logger.info(f"Cleaned up {cleaned_count} old traces")
        
        return cleaned_count
    
    def _update_performance_stats(self, trace: Trace) -> None:
        """Update performance statistics with completed trace."""
        self.performance_stats["total_traces"] += 1
        self.performance_stats["total_spans"] += len(trace.spans)
        
        # Update average duration
        current_avg = self.performance_stats["avg_trace_duration_ms"]
        trace_count = self.performance_stats["total_traces"]
        trace_duration = trace.get_duration_ms()
        
        new_avg = ((current_avg * (trace_count - 1)) + trace_duration) / trace_count
        self.performance_stats["avg_trace_duration_ms"] = new_avg
        
        # Update error rate
        error_spans = sum(1 for span in trace.spans if span.status == SpanStatus.ERROR)
        if error_spans > 0:
            total_spans = self.performance_stats["total_spans"]
            self.performance_stats["error_rate"] = (
                (self.performance_stats["error_rate"] * (total_spans - len(trace.spans)) + error_spans) 
                / total_spans
            )


# Global tracer instance
_tracer_instance = None

def get_tracer() -> ProcurementTracer:
    """Get the global tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = ProcurementTracer()
    return _tracer_instance