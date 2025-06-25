#!/usr/bin/env python3
"""
Test the enhanced docking function with automatic PDB upload capability.
"""

import sys
import os
import time
sys.path.append('./src')

def test_enhanced_docking():
    """Test enhanced docking function with local PDB file."""
    
    print("🚀 Testing ENHANCED docking with automatic PDB upload...")
    print("=" * 70)
    
    try:
        # Import and set up rowan
        import rowan
        
        # Set the API key
        api_key = "rowan-sk07d9f425-f5f1-4be9-82de-67d970dbefe9"
        rowan.api_key = api_key
        print(f"✅ API key configured")
        
        from functions.docking import rowan_docking
        from functions.workflow_management import rowan_workflow_management
        
        print(f"\n🧪 Testing enhanced docking with 1ema.pdb auto-upload...")
        print("This should automatically:")
        print("1. 📁 Detect 1ema.pdb as a local file")
        print("2. 📤 Upload it to Rowan")
        print("3. 🔗 Use the returned UUID for docking")
        print("4. 🧬 Run GFP + water docking")
        
        # Test the enhanced function
        result = rowan_docking(
            name="enhanced_auto_upload_test",
            protein="1ema.pdb",  # This should auto-detect and upload
            ligand="O",  # Water
            blocking=False
        )
        
        print("✅ Enhanced docking submitted!")
        print(f"📊 Result: {result}")
        
        # Monitor completion
        import ast
        result_dict = ast.literal_eval(result)
        tracking_id = result_dict.get('tracking_id')
        
        if tracking_id:
            print(f"\n⏳ Monitoring enhanced docking completion...")
            print(f"🆔 Tracking ID: {tracking_id}")
            
            max_wait = 600  # 10 minutes
            wait_time = 0
            
            while wait_time < max_wait:
                print(f"\n⏰ Status check at {wait_time}s...")
                
                status_result = rowan_workflow_management(
                    action='status',
                    workflow_uuid=tracking_id
                )
                
                print(f"Status: {status_result}")
                
                try:
                    status_dict = ast.literal_eval(status_result)
                    current_status = status_dict.get('status', 'unknown')
                    
                    print(f"Current status: {current_status}")
                    
                    if current_status == 'completed':
                        print(f"\n🎉 ENHANCED DOCKING COMPLETED SUCCESSFULLY!")
                        
                        final_result = rowan_workflow_management(
                            action='retrieve',
                            workflow_uuid=tracking_id
                        )
                        
                        print(f"\n📊 ===== ENHANCED DOCKING SUCCESS =====")
                        print(final_result)
                        print(f"📊 ===== END SUCCESS RESULTS =====")
                        
                        print(f"\n✅ SUCCESS: Enhanced docking with auto-upload works!")
                        return True
                        
                    elif current_status == 'failed':
                        print(f"\n❌ ENHANCED DOCKING FAILED!")
                        
                        error_result = rowan_workflow_management(
                            action='retrieve',
                            workflow_uuid=tracking_id
                        )
                        
                        print(f"\n📋 ===== ENHANCED DOCKING ERROR LOGS =====")
                        print(error_result)
                        print(f"📋 ===== END ERROR LOGS =====")
                        return False
                        
                    elif current_status in ['queued', 'running']:
                        print(f"⏳ Enhanced docking still {current_status}... waiting...")
                    else:
                        print(f"❓ Unknown status: {current_status}")
                        
                except Exception as parse_error:
                    print(f"⚠️ Parse error: {parse_error}")
                    print(f"Raw response: {status_result}")
                
                time.sleep(30)  # Check every 30 seconds
                wait_time += 30
            
            # Timeout
            print(f"\n⏰ TIMEOUT ({max_wait}s). Final check...")
            final_status = rowan_workflow_management(
                action='retrieve',
                workflow_uuid=tracking_id
            )
            print(f"Final: {final_status}")
            return False
        
        else:
            print("❌ No tracking ID found")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced docking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_docking() 