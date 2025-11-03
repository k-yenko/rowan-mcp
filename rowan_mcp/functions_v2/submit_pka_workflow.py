"""
Rowan v2 API: Microscopic pKa Workflow
Calculate microscopic pKa values - the pH at which specific ionizable sites lose their proton, 
given the current protonation state of the rest of the molecule.
"""

from typing import List, Dict, Any, Annotated
import rowan
import json
import stjames

def submit_pka_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule to calculate pKa"],
    pka_range: Annotated[List[float], "pKa range [min, max] to search (e.g., [2, 12])"] = [2, 12],
    deprotonate_elements: Annotated[str, "Comma-separated elements for deprotonation (e.g., 'N,O,S'). Empty for auto-detect"] = "",
    protonate_elements: Annotated[str, "Comma-separated elements for protonation (e.g., 'N,O'). Empty for auto-detect"] = "",
    mode: Annotated[str, "Calculation mode: 'rapid', 'careful', or 'meticulous'"] = "careful",
    name: Annotated[str, "Workflow name for identification and tracking"] = "pKa Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a microscopic pKa prediction workflow using Rowan v2 API.
    
    Microscopic pKa: "At what pH does this site lose its proton, given the current 
    protonation state of the rest of the molecule?" Calculates site-specific pKa values
    for individual ionizable groups considering their local environment.
    
    Args:
        initial_molecule: The molecule to calculate the pKa of. SMILES string.
        pka_range: pKa range [min, max] to search, e.g., [2, 12]
        deprotonate_elements: Atomic numbers to consider for deprotonation, e.g., "[7, 8, 16]" for N, O, S. Empty string uses defaults.
        protonate_elements: Atomic numbers to consider for protonation, e.g., "[7, 8]" for N, O. Empty string uses defaults.
        mode: Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Examples:
        # Phenol pKa
        result = submit_pka_workflow(
            initial_molecule="Oc1ccccc1",
            name="pKa phenol",
            deprotonate_elements="[8]"  # Only consider oxygen
        )
    After submitting a workflow, use exponential backoff when checking status. Wait at least 10 seconds before the first check, 
    then double the wait time between subsequent checks (10s → 20s → 40s → 60s → 120s max). This workflow can take 5 minutes to complete.
    """
    
    # Handle JSON string inputs for element lists
    parsed_deprotonate_elements = None
    if deprotonate_elements:
        try:
            parsed_deprotonate_elements = json.loads(deprotonate_elements)
        except json.JSONDecodeError:
            pass  # Keep as None if not valid JSON
            
    parsed_protonate_elements = None
    if protonate_elements:
        try:
            parsed_protonate_elements = json.loads(protonate_elements)
        except json.JSONDecodeError:
            pass  # Keep as None if not valid JSON

    # Convert List[float] to Tuple[float, float] for Rowan SDK compatibility
    pka_range_tuple = tuple(pka_range) if len(pka_range) == 2 else (pka_range[0], pka_range[1] if len(pka_range) > 1 else pka_range[0])

    result = rowan.submit_pka_workflow(
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        pka_range=pka_range_tuple,
        deprotonate_elements=parsed_deprotonate_elements,
        protonate_elements=parsed_protonate_elements,
        mode=mode,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result