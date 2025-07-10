"""
Rowan conformers function for conformational analysis.
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
    """Log Rowan API calls and let Rowan handle its own errors."""
    
    # Simple logging for long-running calculations
    if workflow_type in ["multistage_opt", "conformer_search"]:
        blocking = kwargs.get('blocking', True)
        if blocking:
            logger.info(f" Starting {workflow_type.replace('_', ' ')}...")
        else:
            logger.info(f" Submitting {workflow_type.replace('_', ' ')} without waiting")
    
    # Let Rowan handle everything - no custom error handling
    return rowan.compute(workflow_type=workflow_type, **kwargs)

def rowan_conformers(
    name: str,
    molecule: str,
    max_conformers: int = 50,
    mode: str = "rapid",
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
):
    """Generate and optimize molecular conformers using Rowan's conformer_search workflow. Valid modes are "reckless", "rapid", "careful", and "meticulous", and default to using SMILES strings for the "molecule" parameter.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name
        max_conformers: Maximum number of conformers to generate (default: 50)
        mode: Conformer search mode - "reckless", "rapid", "careful", "meticulous" (default: "rapid")
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        Conformer search results (actual results if blocking=True)
    """
    
    # Validate mode parameter
    valid_modes = ["reckless", "rapid", "careful", "meticulous"]
    if mode not in valid_modes:
        raise ValueError(
            f"Invalid mode '{mode}'. Valid modes are: {', '.join(valid_modes)}"
        )
    
    return log_rowan_api_call(
        workflow_type="conformer_search",
        name=name,
        molecule=molecule,
        mode=mode,
        max_conformers=max_conformers,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )

if __name__ == "__main__":
    pass 