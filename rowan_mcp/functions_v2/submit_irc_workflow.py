"""
Rowan v2 API: IRC Workflow
Perform Intrinsic Reaction Coordinate calculations to trace reaction paths.
"""

from typing import Annotated
import rowan
import stjames

def submit_irc_workflow(
    initial_molecule: Annotated[str, "SMILES string for IRC calculation"],
    method: Annotated[str, "Computational method for IRC (e.g., 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c')"] = "uma_m_omol",
    engine: Annotated[str, "Computational engine: 'omol25', 'xtb', 'psi4'"] = "omol25",
    preopt: Annotated[bool, "Whether to pre-optimize the transition state before IRC step"] = True,
    step_size: Annotated[float, "Step size for IRC path tracing in Bohr (typically 0.03-0.1)"] = 0.05,
    max_irc_steps: Annotated[int, "Maximum number of IRC steps in each direction from TS"] = 30,
    name: Annotated[str, "Workflow name for identification and tracking"] = "IRC Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submits an Intrinsic Reaction Coordinate (IRC) workflow to the API.
    
    Args:
        initial_molecule: SMILES string for IRC calculation
        method: Computational method for IRC. Options: 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c'
        engine: Computational engine. Options: 'omol25', 'xtb', 'psi4'
        preopt: Whether to pre-optimize the transition state before IRC
        step_size: Step size for IRC path tracing in Bohr (typically 0.03-0.1)
        max_irc_steps: Maximum number of IRC steps in each direction from TS
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Returns:
        Workflow object representing the submitted IRC workflow
        
    Example:
        # IRC from SMILES
        result = submit_irc_workflow(
            initial_molecule="N=C([O-])[OH2+]",  # Transition state SMILES
            name="HNCO + H₂O - IRC",
            preopt=True,  # Pre-optimize TS
            method="gfn2_xtb",
            engine="xtb"
        )
    
    After submitting a workflow, use exponential backoff when checking status. Wait at least 10 seconds before the first check, 
    then double the wait time between subsequent checks (10s → 20s → 40s → 60s → 120s max). This workflow can take 10 minutes to complete.
    """
    
    result = rowan.submit_irc_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        method=method,
        engine=engine,
        preopt=preopt,
        step_size=step_size,
        max_irc_steps=max_irc_steps,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result