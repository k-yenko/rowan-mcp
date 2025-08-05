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
        Field(description="Name for the protein (for identification in your workspace)")
    ],
    code: Annotated[
        str,
        Field(description="PDB ID code (e.g., '1ABC', '7KDM') to fetch protein structure from RCSB PDB database")
    ]
) -> Dict[str, Any]:
    """Create a protein object from a PDB ID code.
    
    Fetches protein structure data from the RCSB Protein Data Bank and creates
    a Protein object in your Rowan workspace for use in docking and other calculations.
    
    The PDB (Protein Data Bank) is the global repository for 3D structural data of
    biological macromolecules. Each structure has a unique 4-character PDB ID.
    
    Returns:
        Dictionary containing protein information including UUID, name, and structure details
        
    Examples:
        # Create protein from lysozyme structure
        protein = create_protein_from_pdb_id(
            name="Lysozyme",
            code="1HEW"
        )
        
        # Create protein from COVID-19 main protease
        protein = create_protein_from_pdb_id(
            name="SARS-CoV-2 Mpro",
            code="7KDM"
        )
        
        # Create protein for kinase docking studies
        protein = create_protein_from_pdb_id(
            name="CDK2 Kinase",
            code="1HCK"
        )
    """
    try:
        # Create protein from PDB ID
        protein = rowan.create_protein_from_pdb_id(name=name, code=code)
        
        # Convert to dictionary for JSON serialization
        return {
            "success": True,
            "uuid": protein.uuid,
            "name": protein.name,
            "pdb_code": code,
            "created_at": str(protein.created_at) if hasattr(protein, 'created_at') else None,
            "message": f"Protein '{name}' created successfully from PDB ID {code}"
        }
        
    except Exception as e:
        # Check if it's a PDB fetch error
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            raise ValueError(f"PDB ID '{code}' not found. Please verify the PDB code is correct.")
        else:
            raise e


def retrieve_protein(
    uuid: Annotated[
        str,
        Field(description="UUID of the protein to retrieve")
    ]
) -> Dict[str, Any]:
    """Retrieve a protein object by its UUID.
    
    Returns:
        Dictionary containing the protein data
    """
    try:
        protein = rowan.retrieve_protein(uuid)
        
        # Convert to dictionary
        result = {
            "uuid": protein.uuid,
            "name": protein.name,
            "created_at": str(protein.created_at) if hasattr(protein, 'created_at') else None,
            "updated_at": str(protein.updated_at) if hasattr(protein, 'updated_at') else None,
        }
        
        # Add any additional fields that exist
        if hasattr(protein, 'pdb_content'):
            result["has_pdb_content"] = bool(protein.pdb_content)
        if hasattr(protein, 'sequence'):
            result["sequence"] = protein.sequence
        if hasattr(protein, 'chains'):
            result["chains"] = protein.chains
            
        return result
        
    except Exception as e:
        raise e


def list_proteins(
    page: Annotated[
        int,
        Field(description="Page number for pagination (0-indexed)")
    ] = 0,
    size: Annotated[
        int,
        Field(description="Number of proteins per page")
    ] = 10
) -> List[Dict[str, Any]]:
    """List all proteins in your workspace.
    
    Returns:
        List of protein dictionaries
    """
    try:
        proteins = rowan.list_proteins(page=page, size=size)
        
        # Convert to list of dicts
        return [
            {
                "uuid": p.uuid,
                "name": p.name,
                "created_at": str(p.created_at) if hasattr(p, 'created_at') else None,
                "updated_at": str(p.updated_at) if hasattr(p, 'updated_at') else None,
            }
            for p in proteins
        ]
        
    except Exception as e:
        raise e


def upload_protein(
    name: Annotated[
        str,
        Field(description="Name for the protein (for identification)")
    ],
    pdb_content: Annotated[
        str,
        Field(description="Complete PDB file content as a string")
    ]
) -> Dict[str, Any]:
    """Upload a protein from PDB file content.
    
    Use this when you have a custom PDB file or modified structure that's not
    in the RCSB database.
    
    Returns:
        Dictionary containing protein information including UUID and name
        
    Example:
        # Upload custom PDB content
        with open("my_protein.pdb", "r") as f:
            pdb_content = f.read()
            
        protein = upload_protein(
            name="Custom Protein",
            pdb_content=pdb_content
        )
    """
    try:
        protein = rowan.upload_protein(name=name, pdb_content=pdb_content)
        
        return {
            "success": True,
            "uuid": protein.uuid,
            "name": protein.name,
            "created_at": str(protein.created_at) if hasattr(protein, 'created_at') else None,
            "message": f"Protein '{name}' uploaded successfully"
        }
        
    except Exception as e:
        raise e


def delete_protein(
    uuid: Annotated[
        str,
        Field(description="UUID of the protein to delete")
    ]
) -> Dict[str, str]:
    """Delete a protein from your workspace.
    
    This permanently removes the protein. Any workflows using this protein
    will still have their results, but won't be able to re-run.
    
    Returns:
        Dictionary with confirmation message
    """
    try:
        protein = rowan.retrieve_protein(uuid)
        protein.delete()
        
        return {
            "message": f"Protein {uuid} deleted successfully",
            "uuid": uuid
        }
        
    except Exception as e:
        raise e


def sanitize_protein(
    uuid: Annotated[
        str,
        Field(description="UUID of the protein to sanitize for docking")
    ]
) -> Dict[str, Any]:
    """Sanitize a protein for docking calculations.
    
    This prepares the protein PDB file for AutoDock Vina by removing
    incompatible tags and ensuring proper formatting. Must be called
    before using the protein in docking workflows.
    
    Returns:
        Dictionary with sanitization status
        
    Example:
        # Sanitize protein before docking
        result = sanitize_protein(uuid="a12378ae-52c2-485f-b2e2-2a9db687f06c")
        
        # Now the protein can be used for docking
        docking = submit_docking_workflow(
            protein=result["uuid"],
            pocket=[[15.0, 5.0, 10.0], [40.0, 25.0, 30.0]],
            initial_molecule="CCO"
        )
    """
    try:
        protein = rowan.retrieve_protein(uuid)
        
        # Check current sanitization status
        was_sanitized = protein.sanitized if hasattr(protein, 'sanitized') else False
        
        # Sanitize the protein
        protein.sanitize()
        
        # Check new status
        is_sanitized = protein.sanitized if hasattr(protein, 'sanitized') else True
        
        return {
            "success": True,
            "uuid": protein.uuid,
            "name": protein.name,
            "was_sanitized": was_sanitized,
            "is_sanitized": is_sanitized,
            "message": f"Protein '{protein.name}' sanitized successfully for docking"
        }
        
    except Exception as e:
        raise e