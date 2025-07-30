"""
CLI entry point for Memory Hub MCP Server (stdio only)
Designed specifically for ZenCoder and other MCP clients
"""

import asyncio
import argparse
import sys
import logging

from .mcp_server import create_server

# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_server():
    """Run MCP server with stdio transport"""
    try:
        server = create_server()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Memory Hub MCP Server - stdio transport for ZenCoder and MCP clients"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info("Starting Memory Hub MCP Server (stdio mode)")
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 