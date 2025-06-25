#!/usr/bin/env python3
"""
Test script for rowan_spin_states with dynamic molecular converter.
Tests various input formats to ensure proper SMILES conversion.
"""

import sys
import os

# Add src to path so we can import the function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from functions.spin_states import rowan_spin_states

def test_spin_states_converter():
    """Test rowan_spin_states with various molecular input formats."""
    
    test_cases = [
        {
            "name": "coordination_complex_bracket_positive",
            "molecule": "[MnCl6]4+",
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+6]",
            "states": "2,4,6"
        },
        {
            "name": "coordination_complex_bracket_negative", 
            "molecule": "[MnCl6]4-",
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            "states": "2,4,6"
        },
        {
            "name": "coordination_complex_parentheses",
            "molecule": "Mn(Cl)6",
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            "states": "2,4,6"
        },
        {
            "name": "simple_formula",
            "molecule": "MnCl6", 
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            "states": "2,4,6"
        },
        {
            "name": "single_metal_atom",
            "molecule": "Mn",
            "expected_smiles": "[Mn]",
            "states": "2,4,6"
        },
        {
            "name": "iron_complex",
            "molecule": "Fe(Cl)6",
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Fe+3]",
            "states": "2,4,6"
        },
        {
            "name": "xyz_coordinates",
            "molecule": "Mn 0.0 0.0 0.0\nCl 2.3 0.0 0.0\nCl -2.3 0.0 0.0\nCl 0.0 2.3 0.0\nCl 0.0 -2.3 0.0\nCl 0.0 0.0 2.3\nCl 0.0 0.0 -2.3",
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            "states": "2,4,6"
        },
        {
            "name": "already_valid_smiles",
            "molecule": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            "expected_smiles": "[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Cl-].[Mn+2]",
            "states": "2,4,6"
        }
    ]
    
    print("🧪 Testing rowan_spin_states with molecular converter\\n")
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"Input molecule: '{case['molecule'][:50]}{'...' if len(case['molecule']) > 50 else ''}'")
        print(f"Expected SMILES: '{case['expected_smiles']}'")
        
        try:
            # Call rowan_spin_states with blocking=False to avoid API calls
            result = rowan_spin_states(
                name=f"test_{case['name']}",
                molecule=case['molecule'],
                states=case['states'],
                blocking=False  # Don't actually submit to Rowan
            )
            
            # Check if conversion happened correctly by looking for the expected SMILES in result
            if case['expected_smiles'] in result:
                print("✅ PASS - SMILES conversion successful")
                passed += 1
            else:
                print("❌ FAIL - SMILES conversion incorrect")
                print(f"Result excerpt: {result[:200]}...")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            failed += 1
        
        print("-" * 60)
    
    print(f"\\n📊 Test Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    return passed, failed


def test_molecule_conversion_only():
    """Test just the molecular conversion without API calls."""
    from functions.molecular_converter import convert_to_smiles
    
    print("\\n🔧 Testing molecular converter directly\\n")
    
    test_molecules = [
        "[MnCl6]4+",
        "[MnCl6]4-", 
        "Mn(Cl)6",
        "MnCl6",
        "Mn",
        "Fe(Cl)6",
        "H2O",
        "CH4",
        "[Cl-].[Mn+2]"  # Already valid SMILES
    ]
    
    for mol in test_molecules:
        converted = convert_to_smiles(mol)
        print(f"'{mol}' → '{converted}'")


if __name__ == "__main__":
    # Test molecular conversion first
    test_molecule_conversion_only()
    
    # Test full spin_states function
    passed, failed = test_spin_states_converter()
    
    # Exit with error code if any tests failed
    sys.exit(failed)