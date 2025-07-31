"""
Rowan v2 API: Conformer Search Workflow
Search for low-energy molecular conformations using various methods.
"""

from typing import Optional
import rowan


def submit_conformer_search_workflow(
    initial_molecule: str,
    conf_gen_mode: str = "rapid",
    final_method: str = "aimnet2_wb97md3",
    solvent: Optional[str] = None,
    transition_state: bool = False,
    name: str = "Conformer Search Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a conformer search workflow using Rowan v2 API.
    
    Explores the conformational space of a molecule to find low-energy structures.
    
    Args:
        initial_molecule: SMILES string or molecule object
        conf_gen_mode: default to "rapid"
            Options: "rapid", "careful", "meticulous"
        final_method: default: "aimnet2_wb97md3"
            Try other options, if user specifies
        solvent: Optional solvent for implicit solvation (e.g., "water", "ethanol")
        transition_state: Whether searching for transition state conformers (default: False)
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic conformer search
        result = submit_conformer_search_workflow(
            initial_molecule="CCCC",
            conf_gen_mode="rapid"
        )
        
        # Careful search with solvent
        result = submit_conformer_search_workflow(
            initial_molecule="CC(C)CC(=O)O",
            conf_gen_mode="careful",
            solvent="water",
            final_method="r2scan_3c"
        )
    """
    
    return rowan.submit_conformer_search_workflow(
        initial_molecule=initial_molecule,
        conf_gen_mode=conf_gen_mode,
        final_method=final_method,
        solvent=solvent,
        transistion_state=transition_state,  # Note: API uses "transistion" (typo)
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )