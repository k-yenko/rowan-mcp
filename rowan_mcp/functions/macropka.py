"""MacropKa workflow function for MCP server."""

import os
import json
import logging
from typing import Optional, Union, List

import rowan

# Configure logging
logger = logging.getLogger(__name__)

# Get API key from environment
api_key = os.environ.get("ROWAN_API_KEY")
if api_key:
    rowan.api_key = api_key
else:
    logger.warning("ROWAN_API_KEY not found in environment")


def log_rowan_api_call(func_name: str, **kwargs):
    """Log Rowan API calls for debugging."""
    logger.debug(f"Calling {func_name} with args: {kwargs}")


def rowan_macropka(
    name: str,
    molecule: str,
    min_pH: float = 0.0,
    max_pH: float = 14.0,
    max_charge: int = 2,
    min_charge: int = -2,
    compute_aqueous_solubility: bool = False,
    compute_solvation_energy: bool = True,
    folder_uuid: Optional[str] = None,
    blocking: bool = True,
    ping_interval: int = 5
) -> str:
    """
    Calculate macroscopic pKa values and related properties for a molecule.
    
    This workflow computes pKa values, microstates, isoelectric point, and optionally
    solvation energy and aqueous solubility across different pH values.
    
    Args:
        name: Name for the calculation
        molecule: SMILES string of the molecule
        min_pH: Minimum pH for calculations (default: 0.0)
        max_pH: Maximum pH for calculations (default: 14.0)
        max_charge: Maximum charge to consider for microstates (default: 2)
        min_charge: Minimum charge to consider for microstates (default: -2)
        compute_aqueous_solubility: Whether to compute aqueous solubility by pH (default: False)
        compute_solvation_energy: Whether to compute solvation energy for Kpuu (default: True)
        folder_uuid: UUID of folder to save results in
        blocking: Wait for calculation to complete (default: True)
        ping_interval: How often to check status in blocking mode (default: 5 seconds)
        
    Returns:
        String with workflow UUID or results depending on blocking mode
    """
    try:
        # Validate pH range
        if min_pH >= max_pH:
            return json.dumps({"error": "min_pH must be less than max_pH"})
        
        # Validate charge range  
        if min_charge >= max_charge:
            return json.dumps({"error": "min_charge must be less than max_charge"})
            
        # Log the API call
        log_rowan_api_call(
            "rowan.compute",
            workflow_type="macropka",
            name=name,
            molecule=molecule,
            min_pH=min_pH,
            max_pH=max_pH,
            max_charge=max_charge,
            min_charge=min_charge,
            compute_aqueous_solubility=compute_aqueous_solubility,
            compute_solvation_energy=compute_solvation_energy,
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval
        )
        
        # Submit calculation
        result = rowan.compute(
            workflow_type="macropka",
            name=name,
            molecule=molecule,  # Required by rowan.compute() API
            folder_uuid=folder_uuid,
            blocking=blocking,
            ping_interval=ping_interval,
            # Workflow-specific parameters for MacropKaWorkflow
            initial_smiles=molecule,  # Required by MacropKaWorkflow Pydantic model
            min_pH=min_pH,
            max_pH=max_pH,
            max_charge=max_charge,
            min_charge=min_charge,
            compute_aqueous_solubility=compute_aqueous_solubility,
            compute_solvation_energy=compute_solvation_energy
        )
        
        if blocking:
            # Format completed results
            status = result.get("status", "unknown")
            uuid = result.get("uuid", "unknown")
            
            if status == "success":
                object_data = result.get("object_data", {})
                
                # Extract key results
                microstates = object_data.get("microstates", [])
                pka_values = object_data.get("pKa_values", [])
                isoelectric_point = object_data.get("isoelectric_point")
                solvation_energy = object_data.get("solvation_energy")
                kpuu_probability = object_data.get("kpuu_probability")
                microstate_weights_by_pH = object_data.get("microstate_weights_by_pH", [])
                logD_by_pH = object_data.get("logD_by_pH", [])
                aqueous_solubility_by_pH = object_data.get("aqueous_solubility_by_pH", [])
                
                formatted = f"✅ MacropKa calculation completed successfully!\n"
                formatted += f"🔖 Workflow UUID: {uuid}\n"
                formatted += f"📋 Status: {status}\n\n"
                
                # Format pKa values
                if pka_values:
                    formatted += "📊 pKa Values:\n"
                    for pka in pka_values:
                        formatted += f"   • {pka.get('initial_charge', 'N/A')} → {pka.get('final_charge', 'N/A')}: pKa = {pka.get('pKa', 'N/A')}\n"
                    formatted += "\n"
                
                # Format microstates
                if microstates:
                    formatted += f"🔬 Microstates ({len(microstates)} found):\n"
                    for i, microstate in enumerate(microstates[:5]):  # Show first 5
                        formatted += f"   {i+1}. Charge: {microstate.get('charge', 'N/A')}, Energy: {microstate.get('energy', 'N/A')} kcal/mol\n"
                    if len(microstates) > 5:
                        formatted += f"   ... and {len(microstates) - 5} more\n"
                    formatted += "\n"
                
                # Add other properties
                if isoelectric_point is not None:
                    formatted += f"⚡ Isoelectric Point: pH {isoelectric_point}\n"
                
                if solvation_energy is not None:
                    formatted += f"💧 Solvation Energy: {solvation_energy} kcal/mol\n"
                    
                if kpuu_probability is not None:
                    formatted += f"🧠 Kpuu Probability (≥0.3): {kpuu_probability:.2%}\n"
                
                # Show pH-dependent properties if available
                if logD_by_pH:
                    formatted += f"\n📈 logD values available for {len(logD_by_pH)} pH points\n"
                    
                if aqueous_solubility_by_pH:
                    formatted += f"💧 Aqueous solubility values available for {len(aqueous_solubility_by_pH)} pH points\n"
                    
                if microstate_weights_by_pH:
                    formatted += f"⚖️  Microstate weights available for {len(microstate_weights_by_pH)} pH points\n"
                
                return formatted
            else:
                # Handle failed calculation
                return f"❌ MacropKa calculation failed\n🔖 UUID: {uuid}\n📋 Status: {status}\n💬 Check workflow details for more information"
        else:
            # Non-blocking mode - return submission confirmation
            uuid = result.get("uuid", "unknown")
            formatted = f"📋 MacropKa calculation submitted!\n"
            formatted += f"🔖 Workflow UUID: {uuid}\n"
            formatted += f"⏳ Status: Running...\n"
            formatted += f"💡 Use rowan_workflow_management to check status\n"
            formatted += f"\nCalculation parameters:\n"
            formatted += f"   • pH range: {min_pH} - {max_pH}\n"
            formatted += f"   • Charge range: {min_charge} to {max_charge}\n"
            formatted += f"   • Compute solvation energy: {compute_solvation_energy}\n"
            formatted += f"   • Compute aqueous solubility: {compute_aqueous_solubility}\n"
            return formatted
            
    except Exception as e:
        logger.error(f"Error in rowan_macropka: {str(e)}")
        return json.dumps({"error": str(e)})


# Test function
if __name__ == "__main__":
    # Test with ethanol
    result = rowan_macropka(
        name="Ethanol MacropKa Test",
        molecule="CCO",
        compute_aqueous_solubility=True,
        blocking=True
    )
    print(result)