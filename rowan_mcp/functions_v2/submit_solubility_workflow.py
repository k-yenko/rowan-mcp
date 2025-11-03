"""
Rowan v2 API: Solubility Workflow
Predict molecular solubility in various solvents at different temperatures.
"""

from typing import List, Annotated
import rowan
import json


def submit_solubility_workflow(
    initial_smiles: Annotated[str, "SMILES string of the molecule for solubility prediction"],
    solvents: Annotated[str, "JSON string list of solvents as SMILES or names (e.g., '[\"water\", \"ethanol\", \"CCO\"]'). Empty string uses defaults"] = "",
    temperatures: Annotated[str, "JSON string list of temperatures in Kelvin (e.g., '[298.15, 310.15]'). Empty string uses default range"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Solubility Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a solubility prediction workflow using Rowan v2 API.
    
    Args:
        initial_smiles: SMILES string of the molecule for solubility prediction
        solvents: JSON string list of solvents as SMILES or names (e.g., '["water", "ethanol", "CCO"]'). Empty string uses defaults
        temperatures: JSON string list of temperatures in Kelvin (e.g., '[298.15, 310.15]'). Empty string uses default range
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Predicts solubility (log S) of a molecule in multiple solvents at various temperatures
    using machine learning models.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Example:
        # Basic solubility prediction
        result = submit_solubility_workflow(
            initial_smiles="CC(=O)Nc1ccc(O)cc1",
            solvents='["water", "ethanol"]',
            temperatures='[298.15, 310.15]'
        )
        
        # With SMILES solvents
        result = submit_solubility_workflow(
            initial_smiles="CC(=O)O",
            solvents='["O", "CCO", "CCCCCC"]',
            temperatures='[273.15, 298.15, 323.15]'
        )
    After submitting a workflow, use exponential backoff when checking status. Wait at least 10 seconds before the first check, 
    then double the wait time between subsequent checks (10s → 20s → 40s → 60s → 120s max). This workflow can take 5 minutes to complete.
    """
    
    # Parse solvents parameter - handle string input
    parsed_solvents = None
    if solvents:
        # Handle various string formats
        solvents = solvents.strip()
        if solvents.startswith('[') and solvents.endswith(']'):
            # JSON array format like '["water", "ethanol"]'
            try:
                parsed_solvents = json.loads(solvents)
            except (json.JSONDecodeError, ValueError):
                # Failed to parse as JSON, try as comma-separated
                solvents = solvents.strip('[]').replace('"', '').replace("'", "")
                parsed_solvents = [s.strip() for s in solvents.split(',') if s.strip()]
        elif ',' in solvents:
            # Comma-separated format like 'water, ethanol'
            parsed_solvents = [s.strip() for s in solvents.split(',') if s.strip()]
        else:
            # Single solvent as string like 'water'
            parsed_solvents = [solvents]
        
        # Convert solvent names to SMILES if needed
        solvent_name_to_smiles = {
            'water': 'O',
            'ethanol': 'CCO',
            'dmso': 'CS(=O)C',
            'acetone': 'CC(=O)C',
            'methanol': 'CO',
            'chloroform': 'C(Cl)(Cl)Cl',
            'dichloromethane': 'C(Cl)Cl',
            'toluene': 'Cc1ccccc1',
            'benzene': 'c1ccccc1',
            'hexane': 'CCCCCC',
            'ether': 'CCOCC',
            'diethyl ether': 'CCOCC',
            'thf': 'C1CCOC1',
            'tetrahydrofuran': 'C1CCOC1',
            'dioxane': 'C1COCCO1',
            'acetonitrile': 'CC#N',
            'pyridine': 'c1ccncc1'
        }
        
        converted_solvents = []
        for solvent in parsed_solvents:
            solvent_lower = solvent.lower().strip()
            if solvent_lower in solvent_name_to_smiles:
                converted_solvents.append(solvent_name_to_smiles[solvent_lower])
            else:
                # Assume it's already a SMILES string or use as-is
                converted_solvents.append(solvent)
        parsed_solvents = converted_solvents
        
        # Validate the final solvent SMILES to catch issues early
        try:
            from rdkit import Chem
            for i, solvent_smiles in enumerate(parsed_solvents):
                mol = Chem.MolFromSmiles(solvent_smiles)
                if mol is None:
                    raise ValueError(f"Invalid solvent SMILES: '{solvent_smiles}' at position {i}")
        except ImportError:
            # RDKit not available for validation, proceed anyway
            pass
    
    # Parse temperatures parameter - handle string input
    parsed_temperatures = None
    if temperatures:
        # Handle various string formats
        temperatures = temperatures.strip()
        if temperatures.startswith('[') and temperatures.endswith(']'):
            # JSON array format like '[298.15, 310.15]'
            try:
                parsed_temperatures = json.loads(temperatures)
            except (json.JSONDecodeError, ValueError):
                # Failed to parse as JSON, try as comma-separated
                temperatures = temperatures.strip('[]').replace('"', '').replace("'", "")
                parsed_temperatures = [float(t.strip()) for t in temperatures.split(',') if t.strip()]
        elif ',' in temperatures:
            # Comma-separated format like '298.15, 310.15'
            parsed_temperatures = [float(t.strip()) for t in temperatures.split(',') if t.strip()]
        else:
            # Single temperature as string like '298.15'
            parsed_temperatures = [float(temperatures)]
    
    # Validate the main SMILES string early to catch issues
    try:
        from rdkit import Chem
        mol = Chem.MolFromSmiles(initial_smiles)
        if mol is None:
            raise ValueError(f"Invalid initial SMILES: '{initial_smiles}'")
    except ImportError:
        # RDKit not available for validation, proceed anyway
        pass
    
    try:
        result = rowan.submit_solubility_workflow(
            initial_smiles=initial_smiles,
            solvents=parsed_solvents,
            temperatures=parsed_temperatures,
            name=name,
            folder_uuid=folder_uuid if folder_uuid else None,
            max_credits=max_credits if max_credits > 0 else None
        )

        # Make workflow publicly viewable
        result.update(public=True)

        return result

    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise