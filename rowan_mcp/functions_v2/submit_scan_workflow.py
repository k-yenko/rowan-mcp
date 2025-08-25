"""
Rowan v2 API: Scan Workflow
Perform potential energy surface scans along molecular coordinates.
"""

from typing import Dict, Any, Annotated
import rowan
import stjames
import json

def submit_scan_workflow(
    initial_molecule: Annotated[str, "SMILES string to scan"],
    scan_settings: Annotated[str, "JSON string of scan parameters: '{\"type\": \"dihedral\"/\"bond\"/\"angle\", \"atoms\": [1-indexed], \"start\": value, \"stop\": value, \"num\": points}'"] = "",
    calculation_engine: Annotated[str, "Computational engine: 'omol25', 'xtb', 'psi4'"] = "omol25",
    calculation_method: Annotated[str, "Computational method (e.g., 'uma_m_omol', 'gfn2-xtb', 'b3lyp-d3bj')"] = "uma_m_omol",
    wavefront_propagation: Annotated[bool, "Whether to use wavefront propagation for scan"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Scan Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a potential energy surface scan workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string to scan
        scan_settings: JSON string of scan parameters: '{"type": "dihedral"/"bond"/"angle", "atoms": [1-indexed], "start": value, "stop": value, "num": points}'
        calculation_engine: Computational engine: 'omol25', 'xtb', or 'psi4'
        calculation_method: Calculation method (depends on engine): 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c'
        wavefront_propagation: Use previous scan point geometries as starting points for faster convergence
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Performs systematic scans along specified molecular coordinates (bonds, angles,
    or dihedrals) to map the potential energy surface.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Water angle scan
        result = submit_scan_workflow(
            initial_molecule="O",  # Water SMILES
            name="Water Angle scan",
            scan_settings='{"type": "angle", "atoms": [2, 1, 3], "start": 100, "stop": 110, "num": 5}',
            calculation_method="GFN2-xTB",
            calculation_engine="xtb"
        )
    """
    # Parse scan_settings if provided
    parsed_scan_settings = None
    if scan_settings:
        try:
            parsed_scan_settings = json.loads(scan_settings)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid scan_settings format: {e}")
    
    # Validate and convert scan_settings
    if parsed_scan_settings is not None:
        # Convert step to num if step is provided instead of num
        if 'step' in parsed_scan_settings and 'num' not in parsed_scan_settings:
            start = parsed_scan_settings.get('start', 0)
            stop = parsed_scan_settings.get('stop', 360)
            step = parsed_scan_settings['step']
            parsed_scan_settings['num'] = int((stop - start) / step) + 1
            del parsed_scan_settings['step']  # Remove step as API doesn't accept it
        
        # Validate required fields
        required_fields = ['type', 'atoms', 'start', 'stop', 'num']
        missing_fields = [field for field in required_fields if field not in parsed_scan_settings]
        if missing_fields:
            raise ValueError(f"Missing required fields in scan_settings: {missing_fields}")
    
    return rowan.submit_scan_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        scan_settings=parsed_scan_settings,
        calculation_engine=calculation_engine,
        calculation_method=calculation_method,
        wavefront_propagation=wavefront_propagation,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )