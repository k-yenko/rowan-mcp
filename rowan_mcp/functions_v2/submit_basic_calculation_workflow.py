"""
Rowan v2 API: Basic Calculation Workflow
Submit basic quantum chemistry calculations with various methods and tasks.
"""

from typing import Optional, List, Dict, Any, Union
import rowan
import stjames


def submit_basic_calculation_workflow(
    initial_molecule: Union[str, Dict[str, Any], Any],
    method: str = "uma_m_omol",
    tasks: Optional[List[str]] = None,
    mode: str = "auto",
    engine: str = "omol25",
    name: str = "Basic Calculation Workflow",
    folder_uuid: Optional[str] = None,
    max_credits: Optional[int] = None
):
    """Submit a basic calculation workflow using Rowan v2 API.
    
    Performs fundamental quantum chemistry calculations with configurable methods
    and computational tasks.
    
    Args:
        initial_molecule: The molecule to perform the calculation on.
            Can be a SMILES string, dict, StJamesMolecule, or RdkitMol object
        method: The method to use for the calculation (default: "uma_m_omol")
            See list of available methods for options
        tasks: default to None
            If None, defaults to method-appropriate tasks
        mode: The mode to run the calculation in (default: "auto")
            See list of available modes for options
        engine: The engine to use for the calculation (default: "omol25")
            See list of available engines
        name: The name of the workflow
        folder_uuid: The UUID of the folder to place the workflow in
        max_credits: The maximum number of credits to use for the workflow
        
    Returns:
        Workflow object representing the submitted workflow
        

    """
    
    # Convert SMILES string to appropriate format
    if isinstance(initial_molecule, str):
        # Try using StJamesMolecule
        try:
            initial_molecule = stjames.Molecule.from_smiles(initial_molecule)
        except:
            # If that fails, pass the string directly - the API might handle it
            pass
    
    return rowan.submit_basic_calculation_workflow(
        initial_molecule=initial_molecule,
        method=method,
        tasks=tasks,
        mode=mode,
        engine=engine,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )