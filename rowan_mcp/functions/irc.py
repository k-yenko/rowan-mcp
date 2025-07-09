"""
Rowan IRC (Intrinsic Reaction Coordinate) function for MCP tool integration.
"""

from typing import Any, Dict, List, Optional
import rowan
import logging
import os

# Set up logger
logger = logging.getLogger(__name__)

# Get API key from environment
api_key = os.environ.get("ROWAN_API_KEY")
if api_key:
    rowan.api_key = api_key
else:
    logger.warning("ROWAN_API_KEY not found in environment")

def rowan_irc(
    name: str,
    molecule: str,
    mode: str = "rapid",
    solvent: Optional[str] = None,
    preopt: bool = False,
    max_irc_steps: int = 10,
    step_size: float = 0.05,
    starting_ts: Optional[str] = None,
    # Workflow parameters
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Follow intrinsic reaction coordinates from transition states.
    
    Traces reaction pathways from transition states to reactants and products.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string (should be a transition state)
        mode: Calculation mode ("rapid", "careful", "meticulous")
        solvent: Solvent for the calculation (optional)
        preopt: Whether to pre-optimize the structure before IRC (default: False)
        max_irc_steps: Maximum number of IRC steps to take (default: 10)
        step_size: Step size for IRC in Angstroms (default: 0.05, range: 0.001-0.1)
        starting_ts: UUID of a previous transition state calculation (optional)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        IRC pathway results
    """
    # Parameter validation
    valid_modes = ["rapid", "careful", "meticulous"]
    mode_lower = mode.lower()
    if mode_lower not in valid_modes:
        return f"Error: Invalid mode '{mode}'. Valid options: {', '.join(valid_modes)}"
    
    # Validate step size (0.001 <= step_size <= 0.1)
    if step_size < 0.001 or step_size > 0.1:
        return f"Error: step_size must be between 0.001 and 0.1 Å (got {step_size})"
    
    if max_irc_steps <= 0:
        return f"Error: max_irc_steps must be positive (got {max_irc_steps})"
    
    try:
        # Build basic parameters for rowan.compute
        compute_params = {
            "name": name,
            "molecule": molecule,
            "workflow_type": "irc",
            "mode": mode_lower,
            "preopt": preopt,
            "max_irc_steps": max_irc_steps,
            "step_size": step_size,
            "folder_uuid": folder_uuid,
            "blocking": blocking,
            "ping_interval": ping_interval
        }
        
        # Add optional parameters
        if solvent:
            compute_params["solvent"] = solvent
            
        if starting_ts:
            compute_params["starting_ts"] = starting_ts
        
        # Submit IRC calculation
        result = rowan.compute(**compute_params)
        
        # Format results
        uuid = result.get('uuid', 'N/A')
        status = result.get('status', 'unknown')
        
        if blocking:
            if status == "success":
                return f"IRC calculation '{name}' completed successfully!\nUUID: {uuid}"
            else:
                return f"IRC calculation failed\nUUID: {uuid}\nStatus: {status}"
        else:
            return f"IRC calculation '{name}' submitted!\nUUID: {uuid}\nStatus: Running..."
            
    except Exception as e:
        logger.error(f"Error in rowan_irc: {str(e)}")
        return f"IRC calculation failed: {str(e)}"

def test_rowan_irc():
    """Test the rowan_irc function."""
    try:
        result = rowan_irc(
            name="test_irc",
            molecule="C=C",
            mode="rapid",
            max_irc_steps=5,
            blocking=False
        )
        print(f"IRC test result: {result}")
        return True
    except Exception as e:
        print(f"IRC test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_irc()