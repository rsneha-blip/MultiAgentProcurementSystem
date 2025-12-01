"""
Agentic AI Implementation - True Agent Autonomy

This package implements autonomous agents that communicate with each other
without central orchestration, demonstrating true agentic behavior vs.
workflow orchestration.
"""

from .agent_communication import BaseAgentV2, MessageBus, MessageType, get_message_bus
from .agentic_supervisor import AgenticSupervisor
from .sourcing_agent import SourcingAgent
from .compliance_agent import ComplianceAgent
from .negotiation_agent import NegotiationAgent

__all__ = [
    "BaseAgentV2",
    "MessageBus", 
    "MessageType",
    "get_message_bus",
    "AgenticSupervisor",
    "SourcingAgent",
    "ComplianceAgent", 
    "NegotiationAgent"
]