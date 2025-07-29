import logging
from fastmcp import FastMCP

mcp = FastMCP("MCP Test Server")
logger = logging.getLogger(__name__)


@mcp.tool()
def greet(name: str) -> str:
    """
    Returns a greeting message for the given name.

    Args:
        name (str): The name of the person to greet.

    Returns:
        str: A greeting message in the format "Hello, {name}!"
    """
    logger.info(f"greeting {name}")
    return f"Hello, {name}!"


@mcp.resource("data://config")
def get_config() -> dict:
    """Provides the application configuration."""
    return {"theme": "dark", "version": "1.0"}


@mcp.resource("data://status")
def get_status() -> dict:
    """Provides the application status."""
    return {"status": "running", "uptime": "24 hours"}
