# 🔬 Rowan MCP: Unified Management Tools

## 📋 Overview

The Rowan MCP server now features **unified management tools** that consolidate multiple related operations into single, powerful tools. Instead of having 13 separate tools for folder and workflow management, we now have **2 unified tools** that handle all operations through an `action` parameter.

## 🎯 Benefits

- **Reduced Complexity**: 30 tools → 23 tools (7 fewer tools!)
- **Better Organization**: Related operations grouped logically
- **Consistent Interface**: Same pattern across management tools
- **Comprehensive Documentation**: Clear action-based documentation
- **Enhanced Error Handling**: Better validation and error messages

---

## 📁 Folder Management Tool

### **`rowan_folder_management`**

**One tool for all folder operations:**

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `create` | Create new folder | `name` | `description` |
| `retrieve` | Get folder details | `folder_uuid` | - |
| `update` | Update folder properties | `folder_uuid` | `name`, `parent_uuid`, `notes`, `starred`, `public` |
| `delete` | Delete folder | `folder_uuid` | - |
| `list` | List folders with filters | - | `name_contains`, `parent_uuid`, `starred`, `public`, `page`, `size` |

### **Usage Examples:**

```python
# Create a folder
rowan_folder_management(action="create", name="My Research", description="All my calculations")

# List all folders
rowan_folder_management(action="list")

# Get folder details
rowan_folder_management(action="retrieve", folder_uuid="folder-uuid-here")

# Star a folder
rowan_folder_management(action="update", folder_uuid="folder-uuid-here", starred=True)

# List only starred folders
rowan_folder_management(action="list", starred=True)

# Delete a folder
rowan_folder_management(action="delete", folder_uuid="folder-uuid-here")
```

---

## 🔬 Workflow Management Tool

### **`rowan_workflow_management`**

**One tool for all workflow operations:**

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `create` | Create new workflow | `name`, `workflow_type`, `initial_molecule` | `parent_uuid`, `notes`, `starred`, `public`, `email_when_complete`, `workflow_data` |
| `retrieve` | Get workflow details | `workflow_uuid` | - |
| `update` | Update workflow properties | `workflow_uuid` | `name`, `parent_uuid`, `notes`, `starred`, `public`, `email_when_complete` |
| `stop` | Stop running workflow | `workflow_uuid` | - |
| `status` | Check workflow status | `workflow_uuid` | - |
| `is_finished` | Check if workflow finished | `workflow_uuid` | - |
| `delete` | Delete workflow | `workflow_uuid` | - |
| `list` | List workflows with filters | - | `name_contains`, `parent_uuid`, `starred`, `public`, `object_status`, `object_type`, `page`, `size` |

### **Workflow Types:**
`admet`, `basic_calculation`, `bde`, `conformer_search`, `descriptors`, `docking`, `electronic_properties`, `fukui`, `hydrogen_bond_basicity`, `irc`, `molecular_dynamics`, `multistage_opt`, `pka`, `redox_potential`, `scan`, `solubility`, `spin_states`, `tautomers`

### **Status Codes:**
- `0`: Queued ⏳
- `1`: Running 🔄  
- `2`: Completed ✅
- `3`: Failed ❌
- `4`: Stopped ⏹️
- `5`: Awaiting Queue ⏸️

### **Usage Examples:**

```python
# Create a workflow
rowan_workflow_management(
    action="create", 
    name="Aspirin Calculation", 
    workflow_type="basic_calculation", 
    initial_molecule="CC(=O)OC1=CC=CC=C1C(=O)O"
)

# Check workflow status
rowan_workflow_management(action="status", workflow_uuid="workflow-uuid-here")

# List all workflows
rowan_workflow_management(action="list")

# List only failed workflows
rowan_workflow_management(action="list", object_status=3)

# List workflows by type
rowan_workflow_management(action="list", object_type="basic_calculation")

# Update workflow (star it)
rowan_workflow_management(action="update", workflow_uuid="workflow-uuid-here", starred=True)

# Stop a running workflow
rowan_workflow_management(action="stop", workflow_uuid="workflow-uuid-here")

# Delete a workflow
rowan_workflow_management(action="delete", workflow_uuid="workflow-uuid-here")
```

---

## 🖥️ System Management Tool

### **`rowan_system_management`**

**One tool for all system utilities and information:**

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|-------------------|-------------------|
| `help` | Get list of all available tools | - | - |
| `set_log_level` | Set logging level for debugging | `log_level` | - |
| `job_redirect` | Redirect legacy job queries | `job_uuid` | - |

### **Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General information messages  
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### **Usage Examples:**

```python
# Get help and list all available tools
rowan_system_management(action="help")

# Set logging level for debugging
rowan_system_management(action="set_log_level", log_level="DEBUG")

# Handle legacy job queries (redirects to workflow management)
rowan_system_management(action="job_redirect", job_uuid="old-job-uuid")
```

---

## 🧪 Testing Guide

### **Quick Functionality Tests**

1. **Test Folder Creation:**
   ```
   Create a folder called "Test Folder"
   ```

2. **Test Workflow Creation:**
   ```
   Create a basic calculation workflow called "Test Calc" for methane
   ```

3. **Test System Help:**
   ```
   Get help and list all available tools
   ```

4. **Test Error Handling:**
   ```
   Use rowan_folder_management with action "invalid"
   Use rowan_workflow_management with action "invalid"
   Use rowan_system_management with action "invalid"
   ```

### **Comprehensive Test Scenarios**

#### **Folder Management Tests:**
- ✅ Create folder with description
- ✅ List all folders
- ✅ Retrieve folder details
- ✅ Update folder (star it)
- ✅ List starred folders only
- ✅ Update folder name
- ✅ Delete folder
- ✅ Error handling for invalid actions

#### **Workflow Management Tests:**
- ✅ Create simple workflow (water molecule)
- ✅ Check workflow status
- ✅ Retrieve workflow details
- ✅ List all workflows
- ✅ List workflows by type
- ✅ Update workflow (star it)
- ✅ Check if workflow finished
- ✅ List failed workflows
- ✅ Error handling for invalid workflow types
- ✅ Error handling for missing parameters

#### **System Management Tests:**
- ✅ Get help and tool listing
- ✅ Set different log levels
- ✅ Handle legacy job redirects
- ✅ Error handling for invalid actions
- ✅ Error handling for missing parameters

#### **Integration Tests:**
- ✅ Create folder and workflow together
- ✅ Full workflow lifecycle test
- ✅ Folder organization with workflows
- ✅ System utilities with other tools

---

## 🔧 Migration from Old Tools

### **Old vs New Tool Mapping:**

**Folder Tools (5 → 1):**
- `rowan_folder_create` → `rowan_folder_management(action="create")`
- `rowan_folder_retrieve` → `rowan_folder_management(action="retrieve")`
- `rowan_folder_update` → `rowan_folder_management(action="update")`
- `rowan_folder_delete` → `rowan_folder_management(action="delete")`
- `rowan_folder_list` → `rowan_folder_management(action="list")`

**Workflow Tools (8 → 1):**
- `rowan_workflow_create` → `rowan_workflow_management(action="create")`
- `rowan_workflow_retrieve` → `rowan_workflow_management(action="retrieve")`
- `rowan_workflow_update` → `rowan_workflow_management(action="update")`
- `rowan_workflow_stop` → `rowan_workflow_management(action="stop")`
- `rowan_workflow_status` → `rowan_workflow_management(action="status")`
- `rowan_workflow_is_finished` → `rowan_workflow_management(action="is_finished")`
- `rowan_workflow_delete` → `rowan_workflow_management(action="delete")`
- `rowan_workflow_list` → `rowan_workflow_management(action="list")`

**System Tools (4 → 1):**
- `rowan_available_workflows` → `rowan_system_management(action="help")`
- `rowan_set_log_level` → `rowan_system_management(action="set_log_level")`
- `rowan_job_status` → `rowan_system_management(action="job_redirect")`
- `rowan_job_results` → `rowan_system_management(action="job_redirect")`

---

## 🚀 Best Practices

### **Folder Organization:**
1. Create descriptive folder names
2. Use descriptions to document folder purpose
3. Star important folders for quick access
4. Use hierarchical organization with parent folders

### **Workflow Management:**
1. Use descriptive workflow names
2. Check status regularly for long-running calculations
3. Star important workflows
4. Use folder organization to group related workflows
5. Clean up completed/failed workflows periodically

### **System Management:**
1. Use `help` action to discover available tools
2. Set appropriate log levels for debugging
3. Use `job_redirect` for legacy compatibility
4. Monitor system performance and logs

### **Error Handling:**
1. Always check for error messages in responses
2. Validate UUIDs before using them
3. Use proper workflow types from the supported list
4. Provide all required parameters for each action

---

## 📊 Tool Statistics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total Tools | 30 | 23 | -23% |
| Folder Tools | 5 | 1 | -80% |
| Workflow Tools | 8 | 1 | -87% |
| System Tools | 4 | 1 | -75% |
| Management Complexity | High | Low | Simplified |
| Interface Consistency | Mixed | Unified | Standardized |

---

## 🔗 Related Tools

The unified management tools work seamlessly with:
- `rowan_quantum_chemistry` - Unified QC calculations
- `rowan_qc_guide` - Quantum chemistry guidance
- `rowan_multistage_opt` - Geometry optimization
- All other Rowan calculation tools

---

## 📝 Support

For issues or questions:
1. Use `rowan_system_management(action="help")` for tool discovery
2. Check error messages for guidance
3. Verify action names and required parameters
4. Ensure UUIDs are valid and properly formatted
5. Review this documentation for usage examples

---

## 🎯 Summary

The unified management tools provide a **cleaner, more organized, and more powerful** interface for managing folders, workflows, and system utilities in Rowan. With consistent action-based interfaces, comprehensive error handling, and reduced tool complexity, these tools make Rowan more accessible and easier to use while maintaining all original functionality.

**Key Benefits:**
- 🎯 **Simplified Interface**: One tool per management area
- 🔧 **Consistent Pattern**: Same action-based approach across all management tools
- 📚 **Better Documentation**: Clear parameter requirements and examples
- 🛡️ **Enhanced Validation**: Better error messages and guidance
- 🚀 **Improved Performance**: Fewer tools to load and manage
- 🔄 **Legacy Support**: Smooth migration path from old tools 