"""
Rowan v2 API: Solubility Workflow
Predict molecular solubility in various solvents at different temperatures.
"""

from typing import Optional, List
import rowan


def submit_solubility_workflow(
    initial_smiles: str,
    solvents: Optional[List[str]] = None,
    temperatures: Optional[List[float]] = None,
    name: str = "Solubility Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
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
        Workflow object representing the submitted workflow
        
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
    
    return rowan.submit_solubility_workflow(
        initial_smiles=initial_smiles,
        solvents=solvents,
        temperatures=temperatures,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )