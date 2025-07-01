# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Server
```bash
# HTTP Server (recommended for modern MCP clients)
uv run python -c "from src.http_server import main; main()"

# STDIO Server (traditional MCP)
uv run python -m src

# Entry point script
rowan-mcp
```

### Development Tools
```bash
# Install dependencies
uv sync

# Code formatting
black src/
isort src/

# Type checking
mypy src/

# Run tests
pytest
```

## Architecture Overview

### Core Components

**MCP Server Implementation**: The project uses FastMCP framework to implement the Model Context Protocol server. Two server modes are supported:

- `src/server.py`: Main MCP server with 15+ chemistry tools using FastMCP and rowan-python SDK
- `src/http_server.py`: HTTP wrapper providing JSON-RPC over HTTP interface on port 6276
- `src/__main__.py`: Entry point that delegates to server.py

**Chemistry Functions**: Located in `src/functions/` directory with modular implementations:
- `solubility.py`: Solubility prediction across multiple solvents/temperatures
- `workflow_management.py`: Workflow creation, monitoring, and lifecycle management  
- `calculation_retrieve.py`: Retrieval and status checking of completed calculations
- `docking.py`: Protein-ligand docking calculations

### API Integration

**Rowan Platform**: All chemistry calculations are performed via Rowan's cloud platform using the rowan-python SDK. Key integration points:

- API key loaded from `ROWAN_API_KEY` environment variable
- All tools return workflow UUIDs for async job tracking
- Built-in retry logic and error handling for API calls
- Comprehensive logging to `rowan_mcp.log`

### Tool Categories

**Basic Calculations**: `rowan_multistage_opt`, `rowan_admet`, `rowan_electronic_properties`

**Molecular Properties**: `rowan_pka`, `rowan_solubility`, `rowan_redox_potential`, `rowan_conformers`, `rowan_descriptors`, `rowan_tautomers`

**Advanced Analysis**: `rowan_scan`, `rowan_fukui`, `rowan_spin_states`, `rowan_irc`, `rowan_molecular_dynamics`

**Drug Discovery**: `rowan_docking` with PDB ID and SMILES support

**Management**: `rowan_folder_management`, `rowan_workflow_management`, `rowan_system_management`, `rowan_calculation_retrieve`

## Configuration

### Environment Setup
- Copy `config.env.example` to `.env`
- Set `ROWAN_API_KEY` from labs.rowansci.com account
- Server runs on 127.0.0.1:6276 for HTTP mode

### Input Formats
- **Molecules**: SMILES strings (e.g., "CCO" for ethanol)
- **Proteins**: PDB IDs (e.g., "1ABC") or full PDB content
- **Solvents**: Names ("water", "ethanol") or SMILES ("O", "CCO")
- **Temperatures**: Celsius/Kelvin, comma-separated or JSON arrays

## Key Development Notes

### Error Handling
- All API calls wrapped in try-catch with detailed error messages
- Solvent name-to-SMILES conversion with fallback handling
- SMILES parsing validation before API submission
- Comprehensive logging for debugging workflow issues

### Async Workflows
- Most calculations return immediately with workflow UUID
- Use `rowan_workflow_management` to check status and retrieve results
- Blocking mode available but not recommended due to timeout constraints

### Testing
- Direct API testing available in `src/test_direct_api.py`
- Tutorial examples demonstrate real usage patterns from official Rowan documentation