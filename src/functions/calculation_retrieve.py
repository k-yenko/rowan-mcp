"""
Rowan calculation retrieval functions for MCP tool integration.
"""

from typing import Optional, Dict, Any
import rowan


def rowan_calculation_retrieve(calculation_uuid: str) -> str:
    """Retrieve details of a specific calculation.
    
    Args:
        calculation_uuid: UUID of the calculation to retrieve
    
    Returns:
        Calculation details
    """
    
    try:
        calculation = rowan.Calculation.retrieve(uuid=calculation_uuid)
        return format_calculation_details(calculation, calculation_uuid)
                
    except Exception as e:
        return f"❌ Error retrieving calculation: {str(e)}"


# Fallback error handling removed - keeping function simple and focused


def format_calculation_details(calculation: Dict[str, Any], calculation_uuid: str) -> str:
    """Format calculation details for display."""
    
    formatted = f"⚙️ **Calculation Details:**\n\n"
    formatted += f"📝 Name: {calculation.get('name', 'N/A')}\n"
    formatted += f"🆔 UUID: {calculation_uuid}\n"
    formatted += f"📊 Status: {calculation.get('status', 'Unknown')}\n"
    formatted += f"⏱️ Elapsed: {calculation.get('elapsed', 0):.3f}s\n"
    
    # Settings information
    settings = calculation.get('settings', {})
    if settings:
        formatted += f"\n⚙️ **Settings:**\n"
        formatted += f"   Method: {settings.get('method', 'N/A')}\n"
        if settings.get('basis_set'):
            formatted += f"   Basis Set: {settings.get('basis_set')}\n"
        if settings.get('tasks'):
            formatted += f"   Tasks: {', '.join(settings.get('tasks', []))}\n"
    
    # Molecule information
    molecules = calculation.get('molecules', [])
    if molecules:
        formatted += f"\n🧪 **Molecules:** {len(molecules)} structure(s)\n"
        if len(molecules) > 0 and isinstance(molecules[0], dict):
            first_mol = molecules[0]
            if 'smiles' in first_mol:
                formatted += f"   Primary SMILES: {first_mol['smiles']}\n"
    
    # Results/output data
    if 'output' in calculation:
        output = calculation['output']
        formatted += f"\n📊 **Results Available:**\n"
        if isinstance(output, dict):
            for key, value in list(output.items())[:5]:  # Show first 5 items
                if isinstance(value, (int, float)):
                    formatted += f"   {key}: {value:.4f}\n"
                elif isinstance(value, str) and len(value) < 50:
                    formatted += f"   {key}: {value}\n"
                elif isinstance(value, list) and len(value) < 10:
                    formatted += f"   {key}: {value}\n"
                else:
                    formatted += f"   {key}: <complex data>\n"
        else:
            formatted += f"   Raw output: {str(output)[:200]}...\n"
    
    return formatted


# Specialized object data formatting removed - keeping function simple


def test_rowan_calculation_retrieve():
    """Test the calculation retrieve function."""
    try:
        # Test with a dummy UUID to see error handling
        result = rowan_calculation_retrieve("test-uuid-123")
        print("✅ Calculation retrieve test successful!")
        print(f"Sample result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Calculation retrieve test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_calculation_retrieve() 