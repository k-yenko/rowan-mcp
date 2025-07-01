# ROWAN MCP TEST QUERIES

Natural language test queries for all Rowan MCP tools.

✅: passed with expected results

⚠️: passed-ish (submitted/ran, but maybe unexpected results or needs some tweaking)

❌: failed

---

# simple queries

## core calculations

### geometry optimizations
- Optimize the geometry of aspirin ✅
- Run a multistage optimization on caffeine ⚠️ (Unexpected Imaginary Frequency

An unexpected large imaginary frequency was encountered, meaning that the calculation is far from a critical point on the PES. It's likely this structure has not been successfully optimized! Thermochemical results will be unreliable.)

- Get the best structure for benzene ✅

### electronic props
- Calculate the HOMO and LUMO of benzene ✅
- Get the electronic properties of nicotine ✅
- What are the molecular orbitals of methanol? ✅

### conformational analysis
- Find the stable conformers of glucose ❌ - stuck on "running"
- Generate 5 conformers of butane ✅
- What are the different shapes ethanol can adopt? ✅

### scans
- Scan the C-C bond in ethane from 1.3 to 1.8 Angstroms ✅

### spin states
- What spin states are possible for iron(III) complex? ✅
- Calculate different spin multiplicities for NO radical ✅ - calculated doublet and quartet states (?)
- Check if iron porphyrin prefers singlet or triplet state ⚠️ log files indicate that this run finished, but doesn't say "finished" on rowan UI. stopped

## cheimcal properties

### redox
- What's the reduction potential of benzoquinone? ✅ (Large Oxidation Potential Predicted. The predicted oxidation potential is very large. The workflow not been thoroughly tested on values in this range—results may be less accurate!)
- Can vitamin E be easily oxidized? ⚠️ log files indicate that this run finished, but doesn't say "finished" on rowan UI. stopped
- Predict the redox behavior of phenol ✅

### solubility
- How soluble is aspirin in water?✅
- How soluble is caffeine in different solvents? Pick 5, and run them at 5 different temps in ascending order. ✅

### descriptors
- Generate descriptors for benzene ✅
- Get QSAR features for ethanol ✅

### pka
- What's the pKa of acetic acid? ✅
- What's the pKa of caffeine? ✅
- What are the pKa values of citric acid? ✅

### bond dissociation energy (no access)

### hydrogen bond basicity (no access)

## advanced analysis

### reactivity (fukui)
- Where will electrophiles attack benzene? ✅
- Find the most reactive sites in phenol ✅

### rxn coordinate
- Find the transition state for hydrogen migration in formic acid, then trace the reaction path to confirm it connects HCOOH and HOCOH isomers ❌

### irc
- Trace the reaction path from this transition state
- Confirm this TS connects reactants and products
- Map the minimum energy pathway

### molecular dynamics
- Run a short MD simulation of water ✅ (use molecule='water', not 'O')
- Simulate the flexibility of ethanol for 500 steps ✅
- Run molecular dynamics on butanol for 1000 steps ✅

## drug discovery

### admet
- Predict drug-likeness of aspirin (follow-up: is it orally bioavailable?) ✅
- Calculate ADMET for KarXT from Karuna Therapeutics ✅

### docking (couldn't resolve)
- Dock aspirin to COX-2 enzyme
- Find binding pose of this ligand
- Predict protein-drug interaction

### tautomers
- What tautomers does acetylacetone have? ✅
- Find tautomers of barbituric acid ✅
- What keto-enol tautomers does phenol have? ✅

## workflow management

### data retrieval
- Get results from this calculation UUID
- Download the optimized geometry
- Retrieve energy data from my scan

### project organization
- Create a new project folder for drug discovery (and delete) ✅
- List all folders in my account ✅
- "Move KarXT-related calculations into the folder" ✅

## system management

### server administration
- Check server status
- Set logging level to debug
- Monitor system health

### molecule database?
- What's the SMILES for caffeine?
- Look up aspirin structure
- Convert 'benzene' to SMILES

# more comprehensive queries tbd...