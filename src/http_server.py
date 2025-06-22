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

# Import all our Rowan functions
from .server import (
    # Basic Calculations
    rowan_admet, rowan_multistage_opt, rowan_electronic_properties,
    
    # Molecular Analysis  
    rowan_conformers, rowan_descriptors, rowan_tautomers,
    
    # Chemical Properties
    rowan_pka, rowan_bde, rowan_redox_potential,
    
    # Advanced Analysis
    rowan_scan, rowan_fukui, rowan_spin_states, rowan_irc, 
    rowan_molecular_dynamics, rowan_hydrogen_bond_basicity,
    
    # Drug Discovery
    rowan_docking,
    
    # Unified Management Tools (NEW - replaces 4 old tools)
    rowan_folder_management, rowan_workflow_management, rowan_system_management,
    
    # Calculation Management
    rowan_calculation_retrieve,
    
    # API key
    api_key
)

# Import the new solubility function
from .functions.solubility import rowan_solubility as rowan_solubility_new

# Mapping of tool names to functions
TOOL_FUNCTIONS = {
    # Basic Calculations
    "rowan_admet": rowan_admet.fn if hasattr(rowan_admet, 'fn') else rowan_admet,
    "rowan_multistage_opt": rowan_multistage_opt.fn if hasattr(rowan_multistage_opt, 'fn') else rowan_multistage_opt,
    "rowan_electronic_properties": rowan_electronic_properties.fn if hasattr(rowan_electronic_properties, 'fn') else rowan_electronic_properties,
    
    # Molecular Analysis
    "rowan_conformers": rowan_conformers.fn if hasattr(rowan_conformers, 'fn') else rowan_conformers,
    "rowan_descriptors": rowan_descriptors.fn if hasattr(rowan_descriptors, 'fn') else rowan_descriptors,
    "rowan_tautomers": rowan_tautomers.fn if hasattr(rowan_tautomers, 'fn') else rowan_tautomers,
    
    # Chemical Properties
    "rowan_pka": rowan_pka.fn if hasattr(rowan_pka, 'fn') else rowan_pka,
    "rowan_bde": rowan_bde.fn if hasattr(rowan_bde, 'fn') else rowan_bde,
    "rowan_redox_potential": rowan_redox_potential.fn if hasattr(rowan_redox_potential, 'fn') else rowan_redox_potential,
    "rowan_solubility": rowan_solubility_new,  # New solubility function from functions/solubility.py
    
    # Advanced Analysis
    "rowan_scan": rowan_scan.fn if hasattr(rowan_scan, 'fn') else rowan_scan,
    "rowan_fukui": rowan_fukui.fn if hasattr(rowan_fukui, 'fn') else rowan_fukui,
    "rowan_spin_states": rowan_spin_states.fn if hasattr(rowan_spin_states, 'fn') else rowan_spin_states,
    "rowan_irc": rowan_irc.fn if hasattr(rowan_irc, 'fn') else rowan_irc,
    "rowan_molecular_dynamics": rowan_molecular_dynamics.fn if hasattr(rowan_molecular_dynamics, 'fn') else rowan_molecular_dynamics,
    "rowan_hydrogen_bond_basicity": rowan_hydrogen_bond_basicity.fn if hasattr(rowan_hydrogen_bond_basicity, 'fn') else rowan_hydrogen_bond_basicity,
    
    # Drug Discovery
    "rowan_docking": rowan_docking.fn if hasattr(rowan_docking, 'fn') else rowan_docking,
    
    # Unified Management Tools (NEW - consolidated from 4 old tools)
    "rowan_folder_management": rowan_folder_management.fn if hasattr(rowan_folder_management, 'fn') else rowan_folder_management,
    "rowan_workflow_management": rowan_workflow_management.fn if hasattr(rowan_workflow_management, 'fn') else rowan_workflow_management,
    "rowan_system_management": rowan_system_management.fn if hasattr(rowan_system_management, 'fn') else rowan_system_management,
    
    # Calculation Management
    "rowan_calculation_retrieve": rowan_calculation_retrieve.fn if hasattr(rowan_calculation_retrieve, 'fn') else rowan_calculation_retrieve,
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
                    doc = func.__doc__ or ""
                    first_line = doc.split('\n')[0].strip() if doc else f"Execute {name}"
                    
                    # Extract basic parameter info from function signature
                    import inspect
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
                        # Call the tool function
                        result = TOOL_FUNCTIONS[tool_name](**arguments)
                        
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
    print("🚀 Starting Rowan MCP HTTP Server...")
    if api_key:
        print("🔑 API Key loaded: ✅")
    else:
        print("❌ No API key found in environment")
        
    print("🌐 Server will be available at: http://127.0.0.1:6276/mcp")
    print("🔗 Connect your MCP client to this endpoint!")
    print(f"🔧 Available tools: {len(TOOL_FUNCTIONS)}")
    
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