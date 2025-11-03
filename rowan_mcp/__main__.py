"""
Main entry point for Rowan MCP Server when run as a module.

Usage:
    python -m rowan_mcp          # STDIO mode
    python -m rowan_mcp --help   # Show help
"""

if __name__ == "__main__":
    # STDIO transport
    from .server import main
    main() 