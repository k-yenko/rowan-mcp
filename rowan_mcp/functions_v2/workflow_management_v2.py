"""
Rowan v2 API: Workflow Management Tools
MCP tools for interacting with Workflow objects returned by v2 API submission functions.
"""

from typing import Optional, Dict, Any, List
import rowan


def workflow_get_status(workflow_uuid: str) -> Dict[str, Any]:
    """Get the current status of a workflow.
    
    Args:
        workflow_uuid: The UUID of the workflow
        
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
    workflow_uuid: str,
    poll_interval: int = 5
) -> Dict[str, Any]:
    """Wait for a workflow to complete and return the result.
    
    Blocks until the workflow completes, polling at specified intervals.
    
    Args:
        workflow_uuid: The UUID of the workflow to wait for
        poll_interval: Time in seconds between status checks (default: 5)
        
    Returns:
        Dictionary containing the completed workflow data including results
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


def workflow_stop(workflow_uuid: str) -> Dict[str, str]:
    """Stop a running workflow.
    
    Args:
        workflow_uuid: The UUID of the workflow to stop
        
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.stop()
    
    return {
        "message": f"Workflow {workflow_uuid} stop request submitted",
        "uuid": workflow_uuid
    }


def workflow_delete(workflow_uuid: str) -> Dict[str, str]:
    """Delete a workflow.
    
    This permanently removes the workflow and its results from the database.
    
    Args:
        workflow_uuid: The UUID of the workflow to delete
        
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.delete()
    
    return {
        "message": f"Workflow {workflow_uuid} deleted successfully",
        "uuid": workflow_uuid
    }


def workflow_fetch_latest(workflow_uuid: str, in_place: bool = False) -> Dict[str, Any]:
    """Fetch the latest workflow data from the database.
    
    Updates the workflow object with the most recent status and results.
    
    Args:
        workflow_uuid: The UUID of the workflow to fetch
        in_place: Whether to update the workflow object in place (default: False)
        
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


def retrieve_workflow(uuid: str) -> Dict[str, Any]:
    """Retrieve a workflow from the API.
    
    Args:
        uuid: The UUID of the workflow to retrieve
        
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
    parent_uuid: Optional[str] = None,
    name_contains: Optional[str] = None,
    public: Optional[bool] = None,
    starred: Optional[bool] = None,
    status: Optional[int] = None,
    workflow_type: Optional[str] = None,
    page: int = 0,
    size: int = 10
) -> List[Dict[str, Any]]:
    """List workflows subject to the specified criteria.
    
    Args:
        parent_uuid: The UUID of the parent folder
        name_contains: Substring to search for in workflow names
        public: Filter workflows by their public status
        starred: Filter workflows by their starred status
        status: Filter workflows by their status
        workflow_type: Filter workflows by their type
        page: The page number to retrieve (default: 0)
        size: The number of items per page (default: 10)
        
    Returns:
        List of workflow dictionaries that match the search criteria
        
    Raises:
        HTTPError: If the request to the API fails
    """
    workflows = rowan.list_workflows(
        parent_uuid=parent_uuid,
        name_contains=name_contains,
        public=public,
        starred=starred,
        status=status,
        workflow_type=workflow_type,
        page=page,
        size=size
    )
    
    # Convert to list of dicts
    return [
        {
            "uuid": w.uuid,
            "name": w.name,
            "status": w.status,
            "created_at": w.created_at,
            "updated_at": w.updated_at,
            "parent_uuid": w.parent_uuid,
            "workflow_type": w.workflow_type,
            "public": w.public,
            "starred": w.starred,
            "credits_charged": w.credits_charged
        }
        for w in workflows
    ]


def retrieve_calculation_molecules(uuid: str) -> List[Dict[str, Any]]:
    """Retrieve a list of molecules from a calculation.
    
    Args:
        uuid: The UUID of the calculation to retrieve molecules from
        
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
    workflow_uuid: str,
    name: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None
) -> Dict[str, Any]:
    """Update workflow details.
    
    Args:
        workflow_uuid: The UUID of the workflow to update
        name: New name for the workflow (optional)
        notes: New notes for the workflow (optional)
        starred: Whether to star/unstar the workflow (optional)
        public: Whether to make the workflow public/private (optional)
        
    Returns:
        Dictionary with updated workflow information
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    
    # Update the workflow
    workflow.update(
        name=name,
        notes=notes,
        starred=starred,
        public=public
    )
    
    return {
        "uuid": workflow.uuid,
        "name": workflow.name,
        "notes": workflow.notes,
        "starred": workflow.starred,
        "public": workflow.public,
        "message": "Workflow updated successfully"
    }


def workflow_is_finished(workflow_uuid: str) -> Dict[str, Any]:
    """Check if a workflow is finished.
    
    Args:
        workflow_uuid: The UUID of the workflow to check
        
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


def workflow_delete_data(workflow_uuid: str) -> Dict[str, str]:
    """Delete workflow data while keeping the workflow record.
    
    Args:
        workflow_uuid: The UUID of the workflow
        
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.delete_data()
    
    return {
        "message": f"Data for workflow {workflow_uuid} deleted successfully",
        "uuid": workflow_uuid
    }