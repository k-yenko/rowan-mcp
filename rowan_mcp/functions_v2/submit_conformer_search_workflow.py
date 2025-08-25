"""
Rowan v2 API: Conformer Search Workflow
Search for low-energy molecular conformations using various methods.
"""

from typing import Any, Dict, Annotated
import rowan
import stjames

def submit_conformer_search_workflow(
    initial_molecule: Annotated[str, "SMILES string representing the initial structure"],
    conf_gen_mode: Annotated[str, "Conformer generation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)"] = "rapid",
    final_method: Annotated[str, "Final optimization method (e.g., 'aimnet2_wb97md3', 'r2scan_3c', 'wb97x-d3_def2-tzvp')"] = "aimnet2_wb97md3",
    solvent: Annotated[str, "Solvent for implicit solvation (SMILES or name). Empty string for vacuum"] = "",
    transition_state: Annotated[bool, "Whether to search for transition state conformers"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Conformer Search Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a conformer search workflow using Rowan v2 API.
    
    Args:
        initial_molecule: SMILES string representing the initial structure
        conf_gen_mode: Conformer generation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)
        final_method: Final optimization method (e.g., 'aimnet2_wb97md3', 'r2scan_3c', 'wb97x-d3_def2-tzvp')
        solvent: Solvent for implicit solvation (e.g., 'water', 'ethanol', 'dmso'). Empty string for gas phase.
        transition_state: Whether to search for transition state conformers
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.
    
    Conformer Generation Modes:
    - 'rapid': RDKit/MMFF, 300 conformers, 0.10 Å RMSD cutoff (recommended for most work)
    - 'careful': CREST/GFN-FF quick mode, 150 conformers max
    - 'meticulous': CREST/GFN2-xTB normal mode, 500 conformers max
    
    Returns:
        Workflow object representing the submitted workflow
        
    Examples:
        # Simple diethyl ether conformer search
        result = submit_conformer_search_workflow(
            initial_molecule="CCOCC"
        )
        
        # Basic butane conformer search with rapid mode
        result = submit_conformer_search_workflow(
            initial_molecule="CCCC",
            conf_gen_mode="rapid"
        )
        
        # Careful search with solvent
        result = submit_conformer_search_workflow(
            initial_molecule="CC(C)CC(=O)O",
            conf_gen_mode="careful",
            solvent="water",
            final_method="r2scan_3c"
        )
    """

    try:
        # Convert initial_molecule to appropriate format
        if isinstance(initial_molecule, str):
            # Try to parse as SMILES
            try:
                mol = stjames.Molecule.from_smiles(initial_molecule)
                initial_molecule = mol.model_dump()
            except Exception:
                # If fails, pass as dict with smiles
                initial_molecule = {"smiles": initial_molecule}
        elif isinstance(initial_molecule, dict):
            # Already in dict format
            pass
        elif hasattr(initial_molecule, 'model_dump'):
            # StJamesMolecule
            initial_molecule = initial_molecule.model_dump()
        else:
            # Assume RdkitMol or similar
            try:
                from rdkit import Chem
                mol = stjames.Molecule.from_rdkit(initial_molecule, cid=0)
                initial_molecule = mol.model_dump()
            except:
                pass
        
        # Convert final_method to Method if it's a string
        if isinstance(final_method, str):
            final_method = stjames.Method(final_method)
        
        # Determine solvent model based on method
        solvent_model = None
        if solvent:
            solvent_model = "alpb" if final_method in stjames.XTB_METHODS else "cpcm"
        
        # Create optimization settings following official API
        opt_settings = stjames.Settings(
            method=final_method,
            tasks=["optimize"],
            mode=stjames.Mode.AUTO,
            solvent_settings={"solvent": solvent, "model": solvent_model} if solvent else None,
            opt_settings={"transition_state": transition_state, "constraints": []},
        )
        
        # Create MultiStageOptSettings
        msos = stjames.MultiStageOptSettings(
            mode=stjames.Mode.MANUAL,
            xtb_preopt=True,
            optimization_settings=[opt_settings],
        )
        
        # Convert to dict and fix the soscf field
        msos_dict = msos.model_dump()
        
        # Fix soscf: convert boolean to string enum
        if 'optimization_settings' in msos_dict:
            for opt_setting in msos_dict['optimization_settings']:
                if 'scf_settings' in opt_setting and 'soscf' in opt_setting['scf_settings']:
                    soscf_val = opt_setting['scf_settings']['soscf']
                    if isinstance(soscf_val, bool):
                        if soscf_val is False:
                            opt_setting['scf_settings']['soscf'] = 'never'
                        elif soscf_val is True:
                            opt_setting['scf_settings']['soscf'] = 'always'
                    elif soscf_val is None:
                        # Default to smart behavior
                        opt_setting['scf_settings']['soscf'] = 'upon_failure'
        
        # Build workflow_data
        workflow_data = {
            "multistage_opt_settings": msos_dict,
            "conf_gen_mode": conf_gen_mode,
            "mso_mode": "manual",
            "solvent": solvent if solvent else None,
            "transition_state": transition_state,
        }
        
        # Build the API request
        data = {
            "name": name,
            "folder_uuid": folder_uuid if folder_uuid else None,
            "workflow_type": "conformer_search",
            "workflow_data": workflow_data,
            "initial_molecule": initial_molecule,
            "max_credits": max_credits if max_credits > 0 else None,
        }
        
        # Submit to API
        from rowan.utils import api_client
        from rowan import Workflow
        
        with api_client() as client:
            response = client.post("/workflow", json=data)
            response.raise_for_status()
            return Workflow(**response.json())
        
    except Exception as e:
        # Re-raise the exception so MCP can handle it
        raise e