"""
Main entry point for Rowan MCP Server when run as a module.

Usage:
    python -m src                # STDIO mode
    python -m src --http         # HTTP mode
"""

import sys

if __name__ == "__main__":
    if "--http" in sys.argv:
        # HTTP mode
        from .http_server import main
        main()
    else:
        # Default STDIO mode  
        from .server import main
        main() 