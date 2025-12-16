from src.tools.serp import search as google_search
from src.tools.wiki import search as wiki_search
from src.config.logging import logger
from pydantic import BaseModel, Field
from typing import Any, Callable, Union, Dict, List
from enum import Enum, auto

Observation = Union[str, Exception]

class Name(Enum):
    """
    Enumeration of available tools.
    """
    WIKIPEDIA = auto()
    GOOGLE = auto()

    def __str__(self) -> str:
        return self.name.lower()


class Choice(BaseModel):
    """
    Represents a tool choice with a reason.
    """
    name: Name = Field(..., description="Name of the selected tool")
    reason: str = Field(..., description="Reason for selecting this tool")

class ToolMetadata(BaseModel):
    """
    Metadata for tools including descriptions and parameters.
    """
    description: str = Field(default="", description="Tool description for the LLM")
    parameters: dict = Field(default_factory=dict, description="Expected parameters schema")
    examples: List[str] = Field(default_factory=list, description="Example usages")


class Tool:
    """
    Enhanced Tool class with metadata support.
    """
    def __init__(self, name: Name, func: Callable[[str], str], metadata: ToolMetadata = None):
        self.name = name
        self.func = func
        self.metadata = metadata or ToolMetadata()
    
    def use(self, query: str) -> Observation:
        """
        Execute the tool's function for a given query and handle exceptions.
        """
        try:
            return self.func(query)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return e


class Manager:
    """
    Enhanced tool manager with metadata support and discovery capabilities.
    """
    def __init__(self) -> None:
        self.tools: Dict[Name, Tool] = {}
        self._tool_metadata: Dict[Name, ToolMetadata] = {}
    
    def register(self, 
               name: Name, 
               func: Callable[[str], str],
               description: str = "",
               parameters: dict = None,
               examples: List[str] = None) -> None:
        """
        Register a new tool with metadata.
        """
        metadata = ToolMetadata(
            description=description,
            parameters=parameters or {},
            examples=examples or []
        )
        self.tools[name] = Tool(name, func, metadata)
        self._tool_metadata[name] = metadata
    
    def get_tool_description(self, name: Name) -> str:
        """Get the formatted description of a tool for LLM prompts."""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        
        meta = self._tool_metadata[name]
        params = ", ".join([f"{k}: {v}" for k, v in meta.parameters.items()])
        return f"{name}: {meta.description}. Params: {params}"
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools with their metadata."""
        return [{
            "name": name,
            "description": meta.description,
            "parameters": meta.parameters,
            "examples": meta.examples
        } for name, meta in self._tool_metadata.items()]
    
    def act(self, name: Name, query: str) -> Observation:
        """
        Retrieve and use a registered tool to process the given query.

        Parameters:
            name (Name): The name of the tool to use.
            query (str): The input query string.

        Returns:
            Observation: The result of the tool's execution or an error.
        """
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        
        processed_query = query.split(' ', 1)[1] if ' ' in query else query
        return self.tools[name].use(processed_query)
    
    def choose(self, query: str) -> Choice:
        """
        Choose the appropriate tool based on the query prefix.
        """
        if query.startswith("/people"):
            return Choice(
                name=Name.WIKIPEDIA, 
                reason="Query starts with /people, using Wikipedia for biographical information."
            )
        elif query.startswith("/location"):
            return Choice(
                name=Name.GOOGLE, 
                reason="Query starts with /location, using Google for location-specific information."
            )
        else:
            raise ValueError("Unsupported query. Use /people or /location prefix.")


def run() -> None:
    """
    Initialize manager, register tools, and process test queries.
    """
    manager = Manager()
    
    manager.register(Name.WIKIPEDIA, wiki_search)
    manager.register(Name.GOOGLE, google_search)
    
    test_cases = [
    "/people kamala harris",
    "/location greek restaurants in miami",
    "What's the weather like today?",
    ]
    
    for i, query in enumerate(test_cases, 1):
        try:
            choice = manager.choose(query)
            result = manager.act(choice.name, query)
            
            logger.info(f"Test Case {i}:")
            logger.info(f"Query: {query}")
            logger.info(f"Tool used: {choice.name}")
            logger.info(f"Reason: {choice.reason}")
            logger.info(f"Result: {result}")
        except ValueError as e:
            logger.error(f"Test Case {i}:")
            logger.error(f"Query: {query}")
            logger.error(f"Error: {str(e)}")
        logger.info("")  # Empty line for readability


if __name__ == "__main__":
    run()