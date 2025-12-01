"""
Negotiation Agent - Autonomous Deal Optimization

This agent independently negotiates with suppliers and optimizes procurement deals
based on organizational objectives and market intelligence.
"""
import asyncio
from typing import Dict, Any, List
import random
from .agent_communication import BaseAgentV2, MessageType
from demo.system_integration import generate_recommendation
from memory.long_term_memory import get_memory
from memory.supplier_learning import get_learning_engine


class NegotiationAgent(BaseAgentV2):
    """Autonomous agent for procurement negotiation and deal optimization."""
    
    def __init__(self):
        super().__init__(agent_id="negotiation_agent", agent_type="negotiation")
        self.capabilities = ["price_negotiation", "contract_optimization", "deal_analysis"]
        
        # Agent's autonomous negotiation parameters
        self.negotiation_style = "collaborative"  # collaborative, competitive, adaptive
        self.target_savings = 0.15  # Target 15% savings
        self.acceptable_risk_level = "medium"
        
        # Connect to memory systems
        self.memory = get_memory()
        self.learning_engine = get_learning_engine()
        
    async def handle_request(self, message):
        """Handle negotiation requests autonomously."""
        request_type = message.content.get("request_type")
        
        if request_type == "negotiate_best_deal":
            await self._handle_deal_negotiation(message)
        elif request_type == "proceed_with_compliant_suppliers":
            await self._handle_compliant_suppliers(message)
        elif request_type == "optimize_contract":
            await self._handle_contract_optimization(message)
        else:
            await self.send_error_response(message, f"Unknown request type: {request_type}")
    
    async def _handle_compliant_suppliers(self, message):
        """Handle suppliers that passed compliance."""
        approved_suppliers = message.content.get("approved_suppliers", [])
        compliance_analysis = message.content.get("compliance_analysis", {})
        
        print(f"💼 {self.agent_id} starting autonomous negotiation with {len(approved_suppliers)} suppliers...")
        
        # Agent performs deal analysis and negotiation
        await self._negotiate_with_suppliers(message, approved_suppliers, compliance_analysis)
    
    async def _handle_deal_negotiation(self, message):
        """Handle direct negotiation requests."""
        suppliers = message.content.get("suppliers", [])
        
        print(f"💼 {self.agent_id} starting direct deal negotiation...")
        
        # Agent performs autonomous negotiation
        await self._negotiate_with_suppliers(message, suppliers, {})
    
    async def _negotiate_with_suppliers(self, original_message, suppliers, compliance_analysis):
        """Autonomous negotiation with suppliers."""
        
        # Agent analyzes suppliers using AI memory
        supplier_analysis = await self._analyze_suppliers_with_memory(suppliers)
        
        # Agent develops negotiation strategy
        strategy = self._develop_negotiation_strategy(suppliers, supplier_analysis, compliance_analysis)
        
        print(f"🧠 {self.agent_id} chose negotiation strategy: {strategy['approach']}")
        
        # Agent performs negotiation simulation
        negotiation_results = await self._simulate_negotiations(suppliers, strategy, supplier_analysis)
        
        # Agent makes final recommendation decision
        final_decision = self._make_final_recommendation(negotiation_results, strategy)
        
        # Agent decides next action
        await self._autonomous_completion(original_message, final_decision, negotiation_results)
    
    async def _analyze_suppliers_with_memory(self, suppliers):
        """Use AI memory to analyze supplier performance."""
        analysis = {}
        
        for supplier in suppliers:
            supplier_id = supplier.get('id')
            
            # Get historical performance from memory
            performance_record = self.memory.get_supplier_performance(supplier_id)
            
            if performance_record:
                # Generate AI scorecard
                scorecard = self.learning_engine.generate_supplier_scorecard(supplier_id)
                
                analysis[supplier_id] = {
                    "historical_orders": performance_record.total_orders,
                    "performance_score": scorecard.overall_score if scorecard else 75,
                    "delivery_score": scorecard.delivery_score if scorecard else 75,
                    "quality_score": scorecard.quality_score if scorecard else 75,
                    "risk_level": scorecard.risk_level if scorecard else "medium",
                    "negotiation_leverage": self._calculate_leverage(performance_record, scorecard)
                }
            else:
                # New supplier - conservative analysis
                analysis[supplier_id] = {
                    "historical_orders": 0,
                    "performance_score": 70,
                    "delivery_score": 70,
                    "quality_score": 70,
                    "risk_level": "medium",
                    "negotiation_leverage": "low"
                }
        
        return analysis
    
    def _calculate_leverage(self, performance_record, scorecard) -> str:
        """Calculate negotiation leverage based on supplier performance."""
        if not scorecard:
            return "low"
        
        if scorecard.overall_score > 90 and performance_record.total_orders > 10:
            return "high"  # Proven excellent supplier
        elif scorecard.overall_score < 70 or scorecard.risk_level == "high":
            return "high"  # Poor supplier, we have leverage
        else:
            return "medium"
    
    def _develop_negotiation_strategy(self, suppliers, supplier_analysis, compliance_analysis):
        """Agent develops autonomous negotiation strategy."""
        
        # Analyze market position
        supplier_count = len(suppliers)
        avg_performance = sum(analysis["performance_score"] for analysis in supplier_analysis.values()) / len(supplier_analysis)
        
        # Choose strategy based on analysis
        if supplier_count == 1:
            approach = "collaborative"  # Limited options, work together
        elif avg_performance > 85:
            approach = "competitive"  # Good suppliers, can be selective
        elif compliance_analysis.get("risk_assessment", {}).get("overall_risk") == "high":
            approach = "careful"  # High risk, prioritize safety
        else:
            approach = "balanced"
        
        return {
            "approach": approach,
            "target_savings": self.target_savings if approach == "competitive" else 0.08,
            "priority_factors": self._determine_priorities(suppliers, supplier_analysis),
            "fallback_plan": self._create_fallback_plan(suppliers)
        }
    
    def _determine_priorities(self, suppliers, supplier_analysis) -> List[str]:
        """Agent determines negotiation priorities."""
        priorities = ["price"]
        
        # Add priorities based on supplier analysis
        low_delivery_scores = [s for s, a in supplier_analysis.items() if a["delivery_score"] < 80]
        if low_delivery_scores:
            priorities.append("delivery_terms")
        
        low_quality_scores = [s for s, a in supplier_analysis.items() if a["quality_score"] < 80]
        if low_quality_scores:
            priorities.append("quality_guarantees")
        
        new_suppliers = [s for s, a in supplier_analysis.items() if a["historical_orders"] == 0]
        if new_suppliers:
            priorities.append("trial_period")
        
        return priorities
    
    def _create_fallback_plan(self, suppliers) -> str:
        """Agent creates fallback plan."""
        if len(suppliers) > 2:
            return "multi_supplier_split"
        elif len(suppliers) == 2:
            return "primary_backup_model"
        else:
            return "single_supplier_with_guarantees"
    
    async def _simulate_negotiations(self, suppliers, strategy, supplier_analysis):
        """Simulate autonomous negotiations with suppliers."""
        print(f"💰 {self.agent_id} simulating negotiations...")
        
        results = []
        
        for supplier in suppliers:
            supplier_id = supplier.get('id')
            supplier_name = supplier.get('name')
            analysis = supplier_analysis.get(supplier_id, {})
            
            # Simulate negotiation based on strategy and leverage
            negotiation_result = self._simulate_single_negotiation(
                supplier, analysis, strategy
            )
            
            results.append({
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "supplier": supplier,
                "analysis": analysis,
                "negotiation": negotiation_result
            })
            
            print(f"   💵 {supplier_name}: {negotiation_result['outcome']} - {negotiation_result['price_reduction']}% savings")
        
        return results
    
    def _simulate_single_negotiation(self, supplier, analysis, strategy):
        """Simulate negotiation with single supplier."""
        leverage = analysis.get("negotiation_leverage", "medium")
        performance_score = analysis.get("performance_score", 70)
        
        # Base success probability
        success_prob = 0.7
        
        # Adjust based on leverage
        if leverage == "high":
            success_prob += 0.2
        elif leverage == "low":
            success_prob -= 0.2
        
        # Adjust based on strategy
        if strategy["approach"] == "competitive":
            success_prob += 0.1
        elif strategy["approach"] == "collaborative":
            success_prob += 0.05
        
        # Simulate outcome
        success = random.random() < success_prob
        
        if success:
            # Calculate price reduction based on leverage and strategy
            base_reduction = strategy["target_savings"] * 100
            actual_reduction = base_reduction * (0.7 + random.random() * 0.6)  # 70-130% of target
            
            if leverage == "high":
                actual_reduction *= 1.3
            elif leverage == "low":
                actual_reduction *= 0.7
            
            return {
                "outcome": "successful",
                "price_reduction": round(actual_reduction, 1),
                "delivery_improvement": random.choice([0, 1, 2, 3]),  # days improved
                "additional_terms": self._generate_additional_terms(strategy),
                "confidence": 0.8 + random.random() * 0.2
            }
        else:
            return {
                "outcome": "no_agreement",
                "price_reduction": 0,
                "delivery_improvement": 0,
                "additional_terms": [],
                "confidence": 0.3 + random.random() * 0.3,
                "reason": "Supplier unwilling to meet terms"
            }
    
    def _generate_additional_terms(self, strategy):
        """Generate additional negotiated terms."""
        terms = []
        
        if "delivery_terms" in strategy["priority_factors"]:
            terms.append("Guaranteed delivery dates with penalties")
        
        if "quality_guarantees" in strategy["priority_factors"]:
            terms.append("Quality guarantee with replacement terms")
        
        if "trial_period" in strategy["priority_factors"]:
            terms.append("3-month trial period with performance review")
        
        return terms
    
    def _make_final_recommendation(self, negotiation_results, strategy):
        """Agent makes autonomous final recommendation."""
        
        # Filter successful negotiations
        successful_negotiations = [r for r in negotiation_results if r["negotiation"]["outcome"] == "successful"]
        
        if not successful_negotiations:
            return {
                "recommendation_type": "no_suitable_deals",
                "message": "Unable to negotiate acceptable terms with any supplier",
                "suggested_action": "Expand supplier search or adjust requirements"
            }
        
        # Rank by combined score (price savings + performance + confidence)
        def score_negotiation(result):
            negotiation = result["negotiation"]
            analysis = result["analysis"]
            
            price_score = negotiation["price_reduction"] * 2  # Weight price highly
            performance_score = analysis["performance_score"] * 0.5
            confidence_score = negotiation["confidence"] * 20
            
            return price_score + performance_score + confidence_score
        
        ranked_results = sorted(successful_negotiations, key=score_negotiation, reverse=True)
        top_choice = ranked_results[0]
        
        return {
            "recommendation_type": "successful_negotiation",
            "recommended_supplier": top_choice["supplier"],
            "negotiation_details": top_choice["negotiation"],
            "supplier_analysis": top_choice["analysis"],
            "estimated_savings": top_choice["negotiation"]["price_reduction"],
            "confidence": top_choice["negotiation"]["confidence"],
            "reasoning": self._generate_recommendation_reasoning(top_choice, strategy),
            "alternatives": ranked_results[1:3] if len(ranked_results) > 1 else []
        }
    
    def _generate_recommendation_reasoning(self, top_choice, strategy):
        """Generate reasoning for the recommendation."""
        supplier_name = top_choice["supplier"]["name"]
        savings = top_choice["negotiation"]["price_reduction"]
        performance = top_choice["analysis"]["performance_score"]
        
        reasoning = f"Selected {supplier_name} based on: "
        reasoning += f"{savings}% cost savings, "
        reasoning += f"{performance}% performance score, "
        reasoning += f"strong negotiation outcome with {len(top_choice['negotiation']['additional_terms'])} additional benefits"
        
        return reasoning
    
    async def _autonomous_completion(self, original_message, final_decision, negotiation_results):
        """Agent completes the procurement process autonomously."""
        
        if final_decision["recommendation_type"] == "successful_negotiation":
            # Success - send to supervisor for final approval
            await self.send_message(
                to_agent="supervisor_agent",
                content={
                    "request_type": "procurement_complete",
                    "final_recommendation": final_decision,
                    "negotiation_summary": self._create_negotiation_summary(negotiation_results),
                    "original_request": original_message.content,
                    "summary": f"Successfully negotiated {final_decision['estimated_savings']}% savings with {final_decision['recommended_supplier']['name']}"
                },
                conversation_id=original_message.conversation_id,
                message_type=MessageType.RESPONSE
            )
        else:
            # Failure - escalate to supervisor
            await self.send_message(
                to_agent="supervisor_agent",
                content={
                    "request_type": "negotiation_failure",
                    "failure_details": final_decision,
                    "negotiation_attempts": negotiation_results,
                    "original_request": original_message.content,
                    "summary": "Negotiation agent unable to secure acceptable deals"
                },
                conversation_id=original_message.conversation_id,
                message_type=MessageType.NOTIFICATION
            )
    
    def _create_negotiation_summary(self, negotiation_results):
        """Create summary of all negotiation attempts."""
        return {
            "total_suppliers_contacted": len(negotiation_results),
            "successful_negotiations": len([r for r in negotiation_results if r["negotiation"]["outcome"] == "successful"]),
            "average_savings_achieved": sum(r["negotiation"]["price_reduction"] for r in negotiation_results) / len(negotiation_results),
            "negotiation_strategy_used": self.negotiation_style
        }
    
    async def handle_response(self, message):
        """Handle responses from other agents."""
        if message.from_agent == "supervisor_agent":
            print(f"📨 {self.agent_id} received supervisor response")
            # Agent could learn from supervisor feedback to improve future negotiations