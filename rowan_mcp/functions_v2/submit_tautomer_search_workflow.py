"""
Rowan v2 API: Tautomer Search Workflow
Search for tautomeric forms of molecules.
"""

from typing import Optional
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_tautomer_search_workflow(
    initial_molecule: str,
    mode: str = "careful",
    name: str = "Tautomer Search Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a tautomer search workflow using Rowan v2 API.
    
    Searches for different tautomeric forms of a molecule and evaluates their
    relative stabilities. Tautomers are structural isomers that readily interconvert.
    
    Args:
        initial_molecule: SMILES string or molecule object
        mode: Search mode (default: "careful")
            Options: "rapid", "careful", "meticulous"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic tautomer search
        result = submit_tautomer_search_workflow(
            initial_molecule="CC(=O)CC(=O)C"
        )
        
        # Meticulous search for complex molecule
        result = submit_tautomer_search_workflow(
            initial_molecule="c1ccc2c(c1)ncc(=O)[nH]2",
            mode="meticulous"
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Submit workflow
        workflow = rowan.submit_tautomer_search_workflow(
            initial_molecule=initial_molecule,
            mode=mode,
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
            "search_details": {
                "mode": mode,
                "description": "Searching for tautomeric forms and evaluating relative stabilities"
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Tautomer search workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit tautomer search workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"Tautomer search workflow submission failed: {str(e)}")
        return str(error_response)