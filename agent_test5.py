# Copyright (c) Microsoft. All rights reserved.

import asyncio

from dotenv import load_dotenv
from pydantic import BaseModel
from rich import print

from utils import create_gptoss120b_client

# Load environment variables from .env file
load_dotenv()

class PersonInfo(BaseModel):
    """Information about a person."""
    name: str | None = None
    age: int | None = None
    occupation: str | None = None


async def example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    agent = create_gptoss120b_client().create_agent(
        name="HelpfulAssistant",
        instructions="You are a helpful assistant that extracts person information from text."
    )

    query = "Please provide information about John Smith, who is a 35-year-old software engineer."
    print(f"User: {query}")

    result = await agent.run(
        "Please provide information about John Smith, who is a 35-year-old software engineer.",
         response_format = PersonInfo
    )

    if result.value:
        person_info = result.value
        print(f"Name: {person_info.name}, Age: {person_info.age}, Occupation: {person_info.occupation}")
    else:
        print("No structured data found in result")



async def main() -> None:
    print("=== Producing Structured Output with Agents ===")
    await example()


if __name__ == "__main__":
    asyncio.run(main())