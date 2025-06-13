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
from .api_functions import (
    rowan_pka, rowan_conformers, rowan_docking,
    rowan_folder_create, rowan_folder_list, rowan_folder_retrieve, 
    rowan_folder_update, rowan_folder_delete,
    rowan_workflow_create, rowan_workflow_retrieve, rowan_workflow_update,
    rowan_workflow_stop, rowan_workflow_status, rowan_workflow_is_finished,
    rowan_workflow_delete, rowan_workflow_list,
    rowan_calculation_retrieve, api_key
)

# Mapping of tool names to functions
TOOL_FUNCTIONS = {
    "rowan_pka": rowan_pka,
    "rowan_conformers": rowan_conformers,
    "rowan_docking": rowan_docking,
    "rowan_folder_create": rowan_folder_create,
    "rowan_folder_list": rowan_folder_list,
    "rowan_folder_retrieve": rowan_folder_retrieve,
    "rowan_folder_update": rowan_folder_update,
    "rowan_folder_delete": rowan_folder_delete,
    "rowan_workflow_create": rowan_workflow_create,
    "rowan_workflow_retrieve": rowan_workflow_retrieve,
    "rowan_workflow_update": rowan_workflow_update,
    "rowan_workflow_stop": rowan_workflow_stop,
    "rowan_workflow_status": rowan_workflow_status,
    "rowan_workflow_is_finished": rowan_workflow_is_finished,
    "rowan_workflow_delete": rowan_workflow_delete,
    "rowan_workflow_list": rowan_workflow_list,
    "rowan_calculation_retrieve": rowan_calculation_retrieve,
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
        log_level="info"
    )

if __name__ == "__main__":
    main() 