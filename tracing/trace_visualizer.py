"""
Trace Visualizer - Creates Visual Representations of Procurement Traces

Generates various visualizations of traces including timeline views,
dependency graphs, and performance heatmaps for demo and debugging.
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics

from .tracer import Trace, Span, SpanKind, SpanStatus
from .span_collector import SpanCollector


class TraceVisualizer:
    """Creates visual representations and data for trace analysis."""
    
    def __init__(self, span_collector: Optional[SpanCollector] = None):
        self.span_collector = span_collector
    
    def generate_timeline_data(self, trace: Trace) -> Dict[str, Any]:
        """
        Generate timeline visualization data for a trace.
        
        Args:
            trace: The trace to visualize
            
        Returns:
            Timeline data suitable for visualization libraries
        """
        if not trace.spans:
            return {"spans": [], "total_duration": 0, "agents": []}
        
        # Sort spans by start time
        spans = sorted(trace.spans, key=lambda s: s.start_time)
        
        # Calculate relative timings
        start_time = trace.start_time
        timeline_spans = []
        agents_involved = set()
        
        for span in spans:
            if span.duration_ms is None:
                continue
                
            relative_start = (span.start_time - start_time) * 1000  # Convert to ms
            
            timeline_span = {
                "id": span.span_id,
                "name": span.operation_name,
                "start": relative_start,
                "duration": span.duration_ms,
                "end": relative_start + span.duration_ms,
                "agent": span.agent_role or "system",
                "kind": span.kind.value,
                "status": span.status.value,
                "workflow_step": span.workflow_step,
                "parent_id": span.parent_span_id,
                "attributes": span.attributes,
                "error_message": span.error_message
            }
            
            timeline_spans.append(timeline_span)
            if span.agent_role:
                agents_involved.add(span.agent_role)
        
        return {
            "trace_id": trace.trace_id,
            "spans": timeline_spans,
            "total_duration": trace.get_duration_ms(),
            "agents": sorted(list(agents_involved)),
            "start_time": trace.start_time,
            "session_id": trace.session_id
        }
    
    def generate_gantt_chart_data(self, trace: Trace) -> Dict[str, Any]:
        """
        Generate Gantt chart data showing agent activities over time.
        
        Args:
            trace: The trace to visualize
            
        Returns:
            Gantt chart data organized by agent
        """
        timeline = self.generate_timeline_data(trace)
        
        # Group spans by agent
        agent_activities = {}
        for span in timeline["spans"]:
            agent = span["agent"]
            if agent not in agent_activities:
                agent_activities[agent] = []
            
            activity = {
                "name": span["name"],
                "start": span["start"],
                "duration": span["duration"],
                "status": span["status"],
                "kind": span["kind"],
                "workflow_step": span["workflow_step"]
            }
            agent_activities[agent].append(activity)
        
        # Sort activities within each agent by start time
        for agent in agent_activities:
            agent_activities[agent].sort(key=lambda x: x["start"])
        
        return {
            "trace_id": trace.trace_id,
            "total_duration": timeline["total_duration"],
            "agents": agent_activities
        }
    
    def generate_dependency_graph(self, trace: Trace) -> Dict[str, Any]:
        """
        Generate dependency graph showing span relationships.
        
        Args:
            trace: The trace to analyze
            
        Returns:
            Graph data with nodes and edges
        """
        nodes = []
        edges = []
        
        for span in trace.spans:
            # Create node
            node = {
                "id": span.span_id,
                "label": span.operation_name,
                "agent": span.agent_role or "system",
                "kind": span.kind.value,
                "status": span.status.value,
                "duration": span.duration_ms or 0,
                "workflow_step": span.workflow_step
            }
            nodes.append(node)
            
            # Create edge to parent
            if span.parent_span_id:
                edge = {
                    "from": span.parent_span_id,
                    "to": span.span_id,
                    "relationship": "parent_child"
                }
                edges.append(edge)
        
        return {
            "trace_id": trace.trace_id,
            "nodes": nodes,
            "edges": edges
        }
    
    def generate_performance_heatmap(self, traces: List[Trace]) -> Dict[str, Any]:
        """
        Generate performance heatmap data from multiple traces.
        
        Args:
            traces: List of traces to analyze
            
        Returns:
            Heatmap data showing operation performance
        """
        operation_stats = {}
        
        for trace in traces:
            for span in trace.spans:
                if span.duration_ms is None:
                    continue
                
                key = f"{span.agent_role or 'system'}:{span.operation_name}"
                
                if key not in operation_stats:
                    operation_stats[key] = {
                        "agent": span.agent_role or "system",
                        "operation": span.operation_name,
                        "durations": [],
                        "error_count": 0,
                        "total_count": 0
                    }
                
                stats = operation_stats[key]
                stats["durations"].append(span.duration_ms)
                stats["total_count"] += 1
                
                if span.status == SpanStatus.ERROR:
                    stats["error_count"] += 1
        
        # Calculate aggregate statistics
        heatmap_data = []
        for key, stats in operation_stats.items():
            if stats["durations"]:
                heatmap_entry = {
                    "agent": stats["agent"],
                    "operation": stats["operation"],
                    "avg_duration": statistics.mean(stats["durations"]),
                    "median_duration": statistics.median(stats["durations"]),
                    "max_duration": max(stats["durations"]),
                    "count": stats["total_count"],
                    "error_rate": stats["error_count"] / stats["total_count"],
                    "performance_score": self._calculate_performance_score(
                        statistics.mean(stats["durations"]),
                        stats["error_count"] / stats["total_count"]
                    )
                }
                heatmap_data.append(heatmap_entry)
        
        return {
            "operations": heatmap_data,
            "total_traces_analyzed": len(traces)
        }
    
    def generate_workflow_flow_diagram(self, traces: List[Trace]) -> Dict[str, Any]:
        """
        Generate workflow flow diagram showing common paths through the system.
        
        Args:
            traces: List of traces to analyze
            
        Returns:
            Flow diagram data
        """
        # Track workflow transitions
        transitions = {}
        step_stats = {}
        
        for trace in traces:
            # Sort spans by start time to get workflow order
            workflow_spans = [
                span for span in sorted(trace.spans, key=lambda s: s.start_time)
                if span.workflow_step
            ]
            
            # Track steps and transitions
            for i, span in enumerate(workflow_spans):
                step = span.workflow_step
                
                # Track step statistics
                if step not in step_stats:
                    step_stats[step] = {
                        "count": 0,
                        "total_duration": 0,
                        "error_count": 0
                    }
                
                step_stats[step]["count"] += 1
                step_stats[step]["total_duration"] += span.duration_ms or 0
                if span.status == SpanStatus.ERROR:
                    step_stats[step]["error_count"] += 1
                
                # Track transitions
                if i < len(workflow_spans) - 1:
                    next_step = workflow_spans[i + 1].workflow_step
                    transition_key = f"{step} -> {next_step}"
                    
                    if transition_key not in transitions:
                        transitions[transition_key] = 0
                    transitions[transition_key] += 1
        
        # Convert to flow diagram format
        nodes = []
        for step, stats in step_stats.items():
            avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
            error_rate = stats["error_count"] / stats["count"] if stats["count"] > 0 else 0
            
            node = {
                "id": step,
                "label": step.replace("_", " ").title(),
                "count": stats["count"],
                "avg_duration": avg_duration,
                "error_rate": error_rate,
                "health_score": self._calculate_health_score(avg_duration, error_rate)
            }
            nodes.append(node)
        
        edges = []
        for transition, count in transitions.items():
            from_step, to_step = transition.split(" -> ")
            edge = {
                "from": from_step,
                "to": to_step,
                "weight": count,
                "label": f"{count} transitions"
            }
            edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_workflows": len(traces)
        }
    
    def generate_agent_communication_graph(self, traces: List[Trace]) -> Dict[str, Any]:
        """
        Generate graph showing communication patterns between agents.
        
        Args:
            traces: List of traces to analyze
            
        Returns:
            Communication graph data
        """
        agent_interactions = {}
        agent_stats = {}
        
        for trace in traces:
            agents_in_trace = set()
            
            for span in trace.spans:
                if span.agent_role:
                    agents_in_trace.add(span.agent_role)
                    
                    # Track agent statistics
                    if span.agent_role not in agent_stats:
                        agent_stats[span.agent_role] = {
                            "total_operations": 0,
                            "total_duration": 0,
                            "error_count": 0
                        }
                    
                    agent_stats[span.agent_role]["total_operations"] += 1
                    agent_stats[span.agent_role]["total_duration"] += span.duration_ms or 0
                    if span.status == SpanStatus.ERROR:
                        agent_stats[span.agent_role]["error_count"] += 1
            
            # Create interaction edges (any two agents in the same trace interact)
            agents_list = list(agents_in_trace)
            for i, agent1 in enumerate(agents_list):
                for agent2 in agents_list[i+1:]:
                    interaction_key = tuple(sorted([agent1, agent2]))
                    
                    if interaction_key not in agent_interactions:
                        agent_interactions[interaction_key] = 0
                    agent_interactions[interaction_key] += 1
        
        # Convert to graph format
        nodes = []
        for agent, stats in agent_stats.items():
            avg_duration = (
                stats["total_duration"] / stats["total_operations"] 
                if stats["total_operations"] > 0 else 0
            )
            error_rate = (
                stats["error_count"] / stats["total_operations"] 
                if stats["total_operations"] > 0 else 0
            )
            
            node = {
                "id": agent,
                "label": agent.replace("_", " ").title(),
                "total_operations": stats["total_operations"],
                "avg_duration": avg_duration,
                "error_rate": error_rate,
                "performance_score": self._calculate_performance_score(avg_duration, error_rate)
            }
            nodes.append(node)
        
        edges = []
        for (agent1, agent2), count in agent_interactions.items():
            edge = {
                "from": agent1,
                "to": agent2,
                "weight": count,
                "label": f"{count} collaborations"
            }
            edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_interactions": sum(agent_interactions.values())
        }
    
    def _calculate_performance_score(self, avg_duration_ms: float, error_rate: float) -> float:
        """
        Calculate a performance score (0-100) based on duration and error rate.
        
        Args:
            avg_duration_ms: Average duration in milliseconds
            error_rate: Error rate as decimal (0.0 to 1.0)
            
        Returns:
            Performance score (higher is better)
        """
        # Normalize duration score (assume 1000ms is baseline, 100ms is excellent)
        duration_score = max(0, 100 - (avg_duration_ms / 10))  # 10ms = 1 point penalty
        duration_score = min(100, duration_score)
        
        # Error rate score (0 errors = 100, 100% errors = 0)
        error_score = max(0, 100 - (error_rate * 100))
        
        # Weighted average (duration 60%, error rate 40%)
        return round((duration_score * 0.6) + (error_score * 0.4), 1)
    
    def _calculate_health_score(self, avg_duration_ms: float, error_rate: float) -> str:
        """Calculate health status based on performance metrics."""
        performance_score = self._calculate_performance_score(avg_duration_ms, error_rate)
        
        if performance_score >= 80:
            return "excellent"
        elif performance_score >= 60:
            return "good"
        elif performance_score >= 40:
            return "fair"
        else:
            return "poor"
    
    def export_visualization_data(self, traces: List[Trace]) -> Dict[str, Any]:
        """
        Export all visualization data for a set of traces.
        
        Args:
            traces: List of traces to visualize
            
        Returns:
            Complete visualization dataset
        """
        if not traces:
            return {"error": "No traces provided"}
        
        # Generate individual trace visualizations
        trace_timelines = []
        for trace in traces[:10]:  # Limit to 10 most recent for performance
            timeline = self.generate_timeline_data(trace)
            trace_timelines.append(timeline)
        
        return {
            "summary": {
                "total_traces": len(traces),
                "date_range": {
                    "start": min(trace.start_time for trace in traces),
                    "end": max(trace.end_time or trace.start_time for trace in traces)
                }
            },
            "trace_timelines": trace_timelines,
            "performance_heatmap": self.generate_performance_heatmap(traces),
            "workflow_flow": self.generate_workflow_flow_diagram(traces),
            "agent_communication": self.generate_agent_communication_graph(traces)
        }