import asyncio
import os
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# This is an integration test that calls the deployed server.
# It requires the server URL and a valid API key to be set as environment variables.
# You can run it like this:
# MCP_SERVER_URL=... MCP_API_KEY=... pytest tests/test_integration.py

URL = os.environ.get("MCP_SERVER_URL", "https://mcp-generate-number.fly.dev/mcp")
API_KEY = os.environ.get("MCP_API_KEY")

@pytest.mark.asyncio
@pytest.mark.skipif(not API_KEY, reason="MCP_API_KEY environment variable not set")
async def test_integration():
    """
    Tests the full flow of connecting to the server, listing tools,
    and calling a tool.
    """
    transport = StreamableHttpTransport(
        url=URL,
        headers={"X-API-Key": API_KEY},
    )

    async with Client(transport) as client:
        tools = await client.list_tools()
        assert "generate_number" in [t["name"] for t in tools]
        assert "generate_string" in [t["name"] for t in tools]

        result = await client.call_tool("generate_number", {})
        assert isinstance(result, int)
        assert 0 <= result <= 100 