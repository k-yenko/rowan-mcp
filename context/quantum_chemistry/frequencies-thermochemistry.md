Frequencies and Thermochemistry
Vibrational frequencies are computed following the 1999 Gaussian white paper. Briefly, the Hessian matrix is converted into mass-weighted Cartesian coordinates, and translational and rotational motion is projected out using the Eckart–Sayvetz conditions. Vibrational modes and frequencies are computed as the eigenvectors and eigenvalues of the resulting Hessian matrix.

Thermochemical values are computed using standard expressions, generally following the 2000 Gaussian white paper. Symmetry-based corrections are applied using symmetry numbers obtained from Pymsym. To account for translation- and rotation-like small vibrational modes, Rowan applies the recommended Cramer–Truhlar correction, where all non-transition state modes below 100 cm−1 are raised to 100 cm−1 for the purpose of computing the entropic correction.

Energies
The energy of a molecule or system can be decomposed into several components, and computational chemists build up the total energy from a variety of calculations. The most common energy components include:

Electronic energy (Ee) - solution to the fixed nuclei Schrödinger equation
Zero point energy (ZPE) - energy arising from the wavelike nature of the molecule "vibrating" in a well
Internal energy (U) - energy of an isolated molecule
Work energy (pV) - energy due to displacing the volume of a system
Enthalpy (H) - sum of electronic energy, ZPE, thermal energy, and pV work
Entropy (S) - measure of "disorder" in a system
Gibbs free energy (G) - total energy of a system
Below is a more detailed explanation of each energy component reported by Rowan.

Electronic Energy (Ee)
Electronic energy (often referred to as the single point energy) is the solution to the electronic Schrödinger equation for a specific molecular configuration without accounting for any nuclear motion. This energy serves as the starting point for all thermochemical calculations, but since it presents a static picture of a molecule, it necessarily omits any contributions from nuclear motion and non-zero temperature. This is the energy you will get from running a single-point or optimization.

Zero-Point Energy (ZPE) Correction
Zero-point energy correction is the additional energy due to the wavelike nature of the molecule being confined in a well. Even at absolute zero, quantum mechanics dictates that molecules possess vibrational energy due to the wavelike nature of matter. The stronger the vibrational frequency (narrower the energy well), the higher the zero-point energy.

The energy of an isolated molecule at absolute zero is simply 
E
0
=
E
e
+
ZPE
E 
0
​
 =E 
e
​
 +ZPE, and calculating the zero-point energy requires a frequency calculation on top of the single point energy calculation.

Thermal Energy (TE) Correction
The thermal energy correction includes non-zero temperature effects. At finite temperatures, translational, rotational, and vibrational modes exist in a Boltzmann distribution, and the thermal energy correction is added to the ZPE to obtain the total energy for an isolated molecule at a given temperature (in Rowan, as in most other quantum chemistry softwares, this temperature defaults to 298.15 K or 25°C).

U
298.15 K
=
E
e
+
Z
P
E
+
T
E
298.15 K
⏟
U 
298.15 K
​
 =E 
e
​
 + 
ZPE+TE 
298.15 K
​
 
​
 

For consistency with quantum chemistry codes, the thermal energy correction reported by Rowan includes both ZPE and the additional thermal energy from non-zero temperature.

Enthalpy Correction
The enthalpy correction expands on the thermal energy correction by adding the pV work term. Displacing the volume of a system requires work, and this work energy is added to the thermal energy to obtain the enthalpy of a system at a given temperature.

H
298.15 K
=
E
e
+
Z
P
E
+
T
E
298.15 K
+
p
V
⏟
H 
298.15 K
​
 =E 
e
​
 + 
ZPE+TE 
298.15 K
​
 +pV
​
 

The enthalpy correction reported by Rowan includes the ZPE, thermal energy, and the 
p
V
pV work term.

Gibbs Free Energy Correction
The Gibbs free energy correction accounts for entropic (S) effects arising in molecules and systems of molecules. This correction accounts for symmetry translational, rotational, and vibrational entropy effects, and is reported at 298.15 K.

G
298.15 K
=
E
e
+
Z
P
E
+
T
E
298.15 K
+
p
V
−
298.15
×
S
⏟
G 
298.15 K
​
 =E 
e
​
 + 
ZPE+TE 
298.15 K
​
 +pV−298.15×S
​
 

The Gibbs free energy correction reported by Rowan includes the ZPE, thermal energy, 
p
V
pV work, and entropy corrections.

Enthalpy (298.15 K)
Enthalpy at room temperature, often written as 
H
298.15 K
H 
298.15 K
​
 , is the total energy of an isolated molecule at 298.15 K, including contributions from nuclear motion and temperature effects, but neglecting any entropic effects.

H
298.15 K
=
E
e
+
Z
P
E
+
T
E
298.15 K
+
p
V
H 
298.15 K
​
 =E 
e
​
 +ZPE+TE 
298.15 K
​
 +pV

Enthalpy at a specific temperature is often reported in spectroscopic works, as it can easily be measured in the lab.

Gibbs Free Energy (298.15 K)
Gibbs free energy at room temperature, often written as 
G
298.15 K
G 
298.15 K
​
 , is the sum of the enthalpy and entropy terms. It is the term that is most relevant to experimental chemists, as most experiments are run with a large number of molecules at a constant pressure in a lab.

G
298.15 K
=
H
298.15 K
−
298.15
S
G 
298.15 K
​
 =H 
298.15 K
​
 −298.15S