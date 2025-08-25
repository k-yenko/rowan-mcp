"""
Rowan workflow management functions for MCP tool integration.
"""

from typing import Optional, Dict, Any, Union, List, Literal
import rowan

def safe_get_attr(obj, attr: str, default=None):
    """Safely get an attribute from an object, returning default if it doesn't exist."""
    try:
        return getattr(obj, attr, default)
    except (AttributeError, TypeError):
        return default

def rowan_workflow_management(
    action: Literal['create', 'retrieve', 'update', 'stop', 'status', 'is_finished', 'delete', 'list'],
    workflow_uuid: Optional[str] = None,
    name: Optional[str] = None,
    workflow_type: Optional[str] = None,
    initial_molecule: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    email_when_complete: Optional[bool] = None,
    workflow_data: Optional[Dict[str, Any]] = None,
    name_contains: Optional[str] = None,
    object_status: Optional[int] = None,
    object_type: Optional[str] = None,
    page: int = 0,
    size: int = 50
) -> str:
    """Unified workflow management tool for all workflow operations. Available actions: create, retrieve, update, stop, status, is_finished, delete, list.
    
    **Available Actions:**
    - **create**: Create a new workflow (requires: name, workflow_type, initial_molecule)
    - **retrieve**: retrieve workflow details (requires: workflow_uuid)
    - **update**: Update workflow properties (requires: workflow_uuid, optional: name, parent_uuid, notes, starred, public, email_when_complete)
    - **stop**: Stop a running workflow (requires: workflow_uuid)
    - **status**: Check workflow status (requires: workflow_uuid)
    - **is_finished**: Check if workflow is finished (requires: workflow_uuid)
    - **delete**: Delete a workflow (requires: workflow_uuid)
    - **list**: List workflows with filters (optional: name_contains, parent_uuid, starred, public, object_status, object_type, page, size)
    
    Args:
        action: Action to perform - must be one of: 'create', 'retrieve', 'update', 'stop', 'status', 'is_finished', 'delete', 'list'
        workflow_uuid: UUID of the workflow (required for retrieve, update, stop, status, is_finished, delete)
        name: Workflow name (required for create, optional for update)
        workflow_type: Type of workflow (required for create)
        initial_molecule: Initial molecule SMILES (required for create)
        parent_uuid: Parent folder UUID (optional for create/update)
        notes: Workflow notes (optional for create/update)
        starred: Star the workflow (optional for create/update)
        public: Make workflow public (optional for create/update)
        email_when_complete: Email when complete (optional for create/update)
        workflow_data: Additional workflow data (optional for create)
        name_contains: Filter by name containing text (optional for list)
        object_status: Filter by status (0=queued, 1=running, 2=completed, 3=failed, 4=stopped, optional for list)
        object_type: Filter by workflow type (optional for list)
        page: Page number for pagination (default: 1, for list)
        size: Results per page (default: 50, for list)
    
    Returns:
        Results of the workflow operation
    """
    
    action = action.lower()
    
    try:
        if action == "create":
            if not all([name, workflow_type, initial_molecule]):
                return " Error: 'name', 'workflow_type', and 'initial_molecule' are required for creating a workflow"
            
            # Validate workflow type
            VALID_WORKFLOWS = {
                "admet", "basic_calculation", "conformer_search", "descriptors", 
                "docking", "electronic_properties", "fukui", 
                "irc", "molecular_dynamics", "multistage_opt", "pka", "redox_potential", 
                "scan", "solubility", "spin_states", "tautomers"
            }
            
            if workflow_type not in VALID_WORKFLOWS:
                error_msg = f" Invalid workflow_type '{workflow_type}'.\n\n"
                error_msg += " **Available Rowan Workflow Types:**\n"
                error_msg += f"{', '.join(sorted(VALID_WORKFLOWS))}"
                return error_msg
            
            workflow = rowan.Workflow.create(
                name=name,
                workflow_type=workflow_type,
                initial_molecule=initial_molecule,
                parent_uuid=parent_uuid,
                notes=notes or "",
                starred=starred or False,
                public=public or False,
                email_when_complete=email_when_complete or False,
                workflow_data=workflow_data or {}
            )
            
            formatted = f" Workflow '{name}' created successfully!\n\n"
            formatted += f" UUID: {safe_get_attr(workflow, 'uuid', 'N/A')}\n"
            formatted += f" Type: {workflow_type}\n"
            formatted += f" Status: {safe_get_attr(workflow, 'object_status', 'Unknown')}\n"
            formatted += f" Created: {safe_get_attr(workflow, 'created_at', 'N/A')}\n"
            return formatted
            
        elif action == "retrieve":
            if not workflow_uuid:
                return " Error: 'workflow_uuid' is required for retrieving a workflow"
            
            try:
                workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
            except Exception as e:
                return f" Error retrieving workflow: {str(e)}"
            
            # Handle workflow as dictionary (which is what Rowan API returns)
            def safe_get_dict_value(data, key, default='N/A'):
                """Safely get a value from a dictionary."""
                if isinstance(data, dict):
                    return data.get(key, default)
                return safe_get_attr(data, key, default)
            
            # Get status and interpret it
            status = safe_get_dict_value(workflow, 'object_status', 'Unknown')
            status_names = {
                0: "Queued",
                1: "Running", 
                2: "Completed",
                3: "Failed",
                4: "Stopped",
                5: "Awaiting Queue"
            }
            status_name = status_names.get(status, f"Unknown ({status})")
            
            formatted = f" Workflow Details:\n\n"
            formatted += f" Name: {safe_get_dict_value(workflow, 'name', 'N/A')}\n"
            formatted += f" UUID: {safe_get_dict_value(workflow, 'uuid', 'N/A')}\n"
            formatted += f" Type: {safe_get_dict_value(workflow, 'object_type', 'N/A')}\n"
            formatted += f" Status: {status_name} ({status})\n"
            formatted += f" Parent: {safe_get_dict_value(workflow, 'parent_uuid', 'Root')}\n"
            formatted += f" Starred: {'Yes' if safe_get_dict_value(workflow, 'starred', False) else 'No'}\n"
            formatted += f" Public: {'Yes' if safe_get_dict_value(workflow, 'public', False) else 'No'}\n"
            formatted += f" Created: {safe_get_dict_value(workflow, 'created_at', 'N/A')}\n"
            formatted += f" Elapsed: {safe_get_dict_value(workflow, 'elapsed', 0):.2f}s\n"
            formatted += f" Credits: {safe_get_dict_value(workflow, 'credits_charged', 0)}\n"
            formatted += f" Notes: {safe_get_dict_value(workflow, 'notes', 'None')}\n\n"
            
            # If workflow is completed (status 2), extract and show results
            if status == 2:
                formatted += f" **Workflow Completed Successfully!**\n\n"
                
                # Show basic completion details
                credits_charged = safe_get_dict_value(workflow, 'credits_charged', 0)
                elapsed_time = safe_get_dict_value(workflow, 'elapsed', 0)
                if credits_charged or elapsed_time:
                    formatted += f" Workflow used {credits_charged} credits and ran for {elapsed_time:.2f}s\n\n"
                
                # Debug: Show all available keys in the workflow dictionary
                if isinstance(workflow, dict):
                    workflow_keys = list(workflow.keys())
                    formatted += f" **Debug - Available Workflow Keys:**\n"
                    formatted += f" {', '.join(workflow_keys)}\n\n"
                else:
                    # Fallback for object-based workflows
                    workflow_attrs = []
                    for attr in dir(workflow):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(workflow, attr)
                                if not callable(value):
                                    workflow_attrs.append(attr)
                            except:
                                pass
                    formatted += f" **Debug - Available Workflow Attributes:**\n"
                    formatted += f" {', '.join(workflow_attrs)}\n\n"
                
                # Extract actual results from object_data
                object_data = safe_get_dict_value(workflow, 'object_data', {})
                workflow_type = safe_get_dict_value(workflow, 'object_type', '')
                
                formatted += f" **Results Analysis:**\n"
                formatted += f" Workflow Type: {workflow_type}\n"
                formatted += f" Object Data Present: {'Yes' if object_data else 'No'}\n"
                
                if object_data:
                    formatted += f" Object Data Keys: {list(object_data.keys()) if isinstance(object_data, dict) else 'Not a dictionary'}\n\n"
                    formatted += extract_workflow_results(workflow_type, object_data)
                else:
                    formatted += f" **No results data found in workflow object_data**\n"
                    formatted += f" This could mean:\n"
                    formatted += f" • The workflow completed but didn't generate data\n"
                    formatted += f" • The results are stored in a different attribute\n"
                    formatted += f" • There was an issue with the workflow execution\n"
            
            elif status == 1:  # Running
                formatted += f" **Workflow is currently running...**\n"
                formatted += f" Check back later or use `rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')` for updates\n"
            elif status == 0:  # Queued
                formatted += f" **Workflow is queued and waiting to start**\n"
                formatted += f" Use `rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')` to check progress\n"
            elif status == 3:  # Failed
                formatted += f" **Workflow failed**\n"
                formatted += f" Check the workflow details in the Rowan web interface for error messages\n"
            elif status == 4:  # Stopped
                formatted += f" **Workflow was stopped**\n"
            
            return formatted
            
        elif action == "update":
            if not workflow_uuid:
                return " Error: 'workflow_uuid' is required for updating a workflow"
            
            # Build update parameters according to Rowan API docs
            update_params = {'uuid': workflow_uuid}
            updates_made = []
            
            if name is not None:
                update_params['name'] = name
                updates_made.append(f"name: {name}")
            if parent_uuid is not None:
                update_params['parent_uuid'] = parent_uuid
                updates_made.append(f"parent_uuid: {parent_uuid}")
            if notes is not None:
                update_params['notes'] = notes
                updates_made.append(f"notes: {notes}")
            if starred is not None:
                update_params['starred'] = starred
                updates_made.append(f"starred: {starred}")
            if public is not None:
                update_params['public'] = public
                updates_made.append(f"public: {public}")
            if email_when_complete is not None:
                update_params['email_when_complete'] = email_when_complete
                updates_made.append(f"email_when_complete: {email_when_complete}")
            
            if len(update_params) == 1:  # Only UUID provided
                return " Error: At least one field must be provided for updating (name, parent_uuid, notes, starred, public, email_when_complete)"
            
            # Call Rowan API with correct parameter structure
            workflow = rowan.Workflow.update(**update_params)
            
            # Format response using the returned workflow object
            formatted = f" Workflow updated successfully!\n\n"
            formatted += f" UUID: {safe_get_attr(workflow, 'uuid', workflow_uuid)}\n"
            formatted += f" Name: {safe_get_attr(workflow, 'name', 'N/A')}\n"
            formatted += f" Type: {safe_get_attr(workflow, 'object_type', 'N/A')}\n"
            formatted += f" Parent: {safe_get_attr(workflow, 'parent_uuid', 'Root')}\n"
            formatted += f" Starred: {'Yes' if safe_get_attr(workflow, 'starred', False) else 'No'}\n"
            formatted += f" Public: {'Yes' if safe_get_attr(workflow, 'public', False) else 'No'}\n"
            formatted += f" Email on Complete: {'Yes' if safe_get_attr(workflow, 'email_when_complete', False) else 'No'}\n"
            formatted += f" Notes: {safe_get_attr(workflow, 'notes', 'None')}\n\n"
            
            formatted += f" **Updates Applied:**\n"
            for update in updates_made:
                formatted += f"• {update}\n"
            
            return formatted
            
        elif action in ["stop", "status", "is_finished"]:
            if not workflow_uuid:
                return f" Error: 'workflow_uuid' is required for {action} action"
            
            if action == "stop":
                result = rowan.Workflow.stop(uuid=workflow_uuid)
                return f" Workflow stop request submitted. Result: {result}"
            elif action == "status":
                workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
                
                # Handle workflow as dictionary
                def safe_get_dict_value(data, key, default='N/A'):
                    if isinstance(data, dict):
                        return data.get(key, default)
                    return safe_get_attr(data, key, default)
                
                status = safe_get_dict_value(workflow, 'object_status', 'Unknown')
                status_names = {
                    0: "Queued",
                    1: "Running", 
                    2: "Completed",
                    3: "Failed",
                    4: "Stopped",
                    5: "Awaiting Queue"
                }
                status_name = status_names.get(status, f"Unknown ({status})")
                
                formatted = f" **Workflow Status**: {status_name} ({status})\n"
                formatted += f" UUID: {workflow_uuid}\n"
                formatted += f" Name: {safe_get_dict_value(workflow, 'name', 'N/A')}\n"
                formatted += f" Elapsed: {safe_get_dict_value(workflow, 'elapsed', 0):.2f}s\n"
                
                if status == 2:
                    formatted += f" **Completed successfully!** Use 'retrieve' action to get results.\n"
                elif status == 1:
                    formatted += f" **Currently running...** Check back later for results.\n"
                elif status == 0:
                    formatted += f" **Queued and waiting to start**\n"
                elif status == 3:
                    formatted += f" **Failed** - Check workflow details for error information.\n"
                elif status == 4:
                    formatted += f" **Stopped**\n"
                    
                return formatted
            elif action == "is_finished":
                workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
                
                # Handle workflow as dictionary
                def safe_get_dict_value(data, key, default='N/A'):
                    if isinstance(data, dict):
                        return data.get(key, default)
                    return safe_get_attr(data, key, default)
                
                status = safe_get_dict_value(workflow, 'object_status', 'Unknown')
                is_finished = status in [2, 3, 4]  # Completed, Failed, or Stopped
                
                formatted = f" **Workflow Finished Check**\n"
                formatted += f" UUID: {workflow_uuid}\n"
                formatted += f" Status: {status}\n"
                formatted += f" Finished: {'Yes' if is_finished else 'No'}\n"
                
                if is_finished:
                    if status == 2:
                        formatted += f" Use 'retrieve' action to get results\n"
                    elif status == 3:
                        formatted += f" Workflow failed - check details for error info\n"
                    elif status == 4:
                        formatted += f" Workflow was stopped\n"
                else:
                    formatted += f" Workflow is still {['queued', 'running'][status] if status in [0, 1] else 'in progress'}\n"
                    
                return formatted
                
        elif action == "delete":
            if not workflow_uuid:
                return " Error: 'workflow_uuid' is required for deleting a workflow"
            
            result = rowan.Workflow.delete(uuid=workflow_uuid)
            return f" Workflow deletion request submitted. Result: {result}"
            
        elif action == "list":
            # Build filters
            filters = {
                'page': page,
                'size': min(size * 5, 250)  # Get more workflows to sort properly, cap at 250
            }
            
            if name_contains:
                filters['name_contains'] = name_contains
            if parent_uuid:
                filters['parent_uuid'] = parent_uuid
            if starred is not None:
                filters['starred'] = starred
            if public is not None:
                filters['public'] = public
            if object_status is not None:
                filters['object_status'] = object_status
            if object_type:
                filters['object_type'] = object_type
            
            workflows = rowan.Workflow.list(**filters)
            
            # Sort workflows by created_at in descending order (most recent first)
            if 'workflows' in workflows and workflows['workflows']:
                from datetime import datetime
                
                def parse_date(date_str):
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        return datetime.min
                
                sorted_workflows = sorted(
                    workflows['workflows'], 
                    key=lambda w: parse_date(w.get('created_at', '')),
                    reverse=True
                )
                
                # Remove object_logfile from each workflow and return only the requested number
                cleaned_workflows = []
                for workflow in sorted_workflows[:size]:
                    cleaned_workflow = {k: v for k, v in workflow.items() if k != 'object_logfile'}
                    cleaned_workflows.append(cleaned_workflow)
                
                workflows['workflows'] = cleaned_workflows
            
            return workflows
            
        else:
            return f" Error: Unknown action '{action}'. Available actions: create, retrieve, update, stop, status, is_finished, delete, list"
            
    except Exception as e:
        return f" Error in workflow management: {str(e)}"

def extract_workflow_results(workflow_type: str, object_data: Dict[str, Any]) -> str:
    """Extract and format workflow results - simple raw data display."""
    
    formatted = f" **{workflow_type.replace('_', ' ').title()} Results:**\n\n"
    
    import json
    try:
        # Pretty print the object_data as JSON
        formatted += f"```json\n{json.dumps(object_data, indent=2, default=str)}\n```\n"
    except Exception as e:
        # Fallback if JSON serialization fails
        formatted += f"Raw object_data:\n{str(object_data)}\n"
        formatted += f"(JSON serialization failed: {e})\n"
    
    return formatted

def test_rowan_workflow_management():
    """Test the workflow management function."""
    try:
        # Test list action
        result = rowan_workflow_management("list", size=5)
        print(" Workflow management test successful!")
        print(f"Sample result: {result[:200]}...")
        return True
    except Exception as e:
        print(f" Workflow management test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_workflow_management() 