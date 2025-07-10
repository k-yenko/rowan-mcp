"""MacropKa workflow function for MCP server."""

import os
import logging
from typing import Optional, Union, List

import rowan

# Configure logging
logger = logging.getLogger(__name__)

# Get API key from environment
api_key = os.environ.get("ROWAN_API_KEY")
if api_key:
    rowan.api_key = api_key
else:
    logger.warning("ROWAN_API_KEY not found in environment")


def log_rowan_api_call(func_name: str, **kwargs):
    """Log Rowan API calls for debugging."""
    logger.debug(f"Calling {func_name} with args: {kwargs}")


def rowan_macropka(
    name: str,
    molecule: str,
    min_pH: float = 0.0,
    max_pH: float = 14.0,
    max_charge: int = 2,
    min_charge: int = -2,
    compute_aqueous_solubility: bool = False,
    compute_solvation_energy: bool = True,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """
    Calculate macroscopic pKa values and related properties for a molecule.
    
    This workflow computes pKa values, microstates, isoelectric point, and optionally
    solvation energy and aqueous solubility across different pH values.
    
    Args:
        name: Name for the calculation
        molecule: SMILES string of the molecule
        min_pH: Minimum pH for calculations (default: 0.0)
        max_pH: Maximum pH for calculations (default: 14.0)
        max_charge: Maximum charge to consider for microstates (default: 2)
        min_charge: Minimum charge to consider for microstates (default: -2)
        compute_aqueous_solubility: Whether to compute aqueous solubility by pH (default: False)
        compute_solvation_energy: Whether to compute solvation energy for Kpuu (default: True)
        folder_uuid: UUID of folder to save results in
        blocking: Wait for calculation to complete (default: True)
        ping_interval: How often to check status in blocking mode (default: 5 seconds)
        
    Returns:
        String with workflow UUID or results depending on blocking mode
    """
    try:
        # Validate pH range
        if min_pH >= max_pH:
            return "Error: min_pH must be less than max_pH"
        
        # Validate charge range  
        if min_charge >= max_charge:
            return "Error: min_charge must be less than max_charge"
            
        # Log the API call
        log_rowan_api_call(
            "rowan.compute",
            workflow_type="macropka",
            name=name,
            molecule=molecule,
            min_pH=min_pH,
            max_pH=max_pH,
            max_charge=max_charge,
            min_charge=min_charge,
            compute_aqueous_solubility=compute_aqueous_solubility,
            compute_solvation_energy=compute_solvation_energy,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        # Submit calculation
        result = rowan.compute(
            workflow_type="macropka",
            name=name,
            molecule=molecule,  # Required by rowan.compute() API
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval,
            # Workflow-specific parameters for MacropKaWorkflow
            initial_smiles=molecule,  # Required by MacropKaWorkflow Pydantic model
            min_pH=min_pH,
            max_pH=max_pH,
            max_charge=max_charge,
            min_charge=min_charge,
            compute_aqueous_solubility=compute_aqueous_solubility,
            compute_solvation_energy=compute_solvation_energy
        )
        
        return result
            
    except Exception as e:
        logger.error(f"Error in rowan_macropka: {str(e)}")
        return f"MacropKa calculation failed: {str(e)}"


# Test function
if __name__ == "__main__":
    # Test with ethanol
    result = rowan_macropka(
        name="Ethanol MacropKa Test",
        molecule="CCO",
        compute_aqueous_solubility=True,
        blocking=True
    )
    print(result)