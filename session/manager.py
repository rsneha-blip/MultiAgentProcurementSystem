"""
Session Manager for Multi-Agent Procurement System

Handles state persistence, agent communication, and workflow coordination
across multiple agents in a procurement workflow.
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
import json
import uuid
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(Enum):
    """Agent role enumeration."""
    SUPERVISOR = "supervisor"
    SOURCING = "sourcing"
    COMPLIANCE = "compliance"
    NEGOTIATION = "negotiation"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    from_agent: str
    to_agent: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class WorkflowStep:
    """Individual step in procurement workflow."""
    step_id: str
    agent_responsible: str
    step_name: str
    status: WorkflowStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class ProcurementRequest:
    """Original procurement request data."""
    request_id: str
    item_description: str
    quantity: int
    budget: float
    urgency: str
    category: str
    requirements: Dict[str, Any]
    requested_by: str
    requested_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SessionState:
    """Complete session state for a procurement workflow."""
    session_id: str
    procurement_request: ProcurementRequest
    workflow_status: WorkflowStatus
    current_step: Optional[str] = None
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    message_history: List[AgentMessage] = field(default_factory=list)
    workflow_steps: List[WorkflowStep] = field(default_factory=list)
    decision_trail: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Procurement-specific data
    supplier_candidates: List[Dict[str, Any]] = field(default_factory=list)
    compliance_results: Dict[str, Any] = field(default_factory=dict)
    negotiation_results: Dict[str, Any] = field(default_factory=dict)
    final_recommendation: Optional[Dict[str, Any]] = None


class SessionManager:
    """Manages session state and agent communication for procurement workflows."""
    
    def __init__(self):
        """Initialize session manager."""
        self.active_sessions: Dict[str, SessionState] = {}
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self, procurement_request: ProcurementRequest) -> str:
        """
        Create a new procurement session.
        
        Args:
            procurement_request: The initial procurement request
            
        Returns:
            str: Session ID
        """
        session_id = str(uuid.uuid4())
        
        session_state = SessionState(
            session_id=session_id,
            procurement_request=procurement_request,
            workflow_status=WorkflowStatus.PENDING
        )
        
        # Initialize workflow steps
        workflow_steps = [
            WorkflowStep("sourcing", AgentRole.SOURCING.value, "Find Suppliers", WorkflowStatus.PENDING),
            WorkflowStep("compliance", AgentRole.COMPLIANCE.value, "Check Compliance", WorkflowStatus.PENDING),
            WorkflowStep("negotiation", AgentRole.NEGOTIATION.value, "Negotiate Terms", WorkflowStatus.PENDING),
            WorkflowStep("approval", AgentRole.SUPERVISOR.value, "Final Approval", WorkflowStatus.PENDING)
        ]
        
        session_state.workflow_steps = workflow_steps
        session_state.current_step = "sourcing"
        
        self.active_sessions[session_id] = session_state
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state by ID."""
        return self.active_sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update session state.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of updates to apply
            
        Returns:
            bool: Success status
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.updated_at = datetime.utcnow()
        return True
    
    def add_agent_message(self, session_id: str, message: AgentMessage) -> bool:
        """Add a message to the session's communication history."""
        if session_id not in self.active_sessions:
            return False
        
        self.active_sessions[session_id].message_history.append(message)
        self.active_sessions[session_id].updated_at = datetime.utcnow()
        return True
    
    def update_agent_state(self, session_id: str, agent_role: str, state_data: Dict[str, Any]) -> bool:
        """Update the state for a specific agent."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.agent_states[agent_role] = state_data
        session.updated_at = datetime.utcnow()
        return True
    
    def get_agent_state(self, session_id: str, agent_role: str) -> Optional[Dict[str, Any]]:
        """Get the current state for a specific agent."""
        if session_id not in self.active_sessions:
            return None
        
        return self.active_sessions[session_id].agent_states.get(agent_role)
    
    def advance_workflow(self, session_id: str, current_step: str, result: Dict[str, Any]) -> bool:
        """
        Advance the workflow to the next step.
        
        Args:
            session_id: Session identifier
            current_step: The step being completed
            result: Results from the completed step
            
        Returns:
            bool: Success status
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Find and update current step
        for step in session.workflow_steps:
            if step.step_id == current_step:
                step.status = WorkflowStatus.COMPLETED
                step.completed_at = datetime.utcnow()
                step.result = result
                break
        
        # Record decision in trail
        decision = {
            "step": current_step,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
            "agent": next((s.agent_responsible for s in session.workflow_steps if s.step_id == current_step), "unknown")
        }
        session.decision_trail.append(decision)
        
        # Determine next step
        step_order = ["sourcing", "compliance", "negotiation", "approval"]
        try:
            current_index = step_order.index(current_step)
            if current_index < len(step_order) - 1:
                next_step = step_order[current_index + 1]
                session.current_step = next_step
                
                # Mark next step as in progress
                for step in session.workflow_steps:
                    if step.step_id == next_step:
                        step.status = WorkflowStatus.IN_PROGRESS
                        step.started_at = datetime.utcnow()
                        break
            else:
                # Workflow complete
                session.workflow_status = WorkflowStatus.COMPLETED
                session.current_step = None
        except ValueError:
            # Unknown step
            return False
        
        session.updated_at = datetime.utcnow()
        return True
    
    def require_human_approval(self, session_id: str, reason: str, data: Dict[str, Any]) -> bool:
        """Flag session as requiring human approval."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.workflow_status = WorkflowStatus.WAITING_FOR_APPROVAL
        
        approval_request = {
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "status": "pending"
        }
        
        session.decision_trail.append(approval_request)
        session.updated_at = datetime.utcnow()
        
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count of cleaned up sessions."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session.updated_at > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(expired_sessions)
    
    def export_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export a summary of the session for reporting/auditing."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        summary = {
            "session_id": session_id,
            "request": asdict(session.procurement_request),
            "status": session.workflow_status.value,
            "steps_completed": [step.step_name for step in session.workflow_steps if step.status == WorkflowStatus.COMPLETED],
            "current_step": session.current_step,
            "decision_trail": session.decision_trail,
            "final_recommendation": session.final_recommendation,
            "duration": (session.updated_at - session.created_at).total_seconds(),
            "message_count": len(session.message_history)
        }
        
        return summary