"""
Rowan v2 API: MacropKa Workflow
Calculate macroscopic pKa values across a pH range.
"""

from typing import Annotated
import rowan

def submit_macropka_workflow(
    initial_smiles: Annotated[str, "SMILES string of the molecule for macropKa calculation"],
    min_pH: Annotated[int, "Minimum pH value for the calculation range"] = 0,
    max_pH: Annotated[int, "Maximum pH value for the calculation range"] = 14,
    min_charge: Annotated[int, "Minimum molecular charge to consider"] = -2,
    max_charge: Annotated[int, "Maximum molecular charge to consider"] = 2,
    compute_solvation_energy: Annotated[bool, "Whether to compute solvation energy corrections"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Macropka Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a MacropKa workflow using Rowan v2 API.
    
    Args:
        initial_smiles: SMILES string of the molecule for macropKa calculation
        min_pH: Minimum pH value for the calculation range
        max_pH: Maximum pH value for the calculation range
        min_charge: Minimum molecular charge to consider
        max_charge: Maximum molecular charge to consider
        compute_solvation_energy: Whether to compute solvation energy for each species
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Calculates macroscopic pKa values across a pH range, determining the
    protonation states and their populations at different pH values.
    
    The workflow will:
    1. Identify all ionizable sites in the molecule
    2. Calculate microscopic pKa values for each site
    3. Determine macroscopic pKa values and species populations
    4. Optionally compute solvation energies
    
    Returns:
        Workflow object representing the submitted workflow
        
    Examples:
        # Simple molecule macropKa
        result = submit_macropka_workflow(
            initial_smiles="CC(=O)O",  # Acetic acid
            min_pH=0,
            max_pH=14
        )
        
        # Complex molecule with custom charge range
        result = submit_macropka_workflow(
            initial_smiles="CC(C)CC(C(=O)O)N",  # Leucine
            min_pH=0,
            max_pH=14,
            min_charge=-3,
            max_charge=3,
            compute_solvation_energy=True
        )
    """
    
    try:
        # Build workflow_data
        workflow_data = {
            "min_pH": min_pH,
            "max_pH": max_pH,
            "min_charge": min_charge,
            "max_charge": max_charge,
            "compute_solvation_energy": compute_solvation_energy,
        }
        
        # Build the API request
        data = {
            "name": name,
            "folder_uuid": folder_uuid,
            "workflow_type": "macropka",
            "workflow_data": workflow_data,
            "initial_smiles": initial_smiles,
            "max_credits": max_credits,
        }
        
        # Submit to API using rowan module
        return rowan.submit_macropka_workflow(
            initial_smiles=initial_smiles,
            min_pH=min_pH,
            max_pH=max_pH,
            min_charge=min_charge,
            max_charge=max_charge,
            compute_solvation_energy=compute_solvation_energy,
            name=name,
            folder_uuid=folder_uuid if folder_uuid else None,
            max_credits=max_credits if max_credits > 0 else None
        )
            
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise e