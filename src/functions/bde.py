"""
Rowan bond dissociation energy (BDE) function.
"""

import os
import logging
import time
from typing import Optional

try:
    import rowan
except ImportError:
    rowan = None

# Setup logging
logger = logging.getLogger(__name__)

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if rowan and api_key:
    rowan.api_key = api_key

def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""

    try:
        start_time = time.time()
        result = rowan.compute(workflow_type=workflow_type, **kwargs)
        api_time = time.time() - start_time
        
        return result
        
    except Exception as e:
        api_time = time.time() - start_time

        raise e

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
    # Basic SMILES formatting (no validation - let Rowan handle that)
    logger.info(f"   Name: {name}")
    logger.info(f"   Input molecule: {molecule}")
    logger.info(f"   Input type: {type(molecule)}")
    
    # Just ensure it's a clean string - no validation
    molecule_to_use = str(molecule).strip()
    
    logger.info(f"    Sending to Rowan API: '{molecule_to_use}'")
    
    result = log_rowan_api_call(
        workflow_type="bde",
        name=name,
        molecule=molecule_to_use,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)

def test_rowan_bde():
    """Test the rowan_bde function."""
    try:
        # Test with a simple molecule (non-blocking to avoid long wait)
        result = rowan_bde("test_bde", "CCO", blocking=False)
        print(" BDE test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f" BDE test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_bde() 