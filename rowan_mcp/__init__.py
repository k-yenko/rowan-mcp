"""
Rowan MCP Server - Computational Chemistry Platform Integration

This package provides MCP (Model Context Protocol) server functionality
for integrating with Rowan's computational chemistry platform.
"""

__version__ = "2.3.0"
__author__ = "Kat Yenko"
__description__ = "MCP server for Rowan computational chemistry platform"

from .server import main

__all__ = ["main"] 