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
from .functions.molecule_lookup import lookup_molecule_smiles

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

# Quantum Chemistry Guidance Tool
@mcp.tool()
def rowan_molecule_lookup(molecule_name: str) -> str:
    """Look up the canonical SMILES string for common molecule names.
    
    Provides consistent SMILES representations for common molecules to ensure
    reproducible results across different Rowan calculations.
    
    Args:
        molecule_name: Name of the molecule (e.g., "phenol", "benzene", "caffeine")
    
    Returns:
        Canonical SMILES string and molecular information
    """
    canonical_smiles = lookup_molecule_smiles(molecule_name)
    
    # Check if we found a match or returned the input as-is
    if canonical_smiles == molecule_name:
        formatted = f" No SMILES lookup found for '{molecule_name}'\n\n"
        formatted += f" **Using input as-is:** {molecule_name}\n"
        formatted += f" **If this is a molecule name, try:**\n"
        formatted += f"• Check spelling (e.g., 'phenol', 'benzene', 'caffeine')\n"
        formatted += f"• Use rowan_molecule_lookup('') to see available molecules\n"
        formatted += f"• If it's already a SMILES string, you can use it directly\n"
    else:
        formatted = f" SMILES lookup successful!\n\n"
        formatted += f" **Molecule:** {molecule_name}\n"
        formatted += f" **Canonical SMILES:** {canonical_smiles}\n"
        formatted += f" **Usage:** Use '{canonical_smiles}' in Rowan calculations for consistent results\n"
    
    # Show available molecules if empty input
    if not molecule_name.strip():
        formatted = f" **Available Molecules for SMILES Lookup:**\n\n"
        
        categories = {
            "Aromatics": ["phenol", "benzene", "toluene", "aniline", "pyridine", "naphthalene"],
            "Aliphatics": ["methane", "ethane", "propane", "butane", "cyclohexane"],
            "Alcohols": ["methanol", "ethanol", "isopropanol"],
            "Common Drugs": ["caffeine", "ibuprofen", "aspirin", "acetaminophen"],
            "Solvents": ["water", "acetone", "dmso", "thf"],
        }
        
        for category, molecules in categories.items():
            formatted += f"**{category}:**\n"
            for mol in molecules:
                smiles = lookup_molecule_smiles(mol)
                formatted += f"• {mol}: `{smiles}`\n"
            formatted += "\n"
        
        formatted += f" **Example:** rowan_molecule_lookup('phenol') → 'Oc1ccccc1'\n"
    
    return formatted

# @mcp.tool()
# def rowan_qc_guide() -> str:
#     """Get comprehensive guidance for quantum chemistry calculations in Rowan.
#     
#     Provides detailed information about:
#     - Required parameters for QC calculations
#     - Available engines (Psi4, TeraChem, PySCF, xTB, AIMNet2)
#     - Common methods and basis sets
#     - Available tasks and properties
#     - Best practices and recommendations
#     
#     Use this for: Understanding Rowan's quantum chemistry capabilities
#     
#     Returns:
#         Comprehensive quantum chemistry guidance
#     """
#     guidance = get_qc_guidance()
#     return guidance

# Unified Quantum Chemistry Tool - COMMENTED OUT FOR NOW
# @mcp.tool()
# @log_mcp_call
# def rowan_quantum_chemistry(
#     name: str,
#     molecule: str,
#     method: Optional[str] = None,
#     basis_set: Optional[str] = None,
#     tasks: Optional[List[str]] = None,
#     corrections: Optional[List[str]] = None,
#     engine: Optional[str] = None,
#     charge: int = 0,
#     multiplicity: int = 1,
#     folder_uuid: Optional[str] = None,
#     blocking: bool = True,
#     ping_interval: int = 5,
#     use_recommended_defaults: bool = True,
#     additional_settings: Optional[Dict[str, Any]] = None
# ) -> str:
#     """Run quantum chemistry calculations with intelligent defaults or custom settings.
#     
#     ** Smart Defaults**: When no parameters are specified, uses Rowan's settings:
#     - Method: B3LYP (popular, reliable hybrid functional)
#     - Basis Set: pcseg-1 (better than 6-31G(d) at same cost)
#     - Tasks: ["energy", "optimize"] (energy + geometry optimization)
#     - Corrections: ["d3bj"] (dispersion correction for better accuracy)
#     
#     ** Full Customization**: All parameters can be overridden for advanced users
#     
#     **Available Methods (16 total):**
#     - HF: Hartree-Fock (unrestricted for open-shell)
#     - Pure DFT: LSDA, PBE, BLYP, BP86, B97-D3, r2SCAN, TPSS, M06-L
#     - Hybrid DFT: PBE0, B3LYP, B3PW91, CAM-B3LYP, ωB97X-D3, ωB97X-V, ωB97M-V
#     
#     **Available Basis Sets (29 total):**
#     - Recommended: pcseg-1 (DFT), pcseg-2 (high accuracy)
#     - Popular: 6-31G*, 6-31G(d,p), cc-pVDZ(seg-opt)
#     - Fast: MIDI!, STO-3G
#     
#     **Available Corrections:**
#     - D3BJ: Grimme's D3 dispersion with Becke-Johnson damping
#     
#     Use this for: All quantum chemistry calculations (beginners get good defaults, experts get full control)
#     
#     Args:
#         name: Name for the calculation
#         molecule: Molecule SMILES string (e.g., 'CC(=O)OC1=CC=CC=C1C(=O)O' for aspirin)
#         method: QC method - if None, uses 'b3lyp' (recommended default)
#         basis_set: Basis set - if None, uses 'pcseg-1' (recommended default)
#         tasks: List of tasks - if None, uses ['energy', 'optimize'] (recommended default)
#         corrections: List of corrections - if None, uses ['d3bj'] (recommended default)
#         engine: Computational engine - if None, defaults to 'psi4' (required by Rowan API)
#         charge: Molecular charge (default: 0)
#         multiplicity: Spin multiplicity (default: 1 for singlet)
#         folder_uuid: Optional folder UUID for organization
#         blocking: Whether to wait for completion (default: True)
#         ping_interval: Check status interval in seconds (default: 5)
#         use_recommended_defaults: If True, uses smart defaults when parameters are None
#         additional_settings: Extra calculation-specific settings
#     
#     Returns:
#         Quantum chemistry calculation results
#     """
#     
#     # Always provide quantum chemistry guidance context first
#     guidance_context = rowan_qc_guide()
#     
#     # Determine if we're using defaults or custom settings
#     using_defaults = (method is None and basis_set is None and 
#                      tasks is None and corrections is None)
#     
#     # Apply intelligent defaults when no parameters specified
#     if use_recommended_defaults and using_defaults:
#         method = "b3lyp"  # Popular, reliable hybrid functional
#         basis_set = "pcseg-1"  # Better than 6-31G(d) at same cost
#         tasks = ["energy", "optimize"]  # Energy + geometry optimization
#         corrections = ["d3bj"]  # Dispersion correction for accuracy
#         if engine is None:  # Only set default if not provided
#             engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#         default_msg = "Rowan's defaults"
#     elif using_defaults:
#         # Fall back to Rowan's system defaults but ensure engine is set
#         if engine is None:  # Only set default if not provided
#             engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#         default_msg = "Rowan's system defaults (HF/STO-3G)"
#     else:
#         # For custom settings, still ensure engine is set if not provided
#         if engine is None:  # Only set default if not provided
#             engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#         default_msg = "Custom user settings"
#     
#     # Validate inputs and provide guidance
#     if method and method.lower() not in QC_METHODS:
#         available_methods = ", ".join(QC_METHODS.keys())
#         return f" Invalid method '{method}'. Available methods: {available_methods}"
#     
#     if basis_set and basis_set.lower() not in QC_BASIS_SETS:
#         available_basis = ", ".join(QC_BASIS_SETS.keys())
#         return f" Invalid basis set '{basis_set}'. Available basis sets: {available_basis}"
#     
#     if tasks:
#         invalid_tasks = [task for task in tasks if task.lower() not in QC_TASKS]
#         if invalid_tasks:
#             available_tasks = ", ".join(QC_TASKS.keys())
#             return f" Invalid tasks {invalid_tasks}. Available tasks: {available_tasks}"
#     
#     if engine and engine.lower() not in QC_ENGINES:
#         available_engines = ", ".join(QC_ENGINES.keys())
#         return f" Invalid engine '{engine}'. Available engines: {available_engines}"
#     
#     if corrections:
#         invalid_corrections = [corr for corr in corrections if corr.lower() not in QC_CORRECTIONS]
#         if invalid_corrections:
#             available_corrections = ", ".join(QC_CORRECTIONS.keys())
#             return f" Invalid corrections {invalid_corrections}. Available corrections: {available_corrections}"
#     
#     # Engine is always required, so ensure it's set
#     if engine is None:
#         engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#     
#     # Log the QC parameters
#     logger.info(f" Tasks: {tasks or 'system default'}")
#     logger.info(f" Corrections: {corrections or 'none'}")
#     
#     try:
#         # Build parameters for rowan.compute call based on documentation
#         compute_params = {
#             "name": name,
#             "input_mol": molecule,  # Use input_mol as shown in docs
#             "folder_uuid": folder_uuid,
#             "blocking": blocking,
#             "ping_interval": ping_interval
#         }
#         
#         # Add QC parameters directly (not in settings object)
#         if method:
#             compute_params["method"] = method.lower()
#         if basis_set:
#             compute_params["basis_set"] = basis_set.lower()
#         if tasks:
#             compute_params["tasks"] = [task.lower() for task in tasks]
#         if corrections:
#             compute_params["corrections"] = [corr.lower() for corr in corrections]
#         if engine:
#             compute_params["engine"] = engine.lower()
#         if charge != 0:
#             compute_params["charge"] = charge
#         if multiplicity != 1:
#             compute_params["multiplicity"] = multiplicity
#         
#         # Add any additional settings
#         if additional_settings:
#             compute_params.update(additional_settings)
#         
#         # Use "calculation" workflow type as shown in documentation
#         result = log_rowan_api_call(
#             workflow_type="calculation",
#             **compute_params
#         )
#         
#         # Check actual job status and format accordingly
#         # First try to get status from submission response, then check via API if needed
#         job_status = result.get('status', result.get('object_status', None))
#         
#         # If status is None (common after submission), try to check via API
#         if job_status is None and result.get('uuid'):
#             try:
#                 job_status = rowan.Workflow.status(uuid=result.get('uuid'))
#             except Exception as e:
#                 job_status = None
#         
#         status_names = {
#             0: ("", "Queued"),
#             1: ("", "Running"), 
#             2: ("", "Completed Successfully"),
#             3: ("", "Failed"),
#             4: ("⏹", "Stopped"),
#             5: ("⏸", "Awaiting Queue")
#         }
#         
#         status_icon, status_text = status_names.get(job_status, ("❓", f"Unknown ({job_status})"))
#         
#         # Special handling for None status (very common case)
#         if job_status is None:
#             status_icon, status_text = ("", "Submitted (status pending)")
#         
#         # Use appropriate header based on actual status
#         if job_status == 2:
#             formatted = f" Quantum chemistry calculation '{name}' completed successfully!\n\n"
#         elif job_status == 3:
#             formatted = f" Quantum chemistry calculation '{name}' failed!\n\n"
#         elif job_status in [0, 1, 5]:
#             formatted = f" Quantum chemistry calculation '{name}' submitted!\n\n"
#         elif job_status == 4:
#             formatted = f"⏹ Quantum chemistry calculation '{name}' was stopped!\n\n"
#         else:
#             formatted = f" Quantum chemistry calculation '{name}' status unknown!\n\n"
#             
#         formatted += f" Molecule: {molecule}\n"
#         formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
#         formatted += f" Status: {status_icon} {status_text} ({job_status})\n"
#         formatted += f"⚙ Used: {default_msg}\n"
#         
#         # Show applied settings
#         if method or basis_set or tasks or corrections or engine or charge != 0 or multiplicity != 1:
#             formatted += f"\n⚙ **Applied Settings:**\n"
#             if method:
#                 formatted += f"   Method: {method.upper()} - {QC_METHODS.get(method.lower(), 'Custom method')}\n"
#             if basis_set:
#                 formatted += f"   Basis Set: {basis_set} - {QC_BASIS_SETS.get(basis_set.lower(), 'Custom basis')}\n"
#             if tasks:
#                 formatted += f"   Tasks: {', '.join(tasks)}\n"
#             if corrections:
#                 formatted += f"   Corrections: {', '.join(corrections)} - "
#                 formatted += ", ".join([QC_CORRECTIONS.get(corr.lower(), 'Custom correction') for corr in corrections]) + "\n"
#             if engine:
#                 formatted += f"   Engine: {engine.upper()} - {QC_ENGINES.get(engine.lower(), 'Custom engine')}\n"
#             if charge != 0 or multiplicity != 1:
#                 formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
#         
#         # Add status-appropriate guidance
#         formatted += f"\n **Next Steps:**\n"
#         if job_status == 2:  # Completed successfully
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to get detailed results\n"
#             formatted += f"• Results should include energies, geometries, and other calculated properties\n"
#         elif job_status == 3:  # Failed
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to see error details\n"
#             formatted += f"• **Troubleshooting tips:**\n"
#             formatted += f"  - Try simpler settings: method='hf', basis_set='sto-3g'\n"
#             formatted += f"  - Use `rowan_multistage_opt()` for geometry optimization (more robust)\n"
#             formatted += f"  - Check if SMILES string is valid\n"
#             formatted += f"  - For difficult molecules, try method='xtb' (semiempirical)\n"
#         elif job_status in [0, 1, 5]:  # Queued/Running/Awaiting
#             formatted += f"• Check status: `rowan_workflow_status('{result.get('uuid', 'UUID')}')`\n"
#             formatted += f"• Wait for completion, then retrieve results\n"
#             formatted += f"• Calculation may take several minutes depending on molecule size\n"
#         elif job_status == 4:  # Stopped
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to see why it was stopped\n"
#             formatted += f"• You can restart with the same or different parameters\n"
#         else:  # Unknown status
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to get more information\n"
#             formatted += f"• Check `rowan_workflow_status('{result.get('uuid', 'UUID')}')` for current status\n"
#             
#         # Add general guidance for successful submissions or unknown states
#         if job_status != 3:  # Don't show alternatives if it failed
#             if using_defaults and use_recommended_defaults:
#                 formatted += f"• **For future calculations:** Try different methods/basis sets for different accuracy/speed trade-offs\n"
#         
#         # Prepend guidance context to the result
#         final_result = f"{guidance_context}\n\n" + "="*80 + "\n\n" + formatted
#         return final_result
#         
#     except Exception as e:
#         error_msg = f" Quantum chemistry calculation submission failed: {str(e)}\n\n"
#         error_msg += " **This is a submission error, not a calculation failure.**\n"
#         error_msg += "The job never started due to invalid parameters or API issues.\n\n"
#         if "method" in str(e).lower() or "basis" in str(e).lower():
#             error_msg += " **Parameter Error**: Try using recommended defaults by calling with just name and molecule\n"
#             error_msg += "Or check parameter spelling and availability\n\n"
#         elif "engine" in str(e).lower():
#             error_msg += " **Engine Error**: The engine parameter is required. This should be auto-set to 'psi4'\n\n"
#         
#         # Prepend guidance context even in error cases
#         final_error_result = f"{guidance_context}\n\n" + "="*80 + "\n\n" + error_msg
#         return final_error_result

# Electronic Properties - HOMO/LUMO, Orbitals (imported from functions/electronic_properties.py)

# Descriptors - Molecular Feature Vectors

# Scan - Potential Energy Surface Scans

# Fukui Indices - Reactivity Analysis (imported from functions/fukui.py)

# Scan Analyzer
@mcp.tool()
@log_mcp_call
def rowan_scan_analyzer(
    scan_uuid: str,
    action: str = "analyze",
    energy_threshold: Optional[float] = None
) -> str:
    """Analyze scan results and extract key geometries for IRC workflows.
    
    ** Essential IRC Tool:**
    - Analyzes completed scan workflows to extract transition state geometries
    - Provides formatted results ready for IRC calculations
    - Identifies energy maxima, minima, and barriers automatically
    
    ** Analysis Actions:**
    - **analyze**: Complete analysis with energy profile and key points (default)
    - **extract_ts**: Extract highest energy geometry (TS approximation for IRC)
    - **extract_minima**: Extract low energy geometries 
    - **energy_profile**: Show energy vs coordinate data for plotting
    
    ** IRC Workflow Integration:**
    1. Run scan → get scan_uuid
    2. Use: rowan_scan_analyzer(scan_uuid, "extract_ts")
    3. Copy TS geometry for transition state optimization
    4. Run IRC from optimized TS
    
    ** Example Usage:**
    - Full analysis: rowan_scan_analyzer("uuid-123", "analyze")
    - Extract TS: rowan_scan_analyzer("uuid-123", "extract_ts")
    - Find minima: rowan_scan_analyzer("uuid-123", "extract_minima", energy_threshold=2.0)
    
    Args:
        scan_uuid: UUID of the completed scan workflow to analyze
        action: Analysis type ("analyze", "extract_ts", "extract_minima", "energy_profile")
        energy_threshold: Energy threshold in kcal/mol above minimum for minima extraction (default: None)
    
    Returns:
        Analysis results with geometries, energies, and IRC preparation instructions
    """
    # Use the imported scan analyzer function from functions module
    return scan_analyzer_function(
        scan_uuid=scan_uuid,
        action=action,
        energy_threshold=energy_threshold
    )

# Spin States
@mcp.tool()
@log_mcp_call
def rowan_spin_states(
    name: str,
    molecule: str,
    states: Optional[List[int]] = None,
    charge: Optional[int] = None,
    multiplicity: Optional[int] = None,
    mode: str = "rapid",
    solvent: Optional[str] = None,
    xtb_preopt: bool = True,
    constraints: Optional[List[Dict[str, Any]]] = None,
    transition_state: bool = False,
    frequencies: bool = False,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 10,
    auto_analyze: bool = True
) -> str:
    """Determine preferred spin states for molecules with intelligent auto-analysis.
    
    **🤖 INTELLIGENT AUTO-ANALYSIS:**
    - Automatically recognizes transition metal complexes (e.g., Mn(Cl)6, Fe(CN)6, Cu(H2O)4)
    - Predicts appropriate charge, multiplicity, and spin states based on chemical knowledge
    - Suggests realistic spin states for d-electron configurations
    - Provides chemical explanations for predictions
    
    ** Spin State Analysis:**
    - Uses multi-stage optimization (xTB → AIMNet2 → DFT) for accurate energies
    - Validates multiplicity consistency (all must have same parity)
    - Ranks spin states by energy to identify ground state
    - Supports transition metal complexes and radical species
    
    ** Auto-Detected Complexes:**
    - Mn(Cl)6 → charge: -4, states: [2, 6] (d5: low-spin vs high-spin)
    - Fe(CN)6 → charge: -4, states: [1, 5] (d6: low-spin vs high-spin) 
    - Cu(H2O)4 → charge: +2, states: [2] (d9: always doublet)
    - Ni(H2O)6 → charge: +2, states: [3] (d8: high-spin triplet)
    - Co(NH3)6 → charge: +3, states: [1] (d6: low-spin singlet)
    
    ** Manual Override Available:**
    - All auto-detected parameters can be manually overridden
    - Set auto_analyze=False to disable automatic analysis
    - Specify states, charge, multiplicity explicitly if needed
    
    Use this for: Transition metal complexes, radical species, magnetic materials, spin crossover systems
    
    Args:
        name: Name for the calculation
        molecule: Molecular formula or SMILES (e.g., "Mn(Cl)6", "Fe(CN)6", SMILES string)
        states: List of spin multiplicities - auto-detected if None (e.g., [1, 3, 5])
        charge: Molecular charge - auto-detected if None (e.g., -4 for Mn(Cl)6)
        multiplicity: Default multiplicity - auto-detected if None
        mode: Calculation precision - "reckless", "rapid", "careful", "meticulous" (default: "rapid")
        solvent: Solvent for optimization (e.g., "water", "acetonitrile", "dmso", default: None = gas phase)
        xtb_preopt: Whether to pre-optimize with xTB before higher-level calculations (default: True)
        constraints: Additional coordinate constraints during optimization (default: None)
        transition_state: Whether this is a transition state optimization (default: False)
        frequencies: Whether to calculate vibrational frequencies (default: False)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 10, longer for spin state calculations)
        auto_analyze: Whether to automatically analyze molecule for appropriate parameters (default: True)
    
    Returns:
        Spin state energetics analysis with relative energies and ground state identification
    """
    # Preprocess molecule input to handle subscripts and chemical formulas
    def preprocess_molecule_input(mol_input: str) -> str:
        """Convert subscripts and normalize chemical formulas."""
        # Replace Unicode subscripts with regular numbers
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', 
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
        }
        
        processed = mol_input
        for sub, num in subscript_map.items():
            processed = processed.replace(sub, num)
            
        logger.info(f" Preprocessed molecule: '{mol_input}' → '{processed}'")
        return processed
    
    # Preprocess the molecule input
    processed_molecule = preprocess_molecule_input(molecule)
    
    # Auto-analyze molecule if enabled and parameters not provided
    analysis_results = None
    if auto_analyze and (states is None or charge is None or multiplicity is None):
        analysis_results = analyze_spin_states(processed_molecule)
        logger.info(f" Analysis results: {analysis_results}")
    
    # Apply auto-analysis results, but allow manual overrides
    if states is None:
        if analysis_results:
            states = analysis_results["states"]
        else:
            return f" Error: 'states' must be provided when auto_analyze=False or analysis fails. Provide as list like [1, 3, 5]"
    
    if charge is None and analysis_results and "charge" in analysis_results:
        charge = analysis_results["charge"]
    
    if multiplicity is None and analysis_results and "multiplicity" in analysis_results:
        multiplicity = analysis_results["multiplicity"]
    
    # For chemical formulas, don't try SMILES lookup - use the processed formula directly
    # Check if this looks like a chemical formula vs SMILES
    import re
    is_chemical_formula = bool(re.search(r'[A-Z][a-z]?\([A-Z]', processed_molecule))
    
    if is_chemical_formula:
        canonical_smiles = processed_molecule
    else:
        # Look up SMILES if a common name was provided
        canonical_smiles = lookup_molecule_smiles(processed_molecule)
    
    # Validate states parameter
    if not states or not isinstance(states, list):
        return f" Error: 'states' must be a non-empty list of positive integers. Got: {states}"
    
    if not all(isinstance(s, int) and s > 0 for s in states):
        return f" Error: All multiplicities in 'states' must be positive integers. Got: {states}"
    
    if len(states) < 1:
        return f" Error: At least one spin multiplicity must be specified. Got: {states}"
    
    # Check multiplicity parity consistency (all odd or all even)
    first_parity = states[0] % 2
    if not all((s % 2) == first_parity for s in states):
        return f" Error: All multiplicities must have the same parity (all odd or all even). Got: {states}"
    
    # Validate mode
    valid_modes = ["reckless", "rapid", "careful", "meticulous"]
    mode_lower = mode.lower()
    if mode_lower not in valid_modes:
        return f" Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
    
    # Log the spin states parameters
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   States (multiplicities): {states}")
    logger.info(f"   Mode: {mode_lower}")
    if analysis_results:
        logger.info(f"   Analysis explanation: {analysis_results.get('explanation', 'N/A')}")
        logger.info(f"   Analysis confidence: {analysis_results.get('confidence', 'N/A')}")
    logger.info(f"   xTB Pre-optimization: {xtb_preopt}")
    logger.info(f"   Transition State: {transition_state}")
    logger.info(f"   Frequencies: {frequencies}")
    logger.info(f"   Constraints: {len(constraints) if constraints else 0} applied")
    
    # Build parameters for Rowan API
    spin_params = {
        "name": name,
        "molecule": canonical_smiles,
        "states": states,
        "mode": mode_lower,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add charge and multiplicity if specified
    if charge is not None:
        spin_params["charge"] = charge
    if multiplicity is not None:
        spin_params["multiplicity"] = multiplicity
    
    # Add optional parameters if specified
    if solvent is not None:
        spin_params["solvent"] = solvent
    if not xtb_preopt:  # Only set if False (True is likely default)
        spin_params["xtb_preopt"] = xtb_preopt
    if constraints is not None:
        spin_params["constraints"] = constraints
    if transition_state:  # Only set if True (False is likely default)
        spin_params["transition_state"] = transition_state
    if frequencies:  # Only set if True (False is likely default) 
        spin_params["frequencies"] = frequencies
    
    result = log_rowan_api_call(
        workflow_type="spin_states",
        **spin_params
    )
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f" Spin states analysis for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f" Spin states analysis for '{name}' failed!\n\n"
        else:
            formatted = f" Spin states analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f" Molecule: {molecule}\n"
        if processed_molecule != molecule:
            formatted += f" Processed: {processed_molecule}\n"
        formatted += f" Input: {canonical_smiles}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {status}\n"
        formatted += f" Multiplicities: {states}\n"
        if charge is not None:
            formatted += f" Charge: {charge:+d}\n"
        if multiplicity is not None:
            formatted += f" Default Multiplicity: {multiplicity}\n"
        
        # Show auto-analysis results if used
        if analysis_results and auto_analyze:
            formatted += f"\n🤖 **Auto-Analysis Results:**\n"
            formatted += f"   Confidence: {analysis_results['confidence'].title()}\n"
            formatted += f"   Explanation: {analysis_results['explanation']}\n"
            if 'oxidation_state' in analysis_results:
                formatted += f"   Metal Oxidation State: +{analysis_results['oxidation_state']}\n"
            if 'd_electrons' in analysis_results:
                formatted += f"   d-Electron Count: d{analysis_results['d_electrons']}\n"
        
        # Applied settings
        formatted += f"\n⚙ **Computational Settings:**\n"
        formatted += f"   Mode: {mode_lower.title()} (multi-stage optimization)\n"
        formatted += f"   Solvent: {solvent or 'Gas Phase'}\n"
        formatted += f"   xTB Pre-optimization: {'Enabled' if xtb_preopt else 'Disabled'}\n"
        if transition_state:
            formatted += f"   Transition State: Yes\n"
        if frequencies:
            formatted += f"   Frequencies: Calculated\n"
        if constraints:
            formatted += f"   Constraints: {len(constraints)} applied\n"
        
        # Try to extract spin states results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Look for spin states data
            if 'spin_states' in data and isinstance(data['spin_states'], list):
                spin_results = data['spin_states']
                if spin_results:
                    formatted += f"\n **Spin States Results:**\n"
                    
                    # Sort by energy to identify ground state
                    sorted_states = sorted(spin_results, key=lambda x: x.get('energy', float('inf')))
                    ground_state = sorted_states[0] if sorted_states else None
                    
                    for i, state in enumerate(sorted_states):
                        mult = state.get('multiplicity', 'N/A')
                        energy = state.get('energy', 'N/A')
                        is_ground = (i == 0)
                        
                        if isinstance(energy, (int, float)):
                            # Calculate relative energy in kcal/mol (assuming energies in Hartree)
                            if is_ground:
                                rel_energy = 0.0
                                formatted += f"   🥇 Multiplicity {mult}: {energy:.6f} au (Ground State)\n"
                            else:
                                rel_energy = (energy - ground_state.get('energy', 0)) * 627.5094740631  # Hartree to kcal/mol
                                formatted += f"    Multiplicity {mult}: {energy:.6f} au (+{rel_energy:.2f} kcal/mol)\n"
                        else:
                            formatted += f"    Multiplicity {mult}: {energy}\n"
                    
                    # Summary
                    if ground_state:
                        ground_mult = ground_state.get('multiplicity', 'Unknown')
                        formatted += f"\n **Ground State:** Multiplicity {ground_mult}\n"
                        
                        # Interpret ground state
                        spin_names = {1: "Singlet", 2: "Doublet", 3: "Triplet", 4: "Quartet", 5: "Quintet", 6: "Sextet", 7: "Septet"}
                        if ground_mult in spin_names:
                            formatted += f"   Spin State: {spin_names[ground_mult]}\n"
                        
                        unpaired_electrons = ground_mult - 1
                        formatted += f"   Unpaired Electrons: {unpaired_electrons}\n"
            
            # Legacy support for other energy formats
            elif 'energies' in data and isinstance(data['energies'], list):
                energies = data['energies']
                if energies and len(energies) == len(states):
                    formatted += f"\n **Spin States Energies:**\n"
                    
                    # Pair with multiplicities and sort by energy
                    paired_results = list(zip(states, energies))
                    paired_results.sort(key=lambda x: x[1])
                    
                    ground_energy = paired_results[0][1]
                    ground_mult = paired_results[0][0]
                    
                    for mult, energy in paired_results:
                        if mult == ground_mult:
                            formatted += f"   🥇 Multiplicity {mult}: {energy:.6f} au (Ground State)\n"
                        else:
                            rel_energy = (energy - ground_energy) * 627.5094740631  # Hartree to kcal/mol
                            formatted += f"    Multiplicity {mult}: {energy:.6f} au (+{rel_energy:.2f} kcal/mol)\n"
                    
                    formatted += f"\n **Ground State:** Multiplicity {ground_mult}\n"
        
        # Status-specific guidance
        formatted += f"\n **Next Steps:**\n"
        if status == 2:  # Completed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed results\n"
            formatted += f"• Ground state identified from relative energies\n"
            formatted += f"• Consider electronic structure analysis for ground state geometry\n"
            formatted += f"• For transition metals: compare with experimental magnetic data\n"
        elif status == 3:  # Failed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            formatted += f"• **Troubleshooting:**\n"
            formatted += f"  - Check multiplicity parity: {states} (all odd or all even)\n"
            formatted += f"  - Try fewer multiplicities or simpler mode: mode='reckless'\n"
            formatted += f"  - For transition metals: ensure reasonable oxidation states\n"
            formatted += f"  - Consider starting with just two states: [1, 3] or [2, 4]\n"
        elif status in [0, 1, 5]:  # Running
            formatted += f"• Check progress: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
            total_calcs = len(states) * 3  # Approximate: 3 levels per multiplicity
            formatted += f"• Spin states calculation involves ~{total_calcs} optimizations ({len(states)} multiplicities × 3 levels)\n"
            formatted += f"• May take 15-60 minutes depending on molecule size and multiplicities\n"
        elif status == 4:  # Stopped
            formatted += f"• Check why stopped: rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
            formatted += f"• You can restart with same or different multiplicities\n"
        else:  # Unknown
            formatted += f"• Check status: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
        
        # Add examples and guidance
        formatted += f"\n **Auto-Analysis Examples:**\n"
        formatted += f"• **Mn(Cl)6** → charge: -4, states: [2, 6] (Mn(II) d5: low vs high-spin)\n"
        formatted += f"• **Fe(CN)6** → charge: -4, states: [1, 5] (Fe(II) d6: low vs high-spin)\n"
        formatted += f"• **Cu(H2O)4** → charge: +2, states: [2] (Cu(II) d9: always doublet)\n"
        formatted += f"• **Ni(H2O)6** → charge: +2, states: [3] (Ni(II) d8: high-spin triplet)\n"
        formatted += f"• **Co(NH3)6** → charge: +3, states: [1] (Co(III) d6: low-spin singlet)\n"
        formatted += f"• **Cr(H2O)6** → charge: +3, states: [4] (Cr(III) d3: always high-spin)\n\n"
        
        formatted += f" **Manual Override Examples:**\n"
        formatted += f"• rowan_spin_states('test', 'Mn(Cl)6') → auto-detects everything\n"
        formatted += f"• rowan_spin_states('test', 'SMILES', states=[1,3,5]) → manual states\n"
        formatted += f"• rowan_spin_states('test', 'complex', charge=-2, states=[2,4]) → manual override\n"
        formatted += f"• rowan_spin_states('test', 'molecule', auto_analyze=False, states=[1]) → no auto-analysis\n\n"
        
        formatted += f" **Multiplicity Guide:**\n"
        formatted += f"• Multiplicity = 2S + 1 (where S = total spin)\n"
        formatted += f"• Singlet (S=0): 0 unpaired electrons → closed shell\n"
        formatted += f"• Doublet (S=1/2): 1 unpaired electron\n" 
        formatted += f"• Triplet (S=1): 2 unpaired electrons, parallel spins\n"
        formatted += f"• Quartet (S=3/2): 3 unpaired electrons\n"
        formatted += f"• Quintet (S=2): 4 unpaired electrons\n"
        
        return formatted
    else:
        formatted = f" Spin states analysis for '{name}' submitted!\n\n"
        formatted += f" Molecule: {molecule}\n"
        if processed_molecule != molecule:
            formatted += f" Processed: {processed_molecule}\n"
        formatted += f" Input: {canonical_smiles}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {result.get('status', 'Submitted')}\n"
        formatted += f" Multiplicities: {states}\n"
        if charge is not None:
            formatted += f" Charge: {charge:+d}\n"
        if multiplicity is not None:
            formatted += f" Default Multiplicity: {multiplicity}\n"
        formatted += f"⚙ Mode: {mode_lower.title()}\n"
        
        # Show auto-analysis results if used
        if analysis_results and auto_analyze:
            formatted += f"\n🤖 **Auto-Analysis Applied:**\n"
            formatted += f"   {analysis_results['explanation']}\n"
            formatted += f"   Confidence: {analysis_results['confidence'].title()}\n"
        
        formatted += f"\n Use rowan_workflow_management tools to check progress and retrieve results\n"
        return formatted

# IRC - Reaction Coordinate Following

@mcp.tool()
def rowan_folder_management(
    action: str,
    folder_uuid: Optional[str] = None,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    name_contains: Optional[str] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """Unified folder management tool for all folder operations.
    
    **Available Actions:**
    - **create**: Create a new folder (requires: name, optional: parent_uuid, notes, starred, public)
    - **retrieve**: Get folder details (requires: folder_uuid)
    - **update**: Update folder properties (requires: folder_uuid, optional: name, parent_uuid, notes, starred, public)
    - **delete**: Delete a folder (requires: folder_uuid)
    - **list**: List folders with filters (optional: name_contains, parent_uuid, starred, public, page, size)
    
    Args:
        action: Action to perform ('create', 'retrieve', 'update', 'delete', 'list')
        folder_uuid: UUID of the folder (required for retrieve, update, delete)
        name: Folder name (required for create, optional for update)
        parent_uuid: Parent folder UUID (optional for create/update, if not provided creates in root)
        notes: Folder notes (optional for create/update)
        starred: Star the folder (optional for create/update)
        public: Make folder public (optional for create/update)
        name_contains: Filter by name containing text (optional for list)
        page: Page number for pagination (default: 1, for list)
        size: Results per page (default: 50, for list)
    
    Returns:
        Results of the folder operation
    """
    
    action = action.lower()
    
    try:
        if action == "create":
            if not name:
                return " Error: 'name' is required for creating a folder"
            
            folder = rowan.Folder.create(
                name=name,
                parent_uuid=parent_uuid,  # Required by API
                notes=notes or "",
                starred=starred or False,
                public=public or False
            )
            
            formatted = f" Folder '{name}' created successfully!\n\n"
            formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f" Notes: {notes or 'None'}\n"
            if parent_uuid:
                formatted += f"📂 Parent: {parent_uuid}\n"
            return formatted
            
        elif action == "retrieve":
            if not folder_uuid:
                return " Error: 'folder_uuid' is required for retrieving a folder"
            
            folder = rowan.Folder.retrieve(uuid=folder_uuid)
            
            formatted = f"📁 Folder Details:\n\n"
            formatted += f" Name: {folder.get('name', 'N/A')}\n"
            formatted += f"🆔 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"📂 Parent: {folder.get('parent_uuid', 'Root')}\n"
            formatted += f" Starred: {'Yes' if folder.get('starred') else 'No'}\n"
            formatted += f" Public: {'Yes' if folder.get('public') else 'No'}\n"
            formatted += f"📅 Created: {folder.get('created_at', 'N/A')}\n"
            formatted += f" Notes: {folder.get('notes', 'None')}\n"
            return formatted
            
        elif action == "update":
            if not folder_uuid:
                return " Error: 'folder_uuid' is required for updating a folder"
            
            # Build update parameters
            update_params = {"uuid": folder_uuid}
            if name is not None:
                update_params["name"] = name
            if parent_uuid is not None:
                update_params["parent_uuid"] = parent_uuid
            if notes is not None:
                update_params["notes"] = notes
            if starred is not None:
                update_params["starred"] = starred
            if public is not None:
                update_params["public"] = public
                
            folder = rowan.Folder.update(**update_params)
            
            formatted = f" Folder '{folder.get('name')}' updated successfully!\n\n"
            formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f" Name: {folder.get('name', 'N/A')}\n"
            formatted += f" Starred: {'Yes' if folder.get('starred') else 'No'}\n"
            formatted += f" Public: {'Yes' if folder.get('public') else 'No'}\n"
            return formatted
            
        elif action == "delete":
            if not folder_uuid:
                return " Error: 'folder_uuid' is required for deleting a folder"
            
            rowan.Folder.delete(uuid=folder_uuid)
            return f" Folder {folder_uuid} deleted successfully."
            
        elif action == "list":
            # Build filter parameters
            filter_params = {"page": page, "size": size}
            if name_contains is not None:
                filter_params["name_contains"] = name_contains
            if parent_uuid is not None:
                filter_params["parent_uuid"] = parent_uuid
            if starred is not None:
                filter_params["starred"] = starred
            if public is not None:
                filter_params["public"] = public
                
            result = rowan.Folder.list(**filter_params)
            folders = result.get("folders", [])
            num_pages = result.get("num_pages", 1)
            
            if not folders:
                return "📁 No folders found matching criteria."
            
            formatted = f"📁 Found {len(folders)} folders (Page {page}/{num_pages}):\n\n"
            for folder in folders:
                starred_icon = "" if folder.get('starred') else "📁"
                public_icon = "" if folder.get('public') else "🔒"
                formatted += f"{starred_icon} {folder.get('name', 'Unnamed')} {public_icon}\n"
                formatted += f"   UUID: {folder.get('uuid', 'N/A')}\n"
                if folder.get('notes'):
                    formatted += f"   Notes: {folder.get('notes')}\n"
                formatted += "\n"
            
            return formatted
            
        else:
            return f" Error: Unknown action '{action}'. Available actions: create, retrieve, update, delete, list"
            
    except Exception as e:
        return f" Error in folder {action}: {str(e)}"

# Workflow management and calculation retrieve functions moved to src/functions/

@mcp.tool()
def rowan_system_management(
    action: str,
    job_uuid: Optional[str] = None,
    log_level: Optional[str] = None
) -> str:
    """Unified system management tool for server utilities and information.
    
    **Available Actions:**
    - **help**: Get list of all available Rowan MCP tools with descriptions
    - **set_log_level**: Set logging level for debugging (requires: log_level)
    - **job_redirect**: Redirect legacy job queries to workflow management (requires: job_uuid)
    
    Args:
        action: Action to perform ('help', 'set_log_level', 'job_redirect')
        job_uuid: UUID of the job (required for job_redirect)
        log_level: Logging level - DEBUG, INFO, WARNING, ERROR (required for set_log_level)
    
    Returns:
        Results of the system operation
    """
    
    action = action.lower()
    
    try:
        if action == "help":
            result = " **Available Rowan MCP Tools** \n\n"
            
            result += "✨ **Now with unified management tools!**\n"
            result += "Each tool has tailored documentation and parameters.\n\n"
            
            # Group by common use cases
            result += "** Quantum Chemistry & Basic Calculations:**\n"
            result += "• `rowan_qc_guide` - Comprehensive quantum chemistry guidance\n"
            result += "• `rowan_quantum_chemistry` - Unified QC tool (smart defaults + full customization)\n"
            result += "• `rowan_electronic_properties` - HOMO/LUMO, orbitals\n"
            result += "• `rowan_multistage_opt` - Multi-level optimization (for geometry)\n\n"
            
            result += "**🧬 Molecular Analysis:**\n"
            result += "• `rowan_conformers` - Find molecular conformations\n"
            result += "• `rowan_tautomers` - Tautomer enumeration\n"
            result += "• `rowan_descriptors` - Molecular descriptors for ML\n\n"
            
            result += "** Chemical Properties:**\n"
            result += "• `rowan_pka` - pKa prediction\n"
            result += "• `rowan_redox_potential` - Redox potentials vs SCE\n"
            result += "• `rowan_bde` - Bond dissociation energies\n"
            result += "• `rowan_solubility` - Solubility prediction\n\n"
            
            result += "** Drug Discovery:**\n"
            result += "• `rowan_admet` - ADME-Tox properties\n\n"
            
            result += "** Advanced Analysis:**\n"
            result += "• `rowan_scan` - Potential energy surface scans (bond/angle/dihedral)\n"
            result += "• `rowan_fukui` - Reactivity analysis\n"
            result += "• `rowan_spin_states` - Spin state preferences\n"
            result += "• `rowan_irc` - Reaction coordinate following\n"
            result += "• `rowan_molecular_dynamics` - MD simulations\n"
            result += "• `rowan_hydrogen_bond_basicity` - H-bond strength\n\n"
            
            result += " **Usage Guidelines:**\n"
            result += "• For geometry optimization: use `rowan_multistage_opt`\n"
            result += "• For energy calculations: use `rowan_quantum_chemistry` (smart defaults)\n"
            result += "• For custom QC settings: use `rowan_quantum_chemistry` with parameters\n"
            result += "• For conformer search: use `rowan_conformers`\n"
            result += "• For pKa prediction: use `rowan_pka`\n"
            result += "• For electronic structure: use `rowan_electronic_properties`\n"
            result += "• For drug properties: use `rowan_admet`\n"
            result += "• For reaction mechanisms: use `rowan_scan` then `rowan_irc`\n"
            result += "• For potential energy scans: use `rowan_scan` with coordinate specification\n\n"
            
            result += "** Management Tools:**\n"
            result += "• `rowan_folder_management` - Unified folder operations (create, retrieve, update, delete, list)\n"
            result += "• `rowan_workflow_management` - Unified workflow operations (create, retrieve, update, stop, status, delete, list)\n"
            result += "• `rowan_system_management` - System utilities (help, set_log_level, job_redirect)\n\n"
            
            result += " **Total Available:** 15+ specialized tools + 3 unified management tools\n"
            result += " **Each tool has specific documentation - check individual tool descriptions**\n"
            result += " **Management tools use 'action' parameter to specify operation**\n"
            
            return result
            
        elif action == "set_log_level":
            if not log_level:
                return " Error: 'log_level' is required for set_log_level action"
            
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            log_level = log_level.upper()
            
            if log_level not in valid_levels:
                return f" Invalid log level. Use one of: {', '.join(valid_levels)}"
            
            logger.setLevel(getattr(logging, log_level))
            logger.info(f" Log level changed to: {log_level}")
            
            return f" Log level set to {log_level}"
            
        elif action == "job_redirect":
            if not job_uuid:
                return " Error: 'job_uuid' is required for job_redirect action"
            
            # Try to treat the job_uuid as a workflow_uuid and retrieve results directly
            try:
                workflow = rowan.Workflow.retrieve(uuid=job_uuid)
                
                # Get status and interpret it
                status = workflow.get('object_status', 'Unknown')
                status_names = {
                    0: "Queued",
                    1: "Running", 
                    2: "Completed",
                    3: "Failed",
                    4: "Stopped",
                    5: "Awaiting Queue"
                }
                status_name = status_names.get(status, f"Unknown ({status})")
                
                formatted = f" **Found Workflow {job_uuid}:**\n\n"
                formatted += f" Name: {workflow.get('name', 'N/A')}\n"
                formatted += f" Type: {workflow.get('object_type', 'N/A')}\n"
                formatted += f" Status: {status_name} ({status})\n"
                formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
                formatted += f" Elapsed: {workflow.get('elapsed', 0):.2f}s\n\n"
                
                if status == 2:  # Completed
                    formatted += f" **Getting Results...**\n\n"
                    
                    # Try to retrieve calculation results
                    try:
                        calc_result = rowan.Calculation.retrieve(uuid=job_uuid)
                        
                        # Extract workflow type to provide specific result formatting
                        workflow_type = workflow.get('object_type', '')
                        
                        if workflow_type == 'electronic_properties':
                            formatted += f" **Electronic Properties Results:**\n\n"
                            
                            # Extract key electronic properties from the result
                            object_data = calc_result.get('object_data', {})
                            
                            # Molecular orbital energies (HOMO/LUMO)
                            if 'molecular_orbitals' in object_data:
                                mo_data = object_data['molecular_orbitals']
                                if isinstance(mo_data, dict) and 'energies' in mo_data:
                                    energies = mo_data['energies']
                                    if isinstance(energies, list) and len(energies) > 0:
                                        # Find HOMO/LUMO
                                        occupations = mo_data.get('occupations', [])
                                        if occupations:
                                            homo_idx = None
                                            lumo_idx = None
                                            for i, occ in enumerate(occupations):
                                                if occ > 0.5:  # Occupied
                                                    homo_idx = i
                                                elif occ < 0.5 and lumo_idx is None:  # First unoccupied
                                                    lumo_idx = i
                                                    break
                                            
                                            if homo_idx is not None and lumo_idx is not None:
                                                homo_energy = energies[homo_idx]
                                                lumo_energy = energies[lumo_idx]
                                                gap = lumo_energy - homo_energy
                                                
                                                formatted += f"• HOMO Energy: {homo_energy:.4f} hartree ({homo_energy * 27.2114:.2f} eV)\n"
                                                formatted += f"• LUMO Energy: {lumo_energy:.4f} hartree ({lumo_energy * 27.2114:.2f} eV)\n"
                                                formatted += f"• HOMO-LUMO Gap: {gap:.4f} hartree ({gap * 27.2114:.2f} eV)\n\n"
                            
                            # Dipole moment
                            if 'dipole' in object_data:
                                dipole = object_data['dipole']
                                if isinstance(dipole, dict) and 'magnitude' in dipole:
                                    formatted += f"🧲 **Dipole Moment:** {dipole['magnitude']:.4f} Debye\n\n"
                                elif isinstance(dipole, (int, float)):
                                    formatted += f"🧲 **Dipole Moment:** {dipole:.4f} Debye\n\n"
                            
                            # If no specific electronic properties found, show available keys
                            if not any(key in object_data for key in ['molecular_orbitals', 'dipole']):
                                if object_data:
                                    formatted += f" **Available Properties:** {', '.join(object_data.keys())}\n\n"
                                else:
                                    formatted += f" **No electronic properties data found in results**\n\n"
                        
                        else:
                            # For other workflow types, show general calculation results
                            formatted += f" **{workflow_type.replace('_', ' ').title()} Results:**\n\n"
                            
                            object_data = calc_result.get('object_data', {})
                            if object_data:
                                # Show first few key-value pairs
                                count = 0
                                for key, value in object_data.items():
                                    if count >= 5:  # Limit to first 5 items for job_redirect
                                        formatted += f"   ... and {len(object_data) - 5} more properties\n"
                                        break
                                    
                                    # Format the value nicely
                                    if isinstance(value, (int, float)):
                                        formatted += f"• **{key}**: {value}\n"
                                    elif isinstance(value, str):
                                        formatted += f"• **{key}**: {value[:50]}{'...' if len(value) > 50 else ''}\n"
                                    elif isinstance(value, list):
                                        formatted += f"• **{key}**: {len(value)} items\n"
                                    elif isinstance(value, dict):
                                        formatted += f"• **{key}**: {len(value)} properties\n"
                                    else:
                                        formatted += f"• **{key}**: {type(value).__name__}\n"
                                    count += 1
                                formatted += "\n"
                            else:
                                formatted += f" **No calculation data found in results**\n\n"
                        
                    except Exception as retrieve_error:
                        formatted += f" **Results retrieval failed:** {str(retrieve_error)}\n\n"
                
                elif status in [0, 1, 5]:  # Still running
                    formatted += f" **Workflow is still {status_name.lower()}**\n"
                    formatted += f" Check back later for results\n\n"
                
                elif status == 3:  # Failed
                    formatted += f" **Workflow failed**\n"
                    formatted += f" Check the workflow parameters and try again\n\n"
                
                formatted += f" **For more details:**\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{job_uuid}') for full workflow details\n"
                formatted += f"• Use rowan_calculation_retrieve('{job_uuid}') for raw calculation data\n"
                
                return formatted
                
            except Exception as e:
                # If workflow retrieval fails, provide the legacy guidance
                formatted = f" **Could not find workflow {job_uuid}:** {str(e)}\n\n"
                formatted += f" **Important Note:**\n"
                formatted += f"Rowan manages computations through workflows, not individual jobs.\n"
                formatted += f"The job/results concept is legacy from older versions.\n\n"
                formatted += f" **To find your workflow:**\n"
                formatted += f"• Use rowan_workflow_management(action='list') to see all workflows\n"
                formatted += f"• Look for workflows with similar names or recent creation times\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='UUID') to get results\n\n"
                formatted += f" **Migration Guide:**\n"
                formatted += f"• Old: rowan_job_status('{job_uuid}') → New: rowan_workflow_management(action='status', workflow_uuid='UUID')\n"
                formatted += f"• Old: rowan_job_results('{job_uuid}') → New: rowan_workflow_management(action='retrieve', workflow_uuid='UUID')\n"
                
                return formatted
            
        else:
            return f" Error: Unknown action '{action}'. Available actions: help, set_log_level, job_redirect"
            
    except Exception as e:
        return f" Error in system {action}: {str(e)}"

def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info(f" Log level: {logger.level}")
        logger.info(f"📁 Log file: rowan_mcp.log")
        logger.info(f"🔑 API Key loaded: {'' if api_key else ''}")
        logger.info(" Server ready for MCP connections!")
        
        print(" Rowan MCP Server starting...")
        print(" Logging enabled - check rowan_mcp.log for detailed logs")
        print(f"🔑 API Key: {' Loaded' if api_key else ' Missing'}")
        
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Server shutdown requested by user")
        print("\n👋 Server shutdown requested by user")
    except Exception as e:
        logger.error(f" Server startup error: {e}")
        logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
        print(f" Server error: {e}")
        print(" Check rowan_mcp.log for detailed error information")

if __name__ == "__main__":
    main() 