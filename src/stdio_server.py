#!/usr/bin/env python3
"""
Rowan MCP Server - STDIO mode for MCP clients that use stdio transport.
"""

from .server import mcp, api_key

def main():
    """Run MCP server with stdio transport."""
    print("🚀 Starting Rowan MCP Server (STDIO mode)...")
    if api_key:
        print("🔑 API Key loaded: ✅")
    else:
        print("❌ No API key found in environment")
        
    print("🔗 Server ready for MCP connections!")
    mcp.run()

if __name__ == "__main__":
    main() 