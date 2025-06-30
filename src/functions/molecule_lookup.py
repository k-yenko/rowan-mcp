"""
Rowan molecule lookup function for SMILES string retrieval.
"""

from typing import Optional

def lookup_molecule_smiles(molecule_name: str) -> str:
    """Look up canonical SMILES for common molecule names.
    
    Args:
        molecule_name: Name of the molecule (e.g., "phenol", "benzene", "water")
    
    Returns:
        Canonical SMILES string for the molecule
    """
    # Common molecule SMILES database
    MOLECULE_SMILES = {
        # Aromatics
        "phenol": "Oc1ccccc1",
        "benzene": "c1ccccc1", 
        "toluene": "Cc1ccccc1",
        "aniline": "Nc1ccccc1",
        "benzoic acid": "O=C(O)c1ccccc1",
        "salicylic acid": "O=C(O)c1ccccc1O",
        "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        "pyridine": "c1ccncc1",
        "furan": "c1ccoc1",
        "thiophene": "c1ccsc1",
        "pyrrole": "c1cc[nH]c1",
        "indole": "c1ccc2[nH]ccc2c1",
        "naphthalene": "c1ccc2ccccc2c1",
        
        # Aliphatics
        "methane": "C",
        "ethane": "CC", 
        "propane": "CCC",
        "butane": "CCCC",
        "pentane": "CCCCC",
        "hexane": "CCCCCC",
        "cyclopropane": "C1CC1",
        "cyclobutane": "C1CCC1", 
        "cyclopentane": "C1CCCC1",
        "cyclohexane": "C1CCCCC1",
        
        # Alcohols
        "methanol": "CO",
        "ethanol": "CCO",
        "propanol": "CCCO",
        "isopropanol": "CC(C)O",
        "butanol": "CCCCO",
        
        # Acids
        "acetic acid": "CC(=O)O",
        "formic acid": "C(=O)O",
        "propionic acid": "CCC(=O)O",
        
        # Common drugs
        "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "acetaminophen": "CC(=O)Nc1ccc(O)cc1",
        "paracetamol": "CC(=O)Nc1ccc(O)cc1",
        
        # Solvents
        "water": "O",
        "acetone": "CC(=O)C",
        "dmso": "CS(=O)C",
        "dmf": "CN(C)C=O",
        "thf": "C1CCOC1",
        "dioxane": "C1COCCO1",
        "chloroform": "ClC(Cl)Cl",
        "dichloromethane": "ClCCl",
        
        # Others
        "glucose": "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
        "ethylene": "C=C",
        "acetylene": "C#C",
        "formaldehyde": "C=O",
        "ammonia": "N",
        "hydrogen peroxide": "OO",
        "carbon dioxide": "O=C=O",
    }
    
    # Normalize the input (lowercase, strip whitespace)
    normalized_name = molecule_name.lower().strip()
    
    # Direct lookup
    if normalized_name in MOLECULE_SMILES:
        smiles = MOLECULE_SMILES[normalized_name]
        return smiles
    
    # Try partial matches for common variations
    for name, smiles in MOLECULE_SMILES.items():
        if normalized_name in name or name in normalized_name:
            return smiles
    
    # If no match found, return the original input (assume it's already SMILES)
    return molecule_name

def rowan_molecule_lookup(molecule_name: str) -> str:
    """Look up the canonical SMILES string for common molecule names.
    
    Provides consistent SMILES representations for common molecules to ensure
    reproducible results across different Rowan calculations.
    
    Args:
        molecule_name: Name of the molecule (e.g., "phenol", "benzene", "caffeine")
    
    Returns:
        Canonical SMILES string and molecular information
    """
    canonical_smiles = lookup_molecule_smiles(molecule_name)
    
    # Check if we found a match or returned the input as-is
    if canonical_smiles == molecule_name:
        formatted = f" No SMILES lookup found for '{molecule_name}'\n\n"
        formatted += f" **Using input as-is:** {molecule_name}\n"
        formatted += f" **If this is a molecule name, try:**\n"
        formatted += f"• Check spelling (e.g., 'phenol', 'benzene', 'caffeine')\n"
        formatted += f"• Use rowan_molecule_lookup('') to see available molecules\n"
        formatted += f"• If it's already a SMILES string, you can use it directly\n"
    else:
        formatted = f" SMILES lookup successful!\n\n"
        formatted += f" **Molecule:** {molecule_name}\n"
        formatted += f" **Canonical SMILES:** {canonical_smiles}\n"
        formatted += f" **Usage:** Use '{canonical_smiles}' in Rowan calculations for consistent results\n"
    
    # Show available molecules if empty input
    if not molecule_name.strip():
        formatted = f" **Available Molecules for SMILES Lookup:**\n\n"
        
        categories = {
            "Aromatics": ["phenol", "benzene", "toluene", "aniline", "pyridine", "naphthalene"],
            "Aliphatics": ["methane", "ethane", "propane", "butane", "cyclohexane"],
            "Alcohols": ["methanol", "ethanol", "isopropanol"],
            "Common Drugs": ["caffeine", "ibuprofen", "aspirin", "acetaminophen"],
            "Solvents": ["water", "acetone", "dmso", "thf"],
        }
        
        for category, molecules in categories.items():
            formatted += f"**{category}:**\n"
            for mol in molecules:
                smiles = lookup_molecule_smiles(mol)
                formatted += f"• {mol}: `{smiles}`\n"
            formatted += "\n"
        
        formatted += f" **Example:** rowan_molecule_lookup('phenol') → 'Oc1ccccc1'\n"
    
    return formatted

def test_rowan_molecule_lookup():
    """Test the rowan_molecule_lookup function."""
    try:
        # Test with a known molecule
        result = rowan_molecule_lookup("phenol")
        print(" Molecule lookup test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f" Molecule lookup test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_molecule_lookup() 