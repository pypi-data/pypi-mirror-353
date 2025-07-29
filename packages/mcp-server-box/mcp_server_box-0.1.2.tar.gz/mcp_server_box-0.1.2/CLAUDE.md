# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Install
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and activate
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Lock dependencies
uv lock
```

### Environment Variables
```bash
# Use Doppler to inject environment variables
doppler run -- uv --directory /path/to/mcp-server-box run src/mcp_server_box.py

# Or set up .env file with:
# BOX_CLIENT_ID=your_client_id
# BOX_CLIENT_SECRET=your_client_secret
# BOX_USE_CCG=true  # Optional: for CCG authentication
```

### Running the Server
```bash
# Run the MCP server with Doppler
doppler run -- uv --directory /path/to/mcp-server-box run src/mcp_server_box.py

# Or without Doppler (requires .env file)
uv --directory /path/to/mcp-server-box run src/mcp_server_box.py

# Run with uvx (after building/publishing to PyPI)
uvx mcp-server-box

# Run with uvx and Doppler
doppler run -- uvx mcp-server-box
```

### Testing
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_box_api_file_ops.py

# Run tests with verbose output
pytest -v

# Run tests with print statements visible
pytest -v -s

# Run tests with Doppler environment variables
doppler run -- pytest
```

Note: Before running tests, update the file and folder IDs in test files to match those in your Box account.

### Build and Publish
```bash
# Build the package
uv build

# Publish to PyPI
uv publish
```

## Architecture Overview

### Main Server File
- `src/mcp_server_box.py`: The core MCP server implementation using FastMCP framework
  - Handles Box client lifecycle with OAuth or CCG authentication
  - Implements all Box API tools as MCP tools using the `@mcp.tool()` decorator
  - Uses `BoxContext` for managing the Box client instance across requests

### Tool Categories
1. **Core Box Operations**: Search, read files, folder operations
2. **AI Tools**: Box AI for file analysis and data extraction
3. **File Management**: Upload/download (including chunked upload for large files)
4. **Document Generation**: Box Doc Gen template operations
5. **Sharing**: Share link creation and management
6. **Custom Tools**: Folder upload, chunked upload tools imported as modules

### Authentication
- Supports both OAuth and Client Credentials Grant (CCG)
- Configuration via environment variables:
  - `BOX_CLIENT_ID` and `BOX_CLIENT_SECRET` (required)
  - `BOX_USE_CCG=true` for CCG authentication

### Key Dependencies
- `box-ai-agents-toolkit`: Provides Box API wrappers and utilities
- `mcp[cli]`: Model Context Protocol framework
- `box-sdk-gen`: Box SDK for Python

### Tool Implementation Pattern
```python
@mcp.tool()
async def box_tool_name(ctx: Context, param1: str, param2: Optional[str] = None) -> str:
    # Get Box client from context
    box_client: BoxClient = cast(BoxContext, ctx.request_context.lifespan_context).client
    
    # Perform operation using box_ai_agents_toolkit functions
    response = box_operation(box_client, param1, param2)
    
    # Return as string (often JSON for structured data)
    return json.dumps(response)
```

### Error Handling
- Tools return error messages as JSON strings when exceptions occur
- Box client initialization failures are handled gracefully

### Special Considerations
- Large file uploads (>50MB) should use the chunked upload tool
- FileIDs and FolderIDs need to be strings, automatic conversion is implemented
- JSON serialization helper `_serialize()` handles Box SDK objects that aren't directly JSON-serializable