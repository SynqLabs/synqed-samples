# Synqed - Multi-Agent Collaboration

**Synqed** is a framework that allows you to build collaborative multi-agent AI systems.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
<!--[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)-->

Why Synqed?

- **5 Minutes to Your First Agent** - Create production-ready agents in minutes, not hours
- **Intelligent Orchestration** - Built-in LLM-powered routing that selects the right agent for each task
- **Zero Protocol Knowledge Required** - High-level API abstracts away A2A complexity
- **Multi-Agent Coordination** - Seamlessly delegate tasks across multiple specialized agents
- **Production Ready** - Battle-tested abstractions with comprehensive error handling

## 📦 Installation

```bash
pip install synqed
```

### Optional Dependencies

```bash
# For gRPC support
pip install synqed[grpc]

# For SQL task store
pip install synqed[sql]

# Everything
pip install synqed[all]
```

### LLM Provider Dependencies

Synqed's Orchestrator works with multiple LLM providers. Install your preferred provider:

```bash
# OpenAI
pip install openai

# Anthropic
pip install anthropic

# Google
pip install google-generativeai
```

## Quick Start

### Step 1: Create Your First Agent

Create a file `my_agent.py`:

```python
import asyncio
import os
from synqed import Agent, AgentServer

async def agent_logic(context):
    """Your agent's brain - this is where the magic happens."""
    user_message = context.get_user_input()
    
    # Use any LLM you want
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

async def main():
    # Create your agent
    agent = Agent(
        name="MyFirstAgent",
        description="A helpful AI assistant",
        skills=["general_assistance", "question_answering"],
        executor=agent_logic
    )
    
    # Start the server
    server = AgentServer(agent, port=8000)
    print(f"Agent running at {agent.url}")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Connect a Client

Create a file `client.py`:

```python
import asyncio
from synqed import Client

async def main():
    async with Client("http://localhost:8000") as client:
        # Option 1: Simple request-response
        response = await client.ask("What's the weather like?")
        print(f"Agent: {response}")
        
        # Option 2: Streaming response (like ChatGPT typing)
        print("Streaming: ", end="")
        async for chunk in client.stream("Tell me a joke"):
            print(chunk, end="", flush=True)
        print()

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run It

```bash
# Terminal 1 - Start your agent
python my_agent.py

# Terminal 2 - Connect your client
python client.py
```

**Congratulations!** You just built and deployed your first AI agent.

---

## 📖 Core Concepts

### The Three Pillars of Synqed

```
┌─────────────┬──────────────┬─────────────────┐
│   Agents    │    Client    │  Orchestrator   │
│             │              │                 │
│  The brains │  The bridge  │  The director   │
└─────────────┴──────────────┴─────────────────┘
```

1. **Agent** - An autonomous AI agent with specific skills
2. **Client** - Connect to and communicate with agents  
3. **Orchestrator** - Intelligently routes tasks to the right agents

---

## Building Agents

### Basic Agent

```python
from synqed import Agent

agent = Agent(
    name="WeatherAgent",
    description="Provides weather forecasts and alerts",
    skills=["weather_forecast", "weather_alerts"],
    executor=my_logic_function
)
```

### Agent with Detailed Skills

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

### Agent Executor Function

The executor function is where your agent's logic/capability lives:

```python
async def agent_logic(context):
    """
    Args:
        context: RequestContext object with methods:
            - get_user_input() → str: The user's message
            - get_task() → Task: Full task object
            - get_message() → Message: Full message object
    
    Returns:
        str or Message: Your agent's response
    """
    user_message = context.get_user_input()
    
    # Your custom logic here
    # - Call LLMs (OpenAI, Anthropic, Google, etc.)
    # - Query databases
    # - Call external APIs
    # - Process data
    # - Whatever your agent needs to do!
    
    return "Agent response"
```

### Agent Capabilities

```python
agent = Agent(
    name="MyAgent",
    description="Does amazing things",
    skills=["skill1"],
    executor=logic,
    capabilities={
        "streaming": True,              # Support real-time streaming
        "push_notifications": False,    # Enable webhook notifications
        "state_transition_history": False  # Track state changes
    }
)
```

### Hosting Your Agent

```python
from synqed import AgentServer

# Create server
server = AgentServer(agent, host="0.0.0.0", port=8000)

# Option 1: Start in foreground (blocking)
await server.start()

# Option 2: Start in background
await server.start_background()
# ... do other things ...
await server.stop()
```

---

## 💬 Using the Client

### Two Ways to Get Responses

#### 1. Complete Response (ask)

Wait for the full response before continuing.

```python
from synqed import Client

async with Client("http://localhost:8000") as client:
    response = await client.ask("What's 2+2?")
    print(response)  # "4"
```

**Use `ask()` when:**
- You need the complete answer before proceeding
- Response time is reasonable (< 30 seconds)
- You want simpler code without iteration

#### 2. Streaming Response (stream)

Get the response piece by piece as it's generated (like ChatGPT).

```python
async with Client("http://localhost:8000") as client:
    async for chunk in client.stream("Tell me a story"):
        print(chunk, end="", flush=True)  # Creates typing effect
```

**Use `stream()` when:**
- You want to show progress to users
- The response might be long
- You want to process data as it arrives

**Pro tip:** Use `end=""` to prevent newlines between chunks and `flush=True` to display output immediately.

### Task Management

```python
async with Client("http://localhost:8000") as client:
    # Submit a task
    task_id = await client.submit_task("Long running operation")
    
    # Check task status
    task = await client.get_task(task_id)
    print(f"Status: {task.state}")
    
    # Cancel if needed
    await client.cancel_task(task_id)
```

### Advanced Client Features

```python
# Custom timeout
client = Client(
    agent_url="http://localhost:8000",
    timeout=120.0  # 2 minutes
)

# Disable streaming
client = Client(
    agent_url="http://localhost:8000",
    streaming=False
)
```

---

## Orchestration (Intelligent Routing)

The **Orchestrator** uses an LLM to analyze tasks and automatically select the best agent(s) to handle them.

### Basic Orchestration

```python
from synqed import Orchestrator, LLMProvider

# Initialize with your LLM of choice
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,  # or ANTHROPIC, GOOGLE
    api_key="your-api-key",
    model="gpt-4o"
)

# Register your agents
orchestrator.register_agent(recipe_agent.card, recipe_agent.url)
orchestrator.register_agent(shopping_agent.card, shopping_agent.url)
orchestrator.register_agent(weather_agent.card, weather_agent.url)

# Let the orchestrator decide which agent to use
result = await orchestrator.orchestrate(
    "I want to cook pasta tonight but need to know what ingredients to buy"
)

# View the results
print(f"Selected Agent: {result.selected_agents[0].agent_name}")
print(f"Confidence: {result.selected_agents[0].confidence:.0%}")
print(f"Reasoning: {result.selected_agents[0].reasoning}")
print(f"Plan: {result.execution_plan}")
```

### Orchestration Result

```python
@dataclass
class OrchestrationResult:
    task: str                                    # The original task
    selected_agents: list[AgentSelection]        # Best agent(s)
    execution_plan: str                          # How to execute
    alternative_agents: list[AgentSelection]     # Backup options
```

### Supported LLM Providers

```python
# OpenAI
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key="sk-...",
    model="gpt-4o"  # or "gpt-4o-mini", "gpt-4-turbo"
)

# Anthropic
orchestrator = Orchestrator(
    provider=LLMProvider.ANTHROPIC,
    api_key="sk-ant-...",
    model="claude-3-5-sonnet-20241022"
)

# Google
orchestrator = Orchestrator(
    provider=LLMProvider.GOOGLE,
    api_key="...",
    model="gemini-2.0-flash-exp"
)
```

### Fine-tune Orchestration

```python
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key="sk-...",
    model="gpt-4o",
    temperature=0.7,     # Creativity (0.0 - 1.0)
    max_tokens=2000      # Response length limit
)
```

---

## Multi-Agent Delegation

The **TaskDelegator** coordinates multiple agents working together on complex tasks.

### Basic Delegation

```python
from synqed import TaskDelegator

# Create delegator
delegator = TaskDelegator()

# Register agents
delegator.register_agent(agent=recipe_agent)
delegator.register_agent(agent=shopping_agent)
delegator.register_agent(agent=weather_agent)

# Submit a task - automatically routed to the right agent
result = await delegator.submit_task(
    "Find me a recipe and create a shopping list"
)
```

### Delegation with Orchestrator

For intelligent routing, combine TaskDelegator with Orchestrator:

```python
# Create orchestrator for intelligent routing
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key="your-key",
    model="gpt-4o"
)

# Create delegator with orchestrator
delegator = TaskDelegator(orchestrator=orchestrator)

# Register agents
delegator.register_agent(agent=recipe_agent)
delegator.register_agent(agent=shopping_agent)

# Now tasks are intelligently routed using LLM analysis
result = await delegator.submit_task(
    "Plan dinner for a cold rainy evening"
)
```

### Remote Agent Registration

```python
# Register a remote agent by URL
delegator.register_agent(
    agent_url="https://recipe-service.example.com",
    agent_card=recipe_agent_card  # Optional pre-loaded card
)
```

---



##  Complete Examples

### Example 1: Simple Customer Support Agent

```python
import asyncio
import os
from synqed import Agent, AgentServer
from openai import AsyncOpenAI

async def support_logic(context):
    """Customer support agent logic."""
    user_message = context.get_user_input()
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful customer support agent. "
                          "Be polite, professional, and solve problems efficiently."
            },
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

async def main():
    agent = Agent(
        name="SupportAgent",
        description="Customer support assistant",
        skills=["customer_support", "ticket_routing", "faq"],
        executor=support_logic
    )
    
    server = AgentServer(agent, port=8000)
    print(f"✅ Support agent running at {agent.url}")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Multi-Agent System with Orchestration

```python
import asyncio
import os
from synqed import Agent, AgentServer, Orchestrator, LLMProvider
from openai import AsyncOpenAI

# ============================================================================
# Agent 1: Recipe Agent
# ============================================================================

async def recipe_logic(context):
    user_message = context.get_user_input()
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a recipe expert. Suggest recipes based on "
                          "ingredients, cuisine type, or dietary restrictions."
            },
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

# ============================================================================
# Agent 2: Shopping Agent
# ============================================================================

async def shopping_logic(context):
    user_message = context.get_user_input()
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a shopping assistant. Create shopping lists, "
                          "compare prices, and suggest where to buy items."
            },
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

# ============================================================================
# Agent 3: Nutrition Agent
# ============================================================================

async def nutrition_logic(context):
    user_message = context.get_user_input()
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a nutrition expert. Provide nutritional "
                          "information, calculate calories, and give healthy eating advice."
            },
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

# ============================================================================
# Main System
# ============================================================================

async def main():
    # Create agents
    recipe_agent = Agent(
        name="RecipeAgent",
        description="Find and recommend recipes",
        skills=[
            {
                "skill_id": "recipe_search",
                "name": "Recipe Search",
                "description": "Find recipes by ingredient or cuisine",
                "tags": ["cooking", "recipes", "food"]
            }
        ],
        executor=recipe_logic
    )
    
    shopping_agent = Agent(
        name="ShoppingAgent",
        description="Create shopping lists and find products",
        skills=[
            {
                "skill_id": "shopping_list",
                "name": "Shopping List",
                "description": "Create and manage shopping lists",
                "tags": ["shopping", "grocery", "list"]
            }
        ],
        executor=shopping_logic
    )
    
    nutrition_agent = Agent(
        name="NutritionAgent",
        description="Provide nutrition information and advice",
        skills=[
            {
                "skill_id": "nutrition_info",
                "name": "Nutrition Info",
                "description": "Calculate calories and provide nutrition facts",
                "tags": ["nutrition", "health", "calories"]
            }
        ],
        executor=nutrition_logic
    )
    
    # Start agents on different ports
    recipe_server = AgentServer(recipe_agent, port=8001)
    shopping_server = AgentServer(shopping_agent, port=8002)
    nutrition_server = AgentServer(nutrition_agent, port=8003)
    
    await recipe_server.start_background()
    await shopping_server.start_background()
    await nutrition_server.start_background()
    
    print("✅ All agents running")
    print(f"  - Recipe Agent: {recipe_agent.url}")
    print(f"  - Shopping Agent: {shopping_agent.url}")
    print(f"  - Nutrition Agent: {nutrition_agent.url}")
    
    # Create orchestrator
    orchestrator = Orchestrator(
        provider=LLMProvider.OPENAI,
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Register agents
    orchestrator.register_agent(recipe_agent.card, recipe_agent.url)
    orchestrator.register_agent(shopping_agent.card, shopping_agent.url)
    orchestrator.register_agent(nutrition_agent.card, nutrition_agent.url)
    
    print("\n✅ Orchestrator configured with 3 agents\n")
    
    # Test orchestration
    tasks = [
        "Find me a healthy pasta recipe",
        "Create a shopping list for a stir fry dinner",
        "How many calories are in a pepperoni pizza?"
    ]
    
    for task in tasks:
        print(f"📋 Task: {task}")
        result = await orchestrator.orchestrate(task)
        print(f"   🎯 Selected: {result.selected_agents[0].agent_name}")
        print(f"   📊 Confidence: {result.selected_agents[0].confidence:.0%}")
        print(f"   💡 Reasoning: {result.selected_agents[0].reasoning}\n")
    
    # Keep servers running
    print("Press Ctrl+C to stop...")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        await recipe_server.stop()
        await shopping_server.stop()
        await nutrition_server.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

### 1. Agent Design

**DO:**
- ✅ Give agents focused, specific skills
- ✅ Write clear, descriptive agent descriptions
- ✅ Use detailed skill definitions with tags
- ✅ Include proper error handling in executor functions

**DON'T:**
- ❌ Create "do everything" agents
- ❌ Use vague descriptions like "General agent"
- ❌ Skip skill tags (they help with routing)
- ❌ Let exceptions crash your executor

### 2. Orchestration

**DO:**
- ✅ Use descriptive agent and skill names
- ✅ Review confidence scores before execution
- ✅ Check alternative agents for complex tasks
- ✅ Tune temperature based on your use case

**DON'T:**
- ❌ Ignore low confidence scores (< 0.6)
- ❌ Use orchestration for single-agent systems
- ❌ Over-rely on default settings
- ❌ Skip testing with various task types

### 3. Production Deployment

**DO:**
- ✅ Use environment variables for API keys
- ✅ Implement comprehensive logging
- ✅ Add health check endpoints
- ✅ Set reasonable timeouts
- ✅ Use async context managers (`async with`)

**DON'T:**
- ❌ Hard-code credentials
- ❌ Run without error monitoring
- ❌ Use default ports in production
- ❌ Forget to clean up resources
- ❌ Skip authentication

### 4. Error Handling

```python
async def robust_executor(context):
    try:
        user_message = context.get_user_input()
        
        # Your logic here
        result = await do_something(user_message)
        
        return result
    
    except ValueError as e:
        # Handle expected errors gracefully
        return f"I couldn't process that: {e}"
    
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Executor error: {e}", exc_info=True)
        return "I encountered an unexpected error. Please try again."
```

### 5. Resource Management

```python
# Good: Use context manager
async with Client("http://localhost:8000") as client:
    response = await client.ask("Hello")

# Good: Manual cleanup
client = Client("http://localhost:8000")
try:
    response = await client.ask("Hello")
finally:
    await client.close()

# Bad: No cleanup
client = Client("http://localhost:8000")
response = await client.ask("Hello")
# Resources leak!
```

---

## 🔒 Security Considerations

### Environment Variables

**Never** hard-code credentials:

```python
# ❌ BAD
orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key="sk-proj-abc123...",  # DON'T DO THIS!
    model="gpt-4o"
)

# ✅ GOOD
import os

orchestrator = Orchestrator(
    provider=LLMProvider.OPENAI,
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)
```

### Authentication

```python
agent = Agent(
    name="SecureAgent",
    description="Requires authentication",
    skills=["secure_skill"],
    executor=logic,
    security_schemes={
        "api_key": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Connection refused"

**Problem:** Client can't connect to agent

**Solution:**
```python
# Make sure agent is running
# Check the port matches
# Try: curl http://localhost:8000/agent-card
```

#### 2. "Module not found: openai"

**Problem:** Missing LLM provider package

**Solution:**
```bash
pip install openai  # or anthropic, google-generativeai
```

#### 3. Streaming not working

**Problem:** No streaming support or agent doesn't stream

**Solution:**
```python
# Enable streaming in agent
agent = Agent(
    name="MyAgent",
    description="...",
    skills=["..."],
    executor=logic,
    capabilities={"streaming": True}  # Add this
)

# Enable in client
client = Client("http://localhost:8000", streaming=True)
```

#### 4. Low orchestration confidence

**Problem:** Orchestrator is unsure which agent to select

**Solution:**
- Improve agent descriptions
- Add more detailed skills with tags
- Make agent names more descriptive
- Use a more powerful LLM (e.g., GPT-4o vs GPT-4o-mini)

#### 5. "Task timeout"

**Problem:** Agent takes too long to respond

**Solution:**
```python
# Increase client timeout
client = Client("http://localhost:8000", timeout=120.0)

# Or implement progress updates in your executor
```

---

## 📊 Performance Tips

### 1. Use Background Servers for Multiple Agents

```python
# Start all agents in background
await recipe_server.start_background()
await shopping_server.start_background()
await weather_server.start_background()

# Now they all run concurrently
```

### 2. Reuse Clients

```python
# ❌ BAD: Create new client for each request
for task in tasks:
    async with Client(url) as client:
        await client.ask(task)

# ✅ GOOD: Reuse client
async with Client(url) as client:
    for task in tasks:
        await client.ask(task)
```

### 3. Use Streaming for Long Responses

```python
# Streaming shows progress and feels faster
async for chunk in client.stream("Long task..."):
    print(chunk, end="", flush=True)
```

### 4. Parallel Task Submission

```python
# Submit multiple tasks in parallel
tasks = [
    client1.ask("Task 1"),
    client2.ask("Task 2"),
    client3.ask("Task 3")
]

results = await asyncio.gather(*tasks)
```

---

## 🆘 Getting Help

### Documentation & Resources

- **Examples:** Check the `examples/` directory for complete working code
- **Tests:** Review `tests/` for usage patterns and edge cases
- **License:** See `LICENSE` file for terms and conditions

### Common Questions

**Q: Do I need to understand A2A protocol?**  
A: No! That's the whole point of Synqed - it abstracts the protocol away.

**Q: Can I use any LLM provider?**  
A: In your agent executor, yes! For orchestration, we support OpenAI, Anthropic, and Google.

**Q: How many agents can I run?**  
A: As many as your system resources allow. Each agent runs on its own port.

**Q: Can agents call other agents?**  
A: Yes! Use the Client within your executor function to call other agents.

**Q: Is Synqed production-ready?**  
A: Yes, with proper error handling, logging, and monitoring in place.

**Q: What's the difference between Orchestrator and TaskDelegator?**  
A: Orchestrator routes tasks intelligently using an LLM. TaskDelegator executes the routing decision and manages the actual delegation.

---

## 📄 License

This software is proprietary and confidential. See [LICENSE](LICENSE) file for full terms.

Copyright © 2025 Synq Team. All rights reserved.

---

## 🚀 Next Steps

Ready to build something amazing?

1. **Install:** `pip install synqed`
2. **Try examples:** Explore the `examples/` directory
3. **Build your first agent:** Start with the Quick Start above
4. **Scale up:** Add orchestration and delegation
5. **Deploy:** Take it to production

**Happy building! 🎉**

