"""
Rowan v2 API: Pose Analysis MD Workflow
Run molecular dynamics simulations on protein-ligand complexes from docking poses.
"""

from typing import Annotated
import rowan
import json


def submit_pose_analysis_md_workflow(
    protein: Annotated[str, "Protein UUID (36-char string) of existing protein. Use create_protein_from_pdb_id first if needed"],
    initial_smiles: Annotated[str, "SMILES string of the ligand molecule"],
    num_trajectories: Annotated[int, "Number of independent MD trajectories to run"] = 1,
    simulation_time_ns: Annotated[int, "Simulation time in nanoseconds for each trajectory"] = 10,
    ligand_residue_name: Annotated[str, "Residue name for the ligand in the protein structure"] = "LIG",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Pose-Analysis MD Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a pose analysis molecular dynamics workflow using Rowan v2 API.

    IMPORTANT: The protein parameter must be a UUID (36-character string) of an existing
    protein in your Rowan account. You cannot use PDB IDs directly. Use the
    create_protein_from_pdb_id tool first to create a protein, then use its UUID here.

    Args:
        protein: UUID of an existing protein (e.g., "abc123-def456-..."). Get this from
                 create_protein_from_pdb_id or from a previous workflow
        initial_smiles: SMILES string of the ligand molecule
        num_trajectories: Number of independent MD simulations to run (default: 1)
        simulation_time_ns: Simulation time in nanoseconds per trajectory (default: 10ns)
        ligand_residue_name: Residue name for the ligand in PDB structure (default: "LIG")
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Runs molecular dynamics simulations on protein-ligand complexes to:
    - Assess binding pose stability over time
    - Calculate binding free energies
    - Analyze protein-ligand interactions
    - Validate docking results with dynamics

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Step 1: First create a protein from PDB ID
        protein_obj = create_protein_from_pdb_id(
            name="CDK2 Protein",
            code="1HCK"
        )
        protein_uuid = protein_obj.uuid  # Get the UUID

        # Step 2: Run MD simulation with the protein UUID
        result = submit_pose_analysis_md_workflow(
            protein=protein_uuid,  # Use the UUID from step 1
            initial_smiles="CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1",
            num_trajectories=1,
            simulation_time_ns=10,
            name="CDK2 Ligand MD"
        )

        # Or use a protein UUID from list_proteins() output
        result = submit_pose_analysis_md_workflow(
            protein="550e8400-e29b-41d4-a716-446655440000",  # UUID format
            initial_smiles="CCO",
            num_trajectories=1,
            simulation_time_ns=5,
            name="Quick MD Validation"
        )

    This workflow can take 1-3 hours depending on simulation length.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Handle protein parameter - could be UUID or dict with PDB ID
    protein_obj = None

    # Try to parse protein as JSON first
    try:
        protein_dict = json.loads(protein)
        if isinstance(protein_dict, dict):
            protein = protein_dict
    except (json.JSONDecodeError, ValueError):
        # Not JSON, keep as string
        pass

    # Check if protein is a UUID (36 chars with dashes)
    if isinstance(protein, str):
        if len(protein) == 36 and '-' in protein:
            # It's a UUID, retrieve the protein
            logger.info(f"Using existing protein UUID: {protein}")
            protein_obj = rowan.retrieve_protein(protein)
        else:
            raise ValueError(f"Invalid protein parameter: {protein}. Expected protein UUID (36 chars)")
    else:
        # Assume it's already a protein object
        protein_obj = protein

    result = rowan.submit_pose_analysis_md_workflow(
        protein=protein_obj,
        initial_smiles=initial_smiles,
        num_trajectories=num_trajectories,
        simulation_time_ns=simulation_time_ns,
        ligand_residue_name=ligand_residue_name,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    logger.info(f"Pose Analysis MD workflow submitted with UUID: {result.uuid}")

    return result
