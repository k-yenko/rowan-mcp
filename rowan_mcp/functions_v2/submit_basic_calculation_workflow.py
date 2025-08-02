"""
Rowan v2 API: Basic Calculation Workflow
Submit basic quantum chemistry calculations with various methods and tasks.
"""

from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import Field
import rowan
import stjames
import json


def submit_basic_calculation_workflow(
    initial_molecule: Annotated[
        Union[str, Dict[str, Any], Any],
        Field(description="The molecule to perform the calculation on. Can be a SMILES string, dict, StJamesMolecule, or RdkitMol object")
    ],
    method: Annotated[
        str,
        Field(description="The method to use for the calculation (e.g., 'uma_m_omol', 'gfn2-xtb', 'r2scan_3c')")
    ] = "uma_m_omol",
    tasks: Annotated[
        Optional[Union[List[str], str]],
        Field(description="Tasks to perform: list ['optimize'], string 'optimize', or comma-separated 'optimize,frequencies'. Defaults to None")
    ] = None,
    mode: Annotated[
        str,
        Field(description="The mode to run the calculation in ('auto', 'rapid', 'careful', 'meticulous')")
    ] = "auto",
    engine: Annotated[
        str,
        Field(description="The computational engine to use ('omol25', 'xtb', 'psi4')")
    ] = "omol25",
    name: Annotated[
        str,
        Field(description="The name of the workflow for identification")
    ] = "Basic Calculation Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of the folder to place the workflow in (optional)")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum number of credits to use for the workflow (optional)")
    ] = None
):
    """Submit a basic calculation workflow using Rowan v2 API.
    
    Performs fundamental quantum chemistry calculations with configurable methods
    and computational tasks. Returns a workflow object for tracking progress.
    """
    
    # Parse tasks parameter - handle string or list
    if tasks is not None:
        if isinstance(tasks, str):
            # Handle various string formats
            tasks = tasks.strip()
            if tasks.startswith('[') and tasks.endswith(']'):
                # JSON array format like '["optimize"]'
                try:
                    tasks = json.loads(tasks)
                except (json.JSONDecodeError, ValueError):
                    # Failed to parse as JSON, try as comma-separated
                    tasks = tasks.strip('[]').replace('"', '').replace("'", "")
                    tasks = [t.strip() for t in tasks.split(',') if t.strip()]
            elif ',' in tasks:
                # Comma-separated format like 'optimize, frequencies'
                tasks = [t.strip() for t in tasks.split(',') if t.strip()]
            else:
                # Single task as string like 'optimize'
                tasks = [tasks]
    
    
    try:
        # Handle initial_molecule parameter - could be JSON string, SMILES, or dict
        if isinstance(initial_molecule, str):
            # Check if it's a JSON string (starts with { or [)
            initial_molecule_str = initial_molecule.strip()
            if (initial_molecule_str.startswith('{') and initial_molecule_str.endswith('}')) or \
               (initial_molecule_str.startswith('[') and initial_molecule_str.endswith(']')):
                try:
                    # Parse the JSON string to dict
                    initial_molecule = json.loads(initial_molecule_str)
                    
                    # Now handle as dict (fall through to dict handling below)
                    if isinstance(initial_molecule, dict) and 'smiles' in initial_molecule:
                        smiles = initial_molecule.get('smiles')
                        if smiles:
                            try:
                                initial_molecule = stjames.Molecule.from_smiles(smiles)
                            except Exception as e:
                                initial_molecule = smiles
                except (json.JSONDecodeError, ValueError) as e:
                    # Not valid JSON, treat as SMILES string
                    try:
                        initial_molecule = stjames.Molecule.from_smiles(initial_molecule)
                    except Exception as e:
                        pass
            else:
                # Regular SMILES string
                try:
                    initial_molecule = stjames.Molecule.from_smiles(initial_molecule)
                except Exception as e:
                    pass
        elif isinstance(initial_molecule, dict) and 'smiles' in initial_molecule:
            # If we have a dict with SMILES, extract and use just the SMILES
            smiles = initial_molecule.get('smiles')
            if smiles:
                try:
                    initial_molecule = stjames.Molecule.from_smiles(smiles)
                except Exception as e:
                    initial_molecule = smiles
        
        result = rowan.submit_basic_calculation_workflow(
            initial_molecule=initial_molecule,
            method=method,
            tasks=tasks,
            mode=mode,
            engine=engine,
            name=name,
            folder_uuid=folder_uuid,
            max_credits=max_credits
        )
        
        return result
        
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise