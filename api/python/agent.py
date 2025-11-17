"""
Agent Creation Example - Build and run your own AI agent

This shows how to create an agent in 3 steps:

1. Define agent_logic() - What your agent does, what LLM it is
   - Gets the user's message from context
   - Calls an LLM (ex. OpenAI) to generate a response

2. Create an Agent - Give it a name, description, and skills
   - name: What to call your agent
   - description: What it does
   - skills: What capabilities it has
   - executor: The function that handles requests (agent_logic)
   - capabilities: Optional dict to configure:
     * streaming: Enable real-time response streaming (default: True)
     * push_notifications: Enable webhook notifications for long tasks (default: False)
     * state_transition_history: Enable state change tracking (default: False)

3. Create a Server - Host your agent so clients can connect
   - The agent runs at http://localhost:8000
   - Clients can connect and send messages to it

Setup:
1. Install dependencies: pip install openai python-dotenv
2. Create a .env file with: OPENAI_API_KEY='your-key-here'
3. Run: python agent.py
4. Test: python client.py (in another terminal)
"""

import asyncio
import os
from pathlib import Path
import synqed
from dotenv import load_dotenv

# Load environment variables from .env file at repository root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

async def agent_logic(context):
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
    agent = synqed.Agent(
        name="MyFirstAgent",
        description="A helpful AI assistant",
        skills=["general_assistance", "question_answering"],
        executor=agent_logic
    )
    
    # Start the server
    server = synqed.AgentServer(agent, port=8000)
    print(f"Agent running at {agent.url}")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())