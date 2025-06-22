"""
Rowan solubility prediction function for MCP tool integration.
"""

from typing import Optional, Union, List, Dict, Any
import rowan


def rowan_solubility(
    name: str,
    molecule: str,
    solvents: Optional[Union[str, List[str]]] = None,
    temperatures: Optional[Union[str, List[Union[str, float]]]] = None,
    folder_uuid: Optional[str] = None,
    blocking: bool = False,  # Changed to False to avoid timeouts
    ping_interval: int = 5
) -> str:
    """Predict molecular solubility in multiple solvents at various temperatures using machine learning.
    
    This tool calculates solubility (log S) predictions for a molecule across different solvents 
    and temperatures. Returns immediately with workflow UUID for progress tracking.
    
    Args:
        name: Name for the solubility calculation
        molecule: SMILES string of the molecule
        solvents: Solvent specification. Supports:
            - Comma-separated: "water,ethanol,hexane" 
            - JSON array: '["O", "CCO", "CCCCCC"]'
            - Single: "water" or "O"
        temperatures: Temperature specification in Celsius or Kelvin. Supports:
            - Comma-separated: "25,37,50" 
            - JSON array: "[298.15, 310.15, 323.15]"
            - Single: "25" or "298.15"
        folder_uuid: Optional folder UUID to organize the calculation
        blocking: Whether to wait for completion (default: False to avoid timeouts)
        ping_interval: Interval in seconds to check calculation status
        
    Returns:
        JSON string with workflow UUID and status (non-blocking) or full results (blocking)
        
    Examples:
        # Comma-separated (user-friendly)
        rowan_solubility(
            name="acetaminophen_analysis",
            molecule="CC(=O)Nc1ccc(O)cc1",
            solvents="water,ethanol,hexane",
            temperatures="25,37,50"
        )
        
        # JSON arrays (precise)
        rowan_solubility(
            name="precise_analysis", 
            molecule="CC(=O)Nc1ccc(O)cc1",
            solvents='["O", "CCO", "CCCCCC"]',
            temperatures='[298.15, 310.15, 323.15]'
        )
    """
    
    # Handle multiple solvent input formats
    if solvents is not None and isinstance(solvents, str):
        # Try to parse as JSON first (for MCP tool calls)
        try:
            import json
            if solvents.startswith('[') and solvents.endswith(']'):
                solvents = json.loads(solvents)
            elif ',' in solvents:
                # Handle comma-separated string
                solvents = [s.strip() for s in solvents.split(',')]
            else:
                # Single solvent string
                solvents = [solvents]
        except json.JSONDecodeError:
            # JSON parsing failed, try comma-separated
            if ',' in solvents:
                solvents = [s.strip() for s in solvents.split(',')]
            else:
                solvents = [solvents]
    
    # Convert solvent names to SMILES if needed
    if solvents is not None:
        solvents = convert_solvent_names_to_smiles(solvents)
    
    # Default temperatures if none provided (room temp to moderate heating)
    if temperatures is None:
        temperatures = [273.15, 298.15, 323.15, 348.15, 373.15]  # K
    
    # Handle multiple temperature input formats
    if isinstance(temperatures, str):
        # Try to parse as JSON first (for MCP tool calls)
        try:
            import json
            if temperatures.strip().startswith('[') and temperatures.strip().endswith(']'):
                parsed_temps = json.loads(temperatures.strip())
                if isinstance(parsed_temps, list):
                    temperatures = parsed_temps
                else:
                    temperatures = [parsed_temps]
            elif ',' in temperatures:
                # Handle comma-separated string
                temperatures = [t.strip() for t in temperatures.split(',')]
            else:
                # Single temperature string
                temperatures = [temperatures.strip()]
        except (json.JSONDecodeError, ValueError) as e:
            # JSON parsing failed, try comma-separated
            if ',' in temperatures:
                temperatures = [t.strip() for t in temperatures.split(',')]
            else:
                temperatures = [temperatures.strip()]
    elif isinstance(temperatures, (float, int)):
        temperatures = [temperatures]
    elif isinstance(temperatures, list):
        # Already a list, keep as is
        pass
    else:
        raise ValueError(f"Invalid temperatures parameter type: {type(temperatures)}. Expected string, number, or list.")
    
    # Convert temperature strings to floats and handle Celsius conversion
    processed_temps = []
    for temp in temperatures:
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except ValueError as e:
                raise ValueError(f"Invalid temperature value: '{temp}'. Expected a number, got: {e}")
        elif isinstance(temp, (int, float)):
            temp = float(temp)
        else:
            raise ValueError(f"Invalid temperature type: {type(temp)}. Expected string or number.")
        
        # Assume Celsius if temperature is < 200, convert to Kelvin
        if temp < 200:
            temp += 273.15
        processed_temps.append(temp)
    
    # Prepare workflow parameters
    workflow_params = {
        "name": name,
        "molecule": molecule,  # Required by rowan.compute() API
        "workflow_type": "solubility",
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval,
        # Workflow-specific parameters for SolubilityWorkflow
        "initial_smiles": molecule,  # Required by SolubilityWorkflow Pydantic model
        "solvents": solvents,
        "temperatures": processed_temps
    }
    
    try:
        # Submit solubility calculation to Rowan
        result = rowan.compute(**workflow_params)
        
        # Format the response based on blocking mode
        if result:
            workflow_uuid = result.get("uuid")
            status = result.get("object_status", 0)
            
            if blocking and status == 2:  # Completed
                # Extract solubility results for completed blocking calls
                object_data = result.get("object_data", {})
                if "solubilities" in object_data:
                    response = {
                        "success": True,
                        "workflow_uuid": workflow_uuid,
                        "name": name,
                        "molecule": molecule,
                        "status": "completed",
                        "solubility_results": object_data["solubilities"],
                        "summary": f"Completed solubility calculation for {len(solvents) if solvents else 'default'} solvents at {len(processed_temps)} temperatures",
                        "runtime_seconds": result.get("elapsed", 0),
                        "credits_charged": result.get("credits_charged", 0)
                    }
                else:
                    response = {
                        "success": True,
                        "workflow_uuid": workflow_uuid,
                        "name": name,
                        "molecule": molecule,
                        "status": "completed", 
                        "message": "Solubility calculation completed successfully",
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
                    "molecule": molecule,
                    "status": status_text,
                    "message": f"✅ Solubility calculation submitted successfully! Use tracking_id to monitor progress.",
                    "calculation_details": {
                        "solvents_count": len(solvents) if solvents else 0,
                        "temperatures_count": len(processed_temps),
                        "blocking_mode": blocking
                    },
                    "progress_tracking": {
                        "tracking_id": workflow_uuid,
                        "check_status": f"rowan_workflow_management(action='status', workflow_uuid='{workflow_uuid}')",
                        "get_results": f"rowan_workflow_management(action='retrieve', workflow_uuid='{workflow_uuid}')"
                    }
                }
        else:
            response = {
                "success": False,
                "error": "No response received from Rowan API",
                "name": name,
                "molecule": molecule
            }
            
        return str(response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Solubility calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)


# Solvent name to SMILES mapping for convenience
SOLVENT_SMILES = {
    "water": "O",
    "ethanol": "CCO", 
    "methanol": "CO",
    "hexane": "CCCCCC",
    "toluene": "CC1=CC=CC=C1",
    "thf": "C1CCCO1",
    "tetrahydrofuran": "C1CCCO1",
    "ethyl_acetate": "CC(=O)OCC",
    "acetonitrile": "CC#N",
    "dmso": "CS(=O)C",
    "acetone": "CC(=O)C",
    "propanone": "CC(=O)C",
    "chloroform": "ClCCl",
    "dichloromethane": "ClCCl"
}


def convert_solvent_names_to_smiles(solvents: List[str]) -> List[str]:
    """
    Convert common solvent names to SMILES strings.
    
    Args:
        solvents: List of solvent names or SMILES
        
    Returns:
        List of SMILES strings
    """
    converted = []
    for solvent in solvents:
        # If it's already a SMILES (contains typical SMILES characters), keep as is
        if any(char in solvent for char in ['=', '#', '(', ')', '[', ']']):
            converted.append(solvent)
        else:
            # Try to convert from name to SMILES
            solvent_lower = solvent.lower().replace(' ', '_')
            converted.append(SOLVENT_SMILES.get(solvent_lower, solvent))
    
    return converted


def test_rowan_solubility():
    """Test the rowan_solubility function with hardcoded values."""
    try:
        result = rowan_solubility("test_acetaminophen_solubility", "dummy_molecule")
        print("✅ Solubility test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Solubility test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_solubility()
