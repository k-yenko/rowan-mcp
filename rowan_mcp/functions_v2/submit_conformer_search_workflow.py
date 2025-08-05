"""
Rowan v2 API: Conformer Search Workflow
Search for low-energy molecular conformations using various methods.
"""

from typing import Optional, Annotated
from pydantic import Field
import rowan
import json
import stjames

def submit_conformer_search_workflow(
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object representing the initial structure")
    ],
    conf_gen_mode: Annotated[
        str,
        Field(description="Conformer generation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)")
    ] = "rapid",
    final_method: Annotated[
        str,
        Field(description="Final optimization method (e.g., 'aimnet2_wb97md3', 'r2scan_3c', 'wb97x-d3_def2-tzvp')")
    ] = "aimnet2_wb97md3",
    solvent: Annotated[
        Optional[str],
        Field(description="Solvent for implicit solvation (e.g., 'water', 'ethanol', 'dmso'). None for gas phase")
    ] = None,
    transistion_state: Annotated[
        bool,
        Field(description="Whether to search for transition state conformers (default: False)")
    ] = False,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Conformer Search Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None
):
    """Submit a conformer search workflow using Rowan v2 API.
    
    Explores the conformational space of a molecule to find low-energy structures.
    
    Conformer Generation Modes:
    - 'rapid': RDKit/MMFF, 300 conformers, 0.10 Å RMSD cutoff (recommended for most work)
    - 'careful': CREST/GFN-FF quick mode, 150 conformers max
    - 'meticulous': CREST/GFN2-xTB normal mode, 500 conformers max
    
    Returns:
        Workflow object representing the submitted workflow
        
    Examples:
        # Simple diethyl ether conformer search (from test)
        result = submit_conformer_search_workflow(
            initial_molecule="CCOCC"
        )
        
        # Basic butane conformer search with rapid mode
        result = submit_conformer_search_workflow(
            initial_molecule="CCCC",
            conf_gen_mode="rapid"
        )
        
        # Careful search with solvent
        result = submit_conformer_search_workflow(
            initial_molecule="CC(C)CC(=O)O",
            conf_gen_mode="careful",
            solvent="water",
            final_method="r2scan_3c"
        )
    """

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
        

        result = rowan.submit_conformer_search_workflow(
            initial_molecule=initial_molecule,
            conf_gen_mode=conf_gen_mode,
            final_method=final_method,
            solvent=solvent,
            transistion_state=transistion_state,  # Note: API uses "transistion" (typo in Rowan API)
            name=name,
            folder_uuid=folder_uuid,
            max_credits=max_credits
        )
        
        return result
        
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise