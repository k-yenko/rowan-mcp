"""
Rowan v2 API: Workflow Management Tools
MCP tools for interacting with Workflow objects returned by v2 API submission functions.
"""

from typing import Dict, Any, List, Annotated
import rowan


def workflow_get_status(
    workflow_uuid: Annotated[str, "UUID of the workflow to check status"]
) -> Dict[str, Any]:
    """Get the current status of a workflow.
    
    Args:
        workflow_uuid: UUID of the workflow to check status
    
    Returns:
        Dictionary with status information
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    status = workflow.get_status()
    
    return {
        "uuid": workflow_uuid,
        "status": status,
        "name": workflow.name,
        "is_finished": workflow.is_finished()
    }


def workflow_wait_for_result(
    workflow_uuid: Annotated[str, "UUID of the workflow to wait for completion"],
    poll_interval: Annotated[int, "Seconds between status checks while waiting"] = 5
) -> Dict[str, Any]:
    """Wait for a workflow to complete and return the result.
    
    Args:
        workflow_uuid: UUID of the workflow to wait for completion
        poll_interval: Seconds between status checks while waiting
    
    Essential for chaining dependent workflows where subsequent calculations 
    require results from previous ones. Blocks execution until the workflow 
    completes, then returns the full results.
    
    Common use cases:
    - Conformer search → Redox potential for each conformer
    - Optimization → Frequency calculation on optimized geometry
    - Multiple sequential optimizations with different methods
    - Any workflow chain where results feed into next calculation
    
    Example workflow chain:
        1. Submit conformer search
        2. Wait for conformer search to complete (using this function)
        3. Extract conformer geometries from results
        4. Submit new workflows using those geometries
    
    Returns:
        Dictionary containing the completed workflow data including results
        needed for dependent workflows (e.g., conformer_uuids, optimized
        geometries, calculation_uuids)
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    
    # Use the built-in wait_for_result method
    workflow.wait_for_result(poll_interval=poll_interval)
    
    # Return complete workflow data
    return {
        "uuid": workflow.uuid,
        "status": workflow.status,
        "name": workflow.name,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "completed_at": workflow.completed_at,
        "parent_uuid": workflow.parent_uuid,
        "workflow_type": workflow.workflow_type,
        "data": workflow.data,
        "credits_charged": workflow.credits_charged,
        "elapsed": workflow.elapsed
    }


def workflow_stop(
    workflow_uuid: Annotated[str, "UUID of the running workflow to stop"]
) -> Dict[str, str]:
    """Stop a running workflow.
    
    Args:
        workflow_uuid: UUID of the running workflow to stop
    
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.stop()
    
    return {
        "message": f"Workflow {workflow_uuid} stop request submitted",
        "uuid": workflow_uuid
    }


def workflow_delete(
    workflow_uuid: Annotated[str, "UUID of the workflow to permanently delete"]
) -> Dict[str, str]:
    """Delete a workflow.
    
    Args:
        workflow_uuid: UUID of the workflow to permanently delete
    
    This permanently removes the workflow and its results from the database.
    
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.delete()
    
    return {
        "message": f"Workflow {workflow_uuid} deleted successfully",
        "uuid": workflow_uuid
    }


def workflow_fetch_latest(
    workflow_uuid: Annotated[str, "UUID of the workflow to fetch latest data"],
    in_place: Annotated[bool, "Whether to update the workflow object in place"] = False
) -> Dict[str, Any]:
    """Fetch the latest workflow data from the database.
    
    Args:
        workflow_uuid: UUID of the workflow to fetch latest data
        in_place: Whether to update the workflow object in place
    
    Updates the workflow object with the most recent status and results.
    
    Returns:
        Dictionary containing the updated workflow data including status and results
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    
    # Fetch latest updates
    workflow.fetch_latest(in_place=in_place)
    
    # Return workflow data as dict
    return {
        "uuid": workflow.uuid,
        "status": workflow.status,
        "name": workflow.name,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "started_at": workflow.started_at,
        "completed_at": workflow.completed_at,
        "parent_uuid": workflow.parent_uuid,
        "workflow_type": workflow.workflow_type,
        "data": workflow.data,
        "notes": workflow.notes,
        "starred": workflow.starred,
        "public": workflow.public,
        "credits_charged": workflow.credits_charged,
        "elapsed": workflow.elapsed
    }


def retrieve_workflow(
    uuid: Annotated[str, "UUID of the workflow to retrieve"]
) -> Dict[str, Any]:
    """Retrieve a workflow from the API.
    
    Args:
        uuid: UUID of the workflow to retrieve
    
    Returns:
        Dictionary containing the complete workflow data
        
    Raises:
        HTTPError: If the API request fails
    """
    workflow = rowan.retrieve_workflow(uuid)
    
    # Convert workflow object to dict
    return {
        "uuid": workflow.uuid,
        "status": workflow.status,
        "name": workflow.name,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "started_at": workflow.started_at,
        "completed_at": workflow.completed_at,
        "parent_uuid": workflow.parent_uuid,
        "workflow_type": workflow.workflow_type,
        "data": workflow.data,
        "notes": workflow.notes,
        "starred": workflow.starred,
        "public": workflow.public,
        "email_when_complete": workflow.email_when_complete,
        "max_credits": workflow.max_credits,
        "elapsed": workflow.elapsed,
        "credits_charged": workflow.credits_charged
    }


def list_workflows(
    parent_uuid: Annotated[str, "UUID of parent folder to filter by. Empty string for all folders"] = "",
    name_contains: Annotated[str, "Substring to search for in workflow names. Empty string for all names"] = "",
    public: Annotated[str, "Filter by public status ('true'/'false'). Empty string for both"] = "",
    starred: Annotated[str, "Filter by starred status ('true'/'false'). Empty string for both"] = "",
    status: Annotated[str, "Filter by workflow status code. Empty string for all statuses"] = "",
    workflow_type: Annotated[str, "Filter by workflow type (e.g., 'conformer_search', 'pka'). Empty string for all types"] = "",
    page: Annotated[int, "Page number for pagination (0-indexed)"] = 0,
    size: Annotated[int, "Number of workflows per page"] = 10
):
    """List workflows subject to the specified criteria.
    
    Args:
        parent_uuid: UUID of parent folder to filter by. Empty string for all folders
        name_contains: Substring to search for in workflow names. Empty string for all names
        public: Filter by public status ("true"/"false"). Empty string for both
        starred: Filter by starred status ("true"/"false"). Empty string for both
        status: Filter by workflow status code. Empty string for all statuses
        workflow_type: Filter by workflow type (e.g., 'conformer_search', 'pka'). Empty string for all types
        page: Page number for pagination (0-indexed)
        size: Number of workflows per page
    
    Returns:
        List of workflow dictionaries that match the search criteria
        
    Raises:
        HTTPError: If the request to the API fails
    """
    # Use direct API call to avoid Workflow validation issues
    with rowan.api_client() as client:
        params = {
            "page": page,
            "size": size
        }
        
        # Add non-empty filters
        if parent_uuid:
            params["parent_uuid"] = parent_uuid
        if name_contains:
            params["name_contains"] = name_contains
        if public:
            params["public"] = public.lower() == "true"
        if starred:
            params["starred"] = starred.lower() == "true"
        if status:
            params["object_status"] = int(status)
        if workflow_type:
            params["object_type"] = workflow_type
        
        response = client.get("/workflow", params=params)
        response.raise_for_status()
        
        data = response.json()
        # Extract workflows from the paginated response
        return data.get("workflows", [])


def retrieve_calculation_molecules(
    uuid: Annotated[str, "UUID of the calculation to retrieve molecules from"]
) -> List[Dict[str, Any]]:
    """Retrieve a list of molecules from a calculation.
    
    Args:
        uuid: UUID of the calculation to retrieve molecules from
    
    Returns:
        List of dictionaries representing the molecules in the calculation
        
    Raises:
        HTTPError: If the API request fails
    """
    molecules = rowan.retrieve_calculation_molecules(uuid)
    
    # Convert molecules to list of dicts
    result = []
    for mol in molecules:
        mol_dict = {
            "smiles": mol.get("smiles"),
            "name": mol.get("name"),
            "charge": mol.get("charge"),
            "multiplicity": mol.get("multiplicity"),
            "energy": mol.get("energy"),
            "coordinates": mol.get("coordinates"),
            "properties": mol.get("properties", {})
        }
        # Remove None values
        mol_dict = {k: v for k, v in mol_dict.items() if v is not None}
        result.append(mol_dict)
    
    return result


def workflow_update(
    workflow_uuid: Annotated[str, "UUID of the workflow to update"],
    name: Annotated[str, "New name for the workflow. Empty string to keep current name"] = "",
    notes: Annotated[str, "New notes/description for the workflow. Empty string to keep current notes"] = "",
    starred: Annotated[str, "Set starred status ('true'/'false'). Empty string to keep current status"] = "",
    public: Annotated[str, "Set public visibility ('true'/'false'). Empty string to keep current status"] = ""
) -> Dict[str, Any]:
    """Update workflow details.
    
    Args:
        workflow_uuid: UUID of the workflow to update
        name: New name for the workflow. Empty string to keep current name
        notes: New notes/description for the workflow. Empty string to keep current notes
        starred: Set starred status ("true"/"false"). Empty string to keep current status
        public: Set public visibility ("true"/"false"). Empty string to keep current status
    
    Returns:
        Dictionary with updated workflow information
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    
    # Parse string boolean inputs
    parsed_starred = None
    if starred:
        parsed_starred = starred.lower() == "true"
    
    parsed_public = None
    if public:
        parsed_public = public.lower() == "true"
    
    # Update the workflow
    workflow.update(
        name=name if name else None,
        notes=notes if notes else None,
        starred=parsed_starred,
        public=parsed_public
    )
    
    return {
        "uuid": workflow.uuid,
        "name": workflow.name,
        "notes": workflow.notes,
        "starred": workflow.starred,
        "public": workflow.public,
        "message": "Workflow updated successfully"
    }


def workflow_is_finished(
    workflow_uuid: Annotated[str, "UUID of the workflow to check completion status"]
) -> Dict[str, Any]:
    """Check if a workflow is finished.
    
    Args:
        workflow_uuid: UUID of the workflow to check completion status
    
    Returns:
        Dictionary with workflow completion status
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    
    return {
        "uuid": workflow_uuid,
        "is_finished": workflow.is_finished(),
        "status": workflow.status,
        "name": workflow.name
    }


def workflow_delete_data(
    workflow_uuid: Annotated[str, "UUID of the workflow whose data to delete (keeps workflow record)"]
) -> Dict[str, str]:
    """Delete workflow data while keeping the workflow record.
    
    Args:
        workflow_uuid: UUID of the workflow whose data to delete (keeps workflow record)
    
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.delete_data()
    
    return {
        "message": f"Data for workflow {workflow_uuid} deleted successfully",
        "uuid": workflow_uuid
    }