"""
Fukui Analysis for Rowan MCP Server

This module provides Fukui indices calculations for reactivity prediction including:
- f(+) indices for electrophilic attack sites
- f(-) indices for nucleophilic attack sites  
- f(0) indices for radical attack sites
- Global electrophilicity index
"""

import os
import logging
import time
from typing import Any, Dict, List, Optional

try:
    import rowan
except ImportError:
    rowan = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if api_key and rowan:
    rowan.api_key = api_key

def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    
    try:
        start_time = time.time()
        
        if not rowan:
            raise ImportError("Rowan package not available - please install with 'pip install rowan'")
        
        logger.info(f"Calling Rowan {workflow_type} workflow")
        for key, value in kwargs.items():
            if key != 'ping_interval':
                logger.info(f"  {key}: {value}")
        
        result = rowan.compute(workflow_type=workflow_type, **kwargs)
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Rowan {workflow_type} completed in {duration:.2f} seconds")
        
        return result
        
    except Exception as e:
        logger.error(f"Rowan {workflow_type} failed: {str(e)}")
        raise e

def lookup_molecule_smiles(molecule_name: str) -> str:
    """Look up canonical SMILES using the advanced molecule_lookup system.
    
    Uses PubChemPy + SQLite caching + RDKit validation for scalable molecule lookup.
    """
    try:
        # Import the advanced molecule lookup system
        from .molecule_lookup import get_lookup_instance
        
        lookup = get_lookup_instance()
        smiles, source, metadata = lookup.get_smiles(molecule_name)
        
        if smiles:
            logger.info(f"Molecule lookup successful: '{molecule_name}' → '{smiles}' (source: {source})")
            return smiles
        else:
            logger.warning(f"Molecule lookup failed for '{molecule_name}': {metadata.get('error', 'Unknown error')}")
            # Return original input as fallback (might be valid SMILES)
            return molecule_name
            
    except ImportError as e:
        logger.error(f"Could not import molecule_lookup: {e}")
        # Fallback: return original input
        return molecule_name
    except Exception as e:
        logger.error(f"Molecule lookup error for '{molecule_name}': {e}")
        # Fallback: return original input
        return molecule_name

def rowan_fukui(
    name: str,
    molecule: str,
    optimize: bool = True,
    opt_method: Optional[str] = None,
    opt_basis_set: Optional[str] = None,
    opt_engine: Optional[str] = None,
    fukui_method: str = "gfn1_xtb",
    fukui_basis_set: Optional[str] = None,
    fukui_engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate Fukui indices for reactivity prediction with comprehensive control.
    
    Predicts sites of chemical reactivity by analyzing electron density changes upon
    gaining/losing electrons. Uses a two-step process: optimization + Fukui calculation.
    
    ** Fukui Index Types:**
    - **f(+)**: Electrophilic attack sites (nucleophile reactivity)
    - **f(-)**: Nucleophilic attack sites (electrophile reactivity)  
    - **f(0)**: Radical attack sites (average of f(+) and f(-))
    - **Global Electrophilicity Index**: Overall electrophilic character
    
    ** Key Features:**
    - Optional geometry optimization before Fukui calculation
    - Separate control over optimization and Fukui calculation methods
    - Per-atom reactivity indices for site-specific analysis
    - Global reactivity descriptors
    
    **Molecule Lookup**: Uses advanced PubChemPy + SQLite caching + RDKit validation system
    for robust molecule identification and SMILES canonicalization.
    
    Args:
        name: Name for the calculation
        molecule: Molecule name (e.g., "aspirin", "taxol") or SMILES string
        optimize: Whether to optimize geometry before Fukui calculation (default: True)
        opt_method: Method for optimization (default: None, uses engine default)
        opt_basis_set: Basis set for optimization (default: None, uses engine default)
        opt_engine: Engine for optimization (default: None, auto-selected)
        fukui_method: Method for Fukui calculation (default: "gfn1_xtb")
        fukui_basis_set: Basis set for Fukui calculation (default: None, uses method default)
        fukui_engine: Engine for Fukui calculation (default: None, auto-selected)
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Fukui indices and reactivity analysis with per-atom and global descriptors
    """
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Build optimization settings if requested
    opt_settings = None
    if optimize:
        opt_settings = {
            "charge": charge,
            "multiplicity": multiplicity
        }
        
        # Add optimization method/basis/engine if specified
        if opt_method:
            opt_settings["method"] = opt_method.lower()
        if opt_basis_set:
            opt_settings["basis_set"] = opt_basis_set.lower()
        
        # Default to fast optimization if no engine specified
        if not opt_engine and not opt_method:
            opt_settings["method"] = "gfn2_xtb"  # Fast optimization
            logger.info(f"No optimization method specified, defaulting to GFN2-xTB")
    
    # Build Fukui calculation settings
    fukui_settings = {
        "method": fukui_method.lower(),
        "charge": charge,
        "multiplicity": multiplicity
    }
    
    # Add Fukui basis set if specified
    if fukui_basis_set:
        fukui_settings["basis_set"] = fukui_basis_set.lower()
    
    # Validate Fukui method
    valid_fukui_methods = ["gfn1_xtb", "gfn2_xtb", "hf", "b3lyp", "pbe", "m06-2x"]
    if fukui_method.lower() not in valid_fukui_methods:
        pass  # Warning already logged by cleanup script
    
    # Build parameters for Rowan API
    fukui_params = {
        "name": name,
        "molecule": canonical_smiles,
        "fukui_settings": fukui_settings,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add optimization settings if enabled
    if optimize and opt_settings:
        fukui_params["opt_settings"] = opt_settings
        
    # Add engines if specified
    if opt_engine:
        fukui_params["opt_engine"] = opt_engine.lower()
    if fukui_engine:
        fukui_params["fukui_engine"] = fukui_engine.lower()
    
    try:
        result = log_rowan_api_call(
            workflow_type="fukui",
            **fukui_params
        )
        
        return result
            
    except Exception as e:
        return f"Fukui analysis failed: {str(e)}"

def test_fukui():
    """Test the fukui function."""
    return rowan_fukui(
        name="test_fukui",
        molecule="benzene",
        fukui_method="gfn1_xtb",
        blocking=True
    )

if __name__ == "__main__":
    print(test_fukui()) 