"""
Plain Python functions for Rowan API operations.
These functions can be imported by the HTTP server without FastMCP decorators.
"""

import os
from typing import Any, Dict, List, Optional

try:
    import rowan
except ImportError:
    rowan = None

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if available
except ImportError:
    pass  # dotenv not required, but helpful if available

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if not api_key:
    raise ValueError(
        "ROWAN_API_KEY environment variable is required. "
        "Get your API key from https://labs.rowansci.com"
    )

if rowan is None:
    raise ImportError(
        "rowan-python package is required. Install with: pip install rowan-python"
    )

rowan.api_key = api_key


def rowan_pka(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None
) -> str:
    """Calculate pKa values for molecules."""
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="pka",
            folder_uuid=folder_uuid
        )
        
        pka_value = result.get("object_data", {}).get("strongest_acid")
        
        formatted = f"✅ pKa calculation for '{name}' completed!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
        
        if pka_value is not None:
            formatted += f"🧬 Strongest Acid pKa: {pka_value:.2f}\n"
        else:
            formatted += "⚠️ pKa result not yet available\n"
            
        return formatted
        
    except Exception as e:
        return f"❌ Error calculating pKa: {str(e)}"


def rowan_conformers(
    name: str,
    molecule: str,
    max_conformers: int = 10,
    folder_uuid: Optional[str] = None
) -> str:
    """Generate conformers for molecules."""
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="conformer_search",
            settings={"max_conformers": max_conformers},
            folder_uuid=folder_uuid
        )
        
        formatted = f"✅ Conformer search for '{name}' completed!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Unknown')}\n"
        formatted += f"🔍 Max Conformers: {max_conformers}\n"
        
        conformer_data = result.get("object_data", {})
        if "conformers" in conformer_data:
            formatted += f"📐 Conformers Found: {len(conformer_data['conformers'])}\n"
            
        return formatted
        
    except Exception as e:
        return f"❌ Error generating conformers: {str(e)}"


# Folder management functions
def rowan_folder_create(name: str, description: Optional[str] = None) -> str:
    """Create a new folder."""
    try:
        result = rowan.Folder.create(name=name)
        # Handle both object and dict responses
        uuid = result.get('uuid') if isinstance(result, dict) else getattr(result, 'uuid', 'N/A')
        return f"✅ Folder '{name}' created successfully!\n🆔 UUID: {uuid}"
    except Exception as e:
        return f"❌ Error creating folder: {str(e)}"


def rowan_folder_retrieve(folder_uuid: str) -> str:
    """Retrieve folder details."""
    try:
        folder = rowan.Folder.get(folder_uuid)
        formatted = f"📁 Folder Details:\n"
        formatted += f"🆔 UUID: {folder.uuid}\n"
        formatted += f"📝 Name: {folder.name}\n"
        formatted += f"📄 Description: {folder.description or 'None'}\n"
        formatted += f"⭐ Starred: {folder.starred}\n"
        formatted += f"🌍 Public: {folder.public}\n"
        formatted += f"📅 Created: {folder.created_at}\n"
        return formatted
    except Exception as e:
        return f"❌ Error retrieving folder: {str(e)}"


def rowan_folder_update(
    folder_uuid: str,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None
) -> str:
    """Update folder properties."""
    try:
        folder = rowan.Folder.get(folder_uuid)
        
        if name is not None:
            folder.name = name
        if parent_uuid is not None:
            folder.parent_uuid = parent_uuid
        if notes is not None:
            folder.notes = notes
        if starred is not None:
            folder.starred = starred
        if public is not None:
            folder.public = public
            
        folder.save()
        return f"✅ Folder updated successfully!\n🆔 UUID: {folder.uuid}\n📝 Name: {folder.name}"
    except Exception as e:
        return f"❌ Error updating folder: {str(e)}"


def rowan_folder_delete(folder_uuid: str) -> str:
    """Delete a folder."""
    try:
        folder = rowan.Folder.get(folder_uuid)
        folder.delete()
        return f"✅ Folder deleted successfully!\n🆔 UUID: {folder_uuid}"
    except Exception as e:
        return f"❌ Error deleting folder: {str(e)}"


def rowan_folder_list(
    name_contains: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """List folders with optional filters."""
    try:
        # Build filters
        filters = {}
        if name_contains:
            filters["name__icontains"] = name_contains
        if parent_uuid:
            filters["parent_uuid"] = parent_uuid
        if starred is not None:
            filters["starred"] = starred
        if public is not None:
            filters["public"] = public
        
        folders = rowan.Folder.objects.filter(**filters).page(page, size)
        
        formatted = f"📁 Folders (page {page}, size {size}):\n\n"
        
        for folder in folders:
            formatted += f"🆔 {folder.uuid}\n"
            formatted += f"📝 {folder.name}\n"
            formatted += f"📄 {folder.description or 'No description'}\n"
            if folder.starred:
                formatted += "⭐ Starred\n"
            formatted += f"📅 Created: {folder.created_at}\n"
            formatted += "─" * 40 + "\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error listing folders: {str(e)}"


# Add more functions as needed...
def rowan_workflow_create(
    name: str,
    workflow_type: str,
    initial_molecule: str,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: bool = False,
    public: bool = False,
    email_when_complete: bool = False,
    workflow_data: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new workflow."""
    
    # Validate workflow type
    VALID_WORKFLOWS = {
        "admet", "basic_calculation", "bde", "conformer_search", "descriptors", 
        "docking", "electronic_properties", "fukui", "hydrogen_bond_basicity", 
        "irc", "molecular_dynamics", "multistage_opt", "pka", "redox_potential", 
        "scan", "solubility", "spin_states", "tautomers"
    }
    
    # Strict validation - no auto-correction
    if workflow_type not in VALID_WORKFLOWS:
        error_msg = f"❌ Invalid workflow_type '{workflow_type}'.\n\n"
        error_msg += "🔧 **Available Rowan Workflow Types:**\n\n"
        
        # Group by common use cases for better guidance
        error_msg += "**🔬 Basic Calculations:**\n"
        error_msg += "• `basic_calculation` - Energy, optimization, frequencies\n"
        error_msg += "• `electronic_properties` - HOMO/LUMO, orbitals\n"
        error_msg += "• `multistage_opt` - Multi-level optimization\n\n"
        
        error_msg += "**🧬 Molecular Analysis:**\n"
        error_msg += "• `conformer_search` - Find molecular conformations\n"
        error_msg += "• `tautomers` - Tautomer enumeration\n"
        error_msg += "• `descriptors` - Molecular descriptors\n\n"
        
        error_msg += "**⚗️ Chemical Properties:**\n"
        error_msg += "• `pka` - pKa prediction\n"
        error_msg += "• `redox_potential` - Redox potentials\n"
        error_msg += "• `bde` - Bond dissociation energies\n"
        error_msg += "• `solubility` - Solubility prediction\n\n"
        
        error_msg += "**🧪 Drug Discovery:**\n"
        error_msg += "• `admet` - ADME-Tox properties\n"
        error_msg += "• `docking` - Protein-ligand docking\n\n"
        
        error_msg += "**🔬 Advanced Analysis:**\n"
        error_msg += "• `scan` - Potential energy scans\n"
        error_msg += "• `fukui` - Reactivity analysis\n"
        error_msg += "• `spin_states` - Spin state preferences\n"
        error_msg += "• `irc` - Reaction coordinate following\n"
        error_msg += "• `molecular_dynamics` - MD simulations\n"
        error_msg += "• `hydrogen_bond_basicity` - H-bond strength\n\n"
        
        raise ValueError(error_msg)
    
    try:
        workflow_kwargs = {
            "name": name,
            "workflow_type": workflow_type,
            "initial_molecule": initial_molecule,
            "starred": starred,
            "public": public,
            "email_when_complete": email_when_complete
        }
        
        if parent_uuid:
            workflow_kwargs["parent_uuid"] = parent_uuid
        if notes:
            workflow_kwargs["notes"] = notes
        if workflow_data:
            workflow_kwargs["workflow_data"] = workflow_data
            
        result = rowan.Workflow.create(**workflow_kwargs)
        
        formatted = f"✅ Workflow '{name}' created successfully!\n\n"
        formatted += f"🆔 UUID: {result.uuid}\n"
        formatted += f"🔬 Type: {workflow_type}\n"
        formatted += f"🧪 Molecule: {initial_molecule}\n"
        formatted += f"📊 Status: {result.status}\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error creating workflow: {str(e)}"


def rowan_workflow_retrieve(workflow_uuid: str) -> str:
    """Retrieve workflow details."""
    try:
        workflow = rowan.Workflow.get(workflow_uuid)
        
        formatted = f"🔬 Workflow Details:\n"
        formatted += f"🆔 UUID: {workflow.uuid}\n"
        formatted += f"📝 Name: {workflow.name}\n"
        formatted += f"🧪 Type: {workflow.workflow_type}\n"
        formatted += f"📊 Status: {workflow.status}\n"
        formatted += f"🧬 Molecule: {workflow.initial_molecule}\n"
        formatted += f"📅 Created: {workflow.created_at}\n"
        
        if workflow.notes:
            formatted += f"📄 Notes: {workflow.notes}\n"
        if workflow.starred:
            formatted += "⭐ Starred\n"
        if workflow.public:
            formatted += "🌍 Public\n"
            
        return formatted
        
    except Exception as e:
        return f"❌ Error retrieving workflow: {str(e)}"


# Add stub functions for other workflow operations
def rowan_workflow_update(workflow_uuid: str, **kwargs) -> str:
    """Update workflow properties."""
    try:
        workflow = rowan.Workflow.get(workflow_uuid)
        for key, value in kwargs.items():
            if hasattr(workflow, key) and value is not None:
                setattr(workflow, key, value)
        workflow.save()
        return f"✅ Workflow updated successfully!\n🆔 UUID: {workflow.uuid}"
    except Exception as e:
        return f"❌ Error updating workflow: {str(e)}"


def rowan_workflow_stop(workflow_uuid: str) -> str:
    """Stop a running workflow."""
    try:
        workflow = rowan.Workflow.get(workflow_uuid)
        workflow.stop()
        return f"✅ Workflow stopped successfully!\n🆔 UUID: {workflow_uuid}"
    except Exception as e:
        return f"❌ Error stopping workflow: {str(e)}"


def rowan_workflow_status(workflow_uuid: str) -> str:
    """Get workflow status."""
    try:
        workflow = rowan.Workflow.get(workflow_uuid)
        return f"📊 Workflow Status: {workflow.status}\n🆔 UUID: {workflow_uuid}"
    except Exception as e:
        return f"❌ Error getting workflow status: {str(e)}"


def rowan_workflow_is_finished(workflow_uuid: str) -> str:
    """Check if workflow is finished."""
    try:
        workflow = rowan.Workflow.get(workflow_uuid)
        finished = workflow.status in ["finished", "failed", "cancelled"]
        return f"✅ Workflow finished: {finished}\n📊 Status: {workflow.status}\n🆔 UUID: {workflow_uuid}"
    except Exception as e:
        return f"❌ Error checking workflow status: {str(e)}"


def rowan_workflow_delete(workflow_uuid: str) -> str:
    """Delete a workflow."""
    try:
        workflow = rowan.Workflow.get(workflow_uuid)
        workflow.delete()
        return f"✅ Workflow deleted successfully!\n🆔 UUID: {workflow_uuid}"
    except Exception as e:
        return f"❌ Error deleting workflow: {str(e)}"


def rowan_workflow_list(**kwargs) -> str:
    """List workflows with optional filtering.
    
    Returns:
        List of workflows
    """
    try:
        # Use the correct Rowan API method
        result = rowan.Workflow.list(**kwargs)
        
        workflows = result.get('workflows', [])
        num_pages = result.get('num_pages', 1)
        
        formatted = f"📋 Found {len(workflows)} workflows (Page {kwargs.get('page', 1)} of {num_pages}):\n\n"
        
        for workflow in workflows:
            formatted += f"🔬 {workflow.get('name', 'Unnamed')}\n"
            formatted += f"   UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"   Type: {workflow.get('object_type', 'N/A')}\n"
            formatted += f"   Status: {workflow.get('object_status', 'Unknown')}\n"
            formatted += f"   Created: {workflow.get('created_at', 'N/A')}\n\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error listing workflows: {str(e)}"


def rowan_calculation_retrieve(calculation_uuid: str) -> str:
    """Retrieve calculation details."""
    try:
        calculation = rowan.Calculation.get(calculation_uuid)
        
        formatted = f"🧮 Calculation Details:\n"
        formatted += f"🆔 UUID: {calculation.uuid}\n"
        formatted += f"📝 Name: {calculation.name}\n"
        formatted += f"📊 Status: {calculation.status}\n"
        formatted += f"🧪 Molecule: {calculation.molecule}\n"
        formatted += f"📅 Created: {calculation.created_at}\n"
        
        if hasattr(calculation, 'energy') and calculation.energy:
            formatted += f"⚡ Energy: {calculation.energy:.6f} Hartree\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error retrieving calculation: {str(e)}"


def rowan_docking(
    name: str,
    protein: str,
    ligand: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5,
    additional_params: Optional[Dict[str, Any]] = None
) -> str:
    """Run protein-ligand docking calculations."""
    try:
        # For docking workflows in Rowan, we need to check the exact format expected
        # Let's try different approaches based on what the API might accept
        
        approaches = []
        
        # Approach 1: Try PDB ID format (4-character codes)
        if len(protein) == 4 and protein.isalnum():
            approaches.append(("PDB ID", protein))
        
        # Approach 2: Try just the ligand SMILES (for small molecule only calculations)
        approaches.append(("Ligand only", ligand))
        
        # Approach 3: Try a structured format if docking supports it
        if len(protein) > 4:
            approaches.append(("Combined format", f"protein:{protein}|ligand:{ligand}"))
        
        last_error = None
        
        for approach_name, molecule_input in approaches:
            try:
                # Prepare kwargs for rowan.compute
                compute_kwargs = {
                    "name": f"{name} ({approach_name})",
                    "molecule": molecule_input,
                    "workflow_type": "docking",
                    "blocking": blocking,
                    "ping_interval": ping_interval
                }
                
                if folder_uuid:
                    compute_kwargs["folder_uuid"] = folder_uuid
                if additional_params:
                    compute_kwargs.update(additional_params)
                    
                result = rowan.compute(**compute_kwargs)
                
                # Format result for display
                formatted = f"✅ Docking calculation '{name}' completed successfully!\n\n"
                formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
                formatted += f"📊 Status: {result.get('status', 'Unknown')}\n"
                formatted += f"🧬 Approach: {approach_name}\n"
                formatted += f"🧬 Protein: {protein[:50]}{'...' if len(protein) > 50 else ''}\n"
                formatted += f"💊 Ligand: {ligand}\n"
                
                docking_data = result.get("object_data", {})
                if "binding_affinity" in docking_data:
                    formatted += f"🔗 Binding Affinity: {docking_data['binding_affinity']:.2f} kcal/mol\n"
                if "poses" in docking_data:
                    formatted += f"📐 Poses Generated: {len(docking_data['poses'])}\n"
                
                return formatted
                
            except Exception as e:
                last_error = e
                continue
        
        # If all approaches failed, provide helpful guidance
        error_msg = f"❌ Docking failed with all approaches. Last error: {str(last_error)}\n\n"
        error_msg += "🔧 **Troubleshooting Protein-Ligand Docking:**\n\n"
        error_msg += "**For protein input, try:**\n"
        error_msg += "• PDB ID (4 characters): `1ABC`\n"
        error_msg += "• Direct PDB file content\n\n"
        error_msg += "**For ligand input:**\n"
        error_msg += "• Valid SMILES string like: `CC(C)c1nc(cs1)CN(C)C(=O)N`\n\n"
        error_msg += "**Alternative approaches:**\n"
        error_msg += "• Use `rowan_compute()` with workflow_type='docking' and experiment with different molecule formats\n"
        error_msg += "• Check if your protein needs to be prepared/processed first\n"
        error_msg += "• Consider using PDB IDs from the Protein Data Bank\n\n"
        error_msg += "**Example working formats:**\n"
        error_msg += "• Protein: `1ABC` (PDB ID)\n"
        error_msg += "• Ligand: `CCO` (ethanol SMILES)\n"
        
        return error_msg
        
    except Exception as e:
        return f"❌ Error running docking: {str(e)}" 