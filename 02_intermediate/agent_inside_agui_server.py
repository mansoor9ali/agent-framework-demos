"""AG-UI server example."""

import os

from agent_framework import ChatAgent
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint

from fastapi import FastAPI
import asyncio
from dotenv import load_dotenv
from utils import create_dotted_client , create_openaichat_client

# Load environment variables
load_dotenv()



chat_client =  create_openaichat_client()

# Create the AI agent
agent = ChatAgent(
    name="AGUIAssistant",
    instructions="You are a helpful assistant.",
    chat_client=chat_client,
)

# Create FastAPI app
app = FastAPI(title="AG-UI Server")

# Register the AG-UI endpoint
add_agent_framework_fastapi_endpoint(app, agent, "/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8878)