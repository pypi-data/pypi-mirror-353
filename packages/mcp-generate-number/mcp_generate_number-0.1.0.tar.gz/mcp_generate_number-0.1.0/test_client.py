import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    # 1. Create a transport object with the required authentication headers.
    transport = StreamableHttpTransport(
        url="https://mcp-generate-number.fly.dev/mcp",
        headers={"X-API-Key": "GXlCkhew3RRCCBw79/JWoEROWyaHgk1CDOh3F/HEAlI="},
    )

    # 2. Create the client using the configured transport.
    async with Client(transport) as client:
        print("Listing available tools...")
        tools = await client.list_tools()
        print("Tools:", tools)

        print("\\nCalling 'generate_number' tool...")
        result = await client.call_tool("generate_number", {})
        print("Result from generate_number:", result)

if __name__ == "__main__":
    asyncio.run(main()) 