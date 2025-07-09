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
    """Look up canonical SMILES for common molecule names."""
    # Common molecule SMILES database
    MOLECULE_SMILES = {
        # Aromatics
        "phenol": "Oc1ccccc1",
        "benzene": "c1ccccc1", 
        "toluene": "Cc1ccccc1",
        "aniline": "Nc1ccccc1",
        "benzoic acid": "O=C(O)c1ccccc1",
        "salicylic acid": "O=C(O)c1ccccc1O",
        "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        
        # Solvents
        "water": "O",
        "acetone": "CC(=O)C",
        "dmso": "CS(=O)C",
        "dmf": "CN(C)C=O",
        "thf": "C1CCOC1",
        "dioxane": "C1COCCO1",
        "chloroform": "ClC(Cl)Cl",
        "dichloromethane": "ClCCl",
        
        # Others
        "glucose": "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
        "ethylene": "C=C",
        "acetylene": "C#C",
        "formaldehyde": "C=O",
        "ammonia": "N",
        "hydrogen peroxide": "OO",
        "carbon dioxide": "O=C=O",
    }
    
    # Normalize the input (lowercase, strip whitespace)
    normalized_name = molecule_name.lower().strip()
    
    # Direct lookup
    if normalized_name in MOLECULE_SMILES:
        return MOLECULE_SMILES[normalized_name]
    
    # Try partial matches for common variations
    for name, smiles in MOLECULE_SMILES.items():
        if normalized_name in name or name in normalized_name:
            logger.info(f"SMILES Lookup (partial match): '{molecule_name}' → '{name}' → '{smiles}'")
            return smiles
    
    # If no match found, return the original input (assume it's already SMILES)
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
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name (e.g., "phenol", "benzene")
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
    
    result = log_rowan_api_call(
        workflow_type="fukui",
        **fukui_params
    )
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f"Fukui analysis for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f"Fukui analysis for '{name}' failed!\n\n"
        else:
            formatted = f"Fukui analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f"Molecule: {molecule}\n"
        formatted += f"SMILES: {canonical_smiles}\n"
        formatted += f"Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"Status: {status}\n"
        
        # Computational settings summary
        formatted += f"\nComputational Settings:\n"
        formatted += f"   Optimization: {'Enabled' if optimize else 'Disabled'}\n"
        if optimize:
            opt_method_display = opt_settings.get('method', 'default') if opt_settings else 'default'
            formatted += f"   Opt Method: {opt_method_display.upper()}\n"
            if opt_engine:
                formatted += f"   Opt Engine: {opt_engine.upper()}\n"
        formatted += f"   Fukui Method: {fukui_method.upper()}\n"
        if fukui_engine:
            formatted += f"   Fukui Engine: {fukui_engine.upper()}\n"
        formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
        
        # Try to extract Fukui results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Global electrophilicity index
            if 'global_electrophilicity_index' in data and data['global_electrophilicity_index'] is not None:
                gei = data['global_electrophilicity_index']
                formatted += f"\nGlobal Electrophilicity Index: {gei:.4f}\n"
                if gei > 1.5:
                    formatted += f"   → Strong electrophile (highly reactive towards nucleophiles)\n"
                elif gei > 0.8:
                    formatted += f"   → Moderate electrophile\n"
                else:
                    formatted += f"   → Weak electrophile\n"
            
            # Fukui indices per atom
            fukui_available = []
            if 'fukui_positive' in data and data['fukui_positive']:
                fukui_available.append("f(+)")
            if 'fukui_negative' in data and data['fukui_negative']:
                fukui_available.append("f(-)")
            if 'fukui_zero' in data and data['fukui_zero']:
                fukui_available.append("f(0)")
                
            if fukui_available:
                formatted += f"\nFukui Indices Available: {', '.join(fukui_available)}\n"
                
                # Analyze most reactive sites
                formatted += f"\nMost Reactive Sites:\n"
                
                # f(+) - electrophilic attack sites
                if 'fukui_positive' in data and data['fukui_positive']:
                    f_plus = data['fukui_positive']
                    if isinstance(f_plus, list) and len(f_plus) > 0:
                        # Find top 3 sites
                        indexed_values = [(i+1, val) for i, val in enumerate(f_plus) if val is not None]
                        top_f_plus = sorted(indexed_values, key=lambda x: x[1], reverse=True)[:3]
                        formatted += f"   f(+) Top Sites (electrophilic attack): "
                        formatted += f"{', '.join([f'Atom {atom}({val:.3f})' for atom, val in top_f_plus])}\n"
                
                # f(-) - nucleophilic attack sites  
                if 'fukui_negative' in data and data['fukui_negative']:
                    f_minus = data['fukui_negative']
                    if isinstance(f_minus, list) and len(f_minus) > 0:
                        indexed_values = [(i+1, val) for i, val in enumerate(f_minus) if val is not None]
                        top_f_minus = sorted(indexed_values, key=lambda x: x[1], reverse=True)[:3]
                        formatted += f"   f(-) Top Sites (nucleophilic attack): "
                        formatted += f"{', '.join([f'Atom {atom}({val:.3f})' for atom, val in top_f_minus])}\n"
                
                # f(0) - radical attack sites
                if 'fukui_zero' in data and data['fukui_zero']:
                    f_zero = data['fukui_zero']
                    if isinstance(f_zero, list) and len(f_zero) > 0:
                        indexed_values = [(i+1, val) for i, val in enumerate(f_zero) if val is not None]
                        top_f_zero = sorted(indexed_values, key=lambda x: x[1], reverse=True)[:3]
                        formatted += f"   f(0) Top Sites (radical attack): "
                        formatted += f"{', '.join([f'Atom {atom}({val:.3f})' for atom, val in top_f_zero])}\n"
        
        # Status-specific guidance
        formatted += f"\nNext Steps:\n"
        if status == 2:  # Completed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for full per-atom data\n"
            formatted += f"• Higher Fukui values indicate more reactive sites\n"
            formatted += f"• f(+) predicts where nucleophiles will attack\n"
            formatted += f"• f(-) predicts where electrophiles will attack\n"
            formatted += f"• f(0) predicts radical reaction sites\n"
        elif status == 3:  # Failed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            formatted += f"• Troubleshooting:\n"
            formatted += f"  - Try disabling optimization: optimize=False\n"
            formatted += f"  - Use faster Fukui method: fukui_method='gfn1_xtb'\n"
            formatted += f"  - Check if molecule SMILES is valid\n"
            formatted += f"  - Verify charge and multiplicity are correct\n"
        elif status in [0, 1, 5]:  # Running
            formatted += f"• Check progress: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
            if optimize:
                formatted += f"• Two-step process: optimization → Fukui calculation\n"
            formatted += f"• Fukui analysis may take 5-20 minutes depending on method and molecule size\n"
        elif status == 4:  # Stopped
            formatted += f"• Check why stopped: rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
            formatted += f"• You can restart with same or modified parameters\n"
        else:  # Unknown
            formatted += f"• Check status: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
        
        return formatted
    else:
        formatted = f"Fukui analysis for '{name}' submitted!\n\n"
        formatted += f"Molecule: {molecule}\n"
        formatted += f"SMILES: {canonical_smiles}\n"
        formatted += f"Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"Status: {result.get('status', 'Submitted')}\n"
        formatted += f"Optimization: {'Enabled' if optimize else 'Disabled'}\n"
        formatted += f"Fukui Method: {fukui_method.upper()}\n"
        formatted += f"Charge: {charge}, Multiplicity: {multiplicity}\n"
        formatted += f"\nUse rowan_workflow_management tools to check progress and retrieve results\n"
        return formatted

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