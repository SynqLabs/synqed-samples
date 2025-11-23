"""
Dynamic Agent Creation with Email Coordination
===============================================

This script demonstrates the most powerful feature of synqed: creating agents
dynamically from just a user task description.

The PlannerLLM analyzes the task and:
1. Breaks down the task hierarchically into subtasks
2. Determines what agent types are needed for each subtask
3. Creates agent specifications (blueprints) with capabilities
4. Agent specifications are turned into actual Agent instances
5. Agents are organized into workspaces
6. All agents coordinate via email-like addressing

No manual agent creation or task planning required! Just provide a task, 
and synqed builds the entire multi-agent system.

Example Tasks:
- "Plan a tech conference with 500 attendees"
- "Research competitor websites and compile a report"
- "Organize a fundraising event with multiple tracks"
- "Create a marketing campaign for a new product"
- "Develop a project plan for a software release"

The system will analyze the task, create specialized agents, and coordinate
their work automatically!
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


async def main(user_task: str, max_agent_turns: int = 15):
    """
    Main function demonstrating dynamic agent creation from a user task.
    
    Args:
        user_task: The user's task description
        max_agent_turns: Maximum agent responses before stopping
    """
    print("\n" + "="*80)
    print("🤖 DYNAMIC AGENT CREATION WITH EMAIL COORDINATION")
    print("="*80)
    print()
    print("This demo shows how synqed can dynamically create agents from a task.")
    print("No manual agent creation needed - just describe what you want!")
    print("="*80)
    print()
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set!")
        print("Please set your API key in .env file")
        return
    
    # Step 1: Display user task
    print("="*80)
    print("📋 USER TASK")
    print("="*80)
    print(f"{user_task}")
    print("="*80)
    print()
    
    # Step 2: Initialize PlannerLLM
    print("🧠 Initializing PlannerLLM...")
    planner = synqed.PlannerLLM(
        provider="anthropic",
        api_key=api_key,
        model="claude-sonnet-4-20250514"
    )
    print("✓ PlannerLLM initialized")
    print()
    
    # Step 3: Break down task FIRST, then create agent specifications
    print("🔍 Analyzing task structure...")
    print("   • Breaking down task hierarchically")
    print("   • Identifying required agent roles")
    print("   • Determining agent specifications")
    print()
    
    # This method does task breakdown FIRST, then creates agent SPECIFICATIONS based on requirements
    # Note: This creates specifications (blueprints), not actual Agent instances yet
    task_plan, agent_specs = await planner.plan_task_and_create_agent_specs(
        user_task=user_task,
        agent_provider="anthropic",
        agent_api_key=api_key,
        agent_model="claude-sonnet-4-20250514"
    )
    
    print("✅ Task breakdown created:")
    print(f"   Root: {task_plan.root.description}")
    print(f"   Subtasks: {len(task_plan.root.children)}")
    print()
    
    for i, child in enumerate(task_plan.root.children, 1):
        print(f"   {i}. {child.description}")
        print(f"      Agents: {', '.join(child.required_agents)}")
    print()
    
    print(f"✅ Created {len(agent_specs)} agent specifications based on task requirements:")
    print()
    
    for i, spec in enumerate(agent_specs, 1):
        print(f"   {i}. {spec['name']} ({spec['role']})")
        print(f"      Description: {spec['description']}")
        print(f"      Capabilities: {', '.join(spec['capabilities'])}")
        print()
    
    # Step 4: Create actual Agent instances from specifications
    print("👥 Creating Agent instances with email capabilities...")
    
    # This takes the specifications (blueprints) and creates actual Agent objects
    agents = synqed.create_agents_from_specs(agent_specs)
    
    for agent in agents:
        print(f"   ✓ {agent.email} - {agent.description}")
    
    print(f"\n✓ Total agents created: {len(agents)}")
    print()
    
    # Step 5: Register agents in runtime registry
    print("📝 Registering agents in runtime registry...")
    for agent in agents:
        synqed.AgentRuntimeRegistry.register(agent.name, agent)
        print(f"  ✓ {agent.name}")
    print()
    
    # Step 6: Setup workspace infrastructure and execute automatically
    print("🏗️  Setting up workspace infrastructure...")
    
    workspace_manager = synqed.WorkspaceManager(
        workspaces_root=Path("/tmp/synqed_dynamic_agents_demo")
    )
    
    execution_engine = synqed.WorkspaceExecutionEngine(
        planner=planner,
        workspace_manager=workspace_manager,
        enable_display=True,
        max_agent_turns=max_agent_turns,
    )
    
    print("✓ Infrastructure configured")
    print(f"  • WorkspaceManager: ready")
    print(f"  • ExecutionEngine: ready")
    print(f"  • Max agent turns: {max_agent_turns}")
    print()
    
    # Step 7: Execute task plan automatically (creates workspaces, distributes tasks, executes)
    print("="*80)
    print("⚡ EXECUTING TASK PLAN")
    print("="*80)
    print()
    print("The ExecutionEngine will now:")
    print("  1. Create workspaces from task plan")
    print("  2. Distribute tasks to agents")
    print("  3. Execute all workspaces in parallel")
    print()
    
    root_workspace, child_workspaces = await execution_engine.execute_task_plan(
        task_plan=task_plan,
        user_task=user_task
    )
    
    print()
    print("="*80)
    print("📊 EXECUTION RESULTS")
    print("="*80)
    print()
    
    # Display results
    if child_workspaces:
        for i, workspace in enumerate(child_workspaces, 1):
            # Find corresponding subtask
            subtask = task_plan.root.children[i-1] if i-1 < len(task_plan.root.children) else None
            
            print(f"✅ Workspace {i}: {subtask.description if subtask else 'N/A'}")
            print(f"   Status: Completed")
            print(f"   Workspace ID: {workspace.workspace_id}")
            
            # Show transcript summary
            transcript = workspace.router.get_transcript()
            print(f"   Messages exchanged: {len(transcript)}")
            
            # Show last message to USER (if any)
            for msg in reversed(transcript):
                if msg.get("to") == "USER":
                    content = msg.get("content", "")
                    if content and content != "[startup]":
                        print(f"   Final message: {content[:100]}...")
                        break
            print()
    else:
        print(f"✅ Root workspace: {root_workspace.workspace_id}")
        transcript = root_workspace.router.get_transcript()
        print(f"   Messages exchanged: {len(transcript)}")
        print()
    
    # Step 11: Summary
    print("="*80)
    print("🎉 DEMO COMPLETE!")
    print("="*80)
    print()
    print("What happened:")
    print(f"  1. ✅ User provided task: \"{user_task[:60]}...\"")
    print(f"  2. ✅ PlannerLLM broke down task hierarchically")
    print(f"  3. ✅ Created {len(agent_specs)} specialized agents based on task requirements")
    print(f"  4. ✅ Agents organized into {1 + len(child_workspaces)} workspace(s)")
    print(f"  5. ✅ Tasks automatically distributed to agents")
    print(f"  6. ✅ Workspaces executed in parallel")
    print(f"  7. ✅ Agents coordinated via email-like addressing")
    print()
    print("Key Innovation:")
    print("  • Task breakdown FIRST, then agents created based on needs!")
    print("  • No manual agent creation or task planning needed")
    print("  • Only creates exactly the agents required")
    print("  • Automatic task distribution and execution")
    print("  • Agents automatically coordinate and delegate")
    print("  • Scales from simple to complex multi-agent systems")
    print()
    
    # Cleanup
    print("🧹 Cleaning up workspaces...")
    for workspace in child_workspaces:
        await workspace_manager.destroy_workspace(workspace.workspace_id)
    await workspace_manager.destroy_workspace(root_workspace.workspace_id)
    print("✓ Workspaces cleaned up")
    print()


if __name__ == "__main__":
    # Example task - you can change this to any task!
    
    user_task = """Plan a tech conference called 'AI Summit 2025' with 500 attendees. 
The conference should include:
- Multiple speaker tracks on AI topics
- Networking sessions and workshops
- Vendor exhibition area
- Catering for all meals
- Online streaming for remote attendees
- A comprehensive schedule with timing for each session
"""
    
    # Alternative task examples:
    
    # Example 2: Marketing campaign
    # user_task = """Create a comprehensive marketing campaign for a new product launch. 
    # Include social media strategy, content calendar, email campaigns, and 
    # partnership outreach plan."""
    
    # Example 3: Project planning
    # user_task = """Develop a detailed project plan for building a mobile app. 
    # Include requirements gathering, design phase, development sprints, 
    # testing strategy, and deployment plan."""
    
    # Example 4: Event coordination
    # user_task = """Organize a virtual team offsite with sessions on:
    # - Q1 planning
    # - Team building activities  
    # - Technical workshops
    # Create a detailed agenda and coordination plan."""
    
    # Run the demo
    asyncio.run(main(user_task, max_agent_turns=20))

