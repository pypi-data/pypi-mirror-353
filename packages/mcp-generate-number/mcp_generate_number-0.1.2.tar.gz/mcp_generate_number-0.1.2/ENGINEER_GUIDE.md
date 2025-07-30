# Engineering Guide: Updating the MCP Server

This guide provides a simple, step-by-step workflow for adding new capabilities (tools) to our MCP server. This process is designed to be straightforward, even with no prior experience with MCP.

The project is configured with a fully automated CI/CD pipeline. When you follow these steps, your changes will be automatically deployed to our live server and published for our users.

---

## The Development Workflow

Let's say you want to add a new tool that generates a random hexadecimal color code.

### Step 1: Add Your New Tool

The only file you need to touch is `mcp_generate_number/server.py`.

Open this file and add a new Python function. The only thing that makes it an MCP tool is the `@mcp.tool` decorator that you place directly above it. The function's docstring will automatically become the description the AI uses to know when to use your tool.

```python
# mcp_generate_number/server.py

# ... existing tools ...

@mcp.tool(description="Return a random hex color code")
def generate_hex_color() -> str:
    """Generates a random 6-digit hexadecimal color code."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# ... rest of the file ...
```

That's it. You've created a new capability.

### Step 2: Bump the Package Version

To release a new version, we must increment the package version number. This is critical for package managers to detect the update.

Open the `pyproject.toml` file in the project root and increment the `version` number. Use standard [semantic versioning](https://semver.org/) (e.g., `0.1.1` for a patch, `0.2.0` for a new feature).

```toml
# pyproject.toml

[project]
name = "mcp-generate-number"
version = "0.1.2" # Changed from 0.1.1
# ... rest of the file ...
```

### Step 3: Commit, Deploy, and Publish

This final step is a single command that bundles the entire release process. It will:
1.  Commit your changes to Git.
2.  Push to GitHub, which automatically triggers a deployment of the new version to our Fly.io server.
3.  Build and publish the new version of the package to the Python Package Index (PyPI).

Before running the command, make sure you are authenticated with PyPI. You only need to do this once.

```bash
# First-time setup: Log in to PyPI
# (Use __token__ as the username and your PyPI token as the password)
python -m twine upload --repository-url https://upload.pypi.org/legacy/
```

Now, run the release command from the `mcp-generate-number` directory:

```bash
# Commit, Deploy, and Publish
git add . && git commit -m "feat: Add generate_hex_color tool" && git push && python -m build && python -m twine upload dist/*
```

*(Note: You will be prompted for your PyPI credentials again here if your session has expired).*

---

## How Users Get the Update

The update process for users (including our friends and other engineers using Goose) is **fully automatic**.

The next time they use the tool in their AI assistant, the `uvx mcp-generate-number` command will check PyPI, see that a new version is available, and download it instantly. The new `generate_hex_color` tool will appear in their list of available tools without any manual intervention on their part. 