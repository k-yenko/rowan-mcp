"""
Rowan v2 API: Redox Potential Workflow
Calculate reduction and oxidation potentials for molecules.
"""

from typing import Optional
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_redox_potential_workflow(
    initial_molecule: str,
    reduction: bool = False,
    oxidization: bool = True,
    mode: str = "rapid",
    name: str = "Redox Potential Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a redox potential calculation workflow using Rowan v2 API.
    
    Calculates reduction and/or oxidation potentials for a molecule using
    quantum chemistry methods.
    
    Args:
        initial_molecule: SMILES string or molecule object
        reduction: Whether to calculate reduction potential (default: False)
        oxidization: Whether to calculate oxidation potential (default: True)
        mode: Calculation mode (default: "rapid")
            Options: "rapid", "careful", "meticulous"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic oxidation potential
        result = submit_redox_potential_workflow(
            initial_molecule="CC1=CC=CC=C1",
            oxidization=True
        )
        
        # Both reduction and oxidation with careful mode
        result = submit_redox_potential_workflow(
            initial_molecule="c1ccccc1",
            reduction=True,
            oxidization=True,
            mode="careful"
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Validate that at least one potential is requested
        if not reduction and not oxidization:
            raise ValueError("At least one of reduction or oxidization must be True")
        
        # Submit workflow
        workflow = rowan.submit_redox_potential_workflow(
            initial_molecule=initial_molecule,
            reduction=reduction,
            oxidization=oxidization,
            mode=mode,
            name=name,
            folder_uuid=folder_uuid,
            max_credits=max_credits
        )
        
        # Format response
        potentials_calculated = []
        if reduction:
            potentials_calculated.append("reduction")
        if oxidization:
            potentials_calculated.append("oxidation")
            
        response = {
            "success": True,
            "workflow_uuid": workflow.uuid,
            "name": name,
            "status": "submitted",
            "calculation_details": {
                "potentials": potentials_calculated,
                "mode": mode
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Redox potential workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit redox potential workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"Redox potential workflow submission failed: {str(e)}")
        return str(error_response)