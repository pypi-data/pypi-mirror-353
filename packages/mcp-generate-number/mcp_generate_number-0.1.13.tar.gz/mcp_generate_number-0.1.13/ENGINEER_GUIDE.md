# Engineering Guide: Updating the MCP Server

This guide provides a step-by-step workflow for adding new capabilities (tools) to our MCP server.

The project is configured with a fully automated CI/CD pipeline:
1.  **Pull Requests** are automatically tested.
2.  **Merges to `main`** are automatically published to PyPI and deployed to our live server.

---

## The Development Workflow

Let's say you want to add a new tool that generates a random hexadecimal color code.

### Step 1: Create a Branch

Start by creating a new branch for your feature.
```bash
git checkout -b feat/add-hex-color-tool
```

### Step 2: Add Your New Tool

The only file you need to touch for adding a tool is `mcp_generate_number/server.py`.

Open this file and add a new Python function.

```python
# mcp_generate_number/server.py

# ... existing functions ...

def _generate_hex_color() -> str:
    """Generates a random 6-digit hexadecimal color code."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# ... then add it to the mcp tools ...
generate_hex_color = mcp.tool(description="Return a random hex color code")(_generate_hex_color)
```

### Step 3: Write a Test for Your Tool

To ensure our server remains reliable, every new tool must have a corresponding test.

Open `tests/test_generate.py` and add a test function that verifies your new tool works as expected.

```python
# tests/test_generate.py

# ... existing tests ...

def test_generate_hex_color():
    """Tests that generate_hex_color returns a valid hex code."""
    color = _generate_hex_color()
    assert isinstance(color, str)
    assert len(color) == 7
    assert color.startswith("#")
```

### Step 4: Bump the Package Version

This is a critical step. To release a new version, you must increment the package version number in `pyproject.toml`. The automated pipeline will fail if the version already exists on PyPI.

Use standard [semantic versioning](https://semver.org/) (e.g., `0.1.3` to `0.1.4`).

```toml
# pyproject.toml

[project]
name = "mcp-generate-number"
version = "0.1.4" # Changed from 0.1.3
# ... rest of the file ...
```

### Step 5: Open a Pull Request

Commit your changes and push them to GitHub to open a Pull Request against the `main` branch.

```bash
git add .
git commit -m "feat: Add generate_hex_color tool"
git push --set-upstream origin feat/add-hex-color-tool
```

Our test suite will run automatically on your PR.

### Step 6: Merge to Release

Once your Pull Request is approved and all tests are passing, you can **merge it into `main`**.

Merging will automatically trigger the deployment pipeline, which will:
1.  Publish the new version of your package to PyPI.
2.  Deploy the new server version to Fly.io.

The update is now live and will be automatically available to all users.

---

## How Users Get the Update

The update process for users is **fully automatic**. The next time they use the tool, the new version will be downloaded automatically. 