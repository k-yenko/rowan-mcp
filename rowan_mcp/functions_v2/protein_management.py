"""
Rowan v2 API: Protein Management
Tools for creating, retrieving, and managing protein structures.
"""

from typing import List, Dict, Any, Annotated
import rowan


def create_protein_from_pdb_id(
    name: Annotated[str, "Name for the protein"],
    code: Annotated[str, "PDB ID code (e.g., '1HCK')"]
) -> Dict[str, Any]:
    """Create a protein from a PDB ID.
    
    Args:
        name: Name for the protein
        code: PDB ID code (e.g., '1HCK')
    
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
    uuid: Annotated[str, "UUID of the protein to retrieve"]
) -> Dict[str, Any]:
    """Retrieve a protein by UUID.
    
    Args:
        uuid: UUID of the protein to retrieve
    
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
    page: Annotated[int, "Page number (0-indexed)"] = 0,
    size: Annotated[int, "Number per page"] = 20
) -> List[Dict[str, Any]]:
    """List proteins.
    
    Args:
        page: Page number (0-indexed)
        size: Number per page
    
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
    name: Annotated[str, "Name for the protein"],
    file_path: Annotated[str, "Path to PDB file"]
) -> Dict[str, Any]:
    """Upload a protein from a PDB file.
    
    Args:
        name: Name for the protein
        file_path: Path to PDB file
    
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
    uuid: Annotated[str, "UUID of the protein to delete"]
) -> Dict[str, str]:
    """Delete a protein.
    
    Args:
        uuid: UUID of the protein to delete
    
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
    uuid: Annotated[str, "UUID of the protein to sanitize"]
) -> Dict[str, Any]:
    """Sanitize a protein for docking.
    
    Args:
        uuid: UUID of the protein to sanitize
    
    Returns:
        Dictionary with sanitization status
    """
    protein = rowan.retrieve_protein(uuid)
    protein.sanitize()
    
    return {
        "uuid": uuid,
        "message": f"Protein {uuid} sanitized"
    }