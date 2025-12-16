"""
Example script demonstrating how to use an OpenAI-compatible LLM with the ReAct agent.
This example can use DeepSeek or any OpenAI API compatible endpoint like Ollama, LocalAI, or LM Studio.

Usage:
    1. Ensure your .env file has DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, and DEEPSEEK_MODEL_ID set
    2. Or ensure your local LLM server is running and set the appropriate environment variables
    3. Run this script: python local_examples/local_llm_example.py
"""

import os
import sys
sys.path.append("")  # Add the project root to the path

from src.config.logging import logger
from src.react.agent import Agent, run
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Example function to run the agent with a custom LLM configuration
def run_with_custom_llm(query: str) -> str:
    """
    Run the ReAct agent with a custom LLM configuration.

    Args:
        query (str): The query to process
        
    Returns:
        str: The final answer from the agent
    """
    # Get configuration from environment variables or use defaults
    model_name = os.getenv('LLM_MODEL_NAME', 'deepseek-chat')
    base_url = os.getenv('LLM_BASE_URL', 'https://api.deepseek.com')
    api_key = os.getenv('LLM_API_KEY', 'not-needed')
    temperature = float(os.getenv('LLM_TEMPERATURE', '0.1'))
    max_tokens = int(os.getenv('LLM_MAX_TOKENS', '2048'))

    # Create OpenAI client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # Create agent directly with the client
    agent = Agent(
        client=client,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Execute the query
    answer = agent.execute(query)
    return answer

if __name__ == "__main__":
    # Set up example query
    query = "What is the tallest building in India and when was it built?"

    # Check if DeepSeek credentials are available
    if os.getenv('DEEPSEEK_API_KEY'):
        logger.info(f"Running query with DeepSeek: {query}")
        final_answer = run(query)  # Uses DeepSeek from .env
    else:
        logger.info(f"Running query with custom LLM configuration: {query}")
        final_answer = run_with_custom_llm(query)  # Uses custom provider with env vars

    logger.info(f"Final answer: {final_answer}")
