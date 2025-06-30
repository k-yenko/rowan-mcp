"""
Rowan MCP Server Implementation using FastMCP

This module implements the Model Context Protocol server for Rowan's
computational chemistry platform using the FastMCP framework.
"""

import os
import logging
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
from .functions.bde import rowan_bde as bde_function
from .functions.multistage_opt import rowan_multistage_opt as multistage_opt_function
from .functions.descriptors import rowan_descriptors as descriptors_function
from .functions.tautomers import rowan_tautomers as tautomers_function
from .functions.hydrogen_bond_basicity import rowan_hydrogen_bond_basicity as hb_basicity_function
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
from .functions.calculation_retrieve import rowan_calculation_retrieve as calculation_retrieve_function

# Import management functions from server_backup (these haven't been moved to separate files yet)
from .server_backup import rowan_folder_management as folder_management_function
from .server_backup import rowan_system_management as system_management_function
from .server_backup import rowan_pka as pka_function

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rowan_mcp.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP()

# Register imported functions as MCP tools
rowan_scan = mcp.tool()(scan_function)
rowan_scan_analyzer = mcp.tool()(scan_analyzer_function)
rowan_admet = mcp.tool()(admet_function)
rowan_bde = mcp.tool()(bde_function)
rowan_multistage_opt = mcp.tool()(multistage_opt_function)
rowan_descriptors = mcp.tool()(descriptors_function)
rowan_tautomers = mcp.tool()(tautomers_function)
rowan_hydrogen_bond_basicity = mcp.tool()(hb_basicity_function)
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
rowan_calculation_retrieve = mcp.tool()(calculation_retrieve_function)
rowan_molecule_lookup = mcp.tool()(molecule_lookup_function)

# Management functions from server_backup are already FastMCP tools, so don't wrap them again
rowan_folder_management = folder_management_function
rowan_system_management = system_management_function
rowan_pka = pka_function

# Manually add the pre-existing FastMCP tools to the main server
mcp.add_tool(folder_management_function)
mcp.add_tool(system_management_function) 
mcp.add_tool(pka_function)

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if not api_key:
    logger.error("ROWAN_API_KEY environment variable not found")
    raise ValueError(
        "ROWAN_API_KEY environment variable is required. "
        "Get your API key from https://labs.rowansci.com"
    )
else:
    logger.info(f" ROWAN_API_KEY loaded (length: {len(api_key)})")

if rowan is None:
    logger.error("rowan-python package not found")
    raise ImportError(
        "rowan-python package is required. Install with: pip install rowan-python"
    )
else:
    logger.info(" rowan-python package loaded successfully")

rowan.api_key = api_key
logger.info(" Rowan API key configured")

def log_mcp_call(func):
    """Decorator to log MCP tool calls with detailed information."""
    import functools
    
    @functools.wraps(func)
    def wrapper(**kwargs):  # Only use **kwargs to be compatible with FastMCP
        func_name = func.__name__
        start_time = time.time()
        
        # Log the incoming request
        logger.info(f" MCP Tool Called: {func_name}")
        logger.info(f" Parameters: {kwargs}")
        
        try:
            # Execute the function
            result = func(**kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Log successful completion
            logger.info(f" {func_name} completed successfully in {execution_time:.2f}s")
            logger.debug(f"📤 Response preview: {str(result)[:200]}...")
            
            return result
            
        except Exception as e:
            # Calculate execution time even for errors
            execution_time = time.time() - start_time
            
            # Log the error with full traceback
            logger.error(f" {func_name} failed after {execution_time:.2f}s")
            logger.error(f" Error: {str(e)}")
            logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
            
            # Extract Rowan's actual error message if available
            rowan_error_msg = None
            http_status = None
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    http_status = getattr(e.response, 'status_code', 'Unknown')
                    
                    if hasattr(e.response, 'text'):
                        response_text = e.response.text
                        # Try to parse JSON error response
                        import json
                        try:
                            error_data = json.loads(response_text)
                            rowan_error_msg = error_data.get('message', error_data.get('error', response_text))
                        except json.JSONDecodeError:
                            rowan_error_msg = response_text
                    elif hasattr(e.response, 'content'):
                        rowan_error_msg = e.response.content.decode('utf-8', errors='ignore')
                except Exception as extract_err:
                    logger.error(f" Could not extract error message: {extract_err}")
            
            # Build comprehensive error message for user
            error_parts = []
            
            if rowan_error_msg and rowan_error_msg.strip():
                error_parts.append(f"Rowan API Error: {rowan_error_msg}")
            
            if http_status:
                error_parts.append(f"HTTP Status: {http_status}")
                
            # Add exception details
            error_parts.append(f"Exception: {type(e).__name__}")
            
            # Add original error message if we have one and it's different
            original_msg = str(e)
            if original_msg and original_msg not in (rowan_error_msg or ''):
                error_parts.append(f"Details: {original_msg}")
            
            # Provide specific guidance for common error types
            if isinstance(e, AssertionError):
                error_parts.append("This appears to be a validation error in the Rowan library")
            
            combined_error = " | ".join(error_parts)
            return f" {combined_error}"
            
    return wrapper

def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    
    # Special handling for long-running calculations
    if workflow_type in ["multistage_opt", "conformer_search"]:
        ping_interval = kwargs.get('ping_interval', 5)
        blocking = kwargs.get('blocking', True)
        if blocking:
            if workflow_type == "multistage_opt":
                logger.info(f" Multi-stage optimization may take several minutes...")
            else:
                logger.info(f" Conformer search may take several minutes...")
            logger.info(f" Progress will be checked every {ping_interval} seconds")
        else:
            logger.info(f" {workflow_type.replace('_', ' ').title()} submitted without waiting")
    
    try:
        start_time = time.time()
        result = rowan.compute(workflow_type=workflow_type, **kwargs)
        api_time = time.time() - start_time
        
        if isinstance(result, dict) and 'uuid' in result:
            job_status = result.get('status', result.get('object_status', 'Unknown'))
            status_names = {0: "Queued", 1: "Running", 2: "Completed", 3: "Failed", 4: "Stopped", 5: "Awaiting Queue"}
            status_text = status_names.get(job_status, f"Unknown ({job_status})")
        
        return result
        
    except Exception as e:
        api_time = time.time() - start_time
        
        # Enhanced error logging for better debugging
        logger.error(f" Exception Type: {type(e).__name__}")
        logger.error(f"📄 Full Exception: {repr(e)}")
        logger.error(f" Exception Args: {e.args}")
        
        # Log full stack trace for debugging
        import traceback
        logger.error(f"📍 Full Stack Trace:\n{traceback.format_exc()}")
        
        # Log the actual response from Rowan API if available
        response_logged = False
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f" HTTP Status: {e.response.status_code}")
            try:
                if hasattr(e.response, 'text'):
                    response_text = e.response.text
                    logger.error(f" Rowan API Response Text: {response_text}")
                    response_logged = True
                elif hasattr(e.response, 'content'):
                    response_content = e.response.content.decode('utf-8', errors='ignore')
                    logger.error(f" Rowan API Response Content: {response_content}")
                    response_logged = True
                
                # Also try to get headers for more context
                if hasattr(e.response, 'headers'):
                    logger.error(f" Response Headers: {dict(e.response.headers)}")
                    
            except Exception as log_err:
                logger.error(f" Could not read response: {log_err}")
        
        # For requests exceptions, try to get more details
        if hasattr(e, '__dict__'):
            logger.error(f" Exception attributes: {list(e.__dict__.keys())}")
            
        # Check if it's a requests exception with specific handling
        if 'requests' in str(type(e).__module__):
            logger.error(f" This is a requests library exception")
            
        # If we couldn't log a response above, try alternative approaches
        if not response_logged:
            logger.error(f" No HTTP response data found in exception")
            
            # Try to get any string representation that might contain useful info
            exception_str = str(e)
            if exception_str and exception_str != '':
                logger.error(f" Exception message: {exception_str}")
            else:
                logger.error(f" Exception has no message")
        
        raise e

# Tool implementations

def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info(f"🚀 Starting Rowan MCP Server...")
        logger.info(f"📊 Log level: {logger.level}")
        logger.info(f"📁 Log file: rowan_mcp.log")
        logger.info(f"🔑 API Key loaded: {'✅' if api_key else '❌'}")
        logger.info("🔗 Server ready for MCP connections!")
        
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Server shutdown requested by user")
        print("\n👋 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server startup error: {e}")
        logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
        print(f"❌ Server error: {e}")
        print("📋 Check rowan_mcp.log for detailed error information")

if __name__ == "__main__":
    main()
