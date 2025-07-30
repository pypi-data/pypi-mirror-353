# main.py - FastAPI App setup and MCP integration for Memory Hub

from fastapi import FastAPI, Depends
import httpx
import logging
from contextlib import asynccontextmanager

from models import MemoryItemIn, MemorySearchRequest, AddMemoryResponse, SearchResponse, ListIdsResponse
from endpoints import add_memory, search_memories, health_check, list_app_ids, list_project_ids, list_ticket_ids, get_http_client
from services import startup_event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MCP reference for proper lifecycle management
mcp_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with comprehensive error handling."""
    global mcp_server
    
    # Startup
    logger.info("Starting Memory Hub MCP Server...")
    
    try:
        await startup_event()
        logger.info("Memory Hub core services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize core services: {e}")
        raise  # Cannot continue without core services
    
    # MCP server should already be set up, just log status
    if mcp_server:
        logger.info("FastAPI-MCP integration already enabled at /mcp")
    else:
        logger.warning("FastAPI-MCP integration not available")
    
    yield
    
    # Shutdown
    try:
        logger.info("Memory Hub shutdown initiated")
        # Add any cleanup logic here if needed
        logger.info("Memory Hub shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# --- FastAPI App Creation ---
app = FastAPI(
    title="Memory Hub MCP Server",
    description="Local Memory Hub for AI agents with MCP integration",
    version="0.1.0",
    lifespan=lifespan
)

# --- Register endpoints FIRST ---
app.post("/add_memory", response_model=AddMemoryResponse, operation_id="add_memory", tags=["memory"])(add_memory)
app.post("/search_memories", response_model=SearchResponse, operation_id="search_memories", tags=["memory"])(search_memories)
app.get("/list_app_ids", response_model=ListIdsResponse, operation_id="list_app_ids", tags=["metadata"])(list_app_ids)
app.get("/list_project_ids", response_model=ListIdsResponse, operation_id="list_project_ids", tags=["metadata"])(list_project_ids)
app.get("/list_ticket_ids", response_model=ListIdsResponse, operation_id="list_ticket_ids", tags=["metadata"])(list_ticket_ids)
app.get("/health", operation_id="health_check", tags=["system"])(health_check)

# --- Setup MCP integration AFTER all routes are registered ---
try:
    from fastapi_mcp import FastApiMCP
    
    # Create MCP wrapper with all routes already registered
    mcp_server = FastApiMCP(
        app,
        name="Memory Hub MCP Server",
        description="Local Memory Hub for AI agents with MCP integration"
    )
    
    # Mount MCP server to expose tools
    mcp_server.mount()
    
    logger.info("FastAPI-MCP integration configured successfully")
    
except ImportError as e:
    logger.warning(f"FastAPI-MCP not available: {e}")
    # Continue without MCP integration - server can still work via direct API calls
    mcp_server = None
except Exception as e:
    logger.error(f"Failed to setup FastAPI-MCP: {e}")
    # Continue without MCP integration - server can still work via direct API calls
    mcp_server = None

if __name__ == "__main__":
    import uvicorn
    # Make sure Qdrant is running and collection exists (or will be created on startup)
    # Make sure LM Studio is running with your models
    uvicorn.run(app, host="0.0.0.0", port=8000) 