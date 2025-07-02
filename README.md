# Rowan MCP Server

This project wraps an MCP (Model Context Protocol) around Rowan's tools, making it easy for users to submit complex quantum chemistry calculations in natural everyday language. 

---

## **Quick Installation**

### **1. Install**
```bash
pip install git+https://github.com/k-yenko/rowan-mcp.git
```

### **2. Get API Key**
- Visit [labs.rowansci.com](https://labs.rowansci.com)
- Create free account → Generate API key

### **3. Configure Your MCP Client**

**Claude Desktop Example:**
```json
{
  "mcpServers": {
    "rowan": {
      "command": "rowan-mcp",
      "env": {
        "ROWAN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### **4. Start Using**
Ask your AI: *"Calculate the pKa of aspirin"* or *"Optimize the geometry of caffeine"*

---

## **What You Can Do** 

Ask the LLM to:
- **Calculate drug properties**: *"Predict drug-likeness of aspirin"*
- **Optimize molecular structures**: *"Optimize the geometry of aspirin"*  
- **Predict chemical behavior**: *"What's the pKa of acetic acid?"*
- **Run calculations**: *"Calculate the HOMO and LUMO of benzene"*

## **System Requirements**

- **Python 3.10+** (Python 3.11+ recommended)
- **Rowan API key** (free at [labs.rowansci.com](https://labs.rowansci.com))
- **MCP-compatible client** (Claude Desktop, Continue, etc.)

---

## Development Setup

For those that would like to contribute (!):

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

### Chemistry Calculations
- `rowan_basic_calculation` - Energy, optimization, frequencies
- `rowan_multistage_opt` - geometry optimization  
- `rowan_electronic_properties` - HOMO/LUMO, orbitals
- `rowan_molecular_dynamics` - MD simulations

### Molecular Properties
- `rowan_pka` - Acid/base strength
- `rowan_conformers` - Conformational search
- `rowan_tautomers` - Tautomer enumeration
- `rowan_descriptors` - ML-ready molecular features
- `rowan_solubility` - Aqueous solubility
- `rowan_redox_potential` - Electrochemical potentials

### Drug Discovery
- `rowan_admet` - ADME-Tox properties


### Reactivity Analysis  
- `rowan_fukui` - Reactivity sites
- `rowan_spin_states` - Spin multiplicities

### Project Management
- `rowan_folder_create/list/update/delete` - Organize calculations
- `rowan_workflow_create/list/status/stop` - Manage workflows

## Requirements

- Python 3.10+
- Rowan API key
- MCP-compatible AI assistant (Claude Desktop, etc.)

## Getting Help

- **Documentation**: [docs.rowansci.com](https://docs.rowansci.com/)
- or ping me! 

---

## **Todo**

- [ ] Remove unnecessary AI spaghetti formatting 🙃
- [ ] Some complex conformer searches hang on "running"
- [ ] Edit MCP one-liner context
- [ ] Transition state finding and IRC
- [ ] `rowan_scan` - Potential energy surfaces
- [ ] `rowan_irc` - Reaction coordinate following
- [ ] `rowan_docking` - Protein-ligand docking
- [ ] Folder listing API bug (returns 500 error)
- [ ] Multistage optimization sometimes shows unexpected imaginary frequencies
- [ ] Some calculations show as finished in logs but not in Rowan UI
