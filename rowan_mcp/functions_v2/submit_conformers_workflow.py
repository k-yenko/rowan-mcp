"""
Rowan v2 API: Conformers Workflow
Generate conformers for molecular structures (different from conformer_search).
"""

from typing import Annotated
import rowan
import stjames


def submit_conformers_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for conformer generation"],
    num_confs_considered: Annotated[int, "Total number of conformers to evaluate during generation"] = 100,
    num_confs_taken: Annotated[int, "Number of conformers to retain after filtering"] = 50,
    rmsd_cutoff: Annotated[float, "Root mean square deviation threshold for conformer uniqueness (Angstroms)"] = 0.1,
    max_energy: Annotated[float, "Energy cutoff for accepting conformers (kcal/mol relative to lowest)"] = 5.0,
    final_method: Annotated[str, "Quantum method for final optimization: 'aimnet2_wb97md3', 'gfn2', 'gfn1'"] = "aimnet2_wb97md3",
    solvent: Annotated[str, "Solvent environment for calculations (name or SMILES). Empty string for gas phase"] = "water",
    transition_state: Annotated[bool, "Whether targeting transition state geometry"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Conformers Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit a conformers workflow to generate molecular conformations.

    Args:
        initial_molecule: SMILES string representing the molecule
        num_confs_considered: Total conformers to evaluate (default: 100)
        num_confs_taken: Conformers to retain after filtering (default: 50)
        rmsd_cutoff: RMSD threshold for uniqueness in Angstroms (default: 0.1)
        max_energy: Energy cutoff in kcal/mol for acceptance (default: 5.0)
        final_method: Quantum method for optimization (default: 'aimnet2_wb97md3')
        solvent: Solvent environment, name or SMILES (default: 'water', empty for gas phase)
        transition_state: Target transition state geometry (default: False)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    This workflow generates conformers (different 3D spatial arrangements of the same molecule)
    which is essential for accurate property predictions and understanding molecular flexibility.

    Note: This is different from submit_conformer_search_workflow which performs conformational
    search with optimization. This workflow focuses on conformer generation and enumeration.

    Returns:
        Workflow object representing the submitted workflow

    """
    import logging
    logger = logging.getLogger(__name__)

    # Build workflow_data with settings
    settings = {
        "num_confs_considered": num_confs_considered,
        "num_confs_taken": num_confs_taken,
        "rmsd_cutoff": rmsd_cutoff,
        "max_energy": max_energy,
        "final_method": final_method,
        "transition_state": transition_state
    }

    # Handle solvent
    if solvent:
        settings["solvent"] = solvent

    workflow_data = {
        "mode": "rapid",
        "settings": settings
    }

    # Submit the workflow
    logger.info(f"Submitting conformers workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="conformers",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"Conformers workflow submitted with UUID: {workflow.uuid}")

    return workflow
