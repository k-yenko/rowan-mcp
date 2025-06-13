"""
Main entry point for Rowan MCP Server when run as a module.

Usage:
    python -m src                # STDIO mode
    python -m src --http         # HTTP mode
"""

import sys

if __name__ == "__main__":
    # Import the server module and let it handle command line args
    from . import server
    # The server module will check sys.argv and run the appropriate mode 