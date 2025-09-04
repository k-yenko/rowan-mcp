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

- **Python 3.11+** 
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
- `submit_basic_calculation_workflow` - Energy, optimization, frequencies with multiple engines (omol25, xtb, psi4)
- `submit_conformer_search_workflow` - Conformational search with multiple search modes (rapid/careful/meticulous)
- `submit_scan_workflow` - Molecular scans (dihedral, bond, angle) with wavefront propagation
- `submit_irc_workflow` - Intrinsic reaction coordinate calculations for transition states

### Molecular Properties
- `submit_pka_workflow` - Microscopic pKa calculations with customizable pH ranges and elements
- `submit_macropka_workflow` - Macroscopic pKa calculations across pH and charge ranges
- `submit_solubility_workflow` - Solubility predictions across multiple solvents and temperatures
- `submit_redox_potential_workflow` - Electrochemical reduction/oxidation potentials
- `submit_descriptors_workflow` - ML-ready molecular descriptors and features
- `submit_tautomer_search_workflow` - Tautomer enumeration with reckless/rapid/careful modes

### Reactivity Analysis  
- `submit_fukui_workflow` - Fukui indices for electrophilic/nucleophilic reactivity sites

### Protein & Drug Discovery
- `submit_docking_workflow` - Protein-ligand docking with conformer search and optimization
- `submit_protein_cofolding_workflow` - Multi-protein and protein-ligand cofolding predictions

### Molecule Management
- `molecule_lookup` - Convert molecule names, CAS numbers, IUPAC names to SMILES
- `batch_molecule_lookup` - Bulk molecule name to SMILES conversion
- `validate_smiles` - Validate and standardize SMILES strings

### Protein Management
- `create_protein_from_pdb_id` - Create protein from PDB ID (e.g., '1HCK')
- `retrieve_protein` - Get protein data by UUID
- `list_proteins` - List all available proteins
- `upload_protein` - Upload custom protein structures
- `delete_protein` - Remove protein from workspace
- `sanitize_protein` - Clean and validate protein structures

### Workflow Management
- `workflow_get_status` - Check workflow status with detailed progress information
- `workflow_stop` - Stop running workflows
- `workflow_delete` - Remove workflows from workspace
- `retrieve_workflow` - Get complete workflow data and results
- `retrieve_calculation_molecules` - Extract molecular structures from calculations
- `list_workflows` - List all workflows with filtering options
- `workflow_update` - Modify workflow parameters
- `workflow_is_finished` - Check if workflow is complete
- `workflow_delete_data` - Remove workflow data while keeping metadata
- `workflow_fetch_latest` - Get most recent workflow results

## **Requirements**

- Python 3.11+
- Rowan API key
- MCP-compatible AI assistant (Claude Desktop, etc.)

## **Getting Help**

- **Documentation**: [docs.rowansci.com](https://docs.rowansci.com/)
- or ping me! 

---

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