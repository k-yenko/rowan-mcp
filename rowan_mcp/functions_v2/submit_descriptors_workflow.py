"""
Rowan v2 API: Descriptors Workflow
Calculate molecular descriptors for QSAR and molecular analysis.
"""

from typing import Annotated
import rowan
import stjames


def submit_descriptors_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule to calculate descriptors for"],
    name: Annotated[str, "Workflow name for identification and tracking"] = "Descriptors Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a molecular descriptors calculation workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string or molecule object for descriptor calculation
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
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

    After submitting a workflow, use exponential backoff when checking status. Wait at least 10 seconds before the first check, 
    then double the wait time between subsequent checks (10s → 20s → 40s → 60s → 120s max). This workflow typically takes 10-30 seconds to complete.
    """
    
    result = rowan.submit_descriptors_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result