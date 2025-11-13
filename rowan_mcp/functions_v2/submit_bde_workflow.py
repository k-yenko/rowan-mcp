"""
Rowan v2 API: Bond Dissociation Energy (BDE) Workflow
Calculate bond dissociation energies for molecular bonds.
"""

from typing import Annotated
import rowan
import stjames
import json


def submit_bde_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for BDE calculations"],
    optimize_fragments: Annotated[bool, "Whether to optimize the resulting fragments after bond cleavage"] = True,
    atoms: Annotated[str, "JSON string list of atom indices to calculate BDEs for. Empty string for automatic selection"] = "",
    fragment_indices: Annotated[str, "JSON string list of lists specifying fragment atom groups. Empty string for automatic"] = "",
    all_CH: Annotated[bool, "Calculate BDEs for all C-H bonds in the molecule"] = False,
    all_CX: Annotated[bool, "Calculate BDEs for all C-X bonds where X is any heavy atom"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "BDE Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit a bond dissociation energy (BDE) workflow.

    Args:
        initial_molecule: SMILES string representing the molecule
        optimize_fragments: Optimize fragment geometries after bond cleavage (default: True)
        atoms: JSON string list of atom indices (0-based) to calculate BDEs for (default: automatic)
        fragment_indices: JSON string list of lists defining fragment atom groups (default: automatic)
        all_CH: Calculate BDEs for all C-H bonds (default: False)
        all_CX: Calculate BDEs for all C-X bonds where X is a heavy atom (default: False)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Bond dissociation energy (BDE) measures the strength of chemical bonds and is crucial for
    understanding reactivity, stability, and reaction mechanisms.

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Calculate BDEs for all C-H bonds in butane
        result = submit_bde_workflow(
            initial_molecule="CCCC",
            all_CH=True,
            name="Butane BDE"
        )

    """
    import logging
    logger = logging.getLogger(__name__)

    # Build workflow_data
    workflow_data = {
        "mode": "rapid",
        "optimize_fragments": optimize_fragments,
        "all_CH": all_CH,
        "all_CX": all_CX
    }

    # Parse atoms if provided
    if atoms:
        try:
            parsed_atoms = json.loads(atoms)
            workflow_data["atoms"] = parsed_atoms
        except json.JSONDecodeError:
            logger.warning(f"Invalid atoms JSON: {atoms}. Skipping atoms parameter.")

    # Parse fragment_indices if provided
    if fragment_indices:
        try:
            parsed_fragments = json.loads(fragment_indices)
            workflow_data["fragment_indices"] = parsed_fragments
        except json.JSONDecodeError:
            logger.warning(f"Invalid fragment_indices JSON: {fragment_indices}. Skipping fragment_indices parameter.")

    # Submit the workflow
    logger.info(f"Submitting BDE workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="bde",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"BDE workflow submitted with UUID: {workflow.uuid}")

    return workflow
