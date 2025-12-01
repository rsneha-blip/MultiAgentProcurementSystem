"""
Sourcing Agent - Autonomous Supplier Discovery

This agent independently finds and evaluates suppliers based on requirements,
communicating results to other agents without central orchestration.
"""
import asyncio
from typing import Dict, Any, List
from .agent_communication import BaseAgentV2, MessageType, get_message_bus
from demo.system_integration import load_system_data


class SourcingAgent(BaseAgentV2):
    """Autonomous agent for supplier sourcing and discovery."""
    
    def __init__(self):
        super().__init__(agent_id="sourcing_agent", agent_type="sourcing")
        self.capabilities = ["supplier_search", "supplier_evaluation", "market_analysis"]
        
        # Load supplier database
        self.suppliers_data, _, _ = load_system_data()
        
        # Agent's autonomous decision-making parameters
        self.confidence_threshold = 0.7
        self.max_suppliers_to_find = 5
        
    async def handle_request(self, message):
        """Handle procurement requests autonomously."""
        request_type = message.content.get("request_type")
        
        if request_type == "find_suppliers":
            await self._handle_supplier_search(message)
        elif request_type == "evaluate_supplier":
            await self._handle_supplier_evaluation(message)
        elif request_type == "expanded_search": 
            await self._handle_expanded_search(message)
        else:
            await self.send_error_response(message, f"Unknown request type: {request_type}")
    
    async def _handle_supplier_search(self, message):
        """Autonomously search for suppliers."""
        print(f"🔍 {self.agent_id} starting autonomous supplier search...")
        
        # Extract requirements
        requirements = message.content.get("requirements", {})
        category = requirements.get("category", "")
        budget = requirements.get("budget", 0)
        urgency = requirements.get("urgency", "medium")
        
        # Agent makes autonomous decision about search strategy
        search_strategy = self._decide_search_strategy(category, budget, urgency)
        print(f"🧠 {self.agent_id} chose search strategy: {search_strategy}")
        
        # Perform intelligent supplier search
        suppliers = self._intelligent_supplier_search(requirements, search_strategy)
        
        # Agent decides if results are good enough
        if self._evaluate_search_results(suppliers, requirements):
            print(f"✅ {self.agent_id} satisfied with {len(suppliers)} suppliers found")
            
            # Agent autonomously decides next step
            await self._autonomous_next_action(message, suppliers, requirements)
        else:
            print(f"⚠️ {self.agent_id} not satisfied with results, expanding search...")
            # Agent decides to expand search or escalate
            await self._handle_insufficient_results(message, requirements)

    async def _handle_expanded_search(self, message):
        """Handle expanded search with randomized success/failure."""
        print(f"🔍 {self.agent_id} handling expanded search with relaxed criteria...")

        adjustments = message.content.get("adjustments", [])
        print(f"🔧 {self.agent_id} applying adjustments: {adjustments}")

        # 30% chance expanded search finds alternative suppliers
        import random
        expanded_success = random.random() < 0.3
    
        if expanded_success:
            print(f"✅ {self.agent_id} found alternative suppliers with relaxed criteria!")
        
            # Simulate finding lower-tier but acceptable suppliers
            await self.send_message(
                to_agent="supervisor_agent",
                content={
                    "request_type": "expanded_search_complete",
                    "result": "found_alternative_suppliers",
                    "supplier_count": random.randint(1, 2),
                    "note": "Found suppliers with relaxed compliance requirements",
                    "summary": "Expanded search successful - found alternative suppliers"
                },
                conversation_id=message.conversation_id,
                message_type=MessageType.RESPONSE
            )
        else:
            print(f"❌ {self.agent_id} expanded search still found insufficient suppliers")
        
            await self.send_message(
                to_agent="supervisor_agent", 
                content={
                    "request_type": "expanded_search_complete",
                    "result": "insufficient_suppliers_in_market",
                    "recommendation": "Consider alternative procurement strategies or market research",
                    "summary": "Expanded search completed - market limitations identified"
                },
                conversation_id=message.conversation_id,
                message_type=MessageType.RESPONSE
            )
    
    def _decide_search_strategy(self, category: str, budget: float, urgency: str) -> str:
        """Agent autonomously decides search strategy."""
        if urgency == "high":
            return "fast_delivery_priority"
        elif budget > 100000:
            return "premium_suppliers_only"
        elif category in ["electronics", "manufacturing"]:
            return "specialized_suppliers"
        else:
            return "balanced_approach"
    
    def _intelligent_supplier_search(self, requirements: Dict[str, Any], strategy: str) -> List[Dict]:
        """Perform intelligent supplier search based on strategy."""
        category = requirements.get("category", "")
        budget = requirements.get("budget", 0)
        urgency = requirements.get("urgency", "medium")
        
        # Filter suppliers by category
        relevant_suppliers = []
        for supplier in self.suppliers_data['suppliers']:
            capabilities = supplier.get('capabilities', [])
            if category in capabilities or any(cap in category for cap in capabilities):
                relevant_suppliers.append(supplier)
        
        # Apply strategy-based filtering
        if strategy == "fast_delivery_priority":
            relevant_suppliers = [s for s in relevant_suppliers if s.get('lead_time_days', 30) <= 10]
        elif strategy == "premium_suppliers_only":
            relevant_suppliers = [s for s in relevant_suppliers if s.get('pricing_tier') == 'premium']
        elif strategy == "specialized_suppliers":
            relevant_suppliers = [s for s in relevant_suppliers if s.get('compliance_score', 0) >= 90]
        
        # Sort by agent's autonomous ranking algorithm
        ranked_suppliers = self._rank_suppliers(relevant_suppliers, requirements, strategy)
        
        return ranked_suppliers[:self.max_suppliers_to_find]
    
    def _rank_suppliers(self, suppliers: List[Dict], requirements: Dict, strategy: str) -> List[Dict]:
        """Agent's autonomous supplier ranking algorithm."""
        urgency = requirements.get("urgency", "medium")
        budget_per_unit = requirements.get("budget", 0) / max(requirements.get("quantity", 1), 1)
        
        def supplier_score(supplier):
            score = supplier.get('compliance_score', 70)
            
            # Adjust based on strategy
            if strategy == "fast_delivery_priority":
                score += max(0, (30 - supplier.get('lead_time_days', 30)) * 2)
            elif strategy == "premium_suppliers_only":
                if supplier.get('pricing_tier') == 'premium':
                    score += 20
            
            # Budget compatibility
            if budget_per_unit > 50 and supplier.get('pricing_tier') in ['budget', 'mid-range']:
                score -= 10
            
            return score
        
        return sorted(suppliers, key=supplier_score, reverse=True)
    
    def _evaluate_search_results(self, suppliers: List[Dict], requirements: Dict) -> bool:
        """Agent evaluates if search results meet its standards."""
        if len(suppliers) == 0:
            return False
        
        # Check if at least one supplier meets minimum standards
        for supplier in suppliers:
            if supplier.get('compliance_score', 0) >= 75:
                return True
        
        return False
    
    async def _autonomous_next_action(self, original_message, suppliers, requirements):
        """Agent autonomously decides what to do next."""
        # Agent decides: should we go to compliance or directly to negotiation?
        if requirements.get("urgency") == "high" and len(suppliers) == 1:
            # Agent chooses to skip compliance for urgent requests
            print(f"🚀 {self.agent_id} autonomously choosing fast-track for urgent request")
            await self._send_to_negotiation(original_message, suppliers)
        else:
            # Agent chooses standard compliance check
            print(f"📋 {self.agent_id} autonomously routing to compliance check")
            await self._send_to_compliance(original_message, suppliers, requirements)
    
    async def _send_to_compliance(self, original_message, suppliers, requirements):
        """Send suppliers to compliance agent."""
        await self.send_message(
            to_agent="compliance_agent",
            content={
                "request_type": "check_compliance",
                "suppliers": suppliers,
                "requirements": requirements,
                "original_request": original_message.content,
                "summary": f"Found {len(suppliers)} suppliers for compliance review"
            },
            conversation_id=original_message.conversation_id
        )
    
    async def _send_to_negotiation(self, original_message, suppliers):
        """Send directly to negotiation (autonomous fast-track)."""
        await self.send_message(
            to_agent="negotiation_agent",
            content={
                "request_type": "negotiate_best_deal",
                "suppliers": suppliers,
                "original_request": original_message.content,
                "summary": f"Fast-track {len(suppliers)} suppliers for negotiation"
            },
            conversation_id=original_message.conversation_id
        )
    
    async def _handle_insufficient_results(self, original_message, requirements):
        """Handle case where search results are insufficient."""
        # Agent decides to either expand search or escalate to supervisor
        await self.send_message(
            to_agent="supervisor_agent",
            content={
                "request_type": "escalation",
                "issue": "insufficient_suppliers_found",
                "requirements": requirements,
                "recommendation": "Consider relaxing requirements or expanding search criteria",
                "summary": "Sourcing agent needs guidance on requirement adjustment"
            },
            conversation_id=original_message.conversation_id,
            message_type=MessageType.NOTIFICATION
        )
    
    async def handle_response(self, message):
        """Handle responses from other agents."""
        if message.from_agent == "compliance_agent":
            print(f"📨 {self.agent_id} received compliance results")
            # Agent could decide to find alternative suppliers if many were rejected
            
        elif message.from_agent == "negotiation_agent":
            print(f"📨 {self.agent_id} received negotiation results")
            # Agent could provide additional supplier options if negotiation failed