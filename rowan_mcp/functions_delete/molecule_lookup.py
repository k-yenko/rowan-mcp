from urllib.request import urlopen
from urllib.parse import quote


def CIRconvert(ids):
    """
    Convert molecule name/identifier to SMILES using Chemical Identifier Resolver.
    
    Args:
        ids (str): Molecule name or identifier (e.g., 'Aspirin', '3-Methylheptane', CAS numbers)
    
    Returns:
        str: SMILES string if found, 'Did not work' if failed
    """
    try:
        url = 'http://cactus.nci.nih.gov/chemical/structure/' + quote(ids) + '/smiles'
        ans = urlopen(url).read().decode('utf8')
        return ans
    except:
        return 'Did not work'


def rowan_molecule_lookup(molecule_name: str) -> str:
    """
    Convert a molecule name to SMILES using Chemical Identifier Resolver.
    
    Args:
        molecule_name (str): Name of the molecule (e.g., 'aspirin', 'benzene')
    
    Returns:
        str: SMILES notation, or error message if not found
    """
    smiles = CIRconvert(molecule_name)
    
    if smiles == 'Did not work':
        return f"{molecule_name}: Not found"
    else:
        return smiles.strip()  # Remove any trailing newlines


def batch_convert(identifiers):
    """
    Convert multiple molecule identifiers to SMILES.
    
    Args:
        identifiers (list): List of molecule names/identifiers
    
    Returns:
        dict: Dictionary mapping identifiers to SMILES
    """
    results = {}
    
    for ids in identifiers:
        results[ids] = CIRconvert(ids)
    
    return results 

