"""
Electronic Properties Analysis for Rowan MCP Server

This module provides electronic structure property calculations including:
- HOMO/LUMO energies and molecular orbitals
- Electron density and electrostatic potential
- Population analysis and bond orders
- Orbital visualization data
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

def rowan_electronic_properties(
    name: str,
    molecule: str,
    # Settings parameters (quantum chemistry calculation settings)
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    # Cube computation control parameters
    compute_density_cube: bool = True,
    compute_electrostatic_potential_cube: bool = True,
    compute_num_occupied_orbitals: int = 1,
    compute_num_virtual_orbitals: int = 1,
    # Workflow control parameters
    mode: Optional[str] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate comprehensive electronic structure properties using Rowan's ElectronicPropertiesWorkflow.
    
    Implements the ElectronicPropertiesWorkflow class for computing detailed electronic properties including:
    - **Molecular Orbitals**: HOMO/LUMO energies, orbital cubes, occupation numbers
    - **Electron Density**: Total, α/β spin densities, spin density differences
    - **Electrostatic Properties**: Dipole moments, quadrupole moments, electrostatic potential
    - **Population Analysis**: Mulliken charges, Löwdin charges
    - **Bond Analysis**: Wiberg bond orders, Mayer bond orders
    - **Visualization Data**: Cube files for density, ESP, and molecular orbitals
    
    **Molecule Lookup**: Uses advanced PubChemPy + SQLite caching + RDKit validation system
    for robust molecule identification and SMILES canonicalization.
    
    Args:
        name: Name for the calculation
        molecule: Molecule name (e.g., "aspirin", "taxol") or SMILES string
        method: QM method (default: b3lyp for electronic properties)
        basis_set: Basis set (default: def2-svp for balanced accuracy)
        engine: Computational engine (default: psi4)
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1 for singlet)
        compute_density_cube: Generate electron density cube (default: True)
        compute_electrostatic_potential_cube: Generate ESP cube (default: True)
        compute_num_occupied_orbitals: Number of occupied MOs to save (default: 1)
        compute_num_virtual_orbitals: Number of virtual MOs to save (default: 1)
        mode: Calculation mode/precision (optional)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Comprehensive electronic properties results following ElectronicPropertiesWorkflow format
    """
    # Look up canonical SMILES using advanced molecule lookup (PubChemPy + caching + RDKit)
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Apply smart defaults for electronic properties calculations
    if method is None:
        method = "b3lyp"  # Good for electronic properties
    if basis_set is None:
        basis_set = "def2-svp"  # Balanced accuracy/cost for properties
    if engine is None:
        engine = "psi4"  # Robust for electronic properties
    
    # Validate orbital count parameters
    if compute_num_occupied_orbitals < 0:
        return f"compute_num_occupied_orbitals must be non-negative (got {compute_num_occupied_orbitals})"
    if compute_num_virtual_orbitals < 0:
        return f"compute_num_virtual_orbitals must be non-negative (got {compute_num_virtual_orbitals})"
    
    # Build parameters following ElectronicPropertiesWorkflow specification
    electronic_params = {
        "name": name,
        "molecule": canonical_smiles,  # API interface requirement
        "initial_molecule": canonical_smiles,  # ElectronicPropertiesWorkflow requirement
        # Settings (quantum chemistry parameters) - exactly as in ElectronicPropertiesWorkflow
        "settings": {
            "method": method.lower(),
            "basis_set": basis_set.lower(),
            "engine": engine.lower(),
            "charge": charge,
            "multiplicity": multiplicity
        },
        # Cube computation control - exactly as in ElectronicPropertiesWorkflow
        "compute_density_cube": compute_density_cube,
        "compute_electrostatic_potential_cube": compute_electrostatic_potential_cube,
        "compute_num_occupied_orbitals": compute_num_occupied_orbitals,
        "compute_num_virtual_orbitals": compute_num_virtual_orbitals,
        # Workflow parameters
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add mode if specified (optional in ElectronicPropertiesWorkflow)
    if mode:
        electronic_params["mode"] = mode
    
    try:
        result = log_rowan_api_call(
            workflow_type="electronic_properties",
            **electronic_params
        )
        
        # Enhanced result formatting for electronic properties
        if blocking:
            status = result.get('status', result.get('object_status', 'Unknown'))
            
            if status == 2:  # Completed successfully
                formatted = f"Electronic properties calculation for '{name}' completed successfully!\n\n"
            elif status == 3:  # Failed
                formatted = f"Electronic properties calculation for '{name}' failed!\n\n"
            else:
                formatted = f"Electronic properties calculation for '{name}' submitted!\n\n"
            
            formatted += f"Molecule: {molecule}\n"
            formatted += f"Canonical SMILES: {canonical_smiles}\n"
            formatted += f"Job UUID: {result.get('uuid', 'N/A')}\n"
            formatted += f"Status: {status}\n\n"
            
            formatted += f"Molecule Lookup: Advanced PubChemPy + SQLite + RDKit system\n\n"
            formatted += f"Calculation Settings:\n"
            formatted += f"• Method: {method.upper()}\n"
            formatted += f"• Basis Set: {basis_set}\n"
            formatted += f"• Engine: {engine.upper()}\n"
            formatted += f"• Charge: {charge}, Multiplicity: {multiplicity}\n\n"
            
            formatted += f"Property Calculations:\n"
            formatted += f"• Density Cube: {'Enabled' if compute_density_cube else 'Disabled'}\n"
            formatted += f"• ESP Cube: {'Enabled' if compute_electrostatic_potential_cube else 'Disabled'}\n"
            formatted += f"• Occupied MOs: {compute_num_occupied_orbitals}\n"
            formatted += f"• Virtual MOs: {compute_num_virtual_orbitals}\n\n"
            
            if status == 2:
                formatted += f"Additional Analysis:\n"
                formatted += f"• Use rowan_calculation_retrieve('{result.get('uuid')}') for full calculation details\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for workflow metadata\n"
                
            elif status == 3:
                formatted += f"Troubleshooting:\n"
                formatted += f"• Try simpler method/basis: method='hf', basis_set='sto-3g'\n"
                formatted += f"• Check molecular charge and multiplicity\n"
                formatted += f"• Disable cube generation for faster calculations\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            else:
                formatted += f"Next Steps:\n"
                formatted += f"• Monitor status with rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
                formatted += f"• Electronic properties calculations may take several minutes\n"
            
            return formatted
        else:
            return str(result)
            
    except Exception as e:
        error_msg = f"Electronic properties calculation failed: {str(e)}\n\n"
        error_msg += f"Molecule: {molecule}\n"
        error_msg += f"Canonical SMILES: {canonical_smiles}\n"
        error_msg += f"Settings: {method}/{basis_set}/{engine}\n\n"
        error_msg += f"Molecule Lookup: Advanced PubChemPy + SQLite + RDKit system\n\n"
        error_msg += f"Common Issues:\n"
        error_msg += f"• Invalid method/basis set combination\n"
        error_msg += f"• Incorrect charge/multiplicity for molecule\n"
        error_msg += f"• Engine compatibility issues\n"
        error_msg += f"• Molecule not found in PubChem database\n"
        error_msg += f"• Try with default parameters first\n"
        return error_msg

def test_electronic_properties():
    """Test the electronic properties function with advanced molecule lookup."""
    return rowan_electronic_properties(
        name="test_electronic_properties",
        molecule="aspirin",  # Test advanced lookup with a pharmaceutical
        method="hf",
        basis_set="sto-3g",
        blocking=True
    )

if __name__ == "__main__":
    print(test_electronic_properties()) 