"""
Rowan v2 API: Solubility Workflow
Predict molecular solubility in various solvents at different temperatures.
"""

from typing import Optional, List, Union
import logging
import rowan

logger = logging.getLogger(__name__)

# Solvent name to SMILES mapping
SOLVENT_SMILES = {
    "water": "O",
    "ethanol": "CCO",
    "methanol": "CO",
    "hexane": "CCCCCC",
    "toluene": "CC1=CC=CC=C1",
    "thf": "C1CCCO1",
    "tetrahydrofuran": "C1CCCO1",
    "ethyl_acetate": "CC(=O)OCC",
    "acetonitrile": "CC#N",
    "dmso": "CS(=O)C",
    "acetone": "CC(=O)C",
    "propanone": "CC(=O)C",
    "chloroform": "ClCCl",
    "dichloromethane": "ClCCl"
}


def convert_solvent_names_to_smiles(solvents: List[str]) -> List[str]:
    """Convert common solvent names to SMILES strings."""
    converted = []
    for solvent in solvents:
        # If it's already a SMILES, keep as is
        if any(char in solvent for char in ['=', '#', '(', ')', '[', ']']):
            converted.append(solvent)
        else:
            # Try to convert from name to SMILES
            solvent_lower = solvent.lower().replace(' ', '_')
            converted.append(SOLVENT_SMILES.get(solvent_lower, solvent))
    return converted


def submit_solubility_workflow(
    initial_smiles: str,
    solvents: Optional[List[str]] = None,
    temperatures: Optional[List[float]] = None,
    name: str = "Solubility Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a solubility prediction workflow using Rowan v2 API.
    
    Predicts solubility (log S) of a molecule in multiple solvents at various temperatures
    using machine learning models.
    
    Args:
        initial_smiles: SMILES string of the molecule
        solvents: List of solvents as SMILES or common names (e.g., ["water", "ethanol"])
            If None, uses default solvents
        temperatures: List of temperatures in Kelvin
            If None, uses default temperature range
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic solubility prediction
        result = submit_solubility_workflow(
            initial_smiles="CC(=O)Nc1ccc(O)cc1",
            solvents=["water", "ethanol"],
            temperatures=[298.15, 310.15]
        )
        
        # With SMILES solvents
        result = submit_solubility_workflow(
            initial_smiles="CC(=O)O",
            solvents=["O", "CCO", "CCCCCC"],
            temperatures=[273.15, 298.15, 323.15]
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Convert solvent names to SMILES if needed
        if solvents is not None:
            solvents = convert_solvent_names_to_smiles(solvents)
        
        # Submit workflow
        workflow = rowan.submit_solubility_workflow(
            initial_smiles=initial_smiles,
            solvents=solvents,
            temperatures=temperatures,
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
            "prediction_details": {
                "molecule": initial_smiles,
                "solvents_count": len(solvents) if solvents else "default",
                "temperatures_count": len(temperatures) if temperatures else "default"
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Solubility workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit solubility workflow: {str(e)}",
            "name": name,
            "molecule": initial_smiles
        }
        logger.error(f"Solubility workflow submission failed: {str(e)}")
        return str(error_response)