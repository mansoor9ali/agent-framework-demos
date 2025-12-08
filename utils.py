# utils.py
import os
from dotenv import load_dotenv
from agent_framework.openai import OpenAIChatClient

# Load environment variables from .env file
load_dotenv()


def create_openai_client() -> OpenAIChatClient:
    """
    Create and return an OpenAIChatClient instance with environment variables.

    Returns:
        OpenAIChatClient: Configured OpenAI chat client
    """
    return OpenAIChatClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_id=os.getenv("OPENAI_MODEL_ID"),
    )
