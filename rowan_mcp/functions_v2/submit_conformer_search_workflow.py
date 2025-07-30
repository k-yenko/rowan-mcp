"""
Rowan v2 API: Conformer Search Workflow
Search for low-energy molecular conformations using various methods.
"""

from typing import Optional
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_conformer_search_workflow(
    initial_molecule: str,
    conf_gen_mode: str = "rapid",
    final_method: str = "aimnet2_wb97md3",
    solvent: Optional[str] = None,
    transition_state: bool = False,
    name: str = "Conformer Search Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a conformer search workflow using Rowan v2 API.
    
    Explores the conformational space of a molecule to find low-energy structures.
    
    Args:
        initial_molecule: SMILES string or molecule object
        conf_gen_mode: Conformer generation mode (default: "rapid")
            Options: "rapid", "careful", "meticulous"
        final_method: Method for final energy evaluation (default: "aimnet2_wb97md3")
            Common options: "aimnet2_wb97md3", "gfn2_xtb", "r2scan_3c"
        solvent: Optional solvent for implicit solvation (e.g., "water", "ethanol")
        transition_state: Whether searching for transition state conformers (default: False)
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic conformer search
        result = submit_conformer_search_workflow(
            initial_molecule="CCCC",
            conf_gen_mode="rapid"
        )
        
        # Careful search with solvent
        result = submit_conformer_search_workflow(
            initial_molecule="CC(C)CC(=O)O",
            conf_gen_mode="careful",
            solvent="water",
            final_method="r2scan_3c"
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Submit workflow
        workflow = rowan.submit_conformer_search_workflow(
            initial_molecule=initial_molecule,
            conf_gen_mode=conf_gen_mode,
            final_method=final_method,
            solvent=solvent,
            transistion_state=transition_state,  # Note: API uses "transistion" (typo)
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
                "conf_gen_mode": conf_gen_mode,
                "final_method": final_method,
                "solvent": solvent or "gas phase",
                "transition_state": transition_state
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Conformer search workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit conformer search workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"Conformer search workflow submission failed: {str(e)}")
        return str(error_response)