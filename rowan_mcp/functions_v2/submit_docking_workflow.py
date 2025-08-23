"""
Rowan v2 API: Docking Workflow
Perform molecular docking simulations for drug discovery.
"""

from typing import Optional, Dict, Any, Union, Annotated, List, Tuple
from pydantic import Field
import rowan
import stjames
import json
from stjames.pdb import PDB, read_pdb

def submit_docking_workflow(
    protein: Annotated[
        Union[str, Dict[str, Any], Any],
        Field(description="Protein for docking. Can be: 1) PDB ID string (e.g., '1HCK'), 2) Protein UUID string, 3) Dict with 'pdb_id' and optional 'name', or 4) Protein object")
    ],
    pocket: Annotated[
        Union[str, List[List[float]]],
        Field(description="Binding pocket as [[x1,y1,z1], [x2,y2,z2]] or JSON string. Defines box corners for docking site")
    ],
    initial_molecule: Annotated[
        str,
        Field(description="SMILES string or molecule object representing the ligand")
    ],
    do_csearch: Annotated[
        bool,
        Field(description="Whether to perform conformational search on the ligand before docking")
    ] = True,
    do_optimization: Annotated[
        bool,
        Field(description="Whether to optimize the ligand geometry before docking")
    ] = True,
    name: Annotated[
        str,
        Field(description="Workflow name for identification and tracking")
    ] = "Docking Workflow",
    folder_uuid: Annotated[
        Optional[str],
        Field(description="UUID of folder to organize this workflow. None uses default folder")
    ] = None,
    max_credits: Annotated[
        Optional[int],
        Field(description="Maximum credits to spend on this calculation. None for no limit")
    ] = None,
    blocking: Annotated[
        bool,
        Field(description="Whether to wait for workflow completion before returning")
    ] = False
):
    """Submits a Docking workflow to the API.
    
    Automatically handles protein creation from PDB ID and sanitization if needed.
    
    Returns:
        Workflow object representing the submitted workflow
        
    Examples:
        # Example 1: Using PDB ID directly
        result = submit_docking_workflow(
            protein="1HCK",  # PDB ID
            pocket=[[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]],
            initial_molecule="CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1",
            name="CDK2 Docking"
        )
        
        # Example 2: Using dict with PDB ID and custom name
        result = submit_docking_workflow(
            protein={"pdb_id": "1HCK", "name": "My CDK2 Protein"},
            pocket=[[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]],
            initial_molecule="CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"
        )
        
        # Example 3: Using existing protein UUID
        result = submit_docking_workflow(
            protein="abc123-def456-...",  # Protein UUID
            pocket=[[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]],
            initial_molecule="CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"
        )
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Handle protein parameter
    protein_obj = None
    
    # Check if protein is a PDB ID or dict with PDB ID
    if isinstance(protein, str):
        # Check if it's a UUID (36 chars with dashes) or PDB ID (4 chars)
        if len(protein) == 36 and '-' in protein:
            # It's a UUID, retrieve the protein
            logger.info(f"Using existing protein UUID: {protein}")
            protein_obj = rowan.retrieve_protein(protein)
        elif len(protein) <= 6:  # PDB IDs are typically 4 characters
            # It's a PDB ID, create protein from it
            logger.info(f"Creating protein from PDB ID: {protein}")
            
            # Get or create a project (REQUIRED for v2.1.1)
            project_uuid = None
            try:
                # Try to get default project
                project = rowan.default_project()
                project_uuid = project.uuid
                logger.info(f"Using default project: {project_uuid}")
            except Exception as e:
                logger.info(f"Could not get default project: {e}")
                try:
                    # List existing projects and use the first one
                    projects = rowan.list_projects(size=1)
                    if projects:
                        project_uuid = projects[0].uuid
                        logger.info(f"Using existing project: {project_uuid}")
                    else:
                        # Create a new project if none exist
                        new_project = rowan.create_project(name="Docking Project")
                        project_uuid = new_project.uuid
                        logger.info(f"Created new project: {project_uuid}")
                except Exception as e2:
                    logger.error(f"Failed to get/create project: {e2}")
                    raise ValueError(f"Cannot create protein without a valid project. Error: {e2}")
            
            # Create protein with REQUIRED project_uuid
            protein_obj = rowan.create_protein_from_pdb_id(
                name=f"Protein from {protein}",
                code=protein,
                project_uuid=project_uuid
            )
            logger.info(f"Created protein with UUID: {protein_obj.uuid}")
            
            # Sanitize the protein for docking
            logger.info("Sanitizing protein for docking...")
            try:
                protein_obj.sanitize()
                
                # Wait for sanitization to complete
                import time
                max_wait = 30
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    time.sleep(2)
                    protein_obj.refresh()
                    if protein_obj.sanitized and protein_obj.sanitized != 0:
                        logger.info(f"Protein sanitized successfully (sanitized={protein_obj.sanitized})")
                        break
                else:
                    logger.warning(f"Sanitization may not be complete after {max_wait} seconds")
            except Exception as e:
                logger.warning(f"Sanitization failed: {e}")
                logger.warning("Proceeding without sanitization - docking may fail if protein needs sanitization")
        else:
            raise ValueError(f"Invalid protein parameter: {protein}. Expected PDB ID (4 chars) or UUID (36 chars)")
            
    elif isinstance(protein, dict):
        # Dict with PDB ID and optional name
        pdb_id = protein.get('pdb_id')
        protein_name = protein.get('name', f"Protein from {pdb_id}")
        
        if not pdb_id:
            raise ValueError("Dict protein parameter must include 'pdb_id' key")
            
        logger.info(f"Creating protein '{protein_name}' from PDB ID: {pdb_id}")
        
        # Get or create a project (REQUIRED for v2.1.1)
        project_uuid = None
        try:
            # Try to get default project
            project = rowan.default_project()
            project_uuid = project.uuid
            logger.info(f"Using default project: {project_uuid}")
        except Exception as e:
            logger.info(f"Could not get default project: {e}")
            try:
                # List existing projects and use the first one
                projects = rowan.list_projects(size=1)
                if projects:
                    project_uuid = projects[0].uuid
                    logger.info(f"Using existing project: {project_uuid}")
                else:
                    # Create a new project if none exist
                    new_project = rowan.create_project(name="Docking Project")
                    project_uuid = new_project.uuid
                    logger.info(f"Created new project: {project_uuid}")
            except Exception as e2:
                logger.error(f"Failed to get/create project: {e2}")
                raise ValueError(f"Cannot create protein without a valid project. Error: {e2}")
        
        # Create protein with REQUIRED project_uuid
        protein_obj = rowan.create_protein_from_pdb_id(
            name=protein_name,
            code=pdb_id,
            project_uuid=project_uuid
        )
        logger.info(f"Created protein with UUID: {protein_obj.uuid}")
        
        # Sanitize the protein
        logger.info("Sanitizing protein for docking...")
        try:
            protein_obj.sanitize()
            
            # Wait for sanitization
            import time
            max_wait = 30
            start_time = time.time()
            while time.time() - start_time < max_wait:
                time.sleep(2)
                protein_obj.refresh()
                if protein_obj.sanitized and protein_obj.sanitized != 0:
                    logger.info(f"Protein sanitized successfully (sanitized={protein_obj.sanitized})")
                    break
            else:
                logger.warning(f"Sanitization may not be complete after {max_wait} seconds")
        except Exception as e:
            logger.warning(f"Sanitization failed: {e}")
            logger.warning("Proceeding without sanitization - docking may fail if protein needs sanitization")
            
    else:
        # Assume it's already a protein object
        protein_obj = protein
    
    # Parse pocket parameter if it's a string
    if isinstance(pocket, str):
        try:
            pocket = json.loads(pocket)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid pocket format: {pocket}. Expected [[x1,y1,z1], [x2,y2,z2]] or valid JSON string")
    
    # Ensure pocket is a list of lists
    if not isinstance(pocket, list) or len(pocket) != 2:
        raise ValueError(f"Pocket must be a list with exactly 2 coordinate lists")
    
    # Ensure each element is a list of floats
    pocket = [list(coord) for coord in pocket]
    
    # Submit the workflow
    logger.info(f"Submitting docking workflow: {name}")
    workflow = rowan.submit_docking_workflow(
        protein=protein_obj,
        pocket=pocket,
        initial_molecule=stjames.Molecule.from_smiles(initial_molecule),
        do_csearch=do_csearch,
        do_optimization=do_optimization,
        name=name,
        folder_uuid=folder_uuid,
        max_credits=max_credits
    )
    
    logger.info(f"Docking workflow submitted with UUID: {workflow.uuid}")
    
    # If blocking, wait for completion
    if blocking:
        workflow.wait_for_result()
    
    return workflow