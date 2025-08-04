from stjames import Molecule

import rowan

# rowan.api_key = ""

result = rowan.submit_workflow(
    initial_molecule=Molecule.from_smiles("CCCC"),
    workflow_type="basic_calculation",
    name="Constrained Butane",
    workflow_data={
        "engine": "xtb",
        "settings": {
            "method": "gfn2_xtb",
            "tasks": ["optimize"],
            "mode": "auto",
            "opt_settings": {
                "constraints": [
                    {
                        "atoms": [4, 3, 2, 1],
                        "constraint_type": "dihedral",
                        "value": 0,
                    },
                ]
            },
        },
    },
)

result.wait_for_result()
result.fetch_latest(in_place=True)

print(result)