"""
Main entry point for Rowan MCP Server when run as a module.

Usage:
    python -m src                # STDIO mode (default)
    python -m src --stdio        # STDIO mode  
    python -m src --http         # HTTP mode
    python -m src --help         # Show help
"""

if __name__ == "__main__":
    # All modes now handled by the unified server
    from .server import main
    main() 