"""
Rowan v2 API: Conformer Search Workflow
Search for low-energy molecular conformations using various methods.
"""

from typing import Optional, Annotated
from pydantic import Field
import rowan


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
    transition_state: Annotated[
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
    
    return rowan.submit_conformer_search_workflow(
        initial_molecule=initial_molecule,
        conf_gen_mode=conf_gen_mode,
        final_method=final_method,
        solvent=solvent,
        transistion_state=transition_state,  # Note: API uses "transistion" (typo)
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )