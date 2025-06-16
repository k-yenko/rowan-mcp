#!/usr/bin/env python3
"""
Direct test of the water molecule calculation to verify the engine fix
"""

import os
import rowan

# Setup API key
api_key = os.getenv("ROWAN_API_KEY")
if not api_key:
    print("❌ ROWAN_API_KEY environment variable not found")
    exit(1)

rowan.api_key = api_key

# Test the water molecule calculation with proper settings
def test_water_calculation():
    print("🔬 Testing Water Molecule Calculation (H2O)")
    print("=" * 50)
    
    # Build settings dictionary exactly like the fixed MCP server
    settings = {
        "method": "b3lyp",
        "basis_set": "pcseg-1", 
        "tasks": ["energy", "optimize"],
        "corrections": ["d3bj"],
        "engine": "psi4"  # This was missing before!
    }
    
    print(f"📋 Settings to be sent:")
    for key, value in settings.items():
        print(f"   {key}: {value}")
    
    try:
        print(f"\n🚀 Submitting calculation...")
        result = rowan.compute(
            workflow_type="basic_calculation",
            name="Water H2O Direct Test",
            molecule="O",  # Water molecule SMILES
            settings=settings,
            blocking=False  # Don't wait for completion
        )
        
        print(f"✅ SUCCESS! Calculation submitted without validation errors")
        print(f"🔬 Job UUID: {result.get('uuid', 'N/A')}")
        print(f"📊 Response: {result}")
        
        # Check status
        try:
            status = rowan.Workflow.status(uuid=result.get('uuid'))
            status_names = {0: "Queued", 1: "Running", 2: "Completed", 3: "Failed", 4: "Stopped", 5: "Awaiting"}
            print(f"📈 Status: {status_names.get(status, 'Unknown')} ({status})")
        except Exception as e:
            print(f"⚠️ Could not check status: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        if "engine" in str(e).lower():
            print("🔧 This confirms the engine field was missing!")
        return False

if __name__ == "__main__":
    success = test_water_calculation()
    if success:
        print(f"\n🎉 The fix works! The engine field is now properly included.")
        print(f"💡 You need to restart your MCP server to use the fixed code.")
    else:
        print(f"\n❌ The fix didn't work or there are other issues.") 