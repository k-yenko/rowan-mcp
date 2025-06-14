# Rowan MCP Server

**Connect AI assistants to chemistry calculations**

This tool lets AI assistants (like Claude) run real chemistry calculations through Rowan's platform. Ask your AI to calculate molecular properties, optimize structures, or predict how molecules behave - and get scientific results back.

## Setup

1. **Get API Key**: Create account at [labs.rowansci.com](https://labs.rowansci.com)
2. **Install**: `uv sync`  
3. **Configure**: `echo "ROWAN_API_KEY=your_key" > .env`
4. **Start**: `uv run python -m src`

## AI Assistant Configuration

🤖 **AI Integration**: Works with any AI assistant that supports MCP

☁️ **Cloud Computing**: Uses Rowan's platform - no need to install complex chemistry software

## Quick Start

### 1. Get a Rowan Account
- Visit [labs.rowansci.com](https://labs.rowansci.com)
- Create a free account
- Generate an API key from your account settings

### 2. Install & Setup
```bash
# Clone this repository
git clone <repository-url>
cd rowan-mcp

# Install dependencies
uv sync

# Add your API key to .env file
echo "ROWAN_API_KEY=your_actual_api_key_here" > .env
```

### 3. Start the Server

**Option A: HTTP Server (Recommended)**
```bash
# Start HTTP server on 127.0.0.1:6276/mcp
uv run python -c "from src.http_server import main; main()"
```

**Option B: STDIO Mode (Traditional)**
```bash  
# For traditional stdio-based MCP clients
uv run python -m src
```

### 4. Connect Your AI Assistant

**Option A: HTTP Connection (Modern)**
```json
{
  "mcpServers": {
    "rowan": {
      "command": "uv",
      "args": ["run", "python", "-m", "src"],
      "cwd": "/path/to/rowan-mcp"
    }
  }
}
```

## Available Tools

### Core Chemistry Calculations
- `rowan_basic_calculation` - Energy, optimization, frequencies
- `rowan_multistage_opt` - **Recommended** geometry optimization  
- `rowan_electronic_properties` - HOMO/LUMO, orbitals
- `rowan_molecular_dynamics` - MD simulations
- `rowan_scan` - Potential energy surfaces
- `rowan_irc` - Reaction coordinate following

### Molecular Properties
- `rowan_pka` - Acid/base strength
- `rowan_conformers` - Conformational search
- `rowan_tautomers` - Tautomer enumeration
- `rowan_descriptors` - ML-ready molecular features
- `rowan_solubility` - Aqueous solubility
- `rowan_redox_potential` - Electrochemical potentials
- `rowan_bde` - Bond dissociation energies

### Drug Discovery
- `rowan_admet` - ADME-Tox properties
- `rowan_docking` - Protein-ligand docking

### Reactivity Analysis  
- `rowan_fukui` - Reactivity sites
- `rowan_spin_states` - Spin multiplicities
- `rowan_hydrogen_bond_basicity` - H-bond acceptor strength

### Project Management
- `rowan_folder_create/list/update/delete` - Organize calculations
- `rowan_workflow_create/list/status/stop` - Manage workflows

## Usage Examples

```python
# Calculate pKa
rowan_pka(name="aspirin", molecule="CC(=O)OC1=CC=CC=C1C(=O)O")

# Optimize geometry (recommended)
rowan_multistage_opt(name="methane", molecule="C")

# Drug properties
rowan_admet(name="caffeine", molecule="CN1C=NC2=C1C(=O)N(C(=O)N2C)C")

# Protein-ligand docking
rowan_docking(name="inhibitor", protein="1ABC", ligand="CCO")
```

## Key Features

- **15+ specialized chemistry tools** with detailed documentation
- **Automatic method selection** for optimal speed/accuracy balance
- **Real-time job monitoring** with status tracking
- **Project organization** with folders and workflows
- **Comprehensive logging** for debugging

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Rowan API key
- MCP-compatible AI assistant

## Getting Help

- **API Issues**: support@rowansci.com
- **Documentation**: [docs.rowansci.com](https://docs.rowansci.com)
- **Tool Help**: Use `rowan_available_workflows()` for complete tool list 

## Enhanced Tutorial Examples
The `rowan_compute` tool has been enhanced with comprehensive examples based on official Rowan tutorials. It now provides intelligent context and formatting for common calculation types:

### Supported Calculation Types
- **Optimization & Frequencies**: Geometry optimization with vibrational analysis
- **Single Point Energy**: Energy calculation at fixed geometry  
- **Transition State Optimization**: Finding and optimizing transition states
- **Orbital Calculations**: Electronic structure and molecular orbital analysis
- **Conformer Search**: Multiple conformer generation and analysis
- **Potential Energy Scans**: Energy profiles along reaction coordinates

### Tutorial Examples
Run the comprehensive tutorial examples:
```bash
python examples/tutorial_examples.py
```

This demonstrates real usage patterns from the [official Rowan tutorials](https://docs.rowansci.com/tutorials/), including:
- Ethane optimization and frequencies (like the official tutorial)
- Benzene single point energy calculations
- Methanol geometry optimization
- Transition state finding
- Water orbital calculations

## 🧬 Protein-Ligand Docking

The Rowan MCP server includes specialized support for protein-ligand docking calculations. Due to the complexity of protein-ligand systems, there are specific format requirements:

### Supported Protein Formats
- **PDB ID**: 4-character codes like `1ABC` (recommended)
- **PDB File Content**: Direct PDB file content
- **Protein Sequences**: Amino acid sequences (experimental)

### Supported Ligand Formats
- **SMILES**: Standard chemical notation like `CCO` or `CC(=O)O`

### Usage Examples

```python
# Using PDB ID (recommended)
result = rowan_docking(
    name="HIV-1 protease inhibitor",
    protein="1HTM",  # HIV-1 protease PDB ID
    ligand="CC(C)c1nc(cs1)CN(C)C(=O)N[C@H](C(C)C)C(=O)N",
)

# The tool will automatically try multiple approaches:
# 1. PDB ID format
# 2. Ligand-only calculation
# 3. Combined format
```

### Troubleshooting SMILES Parsing Errors

If you see errors like:
```
SMILES Parse Error: syntax error while parsing: GLP1R:GLP1
```

This means the system is trying to parse protein names/sequences as chemical SMILES strings. **Solutions:**

1. **Use the dedicated `rowan_docking()` tool** instead of `rowan_compute()` for protein-ligand work
2. **Use valid PDB IDs** from the Protein Data Bank (https://www.rcsb.org/)
3. **Ensure ligands are valid SMILES** strings

### Common Mistakes to Avoid
- ❌ `"glp1r+glp1"` - Not valid SMILES
- ❌ `"GLP1R:GLP1"` - Protein names, not chemical structures  
- ❌ `"GLPR1_HUMAN"` - UniProt IDs are not directly supported

- ✅ `"1F0K"` - Valid PDB ID for GLP-1 receptor
- ✅ `"CCO"` - Valid SMILES for ethanol

---

**Made with ❤️ for the computational chemistry community** 
>>>>>>> 3d23a74d9a5fe2f085d636431d694194fdef2b5b
