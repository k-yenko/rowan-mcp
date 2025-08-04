"""
Rowan v2 API: Fukui Workflow
Calculate Fukui indices for reactivity analysis.
"""

from typing import Optional, Dict, Any, Annotated
from pydantic import Field
import rowan


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
        Optional[Dict[str, Any]],
        Field(description="Solvent configuration dict, e.g., {'solvent': 'water', 'model': 'alpb'}. None for gas phase")
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
    
    return rowan.submit_fukui_workflow(
        initial_molecule=initial_molecule,
        optimization_method=optimization_method,
        fukui_method=fukui_method,
        solvent_settings=solvent_settings,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )