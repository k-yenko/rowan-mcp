"""
Rowan v2 API: Scan Workflow
Perform potential energy surface scans along molecular coordinates.
"""

from typing import Optional, Dict, Any
import rowan


def submit_scan_workflow(
    initial_molecule: str,
    scan_settings: Optional[Dict[str, Any]] = None,
    calculation_engine: str = "omol25",
    calculation_method: str = "uma_m_omol",
    wavefront_propagation: bool = True,
    name: str = "Scan Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a potential energy surface scan workflow using Rowan v2 API.
    
    Performs systematic scans along specified molecular coordinates (bonds, angles,
    or dihedrals) to map the potential energy surface.
    
    Args:
        initial_molecule: SMILES string or molecule object
        scan_settings: Dictionary specifying scan parameters
            Example: {
                "type": "dihedral",  # or "bond", "angle"
                "atoms": [0, 1, 2, 3],  # atom indices
                "start": -180,
                "stop": 180,
                "step": 10
            }
        calculation_engine: Computational engine (default: "omol25")
            Options: "omol25", "xtb", "psi4"
        calculation_method: Method for calculations (default: "uma_m_omol")
            Options depend on engine
        wavefront_propagation: Use wavefront optimization (default: True)
            Speeds up scans by using previous geometries as starting points
        name: Workflow name for tracking
        folder_uuid: Optional folder UUID for organization
        max_credits: Optional credit limit for the calculation
        
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Dihedral scan
        result = submit_scan_workflow(
            initial_molecule="CC(C)CC",
            scan_settings={
                "type": "dihedral",
                "atoms": [0, 1, 2, 3],
                "start": -180,
                "stop": 180,
                "step": 15
            }
        )
        
        # Bond scan with advanced method
        result = submit_scan_workflow(
            initial_molecule="CC",
            scan_settings={
                "type": "bond",
                "atoms": [0, 1],
                "start": 1.0,
                "stop": 2.5,
                "step": 0.1
            },
            calculation_method="r2scan_3c"
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