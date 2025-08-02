#!/usr/bin/env python
"""Test script to debug tasks parameter issue"""

import json
import sys
sys.path.insert(0, '/Users/katherineyenko/Desktop/sandbox/rowan-mcp')

from rowan_mcp.functions_v2.submit_basic_calculation_workflow import submit_basic_calculation_workflow

# Load the test data
with open('data.json', 'r') as f:
    data = json.load(f)

print("Testing submit_basic_calculation_workflow with different tasks parameter formats...")
print("=" * 60)

# Test 1: Using SMILES directly with tasks from data.json
print("\n1. Test with tasks from data.json:")
print(f"   tasks value: {data['settings']['tasks']}")
print(f"   tasks type: {type(data['settings']['tasks'])}")

try:
    result = submit_basic_calculation_workflow(
        initial_molecule="CCCC",  # Using SMILES from data
        method="gfn2-xtb",  # Corrected method name
        tasks=data['settings']['tasks'],  # ["optimize"] from data.json
        mode=data['mode'],  # "auto" from data.json
        engine=data['engine'],  # "xtb" from data.json
        name="Test with tasks from data.json"
    )
    print(f"   ✓ Success! Workflow UUID: {result.uuid}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: With explicit list
print("\n2. Test with explicit list ['optimize']:")
try:
    result = submit_basic_calculation_workflow(
        initial_molecule="CCCC",
        method="gfn2-xtb",
        tasks=["optimize"],
        mode="auto",
        engine="xtb",
        name="Test with explicit list"
    )
    print(f"   ✓ Success! Workflow UUID: {result.uuid}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: With None (default)
print("\n3. Test with tasks=None (default):")
try:
    result = submit_basic_calculation_workflow(
        initial_molecule="CCCC",
        method="gfn2-xtb",
        tasks=None,
        mode="auto",
        engine="xtb",
        name="Test with None"
    )
    print(f"   ✓ Success! Workflow UUID: {result.uuid}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Without tasks parameter (using default)
print("\n4. Test without tasks parameter (using default):")
try:
    result = submit_basic_calculation_workflow(
        initial_molecule="CCCC",
        method="gfn2-xtb",
        mode="auto",
        engine="xtb",
        name="Test without tasks param"
    )
    print(f"   ✓ Success! Workflow UUID: {result.uuid}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Testing complete!")