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

- **System Architects** evaluating distributed vs centralized approaches  
- **Developers** building multi-agent applications
- **Product Teams** understanding autonomous system capabilities
- **AI Researchers** studying agent coordination patterns

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
   supervisor_agent → sourcing_agent | request
   sourcing_agent starting autonomous supplier search...
   sourcing_agent chose search strategy: specialized_suppliers
   sourcing_agent → compliance_agent | request
   compliance_agent starting autonomous compliance review...
   compliance_agent decision: conditional_approval
   compliance_agent → negotiation_agent | request
   negotiation_agent chose negotiation strategy: collaborative
   negotiation_agent simulating negotiations...
   negotiation_agent → supervisor_agent | response
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

## 🏗️ Agent Architecture

### Core Philosophy: Distributed Intelligence

Traditional AI systems use **centralized orchestration** - a supervisor controls every step. This system demonstrates **distributed decision-making** where autonomous agents coordinate through message-passing.
```
Traditional Approach:          Distributed Agent Approach:
┌─────────────┐                ┌─────────┐    ┌─────────┐
│ Supervisor  │                │ Agent A │◄──►│ Agent B │
│ Controls    │                │ Decides │    │ Decides │
│ Everything  │                │ Autonomy│    │ Autonomy│
└─────────────┘                └─────────┘    └─────────┘
```

### 🤖 Agent Autonomy Principles

#### Independent Decision-Making
Each agent operates autonomously with its own:
- **Strategy selection**: Agents choose their approach (collaborative, competitive, adaptive)
- **Communication routing**: Agents decide who to contact next
- **Error handling**: Agents attempt recovery without central intervention
- **Learning adaptation**: Agents improve based on their experience

#### Message-Passing Communication 
```python
# Agents communicate peer-to-peer, not through central dispatcher
await self.send_message(
    to_agent="compliance_agent",
    content={"suppliers": suppliers, "requirements": requirements},
    message_type=MessageType.REQUEST
)
```

#### Emergent Workflows
No predefined workflow sequences - patterns emerge from agent interactions:
- **Success path**: sourcing → compliance → negotiation → completion
- **Failure recovery**: negotiation failure → supervisor → expanded search → retry
- **Escalation patterns**: agents autonomously escalate complex decisions

### 🔄 Message Bus Architecture

Central message bus enables autonomous communication without tight coupling:
```
┌─────────────────────────────────────────────────────────────┐
│                    Message Bus                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Sourcing   │  │ Compliance  │  │ Negotiation │          │
│  │   Agent     │  │    Agent    │  │    Agent    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                  ┌─────────────┐                            │
│                  │ Supervisor  │                            │
│                  │   Agent     │                            │
│                  └─────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- **Loose coupling**: Agents don't need to know about each other's internal logic
- **Dynamic routing**: Messages route based on content and context
- **Observability**: Complete audit trail of all agent communications
- **Scalability**: Easy to add new agent types without system changes

### 🧠 Distributed vs Centralized Trade-offs

| Aspect              | Centralized Control                  | Distributed Agents              | Best For                         |
|---------------------|--------------------------------------|---------------------------------|----------------------------------|
| **Predictability**  | High - deterministic flows           | Variable - emergent patterns    | Compliance vs Innovation         |
| **Debugging**       | Easier - single control point        | Harder - trace conversations    | Simple vs Complex systems        |
| **Scalability**     | Vertical - more powerful coordinator | Horizontal - add more agents    | Load vs Features                 |
| **Adaptability**    | Limited - predefined responses       | High - agents learn and adapt   | Stable vs Dynamic requirements   |
| **Fault Tolerance** | Single point of failure              | Resilient - agents compensate   | Critical vs Experimental systems |
| **Development**     | Faster - centralized logic           | Slower - distributed complexity | Prototypes vs Production         |

### 💡 When to Choose Agent Autonomy

**✅ Ideal Scenarios:**
- **Uncertain environments** where requirements change frequently
- **Complex decision trees** with many interdependent factors
- **High-volume processing** requiring parallel decision-making
- **Learning systems** that improve performance over time
- **Distributed teams** building and maintaining different components

**⚠️ Consider Alternatives:**
- **Regulatory compliance** requiring deterministic audit trails
- **Simple workflows** with well-defined sequential steps
- **Teams new to distributed systems** (learning curve)
- **Systems requiring immediate consistency** across all decisions

### 🔍 Observable Distributed Behavior

The system provides complete visibility into autonomous agent behavior:

- **Message flow tracking**: See exactly how agents route communications
- **Decision reasoning**: Each agent explains why it chose specific actions  
- **Performance metrics**: Measure agent decision speed and success rates
- **Learning progression**: Watch agents improve recommendations over time
- **Failure analysis**: Understand how agents recover from unexpected situations

This transparency makes distributed agent systems debuggable and trustworthy in production environments.

## 💻 Live Demo

### 🎮 Interactive Agent Communication

Watch autonomous agents negotiate and coordinate in real-time. Each agent makes independent decisions, creating unique procurement workflows every time.

![Agent Communication Demo](docs/images/agent-demo.gif)
*Agents communicating autonomously - no central control*

### 🔄 Autonomous Procurement Workflow

#### **Submit a Request**
```bash
streamlit run demo/agentic_demo.py
# Fill out: Manufacturing Equipment, $75,000, Medium Urgency
```

#### **Watch Agents Work**
**Terminal Output - Live Agent Decisions:**
```
🎯 supervisor_agent initiating autonomous procurement workflow
📨 MESSAGE: supervisor_agent → sourcing_agent | request
🔍 sourcing_agent starting autonomous supplier search...
🧠 sourcing_agent chose search strategy: specialized_suppliers
✅ sourcing_agent satisfied with 1 suppliers found
📋 sourcing_agent autonomously routing to compliance check
📨 MESSAGE: sourcing_agent → compliance_agent | request
📋 compliance_agent starting autonomous compliance review...
🧠 compliance_agent decision: conditional_approval
📨 MESSAGE: compliance_agent → negotiation_agent | request
💼 negotiation_agent starting autonomous negotiation...
🧠 negotiation_agent chose negotiation strategy: collaborative
💰 negotiation_agent simulating negotiations...
   💵 TechParts Global: successful - 6.3% savings
📨 MESSAGE: negotiation_agent → supervisor_agent | response
✅ procurement completed successfully!
```

#### **Demo Interface Features**
- **Live Agent Status** - See which agents are active and their current tasks
- **Message Timeline** - Real-time communication flow between agents
- **Decision Explanations** - Each agent explains its reasoning
- **Performance Metrics** - Success rates, timing, savings achieved

### 🎯 Real-time Decision Visualization

**Agent Communication Panel:**
```
Recent Agent Communications:
📨 17:22:48 supervisor_agent → sourcing_agent: New procurement request
📨 17:22:48 sourcing_agent → compliance_agent: Found 1 suppliers for review  
📨 17:22:48 compliance_agent → negotiation_agent: Compliance approved 1 suppliers
✅ 17:22:48 negotiation_agent → supervisor_agent: Successfully negotiated 6.3% savings
```

**Procurement History:**
- ✅ **Success**: TechParts Global selected, 6.3% savings
- ⚠️ **Market Limitations**: No suitable suppliers found, business guidance provided
- 🔄 **Recovery**: Initial negotiation failed, expanded search successful

### 🧪 Experiment with Agent Behavior

**Try Different Scenarios:**
1. **Low Budget** ($15,000) - See simplified workflows
2. **High Budget** ($100,000) - Observe complex negotiations
3. **Urgent Requests** - Watch agents prioritize speed over cost
4. **Multiple Submissions** - See how outcomes vary with identical inputs

**Expected Variations:**
- **Success rates** fluctuate realistically (60-80%)
- **Agent strategies** adapt based on budget and urgency
- **Recovery patterns** emerge when primary approaches fail
- **Learning effects** - performance improves with more data
