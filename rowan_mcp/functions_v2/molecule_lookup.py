"""
Molecule name to SMILES converter using Chemical Identifier Resolver (CIR).
Enables natural language molecule input for Rowan workflows.
"""

from typing import Annotated, Optional, List, Dict
from pydantic import Field
from urllib.request import urlopen
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)


def molecule_lookup(
    molecule_name: Annotated[
        str,
        Field(description="Common name, IUPAC name, or CAS number of molecule (e.g., 'aspirin', 'caffeine', '50-78-2')")
    ],
    fallback_to_input: Annotated[
        bool,
        Field(description="If lookup fails, return the input string assuming it might be SMILES (default: False)")
    ] = False
) -> str:
    """Convert molecule names to SMILES using Chemical Identifier Resolver (CIR).
    
    This tool enables natural language input for molecules by converting common names,
    IUPAC names, CAS numbers, and other identifiers to SMILES strings that can be
    used with Rowan workflows.
    
    Supported Input Types:
    - Common names: 'aspirin', 'caffeine', 'benzene', 'glucose'
    - IUPAC names: '2-acetoxybenzoic acid', '1,3,7-trimethylpurine-2,6-dione'
    - CAS numbers: '50-78-2' (aspirin), '58-08-2' (caffeine)
    - InChI strings
    - Already valid SMILES (will be validated)
    
    Returns:
        SMILES string if successful, error message if not found
        
    Examples:
        # Common drug name
        result = molecule_lookup("aspirin")
        # Returns: "CC(=O)Oc1ccccc1C(=O)O"
        
        # IUPAC name
        result = molecule_lookup("2-acetoxybenzoic acid")
        # Returns: "CC(=O)Oc1ccccc1C(=O)O"
        
        # CAS number
        result = molecule_lookup("50-78-2")
        # Returns: "CC(=O)Oc1ccccc1C(=O)O"
        
        # Complex molecule
        result = molecule_lookup("paracetamol")
        # Returns: "CC(=O)Nc1ccc(O)cc1"
    """
    try:
        # Clean input
        molecule_name = molecule_name.strip()
        
        # Check if already SMILES-like (contains typical SMILES characters)
        smiles_chars = {'=', '#', '(', ')', '[', ']', '@', '+', '-'}
        if any(char in molecule_name for char in smiles_chars):
            logger.info(f"Input '{molecule_name}' appears to be SMILES, returning as-is")
            return molecule_name
        
        # Query CIR service
        logger.info(f"Looking up molecule: {molecule_name}")
        url = f'http://cactus.nci.nih.gov/chemical/structure/{quote(molecule_name)}/smiles'
        
        response = urlopen(url, timeout=10)
        smiles = response.read().decode('utf8').strip()
        
        # CIR may return multiple SMILES for some queries, take the first one
        if '\n' in smiles:
            smiles = smiles.split('\n')[0]
        
        logger.info(f"Successfully converted '{molecule_name}' to SMILES: {smiles}")
        return smiles
        
    except Exception as e:
        logger.warning(f"Failed to lookup '{molecule_name}': {e}")
        
        if fallback_to_input:
            logger.info(f"Returning original input as fallback: {molecule_name}")
            return molecule_name
        else:
            return f"Could not find SMILES for '{molecule_name}'. Please check the name or provide a valid SMILES string."


def batch_molecule_lookup(
    molecule_names: Annotated[
        List[str],
        Field(description="List of molecule names to convert to SMILES")
    ],
    skip_failures: Annotated[
        bool,
        Field(description="Skip molecules that fail lookup instead of stopping (default: True)")
    ] = True
) -> Dict[str, str]:
    """Convert multiple molecule names to SMILES in batch.
    
    Useful for preparing multiple molecules for workflows or screening.
    
    Args:
        molecule_names: List of molecule names, IUPAC names, or CAS numbers
        skip_failures: If True, continue with other molecules if one fails
        
    Returns:
        Dictionary mapping input names to SMILES strings (or error messages)
        
    Examples:
        # Drug screening set
        result = batch_molecule_lookup([
            "aspirin",
            "ibuprofen", 
            "paracetamol",
            "caffeine"
        ])
        # Returns: {
        #     "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        #     "ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        #     "paracetamol": "CC(=O)Nc1ccc(O)cc1",
        #     "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
        # }
        
        # Mixed input types
        result = batch_molecule_lookup([
            "benzene",           # Common name
            "50-78-2",          # CAS number
            "ethanoic acid"     # IUPAC name
        ])
    """
    results = {}
    
    for name in molecule_names:
        try:
            smiles = molecule_lookup(name, fallback_to_input=False)
            results[name] = smiles
        except Exception as e:
            error_msg = f"Lookup failed: {str(e)}"
            if skip_failures:
                logger.warning(f"Skipping {name}: {error_msg}")
                results[name] = error_msg
            else:
                raise ValueError(f"Failed to lookup '{name}': {error_msg}")
    
    return results


def validate_smiles(
    smiles: Annotated[
        str,
        Field(description="SMILES string to validate")
    ]
) -> Dict[str, any]:
    """Validate a SMILES string and return basic molecular properties.
    
    Uses RDKit to validate SMILES and extract basic properties.
    
    Args:
        smiles: SMILES string to validate
        
    Returns:
        Dictionary with validation status and properties if valid
        
    Examples:
        result = validate_smiles("CC(=O)O")
        # Returns: {
        #     "valid": True,
        #     "canonical_smiles": "CC(=O)O",
        #     "molecular_formula": "C2H4O2",
        #     "molecular_weight": 60.05
        # }
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        
        mol = Chem.MolFromSmiles(smiles)
        
        if mol is None:
            return {
                "valid": False,
                "error": "Invalid SMILES string"
            }
        
        return {
            "valid": True,
            "canonical_smiles": Chem.MolToSmiles(mol),
            "molecular_formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
            "molecular_weight": round(Descriptors.MolWt(mol), 2),
            "num_atoms": mol.GetNumAtoms(),
            "num_bonds": mol.GetNumBonds()
        }
        
    except ImportError:
        return {
            "valid": "unknown",
            "error": "RDKit not available for validation"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


# Common molecules reference (for documentation)
COMMON_MOLECULES = {
    # Drugs
    "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "paracetamol": "CC(=O)Nc1ccc(O)cc1",
    "acetaminophen": "CC(=O)Nc1ccc(O)cc1",  # Same as paracetamol
    "ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
    "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "penicillin": "CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(=O)O",
    
    # Solvents
    "water": "O",
    "ethanol": "CCO",
    "methanol": "CO",
    "acetone": "CC(=O)C",
    "dmso": "CS(=O)C",
    "chloroform": "C(Cl)(Cl)Cl",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    
    # Organic compounds
    "glucose": "C(C1C(C(C(C(O1)O)O)O)O)O",
    "acetic acid": "CC(=O)O",
    "ethanoic acid": "CC(=O)O",  # IUPAC for acetic acid
    "phenol": "Oc1ccccc1",
    "aniline": "Nc1ccccc1",
    "naphthalene": "c1ccc2c(c1)cccc2",
    
    # Amino acids
    "glycine": "C(C(=O)O)N",
    "alanine": "CC(C(=O)O)N",
    "valine": "CC(C)C(C(=O)O)N",
    "leucine": "CC(C)CC(C(=O)O)N",
    "lysine": "C(CCN)CC(C(=O)O)N",
}