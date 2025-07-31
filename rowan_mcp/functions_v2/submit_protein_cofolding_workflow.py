"""
Rowan v2 API: Protein Cofolding Workflow
Simulate protein-protein interactions and cofolding.
"""

from typing import Optional, List
import rowan
import stjames


def submit_protein_cofolding_workflow(
    initial_protein_sequences: List[str],
    initial_smiles_list: Optional[List[str]] = None,
    ligand_binding_affinity_index: Optional[int] = None,
    use_msa_server: bool = True,
    use_potentials: bool = False,
    name: str = "Cofolding Workflow",
    model: str = stjames.CofoldingModel.BOLTZ_2.value,
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submits a protein cofolding workflow to the API.
    
    Args:
        initial_protein_sequences: The sequences of the proteins to be cofolded
        initial_smiles_list: A list of SMILES strings for the ligands to be cofolded with
        ligand_binding_affinity_index: The index of the ligand for which to compute the binding affinity
        use_msa_server: Whether to use the MSA server for the computation
        use_potentials: Whether to use potentials for the computation
        name: The name of the workflow
        model: The model to use for the computation
        folder_uuid: The UUID of the folder to store the workflow in
        max_credits: The maximum number of credits to use for the workflow
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Protein dimer cofolding
        result = submit_protein_cofolding_workflow(
            initial_protein_sequences=[
                "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEK",
                "MKQHKAMIVALIVICITAVVAALVTRKDLCEVHIRTGQTEVAVF"
            ]
        )
        
        # Protein-ligand complex
        result = submit_protein_cofolding_workflow(
            initial_protein_sequences=["MGSSHHHHHHSSGLVPRGSH"],
            initial_smiles_list=["CC(=O)O", "CCO"],
            ligand_binding_affinity_index=0,
            use_msa_server=True
        )
    """
    
    return rowan.submit_protein_cofolding_workflow(
        initial_protein_sequences=initial_protein_sequences,
        initial_smiles_list=initial_smiles_list,
        ligand_binding_affinity_index=ligand_binding_affinity_index,
        use_msa_server=use_msa_server,
        use_potentials=use_potentials,
        name=name,
        model=model,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )