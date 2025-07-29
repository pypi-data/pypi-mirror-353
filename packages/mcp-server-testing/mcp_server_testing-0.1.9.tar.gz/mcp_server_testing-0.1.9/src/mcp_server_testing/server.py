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
