"""
Rowan MCP Server - Computational Chemistry Platform Integration

This package provides MCP (Model Context Protocol) server functionality
for integrating with Rowan's computational chemistry platform.
"""

__version__ = "1.0.0"
__author__ = "Rowan MCP Team"
__description__ = "MCP server for Rowan computational chemistry platform"

def main():
    """Entry point for the rowan-mcp command."""
    import sys
    import os
    
    # Add src to path to import the server module
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)
    
    try:
        from src.server import main as server_main
        server_main()
    except ImportError:
        # Fallback for development mode
        import importlib.util
        spec = importlib.util.find_spec("src.server")
        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.main()
        else:
            print("Error: Cannot find Rowan MCP server module")
            print("Make sure the package is properly installed")
            sys.exit(1)

__all__ = ["main"] 