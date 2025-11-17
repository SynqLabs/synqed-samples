# Synqed Python API library

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**AI agents can finally collaborate and interact with each other.**

Synq enables direct AI-to-AI interaction—agents can talk, coordinate, delegate work, and solve problems together for real multi-agent systems.

All seamless. All autonomous.

The library includes simple interfaces for creating collaborative agents with built-in orchestration, and it works with any LLM provider (OpenAI, Anthropic, Google, local models, etc.).

## Documentation

This is the full API documentation

## Installation

```bash
# install from PyPI
pip install synqed
```

Synqed works with the following LLM providers. Install your preferred provider:

```bash
pip install openai                  # For OpenAI (GPT-4, GPT-4o, etc.)
pip install anthropic               # For Anthropic (Claude)
pip install google-generativeai     # For Google (Gemini)
```

## Usage

The primary API for building agent collaboration systems includes three main components: **Agent** (creates autonomous agents), **Client** (connects to agents), and **Orchestrator** (intelligently routes tasks between agents).

### Setup: Environment Variables

Before running the examples, create a `.env` file at the root of the repository with your API keys:

```bash
# At synqed-samples/.env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional
GOOGLE_API_KEY=your_google_api_key_here        # Optional
```

**Note:** The `.env` file is gitignored by default to keep your API keys secure.

Then, load the environment variables in your code:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file
api_key = os.getenv("OPENAI_API_KEY")
```

### Quick Start: Your First Agent

Here's the fastest way to get started:

```python
import synqed
import asyncio

# Step 1: Define agent behavior and the LLM powering it
async def agent_logic(context):
    user_message = context.get_user_input()
    
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key="OPENAI_API_KEY")
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

# Step 2: Create and start agent
async def main():
    agent = synqed.Agent(
        name="MyAgent",
        description="A helpful AI assistant",
        skills=["general_assistance", "question_answering"],
        executor=agent_logic
    )
    
    # Start server
    server = synqed.AgentServer(agent, port=8000)
    await server.start_background()
    
    # Step 3: Connect and interact
    async with synqed.Client("http://localhost:8000") as client:
        response = await client.ask("What is machine learning?")
        print(response)
    
    await server.stop()

asyncio.run(main())
```

---

## Understanding Executor Functions

The **executor** is where you define your agent's behavior. It receives a context object and returns a response:

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

---

## Guide to Creating Agents

### Basic Agent

```python
import synqed

async def simple_agent_logic(context):
    user_message = context.get_user_input()
    # Your logic here
    return f"Processing: {user_message}"

agent = synqed.Agent(
    name="MyAgent",
    description="A helpful AI assistant",
    skills=["general_assistance"],
    executor=simple_agent_logic
)

server = synqed.AgentServer(agent, port=8000)
await server.start()
```

### Agent with Skills

Agents can have simple or detailed skill definitions:

**Simple Skills:**

```python
agent = synqed.Agent(
    name="WeatherAgent",
    description="Provides weather forecasts and alerts",
    skills=["weather_forecast", "weather_alerts", "climate_data"],
    executor=weather_logic
)
```

**Detailed Skills** (recommended for better orchestration):

```python
agent = synqed.Agent(
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

### Agent Capabilities

Configure advanced features:

```python
agent = synqed.Agent(
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

---

## Connecting to Agents

Use the `Client` to interact with any agent:

```python
import synqed

async with synqed.Client("http://localhost:8000") as client:
    # Get complete response
    response = await client.ask("What is machine learning?")
    print(response)
```

### Streaming Responses

Get real-time streaming responses (like ChatGPT's typing effect):

```python
async with synqed.Client("http://localhost:8000") as client:
    async for chunk in client.stream("Tell me about quantum computing"):
        print(chunk, end="", flush=True)
```

### Task Management

Manage long-running tasks programmatically:

```python
async with synqed.Client("http://localhost:8000") as client:
    # Submit task
    task_id = await client.submit_task("Complex analysis task")
    
    # Check status
    task = await client.get_task(task_id)
    print(f"Status: {task.state}")
    
    # Cancel if needed
    await client.cancel_task(task_id)
```

### Client Configuration

```python
import synqed

# Default configuration
client = synqed.Client("http://localhost:8000")

# Custom timeout
client = synqed.Client(
    agent_url="http://localhost:8000",
    timeout=120.0  # 2 minutes (default is 60)
)

# Disable streaming
client = synqed.Client(
    agent_url="http://localhost:8000",
    streaming=False
)

# Override per-request
async with synqed.Client("http://localhost:8000") as client:
    response = await client.with_options(timeout=30.0).ask("Quick question")
```

---

## Agent Collaboration with Orchestrator

The **Orchestrator** uses an LLM to analyze tasks and intelligently route them to the most suitable agents.

### Basic Orchestration

```python
import synqed
import os

# Create orchestrator with LLM-powered routing
orchestrator = synqed.Orchestrator(
    provider=synqed.LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Register your specialized agents
orchestrator.register_agent(research_agent.card, "http://localhost:8001")
orchestrator.register_agent(coding_agent.card, "http://localhost:8002")
orchestrator.register_agent(writing_agent.card, "http://localhost:8003")

# Orchestrator automatically selects the best agent(s) for the task
result = await orchestrator.orchestrate(
    "Research recent AI developments and write a technical summary"
)

print(f"Selected: {result.selected_agents[0].agent_name}")
print(f"Confidence: {result.selected_agents[0].confidence:.0%}")
print(f"Reasoning: {result.selected_agents[0].reasoning}")
```

### Supported LLM Providers

```python
import synqed

# OpenAI
synqed.Orchestrator(
    provider=synqed.LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="model-here" 
)

# Anthropic
synqed.Orchestrator(
    provider=synqed.LLMProvider.ANTHROPIC,
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="model-here"
)

# Google
synqed.Orchestrator(
    provider=synqed.LLMProvider.GOOGLE,
    api_key=os.environ.get("GOOGLE_API_KEY"),
    model="model-here"
)
```

### Orchestration Configuration

```python
import synqed

orchestrator = synqed.Orchestrator(
    provider=synqed.LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=0.7,     # Creativity level (0.0 - 1.0)
    max_tokens=2000      # Maximum response length
)
```

---

## Multi-Agent Delegation

The **TaskDelegator** coordinates multiple agents working together on complex tasks:

```python
import synqed
import os

# Create orchestrator for intelligent routing
orchestrator = synqed.Orchestrator(
    provider=synqed.LLMProvider.OPENAI,
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create delegator
delegator = synqed.TaskDelegator(orchestrator=orchestrator)

# Register specialized agents (local or remote)
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

## Complete Examples

Ready to dive deeper? Check out the complete, runnable examples in this folder.

```bash
# Clone and run
git clone https://github.com/SynqLabs/synqed-samples
cd synqed-samples/api/python
python example.py
```

---

## Async Programming

All Synqed methods support `async`/`await`. Simply use async functions throughout your code:

```python
import synqed
import asyncio

async def my_executor(context):
    user_message = context.get_user_input()
    # Your async logic here
    return f"Response: {user_message}"

async def main() -> None:
    # Create agent
    agent = synqed.Agent(
        name="ResearchAgent",
        description="Research specialist",
        skills=["research", "analysis"],
        executor=my_executor
    )
    
    # Start server in background
    server = synqed.AgentServer(agent, port=8000)
    await server.start_background()
    
    # Connect and interact
    async with synqed.Client("http://localhost:8000") as client:
        response = await client.ask("Latest AI research trends")
        print(response)
    
    await server.stop()

asyncio.run(main())
```

---

## Error Handling & Best Practices

## ⚠️ Troubleshooting

**If you encounter any errors, check the terminal where your server is running.** The most verbose and detailed error information appears in the server logs.

### Exception Handling

When the library encounters connection issues or API errors, appropriate exceptions are raised:

```python
import synqed

try:
    async with synqed.Client("http://localhost:8000") as client:
        response = await client.ask("Hello")
except synqed.ConnectionError as e:
    print("Could not connect to agent")
    print(e.__cause__)
except synqed.TimeoutError as e:
    print("Request timed out")
except synqed.AgentError as e:
    print(f"Agent returned error: {e}")
```

### Resource Management

Always use context managers to ensure proper cleanup:

```python
import synqed

# ✅ Recommended: Use context manager
async with synqed.Client("http://localhost:8000") as client:
    response = await client.ask("Hello")
# Client automatically closed

# ⚠️ Manual cleanup (only if needed)
client = synqed.Client("http://localhost:8000")
try:
    response = await client.ask("Hello")
finally:
    await client.close()
```

### Timeouts

Requests time out after 60 seconds by default. Configure as needed:

```python
import synqed

# Custom timeout
client = synqed.Client("http://localhost:8000", timeout=120.0)

# Per-request timeout override
async with synqed.Client("http://localhost:8000") as client:
    response = await client.with_options(timeout=30.0).ask("Quick task")
```

---

## Requirements

- Python 3.10 or higher

## License

These examples and demos are open source and released under the MIT License. See [LICENSE](https://github.com/SynqLabs/synqed-samples/blob/main/LICENSE) file for full terms.

Copyright © 2025 Synq Team. All rights reserved.

