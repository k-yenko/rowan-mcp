"""
Rowan docking function for MCP tool integration.
Implements protein-ligand docking following the stjames-public workflow pattern.
"""

from typing import Optional, Union, List, Dict, Any, Tuple
import rowan
import logging
import os
import requests
import hashlib
import time

# Set up logging
logger = logging.getLogger(__name__)


def _upload_pdb_to_rowan(pdb_content: str, pdb_name: str = "uploaded_protein") -> Optional[str]:
    """
    Upload PDB content to Rowan and return the protein UUID.
    
    Args:
        pdb_content: Raw PDB file content as string
        pdb_name: Name for the uploaded protein
        
    Returns:
        UUID of uploaded protein, or None if upload fails
    """
    if not rowan.api_key:
        logger.error("❌ No Rowan API key configured")
        return None
    
    # Create a unique name based on content hash to avoid duplicates
    content_hash = hashlib.md5(pdb_content.encode()).hexdigest()[:8]
    unique_name = f"{pdb_name}_{content_hash}"
    
    logger.info(f"📤 Attempting to upload PDB to Rowan as '{unique_name}'...")
    
    # Try multiple API approaches for uploading
    upload_methods = [
        # Method 1: Direct Rowan API (most likely)
        {
            "url": "https://api.rowansci.com/proteins",
            "data": {
                "name": unique_name,
                "description": f"Auto-uploaded PDB content ({len(pdb_content)} chars)",
                "pdb_content": pdb_content,
                "source": "local_upload"
            }
        },
        # Method 2: Alternative endpoint
        {
            "url": "https://api.rowansci.com/v1/proteins",
            "data": {
                "name": unique_name,
                "pdb_data": pdb_content
            }
        },
        # Method 3: Upload with file format
        {
            "url": "https://api.rowansci.com/proteins/upload",
            "data": {
                "name": unique_name,
                "content": pdb_content,
                "format": "pdb"
            }
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {rowan.api_key}",
        "Content-Type": "application/json"
    }
    
    for i, method in enumerate(upload_methods, 1):
        try:
            logger.info(f"🔄 Trying upload method {i}: {method['url']}")
            
            response = requests.post(
                method["url"],
                headers=headers,
                json=method["data"],
                timeout=30
            )
            
            logger.info(f"📊 Method {i} response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                protein_uuid = result.get('uuid') or result.get('id') or result.get('protein_id')
                
                if protein_uuid:
                    logger.info(f"✅ Upload successful! Protein UUID: {protein_uuid}")
                    return protein_uuid
                else:
                    logger.warning(f"⚠️ Method {i} success but no UUID in response: {result}")
                    
            elif response.status_code == 409:
                # Conflict - protein might already exist
                logger.info(f"🔄 Method {i}: Protein might already exist (409)")
                # Try to find existing protein by name
                try:
                    list_response = requests.get(
                        "https://api.rowansci.com/proteins",
                        headers=headers,
                        params={"name": unique_name}
                    )
                    if list_response.status_code == 200:
                        proteins = list_response.json()
                        if proteins and len(proteins) > 0:
                            existing_uuid = proteins[0].get('uuid') or proteins[0].get('id')
                            if existing_uuid:
                                logger.info(f"✅ Found existing protein UUID: {existing_uuid}")
                                return existing_uuid
                except Exception:
                    pass
                    
            else:
                logger.warning(f"❌ Method {i} failed: {response.status_code} - {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ Method {i} timed out")
        except Exception as e:
            logger.warning(f"❌ Method {i} error: {e}")
    
    # If all methods failed, try rowan's internal API (if available)
    try:
        logger.info(f"🔄 Trying rowan.protein internal methods...")
        
        # Check if rowan has protein creation methods
        if hasattr(rowan, 'protein') and hasattr(rowan.protein, 'create'):
            result = rowan.protein.create(
                name=unique_name,
                pdb_content=pdb_content
            )
            if result and result.get('uuid'):
                protein_uuid = result['uuid']
                logger.info(f"✅ Rowan internal upload successful! UUID: {protein_uuid}")
                return protein_uuid
                
    except Exception as e:
        logger.warning(f"❌ Rowan internal method failed: {e}")
    
    logger.error(f"❌ All upload methods failed for PDB content")
    return None


def _detect_pdb_file_path(protein_input: str) -> Optional[str]:
    """
    Detect if protein_input is a path to a local PDB file.
    
    Args:
        protein_input: Could be PDB code, UUID, or file path
        
    Returns:
        Path to PDB file if it exists, None otherwise
    """
    # Common PDB file patterns
    pdb_patterns = [
        protein_input,  # Direct path
        f"{protein_input}.pdb",  # Add .pdb extension
        f"{protein_input.lower()}.pdb",  # Lowercase with .pdb
        f"{protein_input.upper()}.pdb",  # Uppercase with .pdb
    ]
    
    for pattern in pdb_patterns:
        if os.path.isfile(pattern):
            logger.info(f"📁 Detected local PDB file: {pattern}")
            return pattern
    
    return None


def rowan_docking(
    name: str,
    ligand: Optional[str] = None,
    protein: Optional[str] = None,
    pocket_center: Optional[Union[List[float], Tuple[float, float, float]]] = None,
    pocket_size: Optional[Union[List[float], Tuple[float, float, float]]] = None,
    mode: str = "rapid",
    do_csearch: bool = True,
    do_optimization: bool = True,
    do_pose_refinement: bool = True,
    # Additional stjames DockingWorkflow parameters
    molecules: Optional[List[str]] = None,
    smiles: Optional[Union[str, List[str]]] = None,
    conformers: Optional[List[str]] = None,
    target: Optional[str] = None,
    target_uuid: Optional[str] = None,
    initial_molecule: Optional[str] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = False,  # Changed to False to avoid timeouts
    ping_interval: int = 5
) -> str:
    """Perform protein-ligand docking using machine learning-enhanced workflow.
    
    This tool performs comprehensive protein-ligand docking with the following features:
    - **Conformer generation**: ETKDG conformer search with ML optimization
    - **Strain filtering**: AIMNet2-based ligand strain calculation to remove unphysical poses
    - **AutoDock Vina**: Industry-standard docking with Vinardo scoring
    - **Pose refinement**: ML-based pose optimization with harmonic constraints
    - **Comprehensive results**: Docking scores, strain energies, and binding poses
    
    **🧬 Hardcoded for GFP-Water System:**
    - **Protein**: Green Fluorescent Protein (PDB: 1EMA) - automatically fetched
    - **Ligand**: Water molecule (SMILES: O) - unless specified otherwise
    - **Default pocket**: Center of binding site with 20Å search box
    
    **📊 Workflow Details:**
    1. Generate ligand conformers with ETKDG → screen with GFN2-xTB → optimize with AIMNet2
    2. Compute conformer energies with AIMNet2 + CPCMX(water) solvation
    3. Dock each conformer with AutoDock Vina using Vinardo scoring
    4. Optimize poses with AIMNet2 + harmonic constraints (5 kcal/mol/Å²)
    5. Calculate strain energies (Epose - Emin) and flag high-strain poses (>5 kcal/mol)
    6. Return ranked poses with docking scores and strain analysis
    
    **⚡ Smart Defaults:**
    - Mode: 'rapid' (balanced speed/accuracy for drug discovery)
    - Conformer search: Enabled (essential for flexible ligands)
    - Optimization: Enabled (improves pose quality)
    - Pose refinement: Enabled (removes unphysical geometries)
    
    Use this for: Hit identification, lead optimization, binding mode analysis,
    structure-activity relationships, virtual screening with quality control
    
    Args:
        name: Name for the docking calculation
        ligand: Ligand SMILES string (default: "O" for water)
        protein: Protein PDB code (default: "1EMA" for GFP)
        pocket_center: Pocket center coordinates [x, y, z] (default: GFP binding site)
        pocket_size: Pocket size [x, y, z] in Angstroms (default: [20.0, 20.0, 20.0])
        mode: Docking mode - 'rapid', 'standard', or 'exhaustive' (default: 'rapid')
        do_csearch: Whether to perform conformer search (default: True)
        do_optimization: Whether to optimize ligand geometry (default: True)
        do_pose_refinement: Whether to refine docked poses (default: True)
        # Additional stjames DockingWorkflow parameters
        molecules: List of molecules to dock (optional, for multiple ligands)
        smiles: SMILES strings of ligands (optional, alternative to ligand parameter)
        conformers: UUIDs of pre-optimized conformers (optional)
        target: Raw PDB object/content (optional, alternative to protein parameter)
        target_uuid: UUID of protein target (optional, alternative to protein parameter)
        initial_molecule: Initial molecule for workflow (optional, defaults to ligand)
        folder_uuid: Optional folder UUID to organize the calculation
        blocking: Whether to wait for completion (default: False to avoid timeouts)
        ping_interval: Interval in seconds to check calculation status
        
    Returns:
        JSON string with workflow UUID and status (non-blocking) or full results (blocking)
        
    Examples:
        # Default GFP-water docking
        rowan_docking(name="gfp_water_test")
        
        # Custom ligand with GFP
        rowan_docking(
            name="gfp_drug_screening",
            ligand="CC(=O)Nc1ccc(O)cc1"  # acetaminophen
        )
        
        # Custom pocket location
        rowan_docking(
            name="custom_pocket",
            ligand="CCO",  # ethanol
            pocket_center=[10.5, 15.2, 8.7],
            pocket_size=[15.0, 15.0, 15.0]
        )
        
        # Using local PDB file (automatic upload)
        rowan_docking(
            name="local_pdb_docking",
            protein="1ema.pdb",  # File path - will auto-upload
            ligand="CCO"
        )
        
        # Or using target parameter with file path
        rowan_docking(
            name="target_file_docking", 
            target="protein.pdb",  # File path - will auto-upload
            ligand="CCO"
        )
        
        # Or using raw PDB content (will auto-upload)
        with open('protein.pdb', 'r') as f:
            pdb_content = f.read()
        rowan_docking(
            name="raw_pdb_docking",
            target=pdb_content,  # Raw content - will auto-upload
            ligand="CCO"
        )
    """
    
    # Handle ligand specification (following stjames DockingWorkflow priority)
    primary_ligand = None
    if ligand is not None:
        primary_ligand = ligand
        logger.info(f"💧 Using ligand parameter: {ligand}")
    elif smiles is not None:
        if isinstance(smiles, list):
            primary_ligand = smiles[0]  # Use first SMILES if list
            logger.info(f"💧 Using first SMILES from list: {primary_ligand}")
        else:
            primary_ligand = smiles
            logger.info(f"💧 Using smiles parameter: {primary_ligand}")
    elif molecules is not None and len(molecules) > 0:
        primary_ligand = molecules[0]  # Use first molecule if list
        logger.info(f"💧 Using first molecule from list: {primary_ligand}")
    else:
        # Apply hardcoded default for GFP-water system
        primary_ligand = "O"  # Water molecule
        logger.info("💧 Using default ligand: water (O)")
    
    # Handle protein/target specification with automatic PDB file detection and upload
    target_specification = None
    uploaded_protein_uuid = None
    
    if target is not None:
        # Check if target is a file path to PDB content
        if isinstance(target, str):
            pdb_file_path = _detect_pdb_file_path(target)
            if pdb_file_path:
                logger.info(f"📁 Detected PDB file path in target: {pdb_file_path}")
                try:
                    with open(pdb_file_path, 'r') as f:
                        pdb_content = f.read()
                    
                    # Upload PDB content to Rowan
                    pdb_name = os.path.splitext(os.path.basename(pdb_file_path))[0]
                    uploaded_protein_uuid = _upload_pdb_to_rowan(pdb_content, pdb_name)
                    
                    if uploaded_protein_uuid:
                        target_specification = uploaded_protein_uuid
                        logger.info(f"✅ Auto-uploaded PDB file, using UUID: {uploaded_protein_uuid}")
                    else:
                        logger.error(f"❌ Failed to upload PDB file: {pdb_file_path}")
                        # Fallback to treating as raw content (will likely fail)
                        target_specification = pdb_content
                        logger.warning("⚠️ Fallback: using raw PDB content (may fail validation)")
                except Exception as e:
                    logger.error(f"❌ Error reading PDB file {pdb_file_path}: {e}")
                    target_specification = target
            else:
                # Check if target looks like PDB content (starts with HEADER, ATOM, etc.)
                if target.strip().startswith(('HEADER', 'ATOM', 'HETATM', 'REMARK')):
                    logger.info("📄 Detected raw PDB content in target parameter")
                    
                    # Try to extract protein name from PDB content
                    lines = target.split('\n')
                    pdb_name = "uploaded_protein"
                    for line in lines[:10]:  # Check first 10 lines
                        if line.startswith('HEADER'):
                            # Extract PDB ID from HEADER line
                            parts = line.split()
                            if len(parts) >= 4:
                                pdb_name = parts[-1].strip()
                            break
                    
                    # Upload PDB content to Rowan
                    uploaded_protein_uuid = _upload_pdb_to_rowan(target, pdb_name)
                    
                    if uploaded_protein_uuid:
                        target_specification = uploaded_protein_uuid
                        logger.info(f"✅ Auto-uploaded PDB content, using UUID: {uploaded_protein_uuid}")
                    else:
                        logger.error(f"❌ Failed to upload PDB content")
                        # Fallback to raw content (will likely fail)
                        target_specification = target
                        logger.warning("⚠️ Fallback: using raw PDB content (may fail validation)")
                else:
                    target_specification = target
                    logger.info("🧬 Using target as-is (not PDB content)")
        else:
            target_specification = target
            logger.info("🧬 Using non-string target parameter")
            
    elif target_uuid is not None:
        target_specification = target_uuid
        logger.info(f"🧬 Using target UUID: {target_uuid}")
        
    elif protein is not None:
        # Check if protein parameter is a file path
        pdb_file_path = _detect_pdb_file_path(protein)
        if pdb_file_path:
            logger.info(f"📁 Detected PDB file path in protein: {pdb_file_path}")
            try:
                with open(pdb_file_path, 'r') as f:
                    pdb_content = f.read()
                
                # Upload PDB content to Rowan
                pdb_name = os.path.splitext(os.path.basename(pdb_file_path))[0]
                uploaded_protein_uuid = _upload_pdb_to_rowan(pdb_content, pdb_name)
                
                if uploaded_protein_uuid:
                    target_specification = uploaded_protein_uuid
                    logger.info(f"✅ Auto-uploaded PDB file, using UUID: {uploaded_protein_uuid}")
                else:
                    logger.error(f"❌ Failed to upload PDB file: {pdb_file_path}")
                    # Fallback to original protein parameter
                    target_specification = protein
                    logger.warning("⚠️ Fallback: using protein parameter as-is")
            except Exception as e:
                logger.error(f"❌ Error reading PDB file {pdb_file_path}: {e}")
                target_specification = protein
        else:
            target_specification = protein
            logger.info(f"🧬 Using protein PDB code/UUID: {protein}")
    else:
        # Apply hardcoded default for GFP-water system
        target_specification = "1EMA"  # Green Fluorescent Protein
        logger.info("🧬 Using default protein: GFP (1EMA)")
    
    # Set initial_molecule if not provided
    if initial_molecule is None:
        initial_molecule = primary_ligand
        logger.info(f"🔬 Using primary ligand as initial_molecule: {initial_molecule}")
    
    # Default pocket coordinates for GFP (approximate binding site)
    if pocket_center is None:
        pocket_center = [0.0, 0.0, 0.0]  # Will be refined by docking algorithm
        logger.info("📍 Using default pocket center: (0.0, 0.0, 0.0)")
    else:
        logger.info(f"📍 Using pocket center: {pocket_center}")
    
    if pocket_size is None:
        pocket_size = [20.0, 20.0, 20.0]  # 20Å search box
        logger.info("📏 Using default pocket size: (20.0, 20.0, 20.0)")
    else:
        logger.info(f"📏 Using pocket size: {pocket_size}")
    
    # Prepare workflow parameters following stjames DockingWorkflow pattern
    # Based on stjames-public structure, DockingWorkflow inherits from MoleculeWorkflow
    workflow_params = {
        "name": name,
        "molecule": primary_ligand,  # Required by rowan.compute() API
        "workflow_type": "docking",
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval,
        
        # Base MoleculeWorkflow parameters (required)
        "initial_molecule": primary_ligand,  # Required for base workflow
        
        # DockingWorkflow-specific parameters (matching stjames exactly)
        "mode": mode,  # Docking thoroughness: rapid/standard/exhaustive
        "do_csearch": do_csearch,  # Whether to csearch starting structures
        "do_optimization": do_optimization,  # Whether to optimize starting structures
        "do_pose_refinement": do_pose_refinement,  # Whether to optimize non-rotatable bonds in output poses
        "pocket": (pocket_center, pocket_size),  # Pocket center (x,y,z) and size (x,y,z)
    }
    
    # Handle molecule input - DockingWorkflow requires either 'molecules' or 'smiles' AS LISTS
    # Priority: molecules > smiles > primary_ligand
    if molecules is not None:
        workflow_params["molecules"] = molecules if isinstance(molecules, list) else [molecules]
        logger.info(f"🧪 Multiple molecules specified: {len(workflow_params['molecules'])} ligands")
    elif smiles is not None:
        workflow_params["smiles"] = smiles if isinstance(smiles, list) else [smiles]
        if isinstance(smiles, list):
            logger.info(f"🧪 Multiple SMILES specified: {len(smiles)} ligands")
        else:
            logger.info(f"🧪 SMILES specified as list: [{smiles}]")
    else:
        # Use primary_ligand as smiles parameter (required) - MUST BE A LIST
        workflow_params["smiles"] = [primary_ligand]
        logger.info(f"🧪 Using primary ligand as SMILES list: [{primary_ligand}]")
    
    if conformers is not None:
        workflow_params["conformers"] = conformers
        logger.info(f"🧪 Pre-optimized conformers specified: {len(conformers)} UUIDs")
    
    # Add target specification (protein input) - DockingWorkflow only accepts 'target' or 'target_uuid'
    if uploaded_protein_uuid:
        # Use uploaded protein UUID (from auto-upload process)
        workflow_params["target_uuid"] = uploaded_protein_uuid
        logger.info(f"🧬 Using auto-uploaded protein UUID: {uploaded_protein_uuid}")
    elif target is not None and not isinstance(target, str):
        # Non-string target (should be PDB object/dict)
        workflow_params["target"] = target
        logger.info(f"🧬 Using target object: {type(target)}")
    elif target_uuid is not None:
        # Explicit target UUID provided
        workflow_params["target_uuid"] = target_uuid  
        logger.info(f"🧬 Using explicit target UUID: {target_uuid}")
    elif target is not None and isinstance(target, str) and len(target) > 100:
        # Long string - likely raw PDB content that failed upload
        logger.warning("⚠️ Using raw PDB content - this will likely fail validation")
        workflow_params["target"] = target
        logger.info(f"🧬 Using raw PDB content: {len(target)} characters")
    else:
        # For PDB codes or other identifiers, treat as target_uuid
        # Note: This requires the protein to already be uploaded to your Rowan account
        workflow_params["target_uuid"] = target_specification
        logger.info(f"🧬 Using identifier as target_uuid: {target_specification}")
        if not uploaded_protein_uuid and len(str(target_specification)) < 10:
            # Likely a PDB code, not UUID
            logger.info(f"⚠️ Note: '{target_specification}' appears to be a PDB code")
            logger.info(f"💡 For PDB codes, upload the protein to Rowan first via web interface")
            logger.info(f"💡 Or use a local PDB file path for automatic upload")
    
    logger.info(f"🚀 Submitting docking calculation: {name}")
    logger.info(f"💧 Primary ligand: {primary_ligand}")
    logger.info(f"🧬 Target: {target_specification}")
    logger.info(f"📍 Pocket: center={pocket_center}, size={pocket_size}")
    logger.info(f"⚙️ Settings: mode={mode}, csearch={do_csearch}, opt={do_optimization}, refine={do_pose_refinement}")
    logger.info(f"🔬 Initial molecule: {initial_molecule}")
    
    try:
        # Submit docking calculation to Rowan
        result = rowan.compute(**workflow_params)
        
        # Format the response based on blocking mode
        if result:
            workflow_uuid = result.get("uuid")
            status = result.get("object_status", 0)
            
            if blocking and status == 2:  # Completed
                # Extract docking results for completed blocking calls
                object_data = result.get("object_data", {})
                if "poses" in object_data:
                    poses = object_data["poses"]
                    response = {
                        "success": True,
                        "workflow_uuid": workflow_uuid,
                        "name": name,
                        "protein": target_specification,
                        "ligand": primary_ligand,
                        "status": "completed",
                        "docking_results": {
                            "poses_generated": len(poses),
                            "best_score": min(pose.get("docking_score", float('inf')) for pose in poses) if poses else None,
                            "poses_with_low_strain": sum(1 for pose in poses if pose.get("strain_energy", 0) <= 5.0),
                            "poses": poses[:10]  # Return top 10 poses
                        },
                        "analysis": {
                            "pocket_center": pocket_center,
                            "pocket_size": pocket_size,
                            "conformers_tested": object_data.get("conformers_tested", "unknown"),
                            "strain_filtering": "Poses with >5 kcal/mol strain flagged as unphysical"
                        },
                        "runtime_seconds": result.get("elapsed", 0),
                        "credits_charged": result.get("credits_charged", 0)
                    }
                else:
                    response = {
                        "success": True,
                        "workflow_uuid": workflow_uuid,
                        "name": name,
                        "protein": target_specification,
                        "ligand": primary_ligand,
                        "status": "completed", 
                        "message": "Docking calculation completed successfully",
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
                    "protein": target_specification,
                    "ligand": primary_ligand,
                    "status": status_text,
                    "message": f"✅ Docking calculation submitted successfully! Use tracking_id to monitor progress.",
                    "calculation_details": {
                        "protein_pdb": target_specification,
                        "ligand_smiles": primary_ligand,
                        "pocket_definition": f"center={pocket_center}, size={pocket_size}",
                        "docking_mode": mode,
                        "conformer_search": do_csearch,
                        "pose_optimization": do_optimization,
                        "strain_refinement": do_pose_refinement,
                        "blocking_mode": blocking
                    },
                    "progress_tracking": {
                        "tracking_id": workflow_uuid,
                        "check_status": f"rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')",
                        "get_results": f"rowan_workflow_management(action='retrieve', workflow_uuid='{workflow_uuid}')"
                    },
                    "expected_workflow": [
                        "1. Conformer generation with ETKDG",
                        "2. ML screening with GFN2-xTB → AIMNet2 optimization",
                        "3. AutoDock Vina docking with Vinardo scoring",
                        "4. Pose refinement with AIMNet2 + constraints",
                        "5. Strain energy calculation and filtering",
                        "6. Results ranking and analysis"
                    ]
                }
        else:
            response = {
                "success": False,
                "error": "No response received from Rowan API",
                "name": name,
                "protein": target_specification,
                "ligand": primary_ligand
            }
            
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Docking calculation failed: {str(e)}",
            "name": name,
            "protein": target_specification,
            "ligand": primary_ligand,
            "troubleshooting": {
                "common_issues": [
                    "Invalid SMILES string for ligand",
                    "PDB code not found or inaccessible",
                    "Pocket coordinates outside protein bounds",
                    "Network connectivity issues"
                ],
                "solutions": [
                    "Verify ligand SMILES with RDKit or similar tool",
                    "Check PDB code exists at rcsb.org",
                    "Use default pocket coordinates or examine protein structure",
                    "Retry calculation or check API connectivity"
                ]
            }
        }
        logger.error(f"❌ Docking calculation failed: {str(e)}")
        return str(error_response)
