#!/usr/bin/env python3
"""
Check the status of the new MD workflows
"""

import os
import rowan
import time

# Set the API key
os.environ['ROWAN_API_KEY'] = 'rowan-sk07d9f425-f5f1-4be9-82de-67d970dbefe9'
rowan.api_key = os.environ['ROWAN_API_KEY']

# Get recently submitted workflows
print("Retrieving recent workflows...")

# Get workflows from the last few minutes
workflows = rowan.Workflow.list(parent_uuid='e5c3ce65-43df-4ab3-90e0-a56f42584cc0', limit=10)

status_names = {
    0: "⏳ Queued",
    1: "🔄 Running", 
    2: "✅ Completed",
    3: "❌ Failed",
    4: "⏹️ Stopped",
    5: "⏸️ Awaiting Queue"
}

print("\nRecent MD workflows:")
print("-" * 80)

for wf in workflows:
    if wf['object_type'] == 'molecular_dynamics' and 'test_' in wf['name']:
        status = wf.get('object_status', wf.get('status', 'Unknown'))
        status_text = status_names.get(status, f"Unknown ({status})")
        
        print(f"Name: {wf['name']}")
        print(f"UUID: {wf['uuid']}")
        print(f"Status: {status_text}")
        print(f"Created: {wf['created_at']}")
        
        # If failed, try to get error details
        if status == 3:
            try:
                full_result = rowan.Workflow.retrieve(uuid=wf['uuid'])
                if 'object_logfile' in full_result:
                    print(f"Error: {full_result['object_logfile'][:200]}...")
            except:
                pass
        
        print("-" * 40)