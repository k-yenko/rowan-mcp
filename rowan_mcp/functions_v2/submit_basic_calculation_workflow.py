"""
Rowan v2 API: Basic Calculation Workflow
Submit basic quantum chemistry calculations with various methods and tasks.
"""

# Simplified imports - no complex typing needed
from typing import Annotated
import rowan
import stjames
import json


def submit_basic_calculation_workflow(
    initial_molecule: Annotated[str, "SMILES string or molecule JSON for quantum chemistry calculation"],
    method: Annotated[str, "Computational method (e.g., 'gfn2-xtb', 'uma_m_omol', 'b3lyp-d3bj')"] = "uma_m_omol",
    tasks: Annotated[str, "JSON array or comma-separated list of tasks (e.g., '[\"optimize\"]', 'optimize, frequencies')"] = "",
    mode: Annotated[str, "Calculation mode: 'rapid', 'careful', 'meticulous', or 'auto'"] = "auto", 
    engine: Annotated[str, "Computational engine: 'omol25', 'xtb', 'psi4'"] = "omol25",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Basic Calculation Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a basic calculation workflow using Rowan v2 API.
    
    Performs fundamental quantum chemistry calculations with configurable methods
    and computational tasks. Returns a workflow object for tracking progress.
    
    Examples:
        # Simple water optimization with GFN2-xTB
        result = submit_basic_calculation_workflow(
            initial_molecule="O",
            method="gfn2-xtb",
            tasks=["optimize"],
            engine="xtb",
            name="Water Optimization"
        )
        
        # Butane optimization from SMILES
        result = submit_basic_calculation_workflow(
            initial_molecule="CCCC",
            method="gfn2-xtb",
            tasks=["optimize"],
            mode="rapid",
            engine="xtb",
            name="Butane Optimization"
        )
        
        # Using a molecule dict (from data.json)
        molecule_dict = {
            "smiles": "CCCC",
            "charge": 0,
            "multiplicity": 1,
            "atoms": [...]  # atomic positions
        }
        result = submit_basic_calculation_workflow(
            initial_molecule=molecule_dict,
            method="gfn2-xtb",
            tasks=["optimize"],
            engine="xtb"
        )
    """
    
    # Parse tasks parameter - handle string input
    parsed_tasks = None
    if tasks:  # If not empty string
        tasks = tasks.strip()
        if tasks.startswith('[') and tasks.endswith(']'):
            # JSON array format like '["optimize"]'
            try:
                parsed_tasks = json.loads(tasks)
            except (json.JSONDecodeError, ValueError):
                # Failed to parse as JSON, try as comma-separated
                tasks = tasks.strip('[]').replace('"', '').replace("'", "")
                parsed_tasks = [t.strip() for t in tasks.split(',') if t.strip()]
        elif ',' in tasks:
            # Comma-separated format like 'optimize, frequencies'  
            parsed_tasks = [t.strip() for t in tasks.split(',') if t.strip()]
        else:
            # Single task as string like 'optimize'
            parsed_tasks = [tasks]
    
    
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
        
        # Convert to appropriate format
        if hasattr(initial_molecule, 'model_dump'):
            initial_molecule_dict = initial_molecule.model_dump()
        elif isinstance(initial_molecule, dict):
            initial_molecule_dict = initial_molecule
        else:
            # Try to convert to StJamesMolecule if it's a string
            try:
                mol = stjames.Molecule.from_smiles(str(initial_molecule))
                initial_molecule_dict = mol.model_dump()
            except:
                # If that fails, pass as-is
                initial_molecule_dict = initial_molecule
        
        # Convert method string to Method object to get the correct name
        if isinstance(method, str):
            # Handle common method name variations
            method_map = {
                'gfn2_xtb': 'gfn2-xtb',
                'gfn1_xtb': 'gfn1-xtb',
                'gfn0_xtb': 'gfn0-xtb',
                'r2scan_3c': 'r2scan-3c',
                'wb97x_d3': 'wb97x-d3',
                'wb97m_d3bj': 'wb97m-d3bj',
                'b3lyp_d3bj': 'b3lyp-d3bj',
                'uma_m_omol': 'uma_m_omol',  # This one stays the same
            }
            method = method_map.get(method, method)
            
            try:
                method_obj = stjames.Method(method)
                method_name = method_obj.name
            except:
                # If Method conversion fails, use the string as-is
                method_name = method
        else:
            method_name = method
        
        # Use parsed tasks or default
        final_tasks = parsed_tasks if parsed_tasks else ["optimize"]
        
        # Build workflow_data following the official API structure
        workflow_data = {
            "settings": {
                "method": method_name,
                "tasks": final_tasks,
                "mode": mode,
            },
            "engine": engine,
        }
        
        # Build the API request
        data = {
            "name": name,
            "folder_uuid": folder_uuid if folder_uuid else None,
            "workflow_type": "basic_calculation", 
            "workflow_data": workflow_data,
            "initial_molecule": initial_molecule_dict,
            "max_credits": max_credits if max_credits > 0 else None,
        }
        
        # Submit directly to API
        from rowan.utils import api_client
        from rowan import Workflow
        
        with api_client() as client:
            response = client.post("/workflow", json=data)
            response.raise_for_status()
            return Workflow(**response.json())
        
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise