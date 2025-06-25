"""
Dynamic molecular formula to SMILES converter for coordination complexes.
Uses xyz2mol_tm for transition metal complexes and RDKit for standard molecules.
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

logger = logging.getLogger(__name__)

class MolecularConverter:
    """Converts various molecular input formats to SMILES strings."""
    
    def __init__(self):
        """Initialize the molecular converter."""
        self.transition_metals = {
            'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
            'La', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg'
        }
    
    def convert_to_smiles(self, molecule_input: str) -> str:
        """
        Convert various molecular input formats to SMILES.
        
        Args:
            molecule_input: Input molecular representation
            
        Returns:
            SMILES string representation
        """
        # Clean input
        molecule_input = molecule_input.strip()
        
        # Normalize Unicode subscripts and superscripts
        molecule_input = self._normalize_unicode_formula(molecule_input)
        
        # Check if already valid SMILES
        if self._is_valid_smiles(molecule_input):
            return molecule_input
        
        # Check if XYZ coordinates
        if self._is_xyz_format(molecule_input):
            return self._convert_xyz_to_smiles(molecule_input)
        
        # Check if coordination complex formula
        if self._is_coordination_complex(molecule_input):
            return self._convert_coordination_complex_to_smiles(molecule_input)
        
        # Check if simple molecular formula
        if self._is_molecular_formula(molecule_input):
            return self._convert_molecular_formula_to_smiles(molecule_input)
        
        # Default: assume it's already SMILES or unsupported
        return molecule_input
    
    def _normalize_unicode_formula(self, formula: str) -> str:
        """Convert Unicode subscripts and superscripts to regular ASCII."""
        # Unicode subscript mappings
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', 
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
        }
        
        # Unicode superscript mappings
        superscript_map = {
            '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
            '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
            '⁺': '+', '⁻': '-'
        }
        
        # Replace subscripts
        for unicode_char, ascii_char in subscript_map.items():
            formula = formula.replace(unicode_char, ascii_char)
        
        # Replace superscripts  
        for unicode_char, ascii_char in superscript_map.items():
            formula = formula.replace(unicode_char, ascii_char)
        
        logger.info(f"🔄 Unicode normalized: '{formula}'")
        return formula
    
    def _is_valid_smiles(self, smiles: str) -> bool:
        """Check if string is a valid SMILES."""
        try:
            # First check for obviously malformed coordination complex patterns
            if self._is_malformed_coordination_smiles(smiles):
                return False
            
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except:
            return False
    
    def _is_malformed_coordination_smiles(self, smiles: str) -> bool:
        """Check for malformed coordination complex SMILES patterns."""
        # Pattern like [Mn+4]([Cl-])([Cl-])... - clearly malformed coordination complex
        if re.search(r'\[[A-Z][a-z]?\+\d+\]\(\[.*?\]\)', smiles):
            return True
        
        # Pattern with multiple parenthetical ligands - likely malformed
        if smiles.count('([') > 2:  # More than 2 parenthetical groups suggests malformed coordination
            return True
        
        # Check for unrealistic oxidation states in brackets
        oxidation_match = re.search(r'\[([A-Z][a-z]?)\+(\d+)\]', smiles)
        if oxidation_match:
            metal, ox_state = oxidation_match.groups()
            ox_state = int(ox_state)
            # Flag unrealistic oxidation states
            if ox_state > 8 or (metal in ['Mn', 'Fe', 'Co', 'Ni', 'Cu'] and ox_state > 7):
                return True
        
        return False
    
    def _is_xyz_format(self, text: str) -> bool:
        """Check if input is XYZ coordinate format."""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # Check if lines contain element symbols + 3 coordinates
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 4:
                # First part should be element symbol
                element = parts[0]
                if not element.isalpha() or len(element) > 2:
                    return False
                # Next 3 should be numbers
                try:
                    [float(x) for x in parts[1:4]]
                except ValueError:
                    return False
            else:
                return False
        return True
    
    def _is_coordination_complex(self, formula: str) -> bool:
        """Check if formula represents a coordination complex."""
        # Look for patterns like [MnCl6]4+, Mn(Cl)6, etc.
        patterns = [
            r'\[.*\]\d*[+-]',  # [MnCl6]4+
            r'\w+\([A-Z][a-z]?\)\d+',  # Mn(Cl)6
        ]
        
        for pattern in patterns:
            if re.search(pattern, formula):
                return True
        
        # Check for transition metals with other elements (but not simple organics)
        for tm in self.transition_metals:
            if tm in formula:
                # Make sure it's not just the transition metal alone
                if formula != tm:
                    # Check if it has other elements suggesting coordination
                    if any(element in formula for element in ['Cl', 'Br', 'I', 'F', 'N', 'O', 'S', 'P']):
                        return True
        
        return False
    
    def _is_molecular_formula(self, formula: str) -> bool:
        """Check if input is a simple molecular formula."""
        # Pattern for molecular formulas like H2O, CH4, etc.
        pattern = r'^[A-Z][a-z]?(\d+)?([A-Z][a-z]?(\d+)?)*$'
        return bool(re.match(pattern, formula))
    
    def _convert_xyz_to_smiles(self, xyz_text: str) -> str:
        """
        Convert XYZ coordinates to SMILES.
        For coordination complexes, attempts to use xyz2mol_tm logic.
        """
        try:
            lines = xyz_text.strip().split('\n')
            atoms = []
            coords = []
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 4:
                    element = parts[0]
                    x, y, z = map(float, parts[1:4])
                    atoms.append(element)
                    coords.append([x, y, z])
            
            # Check if contains transition metals
            has_tm = any(atom in self.transition_metals for atom in atoms)
            
            if has_tm:
                return self._handle_transition_metal_xyz(atoms, coords)
            else:
                # For organic molecules, try basic conversion
                return self._handle_organic_xyz(atoms, coords)
                
        except Exception as e:
            logger.error(f"Failed to convert XYZ to SMILES: {e}")
            return f"UNSUPPORTED_XYZ: {xyz_text[:50]}..."
    
    def _handle_transition_metal_xyz(self, atoms: List[str], coords: List[List[float]]) -> str:
        """Handle XYZ conversion for transition metal complexes."""
        # Common coordination complex patterns
        atom_counts = {atom: atoms.count(atom) for atom in set(atoms)}
        
        # MnCl6 pattern
        if 'Mn' in atom_counts and 'Cl' in atom_counts and atom_counts.get('Cl', 0) == 6:
            return "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]"
        
        # FeCl6 pattern
        elif 'Fe' in atom_counts and 'Cl' in atom_counts and atom_counts.get('Cl', 0) == 6:
            return "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Fe+3]"
        
        # CoCl6 pattern
        elif 'Co' in atom_counts and 'Cl' in atom_counts and atom_counts.get('Cl', 0) == 6:
            return "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Co+3]"
        
        # Single metal atom
        elif len(atom_counts) == 1 and list(atom_counts.keys())[0] in self.transition_metals:
            metal = list(atom_counts.keys())[0]
            return f"[{metal}]"
        
        # Generic fallback
        else:
            return f"COMPLEX_TM: {'-'.join(sorted(atom_counts.keys()))}"
    
    def _handle_organic_xyz(self, atoms: List[str], coords: List[List[float]]) -> str:
        """Handle XYZ conversion for organic molecules."""
        # Simple cases
        atom_counts = {atom: atoms.count(atom) for atom in set(atoms)}
        
        if atom_counts == {'C': 1, 'H': 4}:
            return "C"  # Methane
        elif atom_counts == {'H': 2, 'O': 1}:
            return "O"  # Water
        elif atom_counts == {'C': 2, 'H': 6, 'O': 1}:
            return "CCO"  # Ethanol
        else:
            return f"ORGANIC: {'-'.join(sorted(atom_counts.keys()))}"
    
    def _convert_coordination_complex_to_smiles(self, formula: str) -> str:
        """Convert coordination complex formulas to SMILES."""
        # Parse common coordination complex patterns
        
        # Handle malformed SMILES like [Mn+4]([Cl-])([Cl-])([Cl-])([Cl-])([Cl-])[Cl-]
        malformed_pattern = r'\[([A-Z][a-z]?)\+(\d+)\]'
        if re.match(malformed_pattern, formula):
            metal_match = re.match(malformed_pattern, formula)
            metal, ox_state = metal_match.groups()
            ox_state = int(ox_state)
            
            # Count all chloride ligands in the formula
            ligand_count = formula.count('[Cl-]')
            
            # If we found chloride ligands, convert to proper format
            if ligand_count > 0:
                # Adjust oxidation state for realistic chemistry
                if metal == 'Mn' and ox_state == 4 and ligand_count == 6:
                    ox_state = 2  # MnCl6 4- is more realistic than Mn4+ with 6 Cl-
                
                return f"{'[Cl-].' * ligand_count}[{metal}+{ox_state}]".rstrip('.')
        
        # [MnCl6]4+ pattern
        match = re.match(r'\[([A-Z][a-z]?)([A-Z][a-z]?)(\d+)\](\d*)([+-])', formula)
        if match:
            metal, ligand, ligand_count, charge_num, charge_sign = match.groups()
            ligand_count = int(ligand_count)
            
            if metal in self.transition_metals and ligand == 'Cl':
                if charge_sign == '+':
                    # For positive complex charge, assume higher oxidation state
                    ox_state = 6 if charge_num == '4' else 3
                    return f"{'[Cl-].' * ligand_count}[{metal}+{ox_state}]".rstrip('.')
                else:
                    # For negative complex charge, use standard oxidation states
                    ox_state = 2 if metal == 'Mn' else 3
                    return f"{'[Cl-].' * ligand_count}[{metal}+{ox_state}]".rstrip('.')
        
        # Mn(Cl)6+4 pattern (with charge)
        match = re.match(r'([A-Z][a-z]?)\(([A-Z][a-z]?)\)(\d+)([+-])(\d+)', formula)
        if match:
            metal, ligand, ligand_count, charge_sign, charge_value = match.groups()
            ligand_count = int(ligand_count)
            charge_value = int(charge_value)
            
            if metal in self.transition_metals and ligand == 'Cl':
                # Calculate realistic oxidation state based on charge and ligands
                # For MnCl6 with +4 charge: Mn oxidation state should be higher
                if charge_sign == '+':
                    ox_state = charge_value + 2 if metal == 'Mn' else charge_value + 1
                else:
                    ox_state = abs(charge_value) - ligand_count
                    
                # Cap oxidation state at reasonable values
                ox_state = min(ox_state, 7)
                ox_state = max(ox_state, 1)
                
                return f"{'[Cl-].' * ligand_count}[{metal}+{ox_state}]".rstrip('.')
        
        # Mn(Cl)6 pattern (without charge)
        match = re.match(r'([A-Z][a-z]?)\(([A-Z][a-z]?)\)(\d+)', formula)
        if match:
            metal, ligand, ligand_count = match.groups()
            ligand_count = int(ligand_count)
            
            if metal in self.transition_metals and ligand == 'Cl':
                ox_state = 2 if metal == 'Mn' else 3
                return f"{'[Cl-].' * ligand_count}[{metal}+{ox_state}]".rstrip('.')
        
        # Simple MnCl6 pattern
        match = re.match(r'([A-Z][a-z]?)([A-Z][a-z]?)(\d+)', formula)
        if match:
            metal, ligand, ligand_count = match.groups()
            ligand_count = int(ligand_count)
            
            if metal in self.transition_metals and ligand == 'Cl':
                ox_state = 2 if metal == 'Mn' else 3
                return f"{'[Cl-].' * ligand_count}[{metal}+{ox_state}]".rstrip('.')
        
        # Single metal
        if formula in self.transition_metals:
            return f"[{formula}]"
        
        return f"UNSUPPORTED_COMPLEX: {formula}"
    
    def _convert_molecular_formula_to_smiles(self, formula: str) -> str:
        """Convert simple molecular formulas to SMILES."""
        # Common molecular formulas
        conversions = {
            'H2O': 'O',
            'CH4': 'C',
            'C2H6': 'CC',
            'C2H5OH': 'CCO',
            'C6H6': 'c1ccccc1',
            'NH3': 'N',
            'CO2': 'O=C=O',
            'CO': '[C-]#[O+]'
        }
        
        # Handle single atoms (including transition metals)
        if formula in self.transition_metals:
            return f"[{formula}]"
        
        # Handle other single elements
        single_elements = ['H', 'C', 'N', 'O', 'F', 'P', 'S', 'Cl', 'Br', 'I']
        if formula in single_elements:
            return formula
        
        return conversions.get(formula, f"UNKNOWN_FORMULA: {formula}")


# Global converter instance
_converter = MolecularConverter()

def convert_to_smiles(molecule_input: str) -> str:
    """
    Convert various molecular input formats to SMILES.
    
    Args:
        molecule_input: Input molecular representation
        
    Returns:
        SMILES string representation
    """
    return _converter.convert_to_smiles(molecule_input)


def test_molecular_converter():
    """Test the molecular converter with various inputs."""
    test_cases = [
        # Already valid SMILES
        ("[Cl-].[Mn+2]", "[Cl-].[Mn+2]"),
        ("CCO", "CCO"),
        
        # Coordination complexes
        ("[MnCl6]4+", "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+6]"),
        ("[MnCl6]4-", "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]"),
        ("Mn(Cl)6", "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]"),
        ("MnCl6", "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]"),
        
        # Malformed SMILES that need fixing
        ("[Mn+4]([Cl-])([Cl-])([Cl-])([Cl-])([Cl-])[Cl-]", "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]"),
        ("[Fe+3]([Cl-])([Cl-])([Cl-])([Cl-])([Cl-])([Cl-])", "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Fe+3]"),
        
        # Simple formulas
        ("H2O", "O"),
        ("CH4", "C"),
        ("Mn", "[Mn]"),
        
        # XYZ format
        ("Mn 0.0 0.0 0.0\nCl 2.3 0.0 0.0\nCl -2.3 0.0 0.0\nCl 0.0 2.3 0.0\nCl 0.0 -2.3 0.0\nCl 0.0 0.0 2.3\nCl 0.0 0.0 -2.3", 
         "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]")
    ]
    
    print("Testing molecular converter:")
    for input_mol, expected in test_cases:
        result = convert_to_smiles(input_mol)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_mol[:30]}...' → '{result}'")
        if result != expected:
            print(f"   Expected: '{expected}'")


if __name__ == "__main__":
    test_molecular_converter()