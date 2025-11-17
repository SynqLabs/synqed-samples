# Synqed Python API library

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Allow AI agents to collaborate, delegate, and coordinate with each other autonomously. Build multi-agent systems where agents work together - a research agent consults specialists, a design agent brainstorms with analysts, or your OpenAI agent delegates to specialized agents. All seamlessly, all automatically.

The library provides type-safe interfaces for creating collaborative agents with built-in intelligent orchestration. It works with any LLM provider (OpenAI, Anthropic, Google) and enables true agent-to-agent interaction.

## Documentation

The full API of this library can be found in the `examples/` directory and throughout this README.

## Installation

```bash
# Install from PyPI
pip install synqed
```

Synqed works with any LLM provider. Install your preferred provider:

```bash
pip install openai                  # For OpenAI (GPT-4, GPT-4o, etc.)
pip install anthropic               # For Anthropic (Claude)
pip install google-generativeai     # For Google (Gemini)
```

Optional dependencies for advanced features:

```bash
pip install synqed[grpc]   # gRPC protocol support
pip install synqed[sql]    # SQL-based task persistence
pip install synqed[all]    # All optional features
```

## Usage

The primary API for building agent collaboration systems includes three main components: **Agent** (creates autonomous agents), **Client** (connects to agents), and **Orchestrator** (intelligently routes tasks between agents).

### Creating an Agent

Create a collaborative agent with custom logic:

```python
import os
from synqed import Agent, AgentServer

async def agent_logic(context):
    """Define your agent's behavior - use any LLM or custom logic."""
    user_message = context.get_user_input()
    
    # Use any LLM provider
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

# Create and serve your agent
agent = Agent(
    name="MyAgent",
    description="A helpful AI assistant",
    skills=["general_assistance", "question_answering"],
    executor=agent_logic
)

server = AgentServer(agent, port=8000)
await server.start()
```

### Connecting to an Agent

Interact with agents using the Client:

```python
from synqed import Client

async with Client("http://localhost:8000") as client:
    # Get complete response
    response = await client.ask("What is machine learning?")
    print(response)
```

### Streaming Responses

Get real-time streaming responses (like ChatGPT's typing effect):

```python
async with Client("http://localhost:8000") as client:
    async for chunk in client.stream("Tell me about quantum computing"):
        print(chunk, end="", flush=True)
```

### Agent Collaboration with Orchestrator

The Orchestrator enables agents to collaborate by intelligently routing tasks:

```python
from synqed import Orchestrator, LLMProvider

# Create orchestrator with LLM-powered routing
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Register multiple specialized agents
orchestrator.register_agent(research_agent.card, research_agent.url)
orchestrator.register_agent(coding_agent.card, coding_agent.url)
orchestrator.register_agent(writing_agent.card, writing_agent.url)

# Orchestrator automatically selects the best agent(s) for the task
result = await orchestrator.orchestrate(
    "Research recent AI developments and write a technical summary"
)

print(f"Selected: {result.selected_agents[0].agent_name}")
print(f"Confidence: {result.selected_agents[0].confidence:.0%}")
print(f"Plan: {result.execution_plan}")
```

---

## Async Usage

Simply use `async`/`await` with all Synqed methods:

```python
import asyncio
from synqed import Agent, AgentServer, Client

async def main() -> None:
    # Create agent
    agent = Agent(
        name="ResearchAgent",
        description="Research specialist",
        skills=["research", "analysis"],
        executor=research_logic
    )
    
    # Start server in background
    server = AgentServer(agent, port=8000)
    await server.start_background()
    
    # Connect and interact
    async with Client("http://localhost:8000") as client:
        response = await client.ask("Latest AI research trends")
        print(response)
    
    await server.stop()

asyncio.run(main())
```

Functionality between synchronous and asynchronous clients is identical.

## Agent Skills

Agents can have simple or detailed skill definitions:

### Simple Skills

```python
from synqed import Agent

agent = Agent(
    name="WeatherAgent",
    description="Provides weather forecasts and alerts",
    skills=["weather_forecast", "weather_alerts", "climate_data"],
    executor=weather_logic
)
```

### Detailed Skills

For better orchestration, provide detailed skill descriptions:

```python
agent = Agent(
    name="RecipeAgent",
    description="Find and recommend recipes",
    skills=[
        {
            "skill_id": "recipe_search",
            "name": "Recipe Search",
            "description": "Search for recipes by ingredients or cuisine type",
            "tags": ["cooking", "recipes", "food", "search"]
        },
        {
            "skill_id": "nutrition_info",
            "name": "Nutrition Information",
            "description": "Get nutritional information for recipes",
            "tags": ["nutrition", "health", "calories"]
        }
    ],
    executor=recipe_logic
)
```

## Executor Functions

The executor defines your agent's behavior. It receives a context and returns a response:

```python
async def agent_logic(context):
    """
    Args:
        context: RequestContext with methods:
            - get_user_input() → str: User's message
            - get_task() → Task: Full task object
            - get_message() → Message: Full message object
    
    Returns:
        str or Message: Agent's response
    """
    user_message = context.get_user_input()
    
    # Implement any logic:
    # - Call LLMs (OpenAI, Anthropic, Google)
    # - Query databases
    # - Call external APIs
    # - Delegate to other agents
    
    return "Agent response"
```

## Agent Capabilities

Configure agent capabilities for advanced features:

```python
agent = Agent(
    name="StreamingAgent",
    description="Agent with streaming support",
    skills=["chat", "analysis"],
    executor=logic,
    capabilities={
        "streaming": True,                    # Real-time streaming
        "push_notifications": False,          # Webhook notifications
        "state_transition_history": False     # State tracking
    }
)
```

## Task Management

Manage long-running tasks programmatically:

```python
async with Client("http://localhost:8000") as client:
    # Submit task
    task_id = await client.submit_task("Complex analysis task")
    
    # Check status
    task = await client.get_task(task_id)
    print(f"Status: {task.state}")
    
    # Cancel if needed
    await client.cancel_task(task_id)
```

## Multi-Agent Delegation

The TaskDelegator coordinates multiple agents working together:

```python
from synqed import TaskDelegator, Orchestrator, LLMProvider

# Create orchestrator for intelligent routing
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create delegator
delegator = TaskDelegator(orchestrator=orchestrator)

# Register specialized agents
delegator.register_agent(agent=research_agent)
delegator.register_agent(agent=coding_agent)
delegator.register_agent(agent=writing_agent)

# Agents automatically collaborate on complex tasks
result = await delegator.submit_task(
    "Research microservices patterns and write implementation guide"
)
```

### Remote Agent Registration

Register agents running anywhere:

```python
# Register remote agent
delegator.register_agent(
    agent_url="https://specialist-agent.example.com",
    agent_card=agent_card  # Optional pre-loaded card
)
```

---

## Client Configuration

Customize client behavior with configuration options:

```python
from synqed import Client

# Default configuration
client = Client("http://localhost:8000")

# Custom timeout
client = Client(
    agent_url="http://localhost:8000",
    timeout=120.0  # 2 minutes (default is 60)
)

# Disable streaming
client = Client(
    agent_url="http://localhost:8000",
    streaming=False
)

# Override per-request
async with Client("http://localhost:8000") as client:
    response = await client.with_options(timeout=30.0).ask("Quick question")
```

---

## Orchestration

The Orchestrator uses an LLM to analyze tasks and intelligently route them to the most suitable agents, enabling seamless agent collaboration.

```python
from synqed import Orchestrator, LLMProvider
import os

orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Register specialized agents
orchestrator.register_agent(research_agent.card, research_agent.url)
orchestrator.register_agent(coding_agent.card, coding_agent.url)
orchestrator.register_agent(writing_agent.card, writing_agent.url)

# Intelligently route complex tasks
result = await orchestrator.orchestrate(
    "Research quantum computing advances and write a technical report"
)

print(f"Selected: {result.selected_agents[0].agent_name}")
print(f"Confidence: {result.selected_agents[0].confidence:.0%}")
print(f"Reasoning: {result.selected_agents[0].reasoning}")
```

### Supported LLM Providers

```python
# OpenAI
Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o"  # or "gpt-4o-mini", "gpt-4-turbo"
)

# Anthropic
Orchestrator(
    provider=LLMProvider.ANTHROPIC,
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20241022"
)

# Google
Orchestrator(
    provider=LLMProvider.GOOGLE,
    api_key=os.environ.get("GOOGLE_API_KEY"),
    model="gemini-2.0-flash-exp"
)
```

### Orchestration Configuration

```python
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=0.7,     # Creativity level (0.0 - 1.0)
    max_tokens=2000      # Maximum response length
)
```

---



## Complete Examples

### Example: Multi-Agent Collaboration System

This example demonstrates agents collaborating on complex tasks through intelligent orchestration:

```python
import asyncio
import os
from synqed import Agent, AgentServer, Orchestrator, LLMProvider, Client
from openai import AsyncOpenAI

# Define agent executors
async def research_logic(context):
    """Research agent - gathers information and analyzes data."""
    message = context.get_user_input()
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a research specialist. Gather comprehensive information and provide detailed analysis."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

async def coding_logic(context):
    """Coding agent - writes and reviews code."""
    message = context.get_user_input()
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a coding expert. Write clean, efficient, well-documented code."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

async def writing_logic(context):
    """Writing agent - creates polished documentation."""
    message = context.get_user_input()
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a technical writer. Create clear, professional documentation."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content


async def main():
    # Create specialized agents
    research_agent = Agent(
        name="ResearchAgent",
        description="Conducts research and data analysis",
        skills=["research", "analysis", "data_gathering"],
        executor=research_logic
    )
    
    coding_agent = Agent(
        name="CodingAgent",
        description="Writes and reviews code",
        skills=["programming", "code_review", "debugging"],
        executor=coding_logic
    )
    
    writing_agent = Agent(
        name="WritingAgent",
        description="Creates technical documentation",
        skills=["documentation", "technical_writing", "editing"],
        executor=writing_logic
    )
    
    # Start agents (running concurrently)
    servers = [
        AgentServer(research_agent, port=8001),
        AgentServer(coding_agent, port=8002),
        AgentServer(writing_agent, port=8003)
    ]
    
    for server in servers:
        await server.start_background()
    
    # Create orchestrator for intelligent task routing
    orchestrator = Orchestrator(
        provider=LLMProvider.OPENAI,
        api_key=os.environ.get("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Register agents with orchestrator
    orchestrator.register_agent(research_agent.card, research_agent.url)
    orchestrator.register_agent(coding_agent.card, coding_agent.url)
    orchestrator.register_agent(writing_agent.card, writing_agent.url)
    
    print("✅ Multi-agent system ready\n")
    
    # Example: Agents collaborate on complex project
    tasks = [
        "Research best practices for microservices architecture",
        "Implement a rate limiter in Python",
        "Write API documentation for the rate limiter"
    ]
    
    for task in tasks:
        print(f"📋 Task: {task}")
        
        # Orchestrator intelligently routes to best agent
        result = await orchestrator.orchestrate(task)
        selected = result.selected_agents[0]
        
        print(f"   → Routed to: {selected.agent_name}")
        print(f"   → Confidence: {selected.confidence:.0%}")
        print(f"   → Reasoning: {selected.reasoning}\n")
        
        # Execute task with selected agent
        async with Client(selected.agent_url) as client:
            response = await client.ask(task)
            print(f"   ✅ Response: {response[:100]}...\n")
    
    # Cleanup
    for server in servers:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

When the library encounters connection issues or API errors, appropriate exceptions are raised:

```python
import synqed
from synqed import Client

try:
    async with Client("http://localhost:8000") as client:
        response = await client.ask("Hello")
except synqed.ConnectionError as e:
    print("Could not connect to agent")
    print(e.__cause__)
except synqed.TimeoutError as e:
    print("Request timed out")
except synqed.AgentError as e:
    print(f"Agent returned error: {e}")
```

## Timeouts

By default, requests time out after 60 seconds. Configure timeouts as needed:

```python
from synqed import Client

# Default timeout (60 seconds)
client = Client("http://localhost:8000")

# Custom timeout
client = Client("http://localhost:8000", timeout=120.0)

# Per-request timeout
async with Client("http://localhost:8000") as client:
    response = await client.with_options(timeout=30.0).ask("Quick task")
```

## Resource Management

Always clean up resources using context managers:

```python
# Recommended: Use context manager
async with Client("http://localhost:8000") as client:
    response = await client.ask("Hello")
# Client automatically closed

# Manual cleanup
client = Client("http://localhost:8000")
try:
    response = await client.ask("Hello")
finally:
    await client.close()
```

## Agent-to-Agent Communication

Agents can collaborate by calling each other directly:

```python
async def coordinator_logic(context):
    """Coordinator agent that delegates to specialists."""
    task = context.get_user_input()
    
    # Call specialist agents
    async with Client("http://localhost:8001") as research_client:
        research = await research_client.ask(f"Research: {task}")
    
    async with Client("http://localhost:8002") as analysis_client:
        analysis = await analysis_client.ask(f"Analyze: {research}")
    
    return f"Final result: {analysis}"
```

## Requirements

- Python 3.10 or higher

## License

This software is proprietary and confidential. See [LICENSE](LICENSE) file for full terms.

Copyright © 2025 Synq Team. All rights reserved.

