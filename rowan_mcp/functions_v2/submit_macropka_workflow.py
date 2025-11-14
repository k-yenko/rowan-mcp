"""
Rowan v2 API: Macroscopic pKa Workflow
Calculate macroscopic pKa values - the pH at which all molecules in solution 
are evenly split between two charge states, considering overall protonation equilibria.
"""

from typing import Annotated
import rowan

def submit_macropka_workflow(
    initial_smiles: Annotated[str, "SMILES string of the molecule for macropKa calculation"],
    min_pH: Annotated[int, "Minimum pH value for the calculation range"] = 0,
    max_pH: Annotated[int, "Maximum pH value for the calculation range"] = 14,
    min_charge: Annotated[int, "Minimum molecular charge to consider"] = -2,
    max_charge: Annotated[int, "Maximum molecular charge to consider"] = 2,
    compute_solvation_energy: Annotated[bool, "Whether to compute solvation energy corrections"] = False,
    compute_aqueous_solubility: Annotated[bool, "Compute quantitative pH-dependent solubility. False (default, 5min): pKa+ionization only, sufficient for 'which pH' questions. True (40min): adds conformer search+solvation energies for absolute mg/mL values"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Macropka Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a Macroscopic pKa workflow using Rowan v2 API.

    Calculates pKa values, microstate populations, and net charge across pH range.
    PERFORMANCE: compute_aqueous_solubility=False is 8x faster (~5 min vs ~40 min).

    Fast mode (False): pKa values, ionization states, isoelectric point. Sufficient
    to determine which pH has highest/lowest solubility (ionization dominates).

    Slow mode (True): Adds conformer search + solvation free energies for quantitative
    solubility predictions (mg/mL). Only needed for absolute values or fold-changes.

    Args:
        initial_smiles: SMILES string
        min_pH: Minimum pH (default: 0)
        max_pH: Maximum pH (default: 14)
        min_charge: Minimum charge (default: -2)
        max_charge: Maximum charge (default: 2)
        compute_solvation_energy: Compute solvation energy corrections (default: False)
        compute_aqueous_solubility: Enable quantitative solubility mode (default: False)
        name: Workflow name
        folder_uuid: Folder UUID (empty = default)
        max_credits: Credit limit (0 = no limit)

    Returns:
        Workflow object. WAIT ~5 min (fast) or ~40 min (slow) before checking results.
        Use workflow_is_finished() to poll (not more than once per minute to avoid loops).

    Examples:
        # Fast: "At which pH is solubility highest?"
        submit_macropka_workflow(initial_smiles=smiles, compute_aqueous_solubility=False)

        # Slow: "What is solubility at pH 7 in mg/mL?"
        submit_macropka_workflow(initial_smiles=smiles, compute_aqueous_solubility=True)
    """
    
    try:
        # Submit to API using rowan module
        result = rowan.submit_macropka_workflow(
            initial_smiles=initial_smiles,
            min_pH=min_pH,
            max_pH=max_pH,
            min_charge=min_charge,
            max_charge=max_charge,
            compute_solvation_energy=compute_solvation_energy,
            compute_aqueous_solubility=compute_aqueous_solubility,
            name=name,
            folder_uuid=folder_uuid if folder_uuid else None,
            max_credits=max_credits if max_credits > 0 else None
        )

        # Make workflow publicly viewable
        result.update(public=True)

        return result

    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise e