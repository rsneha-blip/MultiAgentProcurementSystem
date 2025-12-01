# MultiAgentProcurementSystem
Production-ready autonomous agents with distributed decision-making and emergent workflows that help with procurement process. The agents communicate peer-to-peer, make independent decisions, and coordinate complex business processes without central control. They help with identifying suppliers, verify compliance and assist with negotiating deals.

Unlike traditional workflow orchestration, these agents decide *who* to communicate with, *when* to escalate issues, and *how* to recover from failures, all without human programming of specific scenarios.
```bash
# See it in action - agents negotiating in real-time
git clone https://github.com/your-username/multiagent-procurement-system
cd multiagent-procurement-system
pip install -r requirements.txt
streamlit run demo/agentic_demo.py
```

**Perfect for:**

- 🏗️ **System Architects** evaluating distributed vs centralized approaches  
- 👩‍💻 **Developers** building multi-agent applications
- 📊 **Product Teams** understanding autonomous system capabilities
- 🧠 **AI Researchers** studying agent coordination patterns

## 🚀 Quick Start

### ⚡ 2-Minute Setup
```bash
# Clone and run
git clone https://github.com/your-username/distributed-ai-procurement
cd distributed-ai-procurement
pip install -r requirements.txt

# Launch the autonomous agent demo
streamlit run demo/agentic_demo.py
```

### 🎮 Try This First

1. **Submit a procurement request** with any values (manufacturing equipment, $75,000 budget)

2. **Watch the terminal** - you'll see agents communicating independently:
```
   📨 supervisor_agent → sourcing_agent | request
   🔍 sourcing_agent starting autonomous supplier search...
   🧠 sourcing_agent chose search strategy: specialized_suppliers
   📨 sourcing_agent → compliance_agent | request
   📋 compliance_agent starting autonomous compliance review...
   🧠 compliance_agent decision: conditional_approval
   📨 compliance_agent → negotiation_agent | request
   💼 negotiation_agent chose negotiation strategy: collaborative
   💰 negotiation_agent simulating negotiations...
   📨 negotiation_agent → supervisor_agent | response
```

3. **Refresh the demo** - agents make different decisions each time (success/failure varies)

4. **Check the "Live Agent Communication"** panel - see message routing in real-time

### 🎯 What You'll Notice

**Autonomous Behavior:**
- Agents choose their own communication strategies
- Different outcomes with identical inputs (realistic variability)
- Automatic error recovery when negotiations fail
- No central coordinator controlling the workflow

**vs. Traditional Workflow Systems:**
- No predefined execution sequence
- Agents adapt their approach based on conditions
- Emergent workflow patterns based on agent decisions

### 🔧 System Requirements
- Python 3.9+
- 4GB RAM (for agent communication and memory systems)
- Modern browser (for Streamlit interface)
