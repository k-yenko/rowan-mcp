"""
Rowan v2 API: Batch Docking Workflow
Perform high-throughput molecular docking of multiple ligands against a single protein target.
"""

from typing import Annotated
import rowan
import stjames
import json


def submit_batch_docking_workflow(
    smiles_list: Annotated[str, "JSON string list of ligand SMILES to dock (e.g., '[\"CCO\", \"CC(=O)O\", \"c1ccccc1\"]')"],
    protein: Annotated[str, "Protein UUID or PDB content/path for docking target"],
    pocket: Annotated[str, "JSON string defining binding pocket coordinates or 'auto' for automatic detection"],
    executable: Annotated[str, "Docking software to use: 'vina', 'qvina2', 'smina'"] = "qvina2",
    scoring_function: Annotated[str, "Scoring function: 'vina', 'vinardo', 'ad4'"] = "vina",
    exhaustiveness: Annotated[int, "Search exhaustiveness parameter (higher = more thorough, slower)"] = 8,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Batch Docking Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a batch docking workflow for high-throughput virtual screening using Rowan v2 API.

    Args:
        smiles_list: JSON string list of ligand SMILES strings to dock
        protein: Protein for docking. Can be: 1) PDB ID string (e.g., '1HCK'), 2) Protein UUID string
        pocket: Binding pocket as JSON string "[[x1,y1,z1], [x2,y2,z2]]" defining box corners
        executable: Docking software (default: 'qvina2'). Options: 'vina', 'qvina2', 'smina'
        scoring_function: Scoring function (default: 'vina'). Options: 'vina', 'vinardo', 'ad4'
        exhaustiveness: Search exhaustiveness (default: 8). Higher values = more thorough but slower
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Performs high-throughput docking of multiple ligands against a single protein target.
    Useful for:
    - Virtual screening campaigns
    - Lead optimization
    - Fragment library screening
    - Structure-activity relationship studies

    Returns:
        Workflow object representing the submitted workflow

    Example:
        # CDK2 batch docking screen (shortened from 111 to 5 ligands)
        result = submit_batch_docking_workflow(
            smiles_list='["CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1", "CCC(C)CN=C1NCC2(CCCOC2)CN1", "CC(C)CCNC1=NCC2CC(COC2=N)O1", "CCC(CC)NC1=NCC2CC(CO)CC12", "CCC(C)CN=C1NC=C2CCC(O)CC2=N1"]',
            protein="1HCK",
            pocket="[[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]]",
            name="Docking CDK2"
        )

    """
    import logging
    logger = logging.getLogger(__name__)

    # Parse smiles_list (always a string in MCP)
    try:
        parsed_smiles_list = json.loads(smiles_list)
    except (json.JSONDecodeError, ValueError):
        # Try comma-separated format
        if ',' in smiles_list:
            parsed_smiles_list = [s.strip() for s in smiles_list.split(',') if s.strip()]
        else:
            parsed_smiles_list = [smiles_list.strip()]

    # Handle protein parameter
    protein_obj = None

    # Try to parse protein as JSON first
    try:
        protein_dict = json.loads(protein)
        if isinstance(protein_dict, dict):
            protein = protein_dict
    except (json.JSONDecodeError, ValueError):
        # Not JSON, keep as string
        pass

    # Check if protein is a PDB ID or UUID
    if isinstance(protein, str):
        if len(protein) == 36 and '-' in protein:
            # It's a UUID, retrieve the protein
            logger.info(f"Using existing protein UUID: {protein}")
            protein_obj = rowan.retrieve_protein(protein)
        elif len(protein) <= 6:  # PDB IDs are typically 4 characters
            # It's a PDB ID, create protein from it
            logger.info(f"Creating protein from PDB ID: {protein}")

            # Get or create a project (REQUIRED for v2.1.9)
            project_uuid = None
            try:
                project = rowan.default_project()
                project_uuid = project.uuid
                logger.info(f"Using default project: {project_uuid}")
            except Exception as e:
                logger.info(f"Could not get default project: {e}")
                try:
                    projects = rowan.list_projects(size=1)
                    if projects:
                        project_uuid = projects[0].uuid
                        logger.info(f"Using existing project: {project_uuid}")
                    else:
                        new_project = rowan.create_project(name="Batch Docking Project")
                        project_uuid = new_project.uuid
                        logger.info(f"Created new project: {project_uuid}")
                except Exception as e2:
                    logger.error(f"Failed to get/create project: {e2}")
                    raise ValueError(f"Cannot create protein without a valid project. Error: {e2}")

            protein_obj = rowan.create_protein_from_pdb_id(
                name=f"Protein from {protein}",
                code=protein,
                project_uuid=project_uuid
            )
            logger.info(f"Created protein with UUID: {protein_obj.uuid}")

            # Sanitize the protein
            logger.info("Sanitizing protein for docking...")
            try:
                protein_obj.sanitize()

                import time
                max_wait = 30
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    time.sleep(2)
                    protein_obj.refresh()
                    if protein_obj.sanitized and protein_obj.sanitized != 0:
                        logger.info(f"Protein sanitized successfully")
                        break
                else:
                    logger.warning(f"Sanitization may not be complete after {max_wait} seconds")
            except Exception as e:
                logger.warning(f"Sanitization failed: {e}")
        else:
            raise ValueError(f"Invalid protein parameter: {protein}")
    else:
        protein_obj = protein

    # Parse pocket parameter
    try:
        parsed_pocket = json.loads(pocket)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid pocket format: {pocket}. Expected JSON string like \"[[x1,y1,z1], [x2,y2,z2]]\"")

    if not isinstance(parsed_pocket, list) or len(parsed_pocket) != 2:
        raise ValueError(f"Pocket must be a list with exactly 2 coordinate lists")

    parsed_pocket = [list(coord) for coord in parsed_pocket]

    # Submit the workflow
    logger.info(f"Submitting batch docking workflow for {len(parsed_smiles_list)} ligands")

    result = rowan.submit_batch_docking_workflow(
        smiles_list=parsed_smiles_list,
        protein=protein_obj,
        pocket=parsed_pocket,
        executable=executable,
        scoring_function=scoring_function,
        exhaustiveness=exhaustiveness,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    logger.info(f"Batch docking workflow submitted with UUID: {result.uuid}")

    return result
