"""
Orchestrator Quick Start

This example shows the simplest way to use the Orchestrator for intelligent
agent routing. The orchestrator uses an LLM to analyze tasks and select the
best agent(s) to handle them.

Setup:
1. Install: pip install openai python-dotenv
2. Create .env file with: OPENAI_API_KEY='your-key-here'
3. Run: python orchestrator_quickstart.py
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from synqed import Agent, Orchestrator, LLMProvider

# Load environment
load_dotenv()
load_dotenv(dotenv_path=Path(__file__).parent / '.env')


async def main():
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY in your .env file")
        return
    
    # Step 1: Create the orchestrator with your LLM of choice
    orchestrator = Orchestrator(
        provider=LLMProvider.OPENAI,  # or ANTHROPIC, GOOGLE
        api_key=api_key,
        model="gpt-4o",  # The model that will make routing decisions
    )
    
    # Step 2: Create some agents with different skills
    recipe_agent = Agent(
        name="RecipeAgent",
        description="Search and recommend recipes",
        skills=[
            {
                "skill_id": "recipe_search",
                "name": "Recipe Search",
                "description": "Find recipes by ingredient or cuisine type",
                "tags": ["cooking", "recipes", "food"],
            }
        ],
    )
    
    shopping_agent = Agent(
        name="ShoppingAgent",
        description="Create shopping lists and compare prices",
        skills=[
            {
                "skill_id": "shopping_list",
                "name": "Shopping List Creation",
                "description": "Generate shopping lists for recipes or meal plans",
                "tags": ["shopping", "grocery", "list"],
            }
        ],
    )
    
    weather_agent = Agent(
        name="WeatherAgent",
        description="Provide weather forecasts and alerts",
        skills=[
            {
                "skill_id": "weather_forecast",
                "name": "Weather Forecast",
                "description": "Get current weather and forecasts for any location",
                "tags": ["weather", "forecast", "climate"],
            }
        ],
    )
    
    # Step 3: Register agents with the orchestrator
    orchestrator.register_agent(recipe_agent.card, recipe_agent.url)
    orchestrator.register_agent(shopping_agent.card, shopping_agent.url)
    orchestrator.register_agent(weather_agent.card, weather_agent.url)
    
    print(f"✓ Registered {len(orchestrator.list_agents())} agents\n")
    
    # Step 4: Submit a task and let the orchestrator decide which agent to use
    task = "I want to cook pasta tonight but I need to know what ingredients to buy"
    
    print(f"User Task: {task}\n")
    print("🤖 Orchestrator analyzing...\n")
    
    # Get the orchestration result
    result = await orchestrator.orchestrate(task)
    
    # Step 5: View the results
    print("=" * 70)
    print("ORCHESTRATION RESULT")
    print("=" * 70 + "\n")
    
    print(f"📌 Selected Agent(s):")
    for selection in result.selected_agents:
        print(f"\n  🎯 {selection.agent_name}")
        print(f"     Confidence: {selection.confidence:.0%}")
        print(f"     Recommended Skills: {', '.join(selection.recommended_skills)}")
        print(f"     Reasoning: {selection.reasoning}")
    
    print(f"\n📋 Execution Plan:")
    print(f"   {result.execution_plan}")
    
    if result.alternative_agents:
        print(f"\n💡 Alternative Options:")
        for alt in result.alternative_agents:
            print(f"   • {alt.agent_name} ({alt.confidence:.0%} confidence)")
    
    print("\n" + "=" * 70)
    
    # Example with a different task
    print("\n\nTrying another task...\n")
    
    task2 = "What's the weather like tomorrow?"
    print(f"User Task: {task2}\n")
    
    result2 = await orchestrator.orchestrate(task2)
    
    print(f"✓ Selected: {result2.selected_agents[0].agent_name}")
    print(f"  Confidence: {result2.selected_agents[0].confidence:.0%}")
    print(f"  Reasoning: {result2.selected_agents[0].reasoning}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ORCHESTRATOR QUICK START")
    print("=" * 70 + "\n")
    
    asyncio.run(main())
    
    print("\n✓ Done!\n")

