"""
Rowan v2 API: Basic Calculation Workflow
Submit basic quantum chemistry calculations with various methods and tasks.
"""

from typing import Optional, List, Dict, Any
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_basic_calculation_workflow(
    initial_molecule: str,
    method: str = "uma_m_omol",
    tasks: Optional[List[str]] = None,
    mode: str = "auto",
    engine: str = "omol25",
    name: str = "Basic Calculation Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a basic calculation workflow using Rowan v2 API.
    
    Performs fundamental quantum chemistry calculations with configurable methods
    and computational tasks.
    
    Args:
        initial_molecule: SMILES string or molecule object
        method: Computational method (default: "uma_m_omol")
            Common options: "uma_m_omol", "gfn2_xtb", "r2scan_3c", etc.
        tasks: List of calculation tasks to perform (e.g., ["energy", "gradient", "hessian"])
            If None, defaults to method-appropriate tasks
        mode: Calculation mode (default: "auto")
            Options: "auto", "rapid", "careful", "meticulous"
        engine: Computational engine (default: "omol25")
            Options: "omol25", "xtb", "psi4", etc.
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic energy calculation
        result = submit_basic_calculation_workflow(
            initial_molecule="CCO",
            method="gfn2_xtb",
            tasks=["energy"]
        )
        
        # Advanced calculation with multiple tasks
        result = submit_basic_calculation_workflow(
            initial_molecule="CC(=O)O",
            method="r2scan_3c",
            tasks=["energy", "gradient", "frequencies"],
            mode="careful"
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Submit workflow
        workflow = rowan.submit_basic_calculation_workflow(
            initial_molecule=initial_molecule,
            method=method,
            tasks=tasks,
            mode=mode,
            engine=engine,
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
                "method": method,
                "tasks": tasks or "default",
                "mode": mode,
                "engine": engine
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Basic calculation workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit basic calculation workflow: {str(e)}",
            "name": name,
            "molecule": initial_molecule
        }
        logger.error(f"Basic calculation workflow submission failed: {str(e)}")
        return str(error_response)