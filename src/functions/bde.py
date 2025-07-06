"""
Calculate bond dissociation energy (BDE) for molecules to determine bond strength - useful for reaction prediction, stability analysis, or understanding molecular fragmentation. Modes: reckless/rapid/careful/meticulous. Input: molecule (SMILES), optional atoms to break.
"""

import os
import rowan
from typing import Optional, List, Union

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

def rowan_bde(
    name: str,
    molecule: str,
    mode: str = "rapid",
    atoms: Optional[List[int]] = None,
    optimize_fragments: Optional[bool] = None,
    all_CH: bool = False,
    all_CX: bool = False,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate bond dissociation energy (BDE) for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        mode: Calculation mode - reckless/rapid/careful/meticulous (default: rapid)
        atoms: Specific atoms to dissociate (1-indexed)
        optimize_fragments: Whether to optimize fragments (default depends on mode)
        all_CH: Dissociate all C-H bonds (default: False)
        all_CX: Dissociate all C-X bonds where X is halogen (default: False)
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        Bond dissociation energy calculation results
    """
    try:
        # Build kwargs for API call
        kwargs = {
            "workflow_type": "bde",
            "name": name,
            "molecule": molecule,
            "mode": mode.lower(),
            "folder_uuid": folder_uuid,
            "blocking": blocking,
            "ping_interval": ping_interval
        }
        
        # Add optional parameters only if specified
        if atoms is not None:
            kwargs["atoms"] = atoms
        if optimize_fragments is not None:
            kwargs["optimize_fragments"] = optimize_fragments
        if all_CH:
            kwargs["all_CH"] = all_CH
        if all_CX:
            kwargs["all_CX"] = all_CX
        
        result = log_rowan_api_call(**kwargs)
        
        return str(result)
        
    except Exception as e:
        error_response = {
            "error": f"BDE calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)


def test_rowan_bde():
    """Test the rowan_bde function."""
    try:
        # Test with ethane C-C bond
        result = rowan_bde(
            name="test_ethane_CC",
            molecule="CC",
            mode="rapid"
        )
        print("✅ BDE test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"BDE test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_bde()