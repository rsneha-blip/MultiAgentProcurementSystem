"""
MCP Server Implementation for Procurement Agent Tools

Provides the Model Context Protocol server that exposes tools to agents
with proper security controls and access management.
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import get_settings
from .tools.registry import ToolRegistry


class MCPServer:
    """Model Context Protocol server for procurement tools."""
    
    def __init__(self):
        """Initialize MCP server."""
        self.settings = get_settings()
        self.tool_registry = ToolRegistry()
        self.logger = logging.getLogger("mcp.server")
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.server_running = False
    
    async def start_server(self, host: str = None, port: int = None) -> bool:
        """
        Start the MCP server.
        
        Args:
            host: Server host (defaults to config)
            port: Server port (defaults to config)
            
        Returns:
            bool: Success status
        """
        try:
            server_host = host or self.settings.mcp_server_host
            server_port = port or self.settings.mcp_server_port
            
            if self.settings.debug_mode:
                self.logger.info(f"Starting MCP server on {server_host}:{server_port}")
            
            # In a real implementation, this would start an actual HTTP/WebSocket server
            # For the capstone project, we'll simulate server startup
            self.server_running = True
            
            # Log available tools
            tool_count = len(self.tool_registry.list_all_tools())
            self.logger.info(f"MCP server started with {tool_count} tools available")
            
            if self.settings.debug_mode:
                self._log_tool_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {str(e)}")
            return False
    
    async def stop_server(self) -> bool:
        """Stop the MCP server."""
        try:
            self.server_running = False
            self.active_connections.clear()
            self.logger.info("MCP server stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping MCP server: {str(e)}")
            return False
    
    def register_agent_connection(self, agent_role: str, connection_id: str) -> bool:
        """
        Register an agent connection.
        
        Args:
            agent_role: Role of the connecting agent
            connection_id: Unique connection identifier
            
        Returns:
            bool: Success status
        """
        if not self.server_running:
            return False
        
        try:
            self.active_connections[connection_id] = {
                "agent_role": agent_role,
                "connected_at": datetime.utcnow(),
                "tools_accessed": []
            }
            
            if self.settings.debug_mode:
                available_tools = [tool.name for tool in self.tool_registry.get_tools_for_agent(agent_role)]
                self.logger.info(f"Agent {agent_role} connected with access to {len(available_tools)} tools")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent connection: {str(e)}")
            return False
    
    def get_available_tools(self, agent_role: str) -> List[Dict[str, Any]]:
        """
        Get tools available to a specific agent.
        
        Args:
            agent_role: Role of the requesting agent
            
        Returns:
            List of tool definitions
        """
        if not self.server_running:
            return []
        
        tools = self.tool_registry.get_tools_for_agent(agent_role)
        
        # Convert to MCP format
        tool_definitions = []
        for tool in tools:
            tool_def = {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters,
                "category": tool.category.value,
                "requiresApproval": tool.requires_approval
            }
            tool_definitions.append(tool_def)
        
        return tool_definitions
    
    async def call_tool(self, agent_role: str, connection_id: str, tool_name: str, 
                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool call request from agent.
        
        Args:
            agent_role: Role of the calling agent
            connection_id: Connection identifier
            tool_name: Name of tool to call
            parameters: Tool parameters
            
        Returns:
            Dict with tool call results
        """
        try:
            # Validate connection
            if connection_id not in self.active_connections:
                return {"error": "Invalid connection", "status": "unauthorized"}
            
            # Check tool access
            if not self.tool_registry.can_agent_access_tool(agent_role, tool_name):
                return {"error": f"Agent {agent_role} cannot access tool {tool_name}", "status": "forbidden"}
            
            # Get tool definition
            tool_def = self.tool_registry.get_tool(tool_name)
            if not tool_def:
                return {"error": f"Tool {tool_name} not found", "status": "not_found"}
            
            # Log tool access
            self.active_connections[connection_id]["tools_accessed"].append({
                "tool": tool_name,
                "timestamp": datetime.utcnow(),
                "parameters": parameters
            })
            
            if self.settings.debug_mode:
                self.logger.info(f"Agent {agent_role} calling tool {tool_name}")
            
            # Check if approval is required
            if tool_def.requires_approval:
                return await self._handle_approval_required(agent_role, tool_name, parameters)
            
            # Execute tool
            result = await self._execute_tool(tool_def, parameters)
            
            return {
                "status": "success",
                "result": result,
                "tool": tool_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e), "status": "execution_error"}
    
    async def _execute_tool(self, tool_def, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with given parameters."""
        try:
            # For Day 1, we're using placeholder handlers
            # In Day 3, these will be replaced with actual tool implementations
            if asyncio.iscoroutinefunction(tool_def.handler):
                result = await tool_def.handler(**parameters)
            else:
                result = tool_def.handler(**parameters)
            
            return result
            
        except Exception as e:
            raise Exception(f"Tool execution failed: {str(e)}")
    
    async def _handle_approval_required(self, agent_role: str, tool_name: str, 
                                      parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools that require approval."""
        return {
            "status": "approval_required",
            "message": f"Tool {tool_name} requires approval before execution",
            "approval_request": {
                "agent": agent_role,
                "tool": tool_name,
                "parameters": parameters,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics and status."""
        tool_stats = {}
        for connection in self.active_connections.values():
            for tool_access in connection.get("tools_accessed", []):
                tool_name = tool_access["tool"]
                tool_stats[tool_name] = tool_stats.get(tool_name, 0) + 1
        
        return {
            "server_running": self.server_running,
            "active_connections": len(self.active_connections),
            "registered_tools": len(self.tool_registry.list_all_tools()),
            "tool_usage_stats": tool_stats,
            "uptime": "simulated" if self.server_running else "stopped"
        }
    
    def _log_tool_summary(self):
        """Log summary of available tools for debugging."""
        self.logger.info("=== MCP Server Tool Summary ===")
        
        for category in ["sourcing", "compliance", "negotiation", "workflow"]:
            tools = [tool.name for tool in self.tool_registry.get_tools_by_category(category)]
            self.logger.info(f"{category.title()}: {', '.join(tools)}")
        
        self.logger.info("=== Agent Permissions ===")
        for agent in ["sourcing", "compliance", "negotiation", "supervisor"]:
            tool_names = [tool.name for tool in self.tool_registry.get_tools_for_agent(agent)]
            self.logger.info(f"{agent}: {len(tool_names)} tools available")