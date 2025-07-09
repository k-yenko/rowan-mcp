# Rowan MCP Server

This project wraps an MCP (Model Context Protocol) around Rowan's tools, making it easy for users to submit complex quantum chemistry calculations in natural everyday language. 

---

## **Quick Install - Desktop Extension**

**For Claude Desktop users - this is the easiest way:**

1. **Download** the extension: [`rowan-dxt.dxt`](./rowan-dxt.dxt) 
2. **Drag and drop** the file into **Claude Desktop > Settings > Extensions**
3. **Enter your API key** from [labs.rowansci.com](https://labs.rowansci.com) 
4. **Enable** the MCP tool in the extension settings
5. **Start chatting** Try: *"Using the Rowan MCP tool, calculate the pKa of aspirin"*

That's it - no command line setup needed!

---

## **Manual Installation**

**For developers or users who prefer command-line setup:**

### **1. Clone and Setup**
```bash
git clone https://github.com/k-yenko/rowan-mcp.git
cd rowan-mcp
uv sync
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
      "command": "uv",
      "args": ["run", "python", "-m", "src"],
      "cwd": "/path/to/rowan-mcp",
      "env": {
        "ROWAN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

*Replace `/path/to/rowan-mcp` with the actual path where you cloned the repository*

**To find your path:**
```bash
# After cloning, run this in the rowan-mcp directory:
pwd
# Copy the output and use it as your "cwd" value
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
- **[uv](https://docs.astral.sh/uv/) package manager** 
- **Rowan API key** (free at [labs.rowansci.com](https://labs.rowansci.com))
- **MCP-compatible client** (Claude Desktop, Continue, etc.)

## **Testing Your Setup**

You can test the server directly:
```bash
# In the rowan-mcp directory:
uv run python -m src --help
```

## **Development**

The installation above is the same for development! Additional commands:
```bash
# Run server in HTTP/SSE mode  
uv run python -m src --http

# Run server in STDIO mode (default)
uv run python -m src
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
- [ ] add in h-bond, BDE and macroscopic pka, logD, BBB
- [ ] Folder listing API bug (returns 500 error)
- [ ] Multistage optimization sometimes shows unexpected imaginary frequencies
- [ ] Some calculations show as finished in logs but not in Rowan UI

## Citation

If you use this MCP tool in your research, please cite the underlying Rowan platform:

Rowan Scientific. https://www.rowansci.com (accessed 2025-07-01).

For complete citation information including specific computational engines, methods, and workflows used in your calculations, please refer to [Rowan's citation guidelines](https://docs.rowansci.com/citations).
