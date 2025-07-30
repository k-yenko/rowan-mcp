"""
Rowan v2 API: IRC Workflow
Perform Intrinsic Reaction Coordinate calculations to trace reaction paths.
"""

from typing import Optional, Dict, Any
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_irc_workflow(
    initial_molecule: str,
    transition_state_geometry: Optional[Dict[str, Any]] = None,
    forward_steps: int = 20,
    backward_steps: int = 20,
    step_size: float = 0.1,
    calculation_method: str = "gfn2_xtb",
    name: str = "IRC Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit an Intrinsic Reaction Coordinate (IRC) workflow using Rowan v2 API.
    
    Traces the minimum energy path from a transition state to reactants and products,
    confirming the reaction mechanism.
    
    Args:
        initial_molecule: SMILES string or molecule object (transition state)
        transition_state_geometry: Optional optimized TS geometry
            If not provided, will optimize the initial structure as TS
        forward_steps: Number of steps in forward direction (default: 20)
        backward_steps: Number of steps in backward direction (default: 20)
        step_size: IRC step size in mass-weighted coordinates (default: 0.1)
        calculation_method: Method for IRC calculation (default: "gfn2_xtb")
            Options: "gfn2_xtb", "r2scan_3c", "aimnet2_wb97md3"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic IRC from transition state
        result = submit_irc_workflow(
            initial_molecule="[CH3].[CH3]",
            forward_steps=30,
            backward_steps=30
        )
        
        # IRC with specific method
        result = submit_irc_workflow(
            initial_molecule="CC(O)=CC",
            calculation_method="r2scan_3c",
            step_size=0.05
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Prepare workflow parameters
        params = {
            "initial_molecule": initial_molecule,
            "name": name,
            "folder_uuid": folder_uuid,
            "max_credits": max_credits
        }
        
        # Add optional IRC-specific parameters
        if transition_state_geometry:
            params["transition_state_geometry"] = transition_state_geometry
        if forward_steps != 20:
            params["forward_steps"] = forward_steps
        if backward_steps != 20:
            params["backward_steps"] = backward_steps
        if step_size != 0.1:
            params["step_size"] = step_size
        if calculation_method != "gfn2_xtb":
            params["calculation_method"] = calculation_method
        
        # Submit workflow
        workflow = rowan.submit_irc_workflow(**params)
        
        # Format response
        response = {
            "success": True,
            "workflow_uuid": workflow.uuid,
            "name": name,
            "status": "submitted",
            "irc_details": {
                "forward_steps": forward_steps,
                "backward_steps": backward_steps,
                "step_size": step_size,
                "method": calculation_method,
                "description": "Tracing reaction path from transition state"
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"IRC workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit IRC workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"IRC workflow submission failed: {str(e)}")
        return str(error_response)