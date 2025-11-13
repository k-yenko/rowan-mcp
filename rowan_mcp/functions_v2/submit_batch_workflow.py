"""
Rowan v2 API: Batch Workflow Submission
Submit multiple workflows of the same type with different molecules in a single call.
"""

from typing import Annotated, List
import json

# Import all workflow submission functions
from .submit_pka_workflow import submit_pka_workflow
from .submit_solubility_workflow import submit_solubility_workflow
from .submit_descriptors_workflow import submit_descriptors_workflow
from .submit_redox_potential_workflow import submit_redox_potential_workflow
from .submit_conformer_search_workflow import submit_conformer_search_workflow
from .submit_conformers_workflow import submit_conformers_workflow
from .submit_tautomer_search_workflow import submit_tautomer_search_workflow
from .submit_strain_workflow import submit_strain_workflow
from .submit_fukui_workflow import submit_fukui_workflow
from .submit_ion_mobility_workflow import submit_ion_mobility_workflow
from .submit_admet_workflow import submit_admet_workflow
from .submit_bde_workflow import submit_bde_workflow
from .submit_hydrogen_bond_basicity_workflow import submit_hydrogen_bond_basicity_workflow
from .submit_spin_states_workflow import submit_spin_states_workflow
from .submit_multistage_opt_workflow import submit_multistage_opt_workflow


def batch_submit_workflow(
    workflow_type: Annotated[str, "Type of workflow to run in batch (e.g., pka, descriptors, solubility, conformer_search)"],
    initial_molecules: Annotated[str, "JSON array of SMILES strings. Format: [\"CCO\", \"CCCO\", \"CCCCO\"] (no backslashes or outer quotes)"],
    workflow_data: Annotated[str, "JSON object of workflow-specific parameters. Format: {\"key\": \"value\"} or empty for defaults"] = "",
    names: Annotated[str, "Comma-separated workflow names OR JSON array. Format: Phenol pKa, Acetic Acid pKa OR [\"Name 1\", \"Name 2\"]. Auto-generated if empty"] = "",
    folder_uuid: Annotated[str, "UUID of folder to organize these workflows. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend per workflow. 0 for no limit"] = 0
):
    """Submit multiple workflows of the same type for different molecules using Rowan v2 API.

    FORMATTING NOTES (for MCP Inspector):
    - initial_molecules: Enter as JSON array without backslashes: ["CCO", "CCCO", "CCCCO"]
    - workflow_data: Enter as JSON object without backslashes: {"key": "value"}
    - names: Enter as comma-separated text OR JSON array: Phenol pKa, Acetic Acid pKa

    Args:
        workflow_type: Type of workflow to run (e.g., pka, descriptors, solubility, redox_potential)
        initial_molecules: JSON array of SMILES strings to process in batch
        workflow_data: JSON object of workflow-specific parameters (default: empty for defaults)
        names: Comma-separated workflow names or JSON array (default: auto-generated)
        folder_uuid: UUID of folder to organize workflows. Empty string uses default folder.
        max_credits: Maximum credits to spend per workflow. 0 for no limit.

    Processes multiple molecules through the same workflow type efficiently.
    Useful for:
    - High-throughput property prediction
    - Library screening
    - Dataset generation for machine learning
    - Systematic comparison of molecules

    Supported workflow types include:
    'pka', 'descriptors', 'solubility', 'redox_potential', 'conformer_search',
    'tautomers', 'strain', 'ion_mobility', 'fukui', and more.
    Note: 'nmr' requires subscription upgrade and is not currently available.

    Returns:
        List of Workflow objects representing the submitted workflows

    Examples:
        # Batch pKa calculations (MCP Inspector format)
        workflow_type: pka
        initial_molecules: ["Oc1ccccc1", "CC(=O)O", "c1c[nH]cn1"]
        names: Phenol pKa, Acetic Acid pKa, Imidazole pKa

        # Batch descriptor generation
        workflow_type: descriptors
        initial_molecules: ["CCO", "CCCO", "CCCCO", "CCCCCO"]
        names: Ethanol, Propanol, Butanol, Pentanol

        # Batch conformer search with custom settings
        workflow_type: conformer_search
        initial_molecules: ["CCOCC", "c1ccccc1C", "CC(C)C"]
        workflow_data: {"conf_gen_mode": "rapid", "final_method": "aimnet2_wb97md3"}

        # Batch solubility predictions
        workflow_type: solubility
        initial_molecules: ["CC(=O)Nc1ccc(O)cc1", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"]
        workflow_data: {"solvents": ["water", "ethanol"], "temperatures": [298.15, 310.15]}

    Time varies based on workflow type and number of molecules.
    """

    # Parse initial_molecules (always a string in MCP)
    try:
        parsed_molecules = json.loads(initial_molecules)
    except (json.JSONDecodeError, ValueError):
        # Try comma-separated
        if ',' in initial_molecules:
            parsed_molecules = [s.strip() for s in initial_molecules.split(',') if s.strip()]
        else:
            parsed_molecules = [initial_molecules.strip()]

    # Strip whitespace from all SMILES strings
    parsed_molecules = [s.strip() for s in parsed_molecules]

    # Parse workflow_data if provided
    parsed_workflow_data = {}
    if workflow_data:
        try:
            parsed_workflow_data = json.loads(workflow_data)
        except json.JSONDecodeError:
            pass  # Use empty dict if invalid JSON

    # Parse names if provided
    parsed_names = None
    if names:
        try:
            parsed_names = json.loads(names)
        except (json.JSONDecodeError, ValueError):
            # Try comma-separated
            if ',' in names:
                parsed_names = [n.strip() for n in names.split(',') if n.strip()]
            else:
                parsed_names = [names.strip()]

    # Auto-generate names if not provided
    if not parsed_names:
        parsed_names = [f"{workflow_type.replace('_', ' ').title()} {i+1}" for i in range(len(parsed_molecules))]

    # Ensure we have the right number of names
    if len(parsed_names) != len(parsed_molecules):
        # Pad with auto-generated names or truncate
        if len(parsed_names) < len(parsed_molecules):
            parsed_names.extend([
                f"{workflow_type.replace('_', ' ').title()} {i+1}"
                for i in range(len(parsed_names), len(parsed_molecules))
            ])
        else:
            parsed_names = parsed_names[:len(parsed_molecules)]

    # Get the workflow submission function dynamically
    workflow_func_map = {
        'pka': submit_pka_workflow,
        'solubility': submit_solubility_workflow,
        'descriptors': submit_descriptors_workflow,
        'redox_potential': submit_redox_potential_workflow,
        'conformer_search': submit_conformer_search_workflow,
        'conformers': submit_conformers_workflow,
        'tautomers': submit_tautomer_search_workflow,
        'tautomer_search': submit_tautomer_search_workflow,
        'strain': submit_strain_workflow,
        'fukui': submit_fukui_workflow,
        'ion_mobility': submit_ion_mobility_workflow,
        'admet': submit_admet_workflow,
        'bde': submit_bde_workflow,
        'hydrogen_bond_basicity': submit_hydrogen_bond_basicity_workflow,
        'spin_states': submit_spin_states_workflow,
        'multistage_opt': submit_multistage_opt_workflow,
    }

    if workflow_type not in workflow_func_map:
        raise ValueError(
            f"Unsupported workflow type: {workflow_type}. "
            f"Supported types: {', '.join(workflow_func_map.keys())}"
        )

    submit_func = workflow_func_map[workflow_type]

    # Submit workflows individually (batch pattern from Rowan API)
    results = []
    for i, smiles in enumerate(parsed_molecules):
        # Prepare workflow arguments with SMILES string (not Molecule object)
        workflow_args = {
            'initial_molecule': smiles,  # Pass SMILES string to wrapper function
            'name': parsed_names[i],
            'folder_uuid': folder_uuid,
            'max_credits': max_credits,
        }

        # Add workflow-specific data from workflow_data
        workflow_args.update(parsed_workflow_data)

        # Submit workflow - wrapper functions handle all parsing and make public
        workflow = submit_func(**workflow_args)

        results.append(workflow)

    return results
