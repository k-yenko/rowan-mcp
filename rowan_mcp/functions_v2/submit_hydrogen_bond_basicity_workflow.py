"""
Rowan v2 API: Hydrogen Bond Basicity Workflow
Predict hydrogen bond basicity (pKBHX) of molecules.
"""

from typing import Annotated
import rowan
import stjames


def submit_hydrogen_bond_basicity_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for hydrogen bond basicity prediction"],
    do_csearch: Annotated[bool, "Whether to perform conformer search before calculation"] = False,
    do_optimization: Annotated[bool, "Whether to optimize the molecular geometry before calculation"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Hydrogen Bond Basicity Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit a hydrogen bond basicity workflow to predict pKBHX values.

    Args:
        initial_molecule: SMILES string representing the molecule
        do_csearch: Whether to perform conformer search before calculation (default: False)
        do_optimization: Whether to optimize geometry before calculation (default: False)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Hydrogen bond basicity (pKBHX) quantifies the ability of a molecule to accept hydrogen bonds,
    which is important for understanding molecular interactions, solubility, and drug-receptor binding.

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Basic hydrogen bond basicity prediction
        result = submit_hydrogen_bond_basicity_workflow(
            initial_molecule="CCO",
            name="Ethanol H-bond basicity"
        )

        # With conformer search and optimization
        result = submit_hydrogen_bond_basicity_workflow(
            initial_molecule="c1ccc(cc1)N",
            do_csearch=True,
            do_optimization=True,
            name="Aniline H-bond basicity (optimized)"
        )

        # Predict for a drug molecule
        result = submit_hydrogen_bond_basicity_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            do_csearch=True,
            name="Caffeine H-bond basicity"
        )

    """
    import logging
    logger = logging.getLogger(__name__)

    # Build workflow_data
    workflow_data = {
        "do_csearch": do_csearch,
        "do_optimization": do_optimization
    }

    # Submit the workflow
    logger.info(f"Submitting hydrogen bond basicity workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="hydrogen_bond_basicity",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"Hydrogen bond basicity workflow submitted with UUID: {workflow.uuid}")

    return workflow
