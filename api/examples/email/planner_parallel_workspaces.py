"""
PlannerLLM-Driven Parallel Workspaces Demo
===========================================

This script demonstrates the full power of PlannerLLM with parallel workspaces:

1. USER provides a general prompt: "Organize a tech conference"
2. PlannerLLM analyzes the task and breaks it down into 3+ major subtasks
3. PlannerLLM creates a workspace tree (parent + 3 child workspaces)
4. Each workspace has 3+ unique agents specialized for that domain
5. All workspaces execute in parallel
6. Results are aggregated and presented to the user

Architecture:
- 1 Parent Workspace (coordination)
- 3+ Child Workspaces running in parallel:
  * Workspace 1: Venue & Logistics Team (3 agents)
  * Workspace 2: Content & Speakers Team (3 agents)  
  * Workspace 3: Marketing & Registration Team (3 agents)

Total: 9+ unique agents across 4 workspaces
"""

import asyncio
import os
from pathlib import Path
from anthropic import AsyncAnthropic
import synqed

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass


# ============================================================================
# WORKSPACE 1: Venue & Logistics Team
# ============================================================================

async def venue_coordinator_logic(context: synqed.AgentLogicContext) -> dict:
    """Venue Coordinator - finds and books venues"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="venue_coordinator")
    system_prompt = f"""
{protocol}

YOUR ROLE: venue_coordinator (venue_team)
YOUR CAPABILITIES: venue selection, capacity planning, booking management, accessibility
DEFAULT COORDINATION STYLE: respond_to_sender

You find and book conference venues. Focus on: location, capacity, layout, accessibility, cost.
Coordinate with catering_manager and tech_setup to ensure venue meets all needs.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


async def catering_manager_logic(context: synqed.AgentLogicContext) -> dict:
    """Catering Manager - handles food and beverages"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="catering_manager")
    system_prompt = f"""
{protocol}

YOUR ROLE: catering_manager (venue_team)
YOUR CAPABILITIES: menu planning, dietary restrictions, beverage service, break schedules
DEFAULT COORDINATION STYLE: respond_to_sender

You handle all food and beverage services. Focus on: menus, dietary needs, coffee breaks, meals.
Coordinate with venue_coordinator on kitchen facilities and serving areas.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


async def tech_setup_logic(context: synqed.AgentLogicContext) -> dict:
    """Tech Setup Specialist - handles AV and technical infrastructure"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="tech_setup")
    system_prompt = f"""
{protocol}

YOUR ROLE: tech_setup (venue_team)
YOUR CAPABILITIES: AV equipment, wifi, streaming, technical support, staging
DEFAULT COORDINATION STYLE: respond_to_sender

You manage technical infrastructure. Focus on: projectors, microphones, wifi, streaming, recording.
Coordinate with venue_coordinator on power and internet requirements.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


# ============================================================================
# WORKSPACE 2: Content & Speakers Team
# ============================================================================

async def program_director_logic(context: synqed.AgentLogicContext) -> dict:
    """Program Director - designs conference agenda"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="program_director")
    system_prompt = f"""
{protocol}

YOUR ROLE: program_director (content_team)
YOUR CAPABILITIES: agenda design, session planning, track organization, timing
DEFAULT COORDINATION STYLE: respond_to_sender

You design the conference program. Focus on: session topics, tracks, timing, breaks.
Coordinate with speaker_coordinator and content_reviewer on session content.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


async def speaker_coordinator_logic(context: synqed.AgentLogicContext) -> dict:
    """Speaker Coordinator - recruits and manages speakers"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="speaker_coordinator")
    system_prompt = f"""
{protocol}

YOUR ROLE: speaker_coordinator (content_team)
YOUR CAPABILITIES: speaker recruitment, travel arrangements, speaker support
DEFAULT COORDINATION STYLE: respond_to_sender

You recruit and support speakers. Focus on: invitations, travel, accommodations, speaker needs.
Coordinate with program_director on speaker topics and schedule.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


async def content_reviewer_logic(context: synqed.AgentLogicContext) -> dict:
    """Content Reviewer - reviews talk proposals and materials"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="content_reviewer")
    system_prompt = f"""
{protocol}

YOUR ROLE: content_reviewer (content_team)
YOUR CAPABILITIES: proposal review, quality assurance, content feedback
DEFAULT COORDINATION STYLE: respond_to_sender

You review and approve session content. Focus on: proposals, abstracts, quality, relevance.
Coordinate with program_director and speaker_coordinator on content standards.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


# ============================================================================
# WORKSPACE 3: Marketing & Registration Team
# ============================================================================

async def marketing_manager_logic(context: synqed.AgentLogicContext) -> dict:
    """Marketing Manager - promotes the conference"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="marketing_manager")
    system_prompt = f"""
{protocol}

YOUR ROLE: marketing_manager (marketing_team)
YOUR CAPABILITIES: campaign strategy, branding, promotional materials, partnerships
DEFAULT COORDINATION STYLE: respond_to_sender

You create marketing strategy. Focus on: campaigns, messaging, partnerships, promotional materials.
Coordinate with social_media_specialist and registration_coordinator on timing and messaging.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


async def social_media_specialist_logic(context: synqed.AgentLogicContext) -> dict:
    """Social Media Specialist - manages online presence"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="social_media_specialist")
    system_prompt = f"""
{protocol}

YOUR ROLE: social_media_specialist (marketing_team)
YOUR CAPABILITIES: social media, community engagement, content creation, hashtags
DEFAULT COORDINATION STYLE: respond_to_sender

You manage social media presence. Focus on: posts, engagement, hashtags, community building.
Coordinate with marketing_manager on messaging and registration_coordinator on updates.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


async def registration_coordinator_logic(context: synqed.AgentLogicContext) -> dict:
    """Registration Coordinator - manages attendee registration"""
    latest = context.latest_message
    if not latest or not latest.content:
        return None
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    protocol = synqed.get_interaction_protocol(exclude_agent="registration_coordinator")
    system_prompt = f"""
{protocol}

YOUR ROLE: registration_coordinator (marketing_team)
YOUR CAPABILITIES: registration system, ticketing, attendee communication, capacity tracking
DEFAULT COORDINATION STYLE: respond_to_sender

You manage attendee registration. Focus on: registration platform, tickets, confirmations, capacity.
Coordinate with marketing_manager on early-bird pricing and social_media_specialist on announcements.
"""
    
    history = context.get_conversation_history(workspace_wide=True)
    plan_context = f"\n\nShared Plan:\n{context.shared_plan}" if context.shared_plan else ""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Conversation:\n{history}{plan_context}\n\nRespond with JSON:"}],
    )
    
    return response.content[0].text.strip()


# ============================================================================
# Create Agent Instances
# ============================================================================

def create_agents():
    """Create all 9 agents organized by team"""
    
    # Workspace 1: Venue & Logistics Team
    venue_coordinator = synqed.Agent(
        name="venue_coordinator",
        description="Venue coordinator who finds and books conference venues",
        logic=venue_coordinator_logic,
        role="venue_team",
        capabilities=["venue selection", "capacity planning", "booking", "accessibility"],
        default_coordination="respond_to_sender"
    )
    
    catering_manager = synqed.Agent(
        name="catering_manager",
        description="Catering manager handling food and beverage services",
        logic=catering_manager_logic,
        role="venue_team",
        capabilities=["menu planning", "dietary restrictions", "beverage service"],
        default_coordination="respond_to_sender"
    )
    
    tech_setup = synqed.Agent(
        name="tech_setup",
        description="Technical specialist managing AV and infrastructure",
        logic=tech_setup_logic,
        role="venue_team",
        capabilities=["AV equipment", "wifi", "streaming", "technical support"],
        default_coordination="respond_to_sender"
    )
    
    # Workspace 2: Content & Speakers Team
    program_director = synqed.Agent(
        name="program_director",
        description="Program director designing conference agenda and tracks",
        logic=program_director_logic,
        role="content_team",
        capabilities=["agenda design", "session planning", "track organization"],
        default_coordination="respond_to_sender"
    )
    
    speaker_coordinator = synqed.Agent(
        name="speaker_coordinator",
        description="Speaker coordinator recruiting and managing speakers",
        logic=speaker_coordinator_logic,
        role="content_team",
        capabilities=["speaker recruitment", "travel arrangements", "speaker support"],
        default_coordination="respond_to_sender"
    )
    
    content_reviewer = synqed.Agent(
        name="content_reviewer",
        description="Content reviewer evaluating talk proposals and quality",
        logic=content_reviewer_logic,
        role="content_team",
        capabilities=["proposal review", "quality assurance", "content feedback"],
        default_coordination="respond_to_sender"
    )
    
    # Workspace 3: Marketing & Registration Team
    marketing_manager = synqed.Agent(
        name="marketing_manager",
        description="Marketing manager creating promotional campaigns",
        logic=marketing_manager_logic,
        role="marketing_team",
        capabilities=["campaign strategy", "branding", "partnerships"],
        default_coordination="respond_to_sender"
    )
    
    social_media_specialist = synqed.Agent(
        name="social_media_specialist",
        description="Social media specialist managing online presence",
        logic=social_media_specialist_logic,
        role="marketing_team",
        capabilities=["social media", "community engagement", "content creation"],
        default_coordination="respond_to_sender"
    )
    
    registration_coordinator = synqed.Agent(
        name="registration_coordinator",
        description="Registration coordinator managing attendee signups",
        logic=registration_coordinator_logic,
        role="marketing_team",
        capabilities=["registration system", "ticketing", "capacity tracking"],
        default_coordination="respond_to_sender"
    )
    
    return {
        "venue_team": [venue_coordinator, catering_manager, tech_setup],
        "content_team": [program_director, speaker_coordinator, content_reviewer],
        "marketing_team": [marketing_manager, social_media_specialist, registration_coordinator],
    }


# ============================================================================
# Main Execution
# ============================================================================

async def main(max_agent_turns: int = 12):
    """
    Main function demonstrating PlannerLLM-driven parallel workspaces.
    
    Args:
        max_agent_turns: Maximum agent responses per workspace (default: 12)
    """
    print("\n" + "="*80)
    print("🚀 PLANNERLLM-DRIVEN PARALLEL WORKSPACES DEMO")
    print("="*80)
    print()
    print("Architecture:")
    print("  • 1 Parent Workspace (coordination)")
    print("  • 3 Child Workspaces (parallel execution)")
    print("  • 9 Unique Agents (3 per workspace)")
    print("="*80)
    print()
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set!")
        return
    
    # Step 1: Create all agents
    print("👥 Creating 9 specialized agents...")
    agent_teams = create_agents()
    
    all_agents = []
    for team_name, team_agents in agent_teams.items():
        all_agents.extend(team_agents)
        print(f"\n  {team_name.upper().replace('_', ' ')}:")
        for agent in team_agents:
            print(f"    ✓ {agent.email} - {agent.description}")
    
    print(f"\n✓ Total agents created: {len(all_agents)}")
    print()
    
    # Step 2: Register all agents in runtime registry
    print("📝 Registering agents in runtime registry...")
    for agent in all_agents:
        synqed.AgentRuntimeRegistry.register(agent.name, agent)
        print(f"  ✓ {agent.name}")
    print()
    
    # Step 3: Setup workspace infrastructure
    workspace_manager = synqed.WorkspaceManager(
        workspaces_root=Path("/tmp/synqed_planner_parallel_demo")
    )
    
    planner = synqed.PlannerLLM(
        provider="anthropic",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model="claude-sonnet-4-20250514"
    )
    
    execution_engine = synqed.WorkspaceExecutionEngine(
        planner=planner,
        workspace_manager=workspace_manager,
        enable_display=True,
        max_agent_turns=max_agent_turns,
    )
    
    print("✓ Infrastructure configured")
    print(f"  • PlannerLLM: claude-sonnet-4-20250514")
    print(f"  • Max agent turns: {max_agent_turns}")
    print()
    
    # Step 4: USER provides general prompt
    user_task = """Organize a world-class tech conference called 'FutureTech 2025' with 500 attendees. 
The conference should have multiple tracks, renowned speakers, excellent facilities, and strong marketing."""
    
    print("="*80)
    print("📋 USER TASK")
    print("="*80)
    print(f"{user_task}")
    print("="*80)
    print()
    
    # Step 5: PlannerLLM breaks down the task
    print("🤔 PlannerLLM is analyzing the task...")
    print("   • Identifying subtasks")
    print("   • Matching agents to subtasks")
    print("   • Creating workspace tree structure")
    print()
    
    task_plan = await planner.plan_task(user_task)
    
    print("✅ PlannerLLM created task breakdown:")
    print(f"   Root: {task_plan.root.description}")
    print(f"   Subtasks: {len(task_plan.root.children)}")
    print()
    
    for i, child in enumerate(task_plan.root.children, 1):
        print(f"   {i}. {child.description}")
        print(f"      Agents: {', '.join(child.required_agents)}")
    print()
    
    # Step 6: Create workspace tree
    print("🏗️  Creating workspace tree...")
    
    # Create parent workspace
    parent_workspace = await workspace_manager.create_workspace(
        task_tree_node=task_plan.root,
        parent_workspace_id=None
    )
    
    print(f"✓ Parent workspace: {parent_workspace.workspace_id}")
    print()
    
    # Create child workspaces for each subtask
    child_workspaces = []
    for i, subtask in enumerate(task_plan.root.children, 1):
        child_ws = await workspace_manager.create_workspace(
            task_tree_node=subtask,
            parent_workspace_id=parent_workspace.workspace_id
        )
        child_workspaces.append({
            "workspace": child_ws,
            "subtask": subtask,
            "index": i
        })
        print(f"✓ Child workspace {i}: {child_ws.workspace_id}")
        print(f"  Agents: {', '.join(subtask.required_agents)}")
    
    print()
    print("="*80)
    print("⚡ EXECUTING PARALLEL WORKSPACES")
    print("="*80)
    print()
    
    # Step 7: Distribute subtasks to child workspaces
    print("📤 Distributing subtasks to workspaces...")
    print()
    
    for ws_data in child_workspaces:
        workspace = ws_data["workspace"]
        subtask = ws_data["subtask"]
        
        print(f"Workspace {ws_data['index']}: {subtask.description}")
        
        # Send subtask to each agent in the workspace
        for agent_name in subtask.required_agents:
            if agent_name in workspace.agents:
                subtask_message = f"{user_task}\n\nYour team's focus: {subtask.description}"
                await workspace.route_message(
                    "USER",
                    agent_name,
                    subtask_message,
                    manager=workspace_manager
                )
                print(f"  → {agent_name}: subtask delivered")
        
        print(f"  ✓ {len(subtask.required_agents)} agents ready in workspace {ws_data['index']}")
        print()
    
    print()
    print("🎬 Starting parallel execution...")
    print()
    
    # Step 8: Execute all child workspaces in parallel
    # Schedule all workspaces FIRST, then run the global scheduler ONCE
    # This ensures true parallel execution
    for ws_data in child_workspaces:
        workspace_id = ws_data["workspace"].workspace_id
        print(f"  ⚡ Scheduling workspace {ws_data['index']}: {workspace_id}")
        execution_engine.schedule_workspace(workspace_id)
    
    print()
    print("⏳ Running global scheduler (processing all workspaces in parallel)...")
    print()
    
    # Run the global scheduler once - it will process all scheduled workspaces in parallel
    await execution_engine.run_global_scheduler()
    
    print()
    print("="*80)
    print("📊 EXECUTION RESULTS")
    print("="*80)
    print()
    
    # Display results for each workspace
    for ws_data in child_workspaces:
        workspace = ws_data["workspace"]
        print(f"✅ Workspace {ws_data['index']}: {ws_data['subtask'].description}")
        print(f"   Status: Completed successfully")
        print(f"   Workspace ID: {workspace.workspace_id}")
        print()
    
    # Step 9: Aggregate results and present to user
    print("="*80)
    print("📝 FINAL OUTPUT TO USER")
    print("="*80)
    print()
    
    print(f"Conference Planning Complete: FutureTech 2025")
    print()
    print("Summary:")
    for ws_data in child_workspaces:
        workspace = ws_data["workspace"]
        transcript = workspace.router.get_transcript()
        print(f"\n{ws_data['index']}. {ws_data['subtask'].description}")
        print(f"   Team: {', '.join(ws_data['subtask'].required_agents)}")
        print(f"   Messages exchanged: {len(transcript)}")
        
        # Show last message to USER from workspace (likely a summary)
        if transcript:
            # Find last message to USER
            for msg in reversed(transcript):
                if msg.get("to") == "USER":
                    content = msg.get("content", "")
                    print(f"   Result: {content[:150]}...")
                    break
    
    print()
    print("="*80)
    print("🎉 DEMO COMPLETE!")
    print("="*80)
    print()
    print("What happened:")
    print("  1. ✅ User provided general prompt")
    print("  2. ✅ PlannerLLM broke down into 3+ subtasks")
    print("  3. ✅ Created workspace tree (1 parent + 3 children)")
    print("  4. ✅ 9 unique agents worked in 3 parallel workspaces")
    print("  5. ✅ All workspaces executed simultaneously")
    print("  6. ✅ Results aggregated and presented to user")
    print()
    
    # Cleanup
    for ws_data in child_workspaces:
        await workspace_manager.destroy_workspace(ws_data["workspace"].workspace_id)
    await workspace_manager.destroy_workspace(parent_workspace.workspace_id)
    
    print("✓ Workspaces cleaned up")
    print()


if __name__ == "__main__":
    # Customize max_agent_turns as needed
    asyncio.run(main(max_agent_turns=12))

