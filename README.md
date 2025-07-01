# Rowan MCP Server

⚠️ **IMPORTANT**: This server requires **Python 3.10+** due to rowan-python package dependencies. Use Python 3.11+ for best compatibility.

**🔧 For Python 3.11 users:** If you encounter `ModuleNotFoundError` with rowan-python, install dependencies specifically for Python 3.11:
```bash
/opt/homebrew/bin/python3.11 -m pip install rowan-python fastmcp pubchempy
```

**Connect AI assistants to chemistry calculations**

This tool lets AI assistants (like Claude) run real chemistry calculations through Rowan's platform. Ask your AI to calculate molecular properties, optimize structures, or predict how molecules behave - and get scientific results back.

## 🚀 Quick Installation (For Users)

### 1. Install the Package
```bash
# Install directly from GitHub
pip install git+https://github.com/k-yenko/rowan-mcp.git

# Or if you have the source code locally
pip install .
```

### 2. Get Your API Key
- Visit [labs.rowansci.com](https://labs.rowansci.com)
- Create a free account  
- Generate an API key from your account settings

### 3. Configure Your MCP Client

Add this configuration to your MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "rowan": {
      "command": "rowan-mcp",
      "env": {
        "ROWAN_API_KEY": "your_rowan_api_key_here"
      }
    }
  }
}
```

**That's it!** Your MCP client will automatically launch the Rowan server when needed.

### Alternative: Set Environment Variable
Instead of putting the API key in the config, you can set it globally:
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export ROWAN_API_KEY="your_rowan_api_key_here"
```

Then use this simpler config:
```json
{
  "mcpServers": {
    "rowan": {
      "command": "rowan-mcp"
    }
  }
}
```

---

## 🛠️ Development Setup

For developers who want to modify or contribute to this project:

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager  
- Rowan API key

### Setup
```bash
# Clone this repository
git clone https://github.com/k-yenko/rowan-mcp.git
cd rowan-mcp

# Install dependencies
uv sync

# Add your API key to .env file
echo "ROWAN_API_KEY=your_actual_api_key_here" > .env
```

### Development Commands
```bash
# Run server in STDIO mode
uv run python -m src

# Run server in HTTP/SSE mode  
uv run python -m src --http

# Show help
uv run python -m src --help
```

### Development MCP Configuration
For development, use this configuration that points to your local project:
```json
{
  "mcpServers": {
    "rowan": {
      "command": "uv",
      "args": ["run", "python", "-m", "src"],
      "cwd": "/path/to/your/rowan-mcp",
      "env": {
        "ROWAN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

---

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

### Drug Discovery
- `rowan_admet` - ADME-Tox properties
- `rowan_docking` - Protein-ligand docking

### Reactivity Analysis  
- `rowan_fukui` - Reactivity sites
- `rowan_spin_states` - Spin multiplicities

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
- Rowan API key
- MCP-compatible AI assistant (Claude Desktop, etc.)

## Getting Help

- **API Issues**: support@rowansci.com
- **Documentation**: [docs.rowansci.com](https://docs.rowansci.com)
- **Tool Help**: Use `rowan_available_workflows()` for complete tool list

## Troubleshooting

### Common Installation Issues

**Python Version**: Make sure you're using Python 3.10+
```bash
python --version  # Should show 3.10 or higher
```

**API Key Not Found**: Make sure your API key is properly set
```bash
# Test your installation
rowan-mcp --help
```

**MCP Client Connection**: If your MCP client can't find the command:
```bash
# Make sure the package is installed in the right environment
which rowan-mcp
```

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

1. **Use the dedicated `rowan_docking()` tool** for protein-ligand work
2. **Use valid PDB IDs** from the Protein Data Bank (https://www.rcsb.org/)
3. **Ensure ligands are valid SMILES** strings

### Common Mistakes to Avoid
- ❌ `"glp1r+glp1"` - Not valid SMILES
- ❌ `"GLP1R:GLP1"` - Protein names, not chemical structures  
- ❌ `"GLPR1_HUMAN"` - UniProt IDs are not directly supported

- ✅ `"1F0K"` - Valid PDB ID for GLP-1 receptor
- ✅ `"CCO"` - Valid SMILES for ethanol

---
