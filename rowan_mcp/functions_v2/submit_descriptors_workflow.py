"""
Rowan v2 API: Descriptors Workflow
Calculate molecular descriptors for QSAR and molecular analysis.
"""

from typing import Optional
import rowan


def submit_descriptors_workflow(
    initial_molecule: str,
    name: str = "Descriptors Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a molecular descriptors calculation workflow using Rowan v2 API.
    
    Calculates a comprehensive set of molecular descriptors including:
    - Physical properties (MW, logP, TPSA, etc.)
    - Electronic properties (HOMO/LUMO, dipole moment, etc.)
    - Structural features (rotatable bonds, H-bond donors/acceptors, etc.)
    - Topological indices
    
    Args:
        initial_molecule: SMILES string or molecule object
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
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