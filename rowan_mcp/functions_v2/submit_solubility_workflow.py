"""
Rowan v2 API: Solubility Workflow
Predict molecular solubility in various solvents at different temperatures.
"""

from typing import Optional, List, Annotated, Union
from pydantic import Field
import rowan
import json


def submit_solubility_workflow(
    initial_smiles: Annotated[
        str,
        Field(description="SMILES string of the molecule for solubility prediction")
    ],
    solvents: Annotated[
        Optional[Union[str, List[str]]],
        Field(description="List of solvents as SMILES or names (e.g., ['water', 'ethanol', 'CCO']). Can be a JSON string or list. None uses defaults")
    ] = None,
    temperatures: Annotated[
        Optional[Union[str, List[float]]],
        Field(description="List of temperatures in Kelvin (e.g., [298.15, 310.15]). Can be a JSON string or list. None uses default range")
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
    
    # Parse solvents parameter - handle string or list
    if solvents is not None:
        if isinstance(solvents, str):
            # Handle various string formats
            solvents = solvents.strip()
            if solvents.startswith('[') and solvents.endswith(']'):
                # JSON array format like '["water", "ethanol"]'
                try:
                    solvents = json.loads(solvents)
                except (json.JSONDecodeError, ValueError):
                    # Failed to parse as JSON, try as comma-separated
                    solvents = solvents.strip('[]').replace('"', '').replace("'", "")
                    solvents = [s.strip() for s in solvents.split(',') if s.strip()]
            elif ',' in solvents:
                # Comma-separated format like 'water, ethanol'
                solvents = [s.strip() for s in solvents.split(',') if s.strip()]
            else:
                # Single solvent as string like 'water'
                solvents = [solvents]
    
    # Parse temperatures parameter - handle string or list
    if temperatures is not None:
        if isinstance(temperatures, str):
            # Handle various string formats
            temperatures = temperatures.strip()
            if temperatures.startswith('[') and temperatures.endswith(']'):
                # JSON array format like '[298.15, 310.15]'
                try:
                    temperatures = json.loads(temperatures)
                except (json.JSONDecodeError, ValueError):
                    # Failed to parse as JSON, try as comma-separated
                    temperatures = temperatures.strip('[]').replace('"', '').replace("'", "")
                    temperatures = [float(t.strip()) for t in temperatures.split(',') if t.strip()]
            elif ',' in temperatures:
                # Comma-separated format like '298.15, 310.15'
                temperatures = [float(t.strip()) for t in temperatures.split(',') if t.strip()]
            else:
                # Single temperature as string like '298.15'
                temperatures = [float(temperatures)]
    
    try:
        result = rowan.submit_solubility_workflow(
            initial_smiles=initial_smiles,
            solvents=solvents,
            temperatures=temperatures,
            name=name,
            folder_uuid=folder_uuid,
            max_credits=max_credits
        )
        
        return result
        
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise