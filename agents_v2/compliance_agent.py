"""
Compliance Agent - Autonomous Policy Enforcement

This agent independently evaluates suppliers and procurement requests against
organizational policies, making autonomous decisions about compliance.
"""
import asyncio
from typing import Dict, Any, List
from .agent_communication import BaseAgentV2, MessageType
from demo.system_integration import load_system_data, check_compliance


class ComplianceAgent(BaseAgentV2):
    """Autonomous agent for compliance and policy enforcement."""
    
    def __init__(self):
        super().__init__(agent_id="compliance_agent", agent_type="compliance")
        self.capabilities = ["policy_enforcement", "risk_assessment", "regulatory_compliance"]
        
        # Load policy database
        _, self.policies_data, _ = load_system_data()
        
        # Agent's autonomous decision-making parameters
        self.risk_tolerance = "medium"  # Agent's risk appetite
        self.auto_approve_threshold = 90  # Agent can auto-approve high-score suppliers
        self.escalation_threshold = 50   # Agent escalates low-score suppliers
        
    async def handle_request(self, message):
        """Handle compliance requests autonomously."""
        request_type = message.content.get("request_type")
        
        if request_type == "check_compliance":
            await self._handle_compliance_check(message)
        elif request_type == "risk_assessment":
            await self._handle_risk_assessment(message)
        elif request_type == "policy_update":
            await self._handle_policy_update(message)
        else:
            await self.send_error_response(message, f"Unknown request type: {request_type}")
    
    async def _handle_compliance_check(self, message):
        """Autonomously perform compliance checking."""
        print(f"📋 {self.agent_id} starting autonomous compliance review...")
        
        suppliers = message.content.get("suppliers", [])
        requirements = message.content.get("requirements", {})
        
        # Agent performs comprehensive compliance analysis
        compliance_results = await self._autonomous_compliance_analysis(suppliers, requirements)
        
        # Agent makes autonomous decisions based on results
        decision = self._make_compliance_decision(compliance_results, requirements)
        
        print(f"🧠 {self.agent_id} decision: {decision['action']}")
        
        # Agent autonomously routes to next step
        await self._autonomous_routing(message, compliance_results, decision)
    
    async def _autonomous_compliance_analysis(self, suppliers, requirements):
        """Perform autonomous, comprehensive compliance analysis."""
        # Create a mock request object for the existing function
        mock_request = type('obj', (object,), {
            'budget': requirements.get('budget', 0),
            'category': requirements.get('category', ''),
            'urgency': requirements.get('urgency', 'medium')
        })
        
        # Use existing compliance logic but add agent intelligence
        base_results = check_compliance(mock_request, suppliers, self.policies_data)
        
        # Agent adds its own analysis layer
        enhanced_results = {
            **base_results,
            "risk_assessment": self._assess_risk_levels(suppliers, base_results),
            "agent_confidence": self._calculate_confidence(base_results),
            "alternative_suggestions": self._generate_alternatives(base_results)
        }
        
        return enhanced_results
    
    def _assess_risk_levels(self, suppliers, base_results) -> Dict[str, Any]:
        """Agent's autonomous risk assessment."""
        approved = base_results.get("approved", [])
        rejected = base_results.get("rejected", [])
        
        risk_levels = {
            "overall_risk": "low",
            "supplier_risks": {},
            "process_risks": []
        }
        
        # Assess individual supplier risks
        for supplier in approved:
            supplier_id = supplier.get('id')
            risk_score = 0
            
            # Financial risk
            if supplier.get('financial_rating', 'D') in ['C', 'C-', 'D']:
                risk_score += 2
            
            # Compliance risk
            if supplier.get('compliance_score', 100) < 85:
                risk_score += 2
            
            # Delivery risk
            if supplier.get('lead_time_days', 0) > 30:
                risk_score += 1
            
            risk_levels["supplier_risks"][supplier_id] = {
                "risk_score": risk_score,
                "risk_level": "high" if risk_score > 3 else "medium" if risk_score > 1 else "low"
            }
        
        # Overall risk calculation
        high_risk_count = sum(1 for risk in risk_levels["supplier_risks"].values() if risk["risk_level"] == "high")
        if high_risk_count > len(approved) * 0.5:
            risk_levels["overall_risk"] = "high"
        elif high_risk_count > 0:
            risk_levels["overall_risk"] = "medium"
        
        return risk_levels
    
    def _calculate_confidence(self, base_results) -> float:
        """Agent calculates its confidence in the compliance decision."""
        approved = base_results.get("approved", [])
        rejected = base_results.get("rejected", [])
        
        confidence = 0.8  # Base confidence
        
        # Higher confidence with more approved suppliers
        if len(approved) >= 3:
            confidence += 0.1
        elif len(approved) == 0:
            confidence -= 0.3
        
        # Higher confidence with clear policy violations
        for rejection in rejected:
            if "compliance_score" in rejection.get("reason", ""):
                confidence += 0.05
        
        return min(1.0, max(0.1, confidence))
    
    def _generate_alternatives(self, base_results) -> List[str]:
        """Agent generates alternative suggestions."""
        alternatives = []
        
        approved = base_results.get("approved", [])
        rejected = base_results.get("rejected", [])
        
        if len(approved) == 0:
            alternatives.append("Consider relaxing minimum compliance score requirements")
            alternatives.append("Expand search to additional supplier categories")
        
        if len(approved) < 2:
            alternatives.append("Recommend finding backup suppliers for risk mitigation")
        
        for rejection in rejected:
            if "certification" in rejection.get("reason", "").lower():
                alternatives.append("Consider suppliers with equivalent certifications")
        
        return alternatives
    
    def _make_compliance_decision(self, compliance_results, requirements) -> Dict[str, Any]:
        """Agent makes autonomous compliance decision."""
        approved = compliance_results.get("approved", [])
        risk_assessment = compliance_results.get("risk_assessment", {})
        confidence = compliance_results.get("agent_confidence", 0.5)
        
        # Agent's decision logic
        if len(approved) == 0:
            action = "reject_all_escalate"
        elif risk_assessment["overall_risk"] == "high" and confidence < 0.7:
            action = "escalate_for_review"
        elif len(approved) >= 2 and confidence > 0.8:
            action = "auto_approve"
        else:
            action = "conditional_approval"
        
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": self._generate_reasoning(action, compliance_results),
            "next_agent": self._decide_next_agent(action, requirements)
        }
    
    def _generate_reasoning(self, action: str, compliance_results) -> str:
        """Generate reasoning for the compliance decision."""
        approved_count = len(compliance_results.get("approved", []))
        risk_level = compliance_results.get("risk_assessment", {}).get("overall_risk", "unknown")
        
        reasoning_map = {
            "reject_all_escalate": f"No suppliers meet compliance requirements. Escalation needed.",
            "escalate_for_review": f"Found {approved_count} suppliers but risk level is {risk_level}. Human review recommended.",
            "auto_approve": f"Found {approved_count} compliant suppliers with acceptable risk levels. Proceeding autonomously.",
            "conditional_approval": f"Found {approved_count} suppliers. Proceeding with standard workflow."
        }
        
        return reasoning_map.get(action, "Standard compliance review completed.")
    
    def _decide_next_agent(self, action: str, requirements) -> str:
        """Agent decides which agent to route to next."""
        if action == "reject_all_escalate":
            return "supervisor_agent"
        elif action == "escalate_for_review":
            return "supervisor_agent"  # Human-in-the-loop
        elif requirements.get("urgency") == "high":
            return "negotiation_agent"  # Skip non-essential steps for urgent requests
        else:
            return "negotiation_agent"  # Standard flow
    
    async def _autonomous_routing(self, original_message, compliance_results, decision):
        """Agent autonomously routes to next step."""
        next_agent = decision["next_agent"]
        
        if next_agent == "supervisor_agent":
            # Escalation case
            await self.send_message(
                to_agent=next_agent,
                content={
                    "request_type": "compliance_escalation",
                    "compliance_results": compliance_results,
                    "agent_decision": decision,
                    "original_request": original_message.content,
                    "summary": f"Compliance agent escalating: {decision['reasoning']}"
                },
                conversation_id=original_message.conversation_id,
                message_type=MessageType.NOTIFICATION
            )
        else:
            # Continue to next agent
            await self.send_message(
                to_agent=next_agent,
                content={
                    "request_type": "proceed_with_compliant_suppliers",
                    "approved_suppliers": compliance_results.get("approved", []),
                    "compliance_analysis": compliance_results,
                    "agent_decision": decision,
                    "original_request": original_message.content,
                    "summary": f"Compliance approved {len(compliance_results.get('approved', []))} suppliers"
                },
                conversation_id=original_message.conversation_id
            )
    
    async def handle_response(self, message):
        """Handle responses from other agents."""
        if message.from_agent == "supervisor_agent":
            print(f"📨 {self.agent_id} received supervisor guidance")
            # Agent could adjust its risk tolerance based on supervisor feedback
            
        elif message.from_agent == "negotiation_agent":
            print(f"📨 {self.agent_id} received negotiation feedback")
            # Agent could learn from negotiation outcomes to adjust future compliance decisions