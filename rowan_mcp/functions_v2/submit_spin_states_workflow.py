"""
Rowan v2 API: Spin States Workflow
Calculate energies of different spin states for molecules.
"""

from typing import Annotated
import rowan
import stjames
import json


def submit_spin_states_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for spin state calculations"],
    states: Annotated[str, "JSON array of [charge, multiplicity] pairs. Format: [[0,1], [0,3]] (no outer quotes)"],
    solvent: Annotated[str, "Solvent environment for calculations (name or SMILES). Empty string for gas phase"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Spin States Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit a spin states workflow to calculate energies of different spin multiplicities.

    FORMATTING NOTES (for MCP Inspector):
    - initial_molecule: Plain SMILES string (e.g., CCO, O=O)
    - states: JSON array without outer quotes (e.g., [[0,1], [0,3]])

    Args:
        initial_molecule: SMILES string representing the molecule
        states: JSON array of [charge, multiplicity] pairs to calculate
            Multiplicity = 2S + 1 where S is total spin
            - Singlet (S=0): multiplicity = 1 (paired electrons)
            - Doublet (S=1/2): multiplicity = 2 (one unpaired electron)
            - Triplet (S=1): multiplicity = 3 (two unpaired electrons)
            - Quartet (S=3/2): multiplicity = 4 (three unpaired electrons)
            - Quintet (S=2): multiplicity = 5 (four unpaired electrons)
        solvent: Solvent environment, name or SMILES (default: empty for gas phase)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Spin state calculations are essential for understanding:
    - Transition metal complexes and coordination chemistry
    - Radical species and open-shell molecules
    - Magnetic properties and spin crossover
    - Reaction mechanisms involving spin forbidden transitions

    Returns:
        Workflow object representing the submitted workflow

    Examples (MCP Inspector format):
        # Compare singlet and triplet states for oxygen
        initial_molecule: O=O
        states: [[0,1], [0,3]]
        name: O2 spin states

        # Ethanol singlet and triplet (simple test)
        initial_molecule: CCO
        states: [[0,1], [0,3]]
        name: Ethanol spin states

        # Methylene carbene singlet and triplet
        initial_molecule: [CH2]
        states: [[0,1], [0,3]]
        name: Methylene spin states

        # Iron complex with multiple spin states
        initial_molecule: [Fe+2]
        states: [[2,1], [2,3], [2,5]]
        solvent: water
        name: Fe2+ aqueous spin states

    """
    import logging
    logger = logging.getLogger(__name__)

    # Parse states parameter (required)
    try:
        parsed_states = json.loads(states)
        if not isinstance(parsed_states, list) or not all(isinstance(s, list) and len(s) == 2 for s in parsed_states):
            raise ValueError("states must be a list of [charge, multiplicity] pairs")
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid states format: {states}. Expected JSON list of [charge, multiplicity] pairs like '[[0,1], [0,3]]'. Error: {e}")

    # Extract just multiplicities (second element of each pair)
    # Spin states workflow expects [1, 3, 5] not [[0,1], [0,3], [0,5]]
    multiplicities = [s[1] for s in parsed_states]

    # Build workflow_data
    workflow_data = {
        "states": multiplicities,  # Use just multiplicities, not full pairs
        "mode": "rapid"
    }

    # Handle solvent
    if solvent:
        workflow_data["solvent"] = solvent

    # Submit the workflow
    logger.info(f"Submitting spin states workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="spin_states",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"Spin states workflow submitted with UUID: {workflow.uuid}")

    return workflow
