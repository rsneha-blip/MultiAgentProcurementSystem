"""
Pattern Analyzer - Identifies and Analyzes Procurement Patterns

Uses advanced analytics to identify patterns in procurement behavior,
predict future needs, and optimize procurement strategies.
"""
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

from .long_term_memory import LongTermMemory, ProcurementPattern
from config.settings import get_settings


class SeasonalAnalyzer:
    """Analyzes seasonal patterns in procurement."""
    
    def __init__(self):
        self.seasonal_patterns = defaultdict(lambda: defaultdict(list))
    
    def analyze_seasonal_trends(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal procurement trends."""
        if not decisions:
            return {"message": "No data available"}
        
        # Group decisions by month and category
        monthly_data = defaultdict(lambda: defaultdict(lambda: {"count": 0, "total_value": 0}))
        
        for decision in decisions:
            if "timestamp" in decision and "category" in decision:
                month = decision["timestamp"].month
                category = decision["category"]
                value = decision.get("outcome_cost", 0)
                
                monthly_data[category][month]["count"] += 1
                monthly_data[category][month]["total_value"] += value
        
        # Calculate seasonal multipliers
        seasonal_insights = {}
        for category, months in monthly_data.items():
            if len(months) >= 3:  # Need at least 3 months of data
                yearly_avg = statistics.mean([data["count"] for data in months.values()])
                
                seasonal_multipliers = {}
                peak_months = []
                low_months = []
                
                for month, data in months.items():
                    multiplier = data["count"] / yearly_avg if yearly_avg > 0 else 1.0
                    seasonal_multipliers[month] = round(multiplier, 2)
                    
                    if multiplier > 1.5:
                        peak_months.append(month)
                    elif multiplier < 0.5:
                        low_months.append(month)
                
                seasonal_insights[category] = {
                    "seasonal_multipliers": seasonal_multipliers,
                    "peak_months": peak_months,
                    "low_demand_months": low_months,
                    "seasonality_strength": self._calculate_seasonality_strength(list(seasonal_multipliers.values()))
                }
        
        return {
            "analysis_period": f"{len(decisions)} procurement decisions analyzed",
            "categories_analyzed": len(seasonal_insights),
            "seasonal_patterns": seasonal_insights,
            "recommendations": self._generate_seasonal_recommendations(seasonal_insights)
        }
    
    def _calculate_seasonality_strength(self, multipliers: List[float]) -> str:
        """Calculate how seasonal a category is."""
        if not multipliers:
            return "unknown"
        
        coefficient_of_variation = statistics.stdev(multipliers) / statistics.mean(multipliers)
        
        if coefficient_of_variation > 0.5:
            return "highly_seasonal"
        elif coefficient_of_variation > 0.2:
            return "moderately_seasonal"
        else:
            return "stable"
    
    def _generate_seasonal_recommendations(self, seasonal_insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on seasonal analysis."""
        recommendations = []
        
        for category, data in seasonal_insights.items():
            if data["seasonality_strength"] == "highly_seasonal":
                recommendations.append(f"Plan ahead for {category} - shows strong seasonal demand patterns")
            
            if data["peak_months"]:
                months = [self._month_name(m) for m in data["peak_months"]]
                recommendations.append(f"Expect increased {category} demand in {', '.join(months)}")
        
        return recommendations
    
    def _month_name(self, month_num: int) -> str:
        """Convert month number to name."""
        months = ["", "January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        return months[month_num] if 1 <= month_num <= 12 else "Unknown"


class WorkflowAnalyzer:
    """Analyzes procurement workflow patterns."""
    
    def analyze_workflow_efficiency(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow efficiency patterns."""
        if not traces:
            return {"message": "No workflow data available"}
        
        # Analyze step durations and sequences
        step_durations = defaultdict(list)
        workflow_paths = []
        bottlenecks = []
        
        for trace in traces:
            if "spans" not in trace:
                continue
            
            # Extract workflow steps
            workflow_steps = []
            total_duration = 0
            
            for span in trace["spans"]:
                if span.get("workflow_step"):
                    step_name = span["workflow_step"]
                    duration = span.get("duration", 0)
                    
                    step_durations[step_name].append(duration)
                    workflow_steps.append(step_name)
                    total_duration += duration
                    
                    # Identify bottlenecks (steps taking >50% of total time)
                    if duration > total_duration * 0.5:
                        bottlenecks.append({
                            "step": step_name,
                            "duration": duration,
                            "percentage": (duration / total_duration) * 100
                        })
            
            workflow_paths.append(" -> ".join(workflow_steps))
        
        # Calculate step statistics
        step_stats = {}
        for step, durations in step_durations.items():
            if durations:
                step_stats[step] = {
                    "avg_duration_ms": round(statistics.mean(durations), 2),
                    "median_duration_ms": round(statistics.median(durations), 2),
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "occurrences": len(durations)
                }
        
        # Identify common workflow paths
        path_counter = Counter(workflow_paths)
        common_paths = path_counter.most_common(5)
        
        return {
            "total_workflows_analyzed": len(traces),
            "step_performance": step_stats,
            "common_workflow_paths": [{"path": path, "frequency": freq} for path, freq in common_paths],
            "bottlenecks_identified": len(bottlenecks),
            "top_bottlenecks": sorted(bottlenecks, key=lambda x: x["percentage"], reverse=True)[:3],
            "efficiency_recommendations": self._generate_workflow_recommendations(step_stats, bottlenecks)
        }
    
    def _generate_workflow_recommendations(self, step_stats: Dict[str, Any], 
                                         bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """Generate workflow efficiency recommendations."""
        recommendations = []
        
        # Identify slow steps
        if step_stats:
            avg_durations = [(step, stats["avg_duration_ms"]) for step, stats in step_stats.items()]
            slowest_step = max(avg_durations, key=lambda x: x[1])
            
            if slowest_step[1] > 5000:  # More than 5 seconds
                recommendations.append(f"Optimize {slowest_step[0]} step - taking {slowest_step[1]:.0f}ms on average")
        
        # Address bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck["percentage"] > 60:
                recommendations.append(f"Critical bottleneck in {bottleneck['step']} - consuming {bottleneck['percentage']:.1f}% of workflow time")
        
        return recommendations


class PatternAnalyzer:
    """Main pattern analysis engine."""
    
    def __init__(self, memory_system: LongTermMemory):
        self.memory = memory_system
        self.settings = get_settings()
        
        # Analysis components
        self.seasonal_analyzer = SeasonalAnalyzer()
        self.workflow_analyzer = WorkflowAnalyzer()
        
        # Pattern detection parameters
        self.min_occurrences_for_pattern = 3
        self.confidence_threshold = 0.7
    
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze organizational spending patterns."""
        decisions = list(self.memory.decision_history)
        if not decisions:
            return {"message": "No spending data available"}
        
        # Categorize spending
        category_spending = defaultdict(lambda: {"count": 0, "total": 0, "avg": 0})
        monthly_spending = defaultdict(float)
        urgency_patterns = defaultdict(lambda: {"count": 0, "total": 0})
        
        for decision in decisions:
            category = decision.get("category", "unknown")
            cost = decision.get("outcome_cost", 0) or decision.get("budget", 0)
            urgency = decision.get("urgency", "medium")
            timestamp = decision.get("timestamp", datetime.utcnow())
            
            # Category analysis
            category_spending[category]["count"] += 1
            category_spending[category]["total"] += cost
            
            # Monthly analysis
            month_key = timestamp.strftime("%Y-%m")
            monthly_spending[month_key] += cost
            
            # Urgency analysis
            urgency_patterns[urgency]["count"] += 1
            urgency_patterns[urgency]["total"] += cost
        
        # Calculate averages
        for category in category_spending:
            data = category_spending[category]
            data["avg"] = data["total"] / data["count"] if data["count"] > 0 else 0
        
        # Find trends
        monthly_values = list(monthly_spending.values())
        spending_trend = "stable"
        if len(monthly_values) >= 3:
            recent_avg = statistics.mean(monthly_values[-3:])
            early_avg = statistics.mean(monthly_values[:3])
            
            if recent_avg > early_avg * 1.2:
                spending_trend = "increasing"
            elif recent_avg < early_avg * 0.8:
                spending_trend = "decreasing"
        
        return {
            "analysis_period": f"{len(decisions)} procurement decisions",
            "total_spending": sum(d.get("outcome_cost", 0) for d in decisions),
            "category_breakdown": dict(category_spending),
            "spending_trend": spending_trend,
            "urgency_patterns": dict(urgency_patterns),
            "insights": self._generate_spending_insights(category_spending, urgency_patterns),
            "recommendations": self._generate_spending_recommendations(category_spending, spending_trend)
        }
    
    def detect_procurement_anomalies(self, time_window_days: int = 30) -> Dict[str, Any]:
        """Detect anomalous procurement patterns."""
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        recent_decisions = [
            d for d in self.memory.decision_history 
            if d.get("timestamp", datetime.utcnow()) >= cutoff_date
        ]
        
        if not recent_decisions:
            return {"message": "No recent procurement activity"}
        
        anomalies = []
        
        # Detect spending anomalies
        costs = [d.get("outcome_cost", 0) for d in recent_decisions if d.get("outcome_cost")]
        if costs:
            avg_cost = statistics.mean(costs)
            std_cost = statistics.stdev(costs) if len(costs) > 1 else 0
            
            for decision in recent_decisions:
                cost = decision.get("outcome_cost", 0)
                if std_cost > 0 and abs(cost - avg_cost) > 2 * std_cost:
                    anomalies.append({
                        "type": "spending_anomaly",
                        "description": f"Unusual spending amount: ${cost:,.2f}",
                        "severity": "high" if abs(cost - avg_cost) > 3 * std_cost else "medium",
                        "decision_id": decision.get("session_id", "unknown")
                    })
        
        # Detect frequency anomalies
        daily_counts = defaultdict(int)
        for decision in recent_decisions:
            date_key = decision.get("timestamp", datetime.utcnow()).strftime("%Y-%m-%d")
            daily_counts[date_key] += 1
        
        if daily_counts:
            avg_daily = statistics.mean(daily_counts.values())
            for date, count in daily_counts.items():
                if count > avg_daily * 3:  # More than 3x average
                    anomalies.append({
                        "type": "frequency_anomaly",
                        "description": f"Unusual procurement frequency: {count} orders on {date}",
                        "severity": "medium",
                        "date": date
                    })
        
        return {
            "analysis_period_days": time_window_days,
            "total_decisions_analyzed": len(recent_decisions),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "summary": self._generate_anomaly_summary(anomalies)
        }
    
    def predict_future_procurement_needs(self, forecast_days: int = 90) -> Dict[str, Any]:
        """Predict future procurement needs based on patterns."""
        decisions = list(self.memory.decision_history)
        if len(decisions) < 10:
            return {"message": "Insufficient historical data for prediction"}
        
        # Analyze historical patterns
        category_frequency = defaultdict(lambda: {"count": 0, "avg_interval_days": 0, "last_procurement": None})
        
        for decision in decisions:
            category = decision.get("category", "unknown")
            timestamp = decision.get("timestamp", datetime.utcnow())
            
            category_data = category_frequency[category]
            category_data["count"] += 1
            
            if category_data["last_procurement"]:
                interval = (timestamp - category_data["last_procurement"]).days
                current_avg = category_data["avg_interval_days"]
                # Running average
                category_data["avg_interval_days"] = (current_avg * (category_data["count"] - 2) + interval) / (category_data["count"] - 1) if category_data["count"] > 1 else interval
            
            category_data["last_procurement"] = timestamp
        
        # Generate predictions
        predictions = []
        today = datetime.utcnow()
        
        for category, data in category_frequency.items():
            if data["count"] >= 3 and data["avg_interval_days"] > 0:
                last_procurement = data["last_procurement"]
                if last_procurement:
                    days_since_last = (today - last_procurement).days
                    expected_next_in_days = max(0, data["avg_interval_days"] - days_since_last)
                    
                    if expected_next_in_days <= forecast_days:
                        confidence = min(0.9, data["count"] / 10)  # More data = higher confidence
                        
                        predictions.append({
                            "category": category,
                            "predicted_date": (today + timedelta(days=expected_next_in_days)).strftime("%Y-%m-%d"),
                            "days_from_now": int(expected_next_in_days),
                            "confidence": round(confidence, 2),
                            "historical_frequency": f"Every {data['avg_interval_days']:.0f} days",
                            "urgency": self._predict_urgency(expected_next_in_days)
                        })
        
        # Sort by predicted date
        predictions.sort(key=lambda x: x["days_from_now"])
        
        return {
            "forecast_period_days": forecast_days,
            "predictions_count": len(predictions),
            "predicted_procurements": predictions,
            "seasonal_adjustments": self.seasonal_analyzer.analyze_seasonal_trends(decisions),
            "planning_recommendations": self._generate_planning_recommendations(predictions)
        }
    
    def analyze_supplier_selection_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in supplier selection decisions."""
        decisions = list(self.memory.decision_history)
        if not decisions:
            return {"message": "No supplier selection data available"}
        
        # Analyze supplier choices by category and other factors
        supplier_patterns = defaultdict(lambda: {
            "categories": defaultdict(int),
            "urgency_levels": defaultdict(int),
            "success_rate": {"total": 0, "successful": 0},
            "avg_cost": 0,
            "total_cost": 0
        })
        
        for decision in decisions:
            supplier = decision.get("selected_supplier")
            if not supplier:
                continue
            
            category = decision.get("category", "unknown")
            urgency = decision.get("urgency", "medium")
            success = decision.get("outcome_success", True)
            cost = decision.get("outcome_cost", 0)
            
            pattern_data = supplier_patterns[supplier]
            pattern_data["categories"][category] += 1
            pattern_data["urgency_levels"][urgency] += 1
            pattern_data["success_rate"]["total"] += 1
            if success:
                pattern_data["success_rate"]["successful"] += 1
            pattern_data["total_cost"] += cost
        
        # Calculate averages and patterns
        supplier_analysis = {}
        for supplier, data in supplier_patterns.items():
            success_rate = (data["success_rate"]["successful"] / data["success_rate"]["total"] 
                           if data["success_rate"]["total"] > 0 else 0)
            
            supplier_analysis[supplier] = {
                "total_selections": data["success_rate"]["total"],
                "success_rate": round(success_rate, 3),
                "avg_cost": round(data["total_cost"] / data["success_rate"]["total"], 2) if data["success_rate"]["total"] > 0 else 0,
                "preferred_categories": dict(data["categories"]),
                "urgency_distribution": dict(data["urgency_levels"]),
                "recommendation_score": self._calculate_supplier_recommendation_score(data, success_rate)
            }
        
        return {
            "suppliers_analyzed": len(supplier_analysis),
            "supplier_patterns": supplier_analysis,
            "insights": self._generate_supplier_selection_insights(supplier_analysis),
            "recommendations": self._generate_supplier_recommendations(supplier_analysis)
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive pattern analysis report."""
        return {
            "report_date": datetime.utcnow().isoformat(),
            "spending_analysis": self.analyze_spending_patterns(),
            "seasonal_trends": self.seasonal_analyzer.analyze_seasonal_trends(list(self.memory.decision_history)),
            "anomaly_detection": self.detect_procurement_anomalies(),
            "future_predictions": self.predict_future_procurement_needs(),
            "supplier_patterns": self.analyze_supplier_selection_patterns(),
            "executive_summary": self._generate_executive_summary()
        }
    
    def _generate_spending_insights(self, category_spending: Dict[str, Any], 
                                  urgency_patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from spending analysis."""
        insights = []
        
        # Top spending categories
        top_categories = sorted(category_spending.items(), key=lambda x: x[1]["total"], reverse=True)[:3]
        if top_categories:
            insights.append(f"Top spending categories: {', '.join([cat for cat, _ in top_categories])}")
        
        # Urgency patterns
        if urgency_patterns:
            urgent_percentage = (urgency_patterns.get("high", {}).get("count", 0) / 
                               sum(data.get("count", 0) for data in urgency_patterns.values()) * 100)
            if urgent_percentage > 30:
                insights.append(f"High urgency requests represent {urgent_percentage:.1f}% of procurements - consider better planning")
        
        return insights
    
    def _generate_spending_recommendations(self, category_spending: Dict[str, Any], trend: str) -> List[str]:
        """Generate spending recommendations."""
        recommendations = []
        
        if trend == "increasing":
            recommendations.append("Spending is trending upward - review budget allocations and approval processes")
        
        # High-spend categories
        for category, data in category_spending.items():
            if data["avg"] > 10000:  # High average spend
                recommendations.append(f"Consider bulk purchasing or preferred supplier agreements for {category}")
        
        return recommendations
    
    def _generate_anomaly_summary(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of detected anomalies."""
        severity_counts = Counter(anomaly["severity"] for anomaly in anomalies)
        type_counts = Counter(anomaly["type"] for anomaly in anomalies)
        
        return {
            "total_anomalies": len(anomalies),
            "by_severity": dict(severity_counts),
            "by_type": dict(type_counts),
            "requires_attention": severity_counts.get("high", 0) > 0
        }
    
    def _predict_urgency(self, days_until_need: int) -> str:
        """Predict urgency level based on timing."""
        if days_until_need <= 7:
            return "high"
        elif days_until_need <= 21:
            return "medium"
        else:
            return "low"
    
    def _generate_planning_recommendations(self, predictions: List[Dict[str, Any]]) -> List[str]:
        """Generate planning recommendations based on predictions."""
        recommendations = []
        
        urgent_predictions = [p for p in predictions if p["urgency"] == "high"]
        if urgent_predictions:
            categories = [p["category"] for p in urgent_predictions]
            recommendations.append(f"Urgent attention needed for: {', '.join(categories)}")
        
        return recommendations
    
    def _calculate_supplier_recommendation_score(self, data: Dict[str, Any], success_rate: float) -> float:
        """Calculate a recommendation score for a supplier."""
        base_score = success_rate * 100
        
        # Bonus for experience (more selections)
        experience_bonus = min(20, data["success_rate"]["total"] * 2)
        
        return min(100, base_score + experience_bonus)
    
    def _generate_supplier_selection_insights(self, supplier_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights about supplier selection patterns."""
        insights = []
        
        if supplier_analysis:
            # Find most successful supplier
            best_supplier = max(supplier_analysis.items(), key=lambda x: x[1]["recommendation_score"])
            insights.append(f"Most successful supplier: {best_supplier[0]} with {best_supplier[1]['recommendation_score']:.0f}% recommendation score")
            
            # Category specializations
            category_specialists = {}
            for supplier, data in supplier_analysis.items():
                top_category = max(data["preferred_categories"].items(), key=lambda x: x[1])
                if top_category[1] >= 3:  # At least 3 selections
                    category_specialists[top_category[0]] = supplier
            
            if category_specialists:
                insights.append("Category specialists identified for optimized procurement")
        
        return insights
    
    def _generate_supplier_recommendations(self, supplier_analysis: Dict[str, Any]) -> List[str]:
        """Generate supplier-related recommendations."""
        recommendations = []
        
        # Identify high-performing suppliers
        high_performers = [
            supplier for supplier, data in supplier_analysis.items()
            if data["recommendation_score"] > 80 and data["total_selections"] >= 3
        ]
        
        if high_performers:
            recommendations.append(f"Consider preferred supplier status for: {', '.join(high_performers)}")
        
        return recommendations
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of all analyses."""
        total_decisions = len(self.memory.decision_history)
        total_suppliers = len(self.memory.supplier_records)
        
        return {
            "key_metrics": {
                "total_procurement_decisions": total_decisions,
                "suppliers_tracked": total_suppliers,
                "patterns_identified": len(self.memory.patterns),
                "analysis_confidence": "high" if total_decisions > 50 else "medium"
            },
            "top_insights": [
                f"Analyzed {total_decisions} procurement decisions across {total_suppliers} suppliers",
                "Pattern analysis enables predictive procurement planning",
                "Supplier performance tracking shows clear optimization opportunities"
            ]
        }


# Global pattern analyzer instance
_pattern_analyzer_instance = None

def get_pattern_analyzer() -> PatternAnalyzer:
    """Get the global pattern analyzer instance."""
    global _pattern_analyzer_instance
    if _pattern_analyzer_instance is None:
        from .long_term_memory import get_memory
        _pattern_analyzer_instance = PatternAnalyzer(get_memory())
    return _pattern_analyzer_instance