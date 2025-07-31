# Workflow Management V2 Test Queries

## workflow_fetch_latest

1. Using workflow_fetch_latest, get the current status and data for workflow with UUID "abc-123-def-456"
2. Using workflow_fetch_latest, update and retrieve the latest information for a completed workflow "xyz-789-uvw-012"
3. Using workflow_fetch_latest, check if workflow "workflow-001" has any new results or status changes

## workflow_wait_for_result

1. Using workflow_wait_for_result, wait for workflow "pending-calc-123" to complete with default 5 second polling
2. Using workflow_wait_for_result, wait for workflow "running-job-456" with poll_interval of 10 seconds and timeout of 300 seconds
3. Using workflow_wait_for_result, block until workflow "long-running-789" finishes with poll_interval of 2 seconds

## workflow_get_status

1. Using workflow_get_status, check the current status of workflow "quick-check-111"
2. Using workflow_get_status, verify if workflow "completed-job-222" is still running
3. Using workflow_get_status, get the status of a recently submitted workflow "new-calc-333"

## workflow_stop

1. Using workflow_stop, cancel the running workflow "cancel-me-123"
2. Using workflow_stop, stop a long-running calculation with UUID "expensive-calc-456"
3. Using workflow_stop, terminate workflow "stuck-job-789" that appears to be hanging

## workflow_delete

1. Using workflow_delete, remove the completed workflow "old-result-111" from the database
2. Using workflow_delete, delete the failed workflow "error-job-222" and its data
3. Using workflow_delete, permanently remove workflow "test-calc-333" that is no longer needed

## workflow_list_by_folder

1. Using workflow_list_by_folder, list all workflows with default limit of 100
2. Using workflow_list_by_folder, get workflows from folder_uuid "folder-abc-123" with limit 50 and offset 0
3. Using workflow_list_by_folder, retrieve the next page of workflows from folder "folder-xyz-789" with limit 20 and offset 20

## workflow_get_result

1. Using workflow_get_result, retrieve just the calculation results from workflow "completed-calc-111"
2. Using workflow_get_result, get the final output data from workflow "analysis-job-222"
3. Using workflow_get_result, extract the result field from workflow "finished-sim-333"

## workflow_get_logs

1. Using workflow_get_logs, retrieve stdout and stderr from workflow "debug-job-111"
2. Using workflow_get_logs, get the execution logs for failed workflow "error-calc-222"
3. Using workflow_get_logs, check the output logs from workflow "verbose-run-333"

## workflow_batch_status

1. Using workflow_batch_status, check status of multiple workflows ["job-1", "job-2", "job-3"]
2. Using workflow_batch_status, get the current state of workflows ["calc-aaa", "calc-bbb", "calc-ccc", "calc-ddd", "calc-eee"]
3. Using workflow_batch_status, verify completion status for a batch of 10 workflows ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10"]

## retrieve_workflow

1. Using retrieve_workflow, get the complete workflow object for UUID "workflow-abc-123"
2. Using retrieve_workflow, retrieve detailed information about workflow "completed-calc-456" including its type and visibility settings
3. Using retrieve_workflow, fetch workflow "starred-job-789" to check if it's starred and public

## retrieve_calculation_molecules

1. Using retrieve_calculation_molecules, get all molecules from calculation "calc-result-111"
2. Using retrieve_calculation_molecules, retrieve molecular structures and properties from workflow "conformer-search-222"
3. Using retrieve_calculation_molecules, extract the list of optimized molecules from calculation "opt-job-333"

## list_workflows

1. Using list_workflows, get the first page of all workflows with default page size of 10
2. Using list_workflows, search for workflows with name_contains="solubility" in folder "folder-123" with page=0 and size=20
3. Using list_workflows, filter workflows by status=2 (completed), starred=true, workflow_type="pka" with page=1 and size=50

## Example Workflow Patterns

### Pattern 1: Submit and Wait
1. Submit a basic calculation using submit_basic_calculation_workflow with initial_molecule="CCO"
2. Get the returned workflow UUID
3. Use workflow_wait_for_result with that UUID to wait for completion
4. Use workflow_get_result to extract just the calculation results

### Pattern 2: Submit and Poll
1. Submit a conformer search using submit_conformer_search_workflow with initial_molecule="CC(C)C"
2. Get the returned workflow UUID
3. Use workflow_get_status periodically to check progress
4. Once status is "completed", use workflow_fetch_latest to get full results

### Pattern 3: Batch Processing
1. Submit multiple calculations using different submit_* functions
2. Collect all workflow UUIDs
3. Use workflow_batch_status to monitor all jobs at once
4. Use workflow_get_result for each completed workflow