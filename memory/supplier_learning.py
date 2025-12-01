"""
Supplier Learning Engine - AI-Powered Supplier Performance Analysis

Uses machine learning techniques to analyze supplier patterns,
predict performance, and provide intelligent recommendations.
"""
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

from .long_term_memory import LongTermMemory, SupplierPerformanceRecord
from config.settings import get_settings


class SupplierScorecard:
    """Comprehensive supplier evaluation scorecard."""
    
    def __init__(self, supplier_id: str, performance_record: SupplierPerformanceRecord):
        self.supplier_id = supplier_id
        self.performance_record = performance_record
        self.scorecard_date = datetime.utcnow()
        
        # Calculate detailed scores
        self.delivery_score = self._calculate_delivery_score()
        self.quality_score = self._calculate_quality_score()
        self.financial_score = self._calculate_financial_score()
        self.compliance_score = self._calculate_compliance_score()
        self.relationship_score = self._calculate_relationship_score()
        self.reliability_score = self._calculate_reliability_score()
        
        # Overall composite score
        self.overall_score = self._calculate_overall_score()
        
        # Risk assessment
        self.risk_level = self._assess_risk_level()
        self.risk_factors = self._identify_risk_factors()
        
        # Recommendations
        self.recommendations = self._generate_recommendations()
    
    def _calculate_delivery_score(self) -> float:
        """Calculate delivery performance score (0-100)."""
        record = self.performance_record
        
        if not record.delivery_times:
            return 50.0  # Neutral score for no data
        
        # On-time delivery rate (40% weight)
        on_time_rate = record.get_on_time_rate()
        on_time_score = on_time_rate * 100
        
        # Average delivery speed (30% weight)
        avg_delivery = record.get_avg_delivery_time()
        # Score based on how fast compared to 30-day baseline
        speed_score = max(0, min(100, (30 - avg_delivery) / 30 * 100 + 50))
        
        # Consistency (30% weight)
        if len(record.delivery_times) > 1:
            delivery_std = statistics.stdev(record.delivery_times)
            # Lower standard deviation = higher consistency
            consistency_score = max(0, 100 - (delivery_std * 2))
        else:
            consistency_score = 50
        
        weighted_score = (on_time_score * 0.4 + speed_score * 0.3 + consistency_score * 0.3)
        return round(weighted_score, 1)
    
    def _calculate_quality_score(self) -> float:
        """Calculate quality performance score (0-100)."""
        record = self.performance_record
        
        if not record.quality_scores:
            return 50.0  # Neutral score for no data
        
        # Average quality rating (50% weight)
        avg_quality = record.get_avg_quality_score()
        quality_score = (avg_quality / 5.0) * 100
        
        # Quality consistency (25% weight)
        if len(record.quality_scores) > 1:
            quality_std = statistics.stdev(record.quality_scores)
            consistency_score = max(0, 100 - (quality_std * 20))
        else:
            consistency_score = 80
        
        # Defect rate (25% weight)
        defect_score = max(0, 100 - (record.defect_rate * 100))
        
        weighted_score = (quality_score * 0.5 + consistency_score * 0.25 + defect_score * 0.25)
        return round(weighted_score, 1)
    
    def _calculate_financial_score(self) -> float:
        """Calculate financial performance score (0-100)."""
        record = self.performance_record
        
        # Payment terms compliance (40% weight)
        if record.total_orders > 0:
            payment_compliance_rate = record.payment_terms_honored / record.total_orders
        else:
            payment_compliance_rate = 0.5
        payment_score = payment_compliance_rate * 100
        
        # Pricing competitiveness (35% weight)
        if record.pricing_competitiveness:
            avg_competitiveness = statistics.mean(record.pricing_competitiveness)
            pricing_score = avg_competitiveness * 100
        else:
            pricing_score = 50
        
        # Negotiation flexibility (25% weight)
        flexibility_score = record.negotiation_flexibility * 100
        
        weighted_score = (payment_score * 0.4 + pricing_score * 0.35 + flexibility_score * 0.25)
        return round(weighted_score, 1)
    
    def _calculate_compliance_score(self) -> float:
        """Calculate compliance performance score (0-100)."""
        record = self.performance_record
        
        if record.total_orders == 0:
            return 50.0
        
        # Violation rate (60% weight)
        violation_rate = record.compliance_violations / record.total_orders
        violation_score = max(0, 100 - (violation_rate * 100))
        
        # Audit scores (40% weight)
        if record.audit_scores:
            avg_audit_score = statistics.mean(record.audit_scores)
            audit_score = (avg_audit_score / 5.0) * 100
        else:
            audit_score = 70  # Assume reasonable if no audits
        
        weighted_score = (violation_score * 0.6 + audit_score * 0.4)
        return round(weighted_score, 1)
    
    def _calculate_relationship_score(self) -> float:
        """Calculate relationship management score (0-100)."""
        record = self.performance_record
        
        # Communication quality (50% weight)
        communication_score = (record.communication_quality / 5.0) * 100 if record.communication_quality > 0 else 50
        
        # Responsiveness (50% weight)
        if record.responsiveness > 0:
            # Score based on response time (24 hours = 100%, 72 hours = 0%)
            responsiveness_score = max(0, 100 - ((record.responsiveness - 24) / 48 * 100))
        else:
            responsiveness_score = 50
        
        weighted_score = (communication_score * 0.5 + responsiveness_score * 0.5)
        return round(weighted_score, 1)
    
    def _calculate_reliability_score(self) -> float:
        """Calculate overall reliability score (0-100)."""
        record = self.performance_record
        
        # Success rate (50% weight)
        success_score = record.get_success_rate() * 100
        
        # Experience factor (30% weight)
        # More orders = more reliable data
        experience_score = min(100, (record.total_orders / 20) * 100)
        
        # Tenure factor (20% weight)
        if record.first_order_date:
            days_active = (datetime.utcnow() - record.first_order_date).days
            tenure_score = min(100, (days_active / 365) * 100)  # 1 year = 100%
        else:
            tenure_score = 0
        
        weighted_score = (success_score * 0.5 + experience_score * 0.3 + tenure_score * 0.2)
        return round(weighted_score, 1)
    
    def _calculate_overall_score(self) -> float:
        """Calculate weighted overall performance score."""
        weights = {
            'delivery': 0.25,
            'quality': 0.20,
            'financial': 0.15,
            'compliance': 0.20,
            'relationship': 0.10,
            'reliability': 0.10
        }
        
        overall = (
            self.delivery_score * weights['delivery'] +
            self.quality_score * weights['quality'] +
            self.financial_score * weights['financial'] +
            self.compliance_score * weights['compliance'] +
            self.relationship_score * weights['relationship'] +
            self.reliability_score * weights['reliability']
        )
        
        return round(overall, 1)
    
    def _assess_risk_level(self) -> str:
        """Assess overall risk level for this supplier."""
        score = self.overall_score
        
        if score >= 85:
            return "low"
        elif score >= 70:
            return "medium"
        elif score >= 50:
            return "high"
        else:
            return "critical"
    
    def _identify_risk_factors(self) -> List[str]:
        """Identify specific risk factors."""
        risks = []
        record = self.performance_record
        
        if self.delivery_score < 70:
            risks.append("Delivery performance concerns")
        
        if self.quality_score < 70:
            risks.append("Quality consistency issues")
        
        if record.compliance_violations > 0:
            risks.append("Compliance violations on record")
        
        if record.total_orders < 5:
            risks.append("Limited order history")
        
        if self.financial_score < 60:
            risks.append("Financial reliability concerns")
        
        if record.get_on_time_rate() < 0.8:
            risks.append("Poor on-time delivery rate")
        
        return risks
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if self.delivery_score < 80:
            recommendations.append("Implement delivery tracking and communication improvements")
        
        if self.quality_score < 80:
            recommendations.append("Establish quality improvement programs")
        
        if self.compliance_score < 90:
            recommendations.append("Conduct compliance training and audits")
        
        if self.relationship_score < 75:
            recommendations.append("Improve communication channels and responsiveness")
        
        if self.overall_score >= 85:
            recommendations.append("Consider for preferred supplier status")
        
        return recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scorecard to dictionary."""
        return {
            "supplier_id": self.supplier_id,
            "supplier_name": self.performance_record.supplier_name,
            "scorecard_date": self.scorecard_date.isoformat(),
            "scores": {
                "overall": self.overall_score,
                "delivery": self.delivery_score,
                "quality": self.quality_score,
                "financial": self.financial_score,
                "compliance": self.compliance_score,
                "relationship": self.relationship_score,
                "reliability": self.reliability_score
            },
            "risk_assessment": {
                "risk_level": self.risk_level,
                "risk_factors": self.risk_factors
            },
            "recommendations": self.recommendations,
            "data_quality": {
                "total_orders": self.performance_record.total_orders,
                "data_completeness": self._calculate_data_completeness()
            }
        }
    
    def _calculate_data_completeness(self) -> float:
        """Calculate how complete the performance data is."""
        record = self.performance_record
        completeness_factors = []
        
        # Check various data fields
        completeness_factors.append(1.0 if record.delivery_times else 0.0)
        completeness_factors.append(1.0 if record.quality_scores else 0.0)
        completeness_factors.append(1.0 if record.total_orders >= 3 else record.total_orders / 3)
        completeness_factors.append(1.0 if record.pricing_competitiveness else 0.0)
        completeness_factors.append(1.0 if record.communication_quality > 0 else 0.0)
        
        return round(statistics.mean(completeness_factors) * 100, 1)


class SupplierLearningEngine:
    """AI-powered supplier learning and recommendation engine."""
    
    def __init__(self, memory_system: LongTermMemory):
        self.memory = memory_system
        self.settings = get_settings()
        
        # Learning parameters
        self.learning_threshold = 0.7  # Confidence threshold for recommendations
        self.min_data_points = 3      # Minimum orders for reliable analysis
        
        # Cached analyses
        self.scorecard_cache: Dict[str, SupplierScorecard] = {}
        self.cache_expiry = timedelta(hours=24)
        self.last_cache_update = datetime.utcnow()
    
    def generate_supplier_scorecard(self, supplier_id: str) -> Optional[SupplierScorecard]:
        """
        Generate comprehensive supplier scorecard.
        
        Args:
            supplier_id: Supplier to analyze
            
        Returns:
            SupplierScorecard or None if insufficient data
        """
        performance_record = self.memory.get_supplier_performance(supplier_id)
        if not performance_record or performance_record.total_orders < self.min_data_points:
            return None
        
        # Check cache first
        if (supplier_id in self.scorecard_cache and 
            datetime.utcnow() - self.last_cache_update < self.cache_expiry):
            return self.scorecard_cache[supplier_id]
        
        # Generate new scorecard
        scorecard = SupplierScorecard(supplier_id, performance_record)
        self.scorecard_cache[supplier_id] = scorecard
        
        return scorecard
    
    def analyze_supplier_trends(self, supplier_id: str, time_window_days: int = 90) -> Dict[str, Any]:
        """
        Analyze supplier performance trends over time.
        
        Args:
            supplier_id: Supplier to analyze
            time_window_days: Time window for trend analysis
            
        Returns:
            Trend analysis results
        """
        record = self.memory.get_supplier_performance(supplier_id)
        if not record:
            return {"error": "Supplier not found"}
        
        # For this implementation, we'll simulate trend analysis
        # In a real system, you'd analyze time-series data
        
        recent_performance = record.get_performance_score()
        
        # Simulate trend calculation
        if record.total_orders >= 6:
            # Assume we have enough data to detect trends
            trend_direction = "improving" if recent_performance > 75 else "stable"
            if recent_performance < 60:
                trend_direction = "declining"
        else:
            trend_direction = "insufficient_data"
        
        return {
            "supplier_id": supplier_id,
            "analysis_period_days": time_window_days,
            "current_performance_score": recent_performance,
            "trend_direction": trend_direction,
            "trend_confidence": 0.8 if record.total_orders >= 10 else 0.5,
            "key_metrics": {
                "delivery_trend": "stable",
                "quality_trend": "improving",
                "cost_trend": "stable"
            },
            "predictions": {
                "next_30_days_performance": recent_performance + (2 if trend_direction == "improving" else 0),
                "risk_level_forecast": "low" if recent_performance > 80 else "medium"
            }
        }
    
    def predict_supplier_performance(self, supplier_id: str, 
                                   procurement_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict how a supplier will perform for a specific procurement scenario.
        
        Args:
            supplier_id: Supplier to evaluate
            procurement_scenario: Scenario details (urgency, value, category, etc.)
            
        Returns:
            Performance prediction
        """
        record = self.memory.get_supplier_performance(supplier_id)
        if not record:
            return {"error": "Supplier not found"}
        
        scorecard = self.generate_supplier_scorecard(supplier_id)
        if not scorecard:
            return {"error": "Insufficient data for prediction"}
        
        # Extract scenario parameters
        urgency = procurement_scenario.get("urgency", "medium")
        value = procurement_scenario.get("value", 0)
        category = procurement_scenario.get("category", "")
        requirements = procurement_scenario.get("requirements", {})
        
        # Base prediction on historical performance
        base_score = scorecard.overall_score
        predicted_score = base_score
        confidence = 0.8
        
        # Adjust for urgency
        if urgency == "high":
            if scorecard.delivery_score < 70:
                predicted_score -= 10  # Penalty for poor delivery performance
                confidence -= 0.1
        
        # Adjust for order value
        if value > record.total_value / record.total_orders * 2:  # Large order relative to history
            predicted_score -= 5  # Slight penalty for unfamiliar order size
            confidence -= 0.05
        
        # Quality requirements
        if requirements.get("quality_critical", False):
            if scorecard.quality_score < 80:
                predicted_score -= 15
                confidence -= 0.2
        
        # Calculate success probability
        success_probability = min(0.99, max(0.1, predicted_score / 100))
        
        # Estimated delivery time
        base_delivery = record.get_avg_delivery_time()
        if urgency == "high":
            estimated_delivery = base_delivery * 0.8  # Assume they can expedite
        else:
            estimated_delivery = base_delivery
        
        return {
            "supplier_id": supplier_id,
            "scenario": procurement_scenario,
            "prediction": {
                "predicted_performance_score": round(predicted_score, 1),
                "success_probability": round(success_probability, 3),
                "estimated_delivery_days": round(estimated_delivery, 1),
                "confidence_level": round(confidence, 2)
            },
            "risk_factors": self._identify_scenario_risks(scorecard, procurement_scenario),
            "recommendation": self._generate_scenario_recommendation(predicted_score, confidence),
            "alternatives": self._suggest_alternatives(supplier_id, procurement_scenario)
        }
    
    def recommend_supplier_improvements(self, supplier_id: str) -> Dict[str, Any]:
        """
        Recommend specific improvements for a supplier.
        
        Args:
            supplier_id: Supplier to analyze
            
        Returns:
            Improvement recommendations
        """
        scorecard = self.generate_supplier_scorecard(supplier_id)
        if not scorecard:
            return {"error": "Insufficient data for recommendations"}
        
        improvements = []
        priorities = []
        
        # Analyze each performance area
        performance_areas = {
            "delivery": scorecard.delivery_score,
            "quality": scorecard.quality_score,
            "financial": scorecard.financial_score,
            "compliance": scorecard.compliance_score,
            "relationship": scorecard.relationship_score
        }
        
        for area, score in performance_areas.items():
            if score < 70:
                priority = "high"
            elif score < 85:
                priority = "medium"
            else:
                priority = "low"
            
            if priority in ["high", "medium"]:
                improvement = self._get_area_specific_recommendations(area, score)
                improvements.extend(improvement)
                priorities.append({"area": area, "score": score, "priority": priority})
        
        return {
            "supplier_id": supplier_id,
            "current_overall_score": scorecard.overall_score,
            "improvement_priorities": sorted(priorities, key=lambda x: x["score"]),
            "specific_recommendations": improvements,
            "potential_score_improvement": self._calculate_improvement_potential(scorecard),
            "implementation_timeline": "90-180 days for significant improvements"
        }
    
    def compare_suppliers(self, supplier_ids: List[str], 
                         evaluation_criteria: Dict[str, float]) -> Dict[str, Any]:
        """
        Compare multiple suppliers based on specified criteria.
        
        Args:
            supplier_ids: List of suppliers to compare
            evaluation_criteria: Weights for different criteria
            
        Returns:
            Supplier comparison results
        """
        comparisons = []
        
        for supplier_id in supplier_ids:
            scorecard = self.generate_supplier_scorecard(supplier_id)
            if not scorecard:
                continue
            
            # Calculate weighted score based on criteria
            weighted_score = 0
            criteria_scores = {}
            
            default_weights = {
                "delivery": 0.25,
                "quality": 0.20,
                "financial": 0.15,
                "compliance": 0.20,
                "relationship": 0.10,
                "reliability": 0.10
            }
            
            # Use provided criteria or defaults
            weights = evaluation_criteria if evaluation_criteria else default_weights
            
            for criterion, weight in weights.items():
                if hasattr(scorecard, f"{criterion}_score"):
                    score = getattr(scorecard, f"{criterion}_score")
                    criteria_scores[criterion] = score
                    weighted_score += score * weight
            
            comparison = {
                "supplier_id": supplier_id,
                "supplier_name": scorecard.performance_record.supplier_name,
                "overall_score": scorecard.overall_score,
                "weighted_score": round(weighted_score, 1),
                "criteria_scores": criteria_scores,
                "risk_level": scorecard.risk_level,
                "total_orders": scorecard.performance_record.total_orders,
                "recommendations": scorecard.recommendations[:3]  # Top 3 recommendations
            }
            
            comparisons.append(comparison)
        
        # Sort by weighted score
        comparisons.sort(key=lambda x: x["weighted_score"], reverse=True)
        
        return {
            "comparison_criteria": weights,
            "suppliers_compared": len(comparisons),
            "ranking": comparisons,
            "top_performer": comparisons[0] if comparisons else None,
            "analysis_summary": self._generate_comparison_summary(comparisons)
        }
    
    def _identify_scenario_risks(self, scorecard: SupplierScorecard, 
                               scenario: Dict[str, Any]) -> List[str]:
        """Identify risks specific to the procurement scenario."""
        risks = []
        
        urgency = scenario.get("urgency", "medium")
        if urgency == "high" and scorecard.delivery_score < 75:
            risks.append("May not meet urgent delivery requirements")
        
        value = scenario.get("value", 0)
        if value > scorecard.performance_record.total_value:
            risks.append("Order value exceeds historical range")
        
        if scenario.get("requirements", {}).get("quality_critical") and scorecard.quality_score < 80:
            risks.append("Quality performance may not meet critical requirements")
        
        return risks
    
    def _generate_scenario_recommendation(self, predicted_score: float, confidence: float) -> str:
        """Generate recommendation based on prediction."""
        if predicted_score >= 85 and confidence >= 0.8:
            return "Highly recommended"
        elif predicted_score >= 70 and confidence >= 0.6:
            return "Recommended with monitoring"
        elif predicted_score >= 60:
            return "Caution advised - consider alternatives"
        else:
            return "Not recommended - high risk"
    
    def _suggest_alternatives(self, supplier_id: str, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest alternative suppliers for the scenario."""
        # Get all suppliers and rank them for this scenario
        all_suppliers = []
        
        for sid, record in self.memory.supplier_records.items():
            if sid != supplier_id and record.total_orders >= 3:
                scorecard = self.generate_supplier_scorecard(sid)
                if scorecard:
                    prediction = self.predict_supplier_performance(sid, scenario)
                    if "prediction" in prediction:
                        all_suppliers.append({
                            "supplier_id": sid,
                            "name": record.supplier_name,
                            "predicted_score": prediction["prediction"]["predicted_performance_score"],
                            "confidence": prediction["prediction"]["confidence_level"]
                        })
        
        # Sort by predicted score and return top 3
        all_suppliers.sort(key=lambda x: x["predicted_score"], reverse=True)
        return all_suppliers[:3]
    
    def _get_area_specific_recommendations(self, area: str, score: float) -> List[str]:
        """Get specific recommendations for a performance area."""
        recommendations = []
        
        if area == "delivery":
            if score < 70:
                recommendations.extend([
                    "Implement delivery tracking systems",
                    "Establish delivery performance incentives",
                    "Review and optimize logistics processes"
                ])
        elif area == "quality":
            if score < 70:
                recommendations.extend([
                    "Implement quality management systems",
                    "Conduct regular quality audits",
                    "Establish quality improvement programs"
                ])
        elif area == "financial":
            if score < 70:
                recommendations.extend([
                    "Review payment terms and processes",
                    "Conduct financial stability assessment",
                    "Negotiate improved pricing structures"
                ])
        
        return recommendations
    
    def _calculate_improvement_potential(self, scorecard: SupplierScorecard) -> float:
        """Calculate potential score improvement."""
        current_score = scorecard.overall_score
        
        # Identify lowest performing area
        scores = [
            scorecard.delivery_score,
            scorecard.quality_score,
            scorecard.financial_score,
            scorecard.compliance_score,
            scorecard.relationship_score
        ]
        
        min_score = min(scores)
        improvement_potential = min(20, 85 - min_score)  # Cap at 20 points improvement
        
        return round(improvement_potential, 1)
    
    def _generate_comparison_summary(self, comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of supplier comparison."""
        if not comparisons:
            return {"message": "No suppliers to compare"}
        
        scores = [c["weighted_score"] for c in comparisons]
        
        return {
            "average_score": round(statistics.mean(scores), 1),
            "score_range": {
                "highest": max(scores),
                "lowest": min(scores),
                "spread": round(max(scores) - min(scores), 1)
            },
            "quality_distribution": {
                "excellent": len([s for s in scores if s >= 85]),
                "good": len([s for s in scores if 70 <= s < 85]),
                "fair": len([s for s in scores if 50 <= s < 70]),
                "poor": len([s for s in scores if s < 50])
            }
        }


# Global learning engine instance
_learning_engine_instance = None

def get_learning_engine() -> SupplierLearningEngine:
    """Get the global supplier learning engine instance."""
    global _learning_engine_instance
    if _learning_engine_instance is None:
        from .long_term_memory import get_memory
        _learning_engine_instance = SupplierLearningEngine(get_memory())
    return _learning_engine_instance