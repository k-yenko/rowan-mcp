"""
Rowan v2 API: Descriptors Workflow
Calculate molecular descriptors for QSAR and molecular analysis.
"""

from typing import Optional, Annotated
from pydantic import Field
import rowan


def submit_descriptors_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object for descriptor calculation")
    ],
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Descriptors Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a molecular descriptors calculation workflow using Rowan v2 API.
    
    Calculates a comprehensive set of molecular descriptors including:
    - Physical properties (MW, logP, TPSA, etc.)
    - Electronic properties (HOMO/LUMO, dipole moment, etc.)
    - Structural features (rotatable bonds, H-bond donors/acceptors, etc.)
    - Topological indices
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic descriptor calculation
        result = submit_descriptors_workflow(
            initial_molecule="CC(=O)Nc1ccc(O)cc1"
        )
        
        # For complex molecule
        result = submit_descriptors_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            name="Caffeine Descriptors"
        )
    """
    
    return rowan.submit_descriptors_workflow(
        initial_molecule=initial_molecule,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )