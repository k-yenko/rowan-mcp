import time

import stjames

import rowan

HARTREE_TO_KCALMOL = 627.5096

ligands = [
    "CCC(C)(C)NC1=NCC2(CCC(=O)C2C)N1",
    "CCC(C)CN=C1NCC2(CCCOC2)CN1",
    "CC(C)CCNC1=NCC2CC(COC2=N)O1",
    "CCC(CC)NC1=NCC2CC(CO)CC12",
    "CCC(C)CN=C1NC=C2CCC(O)CC2=N1",
    "CC(C#CC#N)C1=NC=C2C=CC(=O)CN12",
    "CCC(CCN)C1NCC2=C(CC)SC(O)=C12",
    "CCC(CC)N=C1NC=C2C=C(F)C=C(N)N12",
    "CC(C)(C)C(N)C1=NCC2=CC(I)=NC=C2O1",
    "CCC(CC)NC1=NCC2CC(N1)C(C)CN2",
    "CCCC(C)N=C1NCC2CCNC2(C)CO1",
    "CC(C)CC(N)C1NCC2=CC(N)=C(Br)N=C12",
    "CC(C)C(CN)C1=NC=C2C=CN(C)C2=C1Br",
    "CC(CC#C)NC1=NCC2=C(C)N(C)C=C2O1",
    "CCCC(C)(N)C1=NCC2=CC(N)=CC=C2O1",
    "CCCCC(N)C1=NC=C2C=CN(C)C(C)=C12",
    "CCC(CC)N=C1NCC2CC(N)CCCN12",
    "CC(C)C(C)(N)C1=NC=C2C=CNC(=N)C2=N1",
    "CC(C)(CC#N)C1=NCC2CCN=COC2O1",
    "C#CCC(C#N)C1=NC=C2C=CNN=C12",
    "CCCCCNC1=NCC2=C(C)NN=C2N1",
    "CCCCC(N)C1=NC=C2C(C)=NOC2=C1Br",
    "CCCCCNC1=NCC2(CC#N)OCC1O2",
    "CC(C)CCNC1=NC=C2CC(=N)OCCN12",
    "CCCC(C#N)C1N(C)C2=C(C=NS2)C1=O",
    "CCC(CC#N)C1=NCC2=C(CO1)OC(=N)S2",
    "CCC(CCN)C1=NCC2=C(CO1)SC=N2",
    "CCC(C(C)N)C1NCC2CCOC1C2(C)C",
    "CC(C)(C)CNC1=NCC2CCOC1(O2)C#C",
    "CCCCCN=C1N(C)C2CCOC2C1(C)C",
    "CC(C)CCN=C1NCC2(CCOC2O1)C#C",
    "CC(C)C(C#N)C1NCC2=CC(O)=C(Br)N=C12",
    "CCC(C(C)N)C1(N)CC2CC(OC)C1C2C",
    "CC(C)(C)CN=C1NC=C2CC(O)CC2O1",
    "CCC(C)(C#N)C1=NC=C2CC(=O)C(C=O)N12",
    "CCCC(C)NC1=NCC2(CCOC=N2)CC1",
    "CCCC(C)N=C1N=CC2=CC(=O)N=C2C1=N",
    "CC(C)C(C#N)C1=NC=C2C=C(O)OC2=C1N",
    "CCCC(CN=C1NCC2=C(C)SC=C12)C=O",
    "CC(C)(C)CN=C1NCC2=CNC3=C2C1=CN3",
    "CCCCC(N)C1=NC=C2CNCC2=C1I",
    "CC(CC#C)NC1=NCC2=C(NC(=C2)C#C)N1",
    "CCC#CCN=C1NCC2=CNC=C2N1",
    "CCCC(C#N)C1N(C)C2=C(NC=C2)OC1=O",
    "CC(C)(C)CN=C1NC=C2C=NC=C2SC1=N",
    "CC(C)C(C#N)C1NCC2=CN=C(C=C12)C#N",
    "CC(C)C(C#N)C1(N)CC2CN(C)CC2C1C",
    "CCC(C)(C)N=C1NCC2=C(NC(C)=C2)C1O",
    "CC(C)C(C)NC1=NCC2CNC(C)C(C2)C1",
    "CCC(C)CN=C1NCC2C(N)C(C)C(C)C12",
    "CCC(C)(C#N)C1=NC=C2CNC(C)C(C)N12",
    "CC(C)C(C#N)C1NCC2=C(N=C(C)N2)C1C",
    "CCC(C)(C)NC1=NCC2=C(N=C(C)N2)C1C",
    "CCC(C)(C)N=C1N=CC2=CN(C)N=C2N1C",
    "CC(C)CCN=C1NC=C2C=NC(=NN12)C#C",
    "CC(C)C(CN=C1NCC2(CN=CO2)O1)C#N",
    "CCC(CC)N=C1N(C)C2=C(NC(=O)S2)C1=O",
    "CCCC(C#N)C1NCC2=C(N=CS2)S1(=O)=O",
    "CCC(C)(C)NC1=NCC2=CNN=C2C(=N)N1",
    "CC(C)CCN=C1NC=C2C(N)=NC(C)=C2S1",
    "CCC(C)(C)NC1=NC=C2C(=N)N=CNC2=N1",
    "CCC(CC)N=C1N(C)C2=C(NN=N2)C1=NO",
    "CCC(C)(C)NC1=NCC2=CN=NN2CCC1",
    "CCC(C)CN=C1N=CC2=CNN=NC2=N1",
    "CCC(CCN)C1=NC=C2C(N)=NSC2=N1",
    "CCC(C)(CN)C1NCC2=C(N)OC=C2C1C",
    "CC(C)(CCN)C1=NC=C2C(=N)SN=C2C=N1",
    "CC(C)(C)CNC1=NC=C2C(=N)SN=C2O1",
    "CCC(C)C(N)C1=NCC2=C(O1)C=CC(=N)S2",
    "CCCCCN=C1NCC2=C(O1)N=C(S2)C#N",
    "CCC(C)(CNC1=NCC2=C(O1)SC=N2)C=O",
    "CC#CC(CN)C1=NCC2=C(O1)SN=C2C",
    "CCCC(C#N)C1NCC2COC1(C2)C(C)=O",
    "CC(C)(C)C(N)C1(N)CC2COC1C(C)(C)C2",
    "CCCC(C#N)C1NCC2COC1(C)CN2C",
    "CCC(C)(C)N=C1N(C)C2COC1(C)OC2C",
    "CC(C)CCN=C1NCC2=C(OC1=N)N=NN2",
    "CCC(CC#N)(C1NCC2=COC=C12)N(C)C",
    "CCCC(C)(N)C1NCC2=C(OC=C12)N(C)C",
    "CC(C)(C)CNC1=NCC2=C(OCC1)N=CS2",
    "CC#CCCN=C1NCC2=COC=C2C=C1",
    "CCCCCNC1=NC=C2C(OCC2(C)O)=C1",
    "CCC(C)(C#N)C1N(C)C2=COC=C2N=C1N",
    "CCC(C)(C)N=C1NCC2(C)OC(CC12)=NC",
    "CCC(C)(CN)C1NCC2C(O)CCC1C2C",
    "CCCC(C)NC1=NCC2COCC(C1)C2C",
    "CC(C)C(C)NC1=NCC2COCCC2(C)O1",
    "CC(C)CC(N)C1=NC=C2COC(C)C(C)N12",
    "CCC(C)(C)NC1=NCC2COC(C)(O1)C2N",
    "CCCC(C)(N)C1=NC=C2COCCOC2=N1",
    "CCCC(C)N=C1N(C)C2=COC(N)=C2C1=O",
    "CCCCCNC1=NCC2(C)OC=NCCC12",
    "CCC(C(C)N)C1=NC=C2COC(N)=NC2=C1",
    "CCCC(C)NC1=NCC2(C)OC(=O)OC2O1",
    "CCCCC(N)C1NCC2=CON=C2C1C#C",
    "CC(C)C(C)N=C1NCC2=C(O)N(C)C=C2O1",
    "CCCC(C)N=C1N=CC2=C(O)N(C)C=CN12",
    "CC(C)C(C#N)C1=NC=C2C(O)=NSC2=C1O",
    "CCC(CC)N=C1NCC2=C(O)SC(=N)N=C12",
    "CC(C)C(CN)C1NCC2=C(SC=C2C)C1C",
]


workflows = []
results = {}

docking_result_folder = rowan.create_folder(name="Docking results")


protein = rowan.create_protein_from_pdb_id("CDK2", "1HCK")

protein.sanitize()
time.sleep(60)
protein.refresh()

for ligand in ligands:
    workflow = rowan.submit_docking_workflow(
        protein.uuid,
        pocket=[[103.55, 100.59, 82.99], [27.76, 32.67, 48.79]],
        initial_molecule=stjames.Molecule.from_smiles(ligand),
        folder_uuid=docking_result_folder.uuid,
        name=f"Docking {ligand}",
    )
    workflows.append(workflow)


for workflow in workflows:
    workflow.wait_for_result()
    workflow.fetch_latest(in_place=True)

lowest_conformer_energy = 0
for workflow in workflows:
    conformers = workflow.data["conformers"]
    for conformer in conformers:
        energy = rowan.retrieve_calculation_molecules(
            conformer[0] if isinstance(conformer, list) else conformer
        )[0]["energy"]
        lowest_conformer_energy = min(lowest_conformer_energy, energy)

    sorted_scores = sorted(workflow.data["scores"], key=lambda x: float(x["score"]))
    for score in sorted_scores:
        pose_energy = rowan.retrieve_calculation_molecules(score["pose"])[0]["energy"]
        strain = (pose_energy - lowest_conformer_energy) * HARTREE_TO_KCALMOL
        if score["posebusters_valid"] and strain < 4:
            results[workflow.name] = score
            break

print(results)