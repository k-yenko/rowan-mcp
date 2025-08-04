"""
Rowan v2 API: IRC Workflow
Perform Intrinsic Reaction Coordinate calculations to trace reaction paths.
"""

from typing import Optional, Dict, Any, Union, Annotated
from pydantic import Field
import rowan


def submit_irc_workflow(
    initial_molecule: Annotated[
        Optional[Union[Dict[str, Any], Any]],
        Field(description="Transition state molecule for IRC. Can be dict with SMILES, StJamesMolecule, or RdkitMol object")
    ] = None,
    method: Annotated[
        str,
        Field(description="Computational method for IRC. Options: 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c'")
    ] = "uma_m_omol",
    engine: Annotated[
        str,
        Field(description="Computational engine. Options: 'omol25', 'xtb', 'psi4'")
    ] = "omol25",
    preopt: Annotated[
        bool,
        Field(description="Whether to pre-optimize the transition state before IRC")
    ] = True,
    step_size: Annotated[
        float,
        Field(description="Step size for IRC path tracing in Bohr (typically 0.03-0.1)")
    ] = 0.05,
    max_irc_steps: Annotated[
        int,
        Field(description="Maximum number of IRC steps in each direction from TS")
    ] = 30,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "IRC Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submits an Intrinsic Reaction Coordinate (IRC) workflow to the API.
    
    Returns:
        Workflow object representing the submitted IRC workflow
        
    Example:
        # IRC for HNCO + H₂O reaction (from test)
        from stjames import Molecule
        
        result = submit_irc_workflow(
            initial_molecule=Molecule.from_xyz_lines(
                '''7
        SMILES `N=C([O-])[OH2+]`
        N    -0.15519741  -1.36979175  -0.20679433
        C     1.11565384  -1.23943631  -0.14797646
        O     2.17614993  -1.72950370  -0.04017850
        H    -0.55869366  -2.29559315  -0.23834737
        O     1.02571386   0.42871733  -0.27925360
        H    -0.09029954  -0.04166676  -0.31495768
        H     1.26740151   0.88347299   0.53620841
        '''.splitlines()
            ),
            name="HNCO + H₂O - IRC",
            preopt=False
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