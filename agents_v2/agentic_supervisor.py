"""
Agentic Supervisor - Autonomous Workflow Orchestration

This supervisor doesn't control the workflow directly but rather facilitates
communication between autonomous agents and handles escalations.
"""
import asyncio
from typing import Dict, Any, List
import uuid
from .agent_communication import BaseAgentV2, MessageType, get_message_bus


class AgenticSupervisor(BaseAgentV2):
    """Supervisor that enables agent autonomy rather than controlling them."""
    
    def __init__(self):
        super().__init__(agent_id="supervisor_agent", agent_type="supervisor")
        self.capabilities = ["workflow_facilitation", "escalation_handling", "decision_arbitration"]
        
        # Track ongoing procurement conversations
        self.active_procurements = {}
        self.escalations = []
        
    async def initiate_procurement(self, request_data: Dict[str, Any]) -> str:
        """Initiate a procurement by starting the agent conversation."""
        conversation_id = str(uuid.uuid4())
        
        print(f"🎯 {self.agent_id} initiating autonomous procurement workflow")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Request: {request_data.get('item_description', 'Unknown item')}")
        
        # Track this procurement
        self.active_procurements[conversation_id] = {
            "status": "initiated",
            "request": request_data,
            "start_time": asyncio.get_event_loop().time(),
            "agents_involved": ["sourcing_agent"]
        }
        
        # Start the autonomous workflow by messaging the sourcing agent
        await self.send_message(
            to_agent="sourcing_agent",
            content={
                "request_type": "find_suppliers",
                "requirements": {
                    "category": request_data.get("category"),
                    "budget": request_data.get("budget"),
                    "quantity": request_data.get("quantity", 1),
                    "urgency": request_data.get("urgency", "medium")
                },
                "summary": f"New procurement request for {request_data.get('item_description')}"
            },
            conversation_id=conversation_id
        )
        
        return conversation_id
    
    async def handle_request(self, message):
        """Handle requests from other agents."""
        request_type = message.content.get("request_type")
        
        if request_type == "escalation":
            await self._handle_escalation(message)
        elif request_type == "compliance_escalation":
            await self._handle_compliance_escalation(message)
        elif request_type == "procurement_complete":
            await self._handle_procurement_completion(message)
        elif request_type == "negotiation_failure":
            await self._handle_negotiation_failure(message)
        else:
            print(f"🤔 {self.agent_id} received unhandled request: {request_type}")
    
    async def handle_response(self, message):
        """Handle responses from other agents."""
        print(f"📨 {self.agent_id} received response from {message.from_agent}")
        # ✅ ADD: Track all agents mentioned in conversation
        conv_id = message.conversation_id
        if conv_id in self.active_procurements:
            procurement = self.active_procurements[conv_id]
        
            # Add the responding agent
            if message.from_agent not in procurement["agents_involved"]:
                procurement["agents_involved"].append(message.from_agent)
        
            # ✅ NEW: Parse agent mentions from message flow
            self._extract_agents_from_message_history(conv_id)
    
        request_type = message.content.get("request_type")
    
        if request_type == "procurement_complete":
            await self._handle_procurement_completion(message)
        elif request_type == "expanded_search_complete":  
            await self._handle_expanded_search_completion(message)
        else:
            print(f"📨 {self.agent_id} received response: {message.content.get('summary', 'No summary')}")
    
    async def handle_notification(self, message):
        """Handle notifications from agents."""
        print(f"🔔 {self.agent_id} received notification from {message.from_agent}")
        
        # Update procurement status
        conv_id = message.conversation_id
        if conv_id in self.active_procurements:
            procurement = self.active_procurements[conv_id]
            
            # Add agent to involved list if not already there
            if message.from_agent not in procurement["agents_involved"]:
                procurement["agents_involved"].append(message.from_agent)
        
        # Handle specific notification types
        request_type = message.content.get("request_type")
        
        if request_type == "escalation":
            await self._handle_escalation(message)
        elif request_type == "compliance_escalation":
            await self._handle_compliance_escalation(message)
        elif request_type == "negotiation_failure":
            await self._handle_negotiation_failure(message)
    
    async def _handle_escalation(self, message):
        """Handle general escalations from agents."""
        print(f"🚨 {self.agent_id} handling escalation from {message.from_agent}")
        
        escalation = {
            "id": str(uuid.uuid4()),
            "from_agent": message.from_agent,
            "conversation_id": message.conversation_id,
            "issue": message.content.get("issue"),
            "recommendation": message.content.get("recommendation"),
            "status": "pending_human_review"
        }
        
        self.escalations.append(escalation)
        
        # In a real system, this would notify humans
        # For demo, supervisor makes autonomous decision
        decision = await self._make_escalation_decision(escalation, message)
        
        # Send guidance back to agent
        await self.send_message(
            to_agent=message.from_agent,
            content={
                "request_type": "escalation_guidance",
                "decision": decision,
                "guidance": decision.get("guidance"),
                "summary": f"Supervisor decision: {decision['action']}"
            },
            conversation_id=message.conversation_id,
            message_type=MessageType.RESPONSE
        )
    
    async def _make_escalation_decision(self, escalation, message):
        """Supervisor makes autonomous decision on escalations."""
        issue = escalation["issue"]
        
        if issue == "insufficient_suppliers_found":
            return {
                "action": "expand_search",
                "guidance": "Relax compliance requirements by 10 points and expand to adjacent categories",
                "rationale": "Business continuity requires finding viable suppliers"
            }
        elif issue == "high_risk_suppliers":
            return {
                "action": "proceed_with_caution",
                "guidance": "Accept medium-risk suppliers but require additional guarantees",
                "rationale": "Manageable risk with proper safeguards"
            }
        else:
            return {
                "action": "human_review_required",
                "guidance": "Escalate to human decision maker",
                "rationale": "Issue requires human judgment"
            }
    
    async def _handle_compliance_escalation(self, message):
        """Handle compliance-specific escalations."""
        print(f"📋 {self.agent_id} handling compliance escalation")
        
        compliance_results = message.content.get("compliance_results")
        agent_decision = message.content.get("agent_decision")
        
        # Supervisor reviews compliance agent's analysis
        if agent_decision["action"] == "escalate_for_review":
            # In real system, this would trigger human review
            # For demo, supervisor makes decision
            supervisor_decision = {
                "action": "override_approval",
                "rationale": "Risk is acceptable for business needs",
                "conditions": ["Additional monitoring required", "Quarterly performance review"]
            }
            
            # Send decision back to compliance agent
            await self.send_message(
                to_agent="compliance_agent",
                content={
                    "request_type": "supervisor_override",
                    "decision": supervisor_decision,
                    "approved_suppliers": compliance_results.get("approved", []),
                    "summary": "Supervisor approved with conditions"
                },
                conversation_id=message.conversation_id,
                message_type=MessageType.RESPONSE
            )
    
    async def _handle_procurement_completion(self, message):
        """Handle successful procurement completion."""
        print(f"✅ {self.agent_id} procurement completed successfully")
        
        final_recommendation = message.content.get("final_recommendation")
        conv_id = message.conversation_id
        
        if conv_id in self.active_procurements:
            procurement = self.active_procurements[conv_id]
            procurement["status"] = "completed"
            procurement["end_time"] = asyncio.get_event_loop().time()
            procurement["final_recommendation"] = final_recommendation
            procurement["outcome"] = "success"
            
            # Debug print to verify update
            print(f"DEBUG: Updated procurement status to: {procurement['status']}")
            print(f"DEBUG: Recommended supplier: {final_recommendation.get('recommended_supplier', {}).get('name', 'Unknown')}")
            
            duration = procurement["end_time"] - procurement["start_time"]
            print(f"   📊 Procurement completed in {duration:.2f} seconds")
            print(f"   💰 Achieved {final_recommendation.get('estimated_savings', 0)}% savings")
            print(f"   🤝 Selected: {final_recommendation.get('recommended_supplier', {}).get('name', 'Unknown')}")
    
    async def _handle_negotiation_failure(self, message):
        """Handle negotiation failures."""
        print(f"💔 {self.agent_id} handling negotiation failure")
        
        failure_details = message.content.get("failure_details")
        conv_id = message.conversation_id
        
        if conv_id in self.active_procurements:
            procurement = self.active_procurements[conv_id]
            procurement["status"] = "failed"
            procurement["end_time"] = asyncio.get_event_loop().time()
            procurement["failure_reason"] = failure_details.get("message")
            procurement["outcome"] = "failure"
        
        # Supervisor decides next action
        # Could restart with different agents, adjust requirements, etc.
        suggested_action = failure_details.get("suggested_action")
        
        if "expand supplier search" in suggested_action.lower():
            # Restart procurement with expanded criteria
            await self.send_message(
                to_agent="sourcing_agent",
                content={
                    "request_type": "expanded_search",
                    "original_request": message.content.get("original_request"),
                    "adjustments": ["expand_categories", "relax_compliance_10_percent"],
                    "summary": "Supervisor requesting expanded search after negotiation failure"
                },
                conversation_id=conv_id
            )
    async def _handle_expanded_search_completion(self, message):
        """Handle completion of expanded search."""
        result = message.content.get("result")
        conv_id = message.conversation_id
    
        if conv_id in self.active_procurements:
            procurement = self.active_procurements[conv_id]
        
            if result == "found_alternative_suppliers":
                # Success! Update status and complete procurement
                procurement["status"] = "completed"
                procurement["outcome"] = "success_via_expanded_search"
                procurement["supplier_count"] = message.content.get("supplier_count", 1)
                procurement["note"] = message.content.get("note", "Alternative suppliers found")
                procurement["end_time"] = asyncio.get_event_loop().time()
            
                duration = procurement["end_time"] - procurement["start_time"]
                print(f"✅ {self.agent_id} expanded search successful!")
                print(f"   📊 Recovery completed in {duration:.2f} seconds")
                print(f"   🔄 Found {procurement['supplier_count']} alternative suppliers")
            
            else:
                # Still failed, but update with better messaging
                procurement["status"] = "market_limitations"
                procurement["outcome"] = "failure_market_constraints"
                procurement["failure_reason"] = message.content.get("recommendation", "Market limitations identified")
                procurement["end_time"] = asyncio.get_event_loop().time()
            
                print(f"❌ {self.agent_id} expanded search confirms market limitations")
    
    def get_procurement_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get status of a specific procurement."""
        return self.active_procurements.get(conversation_id, {})
    
    def get_all_procurements(self) -> Dict[str, Any]:
        """Get status of all procurements."""
        return {
            "active_count": len([p for p in self.active_procurements.values() if p["status"] not in ["completed", "failed"]]),
            "completed_count": len([p for p in self.active_procurements.values() if p["status"] == "completed"]),
            "failed_count": len([p for p in self.active_procurements.values() if p["status"] == "failed"]),
            "procurements": self.active_procurements
        }
    
    def get_escalations(self) -> List[Dict[str, Any]]:
        """Get current escalations."""
        return self.escalations

    def _extract_agents_from_message_history(self, conv_id):
        """Extract all agents involved by looking at message history."""
        if hasattr(self, 'message_bus') and self.message_bus:
            conversation_messages = self.message_bus.get_conversation_history(conv_id)
        
            if conv_id in self.active_procurements:
                procurement = self.active_procurements[conv_id]
                agents_in_conversation = set(procurement["agents_involved"])
            
                # Add all agents from message history
                for msg in conversation_messages:
                    agents_in_conversation.add(msg.from_agent)
                    agents_in_conversation.add(msg.to_agent)
            
                # Remove supervisor from the list (it's not a "worker" agent)
                agents_in_conversation.discard("supervisor_agent")
            
                # Update the procurement record
                procurement["agents_involved"] = list(agents_in_conversation)