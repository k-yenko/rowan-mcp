"""
System management operations for Rowan API.
"""

import os
import sys
import rowan
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Configure rowan API key
if not hasattr(rowan, 'api_key') or not rowan.api_key:
    api_key = os.getenv("ROWAN_API_KEY")
    if api_key:
        rowan.api_key = api_key
        logger.info("Rowan API key configured")
    else:
        logger.error("No ROWAN_API_KEY found in environment")

def rowan_system_management(
    action: str,
    job_uuid: Optional[str] = None,
    log_level: Optional[str] = None
) -> str:
    """Unified system management tool for server utilities and information.
    
    **Available Actions:**
    - **help**: Get list of all available Rowan MCP tools with descriptions
    - **server_info**: Get server status and configuration information
    - **server_status**: Check server health and connectivity
    - **set_log_level**: Set logging level for debugging (requires: log_level)
    - **job_redirect**: Redirect legacy job queries to workflow management (requires: job_uuid)
    
    Args:
        action: Action to perform ('help', 'server_info', 'server_status', 'set_log_level', 'job_redirect')
        job_uuid: UUID of the job (required for job_redirect)
        log_level: Logging level - DEBUG, INFO, WARNING, ERROR (required for set_log_level)
    
    Returns:
        Results of the system operation
    """
    
    action = action.lower()
    
    try:
        if action == "help":
            result = "**Available Rowan MCP Tools** \n\n"
            
            result += "**Now with unified management tools!**\n"
            result += "Each tool has tailored documentation and parameters.\n\n"
            
            # Group by common use cases
            result += "**Quantum Chemistry & Basic Calculations:**\n"
            result += "• `rowan_electronic_properties` - HOMO/LUMO, orbitals\n"
            result += "• `rowan_multistage_opt` - Multi-level optimization (for geometry)\n\n"
            
            result += "**Molecular Analysis:**\n"
            result += "• `rowan_conformers` - Find molecular conformations\n"
            result += "• `rowan_tautomers` - Tautomer enumeration\n"
            result += "• `rowan_descriptors` - Molecular descriptors for ML\n\n"
            
            result += "**Chemical Properties:**\n"
            result += "• `rowan_pka` - pKa prediction\n"
            result += "• `rowan_redox_potential` - Redox potentials vs SCE\n"
            result += "• `rowan_bde` - Bond dissociation energies\n"
            result += "• `rowan_solubility` - Solubility prediction\n\n"
            
            result += "**Drug Discovery:**\n"
            result += "• `rowan_admet` - ADME-Tox properties\n"
            result += "• `rowan_docking` - Protein-ligand docking\n\n"
            
            result += "**Advanced Analysis:**\n"
            result += "• `rowan_scan` - Potential energy surface scans (bond/angle/dihedral)\n"
            result += "• `rowan_fukui` - Reactivity analysis\n"
            result += "• `rowan_spin_states` - Spin state preferences\n"
            result += "• `rowan_irc` - Reaction coordinate following\n"
            result += "• `rowan_molecular_dynamics` - MD simulations\n"
            result += "• `rowan_hydrogen_bond_basicity` - H-bond strength\n\n"
            
            result += "**Usage Guidelines:**\n"
            result += "• For geometry optimization: use `rowan_multistage_opt`\n"
            result += "• For conformer search: use `rowan_conformers`\n"
            result += "• For pKa prediction: use `rowan_pka`\n"
            result += "• For electronic structure: use `rowan_electronic_properties`\n"
            result += "• For drug properties: use `rowan_admet`\n"
            result += "• For reaction mechanisms: use `rowan_scan` then `rowan_irc`\n"
            result += "• For potential energy scans: use `rowan_scan` with coordinate specification\n\n"
            
            result += "**Management Tools:**\n"
            result += "• `rowan_folder_management` - Unified folder operations (create, retrieve, update, delete, list)\n"
            result += "• `rowan_workflow_management` - Unified workflow operations (create, retrieve, update, stop, status, delete, list)\n"
            result += "• `rowan_system_management` - System utilities (help, set_log_level, job_redirect)\n"
            result += "• `rowan_calculation_retrieve` - Get calculation results\n"
            result += "• `rowan_molecule_lookup` - SMILES lookup for common molecules\n\n"
            
            result += "**Total Available:** 20+ specialized tools + management tools\n"
            result += "**Each tool has specific documentation - check individual tool descriptions**\n"
            result += "**Management tools use 'action' parameter to specify operation**\n"
            
            return result
            
        elif action == "server_info":
            result = "**Rowan MCP Server Information**\n\n"
            
            # Server configuration
            result += "**Configuration:**\n"
            result += f"• API Key: {'Configured' if os.getenv('ROWAN_API_KEY') else 'Missing'}\n"
            result += f"• Rowan Package: {'Available' if rowan else 'Not Found'}\n"
            result += f"• Log Level: {logger.level}\n"
            result += f"• Python Version: {sys.version.split()[0]}\n\n"
            
            # Available tools count
            result += f"**Available Tools:** 20+ specialized computational chemistry tools\n"
            result += f"• Core Calculations: 4 tools (electronic_properties, multistage_opt, etc.)\n"
            result += f"• Molecular Analysis: 3 tools (conformers, tautomers, descriptors)\n"
            result += f"• Chemical Properties: 4 tools (pka, redox_potential, bde, solubility)\n"
            result += f"• Advanced Analysis: 6 tools (scan, fukui, spin_states, irc, md, etc.)\n"
            result += f"• Drug Discovery: 2 tools (admet, docking)\n"
            result += f"• Management Tools: 5 tools (workflow, folder, system, etc.)\n\n"
            
            # Quick status check
            try:
                # Try a simple API call to test connectivity
                recent_workflows = rowan.Workflow.list(size=1)
                total_workflows = len(recent_workflows.get('workflows', []))
                result += f"**API Connectivity:** Connected\n"
                result += f"**Workflow Check:** {total_workflows} workflows accessible\n\n"
            except Exception as e:
                result += f"**API Connectivity:** Error: {str(e)[:100]}...\n\n"
            
            result += f"**Usage:**\n"
            result += f"• Use rowan_system_management(action='help') for tool descriptions\n"
            result += f"• Use rowan_workflow_management(action='list') to see your workflows\n"
            result += f"• Note: Folder management currently has API issues - use workflow organization instead\n"
            
            return result
            
        elif action == "server_status":
            result = "**Rowan MCP Server Health Check**\n\n"
            
            # Test API connectivity with workflow endpoint (the main one)
            status_checks = []
            
            # Test workflow list
            try:
                workflows = rowan.Workflow.list(size=1)
                workflow_count = len(workflows.get('workflows', []))
                status_checks.append(("Workflow API", "OK", f"{workflow_count} workflows accessible"))
            except Exception as e:
                status_checks.append(("Workflow API", "Error", str(e)[:50]))
            
            # Test workflow retrieve (if we have any workflows)
            try:
                workflows = rowan.Workflow.list(size=1)
                if workflows.get('workflows'):
                    first_workflow_uuid = workflows['workflows'][0]['uuid']
                    rowan.Workflow.retrieve(uuid=first_workflow_uuid)
                    status_checks.append(("Workflow Retrieve", "OK", "Can access workflow details"))
                else:
                    status_checks.append(("Workflow Retrieve", "Skipped", "No workflows to test"))
            except Exception as e:
                status_checks.append(("Workflow Retrieve", "Error", str(e)[:50]))
            
            # Display results
            for check_name, status, details in status_checks:
                result += f"**{check_name}:** {status}\n"
                result += f"  Details: {details}\n\n"
            
            # Overall status
            all_ok = all("OK" in check[1] or "Skipped" in check[1] for check in status_checks)
            result += f"**Overall Status:** {'All Systems Operational' if all_ok else 'Some Issues Detected'}\n\n"
            
            if not all_ok:
                result += f"**Troubleshooting:**\n"
                result += f"• Check your ROWAN_API_KEY environment variable\n"
                result += f"• Verify internet connectivity\n"
                result += f"• Check Rowan service status at labs.rowansci.com\n"
            
            return result
            
        elif action == "set_log_level":
            if not log_level:
                return "Error: 'log_level' is required for set_log_level action"
            
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            log_level = log_level.upper()
            
            if log_level not in valid_levels:
                return f"Invalid log level. Use one of: {', '.join(valid_levels)}"
            
            logger.setLevel(getattr(logging, log_level))
            logger.info(f"Log level changed to: {log_level}")
            
            return f"Log level set to {log_level}"
            
        elif action == "job_redirect":
            if not job_uuid:
                return "Error: 'job_uuid' is required for job_redirect action"
            
            # Try to treat the job_uuid as a workflow_uuid and retrieve results directly
            try:
                workflow = rowan.Workflow.retrieve(uuid=job_uuid)
                
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
                
                formatted = f"**Found Workflow {job_uuid}:**\n\n"
                formatted += f"Name: {workflow.get('name', 'N/A')}\n"
                formatted += f"Type: {workflow.get('object_type', 'N/A')}\n"
                formatted += f"Status: {status_name} ({status})\n"
                formatted += f"Created: {workflow.get('created_at', 'N/A')}\n"
                formatted += f"Elapsed: {workflow.get('elapsed', 0):.2f}s\n\n"
                
                if status == 2:  # Completed
                    formatted += f"**Getting Results...**\n\n"
                    
                    # Try to retrieve calculation results
                    try:
                        calc_result = rowan.Calculation.retrieve(uuid=job_uuid)
                        
                        # Extract workflow type to provide specific result formatting
                        workflow_type = workflow.get('object_type', '')
                        
                        if workflow_type == 'electronic_properties':
                            formatted += f"**Electronic Properties Results:**\n\n"
                            
                            # Extract key electronic properties from the result
                            object_data = calc_result.get('object_data', {})
                            
                            # Molecular orbital energies (HOMO/LUMO)
                            if 'molecular_orbitals' in object_data:
                                mo_data = object_data['molecular_orbitals']
                                if isinstance(mo_data, dict) and 'energies' in mo_data:
                                    energies = mo_data['energies']
                                    if isinstance(energies, list) and len(energies) > 0:
                                        # Find HOMO/LUMO
                                        occupations = mo_data.get('occupations', [])
                                        if occupations:
                                            homo_idx = None
                                            lumo_idx = None
                                            for i, occ in enumerate(occupations):
                                                if occ > 0.5:  # Occupied
                                                    homo_idx = i
                                                elif occ < 0.5 and lumo_idx is None:  # First unoccupied
                                                    lumo_idx = i
                                                    break
                                            
                                            if homo_idx is not None and lumo_idx is not None:
                                                homo_energy = energies[homo_idx]
                                                lumo_energy = energies[lumo_idx]
                                                gap = lumo_energy - homo_energy
                                                
                                                formatted += f"• HOMO Energy: {homo_energy:.4f} hartree ({homo_energy * 27.2114:.2f} eV)\n"
                                                formatted += f"• LUMO Energy: {lumo_energy:.4f} hartree ({lumo_energy * 27.2114:.2f} eV)\n"
                                                formatted += f"• HOMO-LUMO Gap: {gap:.4f} hartree ({gap * 27.2114:.2f} eV)\n\n"
                            
                            # Dipole moment
                            if 'dipole' in object_data:
                                dipole = object_data['dipole']
                                if isinstance(dipole, dict) and 'magnitude' in dipole:
                                    formatted += f"**Dipole Moment:** {dipole['magnitude']:.4f} Debye\n\n"
                                elif isinstance(dipole, (int, float)):
                                    formatted += f"**Dipole Moment:** {dipole:.4f} Debye\n\n"
                            
                            # If no specific electronic properties found, show available keys
                            if not any(key in object_data for key in ['molecular_orbitals', 'dipole']):
                                if object_data:
                                    formatted += f"**Available Properties:** {', '.join(object_data.keys())}\n\n"
                                else:
                                    formatted += f"**No electronic properties data found in results**\n\n"
                        
                        else:
                            # For other workflow types, show general calculation results
                            formatted += f"**{workflow_type.replace('_', ' ').title()} Results:**\n\n"
                            
                            object_data = calc_result.get('object_data', {})
                            if object_data:
                                # Show first few key-value pairs
                                count = 0
                                for key, value in object_data.items():
                                    if count >= 5:  # Limit to first 5 items for job_redirect
                                        formatted += f"   ... and {len(object_data) - 5} more properties\n"
                                        break
                                    
                                    # Format the value nicely
                                    if isinstance(value, (int, float)):
                                        formatted += f"• **{key}**: {value}\n"
                                    elif isinstance(value, str):
                                        formatted += f"• **{key}**: {value[:50]}{'...' if len(value) > 50 else ''}\n"
                                    elif isinstance(value, list):
                                        formatted += f"• **{key}**: {len(value)} items\n"
                                    elif isinstance(value, dict):
                                        formatted += f"• **{key}**: {len(value)} properties\n"
                                    else:
                                        formatted += f"• **{key}**: {type(value).__name__}\n"
                                    count += 1
                                formatted += "\n"
                            else:
                                formatted += f"**No calculation data found in results**\n\n"
                        
                    except Exception as retrieve_error:
                        formatted += f"**Results retrieval failed:** {str(retrieve_error)}\n\n"
                
                elif status in [0, 1, 5]:  # Still running
                    formatted += f"**Workflow is still {status_name.lower()}**\n"
                    formatted += f"Check back later for results\n\n"
                
                elif status == 3:  # Failed
                    formatted += f"**Workflow failed**\n"
                    formatted += f"Check the workflow parameters and try again\n\n"
                
                formatted += f"**For more details:**\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{job_uuid}') for full workflow details\n"
                formatted += f"• Use rowan_calculation_retrieve('{job_uuid}') for raw calculation data\n"
                
                return formatted
                
            except Exception as e:
                # If workflow retrieval fails, provide the legacy guidance
                formatted = f"**Could not find workflow {job_uuid}:** {str(e)}\n\n"
                formatted += f"**Important Note:**\n"
                formatted += f"Rowan manages computations through workflows, not individual jobs.\n"
                formatted += f"The job/results concept is legacy from older versions.\n\n"
                formatted += f"**To find your workflow:**\n"
                formatted += f"• Use rowan_workflow_management(action='list') to see all workflows\n"
                formatted += f"• Look for workflows with similar names or recent creation times\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='UUID') to get results\n\n"
                formatted += f"**Migration Guide:**\n"
                formatted += f"• Old: rowan_job_status('{job_uuid}') → New: rowan_workflow_management(action='status', workflow_uuid='UUID')\n"
                formatted += f"• Old: rowan_job_results('{job_uuid}') → New: rowan_workflow_management(action='retrieve', workflow_uuid='UUID')\n"
                
                return formatted
            
        else:
            return f"Error: Unknown action '{action}'. Available actions: help, server_info, server_status, set_log_level, job_redirect"
            
    except Exception as e:
        return f"Error in system {action}: {str(e)}"


def test_rowan_system_management():
    """Test the rowan_system_management function."""
    try:
        # Test the help action
        result = rowan_system_management(action="help")
        print("System management test successful!")
        print(f"Result length: {len(result)} characters")
        print(f"First line: {result.split(chr(10))[0]}")
        return True
    except Exception as e:
        print(f"System management test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_system_management() 