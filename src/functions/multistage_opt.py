"""
Rowan multistage optimization function for geometry optimization.
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
        raise e

def rowan_multistage_opt(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 30
) -> str:
    """Run multi-level geometry optimization.
    
    Performs hierarchical optimization using multiple levels of theory:
    GFN2-xTB → AIMNet2 → DFT for optimal balance of speed and accuracy.
    
    This is a method for geometry optimization as it provides:
    - High accuracy final structures
    - Efficient computational cost
    - Reliable convergence
    
    Use this for: Geometry optimization, conformational analysis, structure refinement
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 30, longer for multi-stage)
    
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

def test_rowan_multistage_opt():
    """Test the rowan_multistage_opt function."""
    try:
        # Test with a simple molecule (non-blocking to avoid long wait)
        result = rowan_multistage_opt("test_opt", "CCO", blocking=False)
        print(" Multistage optimization test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f" Multistage optimization test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_multistage_opt() 