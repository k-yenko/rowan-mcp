"""
Rowan v2 API: Tautomer Search Workflow
Search for tautomeric forms of molecules.
"""

from typing import Optional
import rowan


def submit_tautomer_search_workflow(
    initial_molecule: str,
    mode: str = "careful",
    name: str = "Tautomer Search Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a tautomer search workflow using Rowan v2 API.
    
    Searches for different tautomeric forms of a molecule and evaluates their
    relative stabilities. Tautomers are structural isomers that readily interconvert.
    
    Args:
        initial_molecule: SMILES string or molecule object
        mode: Search mode (default: "careful")
            Options: "rapid", "careful", "meticulous"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic tautomer search
        result = submit_tautomer_search_workflow(
            initial_molecule="CC(=O)CC(=O)C"
        )
        
        # Meticulous search for complex molecule
        result = submit_tautomer_search_workflow(
            initial_molecule="c1ccc2c(c1)ncc(=O)[nH]2",
            mode="meticulous"
        )
    """
    
    return rowan.submit_tautomer_search_workflow(
        initial_molecule=initial_molecule,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )