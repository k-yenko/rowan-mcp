"""
Rowan v2 API: Fukui Workflow
Calculate Fukui indices for reactivity analysis.
"""

from typing import Optional, Dict, Any, Annotated, Union
from pydantic import Field
import rowan
import stjames
import json

def submit_fukui_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object for Fukui analysis")
    ],
    optimization_method: Annotated[
        str,
        Field(description="Method for geometry optimization. Options: 'gfn2_xtb', 'r2scan_3c', 'aimnet2_wb97md3'")
    ] = "gfn2_xtb",
    fukui_method: Annotated[
        str,
        Field(description="Method for Fukui calculation. Options: 'gfn1_xtb', 'gfn2_xtb'")
    ] = "gfn1_xtb",
    solvent_settings: Annotated[
        Optional[Union[str, Dict[str, Any]]],
        Field(description="Solvent configuration dict or JSON string, e.g., {'solvent': 'water', 'model': 'alpb'}. None for gas phase")
    ] = None,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Fukui Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a Fukui indices calculation workflow using Rowan v2 API.
    
    Calculates Fukui indices to predict molecular reactivity at different sites.
    Fukui indices indicate susceptibility to nucleophilic/electrophilic attack.
    
    Returns:
        Workflow object representing the submitted workflow
        
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
    
    # Parse solvent_settings if it's a string
    if solvent_settings is not None and isinstance(solvent_settings, str):
        try:
            solvent_settings = json.loads(solvent_settings)
        except (json.JSONDecodeError, ValueError):
            # If it's not valid JSON, keep it as is
            pass
    
    try:
        # Convert initial_molecule to StJamesMolecule
        if isinstance(initial_molecule, str):
            molecule = stjames.Molecule.from_smiles(initial_molecule)
        elif isinstance(initial_molecule, dict):
            molecule = stjames.Molecule(**initial_molecule)
        else:
            molecule = initial_molecule
            
        # Convert to dict for API payload
        if isinstance(molecule, stjames.Molecule):
            initial_molecule_dict = molecule.model_dump()
        else:
            initial_molecule_dict = molecule
        
        # Create Settings objects and immediately serialize them to JSON-compatible dicts
        # This is the workaround for the bug in rowan.submit_fukui_workflow
        optimization_settings = stjames.Settings(method=optimization_method)
        fukui_settings = stjames.Settings(method=fukui_method, solvent_settings=solvent_settings)
        
        # Use model_dump(mode="json") to ensure JSON serializability
        workflow_data = {
            "opt_settings": optimization_settings.model_dump(mode="json"),
            "opt_engine": stjames.Method(optimization_method).default_engine(),
            "fukui_settings": fukui_settings.model_dump(mode="json"),
            "fukui_engine": stjames.Method(fukui_method).default_engine(),
        }
        
        # Build the API request payload
        data = {
            "name": name,
            "folder_uuid": folder_uuid,
            "workflow_type": "fukui",
            "workflow_data": workflow_data,
            "initial_molecule": initial_molecule_dict,
            "max_credits": max_credits,
        }
        
        # Submit directly to the API, bypassing the buggy rowan.submit_fukui_workflow
        with rowan.api_client() as client:
            response = client.post("/workflow", json=data)
            response.raise_for_status()
            
            # Create and return a Workflow object from the response
            result = rowan.Workflow(**response.json())
            return result
            
    except Exception as e:
        raise e