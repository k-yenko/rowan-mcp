"""
Rowan v2 API: Docking Workflow
Perform molecular docking simulations for drug discovery.
"""

from typing import Optional, Dict, Any, Union, Annotated, List, Tuple
from pydantic import Field
import rowan
import stjames
import json

def submit_docking_workflow(
    protein: Annotated[
        Union[str, Any],
        Field(description="Protein target for docking. Can be a protein UUID string or Protein object. IMPORTANT: Protein must be sanitized first using protein.sanitize()")
    ],
    pocket: Annotated[
        Union[str, List[List[float]]],
        Field(description="Binding pocket as [[x1,y1,z1], [x2,y2,z2]] or JSON string. Defines box corners for docking site")
    ],
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object representing the ligand")
    ],
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
    ] = None,
    blocking: Annotated[
        bool,
        Field(description="Whether to wait for workflow completion before returning")
    ] = False
):
    """Submits a Docking workflow to the API.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Dock a single ligand to CDK2 kinase (based on PDB 1HCK)
        # Create protein from PDB ID 
        # Use the create_protein_from_pdb_id mcp tool to create a protein object
        protein = rowan.create_protein_from_pdb_id("CDK2", "1HCK")
        protein.sanitize()
        
        # Define binding pocket (coordinates from active site)
        pocket = [[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]]
        
        # Submit docking for a single ligand
        ligand_smiles = "CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"
        result = submit_docking_workflow(
            protein=protein.uuid,
            pocket=pocket,
            initial_molecule=ligand_smiles,  # Can pass SMILES directly
            do_csearch=True,
            do_optimization=True,
            name=f"Docking {ligand_smiles}"
        )
    """
    # Parse pocket parameter if it's a string
    if isinstance(pocket, str):
        try:
            pocket = json.loads(pocket)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid pocket format: {pocket}. Expected [[x1,y1,z1], [x2,y2,z2]] or valid JSON string")
    
    # Ensure pocket is a list of lists
    if not isinstance(pocket, list) or len(pocket) != 2:
        raise ValueError(f"Pocket must be a list with exactly 2 coordinate lists")
    
    # Ensure each element is a list of floats
    pocket = [list(coord) for coord in pocket]

    
    # Submit the workflow - let Rowan API handle protein UUID/object conversion
    workflow = rowan.submit_docking_workflow(
        protein=protein,
        pocket=pocket,
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        do_csearch=do_csearch,
        do_optimization=do_optimization,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )
    
    # If blocking, wait for completion
    if blocking:
        workflow.wait_for_result()
    
    return workflow