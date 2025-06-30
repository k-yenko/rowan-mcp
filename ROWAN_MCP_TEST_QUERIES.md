# Rowan MCP Test Queries

This document provides natural language test queries for all Rowan MCP tools, organized by category with both simple and comprehensive examples.

---

## 1. Core Calculations

### Geometry Optimization

**Simple Queries:**
- "Optimize the geometry of aspirin"
- "Run a multistage optimization on caffeine" 
- "Get the best structure for benzene"

**Comprehensive Queries:**
- "Perform a multistage geometry optimization on ibuprofen starting with GFN2-xTB, then AIMNet2, then DFT to get the most accurate structure"
- "Optimize the geometry of morphine using the multistage approach and wait for completion to get final energies"

### Electronic Properties

**Simple Queries:**
- "Calculate the HOMO and LUMO of benzene"
- "Get the electronic properties of water"
- "What are the molecular orbitals of methanol?"

**Comprehensive Queries:**
- "Calculate comprehensive electronic properties for phenol including HOMO/LUMO, electron density cubes, electrostatic potential surfaces, and the top 3 occupied and virtual molecular orbitals using B3LYP/def2-SVP"
- "Analyze the electronic structure of pyridine with density cube generation and ESP mapping for drug design applications"

### Conformational Analysis

**Simple Queries:**
- "Find the stable conformers of glucose"
- "Generate 5 conformers of butane"
- "What are the different shapes ethanol can adopt?"

**Comprehensive Queries:**
- "Generate up to 20 conformers of flexible drug molecule ibuprofen, rank them by energy, and analyze their relative populations for understanding bioavailability"
- "Perform conformational analysis on cyclohexane to identify chair and boat conformations with full energy ranking"

### Potential Energy Scans

**Simple Queries:**
- "Scan the C-C bond in ethane from 1.3 to 1.8 Angstroms"
- "Do a dihedral scan of butane around the central C-C bond"
- "Map the energy surface for water bending angle"

**Comprehensive Queries:**
- "Perform a 2D potential energy scan on hydrogen peroxide: scan both the O-O bond distance from 1.2 to 1.8 Angstroms and the H-O-O-H dihedral angle from 0 to 180 degrees in a 15x15 grid to map the full conformational landscape"
- "Scan the reaction coordinate for SN2 mechanism: vary the C-Cl bond from 1.8 to 3.0 Angstroms in 25 steps to find the transition state region"

### Spin States

**Simple Queries:**
- "What spin states are possible for iron(III) complex?"
- "Calculate different spin multiplicities for NO radical"
- "Check if this molecule prefers singlet or triplet state"

**Comprehensive Queries:**
- "Analyze all reasonable spin states (singlet, doublet, triplet, quintet) for the iron porphyrin complex with automatic molecular complexity analysis and intelligent spin state prediction"
- "Compare the energetics of high-spin vs low-spin states for this cobalt complex in both gas phase and acetonitrile solvent"

---

## 2. Chemical Properties

### Bond Dissociation Energy

**Simple Queries:**
- "What's the bond strength in hydrogen molecule?"
- "Calculate BDE for aspirin to predict metabolic weak points"
- "Find the weakest bond in caffeine"

**Comprehensive Queries:**
- "Calculate comprehensive bond dissociation energies for all major bonds in ibuprofen to identify metabolically labile sites and predict phase I metabolism pathways"
- "Analyze BDE patterns in phenolic compounds to understand antioxidant activity mechanisms"

### Redox Potentials

**Simple Queries:**
- "What's the reduction potential of benzoquinone?"
- "Can this molecule be easily oxidized?"
- "Predict the redox behavior of vitamin E"

**Comprehensive Queries:**
- "Calculate both oxidation and reduction potentials for this organic photovoltaic material in acetonitrile using careful mode to predict its electrochemical stability window and HOMO/LUMO energy levels"
- "Analyze the redox properties of this battery electrolyte additive using meticulous calculations to ensure high accuracy for device applications"

### Solubility Prediction

**Simple Queries:**
- "How soluble is aspirin in water?"
- "Predict the aqueous solubility of this drug candidate"
- "Is caffeine water-soluble?"

**Comprehensive Queries:**
- "Predict aqueous solubility for this series of drug candidates to optimize formulation strategies and assess bioavailability potential"
- "Calculate water solubility for environmental fate assessment of this pesticide molecule"

### Molecular Descriptors

**Simple Queries:**
- "Generate descriptors for benzene"
- "Get QSAR features for this molecule"
- "Calculate topological indices for caffeine"

**Comprehensive Queries:**
- "Generate comprehensive molecular descriptor set including topological, geometric, electronic, and physicochemical properties for machine learning QSAR model development"
- "Calculate full descriptor profile for chemical space analysis and similarity searching in drug discovery"

---

## 3. Advanced Analysis

### Reactivity Prediction (Fukui)

**Simple Queries:**
- "Where will electrophiles attack benzene?"
- "Find the most reactive sites in phenol"
- "Predict nucleophilic attack positions on this molecule"

**Comprehensive Queries:**
- "Perform comprehensive Fukui analysis on this pharmaceutical intermediate with geometry optimization using B3LYP/def2-SVP to predict regioselectivity for synthetic planning"
- "Calculate f(+), f(-), and f(0) indices for this catalyst molecule to understand selectivity patterns in asymmetric synthesis"

### Reaction Coordinate Analysis

**Simple Queries:**
- "Analyze this completed scan for transition states"
- "Extract the highest energy geometry from my scan"
- "Find energy barriers in this reaction pathway"

**Comprehensive Queries:**
- "Analyze the completed potential energy scan to extract transition state geometries, identify reaction intermediates, and prepare XYZ coordinates for subsequent IRC calculations"
- "Process scan results to map complete reaction energy profile with barrier heights and thermodynamic data"

### Intrinsic Reaction Coordinate

**Simple Queries:**
- "Trace the reaction path from this transition state"
- "Confirm this TS connects reactants and products"
- "Map the minimum energy pathway"

**Comprehensive Queries:**
- "Perform bidirectional IRC calculation from the transition state geometry to trace the complete reaction pathway and confirm connectivity to desired reactants and products using B3LYP/def2-SVP"
- "Calculate IRC in both forward and reverse directions with detailed analysis of geometric changes along the reaction coordinate"

### Molecular Dynamics

**Simple Queries:**
- "Run a short MD simulation of water"
- "Simulate the flexibility of this drug molecule"
- "Model thermal motion of benzene"

**Comprehensive Queries:**
- "Perform 500 ps molecular dynamics simulation of this protein-drug complex at 310K using NPT ensemble to analyze binding stability and conformational changes"
- "Run extended MD simulation to sample conformational space and calculate thermodynamic properties including heat capacity and thermal expansion"

---

## 4. Drug Discovery

### ADMET Properties

**Simple Queries:**
- "Predict drug-likeness of aspirin"
- "Is this molecule orally bioavailable?"
- "Calculate ADMET for this drug candidate"

**Comprehensive Queries:**
- "Perform comprehensive ADMET analysis including absorption, distribution, metabolism, excretion, and toxicity predictions for lead optimization in CNS drug discovery"
- "Calculate full pharmacokinetic profile including BBB permeability, CYP inhibition, hERG toxicity, and bioavailability for regulatory submission support"

### Molecular Docking

**Simple Queries:**
- "Dock aspirin to COX-2 enzyme"
- "Find binding pose of this ligand"
- "Predict protein-drug interaction"

**Comprehensive Queries:**
- "Perform high-accuracy molecular docking of this kinase inhibitor to generate 20 binding poses with detailed scoring and analysis of key protein-ligand interactions"
- "Dock this allosteric modulator to identify cryptic binding sites and analyze binding affinity predictions"

### Tautomer Analysis

**Simple Queries:**
- "What tautomers does this molecule have?"
- "Find the most stable tautomeric form"
- "Enumerate keto-enol tautomers"

**Comprehensive Queries:**
- "Enumerate all reasonable tautomers for this pharmaceutical compound and rank by relative stability to identify the predominant forms at physiological pH"
- "Analyze tautomeric equilibria for this drug molecule to understand bioactive conformations and metabolism patterns"

### Hydrogen Bond Strength

**Simple Queries:**
- "How strong are the H-bonds in this molecule?"
- "Predict hydrogen bond acceptor ability"
- "Calculate H-bond basicity of phenol"

**Comprehensive Queries:**
- "Calculate comprehensive hydrogen bond acceptor strengths for all basic sites in this drug molecule to predict crystal packing and solubility behavior"
- "Analyze H-bonding patterns for cocrystal formation and pharmaceutical salt design"

---

## 5. Workflow Management

### Job Control

**Simple Queries:**
- "Check the status of my calculation"
- "Cancel this running job"
- "List all my recent calculations"

**Comprehensive Queries:**
- "Retrieve detailed results from the completed multistage optimization including final geometry, energy, and all intermediate steps"
- "Monitor progress of all submitted calculations and provide status summary with estimated completion times"
- "Cancel all queued jobs in the benzene project folder and restart with updated parameters"

### Data Retrieval

**Simple Queries:**
- "Get results from this calculation UUID"
- "Download the optimized geometry"
- "Retrieve energy data from my scan"

**Comprehensive Queries:**
- "Retrieve complete dataset including geometries, energies, molecular orbitals, and analysis data from the electronic properties calculation for visualization and further analysis"
- "Extract all scan points, energies, and geometries from the 2D potential energy surface calculation for reaction pathway analysis"

### Project Organization

**Simple Queries:**
- "Create a new project folder for drug discovery"
- "List all folders in my account"
- "Move this calculation to the kinetics folder"

**Comprehensive Queries:**
- "Create hierarchical folder structure for systematic drug discovery campaign: create parent folder 'Kinase_Inhibitors' with subfolders for 'Lead_Compounds', 'ADMET_Analysis', 'Docking_Studies', and 'Optimization_Results'"
- "Organize all completed calculations by project type and archive old results for efficient data management"

---

## 6. System Management

### Server Administration

**Simple Queries:**
- "Check server status"
- "Set logging level to debug"
- "Monitor system health"

**Comprehensive Queries:**
- "Perform comprehensive system diagnostics including job queue status, resource utilization, and error log analysis"
- "Configure logging levels and monitor system performance for optimization of calculation throughput"

### Molecule Database

**Simple Queries:**
- "What's the SMILES for caffeine?"
- "Look up aspirin structure"
- "Convert 'benzene' to SMILES"

**Comprehensive Queries:**
- "Search the molecule database for all pharmaceutical compounds and return standardized SMILES for systematic QSAR analysis"
- "Batch convert a list of common drug names to canonical SMILES format for computational workflow automation"

---

## Sample Test Workflows

### Complete Drug Discovery Pipeline
1. "Look up the SMILES for ibuprofen"
2. "Create a folder called 'Ibuprofen_Analysis'"
3. "Optimize the geometry of ibuprofen using multistage approach"
4. "Calculate ADMET properties for the optimized structure"
5. "Predict BDE to identify metabolic sites"
6. "Generate molecular descriptors for QSAR modeling"
7. "Retrieve all results and organize in the project folder"

### Reaction Mechanism Study
1. "Create folder 'SN2_Mechanism_Study'"
2. "Scan the C-Cl bond in chloromethane from 1.8 to 3.0 Angstroms"
3. "Analyze scan results to extract transition state geometry"
4. "Perform IRC calculation from the transition state"
5. "Calculate electronic properties at key points along reaction coordinate"
6. "Retrieve complete reaction pathway data"

### Catalyst Design Workflow  
1. "Look up SMILES for your catalyst precursor"
2. "Calculate different spin states to find ground state"
3. "Optimize geometry in both gas phase and solvent"
4. "Perform Fukui analysis to predict reactive sites"
5. "Calculate redox potentials for stability assessment"
6. "Generate descriptors for machine learning model"

These queries cover all 21 tools with both simple and comprehensive examples, written in natural language as requested. Use these to systematically test your entire Rowan MCP system! 