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
@log_mcp_call
def rowan_electronic_properties(
    name: str,
    molecule: str,
    # Settings parameters (quantum chemistry calculation settings)
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    # Cube computation control parameters
    compute_density_cube: bool = True,
    compute_electrostatic_potential_cube: bool = True,
    compute_num_occupied_orbitals: int = 1,
    compute_num_virtual_orbitals: int = 1,
    # Workflow control parameters
    mode: Optional[str] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate comprehensive electronic structure properties using Rowan's ElectronicPropertiesWorkflow.
    
    Implements the ElectronicPropertiesWorkflow class for computing detailed electronic properties including:
    - **Molecular Orbitals**: HOMO/LUMO energies, orbital cubes, occupation numbers
    - **Electron Density**: Total, α/β spin densities, spin density differences
    - **Electrostatic Properties**: Dipole moments, quadrupole moments, electrostatic potential
    - **Population Analysis**: Mulliken charges, Löwdin charges
    - **Bond Analysis**: Wiberg bond orders, Mayer bond orders
    - **Visualization Data**: Cube files for density, ESP, and molecular orbitals
    
    **🔬 ElectronicPropertiesWorkflow Parameters:**
    - **settings**: QM calculation settings (method, basis_set, engine)
    - **compute_density_cube**: Generate electron density cube files
    - **compute_electrostatic_potential_cube**: Generate ESP cube files
    - **compute_num_occupied_orbitals**: Number of occupied MOs to save
    - **compute_num_virtual_orbitals**: Number of virtual MOs to save
    
    **📊 Output Results Include:**
    - **dipole**: Dipole moment vector (Vector3D)
    - **quadrupole**: Quadrupole moment tensor (Matrix3x3)
    - **mulliken_charges/lowdin_charges**: Atomic partial charges
    - **wiberg_bond_orders/mayer_bond_orders**: Bond order analysis
    - **density_cube**: Electron density visualization data
    - **electrostatic_potential_cube**: ESP visualization data
    - **molecular_orbitals**: MO energies, occupations, and cube data
    
    **⚙️ Smart Defaults:**
    - Method: B3LYP (hybrid DFT, good for electronic properties)
    - Basis Set: def2-SVP (balanced accuracy/cost for properties)
    - Engine: Psi4 (robust quantum chemistry package)
    - Cube Generation: Enabled for density and ESP
    - Orbital Saving: 1 occupied + 1 virtual (HOMO/LUMO)
    
    Use this for: Electronic structure analysis, orbital visualization, reactivity prediction,
    charge analysis, electrostatic property calculation, molecular orbital theory studies
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string or common name
        method: QM method (default: b3lyp for electronic properties)
        basis_set: Basis set (default: def2-svp for balanced accuracy)
        engine: Computational engine (default: psi4)
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1 for singlet)
        compute_density_cube: Generate electron density cube (default: True)
        compute_electrostatic_potential_cube: Generate ESP cube (default: True)
        compute_num_occupied_orbitals: Number of occupied MOs to save (default: 1)
        compute_num_virtual_orbitals: Number of virtual MOs to save (default: 1)
        mode: Calculation mode/precision (optional)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Comprehensive electronic properties results following ElectronicPropertiesWorkflow format
    """
    # Look up SMILES if a common name was provided
    canonical_smiles = lookup_molecule_smiles(molecule)
    
    # Apply smart defaults for electronic properties calculations
    if method is None:
        method = "b3lyp"  # Good for electronic properties
    if basis_set is None:
        basis_set = "def2-svp"  # Balanced accuracy/cost for properties
    if engine is None:
        engine = "psi4"  # Robust for electronic properties
    
    # Validate orbital count parameters
    if compute_num_occupied_orbitals < 0:
        return f"❌ compute_num_occupied_orbitals must be non-negative (got {compute_num_occupied_orbitals})"
    if compute_num_virtual_orbitals < 0:
        return f"❌ compute_num_virtual_orbitals must be non-negative (got {compute_num_virtual_orbitals})"
    
    logger.info(f"🔬 Electronic Properties Calculation: {name}")
    logger.info(f"⚗️ Method: {method}")
    logger.info(f"📐 Basis Set: {basis_set}")
    logger.info(f"🖥️ Engine: {engine}")
    logger.info(f"⚡ Charge: {charge}, Multiplicity: {multiplicity}")
    logger.info(f"📊 Density Cube: {compute_density_cube}")
    logger.info(f"🔋 ESP Cube: {compute_electrostatic_potential_cube}")
    logger.info(f"🎯 Occupied MOs: {compute_num_occupied_orbitals}, Virtual MOs: {compute_num_virtual_orbitals}")
    
    # Build parameters following ElectronicPropertiesWorkflow specification
    electronic_params = {
        "name": name,
        "molecule": canonical_smiles,  # API interface requirement
        "initial_molecule": canonical_smiles,  # ElectronicPropertiesWorkflow requirement
        # Settings (quantum chemistry parameters)
        "settings": {
            "method": method.lower(),
            "basis_set": basis_set.lower(),
            "engine": engine.lower(),
            "charge": charge,
            "multiplicity": multiplicity
        },
        # Cube computation control
        "compute_density_cube": compute_density_cube,
        "compute_electrostatic_potential_cube": compute_electrostatic_potential_cube,
        "compute_num_occupied_orbitals": compute_num_occupied_orbitals,
        "compute_num_virtual_orbitals": compute_num_virtual_orbitals,
        # Workflow parameters
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add mode if specified
    if mode:
        electronic_params["mode"] = mode
    
    try:
        result = log_rowan_api_call(
            workflow_type="electronic_properties",
            **electronic_params
        )
        
        # Enhanced result formatting for electronic properties
        if blocking:
            status = result.get('status', result.get('object_status', 'Unknown'))
            
            if status == 2:  # Completed successfully
                formatted = f"✅ Electronic properties calculation for '{name}' completed successfully!\n\n"
            elif status == 3:  # Failed
                formatted = f"❌ Electronic properties calculation for '{name}' failed!\n\n"
            else:
                formatted = f"📊 Electronic properties calculation for '{name}' submitted!\n\n"
            
            formatted += f"🧪 Molecule: {molecule}\n"
            formatted += f"🔬 SMILES: {canonical_smiles}\n"
            formatted += f"📋 Job UUID: {result.get('uuid', 'N/A')}\n"
            formatted += f"📊 Status: {status}\n\n"
            
            formatted += f"⚙️ **Calculation Settings:**\n"
            formatted += f"• Method: {method.upper()}\n"
            formatted += f"• Basis Set: {basis_set}\n"
            formatted += f"• Engine: {engine.upper()}\n"
            formatted += f"• Charge: {charge}, Multiplicity: {multiplicity}\n\n"
            
            formatted += f"📊 **Property Calculations:**\n"
            formatted += f"• Density Cube: {'✅ Enabled' if compute_density_cube else '❌ Disabled'}\n"
            formatted += f"• ESP Cube: {'✅ Enabled' if compute_electrostatic_potential_cube else '❌ Disabled'}\n"
            formatted += f"• Occupied MOs: {compute_num_occupied_orbitals}\n"
            formatted += f"• Virtual MOs: {compute_num_virtual_orbitals}\n\n"
            
            if status == 2:
                # Try to retrieve and display the actual calculation results
                try:
                    calc_result = rowan.Calculation.retrieve(uuid=result.get('uuid'))
                    
                    formatted += f"🎯 **Electronic Properties Results:**\n\n"
                    
                    # Extract key electronic properties from the result
                    object_data = calc_result.get('object_data', {})
                    
                    # Molecular orbital energies (HOMO/LUMO)
                    if 'molecular_orbitals' in object_data:
                        mo_data = object_data['molecular_orbitals']
                        if isinstance(mo_data, dict):
                            if 'energies' in mo_data:
                                energies = mo_data['energies']
                                if isinstance(energies, list) and len(energies) > 0:
                                    # Find HOMO/LUMO
                                    occupations = mo_data.get('occupations', [])
                                    if occupations:
                                        homo_idx = None
                                        lumo_idx = None
                                        for i, occ in enumerate(occupations):
                                            if occ > 0.5:  # Occupied
                                                homo_idx = i
                                            elif occ < 0.5 and lumo_idx is None:  # First unoccupied
                                                lumo_idx = i
                                                break
                                        
                                        if homo_idx is not None and lumo_idx is not None:
                                            homo_energy = energies[homo_idx]
                                            lumo_energy = energies[lumo_idx]
                                            gap = lumo_energy - homo_energy
                                            
                                            formatted += f"🔋 **Molecular Orbitals:**\n"
                                            formatted += f"• HOMO Energy: {homo_energy:.4f} hartree ({homo_energy * 27.2114:.2f} eV)\n"
                                            formatted += f"• LUMO Energy: {lumo_energy:.4f} hartree ({lumo_energy * 27.2114:.2f} eV)\n"
                                            formatted += f"• HOMO-LUMO Gap: {gap:.4f} hartree ({gap * 27.2114:.2f} eV)\n\n"
                    
                    # Dipole moment
                    if 'dipole' in object_data:
                        dipole = object_data['dipole']
                        if isinstance(dipole, dict):
                            if 'magnitude' in dipole:
                                formatted += f"🧲 **Dipole Moment:** {dipole['magnitude']:.4f} Debye\n"
                            if 'vector' in dipole:
                                vector = dipole['vector']
                                formatted += f"   Vector: ({vector[0]:.4f}, {vector[1]:.4f}, {vector[2]:.4f})\n\n"
                        elif isinstance(dipole, (int, float)):
                            formatted += f"🧲 **Dipole Moment:** {dipole:.4f} Debye\n\n"
                    
                    # Atomic charges
                    if 'mulliken_charges' in object_data:
                        charges = object_data['mulliken_charges']
                        if isinstance(charges, list) and len(charges) > 0:
                            formatted += f"⚡ **Mulliken Charges:**\n"
                            for i, charge in enumerate(charges[:10]):  # Show first 10 atoms
                                formatted += f"   Atom {i+1}: {charge:+.4f}\n"
                            if len(charges) > 10:
                                formatted += f"   ... and {len(charges) - 10} more atoms\n"
                            formatted += "\n"
                    
                    # Bond orders
                    if 'wiberg_bond_orders' in object_data:
                        bond_orders = object_data['wiberg_bond_orders']
                        if isinstance(bond_orders, dict) and bond_orders:
                            formatted += f"🔗 **Wiberg Bond Orders:**\n"
                            count = 0
                            for bond, order in list(bond_orders.items())[:10]:  # Show first 10 bonds
                                formatted += f"   {bond}: {order:.4f}\n"
                                count += 1
                            if len(bond_orders) > 10:
                                formatted += f"   ... and {len(bond_orders) - 10} more bonds\n"
                            formatted += "\n"
                    
                    # If no specific data found, show available keys
                    if not any(key in object_data for key in ['molecular_orbitals', 'dipole', 'mulliken_charges', 'wiberg_bond_orders']):
                        if object_data:
                            formatted += f"📋 **Available Properties:** {', '.join(object_data.keys())}\n\n"
                        else:
                            formatted += f"⚠️ **No electronic properties data found in results**\n\n"
                    
                except Exception as retrieve_error:
                    formatted += f"⚠️ **Results retrieval failed:** {str(retrieve_error)}\n"
                    formatted += f"💡 Use rowan_calculation_retrieve('{result.get('uuid')}') to get detailed results\n\n"
                
                formatted += f"💡 **Additional Analysis:**\n"
                formatted += f"• Use rowan_calculation_retrieve('{result.get('uuid')}') for full calculation details\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for workflow metadata\n"
                
            elif status == 3:
                formatted += f"🔧 **Troubleshooting:**\n"
                formatted += f"• Try simpler method/basis: method='hf', basis_set='sto-3g'\n"
                formatted += f"• Check molecular charge and multiplicity\n"
                formatted += f"• Disable cube generation for faster calculations\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}') for error details\n"
            else:
                formatted += f"⏳ **Next Steps:**\n"
                formatted += f"• Monitor status with rowan_workflow_management(action='retrieve', workflow_uuid='{result.get('uuid')}')\n"
                formatted += f"• Electronic properties calculations may take several minutes\n"
            
            return formatted
        else:
            return str(result)
            
    except Exception as e:
        error_msg = f"❌ Electronic properties calculation failed: {str(e)}\n\n"
        error_msg += f"🧪 Molecule: {molecule}\n"
        error_msg += f"🔬 SMILES: {canonical_smiles}\n"
        error_msg += f"⚙️ Settings: {method}/{basis_set}/{engine}\n\n"
        error_msg += f"🔧 **Common Issues:**\n"
        error_msg += f"• Invalid method/basis set combination\n"
        error_msg += f"• Incorrect charge/multiplicity for molecule\n"
        error_msg += f"• Engine compatibility issues\n"
        error_msg += f"• Try with default parameters first\n"
        return error_msg


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
    
    # ENFORCE REQUIRED PARAMETERS FOR SCANWORKFLOW - Always provide robust defaults for IRC
    # These defaults ensure scan ALWAYS works for IRC workflow
    
    if method is None:
        method = "hf-3c"  # Fast, reliable default for scans - always required
        logger.info("🚀 Using default method 'hf-3c' for scan (recommended for speed)")
        
    if engine is None:
        engine = "psi4"  # REQUIRED by ScanWorkflow - must not be None
        logger.info("🚀 Using default engine 'psi4' for scan (required by Rowan)")
        
    if mode is None:
        mode = "rapid"  # Good balance for scans - always required
        logger.info("🚀 Using default mode 'rapid' for scan (good balance)")
    
    # Ensure all required defaults are lowercase for API consistency
    method = method.lower()
    engine = engine.lower()
    mode = mode.lower()
        
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
        
        logger.info(f"✅ Primary scan_settings built: type='{coord_type_lower}', atoms={atoms}, range={start}→{stop}, num={num}")
        
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
            logger.info(f"✅ Secondary scan_settings built: type='{coord_type_2d_lower}', atoms={atoms_2d}, range={start_2d}→{stop_2d}, num={num_2d}")
        
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
                logger.info(f"✅ Concerted coordinate {i+1} built: type='{coord['coordinate_type'].lower()}', atoms={coord['atoms']}, range={coord['start']}→{coord['stop']}, num={coord['num']}")
        
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
            logger.info(f"✅ Single scan_settings configured: {scan_coordinates[0]}")
        else:
            if is_2d_scan:
                # 2D SCAN: separate scan_settings and scan_settings_2d fields
                compute_params["scan_settings"] = scan_coordinates[0]      # Primary coordinate
                compute_params["scan_settings_2d"] = scan_coordinates[1]   # Secondary coordinate  
                logger.info(f"✅ 2D scan_settings configured: primary={scan_coordinates[0]}, secondary={scan_coordinates[1]}")
            else:
                # CONCERTED SCAN: scan_settings is a list of ScanSettings
                compute_params["scan_settings"] = scan_coordinates
                logger.info(f"✅ Concerted scan_settings configured: {len(scan_coordinates)} coordinates")
        
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
        
        logger.info(f"✅ Required ScanWorkflow parameters guaranteed: calc_settings={calc_settings}, calc_engine={engine}")
        
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


# Workflow management and calculation retrieve functions moved to src/functions/


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
            result += "• `rowan_admet` - ADME-Tox properties\n\n"
            
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
            
            # Try to treat the job_uuid as a workflow_uuid and retrieve results directly
            try:
                workflow = rowan.Workflow.retrieve(uuid=job_uuid)
                
                # Get status and interpret it
                status = workflow.get('object_status', 'Unknown')
                status_names = {
                    0: "Queued",
                    1: "Running", 
                    2: "Completed",
                    3: "Failed",
                    4: "Stopped",
                    5: "Awaiting Queue"
                }
                status_name = status_names.get(status, f"Unknown ({status})")
                
                formatted = f"✅ **Found Workflow {job_uuid}:**\n\n"
                formatted += f"📝 Name: {workflow.get('name', 'N/A')}\n"
                formatted += f"⚗️ Type: {workflow.get('object_type', 'N/A')}\n"
                formatted += f"📊 Status: {status_name} ({status})\n"
                formatted += f"📅 Created: {workflow.get('created_at', 'N/A')}\n"
                formatted += f"⏱️ Elapsed: {workflow.get('elapsed', 0):.2f}s\n\n"
                
                if status == 2:  # Completed
                    formatted += f"🎯 **Getting Results...**\n\n"
                    
                    # Try to retrieve calculation results
                    try:
                        calc_result = rowan.Calculation.retrieve(uuid=job_uuid)
                        
                        # Extract workflow type to provide specific result formatting
                        workflow_type = workflow.get('object_type', '')
                        
                        if workflow_type == 'electronic_properties':
                            formatted += f"🔋 **Electronic Properties Results:**\n\n"
                            
                            # Extract key electronic properties from the result
                            object_data = calc_result.get('object_data', {})
                            
                            # Molecular orbital energies (HOMO/LUMO)
                            if 'molecular_orbitals' in object_data:
                                mo_data = object_data['molecular_orbitals']
                                if isinstance(mo_data, dict) and 'energies' in mo_data:
                                    energies = mo_data['energies']
                                    if isinstance(energies, list) and len(energies) > 0:
                                        # Find HOMO/LUMO
                                        occupations = mo_data.get('occupations', [])
                                        if occupations:
                                            homo_idx = None
                                            lumo_idx = None
                                            for i, occ in enumerate(occupations):
                                                if occ > 0.5:  # Occupied
                                                    homo_idx = i
                                                elif occ < 0.5 and lumo_idx is None:  # First unoccupied
                                                    lumo_idx = i
                                                    break
                                            
                                            if homo_idx is not None and lumo_idx is not None:
                                                homo_energy = energies[homo_idx]
                                                lumo_energy = energies[lumo_idx]
                                                gap = lumo_energy - homo_energy
                                                
                                                formatted += f"• HOMO Energy: {homo_energy:.4f} hartree ({homo_energy * 27.2114:.2f} eV)\n"
                                                formatted += f"• LUMO Energy: {lumo_energy:.4f} hartree ({lumo_energy * 27.2114:.2f} eV)\n"
                                                formatted += f"• HOMO-LUMO Gap: {gap:.4f} hartree ({gap * 27.2114:.2f} eV)\n\n"
                            
                            # Dipole moment
                            if 'dipole' in object_data:
                                dipole = object_data['dipole']
                                if isinstance(dipole, dict) and 'magnitude' in dipole:
                                    formatted += f"🧲 **Dipole Moment:** {dipole['magnitude']:.4f} Debye\n\n"
                                elif isinstance(dipole, (int, float)):
                                    formatted += f"🧲 **Dipole Moment:** {dipole:.4f} Debye\n\n"
                            
                            # If no specific electronic properties found, show available keys
                            if not any(key in object_data for key in ['molecular_orbitals', 'dipole']):
                                if object_data:
                                    formatted += f"📋 **Available Properties:** {', '.join(object_data.keys())}\n\n"
                                else:
                                    formatted += f"⚠️ **No electronic properties data found in results**\n\n"
                        
                        else:
                            # For other workflow types, show general calculation results
                            formatted += f"📊 **{workflow_type.replace('_', ' ').title()} Results:**\n\n"
                            
                            object_data = calc_result.get('object_data', {})
                            if object_data:
                                # Show first few key-value pairs
                                count = 0
                                for key, value in object_data.items():
                                    if count >= 5:  # Limit to first 5 items for job_redirect
                                        formatted += f"   ... and {len(object_data) - 5} more properties\n"
                                        break
                                    
                                    # Format the value nicely
                                    if isinstance(value, (int, float)):
                                        formatted += f"• **{key}**: {value}\n"
                                    elif isinstance(value, str):
                                        formatted += f"• **{key}**: {value[:50]}{'...' if len(value) > 50 else ''}\n"
                                    elif isinstance(value, list):
                                        formatted += f"• **{key}**: {len(value)} items\n"
                                    elif isinstance(value, dict):
                                        formatted += f"• **{key}**: {len(value)} properties\n"
                                    else:
                                        formatted += f"• **{key}**: {type(value).__name__}\n"
                                    count += 1
                                formatted += "\n"
                            else:
                                formatted += f"⚠️ **No calculation data found in results**\n\n"
                        
                    except Exception as retrieve_error:
                        formatted += f"⚠️ **Results retrieval failed:** {str(retrieve_error)}\n\n"
                
                elif status in [0, 1, 5]:  # Still running
                    formatted += f"⏳ **Workflow is still {status_name.lower()}**\n"
                    formatted += f"💡 Check back later for results\n\n"
                
                elif status == 3:  # Failed
                    formatted += f"❌ **Workflow failed**\n"
                    formatted += f"💡 Check the workflow parameters and try again\n\n"
                
                formatted += f"💡 **For more details:**\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='{job_uuid}') for full workflow details\n"
                formatted += f"• Use rowan_calculation_retrieve('{job_uuid}') for raw calculation data\n"
                
                return formatted
                
            except Exception as e:
                # If workflow retrieval fails, provide the legacy guidance
                formatted = f"❌ **Could not find workflow {job_uuid}:** {str(e)}\n\n"
                formatted += f"⚠️ **Important Note:**\n"
                formatted += f"Rowan manages computations through workflows, not individual jobs.\n"
                formatted += f"The job/results concept is legacy from older versions.\n\n"
                formatted += f"💡 **To find your workflow:**\n"
                formatted += f"• Use rowan_workflow_management(action='list') to see all workflows\n"
                formatted += f"• Look for workflows with similar names or recent creation times\n"
                formatted += f"• Use rowan_workflow_management(action='retrieve', workflow_uuid='UUID') to get results\n\n"
                formatted += f"🔄 **Migration Guide:**\n"
                formatted += f"• Old: rowan_job_status('{job_uuid}') → New: rowan_workflow_management(action='status', workflow_uuid='UUID')\n"
                formatted += f"• Old: rowan_job_results('{job_uuid}') → New: rowan_workflow_management(action='retrieve', workflow_uuid='UUID')\n"
                
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