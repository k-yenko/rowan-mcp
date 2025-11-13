"""
Rowan v2 API: ADMET Workflow
Predict absorption, distribution, metabolism, excretion, and toxicity properties.
"""

from typing import Annotated
import rowan


def submit_admet_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for ADMET property prediction"],
    name: Annotated[str, "Workflow name for identification and tracking"] = "ADMET Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit an ADMET workflow to predict drug-like properties using ADMET-AI.

    Args:
        initial_molecule: SMILES string representing the molecule
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) predictions help assess
    drug-likeness and pharmacokinetic properties of molecules early in the drug discovery process.

    Uses the ADMET-AI model to predict various pharmacokinetic properties automatically.

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Predict ADMET properties for aspirin
        result = submit_admet_workflow(
            initial_molecule="CC(=O)Nc1ccc(O)cc1",
            name="Aspirin ADMET"
        )

        # Predict ADMET properties for caffeine
        result = submit_admet_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            name="Caffeine ADMET"
        )

    """
    import logging
    logger = logging.getLogger(__name__)

    # Strip whitespace from SMILES
    initial_molecule = initial_molecule.strip()

    # Submit the workflow using initial_smiles (ADMET workflow requirement)
    # ADMET workflow REQUIRES workflow_data={} even if empty (cannot be None)
    logger.info(f"Submitting ADMET workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="admet",
        initial_smiles=initial_molecule,  # ADMET uses initial_smiles, not initial_molecule
        workflow_data={},  # Required to be empty dict, not None
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"ADMET workflow submitted with UUID: {workflow.uuid}")

    return workflow
