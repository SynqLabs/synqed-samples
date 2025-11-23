"""
Dynamic Agent Creation with Email Coordination + Global MCP Tools
==================================================================

This script demonstrates the most powerful feature of synqed: creating agents
dynamically from just a user task description, with full access to external
services via the Global MCP Server.

The PlannerLLM analyzes the task and:
1. Breaks down the task hierarchically into subtasks
2. Determines what agent types are needed for each subtask
3. Creates agent specifications (blueprints) with capabilities
4. Agent specifications are turned into actual Agent instances
5. Agents are organized into workspaces
6. All agents coordinate via email-like addressing
7. ALL agents have access to Global MCP tools (Zoom, Salesforce, Beautiful)

No manual agent creation or task planning required! Just provide a task, 
and synqed builds the entire multi-agent system with full external service access.

Available MCP Tools for ALL Agents:
- Zoom: create_meeting, list_meetings, get_meeting, delete_meeting
# - Salesforce: query, update_lead, create_lead, get_opportunity, get_lead  # COMMENTED OUT
# - Beautiful: scrape, extract, summarize (web content extraction)  # COMMENTED OUT

Example Tasks:
- "Plan a tech conference with 500 attendees and schedule all speaker meetings via Zoom"
# - "Research competitor websites and create Salesforce leads for each"  # COMMENTED OUT
# - "Query Salesforce for hot leads and schedule follow-up Zoom meetings"  # COMMENTED OUT
# - "Scrape product pricing from competitor sites and update our CRM"  # COMMENTED OUT
- "Organize a fundraising event and coordinate via Zoom meetings"

The system will analyze the task, create specialized agents, and they can all
use Zoom tools automatically!
# Note: Salesforce and Beautiful tools are currently commented out
"""

import asyncio
import os
import sys
from pathlib import Path
from anthropic import AsyncAnthropic
import synqed
import json as json_lib

# Add synqed-python to path for MCP imports
synqed_python_path = Path(__file__).parent.parent.parent.parent.parent / "synqed-python"
if synqed_python_path.exists():
    sys.path.insert(0, str(synqed_python_path / "src"))
    sys.path.insert(0, str(synqed_python_path))

# Import MCP components
try:
    from synqed_mcp.client import RemoteMCPClient, LocalMCPClient
    from synqed_mcp.integrate.injector import create_mcp_middleware
    HAS_MCP = True
except ImportError as e:
    print(f"⚠️  MCP not available: {e}")
    print("    Install with: pip install -e synqed-python")
    HAS_MCP = False

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass


# Global MCP call tracker
MCP_CALL_LOG = []

def log_mcp_call(agent_name: str, tool: str, arguments: dict, result: dict):
    """Track MCP calls made during execution."""
    MCP_CALL_LOG.append({
        "agent": agent_name,
        "tool": tool,
        "arguments": arguments,
        "result": result,
        "status": result.get("status", "unknown")
    })
    
    # Also print to console for real-time visibility
    status_icon = "✅" if result.get("status") == "success" else "❌"
    print(f"[MCP CALL] {status_icon} agent={agent_name} tool={tool} status={result.get('status', 'unknown')}")


class MCPClientLogger:
    """Wrapper that logs all MCP calls."""
    
    def __init__(self, mcp_client, agent_name: str):
        self._client = mcp_client
        self._agent_name = agent_name
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call tool and log the call."""
        result = await self._client.call_tool(tool_name, arguments)
        
        # Log the call
        log_mcp_call(
            agent_name=self._agent_name,
            tool=tool_name,
            arguments=arguments,
            result=result
        )
        
        return result
    
    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped client."""
        return getattr(self._client, name)


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
    
    # Step 4.5: Attach Global MCP Server capability to all agents (UPDATED!)
    if HAS_MCP:
        print("🔧 Attaching Global MCP Server access to all agents...")
        print("   This enables ALL agents to use Zoom tools!")
        print("   (Salesforce and Beautiful are currently commented out)")
        print()
        
        # Global MCP Server endpoint - Cloud only (Fly.io deployment)
        # IMPORTANT: Set SYNQ_GLOBAL_MCP_ENDPOINT to your deployed Fly.io URL
        # Example: export SYNQ_GLOBAL_MCP_ENDPOINT=https://synq-mcp-yourname.fly.dev
        mcp_endpoint = os.getenv("SYNQ_GLOBAL_MCP_ENDPOINT")
        
        if not mcp_endpoint:
            print("   ⚠️  SYNQ_GLOBAL_MCP_ENDPOINT not set!")
            print()
            print("   📋 To use Global MCP Server, you need to:")
            print("      1. Deploy the server to Fly.io:")
            print("         cd synq-mcp-server")
            print("         fly apps create synq-mcp-yourname")
            print("         ./deploy.sh")
            print()
            print("      2. Set the endpoint environment variable:")
            print("         export SYNQ_GLOBAL_MCP_ENDPOINT=https://synq-mcp-yourname.fly.dev")
            print()
            print("      3. Run this script again")
            print()
            print("   ⚠️  Continuing without MCP tools - agents will work but can't use external services")
            print()
            return
        
        print(f"   • Global MCP Server: {mcp_endpoint}")
        print(f"   • Available Tools: Zoom (Salesforce and Beautiful commented out)")
        print()
        
        # Check server connectivity and list available tools
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                # First check health
                health_response = await client.get(f"{mcp_endpoint}/health")
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    print(f"   ✅ Connected to Global MCP Server!")
                    print(f"   • Server status: {health_data.get('status', 'unknown')}")
                    
                    # Show service configuration
                    services = health_data.get('services', {})
                    configured = [k for k, v in services.items() if v == 'configured']
                    if configured:
                        print(f"   • Configured services: {', '.join(configured)}")
                    
                    # List tools
                    tools_response = await client.get(f"{mcp_endpoint}/mcp/tools")
                    if tools_response.status_code == 200:
                        tools_data = tools_response.json()
                        print(f"   • Total tools available: {tools_data.get('count', 0)}")
                        print()
                        
                        # Group tools by namespace
                        tools = tools_data.get('tools', [])
                        namespaces = {}
                        for tool in tools:
                            namespace = tool['name'].split('.')[0]
                            if namespace not in namespaces:
                                namespaces[namespace] = []
                            namespaces[namespace].append(tool['name'])
                        
                        for namespace, tool_names in namespaces.items():
                            print(f"   • {namespace.upper()}: {len(tool_names)} tools")
                            for tool_name in tool_names:
                                print(f"     - {tool_name}")
                        print()
                else:
                    raise Exception(f"Server returned {health_response.status_code}")
                    
        except Exception as e:
            print(f"   ⚠️  Could not connect to Global MCP Server at {mcp_endpoint}")
            print(f"   ⚠️  Error: {e}")
            print()
            print(f"   💡 The Global MCP Server needs to be deployed to Fly.io:")
            print(f"      1. Navigate to synq-mcp-server directory")
            print(f"      2. Run: ./deploy.sh")
            print(f"      3. Or manually: fly deploy")
            print()
            print(f"   💡 Alternatively, set SYNQ_GLOBAL_MCP_ENDPOINT to your deployed server:")
            print(f"      export SYNQ_GLOBAL_MCP_ENDPOINT=https://your-server.fly.dev")
            print()
            print(f"   ⚠️  Continuing without MCP tools - agents will work but can't use external services")
            print()
            
            # Don't return - still attach middleware but tools will fail gracefully
            # This allows agents to continue working without external service access
        
        # Create MCP middleware that connects to Global MCP Server
        mcp_middleware = create_mcp_middleware(
            router=None,  # Not needed for global MCP
            a2a_client=None,  # Not needed for global MCP
            mode="cloud",
            endpoint=f"{mcp_endpoint}/mcp"
        )
        
        # Attach MCP to all agents with logging wrapper
        for agent in agents:
            mcp_middleware.attach(agent)
            
            # Wrap the agent's logic to inject logging MCP client
            if hasattr(agent, 'logic'):
                original_logic = agent.logic
                agent_name = agent.name
                
                # Create closure that captures agent_name
                def make_logged_logic(orig_logic, a_name):
                    async def logged_logic(context):
                        # Wrap the MCP client with logger
                        if hasattr(context, 'mcp'):
                            context.mcp = MCPClientLogger(context.mcp, a_name)
                        return await orig_logic(context)
                    return logged_logic
                
                agent.logic = make_logged_logic(original_logic, agent_name)
            
            print(f"   ✅ {agent.name} - Global MCP access enabled")
        
        print()
        print(f"✅ All {len(agents)} agents now have Global MCP capability!")
        print("   Agents can call ANY tool via: await context.mcp.call_tool(tool_name, arguments)")
        print()
        print("   Example tool calls:")
        print("     • await context.mcp.call_tool('zoom.create_meeting', {...})")
        print("     # • await context.mcp.call_tool('salesforce.query', {...})  # COMMENTED OUT")
        print("     # • await context.mcp.call_tool('beautiful.scrape', {...})  # COMMENTED OUT")
        print()
        print(f"   All calls forward to: {mcp_endpoint}")
        print("   MCP calls will be logged in real-time during execution")
        print()
        
        # Store endpoint for later use
        mcp_endpoint_for_demo = mcp_endpoint
    else:
        print("⚠️  MCP not available - agents will work without external service tools")
        print("    Install synqed-python MCP support to enable Zoom/Salesforce/Beautiful")
        print()
        mcp_endpoint_for_demo = None
    
    # Step 4.75: Demonstrate Global MCP capability with explicit calls (UPDATED!)
    if HAS_MCP and len(agents) > 0 and mcp_endpoint_for_demo:
        print("=" * 80)
        print("🧪 GLOBAL MCP SERVER DEMONSTRATION")
        print("=" * 80)
        print()
        print("Testing Global MCP tools before workspace execution...")
        print("This demonstrates that ALL agents can use external services!")
        print()
        
        # Pick the first agent to demonstrate MCP
        demo_agent = agents[0]
        print(f"Demo agent: {demo_agent.name}")
        print(f"MCP Server: {mcp_endpoint_for_demo}")
        print()
        
        # Create a test MCP client
        test_mcp_client = RemoteMCPClient(
            agent_name=demo_agent.name,
            endpoint=f"{mcp_endpoint_for_demo}/mcp"
        )
        
        # Test 1: Zoom - Create Meeting
        try:
            print("📞 Test 1: Zoom - Create Meeting")
            print("-" * 60)
            test_args = {
                "topic": "MCP Demo Meeting - Dynamic Agents",
                "start_time": "2025-11-25T15:00:00Z",
                "duration": 30
            }
            print(f"Tool: zoom.create_meeting")
            print(f"Arguments: {json_lib.dumps(test_args, indent=2)}")
            print()
            
            result = await test_mcp_client.call_tool("zoom.create_meeting", test_args)
            
            if result.get("status") == "success":
                meeting = result.get("result", {})
                print("✅ Success!")
                print(f"   Meeting ID: {meeting.get('meeting_id', 'N/A')}")
                print(f"   Join URL: {meeting.get('join_url', 'N/A')}")
            else:
                print(f"⚠️  Response: {result}")
            print()
            
        except Exception as e:
            print(f"⚠️  Test failed: {e}")
            print("   (This is expected if Zoom credentials not configured)")
            print()
        
        # # Test 2: Salesforce - Query Leads  # COMMENTED OUT
        # try:
        #     print("📞 Test 2: Salesforce - Query Leads")
        #     print("-" * 60)
        #     test_args = {
        #         "soql_query": "SELECT Id, Name, Email FROM Lead WHERE Status = 'Open' LIMIT 3"
        #     }
        #     print(f"Tool: salesforce.query")
        #     print(f"Arguments: {json_lib.dumps(test_args, indent=2)}")
        #     print()
        #     
        #     result = await test_mcp_client.call_tool("salesforce.query", test_args)
        #     
        #     if result.get("status") == "success":
        #         query_result = result.get("result", {})
        #         print("✅ Success!")
        #         print(f"   Total records: {query_result.get('total_size', 0)}")
        #         for record in query_result.get('records', [])[:2]:
        #             print(f"   - {record.get('Name', 'N/A')}")
        #     else:
        #         print(f"⚠️  Response: {result}")
        #     print()
        #     
        # except Exception as e:
        #     print(f"⚠️  Test failed: {e}")
        #     print("   (This is expected if Salesforce credentials not configured)")
        #     print()
        
        # # Test 3: Beautiful - Scrape Website  # COMMENTED OUT
        # try:
        #     print("📞 Test 3: Beautiful - Scrape Website")
        #     print("-" * 60)
        #     test_args = {
        #         "url": "https://example.com",
        #         "format": "text"
        #     }
        #     print(f"Tool: beautiful.scrape")
        #     print(f"Arguments: {json_lib.dumps(test_args, indent=2)}")
        #     print()
        #     
        #     result = await test_mcp_client.call_tool("beautiful.scrape", test_args)
        #     
        #     if result.get("status") == "success":
        #         scrape_result = result.get("result", {})
        #         print("✅ Success!")
        #         print(f"   URL: {scrape_result.get('url', 'N/A')}")
        #         print(f"   Content length: {scrape_result.get('length', 0)} chars")
        #         content = scrape_result.get('content', '')
        #         if content:
        #             print(f"   Preview: {content[:100]}...")
        #     else:
        #         print(f"⚠️  Response: {result}")
        #     print()
        #     
        # except Exception as e:
        #     print(f"⚠️  Test failed: {e}")
        #     print("   (This is expected if Beautiful API not configured)")
        #     print()
        
        print("=" * 80)
        print("✅ MCP Capability Tests Complete!")
        print()
        print("Key Takeaways:")
        print(f"  • All {len(agents)} agents have access to the same Global MCP tools")
        print("  • Any agent can call Zoom APIs")
        print("  • (Salesforce and Beautiful are commented out for now)")
        print("  • No per-agent configuration needed - just call the tool!")
        print("  • Tools are centrally managed on the Global MCP Server")
        print()
        print("=" * 80)
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
    if HAS_MCP:
        print(f"  4. ✅ All agents equipped with Global MCP Server access")
        print(f"  5. ✅ Every agent can use Zoom tools (Salesforce/Beautiful commented out)")
        print(f"  6. ✅ Agents organized into {1 + len(child_workspaces)} workspace(s)")
        print(f"  7. ✅ Tasks automatically distributed to agents")
        print(f"  8. ✅ Workspaces executed in parallel")
        print(f"  9. ✅ Agents coordinated via email AND used external services")
    else:
        print(f"  4. ✅ Agents organized into {1 + len(child_workspaces)} workspace(s)")
        print(f"  5. ✅ Tasks automatically distributed to agents")
        print(f"  6. ✅ Workspaces executed in parallel")
        print(f"  7. ✅ Agents coordinated via email-like addressing")
    print()
    print("Key Innovation:")
    print("  • Task breakdown FIRST, then agents created based on needs!")
    print("  • No manual agent creation or task planning needed")
    print("  • Only creates exactly the agents required")
    if HAS_MCP:
        print("  • ALL agents have access to Global MCP Server!")
        print("  • Agents can schedule Zoom meetings")
        print("  • (Salesforce and Beautiful tools currently commented out)")
        print("  • Single global endpoint - no per-agent configuration")
    print("  • Automatic task distribution and execution")
    print("  • Agents automatically coordinate and delegate")
    print("  • Scales from simple to complex multi-agent systems")
    print()
    
    # Step 12: Display MCP Call Summary
    if HAS_MCP and len(MCP_CALL_LOG) > 0:
        print("=" * 80)
        print("📊 MCP CALL SUMMARY")
        print("=" * 80)
        print()
        print(f"Total MCP calls made: {len(MCP_CALL_LOG)}")
        print()
        
        success_count = sum(1 for call in MCP_CALL_LOG if call["status"] == "success")
        error_count = len(MCP_CALL_LOG) - success_count
        
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {error_count}")
        print()
        
        if MCP_CALL_LOG:
            print("Call Details:")
            for i, call in enumerate(MCP_CALL_LOG, 1):
                status_icon = "✅" if call["status"] == "success" else "❌"
                print(f"  {i}. {status_icon} {call['agent']} → {call['tool']}")
                if call.get("arguments"):
                    args_str = json_lib.dumps(call["arguments"], indent=6)
                    print(f"     Args: {args_str}")
                if call["status"] != "success":
                    error = call["result"].get("error", "unknown error")
                    print(f"     Error: {error}")
                print()
        
        print("=" * 80)
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
    # The agents will automatically use MCP tools as needed!
    
    user_task = """Plan a tech conference called 'AI Summit 2025' with 500 attendees. 
The conference should include:
- Multiple speaker tracks on AI topics
- Networking sessions and workshops
- Vendor exhibition area
- Catering for all meals
- Online streaming for remote attendees

Agents should:
- Schedule speaker meetings via Zoom
"""
# - Query Salesforce for potential sponsors  # COMMENTED OUT
# - Research venue options by scraping websites  # COMMENTED OUT
# - Create Salesforce leads for all interested attendees  # COMMENTED OUT
    
    # Alternative task examples that leverage MCP tools:
    
    # Example 2: Event coordination with Zoom
    # user_task = """Organize a virtual team offsite with sessions on:
    # - Q1 planning
    # - Team building activities  
    # - Technical workshops
    # Create a Zoom meeting for each session."""
    
    # # COMMENTED OUT - Salesforce examples:
    # # Example 3: Sales automation with Zoom + Salesforce
    # # user_task = """Query Salesforce for all hot leads with status 'Open'. 
    # # For each lead, schedule a 30-minute Zoom follow-up meeting and 
    # # update the lead in Salesforce with the meeting link."""
    # 
    # # Example 4: Competitor research with Beautiful + Salesforce
    # # user_task = """Research the top 5 competitors in the CRM space. 
    # # Scrape their websites for pricing information, summarize their 
    # # offerings, and create Salesforce leads for follow-up analysis."""
    
    # Run the demo
    asyncio.run(main(user_task, max_agent_turns=20))

