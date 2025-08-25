"""
Calculate pKa values for molecules using Rowan API.
"""

import os
import rowan
from typing import Optional

# Set up logging
import logging
logger = logging.getLogger(__name__)



def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls and let Rowan handle its own errors."""
    
    # Simple logging for calculations
    logger.info(f" Starting {workflow_type.replace('_', ' ')}...")
    
    # Let Rowan handle everything - no custom error handling
    return rowan.compute(workflow_type=workflow_type, **kwargs)

def rowan_pka(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate pKa values for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        pKa calculation results
    """
    try:
        result = log_rowan_api_call(
            workflow_type="pka",
            name=name,
            molecule=molecule,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        return str(result)
        
    except Exception as e:
        error_response = {
            "error": f"pKa calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)


def test_rowan_pka():
    """Test the rowan_pka function."""
    try:
        # Test with minimal parameters
        result = rowan_pka(
            name="test_pka_water",
            molecule="O"
        )
        print("pKa test successful")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"pKa test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_pka() 