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
    name: Annotated[str, "Workflow name for identification and tracking"] = "Redox Potential Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a redox potential calculation workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string for redox potential calculation
        reduction: Whether to calculate reduction potential (gaining electron)
        oxidization: Whether to calculate oxidation potential (losing electron)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Calculates reduction and/or oxidation potentials for a molecule using
    quantum chemistry methods.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Benzoic acid redox potential
        result = submit_redox_potential_workflow(
            initial_molecule="C1=CC=C(C=C1)C(=O)O",
            oxidization=True,
            reduction=True,
            name="Benzoic Acid Redox Potential"
        )

    """
    
    result = rowan.submit_redox_potential_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        reduction=reduction,
        oxidization=oxidization,
        mode="rapid",
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result