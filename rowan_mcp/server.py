"""
Rowan MCP Server Implementation using FastMCP
"""

import os
import sys
from fastmcp import FastMCP


# Import v2 API functions
from .functions_v2.submit_basic_calculation_workflow import submit_basic_calculation_workflow
from .functions_v2.submit_conformer_search_workflow import submit_conformer_search_workflow
from .functions_v2.submit_solubility_workflow import submit_solubility_workflow
from .functions_v2.submit_pka_workflow import submit_pka_workflow
from .functions_v2.submit_redox_potential_workflow import submit_redox_potential_workflow
from .functions_v2.submit_fukui_workflow import submit_fukui_workflow
from .functions_v2.submit_tautomer_search_workflow import submit_tautomer_search_workflow
from .functions_v2.submit_descriptors_workflow import submit_descriptors_workflow
from .functions_v2.submit_scan_workflow import submit_scan_workflow
from .functions_v2.submit_irc_workflow import submit_irc_workflow
from .functions_v2.submit_protein_cofolding_workflow import submit_protein_cofolding_workflow
from .functions_v2.submit_docking_workflow import submit_docking_workflow
from .functions_v2.submit_macropka_workflow import submit_macropka_workflow

# Import new v2.1.9 workflow functions
from .functions_v2.submit_strain_workflow import submit_strain_workflow
# from .functions_v2.submit_nmr_workflow import submit_nmr_workflow  # Commented out - requires subscription upgrade
from .functions_v2.submit_ion_mobility_workflow import submit_ion_mobility_workflow
from .functions_v2.submit_double_ended_ts_search_workflow import submit_double_ended_ts_search_workflow
from .functions_v2.submit_pose_analysis_md_workflow import submit_pose_analysis_md_workflow
from .functions_v2.submit_batch_docking_workflow import submit_batch_docking_workflow
from .functions_v2.submit_msa_workflow import submit_msa_workflow
from .functions_v2.submit_batch_workflow import batch_submit_workflow

# Import generic-access workflow functions
from .functions_v2.submit_admet_workflow import submit_admet_workflow
# from .functions_v2.submit_bde_workflow import submit_bde_workflow  # Commented out - tricky return structure
from .functions_v2.submit_conformers_workflow import submit_conformers_workflow
# from .functions_v2.submit_electronic_properties_workflow import submit_electronic_properties_workflow  # Commented out - returns ~100MB data, needs visualization
from .functions_v2.submit_hydrogen_bond_basicity_workflow import submit_hydrogen_bond_basicity_workflow
# from .functions_v2.submit_molecular_dynamics_workflow import submit_molecular_dynamics_workflow  # Commented out - workflow in beta
from .functions_v2.submit_multistage_opt_workflow import submit_multistage_opt_workflow
from .functions_v2.submit_spin_states_workflow import submit_spin_states_workflow

# Import molecule lookup functions
from .functions_v2.molecule_lookup import (
    molecule_lookup,
    batch_molecule_lookup,
    validate_smiles
)

# Import workflow management functions
from .functions_v2.workflow_management_v2 import (
    workflow_wait_for_result,
    workflow_stop,
    workflow_delete,
    retrieve_workflow,
    retrieve_calculation_molecules,
    list_workflows,
    workflow_update,
    workflow_delete_data
)

# Import protein management functions
from .functions_v2.protein_management import (
    create_protein_from_pdb_id,
    retrieve_protein,
    list_proteins,
    upload_protein,
    delete_protein,
    sanitize_protein
)

# Import folder management functions
from .functions_v2.folder_management_v2 import (
    create_folder,
    retrieve_folder,
    list_folders,
    update_folder,
    delete_folder
)

# Import project management functions
from .functions_v2.project_management_v2 import (
    create_project,
    retrieve_project,
    list_projects,
    update_project,
    delete_project,
    get_default_project
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize FastMCP server
mcp = FastMCP("Rowan MCP Server")

# Register v2 API tools
mcp.tool()(submit_basic_calculation_workflow)
mcp.tool()(submit_conformer_search_workflow)
mcp.tool()(submit_solubility_workflow)
mcp.tool()(submit_pka_workflow)
mcp.tool()(submit_redox_potential_workflow)
mcp.tool()(submit_fukui_workflow)
mcp.tool()(submit_tautomer_search_workflow)
mcp.tool()(submit_descriptors_workflow)
mcp.tool()(submit_scan_workflow)
mcp.tool()(submit_irc_workflow)
mcp.tool()(submit_protein_cofolding_workflow)
mcp.tool()(submit_docking_workflow)
mcp.tool()(submit_macropka_workflow)

# Register new v2.1.9 workflow tools
mcp.tool()(submit_strain_workflow)
# mcp.tool()(submit_nmr_workflow)  # Commented out - requires subscription upgrade
mcp.tool()(submit_ion_mobility_workflow)
mcp.tool()(submit_double_ended_ts_search_workflow)
mcp.tool()(submit_pose_analysis_md_workflow)
mcp.tool()(submit_batch_docking_workflow)
mcp.tool()(submit_msa_workflow)
mcp.tool()(batch_submit_workflow)

# Register generic-access workflow tools
mcp.tool()(submit_admet_workflow)
# mcp.tool()(submit_bde_workflow)  # Commented out - tricky return structure
mcp.tool()(submit_conformers_workflow)
# mcp.tool()(submit_electronic_properties_workflow)  # Commented out - returns ~100MB data, needs visualization
mcp.tool()(submit_hydrogen_bond_basicity_workflow)
# mcp.tool()(submit_molecular_dynamics_workflow)  # Commented out - workflow in beta
mcp.tool()(submit_multistage_opt_workflow)
mcp.tool()(submit_spin_states_workflow)

# Register molecule lookup tools
mcp.tool()(molecule_lookup)
mcp.tool()(batch_molecule_lookup)
mcp.tool()(validate_smiles)

# Register workflow management tools
# mcp.tool()(workflow_wait_for_result)  # Removed - all tools should be non-blocking
mcp.tool()(workflow_stop)
mcp.tool()(workflow_delete)
mcp.tool()(retrieve_workflow)  # THE single source of truth for workflow status & data
mcp.tool()(retrieve_calculation_molecules)
mcp.tool()(list_workflows)
mcp.tool()(workflow_update)
mcp.tool()(workflow_delete_data)

# Register protein management tools
mcp.tool()(create_protein_from_pdb_id)
mcp.tool()(retrieve_protein)
mcp.tool()(list_proteins)
mcp.tool()(upload_protein)
mcp.tool()(delete_protein)
mcp.tool()(sanitize_protein)

# Register folder management tools
mcp.tool()(create_folder)
mcp.tool()(retrieve_folder)
mcp.tool()(list_folders)
mcp.tool()(update_folder)
mcp.tool()(delete_folder)

# Register project management tools
mcp.tool()(create_project)
mcp.tool()(retrieve_project)
mcp.tool()(list_projects)
mcp.tool()(update_project)
mcp.tool()(delete_project)
mcp.tool()(get_default_project)

# Validate required configuration
if not os.getenv("ROWAN_API_KEY"):
    raise ValueError(
        "ROWAN_API_KEY environment variable is required. "
        "Get your API key from https://labs.rowansci.com"
    )


def main() -> None:
    """Main entry point for the MCP server."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Rowan MCP Server", file=sys.stderr)
        print("Usage: rowan-mcp [--transport=stdio|http] [--port=6276]", file=sys.stderr)
        print("Environment variables:", file=sys.stderr)
        print("  ROWAN_API_KEY    # Required: Your Rowan API key", file=sys.stderr)
        return

    # Parse command line arguments
    transport = "stdio"
    port = 6276

    for arg in sys.argv[1:]:
        if arg.startswith("--transport="):
            transport = arg.split("=")[1]
        elif arg.startswith("--port="):
            port = int(arg.split("=")[1])

    # Check for environment variable override
    if os.getenv("MCP_TRANSPORT"):
        transport = os.getenv("MCP_TRANSPORT")
    if os.getenv("MCP_PORT"):
        port = int(os.getenv("MCP_PORT"))

    if transport == "http":
        print(f"Starting Rowan MCP Server with HTTP transport on port {port}", file=sys.stderr)
        mcp.run(transport="http", host="localhost", port=port)
    else:
        print("Starting Rowan MCP Server with STDIO transport", file=sys.stderr)
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
