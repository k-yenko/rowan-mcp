"""
Rowan docking function for MCP tool integration.
Implements protein-ligand docking following the stjames-public workflow pattern.
"""

from typing import Optional, Union, List, Tuple, Dict, Any
import rowan
import logging
import os
import requests

# Set up logging
logger = logging.getLogger(__name__)

# Get API key from environment
api_key = os.environ.get("ROWAN_API_KEY")
if api_key:
    rowan.api_key = api_key
else:
    logger.warning("ROWAN_API_KEY not found in environment")

def fetch_pdb_content(pdb_id: str) -> Optional[str]:
    """Fetch PDB content from RCSB PDB database.
    
    Args:
        pdb_id: 4-character PDB ID (e.g., "1COX")
        
    Returns:
        PDB file content as string, or None if fetch fails
    """
    try:
        url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Failed to fetch PDB {pdb_id}: {str(e)}")
        return None

def rowan_docking(
    name: str,
    # Ligand specification (following stjames priority)
    molecules: Optional[List[str]] = None,
    smiles: Optional[Union[str, List[str]]] = None,
    # Protein specification  
    target: Optional[str] = None,
    target_uuid: Optional[str] = None,
    # Pocket specification
    pocket: Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]] = None,
    # Workflow parameters
    do_csearch: bool = True,
    do_optimization: bool = True,
    do_pose_refinement: bool = True,
    conformers: Optional[List[str]] = None,
    # MCP workflow parameters
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Perform protein-ligand docking using Rowan's ML workflow.
    
    Performs comprehensive protein-ligand docking with conformer generation,
    strain filtering, AutoDock Vina docking, and pose refinement.
    
    IMPORTANT: For docking, you need to provide the protein target in one of two ways:
    1. target_uuid: UUID of a pre-uploaded protein in your Rowan account
    2. target: Reserved for future use (currently not supported via API)
    
    To dock against a known protein like 1COX, you should:
    1. Upload the PDB file to your Rowan account via the web interface
    2. Get the protein UUID from your account
    3. Use that UUID with the target_uuid parameter
    
    Args:
        name: Name for the docking calculation
        molecules: List of molecules to dock (SMILES strings)
        smiles: SMILES string(s) of ligands (can be string or list)
        target: Not currently supported - use target_uuid instead
        target_uuid: UUID of pre-uploaded protein target from your Rowan account
        pocket: Tuple of (center, size) where each is (x, y, z) coordinates
                Example: ((10.0, 15.0, 20.0), (20.0, 20.0, 20.0))
        do_csearch: Whether to perform conformer search (default: True)
        do_optimization: Whether to optimize starting structures (default: True)
        do_pose_refinement: Whether to optimize non-rotatable bonds in output poses (default: True)
        conformers: List of pre-optimized conformer UUIDs (optional)
        folder_uuid: Optional folder UUID to organize the calculation
        blocking: Whether to wait for completion (default: True)
        ping_interval: Interval in seconds to check calculation status
        
    Returns:
        Formatted string with workflow results or submission confirmation
        
    Examples:
        # Using pre-uploaded protein
        rowan_docking(
            name="aspirin_docking",
            smiles="CC(=O)Oc1ccccc1C(=O)O",
            target_uuid="your-protein-uuid-here",
            pocket=((10.0, 15.0, 20.0), (20.0, 20.0, 20.0))
        )
        
        # Multiple molecules
        rowan_docking(
            name="multi_ligand_docking",
            molecules=["CCO", "CC(C)O", "CCCO"],
            target_uuid="your-protein-uuid-here",
            pocket=((0.0, 0.0, 0.0), (25.0, 25.0, 25.0))
        )
    """
    
    # Validate that we have ligand input
    if molecules is None and smiles is None:
        return "Error: Either 'molecules' or 'smiles' parameter must be provided"
    
    # Validate that we have protein input
    if target is None and target_uuid is None:
        return "Error: Either 'target' or 'target_uuid' parameter must be provided"
    
    # If target is provided, inform user it's not currently supported
    if target is not None:
        return ("Error: Direct PDB content upload is not currently supported through this API. "
                "Please use one of these alternatives:\n"
                "1. Upload your PDB file through the Rowan web interface at https://labs.rowansci.com\n"
                "2. Get the protein UUID from your account\n"
                "3. Use the 'target_uuid' parameter with that UUID\n\n"
                "For known proteins like 1COX, 2COX, etc., they may already be available "
                "in the Rowan protein library.")
    
    # Validate pocket if provided
    if pocket is not None:
        try:
            center, size = pocket
            if len(center) != 3 or len(size) != 3:
                return "Error: Pocket must be ((x,y,z), (x,y,z)) format"
            
            # Validate that size dimensions are positive
            if any(s <= 0 for s in size):
                return "Error: Pocket size dimensions must be positive"
                
        except (TypeError, ValueError) as e:
            return f"Error: Invalid pocket format. Expected ((x,y,z), (x,y,z)). Got: {pocket}"
    else:
        # Default pocket if not provided
        pocket = ((0.0, 0.0, 0.0), (20.0, 20.0, 20.0))
        logger.info("Using default pocket: center=(0,0,0), size=(20,20,20)")
    
    # Determine initial_molecule for rowan.compute()
    # For docking, the 'molecule' parameter is the ligand to dock
    initial_molecule = None
    ligands_list = None
    
    if molecules and len(molecules) > 0:
        initial_molecule = molecules[0]
        ligands_list = molecules
    elif isinstance(smiles, str):
        initial_molecule = smiles
        ligands_list = [smiles]
    elif isinstance(smiles, list) and len(smiles) > 0:
        initial_molecule = smiles[0]
        ligands_list = smiles
    else:
        return "Error: Could not determine initial molecule from inputs"
    
    try:
        # Build parameters following stjames DockingWorkflow structure
        compute_params = {
            "name": name,
            "molecule": initial_molecule,  # Required by rowan.compute() - this is the ligand
            "workflow_type": "docking",
            "folder_uuid": folder_uuid,
            "blocking": blocking,
            "ping_interval": ping_interval,
            # DockingWorkflow specific parameters
            "do_csearch": do_csearch,
            "do_optimization": do_optimization,
            "do_pose_refinement": do_pose_refinement,
            "pocket": pocket,
        }
        
        # For multiple ligands, pass them as 'molecules' parameter
        # This allows docking multiple ligands in one workflow
        if ligands_list and len(ligands_list) > 1:
            compute_params["molecules"] = ligands_list
            
        # Add protein specification (only one of these should be present)
        if target_uuid is not None:
            compute_params["target_uuid"] = target_uuid
        # Note: Direct PDB upload is not supported in current implementation
        # Users must pre-upload proteins through the Rowan web interface
            
        # Add conformers if provided
        if conformers is not None:
            compute_params["conformers"] = conformers
        
        # Submit docking calculation
        result = rowan.compute(**compute_params)
        
        # Format results
        uuid = result.get('uuid', 'N/A')
        status = result.get('status', 'unknown')
        
        if blocking:
            # Blocking mode - check if successful
            if status == "success":
                formatted = f"✅ Docking calculation '{name}' completed successfully!\n"
                formatted += f"🔖 Workflow UUID: {uuid}\n"
                formatted += f"📊 Status: {status}\n\n"
                
                # Extract docking results if available
                object_data = result.get("object_data", {})
                scores = object_data.get("scores", [])
                
                if scores:
                    formatted += f"🎯 Docking Results: {len(scores)} poses generated\n"
                    formatted += f"📈 Best docking score: {scores[0] if scores else 'N/A'}\n"
                    
                    # Show top poses
                    formatted += "\nTop poses:\n"
                    for i, score in enumerate(scores[:5]):
                        formatted += f"  {i+1}. Score: {score}\n"
                        
                    if len(scores) > 5:
                        formatted += f"  ... and {len(scores) - 5} more poses\n"
                else:
                    formatted += "📈 Results: Check workflow details for docking data\n"
                    
                return formatted
            else:
                # Failed calculation
                return f"Docking calculation failed\n🔖 UUID: {uuid}\n📋 Status: {status}\n💬 Check workflow details for more information"
        else:
            # Non-blocking mode
            formatted = f"Docking calculation '{name}' submitted!\n"
            formatted += f"Workflow UUID: {uuid}\n"
            formatted += f"Status: Running...\n"
            formatted += f"Use rowan_workflow_management to check status\n\n"
            
            formatted += f"Docking Details:\n"
            formatted += f"Ligand: {initial_molecule}\n"
            formatted += f"Target: {target_uuid or target[:50] + '...' if target and len(target) > 50 else target}\n"
            formatted += f"Pocket: center={pocket[0]}, size={pocket[1]}\n"
            formatted += f"Settings: csearch={do_csearch}, optimize={do_optimization}, refine={do_pose_refinement}\n"
            
            if conformers:
                formatted += f"Pre-optimized conformers: {len(conformers)}\n"
                
            return formatted
            
    except Exception as e:
        logger.error(f"Error in rowan_docking: {str(e)}")
        return f"Docking calculation failed: {str(e)}"

def rowan_docking_pdb_id(
    name: str,
    pdb_id: str,
    # Ligand specification
    molecules: Optional[List[str]] = None,
    smiles: Optional[Union[str, List[str]]] = None,
    # Other parameters same as rowan_docking
    pocket: Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]] = None,
    do_csearch: bool = True,
    do_optimization: bool = True,
    do_pose_refinement: bool = True,
    conformers: Optional[List[str]] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Helper function that explains how to dock with a PDB ID.
    
    NOTE: Direct PDB upload is not currently supported through the API.
    This function provides guidance on how to dock against known proteins.
    
    Args:
        name: Name for the docking calculation
        pdb_id: 4-character PDB ID (e.g., "1COX", "2COX", "6COX")
        (other parameters same as rowan_docking)
        
    Returns:
        Instructions on how to perform docking with the given PDB
    """
    # Check if we can fetch the PDB to verify it exists
    logger.info(f"Checking if PDB {pdb_id} exists...")
    pdb_content = fetch_pdb_content(pdb_id)
    
    if pdb_content is None:
        return (f"Error: PDB ID '{pdb_id}' not found in RCSB database. "
                f"Please check that the PDB ID is valid.")
    
    # Provide instructions for the user
    ligand_param = ""
    if molecules:
        ligand_param = f"    molecules={molecules},\n"
    elif smiles:
        if isinstance(smiles, str):
            ligand_param = f'    smiles="{smiles}",\n'
        else:
            ligand_param = f"    smiles={smiles},\n"
    
    return (f"PDB {pdb_id} found in RCSB database!\n\n"
            f"To perform docking with this protein:\n\n"
            f"1. Go to https://labs.rowansci.com\n"
            f"2. Upload the PDB file for {pdb_id}\n"
            f"   - You can download it from: https://files.rcsb.org/download/{pdb_id.upper()}.pdb\n"
            f"3. Once uploaded, find the protein UUID in your account\n"
            f"4. Use the docking function with target_uuid:\n\n"
            f"```python\n"
            f"rowan_docking(\n"
            f"    name=\"{name}\",\n"
            f"{ligand_param}"
            f"    target_uuid=\"your-protein-uuid-here\",\n"
            f"    pocket={pocket},\n"
            f"    do_csearch={do_csearch},\n"
            f"    do_optimization={do_optimization},\n"
            f"    do_pose_refinement={do_pose_refinement}\n"
            f")\n"
            f"```\n\n"
            f"Note: Some common proteins may already be available in the Rowan protein library.\n"
            f"Check your account for pre-uploaded structures.")

def test_rowan_docking():
    """Test the rowan_docking function."""
    try:
        # Test with minimal parameters
        result = rowan_docking(
            name="test_docking",
            smiles="CCO",  # Ethanol
            target_uuid="test-protein-uuid",  # Would need real UUID
            pocket=((0.0, 0.0, 0.0), (20.0, 20.0, 20.0)),
            blocking=False
        )
        print("Docking test result:")
        print(result)
        return True
    except Exception as e:
        print(f"Docking test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_docking()