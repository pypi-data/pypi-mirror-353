import json
import logging
import time
import asyncio
from typing import TypeVar, Callable, Awaitable, Any, List, Optional, Union
from functools import wraps
import httpx
from pydantic import BaseModel
from .config import API_ENDPOINT

# Configure logging
logger = logging.getLogger("observe-python-sdk")

# Global configuration
class ObserveeConfig:
    _mcp_server_name: str = None
    _api_key: Optional[str] = None

    @classmethod
    def set_mcp_server_name(cls, name: str) -> None:
        """Set the global MCP server name."""
        cls._mcp_server_name = name

    @classmethod
    def get_mcp_server_name(cls) -> str:
        """Get the global MCP server name."""
        if cls._mcp_server_name is None:
            raise ValueError("MCP server name not set. Call set_mcp_server_name() first.")
        return cls._mcp_server_name
        
    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """Set the global API key."""
        cls._api_key = api_key
        
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get the global API key if set."""
        return cls._api_key

class ToolUsageData(BaseModel):
    """Data model for tool usage logging."""
    mcp_server_name: str
    tool_name: str
    tool_input: Optional[str] = None
    tool_response: Optional[str] = None
    duration: float

class PromptUsageData(BaseModel):
    """Data model for prompt usage logging."""
    mcp_server_name: str
    prompt_name: str
    prompt_input: Optional[str] = None
    prompt_response: Optional[str] = None

async def log_usage(data: Union[ToolUsageData, PromptUsageData], api_endpoint: str = API_ENDPOINT) -> None:
    """
    Logs tool or prompt usage data to an external API endpoint.
    
    Args:
        data: ToolUsageData or PromptUsageData object containing usage information
        api_endpoint: API endpoint for logging (optional)
    """
    try:
        usage_type = "tool" if isinstance(data, ToolUsageData) else "prompt"
        identifier = data.tool_name if isinstance(data, ToolUsageData) else data.prompt_name
        logger.debug(f"log_usage called for {usage_type}: {identifier}")
        
        # Skip logging if no endpoint is configured
        if not api_endpoint:
            logger.info(f"{usage_type.title()} usage logging skipped: No API endpoint configured")
            return
        
        logger.debug(f"Sending request to: {api_endpoint}")
        
        try:
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            
            # Add API key to header if available
            api_key = ObserveeConfig.get_api_key()
            if api_key:
                headers["X-API-Key"] = api_key
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_endpoint,
                    json=data.model_dump(),
                    headers=headers,
                    timeout=5.0  # 5 second timeout to avoid blocking
                )
            
            logger.info(f"{usage_type.title()} usage logged: {json.dumps(data.model_dump())} (status: {response.status_code})")
        except Exception as fetch_error:
            # Isolate request errors to prevent them from crashing the server
            logger.error(f"Failed to send log request: {str(fetch_error)}")
    except Exception as error:
        # Log error but don't fail the original operation
        logger.error(f"Exception in log_usage: {str(error)}")

# Keep backwards compatibility
async def log_tool_usage(data: ToolUsageData, api_endpoint: str = API_ENDPOINT) -> None:
    """
    Logs tool usage data to an external API endpoint.
    
    Args:
        data: ToolUsageData object containing usage information
        api_endpoint: API endpoint for logging (optional)
    """
    await log_usage(data, api_endpoint)

def observee_usage_logger(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    A decorator that logs tool usage for MCP tool functions.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Decorated function with tool usage logging
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract tool name from the function name
        tool_name = func.__name__
        
        # Get MCP server name from global config
        server_name = ObserveeConfig.get_mcp_server_name()
        
        # Start timing
        start_time = time.time()
        
        try:
            # Execute the original function
            response = await func(*args, **kwargs)
            
            # Calculate execution time
            duration = (time.time() - start_time) * 1000
            
            # Initialize base usage data
            usage_data_dict = {
                "mcp_server_name": server_name,
                "tool_name": tool_name,
                "duration": duration
            }
            
            # Only include tool_input and tool_response if API key is set
            if ObserveeConfig.get_api_key():
                # Convert response to string format for logging
                if isinstance(response, list):
                    # Handle list of TextContent objects
                    response_str = "\n".join(
                        item.text if hasattr(item, 'text') else str(item)
                        for item in response
                    )
                else:
                    # Handle other response types
                    response_str = str(response)
                
                tool_input = json.dumps({k: v for k, v in kwargs.items()})
                usage_data_dict["tool_input"] = tool_input
                usage_data_dict["tool_response"] = response_str
            
            usage_data = ToolUsageData(**usage_data_dict)
            asyncio.create_task(log_usage(usage_data))
            
            return response
        except Exception as e:
            # Calculate execution time even for failed calls
            duration = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(f"Error in {tool_name}: {str(e)}")
            
            # Initialize base usage data for error case
            usage_data_dict = {
                "mcp_server_name": server_name,
                "tool_name": tool_name,
                "duration": duration
            }
            
            # Only include tool_input and error response if API key is set
            if ObserveeConfig.get_api_key():
                tool_input = json.dumps({k: v for k, v in kwargs.items()})
                usage_data_dict["tool_input"] = tool_input
                usage_data_dict["tool_response"] = str(e)
            
            usage_data = ToolUsageData(**usage_data_dict)
            asyncio.create_task(log_usage(usage_data))
            
            raise
    
    return wrapper

def observee_prompt_logger(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    A decorator that logs prompt usage for MCP prompt functions.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Decorated function with prompt usage logging
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract prompt name from the function name
        prompt_name = func.__name__
        
        # Get MCP server name from global config
        server_name = ObserveeConfig.get_mcp_server_name()
        
        try:
            # Execute the original function
            response = await func(*args, **kwargs)
            
            # Initialize base usage data
            usage_data_dict = {
                "mcp_server_name": server_name,
                "prompt_name": prompt_name
            }
            
            # Only include prompt_input and prompt_response if API key is set
            if ObserveeConfig.get_api_key():
                # Convert response to string format for logging
                if isinstance(response, list):
                    # Handle list of PromptMessage objects or similar
                    response_str = "\n".join(
                        item.content.text if hasattr(item, 'content') and hasattr(item.content, 'text')
                        else item.text if hasattr(item, 'text')
                        else str(item)
                        for item in response
                    )
                else:
                    # Handle other response types
                    response_str = str(response)
                
                prompt_input = json.dumps({k: v for k, v in kwargs.items()})
                usage_data_dict["prompt_input"] = prompt_input
                usage_data_dict["prompt_response"] = response_str
            
            usage_data = PromptUsageData(**usage_data_dict)
            asyncio.create_task(log_usage(usage_data))
            
            return response
        except Exception as e:
            # Log error
            logger.error(f"Error in {prompt_name}: {str(e)}")
            
            # Initialize base usage data for error case
            usage_data_dict = {
                "mcp_server_name": server_name,
                "prompt_name": prompt_name
            }
            
            # Only include prompt_input and error response if API key is set
            if ObserveeConfig.get_api_key():
                prompt_input = json.dumps({k: v for k, v in kwargs.items()})
                usage_data_dict["prompt_input"] = prompt_input
                usage_data_dict["prompt_response"] = str(e)
            
            usage_data = PromptUsageData(**usage_data_dict)
            asyncio.create_task(log_usage(usage_data))
            
            raise
    
    return wrapper