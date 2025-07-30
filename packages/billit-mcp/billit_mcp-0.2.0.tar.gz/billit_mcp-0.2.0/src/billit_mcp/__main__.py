"""Main entry point for the Billit MCP server."""

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from .server import mcp

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()