"""
Rowan v2 API: IRC Workflow
Perform Intrinsic Reaction Coordinate calculations to trace reaction paths.
"""

from typing import Optional, Dict, Any, Union
import rowan


def submit_irc_workflow(
    initial_molecule: Optional[Union[Dict[str, Any], Any]] = None,
    method: str = "uma_m_omol",
    engine: str = "omol25",
    preopt: bool = True,
    step_size: float = 0.05,
    max_irc_steps: int = 30,
    name: str = "IRC Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submits an Intrinsic Reaction Coordinate (IRC) workflow to the API.
    
    Args:
        initial_molecule: The initial molecule to perform the IRC calculation on.
            Can be a dict, StJamesMolecule, or RdkitMol object
        method: The computational method to use for the IRC calculation (default: "uma_m_omol")
            See list of available methods for options
        engine: The computational engine to use for the calculation (default: "omol25")
            See list of available engines
        preopt: Whether to perform a pre-optimization of the molecule (default: True)
        step_size: The step size to use for the IRC calculation (default: 0.05)
        max_irc_steps: The maximum number of IRC steps to perform (default: 30)
        name: The name of the workflow
        folder_uuid: The UUID of the folder to place the workflow in
        max_credits: The maximum number of credits to use for the workflow
        
    Returns:
        Workflow object representing the submitted IRC workflow
        
    Example:
        # Basic IRC calculation
        result = submit_irc_workflow(
            initial_molecule={"smiles": "[CH3].[CH3]"},
            method="gfn2_xtb",
            max_irc_steps=50
        )
        
        # IRC with specific method and engine
        result = submit_irc_workflow(
            initial_molecule={"smiles": "CC(O)=CC"},
            method="r2scan_3c",
            engine="psi4",
            step_size=0.03
        )
    """
    
    return rowan.submit_irc_workflow(
        initial_molecule=initial_molecule,
        method=method,
        engine=engine,
        preopt=preopt,
        step_size=step_size,
        max_irc_steps=max_irc_steps,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )