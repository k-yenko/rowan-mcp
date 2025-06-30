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
    """Log Rowan API calls with detailed parameters."""
    try:
        logger.info(f"🚀 Rowan API Call: {workflow_type}")
        for key, value in kwargs.items():
            if key != 'folder_uuid':  # Don't log folder UUIDs as they're not that useful
                logger.info(f"   {key}: {value}")
        
        # Create and execute the workflow
        workflow_class = getattr(rowan, f"{workflow_type.title().replace('_', '')}Workflow")
        workflow = workflow_class(**kwargs)
        result = workflow.submit()
        
        logger.info(f"Workflow submitted successfully: {result.get('uuid', 'N/A')}")
        return result
        
    except Exception as e:
        logger.error(f"Rowan API call failed: {str(e)}")
        error_response = {
            "error": str(e),
            "workflow_type": workflow_type,
            "parameters": kwargs
        }
        return error_response

def rowan_pka(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None
) -> str:
    """Calculate pKa values for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: UUID of folder to organize calculation in
    
    Returns:
        pKa calculation results
    """
    try:
        result = log_rowan_api_call(
            workflow_type="pka",
            name=name,
            molecule=molecule,
            folder_uuid=folder_uuid
        )
        
        # Handle error case
        if "error" in result:
            error_response = {
                "error": f"Failed to submit pKa calculation: {result['error']}",
                "name": name,
                "molecule": molecule
            }
            return str(error_response)
        
        pka_value = result.get("object_data", {}).get("strongest_acid")
        
        formatted = f"pKa calculation for '{name}' completed!\n\n"
        formatted += f"Molecule: {molecule}\n"
        formatted += f"Job UUID: {result.get('uuid', 'N/A')}\n"
        
        if pka_value is not None:
            formatted += f"Strongest Acid pKa: {pka_value:.2f}\n"
        else:
            formatted += "pKa result not yet available\n"
            
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