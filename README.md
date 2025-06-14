# Rowan MCP Server

Connect AI assistants to Rowan's computational chemistry platform via Model Context Protocol (MCP).

## Setup

1. **Get API Key**: Create account at [labs.rowansci.com](https://labs.rowansci.com)
2. **Install**: `uv sync`  
3. **Configure**: `echo "ROWAN_API_KEY=your_key" > .env`
4. **Start**: `uv run python -m src`

## AI Assistant Configuration

Add to your Claude Desktop config:

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