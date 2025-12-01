"""
System Integration for Demo
Uses actual system components and enterprise data.
"""
import json
import asyncio
from typing import Dict, List, Any
from pathlib import Path

def load_system_data():
    """Load supplier and policy data from enterprise databases."""
    base_path = Path("data")
    
    with open(base_path / "mock_suppliers.json") as f:
        suppliers_data = json.load(f)
    
    with open(base_path / "policy_rules.json") as f:
        policies_data = json.load(f)
    
    with open(base_path / "pricing_data.json") as f:
        pricing_data = json.load(f)
    
    return suppliers_data, policies_data, pricing_data

def search_suppliers(request, suppliers_data):
    """Search suppliers using intelligent filtering and ranking."""
    suppliers = suppliers_data['suppliers']
    
    # Filter by category capabilities
    relevant_suppliers = []
    for supplier in suppliers:
        capabilities = supplier.get('capabilities', [])
        if request.category in capabilities or any(cap in request.category for cap in capabilities):
            relevant_suppliers.append(supplier)
    
    # Apply urgency filtering
    if request.urgency == "high":
        relevant_suppliers = [
            s for s in relevant_suppliers 
            if s.get('lead_time_days', 30) <= 15
        ]
    
    # Apply budget filtering
    budget_per_unit = request.budget / request.quantity
    if budget_per_unit < 1.0:  # Low budget
        relevant_suppliers = [
            s for s in relevant_suppliers 
            if s.get('pricing_tier') in ['budget', 'mid-range']
        ]
    
    # Sort by compliance score and financial rating
    relevant_suppliers.sort(
        key=lambda s: (s.get('compliance_score', 0), s.get('financial_rating', 'D')), 
        reverse=True
    )
    
    return relevant_suppliers[:3]

def check_compliance(request, suppliers, policies_data):
    """Perform compliance checking using enterprise policies."""
    policies = policies_data['procurement_policies']
    
    results = {
        "approved": [],
        "rejected": [],
        "needs_approval": False,
        "approval_reason": None
    }
    
    # Check budget limits
    spending_limits = policies['spending_limits']
    if request.budget > spending_limits['manager_approval']:
        results["needs_approval"] = True
        results["approval_reason"] = f"Budget ${request.budget:,} exceeds manager approval limit of ${spending_limits['manager_approval']:,}"
    
    # Check supplier requirements
    min_compliance = policies['supplier_requirements']['minimum_compliance_score']
    required_certs = policies['supplier_requirements']['required_certifications']
    min_rating = policies['supplier_requirements']['minimum_financial_rating']
    
    for supplier in suppliers:
        # Compliance score check
        if supplier.get('compliance_score', 0) < min_compliance:
            results["rejected"].append({
                "supplier": supplier,
                "reason": f"Compliance score {supplier.get('compliance_score')} below minimum {min_compliance}"
            })
            continue
        
        # Certification check
        supplier_certs = supplier.get('certifications', [])
        missing_certs = [cert for cert in required_certs if cert not in supplier_certs]
        if missing_certs:
            results["rejected"].append({
                "supplier": supplier,
                "reason": f"Missing required certifications: {missing_certs}"
            })
            continue
        
        # Financial rating check
        rating = supplier.get('financial_rating', 'D')
        rating_order = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D']
        if rating_order.index(rating) > rating_order.index(min_rating):
            results["rejected"].append({
                "supplier": supplier,
                "reason": f"Financial rating {rating} below minimum {min_rating}"
            })
            continue
        
        # Supplier approved
        results["approved"].append(supplier)
    
    return results

def generate_recommendation(approved_suppliers, memory_system, learning_engine):
    """Generate intelligent recommendation using memory system."""
    if not approved_suppliers:
        return {"error": "No suppliers passed compliance checks"}
    
    # Get supplier performance from memory
    recommendations = []
    
    for supplier in approved_suppliers:
        supplier_id = supplier['id']
        
        # Check if we have historical performance data
        performance_record = memory_system.get_supplier_performance(supplier_id)
        
        if performance_record:
            # Use learning engine for sophisticated scoring
            scorecard = learning_engine.generate_supplier_scorecard(supplier_id)
            
            if scorecard:
                recommendations.append({
                    "supplier": supplier,
                    "performance_score": scorecard.overall_score,
                    "delivery_score": scorecard.delivery_score,
                    "quality_score": scorecard.quality_score,
                    "risk_level": scorecard.risk_level,
                    "total_orders": performance_record.total_orders,
                    "recommendation_reasons": scorecard.recommendations
                })
        else:
            # New supplier - use basic scoring with debug info
            supplier_id = supplier.get('id', 'UNKNOWN')
            supplier_name = supplier.get('name', 'UNKNOWN')
            lead_time = supplier.get('lead_time_days')
            compliance_score = supplier.get('compliance_score', 70)
            
            print(f"DEBUG: Processing new supplier {supplier_id} ({supplier_name})")
            print(f"DEBUG: lead_time_days = {lead_time} (type: {type(lead_time)})")
            print(f"DEBUG: compliance_score = {compliance_score}")
            
            # Handle None values safely  
            if lead_time is None:
                delivery_score = 50
                print(f"DEBUG: Using neutral delivery score (50) due to None lead_time")
            else:
                delivery_score = max(0, 100 - lead_time)
                print(f"DEBUG: Calculated delivery score: {delivery_score}")
            
            # Calculate basic score
            basic_score = (
                compliance_score * 0.4 +
                delivery_score * 0.3 +
                70 * 0.3  # Neutral score for unknown factors
            )
            
            print(f"DEBUG: Final basic_score = {basic_score}")
            
            recommendations.append({
                "supplier": supplier,
                "performance_score": basic_score,
                "delivery_score": delivery_score,
                "quality_score": 75,  # Neutral
                "risk_level": "medium",
                "total_orders": 0,
                "recommendation_reasons": ["New supplier - limited historical data"]
            })
    
    # Sort by performance score
    recommendations.sort(key=lambda r: r["performance_score"], reverse=True)
 
    print(f"DEBUG: Total recommendations: {len(recommendations)}")
    for i, rec in enumerate(recommendations):
        print(f"DEBUG: Recommendation {i}: {rec['supplier'].get('name')} - Score: {rec['performance_score']}")
    
    # Return top recommendation with rich details
    top_rec = recommendations[0]
    supplier = top_rec["supplier"]

    print(f"DEBUG: Selected top recommendation: {supplier.get('name')}")
    print(f"DEBUG: About to return recommendation dict...")
    
    return {
        "supplier_id": supplier["id"],
        "supplier_name": supplier["name"],
        "performance_score": round(top_rec["performance_score"], 1),
        "delivery_score": round(top_rec["delivery_score"], 1),
        "estimated_delivery_days": supplier.get("lead_time_days", 30),
        "risk_level": top_rec["risk_level"],
        "total_historical_orders": top_rec["total_orders"],
        "recommendation_reasons": top_rec["recommendation_reasons"],
        "all_options": recommendations  # For comparison
    }

def populate_memory_system():
    """Populate memory system with historical procurement data."""
    from memory.long_term_memory import get_memory
    memory = get_memory()
    
    # Add historical supplier performance data
    historical_orders = [
        {
            "supplier_id": "SUP001",
            "supplier_name": "TechParts Global",
            "orders": [
                {"success": True, "value": 25000, "delivery_days": 12, "quality_score": 4.5, "on_time": True},
                {"success": True, "value": 35000, "delivery_days": 14, "quality_score": 4.3, "on_time": True},
                {"success": True, "value": 45000, "delivery_days": 11, "quality_score": 4.7, "on_time": True},
                {"success": True, "value": 28000, "delivery_days": 15, "quality_score": 4.4, "on_time": False},
                {"success": True, "value": 52000, "delivery_days": 13, "quality_score": 4.6, "on_time": True}
            ]
        },
        {
            "supplier_id": "SUP002", 
            "supplier_name": "Eco Materials Inc",
            "orders": [
                {"success": True, "value": 18000, "delivery_days": 19, "quality_score": 4.2, "on_time": True},
                {"success": True, "value": 22000, "delivery_days": 21, "quality_score": 4.1, "on_time": True},
                {"success": False, "value": 30000, "delivery_days": 28, "quality_score": 3.8, "on_time": False},
                {"success": True, "value": 25000, "delivery_days": 20, "quality_score": 4.3, "on_time": True}
            ]
        },
        {
            "supplier_id": "SUP005",
            "supplier_name": "Precision Engineering Ltd",
            "orders": [
                {"success": True, "value": 75000, "delivery_days": 42, "quality_score": 4.9, "on_time": True},
                {"success": True, "value": 85000, "delivery_days": 38, "quality_score": 4.8, "on_time": True},
                {"success": True, "value": 95000, "delivery_days": 35, "quality_score": 4.9, "on_time": True}
            ]
        }
    ]
    
    # Record historical data
    total_orders = 0
    for supplier_data in historical_orders:
        for order in supplier_data["orders"]:
            memory.record_supplier_performance(
                supplier_id=supplier_data["supplier_id"],
                supplier_name=supplier_data["supplier_name"],
                order_data=order
            )
            total_orders += 1
    
    return f"Populated memory with {total_orders} historical orders across {len(historical_orders)} suppliers"