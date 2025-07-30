"""Main entry point for the Billit MCP server."""

import logging
import os

from dotenv import load_dotenv

from .server import mcp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()