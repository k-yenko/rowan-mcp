# 🧪 Test Guide: Unified Management Tools

## 📁 **Folder Management Tests**

### **Test 1: Create Folder**
```
Use rowan_folder_management to create a new folder called "Test Folder" with description "Testing unified folder management"
```
**Expected:** ✅ Success message with folder UUID

### **Test 2: List All Folders**
```
Use rowan_folder_management to list all folders
```
**Expected:** List showing "Test Folder" and any existing folders

### **Test 3: Retrieve Folder Details**
```
Use rowan_folder_management to retrieve details of the folder created in Test 1 (use the UUID from Test 1)
```
**Expected:** Full folder details including name, UUID, creation date

### **Test 4: Update Folder (Star It)**
```
Use rowan_folder_management to update the test folder - set starred to true
```
**Expected:** ✅ Update confirmation showing starred: Yes

### **Test 5: List Starred Folders Only**
```
Use rowan_folder_management to list folders with starred filter set to true
```
**Expected:** Only shows starred folders (should include your test folder)

### **Test 6: Update Folder Name**
```
Use rowan_folder_management to update the folder name to "Updated Test Folder"
```
**Expected:** ✅ Update confirmation with new name

### **Test 7: Delete Folder**
```
Use rowan_folder_management to delete the test folder
```
**Expected:** ✅ Deletion confirmation

### **Test 8: Error Handling - Invalid Action**
```
Use rowan_folder_management with action "invalid_action"
```
**Expected:** ❌ Error listing valid actions

---

## 🔬 **Workflow Management Tests**

### **Test 9: Create Simple Workflow**
```
Use rowan_workflow_management to create a workflow:
- action: "create"
- name: "Test Water Calc"
- workflow_type: "basic_calculation"
- initial_molecule: "O"
```
**Expected:** ✅ Workflow created with UUID

### **Test 10: Check Workflow Status**
```
Use rowan_workflow_management to check status of the workflow from Test 9
```
**Expected:** Status report (likely Queued, Running, or Completed)

### **Test 11: Retrieve Workflow Details**
```
Use rowan_workflow_management to retrieve full details of the test workflow
```
**Expected:** Complete workflow info including type, status, creation time, credits

### **Test 12: List All Workflows**
```
Use rowan_workflow_management to list all workflows
```
**Expected:** List showing test workflow and any existing workflows

### **Test 13: List Workflows by Type**
```
Use rowan_workflow_management to list workflows filtered by object_type "basic_calculation"
```
**Expected:** Only basic_calculation workflows shown

### **Test 14: Update Workflow (Star It)**
```
Use rowan_workflow_management to update the test workflow - set starred to true
```
**Expected:** ✅ Update confirmation showing starred: Yes

### **Test 15: Check If Workflow Is Finished**
```
Use rowan_workflow_management with action "is_finished" for the test workflow
```
**Expected:** Yes/No answer about completion status

### **Test 16: List Failed Workflows**
```
Use rowan_workflow_management to list workflows with object_status 3 (failed)
```
**Expected:** List of failed workflows (may be empty if none failed)

### **Test 17: Create Workflow with Invalid Type**
```
Use rowan_workflow_management to create workflow with workflow_type "invalid_type"
```
**Expected:** ❌ Error with list of valid workflow types

### **Test 18: Error Handling - Missing Required Parameters**
```
Use rowan_workflow_management with action "create" but missing name parameter
```
**Expected:** ❌ Error about required parameters

### **Test 19: Error Handling - Invalid Action**
```
Use rowan_workflow_management with action "invalid_action"
```
**Expected:** ❌ Error listing valid actions

---

## 🎯 **Integration Tests**

### **Test 20: Create Folder and Workflow Together**
```
1. Create a folder called "Integration Test"
2. Create a workflow in that folder using the folder's UUID as parent_uuid
3. List workflows filtered by the parent folder UUID
```
**Expected:** Workflow appears in the specified folder

### **Test 21: Workflow Lifecycle Test**
```
1. Create a simple workflow (methane: "C")
2. Check its status immediately
3. Wait 30 seconds, check status again
4. Retrieve full details
5. Update to add notes "Test completed"
6. Delete the workflow
```
**Expected:** Status progression and successful operations

---

## 🚀 **Quick Test Commands**

### **Folder Management Quick Tests:**
```bash
# Test create
rowan_folder_management(action="create", name="Quick Test")

# Test list
rowan_folder_management(action="list")

# Test invalid action
rowan_folder_management(action="wrong")
```

### **Workflow Management Quick Tests:**
```bash
# Test create simple workflow
rowan_workflow_management(action="create", name="Quick Test", workflow_type="basic_calculation", initial_molecule="C")

# Test list all
rowan_workflow_management(action="list")

# Test invalid workflow type
rowan_workflow_management(action="create", name="Bad Test", workflow_type="invalid", initial_molecule="C")
```

---

## ✅ **Success Criteria**

**Folder Management:**
- ✅ All CRUD operations work (Create, Read, Update, Delete)
- ✅ List with filters works
- ✅ Error handling for invalid actions/parameters
- ✅ Proper validation messages

**Workflow Management:**
- ✅ All 8 actions work (create, retrieve, update, stop, status, is_finished, delete, list)
- ✅ Workflow type validation works
- ✅ Status checking and filtering works
- ✅ Error handling for missing parameters
- ✅ Integration with folder organization

**Overall:**
- ✅ Reduced tool count (26 vs 37 tools)
- ✅ Consistent interface across both tools
- ✅ All original functionality preserved
- ✅ Better organization and usability

---

## 🐛 **Common Issues to Watch For**

1. **UUID Format**: Make sure UUIDs are properly formatted strings
2. **Action Case**: Actions should be case-insensitive ("CREATE" = "create")
3. **Required Parameters**: Clear error messages when required params missing
4. **Status Codes**: Proper handling of all status codes (0-5)
5. **Pagination**: List operations should handle pagination correctly
6. **Filter Combinations**: Multiple filters should work together

---

## 📊 **Test Results Template**

| Test | Status | Notes |
|------|--------|-------|
| Folder Create | ✅/❌ | |
| Folder List | ✅/❌ | |
| Folder Retrieve | ✅/❌ | |
| Folder Update | ✅/❌ | |
| Folder Delete | ✅/❌ | |
| Workflow Create | ✅/❌ | |
| Workflow Status | ✅/❌ | |
| Workflow List | ✅/❌ | |
| Error Handling | ✅/❌ | |
| Integration | ✅/❌ | |

**Overall Grade: ___/10** 