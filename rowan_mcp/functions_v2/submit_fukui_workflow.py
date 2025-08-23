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
            pass
    
    try:
        # Convert initial_molecule to StJamesMolecule
        molecule = stjames.Molecule.from_smiles(initial_molecule)
        initial_molecule_dict = molecule.model_dump()
        
        # Create Settings objects
        optimization_settings = stjames.Settings(method=optimization_method)
        fukui_settings = stjames.Settings(method=fukui_method, solvent_settings=solvent_settings)
        
        # Serialize to dicts
        opt_settings_dict = optimization_settings.model_dump(mode="json")
        fukui_settings_dict = fukui_settings.model_dump(mode="json")
        
        # Fix soscf boolean to string enum conversion for optimization settings
        if 'scf_settings' in opt_settings_dict and 'soscf' in opt_settings_dict['scf_settings']:
            soscf_val = opt_settings_dict['scf_settings']['soscf']
            if isinstance(soscf_val, bool):
                if soscf_val is False:
                    opt_settings_dict['scf_settings']['soscf'] = 'never'
                elif soscf_val is True:
                    opt_settings_dict['scf_settings']['soscf'] = 'always'
        
        # Fix soscf boolean to string enum conversion for fukui settings
        if 'scf_settings' in fukui_settings_dict and 'soscf' in fukui_settings_dict['scf_settings']:
            soscf_val = fukui_settings_dict['scf_settings']['soscf']
            if isinstance(soscf_val, bool):
                if soscf_val is False:
                    fukui_settings_dict['scf_settings']['soscf'] = 'never'
                elif soscf_val is True:
                    fukui_settings_dict['scf_settings']['soscf'] = 'always'
        
        workflow_data = {
            "opt_settings": opt_settings_dict,
            "opt_engine": stjames.Method(optimization_method).default_engine(),
            "fukui_settings": fukui_settings_dict,
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
        
        # Submit to API
        with rowan.api_client() as client:
            response = client.post("/workflow", json=data)
            response.raise_for_status()
            return rowan.Workflow(**response.json())
            
    except Exception as e:
        raise e