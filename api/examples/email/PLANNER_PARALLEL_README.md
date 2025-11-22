# PlannerLLM-Driven Parallel Workspaces

This example demonstrates the **full power** of combining PlannerLLM task delegation with parallel workspace execution. It showcases how a complex, real-world task can be automatically broken down and distributed across multiple specialized teams working simultaneously.

## Overview

**Scenario**: User asks to organize a world-class tech conference

**What Happens**:
1. 🧑 **USER** provides a general prompt: "Organize a tech conference"
2. 🤖 **PlannerLLM** analyzes and breaks it into 3+ major subtasks
3. 🏗️  **PlannerLLM** creates a workspace tree (1 parent + 3+ children)
4. 👥 **9+ Unique Agents** are assigned to workspaces (3+ per workspace)
5. ⚡ **Parallel Execution** - all workspaces run simultaneously
6. 📊 **Results Aggregated** and presented back to the user

## Architecture

```
                          ┌─────────────────┐
                          │  USER PROMPT    │
                          │  "Organize a    │
                          │ tech conference"│
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   PlannerLLM    │
                          │  Task Breakdown │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼────┐  ┌──────▼─────┐  ┌────▼──────┐
            │ Workspace 1│  │ Workspace 2│  │Workspace 3│
            │   VENUE    │  │  CONTENT   │  │ MARKETING │
            │ & LOGISTICS│  │ & SPEAKERS │  │& REGISTER │
            └────────────┘  └────────────┘  └───────────┘
                 │               │               │
        ┌────────┼────────┐     │      ┌────────┼────────┐
        │        │        │     │      │        │        │
    ┌───▼──┐ ┌──▼──┐ ┌───▼┐ ┌──▼──┐ ┌─▼──┐  ┌──▼──┐  ┌──▼──┐
    │Venue │ │Cater│ │Tech│ │Prog │ │Spkr│  │Mktg │  │Social│ │Reg│
    │Coord │ │Mgr  │ │Setup│ │Dir  │ │Coord│ │Mgr  │  │Media │ │Coord│
    └──────┘ └─────┘ └────┘ └─────┘ └────┘  └─────┘  └──────┘ └─────┘
```

## The 9 Specialized Agents

### Workspace 1: Venue & Logistics Team
1. **venue_coordinator@venue_team** - Finds and books conference venues
   - Capabilities: venue selection, capacity planning, booking, accessibility
   
2. **catering_manager@venue_team** - Handles food and beverage services
   - Capabilities: menu planning, dietary restrictions, beverage service
   
3. **tech_setup@venue_team** - Manages technical infrastructure
   - Capabilities: AV equipment, wifi, streaming, technical support

### Workspace 2: Content & Speakers Team
4. **program_director@content_team** - Designs conference agenda
   - Capabilities: agenda design, session planning, track organization
   
5. **speaker_coordinator@content_team** - Recruits and manages speakers
   - Capabilities: speaker recruitment, travel arrangements, speaker support
   
6. **content_reviewer@content_team** - Reviews talk proposals
   - Capabilities: proposal review, quality assurance, content feedback

### Workspace 3: Marketing & Registration Team
7. **marketing_manager@marketing_team** - Creates promotional campaigns
   - Capabilities: campaign strategy, branding, partnerships
   
8. **social_media_specialist@marketing_team** - Manages online presence
   - Capabilities: social media, community engagement, content creation
   
9. **registration_coordinator@marketing_team** - Manages attendee signups
   - Capabilities: registration system, ticketing, capacity tracking

## Requirements

```bash
pip install synqed anthropic python-dotenv
```

## Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

Or create a `.env` file in the parent directory:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Basic: Run the demo

```bash
python planner_parallel_workspaces.py
```

### Advanced: Customize max turns

Edit the script and change `max_agent_turns`:

```python
asyncio.run(main(max_agent_turns=15))  # Default is 12
```

## Example Output

```
================================================================================
🚀 PLANNERLLM-DRIVEN PARALLEL WORKSPACES DEMO
================================================================================

Architecture:
  • 1 Parent Workspace (coordination)
  • 3 Child Workspaces (parallel execution)
  • 9 Unique Agents (3 per workspace)
================================================================================

👥 Creating 9 specialized agents...

  VENUE TEAM:
    ✓ venue_coordinator@venue_team - Venue coordinator who finds...
    ✓ catering_manager@venue_team - Catering manager handling...
    ✓ tech_setup@venue_team - Technical specialist managing...

  CONTENT TEAM:
    ✓ program_director@content_team - Program director designing...
    ✓ speaker_coordinator@content_team - Speaker coordinator recruiting...
    ✓ content_reviewer@content_team - Content reviewer evaluating...

  MARKETING TEAM:
    ✓ marketing_manager@marketing_team - Marketing manager creating...
    ✓ social_media_specialist@marketing_team - Social media specialist...
    ✓ registration_coordinator@marketing_team - Registration coordinator...

✓ Total agents created: 9

================================================================================
📋 USER TASK
================================================================================
Organize a world-class tech conference called 'FutureTech 2025' with 500 
attendees. The conference should have multiple tracks, renowned speakers, 
excellent facilities, and strong marketing.
================================================================================

🤔 PlannerLLM is analyzing the task...
   • Identifying subtasks
   • Matching agents to subtasks
   • Creating workspace tree structure

✅ PlannerLLM created task breakdown:
   Root: Organize FutureTech 2025 Conference
   Subtasks: 3

   1. Venue and logistics coordination
      Agents: venue_coordinator, catering_manager, tech_setup

   2. Content and speaker management
      Agents: program_director, speaker_coordinator, content_reviewer

   3. Marketing and registration
      Agents: marketing_manager, social_media_specialist, registration_coordinator

🏗️  Creating workspace tree...
✓ Parent workspace: workspace_parent_abc123

✓ Child workspace 1: workspace_child_1_def456
  Agents: venue_coordinator, catering_manager, tech_setup

✓ Child workspace 2: workspace_child_2_ghi789
  Agents: program_director, speaker_coordinator, content_reviewer

✓ Child workspace 3: workspace_child_3_jkl012
  Agents: marketing_manager, social_media_specialist, registration_coordinator

================================================================================
⚡ EXECUTING PARALLEL WORKSPACES
================================================================================

📤 Distributing subtasks to workspaces...
  ✓ Workspace 1: 3 agents activated
  ✓ Workspace 2: 3 agents activated
  ✓ Workspace 3: 3 agents activated

🎬 Starting parallel execution...

💬 venue_coordinator: Let me start by identifying suitable venues...
💬 program_director: I'll design a multi-track agenda...
💬 marketing_manager: I'll create a comprehensive marketing strategy...

💬 catering_manager: I'll coordinate with venue_coordinator on kitchen...
💬 speaker_coordinator: Working with program_director to identify...
💬 social_media_specialist: Building on marketing_manager's strategy...

💬 tech_setup: Based on venue_coordinator's selection, I'll plan AV...
💬 content_reviewer: Reviewing proposed sessions with program_director...
💬 registration_coordinator: Setting up registration flow based on...

... [multiple exchanges within each workspace] ...

================================================================================
📊 EXECUTION RESULTS
================================================================================

✅ Workspace 1: Venue and logistics coordination
   Status: Completed successfully

✅ Workspace 2: Content and speaker management
   Status: Completed successfully

✅ Workspace 3: Marketing and registration
   Status: Completed successfully

================================================================================
📝 FINAL OUTPUT TO USER
================================================================================

Conference Planning Complete: FutureTech 2025

Summary:

1. Venue and logistics coordination
   Team: venue_coordinator, catering_manager, tech_setup
   Messages exchanged: 18
   Result: Secured downtown convention center with 500-person capacity, 
   planned 3 meals and breaks, configured AV for 3 simultaneous tracks...

2. Content and speaker management
   Team: program_director, speaker_coordinator, content_reviewer
   Messages exchanged: 15
   Result: Created 3-track agenda with 24 sessions, confirmed 18 speakers,
   reviewed all proposals for quality and relevance...

3. Marketing and registration
   Team: marketing_manager, social_media_specialist, registration_coordinator
   Messages exchanged: 16
   Result: Launched multi-channel campaign, created social media presence,
   set up registration with early-bird pricing...

================================================================================
🎉 DEMO COMPLETE!
================================================================================

What happened:
  1. ✅ User provided general prompt
  2. ✅ PlannerLLM broke down into 3+ subtasks
  3. ✅ Created workspace tree (1 parent + 3 children)
  4. ✅ 9 unique agents worked in 3 parallel workspaces
  5. ✅ All workspaces executed simultaneously
  6. ✅ Results aggregated and presented to user
```

## How It Works

### 1. Task Decomposition (PlannerLLM)

The PlannerLLM analyzes the user's prompt and:
- Identifies major subtasks (venue, content, marketing)
- Determines which agents are needed for each subtask
- Creates a hierarchical task tree structure
- Assigns agents to appropriate workspaces
- **Ensures minimum 2 agents per workspace** for collaboration

```python
task_plan = await planner.plan_task(user_task)
```

### 2. Workspace Tree Creation

The framework creates a tree of workspaces:
- **Parent Workspace**: High-level coordination
- **Child Workspaces**: Specialized team execution

```python
# Create parent
parent_workspace = await workspace_manager.create_workspace(
    task_tree_node=task_plan.root,
    parent_workspace_id=None
)

# Create children
for subtask in task_plan.root.children:
    child_ws = await workspace_manager.create_workspace(
        task_tree_node=subtask,
        parent_workspace_id=parent_workspace.workspace_id
    )
```

### 3. Parallel Execution

All child workspaces execute simultaneously using the global scheduler:

```python
# Schedule all workspaces first
for ws_data in child_workspaces:
    execution_engine.schedule_workspace(ws_data["workspace"].workspace_id)

# Run the global scheduler once - processes all workspaces in parallel
await execution_engine.run_global_scheduler()
```

**Why this pattern?** The global scheduler is designed to execute multiple workspaces concurrently. Calling `run()` multiple times would cause sequential execution. Instead, schedule all workspaces first, then run the scheduler once.

### 4. Agent Coordination

Within each workspace, agents:
- Receive their subtask from USER
- Coordinate with teammates using the Global Interaction Protocol
- Share information via workspace-wide conversation history
- Report results back to USER

### 5. Result Aggregation

After all workspaces complete:
- Results from each workspace are collected
- Summaries are generated
- Final output is presented to the user

## Key Features

- ✅ **9+ Unique Agents** - Each with specialized capabilities
- ✅ **3+ Parallel Workspaces** - True concurrent execution
- ✅ **PlannerLLM Integration** - Automatic task breakdown with minimum 2 agents per workspace
- ✅ **Hierarchical Structure** - Parent + child workspaces
- ✅ **Email Addressing** - `name@role` format for all agents
- ✅ **Auto-Coordination** - Global Interaction Protocol
- ✅ **Workspace Isolation** - Each team has independent context
- ✅ **Result Aggregation** - Automatic summary generation

## Customization

### Change the User Task

Edit the `user_task` variable:

```python
user_task = """Plan a music festival with 10,000 attendees, 
including stage setup, artist booking, and ticketing."""
```

### Add More Agents

1. Create new agent logic functions:

```python
async def new_agent_logic(context: synqed.AgentLogicContext) -> dict:
    # Your logic here
    pass
```

2. Add to `create_agents()`:

```python
new_agent = synqed.Agent(
    name="new_agent",
    description="...",
    logic=new_agent_logic,
    role="team_name",
    capabilities=["cap1", "cap2"],
)
```

### Adjust Workspace Count

Modify the PlannerLLM's task breakdown by changing the prompt or adjusting:

```python
task_plan = await planner.plan_task(
    task_description=user_task,
    available_agents=[...],
    max_depth=3  # Add more levels
)
```

### Change AI Model

Edit the model in each agent's logic function:

```python
response = await client.messages.create(
    model="claude-opus-4-20250514",  # Different model
    max_tokens=500,  # More tokens
    # ...
)
```

## Benefits

### 1. Scalability
- Handles complex, multi-faceted tasks
- Easily add more agents and workspaces
- Distributes work across parallel teams

### 2. Specialization
- Each agent has focused expertise
- Teams are organized by domain
- No single agent needs to know everything

### 3. Efficiency
- Parallel execution maximizes throughput
- Independent workspaces avoid bottlenecks
- Agents coordinate within their teams

### 4. Flexibility
- PlannerLLM adapts to different tasks
- Dynamic agent assignment based on capabilities
- Hierarchical structure supports nested complexity

### 5. Real-World Applicability
- Mimics how human organizations work
- Demonstrates production-ready patterns
- Scales from simple to complex scenarios

## Comparison with Other Examples

| Feature | Single Workspace | Parallel Workspaces | **Planner Parallel** |
|---------|------------------|---------------------|---------------------|
| Agents | 3 | 3 | **9+** |
| Workspaces | 1 | 3 | **4+ (1 parent + 3+ children)** |
| Task Breakdown | Manual | Manual | **Automatic (PlannerLLM)** |
| Execution | Sequential | Parallel | **Parallel** |
| Hierarchy | Flat | Flat | **Tree Structure** |
| Coordination | Protocol | None | **Protocol + Planner** |
| Use Case | Simple collab | Independent convos | **Complex projects** |

## Use Cases

This pattern is ideal for:

- 🎯 **Event Planning** - Venues, content, marketing
- 🏗️  **Product Development** - Design, engineering, marketing
- 📚 **Content Production** - Writing, editing, publishing
- 🏥 **Healthcare** - Diagnosis, treatment, coordination
- 💼 **Business Operations** - Sales, operations, support
- 🎓 **Education** - Curriculum, instruction, assessment

## Technical Notes

### Workspace Isolation
- Each child workspace maintains independent state
- Agents in different workspaces don't directly interact
- Results are aggregated at the parent level

### Agent Registry
- All agents must be registered before execution
- PlannerLLM queries the registry for available agents
- Registry uses agent names (not email addresses)

### Agent Assignment Constraints
- **Minimum 2 agents per workspace**: PlannerLLM is configured to assign at least 2 agents to each subtask/workspace
- This enables collaboration and coordination within each team
- Agents are paired based on complementary capabilities
- Single-agent workspaces are avoided to encourage interaction

### Message Routing
- Within workspace: by agent name
- Cross-workspace: not supported (by design)
- To user: via "USER" recipient

### Error Handling
- Each workspace execution is wrapped in try-catch
- Failed workspaces don't block others
- Errors are reported in the final summary

## Troubleshooting

### PlannerLLM not finding agents
**Solution**: Ensure all agents are registered before calling `plan_task()`:
```python
for agent in all_agents:
    synqed.AgentRuntimeRegistry.register(agent.name, agent)
```

### Workspaces not executing in parallel
**Solution**: Check that you're using `asyncio.gather()` correctly:
```python
results = await asyncio.gather(*[task["task"] for task in execution_tasks])
```

### Agents not coordinating
**Solution**: Verify that agents have `workspace_wide=True` in history:
```python
history = context.get_conversation_history(workspace_wide=True)
```

### Out of API quota
**Solution**: Reduce `max_agent_turns` or use a cheaper model:
```python
asyncio.run(main(max_agent_turns=6))  # Fewer turns
```

## License

See the main LICENSE file in the repository root.

## Next Steps

- Try creating your own multi-workspace scenarios
- Experiment with different agent specializations
- Build hierarchies with 3+ levels of workspaces
- Integrate with real APIs and tools
- Add persistence and resumability

---

**Ready to build something amazing?** Run the demo and watch 9 agents collaborate across 3 parallel workspaces! 🚀

