# MCP Inspector Launch Commands for Rowan Server

## Method 1: Direct Python Module (Recommended)
```bash
npx @modelcontextprotocol/inspector python -m src.server
```

## Method 2: Using Python Script Path
```bash
npx @modelcontextprotocol/inspector python src/server.py
```

## Method 3: With Environment Variables
```bash
ROWAN_API_KEY=your_key_here npx @modelcontextprotocol/inspector python -m src.server
```

## Method 4: With UV (if using UV for Python management)
```bash
npx @modelcontextprotocol/inspector uv run python -m src.server
```

## Method 5: Debug Mode with Verbose Logging
```bash
npx @modelcontextprotocol/inspector python -m src.server --log-level DEBUG
```

## What to Test in Inspector

### 1. System Management Tool
- Action: "help" - Should list all 23 tools
- Action: "set_log_level" with log_level: "DEBUG"
- Action: "job_redirect" with job_uuid: "test-uuid"

### 2. Folder Management Tool  
- Action: "create" with name: "Test Folder"
- Action: "list" - Should show your folders
- Action: "retrieve" with folder_uuid from created folder

### 3. Workflow Management Tool
- Action: "create" with name: "Test Workflow", workflow_type: "basic_calculation", initial_molecule: "O"
- Action: "list" - Should show your workflows
- Action: "status" with workflow_uuid from created workflow

### 4. Quantum Chemistry Tool
- Test with defaults: name: "Water Test", molecule: "O"
- Test with custom: method: "b3lyp", basis_set: "6-31g*"

## Expected Inspector Features

✅ **Tools Tab**: Should show ~23 tools total
✅ **Server Connection**: Should show "Connected" status  
✅ **Tool Schemas**: Each tool should show proper parameter documentation
✅ **Real-time Testing**: Click tools to test with custom inputs
✅ **Notifications**: Server logs and responses in real-time
✅ **Error Handling**: Invalid inputs should show helpful error messages

## Troubleshooting

If Inspector doesn't connect:
1. Check that ROWAN_API_KEY is set in environment
2. Verify server starts without Inspector first: `python -m src.server`
3. Try alternative launch methods above
4. Check firewall/network settings
5. Look for error messages in terminal

## Inspector URL
Once running, Inspector typically opens at: http://localhost:3000 