"""
Rowan v2 API: Molecular Dynamics Workflow
Run molecular dynamics simulations to study molecular behavior over time.
"""

from typing import Annotated
import rowan
import stjames


def submit_molecular_dynamics_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule for molecular dynamics simulation"],
    temperature: Annotated[float, "Simulation temperature in Kelvin"] = 300.0,
    simulation_time_ps: Annotated[float, "Total simulation time in picoseconds"] = 1000.0,
    equilibration_time_ps: Annotated[float, "Equilibration time before production run (picoseconds)"] = 100.0,
    timestep_fs: Annotated[float, "Integration timestep in femtoseconds"] = 1.0,
    pressure: Annotated[float, "Simulation pressure in atmospheres (0 for NVT ensemble, >0 for NPT)"] = 0.0,
    calc_engine: Annotated[str, "Calculation engine: 'aimnet2', 'xtb', 'gfn2', 'gfn1'"] = "aimnet2",
    solvent: Annotated[str, "Solvent environment for simulation (name or SMILES). Empty string for gas phase"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Molecular Dynamics Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0,
):
    """Submit a molecular dynamics workflow to simulate molecular motion over time.

    Args:
        initial_molecule: SMILES string representing the molecule
        temperature: Simulation temperature in Kelvin (default: 300.0 K)
        simulation_time_ps: Total production simulation time in picoseconds (default: 1000.0 ps = 1 ns)
        equilibration_time_ps: Equilibration time before production run (default: 100.0 ps)
        timestep_fs: Integration timestep in femtoseconds (default: 1.0 fs)
        pressure: Pressure in atmospheres - 0 for NVT (constant volume), >0 for NPT (constant pressure) (default: 0.0)
        calc_engine: Engine for energy/force calculations (default: 'aimnet2')
            - 'aimnet2': Fast, accurate neural network potential
            - 'xtb': Semi-empirical tight-binding
            - 'gfn2': GFN2-xTB method
            - 'gfn1': GFN1-xTB method
        solvent: Solvent environment, name or SMILES (default: empty for gas phase)
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Molecular dynamics simulations provide insights into:
    - Conformational flexibility and dynamics
    - Thermal stability and behavior
    - Solvent effects on molecular structure
    - Time-dependent properties
    - Reaction pathways and mechanisms

    The simulation will run for equilibration_time_ps + simulation_time_ps total.

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Basic MD simulation in gas phase
        result = submit_molecular_dynamics_workflow(
            initial_molecule="CCCC",
            temperature=300.0,
            simulation_time_ps=500.0,
            name="Butane MD 500ps"
        )

        # NPT ensemble simulation with pressure
        result = submit_molecular_dynamics_workflow(
            initial_molecule="c1ccccc1",
            temperature=298.15,
            pressure=1.0,
            simulation_time_ps=1000.0,
            calc_engine="aimnet2",
            name="Benzene NPT MD"
        )

        # Solvated drug molecule dynamics
        result = submit_molecular_dynamics_workflow(
            initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            solvent="water",
            temperature=310.0,
            simulation_time_ps=2000.0,
            equilibration_time_ps=200.0,
            name="Caffeine in water (2 ns)"
        )

        # High-temperature dynamics with fine timestep
        result = submit_molecular_dynamics_workflow(
            initial_molecule="CCO",
            temperature=400.0,
            timestep_fs=0.5,
            simulation_time_ps=500.0,
            calc_engine="gfn2",
            name="Ethanol high-T dynamics"
        )

        # Long production run with extensive equilibration
        result = submit_molecular_dynamics_workflow(
            initial_molecule="CC(=O)Nc1ccc(O)cc1",
            temperature=300.0,
            equilibration_time_ps=500.0,
            simulation_time_ps=5000.0,
            solvent="ethanol",
            name="Acetaminophen long MD"
        )

    MD simulations can take significant time depending on simulation length and engine.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Calculate total number of MD steps
    # Convert ps to fs, then divide by timestep_fs
    total_time_ps = equilibration_time_ps + simulation_time_ps
    total_time_fs = total_time_ps * 1000  # ps to fs
    num_steps = int(total_time_fs / timestep_fs)

    # Calculate save interval (aim for ~100 frames total)
    save_interval = max(1, num_steps // 100)

    # Build MD settings following exact API structure
    md_settings = {
        "temperature": temperature,
        "timestep": timestep_fs,
        "num_steps": num_steps,
        "save_interval": save_interval,
        "ensemble": "NPT" if pressure > 0 else "NVT"
    }

    # Add pressure if NPT ensemble
    if pressure > 0:
        md_settings["pressure"] = pressure

    # Build calc_settings following exact API structure
    # Note: aimnet2, xtb, gfn2, gfn1 are ML/semi-empirical methods that don't use basis sets
    calc_settings = {"method": calc_engine}

    # Only add basis set if using a method that needs one (not ML/semi-empirical)
    # Settings object expects "basis_set" not "basis"
    if calc_engine not in ["aimnet2", "xtb", "gfn2", "gfn1", "gfn2_xtb", "gfn1_xtb"]:
        calc_settings["basis_set"] = "def2-svp"

    # Build workflow_data
    workflow_data = {
        "settings": md_settings,  # MolecularDynamicsSettings
        "calc_settings": calc_settings,  # Settings for energy/force calculations
    }

    # Handle solvent
    if solvent:
        workflow_data["solvent"] = solvent

    # Submit the workflow
    logger.info(f"Submitting molecular dynamics workflow: {name}")
    logger.info(f"Total simulation: {total_time_ps} ps = {num_steps} steps (timestep: {timestep_fs} fs, saving every {save_interval} steps)")

    workflow = rowan.submit_workflow(
        workflow_type="molecular_dynamics",
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        workflow_data=workflow_data,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    workflow.update(public=True)

    logger.info(f"Molecular dynamics workflow submitted with UUID: {workflow.uuid}")

    return workflow
