#!/usr/bin/env python3
"""Railway startup script for Rowan MCP server"""
import os
import sys

# Add current directory to path to ensure rowan_mcp can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rowan_mcp.server import mcp

if __name__ == "__main__":
    # Get port from Railway's PORT environment variable
    port = int(os.getenv("PORT", 6276))

    print(f"Starting Rowan MCP Server on 0.0.0.0:{port}", file=sys.stderr)

    # Start server with 0.0.0.0 binding (required for Railway)
    mcp.run(transport="http", host="0.0.0.0", port=port)
