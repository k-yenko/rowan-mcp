# Rowan MCP Server - Complete Tools Documentation

This document provides comprehensive documentation for all available tools in the Rowan MCP Server. Each tool includes its complete function signature, parameters with type annotations, descriptions, and usage examples.

## Table of Contents

- [Chemistry Calculations](#chemistry-calculations)
- [Molecular Properties](#molecular-properties) 
- [Reactivity Analysis](#reactivity-analysis)
- [Protein & Drug Discovery](#protein--drug-discovery)
- [Molecule Management](#molecule-management)
- [Protein Management](#protein-management)
- [Workflow Management](#workflow-management)

---

## Chemistry Calculations

### submit_basic_calculation_workflow

**Description**: Submit a basic calculation workflow using Rowan v2 API. Performs fundamental quantum chemistry calculations with configurable methods and computational tasks.

**Function Signature**:
```python
def submit_basic_calculation_workflow(
    initial_molecule: Annotated[str, "SMILES string or molecule JSON for quantum chemistry calculation"],
    method: Annotated[str, "Computational method (e.g., 'gfn2-xtb', 'uma_m_omol', 'b3lyp-d3bj')"] = "uma_m_omol",
    tasks: Annotated[str, "JSON array or comma-separated list of tasks (e.g., '[\"optimize\"]', 'optimize, frequencies')"] = "",
    mode: Annotated[str, "Calculation mode: 'rapid', 'careful', 'meticulous', or 'auto'"] = "auto", 
    engine: Annotated[str, "Computational engine: 'omol25', 'xtb', 'psi4'"] = "omol25",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Basic Calculation Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string or molecule JSON for quantum chemistry calculation
- `method` (str, default: "uma_m_omol"): Computational method (e.g., 'gfn2-xtb', 'uma_m_omol', 'b3lyp-d3bj')
- `tasks` (str, default: ""): JSON array or comma-separated list of tasks (e.g., '["optimize"]', 'optimize, frequencies')
- `mode` (str, default: "auto"): Calculation mode: 'rapid', 'careful', 'meticulous', or 'auto'
- `engine` (str, default: "omol25"): Computational engine: 'omol25', 'xtb', 'psi4'
- `name` (str, default: "Basic Calculation Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Simple water optimization with GFN2-xTB
result = submit_basic_calculation_workflow(
    initial_molecule="O",
    method="gfn2-xtb",
    tasks=["optimize"],
    engine="xtb",
    name="Water Optimization"
)

# Butane optimization from SMILES
result = submit_basic_calculation_workflow(
    initial_molecule="CCCC",
    method="uma_m_omol",
    tasks="optimize, frequencies",
    mode="careful",
    name="Butane Opt+Freq"
)
```

---

### submit_conformer_search_workflow

**Description**: Submit a conformer search workflow using Rowan v2 API. Searches for low-energy molecular conformations using various methods.

**Function Signature**:
```python
def submit_conformer_search_workflow(
    initial_molecule: Annotated[str, "SMILES string representing the initial structure"],
    conf_gen_mode: Annotated[str, "Conformer generation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)"] = "rapid",
    final_method: Annotated[str, "Final optimization method (e.g., 'aimnet2_wb97md3', 'r2scan_3c', 'wb97x-d3_def2-tzvp')"] = "aimnet2_wb97md3",
    solvent: Annotated[str, "Solvent for implicit solvation (SMILES or name). Empty string for vacuum"] = "",
    transition_state: Annotated[bool, "Whether to search for transition state conformers"] = False,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Conformer Search Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string representing the initial structure
- `conf_gen_mode` (str, default: "rapid"): Conformer generation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)
- `final_method` (str, default: "aimnet2_wb97md3"): Final optimization method (e.g., 'aimnet2_wb97md3', 'r2scan_3c', 'wb97x-d3_def2-tzvp')
- `solvent` (str, default: ""): Solvent for implicit solvation (SMILES or name). Empty string for vacuum
- `transition_state` (bool, default: False): Whether to search for transition state conformers
- `name` (str, default: "Conformer Search Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Simple diethyl ether conformer search
result = submit_conformer_search_workflow(
    initial_molecule="CCOCC"
)

# Basic butane conformer search with rapid mode
result = submit_conformer_search_workflow(
    initial_molecule="CCCC",
    conf_gen_mode="rapid",
    name="Butane Conformers"
)

# Thorough conformer search with solvent
result = submit_conformer_search_workflow(
    initial_molecule="CC(C)CC(C(=O)O)N",  # Leucine
    conf_gen_mode="meticulous",
    solvent="water",
    final_method="wb97x-d3_def2-tzvp",
    name="Leucine Conformers in Water"
)
```

---

### submit_scan_workflow

**Description**: Submit a potential energy surface scan workflow. Performs systematic scans along specified molecular coordinates to map the potential energy surface.

**Function Signature**:
```python
def submit_scan_workflow(
    initial_molecule: Annotated[str, "SMILES string to scan"],
    scan_settings: Annotated[str, "JSON string of scan parameters: '{\"type\": \"dihedral\"/\"bond\"/\"angle\", \"atoms\": [1-indexed], \"start\": value, \"stop\": value, \"num\": points}'"] = "",
    calculation_engine: Annotated[str, "Computational engine: 'omol25', 'xtb', 'psi4'"] = "omol25",
    calculation_method: Annotated[str, "Computational method (e.g., 'uma_m_omol', 'gfn2-xtb', 'b3lyp-d3bj')"] = "uma_m_omol",
    wavefront_propagation: Annotated[bool, "Whether to use wavefront propagation for scan"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Scan Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string to scan
- `scan_settings` (str, default: ""): JSON string of scan parameters: '{"type": "dihedral"/"bond"/"angle", "atoms": [1-indexed], "start": value, "stop": value, "num": points}'
- `calculation_engine` (str, default: "omol25"): Computational engine: 'omol25', 'xtb', 'psi4'
- `calculation_method` (str, default: "uma_m_omol"): Computational method (e.g., 'uma_m_omol', 'gfn2-xtb', 'b3lyp-d3bj')
- `wavefront_propagation` (bool, default: True): Whether to use wavefront propagation for scan
- `name` (str, default: "Scan Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

---

### submit_irc_workflow

**Description**: Submit an Intrinsic Reaction Coordinate (IRC) workflow. Performs IRC calculations to trace reaction paths from transition states to reactants and products.

**Function Signature**:
```python
def submit_irc_workflow(
    initial_molecule: Annotated[str, "SMILES string for IRC calculation"],
    method: Annotated[str, "Computational method for IRC (e.g., 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c')"] = "uma_m_omol",
    engine: Annotated[str, "Computational engine: 'omol25', 'xtb', 'psi4'"] = "omol25",
    preopt: Annotated[bool, "Whether to pre-optimize the transition state before IRC step"] = True,
    step_size: Annotated[float, "Step size for IRC path tracing in Bohr (typically 0.03-0.1)"] = 0.05,
    max_irc_steps: Annotated[int, "Maximum number of IRC steps in each direction"] = 30,
    name: Annotated[str, "Workflow name for identification and tracking"] = "IRC Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string for IRC calculation
- `method` (str, default: "uma_m_omol"): Computational method for IRC (e.g., 'uma_m_omol', 'gfn2_xtb', 'r2scan_3c')
- `engine` (str, default: "omol25"): Computational engine: 'omol25', 'xtb', 'psi4'
- `preopt` (bool, default: True): Whether to pre-optimize the transition state before IRC step
- `step_size` (float, default: 0.05): Step size for IRC path tracing in Bohr (typically 0.03-0.1)
- `max_irc_steps` (int, default: 30): Maximum number of IRC steps in each direction
- `name` (str, default: "IRC Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# IRC from SMILES
result = submit_irc_workflow(
    initial_molecule="N=C([O-])[OH2+]",  # Transition state SMILES
    name="HNCO + H₂O - IRC",
    preopt=True,  # Pre-optimize TS
    method="gfn2_xtb",
    engine="xtb"
)
```

---

## Molecular Properties

### submit_pka_workflow

**Description**: Submit a microscopic pKa prediction workflow. Calculates site-specific pKa values for individual ionizable groups considering their local environment and molecular interactions.

**Function Signature**:
```python
def submit_pka_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule to calculate pKa"],
    pka_range: Annotated[List[float], "pKa range [min, max] to search (e.g., [2, 12])"] = [2, 12],
    deprotonate_elements: Annotated[str, "Comma-separated elements for deprotonation (e.g., 'N,O,S'). Empty for auto-detect"] = "",
    protonate_elements: Annotated[str, "Comma-separated elements for protonation (e.g., 'N,O'). Empty for auto-detect"] = "",
    mode: Annotated[str, "Calculation mode: 'rapid', 'careful', or 'meticulous'"] = "careful",
    name: Annotated[str, "Workflow name for identification and tracking"] = "pKa Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string of the molecule to calculate pKa
- `pka_range` (List[float], default: [2, 12]): pKa range [min, max] to search (e.g., [2, 12])
- `deprotonate_elements` (str, default: ""): Comma-separated elements for deprotonation (e.g., 'N,O,S'). Empty for auto-detect
- `protonate_elements` (str, default: ""): Comma-separated elements for protonation (e.g., 'N,O'). Empty for auto-detect
- `mode` (str, default: "careful"): Calculation mode: 'rapid', 'careful', or 'meticulous'
- `name` (str, default: "pKa Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Phenol pKa
result = submit_pka_workflow(
    initial_molecule="Oc1ccccc1",
    name="pKa phenol",
    deprotonate_elements="[8]"  # Only consider oxygen
)

# Amino acid with custom range
result = submit_pka_workflow(
    initial_molecule="CC(C(=O)O)N",  # Alanine
    pka_range=[1, 13],
    mode="careful",
    name="Alanine pKa"
)
```

---

### submit_macropka_workflow

**Description**: Submit a macroscopic pKa workflow. Calculates overall protonation equilibria considering all ionizable sites simultaneously across pH range, providing macroscopic pKa values that account for cooperative effects.

**Function Signature**:
```python
def submit_macropka_workflow(
    initial_smiles: Annotated[str, "SMILES string of the molecule for macropKa calculation"],
    min_pH: Annotated[int, "Minimum pH value for the calculation range"] = 0,
    max_pH: Annotated[int, "Maximum pH value for the calculation range"] = 14,
    min_charge: Annotated[int, "Minimum molecular charge to consider"] = -2,
    max_charge: Annotated[int, "Maximum molecular charge to consider"] = 2,
    compute_solvation_energy: Annotated[bool, "Whether to compute solvation energy corrections"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "MacropKa Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_smiles` (str): SMILES string of the molecule for macropKa calculation
- `min_pH` (int, default: 0): Minimum pH value for the calculation range
- `max_pH` (int, default: 14): Maximum pH value for the calculation range
- `min_charge` (int, default: -2): Minimum molecular charge to consider
- `max_charge` (int, default: 2): Maximum molecular charge to consider
- `compute_solvation_energy` (bool, default: True): Whether to compute solvation energy corrections
- `name` (str, default: "MacropKa Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Simple molecule macropKa
result = submit_macropka_workflow(
    initial_smiles="CC(=O)O",  # Acetic acid
    min_pH=0,
    max_pH=14
)

# Complex molecule with custom charge range
result = submit_macropka_workflow(
    initial_smiles="CC(C)CC(C(=O)O)N",  # Leucine
    min_pH=1,
    max_pH=13,
    min_charge=-1,
    max_charge=2,
    name="Leucine MacropKa"
)
```

---

### submit_solubility_workflow

**Description**: Submit a solubility prediction workflow. Predicts solubility (log S) of a molecule in multiple solvents at various temperatures using machine learning models trained on experimental data.

**Function Signature**:
```python
def submit_solubility_workflow(
    initial_smiles: Annotated[str, "SMILES string of the molecule for solubility prediction"],
    solvents: Annotated[str, "JSON string list of solvents as SMILES or names (e.g., '[\"water\", \"ethanol\", \"CCO\"]'). Empty string uses defaults"] = "",
    temperatures: Annotated[str, "JSON string list of temperatures in Kelvin (e.g., '[298.15, 310.15]'). Empty string uses default range"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Solubility Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_smiles` (str): SMILES string of the molecule for solubility prediction
- `solvents` (str, default: ""): JSON string list of solvents as SMILES or names (e.g., '["water", "ethanol", "CCO"]'). Empty string uses defaults
- `temperatures` (str, default: ""): JSON string list of temperatures in Kelvin (e.g., '[298.15, 310.15]'). Empty string uses default range
- `name` (str, default: "Solubility Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Basic solubility prediction
result = submit_solubility_workflow(
    initial_smiles="CC(=O)Nc1ccc(O)cc1",
    solvents='["water", "ethanol"]',
    temperatures='[298.15, 310.15]'
)

# With SMILES solvents
result = submit_solubility_workflow(
    initial_smiles="CC(=O)O",
    solvents='["O", "CCO"]',  # water, ethanol as SMILES
    temperatures='[298.15]'
)
```

---

### submit_redox_potential_workflow

**Description**: Submit a redox potential calculation workflow. Calculates reduction and/or oxidation potentials for molecules using quantum chemistry methods to determine electron transfer properties.

**Function Signature**:
```python
def submit_redox_potential_workflow(
    initial_molecule: Annotated[str, "SMILES string for redox potential calculation"],
    reduction: Annotated[bool, "Whether to calculate reduction potential (gaining electron)"] = False,
    oxidization: Annotated[bool, "Whether to calculate oxidation potential (losing electron)"] = True,
    mode: Annotated[str, "Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)"] = "rapid",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Redox Potential Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string for redox potential calculation
- `reduction` (bool, default: False): Whether to calculate reduction potential (gaining electron)
- `oxidization` (bool, default: True): Whether to calculate oxidation potential (losing electron)
- `mode` (str, default: "rapid"): Calculation mode: 'rapid' (fast), 'careful' (balanced), or 'meticulous' (thorough)
- `name` (str, default: "Redox Potential Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Simple redox potential from SMILES
result = submit_redox_potential_workflow(
    initial_molecule="Cc1ccccc1",  # Toluene
    reduction=True,
    oxidization=True,
    name="Toluene Redox Potential"
)
```

---

### submit_descriptors_workflow

**Description**: Submit a molecular descriptors calculation workflow. Calculates comprehensive molecular descriptors including physical properties, electronic properties, structural features, and topological indices useful for machine learning applications.

**Function Signature**:
```python
def submit_descriptors_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule to calculate descriptors for"],
    name: Annotated[str, "Workflow name for identification and tracking"] = "Descriptors Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string of the molecule to calculate descriptors for
- `name` (str, default: "Descriptors Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Basic descriptor calculation
result = submit_descriptors_workflow(
    initial_molecule="CC(=O)Nc1ccc(O)cc1"
)

# For complex molecule
result = submit_descriptors_workflow(
    initial_molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    name="Caffeine Descriptors"
)
```

---

### submit_tautomer_search_workflow

**Description**: Submit a tautomer search workflow. Searches for different tautomeric forms of a molecule and evaluates their relative stabilities using quantum chemistry methods.

**Function Signature**:
```python
def submit_tautomer_search_workflow(
    initial_molecule: Annotated[str, "SMILES string to search for tautomers"],
    mode: Annotated[str, "Search mode: 'reckless', 'rapid', or 'careful' (other workflows use different modes)"] = "careful",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Tautomer Search Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string to search for tautomers
- `mode` (str, default: "careful"): Search mode: 'reckless', 'rapid', or 'careful' (other workflows use different modes)
- `name` (str, default: "Tautomer Search Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

---

## Reactivity Analysis

### submit_fukui_workflow

**Description**: Submit a Fukui indices calculation workflow. Calculates Fukui indices to predict molecular reactivity at different sites for electrophilic, nucleophilic, and radical attacks.

**Function Signature**:
```python
def submit_fukui_workflow(
    initial_molecule: Annotated[str, "SMILES string of the molecule to calculate Fukui indices for"],
    optimization_method: Annotated[str, "Method for geometry optimization (e.g., 'gfn2_xtb', 'uma_m_omol')"] = "gfn2_xtb",
    fukui_method: Annotated[str, "Method for Fukui indices calculation (e.g., 'gfn1_xtb', 'gfn2_xtb')"] = "gfn1_xtb",
    solvent_settings: Annotated[str, "JSON string for solvent settings. Empty string for vacuum"] = "",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Fukui Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_molecule` (str): SMILES string of the molecule to calculate Fukui indices for
- `optimization_method` (str, default: "gfn2_xtb"): Method for geometry optimization (e.g., 'gfn2_xtb', 'uma_m_omol')
- `fukui_method` (str, default: "gfn1_xtb"): Method for Fukui indices calculation (e.g., 'gfn1_xtb', 'gfn2_xtb')
- `solvent_settings` (str, default: ""): JSON string for solvent settings. Empty string for vacuum
- `name` (str, default: "Fukui Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Basic Fukui indices
result = submit_fukui_workflow(
    initial_molecule="CC(=O)O"
)

# With solvent and advanced methods
result = submit_fukui_workflow(
    initial_molecule="c1ccccc1N",
    optimization_method="r2scan_3c",
    fukui_method="gfn2_xtb",
    solvent_settings='{"solvent": "water"}',
    name="Aniline Fukui in Water"
)
```

---

## Protein & Drug Discovery

### submit_docking_workflow

**Description**: Submit a docking workflow. Performs molecular docking simulations for drug discovery, automatically handling protein creation from PDB ID and sanitization.

**Function Signature**:
```python
def submit_docking_workflow(
    protein: Annotated[str, "Protein UUID or PDB content/path for docking target"],
    pocket: Annotated[str, "JSON string defining binding pocket coordinates or 'auto' for automatic detection"],
    initial_molecule: Annotated[str, "SMILES string of the ligand molecule to dock"],
    do_csearch: Annotated[bool, "Whether to perform conformer search before docking"] = True,
    do_optimization: Annotated[bool, "Whether to optimize docked poses"] = True,
    name: Annotated[str, "Workflow name for identification and tracking"] = "Docking Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `protein` (str): Protein UUID or PDB content/path for docking target
- `pocket` (str): JSON string defining binding pocket coordinates or 'auto' for automatic detection
- `initial_molecule` (str): SMILES string of the ligand molecule to dock
- `do_csearch` (bool, default: True): Whether to perform conformer search before docking
- `do_optimization` (bool, default: True): Whether to optimize docked poses
- `name` (str, default: "Docking Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Example 1: Using PDB ID directly
result = submit_docking_workflow(
    protein="1HCK",  # PDB ID
    pocket="[[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]]",
    initial_molecule="CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1",
    name="CDK2 Docking"
)

# Example 2: Using existing protein UUID
result = submit_docking_workflow(
    protein="existing-protein-uuid",
    pocket="auto",  # Automatic pocket detection
    initial_molecule="CC(=O)Nc1ccc(O)cc1",
    do_csearch=True,
    do_optimization=False,
    name="Paracetamol Docking"
)
```

---

### submit_protein_cofolding_workflow

**Description**: Submit a protein cofolding workflow. Simulates protein-protein interactions and cofolding with optional ligand binding using advanced structure prediction models.

**Function Signature**:
```python
def submit_protein_cofolding_workflow(
    initial_protein_sequences: Annotated[str, "JSON string list of protein sequences for cofolding (e.g., '[\"MKLLV...\", \"MAHQR...\"]')"],
    initial_smiles_list: Annotated[str, "JSON string list of SMILES for ligands to include in cofolding (e.g., '[\"CCO\", \"CC(=O)O\"]'). Empty for protein-only"] = "",
    ligand_binding_affinity_index: Annotated[str, "JSON string mapping ligand indices to protein binding sites. Empty for automatic detection"] = "",
    use_msa_server: Annotated[bool, "Whether to use multiple sequence alignment server for better structure prediction"] = True,
    use_potentials: Annotated[bool, "Whether to include additional potentials in the calculation"] = False,
    model: Annotated[str, "Structure prediction model to use (e.g., 'boltz_2', 'alphafold3')"] = "boltz_2",
    name: Annotated[str, "Workflow name for identification and tracking"] = "Protein Cofolding Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
)
```

**Parameters**:
- `initial_protein_sequences` (str): JSON string list of protein sequences for cofolding (e.g., '["MKLLV...", "MAHQR..."]')
- `initial_smiles_list` (str, default: ""): JSON string list of SMILES for ligands to include in cofolding (e.g., '["CCO", "CC(=O)O"]'). Empty for protein-only
- `ligand_binding_affinity_index` (str, default: ""): JSON string mapping ligand indices to protein binding sites. Empty for automatic detection
- `use_msa_server` (bool, default: True): Whether to use multiple sequence alignment server for better structure prediction
- `use_potentials` (bool, default: False): Whether to include additional potentials in the calculation
- `model` (str, default: "boltz_2"): Structure prediction model to use (e.g., 'boltz_2', 'alphafold3')
- `name` (str, default: "Protein Cofolding Workflow"): Workflow name for identification and tracking
- `folder_uuid` (str, default: ""): UUID of folder to organize this workflow. Empty string uses default folder
- `max_credits` (int, default: 0): Maximum credits to spend on this calculation. 0 for no limit

**Examples**:
```python
# Protein-ligand cofolding with CDK2 kinase
result = submit_protein_cofolding_workflow(
    initial_protein_sequences='["MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"]',
    initial_smiles_list='["CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1"]',
    ligand_binding_affinity_index="0",
    name="Cofolding CDK2 with ligand"
)
```

---

## Molecule Management

### molecule_lookup

**Description**: Convert molecule names to SMILES using Chemical Identifier Resolver (CIR). Enables natural language input for molecules by converting common names, IUPAC names, CAS numbers, and other identifiers to SMILES strings.

**Function Signature**:
```python
def molecule_lookup(
    molecule_name: Annotated[str, "Common name, IUPAC name, or CAS number of molecule (e.g., 'aspirin', 'caffeine', '50-78-2')"],
    fallback_to_input: Annotated[bool, "If lookup fails, return the input string assuming it might be SMILES"] = False
) -> str
```

**Parameters**:
- `molecule_name` (str): Common name, IUPAC name, or CAS number of molecule (e.g., 'aspirin', 'caffeine', '50-78-2')
- `fallback_to_input` (bool, default: False): If lookup fails, return the input string assuming it might be SMILES

**Returns**: str - SMILES string if successful, error message if not found

**Supported Input Types**:
- Common names: 'aspirin', 'caffeine', 'benzene', 'glucose'
- IUPAC names: '2-acetoxybenzoic acid', '1,3,7-trimethylpurine-2,6-dione'
- CAS numbers: '50-78-2' (aspirin), '58-08-2' (caffeine)
- InChI strings
- Already valid SMILES (will be validated)

**Examples**:
```python
# Common drug name
result = molecule_lookup("aspirin")
# Returns: "CC(=O)Oc1ccccc1C(=O)O"

# IUPAC name
result = molecule_lookup("2-acetoxybenzoic acid")
# Returns: "CC(=O)Oc1ccccc1C(=O)O"

# CAS number
result = molecule_lookup("50-78-2")
# Returns: "CC(=O)Oc1ccccc1C(=O)O"
```

---

### batch_molecule_lookup

**Description**: Convert multiple molecule names to SMILES in batch. Useful for preparing multiple molecules for workflows or screening.

**Function Signature**:
```python
def batch_molecule_lookup(
    molecule_names: Annotated[List[str], "List of molecule names to convert to SMILES"],
    skip_failures: Annotated[bool, "Skip molecules that fail lookup instead of stopping"] = True
) -> Dict[str, str]
```

**Parameters**:
- `molecule_names` (List[str]): List of molecule names to convert to SMILES
- `skip_failures` (bool, default: True): Skip molecules that fail lookup instead of stopping

**Returns**: Dict[str, str] - Dictionary mapping molecule names to SMILES strings

**Examples**:
```python
# Drug screening set
result = batch_molecule_lookup([
    "aspirin",
    "ibuprofen", 
    "paracetamol",
    "caffeine"
])
# Returns: {
#     "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
#     "ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
#     "paracetamol": "CC(=O)Nc1ccc(O)cc1",
#     "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
# }
```

---

### validate_smiles

**Description**: Validate a SMILES string and return basic molecular properties using RDKit.

**Function Signature**:
```python
def validate_smiles(
    smiles: Annotated[str, "SMILES string to validate"]
) -> Dict[str, Any]
```

**Parameters**:
- `smiles` (str): SMILES string to validate

**Returns**: Dict[str, Any] - Dictionary containing validation results and basic molecular properties

**Examples**:
```python
result = validate_smiles("CC(=O)O")
# Returns: {
#     "valid": True,
#     "canonical_smiles": "CC(=O)O",
#     "molecular_formula": "C2H4O2",
#     "molecular_weight": 60.05
# }
```

---

## Protein Management

### create_protein_from_pdb_id

**Description**: Create a protein from a PDB ID.

**Function Signature**:
```python
def create_protein_from_pdb_id(
    name: Annotated[str, "Name for the protein"],
    code: Annotated[str, "PDB ID code (e.g., '1HCK')"]
) -> Dict[str, Any]
```

**Parameters**:
- `name` (str): Name for the protein
- `code` (str): PDB ID code (e.g., '1HCK')

**Returns**: Dict[str, Any] - Dictionary containing protein information (uuid, name, sanitized, created_at)

---

### retrieve_protein

**Description**: Retrieve a protein by UUID.

**Function Signature**:
```python
def retrieve_protein(
    uuid: Annotated[str, "UUID of the protein to retrieve"]
) -> Dict[str, Any]
```

**Parameters**:
- `uuid` (str): UUID of the protein to retrieve

**Returns**: Dict[str, Any] - Dictionary containing the protein data

---

### list_proteins

**Description**: List proteins with pagination support.

**Function Signature**:
```python
def list_proteins(
    page: Annotated[int, "Page number (0-indexed)"] = 0,
    size: Annotated[int, "Number per page"] = 20
) -> List[Dict[str, Any]]
```

**Parameters**:
- `page` (int, default: 0): Page number (0-indexed)
- `size` (int, default: 20): Number per page

**Returns**: List[Dict[str, Any]] - List of protein dictionaries

---

### upload_protein

**Description**: Upload a custom protein structure.

**Function Signature**:
```python
def upload_protein(
    name: Annotated[str, "Name for the protein"],
    protein_data: Annotated[str, "PDB format protein structure data"]
) -> Dict[str, Any]
```

**Parameters**:
- `name` (str): Name for the protein
- `protein_data` (str): PDB format protein structure data

**Returns**: Dict[str, Any] - Dictionary containing uploaded protein information

---

### delete_protein

**Description**: Remove protein from workspace.

**Function Signature**:
```python
def delete_protein(
    uuid: Annotated[str, "UUID of the protein to delete"]
) -> Dict[str, Any]
```

**Parameters**:
- `uuid` (str): UUID of the protein to delete

**Returns**: Dict[str, Any] - Dictionary containing deletion status

---

### sanitize_protein

**Description**: Clean and validate protein structures.

**Function Signature**:
```python
def sanitize_protein(
    uuid: Annotated[str, "UUID of the protein to sanitize"]
) -> Dict[str, Any]
```

**Parameters**:
- `uuid` (str): UUID of the protein to sanitize

**Returns**: Dict[str, Any] - Dictionary containing sanitization results

---

## Workflow Management

### workflow_get_status

**Description**: Get the current status of a workflow with explicit status information. Includes comprehensive status mapping from numeric codes to human-readable descriptions.

**Function Signature**:
```python
def workflow_get_status(
    workflow_uuid: Annotated[str, "UUID of the workflow to check status"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to check status

**Returns**: Dict[str, Any] - Dictionary with status_code, status_description, is_successful, is_failed, is_running flags

**Status Codes**:
- 0: QUEUED - Job created, user below max_concurrency
- 1: RUNNING - Job still in progress
- 2: COMPLETED_OK - Job finished successfully
- 3: FAILED - Job encountered an error
- 4: STOPPED - Job stopped externally (e.g., timeout)
- 5: AWAITING_QUEUE - User exceeded max_concurrency

---

### workflow_stop

**Description**: Stop a running workflow.

**Function Signature**:
```python
def workflow_stop(
    workflow_uuid: Annotated[str, "UUID of the workflow to stop"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to stop

**Returns**: Dict[str, Any] - Dictionary containing stop operation results

---

### workflow_delete

**Description**: Delete a workflow permanently from the workspace.

**Function Signature**:
```python
def workflow_delete(
    workflow_uuid: Annotated[str, "UUID of the workflow to delete"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to delete

**Returns**: Dict[str, Any] - Dictionary containing deletion results

---

### retrieve_workflow

**Description**: Retrieve complete workflow data and results by UUID.

**Function Signature**:
```python
def retrieve_workflow(
    workflow_uuid: Annotated[str, "UUID of the workflow to retrieve"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to retrieve

**Returns**: Dict[str, Any] - Complete workflow data including results if available

---

### retrieve_calculation_molecules

**Description**: Extract molecular structures from completed calculations.

**Function Signature**:
```python
def retrieve_calculation_molecules(
    workflow_uuid: Annotated[str, "UUID of the workflow to extract molecules from"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to extract molecules from

**Returns**: Dict[str, Any] - Dictionary containing extracted molecular structures

---

### list_workflows

**Description**: List all workflows with filtering and pagination options.

**Function Signature**:
```python
def list_workflows(
    page: Annotated[int, "Page number (0-indexed)"] = 0,
    size: Annotated[int, "Number of workflows per page"] = 20,
    status_filter: Annotated[str, "Filter by workflow status (optional)"] = ""
) -> List[Dict[str, Any]]
```

**Parameters**:
- `page` (int, default: 0): Page number (0-indexed)
- `size` (int, default: 20): Number of workflows per page
- `status_filter` (str, default: ""): Filter by workflow status (optional)

**Returns**: List[Dict[str, Any]] - List of workflow dictionaries

---

### workflow_update

**Description**: Modify workflow parameters and metadata.

**Function Signature**:
```python
def workflow_update(
    workflow_uuid: Annotated[str, "UUID of the workflow to update"],
    updates: Annotated[Dict[str, Any], "Dictionary of updates to apply"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to update
- `updates` (Dict[str, Any]): Dictionary of updates to apply

**Returns**: Dict[str, Any] - Dictionary containing update results

---

### workflow_is_finished

**Description**: Check if a workflow is complete (successful or failed).

**Function Signature**:
```python
def workflow_is_finished(
    workflow_uuid: Annotated[str, "UUID of the workflow to check"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to check

**Returns**: Dict[str, Any] - Dictionary with finished status and completion details

---

### workflow_delete_data

**Description**: Remove workflow data while keeping metadata record.

**Function Signature**:
```python
def workflow_delete_data(
    workflow_uuid: Annotated[str, "UUID of the workflow to delete data from"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to delete data from

**Returns**: Dict[str, Any] - Dictionary containing data deletion results

---

### workflow_fetch_latest

**Description**: Get the most recent workflow results and updates.

**Function Signature**:
```python
def workflow_fetch_latest(
    workflow_uuid: Annotated[str, "UUID of the workflow to fetch latest data"]
) -> Dict[str, Any]
```

**Parameters**:
- `workflow_uuid` (str): UUID of the workflow to fetch latest data

**Returns**: Dict[str, Any] - Dictionary containing the latest workflow data and results

---

## Usage Notes

### General Guidelines
- **Workflow Duration**: Simple calculations finish in seconds, complex workflows (conformer searches, large proteins, docking) can take 10-30 minutes
- **Adaptive Polling**: For running workflows, check frequently at first (every 30s for 2 min), then less frequently
- **Credit Management**: Use `max_credits` parameter to control computational spending
- **Organization**: Use `folder_uuid` to organize related workflows

### Input Formats
- **Molecules**: SMILES strings (e.g., "CCO" for ethanol)
- **Proteins**: PDB IDs (e.g., "1ABC") or full PDB content
- **Solvents**: Names ("water", "ethanol") or SMILES ("O", "CCO")
- **Temperatures**: Celsius/Kelvin, comma-separated or JSON arrays

### Error Handling
- All API calls include comprehensive error handling
- Solvent name-to-SMILES conversion with fallback
- SMILES parsing validation before submission
- Detailed logging for debugging workflow issues

### Best Practices
- Always check workflow status before retrieving results
- Use appropriate calculation modes based on accuracy needs
- Consider computational cost when setting parameters
- Organize workflows using folders for large projects