# Rowan MCP Benchmark Queries

## Tier 1: Single Tool Calls

### Basic Calculation
1. "Optimize the geometry of water"
2. "Calculate the energy of methane using GFN2-xTB"

### Conformer Search
3. "Find the conformers of diethyl ether"
4. "Search for low-energy conformations of butane"

### pKa
5. "Calculate the pKa of phenol"
6. "What's the pKa of acetic acid?"

### Redox Potential
7. "Calculate the oxidation potential of benzene"
8. "Find the reduction potential of quinone"

### Solubility
9. "Predict the solubility of aspirin in water"
10. "What's the solubility of caffeine in ethanol?"

### Descriptors
11. "Calculate molecular descriptors for ibuprofen"

### Tautomers
12. "Find the tautomers of 2-hydroxypyridine"

### Scan
13. "Perform an angle scan on water from 100 to 110 degrees"

### IRC
14. "Run an IRC calculation from this transition state: [provide XYZ]"

### Fukui
15. "Calculate Fukui indices for aniline"

### Docking
16. "Dock aspirin to CDK2 kinase"

### Protein Cofolding
17. "Predict the structure of CDK2 with a small molecule ligand"

## Tier 2: Parameter Interpretation

### Basic Calculation with Modes
18. "Carefully optimize ethanol geometry"
19. "Run a meticulous energy calculation on benzene"

### Conformer Search with Settings
20. "Find conformers of cyclohexane using meticulous mode"

### pKa with Specific Sites
21. "Calculate the pKa of lysine, only looking at nitrogen atoms"
22. "Find the pKa of phosphoric acid between pH 1 and 14"

### Redox with Both Potentials
23. "Calculate both oxidation and reduction potentials for ferrocene"

### Solubility with Temperature
24. "Predict caffeine solubility in water at 25 and 50 degrees Celsius"

### Scan with Custom Parameters
25. "Scan the C-C bond in ethane from 1.3 to 1.7 Angstroms with 10 points"

### Docking with Options
26. "Dock ibuprofen to COX-2 without conformational search"

## Tier 3: Batch Operations

### Multiple Molecules
27. "Calculate pKa values for phenol, p-nitrophenol, and p-methoxyphenol"
28. "Find conformers for butane, pentane, and hexane"
29. "Calculate oxidation potentials for benzene, toluene, and xylene"

### Multiple Methods
30. "Optimize water with GFN2-xTB, UMA, and R2SCAN-3c"
31. "Calculate ethanol energy using both rapid and careful modes"

### Comparative Analysis
32. "Compare the solubility of aspirin in water, ethanol, and acetone"
33. "Screen these three molecules for docking to CDK2: [provide 3 SMILES]"

## Tier 4: Workflow Chaining

### Conformer-Dependent Properties
34. "Find conformers of p-methoxybenzophenone, then calculate redox potential for the lowest energy conformer"
35. "Generate conformers of butanol, then calculate pKa for the top 3 structures"

### Optimization to IRC
36. "Optimize this transition state geometry [XYZ], then run IRC from the result"

### Scan to Property
37. "Perform a dihedral scan on butane, then calculate the energy of the highest energy point"

### Sequential Docking
38. "Find conformers of a ligand, then dock the best conformer to CDK2"

## Tier 5: Conditional Logic

### Threshold-Based Analysis
39. "Screen 5 molecules against CDK2, only run detailed conformer analysis for those with scores better than -8.0"
40. "Calculate pKa for histidine, if any site has pKa between 6-8, run a conformer search at that pH"

### Outlier Detection
41. "Find all conformers of cyclohexanol, calculate energies, and recalculate any conformer more than 3 kcal/mol above the minimum with meticulous mode"

### Multi-Stage Screening
42. "Calculate descriptors for these 10 molecules, identify those with logP > 2, then calculate their pKa values"

### Error Recovery
43. "Optimize this complex molecule, if it fails with rapid mode, retry with careful mode"

## Notes
- Queries intentionally use varied phrasing (calculate/find/predict/what's)
- Mix of SMILES, common names, and descriptive terms
- Each science tool appears at least once
- Workflow management tools used implicitly in Tiers 4-5