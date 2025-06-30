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

def rowan_conformers(
    name: str,
    molecule: str,
    max_conformers: int = 10,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    max_wait_time: int = 120,
    ping_interval: int = 5
) -> str:
    """Generate and optimize molecular conformers.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        max_conformers: Maximum number of conformers to generate
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        max_wait_time: Maximum time to wait in seconds (default: 120 = 2 minutes)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        Conformer search results (actual results if blocking=True)
    """
    settings = {"max_conformers": max_conformers}
    
    # Log the expected wait time
    if blocking:
        logger.info(f" Conformer search will wait up to {max_wait_time} seconds ({max_wait_time//60:.1f} minutes)")
        logger.info(f" Checking progress every {ping_interval} seconds")
    
    result = log_rowan_api_call(
        workflow_type="conformer_search",
        name=name,
        molecule=molecule,
        settings=settings,
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
        
        # Guidance based on results
        if status == 2:
            formatted += f"\n **Results Available:**\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
            formatted += f"• Conformers are ranked by energy (lowest = most stable)\n"
        elif status == 3:
            formatted += f"\n **Troubleshooting:**\n"
            formatted += f"• Try reducing max_conformers (currently {max_conformers})\n"
            formatted += f"• Check if molecule SMILES is valid\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
    else:
        # Non-blocking mode - just submission confirmation
        formatted = f" Conformer search for '{name}' submitted!\n\n"
        formatted += f" Molecule: {molecule}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {result.get('status', 'Submitted')}\n"
        formatted += f" Max Conformers: {max_conformers}\n"
        formatted += f"\n Use rowan_workflow_management tools to check progress and retrieve results\n"
    
    return formatted

def test_rowan_conformers():
    """Test the rowan_conformers function."""
    try:
        # Test with a simple molecule (non-blocking to avoid long wait)
        result = rowan_conformers("test_conformers", "CCO", max_conformers=5, blocking=False)
        print(" Conformers test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f" Conformers test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_conformers() 