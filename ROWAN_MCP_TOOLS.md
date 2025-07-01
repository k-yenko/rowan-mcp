# Rowan MCP Tools Documentation

This document provides a comprehensive overview of all available tools in the Rowan Model Context Protocol (MCP) server for computational chemistry calculations.

## Overview

The Rowan MCP server provides access to **23 computational chemistry tools** organized into the following categories:

- **Core Calculations**: Basic quantum chemistry workflows
- **Chemical Properties**: Molecular property predictions  
- **Advanced Analysis**: Specialized computational methods
- **Drug Discovery**: ADMET and pharmaceutical properties
- **Workflow Management**: Job control and data retrieval
- **System Management**: Server administration and utilities

---

## Tool Inventory

### 1. Core Calculations

#### `rowan_scan`
**Description**: Perform potential energy surface scans along molecular coordinates.

Maps energy landscapes by varying bond distances, angles, or dihedrals. Essential for reaction mechanism studies and conformational analysis. Identifies transition states, minima, and energy barriers.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string or molecule name
- `coordinate_type`: "bond", "angle", or "dihedral"
- `atoms`: List of atom indices defining the coordinate
- `start`: Starting value for scan
- `stop`: Ending value for scan  
- `num`: Number of scan points
- `method`: QM method (default: "hf-3c")
- `basis_set`: Basis set (optional)
- `engine`: Computational engine (default: "psi4")
- `charge`: Molecular charge (default: 0)
- `multiplicity`: Spin multiplicity (default: 1)
- `mode`: Calculation mode (optional)
- `solvent`: Solvent environment (optional)
- `constraints`: Additional geometric constraints (optional)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: IRC workflows, reaction mechanism studies, conformational analysis

---

#### `rowan_multistage_opt`
**Description**: Run multi-level geometry optimization.

Performs hierarchical optimization using multiple levels of theory: GFN2-xTB → AIMNet2 → DFT for optimal balance of speed and accuracy. Provides high accuracy final structures with efficient computational cost and reliable convergence.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 30)

**Use Cases**: Geometry optimization, conformational analysis, structure refinement

---

#### `rowan_electronic_properties`
**Description**: Calculate comprehensive electronic structure properties.

Computes detailed electronic properties including molecular orbitals (HOMO/LUMO), electron density, electrostatic properties, population analysis, bond analysis, and visualization data.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string or molecule name
- `method`: QM method (default: "b3lyp")
- `basis_set`: Basis set (default: "def2-svp")
- `engine`: Computational engine (default: "psi4")
- `charge`: Molecular charge (default: 0)
- `multiplicity`: Spin multiplicity (default: 1)
- `compute_density_cube`: Generate density cube files (default: True)
- `compute_electrostatic_potential_cube`: Generate ESP cube files (default: True)
- `compute_num_occupied_orbitals`: Number of occupied MOs to save (default: 1)
- `compute_num_virtual_orbitals`: Number of virtual MOs to save (default: 1)
- `mode`: Calculation mode (optional)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Electronic structure analysis, orbital visualization, reactivity prediction

---

#### `rowan_conformers`
**Description**: Generate and optimize molecular conformers.

Systematically explores conformational space to find stable molecular geometries. Provides energy-ranked conformers with relative stabilities and populations.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `max_conformers`: Maximum number of conformers (default: 10)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `max_wait_time`: Maximum wait time in seconds (default: 120)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Conformational analysis, drug design, molecular flexibility studies

---

#### `rowan_spin_states`
**Description**: Calculate and analyze different spin states of molecules.

Comprehensive spin state analysis including energy differences, spin densities, and magnetic properties. Includes automatic analysis of results with intelligent interpretation.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `states`: List of multiplicities to calculate (optional)
- `charge`: Molecular charge (optional)
- `multiplicity`: Reference spin multiplicity (optional)
- `mode`: Calculation mode (default: "rapid")
- `solvent`: Solvent environment (optional)
- `xtb_preopt`: Pre-optimize with xTB (default: True)
- `constraints`: Geometric constraints (optional)
- `transition_state`: Transition state calculation (default: False)
- `frequencies`: Calculate frequencies (default: False)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 10)
- `auto_analyze`: Automatic result analysis (default: True)

**Use Cases**: Magnetic property prediction, catalysis studies, organometallic chemistry

---

### 2. Chemical Properties



#### `rowan_redox_potential`
**Description**: Predict redox potentials vs. SCE in acetonitrile.

Calculates oxidation and reduction potentials for electrochemical reaction design, battery applications, and electron transfer studies. Only acetonitrile solvent is supported.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string or common name
- `reduction`: Calculate reduction potential (default: True)
- `oxidation`: Calculate oxidation potential (default: True)
- `mode`: Accuracy mode - "reckless", "rapid", "careful", "meticulous" (default: "rapid")
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Electrochemistry, battery materials, electron transfer studies

---

#### `rowan_solubility`
**Description**: Predict aqueous solubility of organic compounds.

Fast and accurate solubility predictions using machine learning models trained on experimental data. Essential for drug discovery and environmental fate assessment.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Drug discovery, environmental chemistry, formulation development

---

#### `rowan_descriptors`
**Description**: Calculate molecular descriptors for data science.

Generates comprehensive molecular descriptors including topological, geometric, electronic, and physicochemical properties. Provides machine learning ready feature vectors.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: QSAR modeling, machine learning, chemical space analysis

---

#### `rowan_pka`
**Description**: Calculate pKa values for ionizable groups.

Predicts acid-base properties for pharmaceutical applications. Calculates pKa values for ionizable functional groups in organic molecules, essential for understanding protonation states at physiological pH.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `folder_uuid`: Organization folder (optional)

**Use Cases**: Drug discovery, pharmaceutical development, ADMET prediction

---

### 3. Advanced Analysis

#### `rowan_fukui`
**Description**: Calculate Fukui indices for reactivity prediction.

Predicts sites of chemical reactivity by analyzing electron density changes. Provides f(+), f(-), and f(0) indices for electrophilic, nucleophilic, and radical attack sites respectively.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string or common name
- `optimize`: Optimize geometry before calculation (default: True)
- `opt_method`: Optimization method (optional)
- `opt_basis_set`: Optimization basis set (optional)
- `opt_engine`: Optimization engine (optional)
- `fukui_method`: Fukui calculation method (default: "gfn1_xtb")
- `fukui_basis_set`: Fukui basis set (optional)
- `fukui_engine`: Fukui engine (optional)
- `charge`: Molecular charge (default: 0)
- `multiplicity`: Spin multiplicity (default: 1)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Reactivity prediction, regioselectivity analysis, catalyst design

---

#### `rowan_scan_analyzer`
**Description**: Analyze scan results and extract key geometries for IRC workflows.

Essential IRC tool that analyzes completed scan workflows to extract transition state geometries. Provides formatted results ready for IRC calculations and identifies energy maxima, minima, and barriers automatically.

**Parameters**:
- `scan_uuid`: UUID of completed scan calculation
- `action`: Analysis action - "analyze", "extract_ts", "extract_minima", "energy_profile" (default: "analyze")
- `energy_threshold`: Energy threshold for filtering (optional)

**Use Cases**: IRC workflows, transition state identification, reaction pathway analysis

---

#### `rowan_irc`
**Description**: Perform Intrinsic Reaction Coordinate calculations.

Traces reaction pathways from transition states to reactants and products. Essential for confirming reaction mechanisms and understanding reaction dynamics.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string or XYZ coordinates
- `direction`: IRC direction - "forward", "reverse", "both" (default: "both")
- `method`: QM method (default: "b3lyp")
- `basis_set`: Basis set (default: "def2-svp")
- `engine`: Computational engine (default: "psi4")
- `charge`: Molecular charge (default: 0)
- `multiplicity`: Spin multiplicity (default: 1)
- `step_size`: IRC step size (default: 0.1)
- `max_steps`: Maximum IRC steps (default: 20)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 10)

**Use Cases**: Reaction mechanism validation, pathway analysis, kinetics studies

---

#### `rowan_molecular_dynamics`
**Description**: Perform molecular dynamics simulations.

Simulates molecular motion and dynamics using classical or quantum mechanical force fields. Provides trajectories, thermodynamic properties, and dynamic behavior analysis.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `duration`: Simulation duration in ps (default: 100)
- `temperature`: Temperature in K (default: 298.15)
- `pressure`: Pressure in atm (default: 1.0)
- `ensemble`: Statistical ensemble (default: "nvt")
- `force_field`: Force field type (optional)
- `solvent`: Solvent environment (optional)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 30)

**Use Cases**: Conformational sampling, thermodynamic properties, dynamic behavior

---

### 4. Drug Discovery

#### `rowan_admet`
**Description**: Predict ADME-Tox properties for drug discovery.

Comprehensive ADMET predictions including bioavailability, permeability, metabolic stability, clearance, toxicity indicators, and drug-likeness metrics.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Drug discovery, pharmaceutical development, toxicity screening

---

#### `rowan_docking`
**Description**: Perform molecular docking calculations.

Predicts binding poses and affinities of small molecules with protein targets. Essential for structure-based drug design and virtual screening.

**Parameters**:
- `name`: Calculation name
- `ligand`: Ligand SMILES string
- `protein`: Protein structure or identifier
- `binding_site`: Binding site specification (optional)
- `num_poses`: Number of poses to generate (default: 10)
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Drug design, virtual screening, binding affinity prediction

---

#### `rowan_tautomers`
**Description**: Enumerate and rank tautomers by stability.

Finds all possible tautomeric forms and ranks them by relative energy. Includes prototropic tautomers, relative populations, and dominant forms.

**Parameters**:
- `name`: Calculation name
- `molecule`: SMILES string
- `folder_uuid`: Organization folder (optional)
- `blocking`: Wait for completion (default: True)
- `ping_interval`: Status check interval (default: 5)

**Use Cases**: Drug design, understanding protonation states, reaction mechanisms

---



### 5. Workflow Management

#### `rowan_workflow_management`
**Description**: Unified workflow management for all calculation operations.

Comprehensive job control including submission, monitoring, retrieval, cancellation, and status checking. Supports both individual calculations and batch operations.

**Parameters**:
- `action`: Management action - "submit", "retrieve", "cancel", "list", "status"
- `workflow_uuid`: UUID of specific workflow (optional)
- `workflow_type`: Type of calculation (optional)
- `status_filter`: Filter by status (optional)
- `page`: Page number for pagination (default: 1)
- `size`: Results per page (default: 50)

**Use Cases**: Job management, result retrieval, workflow monitoring

---

#### `rowan_calculation_retrieve`
**Description**: Retrieve calculation results and data.

Fetches completed calculation results including geometries, energies, properties, and analysis data. Supports multiple output formats and data types.

**Parameters**:
- `uuid`: Calculation UUID
- `format`: Output format (optional)
- `data_type`: Type of data to retrieve (optional)

**Use Cases**: Result analysis, data extraction, post-processing

---

#### `rowan_folder_management`
**Description**: Unified folder management for organization.

Complete folder operations including creation, retrieval, updating, deletion, and listing with filtering capabilities.

**Parameters**:
- `action`: Folder action - "create", "retrieve", "update", "delete", "list"
- `folder_uuid`: Folder UUID (optional)
- `name`: Folder name (optional)
- `parent_uuid`: Parent folder UUID (optional)
- `notes`: Folder notes (optional)
- `starred`: Star status (optional)
- `public`: Public visibility (optional)
- `name_contains`: Name filter (optional)
- `page`: Page number (default: 1)
- `size`: Results per page (default: 50)

**Use Cases**: Project organization, data management, collaboration

---

### 6. System Management

#### `rowan_system_management`
**Description**: Server administration and system utilities.

System-level operations including job management, logging control, and server monitoring. Administrative functions for server maintenance.

**Parameters**:
- `action`: System action
- `job_uuid`: Job UUID (optional)
- `log_level`: Logging level (optional)

**Use Cases**: Server administration, debugging, system monitoring

---

#### `rowan_molecule_lookup`
**Description**: Look up SMILES strings for common molecule names.

Converts common chemical names to canonical SMILES strings. Supports a comprehensive database of organic compounds, drugs, solvents, and biochemical molecules.

**Parameters**:
- `molecule_name`: Common name of the molecule

**Use Cases**: Molecule identification, SMILES conversion, chemical database lookup

---

## Token Count Summary

**Total Tools**: 21

**Average Description Length**: ~150-300 words per tool

**Total Documentation**: ~4,000-5,000 words

**Estimated Tokens**: ~5,000-7,000 tokens (including parameters and use cases)

This documentation provides comprehensive coverage of all computational chemistry capabilities available through the Rowan MCP server, enabling users to understand the full scope of available tools and their appropriate applications. 