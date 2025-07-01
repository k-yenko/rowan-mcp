"""
Rowan MCP Server Implementation using FastMCP

This module implements the Model Context Protocol server for Rowan's
computational chemistry platform using the FastMCP framework.
Supports both STDIO and HTTP transports.
"""

import os
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from stjames import Molecule

# Import functions from functions module
from .functions.scan import rowan_scan as scan_function
from .functions.scan_analyzer import rowan_scan_analyzer as scan_analyzer_function
from .functions.admet import rowan_admet as admet_function

from .functions.multistage_opt import rowan_multistage_opt as multistage_opt_function
from .functions.descriptors import rowan_descriptors as descriptors_function
from .functions.tautomers import rowan_tautomers as tautomers_function

from .functions.redox_potential import rowan_redox_potential as redox_potential_function
from .functions.conformers import rowan_conformers as conformers_function
from .functions.electronic_properties import rowan_electronic_properties as electronic_properties_function
from .functions.fukui import rowan_fukui as fukui_function
from .functions.spin_states import rowan_spin_states as spin_states_function
from .functions.solubility import rowan_solubility as solubility_function
from .functions.molecular_dynamics import rowan_molecular_dynamics as molecular_dynamics_function
from .functions.irc import rowan_irc as irc_function
from .functions.docking import rowan_docking as docking_function
from .functions.workflow_management import rowan_workflow_management as workflow_management_function
# from .functions.calculation_retrieve import rowan_calculation_retrieve as calculation_retrieve_function
from .functions.pka import rowan_pka as pka_function
from .functions.folder_management import rowan_folder_management as folder_management_function
from .functions.system_management import rowan_system_management as system_management_function

# Import molecule lookup from functions
from .functions.molecule_lookup import rowan_molecule_lookup as molecule_lookup_function

try:
    import rowan
except ImportError:
    rowan = None

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if available
except ImportError:
    pass  # dotenv not required, but helpful if available

# Initialize FastMCP server
mcp = FastMCP("Rowan MCP Server")

# Register imported functions as MCP tools
rowan_scan = mcp.tool()(scan_function)
rowan_scan_analyzer = mcp.tool()(scan_analyzer_function)
rowan_admet = mcp.tool()(admet_function)

rowan_multistage_opt = mcp.tool()(multistage_opt_function)
rowan_descriptors = mcp.tool()(descriptors_function)
rowan_tautomers = mcp.tool()(tautomers_function)

rowan_redox_potential = mcp.tool()(redox_potential_function)
rowan_conformers = mcp.tool()(conformers_function)
rowan_electronic_properties = mcp.tool()(electronic_properties_function)
rowan_fukui = mcp.tool()(fukui_function)
rowan_spin_states = mcp.tool()(spin_states_function)
rowan_solubility = mcp.tool()(solubility_function)
rowan_molecular_dynamics = mcp.tool()(molecular_dynamics_function)
rowan_irc = mcp.tool()(irc_function)
rowan_docking = mcp.tool()(docking_function)
rowan_workflow_management = mcp.tool()(workflow_management_function)
# rowan_calculation_retrieve = mcp.tool()(calculation_retrieve_function)
rowan_molecule_lookup = mcp.tool()(molecule_lookup_function)
rowan_pka = mcp.tool()(pka_function)
rowan_folder_management = mcp.tool()(folder_management_function)
rowan_system_management = mcp.tool()(system_management_function)

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if not api_key:
    raise ValueError(
        "ROWAN_API_KEY environment variable is required. "
        "Get your API key from https://labs.rowansci.com"
    )

if rowan is None:
    raise ImportError(
        "rowan-python package is required. Install with: pip install rowan-python"
    )

rowan.api_key = api_key

def main() -> None:
    """Main entry point for the MCP server."""
    try:
        # Check for transport mode from command line args or environment
        transport_mode = os.getenv("ROWAN_MCP_TRANSPORT", "stdio").lower()
        
        # Allow override from command line
        if len(sys.argv) > 1:
            if sys.argv[1] == "--http":
                transport_mode = "http"
            elif sys.argv[1] == "--stdio":
                transport_mode = "stdio"
            elif sys.argv[1] == "--help":
                print("Rowan MCP Server")
                print("Usage:")
                print("  rowan-mcp                      # Default STDIO transport")
                print("  rowan-mcp --stdio              # STDIO transport")
                print("  rowan-mcp --http               # HTTP/SSE transport")
                print("")
                print("Development usage:")
                print("  python -m src.server           # Default STDIO transport")
                print("  python -m src.server --stdio   # STDIO transport")
                print("  python -m src.server --http    # HTTP/SSE transport")
                print("")
                print("Environment variables:")
                print("  ROWAN_API_KEY                  # Required: Your Rowan API key")
                print("  ROWAN_MCP_TRANSPORT            # Optional: 'stdio' or 'http' (default: stdio)")
                print("  ROWAN_MCP_HOST                 # Optional: HTTP host (default: 127.0.0.1)")
                print("  ROWAN_MCP_PORT                 # Optional: HTTP port (default: 6276)")
                print("")
                print("HTTP/SSE mode endpoint: http://host:port/sse")
                return
        
        if transport_mode == "http":
            host = os.getenv("ROWAN_MCP_HOST", "127.0.0.1")
            port = int(os.getenv("ROWAN_MCP_PORT", "6276"))
            
            print("🚀 Starting Rowan MCP Server (HTTP/SSE mode)")
            print(f"📡 Server will be available at: http://{host}:{port}/sse")
            print(f"🔑 API Key loaded: {'✓' if api_key else '✗'}")
            print(f"🛠️  Available tools: {len([attr for attr in dir() if attr.startswith('rowan_')])}")
            print("🔗 Connect your MCP client to this endpoint!")
            print("\nPress Ctrl+C to stop the server")
            
            mcp.run(transport="sse", host=host, port=port)
        else:
            print("🚀 Starting Rowan MCP Server (STDIO mode)")
            print(f"🔑 API Key loaded: {'✓' if api_key else '✗'}")
            print(f"🛠️  Available tools: {len([attr for attr in dir() if attr.startswith('rowan_')])}")
            
            mcp.run()  # Default STDIO transport
            
    except KeyboardInterrupt:
        print("\n👋 Server shutdown requested by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 
