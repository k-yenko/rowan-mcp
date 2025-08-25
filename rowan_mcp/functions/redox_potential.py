"""
Rowan redox potential function for electrochemistry.
"""

import os
import logging
import time
from typing import Optional

try:
    import rowan
except ImportError:
    rowan = None

# Setup logging
logger = logging.getLogger(__name__)



def lookup_molecule_smiles(molecule_name: str) -> str:
    """Look up canonical SMILES for common molecule names."""
    # Common molecule SMILES database
    MOLECULE_SMILES = {
        # Aromatics
        "phenol": "Oc1ccccc1",
        "benzene": "c1ccccc1", 
        "toluene": "Cc1ccccc1",
        "aniline": "Nc1ccccc1",
        "benzoic acid": "O=C(O)c1ccccc1",
        "pyridine": "c1ccncc1",
        "furan": "c1ccoc1",
        "thiophene": "c1ccsc1",
        "pyrrole": "c1cc[nH]c1",
        "imidazole": "c1c[nH]cn1",
        "indole": "c1ccc2c(c1)cc[nH]2",
        "quinoline": "c1ccc2ncccc2c1",
        
        # Aliphatics
        "methane": "C",
        "ethane": "CC",
        "propane": "CCC",
        "butane": "CCCC",
        "pentane": "CCCCC",
        "hexane": "CCCCCC",
        "heptane": "CCCCCCC",
        "octane": "CCCCCCCC",
        "nonane": "CCCCCCCCC",
        "decane": "CCCCCCCCCC",
        
        # Alcohols
        "methanol": "CO",
        "ethanol": "CCO",
        "propanol": "CCCO",
        "isopropanol": "CC(C)O",
        "butanol": "CCCCO",
        "isobutanol": "CC(C)CO",
        "tert-butanol": "CC(C)(C)O",
        
        # Simple molecules
        "water": "O",
        "hydrogen peroxide": "OO",
        "ammonia": "N",
        "methyl amine": "CN",
        "ethyl amine": "CCN",
        "formaldehyde": "C=O",
        "acetaldehyde": "CC=O",
        "acetone": "CC(=O)C",
        "formic acid": "C(=O)O",
        "acetic acid": "CC(=O)O",
        "acetamide": "CC(=O)N",
        "dimethyl sulfoxide": "CS(=O)C",
        "hydrogen sulfide": "S",
        "carbon dioxide": "O=C=O",
        "carbon monoxide": "C#O",
        
        # Cyclic compounds
        "cyclopropane": "C1CC1",
        "cyclobutane": "C1CCC1",
        "cyclopentane": "C1CCCC1",
        "cyclohexane": "C1CCCCC1",
        "cycloheptane": "C1CCCCCC1",
        "cyclooctane": "C1CCCCCCC1",
        
        # Ethers
        "diethyl ether": "CCOCC",
        "tetrahydrofuran": "C1CCOC1",
        "dioxane": "C1COCCO1",
        
        # Halogens
        "chloroform": "C(Cl)(Cl)Cl",
        "carbon tetrachloride": "C(Cl)(Cl)(Cl)Cl",
        "methyl chloride": "CCl",
        "dichloromethane": "C(Cl)Cl",
        "fluoromethane": "CF",
        "bromomethane": "CBr",
        "iodomethane": "CI",
        
        # Sugars
        "glucose": "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",
        "fructose": "C([C@H]([C@H]([C@@H]([C@H](CO)O)O)O)O)O",
        "sucrose": "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O[C@]2([C@H]([C@@H]([C@@H](O2)CO)O)O)CO)O)O)O)O",
        
        # Nucleotides
        "adenine": "c1nc(c2c(n1)ncn2)N",
        "guanine": "c1nc2c(n1)c(=O)[nH]c(=n2)N",
        "cytosine": "c1c(nc(=O)[nH]c1=O)N",
        "thymine": "Cc1c[nH]c(=O)[nH]c1=O",
        "uracil": "c1c[nH]c(=O)[nH]c1=O",
        
        # Amino acids
        "glycine": "C(C(=O)O)N",
        "alanine": "C[C@@H](C(=O)O)N",
        "valine": "CC(C)[C@@H](C(=O)O)N",
        "leucine": "CC(C)C[C@@H](C(=O)O)N",
        "isoleucine": "CC[C@H](C)[C@@H](C(=O)O)N",
        "phenylalanine": "c1ccc(cc1)C[C@@H](C(=O)O)N",
        "tyrosine": "c1cc(ccc1C[C@@H](C(=O)O)N)O",
        "tryptophan": "c1ccc2c(c1)c(c[nH]2)C[C@@H](C(=O)O)N",
        "serine": "C([C@@H](C(=O)O)N)O",
        "threonine": "C[C@H]([C@@H](C(=O)O)N)O",
        "asparagine": "C([C@@H](C(=O)O)N)C(=O)N",
        "glutamine": "C(CC(=O)N)[C@@H](C(=O)O)N",
        "aspartic acid": "C([C@@H](C(=O)O)N)C(=O)O",
        "glutamic acid": "C(CC(=O)O)[C@@H](C(=O)O)N",
        "lysine": "C(CCN)C[C@@H](C(=O)O)N",
        "arginine": "C(C[C@@H](C(=O)O)N)CN=C(N)N",
        "histidine": "c1c([nH]cn1)C[C@@H](C(=O)O)N",
        "cysteine": "C([C@@H](C(=O)O)N)S",
        "methionine": "CCSC[C@@H](C(=O)O)N",
        "proline": "C1C[C@H](NC1)C(=O)O",
        
        # Drugs and bioactive molecules
        "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        "caffeine": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
        "nicotine": "CN1CCC[C@H]1c2cccnc2",
        "morphine": "CN1CC[C@]23c4c5ccc(O)c4O[C@H]2[C@@H](O)C=C[C@H]3[C@H]1C5",
        "codeine": "COc1ccc2c3c1O[C@H]1[C@@H](O)C=C[C@H]4[C@@H]1C[C@@](CC3)(C2)N4C",
        "glucose": "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",
        "cholesterol": "C[C@H](CCCC(C)C)[C@H]1CC[C@@H]2[C@@H]1CC[C@H]3[C@@H]2CC=C4[C@@]3(CC[C@@H](C4)O)C",
        "testosterone": "C[C@]12CC[C@H]3[C@H]([C@@H]1CC[C@@H]2O)CCC4=CC(=O)CC[C@]34C",
        "estradiol": "C[C@]12CC[C@H]3[C@H]([C@@H]1CC[C@@H]2O)CCC4=C3C=CC(=C4)O",
        
        # Solvents
        "dichloromethane": "C(Cl)Cl",
        "chloroform": "C(Cl)(Cl)Cl",
        "carbon tetrachloride": "C(Cl)(Cl)(Cl)Cl",
        "acetonitrile": "CC#N",
        "dimethylformamide": "CN(C)C=O",
        "dimethyl sulfoxide": "CS(=O)C",
        "ethyl acetate": "CCOC(=O)C",
        "diethyl ether": "CCOCC",
        "tetrahydrofuran": "C1CCOC1",
        "1,4-dioxane": "C1COCCO1",
        "toluene": "Cc1ccccc1",
        "xylene": "Cc1ccccc1C",
        "mesitylene": "Cc1cc(C)cc(C)c1",
        "hexane": "CCCCCC",
        "heptane": "CCCCCCC",
        "octane": "CCCCCCCC",
        "cyclohexane": "C1CCCCC1",
        "benzene": "c1ccccc1",
        "nitromethane": "C[N+](=O)[O-]",
        "acetone": "CC(=O)C",
        "2-butanone": "CCC(=O)C",
        "2-propanol": "CC(C)O",
        "1-butanol": "CCCCO",
        "2-butanol": "CC(C)CO",
        "tert-butanol": "CC(C)(C)O",
        "ethylene glycol": "OCCO",
        "propylene glycol": "CC(CO)O",
        "glycerol": "C(C(CO)O)O",
    }
    
    # Try exact match first
    name_lower = molecule_name.lower().strip()
    if name_lower in MOLECULE_SMILES:
        return MOLECULE_SMILES[name_lower]
    
    # If not found, return the original input (assume it's already SMILES)
    return molecule_name

def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    
    try:
        start_time = time.time()
        result = rowan.compute(workflow_type=workflow_type, **kwargs)
        api_time = time.time() - start_time
        
        if isinstance(result, dict) and 'uuid' in result:
            job_status = result.get('status', result.get('object_status', 'Unknown'))
            status_names = {0: "Queued", 1: "Running", 2: "Completed", 3: "Failed", 4: "Stopped", 5: "Awaiting Queue"}
            status_text = status_names.get(job_status, f"Unknown ({job_status})")
        
        return result
        
    except Exception as e:
        api_time = time.time() - start_time
        raise e

def rowan_redox_potential(
    name: str,
    molecule: str,
    reduction: bool = True,
    oxidation: bool = True,
    mode: str = "rapid",
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict redox potentials vs. SCE in acetonitrile.
    
    Calculates oxidation and reduction potentials for:
    - Electrochemical reaction design
    - Battery and energy storage applications
    - Understanding electron transfer processes
    
    **Important**: Only acetonitrile solvent is supported by Rowan's redox workflow.
    
    Use this for: Electrochemistry, battery materials, electron transfer studies
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name (e.g., "phenol", "benzene")
        reduction: Whether to calculate reduction potential (default: True)
        oxidation: Whether to calculate oxidation potential (default: True)
        mode: Calculation accuracy mode - "reckless", "rapid", "careful", "meticulous" (default: "rapid")
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Redox potential results vs. SCE in acetonitrile
    """
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Validate mode
    valid_modes = ["reckless", "rapid", "careful", "meticulous"]
    mode_lower = mode.lower()
    if mode_lower not in valid_modes:
        return f" Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
    
    # At least one type must be selected
    if not reduction and not oxidation:
        return f" At least one of 'reduction' or 'oxidation' must be True"
    
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Mode: {mode_lower}")
    logger.info(f"   Reduction: {reduction}")
    logger.info(f"   Oxidation: {oxidation}")
    
    # Build parameters for Rowan API
    redox_params = {
        "name": name,
        "molecule": canonical_smiles,
        "reduction": reduction,
        "oxidation": oxidation,
        "mode": mode_lower,
        "solvent": "acetonitrile",  # Required by Rowan
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    result = log_rowan_api_call(
        workflow_type="redox_potential",
        **redox_params
    )
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f" Redox potential analysis for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f" Redox potential analysis for '{name}' failed!\n\n"
        else:
            formatted = f" Redox potential analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f" Molecule: {molecule}\n"
        formatted += f" SMILES: {canonical_smiles}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {status}\n"
        formatted += f"⚙ Mode: {mode_lower.title()}\n"
        formatted += f"Solvent: Acetonitrile\n"
        
        # Show which potentials were calculated
        calc_types = []
        if reduction:
            calc_types.append("Reduction")
        if oxidation:
            calc_types.append("Oxidation")
        formatted += f" Calculated: {' + '.join(calc_types)} potential(s)\n"
        
        # Try to extract redox potential results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            if reduction and 'reduction_potential' in data and data['reduction_potential'] is not None:
                formatted += f" Reduction Potential: {data['reduction_potential']:.3f} V vs. SCE\n"
            
            if oxidation and 'oxidation_potential' in data and data['oxidation_potential'] is not None:
                formatted += f" Oxidation Potential: {data['oxidation_potential']:.3f} V vs. SCE\n"
            
            # Legacy support for older format
            if 'redox_potential' in data and data['redox_potential'] is not None:
                redox_type = data.get('redox_type', 'unknown')
                formatted += f" {redox_type.title()} Potential: {data['redox_potential']:.3f} V vs. SCE\n"
        
        if status == 2:
            formatted += f"\n **Results Available:**\n"
            formatted += f"• Potentials reported vs. SCE (Saturated Calomel Electrode)\n"
            formatted += f"• Calculated in acetonitrile solvent\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
        
        return formatted
    else:
        formatted = f" Redox potential analysis for '{name}' submitted!\n\n"
        formatted += f" Molecule: {molecule}\n"
        formatted += f" SMILES: {canonical_smiles}\n"
        formatted += f" Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f" Status: {result.get('status', 'Submitted')}\n"
        formatted += f"⚙ Mode: {mode_lower.title()}\n"
        
        calc_types = []
        if reduction:
            calc_types.append("Reduction")
        if oxidation:
            calc_types.append("Oxidation")
        formatted += f" Will calculate: {' + '.join(calc_types)} potential(s)\n"
        
        return formatted

def test_rowan_redox_potential():
    """Test the rowan_redox_potential function."""
    try:
        # Test with a simple molecule (non-blocking to avoid long wait)
        result = rowan_redox_potential("test_redox", "phenol", blocking=False)
        print(" Redox potential test successful!")
        print(f"Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f" Redox potential test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_redox_potential() 