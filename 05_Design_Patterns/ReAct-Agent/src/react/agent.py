from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.utils.io import write_to_file
from src.config.logging import logger
from src.utils.io import read_file
from pydantic import BaseModel
from typing import Callable
from pydantic import Field 
from typing import Union
from typing import List 
from typing import Dict 
from enum import Enum
from enum import auto
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file at root
load_dotenv()


Observation = Union[str, Exception]

# Get the directory of this file and construct absolute paths
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.join(_CURRENT_DIR, "..", "..")
PROMPT_TEMPLATE_PATH = os.path.join(_PROJECT_ROOT, "data", "input", "react.txt")
OUTPUT_TRACE_PATH = os.path.join(_PROJECT_ROOT, "data", "output", "trace.txt")

class Name(Enum):
    """
    Enumeration for tool names available to the agent.
    """
    WIKIPEDIA = auto()
    GOOGLE = auto()
    NONE = auto()

    def __str__(self) -> str:
        """
        String representation of the tool name.
        """
        return self.name.lower()


class Choice(BaseModel):
    """
    Represents a choice of tool with a reason for selection.
    """
    name: Name = Field(..., description="The name of the tool chosen.")
    reason: str = Field(..., description="The reason for choosing this tool.")


class Message(BaseModel):
    """
    Represents a message with sender role and content.
    """
    role: str = Field(..., description="The role of the message sender.")
    content: str = Field(..., description="The content of the message.")


class Tool:
    """
    A wrapper class for tools used by the agent, executing a function based on tool type.
    """

    def __init__(self, name: Name, func: Callable[[str], str], description: str, parameters: Dict[str, str], examples: List[str]):
        """
        Initializes a Tool with a name, an associated function, and metadata.
        
        Args:
            name (Name): The name of the tool.
            func (Callable[[str], str]): The function associated with the tool.
            description (str): A brief description of the tool.
            parameters (Dict[str, str]): A dictionary of parameter names and descriptions.
            examples (List[str]): A list of example usage strings.
        """
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters
        self.examples = examples

    def use(self, query: str) -> Observation:
        """
        Executes the tool's function with the provided query.

        Args:
            query (str): The input query for the tool.

        Returns:
            Observation: Result of the tool's function or an error message if an exception occurs.
        """
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return str(e)


class Agent:
    """
    Defines the agent responsible for executing queries and handling tool interactions.
    """

    def __init__(self, client: OpenAI, model_name: str, temperature: float = 0.1, max_tokens: int = 2048) -> None:
        """
        Initializes the Agent with an OpenAI client, tools dictionary, and a messages log.

        Args:
            client (OpenAI): The OpenAI client instance.
            model_name (str): The model name to use.
            temperature (float): Temperature for generation.
            max_tokens (int): Maximum tokens for generation.
        """
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools: Dict[Name, Tool] = {}
        self.messages: List[Message] = []
        self.query = ""
        self.max_iterations = 5
        self.current_iteration = 0
        self.template = self.load_template()

    def load_template(self) -> str:
        """
        Loads the prompt template from a file.

        Returns:
            str: The content of the prompt template file.
        """
        return read_file(PROMPT_TEMPLATE_PATH)

    def register(self, name: Name, func: Callable[[str], str], description: str, parameters: Dict[str, str], examples: List[str]) -> None:
        """
        Registers a tool to the agent.

        Args:
            name (Name): The name of the tool.
            func (Callable[[str], str]): The function associated with the tool.
            description (str): A brief description of the tool.
            parameters (Dict[str, str]): A dictionary of parameter names and descriptions.
            examples (List[str]): A list of example usage strings.
        """
        self.tools[name] = Tool(name, func, description, parameters, examples)

    def register_tools(self) -> None:
        """
        Register all available tools with their metadata.
        """
        self.register(
            Name.WIKIPEDIA, 
            wiki_search,
            description="Search Wikipedia for factual information",
            parameters={"query": "search terms"},
            examples=["/wiki quantum mechanics", "/wiki Barack Obama"]
        )
        self.register(
            Name.GOOGLE, 
            google_search,
            description="Search Google for current information",
            parameters={"query": "search terms", "location": "optional location"},
            examples=["/google latest AI news", "/google weather in Paris"]
        )

    def trace(self, role: str, content: str) -> None:
        """
        Logs the message with the specified role and content and writes to file.

        Args:
            role (str): The role of the message sender.
            content (str): The content of the message.
        """
        if role != "system":
            self.messages.append(Message(role=role, content=content))
        write_to_file(path=OUTPUT_TRACE_PATH, content=f"{role}: {content}\n")

    def get_history(self) -> str:
        """
        Retrieves the conversation history.

        Returns:
            str: Formatted history of messages.
        """
        return "\n".join([f"{message.role}: {message.content}" for message in self.messages])

    def think(self) -> None:
        """
        Processes the current query, decides actions, and iterates until a solution or max iteration limit is reached.
        """
        self.current_iteration += 1
        logger.info(f"Starting iteration {self.current_iteration}")
        write_to_file(path=OUTPUT_TRACE_PATH, content=f"\n{'='*50}\nIteration {self.current_iteration}\n{'='*50}\n")

        if self.current_iteration > self.max_iterations:
            logger.warning("Reached maximum iterations. Stopping.")
            self.trace("assistant", "I'm sorry, but I couldn't find a satisfactory answer within the allowed number of iterations. Here's what I know so far: " + self.get_history())
            return

        prompt = self.template.format(
            query=self.query, 
            history=self.get_history(),
            tools=', '.join([str(tool.name) for tool in self.tools.values()])
        )

        response = self.ask_llm(prompt)
        logger.info(f"Thinking => {response}")
        self.trace("assistant", f"Thought: {response}")
        self.decide(response)

    def decide(self, response: str) -> None:
        """
        Processes the agent's response, deciding actions or final answers.

        Args:
            response (str): The response generated by the model.
        """
        try:
            cleaned_response = response.strip().strip('`').strip()
            if cleaned_response.startswith('json'):
                cleaned_response = cleaned_response[4:].strip()
            
            parsed_response = json.loads(cleaned_response)
            
            if "action" in parsed_response:
                action = parsed_response["action"]
                tool_name = Name[action["name"].upper()]
                if tool_name == Name.NONE:
                    logger.info("No action needed. Proceeding to final answer.")
                    self.think()
                else:
                    self.trace("assistant", f"Action: Using {tool_name} tool")
                    self.act(tool_name, action.get("input", self.query))
            elif "answer" in parsed_response:
                self.trace("assistant", f"Final Answer: {parsed_response['answer']}")
            else:
                raise ValueError("Invalid response format")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {response}. Error: {str(e)}")
            self.trace("assistant", "I encountered an error in processing. Let me try again.")
            self.think()
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            self.trace("assistant", "I encountered an unexpected error. Let me try a different approach.")
            self.think()

    def act(self, tool_name: Name, query: str) -> None:
        """
        Executes the specified tool's function on the query and logs the result.

        Args:
            tool_name (Name): The tool to be used.
            query (str): The query for the tool.
        """
        tool = self.tools.get(tool_name)
        if tool:
            result = tool.use(query)
            observation = f"Observation from {tool_name}: {result}"
            self.trace("system", observation)
            self.messages.append(Message(role="system", content=observation))  # Add observation to message history
            self.think()
        else:
            logger.error(f"No tool registered for choice: {tool_name}")
            self.trace("system", f"Error: Tool {tool_name} not found")
            self.think()

    def execute(self, query: str) -> str:
        """
        Executes the agent's query-processing workflow.

        Args:
            query (str): The query to be processed.

        Returns:
            str: The final answer or last recorded message content.
        """
        self.query = query
        self.trace(role="user", content=query)
        self.register_tools()
        self.think()
        return self.messages[-1].content

    def ask_llm(self, prompt: str) -> str:
        """
        Queries the LLM using OpenAI client with a prompt.

        Args:
            prompt (str): The prompt text for the model.

        Returns:
            str: The model's response as a string.
        """
        try:
            logger.info(f"Generating response using {self.model_name}")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            response_text = response.choices[0].message.content

            if not response_text:
                logger.error("Empty response from the model")
                return "No response from LLM"

            logger.info("Successfully generated response")
            return response_text

        except Exception as e:
            logger.error(f"Error querying model: {e}")
            return f"Error: {str(e)}"

def run(query: str) -> str:
    """
    Sets up the agent with OpenAI client using DeepSeek, registers tools, and executes a query.

    Args:
        query (str): The query to execute.

    Returns:
        str: The agent's final answer.
    """
    # Load DeepSeek configuration from environment variables
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    model_id = os.getenv('DEEPSEEK_MODEL_ID', 'deepseek-chat')

    if not api_key:
        logger.error("DEEPSEEK_API_KEY environment variable is not set")
        raise ValueError("DEEPSEEK_API_KEY environment variable is required")

    logger.info(f"Using DeepSeek model: {model_id} at {base_url}")

    # Create OpenAI client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # Create agent with OpenAI client
    agent = Agent(
        client=client,
        model_name=model_id,
        temperature=0.1,
        max_tokens=2048
    )

    answer = agent.execute(query)
    return answer


if __name__ == "__main__":
    query = "What is the country that has won the most FIFA World Cup titles?"
    final_answer = run(query)
    logger.info(final_answer)