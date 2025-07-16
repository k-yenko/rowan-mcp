"""
Rowan tautomers function for drug design.
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



def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    
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
        raise e

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
    result = log_rowan_api_call(
        workflow_type="tautomers",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)

def test_rowan_tautomers():
    """Test the rowan_tautomers function."""
    try:
        # Test with a simple molecule (non-blocking to avoid long wait)
        result = rowan_tautomers("test_tautomers", "CCO", blocking=False)
        print(" Tautomers test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f" Tautomers test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_tautomers() 