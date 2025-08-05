# Rowan MCP Benchmark Queries

## Tier 1: Single Tool Calls
Every tool tested with simplest possible invocation.

1. **Basic Calculation**: "Optimize the geometry of water"
2. **Conformer Search**: "Find the conformers of diethyl ether"
3. **pKa**: "Calculate the pKa of phenol"
4. **Redox Potential**: "Calculate the oxidation potential of benzene"
5. **Solubility**: "Predict the solubility of aspirin in water"
6. **Descriptors**: "Calculate molecular descriptors for ibuprofen"
7. **Tautomers**: "Find the tautomers of 2-hydroxypyridine"
8. **Scan**: "Perform an angle scan on water from 100 to 110 degrees"
9. **IRC**: "Run an IRC calculation for HNCO + H2O transition state"
10. **Fukui**: "Calculate Fukui indices for aniline"
11. **Docking**: "Dock aspirin to CDK2 kinase"
12. **Protein Cofolding**: "Fold CDK2 with a small molecule ligand"

## Tier 2: Parameter Interpretation
Every tool with natural language parameter specification.

13. **Basic Calculation**: "Carefully optimize ethanol geometry using R2SCAN-3c"
14. **Conformer Search**: "Find conformers of cyclohexane using meticulous mode"
15. **pKa**: "Calculate the pKa of lysine, only looking at nitrogen atoms"
16. **Redox Potential**: "Calculate both oxidation and reduction potentials for ferrocene"
17. **Solubility**: "Predict caffeine solubility in water at 25 and 50 degrees Celsius"
18. **Descriptors**: "Get ADMET descriptors for morphine including toxicity predictions"
19. **Tautomers**: "Find all possible tautomers of guanine using careful mode"
20. **Scan**: "Scan the C-C bond in ethane from 1.3 to 1.7 Angstroms with 10 points"
21. **IRC**: "Run IRC without pre-optimization from this transition state geometry"
22. **Fukui**: "Calculate nucleophilic and electrophilic Fukui functions for pyridine"
23. **Docking**: "Dock ibuprofen to COX-2 without conformational search"
24. **Protein Cofolding**: "Cofold this protein sequence with three different ligands"

## Tier 3: Batch Operations
Every tool with multiple molecules or comparative analysis.

25. **Basic Calculation**: "Optimize water with GFN2-xTB, UMA, and R2SCAN-3c methods"
26. **Conformer Search**: "Find conformers for butane, pentane, and hexane"
27. **pKa**: "Calculate pKa values for phenol, p-nitrophenol, and p-methoxyphenol"
28. **Redox Potential**: "Calculate oxidation potentials for benzene, toluene, and xylene"
29. **Solubility**: "Compare the solubility of aspirin in water, ethanol, and acetone"
30. **Descriptors**: "Calculate descriptors for 10 FDA-approved drugs"
31. **Tautomers**: "Find tautomers for adenine, guanine, and cytosine"
32. **Scan**: "Perform dihedral scans on all rotatable bonds in butane"
33. **IRC**: "Run IRC calculations for three different transition states"
34. **Fukui**: "Calculate Fukui indices for all aromatic amino acids"
35. **Docking**: "Screen 5 molecules for docking to CDK2"
36. **Protein Cofolding**: "Fold three different protein-ligand complexes"

## Tier 4: Workflow Chaining
Every tool that makes chemical sense to chain.

37. **Basic Calc → IRC**: "Optimize this transition state geometry, then run IRC from the result"
38. **Conformer → Redox**: "Find conformers of p-methoxybenzophenone, then calculate redox potential for the lowest energy conformer"
39. **Conformer → pKa**: "Generate conformers of histidine, then calculate pKa for the top 3 structures"
40. **Conformer → Solubility**: "Find conformers of a drug molecule, then predict solubility for each conformer"
41. **Conformer → Descriptors**: "Generate conformers of a flexible molecule, calculate descriptors for each"
42. **Conformer → Docking**: "Find conformers of a ligand, then dock each conformer to the target"
43. **Tautomer → pKa**: "Find tautomers of 4-hydroxypyrimidine, then calculate pKa for each tautomer"
44. **Tautomer → Descriptors**: "Generate tautomers of warfarin, then calculate descriptors for each form"
45. **Scan → Fukui**: "Perform a bond scan on a molecule, calculate Fukui indices at the extreme points"
46. **Basic Calc → Fukui**: "Optimize a radical species, then calculate its Fukui indices"
47. **Protein Cofold → Docking**: "Fold a protein with cofactor, then dock substrates to the folded structure"

## Tier 5: Conditional Logic
Every tool with decision-based workflows.

48. **Basic Calc with Fallback**: "Optimize this complex molecule, if it fails with rapid mode, retry with careful mode"
49. **Conformer → Conditional Redox**: "Find conformers, calculate redox only for those within 2 kcal/mol of minimum"
50. **Conformer → Conditional pKa**: "Generate conformers, calculate pKa only for conformers with dipole moment > 3 Debye"
51. **pKa → Conditional Conformer**: "Calculate pKa for histidine, if any site has pKa between 6-8, run conformer search at that pH"
52. **Solubility Threshold**: "Calculate solubility in multiple solvents, only do detailed analysis for solvents where solubility > 1 mg/mL"
53. **Descriptor Filtering**: "Calculate descriptors for 20 molecules, only run pKa for those with logP between 2-5"
54. **Tautomer Selection**: "Find tautomers, only calculate properties for tautomers with population > 5%"
55. **Scan → Conditional IRC**: "Perform scan, if barrier < 20 kcal/mol, run IRC from the transition state"
56. **Fukui-Guided Analysis**: "Calculate Fukui indices, run detailed calculations only on the most reactive sites"
57. **Docking Cascade**: "Screen 10 molecules against a target, only run protein cofolding for those with scores < -8.0"
58. **Multi-Stage Drug Screen**: "Calculate descriptors for 50 molecules, filter by Lipinski's rule, calculate pKa for filtered set, dock those with favorable pKa to target"

## Notes
- Tiers 1-3 test breadth (all tools individually and in batches)
- Tiers 4-5 test depth (meaningful tool combinations and logic)
- Not all tools chain naturally (e.g., IRC typically doesn't chain with other tools)
- Conditional logic focuses on chemically meaningful decision points