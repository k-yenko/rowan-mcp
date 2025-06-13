"""
Rowan MCP Server Implementation using FastMCP

This module implements the Model Context Protocol server for Rowan's
computational chemistry platform using the FastMCP framework.
"""

import os
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Literal
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field

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

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if not api_key:
    logger.error("ROWAN_API_KEY environment variable not found")
    raise ValueError(
        "ROWAN_API_KEY environment variable is required. "
        "Get your API key from https://labs.rowansci.com"
    )
else:
    logger.info(f"✅ ROWAN_API_KEY loaded (length: {len(api_key)})")

if rowan is None:
    logger.error("rowan-python package not found")
    raise ImportError(
        "rowan-python package is required. Install with: pip install rowan-python"
    )
else:
    logger.info("✅ rowan-python package loaded successfully")

rowan.api_key = api_key
logger.info("🔗 Rowan API key configured")


def log_mcp_call(func):
    """Decorator to log MCP tool calls with detailed information."""
    import functools
    
    @functools.wraps(func)
    def wrapper(**kwargs):  # Only use **kwargs to be compatible with FastMCP
        func_name = func.__name__
        start_time = time.time()
        
        # Log the incoming request
        logger.info(f"🔧 MCP Tool Called: {func_name}")
        logger.info(f"📝 Parameters: {kwargs}")
        
        try:
            # Execute the function
            result = func(**kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Log successful completion
            logger.info(f"✅ {func_name} completed successfully in {execution_time:.2f}s")
            logger.debug(f"📤 Response preview: {str(result)[:200]}...")
            
            return result
            
        except Exception as e:
            # Calculate execution time even for errors
            execution_time = time.time() - start_time
            
            # Log the error with full traceback
            logger.error(f"❌ {func_name} failed after {execution_time:.2f}s")
            logger.error(f"🚨 Error: {str(e)}")
            logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
            
            # Return a formatted error message
            error_msg = f"❌ Error in {func_name}: {str(e)}"
            if "rowan" in str(e).lower():
                error_msg += f"\n🔗 Check Rowan API status and your API key"
            return error_msg
            
    return wrapper


def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    logger.info(f"🌐 Rowan API Call: {workflow_type}")
    logger.info(f"🔍 Rowan Parameters: {kwargs}")
    
    try:
        start_time = time.time()
        result = rowan.compute(workflow_type=workflow_type, **kwargs)
        api_time = time.time() - start_time
        
        logger.info(f"🎯 Rowan API success: {workflow_type} ({api_time:.2f}s)")
        if isinstance(result, dict) and 'uuid' in result:
            logger.info(f"📋 Job UUID: {result.get('uuid')}")
            logger.info(f"📊 Status: {result.get('status', 'Unknown')}")
        
        return result
        
    except Exception as e:
        api_time = time.time() - start_time
        logger.error(f"🌐 Rowan API failed: {workflow_type} ({api_time:.2f}s)")
        logger.error(f"🚨 Rowan Error: {str(e)}")
        raise e


# Pydantic models for request validation
class PkaRequest(BaseModel):
    name: str = Field(..., description="Name for the calculation")
    molecule: str = Field(..., description="Molecule SMILES string")
    folder_uuid: Optional[str] = Field(None, description="Folder UUID for organization")


class ConformerRequest(BaseModel):
    name: str = Field(..., description="Name for the calculation")
    molecule: str = Field(..., description="Molecule SMILES string")
    max_conformers: Optional[int] = Field(10, description="Maximum number of conformers")
    folder_uuid: Optional[str] = Field(None, description="Folder UUID for organization")


class FolderRequest(BaseModel):
    name: str = Field(..., description="Name of the folder")
    description: Optional[str] = Field(None, description="Optional description")


class JobRequest(BaseModel):
    job_uuid: str = Field(..., description="UUID of the job")


# Tool implementations

# ADMET - Drug Discovery Properties
@mcp.tool()
@log_mcp_call
def rowan_admet(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict ADME-Tox properties for drug discovery.
    
    ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) properties are crucial
    for drug development. This workflow predicts drug-like properties including:
    - Bioavailability and permeability
    - Metabolic stability and clearance
    - Toxicity indicators and safety profiles
    - Drug-likeness metrics
    
    Use this for: Drug discovery, pharmaceutical development, toxicity screening
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        ADMET prediction results
    """
    result = log_rowan_api_call(
        workflow_type="admet",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Basic Calculation - General Quantum Chemistry
@mcp.tool()
@log_mcp_call
def rowan_basic_calculation(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run general quantum chemistry calculations.
    
    Performs standard quantum chemistry calculations including:
    - Single point energy calculations
    - Geometry optimization
    - Frequency calculations
    - Basic electronic structure properties
    
    Use this for: Energy calculations, geometry optimization, vibrational analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Basic calculation results
    """
    result = log_rowan_api_call(
        workflow_type="basic_calculation",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Bond Dissociation Energy
@mcp.tool()
def rowan_bde(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate bond dissociation energies.
    
    Predicts the energy required to break specific bonds in molecules. Useful for:
    - Understanding metabolic pathways and degradation
    - Predicting reaction selectivity
    - Identifying weak bonds for synthetic planning
    
    Use this for: Metabolism prediction, synthetic planning, reaction mechanism studies
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Bond dissociation energy results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="bde",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating BDE: {str(e)}"


# Multistage Optimization - Recommended for Geometry Optimization
@mcp.tool()
@log_mcp_call
def rowan_multistage_opt(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run multi-level geometry optimization (RECOMMENDED).
    
    Performs hierarchical optimization using multiple levels of theory:
    GFN2-xTB → AIMNet2 → DFT for optimal balance of speed and accuracy.
    
    This is the RECOMMENDED method for geometry optimization as it provides:
    - High accuracy final structures
    - Efficient computational cost
    - Reliable convergence
    
    Use this for: Geometry optimization, conformational analysis, structure refinement
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Optimized geometry and energy results
    """
    result = log_rowan_api_call(
        workflow_type="multistage_opt",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Electronic Properties - HOMO/LUMO, Orbitals
@mcp.tool()
def rowan_electronic_properties(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate electronic structure properties.
    
    Computes electronic properties including:
    - HOMO/LUMO energies and orbitals
    - Molecular orbital analysis
    - Electronic density distributions
    - Band gaps and frontier orbital properties
    
    Use this for: Electronic structure analysis, orbital visualization, reactivity prediction
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Electronic properties results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="electronic_properties",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating electronic properties: {str(e)}"


# Descriptors - Molecular Feature Vectors
@mcp.tool()
def rowan_descriptors(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate molecular descriptors for data science.
    
    Generates comprehensive molecular descriptors including:
    - Topological and geometric descriptors
    - Electronic and physicochemical properties
    - Graph-based molecular features
    - Machine learning ready feature vectors
    
    Use this for: QSAR modeling, machine learning, chemical space analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Molecular descriptors results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="descriptors",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating descriptors: {str(e)}"


# Solubility Prediction
@mcp.tool()
def rowan_solubility(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict aqueous solubility.
    
    Predicts water solubility, a critical property for:
    - Drug formulation and bioavailability
    - Environmental fate and transport
    - Process chemistry and purification
    
    Use this for: Drug development, environmental assessment, process optimization
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Solubility prediction results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="solubility",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error predicting solubility: {str(e)}"


# Redox Potential
@mcp.tool()
def rowan_redox_potential(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict redox potentials vs. SCE in acetonitrile.
    
    Calculates oxidation and reduction potentials for:
    - Electrochemical reaction design
    - Battery and energy storage applications
    - Understanding electron transfer processes
    
    Use this for: Electrochemistry, battery materials, electron transfer studies
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Redox potential results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="redox_potential",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating redox potential: {str(e)}"


# Scan - Potential Energy Surface Scans
@mcp.tool()
def rowan_scan(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run potential energy surface scans.
    
    Performs constrained optimizations along reaction coordinates to:
    - Map reaction pathways and mechanisms
    - Find transition state approximations
    - Study conformational preferences
    - Analyze rotational barriers (atropisomerism)
    
    Use this for: Reaction mechanism studies, transition state searching, conformational analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Scan results with energy profile
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="scan",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error running scan: {str(e)}"


# Fukui Indices - Reactivity Analysis
@mcp.tool()
def rowan_fukui(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate Fukui indices for reactivity prediction.
    
    Predicts sites of chemical reactivity by analyzing electron density changes:
    - f(+): reactivity towards nucleophiles
    - f(-): reactivity towards electrophiles  
    - f(0): reactivity towards radicals
    
    Use this for: Predicting reaction sites, selectivity analysis, drug design
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Fukui indices and reactivity analysis
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="fukui",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating Fukui indices: {str(e)}"


# Spin States
@mcp.tool()
def rowan_spin_states(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Determine preferred spin states for molecules.
    
    Calculates energies of different spin multiplicities to determine:
    - Ground state spin multiplicity
    - Spin crossover energetics
    - High-spin vs low-spin preferences
    
    Use this for: Transition metal complexes, radical species, magnetic materials
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Spin state energetics results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="spin_states",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating spin states: {str(e)}"


# Tautomers
@mcp.tool()
def rowan_tautomers(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Enumerate and rank tautomers by stability.
    
    Finds all possible tautomeric forms and ranks them by relative energy:
    - Prototropic tautomers (keto-enol, etc.)
    - Relative populations at room temperature
    - Dominant tautomeric forms
    
    Use this for: Drug design, understanding protonation states, reaction mechanisms
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Tautomer enumeration and ranking results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="tautomers",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error enumerating tautomers: {str(e)}"


# Hydrogen Bond Basicity
@mcp.tool()
def rowan_hydrogen_bond_basicity(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate hydrogen bond acceptor strength.
    
    Quantifies the ability of molecules to accept hydrogen bonds:
    - Important for drug-target interactions
    - Crystal packing predictions
    - Solvent interactions
    
    Use this for: Drug design, crystal engineering, intermolecular interactions
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Hydrogen bond basicity results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="hydrogen_bond_basicity",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating hydrogen bond basicity: {str(e)}"


# IRC - Reaction Coordinate Following
@mcp.tool()
def rowan_irc(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Follow intrinsic reaction coordinates from transition states.
    
    Traces reaction pathways from transition states to reactants and products:
    - Validates transition state connections
    - Maps complete reaction pathways
    - Confirms reaction mechanisms
    
    Use this for: Mechanism validation, reaction pathway mapping, transition state analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string (should be a transition state)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        IRC pathway results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="irc",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error running IRC: {str(e)}"


# Molecular Dynamics
@mcp.tool()
@log_mcp_call
def rowan_molecular_dynamics(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run molecular dynamics simulations.
    
    Performs MD simulations to study:
    - Dynamic behavior and flexibility
    - Conformational sampling
    - Thermal properties
    - Time-dependent phenomena
    
    Use this for: Conformational dynamics, thermal properties, flexible systems
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Molecular dynamics trajectory and analysis
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="molecular_dynamics",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error running molecular dynamics: {str(e)}"


@mcp.tool()
@log_mcp_call
def rowan_pka(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None
) -> str:
    """Calculate pKa values for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: UUID of folder to organize calculation in
    
    Returns:
        pKa calculation results
    """
    result = log_rowan_api_call(
        workflow_type="pka",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid
    )
    
    pka_value = result.get("object_data", {}).get("strongest_acid")
    
    formatted = f"✅ pKa calculation for '{name}' completed!\n\n"
    formatted += f"🧪 Molecule: {molecule}\n"
    formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
    
    if pka_value is not None:
        formatted += f"🧬 Strongest Acid pKa: {pka_value:.2f}\n"
    else:
        formatted += "⚠️ pKa result not yet available\n"
        
    return formatted


@mcp.tool()
@log_mcp_call
def rowan_conformers(
    name: str,
    molecule: str,
    max_conformers: int = 10,
    folder_uuid: Optional[str] = None
) -> str:
    """Generate and optimize molecular conformers.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        max_conformers: Maximum number of conformers to generate
        folder_uuid: UUID of folder to organize calculation in
    
    Returns:
        Conformer search results
    """
    settings = {"max_conformers": max_conformers}
    
    result = log_rowan_api_call(
        workflow_type="conformer_search",
        name=name,
        molecule=molecule,
        settings=settings,
        folder_uuid=folder_uuid
    )
    
    formatted = f"✅ Conformer search for '{name}' started!\n\n"
    formatted += f"🧪 Molecule: {molecule}\n"
    formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
    formatted += f"📊 Status: {result.get('status', 'Unknown')}\n"
    formatted += f"🔄 Max Conformers: {max_conformers}\n"
    
    return formatted


@mcp.tool()
def rowan_folder_create(
    name: str,
    description: Optional[str] = None
) -> str:
    """Create a new folder for organizing calculations.
    
    Args:
        name: Name of the folder
        description: Optional description of the folder
    
    Returns:
        Folder creation results
    """
    try:
        folder = rowan.Folder.create(
            name=name,
            description=description or ""
        )
        
        formatted = f"✅ Folder '{name}' created successfully!\n\n"
        formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
        formatted += f"📝 Description: {description or 'None'}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error creating folder: {str(e)}"


@mcp.tool()
def rowan_folder_retrieve(folder_uuid: str) -> str:
    """Retrieve details of a specific folder.
    
    Args:
        folder_uuid: UUID of the folder to retrieve
    
    Returns:
        Folder details
    """
    try:
        folder = rowan.Folder.retrieve(uuid=folder_uuid)
        
        formatted = f"📁 Folder Details:\n\n"
        formatted += f"📝 Name: {folder.get('name', 'N/A')}\n"
        formatted += f"🆔 UUID: {folder.get('uuid', 'N/A')}\n"
        formatted += f"📂 Parent: {folder.get('parent_uuid', 'Root')}\n"
        formatted += f"⭐ Starred: {'Yes' if folder.get('starred') else 'No'}\n"
        formatted += f"🌐 Public: {'Yes' if folder.get('public') else 'No'}\n"
        formatted += f"📅 Created: {folder.get('created_at', 'N/A')}\n"
        formatted += f"📝 Notes: {folder.get('notes', 'None')}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error retrieving folder: {str(e)}"


@mcp.tool()
def rowan_folder_update(
    folder_uuid: str,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None
) -> str:
    """Update folder properties.
    
    Args:
        folder_uuid: UUID of the folder to update
        name: New name for the folder
        parent_uuid: New parent folder UUID
        notes: New notes for the folder
        starred: Whether to star the folder
        public: Whether to make the folder public
    
    Returns:
        Updated folder details
    """
    try:
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
        
        formatted = f"✅ Folder '{folder.get('name')}' updated successfully!\n\n"
        formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
        formatted += f"📝 Name: {folder.get('name', 'N/A')}\n"
        formatted += f"⭐ Starred: {'Yes' if folder.get('starred') else 'No'}\n"
        formatted += f"🌐 Public: {'Yes' if folder.get('public') else 'No'}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error updating folder: {str(e)}"


@mcp.tool()
def rowan_folder_delete(folder_uuid: str) -> str:
    """Delete a folder and all its contents.
    
    Args:
        folder_uuid: UUID of the folder to delete
    
    Returns:
        Deletion confirmation
    """
    try:
        rowan.Folder.delete(uuid=folder_uuid)
        return f"✅ Folder {folder_uuid} deleted successfully."
        
    except Exception as e:
        return f"❌ Error deleting folder: {str(e)}"


@mcp.tool()
def rowan_folder_list(
    name_contains: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """List available folders with optional filters.
    
    Args:
        name_contains: Filter folders containing this text in name
        parent_uuid: Filter by parent folder UUID
        starred: Filter by starred status
        public: Filter by public status
        page: Page number for pagination
        size: Number of results per page
    
    Returns:
        List of available folders
    """
    try:
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
            starred_icon = "⭐" if folder.get('starred') else "📁"
            public_icon = "🌐" if folder.get('public') else "🔒"
            formatted += f"{starred_icon} {folder.get('name', 'Unnamed')} {public_icon}\n"
            formatted += f"   UUID: {folder.get('uuid', 'N/A')}\n"
            if folder.get('notes'):
                formatted += f"   Notes: {folder.get('notes')}\n"
            formatted += "\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error listing folders: {str(e)}"


@mcp.tool()
def rowan_workflow_create(
    name: str,
    workflow_type: str,
    initial_molecule: str,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: bool = False,
    public: bool = False,
    email_when_complete: bool = False,
    workflow_data: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new workflow.
    
    Args:
        name: Name of the workflow
        workflow_type: Type of workflow to create
        initial_molecule: Initial molecule (SMILES or stjames.Molecule)
        parent_uuid: Parent folder UUID
        notes: Notes for the workflow
        starred: Whether to star the workflow
        public: Whether to make the workflow public
        email_when_complete: Whether to email when complete
        workflow_data: Additional workflow-specific data
    
    Returns:
        Created workflow details
    """
    
    # Validate workflow type
    VALID_WORKFLOWS = {
        "admet", "basic_calculation", "bde", "conformer_search", "descriptors", 
        "docking", "electronic_properties", "fukui", "hydrogen_bond_basicity", 
        "irc", "molecular_dynamics", "multistage_opt", "pka", "redox_potential", 
        "scan", "solubility", "spin_states", "tautomers"
    }
    
    # Strict validation - no auto-correction
    if workflow_type not in VALID_WORKFLOWS:
        error_msg = f"❌ Invalid workflow_type '{workflow_type}'.\n\n"
        error_msg += "🔧 **Available Rowan Workflow Types:**\n\n"
        
        # Group by common use cases for better guidance
        error_msg += "**🔬 Basic Calculations:**\n"
        error_msg += "• `basic_calculation` - Energy, optimization, frequencies\n"
        error_msg += "• `electronic_properties` - HOMO/LUMO, orbitals\n"
        error_msg += "• `multistage_opt` - Multi-level optimization\n\n"
        
        error_msg += "**🧬 Molecular Analysis:**\n"
        error_msg += "• `conformer_search` - Find molecular conformations\n"
        error_msg += "• `tautomers` - Tautomer enumeration\n"
        error_msg += "• `descriptors` - Molecular descriptors\n\n"
        
        error_msg += "**⚗️ Chemical Properties:**\n"
        error_msg += "• `pka` - pKa prediction\n"
        error_msg += "• `redox_potential` - Redox potentials\n"
        error_msg += "• `bde` - Bond dissociation energies\n"
        error_msg += "• `solubility` - Solubility prediction\n\n"
        
        error_msg += "**🧪 Drug Discovery:**\n"
        error_msg += "• `admet` - ADME-Tox properties\n"
        error_msg += "• `docking` - Protein-ligand docking\n\n"
        
        error_msg += "**🔬 Advanced Analysis:**\n"
        error_msg += "• `scan` - Potential energy scans\n"
        error_msg += "• `fukui` - Reactivity analysis\n"
        error_msg += "• `spin_states` - Spin state preferences\n"
        error_msg += "• `irc` - Reaction coordinate following\n"
        error_msg += "• `molecular_dynamics` - MD simulations\n"
        error_msg += "• `hydrogen_bond_basicity` - H-bond strength\n\n"
        
        raise ValueError(error_msg)

    try:
        workflow = rowan.Workflow.create(
            name=name,
            workflow_type=workflow_type,
            initial_molecule=initial_molecule,
            parent_uuid=parent_uuid,
            notes=notes or "",
            starred=starred,
            public=public,
            email_when_complete=email_when_complete,
            workflow_data=workflow_data or {}
        )
        
        formatted = f"✅ Workflow '{name}' created successfully!\n\n"
        formatted += f"🔬 UUID: {workflow.get('uuid', 'N/A')}\n"
        formatted += f"⚗️ Type: {workflow_type}\n"
        formatted += f"📊 Status: {workflow.get('object_status', 'Unknown')}\n"
        formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error creating workflow: {str(e)}"


@mcp.tool()
def rowan_workflow_retrieve(workflow_uuid: str) -> str:
    """Retrieve details of a specific workflow.
    
    Args:
        workflow_uuid: UUID of the workflow to retrieve
    
    Returns:
        Workflow details
    """
    try:
        workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
        
        formatted = f"🔬 Workflow Details:\n\n"
        formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
        formatted += f"🆔 UUID: {workflow.get('uuid', 'N/A')}\n"
        formatted += f"⚗️ Type: {workflow.get('object_type', 'N/A')}\n"
        formatted += f"📊 Status: {workflow.get('object_status', 'Unknown')}\n"
        formatted += f"📂 Parent: {workflow.get('parent_uuid', 'Root')}\n"
        formatted += f"⭐ Starred: {'Yes' if workflow.get('starred') else 'No'}\n"
        formatted += f"🌐 Public: {'Yes' if workflow.get('public') else 'No'}\n"
        formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
        formatted += f"⏱️ Elapsed: {workflow.get('elapsed', 0):.2f}s\n"
        formatted += f"💰 Credits: {workflow.get('credits_charged', 0)}\n"
        formatted += f"📝 Notes: {workflow.get('notes', 'None')}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error retrieving workflow: {str(e)}"


@mcp.tool()
def rowan_workflow_update(
    workflow_uuid: str,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    email_when_complete: Optional[bool] = None
) -> str:
    """Update workflow properties.
    
    Args:
        workflow_uuid: UUID of the workflow to update
        name: New name for the workflow
        parent_uuid: New parent folder UUID
        notes: New notes for the workflow
        starred: Whether to star the workflow
        public: Whether to make the workflow public
        email_when_complete: Whether to email when complete
    
    Returns:
        Updated workflow details
    """
    try:
        # Build update parameters
        update_params = {"uuid": workflow_uuid}
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
        if email_when_complete is not None:
            update_params["email_when_complete"] = email_when_complete
            
        workflow = rowan.Workflow.update(**update_params)
        
        formatted = f"✅ Workflow '{workflow.get('name')}' updated successfully!\n\n"
        formatted += f"🔬 UUID: {workflow.get('uuid', 'N/A')}\n"
        formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
        formatted += f"⭐ Starred: {'Yes' if workflow.get('starred') else 'No'}\n"
        formatted += f"🌐 Public: {'Yes' if workflow.get('public') else 'No'}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error updating workflow: {str(e)}"


@mcp.tool()
def rowan_workflow_stop(workflow_uuid: str) -> str:
    """Stop a running workflow.
    
    Args:
        workflow_uuid: UUID of the workflow to stop
    
    Returns:
        Stop confirmation
    """
    try:
        rowan.Workflow.stop(uuid=workflow_uuid)
        return f"⏹️ Workflow {workflow_uuid} stopped successfully."
        
    except Exception as e:
        return f"❌ Error stopping workflow: {str(e)}"


@mcp.tool()
def rowan_workflow_status(workflow_uuid: str) -> str:
    """Check the status of a workflow.
    
    Args:
        workflow_uuid: UUID of the workflow to check
    
    Returns:
        Workflow status
    """
    try:
        status = rowan.Workflow.status(uuid=workflow_uuid)
        
        status_names = {
            0: "Queued",
            1: "Running", 
            2: "Completed",
            3: "Failed",
            4: "Stopped"
        }
        
        status_name = status_names.get(status, f"Unknown ({status})")
        
        formatted = f"📊 Workflow Status:\n\n"
        formatted += f"🆔 UUID: {workflow_uuid}\n"
        formatted += f"📈 Status: {status_name} ({status})\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error getting workflow status: {str(e)}"


@mcp.tool()
def rowan_workflow_is_finished(workflow_uuid: str) -> str:
    """Check if a workflow is finished.
    
    Args:
        workflow_uuid: UUID of the workflow to check
    
    Returns:
        Whether the workflow is finished
    """
    try:
        is_finished = rowan.Workflow.is_finished(uuid=workflow_uuid)
        
        formatted = f"✅ Workflow Status:\n\n"
        formatted += f"🆔 UUID: {workflow_uuid}\n"
        formatted += f"🏁 Finished: {'Yes' if is_finished else 'No'}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error checking workflow status: {str(e)}"


@mcp.tool()
def rowan_workflow_delete(workflow_uuid: str) -> str:
    """Delete a workflow.
    
    Args:
        workflow_uuid: UUID of the workflow to delete
    
    Returns:
        Deletion confirmation
    """
    try:
        rowan.Workflow.delete(uuid=workflow_uuid)
        return f"🗑️ Workflow {workflow_uuid} deleted successfully."
        
    except Exception as e:
        return f"❌ Error deleting workflow: {str(e)}"


@mcp.tool()
def rowan_workflow_list(
    name_contains: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    object_status: Optional[int] = None,
    object_type: Optional[str] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """List workflows with optional filters.
    
    Args:
        name_contains: Filter workflows containing this text in name
        parent_uuid: Filter by parent folder UUID
        starred: Filter by starred status
        public: Filter by public status
        object_status: Filter by workflow status (0=queued, 1=running, 2=completed, 3=failed, 4=stopped)
        object_type: Filter by workflow type
        page: Page number for pagination
        size: Number of results per page
    
    Returns:
        List of workflows
    """
    try:
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
        if object_status is not None:
            filter_params["object_status"] = object_status
        if object_type is not None:
            filter_params["object_type"] = object_type
            
        result = rowan.Workflow.list(**filter_params)
        workflows = result.get("workflows", [])
        num_pages = result.get("num_pages", 1)
        
        if not workflows:
            return "🔬 No workflows found matching criteria."
        
        status_names = {0: "⏳", 1: "🔄", 2: "✅", 3: "❌", 4: "⏹️"}
        
        formatted = f"🔬 Found {len(workflows)} workflows (Page {page}/{num_pages}):\n\n"
        for workflow in workflows:
            status_icon = status_names.get(workflow.get('object_status'), "❓")
            starred_icon = "⭐" if workflow.get('starred') else ""
            public_icon = "🌐" if workflow.get('public') else ""
            
            formatted += f"{status_icon} {workflow.get('name', 'Unnamed')} {starred_icon}{public_icon}\n"
            formatted += f"   Type: {workflow.get('object_type', 'N/A')}\n"
            formatted += f"   UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"   Created: {workflow.get('created_at', 'N/A')}\n"
            if workflow.get('elapsed'):
                formatted += f"   Duration: {workflow.get('elapsed', 0):.2f}s\n"
            formatted += "\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error listing workflows: {str(e)}"


@mcp.tool()
def rowan_calculation_retrieve(calculation_uuid: str) -> str:
    """Retrieve details of a specific calculation.
    
    Args:
        calculation_uuid: UUID of the calculation to retrieve
    
    Returns:
        Calculation details
    """
    try:
        calculation = rowan.Calculation.retrieve(uuid=calculation_uuid)
        
        formatted = f"⚙️ Calculation Details:\n\n"
        formatted += f"📝 Name: {calculation.get('name', 'N/A')}\n"
        formatted += f"🆔 UUID: {calculation_uuid}\n"
        formatted += f"📊 Status: {calculation.get('status', 'Unknown')}\n"
        formatted += f"⏱️ Elapsed: {calculation.get('elapsed', 0):.3f}s\n"
        
        settings = calculation.get('settings', {})
        if settings:
            formatted += f"\n⚙️ Settings:\n"
            formatted += f"   Method: {settings.get('method', 'N/A')}\n"
            if settings.get('basis_set'):
                formatted += f"   Basis Set: {settings.get('basis_set')}\n"
            if settings.get('tasks'):
                formatted += f"   Tasks: {', '.join(settings.get('tasks', []))}\n"
        
        molecules = calculation.get('molecules', [])
        if molecules:
            formatted += f"\n🧪 Molecules: {len(molecules)} structure(s)\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error retrieving calculation: {str(e)}"


@mcp.tool()
def rowan_job_status(job_uuid: str) -> str:
    """Get status of a specific job.
    
    Args:
        job_uuid: UUID of the job to check
    
    Returns:
        Job status information
    """
    try:
        # Note: Rowan API doesn't have direct job management
        # Jobs are managed through workflows
        formatted = f"📊 Job Status for {job_uuid}:\n\n"
        formatted += f"⚠️ **Important Note:**\n"
        formatted += f"Rowan manages computations through workflows, not individual jobs.\n"
        formatted += f"Please use `rowan_workflow_status(workflow_uuid)` instead.\n\n"
        formatted += f"💡 **To find your workflow:**\n"
        formatted += f"• Use `rowan_workflow_list()` to see all workflows\n"
        formatted += f"• Look for workflows with similar names or recent creation times\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error getting job status: {str(e)}"


@mcp.tool()
def rowan_job_results(job_uuid: str) -> str:
    """Retrieve results from a completed calculation.
    
    Args:
        job_uuid: UUID of the job to get results for
    
    Returns:
        Job results
    """
    try:
        # Note: Rowan API doesn't have direct job management
        # Results are accessed through workflows
        formatted = f"📊 Job Results for {job_uuid}:\n\n"
        formatted += f"⚠️ **Important Note:**\n"
        formatted += f"Rowan manages results through workflows, not individual jobs.\n"
        formatted += f"Please use `rowan_workflow_retrieve(workflow_uuid)` instead.\n\n"
        formatted += f"💡 **To get your results:**\n"
        formatted += f"1. Use `rowan_workflow_list()` to find your workflow\n"
        formatted += f"2. Use `rowan_workflow_retrieve(workflow_uuid)` to get details\n"
        formatted += f"3. Check the `object_data` field for calculation results\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error getting job results: {str(e)}"


@mcp.tool()
def rowan_docking(
    name: str,
    protein: str,
    ligand: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5,
    additional_params: Optional[Dict[str, Any]] = None
) -> str:
    """Run protein-ligand docking calculations.
    
    Args:
        name: Name for the docking calculation
        protein: Protein specification (PDB ID like '1ABC', PDB content, or protein sequence)
        ligand: Ligand SMILES string
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
        additional_params: Additional docking-specific parameters
    
    Returns:
        Formatted docking results
    """
    try:
        # For docking workflows in Rowan, we need to check the exact format expected
        # Let's try different approaches based on what the API might accept
        
        approaches = []
        
        # Approach 1: Try PDB ID format (4-character codes)
        if len(protein) == 4 and protein.isalnum():
            approaches.append(("PDB ID", protein))
        
        # Approach 2: Try just the ligand SMILES (for small molecule only calculations)
        approaches.append(("Ligand only", ligand))
        
        # Approach 3: Try a structured format if docking supports it
        if len(protein) > 4:
            approaches.append(("Combined format", f"protein:{protein}|ligand:{ligand}"))
        
        last_error = None
        
        for approach_name, molecule_input in approaches:
            try:
                # Prepare kwargs for rowan.compute
                compute_kwargs = {
                    "name": f"{name} ({approach_name})",
                    "molecule": molecule_input,
                    "workflow_type": "docking",
                    "blocking": blocking,
                    "ping_interval": ping_interval
                }
                
                if folder_uuid:
                    compute_kwargs["folder_uuid"] = folder_uuid
                if additional_params:
                    compute_kwargs.update(additional_params)
                    
                result = rowan.compute(**compute_kwargs)
                
                # Format result for display
                formatted = f"✅ Docking calculation '{name}' completed successfully!\n\n"
                formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
                formatted += f"📊 Status: {result.get('status', 'Unknown')}\n"
                formatted += f"🧬 Approach: {approach_name}\n"
                formatted += f"🧬 Protein: {protein[:50]}{'...' if len(protein) > 50 else ''}\n"
                formatted += f"💊 Ligand: {ligand}\n"
                
                docking_data = result.get("object_data", {})
                if "binding_affinity" in docking_data:
                    formatted += f"🔗 Binding Affinity: {docking_data['binding_affinity']:.2f} kcal/mol\n"
                if "poses" in docking_data:
                    formatted += f"📐 Poses Generated: {len(docking_data['poses'])}\n"
                
                return formatted
                
            except Exception as e:
                last_error = e
                continue
        
        # If all approaches failed, provide helpful guidance
        error_msg = f"❌ Docking failed with all approaches. Last error: {str(last_error)}\n\n"
        error_msg += "🔧 **Troubleshooting Protein-Ligand Docking:**\n\n"
        error_msg += "**For protein input, try:**\n"
        error_msg += "• PDB ID (4 characters): `1ABC`\n"
        error_msg += "• Direct PDB file content\n\n"
        error_msg += "**For ligand input:**\n"
        error_msg += "• Valid SMILES string like: `CC(C)c1nc(cs1)CN(C)C(=O)N`\n\n"
        error_msg += "**Alternative approaches:**\n"
        error_msg += "• Use `rowan_compute()` with workflow_type='docking' and experiment with different molecule formats\n"
        error_msg += "• Check if your protein needs to be prepared/processed first\n"
        error_msg += "• Consider using PDB IDs from the Protein Data Bank\n\n"
        error_msg += "**Example working formats:**\n"
        error_msg += "• Protein: `1ABC` (PDB ID)\n"
        error_msg += "• Ligand: `CCO` (ethanol SMILES)\n"
        
        return error_msg
        
    except Exception as e:
        return f"❌ Error running docking: {str(e)}"


@mcp.tool()
def rowan_available_workflows() -> str:
    """Get list of all available Rowan MCP tools with descriptions.
    
    Returns:
        Comprehensive list of available Rowan MCP tools and their use cases
    """
    
    result = "🔬 **Available Rowan MCP Tools** 🔬\n\n"
    
    result += "✨ **Now with specific tools for each workflow type!**\n"
    result += "Each tool has tailored documentation and parameters.\n\n"
    
    # Group by common use cases
    result += "**🔬 Basic Calculations:**\n"
    result += "• `rowan_basic_calculation` - Energy, optimization, frequencies\n"
    result += "• `rowan_electronic_properties` - HOMO/LUMO, orbitals\n"
    result += "• `rowan_multistage_opt` - Multi-level optimization (RECOMMENDED for geometry)\n\n"
    
    result += "**🧬 Molecular Analysis:**\n"
    result += "• `rowan_conformers` - Find molecular conformations\n"
    result += "• `rowan_tautomers` - Tautomer enumeration\n"
    result += "• `rowan_descriptors` - Molecular descriptors for ML\n\n"
    
    result += "**⚗️ Chemical Properties:**\n"
    result += "• `rowan_pka` - pKa prediction\n"
    result += "• `rowan_redox_potential` - Redox potentials vs SCE\n"
    result += "• `rowan_bde` - Bond dissociation energies\n"
    result += "• `rowan_solubility` - Solubility prediction\n\n"
    
    result += "**🧪 Drug Discovery:**\n"
    result += "• `rowan_admet` - ADME-Tox properties\n"
    result += "• `rowan_docking` - Protein-ligand docking\n\n"
    
    result += "**🔬 Advanced Analysis:**\n"
    result += "• `rowan_scan` - Potential energy scans\n"
    result += "• `rowan_fukui` - Reactivity analysis\n"
    result += "• `rowan_spin_states` - Spin state preferences\n"
    result += "• `rowan_irc` - Reaction coordinate following\n"
    result += "• `rowan_molecular_dynamics` - MD simulations\n"
    result += "• `rowan_hydrogen_bond_basicity` - H-bond strength\n\n"
    
    result += "💡 **Usage Guidelines:**\n"
    result += "• For geometry optimization: use `rowan_multistage_opt` (RECOMMENDED)\n"
    result += "• For energy calculations: use `rowan_basic_calculation`\n"
    result += "• For conformer search: use `rowan_conformers`\n"
    result += "• For pKa prediction: use `rowan_pka`\n"
    result += "• For electronic structure: use `rowan_electronic_properties`\n"
    result += "• For drug properties: use `rowan_admet`\n"
    result += "• For reaction mechanisms: use `rowan_scan` then `rowan_irc`\n\n"
    
    result += "📋 **Total Available:** 15+ specialized tools\n"
    result += "🔗 **Each tool has specific documentation - check individual tool descriptions**\n"
    
    return result


@mcp.tool()
@log_mcp_call
def rowan_set_log_level(level: str = "INFO") -> str:
    """Set the logging level for debugging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Confirmation message
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    level = level.upper()
    
    if level not in valid_levels:
        return f"❌ Invalid log level. Use one of: {', '.join(valid_levels)}"
    
    logger.setLevel(getattr(logging, level))
    logger.info(f"📊 Log level changed to: {level}")
    
    return f"✅ Log level set to {level}"


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("🚀 Starting Rowan MCP Server...")
        logger.info(f"📊 Log level: {logger.level}")
        logger.info(f"📁 Log file: rowan_mcp.log")
        logger.info(f"🔑 API Key loaded: {'✅' if api_key else '❌'}")
        logger.info("🔗 Server ready for MCP connections!")
        
        print("🚀 Rowan MCP Server starting...")
        print("📝 Logging enabled - check rowan_mcp.log for detailed logs")
        print(f"🔑 API Key: {'✅ Loaded' if api_key else '❌ Missing'}")
        
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Server shutdown requested by user")
        print("\n👋 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server startup error: {e}")
        logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
        print(f"❌ Server error: {e}")
        print("📝 Check rowan_mcp.log for detailed error information")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP server mode - use dedicated HTTP server
        from .http_server import main as http_main
        http_main()
    else:
        # Default stdio mode
        main() 