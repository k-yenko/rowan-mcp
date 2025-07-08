"""
PDB handler for Rowan docking - attempts to handle PDB input intelligently
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, Tuple
import rowan

logger = logging.getLogger(__name__)

def parse_pdb_content(pdb_content: str) -> Dict[str, Any]:
    """
    Parse PDB content into a structured format that might work with Rowan.
    
    This attempts to extract key information from PDB files that the 
    Rowan API might accept.
    """
    lines = pdb_content.split('\n')
    
    # Extract basic information
    header = ""
    title = ""
    atoms = []
    
    for line in lines:
        if line.startswith("HEADER"):
            header = line[10:50].strip()
        elif line.startswith("TITLE"):
            title += line[10:].strip() + " "
        elif line.startswith("ATOM") or line.startswith("HETATM"):
            atoms.append(line)
    
    # Try to create a structure that might work with Rowan's PDB format
    pdb_data = {
        "description": {
            "title": title.strip() or header,
            "classification": header
        },
        "experiment": {
            "technique": "X-RAY DIFFRACTION"  # Default assumption
        },
        "geometry": {},
        "contents": pdb_content,  # Keep full content
        "name": f"pdb_upload_{len(pdb_content)}"
    }
    
    return pdb_data

def attempt_pdb_upload(pdb_id: str, pdb_content: str, folder_uuid: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Attempt to upload PDB content to Rowan.
    
    Returns:
        Tuple of (uuid or None, status message)
    """
    try:
        # First, try the Protein.create method if it exists
        if hasattr(rowan, 'Protein') and hasattr(rowan.Protein, 'create'):
            logger.info(f"Attempting to create protein from PDB {pdb_id}")
            result = rowan.Protein.create(
                name=f"{pdb_id}_upload",
                pdb_content=pdb_content,
                folder_uuid=folder_uuid
            )
            if result and 'uuid' in result:
                return result['uuid'], f"Successfully uploaded PDB {pdb_id}"
        
        # Try alternative upload methods
        if hasattr(rowan, 'upload_pdb'):
            result = rowan.upload_pdb(pdb_content, name=pdb_id)
            if result and 'uuid' in result:
                return result['uuid'], f"Successfully uploaded PDB {pdb_id}"
        
        # Try to create a file upload
        if hasattr(rowan, 'File') and hasattr(rowan.File, 'create'):
            result = rowan.File.create(
                name=f"{pdb_id}.pdb",
                content=pdb_content,
                file_type="pdb",
                folder_uuid=folder_uuid
            )
            if result and 'uuid' in result:
                return result['uuid'], f"Uploaded PDB {pdb_id} as file"
                
    except Exception as e:
        logger.error(f"Failed to upload PDB {pdb_id}: {str(e)}")
    
    return None, f"Cannot upload PDB through API - manual upload required"

def handle_pdb_input(pdb_input: str, folder_uuid: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle PDB input (either PDB ID or UUID) and return information for docking.
    
    Args:
        pdb_input: Either a PDB ID (like "4Z18") or a UUID
        folder_uuid: Optional folder for uploads
        
    Returns:
        Dictionary with:
        - success: bool
        - uuid: str (if successful)
        - message: str (status/error message)
        - pdb_id: str (if it was a PDB ID)
        - instructions: str (what to do next)
    """
    # Check if it's a UUID (36 chars with dashes)
    if len(pdb_input) == 36 and pdb_input.count('-') == 4:
        return {
            "success": True,
            "uuid": pdb_input,
            "message": "Using provided protein UUID",
            "instructions": None
        }
    
    # Assume it's a PDB ID
    pdb_id = pdb_input.upper()
    
    # Fetch PDB content
    try:
        url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        pdb_content = response.text
        logger.info(f"Successfully fetched PDB {pdb_id} ({len(pdb_content)} characters)")
    except Exception as e:
        return {
            "success": False,
            "uuid": None,
            "message": f"Failed to fetch PDB {pdb_id}: {str(e)}",
            "pdb_id": pdb_id,
            "instructions": "Please verify the PDB ID is correct"
        }
    
    # Attempt to upload
    uuid, upload_status = attempt_pdb_upload(pdb_id, pdb_content, folder_uuid)
    
    if uuid:
        return {
            "success": True,
            "uuid": uuid,
            "message": upload_status,
            "pdb_id": pdb_id,
            "instructions": None
        }
    
    # Upload failed - provide instructions
    instructions = f"""
To use PDB {pdb_id} for docking:

1. Download the PDB file:
   https://files.rcsb.org/download/{pdb_id}.pdb

2. Upload to your Rowan account:
   https://labs.rowansci.com

3. Get the protein UUID from your account

4. Use the UUID in your docking call:
   rowan_docking(
       target_uuid="your-protein-uuid-here",
       ...
   )
"""
    
    return {
        "success": False,
        "uuid": None,
        "message": upload_status,
        "pdb_id": pdb_id,
        "instructions": instructions
    }

def enhance_docking_with_pdb_handler(
    target_input: Optional[str] = None,
    target_uuid: Optional[str] = None,
    **kwargs
) -> Tuple[Optional[str], str]:
    """
    Enhanced target handling for docking that accepts PDB IDs.
    
    Returns:
        Tuple of (target_uuid or None, message)
    """
    # If UUID already provided, use it
    if target_uuid:
        return target_uuid, "Using provided target UUID"
    
    # If target_input provided, try to handle it
    if target_input:
        result = handle_pdb_input(target_input, kwargs.get('folder_uuid'))
        
        if result['success']:
            return result['uuid'], result['message']
        else:
            # Return None but with helpful message
            return None, result['instructions'] or result['message']
    
    return None, "No protein target specified"