"""
Rowan molecular dynamics function for MCP tool integration.
"""

from typing import Any, Dict, List, Optional
import rowan

def rowan_molecular_dynamics(
    name: str,
    molecule: str,
    ensemble: str = "nvt",
    initialization: str = "random",
    timestep: float = 1.0,
    num_steps: int = 500,
    save_interval: int = 10,
    temperature: float = 300.0,
    pressure: Optional[float] = None,
    langevin_thermostat_timescale: float = 100.0,
    berendsen_barostat_timescale: float = 1000.0,
    constraints: Optional[List[Dict[str, Any]]] = None,
    confining_constraint: Optional[Dict[str, Any]] = None,
    # Calculation settings parameters
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    # Workflow control parameters
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run molecular dynamics simulations following Rowan's MolecularDynamicsWorkflow.
    
    Performs MD simulations to study molecular dynamics, conformational sampling, 
    and thermal properties using various thermodynamic ensembles.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name
        ensemble: Thermodynamic ensemble ("nvt", "npt", "nve")
        initialization: Initial velocities ("random", "quasiclassical", "read")
        timestep: Integration timestep in femtoseconds
        num_steps: Number of MD steps to run
        save_interval: Save trajectory every N steps
        temperature: Temperature in Kelvin
        pressure: Pressure in atm (required for NPT)
        langevin_thermostat_timescale: Thermostat coupling timescale in fs
        berendsen_barostat_timescale: Barostat coupling timescale in fs
        constraints: List of pairwise harmonic constraints
        confining_constraint: Spherical harmonic constraint
        method: QM method for force calculation
        basis_set: Basis set for force calculation
        engine: Computational engine for force calculation
        charge: Molecular charge
        multiplicity: Spin multiplicity
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion
        ping_interval: Check status interval in seconds
    
    Example:
        # Glucose molecular dynamics simulation (working example)
        result = rowan_molecular_dynamics(
            name="glucose_md_simulation_v2",
            molecule="C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",
            ensemble="NVT",
            temperature=300,
            num_steps=10000,
            timestep=1,
            save_interval=100,
            initialization="random",
            blocking=True
        )
    
    Returns:
        Molecular dynamics workflow result
    """
    # Parameter validation (following stjames workflow specifications)
    valid_ensembles = ["nvt", "npt", "nve"]
    valid_initializations = ["random", "quasiclassical", "read"]
    
    # Validate ensemble
    ensemble_lower = ensemble.lower()
    if ensemble_lower not in valid_ensembles:
        return f" Error: Invalid ensemble '{ensemble}'. Valid options: {', '.join(valid_ensembles)}"
    
    # Validate initialization
    initialization_lower = initialization.lower()
    if initialization_lower not in valid_initializations:
        return f" Error: Invalid initialization '{initialization}'. Valid options: {', '.join(valid_initializations)}"
    
    # Validate numeric parameters
    if timestep <= 0:
        return f" Error: timestep must be positive (got {timestep})"
    if num_steps <= 0:
        return f" Error: num_steps must be positive (got {num_steps})"
    if save_interval <= 0:
        return f" Error: save_interval must be positive (got {save_interval})"
    if temperature <= 0:
        return f" Error: temperature must be positive (got {temperature})"
    
    # Validate NPT ensemble requirements
    if ensemble_lower == "npt" and pressure is None:
        return f" Error: NPT ensemble requires pressure to be specified"
    if pressure is not None and pressure <= 0:
        return f" Error: pressure must be positive (got {pressure})"
    
    # Apply smart defaults for MD calculations (fast methods preferred)
    if engine is None:
        engine = "xtb"  # Default to xTB for fast MD forces
    if method is None and engine.lower() == "xtb":
        method = "gfn2-xtb"  # Default xTB method
    elif method is None and engine.lower() != "xtb":
        method = "b3lyp"  # Default DFT method for other engines
    if basis_set is None and engine.lower() != "xtb":
        basis_set = "def2-svp"  # Default basis set for non-xTB engines
    
    # Build MD settings following MolecularDynamicsSettings structure
    md_settings = {
        "ensemble": ensemble_lower,
        "initialization": initialization_lower,
        "timestep": timestep,
        "num_steps": num_steps,
        "save_interval": save_interval,
        "temperature": temperature,
        "langevin_thermostat_timescale": langevin_thermostat_timescale,
        "berendsen_barostat_timescale": berendsen_barostat_timescale,
    }
    
    # Add optional fields if provided
    if pressure is not None:
        md_settings["pressure"] = pressure
    
    if constraints:
        md_settings["constraints"] = constraints
        
    if confining_constraint:
        md_settings["confining_constraint"] = confining_constraint
    
    # Build calc_settings following Settings structure
    calc_settings = {
        "charge": charge,
        "multiplicity": multiplicity,
        "engine": engine.lower()
    }
    
    # Add method if specified
    if method:
        calc_settings["method"] = method.lower()
    
    # Add basis_set if specified (not needed for xTB)
    if basis_set and engine.lower() != "xtb":
        calc_settings["basis_set"] = basis_set.lower()
    
    # Build parameters for Rowan API
    workflow_params = {
        "name": name,
        "molecule": molecule,
        "workflow_type": "molecular_dynamics",
        "settings": md_settings,
        "calc_settings": calc_settings,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add calc_engine at top level if different from calc_settings engine
    if engine:
        workflow_params["calc_engine"] = engine.lower()
    
    try:
        # Submit molecular dynamics calculation to Rowan
        result = rowan.compute(**workflow_params)
        return str(result)
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Molecular dynamics calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)

def test_rowan_molecular_dynamics():
    """Test the rowan_molecular_dynamics function."""
    try:
        # Test with minimal parameters
        result = rowan_molecular_dynamics(
            name="test_md_water",
            molecule="O",
            num_steps=10,  # Very short for testing
            blocking=False
        )
        print(" Molecular dynamics test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f" Molecular dynamics test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_molecular_dynamics()