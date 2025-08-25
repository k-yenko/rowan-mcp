"""
Rowan v2 API: Tautomer Search Workflow
Search for tautomeric forms of molecules.
"""

from typing import Annotated
import rowan
import stjames

def submit_tautomer_search_workflow(
    initial_molecule: Annotated[str, "SMILES string to search for tautomers"],
    mode: Annotated[str, "Search mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)"] = "careful",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Tautomer Search Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a tautomer search workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string to search for tautomers
        mode: Search mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Searches for different tautomeric forms of a molecule and evaluates their
    relative stabilities. Tautomers are structural isomers that readily interconvert.
    
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
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        mode=mode,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )