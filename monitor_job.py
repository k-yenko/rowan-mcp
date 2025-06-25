#!/usr/bin/env python3
"""
Monitor the successfully submitted docking job.
"""

import sys
import os
import time
sys.path.append('./src')

def monitor_docking_job():
    """Monitor the docking job that was successfully submitted."""
    
    print("📊 Monitoring docking job...")
    print("=" * 60)
    
    try:
        # Import and set up rowan
        import rowan
        
        # Set the API key
        api_key = "rowan-sk07d9f425-f5f1-4be9-82de-67d970dbefe9"
        rowan.api_key = api_key
        print(f"✅ API key configured")
        
        # Use the workflow UUID from the successful submission
        workflow_uuid = "44c71ef3-7407-4d3c-9d3c-958837ce6efd"
        
        print(f"📋 Monitoring workflow: {workflow_uuid}")
        
        from functions.workflow_management import rowan_workflow_management
        
        # Monitor for up to 2 minutes
        max_checks = 24  # 24 checks * 5 seconds = 2 minutes
        check_count = 0
        
        while check_count < max_checks:
            print(f"\n🔍 Check {check_count + 1}/{max_checks}...")
            
            status_result = rowan_workflow_management(
                action='status',
                workflow_uuid=workflow_uuid
            )
            
            print(f"📊 Status: {status_result}")
            
            # Check if it's completed (status 2) or failed (status 3)
            if "Status: Completed" in status_result or "Status: 2" in status_result:
                print("🎉 Job completed successfully!")
                
                # Get full results
                print("\n📋 Getting full results...")
                results = rowan_workflow_management(
                    action='retrieve',
                    workflow_uuid=workflow_uuid
                )
                print("🎯 Final results:")
                print(results)
                break
                
            elif "Status: Failed" in status_result or "Status: 3" in status_result:
                print("❌ Job failed!")
                
                # Get error details
                print("\n📋 Getting error details...")
                error_details = rowan_workflow_management(
                    action='retrieve',
                    workflow_uuid=workflow_uuid
                )
                print("🔍 Error details:")
                print(error_details)
                break
                
            else:
                print("⏳ Job still running...")
                
            check_count += 1
            if check_count < max_checks:
                print("⏱️ Waiting 5 seconds...")
                time.sleep(5)
        
        if check_count >= max_checks:
            print("⏰ Monitoring timed out after 2 minutes")
            print("💡 Job may still be running - check manually")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    monitor_docking_job() 