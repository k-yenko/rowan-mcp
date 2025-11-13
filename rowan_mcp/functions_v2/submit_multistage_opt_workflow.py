"""
Rowan v2 API: Multi-Stage Optimization Workflow
Perform sequential geometry optimization with increasing levels of theory.
"""

from typing import Annotated
import rowan
import stjames


def submit_multistage_opt_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for multi-stage optimization"],
    xtb_preopt: Annotated[bool, "Whether to pre-optimize with xTB before main optimization stages"] = False,
    transition_state: Annotated[bool, "Whether this is a transition state optimization"] = False,
    frequencies: Annotated[bool, "Whether to calculate vibrational frequencies after optimization"] = False,
    solvent: Annotated[str, "Solvent environment for calculations (name or SMILES). Empty string for gas phase"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Multi-Stage Optimization Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit a multi-stage optimization workflow for sequential geometry refinement.

    Args:
        initial_molecule: SMILES string representing the molecule
        xtb_preopt: Pre-optimize with xTB before main stages (default: False)
        transition_state: Optimize to a transition state instead of minimum (default: False)
        frequencies: Calculate vibrational frequencies after optimization (default: False)
        solvent: Solvent environment, name or SMILES (default: empty for gas phase)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Multi-stage optimization uses sequential calculations with increasing accuracy to efficiently
    find high-quality optimized geometries. This is particularly useful for:
    - Large or complex molecules
    - Transition state searches
    - High-accuracy geometry requirements
    - Systems where initial geometry is poor

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Basic multi-stage optimization
        result = submit_multistage_opt_workflow(
            initial_molecule="CC(=O)O",
            name="Acetic acid optimization"
        )

        # High-accuracy optimization with frequencies
        result = submit_multistage_opt_workflow(
            initial_molecule="c1ccccc1",
            frequencies=True,
            name="Benzene with frequencies"
        )

        # Transition state optimization with xTB pre-optimization
        result = submit_multistage_opt_workflow(
            initial_molecule="CC=CC",
            transition_state=True,
            xtb_preopt=True,
            name="Butene rotation TS"
        )

        # Solvated molecule optimization
        result = submit_multistage_opt_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            solvent="water",
            frequencies=True,
            name="Caffeine in water"
        )

        # Fast screening optimization
        result = submit_multistage_opt_workflow(
            initial_molecule="CCCCCCCCCC",
            xtb_preopt=True,
            name="Decane quick opt"
        )

    """
    import logging
    logger = logging.getLogger(__name__)

    # Build workflow_data
    workflow_data = {
        "mode": "rapid",
        "xtb_preopt": xtb_preopt,
        "transition_state": transition_state,
        "frequencies": frequencies
    }

    # Handle solvent
    if solvent:
        workflow_data["solvent"] = solvent

    # Submit the workflow
    logger.info(f"Submitting multi-stage optimization workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="multistage_opt",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"Multi-stage optimization workflow submitted with UUID: {workflow.uuid}")

    return workflow
