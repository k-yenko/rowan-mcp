"""
Rowan v2 API: Protein Management
Tools for creating, retrieving, and managing protein structures.
"""

from typing import Optional, List, Dict, Any, Annotated
from pydantic import Field
import rowan


def create_protein_from_pdb_id(
    name: Annotated[
        str,
        Field(description="Name for the protein")
    ],
    code: Annotated[
        str,
        Field(description="PDB ID code (e.g., '1HCK')")
    ]
) -> Dict[str, Any]:
    """Create a protein from a PDB ID.
    
    Returns:
        Dictionary containing protein information
    """
    protein = rowan.create_protein_from_pdb_id(name=name, code=code)
    
    return {
        "uuid": protein.uuid,
        "name": protein.name,
        "sanitized": protein.sanitized,
        "created_at": str(protein.created_at) if protein.created_at else None
    }


def retrieve_protein(
    uuid: Annotated[
        str,
        Field(description="UUID of the protein to retrieve")
    ]
) -> Dict[str, Any]:
    """Retrieve a protein by UUID.
    
    Returns:
        Dictionary containing the protein data
    """
    protein = rowan.retrieve_protein(uuid)
    
    return {
        "uuid": protein.uuid,
        "name": protein.name,
        "sanitized": protein.sanitized,
        "created_at": str(protein.created_at) if protein.created_at else None
    }


def list_proteins(
    page: Annotated[
        int,
        Field(description="Page number (0-indexed)")
    ] = 0,
    size: Annotated[
        int,
        Field(description="Number per page")
    ] = 20
) -> List[Dict[str, Any]]:
    """List proteins.
    
    Returns:
        List of protein dictionaries
    """
    proteins = rowan.list_proteins(page=page, size=size)
    
    return [
        {
            "uuid": p.uuid,
            "name": p.name,
            "sanitized": p.sanitized,
            "created_at": str(p.created_at) if p.created_at else None
        }
        for p in proteins
    ]


def upload_protein(
    name: Annotated[
        str,
        Field(description="Name for the protein")
    ],
    file_path: Annotated[
        str,
        Field(description="Path to PDB file")
    ]
) -> Dict[str, Any]:
    """Upload a protein from a PDB file.
    
    Returns:
        Dictionary containing protein information
    """
    from pathlib import Path
    protein = rowan.upload_protein(name=name, file_path=Path(file_path))
    
    return {
        "uuid": protein.uuid,
        "name": protein.name,
        "sanitized": protein.sanitized,
        "created_at": str(protein.created_at) if protein.created_at else None
    }


def delete_protein(
    uuid: Annotated[
        str,
        Field(description="UUID of the protein to delete")
    ]
) -> Dict[str, str]:
    """Delete a protein.
    
    Returns:
        Dictionary with confirmation message
    """
    protein = rowan.retrieve_protein(uuid)
    protein.delete()
    
    return {
        "message": f"Protein {uuid} deleted",
        "uuid": uuid
    }


def sanitize_protein(
    uuid: Annotated[
        str,
        Field(description="UUID of the protein to sanitize")
    ]
) -> Dict[str, Any]:
    """Sanitize a protein for docking.
    
    Returns:
        Dictionary with sanitization status
    """
    protein = rowan.retrieve_protein(uuid)
    protein.sanitize()
    
    return {
        "uuid": uuid,
        "message": f"Protein {uuid} sanitized"
    }