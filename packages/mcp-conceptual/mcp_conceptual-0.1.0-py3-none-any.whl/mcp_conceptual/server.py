"""MCP Server for Conceptual Keywords & Creative Performance API."""

import asyncio
import os
from typing import Any, Sequence

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import CallToolResult, TextContent

from .tools.creatives import (
    CREATIVE_TOOLS,
    get_creative_status,
    get_google_creative_performance,
    get_meta_creative_performance,
    update_creative_status,
)
from .tools.keywords import (
    KEYWORD_TOOLS,
    get_campaign_content_info,
    get_keyword_performance,
    get_manual_keywords_info,
    get_search_terms_performance,
)

# Load environment variables
load_dotenv()

# Create server instance
server = Server("conceptual-api")

# Tool handlers mapping
TOOL_HANDLERS = {
    "get_keyword_performance": get_keyword_performance,
    "get_search_terms_performance": get_search_terms_performance,
    "get_manual_keywords_info": get_manual_keywords_info,
    "get_campaign_content_info": get_campaign_content_info,
    "get_meta_creative_performance": get_meta_creative_performance,
    "get_google_creative_performance": get_google_creative_performance,
    "get_creative_status": get_creative_status,
    "update_creative_status": update_creative_status,
}


@server.list_tools()
async def handle_list_tools() -> list:
    """List available tools."""
    return KEYWORD_TOOLS + CREATIVE_TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls."""
    if name not in TOOL_HANDLERS:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    try:
        handler = TOOL_HANDLERS[name]
        result = await handler(**arguments)
        return result
    except TypeError as e:
        return [TextContent(type="text", text=f"Invalid arguments for {name}: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error calling {name}: {e}")]


async def main():
    """Main entry point for the MCP server."""
    # Check for required environment variables
    api_key = os.getenv("CONCEPTUAL_API_KEY")
    if not api_key:
        print("Error: CONCEPTUAL_API_KEY environment variable is required")
        print("Please set your API key in the environment or .env file")
        return 1
    
    # Server options
    options = InitializationOptions(
        server_name="conceptual-api",
        server_version="0.1.0",
        capabilities=server.get_capabilities(
            notification_options=None,
            experimental_capabilities=None,
        ),
    )
    
    async with server.run_stdio():
        await server.aconnect()


if __name__ == "__main__":
    asyncio.run(main())