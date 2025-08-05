"""
Rowan v2 API: Redox Potential Workflow
Calculate reduction and oxidation potentials for molecules.
"""

from typing import Optional, Annotated
from pydantic import Field
import rowan
import stjames


def submit_redox_potential_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object for redox potential calculation")
    ],
    reduction: Annotated[
        bool,
        Field(description="Whether to calculate reduction potential (gaining electron)")
    ] = False,
    oxidization: Annotated[
        bool,
        Field(description="Whether to calculate oxidation potential (losing electron)")
    ] = True,
    mode: Annotated[
        str,
        Field(description="Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)")
    ] = "rapid",
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Redox Potential Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a redox potential calculation workflow using Rowan v2 API.
    
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
        
        # Using a molecule dict from previous calculation
        molecule_dict = rowan.retrieve_calculation_molecules(conformer_uuid)[0]
        result = submit_redox_potential_workflow(
            initial_molecule=molecule_dict,  # Pass dict directly
            reduction=True,
            oxidization=True
        )
    """
    
    return rowan.submit_redox_potential_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        reduction=reduction,
        oxidization=oxidization,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )