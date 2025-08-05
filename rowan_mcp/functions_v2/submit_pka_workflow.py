"""
Rowan v2 API: pKa Workflow
Predict acid dissociation constants for ionizable groups in molecules.
"""

from typing import Optional, List, Tuple, Annotated, Union, Dict, Any
from pydantic import Field
import rowan
import json
import stjames

def submit_pka_workflow(
    initial_molecule: Annotated[
        Union[str, Dict[str, Any], Any],
        Field(description="The molecule to calculate the pKa of. Can be a SMILES string, dict, StJamesMolecule, or RdkitMol object")
    ],
    pka_range: Annotated[
        Tuple[float, float],
        Field(description="(min, max) pKa range to search, e.g., (2, 12)")
    ] = (2, 12),
    deprotonate_elements: Annotated[
        Optional[Union[str, List[int]]],
        Field(description="Atomic numbers to consider for deprotonation, e.g., [7, 8, 16] for N, O, S. Can be a JSON string '[7, 8, 16]' or list. None uses defaults")
    ] = None,
    protonate_elements: Annotated[
        Optional[Union[str, List[int]]],
        Field(description="Atomic numbers to consider for protonation, e.g., [7, 8] for N, O. Can be a JSON string '[7, 8]' or list. None uses defaults")
    ] = None,
    mode: Annotated[
        str,
        Field(description="Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)")
    ] = "careful",
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "pKa Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a pKa prediction workflow using Rowan v2 API.
    
    Predicts acid dissociation constants (pKa) for ionizable groups in a molecule
    using quantum chemistry calculations.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Examples:
        # p-nitrophenol pKa (from test)
        import stjames
        
        result = submit_pka_workflow(
            initial_molecule=stjames.Molecule.from_smiles("Oc1ccc(N(=O)=O)cc1"),
            name="pKa p-nitrophenol",
            deprotonate_elements=[8]  # Only consider oxygen
        )
        
        # Phenol pKa
        result = submit_pka_workflow(
            initial_molecule=stjames.Molecule.from_smiles("Oc1ccccc1"),
            name="pKa phenol",
            deprotonate_elements=[8]  # Atomic number for oxygen
        )
    """

    return rowan.submit_pka_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        pka_range=pka_range,
        deprotonate_elements=deprotonate_elements,
        protonate_elements=protonate_elements,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )