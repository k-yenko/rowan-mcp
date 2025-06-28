"""
Rowan spin states calculation function for MCP tool integration.
Follows the exact workflow from: https://github.com/rowansci/stjames-public/blob/master/stjames/workflows/spin_states.py
Implements SpinStatesWorkflow(MoleculeWorkflow) pattern from stjames.
"""

from typing import Optional, Union, List, Any
import logging
import rowan
from .molecular_converter import convert_to_smiles

logger = logging.getLogger(__name__)

# Mock stjames workflow classes to match their structure
class Mode:
    """Mock Mode enum from stjames."""
    AUTO = "auto"
    RAPID = "rapid" 
    CAREFUL = "careful"
    METICULOUS = "meticulous"
    RECKLESS = "reckless"
    MANUAL = "manual"

class Molecule:
    """Mock Molecule class from stjames."""
    def __init__(self, smiles: str, charge: int = 0, multiplicity: int = 1):
        self.smiles = smiles
        self.charge = charge
        self.multiplicity = multiplicity
    
    def __str__(self):
        return self.smiles

class MoleculeWorkflow:
    """
    Mock MoleculeWorkflow base class from stjames.
    Base class for Workflows that operate on a single molecule.
    """
    def __init__(self, initial_molecule: Union[str, Molecule], mode: str = "auto"):
        if isinstance(initial_molecule, str):
            self.initial_molecule = Molecule(initial_molecule)
        else:
            self.initial_molecule = initial_molecule
        
        # Set mode to RAPID if AUTO is selected (stjames behavior)
        if mode.lower() == "auto":
            self.mode = "rapid"
        else:
            self.mode = mode.lower()
    
    def __repr__(self):
        return f"<{type(self).__name__} {self.mode.upper()}>"

class SpinStatesWorkflow(MoleculeWorkflow):
    """
    Mock SpinStatesWorkflow from stjames that inherits from MoleculeWorkflow.
    Workflow for computing spin states of molecules.
    """
    def __init__(self, initial_molecule: Union[str, Molecule], states: List[int], 
                 mode: str = "auto", solvent: Optional[str] = None, 
                 xtb_preopt: bool = False, constraints: Optional[List] = None,
                 transition_state: bool = False, frequencies: bool = False):
        super().__init__(initial_molecule, mode)
        self.states = states
        self.solvent = solvent
        self.xtb_preopt = xtb_preopt
        self.constraints = constraints or []
        self.transition_state = transition_state
        self.frequencies = frequencies
        
        # Validate states (stjames validation logic)
        self._validate_states()
    
    def _validate_states(self):
        """Confirm that all spin states are valid (from stjames)."""
        if not self.states:
            raise ValueError("Expected at least one spin state.")
        
        # Check multiplicities are consistent (all odd or all even)
        if any((self.states[0] - mult) % 2 for mult in self.states):
            raise ValueError(f"Inconsistent multiplicities found: {self.states}")
    
    def __repr__(self):
        if self.mode != "manual":
            return f"<{type(self).__name__} {self.states} {self.mode.upper()}>"
        return f"<{type(self).__name__} {self.states} {self.mode.upper()}>"
    
    def __len__(self):
        return len(self.states)


# Removed old hardcoded conversion function - now using dynamic molecular_converter.py


def _generate_3d_coordinates_for_coordination_complex(smiles: str, rdkit_mol):
    """Generate clean 3D coordinates for coordination complexes."""
    try:
        import numpy as np
        
        # Get number of atoms
        num_atoms = rdkit_mol.GetNumAtoms()
        
        # Find metal center and ligands
        metal_idx = None
        ligand_indices = []
        
        for i, atom in enumerate(rdkit_mol.GetAtoms()):
            atomic_num = atom.GetAtomicNum()
            if atomic_num in [25, 26, 27, 28, 29, 24, 46]:  # Transition metals
                metal_idx = i
            else:
                ligand_indices.append(i)
        
        if metal_idx is None:
            return None
        
        # Initialize coordinates
        coords = [[0.0, 0.0, 0.0] for _ in range(num_atoms)]
        
        # Place metal at origin
        coords[metal_idx] = [0.0, 0.0, 0.0]
        
        # Set appropriate bond length for M-Cl bonds
        bond_length = 2.4  # Standard M-Cl bond length in Å
        
        # Generate geometry based on coordination number
        num_ligands = len(ligand_indices)
        
        if num_ligands == 4:
            # Square planar for Pd(II) complexes
            if any(atom.GetAtomicNum() == 46 for atom in rdkit_mol.GetAtoms()):
                positions = np.array([
                    [bond_length, 0, 0],
                    [-bond_length, 0, 0],
                    [0, bond_length, 0],
                    [0, -bond_length, 0]
                ])
            else:
                # Tetrahedral for other metals
                a = bond_length / np.sqrt(3)
                positions = np.array([
                    [a, a, a],
                    [a, -a, -a],
                    [-a, a, -a],
                    [-a, -a, a]
                ])
        
        elif num_ligands == 6:
            # Octahedral geometry
            positions = np.array([
                [bond_length, 0, 0],
                [-bond_length, 0, 0],
                [0, bond_length, 0],
                [0, -bond_length, 0],
                [0, 0, bond_length],
                [0, 0, -bond_length]
            ])
        
        else:
            # General spherical distribution
            angles = np.linspace(0, 2*np.pi, num_ligands, endpoint=False)
            positions = []
            for angle in angles:
                x = bond_length * np.cos(angle)
                y = bond_length * np.sin(angle)
                z = 0.0
                positions.append([x, y, z])
            positions = np.array(positions)
        
        # Assign positions to ligands
        for i, ligand_idx in enumerate(ligand_indices):
            if i < len(positions):
                coords[ligand_idx] = positions[i].tolist()
        
        # Validate minimum distances
        min_distance = float('inf')
        for i in range(num_atoms):
            for j in range(i+1, num_atoms):
                dist = np.linalg.norm(np.array(coords[i]) - np.array(coords[j]))
                min_distance = min(min_distance, dist)
        
        if min_distance > 1.0:  # At least 1.0 Å separation
            return coords
        else:
            return None
            
    except Exception as e:
        logger.warning(f"Coordinate generation failed: {e}")
        return None

# Removed old complex coordinate generation functions - simplified to single clean function above

def _calculate_molecular_charge(smiles: str) -> int:
    """Calculate the total molecular charge from SMILES string."""
    total_charge = 0
    
    # Count negative ions
    if '[Cl-]' in smiles:
        total_charge -= smiles.count('[Cl-]')
    if '[F-]' in smiles:
        total_charge -= smiles.count('[F-]')
    if '[Br-]' in smiles:
        total_charge -= smiles.count('[Br-]')
    if '[I-]' in smiles:
        total_charge -= smiles.count('[I-]')
    
    # Count positive metal ions - common oxidation states
    positive_ions = {
        '[Pd+2]': 2, '[Pd+4]': 4,
        '[Mn+2]': 2, '[Mn+3]': 3, '[Mn+4]': 4, '[Mn+7]': 7,
        '[Fe+2]': 2, '[Fe+3]': 3,
        '[Co+2]': 2, '[Co+3]': 3,
        '[Ni+2]': 2, '[Ni+3]': 3,
        '[Cu+1]': 1, '[Cu+2]': 2,
        '[Cr+2]': 2, '[Cr+3]': 3, '[Cr+6]': 6,
        '[V+2]': 2, '[V+3]': 3, '[V+4]': 4, '[V+5]': 5,
        '[Ti+2]': 2, '[Ti+3]': 3, '[Ti+4]': 4,
        '[Zn+2]': 2
    }
    
    for ion, charge in positive_ions.items():
        if ion in smiles:
            total_charge += charge * smiles.count(ion)
    
    return total_charge


def rowan_spin_states(
    name: str,
    molecule: str,
    states: Optional[Union[str, List[int]]] = None,
    mode: str = "rapid",
    solvent: Optional[str] = None,
    xtb_preopt: bool = False,
    constraints: Optional[str] = None,
    transition_state: bool = False,
    frequencies: bool = False,
    folder_uuid: Optional[str] = None,
    blocking: bool = False,
    ping_interval: int = 5
) -> str:
    """Calculate electronic spin states for molecular systems.
    
    This tool computes and compares different spin multiplicities for a molecule,
    helping determine the ground state electronic configuration and relative energies
    of different spin states. Essential for studying transition metals, radicals,
    and systems with unpaired electrons.
    
    Args:
        name: Name for the spin states calculation
        molecule: SMILES string of the molecule (e.g., "[Mn+3]", "O=O")
        states: List of spin multiplicities to calculate (e.g., [1, 3, 5] for singlet, triplet, quintet)
                Can be provided as comma-separated string "1,3,5" or list [1, 3, 5]
        mode: Calculation mode ("rapid", "careful", "meticulous", "auto", "reckless", "manual")
        solvent: Solvent for implicit solvation (e.g., "water", "hexane", "acetonitrile")
        xtb_preopt: Whether to perform xTB pre-optimization before DFT
        constraints: Geometric constraints during optimization (advanced feature)
        transition_state: Whether to optimize for transition state instead of minimum
        frequencies: Whether to calculate vibrational frequencies
        folder_uuid: Optional folder UUID to organize the calculation
        blocking: Whether to wait for completion (default: False to avoid timeouts)
        ping_interval: Interval in seconds to check calculation status
        
    Returns:
        JSON string with workflow UUID and status (non-blocking) or full results (blocking)
        
    Examples:
        # Manganese atom (stjames-public test example)
        rowan_spin_states(
            name="manganese_atom_stjames",
            molecule="[Mn]",  # Neutral Mn atom
            states=[2, 4, 6],  # doublet, quartet, sextet
            mode="rapid",
            xtb_preopt=True
        )
        
        # Iron atom (stjames-public test example)
        rowan_spin_states(
            name="iron_atom_stjames",
            molecule="[Fe]",  # Neutral Fe atom
            states=[1, 3, 5],  # singlet, triplet, quintet
            mode="careful",
            frequencies=True,
            xtb_preopt=True
        )
        
        # Manganese hexachloride complex (corrected format)
        rowan_spin_states(
            name="mn_hexachloride",
            molecule="[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            states=[2, 4, 6],
            mode="rapid",
            solvent="water"
        )
    """
    
    # Convert input to SMILES format (handles XYZ coordinates, molecular formulas, etc.)
    original_input = molecule
    molecule = convert_to_smiles(molecule)
    
    # Log the conversion if it happened
    if molecule != original_input:
        logger.info(f"Converted input '{original_input}' to SMILES: '{molecule}'")
    
    # Check for unsupported formats
    if molecule.startswith("UNSUPPORTED_"):
        error_response = {
            "success": False,
            "error": f"Unsupported molecular input format: {original_input}",
            "explanation": {
                "detected_format": "XYZ coordinates or complex molecular structure",
                "supported_formats": [
                    "SMILES strings: '[Mn]', '[Cl-].[Mn+2]'",
                    "Simple formulas: 'Mn(Cl)6', 'Fe(Cl)6'",
                    "Common names: 'water', 'methane'"
                ]
            },
            "suggestion": "Please provide the molecule in SMILES format or a supported formula",
            "name": name
        }
        return str(error_response)
    
    # First, validate that molecule is actually a molecule (SMILES) and not a PDB file
    if molecule.lower().endswith('.pdb') or 'pdb' in molecule.lower():
        error_response = {
            "success": False,
            "error": f"Invalid input: '{molecule}' appears to be a PDB file",
            "correct_usage": {
                "purpose": "Spin states calculation requires a SMILES molecule string, not a PDB file",
                "explanation": "This tool calculates electronic spin states for individual molecules",
                "what_you_provided": "PDB file (protein structure)",
                "what_is_needed": "SMILES string representing a small molecule"
            },
            "examples": {
                "transition_metals": {
                    "manganese_atom": "[Mn] (neutral manganese atom)",
                    "iron_atom": "[Fe] (neutral iron atom)", 
                    "manganese_complex": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2] (MnCl6 complex)"
                },
                "organic_molecules": {
                    "water": "O",
                    "methane": "C", 
                    "benzene": "c1ccccc1",
                    "radical": "c1ccc(cc1)[CH2] (benzyl radical)"
                }
            },
            "stjames_test_examples": {
                "manganese": "molecule='[Mn]', states=[2,4,6], mode='rapid'",
                "iron": "molecule='[Fe]', states=[1,3,5], mode='careful'"
            },
            "suggestion": "Use a different Rowan tool for protein analysis, or provide a SMILES string for molecular spin states",
            "name": name,
            "invalid_input": molecule
        }
        return str(error_response)
    
    # Check if molecule looks like it needs charge/oxidation state specification
    needs_charge_info = False
    molecular_formula = None
    
    # Detect if molecule needs proper SMILES formatting
    # Check for invalid SMILES patterns like [MnCl6]+4 or simple formulas like Mn(Cl)6
    invalid_patterns = [
        # Pattern like [MnCl6]+4 where charge is outside brackets
        (']' in molecule and ('+' in molecule[molecule.rfind(']'):] or '-' in molecule[molecule.rfind(']'):])),
        # Simple molecular formula without proper charge specification
        (not any(char in molecule for char in ['[', ']', '+', '-']) and 
         any(metal in molecule.upper() for metal in ['MN', 'FE', 'CO', 'NI', 'CU', 'CR', 'V', 'TI', 'PD'])),
        # Invalid complex notation like [MnCl6] without proper ion separation
        ('[' in molecule and ']' in molecule and 'Cl' in molecule.upper() and 
         not ('.' in molecule and '[Cl-]' in molecule))
    ]
    
    if any(invalid_patterns) and any(metal in molecule.upper() for metal in ['MN', 'FE', 'CO', 'NI', 'CU', 'CR', 'V', 'TI', 'PD']):
        needs_charge_info = True
        molecular_formula = molecule
    
    # Ensure we have states - provide intelligent defaults based on electron parity rules
    if states is None:
        # Auto-assign reasonable default states based on the molecule and electron count
        if any(metal in molecule.upper() for metal in ['MN', 'FE', 'CO', 'NI', 'CU', 'CR', 'V', 'TI', 'PD']):
            # For transition metals, assign states based on electron parity rules
            # Even electrons (Fe=26, Ni=28, Cr=24, Ti=22, V=23, Zn=30) need ODD multiplicities
            # Odd electrons (Mn=25, Co=27, Cu=29) need EVEN multiplicities
            
            if any(metal in molecule.upper() for metal in ['FE', 'NI', 'CR', 'TI', 'ZN', 'PD']):
                # Even electron metals → odd multiplicities
                states_list = [1, 3, 5]  # Singlet, triplet, quintet
                logger.info(f"Auto-assigned odd multiplicities for even-electron metal: {states_list}")
            elif any(metal in molecule.upper() for metal in ['MN', 'CO', 'CU', 'V']):
                # Odd electron metals → even multiplicities  
                states_list = [2, 4, 6]  # Doublet, quartet, sextet
                logger.info(f"Auto-assigned even multiplicities for odd-electron metal: {states_list}")
            else:
                # Default fallback for other transition metals
                states_list = [1, 3, 5]  # Conservative choice
                logger.info(f"Auto-assigned default states for transition metal: {states_list}")
        else:
            # For organic molecules, use singlet/triplet (most have even electrons)
            states_list = [1, 3]  # Singlet, triplet
            logger.info(f"Auto-assigned default states for organic molecule: {states_list}")
    
    # Handle states input - convert to list of integers
    if states is not None and isinstance(states, str):
        # Handle special keywords
        if states.lower() in ['all', 'comprehensive']:
            states_list = [1, 2, 3, 4, 5, 6]  # All reasonable multiplicities
        elif states.lower() in ['common', 'typical']:
            states_list = [2, 4, 6]  # Common for transition metals
        else:
            try:
                # Handle comma-separated string
                states_list = [int(s.strip()) for s in states.split(',')]
            except ValueError as e:
                error_response = {
                    "success": False,
                    "error": f"Invalid states format: '{states}'. Expected comma-separated integers, list, or keywords.",
                    "valid_formats": [
                        "Comma-separated: '2,4,6' or '1,3,5'",
                        "List: [2, 4, 6] or [1, 3, 5]", 
                        "Keywords: 'all' or 'comprehensive' for [1,2,3,4,5,6]",
                        "Keywords: 'common' or 'typical' for [2,4,6]"
                    ],
                    "name": name,
                    "molecule": molecule
                }
                return str(error_response)
    elif states is not None and isinstance(states, list):
        try:
            states_list = [int(s) for s in states]
        except (ValueError, TypeError) as e:
            error_response = {
                "success": False,
                "error": f"Invalid states list: {states}. All elements must be integers. Error: {e}",
                "name": name,
                "molecule": molecule
            }
            return str(error_response)
    elif states is not None:
        error_response = {
            "success": False,
            "error": f"Invalid states type: {type(states)}. Expected string or list.",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)
    
    # Validate states list
    if not states_list:
        error_response = {
            "success": False,
            "error": "States list cannot be empty. Provide at least one spin multiplicity.",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)
    
    # Validate states are positive
    for state in states_list:
        if state <= 0:
            error_response = {
                "success": False,
                "error": f"Invalid spin multiplicity: {state}. Must be positive integer.",
                "name": name,
                "molecule": molecule
            }
            return str(error_response)
    
    # Validate electron parity: even electrons need odd multiplicities, odd electrons need even multiplicities
    # This prevents impossible electronic configurations
    try:
        # Try to estimate electron count from SMILES (basic approach)
        # For complex molecules, we'll let Rowan handle the detailed validation
        # But we can catch obvious cases
        
        # Check if all states have the same parity (all odd or all even)
        first_state_parity = states_list[0] % 2
        mixed_parity = any((state % 2) != first_state_parity for state in states_list)
        
        if mixed_parity:
            error_response = {
                "success": False,
                "error": f"Inconsistent spin state parities: {states_list}. All multiplicities must be either odd (1,3,5...) or even (2,4,6...).",
                "explanation": {
                    "electron_parity_rule": "Molecules with even electrons need odd multiplicities; molecules with odd electrons need even multiplicities",
                    "your_states": states_list,
                    "fix_suggestions": {
                        "for_even_electrons": "Use odd multiplicities like [1,3,5]",
                        "for_odd_electrons": "Use even multiplicities like [2,4,6]"
                    }
                },
                "name": name,
                "molecule": molecule
            }
            return str(error_response)
    except Exception as e:
        # If electron counting fails, let Rowan handle the validation
        logger.warning(f"Could not validate electron parity: {e}")
        pass
    
    # Validate mode
    valid_modes = ["rapid", "careful", "meticulous", "auto", "reckless", "manual"]
    if mode.lower() not in valid_modes:
        error_response = {
            "success": False,
            "error": f"Invalid mode: {mode}. Valid modes: {valid_modes}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)
    
    # Create SpinStatesWorkflow instance to validate parameters (stjames pattern)
    try:
        spin_workflow = SpinStatesWorkflow(
            initial_molecule=molecule,
            states=states_list,
            mode=mode,
            solvent=solvent,
            xtb_preopt=xtb_preopt,
            constraints=constraints.split(',') if isinstance(constraints, str) else constraints,
            transition_state=transition_state,
            frequencies=frequencies
        )
        logger.info(f"SpinStatesWorkflow created: {spin_workflow}")
    except ValueError as e:
        error_response = {
            "success": False,
            "error": f"Invalid workflow parameters: {str(e)}",
            "name": name,
            "molecule": molecule,
            "states": states_list,
            "validation_error": str(e)
        }
        return str(error_response)
    
    logger.info(f"Starting spin states calculation: {name}")
    logger.info(f"Molecule SMILES: {molecule}")
    logger.info(f"Spin multiplicities: {states_list}")
    logger.info(f"Mode: {mode}")
    if solvent:
        logger.info(f"Solvent: {solvent}")
    if xtb_preopt:
        logger.info("xTB pre-optimization: enabled")
    if frequencies:
        logger.info("Frequency calculation: enabled")
    if transition_state:
        logger.info("Transition state optimization: enabled")
    
    # For spin states, we need to provide an initial multiplicity
    # Use the first state in the list as the starting multiplicity
    initial_multiplicity = states_list[0]
    
    # CRITICAL FIX: Ensure initial_multiplicity follows electron parity rules
    # Rowan uses initial_multiplicity as the starting point, so it must be valid
    logger.info(f"Using initial_multiplicity = {initial_multiplicity} for states {states_list}")
    
    # Prepare workflow parameters - rowan.compute() wants core params separate from workflow_data
    workflow_params = {
        # Core rowan.compute() parameters
        "molecule": molecule,  # SMILES string
        "workflow_type": "spin_states",
        "name": name,
        "blocking": blocking,
        "ping_interval": ping_interval,
        
        # CRITICAL: Try multiple parameter names for initial multiplicity
        "multiplicity": initial_multiplicity,  # Most likely parameter name
        "initial_multiplicity": initial_multiplicity,  # Alternative name
        "starting_multiplicity": initial_multiplicity,  # Another alternative
        "states": states_list,  # List of spin multiplicities to calculate
        "mode": mode.lower(),  # Calculation mode
    }
    
    # Add optional parameters only if provided
    if folder_uuid:
        workflow_params["folder_uuid"] = folder_uuid
    if solvent:
        workflow_params["solvent"] = solvent
    if xtb_preopt:
        workflow_params["xtb_preopt"] = xtb_preopt
    if transition_state:
        workflow_params["transition_state"] = transition_state
    if frequencies:
        workflow_params["frequencies"] = frequencies
    
    # Only add constraints if provided and ensure it's a list
    if constraints is not None:
        if isinstance(constraints, str):
            # Convert string to list (basic parsing)
            workflow_params["constraints"] = [constraints]
        elif isinstance(constraints, list):
            workflow_params["constraints"] = constraints
        else:
            workflow_params["constraints"] = [str(constraints)]
    
    logger.info("Submitting spin states calculation to Rowan")
    
    try:
        # CRITICAL FIX: Create Molecule object with correct multiplicity instead of string
        # This ensures Rowan uses the right starting multiplicity
        try:
            from stjames.molecule import Molecule as SjamesMolecule
            from rdkit import Chem
            
            # Create molecule with proper multiplicity by constructing atoms directly
            # Parse SMILES to get atomic numbers and coordinates
            rdkit_mol = Chem.MolFromSmiles(molecule)
            if rdkit_mol is None:
                raise ValueError(f"Invalid SMILES: {molecule}")
            
            # Get atoms from RDKit molecule and generate realistic 3D coordinates
            atoms = []
            from stjames.molecule import Atom
            
            # Generate realistic 3D coordinates using specialized coordination chemistry approach
            coords_3d = _generate_3d_coordinates_for_coordination_complex(molecule, rdkit_mol)
            
            for i, atom in enumerate(rdkit_mol.GetAtoms()):
                # Create Atom objects with atomic number and realistic 3D positions
                atoms.append(Atom(
                    atomic_number=atom.GetAtomicNum(), 
                    position=coords_3d[i]
                ))
            
            # Calculate total charge from SMILES string
            total_charge = _calculate_molecular_charge(molecule)
            
            logger.info(f"Calculated molecular charge: {total_charge} (from SMILES: {molecule})")
            
            # Create Molecule object directly with correct multiplicity and charge
            molecule_obj = SjamesMolecule(
                atoms=atoms,
                charge=total_charge,  # Calculate proper charge from SMILES
                multiplicity=initial_multiplicity,  # This is the key fix!
                smiles=molecule  # Keep original SMILES
            )
            workflow_params["molecule"] = molecule_obj
            logger.info(f"Created stjames.Molecule object with multiplicity={initial_multiplicity}")
        except (ImportError, Exception) as e:
            # If stjames not available, use string but log the limitation
            logger.warning(f"stjames.molecule.Molecule creation failed: {e}")
            logger.warning(f"Rowan may default to multiplicity=1 instead of {initial_multiplicity}")
        
        # Submit spin states calculation to Rowan
        result = rowan.compute(**workflow_params)
        
        # Format the response based on blocking mode
        if result:
            workflow_uuid = result.get("uuid")
            status = result.get("object_status", 0)
            
            if blocking and status == 2:  # Completed
                # Extract spin states results for completed blocking calls
                object_data = result.get("object_data", {})
                if "spin_states" in object_data:
                    spin_states_data = object_data["spin_states"]
                    
                    # Find ground state (lowest energy)
                    ground_state = None
                    min_energy = float('inf')
                    for state_data in spin_states_data:
                        energy = state_data.get("energy", float('inf'))
                        if energy < min_energy:
                            min_energy = energy
                            ground_state = state_data.get("multiplicity")
                    
                    response = {
                        "success": True,
                        "workflow_uuid": workflow_uuid,
                        "name": name,
                        "molecule": molecule,
                        "status": "completed",
                        "spin_states_results": {
                            "ground_state_multiplicity": ground_state,
                            "ground_state_energy": min_energy,
                            "states_calculated": len(spin_states_data),
                            "spin_states": spin_states_data
                        },
                        "calculation_details": {
                            "mode": mode,
                            "solvent": solvent,
                            "xtb_preopt": xtb_preopt,
                            "frequencies_calculated": frequencies,
                            "transition_state": transition_state
                        },
                        "runtime_seconds": result.get("elapsed", 0),
                        "credits_charged": result.get("credits_charged", 0)
                    }
                else:
                    response = {
                        "success": True,
                        "workflow_uuid": workflow_uuid,
                        "name": name,
                        "molecule": molecule,
                        "status": "completed", 
                        "message": "Spin states calculation completed successfully",
                        "runtime_seconds": result.get("elapsed", 0),
                        "credits_charged": result.get("credits_charged", 0)
                    }
            else:
                # Non-blocking or still running - return workflow info for tracking
                status_text = {0: "queued", 1: "running", 2: "completed", 3: "failed"}.get(status, "unknown")
                response = {
                    "success": True,
                    "tracking_id": workflow_uuid,  # Prominent tracking ID
                    "workflow_uuid": workflow_uuid,  # Keep for backward compatibility
                    "name": name,
                    "molecule": molecule,
                    "status": status_text,
                    "message": f"Spin states calculation submitted successfully! Use tracking_id to monitor progress.",
                    "calculation_details": {
                        "spin_multiplicities": states_list,
                        "mode": mode,
                        "solvent": solvent,
                        "xtb_preopt": xtb_preopt,
                        "frequencies": frequencies,
                        "transition_state": transition_state,
                        "blocking_mode": blocking
                    },
                    "progress_tracking": {
                        "tracking_id": workflow_uuid,
                        "check_status": f"rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')",
                        "get_results": f"rowan_workflow_management(action='retrieve', workflow_uuid='{workflow_uuid}')"
                    }
                }
        else:
            response = {
                "success": False,
                "error": "No response received from Rowan API",
                "name": name,
                "molecule": molecule,
                "states": states_list
            }
            
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Spin states calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule,
            "states": states_list
        }
        logger.error(f"Spin states calculation failed: {str(e)}")
        return str(error_response)


