"""
Rowan v2 API: Protein Cofolding Workflow
Simulate protein-protein interactions and cofolding.
"""

from typing import List, Annotated
import rowan
import stjames
import json


def submit_protein_cofolding_workflow(
    initial_protein_sequences: Annotated[str, "JSON string list of protein sequences for cofolding (e.g., '[\"MKLLV...\", \"MAHQR...\"]')"],
    initial_smiles_list: Annotated[str, "JSON string list of SMILES for ligands to include in cofolding (e.g., '[\"CCO\", \"CC(=O)O\"]'). Empty for protein-only"] = "",
    ligand_binding_affinity_index: Annotated[str, "JSON string mapping ligand indices to protein binding sites. Empty for automatic detection"] = "",
    use_msa_server: Annotated[bool, "Whether to use multiple sequence alignment server for better structure prediction"] = True,
    use_potentials: Annotated[bool, "Whether to include additional potentials in the calculation"] = False,
    compute_strain: Annotated[bool, "Whether to compute the strain of the pose (if pose_refinement is enabled)"] = False,
    do_pose_refinement: Annotated[bool, "Whether to optimize non-rotatable bonds in output poses"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Cofolding Workflow",
    model: Annotated[str, "Structure prediction model to use (e.g., 'boltz_2', 'alphafold3')"] = "boltz_2",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submits a protein cofolding workflow to the API.
    
    Args:
        initial_protein_sequences: JSON string list of protein sequences (amino acid strings) to cofold
        initial_smiles_list: JSON string list of ligand SMILES strings to include in cofolding. Empty string for protein-only
        ligand_binding_affinity_index: Index of ligand in initial_smiles_list for binding affinity calculation (e.g., "0"). Empty string skips affinity
        use_msa_server: Whether to use MSA (Multiple Sequence Alignment) server for improved accuracy
        use_potentials: Whether to use statistical potentials in the calculation
        name: Workflow name for identification and tracking
        model: Cofolding model to use (e.g., 'boltz_2', 'alphafold3')
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Protein-ligand cofolding with CDK2 kinase (from test)
        result = submit_protein_cofolding_workflow(
            initial_protein_sequences='["MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"]',
            initial_smiles_list='["CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"]',
            ligand_binding_affinity_index="0",
            name="Cofolding CDK2 with ligand"
        )
    After submitting a workflow, use exponential backoff when checking status. Wait at least 10 seconds before the first check, 
    then double the wait time between subsequent checks (10s → 20s → 40s → 60s → 120s max). This workflow can take 30 minutes to complete.
    """
    # Parse initial_protein_sequences (always a string in simplified version)
    try:
        initial_protein_sequences = json.loads(initial_protein_sequences)
    except (json.JSONDecodeError, ValueError):
        # Try to parse as comma-separated
        if ',' in initial_protein_sequences:
            initial_protein_sequences = [s.strip() for s in initial_protein_sequences.split(',') if s.strip()]
        else:
            initial_protein_sequences = [initial_protein_sequences.strip()]
    
    # Parse initial_smiles_list if provided
    parsed_initial_smiles_list = None
    if initial_smiles_list:
        try:
            parsed_initial_smiles_list = json.loads(initial_smiles_list)
        except (json.JSONDecodeError, ValueError):
            # Try to parse as comma-separated
            if ',' in initial_smiles_list:
                parsed_initial_smiles_list = [s.strip() for s in initial_smiles_list.split(',') if s.strip()]
            else:
                parsed_initial_smiles_list = [initial_smiles_list.strip()]
    
    # Parse ligand_binding_affinity_index if provided
    parsed_ligand_index = None
    if ligand_binding_affinity_index:
        try:
            parsed_ligand_index = int(ligand_binding_affinity_index)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid ligand_binding_affinity_index: '{ligand_binding_affinity_index}' must be an integer")
    
    result = rowan.submit_protein_cofolding_workflow(
        initial_protein_sequences=initial_protein_sequences,
        initial_smiles_list=parsed_initial_smiles_list,
        ligand_binding_affinity_index=parsed_ligand_index,
        use_msa_server=use_msa_server,
        use_potentials=use_potentials,
        compute_strain=compute_strain,
        do_pose_refinement=do_pose_refinement,
        name=name,
        model=model,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result