"""
Rowan v2 API: Workflow Management Tools
MCP tools for interacting with Workflow objects returned by v2 API submission functions.
"""

from typing import Dict, Any, List, Annotated
import rowan


# Status mapping from stjames Status enum
# https://github.com/rowansci/stjames-public/blob/master/stjames/status.py
STATUS_DESCRIPTIONS = {
    0: "QUEUED",         # Job created, user below max_concurrency
    1: "RUNNING",        # Job still in progress
    2: "COMPLETED_OK",   # Job finished successfully
    3: "FAILED",         # Job encountered an error
    4: "STOPPED",        # Job stopped externally (e.g., timeout)
    5: "AWAITING_QUEUE"  # User exceeded max_concurrency
}


def _workflow_to_dict(workflow: rowan.Workflow) -> Dict[str, Any]:
    """Convert Workflow object to dictionary with all fields.

    This is the single source of truth for workflow serialization.
    Uses direct attribute access to avoid redundant API calls.

    Args:
        workflow: Rowan Workflow object (already fetched from API)

    Returns:
        Dictionary with all workflow fields including computed status flags

    Example:
        >>> workflow = rowan.retrieve_workflow("uuid-here")
        >>> data = _workflow_to_dict(workflow)
        >>> if data["is_finished"] and data["is_successful"]:
        ...     results = data["data"]
    """
    # Direct attribute access - NO API calls
    status_code = workflow.status

    # Compute is_finished locally instead of calling workflow.is_finished()
    # which would make another API call
    is_finished = status_code in {
        2,  # COMPLETED_OK
        3,  # FAILED
        4,  # STOPPED
    }

    return {
        # Identifiers
        "uuid": workflow.uuid,
        "name": workflow.name,
        "workflow_type": workflow.workflow_type,
        "parent_uuid": workflow.parent_uuid,

        # Status information (computed from direct attribute access)
        "status_code": status_code,
        "status_description": STATUS_DESCRIPTIONS.get(status_code, f"UNKNOWN_STATUS_{status_code}"),
        "is_finished": is_finished,
        "is_successful": status_code == 2,  # COMPLETED_OK
        "is_failed": status_code == 3,      # FAILED
        "is_running": status_code == 1,     # RUNNING

        # Timestamps
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "started_at": workflow.started_at,
        "completed_at": workflow.completed_at,

        # Results and data
        "data": workflow.data,

        # Metadata
        "notes": workflow.notes,
        "starred": workflow.starred,
        "public": workflow.public,
        "email_when_complete": workflow.email_when_complete,
        "max_credits": workflow.max_credits,

        # Resource usage
        "elapsed": workflow.elapsed,
        "credits_charged": workflow.credits_charged,
    }



def workflow_wait_for_result(
    workflow_uuid: Annotated[str, "UUID of the workflow to wait for completion"],
    poll_interval: Annotated[int, "Seconds between status checks while waiting"] = 5
) -> Dict[str, Any]:
    """Wait for a workflow to complete and return the result.

    WARNING: This function BLOCKS and can cause MCP timeouts!

    Workflow duration varies widely:
    - Simple calculations: seconds
    - Complex workflows (conformer searches, docking): 10-30+ minutes

    Consider using retrieve_workflow() with manual polling instead of this blocking function.

    Args:
        workflow_uuid: UUID of the workflow to wait for completion
        poll_interval: Seconds between status checks while waiting (default: 5)

    Returns:
        Dictionary with complete workflow data including results

    Important:
        - This function waits until workflow is "finished" (includes FAILED workflows!)
        - Always check "is_successful" and "is_failed" flags in the response
        - Essential for chaining dependent workflows

    Common Use Cases:
        - Conformer search → Redox potential for each conformer
        - Optimization → Frequency calculation on optimized geometry
        - Sequential optimizations with different methods
        - Any workflow chain where results feed into next calculation

    Example:
        >>> # Wait for workflow and check success
        >>> result = workflow_wait_for_result("uuid-here", poll_interval=10)
        >>>
        >>> if result["is_successful"]:
        ...     conformers = result["data"]["conformers"]
        ...     # Submit new workflows using conformer data
        >>> elif result["is_failed"]:
        ...     print(f"Workflow failed: {result['status_description']}")

    Raises:
        RuntimeError: If wait fails or API errors occur
    """
    try:
        workflow = rowan.retrieve_workflow(workflow_uuid)

        # Use the built-in wait_for_result method (blocks until complete)
        workflow.wait_for_result(poll_interval=poll_interval)

        # Use helper function for consistent conversion
        return _workflow_to_dict(workflow)

    except Exception as e:
        raise RuntimeError(
            f"Failed to wait for workflow '{workflow_uuid}' completion: {str(e)}"
        ) from e


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


def retrieve_workflow(
    uuid: Annotated[str, "UUID of the workflow to retrieve"]
) -> Dict[str, Any]:
    """Retrieve complete workflow data including status, results, and metadata.

    This is THE primary function for getting workflow information in a single API call.
    Returns all available workflow data including:
    - Status information (status_code, is_finished, is_successful, is_failed, is_running)
    - Results data (in 'data' field when workflow is complete)
    - Metadata (name, timestamps, credits, notes, etc.)

    Args:
        uuid: UUID of the workflow to retrieve

    Returns:
        Dictionary with complete workflow data

    Example:
        >>> # Check status and get results in one call
        >>> workflow = retrieve_workflow("workflow-uuid-here")
        >>>
        >>> if workflow["is_finished"]:
        ...     if workflow["is_successful"]:
        ...         results = workflow["data"]
        ...         print(f"Success! Results: {results}")
        ...         print(f"Credits used: {workflow['credits_charged']}")
        ...     elif workflow["is_failed"]:
        ...         print(f"Failed: {workflow['status_description']}")
        >>> else:
        ...     print(f"Still running: {workflow['status_description']}")
        >>>
        >>> # Poll for completion
        >>> import time
        >>> while not workflow["is_finished"]:
        ...     time.sleep(60)  # Wait 1 minute
        ...     workflow = retrieve_workflow(uuid)

    Raises:
        ValueError: If workflow UUID is invalid or workflow not found
        RuntimeError: If API authentication fails or other API errors occur
    """
    try:
        # Single API call gets all data
        workflow = rowan.retrieve_workflow(uuid)

        # Use helper function for consistent conversion with direct attribute access
        return _workflow_to_dict(workflow)

    except Exception as e:
        # Check if it's an HTTP error with a response
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code

            if status_code == 404:
                raise ValueError(
                    f"Workflow '{uuid}' not found. "
                    f"Verify the UUID is correct and the workflow hasn't been deleted."
                ) from e
            elif status_code == 401:
                raise RuntimeError(
                    "Authentication failed. Check your ROWAN_API_KEY environment variable."
                ) from e
            elif status_code == 429:
                raise RuntimeError(
                    "Rate limit exceeded. Wait before making more requests."
                ) from e
            else:
                raise RuntimeError(
                    f"Failed to retrieve workflow '{uuid}': HTTP {status_code}"
                ) from e
        else:
            # Not an HTTP error - could be network issue, invalid data, etc.
            raise RuntimeError(
                f"Failed to retrieve workflow '{uuid}': {str(e)}"
            ) from e


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