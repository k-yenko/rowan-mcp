#!/usr/bin/env python3
"""
HTTP Server for Rowan MCP - A simple HTTP interface for MCP over HTTP.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API key from server
from .server import api_key

# Import all functions from their individual files in functions/
from .functions.solubility import rowan_solubility
from .functions.workflow_management import rowan_workflow_management
# from .functions.calculation_retrieve import rowan_calculation_retrieve
from .functions.docking import rowan_docking
from .functions.spin_states import rowan_spin_states
from .functions.molecular_dynamics import rowan_molecular_dynamics
from .functions.irc import rowan_irc
from .functions.scan import rowan_scan
from .functions.scan_analyzer import rowan_scan_analyzer
from .functions.admet import rowan_admet
from .functions.bde import rowan_bde
from .functions.multistage_opt import rowan_multistage_opt
from .functions.descriptors import rowan_descriptors
from .functions.tautomers import rowan_tautomers
from .functions.hydrogen_bond_basicity import rowan_hydrogen_bond_basicity
from .functions.redox_potential import rowan_redox_potential
from .functions.conformers import rowan_conformers
from .functions.electronic_properties import rowan_electronic_properties
from .functions.fukui import rowan_fukui
from .functions.molecule_lookup import rowan_molecule_lookup
# Import the 3 newly created functions
from .functions.pka import rowan_pka
from .functions.folder_management import rowan_folder_management
from .functions.system_management import rowan_system_management

# Mapping of tool names to functions - ONLY from individual function files
TOOL_FUNCTIONS = {
    # Basic Calculations
    "rowan_admet": rowan_admet,
    "rowan_multistage_opt": rowan_multistage_opt,
    "rowan_electronic_properties": rowan_electronic_properties,
    
    # Molecular Analysis
    "rowan_conformers": rowan_conformers,
    "rowan_descriptors": rowan_descriptors,
    "rowan_tautomers": rowan_tautomers,
    
    # Chemical Properties  
    "rowan_bde": rowan_bde,
    "rowan_redox_potential": rowan_redox_potential,
    "rowan_solubility": rowan_solubility,
    "rowan_pka": rowan_pka,
    
    # Advanced Analysis
    "rowan_scan": rowan_scan,
    "rowan_scan_analyzer": rowan_scan_analyzer,
    "rowan_fukui": rowan_fukui,
    "rowan_spin_states": rowan_spin_states,
    "rowan_irc": rowan_irc,
    "rowan_molecular_dynamics": rowan_molecular_dynamics,
    "rowan_hydrogen_bond_basicity": rowan_hydrogen_bond_basicity,
    
    # Drug Discovery
    "rowan_docking": rowan_docking,
    
    # Management Tools
    "rowan_folder_management": rowan_folder_management,
    "rowan_workflow_management": rowan_workflow_management,
    "rowan_system_management": rowan_system_management,
    # "rowan_calculation_retrieve": rowan_calculation_retrieve,
    
    # Lookup Tools
    "rowan_molecule_lookup": rowan_molecule_lookup,
}

def create_app():
    """Create the FastAPI app."""
    app = FastAPI(
        title="Rowan MCP Server", 
        description="HTTP interface for Rowan computational chemistry MCP server",
        version="0.1.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Rowan MCP Server",
            "version": "0.1.0",
            "endpoint": "/mcp",
            "tools_available": len(TOOL_FUNCTIONS)
        }
    
    @app.post("/mcp")
    async def mcp_endpoint(request: Request):
        """Handle MCP JSON-RPC requests over HTTP."""
        try:
            body = await request.json()
            method = body.get("method")
            params = body.get("params", {})
            request_id = body.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "rowan-mcp",
                            "version": "0.1.0"
                        }
                    }
                }
                
            elif method == "tools/list":
                tools = []
                for name, func in TOOL_FUNCTIONS.items():
                    # Handle both regular functions and FunctionTool objects
                    if hasattr(func, '__call__') and hasattr(func, '__doc__'):
                        # Regular function
                        doc = func.__doc__ or ""
                        first_line = doc.split('\n')[0].strip() if doc else f"Execute {name}"
                        
                        # Extract basic parameter info from function signature
                        import inspect
                        try:
                            sig = inspect.signature(func)
                            properties = {}
                            required = []
                            
                            for param_name, param in sig.parameters.items():
                                if param.annotation != inspect.Parameter.empty:
                                    # Basic type mapping
                                    param_type = "string"  # Default
                                    if param.annotation == int:
                                        param_type = "integer"
                                    elif param.annotation == bool:
                                        param_type = "boolean"
                                    elif param.annotation == float:
                                        param_type = "number"
                                    
                                    properties[param_name] = {"type": param_type}
                                    
                                    # Check if required (no default value)
                                    if param.default == inspect.Parameter.empty:
                                        required.append(param_name)
                        except (TypeError, ValueError):
                            # If we can't get signature, provide minimal schema
                            properties = {}
                            required = []
                    
                    elif hasattr(func, 'description'):
                        # FunctionTool object from @mcp.tool() decorator
                        first_line = func.description.split('\n')[0].strip() if func.description else f"Execute {name}"
                        # For FunctionTool objects, we can't easily extract parameter info
                        # so we'll provide a minimal schema
                        properties = {}
                        required = []
                    
                    else:
                        # Fallback for unknown object types
                        first_line = f"Execute {name}"
                        properties = {}
                        required = []
                    
                    tools.append({
                        "name": name,
                        "description": first_line,
                        "inputSchema": {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    })
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in TOOL_FUNCTIONS:
                    try:
                        func = TOOL_FUNCTIONS[tool_name]
                        
                        # Handle both regular functions and FunctionTool objects
                        if hasattr(func, '__call__') and hasattr(func, '__doc__'):
                            # Regular function - call directly
                            result = func(**arguments)
                        elif hasattr(func, 'fn'):
                            # FunctionTool object - call the underlying function
                            result = func.fn(**arguments)
                        else:
                            # Try to call it directly as fallback
                            result = func(**arguments)
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": str(result)
                                    }
                                ]
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": f"Tool execution error: {str(e)}"
                            }
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
                    
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return JSONResponse(content=response)
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id") if 'body' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
            )
    
    return app

# Create the app instance for uvicorn
app = create_app()

def main():
    """Run the HTTP server."""
    print("Starting Rowan MCP HTTP Server...")
    
    api_key = os.getenv("ROWAN_API_KEY")
    if api_key:
        print("API Key loaded: OK")
    else:
        print("No API key found in environment")
        return
        
    print("Server will be available at: http://127.0.0.1:6276/mcp")
    print("Connect your MCP client to this endpoint!")
    print(f"Available tools: {len(TOOL_FUNCTIONS)}")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=6276,
        log_level="info",
        timeout_keep_alive=300,  # 5 minutes keep-alive
        timeout_graceful_shutdown=30,  # 30 seconds graceful shutdown
        # No request timeout limit for long-running calculations
    )

if __name__ == "__main__":
    main() 