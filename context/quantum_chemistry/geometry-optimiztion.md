Geometry Optimization
For molecule systems, Rowan uses geomeTRIC to run optimizations. For "fast" methods without internal coordinate constraints (e.g. semiempirical methods or neural network potentials), Rowan uses Cartesian coordinates with a maximum of 1250 optimization steps. For slower methods or optimizations with internal constraints, Rowan uses delocalized internal coordinates with a maximum of 250 steps. To accelerate convergence, Rowan computes initial Hessian matrices using the AIMNet2 neural network potential (where applicable) or GFN2-xTB. The energy and gradient convergence parameters are determined by the specific mode selected. Other optimization settings are handled automatically by geomeTRIC (documentation).

For periodic systems, Rowan uses the Sella optimizer. In cases where cell optimization is also required, Rowan uses the QuasiNewton optimizer in the Atomic Simulation Environment in combination with the Frechet Cell Filter, as Sella is not compatible with cell optimization. The gradient convergence cutoff is determined by the specific mode selected, with the caveat that a lower bound of 0.002 Hartree/Å is enforced, as below this threshold converging cell optimizations becomes unreliable with current engines. (A higher threshold of 0.01 Hartree/Å is enforced for OMat24 eqV2 models, which seem to have a much noisier gradient.)

Optimizing molecular geometries is a hard problem mathematically, so it's almost always a good idea to check that optimization actually succeeded by running a subsequent frequency calculation. In general, ground state should be free from imaginary frequencies (i.e. those with negative values); very small imaginary frequencies can sometimes be hard to eliminate, so it may be prudent to rerun the geometry optimization with higher precision. (This is an eternally debated point: see this discussion for some different perspectives.)

Constraints
Rowan supports freezing bonds, angles, dihedral angles, and atom Cartesian coordinates in geometry optimizations. Constraints can be specified by tuning optimization settings in the Python API, or by clicking "Freeze New Coordinate" in the web interface. (Scans can only be run through the web interface.)

Any number of coordinates can be added, although in practice adding more than a handful tends to destabilize the optimization. To specify a coordinate through the API, set the constraint type (bond, angle, or dihedral) and the list of 1-indexed atom numbers (2, 3, or 4 atoms respectively). The full API documentation is available here.

result = client.compute(
    "calculation",
    input_mol=molecule,
    name="dimethyl ether constraint optimization",
    method="aimnet2_wb97md3",
    tasks=["optimize"],
    opt_settings={"constraints": [
        {"constraint_type": "angle", "atoms": [2, 1, 3]},
    ]},
)
Transition-State Optimizations
Rowan also supports transition-state optimizations, which can be run by selecting the optimize_ts task ("Optimize (TS)" in the web interface). Constraints are not supported for transition-state optimizations. For transition-state optimizations, we recommend running a subsequent frequency calculation to validate that a single imaginary frequency is present.

Finding transition states can be very challenging and requires a certain amount of chemical intuition and trial-and-error. In general, running an initial scan along the reaction coordinate is recommended.