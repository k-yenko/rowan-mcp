"""
Rowan v2 API: Workflow Management Tools
MCP tools for interacting with Workflow objects returned by v2 API submission functions.
"""

from typing import Optional, Dict, Any, List, Annotated
from pydantic import Field
import rowan


def workflow_get_status(
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow to check status")
    ]
) -> Dict[str, Any]:
    """Get the current status of a workflow.
    
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
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow to wait for completion")
    ],
    poll_interval: Annotated[
        int,
        Field(description="Seconds between status checks while waiting")
    ] = 5
) -> Dict[str, Any]:
    """Wait for a workflow to complete and return the result.
    
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
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the running workflow to stop")
    ]
) -> Dict[str, str]:
    """Stop a running workflow.
    
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
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow to permanently delete")
    ]
) -> Dict[str, str]:
    """Delete a workflow.
    
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
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow to fetch latest data")
    ],
    in_place: Annotated[
        bool,
        Field(description="Whether to update the workflow object in place")
    ] = False
) -> Dict[str, Any]:
    """Fetch the latest workflow data from the database.
    
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
    uuid: Annotated[
        str,
        Field(description="UUID of the workflow to retrieve")
    ]
) -> Dict[str, Any]:
    """Retrieve a workflow from the API.
    
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
    parent_uuid: Annotated[
        Optional[str],
        Field(description="UUID of parent folder to filter by. None for all folders")
    ] = None,
    name_contains: Annotated[
        Optional[str],
        Field(description="Substring to search for in workflow names. None for all names")
    ] = None,
    public: Annotated[
        Optional[bool],
        Field(description="Filter by public status. None for both public and private")
    ] = None,
    starred: Annotated[
        Optional[bool],
        Field(description="Filter by starred status. None for both starred and unstarred")
    ] = None,
    status: Annotated[
        Optional[int],
        Field(description="Filter by workflow status code. None for all statuses")
    ] = None,
    workflow_type: Annotated[
        Optional[str],
        Field(description="Filter by workflow type (e.g., 'conformer_search', 'pka'). None for all types")
    ] = None,
    page: Annotated[
        int,
        Field(description="Page number for pagination (0-indexed)")
    ] = 0,
    size: Annotated[
        int,
        Field(description="Number of workflows per page")
    ] = 10
) -> List[Dict[str, Any]]:
    """List workflows subject to the specified criteria.
    
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


def retrieve_calculation_molecules(
    uuid: Annotated[
        str,
        Field(description="UUID of the calculation to retrieve molecules from")
    ]
) -> List[Dict[str, Any]]:
    """Retrieve a list of molecules from a calculation.
    
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
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow to update")
    ],
    name: Annotated[
        Optional[str],
        Field(description="New name for the workflow. None to keep current name")
    ] = None,
    notes: Annotated[
        Optional[str],
        Field(description="New notes/description for the workflow. None to keep current notes")
    ] = None,
    starred: Annotated[
        Optional[bool],
        Field(description="Set starred status (True/False). None to keep current status")
    ] = None,
    public: Annotated[
        Optional[bool],
        Field(description="Set public visibility (True/False). None to keep current status")
    ] = None
) -> Dict[str, Any]:
    """Update workflow details.
    
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


def workflow_is_finished(
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow to check completion status")
    ]
) -> Dict[str, Any]:
    """Check if a workflow is finished.
    
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
    workflow_uuid: Annotated[
        str,
        Field(description="UUID of the workflow whose data to delete (keeps workflow record)")
    ]
) -> Dict[str, str]:
    """Delete workflow data while keeping the workflow record.
    
    Returns:
        Dictionary with confirmation message
    """
    workflow = rowan.retrieve_workflow(workflow_uuid)
    workflow.delete_data()
    
    return {
        "message": f"Data for workflow {workflow_uuid} deleted successfully",
        "uuid": workflow_uuid
    }