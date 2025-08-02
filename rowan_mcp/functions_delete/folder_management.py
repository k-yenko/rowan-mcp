"""
Folder management operations for Rowan API.
"""

import os
import rowan
from typing import Optional

# Set up logging
import logging
logger = logging.getLogger(__name__)



def rowan_folder_management(
    action: str,
    folder_uuid: Optional[str] = None,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
    is_root: Optional[bool] = None,
    uuid: Optional[str] = None,
    name_contains: Optional[str] = None,
    page: int = 0,
    size: int = 50
) -> str:
    """Unified folder management tool for all folder operations. Available actions: create, retrieve, update, delete, list.
    
    **Available Actions:**
    - **create**: Create a new folder (requires: name, optional: parent_uuid, notes, starred, public)
    - **retrieve**: Get folder details (requires: folder_uuid)
    - **update**: Update folder properties (requires: folder_uuid, optional: name, parent_uuid, notes, starred, public)
    - **delete**: Delete a folder (requires: folder_uuid)
    - **list**: List folders with filters (optional: name_contains, parent_uuid, starred, public, page, size)
    
    Args:
        action: Action to perform ('create', 'retrieve', 'update', 'delete', 'list')
        folder_uuid: UUID of the folder (required for retrieve, update, delete)
        name: Folder name (required for create, optional for update)
        parent_uuid: Parent folder UUID (optional for create/update, if not provided creates in root)
        notes: Folder notes (optional for create/update)
        starred: Star the folder (optional for create/update)
        public: Make folder public (optional for create/update)
        created_at: The date and time at which this folder was created
        updated_at: The date and time at which this folder was most recently updated
        is_root: Whether or not this folder is the user's root folder
        uuid: The UUID of this folder
        name_contains: Filter by name containing text (optional for list)
        page: Page number for pagination (default: 1, for list)
        size: Results per page (default: 50, for list)
    
    Returns:
        Results of the folder operation
    """
    
    action = action.lower()
    
    try:
        if action == "create":
            if not name:
                return "Error: 'name' is required for creating a folder"
            
            return rowan.Folder.create(
                name=name,
                parent_uuid=parent_uuid,
                notes=notes or "",
                starred=starred or False,
                public=public or False
            )
            
        elif action == "retrieve":
            if not folder_uuid:
                return "Error: 'folder_uuid' is required for retrieving a folder"
            
            return rowan.Folder.retrieve(uuid=folder_uuid)
            
        elif action == "update":
            if not folder_uuid:
                return "Error: 'folder_uuid' is required for updating a folder"

            return rowan.Folder.update(
                uuid=folder_uuid,
                name=name,
                notes=notes,
                starred=starred,
                public=public,
                parent_uuid=parent_uuid
                
            )
            
        elif action == "delete":
            if not folder_uuid:
                return "Error: 'folder_uuid' is required for deleting a folder"
            
            rowan.Folder.delete(uuid=folder_uuid)
            return "Folder deleted successfully"
            
        elif action == "list":
            return rowan.Folder.list(
                name_contains=name_contains,
                parent_uuid=parent_uuid,
                starred=starred,
                public=public,
                page=page,
                size=size
            )
              
    except Exception as e:
        return f"Error in folder {action}: {str(e)}"


def test_rowan_folder_management():
    """Test the rowan_folder_management function."""
    try:
        # Test listing folders
        result = rowan_folder_management(action="list", size=5)
        print("Folder management test successful!")
        print(f"Result: {result[:200]}...")  # Show first 200 chars
        return True
    except Exception as e:
        print(f"Folder management test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_folder_management() 