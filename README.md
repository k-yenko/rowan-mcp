# Rowan MCP Server

**Connect AI assistants to chemistry calculations**

This tool lets AI assistants (like Claude) run real chemistry calculations through Rowan's platform. Ask your AI to calculate molecular properties, optimize structures, or predict how molecules behave - and get scientific results back.

## What This Does

🧪 **Chemistry Calculations**: Your AI can run quantum chemistry calculations, optimize molecular structures, and predict chemical properties

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
      "url": "http://127.0.0.1:6276/mcp"
    }
  }
}
```

**Option B: STDIO Connection (Traditional)**

Add this to your Claude config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
          "rowan": {
        "command": "uv",
        "args": ["run", "python", "-m", "src"],
        "cwd": "/path/to/your/rowan-mcp"
      }
  }
}
```

### 5. Test the Connection
```bash
# Test HTTP endpoint (if using Option A)
uv run python client_example.py
```

## What Your AI Can Do

Once connected, you can ask your AI assistant natural questions like:

### 🧬 **Molecular Properties**
- "What's the pKa of aspirin?"
- "Calculate the acidity of caffeine"
- "How toxic is this drug molecule?"

### ⚗️ **Structure Optimization**  
- "Optimize the geometry of methane using quantum mechanics"
- "Find the lowest energy shape of cyclohexane"
- "Calculate the dipole moment of water"

### 🔄 **Conformational Analysis**
- "Generate different shapes for this flexible molecule"
- "Find all the conformers of butane"
- "Which conformation is most stable?"

### 📁 **Project Organization**
- "Create a folder for my drug discovery project"
- "Check the status of my calculations"
- "Show me the results from yesterday's jobs"

## Available Tools

Your AI gets access to these chemistry tools:

| Tool | What It Does |
|------|-------------|
| **Core Computing** | |
| `rowan_compute` | Run any chemistry calculation with full API support |
| `rowan_pka` | Calculate acid/base strength (pKa/pKb) |
| `rowan_conformers` | Find different molecular shapes |
| **Project Management** | |
| `rowan_folder_create` | Create organization folders |
| `rowan_folder_list` | List folders with filters |
| `rowan_folder_retrieve` | Get folder details |
| `rowan_folder_update` | Update folder properties |
| `rowan_folder_delete` | Delete folders |
| **Workflow Management** | |
| `rowan_workflow_create` | Create custom workflows |
| `rowan_workflow_list` | List workflows with filters |
| `rowan_workflow_retrieve` | Get workflow details |
| `rowan_workflow_update` | Update workflow properties |
| `rowan_workflow_status` | Check workflow status |
| `rowan_workflow_stop` | Stop running workflows |
| `rowan_workflow_delete` | Delete workflows |
| **Job Monitoring** | |
| `rowan_job_status` | Check calculation progress |
| `rowan_job_results` | Get your results |
| `rowan_calculation_retrieve` | Get detailed calculation info |

## Real Examples

### Calculate pKa (Acidity)
```
You: "What's the pKa of phenol?"

AI: I'll calculate the pKa of phenol using Rowan...

✅ pKa calculation for 'phenol pKa' completed!
🧪 Molecule: c1ccccc1O
🧬 Strongest Acid pKa: 10.17
```

### Optimize a Molecule
```
You: "Optimize caffeine with DFT"

AI: I'll run a DFT optimization of caffeine...

✅ Calculation 'caffeine optimization' completed successfully!
🔬 Job UUID: abc123...
⚡ Energy: -680.123456 Hartree
🧲 Dipole Moment: 3.64 Debye
```

## How It Works

```
[Your AI] ←→ [This MCP Server] ←→ [Rowan Platform] ←→ [Chemistry Software]
```

1. **You ask** your AI a chemistry question
2. **AI calls** this MCP server with the right parameters  
3. **Server sends** the calculation to Rowan's cloud platform
4. **Rowan runs** the calculation using professional chemistry software
5. **Results flow back** to your AI, formatted nicely

## Project Structure

```
rowan-mcp/
├── src/                 # All the code
│   ├── server.py       # Main MCP server (FastMCP-based)
│   ├── types.py        # Data structures
│   └── __main__.py     # Entry point
├── .env                # Your API key (create this)
├── .venv/              # Python dependencies
└── tests/              # Tests
```

## Chemistry Methods Available

### **Quantum Methods**
- **DFT**: B3LYP, M06-2X, ωB97X-D (high accuracy)
- **Semiempirical**: GFN2-xTB, GFN1-xTB (fast calculations)

### **Software Engines**  
- **Gaussian**: Industry standard quantum chemistry
- **ORCA**: Fast and reliable calculations
- **xTB**: Ultra-fast semiempirical methods
- **Auto**: Let Rowan pick the best method

### **Property Predictions**
- **pKa/pKb**: Acid and base strength
- **ADME-Tox**: Drug-like properties (`admet`)
- **Redox Potentials**: Electrochemical properties
- **Solubility**: Solubility predictions
- **Bond-Dissociation Energy**: BDE calculations (`bde`)
- **Electronic Properties**: Electronic structure analysis
- **Fukui Indices**: Reactivity predictions
- **Hydrogen-Bond Basicity**: H-bonding properties
- **Conformers**: 3D molecular shapes
- **Tautomers**: Tautomer enumeration and ranking

### **Advanced Simulations**
- **Molecular Dynamics**: MD simulations (`molecular_dynamics`)
- **Molecular Docking**: Protein-ligand docking
- **Coordinate Scans**: Potential energy surfaces (`scan`)
- **IRC**: Intrinsic reaction coordinate calculations
- **Spin States**: Electronic spin state analysis

## Troubleshooting

### "API key required" error
```bash
# Make sure your .env file has your real API key
cat .env
# Should show: ROWAN_API_KEY=rw_your_actual_key_here
```

### Server won't start
```bash
# Check dependencies are installed
uv sync

# Test Python can find the module
uv run python -c "import src.server"
```

### AI can't connect
- Check the file path in your MCP config is correct
- Make sure the server starts without errors
- Restart your AI assistant after changing config

## Getting Help

- **Rowan API Issues**: Contact support@rowansci.com
- **This Tool**: Open an issue on GitHub
- **Documentation**: [docs.rowansci.com](https://docs.rowansci.com)

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Rowan API key (free account at labs.rowansci.com)
- MCP-compatible AI assistant

## 🧪 Tutorial-Based Examples

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
