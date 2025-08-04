"""
Rowan v2 API: Protein Cofolding Workflow
Simulate protein-protein interactions and cofolding.
"""

from typing import Optional, List, Annotated
from pydantic import Field
import rowan
import stjames


def submit_protein_cofolding_workflow(
    initial_protein_sequences: Annotated[
        List[str],
        Field(description="List of protein sequences (amino acid strings) to cofold")
    ],
    initial_smiles_list: Annotated[
        Optional[List[str]],
        Field(description="List of ligand SMILES strings to include in cofolding. None for protein-only")
    ] = None,
    ligand_binding_affinity_index: Annotated[
        Optional[int],
        Field(description="Index of ligand in initial_smiles_list for binding affinity calculation. None skips affinity")
    ] = None,
    use_msa_server: Annotated[
        bool,
        Field(description="Whether to use MSA (Multiple Sequence Alignment) server for improved accuracy")
    ] = True,
    use_potentials: Annotated[
        bool,
        Field(description="Whether to use statistical potentials in the calculation")
    ] = False,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Cofolding Workflow",
    model: Annotated[
        str,
        Field(description="Cofolding model to use (e.g., 'boltz_2', 'alphafold3')")
    ] = stjames.CofoldingModel.BOLTZ_2.value,
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submits a protein cofolding workflow to the API.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Protein-ligand cofolding with CDK2 kinase (from test)
        result = submit_protein_cofolding_workflow(
            initial_protein_sequences=[
                "MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"
            ],
            initial_smiles_list=["CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"],
            ligand_binding_affinity_index=0,
            name="Cofolding CDK2 with ligand"
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