"""
Rowan v2 API: pKa Workflow
Predict acid dissociation constants for ionizable groups in molecules.
"""

from typing import Optional, List, Tuple
import rowan


def submit_pka_workflow(
    initial_molecule: str,
    pka_range: Tuple[float, float] = (2, 12),
    deprotonate_elements: Optional[List[str]] = None,
    protonate_elements: Optional[List[str]] = None,
    mode: str = "careful",
    name: str = "pKa Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a pKa prediction workflow using Rowan v2 API.
    
    Predicts acid dissociation constants (pKa) for ionizable groups in a molecule
    using quantum chemistry calculations.
    
    Args:
        initial_molecule: SMILES string or molecule object
        pka_range: Tuple of (min, max) pKa values to search (default: (2, 12))
        deprotonate_elements: List of elements to consider for deprotonation
            (e.g., ["N", "O", "S"]). If None, uses defaults
        protonate_elements: List of elements to consider for protonation
            (e.g., ["N", "O"]). If None, uses defaults
        mode: Calculation mode (default: "careful")
            Options: "rapid", "careful", "meticulous"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic pKa prediction
        result = submit_pka_workflow(
            initial_molecule="CC(=O)O",
            pka_range=(2, 8)
        )
        
        # Specific elements with meticulous mode
        result = submit_pka_workflow(
            initial_molecule="NC(C)C(=O)O",
            pka_range=(1, 14),
            deprotonate_elements=["N", "O"],
            mode="meticulous"
        )
    """
    
    return rowan.submit_pka_workflow(
        initial_molecule=initial_molecule,
        pka_range=pka_range,
        deprotonate_elements=deprotonate_elements,
        protonate_elements=protonate_elements,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )