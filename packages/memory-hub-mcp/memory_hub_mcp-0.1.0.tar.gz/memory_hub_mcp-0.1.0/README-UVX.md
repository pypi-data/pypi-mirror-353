# Memory Hub MCP Server (UV/UVX)

A local memory hub for AI agents with MCP integration, designed for ZenCoder and other MCP clients using stdio transport.

## Quick Start with UVX

### Installation & Usage

```bash
# Install and run directly with uvx
uvx memory-hub-mcp

# Or install locally first
uv pip install memory-hub-mcp
memory-hub-mcp
```

### For ZenCoder Integration

In ZenCoder's custom MCP server configuration:

**Command:** `uvx memory-hub-mcp`  
**Arguments:** (leave empty for default stdio mode)

## Development Setup

```bash
# Clone and setup
git clone <your-repo>
cd memory-hub
uv venv
source .venv/bin/activate
uv pip install -e .

# Run in development
memory-hub-mcp --log-level DEBUG
```

## Available Tools

- **add_memory**: Store content with hierarchical metadata (app_id, project_id, ticket_id)
- **search_memories**: Semantic search with keyword enhancement and LLM synthesis
- **list_app_ids**: List all application IDs
- **list_project_ids**: List all project IDs  
- **list_ticket_ids**: List all ticket IDs
- **health_check**: Server health status

## Configuration

The server expects:
- **Qdrant**: Vector database running (see docker-compose.yml)
- **LM Studio**: For embeddings and chat completions
- **Environment**: Standard .env configuration

## Architecture

- **stdio transport**: Direct MCP protocol communication
- **No HTTP dependencies**: Lightweight, focused on MCP clients
- **Hierarchical memory**: Flexible app/project/ticket organization
- **Hybrid search**: Vector similarity + keyword matching + LLM synthesis

## Differences from HTTP Version

This UV/UVX version:
- ✅ Uses stdio transport (ZenCoder compatible)
- ✅ No FastAPI dependencies
- ✅ Lightweight packaging
- ✅ Direct MCP protocol
- ❌ No web interface
- ❌ No HTTP endpoints 