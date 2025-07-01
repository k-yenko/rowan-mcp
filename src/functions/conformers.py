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
) -> str:
    """Generate and optimize molecular conformers using Rowan's conformer_search workflow.
    
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
    
    result = log_rowan_api_call(
        workflow_type="conformer_search",
        name=name,
        molecule=molecule,
        mode=mode,
        max_conformers=max_conformers,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    
    # Format results based on whether we waited or not
    if blocking:
        # We waited for completion - format actual results
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f" Conformer search for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f" Conformer search for '{name}' failed!\n\n"
        else:
            formatted = f" Conformer search for '{name}' finished with status {status}\n\n"
            
        formatted += f" Molecule: {molecule}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {status}\n"
        formatted += f" Mode: {mode.upper()}\n"
        formatted += f" Max Conformers: {max_conformers}\n"
        
        # Try to extract actual results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Count conformers found
            if 'conformers' in data:
                conformer_count = len(data['conformers']) if isinstance(data['conformers'], list) else data.get('num_conformers', 'Unknown')
                formatted += f" Generated Conformers: {conformer_count}\n"
            
            # Energy information
            if 'energies' in data and isinstance(data['energies'], list) and data['energies']:
                energies = data['energies']
                min_energy = min(energies)
                max_energy = max(energies)
                energy_range = max_energy - min_energy
                formatted += f" Energy Range: {min_energy:.3f} to {max_energy:.3f} kcal/mol (Δ={energy_range:.3f})\n"
                formatted += f" Lowest Energy Conformer: {min_energy:.3f} kcal/mol\n"
            
            # Additional properties if available
            if 'properties' in data:
                props = data['properties']
                formatted += f" Properties calculated: {', '.join(props.keys())}\n"
        
        # Basic guidance
        if status == 2:
            formatted += f"\n Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
    else:
        # Non-blocking mode - just submission confirmation
        formatted = f" Conformer search for '{name}' submitted!\n\n"
        formatted += f" Molecule: {molecule}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {result.get('status', 'Submitted')}\n"
        formatted += f" Mode: {mode.upper()}\n"
        formatted += f" Max Conformers: {max_conformers}\n"
    
    return formatted

if __name__ == "__main__":
    pass 