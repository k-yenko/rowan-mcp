"""
Rowan v2 API: Ion Mobility Workflow
Predict collision cross-section (CCS) values for ion mobility mass spectrometry.
"""

from typing import Annotated
import rowan
import stjames


def submit_ion_mobility_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for ion mobility prediction"],
    temperature: Annotated[int, "Temperature in Kelvin for CCS calculation"] = 300,
    protonate: Annotated[bool, "Whether to automatically protonate the molecule"] = False,
    do_csearch: Annotated[bool, "Whether to perform conformational search before CCS calculation"] = True,
    do_optimization: Annotated[bool, "Whether to optimize molecular geometry before CCS calculation"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Ion-Mobility Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit an ion mobility (CCS) prediction workflow using Rowan v2 API.

    Args:
        initial_molecule: SMILES string of the molecule for collision cross-section prediction
        temperature: Temperature in Kelvin for CCS calculation (default: 300K)
        protonate: Whether to automatically protonate the molecule (default: False)
        do_csearch: Whether to perform conformational search (default: True)
        do_optimization: Whether to optimize geometry (default: True)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Predicts collision cross-section (CCS) values for ion mobility mass spectrometry
    using conformational averaging and theoretical calculations. Useful for:
    - Validating experimental IM-MS data
    - Predicting CCS values for method development
    - Structural characterization of biomolecules

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Pyridinium CCS
        result = submit_ion_mobility_workflow(
            initial_molecule="c1ccccn1",
            protonate=True,
            name="pyridinium CCS"
        )

    """

    result = rowan.submit_ion_mobility_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        temperature=temperature,
        protonate=protonate,
        do_csearch=do_csearch,
        do_optimization=do_optimization,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result
