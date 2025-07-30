"""
Rowan v2 API: Descriptors Workflow
Calculate molecular descriptors for QSAR and molecular analysis.
"""

from typing import Optional
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_descriptors_workflow(
    initial_molecule: str,
    name: str = "Descriptors Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a molecular descriptors calculation workflow using Rowan v2 API.
    
    Calculates a comprehensive set of molecular descriptors including:
    - Physical properties (MW, logP, TPSA, etc.)
    - Electronic properties (HOMO/LUMO, dipole moment, etc.)
    - Structural features (rotatable bonds, H-bond donors/acceptors, etc.)
    - Topological indices
    
    Args:
        initial_molecule: SMILES string or molecule object
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic descriptor calculation
        result = submit_descriptors_workflow(
            initial_molecule="CC(=O)Nc1ccc(O)cc1"
        )
        
        # For complex molecule
        result = submit_descriptors_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            name="Caffeine Descriptors"
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Submit workflow
        workflow = rowan.submit_descriptors_workflow(
            initial_molecule=initial_molecule,
            name=name,
            folder_uuid=folder_uuid,
            max_credits=max_credits
        )
        
        # Format response
        response = {
            "success": True,
            "workflow_uuid": workflow.uuid,
            "name": name,
            "status": "submitted",
            "calculation_details": {
                "description": "Calculating comprehensive molecular descriptors",
                "categories": [
                    "Physical properties",
                    "Electronic properties",
                    "Structural features",
                    "Topological indices"
                ]
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Descriptors workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit descriptors workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"Descriptors workflow submission failed: {str(e)}")
        return str(error_response)