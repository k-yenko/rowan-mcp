# Rowan MCP Server

MCP server for making it easy to run Rowan's molecular design and simulation tools.

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

## **Package Installation**

### **Option 1: Auto-Install (No manual installation needed!)**

Just add this to your MCP configuration and it will automatically install and run:

**HTTP/SSE configuration:**
```json
{
  "mcpServers": {
    "rowan": {
      "type": "http",
      "url": "http://127.0.0.1:6276/sse"
    }
  }
}
```

Then start the server:
```bash
# Set your API key
export ROWAN_API_KEY="your_api_key_here"

# Start the HTTP server
uvx --from rowan-mcp rowan-mcp
```

### **Option 2: Manual Installation**

If you prefer to install the package first:

**Using uv:**
```bash
uv add rowan-mcp
```

**Using pip:**
```bash
pip install rowan-mcp
```

Then configure and start:
```json
{
  "mcpServers": {
    "rowan": {
      "type": "http", 
      "url": "http://127.0.0.1:6276/sse"
    }
  }
}
```

```bash
# Set API key and start server
export ROWAN_API_KEY="your_api_key_here"
rowan-mcp
```

### **Get API Key**

Visit [labs.rowansci.com](https://labs.rowansci.com) → Create account → Generate API key

### **Start Using**

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
- **Package manager**: [uv](https://docs.astral.sh/uv/) (recommended) or pip
- **Rowan API key** (free at [labs.rowansci.com](https://labs.rowansci.com))
- **MCP-compatible client** (Claude Desktop, etc.)

**Development commands** (if you cloned the repo):
```bash
# Run from source
export ROWAN_API_KEY="your_api_key_here"
uv run python -m rowan_mcp
```

---

## **Available Tools**

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

## **Requirements**

- Python 3.10+
- Rowan API key
- MCP-compatible AI assistant (Claude Desktop, etc.)

## **Getting Help**

- **Documentation**: [docs.rowansci.com](https://docs.rowansci.com/)
- or ping me! 

---

## **Todo**

- [X] Remove unnecessary AI spaghetti formatting
- [X] Remove no longer necessary API config lines
- [ ] Some complex conformer searches hang on "running"
- [X] Edit MCP one-liner context
- [ ] Transition state finding and IRC
- [X] `rowan_scan` - Potential energy surfaces
- [ ] `rowan_docking` - Protein-ligand docking
- [X] add in h-bond, BDE and macroscopic pka, logD, BBB
- [ ] Folder listing API bug (returns 500 error) - Rowan side?
- [ ] Multistage optimization sometimes shows unexpected imaginary frequencies
- [X] Some calculations show as finished in logs but not in Rowan UI
- [ ] Can you hook up Rowan's visual capabilites? 

## **Citation**

If you use this MCP tool in your research, please cite the underlying Rowan platform:

Rowan Scientific. https://www.rowansci.com (accessed 2025-07-01).

For complete citation information including specific computational engines, methods, and workflows used in your calculations, please refer to [Rowan's citation guidelines](https://docs.rowansci.com/citations).

---

## **Publishing (Maintainer Notes)**

To publish a new version to PyPI:

```bash
# Update version in pyproject.toml and rowan_mcp/__init__.py
# Build the package
uv build

# Publish to PyPI (requires API token)
uv publish

# Or publish to TestPyPI first
uv publish --index-url https://test.pypi.org/simple/
```

To update the dxt file:
```bash
# After updating the PyPI package, update all changed tools/functions

# Then update the desktop extension
dxt pack rowan-dxt
```
### MCP inspector
```bash
# Start the server first
export ROWAN_API_KEY="your_api_key_here" 
uv run python -m rowan_mcp &

# Then inspect
npx @modelcontextprotocol/inspector http://127.0.0.1:6276/sse
```        