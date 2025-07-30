import random
from fastmcp import FastMCP
import os

# Define the core functions
def _generate_number() -> int:
    """Generates a random integer between 0 and 100."""
    return random.randint(0, 100)

def _generate_string(length: int = 10) -> str:
    """Generates a random string of a given length."""
    # Triggering workflow to publish to PyPI
    # This is a test comment for our automated release
    # This is another test comment to trigger deployment.
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))

def authenticate(api_key: str | None) -> bool:
    """
    Authenticates requests.
    Returns True if the request is allowed, False otherwise.
    """
    # Get the required API key from the environment.
    required_key = os.environ.get("API_KEY")
    # If the required key is not set on the server, deny all requests.
    if not required_key:
        return False
    # If the client provides a key, it must match the required key.
    return api_key == required_key

# --- MCP Server Setup ---

# FastMCP will handle the authentication check internally using the provided function.
mcp = FastMCP(
    "Random-Number-Server",
    authenticate=authenticate,
    api_key_header="X-API-Key",
)

# Create tools from the core functions
generate_number = mcp.tool(description="Return a random integer 0–100")(_generate_number)
generate_string = mcp.tool(description="Return a random string of a given length")(_generate_string)

def main():
    """Main function to run the MCP server."""
    # If running on Fly.io, use the streamable-http transport.
    # Otherwise, default to stdio for local use (e.g., with Goose).
    if os.environ.get("FLY_APP_NAME"):
        mcp.run(transport="streamable-http", port=8080)
    else:
        mcp.run()

if __name__ == "__main__":
    main() 