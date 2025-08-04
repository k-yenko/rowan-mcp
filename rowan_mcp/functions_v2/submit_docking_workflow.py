"""
Rowan v2 API: Docking Workflow
Perform molecular docking simulations for drug discovery.
"""

from typing import Optional, Dict, Any, Union, Annotated
from pydantic import Field
import rowan


def submit_docking_workflow(
    protein: Annotated[
        Union[str, Any],
        Field(description="Protein target for docking. Can be a protein UUID string or Protein object")
    ],
    pocket: Annotated[
        Any,
        Field(description="Binding pocket definition for the docking site")
    ],
    initial_molecule: Annotated[
        Optional[Union[Dict[str, Any], Any]],
        Field(description="Ligand molecule to dock. Can be dict with SMILES, StJamesMolecule, or RdkitMol object. None for blind docking")
    ] = None,
    do_csearch: Annotated[
        bool,
        Field(description="Whether to perform conformational search on the ligand before docking")
    ] = True,
    do_optimization: Annotated[
        bool,
        Field(description="Whether to optimize the ligand geometry before docking")
    ] = True,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Docking Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submits a Docking workflow to the API.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Dock a single ligand to CDK2 kinase (based on PDB 1HCK)
        import stjames
        
        # Create protein from PDB ID
        protein = rowan.create_protein_from_pdb_id("CDK2", "1HCK")
        protein.sanitize()
        
        # Define binding pocket (coordinates from active site)
        pocket = [[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]]
        
        # Submit docking for a single ligand
        ligand_smiles = "CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"
        result = submit_docking_workflow(
            protein=protein.uuid,
            pocket=pocket,
            initial_molecule=stjames.Molecule.from_smiles(ligand_smiles),
            do_csearch=True,
            do_optimization=True,
            name=f"Docking {ligand_smiles}"
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