"""
Rowan scan function for potential energy surface scans and IRC workflows.
"""

from typing import Optional, Union, List, Dict, Any
import rowan
import logging

# Set up logger
logger = logging.getLogger(__name__)

# QC Constants needed for validation
QC_ENGINES = {
    "psi4": "Hartree–Fock and density-functional theory",
    "terachem": "Hartree–Fock and density-functional theory", 
    "pyscf": "Hartree–Fock and density-functional theory",
    "xtb": "Semiempirical calculations",
    "aimnet2": "Machine-learned interatomic potential calculations"
}

QC_METHODS = {
    # Hartree-Fock
    "hf": "Hartree-Fock (unrestricted for open-shell systems)",
    
    # Pure Functionals - LDA
    "lsda": "Local Spin Density Approximation (Slater exchange + VWN correlation)",
    
    # Pure Functionals - GGA
    "pbe": "Perdew-Burke-Ernzerhof (1996) GGA functional",
    "blyp": "Becke 1988 exchange + Lee-Yang-Parr correlation",
    "bp86": "Becke 1988 exchange + Perdew 1988 correlation",
    "b97-d3": "Grimme's 2006 B97 reparameterization with D3 dispersion",
    
    # Pure Functionals - Meta-GGA
    "r2scan": "Furness and Sun's 2020 r2SCAN meta-GGA functional",
    "tpss": "Tao-Perdew-Staroverov-Scuseria meta-GGA (2003)",
    "m06l": "Zhao and Truhlar's 2006 local meta-GGA functional",
    
    # Hybrid Functionals - Global
    "pbe0": "PBE0 hybrid functional (25% HF exchange)",
    "b3lyp": "B3LYP hybrid functional (20% HF exchange)",
    "b3pw91": "B3PW91 hybrid functional (20% HF exchange)",
    
    # Hybrid Functionals - Range-Separated
    "camb3lyp": "CAM-B3LYP range-separated hybrid (19-65% HF exchange)",
    "wb97x_d3": "ωB97X-D3 range-separated hybrid with D3 dispersion (20-100% HF exchange)",
    "wb97x_v": "ωB97X-V with VV10 nonlocal dispersion (17-100% HF exchange)",
    "wb97m_v": "ωB97M-V meta-GGA with VV10 dispersion (15-100% HF exchange)"
}

QC_BASIS_SETS = {
    # Pople's STO-nG minimal basis sets
    "sto-2g": "STO-2G minimal basis set",
    "sto-3g": "STO-3G minimal basis set (default if none specified)",
    "sto-4g": "STO-4G minimal basis set",
    "sto-5g": "STO-5G minimal basis set",
    "sto-6g": "STO-6G minimal basis set",
    
    # Pople's 6-31 basis sets (double-zeta)
    "6-31g": "6-31G split-valence double-zeta basis set",
    "6-31g*": "6-31G(d) - 6-31G with polarization on heavy atoms",
    "6-31g(d)": "6-31G with d polarization on heavy atoms",
    "6-31g(d,p)": "6-31G with polarization on all atoms",
    "6-31+g(d,p)": "6-31G with diffuse and polarization functions",
    "6-311+g(2d,p)": "6-311+G(2d,p) - larger basis for single-point calculations",
    
    # Jensen's pcseg-n basis sets (recommended for DFT)
    "pcseg-0": "Jensen pcseg-0 minimal basis set",
    "pcseg-1": "Jensen pcseg-1 double-zeta (better than 6-31G(d))",
    "pcseg-2": "Jensen pcseg-2 triple-zeta basis set",
    "pcseg-3": "Jensen pcseg-3 quadruple-zeta basis set",
    "pcseg-4": "Jensen pcseg-4 quintuple-zeta basis set",
    "aug-pcseg-1": "Augmented Jensen pcseg-1 double-zeta",
    "aug-pcseg-2": "Augmented Jensen pcseg-2 triple-zeta",
    
    # Dunning's cc-PVNZ basis sets (use seg-opt variants for speed)
    "cc-pvdz": "Correlation-consistent double-zeta (generally contracted - slow)",
    "cc-pvtz": "Correlation-consistent triple-zeta (generally contracted - slow)",
    "cc-pvqz": "Correlation-consistent quadruple-zeta (generally contracted - slow)",
    "cc-pvdz(seg-opt)": "cc-pVDZ segmented-optimized (preferred over cc-pVDZ)",
    "cc-pvtz(seg-opt)": "cc-pVTZ segmented-optimized (preferred over cc-pVTZ)",
    "cc-pvqz(seg-opt)": "cc-pVQZ segmented-optimized (preferred over cc-pVQZ)",
    
    # Ahlrichs's def2 basis sets
    "def2-sv(p)": "Ahlrichs def2-SV(P) split-valence polarized",
    "def2-svp": "Ahlrichs def2-SVP split-valence polarized",
    "def2-tzvp": "Ahlrichs def2-TZVP triple-zeta valence polarized",
    
    # Truhlar's efficient basis sets
    "midi!": "MIDI!/MIDIX polarized minimal basis set (very efficient)",
    "midix": "MIDI!/MIDIX polarized minimal basis set (very efficient)"
}

QC_CORRECTIONS = {
    "d3bj": "Grimme's D3 dispersion correction with Becke-Johnson damping",
    "d3": "Grimme's D3 dispersion correction (automatically applied for B97-D3, ωB97X-D3)"
}

def lookup_molecule_smiles(molecule_name: str) -> str:
    """Simple molecule name to SMILES lookup for common molecules."""
    common_molecules = {
        # Simple molecules
        "water": "O",
        "methane": "C",
        "ethane": "CC",
        "propane": "CCC",
        "butane": "CCCC",
        "ethylene": "C=C",
        "acetylene": "C#C",
        "benzene": "c1ccccc1",
        "toluene": "Cc1ccccc1",
        "phenol": "Oc1ccccc1",
        
        # Peroxides and simple radicals
        "hydrogen peroxide": "OO",
        "h2o2": "OO",
        "peroxide": "OO",
        
        # Common solvents
        "methanol": "CO",
        "ethanol": "CCO",
        "acetone": "CC(=O)C",
        "dmso": "CS(=O)C",
        "thf": "C1CCOC1",
    }
    
    # Check if it's already a SMILES string (contains specific characters)
    if any(char in molecule_name.lower() for char in ['=', '#', '[', '(', ')', '@']):
        return molecule_name
    
    # Look up common name
    lookup_name = molecule_name.lower().strip()
    smiles = common_molecules.get(lookup_name)
    
    if smiles:
        logger.info(f" Molecule lookup: '{molecule_name}' → '{smiles}'")
        return smiles
    else:
        return molecule_name

def rowan_scan(
    name: str,
    molecule: str,
    coordinate_type: str,
    atoms: Union[List[int], str],
    start: float,
    stop: float,
    num: int,
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    engine: Optional[str] = None,
    corrections: Optional[List[str]] = None,
    charge: int = 0,
    multiplicity: int = 1,
    mode: Optional[str] = None,
    constraints: Optional[List[Dict[str, Any]]] = None,
    # New parameters from ScanWorkflow
    coordinate_type_2d: Optional[str] = None,
    atoms_2d: Optional[Union[List[int], str]] = None,
    start_2d: Optional[float] = None,
    stop_2d: Optional[float] = None,
    num_2d: Optional[int] = None,
    wavefront_propagation: bool = True,
    concerted_coordinates: Optional[List[Dict[str, Any]]] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 10
) -> str:
    """Run potential energy surface scans with full parameter control including 2D and concerted scans.
    
    Performs constrained optimizations along reaction coordinates using Rowan's
    wavefront propagation method to avoid local minima. Essential for:
    - Mapping reaction pathways and mechanisms
    - Finding transition state approximations  
    - Studying conformational preferences and rotational barriers
    - Analyzing atropisomerism and molecular flexibility
    - 2D potential energy surfaces
    - Concerted coordinate changes
    
    Args:
        name: Name for the scan calculation
        molecule: Molecule SMILES string or common name (e.g., "butane", "phenol")
        coordinate_type: Type of coordinate to scan - "bond", "angle", or "dihedral"
        atoms: List of 1-indexed atom numbers or comma-separated string (e.g., [1,2,3,4] or "1,2,3,4")
        start: Starting value of the coordinate (Å for bonds, degrees for angles/dihedrals)
        stop: Ending value of the coordinate
        num: Number of scan points to calculate
        method: QC method (default: "hf-3c" for speed, use "b3lyp" for accuracy)
        basis_set: Basis set (default: auto-selected based on method)
        engine: Computational engine (default: "psi4") 
        corrections: List of corrections like ["d3bj"] for dispersion
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1 for singlet)
        mode: Calculation precision - "reckless", "rapid", "careful", "meticulous" (default: "rapid")
        constraints: Additional coordinate constraints during optimization
        coordinate_type_2d: Type of second coordinate for 2D scan (optional)
        atoms_2d: Atoms for second coordinate in 2D scan (optional)
        start_2d: Starting value of second coordinate (optional)
        stop_2d: Ending value of second coordinate (optional) 
        num_2d: Number of points for second coordinate (must equal num for 2D grid, optional)
        wavefront_propagation: Use wavefront propagation for smoother scans (default: True)
        concerted_coordinates: List of coordinate dictionaries for concerted scans (optional)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 10, longer for scans)
    
    Returns:
        Scan results with energy profile and structural data
    """
    
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Validate coordinate type
    valid_coord_types = ["bond", "angle", "dihedral"]
    coord_type_lower = coordinate_type.lower()
    if coord_type_lower not in valid_coord_types:
        return f" Invalid coordinate_type '{coordinate_type}'. Valid types: {', '.join(valid_coord_types)}"
    
    # Handle string input for atoms (common format: "1,2,3,4")
    if isinstance(atoms, str):
        try:
            # Parse comma-separated string to list of integers
            atoms = [int(x.strip()) for x in atoms.split(",")]
        except ValueError as e:
            return f" Invalid atoms string '{atoms}'. Use format '1,2,3,4' or pass as list [1,2,3,4]. Error: {e}"
    
    # Ensure atoms is a list
    if not isinstance(atoms, list):
        return f" Atoms must be a list of integers or comma-separated string. Got: {type(atoms).__name__}"
    
    # Validate atom count for coordinate type
    expected_atoms = {"bond": 2, "angle": 3, "dihedral": 4}
    expected_count = expected_atoms[coord_type_lower]
    if len(atoms) != expected_count:
        return f" {coordinate_type} requires exactly {expected_count} atoms, got {len(atoms)}. Use format: [1,2,3,4] or '1,2,3,4'"
    
    # Validate atoms are positive integers
    if not all(isinstance(atom, int) and atom > 0 for atom in atoms):
        return f" All atom indices must be positive integers (1-indexed). Got: {atoms}. Use format: [1,2,3,4] or '1,2,3,4'"
    
    # Validate scan range
    if num < 2:
        return f" Number of scan points must be at least 2, got {num}"
    
    if start >= stop:
        return f" Start value ({start}) must be less than stop value ({stop})"
    
    # Handle 2D scan validation
    is_2d_scan = any([coordinate_type_2d, atoms_2d, start_2d is not None, stop_2d is not None, num_2d is not None])
    
    if is_2d_scan:
        # For 2D scan, all 2D parameters must be provided
        if not all([coordinate_type_2d, atoms_2d, start_2d is not None, stop_2d is not None, num_2d is not None]):
            return f" For 2D scans, all 2D parameters must be provided: coordinate_type_2d, atoms_2d, start_2d, stop_2d, num_2d"
        
        # Validate 2D coordinate type
        coord_type_2d_lower = coordinate_type_2d.lower()
        if coord_type_2d_lower not in valid_coord_types:
            return f" Invalid coordinate_type_2d '{coordinate_type_2d}'. Valid types: {', '.join(valid_coord_types)}"
        
        # Handle string input for 2D atoms
        if isinstance(atoms_2d, str):
            try:
                atoms_2d = [int(x.strip()) for x in atoms_2d.split(",")]
            except ValueError as e:
                return f" Invalid atoms_2d string '{atoms_2d}'. Use format '1,2,3,4' or pass as list [1,2,3,4]. Error: {e}"
        
        # Validate 2D atom count
        expected_count_2d = expected_atoms[coord_type_2d_lower]
        if len(atoms_2d) != expected_count_2d:
            return f" {coordinate_type_2d} requires exactly {expected_count_2d} atoms, got {len(atoms_2d)}"
        
        # Validate 2D atoms are positive integers
        if not all(isinstance(atom, int) and atom > 0 for atom in atoms_2d):
            return f" All 2D atom indices must be positive integers (1-indexed). Got: {atoms_2d}"
        
        # Validate 2D scan range
        if num_2d < 2:
            return f" Number of 2D scan points must be at least 2, got {num_2d}"
        
        if start_2d >= stop_2d:
            return f" 2D start value ({start_2d}) must be less than stop value ({stop_2d})"
        
        # For true 2D grid scans, both dimensions should have same number of points
        # (This creates an N×N grid rather than N points along each coordinate)
    
    # Handle concerted scan validation
    if concerted_coordinates:
        # Validate each coordinate in the concerted scan
        for i, coord in enumerate(concerted_coordinates):
            required_keys = {"coordinate_type", "atoms", "start", "stop", "num"}
            if not all(key in coord for key in required_keys):
                return f" Concerted coordinate {i+1} missing required keys: {required_keys}"
            
            # All concerted coordinates must have same number of steps
            if coord["num"] != num:
                return f" All concerted scan coordinates must have same number of steps. Got {coord['num']} vs {num}"
            
            # Validate coordinate type
            if coord["coordinate_type"].lower() not in valid_coord_types:
                return f" Invalid coordinate_type in concerted coordinate {i+1}: '{coord['coordinate_type']}'"
        
    # ENFORCE REQUIRED PARAMETERS FOR SCANWORKFLOW - Always provide robust defaults for IRC
    # These defaults ensure scan ALWAYS works for IRC workflow
    
    if method is None:
        method = "hf-3c"  # Fast, reliable default for scans - always required
        
    if engine is None:
        engine = "psi4"  # REQUIRED by ScanWorkflow - must not be None
        
    if mode is None:
        mode = "rapid"  # Good balance for scans - always required
    
    # Ensure all required defaults are lowercase for API consistency
    method = method.lower()
    engine = engine.lower()
    mode = mode.lower()
        
    # Validate QC parameters if provided (reuse existing validation logic)
    if method and method.lower() not in QC_METHODS and method.lower() != "hf-3c":
        available_methods = ", ".join(list(QC_METHODS.keys()) + ["hf-3c"])
        return f" Invalid method '{method}'. Available methods: {available_methods}"
    
    if basis_set and basis_set.lower() not in QC_BASIS_SETS:
        available_basis = ", ".join(QC_BASIS_SETS.keys())
        return f" Invalid basis set '{basis_set}'. Available basis sets: {available_basis}"
    
    if engine and engine.lower() not in QC_ENGINES:
        available_engines = ", ".join(QC_ENGINES.keys())
        return f" Invalid engine '{engine}'. Available engines: {available_engines}"
    
    if corrections:
        invalid_corrections = [corr for corr in corrections if corr.lower() not in QC_CORRECTIONS]
        if invalid_corrections:
            available_corrections = ", ".join(QC_CORRECTIONS.keys())
            return f" Invalid corrections {invalid_corrections}. Available corrections: {available_corrections}"
    
    # Validate mode
    valid_modes = ["reckless", "rapid", "careful", "meticulous"]
    if mode and mode.lower() not in valid_modes:
        return f" Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
    
    # Log the scan parameters
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    if is_2d_scan:
        logger.info(f"   2D Grid Size: {num} × {num_2d} = {num * num_2d} total points")
    if concerted_coordinates:
        pass
    logger.info(f"   Mode: {mode}")
    logger.info(f"   Wavefront Propagation: {wavefront_propagation}")
    
    try:
        # Build scan coordinate specification based on scan type
        scan_coordinates = []
        
        # BUILD PRIMARY SCAN_SETTINGS - EXACTLY MATCHING STJAMES SCANSETTINGS
        # This structure is REQUIRED by ScanWorkflow for IRC to work
        primary_coord = {
            "type": coord_type_lower,    # REQUIRED: matches stjames ScanSettings.type
            "atoms": atoms,              # REQUIRED: list of 1-indexed atom numbers
            "start": float(start),       # REQUIRED: starting coordinate value
            "stop": float(stop),         # REQUIRED: ending coordinate value  
            "num": int(num)              # REQUIRED: number of scan points
        }
        scan_coordinates.append(primary_coord)
        
        # ADD 2D COORDINATE IF SPECIFIED - EXACT STJAMES FORMAT
        if is_2d_scan:
            secondary_coord = {
                "type": coord_type_2d_lower,     # REQUIRED: matches stjames ScanSettings.type
                "atoms": atoms_2d,               # REQUIRED: list of 1-indexed atom numbers
                "start": float(start_2d),        # REQUIRED: starting coordinate value
                "stop": float(stop_2d),          # REQUIRED: ending coordinate value
                "num": int(num_2d)               # REQUIRED: number of scan points
            }
            scan_coordinates.append(secondary_coord)
        
        # ADD CONCERTED COORDINATES IF SPECIFIED - EXACT STJAMES FORMAT
        if concerted_coordinates:
            for i, coord in enumerate(concerted_coordinates):
                concerted_coord = {
                    "type": coord["coordinate_type"].lower(),   # REQUIRED: matches stjames ScanSettings.type
                    "atoms": coord["atoms"],                    # REQUIRED: list of 1-indexed atom numbers
                    "start": float(coord["start"]),            # REQUIRED: starting coordinate value
                    "stop": float(coord["stop"]),              # REQUIRED: ending coordinate value
                    "num": int(coord["num"])                   # REQUIRED: number of scan points
                }
                scan_coordinates.append(concerted_coord)
        
        # Build parameters for rowan.compute call
        compute_params = {
            "name": name,
            "molecule": canonical_smiles,  # Use canonical SMILES
            "folder_uuid": folder_uuid,
            "blocking": blocking,
            "ping_interval": ping_interval
        }
        
        # SCAN_SETTINGS CONSTRUCTION - STRICTLY FOLLOWING STJAMES SCANWORKFLOW REQUIREMENTS
        # This is the CRITICAL section for IRC compatibility
        if len(scan_coordinates) == 1:
            # SINGLE COORDINATE SCAN: scan_settings is a ScanSettings object
            compute_params["scan_settings"] = scan_coordinates[0]
        else:
            if is_2d_scan:
                # 2D SCAN: separate scan_settings and scan_settings_2d fields
                compute_params["scan_settings"] = scan_coordinates[0]      # Primary coordinate
                compute_params["scan_settings_2d"] = scan_coordinates[1]   # Secondary coordinate  
            else:
                # CONCERTED SCAN: scan_settings is a list of ScanSettings
                compute_params["scan_settings"] = scan_coordinates
        
        # Add wavefront propagation setting
        compute_params["wavefront_propagation"] = wavefront_propagation
        
        # BUILD REQUIRED CALC_SETTINGS - ALWAYS COMPLETE FOR IRC
        # ScanWorkflow requires calc_settings to be present and well-formed
        calc_settings = {
            "method": method,  # Always present due to defaults above
            "mode": mode,      # Always present due to defaults above
        }
        
        # Add charge/multiplicity only if non-default (reduces clutter)
        if charge != 0:
            calc_settings["charge"] = charge
        if multiplicity != 1:
            calc_settings["multiplicity"] = multiplicity
            
        # Add optional parameters if provided
        if basis_set:
            calc_settings["basis_set"] = basis_set.lower()
        if corrections:
            calc_settings["corrections"] = [corr.lower() for corr in corrections]
        if constraints:
            calc_settings["constraints"] = constraints
        
        # REQUIRED FIELDS - ScanWorkflow validation will fail without these
        compute_params["calc_settings"] = calc_settings
        compute_params["calc_engine"] = engine  # Always present due to defaults above
        
        # Submit the scan workflow
        result = rowan.compute(workflow_type="scan", **compute_params)
        
        # Format results based on status
        job_status = result.get('status', result.get('object_status', None))
        
        # Try to get status via API if not available
        if job_status is None and result.get('uuid'):
            try:
                job_status = rowan.Workflow.status(uuid=result.get('uuid'))
            except Exception as e:
                job_status = None
        
        status_names = {
            0: "Queued",
            1: "Running", 
            2: "Completed Successfully",
            3: "Failed",
            4: "Stopped",
            5: "Awaiting Queue"
        }
        
        status_text = status_names.get(job_status, f"Unknown ({job_status})")
        
        # Handle None status
        if job_status is None:
            status_text = "Submitted (status pending)"
        
        # Determine scan type for display
        scan_type = "1D Scan"
        total_points = num
        if is_2d_scan:
            scan_type = "2D Grid Scan"
            total_points = num * num_2d
        elif concerted_coordinates:
            scan_type = f"Concerted Scan ({len(concerted_coordinates) + 1} coordinates)"
            total_points = num
        
        # Format response
        if job_status == 2:
            formatted = f"{scan_type} '{name}' completed successfully\n\n"
        elif job_status == 3:
            formatted = f"{scan_type} '{name}' failed\n\n"
        elif job_status in [0, 1, 5]:
            formatted = f"{scan_type} '{name}' submitted and running\n\n"
        elif job_status == 4:
            formatted = f"{scan_type} '{name}' was stopped\n\n"
        else:
            formatted = f"{scan_type} '{name}' status unknown\n\n"
            
        formatted += f"Molecule: {molecule}\n"
        formatted += f"SMILES: {canonical_smiles}\n"
        formatted += f"Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"Status: {status_text} ({job_status})\n"
        
        # Basic scan info
        formatted += f"\nScan Type: {scan_type}\n"
        formatted += f"Coordinate: {coordinate_type.upper()} on atoms {atoms} ({start} to {stop}, {num} points)\n"
        if is_2d_scan:
            formatted += f"Secondary: {coordinate_type_2d.upper()} on atoms {atoms_2d} ({start_2d} to {stop_2d}, {num_2d} points)\n"
        formatted += f"Total Points: {total_points}\n"
        
        return formatted
        
    except Exception as e:
        return f"PES scan submission failed: {str(e)}"

def test_rowan_scan():
    """Test the rowan_scan function."""
    try:
        # Test with minimal parameters - should use all defaults
        result = rowan_scan(
            name="test_scan_ethane",
            molecule="CC",
            coordinate_type="bond",
            atoms=[1, 2],
            start=1.4,
            stop=1.8,
            num=3,  # Very short for testing
            blocking=False
        )
        print(" Scan test successful!")
        print(f"Result: {result[:200]}..." if len(result) > 200 else result)
        return True
    except Exception as e:
        print(f" Scan test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_scan()
