"""
Main entry point for Rowan MCP Server when run as a module.

Usage:
    python -m rowan_mcp          # HTTP/SSE mode
    python -m rowan_mcp --help   # Show help
"""

if __name__ == "__main__":
    # HTTP transport only
    from .server import main
    main() 