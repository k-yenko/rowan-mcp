"""
Rowan v2 API: Docking Workflow
Perform molecular docking simulations for drug discovery.
"""

from typing import Optional, List, Dict, Any, Union
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_docking_workflow(
    ligand_smiles: Union[str, List[str]],
    protein_pdb: str,
    binding_site: Optional[Dict[str, Any]] = None,
    num_poses: int = 10,
    exhaustiveness: int = 8,
    scoring_function: str = "vina",
    flexible_residues: Optional[List[str]] = None,
    name: str = "Docking Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a molecular docking workflow using Rowan v2 API.
    
    Performs protein-ligand docking to predict binding modes and affinities
    for drug discovery applications.
    
    Args:
        ligand_smiles: SMILES string or list of SMILES for ligands to dock
        protein_pdb: PDB ID (e.g., "1A2B") or PDB file content as string
        binding_site: Optional binding site definition
            Example: {
                "center": [10.5, 20.3, 15.2],  # x, y, z coordinates
                "size": [20, 20, 20]  # box dimensions
            }
            If not provided, will attempt automatic cavity detection
        num_poses: Number of binding poses to generate (default: 10)
        exhaustiveness: Search exhaustiveness (default: 8, higher = more thorough)
        scoring_function: Scoring function to use (default: "vina")
            Options: "vina", "vinardo", "ad4"
        flexible_residues: List of flexible residue IDs (e.g., ["ASP125", "TYR308"])
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Basic docking with PDB ID
        result = submit_docking_workflow(
            ligand_smiles="CC(=O)Oc1ccccc1C(=O)O",
            protein_pdb="1OXR",
            num_poses=5
        )
        
        # Multiple ligands with defined binding site
        result = submit_docking_workflow(
            ligand_smiles=["CCO", "CC(=O)O", "c1ccccc1"],
            protein_pdb="2VCJ",
            binding_site={
                "center": [15.0, 25.0, 30.0],
                "size": [25, 25, 25]
            },
            exhaustiveness=16
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Ensure ligand_smiles is a list
        if isinstance(ligand_smiles, str):
            ligand_smiles = [ligand_smiles]
        
        # Prepare workflow parameters
        params = {
            "ligand_smiles": ligand_smiles,
            "protein_pdb": protein_pdb,
            "name": name,
            "folder_uuid": folder_uuid,
            "max_credits": max_credits
        }
        
        # Add optional parameters if different from defaults
        if binding_site:
            params["binding_site"] = binding_site
        if num_poses != 10:
            params["num_poses"] = num_poses
        if exhaustiveness != 8:
            params["exhaustiveness"] = exhaustiveness
        if scoring_function != "vina":
            params["scoring_function"] = scoring_function
        if flexible_residues:
            params["flexible_residues"] = flexible_residues
        
        # Submit workflow
        workflow = rowan.submit_docking_workflow(**params)
        
        # Format response
        is_pdb_id = len(protein_pdb) == 4 and protein_pdb.isalnum()
        response = {
            "success": True,
            "workflow_uuid": workflow.uuid,
            "name": name,
            "status": "submitted",
            "docking_details": {
                "num_ligands": len(ligand_smiles),
                "protein": f"PDB {protein_pdb}" if is_pdb_id else "custom structure",
                "num_poses": num_poses,
                "exhaustiveness": exhaustiveness,
                "scoring_function": scoring_function,
                "binding_site": "automatic detection" if not binding_site else "user-defined",
                "flexible_residues": len(flexible_residues) if flexible_residues else 0
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Docking workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit docking workflow: {str(e)}",
            "name": name,
            "ligands": ligand_smiles if isinstance(ligand_smiles, list) else [ligand_smiles]
        }
        logger.error(f"Docking workflow submission failed: {str(e)}")
        return str(error_response)