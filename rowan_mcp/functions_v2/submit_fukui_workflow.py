"""
Rowan v2 API: Fukui Workflow
Calculate Fukui indices for reactivity analysis.
"""

from typing import Optional, Dict, Any
import rowan


def submit_fukui_workflow(
    initial_molecule: str,
    optimization_method: str = "gfn2_xtb",
    fukui_method: str = "gfn1_xtb",
    solvent_settings: Optional[Dict[str, Any]] = None,
    name: str = "Fukui Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a Fukui indices calculation workflow using Rowan v2 API.
    
    Calculates Fukui indices to predict molecular reactivity at different sites.
    Fukui indices indicate susceptibility to nucleophilic/electrophilic attack.
    
    Args:
        initial_molecule: SMILES string or molecule object
        optimization_method: Method for geometry optimization (default: "gfn2_xtb")
            Common options: "gfn2_xtb", "r2scan_3c", "aimnet2_wb97md3"
        fukui_method: Method for Fukui calculation (default: "gfn1_xtb")
            Common options: "gfn1_xtb", "gfn2_xtb"
        solvent_settings: Optional solvent configuration dictionary
            Example: {"solvent": "water", "model": "alpb"}
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
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