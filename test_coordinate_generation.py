#!/usr/bin/env python3
"""
Test script for coordinate generation functionality.
Tests the specialized coordination chemistry geometry generation without rowan dependencies.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from functions.molecular_converter import convert_to_smiles
from rdkit import Chem
import math

def _generate_manual_octahedral_geometry(rdkit_mol):
    """Generate octahedral geometry manually for coordination complexes."""
    try:
        num_atoms = rdkit_mol.GetNumAtoms()
        coords = []
        
        # Identify metal and ligands by atomic number
        metal_idx = None
        ligand_indices = []
        
        for i, atom in enumerate(rdkit_mol.GetAtoms()):
            atomic_num = atom.GetAtomicNum()
            if atomic_num in [25, 26, 27, 28, 29, 24]:  # Transition metals
                metal_idx = i
            else:
                ligand_indices.append(i)
        
        # Initialize coordinate array
        coords = [[0.0, 0.0, 0.0] for _ in range(num_atoms)]
        
        if metal_idx is not None and len(ligand_indices) == 6:
            # Place metal at origin
            coords[metal_idx] = [0.0, 0.0, 0.0]
            
            # Octahedral positions (bond length ~2.4 Å for M-Cl)
            bond_length = 2.4
            octahedral_positions = [
                [bond_length, 0.0, 0.0],      # +x
                [-bond_length, 0.0, 0.0],     # -x  
                [0.0, bond_length, 0.0],      # +y
                [0.0, -bond_length, 0.0],     # -y
                [0.0, 0.0, bond_length],      # +z
                [0.0, 0.0, -bond_length]      # -z
            ]
            
            # Place ligands at octahedral positions
            for i, ligand_idx in enumerate(ligand_indices[:6]):
                coords[ligand_idx] = octahedral_positions[i]
            
            return coords
        
        # For other coordination numbers, distribute on sphere
        elif metal_idx is not None and len(ligand_indices) > 0:
            coords[metal_idx] = [0.0, 0.0, 0.0]
            
            bond_length = 2.4
            for i, ligand_idx in enumerate(ligand_indices):
                # Distribute ligands around sphere
                phi = 2 * math.pi * i / len(ligand_indices)
                theta = math.pi / 3  # ~60 degrees from z-axis
                
                x = bond_length * math.sin(theta) * math.cos(phi)
                y = bond_length * math.sin(theta) * math.sin(phi) 
                z = bond_length * math.cos(theta)
                
                coords[ligand_idx] = [x, y, z]
            
            return coords
            
    except Exception as e:
        print(f"⚠️ Manual octahedral generation failed: {e}")
    
    return None

def test_coordination_complex_geometry():
    """Test coordination complex geometry generation."""
    
    test_cases = [
        {
            "name": "MnCl6_unicode",
            "input": "Mn(Cl)₆⁺⁴",
            "description": "User's specific example with Unicode"
        },
        {
            "name": "MnCl6_simple", 
            "input": "Mn(Cl)6",
            "description": "Simple parentheses notation"
        },
        {
            "name": "FeCl6_complex",
            "input": "Fe(Cl)6",
            "description": "Iron hexachloride complex"
        },
        {
            "name": "bracket_notation",
            "input": "[MnCl6]4-",
            "description": "Bracket notation with charge"
        }
    ]
    
    print("🧪 Testing Coordination Complex Geometry Generation")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        print(f"\n📋 Test: {case['name']}")
        print(f"Input: {case['input']}")
        print(f"Description: {case['description']}")
        
        try:
            # Step 1: Convert to SMILES
            converted_smiles = convert_to_smiles(case['input'])
            print(f"✅ SMILES: {converted_smiles}")
            
            # Step 2: Create RDKit molecule
            rdkit_mol = Chem.MolFromSmiles(converted_smiles)
            if not rdkit_mol:
                print("❌ Failed to create RDKit molecule")
                failed += 1
                continue
                
            print(f"✅ RDKit molecule: {rdkit_mol.GetNumAtoms()} atoms")
            
            # Step 3: Generate coordinates
            coords = _generate_manual_octahedral_geometry(rdkit_mol)
            
            if coords and len(coords) == rdkit_mol.GetNumAtoms():
                print(f"✅ Generated {len(coords)} coordinates")
                
                # Verify no atoms at origin (except metal)
                non_origin_count = 0
                metal_at_origin = False
                
                for i, coord in enumerate(coords):
                    atom = rdkit_mol.GetAtomWithIdx(i)
                    if coord == [0.0, 0.0, 0.0]:
                        if atom.GetAtomicNum() in [25, 26, 27, 28, 29, 24]:
                            metal_at_origin = True
                        else:
                            print(f"⚠️ Non-metal atom {atom.GetSymbol()} at origin")
                    else:
                        non_origin_count += 1
                
                if metal_at_origin and non_origin_count >= 6:
                    print("✅ Proper octahedral geometry: metal at center, ligands positioned")
                    
                    # Check distances
                    metal_ligand_distances = []
                    for i, coord in enumerate(coords):
                        atom = rdkit_mol.GetAtomWithIdx(i)
                        if atom.GetAtomicNum() not in [25, 26, 27, 28, 29, 24]:  # Ligand
                            dist = math.sqrt(sum(c**2 for c in coord))  # Distance from origin
                            metal_ligand_distances.append(dist)
                    
                    if metal_ligand_distances and all(2.0 <= d <= 3.0 for d in metal_ligand_distances):
                        print(f"✅ Realistic bond lengths: {metal_ligand_distances[0]:.2f} Å")
                        passed += 1
                    else:
                        print(f"❌ Unrealistic bond lengths: {metal_ligand_distances}")
                        failed += 1
                else:
                    print("❌ Incorrect geometry arrangement")
                    failed += 1
            else:
                print("❌ Failed to generate coordinates")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
            
        print("-" * 40)
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if passed >= 3:
        print("\n🎉 SUCCESS: Coordination complex geometry generation is working!")
        print("✅ This should resolve the 'Short Interatomic Distances' errors in Rowan")
        print("✅ Ready to test with actual Rowan submissions")
    else:
        print("\n❌ Issues detected with coordinate generation")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = test_coordination_complex_geometry()
    sys.exit(failed)