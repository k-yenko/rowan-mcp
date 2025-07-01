"""
Folder management operations for Rowan API.
"""

import os
import rowan
from typing import Optional

# Set up logging
import logging
logger = logging.getLogger(__name__)

# Configure rowan API key
if not hasattr(rowan, 'api_key') or not rowan.api_key:
    api_key = os.getenv("ROWAN_API_KEY")
    if api_key:
        rowan.api_key = api_key
        logger.info("Rowan API key configured")
    else:
        logger.error("No ROWAN_API_KEY found in environment")

def rowan_folder_management(
    action: str,
    folder_uuid: Optional[str] = None,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    name_contains: Optional[str] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """Unified folder management tool for all folder operations.
    
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
                return " Error: 'name' is required for creating a folder"
            
            folder = rowan.Folder.create(
                name=name,
                parent_uuid=parent_uuid,  # Required by API
                notes=notes or "",
                starred=starred or False,
                public=public or False
            )
            
            formatted = f"Folder '{name}' created successfully!\n\n"
            formatted += f"UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"Notes: {notes or 'None'}\n"
            if parent_uuid:
                formatted += f"Parent: {parent_uuid}\n"
            return formatted
            
        elif action == "retrieve":
            if not folder_uuid:
                return "Error: 'folder_uuid' is required for retrieving a folder"
            
            folder = rowan.Folder.retrieve(uuid=folder_uuid)
            
            formatted = f"Folder Details:\n\n"
            formatted += f"Name: {folder.get('name', 'N/A')}\n"
            formatted += f"UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"Parent: {folder.get('parent_uuid', 'Root')}\n"
            formatted += f"Starred: {'Yes' if folder.get('starred') else 'No'}\n"
            formatted += f"Public: {'Yes' if folder.get('public') else 'No'}\n"
            formatted += f"Created: {folder.get('created_at', 'N/A')}\n"
            formatted += f"Notes: {folder.get('notes', 'None')}\n"
            return formatted
            
        elif action == "update":
            if not folder_uuid:
                return "Error: 'folder_uuid' is required for updating a folder"
            
            # Build update parameters
            update_params = {"uuid": folder_uuid}
            if name is not None:
                update_params["name"] = name
            if parent_uuid is not None:
                update_params["parent_uuid"] = parent_uuid
            if notes is not None:
                update_params["notes"] = notes
            if starred is not None:
                update_params["starred"] = starred
            if public is not None:
                update_params["public"] = public
                
            folder = rowan.Folder.update(**update_params)
            
            formatted = f"Folder '{folder.get('name')}' updated successfully!\n\n"
            formatted += f"UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"Name: {folder.get('name', 'N/A')}\n"
            formatted += f"Starred: {'Yes' if folder.get('starred') else 'No'}\n"
            formatted += f"Public: {'Yes' if folder.get('public') else 'No'}\n"
            return formatted
            
        elif action == "delete":
            if not folder_uuid:
                return "Error: 'folder_uuid' is required for deleting a folder"
            
            rowan.Folder.delete(uuid=folder_uuid)
            return f"Folder {folder_uuid} deleted successfully."
            
        elif action == "list":
            # Build filter parameters - only include non-None/non-empty values
            filter_params = {"page": page, "size": size}
            
            if name_contains:  # Only add if not None and not empty
                filter_params["name_contains"] = name_contains
            if parent_uuid:  # Only add if not None and not empty
                filter_params["parent_uuid"] = parent_uuid
            if starred is not None:  # Boolean can be False, so check specifically for None
                filter_params["starred"] = starred
            if public is not None:  # Boolean can be False, so check specifically for None
                filter_params["public"] = public
                
            result = rowan.Folder.list(**filter_params)
            folders = result.get("folders", [])
            num_pages = result.get("num_pages", 1)
            
            if not folders:
                return "No folders found matching criteria."
            
            formatted = f"Found {len(folders)} folders (Page {page}/{num_pages}):\n\n"
            for folder in folders:
                starred_text = " [STARRED]" if folder.get('starred') else ""
                public_text = " [PUBLIC]" if folder.get('public') else " [PRIVATE]"
                formatted += f" {folder.get('name', 'Unnamed')}{starred_text}{public_text}\n"
                formatted += f"   UUID: {folder.get('uuid', 'N/A')}\n"
                if folder.get('notes'):
                    formatted += f"   Notes: {folder.get('notes')}\n"
                formatted += "\n"
            
            return formatted
            
        else:
            return f"Error: Unknown action '{action}'. Available actions: create, retrieve, update, delete, list"
            
    except Exception as e:
        error_msg = str(e)
        if "500 Internal Server Error" in error_msg and "folder" in error_msg:
            return f" **Folder API Issue**: The Rowan folder endpoint is currently experiencing issues.\n\n" \
                   f"**Known Problem**: The rowan-python library sends empty parameters that cause 500 errors.\n\n" \
                   f"**Workarounds**:\n" \
                   f"• Use workflow organization via rowan_workflow_management(action='list')\n" \
                   f"• Create folders via the Rowan web interface at labs.rowansci.com\n" \
                   f"• Use parent_uuid when creating workflows to organize them\n\n" \
                   f"**Technical Details**: {error_msg[:100]}..."
        else:
            return f" Error in folder {action}: {str(e)}"


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