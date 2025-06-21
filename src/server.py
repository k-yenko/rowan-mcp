"""
Rowan MCP Server Implementation using FastMCP

This module implements the Model Context Protocol server for Rowan's
computational chemistry platform using the FastMCP framework.
"""

import os
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from stjames import Molecule

try:
    import rowan
except ImportError:
    rowan = None

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if available
except ImportError:
    pass  # dotenv not required, but helpful if available

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rowan_mcp.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP()

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if not api_key:
    logger.error("ROWAN_API_KEY environment variable not found")
    raise ValueError(
        "ROWAN_API_KEY environment variable is required. "
        "Get your API key from https://labs.rowansci.com"
    )
else:
    logger.info(f"✅ ROWAN_API_KEY loaded (length: {len(api_key)})")

if rowan is None:
    logger.error("rowan-python package not found")
    raise ImportError(
        "rowan-python package is required. Install with: pip install rowan-python"
    )
else:
    logger.info("✅ rowan-python package loaded successfully")

rowan.api_key = api_key
logger.info("🔗 Rowan API key configured")


def log_mcp_call(func):
    """Decorator to log MCP tool calls with detailed information."""
    import functools
    
    @functools.wraps(func)
    def wrapper(**kwargs):  # Only use **kwargs to be compatible with FastMCP
        func_name = func.__name__
        start_time = time.time()
        
        # Log the incoming request
        logger.info(f"🔧 MCP Tool Called: {func_name}")
        logger.info(f"📝 Parameters: {kwargs}")
        
        try:
            # Execute the function
            result = func(**kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Log successful completion
            logger.info(f"✅ {func_name} completed successfully in {execution_time:.2f}s")
            logger.debug(f"📤 Response preview: {str(result)[:200]}...")
            
            return result
            
        except Exception as e:
            # Calculate execution time even for errors
            execution_time = time.time() - start_time
            
            # Log the error with full traceback
            logger.error(f"❌ {func_name} failed after {execution_time:.2f}s")
            logger.error(f"🚨 Error: {str(e)}")
            logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
            
            # Extract Rowan's actual error message if available
            rowan_error_msg = None
            http_status = None
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    http_status = getattr(e.response, 'status_code', 'Unknown')
                    
                    if hasattr(e.response, 'text'):
                        response_text = e.response.text
                        # Try to parse JSON error response
                        import json
                        try:
                            error_data = json.loads(response_text)
                            rowan_error_msg = error_data.get('message', error_data.get('error', response_text))
                        except json.JSONDecodeError:
                            rowan_error_msg = response_text
                    elif hasattr(e.response, 'content'):
                        rowan_error_msg = e.response.content.decode('utf-8', errors='ignore')
                except Exception as extract_err:
                    logger.error(f"⚠️ Could not extract error message: {extract_err}")
            
            # Build comprehensive error message for user
            error_parts = []
            
            if rowan_error_msg and rowan_error_msg.strip():
                error_parts.append(f"Rowan API Error: {rowan_error_msg}")
            
            if http_status:
                error_parts.append(f"HTTP Status: {http_status}")
                
            # Add exception details
            error_parts.append(f"Exception: {type(e).__name__}")
            
            # Add original error message if we have one and it's different
            original_msg = str(e)
            if original_msg and original_msg not in (rowan_error_msg or ''):
                error_parts.append(f"Details: {original_msg}")
            
            # Provide specific guidance for common error types
            if isinstance(e, AssertionError):
                error_parts.append("This appears to be a validation error in the Rowan library")
            
            combined_error = " | ".join(error_parts)
            return f"❌ {combined_error}"
            
    return wrapper


def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    logger.info(f"🌐 Rowan API Call: {workflow_type}")
    logger.info(f"🔍 Rowan Parameters: {kwargs}")
    
    # Special handling for long-running calculations
    if workflow_type in ["multistage_opt", "conformer_search"]:
        ping_interval = kwargs.get('ping_interval', 5)
        blocking = kwargs.get('blocking', True)
        if blocking:
            if workflow_type == "multistage_opt":
                logger.info(f"⏳ Multi-stage optimization may take several minutes...")
            else:
                logger.info(f"⏳ Conformer search may take several minutes...")
            logger.info(f"🔄 Progress will be checked every {ping_interval} seconds")
        else:
            logger.info(f"🚀 {workflow_type.replace('_', ' ').title()} submitted without waiting")
    
    try:
        start_time = time.time()
        result = rowan.compute(workflow_type=workflow_type, **kwargs)
        api_time = time.time() - start_time
        
        logger.info(f"🎯 Rowan API submission successful: {workflow_type} ({api_time:.2f}s)")
        if isinstance(result, dict) and 'uuid' in result:
            logger.info(f"📋 Job UUID: {result.get('uuid')}")
            job_status = result.get('status', result.get('object_status', 'Unknown'))
            status_names = {0: "Queued", 1: "Running", 2: "Completed", 3: "Failed", 4: "Stopped", 5: "Awaiting Queue"}
            status_text = status_names.get(job_status, f"Unknown ({job_status})")
            logger.info(f"📊 Job Status: {status_text} ({job_status})")
        
        return result
        
    except Exception as e:
        api_time = time.time() - start_time
        logger.error(f"🌐 Rowan API failed: {workflow_type} ({api_time:.2f}s)")
        logger.error(f"🚨 Rowan Error: {str(e)}")
        
        # Enhanced error logging for better debugging
        logger.error(f"📋 Exception Type: {type(e).__name__}")
        logger.error(f"📄 Full Exception: {repr(e)}")
        logger.error(f"🔍 Exception Args: {e.args}")
        
        # Log full stack trace for debugging
        import traceback
        logger.error(f"📍 Full Stack Trace:\n{traceback.format_exc()}")
        
        # Log the actual response from Rowan API if available
        response_logged = False
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"🌐 HTTP Status: {e.response.status_code}")
            try:
                if hasattr(e.response, 'text'):
                    response_text = e.response.text
                    logger.error(f"📝 Rowan API Response Text: {response_text}")
                    response_logged = True
                elif hasattr(e.response, 'content'):
                    response_content = e.response.content.decode('utf-8', errors='ignore')
                    logger.error(f"📝 Rowan API Response Content: {response_content}")
                    response_logged = True
                
                # Also try to get headers for more context
                if hasattr(e.response, 'headers'):
                    logger.error(f"📋 Response Headers: {dict(e.response.headers)}")
                    
            except Exception as log_err:
                logger.error(f"⚠️ Could not read response: {log_err}")
        
        # For requests exceptions, try to get more details
        if hasattr(e, '__dict__'):
            logger.error(f"🔍 Exception attributes: {list(e.__dict__.keys())}")
            
        # Check if it's a requests exception with specific handling
        if 'requests' in str(type(e).__module__):
            logger.error(f"🌐 This is a requests library exception")
            
        # If we couldn't log a response above, try alternative approaches
        if not response_logged:
            logger.error(f"⚠️ No HTTP response data found in exception")
            
            # Try to get any string representation that might contain useful info
            exception_str = str(e)
            if exception_str and exception_str != '':
                logger.error(f"📝 Exception message: {exception_str}")
            else:
                logger.error(f"📝 Exception has no message")
        
        raise e

# Quantum Chemistry Constants and Helper Functions
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

QC_TASKS = {
    "energy": "Single point energy calculation",
    "optimize": "Geometry optimization",
    "frequencies": "Vibrational frequency analysis",
    "frequency": "Vibrational frequency analysis (alias for frequencies)",
    "forces": "Calculate atomic forces",
    "dipole": "Electric dipole moment",
    "charges": "Atomic partial charges",
    "orbitals": "Molecular orbital analysis",
    "esp": "Electrostatic potential",
    "nbo": "Natural bond orbital analysis"
}

QC_CORRECTIONS = {
    "d3bj": "Grimme's D3 dispersion correction with Becke-Johnson damping",
    "d3": "Grimme's D3 dispersion correction (automatically applied for B97-D3, ωB97X-D3)"
}

def analyze_spin_states(molecule: str) -> Dict[str, Any]:
    """Analyze molecule to predict charge, multiplicity, and appropriate spin states.
    
    Args:
        molecule: Molecular formula or name (e.g., "Mn(Cl)6", "Fe(CN)6", "CuSO4")
    
    Returns:
        Dictionary with predicted charge, multiplicity, and spin states
    """
    import re
    
    analysis = {
        "charge": 0,
        "multiplicity": 1,
        "states": [1],
        "confidence": "low",
        "explanation": "Default singlet state assumed"
    }
    
    # Common transition metal complex patterns
    complex_patterns = {
        # Manganese complexes
        r"Mn\(Cl\)6": {"charge": -4, "oxidation_state": 2, "d_electrons": 5, "states": [2, 6], "explanation": "Mn(II)Cl6^4- - d5, low-spin vs high-spin"},
        r"Mn\(CN\)6": {"charge": -4, "oxidation_state": 2, "d_electrons": 5, "states": [2, 6], "explanation": "Mn(II)(CN)6^4- - d5, strong field ligand favors low-spin"},
        r"Mn\(H2O\)6": {"charge": 2, "oxidation_state": 2, "d_electrons": 5, "states": [6], "explanation": "Mn(II)(H2O)6^2+ - d5, weak field favors high-spin"},
        r"MnO4": {"charge": -1, "oxidation_state": 7, "d_electrons": 0, "states": [1], "explanation": "MnO4^- - d0, diamagnetic"},
        
        # Iron complexes  
        r"Fe\(CN\)6": {"charge": -4, "oxidation_state": 2, "d_electrons": 6, "states": [1, 5], "explanation": "Fe(II)(CN)6^4- - d6, low-spin vs high-spin"},
        r"Fe\(H2O\)6": {"charge": 2, "oxidation_state": 2, "d_electrons": 6, "states": [5], "explanation": "Fe(II)(H2O)6^2+ - d6, weak field favors high-spin"},
        r"FeCl4": {"charge": -1, "oxidation_state": 3, "d_electrons": 5, "states": [6], "explanation": "FeCl4^- - d5, tetrahedral high-spin"},
        
        # Copper complexes
        r"Cu\(H2O\)4": {"charge": 2, "oxidation_state": 2, "d_electrons": 9, "states": [2], "explanation": "Cu(II)(H2O)4^2+ - d9, Jahn-Teller distorted"},
        r"CuCl4": {"charge": -2, "oxidation_state": 2, "d_electrons": 9, "states": [2], "explanation": "CuCl4^2- - d9, always doublet"},
        
        # Chromium complexes
        r"Cr\(H2O\)6": {"charge": 3, "oxidation_state": 3, "d_electrons": 3, "states": [4], "explanation": "Cr(III)(H2O)6^3+ - d3, always high-spin"},
        r"Cr\(CN\)6": {"charge": -3, "oxidation_state": 3, "d_electrons": 3, "states": [4], "explanation": "Cr(III)(CN)6^3- - d3, strong field but still high-spin"},
        
        # Cobalt complexes
        r"Co\(NH3\)6": {"charge": 3, "oxidation_state": 3, "d_electrons": 6, "states": [1], "explanation": "Co(III)(NH3)6^3+ - d6, strong field low-spin"},
        r"Co\(H2O\)6": {"charge": 2, "oxidation_state": 2, "d_electrons": 7, "states": [2, 4], "explanation": "Co(II)(H2O)6^2+ - d7, low-spin vs high-spin"},
        
        # Nickel complexes
        r"Ni\(H2O\)6": {"charge": 2, "oxidation_state": 2, "d_electrons": 8, "states": [3], "explanation": "Ni(II)(H2O)6^2+ - d8, always high-spin triplet"},
        r"Ni\(CN\)4": {"charge": -2, "oxidation_state": 2, "d_electrons": 8, "states": [1], "explanation": "Ni(II)(CN)4^2- - d8, square planar low-spin"},
    }
    
    # Check for transition metal complex patterns
    molecule_clean = molecule.strip()
    for pattern, data in complex_patterns.items():
        if re.search(pattern, molecule_clean, re.IGNORECASE):
            analysis.update({
                "charge": data["charge"],
                "multiplicity": data["states"][0],  # Use first/most likely state as default
                "states": data["states"],
                "confidence": "high",
                "explanation": data["explanation"],
                "oxidation_state": data["oxidation_state"],
                "d_electrons": data["d_electrons"]
            })
            logger.info(f"🔍 Complex Analysis: {molecule} → {data['explanation']}")
            return analysis
    
    # Check for simple metal ions or common patterns
    metal_patterns = {
        r"\bFe2\+": {"charge": 2, "d_electrons": 6, "states": [1, 5], "explanation": "Fe(II) - d6, low-spin vs high-spin"},
        r"\bFe3\+": {"charge": 3, "d_electrons": 5, "states": [2, 6], "explanation": "Fe(III) - d5, low-spin vs high-spin"},
        r"\bMn2\+": {"charge": 2, "d_electrons": 5, "states": [2, 6], "explanation": "Mn(II) - d5, low-spin vs high-spin"},
        r"\bCu2\+": {"charge": 2, "d_electrons": 9, "states": [2], "explanation": "Cu(II) - d9, always doublet"},
        r"\bNi2\+": {"charge": 2, "d_electrons": 8, "states": [1, 3], "explanation": "Ni(II) - d8, depends on ligand field"},
        r"\bCo2\+": {"charge": 2, "d_electrons": 7, "states": [2, 4], "explanation": "Co(II) - d7, low-spin vs high-spin"},
        r"\bCr3\+": {"charge": 3, "d_electrons": 3, "states": [4], "explanation": "Cr(III) - d3, always high-spin"},
    }
    
    for pattern, data in metal_patterns.items():
        if re.search(pattern, molecule_clean, re.IGNORECASE):
            analysis.update({
                "charge": data["charge"],
                "multiplicity": data["states"][0],
                "states": data["states"],
                "confidence": "medium",
                "explanation": data["explanation"],
                "d_electrons": data["d_electrons"]
            })
            logger.info(f"🔍 Metal Ion Analysis: {molecule} → {data['explanation']}")
            return analysis
    
    # Check for organic radicals or common molecules
    radical_patterns = {
        r"^\.CH3$|^CH3\.$": {"states": [2], "explanation": "Methyl radical - doublet"},
        r"^\.OH$|^OH\.$": {"states": [2], "explanation": "Hydroxyl radical - doublet"},
        r"^O2$": {"states": [3], "explanation": "Molecular oxygen - triplet"},
        r"^NO$": {"states": [2], "explanation": "Nitric oxide - doublet"},
        r"carbene": {"states": [1, 3], "explanation": "Carbene - singlet vs triplet"},
        r"biradical": {"states": [1, 3, 5], "explanation": "Biradical - various spin coupling schemes"},
    }
    
    for pattern, data in radical_patterns.items():
        if re.search(pattern, molecule_clean, re.IGNORECASE):
            analysis.update({
                "multiplicity": data["states"][0],
                "states": data["states"],
                "confidence": "medium",
                "explanation": data["explanation"]
            })
            logger.info(f"🔍 Radical Analysis: {molecule} → {data['explanation']}")
            return analysis
    
    # If no patterns match, try to infer from SMILES or molecule name
    if molecule_clean.lower() in ["o2", "oxygen"]:
        analysis.update({
            "multiplicity": 3,
            "states": [1, 3],
            "confidence": "high",
            "explanation": "Molecular oxygen - ground state triplet"
        })
    elif "radical" in molecule_clean.lower():
        analysis.update({
            "multiplicity": 2,
            "states": [2],
            "confidence": "medium",
            "explanation": "Assumed organic radical - doublet"
        })
    
    logger.info(f"🔍 Spin Analysis: {molecule} → {analysis['explanation']} (confidence: {analysis['confidence']})")
    return analysis


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
        logger.info(f"🔍 SMILES Lookup: '{molecule_name}' → '{smiles}'")
        return smiles
    
    # Try partial matches for common variations
    for name, smiles in MOLECULE_SMILES.items():
        if normalized_name in name or name in normalized_name:
            logger.info(f"🔍 SMILES Lookup (partial match): '{molecule_name}' → '{name}' → '{smiles}'")
            return smiles
    
    # If no match found, return the original input (assume it's already SMILES)
    logger.warning(f"⚠️ No SMILES found for '{molecule_name}', using as-is")
    return molecule_name


def get_qc_guidance() -> str:
    """Generate comprehensive quantum chemistry guidance."""
    guidance = "🔬 **Rowan Quantum Chemistry Requirements** 🔬\n\n"
    
    guidance += "**📋 Required Parameters:**\n"
    guidance += "1. **Molecule Identity**: SMILES string (e.g., 'CC(=O)OC1=CC=CC=C1C(=O)O' for aspirin)\n"
    guidance += "2. **Level of Theory**: Method + Basis Set combination\n"
    guidance += "3. **Task**: What property to calculate\n"
    guidance += "4. **Settings**: Optional calculation-specific parameters\n"
    guidance += "5. **Corrections**: Optional post-hoc corrections (e.g., dispersion)\n\n"
    
    guidance += "**⚗️ Available Engines:**\n"
    for engine, description in QC_ENGINES.items():
        guidance += f"• **{engine.upper()}**: {description}\n"
    guidance += "\n"
    
    guidance += "**🧮 Methods by Category:**\n"
    guidance += "**Hartree-Fock:**\n"
    guidance += f"• **HF**: {QC_METHODS['hf']}\n\n"
    
    guidance += "**Pure Functionals (LDA/GGA/Meta-GGA):**\n"
    pure_methods = ["lsda", "pbe", "blyp", "bp86", "b97-d3", "r2scan", "tpss", "m06l"]
    for method in pure_methods:
        guidance += f"• **{method.upper()}**: {QC_METHODS[method]}\n"
    guidance += "\n"
    
    guidance += "**Hybrid Functionals:**\n"
    hybrid_methods = ["pbe0", "b3lyp", "b3pw91", "camb3lyp", "wb97x_d3", "wb97x_v", "wb97m_v"]
    for method in hybrid_methods:
        guidance += f"• **{method.upper()}**: {QC_METHODS[method]}\n"
    guidance += "\n"
    
    guidance += "**📐 Basis Sets by Type:**\n"
    guidance += "**Recommended for DFT (Jensen pcseg):**\n"
    guidance += f"• **pcseg-1**: {QC_BASIS_SETS['pcseg-1']}\n"
    guidance += f"• **pcseg-2**: {QC_BASIS_SETS['pcseg-2']}\n\n"
    
    guidance += "**Popular Pople Basis Sets:**\n"
    guidance += f"• **6-31G***: {QC_BASIS_SETS['6-31g*']}\n"
    guidance += f"• **6-31G(d,p)**: {QC_BASIS_SETS['6-31g(d,p)']}\n\n"
    
    guidance += "**Efficient Options:**\n"
    guidance += f"• **cc-pVDZ(seg-opt)**: {QC_BASIS_SETS['cc-pvdz(seg-opt)']}\n"
    guidance += f"• **MIDI!**: {QC_BASIS_SETS['midi!']}\n\n"
    
    guidance += "**🎯 Available Tasks:**\n"
    for task, description in QC_TASKS.items():
        guidance += f"• **{task}**: {description}\n"
    guidance += "\n"
    
    guidance += "**🔧 Available Corrections:**\n"
    for correction, description in QC_CORRECTIONS.items():
        guidance += f"• **{correction}**: {description}\n"
    guidance += "\n"
    
    guidance += "**💡 Rowan Guidance:**\n"
    guidance += "• **Smart defaults**: `rowan_quantum_chemistry()` uses B3LYP/pcseg-1 + D3BJ\n"
    guidance += "• **For geometry optimization**: Use `rowan_multistage_opt`\n"
    guidance += "• **For general QC**: Use `rowan_quantum_chemistry` (auto-defaults or custom settings)\n"
    guidance += "• **Best DFT functional**: ωB97M-V (most accurate non-double hybrid)\n"
    guidance += "• **Best pure functional**: B97-D3 (according to Grimme 2011 benchmark)\n"
    guidance += "• **Best basis for DFT**: pcseg-1 (better than 6-31G(d) at same cost)\n"
    guidance += "• **For speed**: Use MIDI! basis set or minimal basis sets\n"
    guidance += "• **For dispersion**: Use D3BJ correction with most functionals\n"
    guidance += "• **Avoid**: Generally contracted basis sets (slow), excessive augmentation\n\n"
    
    guidance += "**⚠️ Important Notes:**\n"
    guidance += "• Rowan uses spherical/pure basis functions (5d, 7f, etc.)\n"
    guidance += "• No effective core potentials (ECPs) currently supported\n"
    guidance += "• Some functionals have built-in dispersion (B97-D3, ωB97X-D3)\n"
    guidance += "• Augmentation should be avoided unless absolutely necessary\n\n"
    
    guidance += "**🔗 Example SMILES:**\n"
    guidance += "• Aspirin: `CC(=O)OC1=CC=CC=C1C(=O)O`\n"
    guidance += "• Water: `O`\n"
    guidance += "• Methane: `C`\n"
    guidance += "• Benzene: `c1ccccc1`\n"
    
    return guidance

# Tool implementations

# Quantum Chemistry Guidance Tool
@mcp.tool()
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
        formatted = f"⚠️ No SMILES lookup found for '{molecule_name}'\n\n"
        formatted += f"📝 **Using input as-is:** {molecule_name}\n"
        formatted += f"💡 **If this is a molecule name, try:**\n"
        formatted += f"• Check spelling (e.g., 'phenol', 'benzene', 'caffeine')\n"
        formatted += f"• Use rowan_molecule_lookup('') to see available molecules\n"
        formatted += f"• If it's already a SMILES string, you can use it directly\n"
    else:
        formatted = f"✅ SMILES lookup successful!\n\n"
        formatted += f"🧪 **Molecule:** {molecule_name}\n"
        formatted += f"🔬 **Canonical SMILES:** {canonical_smiles}\n"
        formatted += f"💡 **Usage:** Use '{canonical_smiles}' in Rowan calculations for consistent results\n"
    
    # Show available molecules if empty input
    if not molecule_name.strip():
        formatted = f"📚 **Available Molecules for SMILES Lookup:**\n\n"
        
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
        
        formatted += f"💡 **Example:** rowan_molecule_lookup('phenol') → 'Oc1ccccc1'\n"
    
    return formatted


# @mcp.tool()
# def rowan_qc_guide() -> str:
#     """Get comprehensive guidance for quantum chemistry calculations in Rowan.
#     
#     Provides detailed information about:
#     - Required parameters for QC calculations
#     - Available engines (Psi4, TeraChem, PySCF, xTB, AIMNet2)
#     - Common methods and basis sets
#     - Available tasks and properties
#     - Best practices and recommendations
#     
#     Use this for: Understanding Rowan's quantum chemistry capabilities
#     
#     Returns:
#         Comprehensive quantum chemistry guidance
#     """
#     guidance = get_qc_guidance()
#     return guidance

# Unified Quantum Chemistry Tool - COMMENTED OUT FOR NOW
# @mcp.tool()
# @log_mcp_call
# def rowan_quantum_chemistry(
#     name: str,
#     molecule: str,
#     method: Optional[str] = None,
#     basis_set: Optional[str] = None,
#     tasks: Optional[List[str]] = None,
#     corrections: Optional[List[str]] = None,
#     engine: Optional[str] = None,
#     charge: int = 0,
#     multiplicity: int = 1,
#     folder_uuid: Optional[str] = None,
#     blocking: bool = True,
#     ping_interval: int = 5,
#     use_recommended_defaults: bool = True,
#     additional_settings: Optional[Dict[str, Any]] = None
# ) -> str:
#     """Run quantum chemistry calculations with intelligent defaults or custom settings.
#     
#     **🔬 Smart Defaults**: When no parameters are specified, uses Rowan's settings:
#     - Method: B3LYP (popular, reliable hybrid functional)
#     - Basis Set: pcseg-1 (better than 6-31G(d) at same cost)
#     - Tasks: ["energy", "optimize"] (energy + geometry optimization)
#     - Corrections: ["d3bj"] (dispersion correction for better accuracy)
#     
#     **⚗️ Full Customization**: All parameters can be overridden for advanced users
#     
#     **Available Methods (16 total):**
#     - HF: Hartree-Fock (unrestricted for open-shell)
#     - Pure DFT: LSDA, PBE, BLYP, BP86, B97-D3, r2SCAN, TPSS, M06-L
#     - Hybrid DFT: PBE0, B3LYP, B3PW91, CAM-B3LYP, ωB97X-D3, ωB97X-V, ωB97M-V
#     
#     **Available Basis Sets (29 total):**
#     - Recommended: pcseg-1 (DFT), pcseg-2 (high accuracy)
#     - Popular: 6-31G*, 6-31G(d,p), cc-pVDZ(seg-opt)
#     - Fast: MIDI!, STO-3G
#     
#     **Available Corrections:**
#     - D3BJ: Grimme's D3 dispersion with Becke-Johnson damping
#     
#     Use this for: All quantum chemistry calculations (beginners get good defaults, experts get full control)
#     
#     Args:
#         name: Name for the calculation
#         molecule: Molecule SMILES string (e.g., 'CC(=O)OC1=CC=CC=C1C(=O)O' for aspirin)
#         method: QC method - if None, uses 'b3lyp' (recommended default)
#         basis_set: Basis set - if None, uses 'pcseg-1' (recommended default)
#         tasks: List of tasks - if None, uses ['energy', 'optimize'] (recommended default)
#         corrections: List of corrections - if None, uses ['d3bj'] (recommended default)
#         engine: Computational engine - if None, defaults to 'psi4' (required by Rowan API)
#         charge: Molecular charge (default: 0)
#         multiplicity: Spin multiplicity (default: 1 for singlet)
#         folder_uuid: Optional folder UUID for organization
#         blocking: Whether to wait for completion (default: True)
#         ping_interval: Check status interval in seconds (default: 5)
#         use_recommended_defaults: If True, uses smart defaults when parameters are None
#         additional_settings: Extra calculation-specific settings
#     
#     Returns:
#         Quantum chemistry calculation results
#     """
#     
#     # Always provide quantum chemistry guidance context first
#     guidance_context = rowan_qc_guide()
#     
#     # Determine if we're using defaults or custom settings
#     using_defaults = (method is None and basis_set is None and 
#                      tasks is None and corrections is None)
#     
#     # Apply intelligent defaults when no parameters specified
#     if use_recommended_defaults and using_defaults:
#         method = "b3lyp"  # Popular, reliable hybrid functional
#         basis_set = "pcseg-1"  # Better than 6-31G(d) at same cost
#         tasks = ["energy", "optimize"]  # Energy + geometry optimization
#         corrections = ["d3bj"]  # Dispersion correction for accuracy
#         if engine is None:  # Only set default if not provided
#             engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#         default_msg = "Rowan's defaults"
#     elif using_defaults:
#         # Fall back to Rowan's system defaults but ensure engine is set
#         if engine is None:  # Only set default if not provided
#             engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#         default_msg = "Rowan's system defaults (HF/STO-3G)"
#     else:
#         # For custom settings, still ensure engine is set if not provided
#         if engine is None:  # Only set default if not provided
#             engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#         default_msg = "Custom user settings"
#     
#     # Validate inputs and provide guidance
#     if method and method.lower() not in QC_METHODS:
#         available_methods = ", ".join(QC_METHODS.keys())
#         return f"❌ Invalid method '{method}'. Available methods: {available_methods}"
#     
#     if basis_set and basis_set.lower() not in QC_BASIS_SETS:
#         available_basis = ", ".join(QC_BASIS_SETS.keys())
#         return f"❌ Invalid basis set '{basis_set}'. Available basis sets: {available_basis}"
#     
#     if tasks:
#         invalid_tasks = [task for task in tasks if task.lower() not in QC_TASKS]
#         if invalid_tasks:
#             available_tasks = ", ".join(QC_TASKS.keys())
#             return f"❌ Invalid tasks {invalid_tasks}. Available tasks: {available_tasks}"
#     
#     if engine and engine.lower() not in QC_ENGINES:
#         available_engines = ", ".join(QC_ENGINES.keys())
#         return f"❌ Invalid engine '{engine}'. Available engines: {available_engines}"
#     
#     if corrections:
#         invalid_corrections = [corr for corr in corrections if corr.lower() not in QC_CORRECTIONS]
#         if invalid_corrections:
#             available_corrections = ", ".join(QC_CORRECTIONS.keys())
#             return f"❌ Invalid corrections {invalid_corrections}. Available corrections: {available_corrections}"
#     
#     # Engine is always required, so ensure it's set
#     if engine is None:
#         engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
#     
#     # Log the QC parameters
#     logger.info(f"🔬 Quantum Chemistry Calculation: {name}")
#     logger.info(f"⚙️ Using: {default_msg}")
#     logger.info(f"⚗️ Method: {method or 'system default'}")
#     logger.info(f"📐 Basis Set: {basis_set or 'system default'}")
#     logger.info(f"🎯 Tasks: {tasks or 'system default'}")
#     logger.info(f"🔧 Corrections: {corrections or 'none'}")
#     logger.info(f"🖥️ Engine: {engine or 'auto-selected'}")
#     logger.info(f"⚡ Charge: {charge}, Multiplicity: {multiplicity}")
#     
#     try:
#         # Build parameters for rowan.compute call based on documentation
#         compute_params = {
#             "name": name,
#             "input_mol": molecule,  # Use input_mol as shown in docs
#             "folder_uuid": folder_uuid,
#             "blocking": blocking,
#             "ping_interval": ping_interval
#         }
#         
#         # Add QC parameters directly (not in settings object)
#         if method:
#             compute_params["method"] = method.lower()
#         if basis_set:
#             compute_params["basis_set"] = basis_set.lower()
#         if tasks:
#             compute_params["tasks"] = [task.lower() for task in tasks]
#         if corrections:
#             compute_params["corrections"] = [corr.lower() for corr in corrections]
#         if engine:
#             compute_params["engine"] = engine.lower()
#         if charge != 0:
#             compute_params["charge"] = charge
#         if multiplicity != 1:
#             compute_params["multiplicity"] = multiplicity
#         
#         # Add any additional settings
#         if additional_settings:
#             compute_params.update(additional_settings)
#         
#         # Use "calculation" workflow type as shown in documentation
#         result = log_rowan_api_call(
#             workflow_type="calculation",
#             **compute_params
#         )
#         
#         # Check actual job status and format accordingly
#         # First try to get status from submission response, then check via API if needed
#         job_status = result.get('status', result.get('object_status', None))
#         
#         # If status is None (common after submission), try to check via API
#         if job_status is None and result.get('uuid'):
#             try:
#                 job_status = rowan.Workflow.status(uuid=result.get('uuid'))
#                 logger.info(f"📊 Retrieved status via API: {job_status}")
#             except Exception as e:
#                 logger.warning(f"⚠️ Could not retrieve status via API: {e}")
#                 job_status = None
#         
#         status_names = {
#             0: ("⏳", "Queued"),
#             1: ("🔄", "Running"), 
#             2: ("✅", "Completed Successfully"),
#             3: ("❌", "Failed"),
#             4: ("⏹️", "Stopped"),
#             5: ("⏸️", "Awaiting Queue")
#         }
#         
#         status_icon, status_text = status_names.get(job_status, ("❓", f"Unknown ({job_status})"))
#         
#         # Special handling for None status (very common case)
#         if job_status is None:
#             status_icon, status_text = ("📝", "Submitted (status pending)")
#             logger.info(f"📝 Workflow submitted, status will be available shortly")
#         
#         # Use appropriate header based on actual status
#         if job_status == 2:
#             formatted = f"✅ Quantum chemistry calculation '{name}' completed successfully!\n\n"
#         elif job_status == 3:
#             formatted = f"❌ Quantum chemistry calculation '{name}' failed!\n\n"
#         elif job_status in [0, 1, 5]:
#             formatted = f"🔄 Quantum chemistry calculation '{name}' submitted!\n\n"
#         elif job_status == 4:
#             formatted = f"⏹️ Quantum chemistry calculation '{name}' was stopped!\n\n"
#         else:
#             formatted = f"📊 Quantum chemistry calculation '{name}' status unknown!\n\n"
#             
#         formatted += f"🧪 Molecule: {molecule}\n"
#         formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
#         formatted += f"📊 Status: {status_icon} {status_text} ({job_status})\n"
#         formatted += f"⚙️ Used: {default_msg}\n"
#         
#         # Show applied settings
#         if method or basis_set or tasks or corrections or engine or charge != 0 or multiplicity != 1:
#             formatted += f"\n⚙️ **Applied Settings:**\n"
#             if method:
#                 formatted += f"   Method: {method.upper()} - {QC_METHODS.get(method.lower(), 'Custom method')}\n"
#             if basis_set:
#                 formatted += f"   Basis Set: {basis_set} - {QC_BASIS_SETS.get(basis_set.lower(), 'Custom basis')}\n"
#             if tasks:
#                 formatted += f"   Tasks: {', '.join(tasks)}\n"
#             if corrections:
#                 formatted += f"   Corrections: {', '.join(corrections)} - "
#                 formatted += ", ".join([QC_CORRECTIONS.get(corr.lower(), 'Custom correction') for corr in corrections]) + "\n"
#             if engine:
#                 formatted += f"   Engine: {engine.upper()} - {QC_ENGINES.get(engine.lower(), 'Custom engine')}\n"
#             if charge != 0 or multiplicity != 1:
#                 formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
#         
#         # Add status-appropriate guidance
#         formatted += f"\n💡 **Next Steps:**\n"
#         if job_status == 2:  # Completed successfully
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to get detailed results\n"
#             formatted += f"• Results should include energies, geometries, and other calculated properties\n"
#         elif job_status == 3:  # Failed
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to see error details\n"
#             formatted += f"• **Troubleshooting tips:**\n"
#             formatted += f"  - Try simpler settings: method='hf', basis_set='sto-3g'\n"
#             formatted += f"  - Use `rowan_multistage_opt()` for geometry optimization (more robust)\n"
#             formatted += f"  - Check if SMILES string is valid\n"
#             formatted += f"  - For difficult molecules, try method='xtb' (semiempirical)\n"
#         elif job_status in [0, 1, 5]:  # Queued/Running/Awaiting
#             formatted += f"• Check status: `rowan_workflow_status('{result.get('uuid', 'UUID')}')`\n"
#             formatted += f"• Wait for completion, then retrieve results\n"
#             formatted += f"• Calculation may take several minutes depending on molecule size\n"
#         elif job_status == 4:  # Stopped
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to see why it was stopped\n"
#             formatted += f"• You can restart with the same or different parameters\n"
#         else:  # Unknown status
#             formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to get more information\n"
#             formatted += f"• Check `rowan_workflow_status('{result.get('uuid', 'UUID')}')` for current status\n"
#             
#         # Add general guidance for successful submissions or unknown states
#         if job_status != 3:  # Don't show alternatives if it failed
#             if using_defaults and use_recommended_defaults:
#                 formatted += f"• **For future calculations:** Try different methods/basis sets for different accuracy/speed trade-offs\n"
#         
#         # Prepend guidance context to the result
#         final_result = f"{guidance_context}\n\n" + "="*80 + "\n\n" + formatted
#         return final_result
#         
#     except Exception as e:
#         error_msg = f"❌ Quantum chemistry calculation submission failed: {str(e)}\n\n"
#         error_msg += "🔧 **This is a submission error, not a calculation failure.**\n"
#         error_msg += "The job never started due to invalid parameters or API issues.\n\n"
#         if "method" in str(e).lower() or "basis" in str(e).lower():
#             error_msg += "💡 **Parameter Error**: Try using recommended defaults by calling with just name and molecule\n"
#             error_msg += "Or check parameter spelling and availability\n\n"
#         elif "engine" in str(e).lower():
#             error_msg += "💡 **Engine Error**: The engine parameter is required. This should be auto-set to 'psi4'\n\n"
#         
#         # Prepend guidance context even in error cases
#         final_error_result = f"{guidance_context}\n\n" + "="*80 + "\n\n" + error_msg
#         return final_error_result

# ADMET - Drug Discovery Properties
@mcp.tool()
@log_mcp_call
def rowan_admet(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict ADME-Tox properties for drug discovery.
    
    ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) properties are crucial
    for drug development. This workflow predicts drug-like properties including:
    - Bioavailability and permeability
    - Metabolic stability and clearance
    - Toxicity indicators and safety profiles
    - Drug-likeness metrics
    
    Use this for: Drug discovery, pharmaceutical development, toxicity screening
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        ADMET prediction results
    """
    result = log_rowan_api_call(
        workflow_type="admet",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)





# Bond Dissociation Energy
@mcp.tool()
@log_mcp_call
def rowan_bde(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate bond dissociation energies.
    
    Predicts the energy required to break specific bonds in molecules. Useful for:
    - Understanding metabolic pathways and degradation
    - Predicting reaction selectivity
    - Identifying weak bonds for synthetic planning
    
    Use this for: Metabolism prediction, synthetic planning, reaction mechanism studies
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Bond dissociation energy results
    """
    # Basic SMILES formatting (no validation - let Rowan handle that)
    logger.info(f"🔬 BDE Calculation Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input molecule: {molecule}")
    logger.info(f"   Input type: {type(molecule)}")
    
    # Just ensure it's a clean string - no validation
    molecule_to_use = str(molecule).strip()
    
    logger.info(f"   🚀 Sending to Rowan API: '{molecule_to_use}'")
    
    result = log_rowan_api_call(
        workflow_type="bde",
        name=name,
        molecule=molecule_to_use,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Multistage Optimization - Recommended for Geometry Optimization
@mcp.tool()
@log_mcp_call
def rowan_multistage_opt(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 30
) -> str:
    """Run multi-level geometry optimization.
    
    Performs hierarchical optimization using multiple levels of theory:
    GFN2-xTB → AIMNet2 → DFT for optimal balance of speed and accuracy.
    
    This is a method for geometry optimization as it provides:
    - High accuracy final structures
    - Efficient computational cost
    - Reliable convergence
    
    Use this for: Geometry optimization, conformational analysis, structure refinement
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 30, longer for multi-stage)
    
    Returns:
        Optimized geometry and energy results
    """
    logger.info(f"🚀 Starting multistage optimization: {name}")
    logger.info(f"⏱️  Using ping_interval: {ping_interval}s (longer for multi-stage calculation)")
    
    result = log_rowan_api_call(
        workflow_type="multistage_opt",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Electronic Properties - HOMO/LUMO, Orbitals
@mcp.tool()
def rowan_electronic_properties(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate electronic structure properties.
    
    Computes electronic properties including:
    - HOMO/LUMO energies and orbitals
    - Molecular orbital analysis
    - Electronic density distributions
    - Band gaps and frontier orbital properties
    
    Use this for: Electronic structure analysis, orbital visualization, reactivity prediction
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Electronic properties results
    """
    # Electronic properties workflow might need basic QC settings
    # Try with minimal required parameters based on error analysis
    result = log_rowan_api_call(
        workflow_type="electronic_properties",
        name=name,
        molecule=Molecule.from_smiles(molecule),
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval,
        # Add minimal QC settings that the workflow expects
        method="b3lyp",  # Common default method
        basis_set="sto-3g",  # Minimal basis set to start
        tasks=["energy", "orbitals"]  # Needed for electronic properties
    )
    return str(result)


# Descriptors - Molecular Feature Vectors
@mcp.tool()
def rowan_descriptors(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate molecular descriptors for data science.
    
    Generates comprehensive molecular descriptors including:
    - Topological and geometric descriptors
    - Electronic and physicochemical properties
    - Graph-based molecular features
    - Machine learning ready feature vectors
    
    Use this for: QSAR modeling, machine learning, chemical space analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Molecular descriptors results
    """
    result = log_rowan_api_call(
        workflow_type="descriptors",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Solubility Prediction
@mcp.tool()
@log_mcp_call
def rowan_solubility(
    name: str,
    molecule: str,
    solvents: Optional[List[str]] = None,
    temperatures: Optional[List[float]] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict solubility in various solvents and temperatures using Rowan's SolubilityWorkflow.
    
    Implements the SolubilityWorkflow class for predicting molecular solubility across
    multiple solvents and temperature ranges. Critical for:
    - Drug formulation and bioavailability optimization
    - Environmental fate and transport modeling
    - Process chemistry and purification design
    - Crystallization and precipitation studies
    
    **🌡️ Temperature Control (SolubilityWorkflow.temperatures):**
    - Default: 0-150°C range [273.15, 298.15, 323.15, 348.15, 373.15, 398.15, 423.15] K
    - Custom: Specify any temperatures in Kelvin as list[float]
    - Results: log(S) solubility values with uncertainties for each temperature
    
    **🧪 Solvent Support (SolubilityWorkflow.solvents):**
    - Water (default): "O" SMILES for aqueous solubility
    - Organic solvents: Any valid SMILES strings (e.g., "CCO" for ethanol)
    - Multiple solvents: Comparative solubility analysis across solvents
    
    **📊 Output Format (SolubilityResult):**
    - solubilities: log(S) values in mol/L units (list[float])
    - uncertainties: Prediction confidence intervals (list[float])
    - Temperature dependence: Results for each temperature point
    - Per-solvent results: dict[solvent_smiles, SolubilityResult]
    
    **🔬 SolubilityWorkflow Parameters:**
    - initial_smiles: Target molecule SMILES string
    - solvents: List of solvent SMILES strings
    - temperatures: Temperature points in Kelvin (default 0-150°C)
    
    Use this for: Drug development, environmental assessment, process optimization,
    crystallization studies, solvent selection
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name (converted to initial_smiles)
        solvents: List of solvent SMILES strings (default: ["O"] for water)
        temperatures: Temperatures in Kelvin (default: 0-150°C range as per SolubilityWorkflow)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Comprehensive solubility prediction results following SolubilityWorkflow output format
    """
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Handle solvents parameter - fix string to list conversion issue
    if solvents is None:
        solvents = ["O"]  # Water SMILES
    elif isinstance(solvents, str):
        # Handle common solvent names
        if solvents.lower() in ["water", "h2o"]:
            solvents = ["O"]  # Water SMILES
        else:
            # Assume it's a SMILES string for a custom solvent
            solvents = [solvents]
    
    # Set default temperature range (0-150°C) if not provided
    if temperatures is None:
        temperatures = [273.15, 298.15, 323.15, 348.15, 373.15, 398.15, 423.15]  # 0-150°C
    elif isinstance(temperatures, (int, float, str)):
        # Handle single temperature value
        try:
            temp_val = float(temperatures)
            temperatures = [temp_val]
        except (ValueError, TypeError):
            return f"❌ Invalid temperature value: {temperatures}"
    
    # Validate temperatures
    if not temperatures or len(temperatures) == 0:
        return "❌ At least one temperature must be specified"
    
    # Convert all temperatures to float and validate
    validated_temps = []
    for temp in temperatures:
        try:
            temp_val = float(temp)
            if temp_val <= 0:
                return f"❌ Temperature must be positive (got {temp_val} K)"
            if temp_val < 200 or temp_val > 500:
                return f"⚠️ Temperature {temp_val} K is outside typical range (200-500 K)"
            validated_temps.append(temp_val)
        except (ValueError, TypeError):
            return f"❌ Invalid temperature value: {temp} (must be numeric)"
    
    temperatures = validated_temps
    
    # Validate solvents
    if not solvents or len(solvents) == 0:
        return "❌ At least one solvent must be specified"
    
    # Basic validation for solvent SMILES strings
    for i, solvent in enumerate(solvents):
        if not isinstance(solvent, str) or len(solvent.strip()) == 0:
            return f"❌ Solvent {i+1} must be a non-empty string (SMILES format)"
        # Check for obviously invalid SMILES characters (basic check)
        if any(char in solvent for char in [' ', '\t', '\n']):
            return f"❌ Solvent {i+1} contains invalid whitespace characters: '{solvent}'"
    
    logger.info(f"🧪 Solubility Analysis Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Using SMILES: {canonical_smiles}")
    logger.info(f"   Solvents: {solvents}")
    logger.info(f"   Temperatures: {temperatures} K")
    logger.info(f"   Temperature range: {min(temperatures):.1f}-{max(temperatures):.1f} K")
    
    # Build parameters for Rowan API following SolubilityWorkflow specification
    solubility_params = {
        "name": name,
        "molecule": canonical_smiles,  # Required by compute() function interface
        "initial_smiles": canonical_smiles,  # Required by SolubilityWorkflow class
        "solvents": solvents,  # List of solvent SMILES strings
        "temperatures": temperatures,  # Temperatures in Kelvin
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    try:
        result = log_rowan_api_call(
            workflow_type="solubility",
            **solubility_params
        )
    except Exception as e:
        # Handle all errors gracefully with detailed reporting
        error_msg = str(e)
        error_type = type(e).__name__
        
        formatted = f"❌ Solubility analysis for '{name}' failed!\n\n"
        formatted += f"🚨 Error Type: {error_type}\n"
        formatted += f"🚨 Error Details: {error_msg}\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"🧪 Solvents: {solvents}\n"
        formatted += f"🌡️ Temperatures: {temperatures} K\n\n"
        
        # Provide specific guidance based on error type
        if "typeerror" in error_msg.lower() or error_type == "TypeError":
            formatted += f"🔧 **TypeError Detected:**\n"
            formatted += f"• This usually indicates a parameter type mismatch\n"
            formatted += f"• Check that temperatures are numeric (not strings)\n"
            formatted += f"• Verify solvents are provided as a list of strings\n"
        elif "validation error" in error_msg.lower():
            formatted += f"🔧 **Validation Error:**\n"
            formatted += f"• Invalid SMILES string format\n"
            formatted += f"• Incorrect parameter types\n"
            formatted += f"• Missing required parameters\n"
        else:
            formatted += f"🔧 **General Troubleshooting:**\n"
            formatted += f"• Check molecule SMILES format\n"
            formatted += f"• Verify parameter types and values\n"
            formatted += f"• Ensure all required fields are provided\n"
        
        return formatted
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        # Check for explicit failure indicators
        has_failed = False
        failure_reason = None
        
        if status == 3:  # Explicit failure status
            has_failed = True
        elif status is None or status == 'Unknown':
            # Check for validation errors or other failure indicators
            if isinstance(result, dict):
                error_msg = result.get('error', result.get('message', ''))
                if error_msg and ('validation error' in str(error_msg).lower() or 'failed' in str(error_msg).lower()):
                    has_failed = True
                    failure_reason = str(error_msg)
        
        if has_failed:
            formatted = f"❌ Solubility analysis for '{name}' failed!\n\n"
            if failure_reason:
                formatted += f"🚨 Error: {failure_reason}\n\n"
        elif status == 2:  # Completed successfully
            formatted = f"✅ Solubility analysis for '{name}' completed successfully!\n\n"
        else:
            formatted = f"⚠️ Solubility analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status}\n"
        
        # Format solvent information
        solvent_names = []
        for solvent in solvents:
            if solvent == "O":
                solvent_names.append("Water")
            else:
                solvent_names.append(f"Custom ({solvent})")
        formatted += f"🧪 Solvents: {', '.join(solvent_names)}\n"
        
        # Format temperature information
        temp_celsius = [f"{t-273.15:.1f}°C" for t in temperatures]
        formatted += f"🌡️ Temperatures: {', '.join(temp_celsius)}\n"
        formatted += f"📏 Temperature Range: {min(temperatures)-273.15:.1f}-{max(temperatures)-273.15:.1f}°C\n"
        
        # Try to extract solubility results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            if 'solubilities' in data and data['solubilities']:
                formatted += f"\n🎯 **Solubility Results:**\n"
                
                for solvent, solub_data in data['solubilities'].items():
                    solvent_name = "Water" if solvent == "O" else f"Solvent ({solvent})"
                    formatted += f"\n💧 **{solvent_name}:**\n"
                    
                    if 'solubilities' in solub_data and 'uncertainties' in solub_data:
                        solubilities = solub_data['solubilities']
                        uncertainties = solub_data['uncertainties']
                        
                        for i, (temp, sol, unc) in enumerate(zip(temperatures, solubilities, uncertainties)):
                            temp_c = temp - 273.15
                            formatted += f"  • {temp_c:.1f}°C: log(S) = {sol:.3f} ± {unc:.3f} L\n"
                        
                        # Show solubility interpretation
                        avg_sol = sum(solubilities) / len(solubilities)
                        if avg_sol > -2:
                            interp = "Highly soluble"
                        elif avg_sol > -4:
                            interp = "Moderately soluble"
                        elif avg_sol > -6:
                            interp = "Poorly soluble"
                        else:
                            interp = "Very poorly soluble"
                        formatted += f"  📊 Average: {avg_sol:.3f} log(S) ({interp})\n"
        
        if has_failed:
            formatted += f"\n🔧 **Troubleshooting:**\n"
            formatted += f"• Check that molecule SMILES is valid\n"
            formatted += f"• Verify solvent specifications (use 'water' or SMILES)\n"
            formatted += f"• Ensure temperature range is reasonable (200-500 K)\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed error logs\n"
        elif status == 2:
            formatted += f"\n🎯 **Analysis Complete:**\n"
            formatted += f"• Solubilities in log(S) units (mol/L)\n"
            formatted += f"• Higher values = more soluble\n"
            formatted += f"• Uncertainties indicate prediction confidence\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
        
        return formatted
    else:
        formatted = f"🚀 Solubility analysis for '{name}' submitted!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Submitted')}\n"
        
        solvent_names = []
        for solvent in solvents:
            if solvent == "O":
                solvent_names.append("Water")
            else:
                solvent_names.append(f"Custom ({solvent})")
        formatted += f"🧪 Solvents: {', '.join(solvent_names)}\n"
        
        temp_celsius = [f"{t-273.15:.1f}°C" for t in temperatures]
        formatted += f"🌡️ Temperatures: {', '.join(temp_celsius)}\n"
        
        return formatted


# Redox Potential
@mcp.tool()
@log_mcp_call
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
        return f"❌ Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
    
    # At least one type must be selected
    if not reduction and not oxidation:
        return f"❌ At least one of 'reduction' or 'oxidation' must be True"
    
    logger.info(f"🔬 Redox Potential Analysis Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Using SMILES: {canonical_smiles}")
    logger.info(f"   Mode: {mode_lower}")
    logger.info(f"   Reduction: {reduction}")
    logger.info(f"   Oxidation: {oxidation}")
    logger.info(f"   Solvent: acetonitrile (required)")
    
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
            formatted = f"✅ Redox potential analysis for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f"❌ Redox potential analysis for '{name}' failed!\n\n"
        else:
            formatted = f"⚠️ Redox potential analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status}\n"
        formatted += f"⚙️ Mode: {mode_lower.title()}\n"
        formatted += f"💧 Solvent: Acetonitrile\n"
        
        # Show which potentials were calculated
        calc_types = []
        if reduction:
            calc_types.append("Reduction")
        if oxidation:
            calc_types.append("Oxidation")
        formatted += f"⚡ Calculated: {' + '.join(calc_types)} potential(s)\n"
        
        # Try to extract redox potential results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            if reduction and 'reduction_potential' in data and data['reduction_potential'] is not None:
                formatted += f"🔋 Reduction Potential: {data['reduction_potential']:.3f} V vs. SCE\n"
            
            if oxidation and 'oxidation_potential' in data and data['oxidation_potential'] is not None:
                formatted += f"⚡ Oxidation Potential: {data['oxidation_potential']:.3f} V vs. SCE\n"
            
            # Legacy support for older format
            if 'redox_potential' in data and data['redox_potential'] is not None:
                redox_type = data.get('redox_type', 'unknown')
                formatted += f"⚡ {redox_type.title()} Potential: {data['redox_potential']:.3f} V vs. SCE\n"
        
        if status == 2:
            formatted += f"\n🎯 **Results Available:**\n"
            formatted += f"• Potentials reported vs. SCE (Saturated Calomel Electrode)\n"
            formatted += f"• Calculated in acetonitrile solvent\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
        
        return formatted
    else:
        formatted = f"🚀 Redox potential analysis for '{name}' submitted!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Submitted')}\n"
        formatted += f"⚙️ Mode: {mode_lower.title()}\n"
        
        calc_types = []
        if reduction:
            calc_types.append("Reduction")
        if oxidation:
            calc_types.append("Oxidation")
        formatted += f"⚡ Will calculate: {' + '.join(calc_types)} potential(s)\n"
        
        return formatted


# Scan - Potential Energy Surface Scans
@mcp.tool()
@log_mcp_call
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
    
    **📐 Coordinate Types:**
    - **bond**: Distance between 2 atoms (requires 2 atom indices)
    - **angle**: Angle between 3 atoms (requires 3 atom indices)  
    - **dihedral**: Dihedral angle between 4 atoms (requires 4 atom indices)
    
    **🔢 Scan Types:**
    - **1D Scan**: Single coordinate (coordinate_type, atoms, start, stop, num)
    - **2D Scan**: Two coordinates simultaneously creating a grid (add coordinate_type_2d, atoms_2d, start_2d, stop_2d, num_2d)
    - **Concerted Scan**: Multiple coordinates changing together (use concerted_coordinates list)
    
    **⚙️ Advanced Features:**
    - **Wavefront Propagation**: Uses previous scan point geometries as starting points (wavefront_propagation=True)
    - **2D Grids**: Scan two coordinates simultaneously to create potential energy surfaces
    - **Concerted Scans**: Multiple coordinates can be scanned simultaneously with same number of steps
    
    **Example: Ethane C-C rotation (1D)**
    ```
    rowan_scan(
        name="ethane_rotation", 
        molecule="CC",
        coordinate_type="dihedral",
        atoms=[1, 2, 3, 4],  # H-C-C-H dihedral
        start=0, stop=360, num=24,  # Full rotation in 15° steps
        method="b3lyp", basis_set="pcseg-1"
    )
    ```
    
    **Example: 2D scan (bond + dihedral)**
    ```
    rowan_scan(
        name="2d_scan", 
        molecule="CC",
        coordinate_type="bond", atoms=[1, 2], start=1.3, stop=1.8, num=10,
        coordinate_type_2d="dihedral", atoms_2d=[1, 2, 3, 4], start_2d=0, stop_2d=180, num_2d=10,
        wavefront_propagation=True
    )
    ```
    
    Use this for: Reaction mechanism studies, transition state searching, conformational analysis, 2D energy surfaces
    
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
        return f"❌ Invalid coordinate_type '{coordinate_type}'. Valid types: {', '.join(valid_coord_types)}"
    
    # Handle string input for atoms (common format: "1,2,3,4")
    if isinstance(atoms, str):
        try:
            # Parse comma-separated string to list of integers
            atoms = [int(x.strip()) for x in atoms.split(",")]
            logger.info(f"🔍 Parsed atom string '{atoms}' to list: {atoms}")
        except ValueError as e:
            return f"❌ Invalid atoms string '{atoms}'. Use format '1,2,3,4' or pass as list [1,2,3,4]. Error: {e}"
    
    # Ensure atoms is a list
    if not isinstance(atoms, list):
        return f"❌ Atoms must be a list of integers or comma-separated string. Got: {type(atoms).__name__}"
    
    # Validate atom count for coordinate type
    expected_atoms = {"bond": 2, "angle": 3, "dihedral": 4}
    expected_count = expected_atoms[coord_type_lower]
    if len(atoms) != expected_count:
        return f"❌ {coordinate_type} requires exactly {expected_count} atoms, got {len(atoms)}. Use format: [1,2,3,4] or '1,2,3,4'"
    
    # Validate atoms are positive integers
    if not all(isinstance(atom, int) and atom > 0 for atom in atoms):
        return f"❌ All atom indices must be positive integers (1-indexed). Got: {atoms}. Use format: [1,2,3,4] or '1,2,3,4'"
    
    # Validate scan range
    if num < 2:
        return f"❌ Number of scan points must be at least 2, got {num}"
    
    if start >= stop:
        return f"❌ Start value ({start}) must be less than stop value ({stop})"
    
    # Handle 2D scan validation
    is_2d_scan = any([coordinate_type_2d, atoms_2d, start_2d is not None, stop_2d is not None, num_2d is not None])
    
    if is_2d_scan:
        # For 2D scan, all 2D parameters must be provided
        if not all([coordinate_type_2d, atoms_2d, start_2d is not None, stop_2d is not None, num_2d is not None]):
            return f"❌ For 2D scans, all 2D parameters must be provided: coordinate_type_2d, atoms_2d, start_2d, stop_2d, num_2d"
        
        # Validate 2D coordinate type
        coord_type_2d_lower = coordinate_type_2d.lower()
        if coord_type_2d_lower not in valid_coord_types:
            return f"❌ Invalid coordinate_type_2d '{coordinate_type_2d}'. Valid types: {', '.join(valid_coord_types)}"
        
        # Handle string input for 2D atoms
        if isinstance(atoms_2d, str):
            try:
                atoms_2d = [int(x.strip()) for x in atoms_2d.split(",")]
                logger.info(f"🔍 Parsed 2D atom string to list: {atoms_2d}")
            except ValueError as e:
                return f"❌ Invalid atoms_2d string '{atoms_2d}'. Use format '1,2,3,4' or pass as list [1,2,3,4]. Error: {e}"
        
        # Validate 2D atom count
        expected_count_2d = expected_atoms[coord_type_2d_lower]
        if len(atoms_2d) != expected_count_2d:
            return f"❌ {coordinate_type_2d} requires exactly {expected_count_2d} atoms, got {len(atoms_2d)}"
        
        # Validate 2D atoms are positive integers
        if not all(isinstance(atom, int) and atom > 0 for atom in atoms_2d):
            return f"❌ All 2D atom indices must be positive integers (1-indexed). Got: {atoms_2d}"
        
        # Validate 2D scan range
        if num_2d < 2:
            return f"❌ Number of 2D scan points must be at least 2, got {num_2d}"
        
        if start_2d >= stop_2d:
            return f"❌ 2D start value ({start_2d}) must be less than stop value ({stop_2d})"
        
        # For true 2D grid scans, both dimensions should have same number of points
        # (This creates an N×N grid rather than N points along each coordinate)
        logger.info(f"🔲 2D Scan: {num} × {num_2d} grid ({num * num_2d} total points)")
    
    # Handle concerted scan validation
    if concerted_coordinates:
        # Validate each coordinate in the concerted scan
        for i, coord in enumerate(concerted_coordinates):
            required_keys = {"coordinate_type", "atoms", "start", "stop", "num"}
            if not all(key in coord for key in required_keys):
                return f"❌ Concerted coordinate {i+1} missing required keys: {required_keys}"
            
            # All concerted coordinates must have same number of steps
            if coord["num"] != num:
                return f"❌ All concerted scan coordinates must have same number of steps. Got {coord['num']} vs {num}"
            
            # Validate coordinate type
            if coord["coordinate_type"].lower() not in valid_coord_types:
                return f"❌ Invalid coordinate_type in concerted coordinate {i+1}: '{coord['coordinate_type']}'"
        
        logger.info(f"🔗 Concerted Scan: {len(concerted_coordinates)} coordinates with {num} steps each")
    
    # Set intelligent defaults based on coordinate type and method preferences
    if method is None:
        method = "hf-3c"  # Fast default for scans as recommended in docs
        
    if engine is None:
        engine = "psi4"  # Required by Rowan API
        
    if mode is None:
        mode = "rapid"  # Good balance for scans
        
    # Validate QC parameters if provided (reuse existing validation logic)
    if method and method.lower() not in QC_METHODS and method.lower() != "hf-3c":
        available_methods = ", ".join(list(QC_METHODS.keys()) + ["hf-3c"])
        return f"❌ Invalid method '{method}'. Available methods: {available_methods}"
    
    if basis_set and basis_set.lower() not in QC_BASIS_SETS:
        available_basis = ", ".join(QC_BASIS_SETS.keys())
        return f"❌ Invalid basis set '{basis_set}'. Available basis sets: {available_basis}"
    
    if engine and engine.lower() not in QC_ENGINES:
        available_engines = ", ".join(QC_ENGINES.keys())
        return f"❌ Invalid engine '{engine}'. Available engines: {available_engines}"
    
    if corrections:
        invalid_corrections = [corr for corr in corrections if corr.lower() not in QC_CORRECTIONS]
        if invalid_corrections:
            available_corrections = ", ".join(QC_CORRECTIONS.keys())
            return f"❌ Invalid corrections {invalid_corrections}. Available corrections: {available_corrections}"
    
    # Validate mode
    valid_modes = ["reckless", "rapid", "careful", "meticulous"]
    if mode and mode.lower() not in valid_modes:
        return f"❌ Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
    
    # Log the scan parameters
    logger.info(f"🔬 PES Scan Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Using SMILES: {canonical_smiles}")
    logger.info(f"   Primary Coordinate: {coord_type_lower}")
    logger.info(f"   Primary Atoms: {atoms}")
    logger.info(f"   Primary Range: {start} to {stop} in {num} steps")
    if is_2d_scan:
        logger.info(f"   Secondary Coordinate: {coord_type_2d_lower}")
        logger.info(f"   Secondary Atoms: {atoms_2d}")
        logger.info(f"   Secondary Range: {start_2d} to {stop_2d} in {num_2d} steps")
        logger.info(f"   2D Grid Size: {num} × {num_2d} = {num * num_2d} total points")
    if concerted_coordinates:
        logger.info(f"   Concerted Coordinates: {len(concerted_coordinates)}")
    logger.info(f"   Method: {method}")
    logger.info(f"   Basis Set: {basis_set or 'auto-selected'}")
    logger.info(f"   Engine: {engine}")
    logger.info(f"   Mode: {mode}")
    logger.info(f"   Wavefront Propagation: {wavefront_propagation}")
    
    try:
        # Build scan coordinate specification based on scan type
        scan_coordinates = []
        
        # Primary coordinate
        primary_coord = {
            "coordinate_type": coord_type_lower,
            "atoms": atoms,
            "start": start,
            "stop": stop,
            "num": num
        }
        scan_coordinates.append(primary_coord)
        
        # Add 2D coordinate if specified
        if is_2d_scan:
            secondary_coord = {
                "coordinate_type": coord_type_2d_lower,
                "atoms": atoms_2d,
                "start": start_2d,
                "stop": stop_2d,
                "num": num_2d
            }
            scan_coordinates.append(secondary_coord)
        
        # Add concerted coordinates if specified
        if concerted_coordinates:
            for coord in concerted_coordinates:
                scan_coordinates.append({
                    "coordinate_type": coord["coordinate_type"].lower(),
                    "atoms": coord["atoms"],
                    "start": coord["start"],
                    "stop": coord["stop"],
                    "num": coord["num"]
                })
        
        # Build parameters for rowan.compute call
        compute_params = {
            "name": name,
            "molecule": canonical_smiles,  # Use canonical SMILES
            "folder_uuid": folder_uuid,
            "blocking": blocking,
            "ping_interval": ping_interval
        }
        
        # Handle different scan coordinate formats based on what Rowan API expects
        if len(scan_coordinates) == 1:
            # Single coordinate scan - use the existing format
            compute_params["scan_coordinate"] = scan_coordinates[0]
        else:
            # Multiple coordinates - use scan_settings format
            compute_params["scan_settings"] = scan_coordinates
            if is_2d_scan:
                # For 2D scans, separate primary and secondary coordinates
                compute_params["scan_settings"] = scan_coordinates[0]
                compute_params["scan_settings_2d"] = scan_coordinates[1]
        
        # Add wavefront propagation setting
        compute_params["wavefront_propagation"] = wavefront_propagation
        
        # Add QC parameters
        if method:
            compute_params["method"] = method.lower()
        if basis_set:
            compute_params["basis_set"] = basis_set.lower()
        if engine:
            compute_params["engine"] = engine.lower()
        if corrections:
            compute_params["corrections"] = [corr.lower() for corr in corrections]
        if charge != 0:
            compute_params["charge"] = charge
        if multiplicity != 1:
            compute_params["multiplicity"] = multiplicity
        if mode:
            compute_params["mode"] = mode.lower()
        if constraints:
            compute_params["constraints"] = constraints
        
        # Use "scan" workflow type
        result = log_rowan_api_call(
            workflow_type="scan",
            **compute_params
        )
        
        # Format results based on status
        job_status = result.get('status', result.get('object_status', None))
        
        # Try to get status via API if not available
        if job_status is None and result.get('uuid'):
            try:
                job_status = rowan.Workflow.status(uuid=result.get('uuid'))
                logger.info(f"📊 Retrieved scan status via API: {job_status}")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve scan status: {e}")
                job_status = None
        
        status_names = {
            0: ("⏳", "Queued"),
            1: ("🔄", "Running"), 
            2: ("✅", "Completed Successfully"),
            3: ("❌", "Failed"),
            4: ("⏹️", "Stopped"),
            5: ("⏸️", "Awaiting Queue")
        }
        
        status_icon, status_text = status_names.get(job_status, ("❓", f"Unknown ({job_status})"))
        
        # Handle None status
        if job_status is None:
            status_icon, status_text = ("📝", "Submitted (status pending)")
        
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
            formatted = f"✅ {scan_type} '{name}' completed successfully!\n\n"
        elif job_status == 3:
            formatted = f"❌ {scan_type} '{name}' failed!\n\n"
        elif job_status in [0, 1, 5]:
            formatted = f"🔄 {scan_type} '{name}' submitted and running!\n\n"
        elif job_status == 4:
            formatted = f"⏹️ {scan_type} '{name}' was stopped!\n\n"
        else:
            formatted = f"📊 {scan_type} '{name}' status unknown!\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status_icon} {status_text} ({job_status})\n"
        
        # Scan coordinate details
        formatted += f"\n📐 **Scan Coordinates:**\n"
        formatted += f"   Type: {scan_type}\n"
        formatted += f"   Primary: {coordinate_type.upper()} on atoms {atoms} ({start} → {stop}, {num} points)\n"
        if is_2d_scan:
            formatted += f"   Secondary: {coordinate_type_2d.upper()} on atoms {atoms_2d} ({start_2d} → {stop_2d}, {num_2d} points)\n"
            formatted += f"   Grid Size: {num} × {num_2d} = {total_points} total points\n"
        elif concerted_coordinates:
            for i, coord in enumerate(concerted_coordinates):
                formatted += f"   Coordinate {i+2}: {coord['coordinate_type'].upper()} on atoms {coord['atoms']} ({coord['start']} → {coord['stop']})\n"
        formatted += f"   Total Points: {total_points}\n"
        
        # Applied settings
        formatted += f"\n⚙️ **Computational Settings:**\n"
        if method:
            method_desc = QC_METHODS.get(method.lower(), "Fast composite method" if "3c" in method else "Custom method")
            formatted += f"   Method: {method.upper()} - {method_desc}\n"
        if basis_set:
            basis_desc = QC_BASIS_SETS.get(basis_set.lower(), "Custom basis set")
            formatted += f"   Basis Set: {basis_set} - {basis_desc}\n"
        if engine:
            engine_desc = QC_ENGINES.get(engine.lower(), "Custom engine")
            formatted += f"   Engine: {engine.upper()} - {engine_desc}\n"
        if corrections:
            formatted += f"   Corrections: {', '.join(corrections)}\n"
        if charge != 0 or multiplicity != 1:
            formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
        if mode:
            formatted += f"   Mode: {mode.title()}\n"
        if constraints:
            formatted += f"   Additional Constraints: {len(constraints)} applied\n"
        formatted += f"   Wavefront Propagation: {'Enabled' if wavefront_propagation else 'Disabled'}\n"
        
        # Status-specific guidance
        formatted += f"\n💡 **Next Steps:**\n"
        if job_status == 2:  # Completed
            formatted += f"• Use `rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid', 'UUID')}')` for detailed results\n"
            if is_2d_scan:
                formatted += f"• 2D scan creates energy surface - look for minima, maxima, and saddle points\n"
                formatted += f"• Results can be visualized as contour plots or 3D surfaces\n"
            else:
                formatted += f"• Scan shows energy profile along coordinate(s)\n"
                formatted += f"• Look for energy maxima (potential transition states) and minima (stable conformers)\n"
            formatted += f"• High-energy points can be used as starting guesses for transition state optimizations\n"
        elif job_status == 3:  # Failed
            formatted += f"• Use `rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid', 'UUID')}')` for error details\n"
            formatted += f"• **Troubleshooting:**\n"
            formatted += f"  - Check atom indices are correct and within molecule range\n"
            formatted += f"  - Try smaller scan range or fewer points\n"
            formatted += f"  - Use faster method: method='hf-3c' (recommended for scans)\n"
            formatted += f"  - For 2D scans: consider reducing grid size ({num}×{num_2d} = {total_points} points)\n"
            formatted += f"  - Ensure coordinate ranges are chemically reasonable\n"
        elif job_status in [0, 1, 5]:  # Running
            formatted += f"• Check progress: `rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid', 'UUID')}')`\n"
            if is_2d_scan:
                formatted += f"• 2D scan with {total_points} points may take several hours depending on method and molecule size\n"
            else:
                formatted += f"• Scan with {total_points} points may take 10-60 minutes depending on method and molecule size\n"
            formatted += f"• Each scan point involves a constrained geometry optimization\n"
            if wavefront_propagation:
                formatted += f"• Wavefront propagation helps avoid local minima by using previous geometries\n"
        elif job_status == 4:  # Stopped
            formatted += f"• Check why stopped: `rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid', 'UUID')}')`\n"
            formatted += f"• You can restart with same or modified parameters\n"
        else:  # Unknown
            formatted += f"• Check status: `rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid', 'UUID')}')`\n"
            formatted += f"• Get details: `rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid', 'UUID')}')`\n"
        
        # Add examples and guidance
        formatted += f"\n📚 **Scan Examples:**\n"
        formatted += f"• **1D Bond scan**: coordinate_type='bond', atoms=[1,2], start=1.0, stop=3.0\n"
        formatted += f"• **1D Angle scan**: coordinate_type='angle', atoms=[1,2,3], start=90, stop=180\n"
        formatted += f"• **1D Dihedral scan**: coordinate_type='dihedral', atoms=[1,2,3,4], start=0, stop=360\n"
        formatted += f"• **2D Bond+Dihedral**: Add coordinate_type_2d='dihedral', atoms_2d=[1,2,3,4], etc.\n"
        formatted += f"• **Concerted scan**: Use concerted_coordinates=[{{...}}, {{...}}] for multiple coordinates\n"
        formatted += f"• For atropisomerism studies: Use dihedral scans with 15-30 points over 360°\n"
        formatted += f"• For reaction mechanisms: 1D scans first, then 2D near transition states\n"
        
        return formatted
        
    except Exception as e:
        error_msg = f"❌ PES scan submission failed: {str(e)}\n\n"
        error_msg += "🔧 **Enhanced Scan Troubleshooting:**\n"
        error_msg += "• **Atom indices**: Check that atom numbers exist in the molecule (1-indexed)\n"
        error_msg += "• **Coordinate range**: Ensure start < stop and range is chemically reasonable\n"
        error_msg += "• **Method compatibility**: Some methods may not support scan calculations\n"
        error_msg += "• **Parameter format**: Use atoms=[1,2,3,4] or atoms='1,2,3,4'\n"
        error_msg += "• **2D scans**: All 2D parameters required if any are specified\n"
        error_msg += "• **Concerted scans**: All coordinates must have same number of steps\n\n"
        error_msg += "💡 **Quick Fix Examples:**\n"
        error_msg += f"• **1D scan**: rowan_scan('{name}', '{molecule}', '{coordinate_type}', [1,2,3,4], {start}, {stop}, {num})\n"
        error_msg += f"• **2D scan**: Add coordinate_type_2d='dihedral', atoms_2d=[1,2,3,4], start_2d=0, stop_2d=180, num_2d={num}\n"
        error_msg += f"• **With method**: rowan_scan(..., method='hf-3c', wavefront_propagation=True)\n\n"
        error_msg += "📚 **New Features:**\n"
        error_msg += "• **2D Scans**: Create potential energy surfaces with two coordinates\n"
        error_msg += "• **Concerted Scans**: Multiple coordinates changing simultaneously\n"
        error_msg += "• **Wavefront Propagation**: Better convergence using previous scan point geometries\n"
        return error_msg


# Fukui Indices - Reactivity Analysis
@mcp.tool()
@log_mcp_call
def rowan_fukui(
    name: str,
    molecule: str,
    optimize: bool = True,
    opt_method: Optional[str] = None,
    opt_basis_set: Optional[str] = None,
    opt_engine: Optional[str] = None,
    fukui_method: str = "gfn1_xtb",
    fukui_basis_set: Optional[str] = None,
    fukui_engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate Fukui indices for reactivity prediction with comprehensive control.
    
    Predicts sites of chemical reactivity by analyzing electron density changes upon
    gaining/losing electrons. Uses a two-step process: optimization + Fukui calculation.
    
    **🔬 Fukui Index Types:**
    - **f(+)**: Electrophilic attack sites (nucleophile reactivity)
    - **f(-)**: Nucleophilic attack sites (electrophile reactivity)  
    - **f(0)**: Radical attack sites (average of f(+) and f(-))
    - **Global Electrophilicity Index**: Overall electrophilic character
    
    **⚡ Key Features:**
    - Optional geometry optimization before Fukui calculation
    - Separate control over optimization and Fukui calculation methods
    - Per-atom reactivity indices for site-specific analysis
    - Global reactivity descriptors
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name (e.g., "phenol", "benzene")
        optimize: Whether to optimize geometry before Fukui calculation (default: True)
        opt_method: Method for optimization (default: None, uses engine default)
        opt_basis_set: Basis set for optimization (default: None, uses engine default)
        opt_engine: Engine for optimization (default: None, auto-selected)
        fukui_method: Method for Fukui calculation (default: "gfn1_xtb")
        fukui_basis_set: Basis set for Fukui calculation (default: None, uses method default)
        fukui_engine: Engine for Fukui calculation (default: None, auto-selected)
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Fukui indices and reactivity analysis with per-atom and global descriptors
    """
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Build optimization settings if requested
    opt_settings = None
    if optimize:
        opt_settings = {
            "charge": charge,
            "multiplicity": multiplicity
        }
        
        # Add optimization method/basis/engine if specified
        if opt_method:
            opt_settings["method"] = opt_method.lower()
        if opt_basis_set:
            opt_settings["basis_set"] = opt_basis_set.lower()
        
        # Default to fast optimization if no engine specified
        if not opt_engine and not opt_method:
            opt_settings["method"] = "gfn2_xtb"  # Fast optimization
            logger.info(f"🚀 No optimization method specified, defaulting to GFN2-xTB")
    
    # Build Fukui calculation settings
    fukui_settings = {
        "method": fukui_method.lower(),
        "charge": charge,
        "multiplicity": multiplicity
    }
    
    # Add Fukui basis set if specified
    if fukui_basis_set:
        fukui_settings["basis_set"] = fukui_basis_set.lower()
    
    # Validate Fukui method
    valid_fukui_methods = ["gfn1_xtb", "gfn2_xtb", "hf", "b3lyp", "pbe", "m06-2x"]
    if fukui_method.lower() not in valid_fukui_methods:
        logger.warning(f"⚠️ Unusual Fukui method '{fukui_method}'. Common methods: {valid_fukui_methods}")
    
    # Log the Fukui parameters
    logger.info(f"🔬 Fukui Analysis Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Using SMILES: {canonical_smiles}")
    logger.info(f"   Optimization: {'Enabled' if optimize else 'Disabled'}")
    if optimize:
        logger.info(f"   Opt Method: {opt_settings.get('method', 'default')}")
        if opt_engine:
            logger.info(f"   Opt Engine: {opt_engine}")
    logger.info(f"   Fukui Method: {fukui_method}")
    if fukui_engine:
        logger.info(f"   Fukui Engine: {fukui_engine}")
    logger.info(f"   Charge: {charge}, Multiplicity: {multiplicity}")
    
    # Build parameters for Rowan API
    fukui_params = {
        "name": name,
        "molecule": canonical_smiles,
        "fukui_settings": fukui_settings,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add optimization settings if enabled
    if optimize and opt_settings:
        fukui_params["opt_settings"] = opt_settings
        
    # Add engines if specified
    if opt_engine:
        fukui_params["opt_engine"] = opt_engine.lower()
    if fukui_engine:
        fukui_params["fukui_engine"] = fukui_engine.lower()
    
    result = log_rowan_api_call(
        workflow_type="fukui",
        **fukui_params
    )
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f"✅ Fukui analysis for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f"❌ Fukui analysis for '{name}' failed!\n\n"
        else:
            formatted = f"⚠️ Fukui analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status}\n"
        
        # Computational settings summary
        formatted += f"\n⚙️ **Computational Settings:**\n"
        formatted += f"   Optimization: {'Enabled' if optimize else 'Disabled'}\n"
        if optimize:
            opt_method_display = opt_settings.get('method', 'default') if opt_settings else 'default'
            formatted += f"   Opt Method: {opt_method_display.upper()}\n"
            if opt_engine:
                formatted += f"   Opt Engine: {opt_engine.upper()}\n"
        formatted += f"   Fukui Method: {fukui_method.upper()}\n"
        if fukui_engine:
            formatted += f"   Fukui Engine: {fukui_engine.upper()}\n"
        formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
        
        # Try to extract Fukui results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Global electrophilicity index
            if 'global_electrophilicity_index' in data and data['global_electrophilicity_index'] is not None:
                gei = data['global_electrophilicity_index']
                formatted += f"\n🌐 **Global Electrophilicity Index:** {gei:.4f}\n"
                if gei > 1.5:
                    formatted += f"   → Strong electrophile (highly reactive towards nucleophiles)\n"
                elif gei > 0.8:
                    formatted += f"   → Moderate electrophile\n"
                else:
                    formatted += f"   → Weak electrophile\n"
            
            # Fukui indices per atom
            fukui_available = []
            if 'fukui_positive' in data and data['fukui_positive']:
                fukui_available.append("f(+)")
            if 'fukui_negative' in data and data['fukui_negative']:
                fukui_available.append("f(-)")
            if 'fukui_zero' in data and data['fukui_zero']:
                fukui_available.append("f(0)")
                
            if fukui_available:
                formatted += f"\n⚡ **Fukui Indices Available:** {', '.join(fukui_available)}\n"
                
                # Analyze most reactive sites
                formatted += f"\n🎯 **Most Reactive Sites:**\n"
                
                # f(+) - electrophilic attack sites
                if 'fukui_positive' in data and data['fukui_positive']:
                    f_plus = data['fukui_positive']
                    if isinstance(f_plus, list) and len(f_plus) > 0:
                        # Find top 3 sites
                        indexed_values = [(i+1, val) for i, val in enumerate(f_plus) if val is not None]
                        top_f_plus = sorted(indexed_values, key=lambda x: x[1], reverse=True)[:3]
                        formatted += f"   f(+) Top Sites (electrophilic attack): "
                        formatted += f"{', '.join([f'Atom {atom}({val:.3f})' for atom, val in top_f_plus])}\n"
                
                # f(-) - nucleophilic attack sites  
                if 'fukui_negative' in data and data['fukui_negative']:
                    f_minus = data['fukui_negative']
                    if isinstance(f_minus, list) and len(f_minus) > 0:
                        indexed_values = [(i+1, val) for i, val in enumerate(f_minus) if val is not None]
                        top_f_minus = sorted(indexed_values, key=lambda x: x[1], reverse=True)[:3]
                        formatted += f"   f(-) Top Sites (nucleophilic attack): "
                        formatted += f"{', '.join([f'Atom {atom}({val:.3f})' for atom, val in top_f_minus])}\n"
                
                # f(0) - radical attack sites
                if 'fukui_zero' in data and data['fukui_zero']:
                    f_zero = data['fukui_zero']
                    if isinstance(f_zero, list) and len(f_zero) > 0:
                        indexed_values = [(i+1, val) for i, val in enumerate(f_zero) if val is not None]
                        top_f_zero = sorted(indexed_values, key=lambda x: x[1], reverse=True)[:3]
                        formatted += f"   f(0) Top Sites (radical attack): "
                        formatted += f"{', '.join([f'Atom {atom}({val:.3f})' for atom, val in top_f_zero])}\n"
        
        # Status-specific guidance
        formatted += f"\n💡 **Next Steps:**\n"
        if status == 2:  # Completed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for full per-atom data\n"
            formatted += f"• Higher Fukui values indicate more reactive sites\n"
            formatted += f"• f(+) predicts where nucleophiles will attack\n"
            formatted += f"• f(-) predicts where electrophiles will attack\n"
            formatted += f"• f(0) predicts radical reaction sites\n"
        elif status == 3:  # Failed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            formatted += f"• **Troubleshooting:**\n"
            formatted += f"  - Try disabling optimization: optimize=False\n"
            formatted += f"  - Use faster Fukui method: fukui_method='gfn1_xtb'\n"
            formatted += f"  - Check if molecule SMILES is valid\n"
            formatted += f"  - Verify charge and multiplicity are correct\n"
        elif status in [0, 1, 5]:  # Running
            formatted += f"• Check progress: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
            if optimize:
                formatted += f"• Two-step process: optimization → Fukui calculation\n"
            formatted += f"• Fukui analysis may take 5-20 minutes depending on method and molecule size\n"
        elif status == 4:  # Stopped
            formatted += f"• Check why stopped: rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
            formatted += f"• You can restart with same or modified parameters\n"
        else:  # Unknown
            formatted += f"• Check status: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
        
        # Add examples and guidance
        formatted += f"\n📚 **Fukui Examples:**\n"
        formatted += f"• **Basic analysis**: rowan_fukui('benzene_fukui', 'benzene')\n"
        formatted += f"• **Skip optimization**: rowan_fukui('quick', 'SMILES', optimize=False)\n"
        formatted += f"• **High-accuracy**: rowan_fukui('accurate', 'SMILES', fukui_method='b3lyp', fukui_basis_set='def2-tzvp')\n"
        formatted += f"• **Charged species**: rowan_fukui('cation', 'SMILES', charge=+1)\n"
        formatted += f"• **Custom optimization**: rowan_fukui('custom', 'SMILES', opt_method='b3lyp', opt_basis_set='def2-svp')\n\n"
        
        formatted += f"🔬 **Method Guide:**\n"
        formatted += f"• **gfn1_xtb**: Fast semiempirical, good for large molecules (default)\n"
        formatted += f"• **gfn2_xtb**: More accurate semiempirical method\n"
        formatted += f"• **hf**: Hartree-Fock, basic quantum method\n"
        formatted += f"• **b3lyp**: Popular DFT method, good accuracy\n"
        formatted += f"• **m06-2x**: Meta-GGA DFT, excellent for organics\n\n"
        
        formatted += f"⚡ **Interpretation Guide:**\n"
        formatted += f"• **f(+) > 0.1**: Strong electrophilic attack site\n"
        formatted += f"• **f(-) > 0.1**: Strong nucleophilic attack site\n"
        formatted += f"• **f(0) > 0.1**: Strong radical attack site\n"
        formatted += f"• Compare relative values within the same molecule\n"
        
        return formatted
    else:
        formatted = f"🚀 Fukui analysis for '{name}' submitted!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Submitted')}\n"
        formatted += f"⚙️ Optimization: {'Enabled' if optimize else 'Disabled'}\n"
        formatted += f"🔬 Fukui Method: {fukui_method.upper()}\n"
        formatted += f"⚡ Charge: {charge}, Multiplicity: {multiplicity}\n"
        formatted += f"\n💡 Use rowan_workflow_management tools to check progress and retrieve results\n"
        return formatted


# Spin States
@mcp.tool()
@log_mcp_call
def rowan_spin_states(
    name: str,
    molecule: str,
    states: Optional[List[int]] = None,
    charge: Optional[int] = None,
    multiplicity: Optional[int] = None,
    mode: str = "rapid",
    solvent: Optional[str] = None,
    xtb_preopt: bool = True,
    constraints: Optional[List[Dict[str, Any]]] = None,
    transition_state: bool = False,
    frequencies: bool = False,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 10,
    auto_analyze: bool = True
) -> str:
    """Determine preferred spin states for molecules with intelligent auto-analysis.
    
    **🤖 INTELLIGENT AUTO-ANALYSIS:**
    - Automatically recognizes transition metal complexes (e.g., Mn(Cl)6, Fe(CN)6, Cu(H2O)4)
    - Predicts appropriate charge, multiplicity, and spin states based on chemical knowledge
    - Suggests realistic spin states for d-electron configurations
    - Provides chemical explanations for predictions
    
    **🔬 Spin State Analysis:**
    - Uses multi-stage optimization (xTB → AIMNet2 → DFT) for accurate energies
    - Validates multiplicity consistency (all must have same parity)
    - Ranks spin states by energy to identify ground state
    - Supports transition metal complexes and radical species
    
    **⚡ Auto-Detected Complexes:**
    - Mn(Cl)6 → charge: -4, states: [2, 6] (d5: low-spin vs high-spin)
    - Fe(CN)6 → charge: -4, states: [1, 5] (d6: low-spin vs high-spin) 
    - Cu(H2O)4 → charge: +2, states: [2] (d9: always doublet)
    - Ni(H2O)6 → charge: +2, states: [3] (d8: high-spin triplet)
    - Co(NH3)6 → charge: +3, states: [1] (d6: low-spin singlet)
    
    **🎯 Manual Override Available:**
    - All auto-detected parameters can be manually overridden
    - Set auto_analyze=False to disable automatic analysis
    - Specify states, charge, multiplicity explicitly if needed
    
    Use this for: Transition metal complexes, radical species, magnetic materials, spin crossover systems
    
    Args:
        name: Name for the calculation
        molecule: Molecular formula or SMILES (e.g., "Mn(Cl)6", "Fe(CN)6", SMILES string)
        states: List of spin multiplicities - auto-detected if None (e.g., [1, 3, 5])
        charge: Molecular charge - auto-detected if None (e.g., -4 for Mn(Cl)6)
        multiplicity: Default multiplicity - auto-detected if None
        mode: Calculation precision - "reckless", "rapid", "careful", "meticulous" (default: "rapid")
        solvent: Solvent for optimization (e.g., "water", "acetonitrile", "dmso", default: None = gas phase)
        xtb_preopt: Whether to pre-optimize with xTB before higher-level calculations (default: True)
        constraints: Additional coordinate constraints during optimization (default: None)
        transition_state: Whether this is a transition state optimization (default: False)
        frequencies: Whether to calculate vibrational frequencies (default: False)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 10, longer for spin state calculations)
        auto_analyze: Whether to automatically analyze molecule for appropriate parameters (default: True)
    
    Returns:
        Spin state energetics analysis with relative energies and ground state identification
    """
    # Preprocess molecule input to handle subscripts and chemical formulas
    def preprocess_molecule_input(mol_input: str) -> str:
        """Convert subscripts and normalize chemical formulas."""
        # Replace Unicode subscripts with regular numbers
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', 
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
        }
        
        processed = mol_input
        for sub, num in subscript_map.items():
            processed = processed.replace(sub, num)
            
        logger.info(f"🔧 Preprocessed molecule: '{mol_input}' → '{processed}'")
        return processed
    
    # Preprocess the molecule input
    processed_molecule = preprocess_molecule_input(molecule)
    
    # Auto-analyze molecule if enabled and parameters not provided
    analysis_results = None
    if auto_analyze and (states is None or charge is None or multiplicity is None):
        analysis_results = analyze_spin_states(processed_molecule)
        logger.info(f"🤖 Auto-analysis enabled for '{processed_molecule}'")
        logger.info(f"🔍 Analysis results: {analysis_results}")
    
    # Apply auto-analysis results, but allow manual overrides
    if states is None:
        if analysis_results:
            states = analysis_results["states"]
            logger.info(f"🎯 Auto-detected spin states: {states}")
        else:
            return f"❌ Error: 'states' must be provided when auto_analyze=False or analysis fails. Provide as list like [1, 3, 5]"
    
    if charge is None and analysis_results and "charge" in analysis_results:
        charge = analysis_results["charge"]
        logger.info(f"⚡ Auto-detected charge: {charge}")
    
    if multiplicity is None and analysis_results and "multiplicity" in analysis_results:
        multiplicity = analysis_results["multiplicity"]
        logger.info(f"🔬 Auto-detected multiplicity: {multiplicity}")
    
    # For chemical formulas, don't try SMILES lookup - use the processed formula directly
    # Check if this looks like a chemical formula vs SMILES
    import re
    is_chemical_formula = bool(re.search(r'[A-Z][a-z]?\([A-Z]', processed_molecule))
    
    if is_chemical_formula:
        canonical_smiles = processed_molecule
        logger.info(f"🔬 Using chemical formula directly: {canonical_smiles}")
    else:
        # Look up SMILES if a common name was provided
        canonical_smiles = lookup_molecule_smiles(processed_molecule)
    
    # Validate states parameter
    if not states or not isinstance(states, list):
        return f"❌ Error: 'states' must be a non-empty list of positive integers. Got: {states}"
    
    if not all(isinstance(s, int) and s > 0 for s in states):
        return f"❌ Error: All multiplicities in 'states' must be positive integers. Got: {states}"
    
    if len(states) < 1:
        return f"❌ Error: At least one spin multiplicity must be specified. Got: {states}"
    
    # Check multiplicity parity consistency (all odd or all even)
    first_parity = states[0] % 2
    if not all((s % 2) == first_parity for s in states):
        return f"❌ Error: All multiplicities must have the same parity (all odd or all even). Got: {states}"
    
    # Validate mode
    valid_modes = ["reckless", "rapid", "careful", "meticulous"]
    mode_lower = mode.lower()
    if mode_lower not in valid_modes:
        return f"❌ Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}"
    
    # Log the spin states parameters
    logger.info(f"🔬 Spin States Analysis Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Using SMILES: {canonical_smiles}")
    logger.info(f"   States (multiplicities): {states}")
    logger.info(f"   Charge: {charge}")
    logger.info(f"   Multiplicity: {multiplicity}")
    logger.info(f"   Mode: {mode_lower}")
    logger.info(f"   Auto-analysis: {auto_analyze}")
    if analysis_results:
        logger.info(f"   Analysis explanation: {analysis_results.get('explanation', 'N/A')}")
        logger.info(f"   Analysis confidence: {analysis_results.get('confidence', 'N/A')}")
    logger.info(f"   Solvent: {solvent or 'gas phase'}")
    logger.info(f"   xTB Pre-optimization: {xtb_preopt}")
    logger.info(f"   Transition State: {transition_state}")
    logger.info(f"   Frequencies: {frequencies}")
    logger.info(f"   Constraints: {len(constraints) if constraints else 0} applied")
    
    # Build parameters for Rowan API
    spin_params = {
        "name": name,
        "molecule": canonical_smiles,
        "states": states,
        "mode": mode_lower,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add charge and multiplicity if specified
    if charge is not None:
        spin_params["charge"] = charge
    if multiplicity is not None:
        spin_params["multiplicity"] = multiplicity
    
    # Add optional parameters if specified
    if solvent is not None:
        spin_params["solvent"] = solvent
    if not xtb_preopt:  # Only set if False (True is likely default)
        spin_params["xtb_preopt"] = xtb_preopt
    if constraints is not None:
        spin_params["constraints"] = constraints
    if transition_state:  # Only set if True (False is likely default)
        spin_params["transition_state"] = transition_state
    if frequencies:  # Only set if True (False is likely default) 
        spin_params["frequencies"] = frequencies
    
    result = log_rowan_api_call(
        workflow_type="spin_states",
        **spin_params
    )
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f"✅ Spin states analysis for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f"❌ Spin states analysis for '{name}' failed!\n\n"
        else:
            formatted = f"⚠️ Spin states analysis for '{name}' finished with status {status}\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        if processed_molecule != molecule:
            formatted += f"🔧 Processed: {processed_molecule}\n"
        formatted += f"🔬 Input: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status}\n"
        formatted += f"⚡ Multiplicities: {states}\n"
        if charge is not None:
            formatted += f"⚡ Charge: {charge:+d}\n"
        if multiplicity is not None:
            formatted += f"🔬 Default Multiplicity: {multiplicity}\n"
        
        # Show auto-analysis results if used
        if analysis_results and auto_analyze:
            formatted += f"\n🤖 **Auto-Analysis Results:**\n"
            formatted += f"   Confidence: {analysis_results['confidence'].title()}\n"
            formatted += f"   Explanation: {analysis_results['explanation']}\n"
            if 'oxidation_state' in analysis_results:
                formatted += f"   Metal Oxidation State: +{analysis_results['oxidation_state']}\n"
            if 'd_electrons' in analysis_results:
                formatted += f"   d-Electron Count: d{analysis_results['d_electrons']}\n"
        
        # Applied settings
        formatted += f"\n⚙️ **Computational Settings:**\n"
        formatted += f"   Mode: {mode_lower.title()} (multi-stage optimization)\n"
        formatted += f"   Solvent: {solvent or 'Gas Phase'}\n"
        formatted += f"   xTB Pre-optimization: {'Enabled' if xtb_preopt else 'Disabled'}\n"
        if transition_state:
            formatted += f"   Transition State: Yes\n"
        if frequencies:
            formatted += f"   Frequencies: Calculated\n"
        if constraints:
            formatted += f"   Constraints: {len(constraints)} applied\n"
        
        # Try to extract spin states results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Look for spin states data
            if 'spin_states' in data and isinstance(data['spin_states'], list):
                spin_results = data['spin_states']
                if spin_results:
                    formatted += f"\n⚡ **Spin States Results:**\n"
                    
                    # Sort by energy to identify ground state
                    sorted_states = sorted(spin_results, key=lambda x: x.get('energy', float('inf')))
                    ground_state = sorted_states[0] if sorted_states else None
                    
                    for i, state in enumerate(sorted_states):
                        mult = state.get('multiplicity', 'N/A')
                        energy = state.get('energy', 'N/A')
                        is_ground = (i == 0)
                        
                        if isinstance(energy, (int, float)):
                            # Calculate relative energy in kcal/mol (assuming energies in Hartree)
                            if is_ground:
                                rel_energy = 0.0
                                formatted += f"   🥇 Multiplicity {mult}: {energy:.6f} au (Ground State)\n"
                            else:
                                rel_energy = (energy - ground_state.get('energy', 0)) * 627.5094740631  # Hartree to kcal/mol
                                formatted += f"   ⚡ Multiplicity {mult}: {energy:.6f} au (+{rel_energy:.2f} kcal/mol)\n"
                        else:
                            formatted += f"   ⚡ Multiplicity {mult}: {energy}\n"
                    
                    # Summary
                    if ground_state:
                        ground_mult = ground_state.get('multiplicity', 'Unknown')
                        formatted += f"\n🎯 **Ground State:** Multiplicity {ground_mult}\n"
                        
                        # Interpret ground state
                        spin_names = {1: "Singlet", 2: "Doublet", 3: "Triplet", 4: "Quartet", 5: "Quintet", 6: "Sextet", 7: "Septet"}
                        if ground_mult in spin_names:
                            formatted += f"   Spin State: {spin_names[ground_mult]}\n"
                        
                        unpaired_electrons = ground_mult - 1
                        formatted += f"   Unpaired Electrons: {unpaired_electrons}\n"
            
            # Legacy support for other energy formats
            elif 'energies' in data and isinstance(data['energies'], list):
                energies = data['energies']
                if energies and len(energies) == len(states):
                    formatted += f"\n⚡ **Spin States Energies:**\n"
                    
                    # Pair with multiplicities and sort by energy
                    paired_results = list(zip(states, energies))
                    paired_results.sort(key=lambda x: x[1])
                    
                    ground_energy = paired_results[0][1]
                    ground_mult = paired_results[0][0]
                    
                    for mult, energy in paired_results:
                        if mult == ground_mult:
                            formatted += f"   🥇 Multiplicity {mult}: {energy:.6f} au (Ground State)\n"
                        else:
                            rel_energy = (energy - ground_energy) * 627.5094740631  # Hartree to kcal/mol
                            formatted += f"   ⚡ Multiplicity {mult}: {energy:.6f} au (+{rel_energy:.2f} kcal/mol)\n"
                    
                    formatted += f"\n🎯 **Ground State:** Multiplicity {ground_mult}\n"
        
        # Status-specific guidance
        formatted += f"\n💡 **Next Steps:**\n"
        if status == 2:  # Completed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed results\n"
            formatted += f"• Ground state identified from relative energies\n"
            formatted += f"• Consider electronic structure analysis for ground state geometry\n"
            formatted += f"• For transition metals: compare with experimental magnetic data\n"
        elif status == 3:  # Failed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            formatted += f"• **Troubleshooting:**\n"
            formatted += f"  - Check multiplicity parity: {states} (all odd or all even)\n"
            formatted += f"  - Try fewer multiplicities or simpler mode: mode='reckless'\n"
            formatted += f"  - For transition metals: ensure reasonable oxidation states\n"
            formatted += f"  - Consider starting with just two states: [1, 3] or [2, 4]\n"
        elif status in [0, 1, 5]:  # Running
            formatted += f"• Check progress: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
            total_calcs = len(states) * 3  # Approximate: 3 levels per multiplicity
            formatted += f"• Spin states calculation involves ~{total_calcs} optimizations ({len(states)} multiplicities × 3 levels)\n"
            formatted += f"• May take 15-60 minutes depending on molecule size and multiplicities\n"
        elif status == 4:  # Stopped
            formatted += f"• Check why stopped: rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
            formatted += f"• You can restart with same or different multiplicities\n"
        else:  # Unknown
            formatted += f"• Check status: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
        
        # Add examples and guidance
        formatted += f"\n📚 **Auto-Analysis Examples:**\n"
        formatted += f"• **Mn(Cl)6** → charge: -4, states: [2, 6] (Mn(II) d5: low vs high-spin)\n"
        formatted += f"• **Fe(CN)6** → charge: -4, states: [1, 5] (Fe(II) d6: low vs high-spin)\n"
        formatted += f"• **Cu(H2O)4** → charge: +2, states: [2] (Cu(II) d9: always doublet)\n"
        formatted += f"• **Ni(H2O)6** → charge: +2, states: [3] (Ni(II) d8: high-spin triplet)\n"
        formatted += f"• **Co(NH3)6** → charge: +3, states: [1] (Co(III) d6: low-spin singlet)\n"
        formatted += f"• **Cr(H2O)6** → charge: +3, states: [4] (Cr(III) d3: always high-spin)\n\n"
        
        formatted += f"🎯 **Manual Override Examples:**\n"
        formatted += f"• rowan_spin_states('test', 'Mn(Cl)6') → auto-detects everything\n"
        formatted += f"• rowan_spin_states('test', 'SMILES', states=[1,3,5]) → manual states\n"
        formatted += f"• rowan_spin_states('test', 'complex', charge=-2, states=[2,4]) → manual override\n"
        formatted += f"• rowan_spin_states('test', 'molecule', auto_analyze=False, states=[1]) → no auto-analysis\n\n"
        
        formatted += f"⚗️ **Multiplicity Guide:**\n"
        formatted += f"• Multiplicity = 2S + 1 (where S = total spin)\n"
        formatted += f"• Singlet (S=0): 0 unpaired electrons → closed shell\n"
        formatted += f"• Doublet (S=1/2): 1 unpaired electron\n" 
        formatted += f"• Triplet (S=1): 2 unpaired electrons, parallel spins\n"
        formatted += f"• Quartet (S=3/2): 3 unpaired electrons\n"
        formatted += f"• Quintet (S=2): 4 unpaired electrons\n"
        
        return formatted
    else:
        formatted = f"🚀 Spin states analysis for '{name}' submitted!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        if processed_molecule != molecule:
            formatted += f"🔧 Processed: {processed_molecule}\n"
        formatted += f"🔬 Input: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Submitted')}\n"
        formatted += f"⚡ Multiplicities: {states}\n"
        if charge is not None:
            formatted += f"⚡ Charge: {charge:+d}\n"
        if multiplicity is not None:
            formatted += f"🔬 Default Multiplicity: {multiplicity}\n"
        formatted += f"⚙️ Mode: {mode_lower.title()}\n"
        
        # Show auto-analysis results if used
        if analysis_results and auto_analyze:
            formatted += f"\n🤖 **Auto-Analysis Applied:**\n"
            formatted += f"   {analysis_results['explanation']}\n"
            formatted += f"   Confidence: {analysis_results['confidence'].title()}\n"
        
        formatted += f"\n💡 Use rowan_workflow_management tools to check progress and retrieve results\n"
        return formatted


# Tautomers
@mcp.tool()
def rowan_tautomers(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Enumerate and rank tautomers by stability.
    
    Finds all possible tautomeric forms and ranks them by relative energy:
    - Prototropic tautomers (keto-enol, etc.)
    - Relative populations at room temperature
    - Dominant tautomeric forms
    
    Use this for: Drug design, understanding protonation states, reaction mechanisms
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Tautomer enumeration and ranking results
    """
    result = log_rowan_api_call(
        workflow_type="tautomers",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Hydrogen Bond Basicity
@mcp.tool()
def rowan_hydrogen_bond_basicity(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate hydrogen bond acceptor strength.
    
    Quantifies the ability of molecules to accept hydrogen bonds:
    - Important for drug-target interactions
    - Crystal packing predictions
    - Solvent interactions
    
    Use this for: Drug design, crystal engineering, intermolecular interactions
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Hydrogen bond basicity results
    """
    result = log_rowan_api_call(
        workflow_type="hydrogen_bond_basicity",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# IRC - Reaction Coordinate Following
@mcp.tool()
def rowan_irc(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Follow intrinsic reaction coordinates from transition states.
    
    Traces reaction pathways from transition states to reactants and products:
    - Validates transition state connections
    - Maps complete reaction pathways
    - Confirms reaction mechanisms
    
    Use this for: Mechanism validation, reaction pathway mapping, transition state analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string (should be a transition state)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        IRC pathway results
    """
    result = log_rowan_api_call(
        workflow_type="irc",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    return str(result)


# Molecular Dynamics
@mcp.tool()
@log_mcp_call
def rowan_molecular_dynamics(
    name: str,
    molecule: str,
    ensemble: str = "nvt",
    temperature: float = 300.0,
    pressure: Optional[float] = None,
    timestep: float = 1.0,
    num_steps: int = 500,
    save_interval: int = 10,
    initialization: str = "random",
    langevin_thermostat_timescale: float = 100.0,
    berendsen_barostat_timescale: float = 1000.0,
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    constraints: Optional[List[Dict[str, Any]]] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run molecular dynamics simulations with comprehensive control following Rowan's MolecularDynamicsWorkflow.
    
    Performs MD simulations to study molecular dynamics, conformational sampling, 
    and thermal properties using various thermodynamic ensembles. Based on Rowan's
    MolecularDynamicsWorkflow with full parameter control.
    
    **🔬 Simulation Types:**
    - **NVT**: Constant volume and temperature (canonical ensemble)
    - **NPT**: Constant pressure and temperature (isothermal-isobaric)
    - **NVE**: Constant energy and volume (microcanonical)
    
    **⚡ Key Features:**
    - Multiple thermodynamic ensembles (NVT, NPT, NVE)
    - Configurable timestep and trajectory length
    - Temperature and pressure control with thermostat/barostat settings
    - Various initialization methods
    - Constraint support for bond lengths/angles
    - Smart engine/method selection with compatibility validation
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name
        ensemble: Thermodynamic ensemble ("nvt", "npt", "nve") (default: "nvt")
        temperature: Temperature in Kelvin (default: 300.0 K)
        pressure: Pressure in atm (required for NPT, ignored for NVT/NVE)
        timestep: Integration timestep in femtoseconds (default: 1.0 fs)
        num_steps: Number of MD steps to run (default: 500)
        save_interval: Save trajectory every N steps (default: 10)
        initialization: Initial velocities ("random", "quasiclassical", "read") (default: "random")
        langevin_thermostat_timescale: Thermostat coupling timescale in fs (default: 100.0)
        berendsen_barostat_timescale: Barostat coupling timescale in fs (default: 1000.0)
        method: QM method for forces (default: None, auto-selected based on engine)
        basis_set: Basis set for QM calculations (default: None, auto-selected based on engine)
        engine: Computational engine ("xtb", "aimnet2", "psi4", etc.) (default: "xtb" for speed)
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1)
        constraints: List of geometric constraints during MD
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Molecular dynamics trajectory with Frame objects containing energies, temperatures, and structures
    """
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Validate ensemble and parameters
    ensemble_lower = ensemble.lower()
    valid_ensembles = ["nvt", "npt", "nve"]
    if ensemble_lower not in valid_ensembles:
        return f"❌ Error: ensemble must be one of {valid_ensembles}. Got: '{ensemble}'"
    
    # Validate ensemble-specific requirements (following MolecularDynamicsSettings validation)
    if ensemble_lower == "nvt" and temperature <= 0:
        return f"❌ Error: NVT ensemble must have a positive temperature defined. Got: {temperature}"
    elif ensemble_lower == "npt":
        if temperature <= 0:
            return f"❌ Error: NPT ensemble must have a positive temperature defined. Got: {temperature}"
        if pressure is None or pressure <= 0:
            return f"❌ Error: NPT ensemble must have a positive pressure defined. Got: {pressure}"
    elif ensemble_lower == "nve":
        # NVE doesn't require temperature/pressure validation (energy conserving)
        pass
    
    # Validate simulation parameters (following PositiveFloat/PositiveInt validation)
    if timestep <= 0:
        return f"❌ Error: timestep must be positive. Got: {timestep}"
    
    if num_steps <= 0:
        return f"❌ Error: num_steps must be positive. Got: {num_steps}"
    
    if save_interval <= 0 or save_interval > num_steps:
        return f"❌ Error: save_interval must be positive and ≤ num_steps. Got: {save_interval} (num_steps: {num_steps})"
    
    if langevin_thermostat_timescale <= 0:
        return f"❌ Error: langevin_thermostat_timescale must be positive. Got: {langevin_thermostat_timescale}"
    
    if berendsen_barostat_timescale <= 0:
        return f"❌ Error: berendsen_barostat_timescale must be positive. Got: {berendsen_barostat_timescale}"
    
    # Validate initialization method
    initialization_lower = initialization.lower()
    valid_init = ["random", "quasiclassical", "read"]
    if initialization_lower not in valid_init:
        return f"❌ Error: initialization must be one of {valid_init}. Got: '{initialization}'"
    
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
        "constraints": constraints or []
    }
    
    # Add pressure for NPT ensemble
    if ensemble_lower == "npt":
        md_settings["pressure"] = pressure
    
    # Build calculation settings for forces
    calc_settings = {
        "charge": charge,
        "multiplicity": multiplicity
    }
    
    # For MD simulations, default to fast methods if none specified
    # Smart engine/method selection to avoid incompatibilities
    actual_engine = engine
    
    if not engine and not method:
        # Default to xTB for fast MD simulations
        actual_engine = "xtb"
        calc_settings["engine"] = "xtb"
        # Don't set method - let xTB use its default (gfn2-xtb)
        logger.info(f"🚀 No engine/method specified, defaulting to xTB engine for fast MD forces")
    elif engine and not method:
        # Engine specified but no method - let engine choose its default
        calc_settings["engine"] = engine.lower()
        actual_engine = engine
        logger.info(f"🔧 Engine '{engine}' specified, using engine's default method")
    elif method and not engine:
        # Method specified but no engine - choose appropriate engine
        method_lower = method.lower()
        calc_settings["method"] = method_lower
        
        # Determine appropriate engine based on method
        if method_lower in ["gfn1-xtb", "gfn1_xtb", "gfn2-xtb", "gfn2_xtb"]:
            actual_engine = "xtb"
            calc_settings["engine"] = "xtb"
            logger.info(f"🚀 xTB method '{method}' specified, using xTB engine")
        elif method_lower in ["hf", "b3lyp", "pbe", "m06-2x", "mp2", "ccsd"]:
            actual_engine = "psi4"
            calc_settings["engine"] = "psi4"
            logger.info(f"🔬 Quantum method '{method}' specified, using Psi4 engine")
        else:
            # Unknown method - default to Psi4 and let it handle validation
            actual_engine = "psi4"
            calc_settings["engine"] = "psi4"
            logger.warning(f"⚠️ Unknown method '{method}', defaulting to Psi4 engine")
    else:
        # Both engine and method specified - use as provided
        calc_settings["method"] = method.lower()
        calc_settings["engine"] = engine.lower()
        actual_engine = engine
        logger.info(f"🎯 Both engine '{engine}' and method '{method}' specified")
        
        # Validate compatibility
        method_lower = method.lower()
        engine_lower = engine.lower()
        if engine_lower == "xtb" and method_lower not in ["gfn1-xtb", "gfn1_xtb", "gfn2-xtb", "gfn2_xtb"]:
            logger.warning(f"⚠️ Method '{method}' may not be compatible with xTB engine")
        elif engine_lower == "psi4" and method_lower in ["gfn1-xtb", "gfn1_xtb", "gfn2-xtb", "gfn2_xtb"]:
            logger.warning(f"⚠️ xTB method '{method}' may not be compatible with Psi4 engine")
    
    # Add basis set if specified
    if basis_set:
        calc_settings["basis_set"] = basis_set.lower()
            
    # If using Psi4 (explicitly or via method), ensure we have a basis set
    specified_engine = actual_engine.lower() if actual_engine else None
    if specified_engine == "psi4" and not basis_set:
        # Default basis set for Psi4/DFT methods
        calc_settings["basis_set"] = "def2-svp"
        logger.info(f"🔬 Using Psi4 engine, defaulting to def2-SVP basis set")
    
    # Log the MD parameters
    logger.info(f"🔬 Molecular Dynamics Debug:")
    logger.info(f"   Name: {name}")
    logger.info(f"   Input: {molecule}")
    logger.info(f"   Using SMILES: {canonical_smiles}")
    logger.info(f"   Ensemble: {ensemble_lower.upper()}")
    logger.info(f"   Temperature: {temperature} K")
    if ensemble_lower == "npt":
        logger.info(f"   Pressure: {pressure} atm")
    logger.info(f"   Timestep: {timestep} fs")
    logger.info(f"   Steps: {num_steps} ({num_steps * timestep / 1000:.1f} ps total)")
    logger.info(f"   Save interval: every {save_interval} steps")
    logger.info(f"   Initialization: {initialization_lower}")
    logger.info(f"   Thermostat timescale: {langevin_thermostat_timescale} fs")
    logger.info(f"   Barostat timescale: {berendsen_barostat_timescale} fs")
    
    # Build parameters for Rowan API
    md_params = {
        "name": name,
        "molecule": canonical_smiles,
        "settings": md_settings,
        "calc_settings": calc_settings,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add calc_engine - use actual_engine which includes defaults
    if actual_engine:
        md_params["calc_engine"] = actual_engine.lower()
    
    result = log_rowan_api_call(
        workflow_type="molecular_dynamics",
        **md_params
    )
    
    if blocking:
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f"✅ Molecular dynamics simulation for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f"❌ Molecular dynamics simulation for '{name}' failed!\n\n"
        else:
            formatted = f"⚠️ Molecular dynamics simulation for '{name}' finished with status {status}\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status}\n"
        
        # Simulation settings summary
        formatted += f"\n⚙️ **Simulation Settings:**\n"
        formatted += f"   Ensemble: {ensemble_lower.upper()}\n"
        formatted += f"   Temperature: {temperature} K\n"
        if ensemble_lower == "npt":
            formatted += f"   Pressure: {pressure} atm\n"
        formatted += f"   Timestep: {timestep} fs\n"
        formatted += f"   Total Steps: {num_steps:,}\n"
        formatted += f"   Simulation Time: {num_steps * timestep / 1000:.1f} ps\n"
        formatted += f"   Save Frequency: Every {save_interval} steps\n"
        formatted += f"   Initialization: {initialization_lower.title()}\n"
        formatted += f"   Thermostat Timescale: {langevin_thermostat_timescale} fs\n"
        formatted += f"   Barostat Timescale: {berendsen_barostat_timescale} fs\n"
        
        # Computational settings
        formatted += f"\n🔬 **Computational Settings:**\n"
        actual_engine = calc_settings.get("engine", "default")
        if method:
            formatted += f"   Method: {method.upper()}\n"
        if calc_settings.get("basis_set"):
            formatted += f"   Basis Set: {calc_settings['basis_set']}\n"
        formatted += f"   Engine: {actual_engine.upper()}\n"
        formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
        if constraints:
            formatted += f"   Constraints: {len(constraints)} applied\n"
        
        # Try to extract MD results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Check for trajectory frames
            if 'frames' in data and isinstance(data['frames'], list):
                frames = data['frames']
                num_frames = len(frames)
                formatted += f"\n📊 **Trajectory Results:**\n"
                formatted += f"   Total Frames: {num_frames}\n"
                
                if frames:
                    # Analyze trajectory
                    first_frame = frames[0]
                    last_frame = frames[-1]
                    
                    if 'temperature' in first_frame and 'temperature' in last_frame:
                        avg_temp = sum(f.get('temperature', 0) for f in frames) / num_frames
                        formatted += f"   Average Temperature: {avg_temp:.1f} K\n"
                    
                    if 'potential_energy' in first_frame and 'potential_energy' in last_frame:
                        energies = [f.get('potential_energy', 0) for f in frames]
                        avg_energy = sum(energies) / len(energies)
                        min_energy = min(energies)
                        max_energy = max(energies)
                        formatted += f"   Average Potential Energy: {avg_energy:.2f} kcal/mol\n"
                        formatted += f"   Energy Range: {min_energy:.2f} to {max_energy:.2f} kcal/mol\n"
                    
                    if ensemble_lower == "npt" and 'volume' in first_frame:
                        volumes = [f.get('volume', 0) for f in frames]
                        avg_volume = sum(volumes) / len(volumes)
                        formatted += f"   Average Volume: {avg_volume:.2f} Ų\n"
        
        # Status-specific guidance
        formatted += f"\n💡 **Next Steps:**\n"
        if status == 2:  # Completed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for full trajectory\n"
            formatted += f"• Trajectory contains {num_steps//save_interval} frames over {num_steps * timestep / 1000:.1f} ps\n"
            formatted += f"• Analyze conformational flexibility and thermal motion\n"
            formatted += f"• Consider longer simulations for better sampling\n"
        elif status == 3:  # Failed
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            formatted += f"• **Troubleshooting:**\n"
            formatted += f"  - Try smaller timestep (current: {timestep} fs → try 0.5 fs)\n"
            formatted += f"  - Reduce number of steps for testing (current: {num_steps})\n"
            formatted += f"  - Check if molecule SMILES is valid\n"
            formatted += f"  - For NPT: verify pressure is reasonable ({pressure} atm)\n"
            formatted += f"  - Try different computational engine: engine='xtb' (fastest) or engine='aimnet2'\n"
            formatted += f"  - If using Psi4: ensure basis_set is specified (e.g., basis_set='def2-svp')\n"
            formatted += f"  - Try different initialization method\n"
        elif status in [0, 1, 5]:  # Running
            formatted += f"• Check progress: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
            formatted += f"• MD simulation with {num_steps:,} steps may take 10-60 minutes\n"
            formatted += f"• Each step requires force calculation on the molecule\n"
            formatted += f"• {ensemble_lower.upper()} ensemble with {timestep} fs timestep\n"
        elif status == 4:  # Stopped
            formatted += f"• Check why stopped: rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
            formatted += f"• You can restart with same or modified parameters\n"
        else:  # Unknown
            formatted += f"• Check status: rowan_workflow_management(action='status', workflow_uuid='{result.get('uuid')}')\n"
        
        # Add examples and guidance
        formatted += f"\n📚 **MD Examples:**\n"
        formatted += f"• **Basic NVT**: rowan_molecular_dynamics('glucose_md', 'glucose', temperature=300)\n"
        formatted += f"• **NPT simulation**: rowan_molecular_dynamics('drug_npt', 'SMILES', ensemble='npt', pressure=1.0)\n"
        formatted += f"• **Long trajectory**: rowan_molecular_dynamics('protein_md', 'SMILES', num_steps=5000, timestep=0.5)\n"
        formatted += f"• **High-accuracy**: rowan_molecular_dynamics('accurate', 'SMILES', engine='aimnet2', num_steps=1000)\n"
        formatted += f"• **DFT forces**: rowan_molecular_dynamics('dft_md', 'SMILES', engine='psi4', method='b3lyp', basis_set='def2-svp')\n\n"
        
        formatted += f"⚗️ **Ensemble Guide:**\n"
        formatted += f"• **NVT**: Fixed volume, controlled temperature (most common)\n"
        formatted += f"• **NPT**: Fixed pressure, controlled temperature (realistic conditions)\n"
        formatted += f"• **NVE**: Energy conserving (microcanonical, for testing)\n\n"
        
        formatted += f"🔬 **Engine Guide:**\n"
        formatted += f"• **xTB**: Fastest, good for large systems and long MD (default)\n"
        formatted += f"• **AIMNet2**: Neural network, balance of speed and accuracy\n"
        formatted += f"• **Psi4**: Quantum chemistry, highest accuracy but slowest\n\n"
        
        formatted += f"🕐 **Timescale Guide:**\n"
        formatted += f"• **Timestep**: 0.5-2.0 fs (smaller = more stable, slower)\n"
        formatted += f"• **Short MD**: 100-500 steps (0.1-1 ps) for quick sampling\n"
        formatted += f"• **Medium MD**: 1000-5000 steps (1-10 ps) for conformations\n"
        formatted += f"• **Long MD**: 10000+ steps (10+ ps) for rare events\n"
        
        return formatted
    else:
        formatted = f"🚀 Molecular dynamics simulation for '{name}' submitted!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 SMILES: {canonical_smiles}\n"
        formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Submitted')}\n"
        formatted += f"⚙️ Ensemble: {ensemble_lower.upper()}\n"
        formatted += f"🌡️ Temperature: {temperature} K\n"
        if ensemble_lower == "npt":
            formatted += f"🔘 Pressure: {pressure} atm\n"
        formatted += f"⏱️ Steps: {num_steps:,} ({num_steps * timestep / 1000:.1f} ps)\n"
        formatted += f"\n💡 Use rowan_workflow_management tools to check progress and retrieve trajectory\n"
        return formatted


@mcp.tool()
@log_mcp_call
def rowan_pka(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None
) -> str:
    """Calculate pKa values for molecules.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: UUID of folder to organize calculation in
    
    Returns:
        pKa calculation results
    """
    result = log_rowan_api_call(
        workflow_type="pka",
        name=name,
        molecule=molecule,
        folder_uuid=folder_uuid
    )
    
    pka_value = result.get("object_data", {}).get("strongest_acid")
    
    formatted = f"✅ pKa calculation for '{name}' completed!\n\n"
    formatted += f"🧪 Molecule: {molecule}\n"
    formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
    
    if pka_value is not None:
        formatted += f"🧬 Strongest Acid pKa: {pka_value:.2f}\n"
    else:
        formatted += "⚠️ pKa result not yet available\n"
        
    return formatted


@mcp.tool()
@log_mcp_call
def rowan_conformers(
    name: str,
    molecule: str,
    max_conformers: int = 10,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    max_wait_time: int = 120,
    ping_interval: int = 5
) -> str:
    """Generate and optimize molecular conformers.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        max_conformers: Maximum number of conformers to generate
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        max_wait_time: Maximum time to wait in seconds (default: 120 = 2 minutes)
        ping_interval: How often to check status in seconds (default: 5)
    
    Returns:
        Conformer search results (actual results if blocking=True)
    """
    settings = {"max_conformers": max_conformers}
    
    # Log the expected wait time
    if blocking:
        logger.info(f"🕐 Conformer search will wait up to {max_wait_time} seconds ({max_wait_time//60:.1f} minutes)")
        logger.info(f"🔄 Checking progress every {ping_interval} seconds")
    
    result = log_rowan_api_call(
        workflow_type="conformer_search",
        name=name,
        molecule=molecule,
        settings=settings,
        folder_uuid=folder_uuid,
        blocking=blocking,
        ping_interval=ping_interval
    )
    
    # Format results based on whether we waited or not
    if blocking:
        # We waited for completion - format actual results
        status = result.get('status', result.get('object_status', 'Unknown'))
        
        if status == 2:  # Completed successfully
            formatted = f"✅ Conformer search for '{name}' completed successfully!\n\n"
        elif status == 3:  # Failed
            formatted = f"❌ Conformer search for '{name}' failed!\n\n"
        else:
            formatted = f"⚠️ Conformer search for '{name}' finished with status {status}\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status}\n"
        formatted += f"🔄 Max Conformers: {max_conformers}\n"
        
        # Try to extract actual results
        if isinstance(result, dict) and 'object_data' in result and result['object_data']:
            data = result['object_data']
            
            # Count conformers found
            if 'conformers' in data:
                conformer_count = len(data['conformers']) if isinstance(data['conformers'], list) else data.get('num_conformers', 'Unknown')
                formatted += f"🎯 Generated Conformers: {conformer_count}\n"
            
            # Energy information
            if 'energies' in data and isinstance(data['energies'], list) and data['energies']:
                energies = data['energies']
                min_energy = min(energies)
                max_energy = max(energies)
                energy_range = max_energy - min_energy
                formatted += f"⚡ Energy Range: {min_energy:.3f} to {max_energy:.3f} kcal/mol (Δ={energy_range:.3f})\n"
                formatted += f"📊 Lowest Energy Conformer: {min_energy:.3f} kcal/mol\n"
            
            # Additional properties if available
            if 'properties' in data:
                props = data['properties']
                formatted += f"🔬 Properties calculated: {', '.join(props.keys())}\n"
        
        # Guidance based on results
        if status == 2:
            formatted += f"\n💡 **Results Available:**\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for detailed data\n"
            formatted += f"• Conformers are ranked by energy (lowest = most stable)\n"
        elif status == 3:
            formatted += f"\n💡 **Troubleshooting:**\n"
            formatted += f"• Try reducing max_conformers (currently {max_conformers})\n"
            formatted += f"• Check if molecule SMILES is valid\n"
            formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
    else:
        # Non-blocking mode - just submission confirmation
        formatted = f"🚀 Conformer search for '{name}' submitted!\n\n"
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {result.get('status', 'Submitted')}\n"
        formatted += f"🔄 Max Conformers: {max_conformers}\n"
        formatted += f"\n💡 Use rowan_workflow_management tools to check progress and retrieve results\n"
    
    return formatted


@mcp.tool()
def rowan_folder_management(
    action: str,
    folder_uuid: Optional[str] = None,
    name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    name_contains: Optional[str] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """Unified folder management tool for all folder operations.
    
    **Available Actions:**
    - **create**: Create a new folder (requires: name, optional: parent_uuid, notes, starred, public)
    - **retrieve**: Get folder details (requires: folder_uuid)
    - **update**: Update folder properties (requires: folder_uuid, optional: name, parent_uuid, notes, starred, public)
    - **delete**: Delete a folder (requires: folder_uuid)
    - **list**: List folders with filters (optional: name_contains, parent_uuid, starred, public, page, size)
    
    Args:
        action: Action to perform ('create', 'retrieve', 'update', 'delete', 'list')
        folder_uuid: UUID of the folder (required for retrieve, update, delete)
        name: Folder name (required for create, optional for update)
        parent_uuid: Parent folder UUID (optional for create/update, if not provided creates in root)
        notes: Folder notes (optional for create/update)
        starred: Star the folder (optional for create/update)
        public: Make folder public (optional for create/update)
        name_contains: Filter by name containing text (optional for list)
        page: Page number for pagination (default: 1, for list)
        size: Results per page (default: 50, for list)
    
    Returns:
        Results of the folder operation
    """
    
    action = action.lower()
    
    try:
        if action == "create":
            if not name:
                return "❌ Error: 'name' is required for creating a folder"
            
            folder = rowan.Folder.create(
                name=name,
                parent_uuid=parent_uuid,  # Required by API
                notes=notes or "",
                starred=starred or False,
                public=public or False
            )
            
            formatted = f"✅ Folder '{name}' created successfully!\n\n"
            formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"📝 Notes: {notes or 'None'}\n"
            if parent_uuid:
                formatted += f"📂 Parent: {parent_uuid}\n"
            return formatted
            
        elif action == "retrieve":
            if not folder_uuid:
                return "❌ Error: 'folder_uuid' is required for retrieving a folder"
            
            folder = rowan.Folder.retrieve(uuid=folder_uuid)
            
            formatted = f"📁 Folder Details:\n\n"
            formatted += f"📝 Name: {folder.get('name', 'N/A')}\n"
            formatted += f"🆔 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"📂 Parent: {folder.get('parent_uuid', 'Root')}\n"
            formatted += f"⭐ Starred: {'Yes' if folder.get('starred') else 'No'}\n"
            formatted += f"🌐 Public: {'Yes' if folder.get('public') else 'No'}\n"
            formatted += f"📅 Created: {folder.get('created_at', 'N/A')}\n"
            formatted += f"📝 Notes: {folder.get('notes', 'None')}\n"
            return formatted
            
        elif action == "update":
            if not folder_uuid:
                return "❌ Error: 'folder_uuid' is required for updating a folder"
            
            # Build update parameters
            update_params = {"uuid": folder_uuid}
            if name is not None:
                update_params["name"] = name
            if parent_uuid is not None:
                update_params["parent_uuid"] = parent_uuid
            if notes is not None:
                update_params["notes"] = notes
            if starred is not None:
                update_params["starred"] = starred
            if public is not None:
                update_params["public"] = public
                
            folder = rowan.Folder.update(**update_params)
            
            formatted = f"✅ Folder '{folder.get('name')}' updated successfully!\n\n"
            formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"📝 Name: {folder.get('name', 'N/A')}\n"
            formatted += f"⭐ Starred: {'Yes' if folder.get('starred') else 'No'}\n"
            formatted += f"🌐 Public: {'Yes' if folder.get('public') else 'No'}\n"
            return formatted
            
        elif action == "delete":
            if not folder_uuid:
                return "❌ Error: 'folder_uuid' is required for deleting a folder"
            
            rowan.Folder.delete(uuid=folder_uuid)
            return f"✅ Folder {folder_uuid} deleted successfully."
            
        elif action == "list":
            # Build filter parameters
            filter_params = {"page": page, "size": size}
            if name_contains is not None:
                filter_params["name_contains"] = name_contains
            if parent_uuid is not None:
                filter_params["parent_uuid"] = parent_uuid
            if starred is not None:
                filter_params["starred"] = starred
            if public is not None:
                filter_params["public"] = public
                
            result = rowan.Folder.list(**filter_params)
            folders = result.get("folders", [])
            num_pages = result.get("num_pages", 1)
            
            if not folders:
                return "📁 No folders found matching criteria."
            
            formatted = f"📁 Found {len(folders)} folders (Page {page}/{num_pages}):\n\n"
            for folder in folders:
                starred_icon = "⭐" if folder.get('starred') else "📁"
                public_icon = "🌐" if folder.get('public') else "🔒"
                formatted += f"{starred_icon} {folder.get('name', 'Unnamed')} {public_icon}\n"
                formatted += f"   UUID: {folder.get('uuid', 'N/A')}\n"
                if folder.get('notes'):
                    formatted += f"   Notes: {folder.get('notes')}\n"
                formatted += "\n"
            
            return formatted
            
        else:
            return f"❌ Error: Unknown action '{action}'. Available actions: create, retrieve, update, delete, list"
            
    except Exception as e:
        return f"❌ Error in folder {action}: {str(e)}"


@mcp.tool()
def rowan_workflow_management(
    action: str,
    workflow_uuid: Optional[str] = None,
    name: Optional[str] = None,
    workflow_type: Optional[str] = None,
    initial_molecule: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    notes: Optional[str] = None,
    starred: Optional[bool] = None,
    public: Optional[bool] = None,
    email_when_complete: Optional[bool] = None,
    workflow_data: Optional[Dict[str, Any]] = None,
    name_contains: Optional[str] = None,
    object_status: Optional[int] = None,
    object_type: Optional[str] = None,
    page: int = 1,
    size: int = 50
) -> str:
    """Unified workflow management tool for all workflow operations.
    
    **Available Actions:**
    - **create**: Create a new workflow (requires: name, workflow_type, initial_molecule)
    - **retrieve**: Get workflow details (requires: workflow_uuid)
    - **update**: Update workflow properties (requires: workflow_uuid, optional: name, parent_uuid, notes, starred, public, email_when_complete)
    - **stop**: Stop a running workflow (requires: workflow_uuid)
    - **status**: Check workflow status (requires: workflow_uuid)
    - **is_finished**: Check if workflow is finished (requires: workflow_uuid)
    - **delete**: Delete a workflow (requires: workflow_uuid)
    - **list**: List workflows with filters (optional: name_contains, parent_uuid, starred, public, object_status, object_type, page, size)
    
    Args:
        action: Action to perform ('create', 'retrieve', 'update', 'stop', 'status', 'is_finished', 'delete', 'list')
        workflow_uuid: UUID of the workflow (required for retrieve, update, stop, status, is_finished, delete)
        name: Workflow name (required for create, optional for update)
        workflow_type: Type of workflow (required for create)
        initial_molecule: Initial molecule SMILES (required for create)
        parent_uuid: Parent folder UUID (optional for create/update)
        notes: Workflow notes (optional for create/update)
        starred: Star the workflow (optional for create/update)
        public: Make workflow public (optional for create/update)
        email_when_complete: Email when complete (optional for create/update)
        workflow_data: Additional workflow data (optional for create)
        name_contains: Filter by name containing text (optional for list)
        object_status: Filter by status (0=queued, 1=running, 2=completed, 3=failed, 4=stopped, optional for list)
        object_type: Filter by workflow type (optional for list)
        page: Page number for pagination (default: 1, for list)
        size: Results per page (default: 50, for list)
    
    Returns:
        Results of the workflow operation
    """
    
    action = action.lower()
    
    try:
        if action == "create":
            if not all([name, workflow_type, initial_molecule]):
                return "❌ Error: 'name', 'workflow_type', and 'initial_molecule' are required for creating a workflow"
            
            # Validate workflow type
            VALID_WORKFLOWS = {
                "admet", "basic_calculation", "bde", "conformer_search", "descriptors", 
                "docking", "electronic_properties", "fukui", "hydrogen_bond_basicity", 
                "irc", "molecular_dynamics", "multistage_opt", "pka", "redox_potential", 
                "scan", "solubility", "spin_states", "tautomers"
            }
            
            if workflow_type not in VALID_WORKFLOWS:
                error_msg = f"❌ Invalid workflow_type '{workflow_type}'.\n\n"
                error_msg += "🔧 **Available Rowan Workflow Types:**\n"
                error_msg += f"{', '.join(sorted(VALID_WORKFLOWS))}"
                return error_msg
            
            workflow = rowan.Workflow.create(
                name=name,
                workflow_type=workflow_type,
                initial_molecule=initial_molecule,
                parent_uuid=parent_uuid,
                notes=notes or "",
                starred=starred or False,
                public=public or False,
                email_when_complete=email_when_complete or False,
                workflow_data=workflow_data or {}
            )
            
            formatted = f"✅ Workflow '{name}' created successfully!\n\n"
            formatted += f"🔬 UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"⚗️ Type: {workflow_type}\n"
            formatted += f"📊 Status: {workflow.get('object_status', 'Unknown')}\n"
            formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
            return formatted
            
        elif action == "retrieve":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for retrieving a workflow"
            
            workflow = rowan.Workflow.retrieve(uuid=workflow_uuid)
            
            formatted = f"🔬 Workflow Details:\n\n"
            formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
            formatted += f"🆔 UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"⚗️ Type: {workflow.get('object_type', 'N/A')}\n"
            formatted += f"📊 Status: {workflow.get('object_status', 'Unknown')}\n"
            formatted += f"📂 Parent: {workflow.get('parent_uuid', 'Root')}\n"
            formatted += f"⭐ Starred: {'Yes' if workflow.get('starred') else 'No'}\n"
            formatted += f"🌐 Public: {'Yes' if workflow.get('public') else 'No'}\n"
            formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
            formatted += f"⏱️ Elapsed: {workflow.get('elapsed', 0):.2f}s\n"
            formatted += f"💰 Credits: {workflow.get('credits_charged', 0)}\n"
            formatted += f"📝 Notes: {workflow.get('notes', 'None')}\n"
            return formatted
            
        elif action == "update":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for updating a workflow"
            
            # Build update parameters
            update_params = {"uuid": workflow_uuid}
            if name is not None:
                update_params["name"] = name
            if parent_uuid is not None:
                update_params["parent_uuid"] = parent_uuid
            if notes is not None:
                update_params["notes"] = notes
            if starred is not None:
                update_params["starred"] = starred
            if public is not None:
                update_params["public"] = public
            if email_when_complete is not None:
                update_params["email_when_complete"] = email_when_complete
                
            workflow = rowan.Workflow.update(**update_params)
            
            formatted = f"✅ Workflow '{workflow.get('name')}' updated successfully!\n\n"
            formatted += f"🔬 UUID: {workflow.get('uuid', 'N/A')}\n"
            formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
            formatted += f"⭐ Starred: {'Yes' if workflow.get('starred') else 'No'}\n"
            formatted += f"🌐 Public: {'Yes' if workflow.get('public') else 'No'}\n"
            return formatted
            
        elif action == "stop":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for stopping a workflow"
            
            rowan.Workflow.stop(uuid=workflow_uuid)
            return f"⏹️ Workflow {workflow_uuid} stopped successfully."
            
        elif action == "status":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for checking workflow status"
            
            status = rowan.Workflow.status(uuid=workflow_uuid)
            
            status_names = {
                0: "Queued",
                1: "Running", 
                2: "Completed",
                3: "Failed",
                4: "Stopped",
                5: "Awaiting Queue"
            }
            
            status_name = status_names.get(status, f"Unknown ({status})")
            
            formatted = f"📊 Workflow Status:\n\n"
            formatted += f"🆔 UUID: {workflow_uuid}\n"
            formatted += f"📈 Status: {status_name} ({status})\n"
            return formatted
            
        elif action == "is_finished":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for checking if workflow is finished"
            
            is_finished = rowan.Workflow.is_finished(uuid=workflow_uuid)
            
            formatted = f"✅ Workflow Status:\n\n"
            formatted += f"🆔 UUID: {workflow_uuid}\n"
            formatted += f"🏁 Finished: {'Yes' if is_finished else 'No'}\n"
            return formatted
            
        elif action == "delete":
            if not workflow_uuid:
                return "❌ Error: 'workflow_uuid' is required for deleting a workflow"
            
            rowan.Workflow.delete(uuid=workflow_uuid)
            return f"🗑️ Workflow {workflow_uuid} deleted successfully."
            
        elif action == "list":
            # Build filter parameters
            filter_params = {"page": page, "size": size}
            if name_contains is not None:
                filter_params["name_contains"] = name_contains
            if parent_uuid is not None:
                filter_params["parent_uuid"] = parent_uuid
            if starred is not None:
                filter_params["starred"] = starred
            if public is not None:
                filter_params["public"] = public
            if object_status is not None:
                filter_params["object_status"] = object_status
            if object_type is not None:
                filter_params["object_type"] = object_type
                
            result = rowan.Workflow.list(**filter_params)
            workflows = result.get("workflows", [])
            num_pages = result.get("num_pages", 1)
            
            if not workflows:
                return "🔬 No workflows found matching criteria."
            
            status_names = {0: "⏳", 1: "🔄", 2: "✅", 3: "❌", 4: "⏹️", 5: "⏸️"}
            
            formatted = f"🔬 Found {len(workflows)} workflows (Page {page}/{num_pages}):\n\n"
            for workflow in workflows:
                status_icon = status_names.get(workflow.get('object_status'), "❓")
                starred_icon = "⭐" if workflow.get('starred') else ""
                public_icon = "🌐" if workflow.get('public') else ""
                
                formatted += f"{status_icon} {workflow.get('name', 'Unnamed')} {starred_icon}{public_icon}\n"
                formatted += f"   Type: {workflow.get('object_type', 'N/A')}\n"
                formatted += f"   UUID: {workflow.get('uuid', 'N/A')}\n"
                formatted += f"   Created: {workflow.get('created_at', 'N/A')}\n"
                if workflow.get('elapsed'):
                    formatted += f"   Duration: {workflow.get('elapsed', 0):.2f}s\n"
                formatted += "\n"
            
            return formatted
            
        else:
            return f"❌ Error: Unknown action '{action}'. Available actions: create, retrieve, update, stop, status, is_finished, delete, list"
            
    except Exception as e:
        return f"❌ Error in workflow {action}: {str(e)}"


@mcp.tool()
def rowan_calculation_retrieve(calculation_uuid: str) -> str:
    """Retrieve details of a specific calculation.
    
    Args:
        calculation_uuid: UUID of the calculation to retrieve
    
    Returns:
        Calculation details
    """
    try:
        calculation = rowan.Calculation.retrieve(uuid=calculation_uuid)
        
        formatted = f"⚙️ Calculation Details:\n\n"
        formatted += f"📝 Name: {calculation.get('name', 'N/A')}\n"
        formatted += f"🆔 UUID: {calculation_uuid}\n"
        formatted += f"📊 Status: {calculation.get('status', 'Unknown')}\n"
        formatted += f"⏱️ Elapsed: {calculation.get('elapsed', 0):.3f}s\n"
        
        settings = calculation.get('settings', {})
        if settings:
            formatted += f"\n⚙️ Settings:\n"
            formatted += f"   Method: {settings.get('method', 'N/A')}\n"
            if settings.get('basis_set'):
                formatted += f"   Basis Set: {settings.get('basis_set')}\n"
            if settings.get('tasks'):
                formatted += f"   Tasks: {', '.join(settings.get('tasks', []))}\n"
        
        molecules = calculation.get('molecules', [])
        if molecules:
            formatted += f"\n🧪 Molecules: {len(molecules)} structure(s)\n"
        
        return formatted
        
    except Exception as e:
        return f"❌ Error retrieving calculation: {str(e)}"


@mcp.tool()
def rowan_docking(
    name: str,
    protein: str,
    ligand: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5,
    additional_params: Optional[Dict[str, Any]] = None
) -> str:
    """Run protein-ligand docking calculations.
    
    Args:
        name: Name for the docking calculation
        protein: Protein specification (PDB ID like '1ABC', PDB content, or protein sequence)
        ligand: Ligand SMILES string
        folder_uuid: UUID of folder to organize calculation in
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
        additional_params: Additional docking-specific parameters
    
    Returns:
        Formatted docking results
    """
    try:
        # For docking workflows in Rowan, we need to check the exact format expected
        # Let's try different approaches based on what the API might accept
        
        approaches = []
        
        # Approach 1: Try PDB ID format (4-character codes)
        if len(protein) == 4 and protein.isalnum():
            approaches.append(("PDB ID", protein))
        
        # Approach 2: Try just the ligand SMILES (for small molecule only calculations)
        approaches.append(("Ligand only", ligand))
        
        # Approach 3: Try a structured format if docking supports it
        if len(protein) > 4:
            approaches.append(("Combined format", f"protein:{protein}|ligand:{ligand}"))
        
        last_error = None
        
        for approach_name, molecule_input in approaches:
            try:
                # Prepare kwargs for rowan.compute
                compute_kwargs = {
                    "name": f"{name} ({approach_name})",
                    "molecule": molecule_input,
                    "workflow_type": "docking",
                    "blocking": blocking,
                    "ping_interval": ping_interval
                }
                
                if folder_uuid:
                    compute_kwargs["folder_uuid"] = folder_uuid
                if additional_params:
                    compute_kwargs.update(additional_params)
                    
                result = rowan.compute(**compute_kwargs)
                
                # Format result for display
                formatted = f"✅ Docking calculation '{name}' completed successfully!\n\n"
                formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
                formatted += f"📊 Status: {result.get('status', 'Unknown')}\n"
                formatted += f"🧬 Approach: {approach_name}\n"
                formatted += f"🧬 Protein: {protein[:50]}{'...' if len(protein) > 50 else ''}\n"
                formatted += f"💊 Ligand: {ligand}\n"
                
                docking_data = result.get("object_data", {})
                if "binding_affinity" in docking_data:
                    formatted += f"🔗 Binding Affinity: {docking_data['binding_affinity']:.2f} kcal/mol\n"
                if "poses" in docking_data:
                    formatted += f"📐 Poses Generated: {len(docking_data['poses'])}\n"
                
                return formatted
                
            except Exception as e:
                last_error = e
                continue
        
        # If all approaches failed, provide helpful guidance
        error_msg = f"❌ Docking failed with all approaches. Last error: {str(last_error)}\n\n"
        error_msg += "🔧 **Troubleshooting Protein-Ligand Docking:**\n\n"
        error_msg += "**For protein input, try:**\n"
        error_msg += "• PDB ID (4 characters): `1ABC`\n"
        error_msg += "• Direct PDB file content\n\n"
        error_msg += "**For ligand input:**\n"
        error_msg += "• Valid SMILES string like: `CC(C)c1nc(cs1)CN(C)C(=O)N`\n\n"
        error_msg += "**Alternative approaches:**\n"
        error_msg += "• Use `rowan_compute()` with workflow_type='docking' and experiment with different molecule formats\n"
        error_msg += "• Check if your protein needs to be prepared/processed first\n"
        error_msg += "• Consider using PDB IDs from the Protein Data Bank\n\n"
        error_msg += "**Example working formats:**\n"
        error_msg += "• Protein: `1ABC` (PDB ID)\n"
        error_msg += "• Ligand: `CCO` (ethanol SMILES)\n"
        
        return error_msg
        
    except Exception as e:
        return f"❌ Error running docking: {str(e)}"


@mcp.tool()
def rowan_system_management(
    action: str,
    job_uuid: Optional[str] = None,
    log_level: Optional[str] = None
) -> str:
    """Unified system management tool for server utilities and information.
    
    **Available Actions:**
    - **help**: Get list of all available Rowan MCP tools with descriptions
    - **set_log_level**: Set logging level for debugging (requires: log_level)
    - **job_redirect**: Redirect legacy job queries to workflow management (requires: job_uuid)
    
    Args:
        action: Action to perform ('help', 'set_log_level', 'job_redirect')
        job_uuid: UUID of the job (required for job_redirect)
        log_level: Logging level - DEBUG, INFO, WARNING, ERROR (required for set_log_level)
    
    Returns:
        Results of the system operation
    """
    
    action = action.lower()
    
    try:
        if action == "help":
            result = "🔬 **Available Rowan MCP Tools** 🔬\n\n"
            
            result += "✨ **Now with unified management tools!**\n"
            result += "Each tool has tailored documentation and parameters.\n\n"
            
            # Group by common use cases
            result += "**🔬 Quantum Chemistry & Basic Calculations:**\n"
            result += "• `rowan_qc_guide` - Comprehensive quantum chemistry guidance\n"
            result += "• `rowan_quantum_chemistry` - Unified QC tool (smart defaults + full customization)\n"
            result += "• `rowan_electronic_properties` - HOMO/LUMO, orbitals\n"
            result += "• `rowan_multistage_opt` - Multi-level optimization (for geometry)\n\n"
            
            result += "**🧬 Molecular Analysis:**\n"
            result += "• `rowan_conformers` - Find molecular conformations\n"
            result += "• `rowan_tautomers` - Tautomer enumeration\n"
            result += "• `rowan_descriptors` - Molecular descriptors for ML\n\n"
            
            result += "**⚗️ Chemical Properties:**\n"
            result += "• `rowan_pka` - pKa prediction\n"
            result += "• `rowan_redox_potential` - Redox potentials vs SCE\n"
            result += "• `rowan_bde` - Bond dissociation energies\n"
            result += "• `rowan_solubility` - Solubility prediction\n\n"
            
            result += "**🧪 Drug Discovery:**\n"
            result += "• `rowan_admet` - ADME-Tox properties\n"
            result += "• `rowan_docking` - Protein-ligand docking\n\n"
            
            result += "**🔬 Advanced Analysis:**\n"
            result += "• `rowan_scan` - Potential energy surface scans (bond/angle/dihedral)\n"
            result += "• `rowan_fukui` - Reactivity analysis\n"
            result += "• `rowan_spin_states` - Spin state preferences\n"
            result += "• `rowan_irc` - Reaction coordinate following\n"
            result += "• `rowan_molecular_dynamics` - MD simulations\n"
            result += "• `rowan_hydrogen_bond_basicity` - H-bond strength\n\n"
            
            result += "💡 **Usage Guidelines:**\n"
            result += "• For geometry optimization: use `rowan_multistage_opt`\n"
            result += "• For energy calculations: use `rowan_quantum_chemistry` (smart defaults)\n"
            result += "• For custom QC settings: use `rowan_quantum_chemistry` with parameters\n"
            result += "• For conformer search: use `rowan_conformers`\n"
            result += "• For pKa prediction: use `rowan_pka`\n"
            result += "• For electronic structure: use `rowan_electronic_properties`\n"
            result += "• For drug properties: use `rowan_admet`\n"
            result += "• For reaction mechanisms: use `rowan_scan` then `rowan_irc`\n"
            result += "• For potential energy scans: use `rowan_scan` with coordinate specification\n\n"
            
            result += "**🗂️ Management Tools:**\n"
            result += "• `rowan_folder_management` - Unified folder operations (create, retrieve, update, delete, list)\n"
            result += "• `rowan_workflow_management` - Unified workflow operations (create, retrieve, update, stop, status, delete, list)\n"
            result += "• `rowan_system_management` - System utilities (help, set_log_level, job_redirect)\n\n"
            
            result += "📋 **Total Available:** 15+ specialized tools + 3 unified management tools\n"
            result += "🔗 **Each tool has specific documentation - check individual tool descriptions**\n"
            result += "💡 **Management tools use 'action' parameter to specify operation**\n"
            
            return result
            
        elif action == "set_log_level":
            if not log_level:
                return "❌ Error: 'log_level' is required for set_log_level action"
            
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            log_level = log_level.upper()
            
            if log_level not in valid_levels:
                return f"❌ Invalid log level. Use one of: {', '.join(valid_levels)}"
            
            logger.setLevel(getattr(logging, log_level))
            logger.info(f"📊 Log level changed to: {log_level}")
            
            return f"✅ Log level set to {log_level}"
            
        elif action == "job_redirect":
            if not job_uuid:
                return "❌ Error: 'job_uuid' is required for job_redirect action"
            
            formatted = f"📊 Legacy Job Query for {job_uuid}:\n\n"
            formatted += f"⚠️ **Important Note:**\n"
            formatted += f"Rowan manages computations through workflows, not individual jobs.\n"
            formatted += f"The job/results concept is legacy from older versions.\n\n"
            formatted += f"💡 **To find your workflow:**\n"
            formatted += f"• Use `rowan_workflow_management(action='list')` to see all workflows\n"
            formatted += f"• Look for workflows with similar names or recent creation times\n"
            formatted += f"• Use `rowan_workflow_management(action='status', workflow_uuid='UUID')` to check status\n"
            formatted += f"• Use `rowan_workflow_management(action='retrieve', workflow_uuid='UUID')` to get results\n\n"
            formatted += f"🔄 **Migration Guide:**\n"
            formatted += f"• Old: `rowan_job_status('{job_uuid}')` → New: `rowan_workflow_management(action='status', workflow_uuid='UUID')`\n"
            formatted += f"• Old: `rowan_job_results('{job_uuid}')` → New: `rowan_workflow_management(action='retrieve', workflow_uuid='UUID')`\n"
            
            return formatted
            
        else:
            return f"❌ Error: Unknown action '{action}'. Available actions: help, set_log_level, job_redirect"
            
    except Exception as e:
        return f"❌ Error in system {action}: {str(e)}"


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("🚀 Starting Rowan MCP Server...")
        logger.info(f"📊 Log level: {logger.level}")
        logger.info(f"📁 Log file: rowan_mcp.log")
        logger.info(f"🔑 API Key loaded: {'✅' if api_key else '❌'}")
        logger.info("🔗 Server ready for MCP connections!")
        
        print("🚀 Rowan MCP Server starting...")
        print("📝 Logging enabled - check rowan_mcp.log for detailed logs")
        print(f"🔑 API Key: {'✅ Loaded' if api_key else '❌ Missing'}")
        
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Server shutdown requested by user")
        print("\n👋 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server startup error: {e}")
        logger.error(f"📍 Traceback:\n{traceback.format_exc()}")
        print(f"❌ Server error: {e}")
        print("📝 Check rowan_mcp.log for detailed error information")


if __name__ == "__main__":
    main() 