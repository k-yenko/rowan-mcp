"""
Rowan v2 API: Project Management
Tools for creating, retrieving, listing, and managing projects to organize workflows, folders, and structures.
"""

from typing import List, Dict, Any, Annotated
import rowan


def create_project(
    name: Annotated[str, "Name for the project"]
) -> Dict[str, Any]:
    """Create a new project to organize workflows, folders, and molecular structures.

    Projects are top-level organizational spaces that automatically include a home folder
    and structure repository. Use projects to separate research directions, targets, or clients.

    Args:
        name: Name for the project

    Returns:
        Dictionary containing project information including uuid, name, created_at, and URL

    Example:
        >>> result = create_project("BioArena Battles 2025")
        >>> print(result['url'])
        https://labs.rowansci.com/project/abc-123
    """
    project = rowan.create_project(name=name)

    return {
        "uuid": project.uuid,
        "name": project.name,
        "created_at": str(project.created_at) if project.created_at else None,
        "url": f"https://labs.rowansci.com/project/{project.uuid}"
    }


def retrieve_project(
    uuid: Annotated[str, "UUID of the project to retrieve"]
) -> Dict[str, Any]:
    """Retrieve project details by UUID.

    Args:
        uuid: UUID of the project to retrieve

    Returns:
        Dictionary containing complete project information

    Example:
        >>> project = retrieve_project("abc-123")
        >>> print(project['name'])
        BioArena Battles 2025
    """
    project = rowan.retrieve_project(uuid)

    return {
        "uuid": project.uuid,
        "name": project.name,
        "created_at": str(project.created_at) if project.created_at else None,
        "url": f"https://labs.rowansci.com/project/{project.uuid}"
    }


def list_projects(
    name_contains: Annotated[str, "Filter by name substring. Empty string for all projects"] = "",
    page: Annotated[int, "Page number for pagination (0-indexed)"] = 0,
    size: Annotated[int, "Number of projects per page"] = 10
) -> List[Dict[str, Any]]:
    """List projects with optional name filter.

    Projects are top-level organizational containers for workflows, folders, and structures.
    Each project has a home folder and structure repository.

    Args:
        name_contains: Filter by name substring. Empty string for all projects
        page: Page number for pagination (0-indexed)
        size: Number of projects per page

    Returns:
        List of project dictionaries matching the search criteria

    Example:
        >>> projects = list_projects(name_contains="BioArena")
        >>> for p in projects:
        ...     print(f"{p['name']}: {p['url']}")
    """
    # Parse optional parameters
    parsed_name_contains = name_contains if name_contains else None

    projects = rowan.list_projects(
        name_contains=parsed_name_contains,
        page=page,
        size=size
    )

    return [
        {
            "uuid": p.uuid,
            "name": p.name,
            "created_at": str(p.created_at) if p.created_at else None,
            "url": f"https://labs.rowansci.com/project/{p.uuid}"
        }
        for p in projects
    ]


def update_project(
    uuid: Annotated[str, "UUID of the project to update"],
    name: Annotated[str, "New name for the project"]
) -> Dict[str, Any]:
    """Update project name.

    Note: Projects use role-based access control (Owner/Collaborator).
    You must be the project owner to update it.

    Args:
        uuid: UUID of the project to update
        name: New name for the project

    Returns:
        Dictionary with updated project information

    Example:
        >>> result = update_project("abc-123", "BioArena Battles 2026")
        >>> print(result['message'])
        Project updated successfully
    """
    project = rowan.retrieve_project(uuid)

    # Update the project
    project.update(name=name)

    return {
        "uuid": project.uuid,
        "name": project.name,
        "created_at": str(project.created_at) if project.created_at else None,
        "url": f"https://labs.rowansci.com/project/{project.uuid}",
        "message": "Project updated successfully"
    }


def delete_project(
    uuid: Annotated[str, "UUID of the project to permanently delete"]
) -> Dict[str, str]:
    """Delete a project and all its contents.

    WARNING: This is a DESTRUCTIVE action that will delete:
    - All folders within the project
    - All workflows within the project
    - The project's structure repository
    - All data cannot be recovered

    You cannot delete your default project. Set a different default project first.

    Args:
        uuid: UUID of the project to permanently delete

    Returns:
        Dictionary with confirmation message

    Example:
        >>> result = delete_project("abc-123")
        >>> print(result['message'])
        Project abc-123 and all its contents deleted successfully
    """
    project = rowan.retrieve_project(uuid)
    project.delete()

    return {
        "message": f"Project {uuid} and all its contents deleted successfully",
        "uuid": uuid,
        "warning": "All folders, workflows, and structures in this project have been permanently deleted"
    }


def get_default_project() -> Dict[str, Any]:
    """Get your default project.

    The default project is where workflows are placed when submitted via API without
    specifying a folder UUID. You can set your default project in account settings.

    Returns:
        Dictionary containing default project information

    Example:
        >>> default = get_default_project()
        >>> print(f"Default project: {default['name']}")
        Default project: My Research
    """
    project = rowan.default_project()

    return {
        "uuid": project.uuid,
        "name": project.name,
        "created_at": str(project.created_at) if project.created_at else None,
        "url": f"https://labs.rowansci.com/project/{project.uuid}",
        "is_default": True
    }
