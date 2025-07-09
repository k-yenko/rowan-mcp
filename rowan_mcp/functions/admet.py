"""
Rowan ADMET properties function for drug discovery.
"""

import os
import logging
import time
import traceback
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


def test_rowan_admet():
    """Test the rowan_admet function."""
    try:
        # Test with a simple molecule (non-blocking to avoid long wait)
        result = rowan_admet("test_admet", "CCO", blocking=False)
        print("ADMET test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f"ADMET test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_admet() 