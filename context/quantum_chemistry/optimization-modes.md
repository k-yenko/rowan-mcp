Modes
There are a large number of settings in computational chemistry programs, and while expert users may wish to individually tune dozens of parameters, this is not usually necessary. Instead, all that typically matters is the ability to move along the speed–accuracy Pareto frontier: initial investigations can be done quickly, while precise values can be obtained through more painstaking means. At a high level, this can be done through adjusting the level of theory: hf-3c is fast, while b97-d3/pcseg-1 is slower and more accurate. But there are also many less obvious ways in which calculations can be tuned to provide more or less accuracy.

In Rowan, some of these other parameters can be conveniently tuned through "modes." There are five modes in Rowan: reckless, rapid, careful, meticulous, and debug. As the names imply, some modes choose very aggressive values for each parameter, while other modes are very conservative. If no mode is selected, Rowan will default to careful for anything involving a gradient or Hessian calculation and rapid for everything else.

import rowan
import stjames

rowan.api_key = "rowan-SK"

# load molecule from smiles
molecule = stjames.Molecule.from_smiles("CC1=C2[C@H](C(=O)[C@@]3([C@H](C[C@@H]4[C@]([C@H]3[C@@H]([C@@](C2(C)C)(C[C@@H]1OC(=O)[C@@H]([C@H](C5=CC=CC=C5)NC(=O)C6=CC=CC=C6)O)O)OC(=O)C7=CC=CC=C7)(CO4)OC(=O)C)O)C)OC(=O)C")

# run calculation remotely and return result
result = rowan.compute(
    "calculation",
    input_mol=molecule,
    name="fast taxol dipole estimate",
    method="hf-3c",
    mode="reckless",
    tasks=["dipole"],
)
How Modes Work
For isolated calculations, the mode selected mainly determines if a geometry optimization has converged. Here are the parameters changed by each mode:

Mode	∆ Energy (Hartree)	Max Gradient (Hartree/Å)	RMS Gradient (Hartree/Å)
Reckless	0.00002	0.007	0.006
Rapid	0.00005	0.005	0.0035
Careful	0.000001	0.0009	0.0006
Meticulous	0.000001	0.00003	0.00002
Debug	0.000001	0.000004	0.000002
(Past iterations of Rowan, which used our own in-house quantum chemistry code, also used the mode to determine a whole host of internal thresholds and cutoffs. We no longer do this, although we reserve the right to tweak a setting here or there in the future.)

For workflows, modes determine a variety of workflow-specific parameters.