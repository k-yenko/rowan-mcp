"""
Calculate hydrogen bond basicity (pKBHX) values for molecules to predict H-bond acceptor strength - useful for queries about pyridine/imine nitrogen basicity, comparing acceptor sites, or understanding binding selectivity. Input: molecule (SMILES string).
"""

import os
import rowan
from typing import Optional

# Set up logging
import logging
logger = logging.getLogger(__name__)

# Configure rowan API key
if not hasattr(rowan, 'api_key') or not rowan.api_key:
    api_key = os.getenv("ROWAN_API_KEY")
    if api_key:
        rowan.api_key = api_key
        logger.info("🔑 Rowan API key configured")
    else:
        logger.error("No ROWAN_API_KEY found in environment")

def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls and let Rowan handle its own errors."""
    
    # Simple logging for calculations
    logger.info(f" Starting {workflow_type.replace('_', ' ')}...")
    
    # Let Rowan handle everything - no custom error handling
    return rowan.compute(workflow_type=workflow_type, **kwargs)

def rowan_hydrogen_bond_basicity(
    name: str,
    molecule: str,
    do_csearch: bool = True,
    do_optimization: bool = True,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate hydrogen bond basicity (pKBHX) values for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        do_csearch: Whether to perform conformational search (default: True)
        do_optimization: Whether to perform optimization (default: True)
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        Hydrogen bond basicity calculation results with pKBHX values
    """
    try:
        result = log_rowan_api_call(
            workflow_type="hydrogen_bond_basicity",
            name=name,
            molecule=molecule,
            do_csearch=do_csearch,
            do_optimization=do_optimization,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        return str(result)
        
    except Exception as e:
        error_response = {
            "error": f"Hydrogen bond basicity calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)


def test_rowan_hydrogen_bond_basicity():
    """Test the rowan_hydrogen_bond_basicity function."""
    try:
        # Test with pyridine
        result = rowan_hydrogen_bond_basicity(
            name="test_pyridine_basicity",
            molecule="c1ccncc1"
        )
        print("✅ Hydrogen bond basicity test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"Hydrogen bond basicity test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_hydrogen_bond_basicity()