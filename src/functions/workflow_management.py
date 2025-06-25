"""
Rowan workflow management functions for MCP tool integration.
"""

from typing import Optional, Dict, Any, Union, List
import rowan


def rowan_workflow_management(
    action: str,
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
    page: int = 1,
    size: int = 50
) -> str:
    """Unified workflow management tool for all workflow operations.
    
    **Available Actions:**
    - **create**: Create a new workflow (requires: name, workflow_type, initial_molecule)
    - **retrieve**: Get workflow details (requires: workflow_uuid)
    - **update**: Update workflow properties (requires: workflow_uuid, optional: name, parent_uuid, notes, starred, public, email_when_complete)
    - **stop**: Stop a running workflow (requires: workflow_uuid)
    - **status**: Check workflow status (requires: workflow_uuid)
    - **is_finished**: Check if workflow is finished (requires: workflow_uuid)
    - **delete**: Delete a workflow (requires: workflow_uuid)
    - **list**: List workflows with filters (optional: name_contains, parent_uuid, starred, public, object_status, object_type, page, size)
    
    Args:
        action: Action to perform ('create', 'retrieve', 'update', 'stop', 'status', 'is_finished', 'delete', 'list')
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
                return "❌ Error: 'name', 'workflow_type', and 'initial_molecule' are required for creating a workflow"
            
            # Validate workflow type
            VALID_WORKFLOWS = {
                "admet", "basic_calculation", "bde", "conformer_search", "descriptors", 
                "docking", "electronic_properties", "fukui", "hydrogen_bond_basicity", 
                "irc", "molecular_dynamics", "multistage_opt", "pka", "redox_potential", 
                "scan", "solubility", "spin_states", "tautomers"
            }
            
            if workflow_type not in VALID_WORKFLOWS:
                error_msg = f"❌ Invalid workflow_type '{workflow_type}'.\n\n"
                error_msg += "🔧 **Available Rowan Workflow Types:**\n"
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
            
            formatted = f"✅ Workflow '{name}' created successfully!\n\n"
            formatted += f"🔬 UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"⚗️ Type: {workflow_type}\n"
            formatted += f"📊 Status: {workflow.get('object_status', 'Unknown')}\n"
            formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
            return formatted
            
        elif action == "retrieve":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for retrieving a workflow"
            
            workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
            
            # Get status and interpret it
            status = workflow.get('object_status', 'Unknown')
            status_names = {
                0: "Queued",
                1: "Running", 
                2: "Completed",
                3: "Failed",
                4: "Stopped",
                5: "Awaiting Queue"
            }
            status_name = status_names.get(status, f"Unknown ({status})")
            
            formatted = f"🔬 Workflow Details:\n\n"
            formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
            formatted += f"🆔 UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"⚗️ Type: {workflow.get('object_type', 'N/A')}\n"
            formatted += f"📊 Status: {status_name} ({status})\n"
            formatted += f"📂 Parent: {workflow.get('parent_uuid', 'Root')}\n"
            formatted += f"⭐ Starred: {'Yes' if workflow.get('starred') else 'No'}\n"
            formatted += f"🌐 Public: {'Yes' if workflow.get('public') else 'No'}\n"
            formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
            formatted += f"⏱️ Elapsed: {workflow.get('elapsed', 0):.2f}s\n"
            formatted += f"💰 Credits: {workflow.get('credits_charged', 0)}\n"
            formatted += f"📝 Notes: {workflow.get('notes', 'None')}\n\n"
            
            # If workflow is completed (status 2), extract and show results
            if status == 2:
                formatted += f"✅ **Workflow Completed Successfully!**\n\n"
                
                # Show basic completion details
                if workflow.get('credits_charged'):
                    formatted += f"✅ Workflow used {workflow.get('credits_charged')} credits and ran for {workflow.get('elapsed', 0):.2f}s\n\n"
                
                # Extract actual results from object_data
                object_data = workflow.get('object_data', {})
                if object_data:
                    formatted += extract_workflow_results(workflow.get('object_type', ''), object_data)
                else:
                    formatted += f"⚠️ No results data found in workflow object_data\n"
            
            elif status == 1:  # Running
                formatted += f"🔄 **Workflow is currently running...**\n"
                formatted += f"💡 Check back later or use `rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')` for updates\n"
            elif status == 0:  # Queued
                formatted += f"⏳ **Workflow is queued and waiting to start**\n"
                formatted += f"💡 Use `rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')` to check progress\n"
            elif status == 3:  # Failed
                formatted += f"❌ **Workflow failed**\n"
                formatted += f"💡 Check the workflow details in the Rowan web interface for error messages\n"
            elif status == 4:  # Stopped
                formatted += f"⏹️ **Workflow was stopped**\n"
                
            return formatted
            
        elif action == "update":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for updating a workflow"
            
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if parent_uuid is not None:
                update_data['parent_uuid'] = parent_uuid
            if notes is not None:
                update_data['notes'] = notes
            if starred is not None:
                update_data['starred'] = starred
            if public is not None:
                update_data['public'] = public
            if email_when_complete is not None:
                update_data['email_when_complete'] = email_when_complete
            
            if not update_data:
                return "❌ Error: At least one field must be provided for updating (name, parent_uuid, notes, starred, public, email_when_complete)"
            
            workflow = rowan.Workflow.update(uuid=workflow_uuid, **update_data)
            
            formatted = f"✅ Workflow updated successfully!\n\n"
            formatted += f"🆔 UUID: {workflow_uuid}\n"
            for key, value in update_data.items():
                formatted += f"📝 {key.replace('_', ' ').title()}: {value}\n"
            
            return formatted
            
        elif action in ["stop", "status", "is_finished"]:
            if not workflow_uuid:
                return f"❌ Error: 'workflow_uuid' is required for {action} action"
            
            if action == "stop":
                result = rowan.Workflow.stop(uuid=workflow_uuid)
                return f"⏹️ Workflow stop request submitted. Result: {result}"
            elif action == "status":
                workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
                status = workflow.get('object_status', 'Unknown')
                status_names = {
                    0: "Queued",
                    1: "Running", 
                    2: "Completed",
                    3: "Failed",
                    4: "Stopped",
                    5: "Awaiting Queue"
                }
                status_name = status_names.get(status, f"Unknown ({status})")
                
                formatted = f"📊 **Workflow Status**: {status_name} ({status})\n"
                formatted += f"🆔 UUID: {workflow_uuid}\n"
                formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
                formatted += f"⏱️ Elapsed: {workflow.get('elapsed', 0):.2f}s\n"
                
                if status == 2:
                    formatted += f"✅ **Completed successfully!** Use 'retrieve' action to get results.\n"
                elif status == 1:
                    formatted += f"🔄 **Currently running...** Check back later for results.\n"
                elif status == 0:
                    formatted += f"⏳ **Queued and waiting to start**\n"
                elif status == 3:
                    formatted += f"❌ **Failed** - Check workflow details for error information.\n"
                elif status == 4:
                    formatted += f"⏹️ **Stopped**\n"
                    
                return formatted
            elif action == "is_finished":
                workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
                status = workflow.get('object_status', 'Unknown')
                is_finished = status in [2, 3, 4]  # Completed, Failed, or Stopped
                
                formatted = f"🔍 **Workflow Finished Check**\n"
                formatted += f"🆔 UUID: {workflow_uuid}\n"
                formatted += f"📊 Status: {status}\n"
                formatted += f"✅ Finished: {'Yes' if is_finished else 'No'}\n"
                
                if is_finished:
                    if status == 2:
                        formatted += f"💡 Use 'retrieve' action to get results\n"
                    elif status == 3:
                        formatted += f"💡 Workflow failed - check details for error info\n"
                    elif status == 4:
                        formatted += f"💡 Workflow was stopped\n"
                else:
                    formatted += f"💡 Workflow is still {['queued', 'running'][status] if status in [0, 1] else 'in progress'}\n"
                    
                return formatted
                
        elif action == "delete":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for deleting a workflow"
            
            result = rowan.Workflow.delete(uuid=workflow_uuid)
            return f"🗑️ Workflow deletion request submitted. Result: {result}"
            
        elif action == "list":
            # Build filters
            filters = {
                'page': page,
                'size': size
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
            
            if not workflows or 'results' not in workflows:
                return "📋 No workflows found matching the criteria"
            
            results = workflows['results']
            total_count = workflows.get('total_count', len(results))
            
            formatted = f"📋 **Workflows** (showing {len(results)} of {total_count} total)\n\n"
            
            status_names = {
                0: "Queued",
                1: "Running", 
                2: "Completed",
                3: "Failed",
                4: "Stopped",
                5: "Awaiting Queue"
            }
            
            for workflow in results:
                status = workflow.get('object_status', 'Unknown')
                status_name = status_names.get(status, f"Unknown ({status})")
                
                formatted += f"🔬 **{workflow.get('name', 'Unnamed')}**\n"
                formatted += f"   🆔 {workflow.get('uuid', 'N/A')}\n"
                formatted += f"   ⚗️ {workflow.get('object_type', 'N/A')} | 📊 {status_name}\n"
                formatted += f"   📅 {workflow.get('created_at', 'N/A')} | ⏱️ {workflow.get('elapsed', 0):.1f}s\n\n"
            
            # Pagination info
            if total_count > len(results):
                formatted += f"📄 Page {page} of {(total_count - 1) // size + 1} | Use 'page' parameter to navigate\n"
            
            return formatted
            
        else:
            return f"❌ Error: Unknown action '{action}'. Available actions: create, retrieve, update, stop, status, is_finished, delete, list"
            
    except Exception as e:
        return f"❌ Error in workflow management: {str(e)}"


def extract_workflow_results(workflow_type: str, object_data: Dict[str, Any]) -> str:
    """Extract and format workflow results based on type."""
    
    if workflow_type == 'solubility':
        if 'solubilities' in object_data:
            formatted = f"🧪 **Solubility Results (log S):**\n\n"
            solubilities = object_data['solubilities']
            
            if isinstance(solubilities, dict):
                # Define temperature range based on typical solubility workflow
                # Most solubility workflows use 5 temperatures: 273.15, 298.15, 323.15, 348.15, 373.15 K
                default_temps = [273.15, 298.15, 323.15, 348.15, 373.15]  # Kelvin
                
                for solvent_smiles, solvent_data in solubilities.items():
                    # Convert SMILES to common name if possible
                    solvent_names = {
                        'O': 'Water', 'CCO': 'Ethanol', 'CCCCCC': 'Hexane',
                        'CC(=O)C': 'Acetone', 'CS(=O)C': 'DMSO', 'CC#N': 'Acetonitrile',
                        'CC1=CC=CC=C1': 'Toluene', 'C1CCCO1': 'THF'
                    }
                    solvent_name = solvent_names.get(solvent_smiles, solvent_smiles)
                    
                    formatted += f"**{solvent_name} ({solvent_smiles}):**\n"
                    
                    if isinstance(solvent_data, dict):
                        solubilities_vals = solvent_data.get('solubilities', [])
                        uncertainties_vals = solvent_data.get('uncertainties', [])
                        
                        # Match solubility values with temperatures
                        for i, sol_val in enumerate(solubilities_vals):
                            temp_k = default_temps[i] if i < len(default_temps) else 298.15
                            temp_c = temp_k - 273.15
                            
                            uncertainty = f" ± {uncertainties_vals[i]:.3f}" if i < len(uncertainties_vals) else ""
                            formatted += f"  • {temp_c:.0f}°C: {sol_val:.3f}{uncertainty} log S\n"
                    else:
                        formatted += f"  • {solvent_data}\n"
                    
                    formatted += "\n"
            else:
                formatted += f"Raw data: {solubilities}\n"
            
            return formatted
    
    elif workflow_type == 'electronic_properties':
        formatted = f"🔋 **Electronic Properties:**\n\n"
        
        # HOMO/LUMO energies
        if 'molecular_orbitals' in object_data:
            mo_data = object_data['molecular_orbitals']
            if isinstance(mo_data, dict) and 'energies' in mo_data:
                energies = mo_data['energies']
                occupations = mo_data.get('occupations', [])
                
                if energies and occupations:
                    homo_idx = None
                    lumo_idx = None
                    for i, occ in enumerate(occupations):
                        if occ > 0.5:
                            homo_idx = i
                        elif occ < 0.5 and lumo_idx is None:
                            lumo_idx = i
                            break
                    
                    if homo_idx is not None and lumo_idx is not None:
                        homo_energy = energies[homo_idx]
                        lumo_energy = energies[lumo_idx]
                        gap = lumo_energy - homo_energy
                        
                        formatted += f"• HOMO: {homo_energy:.4f} hartree ({homo_energy * 27.2114:.2f} eV)\n"
                        formatted += f"• LUMO: {lumo_energy:.4f} hartree ({lumo_energy * 27.2114:.2f} eV)\n"
                        formatted += f"• Gap: {gap:.4f} hartree ({gap * 27.2114:.2f} eV)\n\n"
        
        # Dipole moment
        if 'dipole' in object_data:
            dipole = object_data['dipole']
            if isinstance(dipole, dict) and 'magnitude' in dipole:
                formatted += f"• Dipole: {dipole['magnitude']:.4f} Debye\n\n"
            elif isinstance(dipole, (int, float)):
                formatted += f"• Dipole: {dipole:.4f} Debye\n\n"
        
        return formatted
    
    else:
        # Generic formatting for other workflow types
        formatted = f"📋 **{workflow_type.replace('_', ' ').title()} Results:**\n\n"
        
        # Show key-value pairs if they're simple
        for key, value in list(object_data.items())[:5]:
            if isinstance(value, (int, float)):
                formatted += f"• {key}: {value:.4f}\n"
            elif isinstance(value, str) and len(value) < 100:
                formatted += f"• {key}: {value}\n"
            elif isinstance(value, list) and len(value) < 5:
                formatted += f"• {key}: {value}\n"
            else:
                formatted += f"• {key}: <data available>\n"
        
        if len(object_data) > 5:
            formatted += f"... and {len(object_data) - 5} more properties\n"
        
        return formatted


def test_rowan_workflow_management():
    """Test the workflow management function."""
    try:
        # Test list action
        result = rowan_workflow_management("list", size=5)
        print("✅ Workflow management test successful!")
        print(f"Sample result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Workflow management test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_workflow_management() 