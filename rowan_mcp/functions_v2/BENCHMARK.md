# Rowan MCP Benchmark Suite

## Overview
Systematic evaluation of the Rowan MCP server's ability to handle chemistry workflows through natural language queries.

## Evaluation Tiers

### Tier 1: Single Tool Calls
**Tests**: Basic tool invocation and parameter passing  
**Characteristics**:
- Single workflow submission
- Explicit parameters
- No dependencies
- Direct SMILES or common molecule names

**Example Queries**:
- "Calculate the pKa of phenol"
- "Optimize water geometry with GFN2-xTB"
- "Find conformers of ethanol"

### Tier 2: Parameter Interpretation
**Tests**: Natural language to parameter mapping, molecule name resolution  
**Characteristics**:
- Requires interpreting descriptive terms into API parameters
- Mode selection (rapid/careful/meticulous)
- Element specification by name vs atomic number
- Common name to SMILES conversion

**Example Queries**:
- "Calculate the oxidation potential of caffeine using careful mode"
- "Find the pKa of aspirin, only considering oxygen atoms"
- "Dock ibuprofen to CDK2 without optimization"

### Tier 3: Batch Operations
**Tests**: Multiple independent calculations, result organization  
**Characteristics**:
- Multiple molecules or methods
- Parallel workflow submission
- Result comparison/aggregation
- Folder organization

**Example Queries**:
- "Calculate pKa for phenol, p-nitrophenol, and p-chlorophenol"
- "Optimize butane with GFN2-xTB, UMA, and R2SCAN-3c methods"
- "Screen 5 molecules for docking against CDK2"

### Tier 4: Workflow Chaining
**Tests**: Sequential dependent calculations, data extraction from results  
**Characteristics**:
- Output from one workflow feeds into next
- Requires waiting for completion
- UUID and result extraction
- Proper async handling

**Example Queries**:
- "Find conformers of benzophenone, then calculate redox potential for top 3"
- "Optimize this transition state, then run IRC from the result"
- "Calculate pKa, then run conformer search at the predicted pKa value"

### Tier 5: Conditional Logic
**Tests**: Decision-making based on results, complex multi-step analysis  
**Characteristics**:
- Conditional branching based on results
- Threshold-based decisions
- Error handling and retries
- Statistical analysis of results

**Example Queries**:
- "Screen molecules for docking, only run detailed analysis if score < -8.0"
- "Calculate conformer energies, identify outliers (>2 kcal/mol from lowest), recalculate outliers with meticulous mode"
- "Find pKa sites, if any are between 6-8, run pH-dependent calculations at those values"

## Scoring Criteria

### Per Query
- **Success**: Workflow submitted correctly (1 point)
- **Parameters**: All parameters correctly mapped (1 point)
- **Completion**: Workflow completes without error (1 point)
- **Chaining**: Dependencies handled correctly (1 point, Tier 4-5 only)
- **Logic**: Conditional logic executed correctly (1 point, Tier 5 only)

### Overall Metrics
- Success rate per tier
- Average time to completion
- Error recovery rate
- Parameter accuracy rate