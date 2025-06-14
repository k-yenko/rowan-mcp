"""
Rowan MCP Server Implementation using FastMCP

This module implements the Model Context Protocol server for Rowan's
computational chemistry platform using the FastMCP framework.
"""

import os
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Literal
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field

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
            
            # Return a formatted error message
            error_msg = f"❌ Error in {func_name}: {str(e)}"
            if "rowan" in str(e).lower():
                error_msg += f"\n🔗 Check Rowan API status and your API key"
            return error_msg
            
    return wrapper


def log_rowan_api_call(workflow_type: str, **kwargs):
    """Log Rowan API calls with detailed parameters."""
    logger.info(f"🌐 Rowan API Call: {workflow_type}")
    logger.info(f"🔍 Rowan Parameters: {kwargs}")
    
    # Special handling for long-running calculations
    if workflow_type == "multistage_opt":
        ping_interval = kwargs.get('ping_interval', 5)
        logger.info(f"⏳ Multi-stage optimization may take several minutes...")
        logger.info(f"🔄 Progress will be checked every {ping_interval} seconds")
    
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
        raise e


# Pydantic models for request validation
class PkaRequest(BaseModel):
    name: str = Field(..., description="Name for the calculation")
    molecule: str = Field(..., description="Molecule SMILES string")
    folder_uuid: Optional[str] = Field(None, description="Folder UUID for organization")


class ConformerRequest(BaseModel):
    name: str = Field(..., description="Name for the calculation")
    molecule: str = Field(..., description="Molecule SMILES string")
    max_conformers: Optional[int] = Field(10, description="Maximum number of conformers")
    folder_uuid: Optional[str] = Field(None, description="Folder UUID for organization")


class FolderRequest(BaseModel):
    name: str = Field(..., description="Name of the folder")
    description: Optional[str] = Field(None, description="Optional description")


class JobRequest(BaseModel):
    job_uuid: str = Field(..., description="UUID of the job")


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
    "cc-pvdz(seg-opt)": "cc-pVDZ segmented-optimized (RECOMMENDED over cc-pVDZ)",
    "cc-pvtz(seg-opt)": "cc-pVTZ segmented-optimized (RECOMMENDED over cc-pVTZ)",
    "cc-pvqz(seg-opt)": "cc-pVQZ segmented-optimized (RECOMMENDED over cc-pVQZ)",
    
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
    
    guidance += "**💡 Rowan Recommendations:**\n"
    guidance += "• **Smart defaults**: `rowan_quantum_chemistry()` uses B3LYP/pcseg-1 + D3BJ (recommended)\n"
    guidance += "• **For geometry optimization**: Use `rowan_multistage_opt` (RECOMMENDED)\n"
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
def rowan_qc_guide() -> str:
    """Get comprehensive guidance for quantum chemistry calculations in Rowan.
    
    Provides detailed information about:
    - Required parameters for QC calculations
    - Available engines (Psi4, TeraChem, PySCF, xTB, AIMNet2)
    - Common methods and basis sets
    - Available tasks and properties
    - Best practices and recommendations
    
    Use this for: Understanding Rowan's quantum chemistry capabilities
    
    Returns:
        Comprehensive quantum chemistry guidance
    """
    return get_qc_guidance()

# Unified Quantum Chemistry Tool
@mcp.tool()
@log_mcp_call
def rowan_quantum_chemistry(
    name: str,
    molecule: str,
    method: Optional[str] = None,
    basis_set: Optional[str] = None,
    tasks: Optional[List[str]] = None,
    corrections: Optional[List[str]] = None,
    engine: Optional[str] = None,
    charge: int = 0,
    multiplicity: int = 1,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5,
    use_recommended_defaults: bool = True,
    additional_settings: Optional[Dict[str, Any]] = None
) -> str:
    """Run quantum chemistry calculations with intelligent defaults or custom settings.
    
    **🔬 Smart Defaults**: When no parameters are specified, uses Rowan's RECOMMENDED settings:
    - Method: B3LYP (popular, reliable hybrid functional)
    - Basis Set: pcseg-1 (better than 6-31G(d) at same cost)
    - Tasks: ["energy", "optimize"] (energy + geometry optimization)
    - Corrections: ["d3bj"] (dispersion correction for better accuracy)
    
    **⚗️ Full Customization**: All parameters can be overridden for advanced users
    
    **Available Methods (16 total):**
    - HF: Hartree-Fock (unrestricted for open-shell)
    - Pure DFT: LSDA, PBE, BLYP, BP86, B97-D3, r2SCAN, TPSS, M06-L
    - Hybrid DFT: PBE0, B3LYP, B3PW91, CAM-B3LYP, ωB97X-D3, ωB97X-V, ωB97M-V
    
    **Available Basis Sets (29 total):**
    - Recommended: pcseg-1 (DFT), pcseg-2 (high accuracy)
    - Popular: 6-31G*, 6-31G(d,p), cc-pVDZ(seg-opt)
    - Fast: MIDI!, STO-3G
    
    **Available Corrections:**
    - D3BJ: Grimme's D3 dispersion with Becke-Johnson damping
    
    Use this for: All quantum chemistry calculations (beginners get good defaults, experts get full control)
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string (e.g., 'CC(=O)OC1=CC=CC=C1C(=O)O' for aspirin)
        method: QC method - if None, uses 'b3lyp' (recommended default)
        basis_set: Basis set - if None, uses 'pcseg-1' (recommended default)
        tasks: List of tasks - if None, uses ['energy', 'optimize'] (recommended default)
        corrections: List of corrections - if None, uses ['d3bj'] (recommended default)
        engine: Computational engine - if None, defaults to 'psi4' (required by Rowan API)
        charge: Molecular charge (default: 0)
        multiplicity: Spin multiplicity (default: 1 for singlet)
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
        use_recommended_defaults: If True, uses smart defaults when parameters are None
        additional_settings: Extra calculation-specific settings
    
    Returns:
        Quantum chemistry calculation results
    """
    
    # Determine if we're using defaults or custom settings
    using_defaults = (method is None and basis_set is None and 
                     tasks is None and corrections is None)
    
    # Apply intelligent defaults when no parameters specified
    if use_recommended_defaults and using_defaults:
        method = "b3lyp"  # Popular, reliable hybrid functional
        basis_set = "pcseg-1"  # Better than 6-31G(d) at same cost
        tasks = ["energy", "optimize"]  # Energy + geometry optimization
        corrections = ["d3bj"]  # Dispersion correction for accuracy
        if engine is None:  # Only set default if not provided
            engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
        default_msg = "Rowan's RECOMMENDED defaults"
    elif using_defaults:
        # Fall back to Rowan's system defaults but ensure engine is set
        if engine is None:  # Only set default if not provided
            engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
        default_msg = "Rowan's system defaults (HF/STO-3G)"
    else:
        # For custom settings, still ensure engine is set if not provided
        if engine is None:  # Only set default if not provided
            engine = "psi4"  # Default to Psi4 engine (REQUIRED by Rowan API)
        default_msg = "Custom user settings"
    
    # Validate inputs and provide guidance
    if method and method.lower() not in QC_METHODS:
        available_methods = ", ".join(QC_METHODS.keys())
        return f"❌ Invalid method '{method}'. Available methods: {available_methods}\n\n" + get_qc_guidance()
    
    if basis_set and basis_set.lower() not in QC_BASIS_SETS:
        available_basis = ", ".join(QC_BASIS_SETS.keys())
        return f"❌ Invalid basis set '{basis_set}'. Available basis sets: {available_basis}\n\n" + get_qc_guidance()
    
    if tasks:
        invalid_tasks = [task for task in tasks if task.lower() not in QC_TASKS]
        if invalid_tasks:
            available_tasks = ", ".join(QC_TASKS.keys())
            return f"❌ Invalid tasks {invalid_tasks}. Available tasks: {available_tasks}\n\n" + get_qc_guidance()
    
    if engine and engine.lower() not in QC_ENGINES:
        available_engines = ", ".join(QC_ENGINES.keys())
        return f"❌ Invalid engine '{engine}'. Available engines: {available_engines}\n\n" + get_qc_guidance()
    
    if corrections:
        invalid_corrections = [corr for corr in corrections if corr.lower() not in QC_CORRECTIONS]
        if invalid_corrections:
            available_corrections = ", ".join(QC_CORRECTIONS.keys())
            return f"❌ Invalid corrections {invalid_corrections}. Available corrections: {available_corrections}\n\n" + get_qc_guidance()
    
    # Build settings dictionary
    settings = additional_settings or {}
    
    if method:
        settings["method"] = method.lower()
    if basis_set:
        settings["basis_set"] = basis_set.lower()
    if tasks:
        settings["tasks"] = [task.lower() for task in tasks]
    if corrections:
        settings["corrections"] = [corr.lower() for corr in corrections]
    # Always include engine (REQUIRED by Rowan API)
    if engine:
        settings["engine"] = engine.lower()
    if charge != 0:
        settings["charge"] = charge
    if multiplicity != 1:
        settings["multiplicity"] = multiplicity
    
    # Log the QC parameters
    logger.info(f"🔬 Quantum Chemistry Calculation: {name}")
    logger.info(f"⚙️ Using: {default_msg}")
    logger.info(f"⚗️ Method: {method or 'system default'}")
    logger.info(f"📐 Basis Set: {basis_set or 'system default'}")
    logger.info(f"🎯 Tasks: {tasks or 'system default'}")
    logger.info(f"🔧 Corrections: {corrections or 'none'}")
    logger.info(f"🖥️ Engine: {engine or 'auto-selected'}")
    logger.info(f"⚡ Charge: {charge}, Multiplicity: {multiplicity}")
    
    try:
        # Use basic_calculation workflow with settings
        result = log_rowan_api_call(
            workflow_type="basic_calculation",
            name=name,
            molecule=molecule,
            settings=settings if settings else None,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        # Check actual job status and format accordingly
        job_status = result.get('status', result.get('object_status', 'Unknown'))
        status_names = {
            0: ("⏳", "Queued"),
            1: ("🔄", "Running"), 
            2: ("✅", "Completed Successfully"),
            3: ("❌", "Failed"),
            4: ("⏹️", "Stopped"),
            5: ("⏸️", "Awaiting Queue")
        }
        
        status_icon, status_text = status_names.get(job_status, ("❓", f"Unknown ({job_status})"))
        
        # Use appropriate header based on actual status
        if job_status == 2:
            formatted = f"✅ Quantum chemistry calculation '{name}' completed successfully!\n\n"
        elif job_status == 3:
            formatted = f"❌ Quantum chemistry calculation '{name}' failed!\n\n"
        elif job_status in [0, 1, 5]:
            formatted = f"🔄 Quantum chemistry calculation '{name}' submitted!\n\n"
        elif job_status == 4:
            formatted = f"⏹️ Quantum chemistry calculation '{name}' was stopped!\n\n"
        else:
            formatted = f"📊 Quantum chemistry calculation '{name}' status unknown!\n\n"
            
        formatted += f"🧪 Molecule: {molecule}\n"
        formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
        formatted += f"📊 Status: {status_icon} {status_text} ({job_status})\n"
        formatted += f"⚙️ Used: {default_msg}\n"
        
        # Show applied settings
        if method or basis_set or tasks or corrections or engine or charge != 0 or multiplicity != 1:
            formatted += f"\n⚙️ **Applied Settings:**\n"
            if method:
                formatted += f"   Method: {method.upper()} - {QC_METHODS.get(method.lower(), 'Custom method')}\n"
            if basis_set:
                formatted += f"   Basis Set: {basis_set} - {QC_BASIS_SETS.get(basis_set.lower(), 'Custom basis')}\n"
            if tasks:
                formatted += f"   Tasks: {', '.join(tasks)}\n"
            if corrections:
                formatted += f"   Corrections: {', '.join(corrections)} - "
                formatted += ", ".join([QC_CORRECTIONS.get(corr.lower(), 'Custom correction') for corr in corrections]) + "\n"
            if engine:
                formatted += f"   Engine: {engine.upper()} - {QC_ENGINES.get(engine.lower(), 'Custom engine')}\n"
            if charge != 0 or multiplicity != 1:
                formatted += f"   Charge: {charge}, Multiplicity: {multiplicity}\n"
        
        # Add status-appropriate guidance
        formatted += f"\n💡 **Next Steps:**\n"
        if job_status == 2:  # Completed successfully
            formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to get detailed results\n"
            formatted += f"• Results should include energies, geometries, and other calculated properties\n"
        elif job_status == 3:  # Failed
            formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to see error details\n"
            formatted += f"• **Troubleshooting tips:**\n"
            formatted += f"  - Try simpler settings: method='hf', basis_set='sto-3g'\n"
            formatted += f"  - Use `rowan_multistage_opt()` for geometry optimization (more robust)\n"
            formatted += f"  - Check if SMILES string is valid\n"
            formatted += f"  - For difficult molecules, try method='xtb' (semiempirical)\n"
        elif job_status in [0, 1, 5]:  # Queued/Running/Awaiting
            formatted += f"• Check status: `rowan_workflow_status('{result.get('uuid', 'UUID')}')`\n"
            formatted += f"• Wait for completion, then retrieve results\n"
            formatted += f"• Calculation may take several minutes depending on molecule size\n"
        elif job_status == 4:  # Stopped
            formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to see why it was stopped\n"
            formatted += f"• You can restart with the same or different parameters\n"
        else:  # Unknown status
            formatted += f"• Use `rowan_workflow_retrieve('{result.get('uuid', 'UUID')}')` to get more information\n"
            formatted += f"• Check `rowan_workflow_status('{result.get('uuid', 'UUID')}')` for current status\n"
            
        # Add general guidance for successful submissions or unknown states
        if job_status != 3:  # Don't show alternatives if it failed
            if using_defaults and use_recommended_defaults:
                formatted += f"• **For future calculations:** Try different methods/basis sets for different accuracy/speed trade-offs\n"
        
        return formatted
        
    except Exception as e:
        error_msg = f"❌ Quantum chemistry calculation submission failed: {str(e)}\n\n"
        error_msg += "🔧 **This is a submission error, not a calculation failure.**\n"
        error_msg += "The job never started due to invalid parameters or API issues.\n\n"
        if "method" in str(e).lower() or "basis" in str(e).lower():
            error_msg += "💡 **Parameter Error**: Try using recommended defaults by calling with just name and molecule\n"
            error_msg += "Or check parameter spelling and availability\n\n"
        elif "engine" in str(e).lower():
            error_msg += "💡 **Engine Error**: The engine parameter is required. This should be auto-set to 'psi4'\n\n"
        error_msg += get_qc_guidance()
        return error_msg

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
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="bde",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating BDE: {str(e)}"


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
    """Run multi-level geometry optimization (RECOMMENDED).
    
    Performs hierarchical optimization using multiple levels of theory:
    GFN2-xTB → AIMNet2 → DFT for optimal balance of speed and accuracy.
    
    This is the RECOMMENDED method for geometry optimization as it provides:
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
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="electronic_properties",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating electronic properties: {str(e)}"


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
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="descriptors",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating descriptors: {str(e)}"


# Solubility Prediction
@mcp.tool()
def rowan_solubility(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict aqueous solubility.
    
    Predicts water solubility, a critical property for:
    - Drug formulation and bioavailability
    - Environmental fate and transport
    - Process chemistry and purification
    
    Use this for: Drug development, environmental assessment, process optimization
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Solubility prediction results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="solubility",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error predicting solubility: {str(e)}"


# Redox Potential
@mcp.tool()
def rowan_redox_potential(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Predict redox potentials vs. SCE in acetonitrile.
    
    Calculates oxidation and reduction potentials for:
    - Electrochemical reaction design
    - Battery and energy storage applications
    - Understanding electron transfer processes
    
    Use this for: Electrochemistry, battery materials, electron transfer studies
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Redox potential results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="redox_potential",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating redox potential: {str(e)}"


# Scan - Potential Energy Surface Scans
@mcp.tool()
def rowan_scan(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run potential energy surface scans.
    
    Performs constrained optimizations along reaction coordinates to:
    - Map reaction pathways and mechanisms
    - Find transition state approximations
    - Study conformational preferences
    - Analyze rotational barriers (atropisomerism)
    
    Use this for: Reaction mechanism studies, transition state searching, conformational analysis
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Scan results with energy profile
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="scan",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error running scan: {str(e)}"


# Fukui Indices - Reactivity Analysis
@mcp.tool()
def rowan_fukui(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Calculate Fukui indices for reactivity prediction.
    
    Predicts sites of chemical reactivity by analyzing electron density changes:
    - f(+): reactivity towards nucleophiles
    - f(-): reactivity towards electrophiles  
    - f(0): reactivity towards radicals
    
    Use this for: Predicting reaction sites, selectivity analysis, drug design
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Fukui indices and reactivity analysis
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="fukui",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating Fukui indices: {str(e)}"


# Spin States
@mcp.tool()
def rowan_spin_states(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Determine preferred spin states for molecules.
    
    Calculates energies of different spin multiplicities to determine:
    - Ground state spin multiplicity
    - Spin crossover energetics
    - High-spin vs low-spin preferences
    
    Use this for: Transition metal complexes, radical species, magnetic materials
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Spin state energetics results
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="spin_states",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating spin states: {str(e)}"


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
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="tautomers",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error enumerating tautomers: {str(e)}"


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
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="hydrogen_bond_basicity",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error calculating hydrogen bond basicity: {str(e)}"


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
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="irc",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error running IRC: {str(e)}"


# Molecular Dynamics
@mcp.tool()
@log_mcp_call
def rowan_molecular_dynamics(
    name: str,
    molecule: str,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """Run molecular dynamics simulations.
    
    Performs MD simulations to study:
    - Dynamic behavior and flexibility
    - Conformational sampling
    - Thermal properties
    - Time-dependent phenomena
    
    Use this for: Conformational dynamics, thermal properties, flexible systems
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Returns:
        Molecular dynamics trajectory and analysis
    """
    try:
        result = rowan.compute(
            name=name,
            molecule=molecule,
            workflow_type="molecular_dynamics",
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        return str(result)
    except Exception as e:
        return f"❌ Error running molecular dynamics: {str(e)}"


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
    folder_uuid: Optional[str] = None
) -> str:
    """Generate and optimize molecular conformers.
    
    Args:
        name: Name for the calculation
        molecule: Molecule SMILES string
        max_conformers: Maximum number of conformers to generate
        folder_uuid: UUID of folder to organize calculation in
    
    Returns:
        Conformer search results
    """
    settings = {"max_conformers": max_conformers}
    
    result = log_rowan_api_call(
        workflow_type="conformer_search",
        name=name,
        molecule=molecule,
        settings=settings,
        folder_uuid=folder_uuid
    )
    
    formatted = f"✅ Conformer search for '{name}' started!\n\n"
    formatted += f"🧪 Molecule: {molecule}\n"
    formatted += f"🔬 Job UUID: {result.get('uuid', 'N/A')}\n"
    formatted += f"📊 Status: {result.get('status', 'Unknown')}\n"
    formatted += f"🔄 Max Conformers: {max_conformers}\n"
    
    return formatted


@mcp.tool()
def rowan_folder_management(
    action: str,
    folder_uuid: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
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
    - **create**: Create a new folder (requires: name, optional: parent_uuid, notes/description, starred, public)
    - **retrieve**: Get folder details (requires: folder_uuid)
    - **update**: Update folder properties (requires: folder_uuid, optional: name, parent_uuid, notes, starred, public)
    - **delete**: Delete a folder (requires: folder_uuid)
    - **list**: List folders with filters (optional: name_contains, parent_uuid, starred, public, page, size)
    
    Args:
        action: Action to perform ('create', 'retrieve', 'update', 'delete', 'list')
        folder_uuid: UUID of the folder (required for retrieve, update, delete)
        name: Folder name (required for create, optional for update)
        description: Folder description (optional for create, legacy parameter - use notes instead)
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
            
            # Use description as notes if provided, otherwise use notes parameter
            notes_to_use = description or notes or ""
            
            folder = rowan.Folder.create(
                name=name,
                parent_uuid=parent_uuid,  # Required by API
                notes=notes_to_use,       # Use notes instead of description
                starred=starred or False,
                public=public or False
            )
            
            formatted = f"✅ Folder '{name}' created successfully!\n\n"
            formatted += f"📁 UUID: {folder.get('uuid', 'N/A')}\n"
            formatted += f"📝 Notes: {notes_to_use or 'None'}\n"
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
            result += "• `rowan_multistage_opt` - Multi-level optimization (RECOMMENDED for geometry)\n\n"
            
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
            result += "• `rowan_scan` - Potential energy scans\n"
            result += "• `rowan_fukui` - Reactivity analysis\n"
            result += "• `rowan_spin_states` - Spin state preferences\n"
            result += "• `rowan_irc` - Reaction coordinate following\n"
            result += "• `rowan_molecular_dynamics` - MD simulations\n"
            result += "• `rowan_hydrogen_bond_basicity` - H-bond strength\n\n"
            
            result += "💡 **Usage Guidelines:**\n"
            result += "• For geometry optimization: use `rowan_multistage_opt` (RECOMMENDED)\n"
            result += "• For energy calculations: use `rowan_quantum_chemistry` (smart defaults)\n"
            result += "• For custom QC settings: use `rowan_quantum_chemistry` with parameters\n"
            result += "• For conformer search: use `rowan_conformers`\n"
            result += "• For pKa prediction: use `rowan_pka`\n"
            result += "• For electronic structure: use `rowan_electronic_properties`\n"
            result += "• For drug properties: use `rowan_admet`\n"
            result += "• For reaction mechanisms: use `rowan_scan` then `rowan_irc`\n\n"
            
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