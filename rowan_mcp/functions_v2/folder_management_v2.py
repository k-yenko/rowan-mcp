"""
Rowan v2 API: Folder Management
Tools for creating, retrieving, listing, and managing folders to organize workflows.
"""

from typing import List, Dict, Any, Annotated
import rowan


def create_folder(
    name: Annotated[str, "Name for the folder"],
    parent_uuid: Annotated[str, "UUID of parent folder for nesting. Empty string for root level"] = "",
    notes: Annotated[str, "Description or notes for the folder. Empty string for no notes"] = "",
    starred: Annotated[str, "Set starred status ('true'/'false'). Empty string defaults to false"] = ""
) -> Dict[str, Any]:
    """Create a public folder to organize related workflows. Use for battle submissions, research projects, or grouped calculations. Folders are always public for transparency and can be nested.

    Args:
        name: Name for the folder
        parent_uuid: UUID of parent folder for nesting. Empty string for root level
        notes: Description or notes for the folder. Empty string for no notes
        starred: Set starred status ("true"/"false"). Empty string defaults to false

    Returns:
        Dictionary containing folder information including uuid, name, public status (always True), parent_uuid, and URL
    """
    # Parse optional parameters
    parsed_parent_uuid = parent_uuid if parent_uuid else None
    parsed_notes = notes if notes else ""
    parsed_starred = starred.lower() == "true" if starred else False

    # CRITICAL: Always create public folders for BioArena transparency
    folder = rowan.create_folder(
        name=name,
        parent_uuid=parsed_parent_uuid,
        notes=parsed_notes,
        starred=parsed_starred,
        public=True  # Hardcoded - all folders are public
    )

    return {
        "uuid": folder.uuid,
        "name": folder.name,
        "public": folder.public,  # Will always be True
        "parent_uuid": folder.parent_uuid,
        "notes": folder.notes,
        "starred": folder.starred,
        "created_at": str(folder.created_at) if folder.created_at else None,
        "url": f"https://labs.rowansci.com/folder/{folder.uuid}"
    }


def retrieve_folder(
    uuid: Annotated[str, "UUID of the folder to retrieve"]
) -> Dict[str, Any]:
    """Retrieve folder details including name, public status, parent folder, and metadata.

    Args:
        uuid: UUID of the folder to retrieve

    Returns:
        Dictionary containing complete folder information
    """
    folder = rowan.retrieve_folder(uuid)

    return {
        "uuid": folder.uuid,
        "name": folder.name,
        "public": folder.public,
        "parent_uuid": folder.parent_uuid,
        "notes": folder.notes,
        "starred": folder.starred,
        "created_at": str(folder.created_at) if folder.created_at else None,
        "url": f"https://labs.rowansci.com/folder/{folder.uuid}"
    }


def list_folders(
    parent_uuid: Annotated[str, "Filter by parent folder UUID. Empty string for all folders"] = "",
    name_contains: Annotated[str, "Filter by name substring. Empty string for all names"] = "",
    public: Annotated[str, "Filter by public status ('true'/'false'). Empty string for both"] = "",
    starred: Annotated[str, "Filter by starred status ('true'/'false'). Empty string for both"] = "",
    page: Annotated[int, "Page number for pagination (0-indexed)"] = 0,
    size: Annotated[int, "Number of folders per page"] = 10
) -> List[Dict[str, Any]]:
    """List folders with optional filters by name, parent, public/starred status.

    Args:
        parent_uuid: Filter by parent folder UUID. Empty string for all folders
        name_contains: Filter by name substring. Empty string for all names
        public: Filter by public status ("true"/"false"). Empty string for both
        starred: Filter by starred status ("true"/"false"). Empty string for both
        page: Page number for pagination (0-indexed)
        size: Number of folders per page

    Returns:
        List of folder dictionaries matching the search criteria
    """
    # Parse optional parameters
    parsed_parent_uuid = parent_uuid if parent_uuid else None
    parsed_name_contains = name_contains if name_contains else None
    parsed_public = None
    if public:
        parsed_public = public.lower() == "true"
    parsed_starred = None
    if starred:
        parsed_starred = starred.lower() == "true"

    folders = rowan.list_folders(
        parent_uuid=parsed_parent_uuid,
        name_contains=parsed_name_contains,
        public=parsed_public,
        starred=parsed_starred,
        page=page,
        size=size
    )

    return [
        {
            "uuid": f.uuid,
            "name": f.name,
            "public": f.public,
            "parent_uuid": f.parent_uuid,
            "notes": f.notes,
            "starred": f.starred,
            "created_at": str(f.created_at) if f.created_at else None,
            "url": f"https://labs.rowansci.com/folder/{f.uuid}"
        }
        for f in folders
    ]


def update_folder(
    uuid: Annotated[str, "UUID of the folder to update"],
    name: Annotated[str, "New name for the folder. Empty string to keep current name"] = "",
    parent_uuid: Annotated[str, "UUID of new parent folder to move this folder. Empty string to keep current parent"] = "",
    notes: Annotated[str, "New notes/description. Empty string to keep current notes"] = "",
    starred: Annotated[str, "Set starred status ('true'/'false'). Empty string to keep current status"] = ""
) -> Dict[str, Any]:
    """Update folder metadata. Note: Cannot change public status (always public for battle transparency).

    Args:
        uuid: UUID of the folder to update
        name: New name for the folder. Empty string to keep current name
        parent_uuid: UUID of new parent folder to move this folder. Empty string to keep current parent
        notes: New notes/description. Empty string to keep current notes
        starred: Set starred status ("true"/"false"). Empty string to keep current status

    Returns:
        Dictionary with updated folder information
    """
    folder = rowan.retrieve_folder(uuid)

    # Parse optional parameters
    parsed_name = name if name else None
    parsed_parent_uuid = parent_uuid if parent_uuid else None
    parsed_notes = notes if notes else None
    parsed_starred = None
    if starred:
        parsed_starred = starred.lower() == "true"

    # Update the folder (public always stays True, not exposed as parameter)
    folder.update(
        name=parsed_name,
        parent_uuid=parsed_parent_uuid,
        notes=parsed_notes,
        starred=parsed_starred,
        public=None  # Don't change public status - always True
    )

    return {
        "uuid": folder.uuid,
        "name": folder.name,
        "public": folder.public,  # Will always be True
        "parent_uuid": folder.parent_uuid,
        "notes": folder.notes,
        "starred": folder.starred,
        "created_at": str(folder.created_at) if folder.created_at else None,
        "url": f"https://labs.rowansci.com/folder/{folder.uuid}",
        "message": "Folder updated successfully"
    }
