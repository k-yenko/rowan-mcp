"""
Rowan v2 API: Double-Ended Transition State Search Workflow
Find transition states between known reactant and product structures.
"""

from typing import Annotated, Optional
import rowan
import stjames
import json


def submit_double_ended_ts_search_workflow(
    reactant: Annotated[str, "Reactant SMILES string (e.g., 'C#N'). MUST have same atom count as product"],
    product: Annotated[str, "Product SMILES string (e.g., '[C-]#[NH+]'). MUST have same atom count as reactant"],
    calculation_settings: Annotated[str, "JSON string for calculation settings (method, basis set, etc.). Empty for defaults"] = "",
    search_settings: Annotated[str, "JSON string for TS search settings (e.g., convergence criteria). Empty for defaults"] = "",
    optimize_inputs: Annotated[bool, "Whether to optimize reactant and product geometries before TS search"] = False,
    optimize_ts: Annotated[bool, "Whether to optimize the transition state after finding it"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Double-Ended TS Search Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a double-ended transition state search workflow using Rowan v2 API.

    IMPORTANT: Reactant and product MUST have the exact same number and types of atoms,
    just in different arrangements (e.g., C#N and [C-]#[NH+] both have 1C, 1N, 1H).
    The workflow will fail if atom counts don't match.

    Args:
        reactant: Reactant molecule as SMILES string. Must have same atoms as product.
        product: Product molecule as SMILES string. Must have same atoms as reactant.
        calculation_settings: JSON string for calculation settings. Empty string uses defaults.
        search_settings: JSON string for TS search configuration. Empty string uses defaults.
        optimize_inputs: Whether to optimize reactant/product before search (default: False)
        optimize_ts: Whether to optimize found transition state (default: True)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Locates transition states connecting known reactant and product structures using
    double-ended search algorithms. More robust than single-ended TS optimization
    when both endpoints are known.

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # HCN isomerization - both have 1C, 1N, 1H ✓
        result = submit_double_ended_ts_search_workflow(
            reactant="C#N",              # HCN (hydrogen cyanide)
            product="[C-]#[NH+]",        # CNH (isocyanic acid tautomer)
            optimize_inputs=True,
            optimize_ts=True,
            name="H-C≡N Isomerization"
        )

        # Keto-enol tautomerization - both have C3H6O ✓
        result = submit_double_ended_ts_search_workflow(
            reactant="CC(=O)C",          # Acetone (keto form)
            product="CC(O)=C",           # Prop-1-en-2-ol (enol form)
            name="Keto-Enol Tautomerization"
        )

    """

    # Strip whitespace from SMILES strings
    reactant = reactant.strip()
    product = product.strip()

    # Parse calculation_settings if provided, default to sensible defaults
    # Settings object expects "basis_set" not "basis", and "method"
    parsed_calc_settings = {
        "basis_set": "def2-svp",  # Default basis set (NOTE: basis_set not basis!)
        "method": "b3lyp"         # Default method
    }
    if calculation_settings:
        try:
            user_settings = json.loads(calculation_settings)
            # Merge user settings with defaults (user settings override)
            parsed_calc_settings.update(user_settings)
        except json.JSONDecodeError:
            pass  # Keep defaults if JSON is invalid

    # Parse search_settings if provided, default to empty dict
    parsed_search_settings = {}
    if search_settings:
        try:
            parsed_search_settings = json.loads(search_settings)
        except json.JSONDecodeError:
            parsed_search_settings = {}

    result = rowan.submit_double_ended_ts_search_workflow(
        reactant=stjames.Molecule.from_smiles(reactant),
        product=stjames.Molecule.from_smiles(product),
        calculation_settings=parsed_calc_settings,
        search_settings=parsed_search_settings,
        optimize_inputs=optimize_inputs,
        optimize_ts=optimize_ts,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result
