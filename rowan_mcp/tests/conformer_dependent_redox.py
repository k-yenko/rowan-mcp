import stjames
from stjames import Molecule

import rowan

# rowan.api_key = ""

conformer_dependent_redox_folder = rowan.create_folder(name="Conformer dependent redox results")

result = rowan.submit_conformer_search_workflow(
    initial_molecule=Molecule.from_smiles("CC(C)Cc1ccc(C(=O)c2ccc(O)cc2)cc1"),
    folder_uuid=conformer_dependent_redox_folder.uuid,
)
result.wait_for_result()
result.fetch_latest(in_place=True)

redox_potential_workflows = []

for conformer in result.data["conformer_uuids"][:10]:
    uuid = conformer[0]
    molecule = rowan.retrieve_calculation_molecules(uuid)[0]
    stjames_molecule = stjames.Molecule.model_validate(molecule)
    redox_potential_workflows.append(
        rowan.submit_redox_potential_workflow(
            stjames_molecule,
            reduction=True,
            oxidization=True,
            folder_uuid=conformer_dependent_redox_folder.uuid,
        )
    )

for workflow in redox_potential_workflows:
    workflow.wait_for_result()
    workflow.fetch_latest(in_place=True)


print([workflow.data["redox_potential"] for workflow in redox_potential_workflows])