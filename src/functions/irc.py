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
        mode: Calculation mode ("rapid", "balanced", "thorough") - controls accuracy/speed tradeoff
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
            mode="rapid",
            max_irc_steps=15,
            preopt=False,
            blocking=True
        )
    
    Returns:
        IRC pathway results
    """
    # Parameter validation
    valid_modes = ["rapid", "balanced", "thorough", "reckless"]
    
    # Validate mode
    mode_lower = mode.lower()
    if mode_lower not in valid_modes:
        return f"❌ Error: Invalid mode '{mode}'. Valid options: {', '.join(valid_modes)}"
    
    # Validate mode restrictions
    if mode_lower == "reckless":
        return f"❌ Error: 'reckless' mode is not allowed for IRC calculations"
    
    # Validate numeric parameters
    if max_irc_steps <= 0:
        return f"❌ Error: max_irc_steps must be positive (got {max_irc_steps})"
    if max_irc_steps > 100:
        return f"❌ Error: max_irc_steps should be reasonable (got {max_irc_steps}, max recommended: 100)"
    
    # Validate level of theory
    valid_theories = ["gfn2_xtb", "gfn1_xtb", "b3lyp", "pbe", "m06-2x", "mp2"]
    if level_of_theory.lower() not in [theory.lower() for theory in valid_theories]:
        return f"❌ Warning: Unusual level_of_theory '{level_of_theory}'. Common options: {', '.join(valid_theories)}"
    
    # Build IRC settings
    irc_settings = {
        "mode": mode_lower,
        "preopt": preopt,
        "max_irc_steps": max_irc_steps,
        "level_of_theory": level_of_theory.lower()
    }
    
    # Add solvent if specified
    if solvent:
        irc_settings["solvent"] = solvent.lower()
    
    # Build parameters for Rowan API
    workflow_params = {
        "name": name,
        "molecule": molecule,
        "workflow_type": "irc",
        "settings": irc_settings,
        "folder_uuid": folder_uuid,
        "blocking": blocking,
        "ping_interval": ping_interval
    }
    
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
    """Test the rowan_irc function."""
    try:
        # Test with minimal parameters
        result = rowan_irc(
            name="test_irc_ts",
            molecule="CC[CH]C",  # Simple transition state example
            mode="rapid",
            max_irc_steps=5,  # Short for testing
            blocking=False
        )
        print("✅ IRC test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ IRC test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_irc() 