"""
NEW 08: Structured Output with Pydantic (Interactive Demo)

This demo shows how to extract structured data from text using Pydantic models.
The agent returns typed Python objects instead of plain text.
"""

import asyncio
import os

from agent_framework.openai import OpenAIChatClient
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()



# Define structured output model
class PersonInfo(BaseModel):
    """Extract person information from text."""
    name: str | None = None
    age: int | None = None
    occupation: str | None = None
    city: str | None = None


async def main():
    """Interactive demo: Structured output extraction."""
    
    print("\n" + "="*70)
    print("📊 DEMO: Structured Output with Pydantic")
    print("="*70)
    
    # Create agent
    agent = OpenAIChatClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_id=os.getenv("OPENAI_MODEL_ID"),
    ).create_agent(
        instructions="Extract person information from the user's text.",
        name="ExtractorBot"
    )
    
    print("\n✅ Agent created with PersonInfo schema")
    print("📋 Schema: name, age, occupation, city")
    
    print("\n" + "="*70)
    print("💬 Interactive Chat (Type 'quit' to exit)")
    print("="*70)
    print("\n💡 TIP: Describe a person and see structured extraction\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        # Get structured response
        print("\n🔄 Extracting structured data...")
        response = await agent.run(user_input, response_format=PersonInfo)
        
        if response.value:
            person = response.value
            print("\n📊 Extracted Information:")
            print(f"   Name: {person.name}")
            print(f"   Age: {person.age}")
            print(f"   Occupation: {person.occupation}")
            print(f"   City: {person.city}")
        else:
            print("❌ Could not extract information")
        
        print()


if __name__ == "__main__":
    asyncio.run(main())
