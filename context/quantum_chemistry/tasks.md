Tasks
In Rowan, each calculation is given a list of tasks to accomplish. These tasks dictate which properties or parameters Rowan will calculate behind the scenes.

import rowan
import stjames

rowan.api_key = "rowan-SK"

# load molecule from smiles
molecule = stjames.Molecule.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O")  # ibuprofen

# run calculation remotely and return result
result = rowan.compute(
    "calculation",
    input_mol=molecule,
    name="ibuprofen",
    method="B3LYP",
    basis_set="6-31G(d)",
    tasks=["optimize", "charge", "spin_density", "dipole", "frequency"]
)
For instructions on how to select tasks when submitting calculations using the web interface, see the web interface documentation.

Energy
The keyword energy requests a single-point energy calculation. This is run implicitly when any other task is run, so it only needs to be explicitly stated when it's the only task requested.

Gradient
The keyword gradient requests that the first derivatives of energy with respect to nuclear position be calculated. This is equivalent to the inverse of the nuclear forces, and so can be used in ab initio molecular dynamics (if desired).

Charge
The keyword charge requests atom-centered charges. Currently, these are calculated only using the Mulliken scheme, which is known to be basis-set dependent. (See this discussion of the advantages and disadvantages of different schemes.)

Support for Hirshfeld charges is planned in the future.

Spin Density
The keyword spin_density requests atom-centered spin densities, which are also calculated using the Mulliken scheme. This task can be selected for closed-shell calculations, but will not give very interesting results.

Dipole
The keyword dipole requests a dipole moment calculation.

Hessian/Frequencies
The keywords hessian and frequencies both request a Hessian calculation (the second derivatives of energy with respect to nuclear position). The corresponding vibrational frequencies are automatically computed, and thermochemical analysis is conducted to yield values for zero-point energy, enthalpy, and Gibbs free energy. The frequencies, and thus the thermochemistry also, are physically meaningless at non-stationary points.

When computing vibrational frequencies, translational and rotational modes are automatically projected out, to prevent unphysical low-energy vibrational modes. This white paper explains how this process can be carried out. If the rotational modes found have a frequency of more than 75 wavenumbers, Rowan will print a warning to the logfile. High rotational frequencies can indicate that geometries are insufficiently optimized, or that there's excessive numerical noise (i.e. from integration grids in DFT).

Infrared and Raman intensities are not calculated for vibrational modes.

Optimize
The keyword optimize requests a geometry optimization. When this keyword is present, Rowan will always conduct the geometry optimization first and carry out all other tasks on the final structure. (Thus, for instance, tasks=[optimize, frequencies] behaves the same as opt freq would in Gaussian.) Similarly, optimize_ts requests a transition-state optimization.

For more details on geometry optimization, see the full documentation page.

Performance
Some tasks run very quickly, while others take a long time to run. Here are some helpful guidelines:

Relative to the base self-consistent field calculation, charge and spin_density will run almost instantly, so you never need to worry about including them in the list.
dipole takes a little bit longer, but is still generally much faster than the underlying SCF calculation.
gradient is comparable in speed to the SCF calculation or a bit slower (but shouldn't be orders-of-magnitude slower). Since optimize requires a gradient calculation at each step, the speed of optimization depends on the speed of the gradients and how many steps it takes to find a minimum.
hessian/frequencies are slow, particularly for non-ML methods. Many methods in Rowan currently compute the Hessian through finite differences of the gradient, so a Hessian calculation on a molecule with 
N
N atoms will require 
6
N
6N gradient calculations.
optimize/optimize_ts are also pretty slow, but depend a lot on the molecule: flexible molecules or complexes of multiple molecules will take a lot longer to optimize than rigid aromatic systems. TS optimizations commence with a numerical Hessian calculation, which is often annoyingly slow: hopefully this can be improved in the future.