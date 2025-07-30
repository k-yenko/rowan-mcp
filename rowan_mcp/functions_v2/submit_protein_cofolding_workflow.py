"""
Rowan v2 API: Protein Cofolding Workflow
Simulate protein-protein interactions and cofolding.
"""

from typing import Optional, List, Dict, Any
import logging
import rowan

logger = logging.getLogger(__name__)


def submit_protein_cofolding_workflow(
    protein_sequences: List[str],
    prediction_method: str = "alphafold2",
    num_models: int = 5,
    relaxation: bool = True,
    msa_mode: str = "mmseqs2",
    name: str = "Protein Cofolding Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
) -> str:
    """Submit a protein cofolding workflow using Rowan v2 API.
    
    Predicts the 3D structure of protein complexes from amino acid sequences,
    simulating how multiple proteins fold together.
    
    Args:
        protein_sequences: List of protein sequences in single-letter amino acid code
            Each sequence represents one protein chain in the complex
        prediction_method: Structure prediction method (default: "alphafold2")
            Options: "alphafold2", "rosettafold", "esmfold"
        num_models: Number of structure models to generate (default: 5)
        relaxation: Whether to relax the predicted structures (default: True)
        msa_mode: Multiple sequence alignment mode (default: "mmseqs2")
            Options: "mmseqs2", "jackhmmer", "hhblits"
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        JSON string with workflow details including UUID for tracking
        
    Example:
        # Protein dimer prediction
        result = submit_protein_cofolding_workflow(
            protein_sequences=[
                "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEK",
                "MKQHKAMIVALIVICITAVVAALVTRKDLCEVHIRTGQTEVAVF"
            ],
            num_models=3
        )
        
        # Complex with multiple chains
        result = submit_protein_cofolding_workflow(
            protein_sequences=[
                "MGSSHHHHHHSSGLVPRGSH",
                "MASMTGGQQMGRGSEF",
                "MHHHHHHENLYFQG"
            ],
            prediction_method="alphafold2",
            relaxation=True
        )
    """
    
    try:
        # Get API key
        api_key = rowan.get_api_key()
        if not api_key:
            raise ValueError("ROWAN_API_KEY environment variable not set")
        
        # Validate inputs
        if not protein_sequences or len(protein_sequences) < 2:
            raise ValueError("At least 2 protein sequences required for cofolding")
        
        # Prepare workflow parameters
        params = {
            "protein_sequences": protein_sequences,
            "name": name,
            "folder_uuid": folder_uuid,
            "max_credits": max_credits
        }
        
        # Add optional parameters if different from defaults
        if prediction_method != "alphafold2":
            params["prediction_method"] = prediction_method
        if num_models != 5:
            params["num_models"] = num_models
        if not relaxation:
            params["relaxation"] = relaxation
        if msa_mode != "mmseqs2":
            params["msa_mode"] = msa_mode
        
        # Submit workflow
        workflow = rowan.submit_protein_cofolding_workflow(**params)
        
        # Format response
        response = {
            "success": True,
            "workflow_uuid": workflow.uuid,
            "name": name,
            "status": "submitted",
            "cofolding_details": {
                "num_chains": len(protein_sequences),
                "total_residues": sum(len(seq) for seq in protein_sequences),
                "method": prediction_method,
                "num_models": num_models,
                "relaxation": relaxation,
                "msa_mode": msa_mode
            },
            "tracking": {
                "workflow_uuid": workflow.uuid,
                "folder_uuid": folder_uuid
            }
        }
        
        logger.info(f"Protein cofolding workflow submitted: {workflow.uuid}")
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Failed to submit protein cofolding workflow: {str(e)}",
            "name": name,
            "num_sequences": len(protein_sequences) if protein_sequences else 0
        }
        logger.error(f"Protein cofolding workflow submission failed: {str(e)}")
        return str(error_response)