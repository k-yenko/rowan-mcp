"""
Rowan v2 API: IRC Workflow
Perform Intrinsic Reaction Coordinate calculations to trace reaction paths.
"""

from typing import Optional, Dict, Any, Union, Annotated
from pydantic import Field
import rowan
import stjames

def submit_irc_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object for descriptor calculation")
    ],
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
        # IRC from SMILES
        result = submit_irc_workflow(
            initial_molecule="N=C([O-])[OH2+]",  # Transition state SMILES
            name="HNCO + H₂O - IRC",
            preopt=True,  # Pre-optimize TS
            method="gfn2_xtb",
            engine="xtb"
        )
        
        # IRC from molecule dict with coordinates
        molecule_dict = {
            "smiles": "N=C([O-])[OH2+]",
            "atoms": [  # XYZ coordinates if available
                {"element": "N", "x": -0.155, "y": -1.370, "z": -0.207},
                # ... more atoms
            ]
        }
        result = submit_irc_workflow(
            initial_molecule=molecule_dict,
            name="HNCO + H₂O - IRC",
            preopt=False  # Already at TS
        )
    """
    
    return rowan.submit_irc_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        method=method,
        engine=engine,
        preopt=preopt,
        step_size=step_size,
        max_irc_steps=max_irc_steps,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )