import json

import rowan

# rowan.api_key = ""

with open("data.json", "r") as f:
    workflow_data = json.load(f)

result = rowan.submit_workflow(
    workflow_type="basic_calculation",
    workflow_data=workflow_data,
    name="basic calculation from json",
    initial_molecule=workflow_data["initial_molecule"],
)

result.wait_for_result()
result.fetch_latest(in_place=True)

print(result)