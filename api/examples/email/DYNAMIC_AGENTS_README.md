# Dynamic Agent Creation with Email Coordination

## Overview

This example demonstrates the most powerful feature of synqed: **creating agents dynamically from just a user task description**. No manual agent creation required!

The PlannerLLM analyzes your task and:
1. ✅ Determines what agents are needed
2. ✅ Creates agent specifications with appropriate capabilities
3. ✅ Organizes agents into workspaces
4. ✅ All agents coordinate via email-like addressing

## What Makes This Special?

Traditional multi-agent frameworks require you to:
- Manually define each agent
- Write custom logic for each agent
- Configure agent interactions
- Set up communication protocols

**Synqed does all of this automatically!** Just describe what you want to accomplish, and synqed builds the entire multi-agent system for you.

## How It Works

### Step 1: Provide a Task
```python
user_task = """Plan a tech conference called 'AI Summit 2025' with 500 attendees. 
The conference should include:
- Multiple speaker tracks on AI topics
- Networking sessions and workshops
- Vendor exhibition area
- Catering for all meals
- Online streaming for remote attendees
"""
```

### Step 2: PlannerLLM Creates Agents
```python
planner = synqed.PlannerLLM(
    provider="anthropic",
    api_key=api_key,
    model="claude-sonnet-4-20250514"
)

# Dynamically create agent specifications
agent_specs = await planner.create_agents_from_task(
    user_task=user_task,
    provider="anthropic",
    api_key=api_key,
    model="claude-sonnet-4-20250514"
)
```

**Example Output:**
```json
[
  {
    "name": "conference_coordinator",
    "description": "Lead coordinator for overall project management",
    "capabilities": ["project_management", "coordination", "timeline_oversight"],
    "role": "coordination_team"
  },
  {
    "name": "venue_manager",
    "description": "Manages venue selection and logistics",
    "capabilities": ["venue_selection", "logistics", "vendor_management"],
    "role": "venue_team"
  },
  {
    "name": "speaker_coordinator",
    "description": "Handles speaker recruitment and scheduling",
    "capabilities": ["speaker_outreach", "scheduling", "content_curation"],
    "role": "content_team"
  }
]
```

### Step 3: Create Agent Instances
```python
# Convert specifications to Agent instances
agents = synqed.create_agents_from_specs(agent_specs)

# Each agent gets:
# - Email-like identity (name@role)
# - Generic LLM-powered logic
# - Capabilities-based coordination
# - Automatic team awareness
```

### Step 4: Register and Execute
```python
# Register agents
for agent in agents:
    synqed.AgentRuntimeRegistry.register(agent.name, agent)

# Create task plan and workspaces
task_plan = await planner.plan_task(user_task)

# Execute!
workspace_manager = synqed.WorkspaceManager()
execution_engine = synqed.WorkspaceExecutionEngine(
    planner=planner,
    workspace_manager=workspace_manager
)
```

## Running the Example

### Prerequisites

```bash
# Install synqed
pip install synqed

# Set API key
export ANTHROPIC_API_KEY="your-api-key"
```

### Run the Demo

```bash
cd synqed-samples/api/examples/email
python dynamic_agents_email.py
```

### Customize the Task

Edit the `user_task` variable in the script to try different scenarios:

```python
# Example 1: Software Development
user_task = "Build a full-stack web application with user authentication, database, and REST API"

# Example 2: Event Planning
user_task = "Organize a charity fundraising gala with entertainment, catering, and donor management"

# Example 3: Research Project
user_task = "Research and write a comprehensive report on the impact of AI on healthcare"

# Example 4: Marketing Campaign
user_task = "Create a multi-channel marketing campaign for a new product launch"
```

## Key Features

### 1. Automatic Agent Discovery
The PlannerLLM analyzes your task and determines what types of agents are needed. No manual configuration!

### 2. Capability-Based Coordination
Agents automatically discover each other's capabilities and coordinate accordingly:
```python
# Agent logic automatically includes team roster:
"""
TEAM MEMBERS (other agents in this workspace):
  - venue_manager: Manages venue selection and logistics
    Capabilities: venue_selection, logistics, vendor_management
  - speaker_coordinator: Handles speaker recruitment
    Capabilities: speaker_outreach, scheduling, content_curation
"""
```

### 3. Email-Like Addressing
Agents communicate using email-style addressing:
```json
{
  "send_to": "speaker_coordinator@content_team",
  "content": "Can you help recruit speakers for the AI ethics track?"
}
```

### 4. Hierarchical Workspaces
Complex tasks are automatically broken down into workspaces:
```
Root Workspace (coordination)
├── Workspace 1: Venue & Logistics Team
│   ├── venue_manager
│   └── catering_coordinator
├── Workspace 2: Content & Speakers Team
│   ├── speaker_coordinator
│   └── content_reviewer
└── Workspace 3: Marketing Team
    ├── marketing_manager
    └── social_media_specialist
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER TASK                            │
│   "Plan a tech conference with speakers and catering"        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      PLANNERLLM                              │
│  • Analyzes task requirements                                │
│  • Creates agent specifications                              │
│  • Determines workspace structure                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT FACTORY                              │
│  • Creates Agent instances from specs                        │
│  • Generates generic LLM-powered logic                       │
│  • Configures capabilities and roles                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              WORKSPACE EXECUTION ENGINE                      │
│  • Creates hierarchical workspaces                           │
│  • Routes messages between agents                            │
│  • Manages parallel execution                                │
│  • Aggregates results                                        │
└─────────────────────────────────────────────────────────────┘
```

## API Reference

### Creating Agent Specifications

```python
agent_specs = await planner.create_agents_from_task(
    user_task: str,              # Task description
    provider: str = "anthropic",  # LLM provider
    api_key: Optional[str] = None,  # API key (defaults to planner's)
    model: Optional[str] = None,    # Model name
) -> list[dict[str, Any]]
```

**Returns:** List of agent specifications, each containing:
- `name`: Agent identifier (snake_case)
- `description`: Agent purpose
- `capabilities`: List of skills
- `role`: Team/domain identifier
- `provider`: LLM provider
- `api_key`: API credentials
- `model`: Model name

### Creating Agents from Specifications

```python
# Single agent
agent = synqed.create_agent_from_spec(
    agent_spec: dict[str, Any],
    custom_instructions: str = ""
) -> Agent

# Multiple agents
agents = synqed.create_agents_from_specs(
    agent_specs: list[dict[str, Any]],
    custom_instructions: str = ""
) -> list[Agent]
```

### Generic Agent Logic

```python
logic_fn = synqed.create_generic_agent_logic(
    agent_name: str,
    agent_description: str,
    agent_capabilities: list[str],
    provider: str = "anthropic",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    custom_instructions: str = ""
)
```

## Example Tasks

### Simple Task (2-3 agents)
```python
"Research the top 10 programming languages and create a comparison report"
```

**Expected Agents:**
- research_specialist: Gathers data
- analyst: Compares and analyzes
- report_writer: Creates final report

### Medium Task (4-5 agents)
```python
"Plan a company team-building retreat with activities, accommodation, and meals"
```

**Expected Agents:**
- retreat_coordinator: Overall planning
- venue_scout: Finds accommodation
- activity_planner: Organizes activities
- catering_manager: Handles meals
- budget_controller: Manages costs

### Complex Task (6+ agents)
```python
"Launch a new mobile app with development, testing, marketing, and user support"
```

**Expected Agents:**
- project_manager: Coordinates teams
- developer: Builds the app
- qa_tester: Tests functionality
- ux_designer: Designs interface
- marketing_specialist: Promotes app
- support_coordinator: Handles users

## Configuration Options

### Execution Limits

```python
execution_engine = synqed.WorkspaceExecutionEngine(
    planner=planner,
    workspace_manager=workspace_manager,
    max_agent_turns=20,           # Max agent responses
    max_cycles=20,                # Max processing cycles
    max_events_per_cycle=50,      # Events per cycle
    enable_display=True,          # Real-time display
)
```

### Agent Configuration

```python
# Custom instructions for all agents
agents = synqed.create_agents_from_specs(
    agent_specs,
    custom_instructions="""
    Be concise and action-oriented.
    Always summarize your work before delegating.
    Flag any blockers immediately.
    """
)
```

## Benefits

### 1. Zero Boilerplate
No need to write custom agent logic or configure communication protocols.

### 2. Intelligent Coordination
Agents automatically discover each other's capabilities and coordinate effectively.

### 3. Scalable Architecture
Handles simple tasks with 2 agents or complex tasks with 10+ agents.

### 4. Production-Ready
Built-in error handling, message routing, and execution limits.

### 5. Flexible
Works with any LLM provider (Anthropic, OpenAI, etc.)

## Comparison with Manual Agent Creation

### Traditional Approach
```python
# Define each agent manually
async def venue_logic(context):
    # Custom logic for venue management
    # 50+ lines of code
    ...

async def speaker_logic(context):
    # Custom logic for speaker coordination
    # 50+ lines of code
    ...

# Repeat for each agent...
venue_agent = Agent(name="venue", logic=venue_logic, ...)
speaker_agent = Agent(name="speaker", logic=speaker_logic, ...)
# ...
```

**Total:** 500+ lines of boilerplate for 10 agents

### Dynamic Approach (This Example)
```python
# Just describe the task
agent_specs = await planner.create_agents_from_task(user_task)
agents = synqed.create_agents_from_specs(agent_specs)
```

**Total:** 2 lines, fully functional agents

## Limitations

1. **Generic Logic:** Agents use generic LLM-powered logic. For highly specialized tasks, manual agent creation may be better.

2. **API Costs:** Each agent uses LLM API calls. Set `max_agent_turns` to control costs.

3. **Task Complexity:** Very complex tasks may require task decomposition or multiple runs.

## Next Steps

- **Tutorial:** [Getting Started with Dynamic Agents](../../../docs/tutorials/dynamic_agents.md)
- **API Docs:** [PlannerLLM Reference](../../../docs/api/planner.md)
- **Examples:** Check out other email coordination examples in this directory

## Support

- **Issues:** [GitHub Issues](https://github.com/synqed/synqed-python/issues)
- **Docs:** [Full Documentation](https://synqed.dev/docs)
- **Community:** [Discord](https://discord.gg/synqed)

## License

MIT License - see [LICENSE](../../../../../LICENSE) for details.

