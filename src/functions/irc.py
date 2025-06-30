"""
Rowan IRC (Intrinsic Reaction Coordinate) function for MCP tool integration.
"""

from typing import Any, Dict, List, Optional
import rowan

def rowan_irc(
    name: str,
    molecule: str,
    mode: str = "rapid",
    solvent: Optional[str] = None,
    preopt: bool = False,
    max_irc_steps: int = 10,
    level_of_theory: str = "gfn2_xtb",
    # Additional workflow parameters
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
        mode: Calculation mode ("rapid", "careful", "meticulous") - controls accuracy/speed tradeoff
        solvent: Solvent for the calculation (optional)
        preopt: Whether to pre-optimize the structure before IRC (default: False)
        max_irc_steps: Maximum number of IRC steps to take (default: 10)
        level_of_theory: Level of theory for the calculation (default: "gfn2_xtb")
        folder_uuid: Optional folder UUID for organization
        blocking: Whether to wait for completion (default: True)
        ping_interval: Check status interval in seconds (default: 5)
    
    Example:
        # Basic IRC calculation for a transition state
        result = rowan_irc(
            name="ts_irc_analysis",
            molecule="C1C[CH]C1",  # Example transition state SMILES
            mode="careful",  # Valid modes: rapid, careful, meticulous
            max_irc_steps=15,
            preopt=False,
            blocking=True
        )
    
    Returns:
        IRC pathway results
    """
    # Parameter validation - using actual IRCWorkflow enum values from stjames
    # Based on: https://github.com/rowansci/stjames-public/blob/master/stjames/workflows/irc.py
    valid_modes = ["rapid", "careful", "meticulous"]
    
    # Validate mode
    mode_lower = mode.lower()
    if mode_lower not in valid_modes:
        return f" Error: Invalid mode '{mode}'. Valid options: {', '.join(valid_modes)}"
    
    # IRC workflow only supports these 3 modes as defined in stjames
    
    # Validate numeric parameters
    if max_irc_steps <= 0:
        return f" Error: max_irc_steps must be positive (got {max_irc_steps})"
    if max_irc_steps > 100:
        return f" Error: max_irc_steps should be reasonable (got {max_irc_steps}, max recommended: 100)"
    
    # Validate level of theory
    valid_theories = ["gfn2_xtb", "gfn1_xtb", "b3lyp", "pbe", "m06-2x", "mp2"]
    if level_of_theory.lower() not in [theory.lower() for theory in valid_theories]:
        return f" Warning: Unusual level_of_theory '{level_of_theory}'. Common options: {', '.join(valid_theories)}"
    
    # Build parameters for Rowan API - following stjames IRCWorkflow structure
    # IRCWorkflow expects mode as top-level parameter with other params also at top-level
    workflow_params = {
        "name": name,
        "molecule": molecule,
        "workflow_type": "irc",
        "mode": mode_lower,  # Mode is top-level parameter (required by IRCWorkflow)
        "preopt": preopt,    # IRC-specific parameters at top-level
        "max_irc_steps": max_irc_steps,
        "level_of_theory": level_of_theory.lower(),
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
    # Add solvent if specified
    if solvent:
        workflow_params["solvent"] = solvent.lower()
    
    try:
        # Submit IRC calculation to Rowan
        result = rowan.compute(**workflow_params)
        return str(result)
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"IRC calculation failed: {str(e)}",
            "name": name,
            "molecule": molecule
        }
        return str(error_response)

def test_rowan_irc():
    """Test the rowan_irc function with actual Rowan API response."""
    try:
        print(" Testing IRC with actual Rowan API call...")
        
        # Test with minimal parameters - actually wait for result
        result = rowan_irc(
            name="test_irc_valid_modes",
            molecule="C=C",  # Simple molecule that should work
            mode="rapid",    # Valid mode from IRCWorkflow enum
            max_irc_steps=5,  # Short for testing
            blocking=True,   # Actually wait for completion
            ping_interval=2  # Check every 2 seconds
        )
        
        print(f" Raw result: {result}")
        
        # Check if result contains error
        if "Error" in str(result) or "failed" in str(result).lower():
            print(f" IRC test failed with error: {result}")
            return False
        
        # Try to parse the result to check for success indicators
        if "uuid" in str(result).lower() and ("status" in str(result).lower() or "object_status" in str(result).lower()):
            print(" IRC test successful - workflow submitted and processed!")
            return True
        else:
            print(f" IRC test completed but result unclear: {result}")
            return False
            
    except Exception as e:
        print(f" IRC test failed with exception: {e}")
        return False

if __name__ == "__main__":
    test_rowan_irc() 