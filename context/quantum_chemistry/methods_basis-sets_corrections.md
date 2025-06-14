Rowan currently supports Hartree-Fock and density-functional theory calculations. In incorporating density functionals, we have attempted to balance including useful functionals with a desire to avoid overwhelming end users with unnecessary options. If a certain functional that's not included is exceedingly important to your work, please let us know!

Rowan supports all commonly used classes of functional, including meta-GGA functionals and range-separated hybrids, although not every engine supports every functional. At this point, there are no immediate plans to add support for double-hybrid functionals. For advice on which functional to choose for a given task, see Recommendations below.

When submitting calculations using the Python API, methods can be selected by keyword. If no method is specified, a Hartree–Fock calculation will be performed.

import rowan
import stjames

rowan.api_key = "rowan-SK"

# load molecule from smiles
molecule = stjames.Molecule.from_smiles("C1CCCC1")  # cyclopentane

# run calculation remotely and return result
result = rowan.compute(
    "calculation",
    input_mol=molecule,
    name="opt cyclopentane",
    method="m06",
    tasks=["optimize", "frequency"]
)
For instructions on how to select methods when submitting calculations using the web interface, see the web interface documentation.

Hartree–Fock
Rowan supports Hartree–Fock calculations. For open-shell systems, Rowan uses the unrestricted Hartree–Fock formalism.

Keyword
hf
Density-Functional Theory
Rowan supports a variety of density functionals.

For a variety of historical reasons, there are many competing implementations of several popular density functionals, like B3LYP and PBE, which can lead to slight differences when comparing outputs of one program to another. (See this excellent overview by Susi Lehtola and Miguel Marques, the authors of Libxc.)

Pure Functionals
Local Density Approximation
LSDA
The local spin density approximation, using the Slater exchange functional and the VWN correlation functional.

Keyword
lsda
Generalized Gradient Approximation
PBE
The 1996 Perdew–Burke–Ernzerhof functional.

Keyword
pbe
BLYP
Becke's 1988 exchange functional with the Lee–Yang–Parr correlation functional.

Keyword
blyp
BP86
Becke's 1988 exchange functional with Perdew's 1988 correlation functional.

Keyword
bp86
B97-D3
Grimme's 2006 reparameterization of Becke's 1997 power-series ansatz, using the D3 dispersion correction. Note that choosing this method will also automatically load the D3BJ correction (in PySCF) or the D3 correction (in TeraChem).

Keyword
b97-d3
Meta-Generalized Gradient Approximation
R2SCAN
Furness and Sun's 2020 improvement over the numerically unstable SCAN functional. r2SCAN still struggles with numerical instability, as shown by Lehtola and Marques recently.

Keyword
r2scan
TPSS
Scuseria and Perdew's 2003 mGGA functional, with no empirical parameters.

Keyword
tpss
M06-L
Zhao and Truhlar's 2006 local mGGA functional.

Keyword
m06l
Hybrid Functionals
Global Hybrid Functionals
PBE0
Adamo and Barone's hybrid functional derived from PBE (also evaluated by Ernzerhof and Scuseria).

Keyword	% HF exchange
pbe0	25%
B3LYP
The famous 1994 functional of Stephens, Devlin, Chabalowski, and Frisch. (We follow the original Gaussian implementation here in employing the VWN(RPA) correlation functional rather than the VWN5 correlation functional.)

Keyword	% HF exchange
b3lyp	20%
B3PW91
Becke's 1993 hybrid functional with Perdew–Wang correlation.

Keyword	% HF exchange
b3pw91	20%
Range-Separated Hybrid Functionals
CAM-B3LYP
Yanai, Tew, and Handy's 2004 range-separated hybrid based on B3LYP.

Keyword	% HF exchange
camb3lyp	19–65%
ωB97X-D3
Chai's reparameterization of ωB97X-D with the D3 dispersion correction. Note that this is not currently supported in PySCF; we're working on it.

Keyword	% HF exchange
wb97x_d3	20-100%
ωB97X-V
Mardirossian and Head-Gordon's 2014 10-parameter combinatorially optimized GGA functional, with the VV10 nonlocal dispersion correction.

Keyword	% HF exchange
wb97x_v	17-100%
ωB97M-V
Mardirossian and Head-Gordon's 2016 12-parameter combinatorially optimized mGGA functional, with the VV10 nonlocal dispersion correction. Consistently one of the most accurate non-double hybrid functionals out there: see e.g. this benchmark and this one.

Keyword	% HF exchange
wb97m_v	15-100%
Recommendations
Choosing the appropriate level of theory can be challenging! An extensive 2011 Grimme benchmark suggests that B97-D3 performs best among conventional "pure" density functionals, while higher accuracy can be achieved using any of the hybrid functionals included in Rowan. This recent paper from Grimme and co-workers offers many useful recommendations depending on the task at hand. The best guide, however, is to find a paper which reports benchmark results for systems like those you wish to study and follow those recommendations.

Basis Sets
Choosing a basis set is an important part of running a quantum chemical calculation. Rowan supports many commonly used basis sets of various sizes, permitting users to select the best basis set for their applciation.

When submitting calculations using the Python API, basis sets can be selected through their name, typically the one in the Basis Set Exchange. If no basis set is specified, STO-3G will be used.

import rowan
import stjames

rowan.api_key = "rowan-SK"

# load molecule from smiles
molecule = stjames.Molecule.from_smiles("C1CCCC1")  # cyclopentane

# run calculation remotely and return result
result = rowan.compute(
    "calculation",
    input_mol=molecule,
    name="opt cyclopentane",
    method="b3lyp",
    basis_set="6-31G*",
    tasks=["optimize", "frequency"]
)
For instructions on how to select basis sets when submitting calculations using the web interface, see the web interface documentation.

How Rowan Handles Basis Sets
Generally contracted basis sets are not handled efficiently in Rowan (and many other programs: see this explanation), so we recommend avoiding general contraction unless there is no reasonable alternative. This will probably change in the future.

Rowan uses "pure"/spherical basis functions for d orbitals and higher, meaning that there are 5 d orbitals instead of 6, 7 f orbitals instead of 10, and so forth. This increases computational efficiency because the number of orbitals grows as 
L
L and not as 
L
2
L 
2
 , but differs from how some other programs are structured (for instance, Gaussian uses 6 d functions for Pople basis sets).

Rowan does not currently support effective core potentials, although we hope to change this in the near future. There is also currently no way to specify custom basis sets in Rowan, or to employ different basis sets on different atoms.

Common or Recommended Basis Sets
The number of basis sets available through the Basis Set Exchange can be overwhelming! Here are some common choices, as well as some less common but underrated choices:

Pople's STO-nG basis sets
The venerable STO-nG family of minimal basis sets can be requested for any n between 2 and 6. STO-3G is probably the most popular: however, HF-3c or MIDI! might be a better choice today.

Pople's 6-31 basis sets
Perhaps the most famous basis sets are Pople's 6-31 basis sets. The ubiquitous "6-31G(d)" double-zeta basis set can be requested as 6-31G*, while a larger basis set suitable for single-point calculations is 6-311+G(2d,p). There are many other combinations of augmentation, zeta, and polarization functions possible, but most of them are considered unbalanced and should be avoided.

Jensen's pcseg-n basis sets
An underrated class of basis sets for density-functional theory is Frank Jensen's pcseg family. pcseg-0 requests a minimal basis set, pcseg-1 requests a double-zeta basis set, and so on up until pcseg-4. Augmentation can be requested by prepending "aug", so the augmented triple-zeta Jensen basis set is aug-pcseg-2.

In our experience, these basis sets often dramatically outperform Pople basis sets without incurring a higher computational cost. (See also this discussion by Jensen himself, comparing the pcseg and 6-31 basis sets.)

Dunning's cc-PVNZ basis sets
The correlation-consistent basis sets of Thom Dunning can be requested with keywords cc-pVDZ, cc-pVTZ, and so forth—but these basis sets are generally contracted and thus horribly slow. Instead, we recommend using the "(seg-opt)" variants, which are almost exactly the same but will run much faster. (Gaussian performs an analogous operation on the Dunning basis sets: see the discussion on their website.)

To request these basis sets, use the keywords cc-pVDZ(seg-opt), cc-pVTZ(seg-opt), and cc-pVQZ(seg-opt). Unfortunately, those are the only three Dunning basis sets with optimized variants in the Basis Set Exchange, so any other Dunning basis sets will be very slow (e.g. aug-cc-pVTZ).

Ahlrichs's def2 basis sets
The def2 family of basis sets from Ahlrichs/Karlsruhe can be requested with keywords def2-SV(P), def2-TZVP, and so forth. Their minimally augmented congeners are not yet available on the Basis Set Exchange, but will hopefully be added soon.

Truhlar's MIDI! basis set
The very efficient polarized minimal basis set MIDI!/MIDIX is available under either name, and is a good choice when speed is at a premium (see the discussion here).

Recommendations
Choosing a basis set is challenging but important: this recent paper from Grimme and co-workers offers many useful recommendations depending on the task at hand. In general, we find Jensen's pcseg basis sets are a great choice for DFT calculations: in particular, pcseg-1 is a drop-in replacement for 6-31G(d) with substantially higher accuracy.

While augmentation can be essential in certain cases (e.g. anionic systems), it should be avoided if it's not absolutely necessary, because it can lead to immense challenges with runtime and SCF convergence.

Corrections
It's frequently beneficial to add post hoc corrections to mean-field calculations to compensate for certain inaccuracies in the theory. Rowan supports use of Grimme's empirical "D3" dispersion correction, which has been shown to dramatically improve the performance of Hartree–Fock and density-functional theory calculations (e.g.).

For now, Rowan only supports the D3 correction with Becke–Johnson damping (with the exception of the geometric counterpoise and short-range basis corrections performed internally for composite methods). This correction can be requested by adding the keyword d3bj to the corrections list:

import rowan
import stjames

rowan.api_key = "rowan-SK"

# load molecule from smiles
molecule = stjames.Molecule.from_smiles("C1CCCC1")  # cyclopentane

# run calculation remotely and return result
result = rowan.compute(
    molecule,
    name="opt cyclopentane",
    method="b3lyp",
    basis_set="6-31G*",
    corrections=["d3bj"],
    tasks=["optimize", "frequency"]
)
For instructions on how to select corrections when submitting calculations using the web interface, see the web interface documentation.