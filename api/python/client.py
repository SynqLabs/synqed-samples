"""
Client Example - Two ways to talk to an AI agent

There are 2 ways to get responses:

1. ask() - Wait for the complete answer
   Example: response = await client.ask("What's 2+2?")
   Use when: You need the full answer at once

2. stream() - Get the answer piece by piece (like ChatGPT typing)
   Example: async for chunk in client.stream("Tell a story"):
   Use when: You want to show text appearing in real-time

Why use end="" and flush=True?
- end="" makes chunks print on the same line (not separate lines)
- flush=True makes text appear immediately (creates typing effect)

To run:
1. First, start the agent: python agent_creation_and_card.py
2. Then run this client: python client.py
"""
import asyncio
from pathlib import Path
import synqed
from dotenv import load_dotenv

# Load environment variables from .env file at repository root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

async def main():
    async with synqed.Client("http://localhost:8000") as client:
        # Option 1: Simple request-response
        response = await client.ask("What are the top 3 most popular songs of all time?")
        print(f"Agent: {response}")
        
        # Option 2: Streaming response (like ChatGPT typing)
        print("Streaming: ", end="")
        async for chunk in client.stream("Tell me a joke"):
            print(chunk, end="", flush=True)
        print()

if __name__ == "__main__":
    asyncio.run(main())