# Engineering Guide: Updating the MCP Server

This guide provides a step-by-step workflow for adding new capabilities (tools) to our MCP server. This process is designed to be straightforward and maintain a high-quality, stable codebase.

The project is configured with a CI pipeline that automatically runs tests on every pull request.

---

## The Development Workflow

Let's say you want to add a new tool that generates a random hexadecimal color code.

### Step 1: Add Your New Tool

The only file you need to touch for adding a tool is `mcp_generate_number/server.py`.

Open this file and add a new Python function. The `@mcp.tool` decorator makes it an MCP tool. The function's docstring will automatically become the description the AI uses to know when to use your tool.

```python
# mcp_generate_number/server.py

# ... existing tools ...

@mcp.tool(description="Return a random hex color code")
def generate_hex_color() -> str:
    """Generates a random 6-digit hexadecimal color code."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# ... rest of the file ...
```

### Step 2: Write a Test for Your Tool

To ensure our server remains reliable, every new tool must have a corresponding test.

Open `tests/test_generate.py` and add a test function that verifies your new tool works as expected.

```python
# tests/test_generate.py

# ... existing tests ...

def test_generate_hex_color():
    """Tests that generate_hex_color returns a valid hex code."""
    color = generate_hex_color()
    assert isinstance(color, str)
    assert len(color) == 7
    assert color.startswith("#")
```

You can run all tests locally before submitting your changes:

```bash
pytest
```

### Step 3: Managing Dependencies

If your new tool requires a new Python package, add it to `requirements.in`. Then, run the following command to update the pinned `requirements.txt` file:

```bash
# Make sure you have uv installed: pip install uv
uv pip compile requirements.in -o requirements.txt
```
This ensures our builds are reproducible.

### Step 4: Bump the Package Version

To release a new version, increment the package version number in `pyproject.toml`. Use standard [semantic versioning](https://semver.org/) (e.g., `0.1.1` for a patch, `0.2.0` for a new feature).

```toml
# pyproject.toml

[project]
name = "mcp-generate-number"
version = "0.1.2" # Changed from 0.1.1
# ... rest of the file ...
```

### Step 5: Release Your Changes

We follow a Pull Request-based workflow to ensure code quality.

1.  **Commit your changes** to a new branch.
    ```bash
    git checkout -b feat/add-hex-color-tool
    git add .
    git commit -m "feat: Add generate_hex_color tool"
    git push --set-upstream origin feat/add-hex-color-tool
    ```
2.  **Open a Pull Request** on GitHub. The CI pipeline will automatically run tests.
3.  **Merge the Pull Request** after it has been approved.
4.  **Publish to PyPI and Deploy**. After merging, checkout the `main` branch, pull the latest changes, and then build and publish the package. Deployment to Fly.io is manual for now.

    ```bash
    # From the main branch, after merging your PR
    git checkout main
    git pull

    # Build and publish to PyPI
    python -m build
    python -m twine upload dist/*

    # Deploy to Fly.io
    flyctl deploy
    ```

---

## How Users Get the Update

The update process for users is **fully automatic**. The next time they use the tool, the new version will be downloaded automatically. 