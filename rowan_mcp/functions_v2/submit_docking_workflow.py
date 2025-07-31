"""
Rowan v2 API: Docking Workflow
Perform molecular docking simulations for drug discovery.
"""

from typing import Optional, Dict, Any, Union
import rowan


def submit_docking_workflow(
    protein: Union[str, Any],
    pocket: Any,
    initial_molecule: Optional[Union[Dict[str, Any], Any]] = None,
    do_csearch: bool = True,
    do_optimization: bool = True,
    name: str = "Docking Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submits a Docking workflow to the API.
    
    Args:
        protein: The protein to dock. Can be fed as a uuid or a Protein object
        pocket: The pocket to dock into
        initial_molecule: The initial molecule to be docked.
            Can be a dict, StJamesMolecule, or RdkitMol object
        do_csearch: Whether to perform a conformational search on the ligand
        do_optimization: Whether to perform an optimization on the ligand
        name: The name of the workflow
        folder_uuid: The UUID of the folder to place the workflow in
        max_credits: The maximum number of credits to use for the workflow
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic docking with protein UUID
        result = submit_docking_workflow(
            protein="protein-uuid-123",
            pocket=pocket_obj,
            initial_molecule={"smiles": "CC(=O)Oc1ccccc1C(=O)O"}
        )
        
        # Docking with optimization disabled
        result = submit_docking_workflow(
            protein=protein_obj,
            pocket=pocket_obj,
            initial_molecule={"smiles": "CCO"},
            do_csearch=False,
            do_optimization=False
        )
    """
    
    return rowan.submit_docking_workflow(
        protein=protein,
        pocket=pocket,
        initial_molecule=initial_molecule,
        do_csearch=do_csearch,
        do_optimization=do_optimization,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )