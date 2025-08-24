"""
Rowan v2 API: MacropKa Workflow
Calculate macroscopic pKa values across a pH range.
"""

from typing import Optional, Annotated
from pydantic import Field
import rowan

def submit_macropka_workflow(
    initial_smiles: Annotated[
        str,
        Field(description="SMILES string of the molecule for macropKa calculation")
    ],
    min_pH: Annotated[
        int,
        Field(description="Minimum pH value for the calculation range")
    ] = 0,
    max_pH: Annotated[
        int,
        Field(description="Maximum pH value for the calculation range")
    ] = 14,
    min_charge: Annotated[
        int,
        Field(description="Minimum molecular charge to consider")
    ] = -2,
    max_charge: Annotated[
        int,
        Field(description="Maximum molecular charge to consider")
    ] = 2,
    compute_solvation_energy: Annotated[
        bool,
        Field(description="Whether to compute solvation energy for each species")
    ] = True,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Macropka Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a MacropKa workflow using Rowan v2 API.
    
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
        
        # Drug-like molecule
        result = submit_macropka_workflow(
            initial_smiles="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
            min_pH=2,
            max_pH=12,
            min_charge=-1,
            max_charge=1
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
            folder_uuid=folder_uuid,
            max_credits=max_credits
        )
            
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise e