"""
Rowan v2 API: Protein Cofolding Workflow
Simulate protein-protein interactions and cofolding.
"""

from typing import Optional, List, Annotated, Union
from pydantic import Field
import rowan
import stjames
import json


def submit_protein_cofolding_workflow(
    initial_protein_sequences: Annotated[
        Union[str, List[str]],
        Field(description="List of protein sequences (amino acid strings) to cofold. Can be a JSON string or list")
    ],
    initial_smiles_list: Annotated[
        Optional[Union[str, List[str]]],
        Field(description="List of ligand SMILES strings to include in cofolding. Can be a JSON string or list. None for protein-only")
    ] = None,
    ligand_binding_affinity_index: Annotated[
        Optional[Union[str, int]],
        Field(description="Index of ligand in initial_smiles_list for binding affinity calculation (e.g., 0, '0'). None skips affinity")
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
    if isinstance(initial_protein_sequences, str):
        initial_protein_sequences = initial_protein_sequences.strip()
        if initial_protein_sequences.startswith('[') and initial_protein_sequences.endswith(']'):
            try:
                initial_protein_sequences = json.loads(initial_protein_sequences)
            except (json.JSONDecodeError, ValueError):
                initial_protein_sequences = initial_protein_sequences.strip('[]').replace('"', '').replace("'", "")
                initial_protein_sequences = [s.strip() for s in initial_protein_sequences.split(',') if s.strip()]
        elif ',' in initial_protein_sequences:
            initial_protein_sequences = [s.strip() for s in initial_protein_sequences.split(',') if s.strip()]
        else:
            initial_protein_sequences = [initial_protein_sequences]
    
    if initial_smiles_list is not None and isinstance(initial_smiles_list, str):
        initial_smiles_list = initial_smiles_list.strip()
        if initial_smiles_list.startswith('[') and initial_smiles_list.endswith(']'):
            try:
                initial_smiles_list = json.loads(initial_smiles_list)
            except (json.JSONDecodeError, ValueError):
                initial_smiles_list = initial_smiles_list.strip('[]').replace('"', '').replace("'", "")
                initial_smiles_list = [s.strip() for s in initial_smiles_list.split(',') if s.strip()]
        elif ',' in initial_smiles_list:
            initial_smiles_list = [s.strip() for s in initial_smiles_list.split(',') if s.strip()]
        else:
            initial_smiles_list = [initial_smiles_list]
    
    if ligand_binding_affinity_index is not None and isinstance(ligand_binding_affinity_index, str):
        try:
            ligand_binding_affinity_index = int(ligand_binding_affinity_index)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid ligand_binding_affinity_index: '{ligand_binding_affinity_index}' must be an integer")
    
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