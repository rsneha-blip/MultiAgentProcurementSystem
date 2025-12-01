"""
Long-term Memory System - Persistent Learning Across Sessions

Stores and retrieves organizational knowledge, supplier performance history,
and procurement patterns to improve decision-making over time.
"""
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
import statistics

from config.settings import get_settings


@dataclass
class SupplierPerformanceRecord:
    """Historical performance record for a supplier."""
    supplier_id: str
    supplier_name: str
    
    # Performance metrics
    total_orders: int = 0
    successful_orders: int = 0
    total_value: float = 0.0
    
    # Delivery metrics
    delivery_times: List[float] = field(default_factory=list)  # In days
    on_time_deliveries: int = 0
    late_deliveries: int = 0
    
    # Quality metrics
    quality_scores: List[float] = field(default_factory=list)  # 1-5 scale
    defect_rate: float = 0.0
    return_rate: float = 0.0
    
    # Compliance metrics
    compliance_violations: int = 0
    audit_scores: List[float] = field(default_factory=list)
    
    # Financial metrics
    payment_terms_honored: int = 0
    pricing_competitiveness: List[float] = field(default_factory=list)
    negotiation_flexibility: float = 0.0  # 0-1 scale
    
    # Relationship metrics
    communication_quality: float = 0.0  # 1-5 scale
    responsiveness: float = 0.0  # Response time in hours
    
    # Temporal data
    first_order_date: Optional[datetime] = None
    last_order_date: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_order_outcome(self, success: bool, value: float, delivery_days: float,
                         quality_score: float = None, on_time: bool = True) -> None:
        """Record an order outcome."""
        self.total_orders += 1
        if success:
            self.successful_orders += 1
        
        self.total_value += value
        self.delivery_times.append(delivery_days)
        
        if on_time:
            self.on_time_deliveries += 1
        else:
            self.late_deliveries += 1
        
        if quality_score:
            self.quality_scores.append(quality_score)
        
        self.last_order_date = datetime.utcnow()
        if not self.first_order_date:
            self.first_order_date = datetime.utcnow()
        
        self.last_updated = datetime.utcnow()
    
    def get_success_rate(self) -> float:
        """Get order success rate."""
        return self.successful_orders / self.total_orders if self.total_orders > 0 else 0.0
    
    def get_avg_delivery_time(self) -> float:
        """Get average delivery time in days."""
        return statistics.mean(self.delivery_times) if self.delivery_times else 0.0
    
    def get_on_time_rate(self) -> float:
        """Get on-time delivery rate."""
        total_deliveries = self.on_time_deliveries + self.late_deliveries
        return self.on_time_deliveries / total_deliveries if total_deliveries > 0 else 0.0
    
    def get_avg_quality_score(self) -> float:
        """Get average quality score."""
        return statistics.mean(self.quality_scores) if self.quality_scores else 0.0
    
    def get_performance_score(self) -> float:
        """Calculate composite performance score (0-100)."""
        if self.total_orders == 0:
            return 0.0
        
        # Weight different factors
        success_weight = 0.3
        delivery_weight = 0.25
        quality_weight = 0.25
        compliance_weight = 0.2
        
        # Calculate component scores
        success_score = self.get_success_rate() * 100
        
        # Delivery score (on-time rate)
        delivery_score = self.get_on_time_rate() * 100
        
        # Quality score (1-5 scale to 0-100)
        avg_quality = self.get_avg_quality_score()
        quality_score = (avg_quality / 5.0 * 100) if avg_quality > 0 else 50
        
        # Compliance score (inverse of violations)
        violation_rate = self.compliance_violations / self.total_orders
        compliance_score = max(0, 100 - (violation_rate * 100))
        
        # Weighted average
        composite_score = (
            success_score * success_weight +
            delivery_score * delivery_weight +
            quality_score * quality_weight +
            compliance_score * compliance_weight
        )
        
        return round(composite_score, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        
        # Add computed metrics
        data.update({
            "success_rate": self.get_success_rate(),
            "avg_delivery_time": self.get_avg_delivery_time(),
            "on_time_rate": self.get_on_time_rate(),
            "avg_quality_score": self.get_avg_quality_score(),
            "performance_score": self.get_performance_score()
        })
        
        # Convert datetime objects
        if self.first_order_date:
            data["first_order_date"] = self.first_order_date.isoformat()
        if self.last_order_date:
            data["last_order_date"] = self.last_order_date.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        
        return data


@dataclass
class ProcurementPattern:
    """Identified procurement pattern."""
    pattern_id: str
    pattern_type: str  # "seasonal", "category", "supplier", "workflow"
    description: str
    
    # Pattern data
    trigger_conditions: Dict[str, Any]
    common_outcomes: Dict[str, Any]
    success_factors: List[str]
    risk_factors: List[str]
    
    # Statistics
    occurrence_count: int = 0
    success_rate: float = 0.0
    avg_duration_days: float = 0.0
    avg_cost: float = 0.0
    
    # Temporal info
    first_observed: datetime = field(default_factory=datetime.utcnow)
    last_observed: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0  # 0-1 scale
    
    def update_statistics(self, success: bool, duration_days: float, cost: float) -> None:
        """Update pattern statistics with new observation."""
        self.occurrence_count += 1
        
        # Update success rate
        if self.occurrence_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            # Running average
            current_successes = self.success_rate * (self.occurrence_count - 1)
            if success:
                current_successes += 1
            self.success_rate = current_successes / self.occurrence_count
        
        # Update duration (running average)
        if self.occurrence_count == 1:
            self.avg_duration_days = duration_days
        else:
            total_duration = self.avg_duration_days * (self.occurrence_count - 1)
            self.avg_duration_days = (total_duration + duration_days) / self.occurrence_count
        
        # Update cost (running average)
        if self.occurrence_count == 1:
            self.avg_cost = cost
        else:
            total_cost = self.avg_cost * (self.occurrence_count - 1)
            self.avg_cost = (total_cost + cost) / self.occurrence_count
        
        # Update confidence (more observations = higher confidence, up to 1.0)
        self.confidence_score = min(1.0, self.occurrence_count / 10.0)
        
        self.last_observed = datetime.utcnow()


class LongTermMemory:
    """Long-term memory system for procurement knowledge."""
    
    def __init__(self):
        """Initialize long-term memory system."""
        self.settings = get_settings()
        
        # Supplier performance tracking
        self.supplier_records: Dict[str, SupplierPerformanceRecord] = {}
        
        # Procurement patterns
        self.patterns: Dict[str, ProcurementPattern] = {}
        
        # Organizational preferences
        self.org_preferences = {
            "preferred_suppliers": {},  # category -> list of supplier_ids
            "avoided_suppliers": {},    # supplier_id -> reason
            "policy_adaptations": {},   # policy_type -> adjustments
            "workflow_optimizations": {},  # step -> optimization
            "budget_patterns": {},      # category -> typical budgets
            "seasonal_trends": {}       # category -> seasonal multipliers
        }
        
        # Decision history for learning
        self.decision_history: deque = deque(maxlen=1000)
        
        # Performance metrics
        self.memory_stats = {
            "total_suppliers_tracked": 0,
            "total_patterns_identified": 0,
            "total_decisions_recorded": 0,
            "memory_effectiveness_score": 0.0
        }
    
    def record_supplier_performance(self, supplier_id: str, supplier_name: str,
                                  order_data: Dict[str, Any]) -> None:
        """
        Record supplier performance data from completed procurement.
        
        Args:
            supplier_id: Unique supplier identifier
            supplier_name: Supplier name
            order_data: Dictionary containing order outcome data
        """
        if supplier_id not in self.supplier_records:
            self.supplier_records[supplier_id] = SupplierPerformanceRecord(
                supplier_id=supplier_id,
                supplier_name=supplier_name
            )
        
        record = self.supplier_records[supplier_id]
        
        # Extract order data
        success = order_data.get("success", True)
        value = order_data.get("value", 0.0)
        delivery_days = order_data.get("delivery_days", 0.0)
        quality_score = order_data.get("quality_score")
        on_time = order_data.get("on_time", True)
        
        record.add_order_outcome(success, value, delivery_days, quality_score, on_time)
        
        # Update additional metrics if provided
        if "compliance_violation" in order_data and order_data["compliance_violation"]:
            record.compliance_violations += 1
        
        if "communication_quality" in order_data:
            record.communication_quality = order_data["communication_quality"]
        
        if "responsiveness_hours" in order_data:
            record.responsiveness = order_data["responsiveness_hours"]
        
        self.memory_stats["total_suppliers_tracked"] = len(self.supplier_records)
    
    def get_supplier_performance(self, supplier_id: str) -> Optional[SupplierPerformanceRecord]:
        """Get performance record for a supplier."""
        return self.supplier_records.get(supplier_id)
    
    def get_supplier_recommendations(self, category: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get supplier recommendations based on historical performance.
        
        Args:
            category: Procurement category
            requirements: Specific requirements
            
        Returns:
            List of recommended suppliers with performance data
        """
        recommendations = []
        
        # Get minimum requirements
        min_performance_score = requirements.get("min_performance_score", 70.0)
        max_delivery_days = requirements.get("max_delivery_days", 30.0)
        min_success_rate = requirements.get("min_success_rate", 0.9)
        
        for supplier_id, record in self.supplier_records.items():
            # Apply filters
            if record.get_performance_score() < min_performance_score:
                continue
            
            if record.get_avg_delivery_time() > max_delivery_days:
                continue
            
            if record.get_success_rate() < min_success_rate:
                continue
            
            # Calculate recommendation score
            recommendation_score = self._calculate_recommendation_score(record, requirements)
            
            recommendation = {
                "supplier_id": supplier_id,
                "supplier_name": record.supplier_name,
                "performance_score": record.get_performance_score(),
                "success_rate": record.get_success_rate(),
                "avg_delivery_time": record.get_avg_delivery_time(),
                "on_time_rate": record.get_on_time_rate(),
                "avg_quality_score": record.get_avg_quality_score(),
                "total_orders": record.total_orders,
                "recommendation_score": recommendation_score,
                "recommendation_reasons": self._get_recommendation_reasons(record, requirements)
            }
            
            recommendations.append(recommendation)
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return recommendations
    
    def record_procurement_decision(self, decision_data: Dict[str, Any]) -> None:
        """
        Record a procurement decision for pattern learning.
        
        Args:
            decision_data: Dictionary containing decision information
        """
        decision_record = {
            "timestamp": datetime.utcnow(),
            "session_id": decision_data.get("session_id"),
            "category": decision_data.get("category"),
            "budget": decision_data.get("budget"),
            "urgency": decision_data.get("urgency"),
            "selected_supplier": decision_data.get("selected_supplier"),
            "decision_factors": decision_data.get("decision_factors", []),
            "outcome_success": decision_data.get("outcome_success"),
            "outcome_cost": decision_data.get("outcome_cost"),
            "outcome_duration": decision_data.get("outcome_duration")
        }
        
        self.decision_history.append(decision_record)
        self.memory_stats["total_decisions_recorded"] = len(self.decision_history)
        
        # Analyze for patterns
        self._analyze_decision_patterns(decision_record)
    
    def identify_procurement_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns in procurement decisions."""
        patterns_summary = []
        
        for pattern_id, pattern in self.patterns.items():
            if pattern.confidence_score > 0.5:  # Only include confident patterns
                patterns_summary.append({
                    "pattern_id": pattern_id,
                    "type": pattern.pattern_type,
                    "description": pattern.description,
                    "occurrence_count": pattern.occurrence_count,
                    "success_rate": pattern.success_rate,
                    "confidence_score": pattern.confidence_score,
                    "avg_cost": pattern.avg_cost,
                    "avg_duration_days": pattern.avg_duration_days,
                    "success_factors": pattern.success_factors,
                    "risk_factors": pattern.risk_factors
                })
        
        return sorted(patterns_summary, key=lambda x: x["confidence_score"], reverse=True)
    
    def get_organizational_insights(self) -> Dict[str, Any]:
        """Get insights about organizational procurement patterns."""
        if not self.decision_history:
            return {"message": "Insufficient data for insights"}
        
        decisions = list(self.decision_history)
        
        # Category analysis
        category_stats = defaultdict(lambda: {"count": 0, "total_cost": 0, "successes": 0})
        for decision in decisions:
            category = decision.get("category", "unknown")
            category_stats[category]["count"] += 1
            if decision.get("outcome_cost"):
                category_stats[category]["total_cost"] += decision["outcome_cost"]
            if decision.get("outcome_success"):
                category_stats[category]["successes"] += 1
        
        # Supplier preference analysis
        supplier_usage = defaultdict(int)
        for decision in decisions:
            supplier = decision.get("selected_supplier")
            if supplier:
                supplier_usage[supplier] += 1
        
        # Budget analysis
        budget_ranges = {"<5K": 0, "5K-25K": 0, "25K-100K": 0, ">100K": 0}
        for decision in decisions:
            budget = decision.get("budget", 0)
            if budget < 5000:
                budget_ranges["<5K"] += 1
            elif budget < 25000:
                budget_ranges["5K-25K"] += 1
            elif budget < 100000:
                budget_ranges["25K-100K"] += 1
            else:
                budget_ranges[">100K"] += 1
        
        return {
            "total_decisions_analyzed": len(decisions),
            "category_breakdown": dict(category_stats),
            "top_suppliers": dict(sorted(supplier_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
            "budget_distribution": budget_ranges,
            "patterns_identified": len([p for p in self.patterns.values() if p.confidence_score > 0.5]),
            "memory_effectiveness": self._calculate_memory_effectiveness()
        }
    
    def update_organizational_preferences(self, category: str, preferences: Dict[str, Any]) -> None:
        """Update organizational preferences for a category."""
        if "preferred_suppliers" in preferences:
            self.org_preferences["preferred_suppliers"][category] = preferences["preferred_suppliers"]
        
        if "budget_guidelines" in preferences:
            self.org_preferences["budget_patterns"][category] = preferences["budget_guidelines"]
        
        if "seasonal_adjustments" in preferences:
            self.org_preferences["seasonal_trends"][category] = preferences["seasonal_adjustments"]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory system summary."""
        # Top performing suppliers
        top_suppliers = sorted(
            [(sid, record) for sid, record in self.supplier_records.items()],
            key=lambda x: x[1].get_performance_score(),
            reverse=True
        )[:5]
        
        # Recent patterns
        recent_patterns = [
            pattern for pattern in self.patterns.values()
            if (datetime.utcnow() - pattern.last_observed).days <= 30
        ]
        
        return {
            "memory_statistics": self.memory_stats.copy(),
            "supplier_performance": {
                "total_suppliers": len(self.supplier_records),
                "top_performers": [
                    {
                        "supplier_id": sid,
                        "name": record.supplier_name,
                        "performance_score": record.get_performance_score(),
                        "total_orders": record.total_orders
                    }
                    for sid, record in top_suppliers
                ]
            },
            "pattern_analysis": {
                "total_patterns": len(self.patterns),
                "confident_patterns": len([p for p in self.patterns.values() if p.confidence_score > 0.7]),
                "recent_patterns": len(recent_patterns)
            },
            "organizational_learning": {
                "preferred_suppliers_by_category": len(self.org_preferences["preferred_suppliers"]),
                "policy_adaptations": len(self.org_preferences["policy_adaptations"]),
                "workflow_optimizations": len(self.org_preferences["workflow_optimizations"])
            }
        }
    
    def _calculate_recommendation_score(self, record: SupplierPerformanceRecord, 
                                      requirements: Dict[str, Any]) -> float:
        """Calculate recommendation score for a supplier."""
        base_score = record.get_performance_score()
        
        # Adjust based on requirements
        if "urgency" in requirements and requirements["urgency"] == "high":
            # Prioritize fast delivery
            delivery_bonus = max(0, (30 - record.get_avg_delivery_time()) / 30 * 20)
            base_score += delivery_bonus
        
        if "quality_critical" in requirements and requirements["quality_critical"]:
            # Prioritize quality
            quality_bonus = record.get_avg_quality_score() / 5.0 * 20
            base_score += quality_bonus
        
        # Experience bonus (more orders = more reliable)
        experience_bonus = min(10, record.total_orders / 10)
        base_score += experience_bonus
        
        return min(100, base_score)
    
    def _get_recommendation_reasons(self, record: SupplierPerformanceRecord,
                                  requirements: Dict[str, Any]) -> List[str]:
        """Get reasons for recommending a supplier."""
        reasons = []
        
        if record.get_performance_score() >= 90:
            reasons.append("Excellent overall performance score")
        
        if record.get_on_time_rate() >= 0.95:
            reasons.append("Consistently on-time deliveries")
        
        if record.get_avg_quality_score() >= 4.5:
            reasons.append("High quality ratings")
        
        if record.total_orders >= 10:
            reasons.append("Proven track record with multiple orders")
        
        if record.compliance_violations == 0:
            reasons.append("Perfect compliance record")
        
        return reasons
    
    def _analyze_decision_patterns(self, new_decision: Dict[str, Any]) -> None:
        """Analyze new decision for patterns."""
        # Example pattern analysis - could be made more sophisticated
        category = new_decision.get("category")
        budget = new_decision.get("budget", 0)
        urgency = new_decision.get("urgency", "medium")
        
        # Budget-category pattern
        pattern_id = f"budget_pattern_{category}"
        if pattern_id not in self.patterns:
            self.patterns[pattern_id] = ProcurementPattern(
                pattern_id=pattern_id,
                pattern_type="budget",
                description=f"Budget patterns for {category} procurement",
                trigger_conditions={"category": category},
                common_outcomes={},
                success_factors=[],
                risk_factors=[]
            )
        
        # Update pattern with new observation
        success = new_decision.get("outcome_success", True)
        duration = new_decision.get("outcome_duration", 0)
        cost = new_decision.get("outcome_cost", budget)
        
        self.patterns[pattern_id].update_statistics(success, duration, cost)
    
    def _calculate_memory_effectiveness(self) -> float:
        """Calculate how effective the memory system is."""
        if not self.decision_history:
            return 0.0
        
        # Simple effectiveness calculation based on:
        # - Number of suppliers with performance data
        # - Confidence in identified patterns
        # - Data completeness
        
        supplier_coverage = min(1.0, len(self.supplier_records) / 10)  # Target: 10 suppliers
        pattern_confidence = statistics.mean([p.confidence_score for p in self.patterns.values()]) if self.patterns else 0.0
        data_completeness = min(1.0, len(self.decision_history) / 100)  # Target: 100 decisions
        
        effectiveness = (supplier_coverage * 0.4 + pattern_confidence * 0.3 + data_completeness * 0.3) * 100
        
        return round(effectiveness, 1)


# Global memory instance
_memory_instance = None

def get_memory() -> LongTermMemory:
    """Get the global long-term memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = LongTermMemory()
    return _memory_instance