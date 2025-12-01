"""
Tool Registry for MCP Server

Manages registration and discovery of tools available to agents.
Implements security controls to ensure agents only access appropriate tools.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import logging
from enum import Enum

from config.settings import get_settings


class ToolCategory(Enum):
    """Tool categories for organization and access control."""
    SOURCING = "sourcing"
    COMPLIANCE = "compliance"
    NEGOTIATION = "negotiation"
    WORKFLOW = "workflow"
    UTILITY = "utility"


@dataclass
class ToolDefinition:
    """Definition of an MCP tool."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any]
    allowed_agents: List[str]
    handler: Callable
    requires_approval: bool = False


class ToolRegistry:
    """Registry for managing MCP tools and access control."""
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, ToolDefinition] = {}
        self.settings = get_settings()
        self.logger = logging.getLogger("mcp.tools")
        
        # Initialize with basic tools
        self._register_default_tools()
    
    def register_tool(self, tool_def: ToolDefinition) -> bool:
        """
        Register a new tool.
        
        Args:
            tool_def: Tool definition to register
            
        Returns:
            bool: Success status
        """
        try:
            self.tools[tool_def.name] = tool_def
            
            if self.settings.debug_mode:
                self.logger.info(f"Registered tool: {tool_def.name} ({tool_def.category.value})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_def.name}: {str(e)}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name."""
        return self.tools.get(tool_name)
    
    def get_tools_for_agent(self, agent_role: str) -> List[ToolDefinition]:
        """
        Get all tools available to a specific agent.
        
        Args:
            agent_role: Role of the requesting agent
            
        Returns:
            List of tool definitions the agent can access
        """
        available_tools = []
        
        for tool in self.tools.values():
            if agent_role in tool.allowed_agents or "all" in tool.allowed_agents:
                available_tools.append(tool)
        
        return available_tools
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a specific category."""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def list_all_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self.tools.keys())
    
    def can_agent_access_tool(self, agent_role: str, tool_name: str) -> bool:
        """
        Check if an agent can access a specific tool.
        
        Args:
            agent_role: Role of the requesting agent
            tool_name: Name of the tool to check
            
        Returns:
            bool: Whether agent can access the tool
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return False
        
        return agent_role in tool.allowed_agents or "all" in tool.allowed_agents
    
    def _register_default_tools(self):
        """Register default tools for the procurement system."""
        
        # Sourcing tools
        sourcing_tools = [
            ToolDefinition(
                name="supplier_search",
                description="Search for suppliers based on requirements",
                category=ToolCategory.SOURCING,
                parameters={
                    "type": "object",
                    "properties": {
                        "requirements": {"type": "string", "description": "Supplier requirements"},
                        "category": {"type": "string", "description": "Product category"},
                        "budget": {"type": "number", "description": "Budget constraint"}
                    },
                    "required": ["requirements", "category"]
                },
                allowed_agents=["sourcing", "supervisor"],
                handler=self._placeholder_handler
            ),
            ToolDefinition(
                name="supplier_evaluation",
                description="Evaluate supplier capabilities and scores",
                category=ToolCategory.SOURCING,
                parameters={
                    "type": "object",
                    "properties": {
                        "supplier_id": {"type": "string", "description": "Supplier identifier"},
                        "criteria": {"type": "array", "description": "Evaluation criteria"}
                    },
                    "required": ["supplier_id"]
                },
                allowed_agents=["sourcing"],
                handler=self._placeholder_handler
            )
        ]
        
        # Compliance tools
        compliance_tools = [
            ToolDefinition(
                name="compliance_check",
                description="Check supplier against compliance policies",
                category=ToolCategory.COMPLIANCE,
                parameters={
                    "type": "object",
                    "properties": {
                        "supplier_id": {"type": "string", "description": "Supplier to check"},
                        "policy_category": {"type": "string", "description": "Policy category"}
                    },
                    "required": ["supplier_id"]
                },
                allowed_agents=["compliance", "supervisor"],
                handler=self._placeholder_handler
            ),
            ToolDefinition(
                name="policy_lookup",
                description="Look up specific policy requirements",
                category=ToolCategory.COMPLIANCE,
                parameters={
                    "type": "object",
                    "properties": {
                        "policy_type": {"type": "string", "description": "Type of policy"},
                        "category": {"type": "string", "description": "Product category"}
                    },
                    "required": ["policy_type"]
                },
                allowed_agents=["compliance", "sourcing"],
                handler=self._placeholder_handler
            )
        ]
        
        # Negotiation tools
        negotiation_tools = [
            ToolDefinition(
                name="price_negotiation",
                description="Negotiate price with supplier",
                category=ToolCategory.NEGOTIATION,
                parameters={
                    "type": "object",
                    "properties": {
                        "supplier_id": {"type": "string", "description": "Supplier to negotiate with"},
                        "target_price": {"type": "number", "description": "Target price"},
                        "volume": {"type": "integer", "description": "Order volume"}
                    },
                    "required": ["supplier_id", "target_price"]
                },
                allowed_agents=["negotiation"],
                handler=self._placeholder_handler,
                requires_approval=True  # High-value negotiations need approval
            )
        ]
        
        # Workflow tools
        workflow_tools = [
            ToolDefinition(
                name="workflow_status",
                description="Check workflow status and progress",
                category=ToolCategory.WORKFLOW,
                parameters={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["session_id"]
                },
                allowed_agents=["supervisor"],
                handler=self._placeholder_handler
            ),
            ToolDefinition(
                name="approval_check",
                description="Check if approval is required for decision",
                category=ToolCategory.WORKFLOW,
                parameters={
                    "type": "object",
                    "properties": {
                        "decision_type": {"type": "string", "description": "Type of decision"},
                        "amount": {"type": "number", "description": "Financial amount"}
                    },
                    "required": ["decision_type"]
                },
                allowed_agents=["all"],
                handler=self._placeholder_handler
            )
        ]
        
        # Register all default tools
        all_tools = sourcing_tools + compliance_tools + negotiation_tools + workflow_tools
        
        for tool in all_tools:
            self.register_tool(tool)
    
    def _placeholder_handler(self, **kwargs) -> Dict[str, Any]:
        """Placeholder handler for tools - will be implemented in Day 3."""
        return {
            "status": "placeholder",
            "message": "Tool handler will be implemented in Day 3",
            "parameters": kwargs
        }
    
    def export_tool_definitions(self) -> Dict[str, Any]:
        """Export tool definitions for MCP server configuration."""
        export_data = {
            "tools": {},
            "categories": [cat.value for cat in ToolCategory],
            "agent_permissions": {}
        }
        
        # Export tool definitions
        for name, tool in self.tools.items():
            export_data["tools"][name] = {
                "description": tool.description,
                "category": tool.category.value,
                "parameters": tool.parameters,
                "requires_approval": tool.requires_approval
            }
        
        # Export agent permissions
        for agent_role in ["sourcing", "compliance", "negotiation", "supervisor"]:
            agent_tools = [tool.name for tool in self.get_tools_for_agent(agent_role)]
            export_data["agent_permissions"][agent_role] = agent_tools
        
        return export_data