"""
Rowan v2 API: Electronic Properties Workflow
Calculate electronic structure properties including HOMO/LUMO, dipole moments, and frontier orbitals.
"""

from typing import Annotated
import rowan
import stjames


def submit_electronic_properties_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for electronic property calculations"],
    functional: Annotated[str, "DFT functional to use (e.g., 'B3LYP', 'PBE', 'PBEh', 'wB97X-D3')"] = "B3LYP",
    basis: Annotated[str, "Basis set (e.g., 'def2-SVP', 'def2-TZVP', '6-31G*')"] = "def2-SVP",
    compute_density_cube: Annotated[bool, "Generate electron density cube files"] = True,
    compute_electrostatic_potential_cube: Annotated[bool, "Generate electrostatic potential cube files"] = True,
    compute_num_occupied_orbitals: Annotated[int, "Number of occupied orbitals to output (HOMO, HOMO-1, etc.)"] = 1,
    compute_num_virtual_orbitals: Annotated[int, "Number of virtual orbitals to output (LUMO, LUMO+1, etc.)"] = 1,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Electronic Properties Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit an electronic properties workflow to calculate molecular electronic structure using DFT.

    Args:
        initial_molecule: SMILES string representing the molecule
        functional: DFT functional (default: 'B3LYP'). Examples: 'B3LYP', 'PBE', 'PBEh', 'wB97X-D3'
        basis: Basis set (default: 'def2-SVP'). Examples: 'def2-SVP', 'def2-TZVP', '6-31G*'
        compute_density_cube: Generate electron density cube files (default: True)
        compute_electrostatic_potential_cube: Generate electrostatic potential cube files (default: True)
        compute_num_occupied_orbitals: Number of occupied orbitals to output (default: 1 = HOMO only)
        compute_num_virtual_orbitals: Number of virtual orbitals to output (default: 1 = LUMO only)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Automatically calculates:
    - HOMO/LUMO energies and orbitals
    - Molecular orbital cube files
    - Electron density cubes (if compute_density_cube=True)
    - Electrostatic potential cubes (if compute_electrostatic_potential_cube=True)
    - Dipole moment
    - Quadrupole moment
    - Mulliken and Löwdin atomic charges
    - Wiberg and Mayer bond orders

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Basic electronic properties
        result = submit_electronic_properties_workflow(
            initial_molecule="c1ccccc1",
            name="Benzene HOMO-LUMO"
        )

        # Full electronic analysis with visualization
        result = submit_electronic_properties_workflow(
            initial_molecule="CC(=O)Nc1ccc(O)cc1",
            functional="B3LYP",
            basis="def2-TZVP",
            compute_density_cube=True,
            compute_electrostatic_potential_cube=True,
            compute_num_occupied_orbitals=2,  # HOMO and HOMO-1
            compute_num_virtual_orbitals=2,   # LUMO and LUMO+1
            name="Acetaminophen electronic structure"
        )

        # Higher-level calculation with larger basis
        result = submit_electronic_properties_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            functional="wB97X-D3",
            basis="def2-TZVP",
            compute_num_occupied_orbitals=3,
            compute_num_virtual_orbitals=3,
            name="Caffeine DFT properties"
        )

        # Multiple orbital visualization
        result = submit_electronic_properties_workflow(
            initial_molecule="CCCC",
            compute_density_cube=True,
            compute_num_occupied_orbitals=5,
            compute_num_virtual_orbitals=5,
            name="Butane molecular orbitals"
        )

        # Electrostatic potential analysis
        result = submit_electronic_properties_workflow(
            initial_molecule="c1ccc(cc1)C=O",
            functional="PBE",
            compute_electrostatic_potential_cube=True,
            compute_density_cube=True,
            name="Benzaldehyde electrostatic potential"
        )

    """
    import logging
    logger = logging.getLogger(__name__)

    # Build workflow_data following exact API structure from GitHub tests
    # Settings object takes functional and basis (not method/basis_set at this level)
    workflow_data = {
        "settings": {
            "functional": functional,  # Pass as-is, API will normalize
            "basis": basis  # Pass as-is, API will normalize
        },
        "compute_density_cube": compute_density_cube,
        "compute_electrostatic_potential_cube": compute_electrostatic_potential_cube,
        "compute_num_occupied_orbitals": compute_num_occupied_orbitals,
        "compute_num_virtual_orbitals": compute_num_virtual_orbitals
    }

    # Submit the workflow
    logger.info(f"Submitting electronic properties workflow: {name}")
    workflow = rowan.submit_workflow(
        workflow_type="electronic_properties",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"Electronic properties workflow submitted with UUID: {workflow.uuid}")

    return workflow
