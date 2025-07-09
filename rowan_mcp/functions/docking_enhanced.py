"""
Enhanced docking function that accepts PDB IDs directly
"""

from typing import Optional, Union, List, Tuple
import logging
from .docking import rowan_docking
from .pdb_handler import handle_pdb_input

logger = logging.getLogger(__name__)

def rowan_docking_enhanced(
    name: str,
    # Ligand specification
    smiles: Optional[Union[str, List[str]]] = None,
    molecules: Optional[List[str]] = None,
    # Protein specification - NEW: accepts PDB ID or UUID
    target: Optional[str] = None,  # Can be PDB ID (e.g., "4Z18") or UUID
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
    """
    Enhanced docking function that accepts PDB IDs directly.
    
    This function intelligently handles protein input:
    - If target looks like a UUID (36 chars with dashes), uses it directly
    - If target looks like a PDB ID (e.g., "4Z18"), attempts to fetch and use it
    - Provides clear instructions when manual upload is needed
    
    Args:
        name: Name for the docking calculation
        smiles: SMILES string(s) of ligands
        molecules: Alternative to smiles - list of molecules
        target: PDB ID (e.g., "4Z18") or protein UUID
        pocket: Pocket specification ((center), (size))
        (other parameters same as rowan_docking)
        
    Returns:
        Docking results or clear instructions on what to do
        
    Examples:
        # Using PDB ID directly
        rowan_docking_enhanced(
            name="my_docking",
            smiles="CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
            target="4Z18",  # PDB ID
            pocket=((10.0, 15.0, 20.0), (20.0, 20.0, 20.0))
        )
        
        # Using UUID (if you already have one)
        rowan_docking_enhanced(
            name="my_docking",
            smiles="CC(=O)Oc1ccccc1C(=O)O",
            target="abc123de-f456-7890-ghij-klmnopqrstuv",  # UUID
            pocket=((10.0, 15.0, 20.0), (20.0, 20.0, 20.0))
        )
    """
    
    # Validate ligand input
    if smiles is None and molecules is None:
        return "Error: Either 'smiles' or 'molecules' must be provided"
    
    # Validate protein input
    if target is None:
        return "Error: 'target' parameter is required (PDB ID or protein UUID)"
    
    # Handle the target input
    logger.info(f"Processing target input: {target}")
    pdb_result = handle_pdb_input(target, folder_uuid)
    
    # If we successfully got a UUID, proceed with docking
    if pdb_result['success'] and pdb_result['uuid']:
        logger.info(f"Successfully resolved target to UUID: {pdb_result['uuid']}")
        
        # Call the main docking function with the UUID
        result = rowan_docking(
            name=name,
            smiles=smiles,
            molecules=molecules,
            target_uuid=pdb_result['uuid'],
            pocket=pocket,
            do_csearch=do_csearch,
            do_optimization=do_optimization,
            do_pose_refinement=do_pose_refinement,
            conformers=conformers,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        # Add context about PDB if it was used
        if 'pdb_id' in pdb_result:
            result = f"🧬 Using PDB {pdb_result['pdb_id']}:\n\n{result}"
        
        return result
    
    # If we couldn't get a UUID, provide helpful information
    else:
        pdb_id = pdb_result.get('pdb_id', target)
        
        # Format a helpful response
        response = f"🔍 PDB Input Detected: {pdb_id}\n\n"
        response += f"❌ {pdb_result['message']}\n\n"
        
        if pdb_result.get('instructions'):
            response += pdb_result['instructions']
        else:
            response += f"""
📋 To dock with PDB {pdb_id}:

1. **Download the PDB file**:
   https://files.rcsb.org/download/{pdb_id}.pdb

2. **Upload to Rowan**:
   https://labs.rowansci.com

3. **Get the protein UUID** from your account

4. **Run docking with the UUID**:
   ```python
   rowan_docking_enhanced(
       name="{name}",
       smiles={f'"{smiles}"' if isinstance(smiles, str) else smiles},
       target="your-protein-uuid-here",
       pocket={pocket}
   )
   ```

Note: Direct PDB upload through the API is not currently supported.
Proteins must be uploaded through the web interface.
"""
        
        return response

def test_enhanced_docking():
    """Test the enhanced docking function"""
    
    print("Testing enhanced docking with PDB ID...")
    
    # Test with PDB ID
    result = rowan_docking_enhanced(
        name="test_4z18_docking",
        smiles="CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
        target="4Z18",  # PDB ID
        pocket=((10.0, 15.0, 20.0), (20.0, 20.0, 20.0)),
        blocking=False
    )
    
    print(result)
    
    # Test with UUID
    print("\n" + "="*60 + "\n")
    print("Testing with UUID...")
    
    result = rowan_docking_enhanced(
        name="test_uuid_docking",
        smiles="CC(=O)Oc1ccccc1C(=O)O",
        target="12345678-1234-5678-1234-567812345678",  # Fake UUID format
        blocking=False
    )
    
    print(result)

if __name__ == "__main__":
    test_enhanced_docking()