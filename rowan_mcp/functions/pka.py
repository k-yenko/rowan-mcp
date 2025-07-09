"""
Calculate pKa values for molecules using Rowan API.
"""

import os
import rowan
from typing import Optional

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

def rowan_pka(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate pKa values for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        pKa calculation results
    """
    try:
        result = log_rowan_api_call(
            workflow_type="pka",
            name=name,
            molecule=molecule,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        # Format results based on whether we waited or not
        if blocking:
            # We waited for completion - format actual results
            status = result.get('status', result.get('object_status', 'Unknown'))
            
            if status == 2:  # Completed successfully
                formatted = f" pKa calculation for '{name}' completed successfully!\n\n"
            elif status == 3:  # Failed
                formatted = f" pKa calculation for '{name}' failed!\n\n"
            else:
                formatted = f" pKa calculation for '{name}' finished with status {status}\n\n"
                
            formatted += f" Molecule: {molecule}\n"
            formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
            formatted += f" Status: {status}\n"
            
            # Try to extract pKa results
            if isinstance(result, dict) and 'object_data' in result and result['object_data']:
                data = result['object_data']
                
                # Extract pKa values
                if 'strongest_acid' in data:
                    if data['strongest_acid'] is not None:
                        formatted += f" Strongest Acid pKa: {data['strongest_acid']:.2f}\n"
                    else:
                        formatted += f" Strongest Acid pKa: N/A (no acidic sites found)\n"
                        
                if 'strongest_base' in data:
                    if data['strongest_base'] is not None:
                        formatted += f" Strongest Base pKa: {data['strongest_base']:.2f}\n"
                    else:
                        formatted += f" Strongest Base pKa: N/A (no basic sites found)\n"
                if 'pka_values' in data and isinstance(data['pka_values'], list):
                    formatted += f" All pKa values: {', '.join([f'{val:.2f}' for val in data['pka_values']])}\n"
                
                # Additional properties if available
                if 'ionizable_sites' in data:
                    formatted += f" Ionizable sites found: {data['ionizable_sites']}\n"
            
            # Basic guidance
            if status == 2:
                formatted += f"\n Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
        else:
            # Non-blocking mode - just submission confirmation
            formatted = f" pKa calculation for '{name}' submitted!\n\n"
            formatted += f" Molecule: {molecule}\n"
            formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
            formatted += f" Status: {result.get('status', 'Submitted')}\n"
        
        return formatted
        
    except Exception as e:
        error_response = {
            "error": f"pKa calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)


def test_rowan_pka():
    """Test the rowan_pka function."""
    try:
        # Test with minimal parameters
        result = rowan_pka(
            name="test_pka_water",
            molecule="O"
        )
        print("✅ pKa test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"pKa test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_pka() 