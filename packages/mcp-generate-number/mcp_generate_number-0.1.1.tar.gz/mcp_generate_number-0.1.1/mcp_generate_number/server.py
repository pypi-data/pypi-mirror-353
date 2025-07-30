import random
from fastmcp import FastMCP
import os

# The API key is read from an environment variable for security.
# The server will require this key in the 'X-API-Key' header.
mcp = FastMCP(
    "Random-Number-Server",
    api_key=os.environ.get("API_KEY"),
    api_key_header="X-API-Key",
)

# A simple MCP server that generates a random number.
@mcp.tool(description="Return a random integer 0–100")
def generate_number() -> int:
    return random.randint(0, 100)

@mcp.tool(description="Return a random string of a given length")
def generate_string(length: int = 10) -> str:
    """Generates a random string of a given length."""
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))

def main():
    # If running on Fly.io, use the streamable-http transport.
    # Otherwise, default to stdio for local use (e.g., with Goose).
    if os.environ.get("FLY_APP_NAME"):
        mcp.run(transport="streamable-http", port=8080)
    else:
        mcp.run()

if __name__ == "__main__":
    main() 