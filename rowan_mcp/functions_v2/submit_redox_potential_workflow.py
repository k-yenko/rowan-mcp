"""
Rowan v2 API: Redox Potential Workflow
Calculate reduction and oxidation potentials for molecules.
"""

from typing import Optional
import rowan


def submit_redox_potential_workflow(
    initial_molecule: str,
    reduction: bool = False,
    oxidization: bool = True,
    mode: str = "rapid",
    name: str = "Redox Potential Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a redox potential calculation workflow using Rowan v2 API.
    
    Calculates reduction and/or oxidation potentials for a molecule using
    quantum chemistry methods.
    
    Args:
        initial_molecule: SMILES string or molecule object
        reduction: Whether to calculate reduction potential (default: False)
        oxidization: Whether to calculate oxidation potential (default: True)
        mode: Calculation mode (default: "rapid")
            Options: "rapid", "careful", "meticulous"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic oxidation potential
        result = submit_redox_potential_workflow(
            initial_molecule="CC1=CC=CC=C1",
            oxidization=True
        )
        
        # Both reduction and oxidation with careful mode
        result = submit_redox_potential_workflow(
            initial_molecule="c1ccccc1",
            reduction=True,
            oxidization=True,
            mode="careful"
        )
    """
    
    return rowan.submit_redox_potential_workflow(
        initial_molecule=initial_molecule,
        reduction=reduction,
        oxidization=oxidization,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )