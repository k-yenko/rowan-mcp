"""
Rowan v2 API: Redox Potential Workflow
Calculate reduction and oxidation potentials for molecules.
"""

from typing import Annotated
import rowan
import stjames


def submit_redox_potential_workflow(
    initial_molecule: Annotated[str, "SMILES string for redox potential calculation"],
    reduction: Annotated[bool, "Whether to calculate reduction potential (gaining electron)"] = False,
    oxidization: Annotated[bool, "Whether to calculate oxidation potential (losing electron)"] = True,
    mode: Annotated[str, "Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)"] = "rapid",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Redox Potential Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a redox potential calculation workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string for redox potential calculation
        reduction: Whether to calculate reduction potential (gaining electron)
        oxidization: Whether to calculate oxidation potential (losing electron)
        mode: Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Calculates reduction and/or oxidation potentials for a molecule using
    quantum chemistry methods.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Simple redox potential from SMILES
        result = submit_redox_potential_workflow(
            initial_molecule="Cc1ccccc1",  # Toluene
            reduction=True,
            oxidization=True,
            name="Toluene Redox Potential"
        )
    """
    
    return rowan.submit_redox_potential_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        reduction=reduction,
        oxidization=oxidization,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )