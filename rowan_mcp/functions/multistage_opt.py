"""
Rowan multistage optimization function for geometry optimization.
"""

import os
import logging
import time
from typing import Optional, List, Dict, Any

try:
    import rowan
except ImportError:
    rowan = None

# Setup logging
logger = logging.getLogger(__name__)



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
    mode: str = "rapid",
    solvent: Optional[str] = None,
    xtb_preopt: bool = False,
    constraints: Optional[List[Dict[str, Any]]] = None,
    transition_state: bool = False,
    frequencies: bool = False,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 30
) -> str:
    """Run multi-level geometry optimization using stjames MultiStageOptWorkflow.
    
    Performs hierarchical optimization using multiple levels of theory based on mode. There are only four valid modes:
    
    **RAPID** (default): GFN2-xTB optimization → r²SCAN-3c single point
    **RECKLESS**: GFN-FF optimization → GFN2-xTB single point  
    **CAREFUL**: GFN2-xTB preopt → r²SCAN-3c optimization → ωB97X-3c single point
    **METICULOUS**: GFN2-xTB preopt → r²SCAN-3c opt → ωB97X-3c opt → ωB97M-D3BJ/def2-TZVPPD single point
    
    This follows the exact stjames MultiStageOptWorkflow implementation for:
    - High accuracy final structures
    - Efficient computational cost  
    - Reliable convergence across chemical space
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        mode: Optimization mode - "rapid", "reckless", "careful", or "meticulous" (default: "rapid")
        solvent: Solvent for single point calculation (e.g., "water", "dmso", "acetone")
        xtb_preopt: Whether to include xTB pre-optimization step (default: False)
        constraints: List of optimization constraints (default: None)
        transition_state: Whether this is a transition state optimization (default: False)
        frequencies: Whether to calculate vibrational frequencies (default: False)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 30)
    
    Returns:
        Comprehensive optimization results following MultiStageOptWorkflow format
        
    Example:
        # Basic optimization
        result = rowan_multistage_opt("aspirin_opt", "CC(=O)Oc1ccccc1C(=O)O")
        
        # With solvent and frequency analysis
        result = rowan_multistage_opt(
            "aspirin_water", 
            "CC(=O)Oc1ccccc1C(=O)O",
            mode="careful",
            solvent="water",
            frequencies=True
        )
    """
    
    # Validate mode parameter - only allow Rowan's supported modes
    valid_modes = ["rapid", "reckless", "careful", "meticulous"]
    if mode.lower() not in valid_modes:
        error_msg = f"Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}"
        logger.error(f"Mode validation failed: {error_msg}")
        return f"Error: {error_msg}"
    
    # Prepare parameters following stjames MultiStageOptWorkflow structure
    params = {
        "name": name,
        "molecule": molecule,
        "initial_molecule": molecule,  # Required by MultiStageOptWorkflow
        "mode": mode.lower(),
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add optional parameters if specified
    if solvent:
        params["solvent"] = solvent
        
    if xtb_preopt:
        params["xtb_preopt"] = xtb_preopt
        
    if constraints:
        params["constraints"] = constraints
        
    if transition_state:
        params["transition_state"] = transition_state
        
    if frequencies:
        params["frequencies"] = frequencies
    
    # Submit to Rowan using multistage_opt workflow
    result = log_rowan_api_call(
        workflow_type="multistage_opt",
        **params
    )
    return str(result)

def test_rowan_multistage_opt():
    """Test the rowan_multistage_opt function with stjames parameters."""
    try:
        # Test with stjames-compatible parameters
        result = rowan_multistage_opt(
            name="test_stjames_opt", 
            molecule="CCO", 
            mode="rapid",
            blocking=False
        )
        print("✅ Multistage optimization test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f"Multistage optimization test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_multistage_opt() 