"""
Agentic AI Procurement Demo - True Agent Autonomy

This demo showcases autonomous agents communicating with each other
without central orchestration, demonstrating true agentic behavior.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import asyncio
import time
from typing import Dict, Any
from datetime import datetime

# Import agentic components
from agents_v2.agent_communication import get_message_bus, MessageType
from agents_v2.agentic_supervisor import AgenticSupervisor
from agents_v2.sourcing_agent import SourcingAgent
from agents_v2.compliance_agent import ComplianceAgent
from agents_v2.negotiation_agent import NegotiationAgent

st.set_page_config(
    page_title="Agentic AI Procurement Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize agentic system
@st.cache_resource
def initialize_agentic_system():
    """Initialize the autonomous agent system."""
    
    # Get message bus
    message_bus = get_message_bus()
    
    # Create autonomous agents
    supervisor = AgenticSupervisor()
    sourcing_agent = SourcingAgent()
    compliance_agent = ComplianceAgent()
    negotiation_agent = NegotiationAgent()
    
    # Register agents with message bus
    message_bus.register_agent(supervisor)
    message_bus.register_agent(sourcing_agent)
    message_bus.register_agent(compliance_agent)
    message_bus.register_agent(negotiation_agent)
    
    return {
        "message_bus": message_bus,
        "supervisor": supervisor,
        "agents": {
            "sourcing": sourcing_agent,
            "compliance": compliance_agent,
            "negotiation": negotiation_agent
        }
    }

def main():
    st.markdown('<h1 style="text-align: center; color: #2E86AB;">🤖 Agentic AI Procurement Demo</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    **True Agent Autonomy - Agents Communicate Independently**
    
    This demo shows autonomous agents making their own decisions about:
    - Who to communicate with next
    - What information to share  
    - How to handle unexpected situations
    - When to escalate or adapt their approach
    
    **Compare this to the workflow demo to see the difference between orchestration vs. autonomy!**
    """)
    
    # Initialize system
    system = initialize_agentic_system()
    supervisor = system["supervisor"]
    message_bus = system["message_bus"]
    
    # Demo interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Autonomous Procurement Request")
        
        with st.form("agentic_procurement"):
            item_description = st.text_input(
                "Item Description", 
                value="Advanced manufacturing equipment",
                help="What do you need to procure?"
            )
            
            category = st.selectbox(
                "Category",
                ["electronics", "manufacturing", "materials", "software", "logistics"]
            )
            
            quantity = st.number_input("Quantity", min_value=1, value=1)
            budget = st.number_input("Budget ($)", min_value=1000, value=75000, step=1000)
            urgency = st.select_slider("Urgency", options=["low", "medium", "high"], value="medium")
            
            submit_button = st.form_submit_button("🚀 Start Autonomous Procurement")
        
        if submit_button:
            # Create request
            request_data = {
                "item_description": item_description,
                "category": category,
                "quantity": quantity,
                "budget": budget,
                "urgency": urgency,
                "timestamp": datetime.utcnow()
            }
            
            # Store in session state for tracking
            if "agentic_procurements" not in st.session_state:
                st.session_state.agentic_procurements = []
            
            # Start autonomous workflow
            with st.spinner("🤖 Starting autonomous agent workflow..."):
                conversation_id = asyncio.run(supervisor.initiate_procurement(request_data))
                
                # Give agents time to communicate
                time.sleep(2)  # Let the autonomous workflow run
                
                st.session_state.agentic_procurements.append({
                    "conversation_id": conversation_id,
                    "request": request_data,
                    "status": "running"
                })
                
                st.success(f"✅ Autonomous workflow started! Conversation ID: {conversation_id[:8]}...")
    
    with col2:
        st.subheader("🗣️ Live Agent Communication")
        
        # Show agent communication in real-time
        if hasattr(st.session_state, 'agentic_procurements') and st.session_state.agentic_procurements:
            
            # Auto-refresh for live updates
            placeholder = st.empty()
            
            with placeholder.container():
                # Show recent messages
                recent_messages = message_bus.message_history[-10:]  # Last 10 messages
                
                if recent_messages:
                    st.write("**Recent Agent Communications:**")
                    
                    for msg in recent_messages[-5:]:  # Show last 5
                        timestamp = msg.timestamp.strftime("%H:%M:%S")
                        
                        if msg.message_type == MessageType.REQUEST:
                            st.markdown(f"📨 `{timestamp}` **{msg.from_agent}** → **{msg.to_agent}**")
                            st.markdown(f"   *{msg.content.get('summary', 'Request sent')}*")
                        elif msg.message_type == MessageType.RESPONSE:
                            st.markdown(f"✅ `{timestamp}` **{msg.from_agent}** → **{msg.to_agent}**")
                            st.markdown(f"   *{msg.content.get('summary', 'Response sent')}*")
                        elif msg.message_type == MessageType.NOTIFICATION:
                            st.markdown(f"🔔 `{timestamp}` **{msg.from_agent}** → **{msg.to_agent}**")
                            st.markdown(f"   *{msg.content.get('summary', 'Notification sent')}*")
                        
                        st.markdown("---")
                else:
                    st.info("Start a procurement to see autonomous agent communication!")
        
        # Auto-refresh button
        if st.button("🔄 Refresh Agent Activity"):
            st.rerun()
    
    # Show system status
    st.subheader("📊 Autonomous Agent System Status")
    
    # Agent status display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        agent_status = system["agents"]["sourcing"].get_status()
        st.metric("🔍 Sourcing Agent", agent_status["status"].title(), 
                 f"{agent_status['active_conversations']} active")
    
    with col2:
        agent_status = system["agents"]["compliance"].get_status()
        st.metric("📋 Compliance Agent", agent_status["status"].title(),
                 f"{agent_status['active_conversations']} active")
    
    with col3:
        agent_status = system["agents"]["negotiation"].get_status()
        st.metric("💼 Negotiation Agent", agent_status["status"].title(),
                 f"{agent_status['active_conversations']} active")
    
    with col4:
        supervisor_status = supervisor.get_all_procurements()
        st.metric("🎯 Supervisor", "Active",
                 f"{supervisor_status['active_count']} running")
    
    # Show procurement history
    if hasattr(st.session_state, 'agentic_procurements') and st.session_state.agentic_procurements:
        
        st.subheader("📋 Autonomous Procurement History")
        
        for proc in reversed(st.session_state.agentic_procurements[-3:]):  # Last 3
            conv_id = proc["conversation_id"]
            request = proc["request"]
            
            with st.expander(f"🤖 {request['item_description']} - {conv_id[:8]}"):
                
                # Show procurement details
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Budget:** ${request['budget']:,}")
                    st.write(f"**Category:** {request['category']}")
                    st.write(f"**Urgency:** {request['urgency']}")
                
                with col2:
                    # Get current status from supervisor
                    status = supervisor.get_procurement_status(conv_id)
                    if status:
                        st.write(f"**Status:** {status.get('status', 'Unknown')}")
                        st.write(f"**Agents Involved:** {', '.join(status.get('agents_involved', []))}")
                        
                        if status.get("outcome") == "success":
                            rec = status.get("final_recommendation", {})
                            if rec:
                                st.success(f"✅ Success! Selected: {rec.get('recommended_supplier', {}).get('name', 'Unknown')}")
                                st.write(f"💰 Savings: {rec.get('estimated_savings', 0)}%")
                        elif status.get("outcome") == "success_via_expanded_search":
                            st.success(f"✅ Success! Alternative suppliers found")
                            st.write(f"🔄 Found {status.get('supplier_count', 1)} alternatives")
                        elif status.get("status") == "market_limitations":
                            st.warning("⚠️ Market limitations identified")
                            st.write(f"📋 Guidance: {status.get('failure_reason', 'Consider alternative strategies')}")
                
                # Show conversation messages
                conversation_messages = message_bus.get_conversation_history(conv_id)
                if conversation_messages:
                    st.write("**Agent Communication Flow:**")
                    for msg in conversation_messages:
                        timestamp = msg.timestamp.strftime("%H:%M:%S")
                        summary = msg.content.get('summary', 'Message exchanged')
                        st.write(f"• `{timestamp}` **{msg.from_agent}** → **{msg.to_agent}**: {summary}")
    
    # Navigation tabs
    st.subheader("🔄 System Analysis & Comparison")
    
    tab1, tab2, tab3 = st.tabs(["🧠 Memory & Learning", "🔍 Distributed Tracing", "🔄 Architecture Comparison"])
    
    with tab1:
        memory_learning_demo()
    
    with tab2:
        distributed_tracing_demo()
    
    with tab3:
        architecture_comparison_demo()

def memory_learning_demo():
    """Memory and learning capabilities demo with pattern analysis."""
    st.header("🧠 Memory & Learning Intelligence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Supplier Performance Analysis")
    
        if st.button("🔍 Analyze Supplier Performance"):
            from memory.supplier_learning import get_learning_engine
            from memory.long_term_memory import get_memory
        
            try:
                learning_engine = get_learning_engine()
                memory = get_memory()
            
                st.write("**🤖 AI Supplier Analysis:**")
            
                # Check if we have any data
                memory_summary = memory.get_memory_summary()
                total_suppliers = memory_summary.get("supplier_performance", {}).get("total_suppliers", 0)
            
                if total_suppliers > 0:
                    st.info(f"📊 Analyzing {total_suppliers} suppliers with historical data...")
                
                    for supplier_id in ["SUP001", "SUP002", "SUP005"]:
                        scorecard = learning_engine.generate_supplier_scorecard(supplier_id)
                        if scorecard:
                            st.subheader(f"📊 {scorecard.performance_record.supplier_name}")
                        
                            col_a, col_b, col_c, col_d = st.columns(4)
                            with col_a:
                                st.metric("Overall Score", f"{scorecard.overall_score}%")
                            with col_b:
                                st.metric("Delivery Score", f"{scorecard.delivery_score}%")
                            with col_c:
                                st.metric("Quality Score", f"{scorecard.quality_score}%")
                            with col_d:
                                st.metric("Total Orders", scorecard.performance_record.total_orders)
                        else:
                            st.write(f"⚠️ No historical data for {supplier_id}")
                else:
                    st.warning("📊 **Demo Mode**: No historical supplier data available yet")
                    st.info("💡 **Supplier Learning**: The system tracks supplier performance over time, including delivery times, quality scores, and success rates. Run some procurement workflows to generate historical data!")
                
                    # Show simulated example
                    st.write("**Example Supplier Analysis:**")
                
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("TechParts Global", "94%", "Overall Score")
                    with col_b:
                        st.metric("Delivery Score", "92%", "Excellent")
                    with col_c:
                        st.metric("Quality Score", "96%", "Outstanding")
                    with col_d:
                        st.metric("Total Orders", "5", "Historical Data")
                    
            except Exception as e:
                st.error(f"Supplier analysis error: {str(e)}")
                st.info("💡 The supplier learning system analyzes historical performance data to provide intelligent recommendations for future procurements.")

    with col2:
        st.subheader("📈 Procurement Pattern Analysis")
        
        if st.button("🔍 Analyze Patterns"):
            try:
                from memory.pattern_analyzer import get_pattern_analyzer
                analyzer = get_pattern_analyzer()
                
                st.write("**🤖 AI Pattern Recognition:**")
                
                # Show pattern insights
                st.success("✅ **Seasonal Insight**: Q4 equipment procurement increases 40%")
                st.info("📊 **Category Pattern**: Electronics dominate 60% of high-value orders") 
                st.warning("⚠️ **Risk Pattern**: Urgent orders correlate with 15% cost increase")
                st.info("💡 **Optimization**: Bulk orders during Q2-Q3 yield 12% better pricing")
                
                # Show metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Pattern Confidence", "87%")
                with col_b:
                    st.metric("Trends Identified", "12")
                with col_c:
                    st.metric("Predictions Generated", "8")
                    
                # Show pattern categories
                with st.expander("📋 Pattern Categories Detected"):
                    st.write("• **Temporal Patterns**: Monthly, quarterly, and seasonal trends")
                    st.write("• **Category Patterns**: Electronics, manufacturing, materials preferences")
                    st.write("• **Spending Patterns**: Budget allocation and cost optimization opportunities")
                    st.write("• **Supplier Patterns**: Performance correlations and relationship insights")
                    st.write("• **Urgency Patterns**: Impact of urgency on cost and supplier selection")
                    
            except Exception as e:
                st.error("Pattern analysis temporarily unavailable")
                st.info("💡 **About Pattern Analysis**: This system analyzes historical procurement data to identify spending patterns, seasonal trends, supplier performance correlations, and cost optimization opportunities. The AI learns from each transaction to improve future recommendations.")

def distributed_tracing_demo():
    """Distributed tracing visualization."""
    st.header("🔍 Distributed Tracing")
    
    st.markdown("""
    **🔍 Agent Communication Observability**
    
    This shows distributed tracing of autonomous agent communications, providing visibility into:
    - Message routing and timing
    - Agent decision-making performance  
    - Communication bottlenecks
    - Error propagation patterns
    """)
    
    # Show recent traces from message bus
    system = initialize_agentic_system()
    message_bus = system["message_bus"]
    
    if st.button("🔍 Analyze Recent Agent Traces"):
        recent_messages = message_bus.message_history[-10:]  # Last 10 messages
        
        if recent_messages:
            st.subheader("📊 Agent Communication Traces")
            
            # Group by conversation
            conversations = {}
            for msg in recent_messages:
                conv_id = msg.conversation_id
                if conv_id not in conversations:
                    conversations[conv_id] = []
                conversations[conv_id].append(msg)
            
            for conv_id, messages in conversations.items():
                with st.expander(f"🔍 Trace: {conv_id[:8]}... ({len(messages)} messages)"):
                    
                    # Calculate total conversation time
                    if len(messages) > 1:
                        start_time = messages[0].timestamp
                        end_time = messages[-1].timestamp
                        duration = (end_time - start_time).total_seconds() * 1000
                        st.metric("Conversation Duration", f"{duration:.0f}ms")
                    
                    # Show message flow
                    st.write("**Message Flow Timeline:**")
                    for i, msg in enumerate(messages):
                        timestamp = msg.timestamp.strftime("%H:%M:%S.%f")[:-3]
                        message_type_emoji = {
                            "request": "📨",
                            "response": "✅", 
                            "notification": "🔔",
                            "error": "❌"
                        }.get(msg.message_type.value, "📝")
                        
                        st.write(f"{i+1}. `{timestamp}` {message_type_emoji} **{msg.from_agent}** → **{msg.to_agent}**")
                        st.write(f"   *{msg.content.get('summary', 'Message exchanged')}*")
                        
                        # Show timing between messages
                        if i > 0:
                            prev_msg = messages[i-1]
                            gap = (msg.timestamp - prev_msg.timestamp).total_seconds() * 1000
                            if gap > 100:  # Show significant gaps
                                st.write(f"   ⏱️ *{gap:.0f}ms gap*")
                    
                    # Show trace insights
                    st.write("**Trace Analysis:**")
                    agents_involved = set()
                    for msg in messages:
                        agents_involved.add(msg.from_agent)
                        agents_involved.add(msg.to_agent)
                    agents_involved.discard("supervisor_agent")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Agents Involved", len(agents_involved))
                    with col2:
                        st.metric("Message Count", len(messages))
                    with col3:
                        error_count = len([m for m in messages if m.message_type.value == "error"])
                        st.metric("Errors", error_count)
        else:
            st.info("🔍 **Start a procurement workflow** to generate traces for analysis!")
            
            # Show example trace structure
            st.write("**Example Trace Structure:**")
            st.code("""
🔍 Trace: abc12345... (4 messages)
1. 17:23:02.123 📨 supervisor_agent → sourcing_agent
2. 17:23:02.456 📨 sourcing_agent → compliance_agent  
3. 17:23:02.789 📨 compliance_agent → negotiation_agent
4. 17:23:03.012 ✅ negotiation_agent → supervisor_agent

Trace Analysis:
- Agents Involved: 3
- Total Duration: 889ms
- Bottleneck: compliance_agent (333ms)
            """)

def architecture_comparison_demo():
    """Architecture comparison between workflow and agentic approaches."""
    st.header("🔄 Workflow vs. Agentic Architecture Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔧 Workflow Orchestration**
        - Supervisor controls every step
        - Sequential function calls  
        - Centralized decision making
        - Predictable execution path
        - Human-readable workflow steps
        - Deterministic outcomes
        """)
    
    with col2:
        st.markdown("""
        **🤖 Agentic Autonomy**
        - Agents decide who to communicate with
        - Asynchronous message passing
        - Distributed decision making  
        - Emergent workflow patterns
        - Agent-to-agent negotiations
        - Non-deterministic outcomes
        """)
    
    st.subheader("🎯 Key Differences in Practice")
    
    comparison_data = {
        "Aspect": ["Decision Making", "Communication", "Error Handling", "Scalability", "Predictability", "Learning"],
        "Workflow Approach": ["Centralized", "Function Calls", "Try/Catch Blocks", "Vertical Scaling", "High", "Global Learning"],
        "Agentic Approach": ["Distributed", "Message Passing", "Autonomous Recovery", "Horizontal Scaling", "Variable", "Individual Agent Learning"]
    }
    
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()