"""
Rowan v2 API: Fukui Workflow
Calculate Fukui indices for reactivity analysis.
"""

from typing import Dict, Any, Annotated
import rowan
import stjames
import json

def submit_fukui_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule to calculate Fukui indices for"],
    optimization_method: Annotated[str, "Method for geometry optimization (e.g., 'gfn2_xtb', 'uma_m_omol')"] = "gfn2_xtb",
    fukui_method: Annotated[str, "Method for Fukui indices calculation (e.g., 'gfn1_xtb', 'gfn2_xtb')"] = "gfn1_xtb",
    solvent_settings: Annotated[str, "JSON string for solvent settings. Empty string for vacuum"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Fukui Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a Fukui indices calculation workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string for Fukui analysis
        optimization_method: Method for geometry optimization. Options: 'gfn2_xtb', 'r2scan_3c', 'aimnet2_wb97md3'
        fukui_method: Method for Fukui calculation. Options: 'gfn1_xtb', 'gfn2_xtb'
        solvent_settings: Solvent configuration JSON string, e.g., '{"solvent": "water", "model": "alpb"}'. Empty for gas phase.
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
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
            solvent_settings='{"solvent": "water", "model": "alpb"}'
        )
    After submitting a workflow, use exponential backoff when checking status. Wait at least 10 seconds before the first check, 
    then double the wait time between subsequent checks (10s → 20s → 40s → 60s → 120s max). this workflow can take 10 minutes to complete.
    """
    # Parse solvent_settings if provided
    parsed_solvent_settings = None
    if solvent_settings:
        try:
            parsed_solvent_settings = json.loads(solvent_settings)
        except (json.JSONDecodeError, ValueError):
            pass
    
    try:
        # Convert initial_molecule to StJamesMolecule
        molecule = stjames.Molecule.from_smiles(initial_molecule)
        initial_molecule_dict = molecule.model_dump()
        
        # Create Settings objects
        optimization_settings = stjames.Settings(method=optimization_method)
        fukui_settings = stjames.Settings(method=fukui_method, solvent_settings=parsed_solvent_settings)
        
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
            "folder_uuid": folder_uuid if folder_uuid else None,
            "workflow_type": "fukui",
            "workflow_data": workflow_data,
            "initial_molecule": initial_molecule_dict,
            "max_credits": max_credits if max_credits > 0 else None,
        }

        # Submit to API
        with rowan.api_client() as client:
            response = client.post("/workflow", json=data)
            response.raise_for_status()
            result = rowan.Workflow(**response.json())

        # Make workflow publicly viewable
        result.update(public=True)

        return result
            
    except Exception as e:
        raise e