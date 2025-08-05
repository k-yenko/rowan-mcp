"""
Rowan v2 API: Tautomer Search Workflow
Search for tautomeric forms of molecules.
"""

from typing import Optional, Annotated
from pydantic import Field
import rowan
import stjames

def submit_tautomer_search_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object to search for tautomers")
    ],
    mode: Annotated[
        str,
        Field(description="Search mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)")
    ] = "careful",
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Tautomer Search Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a tautomer search workflow using Rowan v2 API.
    
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
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )