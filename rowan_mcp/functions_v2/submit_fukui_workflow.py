"""
Rowan v2 API: Fukui Workflow
Calculate Fukui indices for reactivity analysis.
"""

from typing import Optional, Dict, Any
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_fukui_workflow(
    initial_molecule: str,
    optimization_method: str = "gfn2_xtb",
    fukui_method: str = "gfn1_xtb",
    solvent_settings: Optional[Dict[str, Any]] = None,
    name: str = "Fukui Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a Fukui indices calculation workflow using Rowan v2 API.
    
    Calculates Fukui indices to predict molecular reactivity at different sites.
    Fukui indices indicate susceptibility to nucleophilic/electrophilic attack.
    
    Args:
        initial_molecule: SMILES string or molecule object
        optimization_method: Method for geometry optimization (default: "gfn2_xtb")
            Common options: "gfn2_xtb", "r2scan_3c", "aimnet2_wb97md3"
        fukui_method: Method for Fukui calculation (default: "gfn1_xtb")
            Common options: "gfn1_xtb", "gfn2_xtb"
        solvent_settings: Optional solvent configuration dictionary
            Example: {"solvent": "water", "model": "alpb"}
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic Fukui indices
        result = submit_fukui_workflow(
            initial_molecule="CC(=O)O"
        )
        
        # With solvent and advanced methods
        result = submit_fukui_workflow(
            initial_molecule="c1ccccc1N",
            optimization_method="r2scan_3c",
            fukui_method="gfn2_xtb",
            solvent_settings={"solvent": "water", "model": "alpb"}
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Submit workflow
        workflow = rowan.submit_fukui_workflow(
            initial_molecule=initial_molecule,
            optimization_method=optimization_method,
            fukui_method=fukui_method,
            solvent_settings=solvent_settings,
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
                "optimization_method": optimization_method,
                "fukui_method": fukui_method,
                "solvent": solvent_settings.get("solvent", "gas phase") if solvent_settings else "gas phase"
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Fukui workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit Fukui workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"Fukui workflow submission failed: {str(e)}")
        return str(error_response)