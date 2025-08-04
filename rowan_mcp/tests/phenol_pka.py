import stjames

import rowan

phenols_to_compute = {
    "p-nitrophenol": "Oc1ccc(N(=O)=O)cc1",
    "p-(trifluoromethyl)phenol": "Oc1ccc(C(F)(F)F)cc1",
    "methyl p-hydroxybenzoate": "COC(=O)c1ccc(O)cc1",
    "p-fluorophenol": "Oc1ccc(F)cc1",
    "p-chlorophenol": "Oc1ccc(Cl)cc1",
    "phenol": "Oc1ccccc1",
    "p-cresol": "Oc1ccc(C)cc1",
    "p-methoxyphenol": "COc1ccc(O)cc1",
    "p-(dimethylamino)phenol": "CN(C)c1ccc(O)cc1",
}

pka_folder = rowan.create_folder(name="phenol pKa results")

workflows = []
for name, smiles in phenols_to_compute.items():
    stjames_molecule = stjames.Molecule.from_smiles(smiles)
    workflows.append(
        rowan.submit_pka_workflow(
            stjames_molecule,
            name=f"pKa {name}",
            folder_uuid=pka_folder.uuid,
            deprotonate_elements=[8],
        )
    )


for workflow in workflows:
    workflow.wait_for_result()
    workflow.fetch_latest(in_place=True)

print([(workflow.name, workflow.data["conjugate_bases"][0]["pka"]) for workflow in workflows])