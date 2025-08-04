"""
Rowan v2 API: Scan Workflow
Perform potential energy surface scans along molecular coordinates.
"""

from typing import Optional, Dict, Any, Annotated
from pydantic import Field
import rowan


def submit_scan_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object to scan")
    ],
    scan_settings: Annotated[
        Optional[Dict[str, Any]],
        Field(description="Scan parameters dict: {'type': 'dihedral'/'bond'/'angle', 'atoms': [1-indexed], 'start': value, 'stop': value, 'num': points or 'step': size}")
    ] = None,
    calculation_engine: Annotated[
        str,
        Field(description="Computational engine: 'omol25', 'xtb', or 'psi4'")
    ] = "omol25",
    calculation_method: Annotated[
        str,
        Field(description="Calculation method (depends on engine): 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c'")
    ] = "uma_m_omol",
    wavefront_propagation: Annotated[
        bool,
        Field(description="Use previous scan point geometries as starting points for faster convergence")
    ] = True,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Scan Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a potential energy surface scan workflow using Rowan v2 API.
    
    Performs systematic scans along specified molecular coordinates (bonds, angles,
    or dihedrals) to map the potential energy surface.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Water angle scan (from test)
        from stjames import Molecule
        
        result = submit_scan_workflow(
            initial_molecule=Molecule.from_smiles("O"),
            name="Water Angle scan",
            scan_settings={
                "type": "angle",
                "atoms": [2, 1, 3],  # 1-indexed atom indices
                "start": 100,
                "stop": 110,
                "num": 5,  # Number of points
            },
            calculation_method="GFN2-xTB",
            calculation_engine="xtb"
        )
    """
    
    return rowan.submit_scan_workflow(
        initial_molecule=initial_molecule,
        scan_settings=scan_settings,
        calculation_engine=calculation_engine,
        calculation_method=calculation_method,
        wavefront_propagation=wavefront_propagation,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )