"""
Arxiv MCP Server initialization
"""

import sys
import os
# Add the parent directory to sys.path so we can import modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arxiv_mcp_server import server
import asyncio


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())

if __name__ == "__main__":
    main()

__all__ = ["main", "server"]
