"""
Rowan v2 API: NMR Workflow
Predict NMR chemical shifts for molecules using quantum chemistry methods.
"""

from typing import Annotated
import rowan
import stjames


def submit_nmr_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for NMR prediction"],
    solvent: Annotated[str, "Solvent for NMR calculation (SMILES or name, e.g., 'chloroform', 'CDCl3', 'C(Cl)(Cl)Cl')"] = "chloroform",
    do_csearch: Annotated[bool, "Whether to perform conformational search before NMR calculation"] = True,
    do_optimization: Annotated[bool, "Whether to optimize molecular geometry before NMR calculation"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "NMR Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit an NMR chemical shift prediction workflow using Rowan v2 API.

    Args:
        initial_molecule: SMILES string of the molecule for NMR spectrum prediction
        solvent: Solvent for NMR calculation (default: 'chloroform'). Can be solvent name or SMILES
        do_csearch: Whether to perform conformational search (default: True)
        do_optimization: Whether to optimize geometry (default: True)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Predicts NMR chemical shifts (¹H and ¹³C) for a molecule using quantum chemistry
    methods. Automatically accounts for conformational averaging and solvent effects.

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Menthol NMR
        result = submit_nmr_workflow(
            initial_molecule="O[C@H]1[C@H](C(C)C)CC[C@@H](C)C1",
            name="menthol NMR"
        )

    """

    result = rowan.submit_nmr_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        solvent=solvent,
        do_csearch=do_csearch,
        do_optimization=do_optimization,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result
