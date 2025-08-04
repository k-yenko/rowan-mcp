"""
Rowan v2 API: Solubility Workflow
Predict molecular solubility in various solvents at different temperatures.
"""

from typing import Optional, List, Annotated
from pydantic import Field
import rowan


def submit_solubility_workflow(
    initial_smiles: Annotated[
        str,
        Field(description="SMILES string of the molecule for solubility prediction")
    ],
    solvents: Annotated[
        Optional[List[str]],
        Field(description="List of solvents as SMILES or names (e.g., ['water', 'ethanol', 'CCO']). None uses defaults")
    ] = None,
    temperatures: Annotated[
        Optional[List[float]],
        Field(description="List of temperatures in Kelvin (e.g., [298.15, 310.15]). None uses default range")
    ] = None,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Solubility Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a solubility prediction workflow using Rowan v2 API.
    
    Predicts solubility (log S) of a molecule in multiple solvents at various temperatures
    using machine learning models.
    
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