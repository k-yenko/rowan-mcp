# Rowan MCP Server

MCP server for making it easy to run Rowan's molecular design and simulation tools.

---

## **Installation**

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

**Total: 48 MCP Tools**
- 28 Dedicated Workflow Functions (all workflows from Rowan v2.1.9)
- 1 Batch Workflow Function
- 3 Molecule Lookup Tools
- 10 Workflow Management Tools
- 6 Protein Management Tools

---

### Chemistry Calculations
- `submit_basic_calculation_workflow` - Energy, optimization, frequencies with multiple engines (omol25, xtb, psi4)
- `submit_conformer_search_workflow` - Conformational search with multiple search modes (rapid/careful/meticulous)
- `submit_conformers_workflow` - Conformer generation and enumeration (different from conformer_search)
- `submit_multistage_opt_workflow` - Multi-stage geometry optimization with sequential accuracy levels
- `submit_scan_workflow` - Molecular scans (dihedral, bond, angle) with wavefront propagation
- `submit_irc_workflow` - Intrinsic reaction coordinate calculations for transition states

### Molecular Properties
- `submit_pka_workflow` - Microscopic pKa calculations with customizable pH ranges and elements
- `submit_macropka_workflow` - Macroscopic pKa calculations across pH and charge ranges
- `submit_solubility_workflow` - Solubility predictions across multiple solvents and temperatures
- `submit_redox_potential_workflow` - Electrochemical reduction/oxidation potentials
- `submit_descriptors_workflow` - ML-ready molecular descriptors and features
- `submit_tautomer_search_workflow` - Tautomer enumeration with reckless/rapid/careful modes
- `submit_admet_workflow` - ADME/Tox property predictions for drug discovery
- `submit_hydrogen_bond_basicity_workflow` - Hydrogen bond basicity (pKBHX) predictions

### Reactivity Analysis
- `submit_fukui_workflow` - Fukui indices for electrophilic/nucleophilic reactivity sites

### Electronic Structure
- `submit_spin_states_workflow` - Spin state energy calculations for different multiplicities

### Spectroscopy & Analysis
<!-- - `submit_nmr_workflow` - NMR chemical shift predictions (¹H and ¹³C NMR spectra) [Requires subscription upgrade] -->
- `submit_ion_mobility_workflow` - Ion mobility mass spectrometry collision cross-section (CCS) predictions
- `submit_strain_workflow` - Molecular strain energy calculations for rings and cages

### Transition States & Reactions
- `submit_double_ended_ts_search_workflow` - Transition state search from reactant and product structures
- `submit_pose_analysis_md_workflow` - Molecular dynamics simulations on docked protein-ligand complexes

### Protein & Drug Discovery
- `submit_docking_workflow` - Protein-ligand docking with multiple executables (Vina, QVina2, Smina)
- `submit_batch_docking_workflow` - High-throughput docking for virtual screening campaigns
- `submit_protein_cofolding_workflow` - Multi-protein and protein-ligand cofolding predictions
- `submit_msa_workflow` - Multiple sequence alignment for protein structure prediction

### Batch Processing
- `batch_submit_workflow` - Submit multiple molecules through any workflow type for high-throughput processing

---

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

## **Recent Updates**

### Latest Fixes (November 2025)
- ✅ **Fixed `double_ended_ts_search`**: Corrected Settings parameter structure (`basis_set` instead of `basis`)
- ✅ **Fixed `spin_states`**: Now correctly extracts multiplicities from charge/multiplicity pairs
- 🔧 **Streamlined workflows**: Removed workflows better suited for web interface (large data outputs, beta features)

All workflow implementations now match the exact Rowan API specification from the stjames-public repository.

---

## **Experimental: Desktop Extension (Work in Progress)**

We're developing a one-click desktop extension (.dxt) for Claude Desktop that eliminates command-line setup. This feature is currently being refined for optimal compatibility with the MCP extension system.

**Current status:** Installation workflow needs refinement for seamless user experience.

For now, we recommend using the standard Package Installation method above, which is fully tested and reliable.

---

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
### MCP inspector
```bash
# Start the server first
export ROWAN_API_KEY="your_api_key_here" 
uv run python -m rowan_mcp &

# Then inspect
npx @modelcontextprotocol/inspector http://127.0.0.1:6276/sse
```        