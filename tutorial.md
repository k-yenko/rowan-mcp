Running a Geometry Optimization and Frequencies Calculation on Rowan

First, log into labs.rowansci.com and click on new calculation. Here we can upload a file, input the SMILES of the molecule, or draw a 3D structure. We can select the periodic table and the carbon atom to add a carbon, and select the hydrogen here to add another carbon to produce an ethane. We can decorate this ethane with various different atoms, such as a nitrogen on this side and a chlorine on the other. We can quickly optimize this with either a force field or with GFN-FF to produce a better starting structure for future optimizations.

Let's go ahead and save this molecule and change the name to its SMILES name. We can select the level of theory, here defaulting to AIMNet2, which is excellent for organic molecules. select the tasks of optimize and frequencies and click submit calculation. AIMNet2 is a very quick neural network potential and can optimize molecules like this in only a few seconds.

If we click on the optimize tab we can see it is already completed and has done 53 steps in the optimization. We can see it changed slightly from our starting geometry to a slightly more accurate geometry. We can then visualize the frequencies with the lowest frequency here being a wag, the chlorine stretch coming in at 777 wavenumbers, and the highest frequency being an anti-symmetric hydrogen stretch on the nitrogen. We can also compare this to the gauche version of this molecule by clicking on the resubmit button resubmit as calculation and editing the molecule. If we select edit bond angle or dihedral and select the atoms of interest we can then rotate around this dihedral to produce the new structure. We can clean it up with a quick GFN-FF optimization and go ahead and save and rename the structure.

We can then select the optimize and frequency tasks and submit the calculation. While we're at it, let's rename our initial molecule to have trans appended to it so we can differentiate. The optimization of the gauche structure is now done, and we can see that it was able to optimize in only 36 steps, and that all the frequencies are positive. We can select both of these to compare their energetics, and we find that the trans structure is 0.6 kcal/mol higher in energy than the gauche structure. We can also overlay these structures to see how they differ.

Submitting a Single Point Energy Calculation
To run a new single point energy calculation, find your way to this screen in Rowan:

Rowan's workflow selection page

If you're currently viewing a calculation or workflow you already ran, hit the "X" icon in the top left of your screen, just below the navigation bar.

To start submitting a singe point energy calculation, click "New calculation."

Select a Molecule
Calculations in Rowan are run on molecules (or systems of molecules).

To upload a molecule, you can use any of the following input formats:

Upload a file, using the "Upload Files" button. (Rowan accepts .xyz, .gjf, .out, .mol2, and .mae chemical file formats.)
Input a SMILES string, using the "Input SMILES" button.
Paste XYZ coordinates, using the "Paste XYZ" button.
Drag and drop files anywhere on the new calculation page.
For small molecules, it's often easiest to start with a SMILES string. Many 2D molecule drawing programs, including ChemDraw and MarvinJS, will let you export/copy structures as SMILES.

Editing Structures
To modify a structure you've already input, you can click the pencil icon in the top right corner of the molecule viewer and use Rowan's 3D editor.

Charge and Multiplicity
Make sure to set the charge and spin multiplicity for your selected molecule.

Level of Theory
Select the level of theory you'd like to run your calculation at by choosing an appropriate method and basis set.

Rowan won't let you submit a calculation with an incomplete basis set for the molecules you've input.

If any input field shows red, hover over it and read the text that will appear for information about the error.

Corrections
If the engine and method you've selected supports it, use the dropdown to select a correction (currently, Rowan only supports the D3BJ correction).

Solvent
If the engine and method you've selected supports it, click on the solvent field to select a solvent model and solvent.

Tasks
Select the tasks you'd like to run on your structure by clicking the corresponding checkboxes.

To run a single point energy calculation, check "Single Point Energy" and leave all the other checkboxes unchecked.

Rowan can run the following tasks:

Single Point Energy
Gradient
Charge
Spin Density
Dipole
Hessian/Frequencies
Thermochemistry
Optimize
Optimize (TS)
When "Optimize" is selected, Rowan will always conduct the geometry optimization first and carry out all other tasks on the final structure.

Submitting a Geometry Optimization
To run a new geometry optimization, find your way to this screen in Rowan:

Rowan's workflow selection page

If you're currently viewing a calculation or workflow you already ran, hit the "X" icon in the top left of your screen, just below the navigation bar.

To start submitting a geometry optimization, click "New calculation."

Select a Molecule
Calculations in Rowan are run on molecules (or systems of molecules).

To upload a molecule, you can use any of the following input formats:

Upload a file, using the "Upload Files" button. (Rowan accepts .xyz, .gjf, .out, .mol2, and .mae chemical file formats.)
Input a SMILES string, using the "Input SMILES" button.
Paste XYZ coordinates, using the "Paste XYZ" button.
Drag and drop files anywhere on the new calculation page.
For small molecules, it's often easiest to start with a SMILES string. Many 2D molecule drawing programs, including ChemDraw and MarvinJS, will let you export/copy structures as SMILES.

Editing Structures
To modify a structure you've already input, you can click the pencil icon in the top right corner of the molecule viewer and use Rowan's 3D editor.

Charge and Multiplicity
Make sure to set the charge and spin multiplicity for your selected molecule.

Level of Theory
Select the level of theory you'd like to run your calculation at by choosing an appropriate method and basis set.

Rowan won't let you submit a calculation with an incomplete basis set for the molecules you've input.

If any input field shows red, hover over it and read the text that will appear for information about the error.

Corrections
If the engine and method you've selected supports it, use the dropdown to select a correction (currently, Rowan only supports the D3BJ correction).

Solvent
If the engine and method you've selected supports it, click on the solvent field to select a solvent model and solvent.

Tasks
Select the tasks you'd like to run on your structure by clicking the corresponding checkboxes.

To run a geometry optimization, check "Optimize."

Rowan can run the following tasks:

Single Point Energy
Gradient
Charge
Spin Density
Dipole
Hessian/Frequencies
Thermochemistry
Optimize
Optimize (TS)
When "Optimize" is selected, Rowan will always conduct the geometry optimization first and carry out all other tasks on the final structure.

Adding Constraints
If you want to constrain your geometry optimization, you can add constraints. (This is optional.) You can constrain a bond length, an angle, or a dihedral angle.

Adding a constraint means the given bond length or angle won't change during the geometry optimization process.

To add a constraint, click "Add new constraint" at the bottom of the new calculation page. Select the type of coordinate you'd like to constrain and input the appropriate indices. You can also select the atoms using the molecule viewer by first selecting the constraint row and then clicking on the atoms.

Be sure to input the right indices in the right order, otherwise you'll get unexpected results. (Angle A–B–C is not equivalent to angle B–A–C!)

Finding a Transition State

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan, and in this video, we're going to show how to find a transition state in Rowan. In this video, we'll first draw out the reactants, perform a scan to locate a structure that's near the transition state, and then of course, do a transition state search to find the actual transition state and look at the frequencies to confirm that we have indeed found the correct one.

The reaction we're going to be studying is this concerted nucleophilic aromatic substitutions from a 2018 paper by Eugene Kwan and coworkers. And this paper—not super relevant for this video—essentially argues that most SnAr reactions, most nucleophilic aromatic substitutions, in fact, don't proceed through the textbook Meisenheimer intermediate, but instead proceed through a concerted one-step mechanism with no intermediate. And they argue that essentially this only happens in cases where you have extremely electron withdrawing groups that stabilize the anionic intermediate, and then for most reactions of interest in medicinal chemistry, synthetic organic chemistry, etc., that this intermediate is just too unstable and that the reaction happens in a single step. So let's see if we can find that one step mechanism today in Rowan.

We'll start here from the home page of Rowan that shows you all the different calculations you can run. And here we'll click on "New Calculation." And since this is a nucleophilic aromatic substitution, we'll want to start with an aromatic ring. So we'll go to "Add From Library," we'll go to rings, and we'll add this phenyl ring, this benzene ring. And from here, whoops, we'll click on this, turn it into a nitrogen. We'll delete this hydrogen, so we've got ourselves now a pyridine ring. Shift + E gives us a CO2Me, a carboxyl group, sort of a little ester, and then we'll add a bromine here to serve as our electrophile. So this will be a lovely aryl halide that we can use for our nucleophilic aromatic substitution. So we'll say save, we'll say "Ar–Br." You know, maybe if we're gonna look at other ones, we would want to have a better nomenclature than that, but this will be just fine for right now. And we'll say optimize plus frequencies. Say "Submit calculation."

So this has already started running. We expect that this will hopefully be a very fast calculation. Usually things take a sec just to get going. This will be using the AIMNet2 neural network potential, which is a fast and quite accurate neural network potential. It's one of the most efficient methods on Rowan. And it should give very good results for a first pass here. And now here is our optimized structure. So if we play the optimization through, we can see the big changes that we rotate the CO2Me to be in plane, which makes sense. So now we have some conjugation here. And if we look at our frequencies, you know they're all positive. We have no imaginary frequencies, just like we expect. So this is indeed truly a ground state. And this is a lovely reactant complex for our reaction.

So now let's say resubmit, resubmit this now as a scan and now let's edit this. So this is our, you know, this is sort of the ground state of our reactant and now we need a nucleophile. So let's add a nucleophile from the library and for this one let's look at CN-, so cyanide, this is a really good nucleophile and yeah well we'll just try it right here. So we've just sort of, whoops, we only want one. We sort of tossed a cyanide up here. It's sort of hovering above the ring. Maybe this is a little too far away so we can hold Z and drag it down sort of a little more on close. It's a bit tough to do this in three dimensions because you never can quite tell what you're doing in every dimension. But I think this is getting to be about the right spot. Yeah, so now it's hovering over the top of the ring. And this looks like a decent place to start scanning. So let's say save. And now we're gonna say "Ar–Br + CN- scan". So notice we have now a couple of things that demand our attention. So these red boxes here tell us essentially that this combination of parameters does not make sense. So this combination of electrons, charge, and multiplicity is not possible. And it's telling us "I think you've made a mistake." This is either a radical or it has a non-zero charge. In this case, we have added a cyanide to a neutral molecule. So it's right, and our charge should be minus 1. And now this makes sense. We also are going to be doing a scan here, and the scan needs to make sense as well. So we haven't actually specified what we're scanning yet. So let's click. We're going to take this, the nucleophilic carbon here, carbon 18, the carbon on this cyanide. So sorry, let's click into the box. We'll click carbon 18, which auto-populates there. We'll click carbon 5. And now this is saying that right now these are 4 Å apart. OK, so. Let's say our start value, let's say 4 exactly, because we like round numbers. We'll say 1.5 Å is where we should stop the scan, which is about the length of a C–C bond. So that's a very reasonable place to stop the scan. And then we'll say we want, let's say 30 steps. So now we'll say "Submit scan."

Okay, so what this is going to do is it's going to run a constrained optimization with this bond distance frozen at 4 Å. And then what's going to happen is it's going to bring them a step closer together. So the 4 Å optimization will be the first step of the scan. Then it will bring them a little bit closer together and do another optimization. And it will keep doing that until we are all the way to 1.5 Å. So essentially we're scanning along the reaction coordinate or along the specific degree of freedom which we think corresponds pretty closely to the reaction coordinate. And we're going to watch essentially the reaction happen in the computer, which is pretty cool. So on the x-axis here we have, you know, the C18 to C5 bond distance. So from 4 Å to 3.91 Å to 3.82 Å. We can see that these are all pretty low in energy. You know, the cyanide is really pretty far away. It's sort of bouncing around a little bit right now. you know, if some sort of odd and strange things are happening. But in general, we expect that the energy will start climbing at some point once we actually start reacting.

So I've jumped forward about two minutes just to fast forward through some of the scan running time, which isn't... terribly interesting to watch from a video perspective. But this hasn't taken too long. The whole thing has been running for about four minutes. So there's no deceptive video editing occurring here. And what we see is that now the bond is actually starting to form here. So the C18 to C5 distance is about 2.5 Å. So it's definitely not a bond yet, but it's a lot more like a bond than a 4 Å distance is. And if we now hit this play button here the steps that have happened. You know, we can see that down here, when the cyanide is pretty far away, you know, we're sort of just bouncing around over the ring trying to find a stable, I guess, anion–π place to be, but it's, you know, there's not much happening.

Now we're starting to really rise in energy as we actually start reacting. And this is sort of the classical potential energy surface that we expect from a physical organic chemistry class. And so something interesting that we can look at here is, you know, also looking perhaps at this C–Br bond distance. So it, you know, it's bounced around, oh no, that's an angle, sorry about that. So the C–Br bond distance, it's bounced around a little bit down here, sort of as we jitter through the ring. Oh, that just went away as it refreshed. But we do see it now start to increase pretty starkly, which implies that we're essentially breaking the C–Br bond as the C–C bond is formed. So sort of exactly what we expect from a concerted reaction is one bond forms, the other breaks. And so now, you know, if we look at these later steps, now the reaction's really happening. You know, now we're actually just from a distance geometry point of view, we're actually predicting the bond is forming here now. You know, we see this reaction sort of rotating and the bromine coming out of plane and the cyanide coming into plane. And this looks very much like sort of a... potential energy surface. So, you know, we can leave this to keep running and we'll see, you know, the product inexorably form and the bromine be ejected. Oh, there we go. That's pretty formed.

What we now want to do is sort of zoom in and find where we can run a transition state search from. So these points are constrained ground-state optimizations. So we're still finding minima, sort of places where the forces are zero, except for the degree of freedom that we've frozen. This isn't actually what we want for a transition state. So this looks a bit like a transition state, but a transition state is a first-order saddle point on the potential energy surface. So we need actually a totally different optimization algorithm so that we can optimize to a saddle point where we have an imaginary frequency, as opposed to these sort of like constrained ground states. And so if we look here, you know, we can see just the energy, you know, this is sort of the highest energy point. Yep, it's this one.

So let's resubmit from this geometry now. And we'll resubmit this again as a calculation. We'll say "Ar–Br + CN-." But instead of a scan, we're submitting this as a transition state. And so what's really important here is we will deselect optimize, and we'll say optimize parentheses ts for transition state. And so this is now just a different optimization. We're using a different algorithm. We're looking for a different thing. And while ground state optimizations are pretty robust, like you can put something in and you'll usually find a ground state, transition state optimizations, you have to be a lot closer to the transition state for it to converge because it's very difficult to do these saddle point optimizations. There's a lot of spurious saddle points. There's actually some interesting mathematics behind this, but the long and short of it is you want to do a scan first so that you know you're pretty close to where the transition state is before you just start running these optimizations. So we'll say "Submit calculation."

Again, this starts running very quickly. And we'll just give this a sec. Let's go back to our scan, which has since finished. And we can now run the whole thing through, maybe from a little zoom out a little bit and get a different point of view. And what we can really see is just this sort of, you know, almost like a video of the reaction happening, which is pretty cool. So. As we go here, you know, we bring the cyanide in and then we can step through with our arrow keys through here. We do actually, we form one brond, we break the other and just like clockwork, the bromide flies off. And what we see is that the products are much, much more stable than the starting materials, which makes sense because this is indeed a reaction that goes forwards.

Okay, so our transition state optimization took... What was this? 24 steps. And what we should see successfully from a transition state optimization is a single imaginary frequency. So this frequency is actually imaginary. It's an imaginary number because we have sort of an inverted degree of freedom when we do the harmonic approximation, like we have a negative spring constant. We usually write it just as a negative frequency because that's a bit easier to think about. What we want to do is we actually want to visualize what's happening here. We can even tune up the amplitude a little bit to see, and what we expect is that the imaginary frequency corresponds to what's happening in the transition state. So this is showing which atoms are moving. sort of in the saddle point, and what we see is actually, you know, the carbon and the cyanide are getting closer together, and the carbon and the bromine are getting farther apart. And so this is exactly what we expect from an SnAr transition state. And what this shows us, this check that we have only one imaginary frequency, and there's the right imaginary frequency, this shows us that we found the correct transition state.

Okay, so that's how to find a transition state in Rowan. If we want to do this in more depth, so if we wanted to do this perhaps a little bit more rigorously for publication, we could then sort of take this and correct this transition state geometry with a single point energy, perhaps with DFT. So something that's slower, but more reliable and more accurate. This gives us the geometry of the transition state. And then if we want to actually convert this to an energy barrier, so if we want to make a potential energy surface, we would take this number here, the electronic energy, subtract the energy of the starting material, and then subtract the energy of cyanide. So we'd also want to run a calculation on CN minus by itself. And then the barrier to the reaction would be energy of transition state minus energy of aerobromide minus energy of cyanide. And that would give us the barrier to the reaction, and we could predict the rate with the Arrhenius equation.

Submitting a Transition State Optimization
To run a new TS optimization, find your way to this screen in Rowan:

Rowan's workflow selection page

If you're currently viewing a calculation or workflow you already ran, hit the "X" icon in the top left of your screen, just below the navigation bar.

To start submitting a TS optimization, click "New calculation."

Select a Molecule
Calculations in Rowan are run on molecules (or systems of molecules).

To upload a molecule, you can use any of the following input formats:

Upload a file, using the "Upload Files" button. (Rowan accepts .xyz, .gjf, .out, .mol2, and .mae chemical file formats.)
Input a SMILES string, using the "Input SMILES" button.
Paste XYZ coordinates, using the "Paste XYZ" button.
Drag and drop files anywhere on the new calculation page.
For small molecules, it's often easiest to start with a SMILES string. Many 2D molecule drawing programs, including ChemDraw and MarvinJS, will let you export/copy structures as SMILES.

Editing Structures
To modify a structure you've already input, you can click the pencil icon in the top right corner of the molecule viewer and use Rowan's 3D editor.

Charge and Multiplicity
Make sure to set the charge and spin multiplicity for your selected molecule.

Level of Theory
Select the level of theory you'd like to run your calculation at by choosing an appropriate method and basis set.

Rowan won't let you submit a calculation with an incomplete basis set for the molecules you've input.

If any input field shows red, hover over it and read the text that will appear for information about the error.

Corrections
If the engine and method you've selected supports it, use the dropdown to select a correction (currently, Rowan only supports the D3BJ correction).

Solvent
If the engine and method you've selected supports it, click on the solvent field to select a solvent model and solvent.

Tasks
Select the tasks you'd like to run on your structure by clicking the corresponding checkboxes.

To run a TS optimization, check "Optimize (TS)."

Rowan can run the following tasks:

Single Point Energy
Gradient
Charge
Spin Density
Dipole
Hessian/Frequencies
Thermochemistry
Optimize
Optimize (TS)
When "Optimize" is selected, Rowan will always conduct the geometry/TS optimization first and carry out all other tasks on the final structure.

Adding Constraints
If you want to constrain your geometry optimization, you can add constraints. (This is optional.) You can constrain a bond length, an angle, or a dihedral angle.

Adding a constraint means the given bond length or angle won't change during the geometry optimization process.

To add a constraint, click "Add new constraint" at the bottom of the new calculation page. Select the type of coordinate you'd like to constrain and input the appropriate indices. You can also select the atoms using the molecule viewer by first selecting the constraint row and then clicking on the atoms.

Be sure to input the right indices in the right order, otherwise you'll get unexpected results. (Angle A–B–C is not equivalent to angle B–A–C!)

Running Rowan's Multistage Optimization Workflow

Transcript
This is Jonathan Vandezande, the Director of Computational Chemistry here at Rowan. Today I will be providing an introduction to using the Multistage Optimization workflow on the Rowan platform. Optimizations in computational chemistry can be very expensive, and it is often recommended to use a different method for optimization and single points to reduce the computational cost or increase the accuracy of computations. Rowan's Multistage Optimization workflow provides Pareto optimal combinations of methods that span the fast to accurate frontier. We spent a lot of time choosing the best modes for a wide variety of systems, preventing users from having to memorize a bunch of magic methods. These modes cover all of the first 86 elements in the periodic table and are excellent for computing the geometries and energies of molecules, non-covalent interactions, and transition states. To run a Multistage Optimization, log into the Rowan platform at labs.rowansci.com and select new Multistage Optimization. Enter the molecule or system you are interested in with one of our input methods. In this tutorial we will upload a butane molecule via SMILES. Here we have the trans configuration of butane, so we will change the name to "Butane - trans". We can check that the charge and multiplicity are correct, and then choose the type of method we would like to do. We can choose to run a transition state as the multistage optimization supports both traditional and transition state optimizations and compute frequencies. We can also choose our mode. The Rowan platform supports four different optimized modes. These are typically RECKLESS, RAPID, CAREFUL, AND METICULOUS. The first two are good for exploratory work and generating initial data. Careful is useful for publication quality results and meticulous is only used for the most demanding of situations. We can see the methods that make up these modes by mousing over the info box. RECKLESS utilizes a GFN-FF optimization with GFN2-xTB single points, generating very quick results that can direct the optimization of your work. RAPID uses a GFN2-xTB optimization with an r²SCAN-3c single point, combining the optimization speed of a semi-empirical method with the accuracy of DFT single points. This is the mode that I use the most often in my own research and strikes an excellent balance between speed and accuracy. CAREFUL runs a DFT optimization with r²SCAN-3c and a single point with ωB97X-3c and produces excellent publication quality results. METICULOUS stacks multiple DFT optimizations to quickly converge on the minimum without requiring a costly optimization with the highest accuracy method. This mode is typically only used when the utmost accuracy is needed and can be very expensive for larger systems. For this demonstration we will use the RECKLESS mode. I will go ahead and submit this job now and we can see it start running. Since this is running in the cloud on compute servers managed by Rowan, the job will run very quickly. We can see here our molecule has already optimized at the GFN-FF level of theory and performed a GFN2-xTB single point. We have our total electronic energy listed here and if we had run frequencies we would also be able to visualize them. We can check the charge tab to see the Mulliken charges of our molecule. Here we can of course see that our carbons are slightly negative and our hydrogens are slightly positive. We can then run a resubmission to compare this to the gauche conformation. Here I click the resubmit and resubmit as multistage optimization and change the name to "Butane - Gauche" We can then edit the molecule and select edit bond angle or dihedral to change the dihedral angle of this carbon backbone. Here we can drag to turn this into the gauche conformation, putting it in the approximately right condition and then selecting optimize with GFN-FF to further get a good starting guess geometry. We can then click save and then submit MultiStage Workflow. As this is running in the cloud again we can see now here our gauche conformation of the molecule. In a few seconds it should be fully optimized and we can see the fully optimized energy here. We can then select both of them to see the relative energies here with the gauche conformation being about 0.6 kcal/mole higher in energy, as would be expected. We can overlay the structures to see the differences as one of them here is trans and one of them is gauche.

Running Rowan's Orbitals Calculation Workflow

Transcript
Hey everybody, it's Corin, CEO and co-founder of Rowan. Today we're going to look at orbitals calculations in Rowan. And we're going to do so by looking at the molecule azulene.

Azulene is an interesting hydrocarbon because unlike most hydrocarbons, which are clear liquids or white solids, azulene is actually blue. It's found in this cool blue mushroom here—it's the compound that makes the mushroom blue. And the reason that azulene is blue is because it has these two interesting rings, a seven-membered ring here and a five-membered ring here. And if you think back to intro organic chemistry, you can remember that seven-membered rings can be aromatic if they have a positive charge in addition to three double bonds, whereas five-membered rings can be aromatic if they have a negative charge in addition to two double bonds, because then they're both 6π systems, following the 4n+2 rule.

And so what you get in azulene is actually this really strong, sort of like, delta positive character in the larger ring and delta minus character in the smaller ring. And as a side effect of this, it also happens to be blue, which is quite cool. You can imagine a good comparison here is naphthalene, which is the same number of atoms, but sort of a 6 and a 6 instead of a 7 and a 5, and naphthalene is colorless and does not have the same dipole moment. So I thought it'd be fun to look at the orbitals of azulene for this demo and sort of maybe gain some insight into this molecule.

So to submit an orbitals calculation, we go to sort of the main submission page of Rowan that you get here when you don't have a calculation selected and you click “New Orbitals Calculation.” You'll almost always want to run an orbitals calculation on an optimized structure if you want to view the orbitals for the optimized form of that structure. There are cases where you might want to view orbitals on a non-stationary or distorted structure, but in general, it's good practice to run an optimization first. So let's go over here to the azulene optimization/frequency. We can go over here to this optimization tab and watch what happened. So we're pretty close; I input this from a SMILEs string, and it looks about right. But this just gets us all the way down to the correct geometry. And then we can check the frequencies and see that, yep, there's no negative or imaginary frequencies. These are all very normal stretching modes, indicating that this is indeed a ground-state structure.

Now the reason I didn't run this on the call is that this is a DFT optimization: we have to do orbitals with DFT in Rowan, and so we need to do the optimization at DFT if we want to get the true minimum, and so this took about half an hour to run, so I didn't want to do that on the call. In contrast, the actual orbital calculation here took a lot less time. So it only took about a minute, not even a minute. And we can see here that it's resubmitted from this previous calculation. So if we lost track of where the optimization was, we could go find it this way.

Okay, so what actually happens when we run an orbitals calculation in Rowan? So we have all these tabs up here, and what this is, is it's not just orbitals, it's a wide variety of properties that let us sort of understand where the electrons are, what they're doing, what the electronic distribution and properties of this molecule is. So the idea here is a whole toolkit of closely related methods that'll let us really dive into this molecule's electronics in detail.

So we'll start here with orbitals. So this is the HOMO, the highest occupied molecular orbital. We can see here that the occupation is 2 for this, in this column, and that the energy in Hartree is about negative 0.18. If you're more used to seeing this in eV, of course we can convert to eV, and that's about what we expect for HOMO. That seems very reasonable. And now this actually illustrates what this orbital looks like. So red and blue represent different signs. We can invert this if we want to, just for visual preference. This is where the highest occupied molecular orbital is. And we see that it's sort of predominantly localized on this ring here, on the five-membered ring, which makes sense, because we remember that there's more electrons hanging out in the five-membered ring than on the seven-membered ring, and so it's not surprising that the HOMO reflects that. And we can sort of change this cutoff to make these bigger. So if we want to see this instead, this is just visual style. You know, we're drawing an isosurface, so if we use smaller values for the cutoff, the orbitals will be bigger. If we use bigger values for the cutoff, the orbitals will get much smaller.

So we can look now also—well, let's reset that because this looks a little silly—we can look at the HOMO - 1, which is different. We can look at the LUMO, which sort of starts to pick up more antibonding character and is more localized on the seven-membered ring. We can look at the LUMO + 1. And when you submit an orbitals job, you can say how many orbitals you want to see. So if we wanted to go all the way up to the LUMO + 6 or the HOMO - 6, we could do that. We just don't do it by default because often those orbitals aren't relevant, and we just really care about the frontier orbitals. Obviously, one thing you might care about here is that band gap. And so that would just be the energy of the LUMO minus the energy of the HOMO.

So the next tab over is isosurfaces. And what this lets us view is electron density and electrostatic potential. If this job had radicals—if this were unpaired electrons—we could also view the spin density isosurface. But since azulene, all the electrons are paired, it's not a radical species, we can't view the spin density because it's zero everywhere. So we can start with the electron-density isosurface. So this just tells us where the electrons are. You can see that they're in the bonds, right where you'd expect. There's some more on this side. There's slightly fewer; maybe you can imagine you see that on this side. But it pretty much just looks like bonds. And again, we can tune the cutoff to make this look bigger or smaller.

The electrostatic potential, this is sort of the positive or negative potential put out by the charged nuclei and electrons. So this tells you the force that a test charge would feel at a given point. And again, this does sort of scale, it looks a little bit like the electron density, because if you're really close to the nuclei, you'll feel a repulsive force, and as you get farther away, that attenuates. So we make the cutoff smaller, and it gets bigger. If we make the cutoff bigger, the isosurface gets smaller.

In general, the most helpful way to view this though is to actually color the electron density isosurface by the electrostatic potential. And so this is what you'll often see in figures and papers. And if we do this, what we see is it's the same shape as just the electron density isosurface, but now instead of being gray, here we have a little bit of a different cutoff, we can see the areas where there's delta positive character in blue and delta negative character in red. None of this is quite red but we can change the cutoff to sort of exaggerate it, so there that's a little more red. I mean this actually now looks exactly like what we expect. So here around the outside we have the the delta positive from these sort of acidic or you know maybe not acidic and there's a pKa but they're actually not not terrible hydrogen-bond donors, these C–H bonds. And so you can imagine these, you know, sort of sticking to a hydrogen-bond acceptor and creating some of these C–H binding interactions we often see in binding sites or crystal structures. And then on the top we have this electron cloud. You see a region of delta minus. So this is now there's a lot of electron density above and below the ring and we see that reflected in the electrostatic potential.

Something else that's a little bit more subtle here is that, you know, it doesn't come through perhaps as clearly as it would in a different system, but if we actually look, there's more red on the five-membered ring. This is sort of orange, whereas we're just yellow and green over here on the seven-membered ring. And this reflects the exact same idea that the five-membered ring is delta minus and the seven-membered ring is delta plus. So that's sort of reflected here in the electrostatic potential, which is pretty cool. We can switch to a red–blue color map if that's more visually appealing to you, where the delta positive is blue and the delta minus is red, but instead of going through the rainbow, it sort of goes through white instead, as a neutral color. It's sort of just a matter of visual style. This is more common in the literature, though.

Some other properties here: these are different atom-centered charges. So when we talk about atom-centered charge, there's no one correct way to localize a distributed electron density onto specific atoms. So there's many different schemes: there's Mulliken charge, there's Löwdin charge, there's Hirshfeld charge, CM5, RESP, CHELPG. You know, there's a lot of these different schemes. We've put two of the more common ones in here, so Mulliken and Löwdin, and in general we recommend Löwdin as Mullikin is quite basis-set sensitive. You know, all methods are basis set sensitive to some degree, but Mullikin is notoriously basis -et sensitive. But we can switch which one to visualize by clicking on the different columns. And what we can do is just look around and see what charge do different atoms have, and so we can see different numerical values. I think probably the biggest takeaway we see from this is that the hydrogens are delta plus and the carbons are delta minus, which does match exactly what we saw from the isosurface. So that's reassuring.

The bond orders tab—this is something that I actually didn't encounter for quite a while as a computational chemist. But there are ways that you can actually quantify bond order between two species. You know, we often draw different resonance structures where benzene alternates between single and double bonds. And so we sort of, you know, you'll sometimes hear that like a C–C aromatic bond has a bond order of like 1.5 on average. But in different systems that's true or untrue to varying degrees. We can actually computationally come up with guesses for what the bond order as a decimal is for a given pair of elements.

And so if we look here, for instance, at this C–C bond, the Mayer bond order is predicted to be 1.35, and Wiberg bond order is predicted to be 1.45. Both of those are reasonable. These usually match relatively closely. Here, this bond is predicted to be quite a bit longer, though, so 1.03 and 1.20. And so we might actually have a decent standing to argue that this bond here, C5 to C9, is a longer and less double C–C bond than C4 to C5. So we do indeed see this reflected in the bond distances. This one is 1.39 Å up in the top left corner here. So this is 1.39 Å versus this one is about 1.5 Å. And so you know this is just a complementary way to quantify the extent of delocalization and bonding, which can be very useful in certain circumstances.

And then our last tab here is multipole moment. This shows us the dipole moment and the quadrupole moment of this molecule. So the dipole is a vector. The traditional way to depict it is to point from the region of positive charge to the region of negative charge. You can invert that in Rowan if you want to, but that's standard. And what we see here is that we're pointing, again, from the seven-membered ring to the five-membered ring, from positive to negative, just like we expected. And we also have the magnitude, which is 0.4 Debye, and then we have the actual components of this vector.

Something that's interesting to note is that this prediction of the dipole moment is quite wrong. So the dipole moment is experimentally 1.08 Debye, whereas here we're 0.4. I'm sure we're like, you know, almost 3x too small, or almost a third of the true value for the dipole moment. It's interesting to think about why this might be. I'm not actually sure, but my guess is that this reflects sort of the self-interaction error you get with r2SCAN. So r2SCAN is, in general, a really, really good level of theory for geometries and sort of routine work. But it doesn't have the long-range Hartree–Fock exchange that you might expect from a hybrid functional. And so it's less accurate at band gaps and things like this, and I think that's reflected in the erroneous prediction of the dipole moment, so this is actually quite an interesting test case.

And if you were doing a project focusing on azulene, one of the things you might want to do right off the bat is to check that the DFT method you're using actually can reproduce the electronic distribution as quantified via the dipole moment correctly. And if it can't, then you might consider trying a different functional or reaching out to a computational expert to figure out what functional would be appropriate. (You're of course always welcome to reach out to our team at Rowan for a consult.)

And then last but not least we have the quadrupole, which is less easily visualized, unfortunately. But we can see the trace, sort of the matrix elements, we can diagonalize it. And so if you're working on a project that depends on sort of higher order multipole moments, then this might be very useful to you. Anyhow, this is how to do orbitals calculations in Rowan. I think what I've hopefully conveyed is that there's a lot of ways to get insight at a very low computational cost. So happy computing.

Running Dihedral Scans on Rowan

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan, and in this video we're going to look at scans: what they are, how to submit scans through Rowan, and how to analyze the results.

First off, what is a scan? A scan provides us a way to ask how a molecule or system of molecules responds when we change one of its geometric parameters. This could be the distance between two atoms, the angle, or the dihedral angle between groups of atoms. And what a scan does is essentially run a series of constrained optimizations for different values of the coordinate we're scanning along and then shows us how the geometry and energy of the system responds to this perturbation. It's easiest to show with an example, so let's hop right in.

From the home page of Rowan we can go to this "new scan" button and click it, and then we can go ahead and just draw a molecule. So let's start by inputting the SMILES string for butane. We can, as always, also draw the molecules ourselves, upload a file, or load in from an external source. So this is butane, the four-carbon alkane. And to look at a scan, we say "butane scan," we want to first specify which coordinate we want to scan along. So we can click into this box and then click the four atoms for which we want to study the dihedral. Here we can see we've selected the four carbon atoms of butane and we can see the current value for their dihedral angle both here and here. In both cases we see that this is 295 degrees or so, which is corresponds pretty closely to the gauche geometry of butane. So let's look at all of the different possible values here: we'll scan from 0 to 360 and then we will look at 30 points for this and we'll say go.

This is going to queue a series of constrained optimizations like we talked about. We selected 30 different steps, so at 30 different coordinates we will run constrained optimizations and we're going to be doing this using the AIMNet2 level of theory which is a machine-learned interatomic potential that provides very fast and quite accurate results for studies like this. And what we can see is that this is actually so fast that we're already seeing these optimizations finish. It helps that butane is such a small system. Each of these points represents a different geometry that's been optimized with the constraint that this dihedral indicated is frozen, and we can see how the energy changes as we move along this coordinate. Looking more closely at this plot here, obviously we have the dihedral angle in question here, and right now we're seeing values from 220 to 360 and we'll populate the rest of these values as time goes on, and we're seeing the relative energy of these different constrained geometries. The lowest energy, which currently is this one, is shown as zero, and the highest energy, which is this one, is shown as 4.62. You can see the relative energy here.

This is a really nice way to visualize the torsional preferences of this bond, like you might do in an introductory conformational analysis portion of a class, and what we might see is we've actually just found a new lowest energy geometry over here while I've been talking. This corresponds to a value of about 180 degrees—I'm sure if we had exactly 180 as a scan point that that would be the minimum. And this sort of intuitively makes sense. Here we have the two bulky methyl substituents around the central bond as far away as possible, so they're 180 degrees from each other, that's sort of the fully staggered geometry. And here we can see we have some sort of local minima that are about 0.3 or 0.4 kcals uphill in energy, so this corresponds to the gauche configuration. So these bonds are still interleaved nicely here: we're in a nice staggered conformation, but the two methyls are a little bit closer to one another, and so we pick up these extra destabilizing interactions. Here we can say these barriers here, where we're staggered but the methyls are 120 degrees from each other, those are a good bit higher in energy, about 3 kcal/mol above the minimum. And then this conformation here, where the methyls are fully eclipsed with one another, is very, very unstable—that's almost 5 kcal/mol above the minimum.

So this shows what a scan is: it's pretty nice to click through, it quickly gives you a sense for where this compound will prefer to hang out. Let's resubmit it now with a perturbation and see how it changes. So we can resubmit this here. Again we can say "resubmit as scan," and instead of butane this time, let's look at 2-fluorobutane. And so to do this we will go to the periodic table function here, select fluorine, put this in here. So this will break the symmetry of the system. We'll say "save," and now we'll have an extra bulky group here—probably not quite as bulky as the methyl group, but still a noticeable amount larger than hydrogen. And so this will be pretty interesting to look and see how this actually modulates the energetics around this C–C single bond. So we'll submit this scan, just like we did the first, and it will start running.

We can see here, if we want, that we can go to the logfile and actually read details about what's happening, for debugging or just if you want to get a good sense for all of the steps involved in a scan. It really ends up being quite a lot because we're running so many constrained optimizations. And furthermore, Rowan uses something called the "wavefront propagation" method, which came out a couple years ago in the literature, where we essentially scan not just in one direction, but also backwards along the points we've already scanned to make sure we don't discover any new low-energy geometries. And this leads to nice smooth-looking scan curves that are more reproducible and a bit more rigorous than if you just scan over the whole potential-energy surface once. You can sometimes get these artifacts from incomplete relaxation.

So here we're seeing this potential energy surface unfold as the scan continues running, and it's not necessarily obvious how this differs from the previous one. What we can do is now actually select both scans and see them superimposed on the same graph. And so now we have the butane scan that's shown in red—here's our butane molecule when we click here—then we have our 2-fluorobutane scan shown in blue. And what you can see is that actually some of these barriers are about the same, such as this one here, where we have the two methyl groups right next to each other, which is still really high in energy. This one's also pretty similar where we have the two methyls gauche. But this one is much, much higher in energy than it was before. And this now starts to make sense because now we have this, the fluorine group we added, which is sort of bonking into this methyl group here. And so that adds an extra steric destabilization, which raises this by quite a bit, it looks like almost two kcal/mol of extra destabilization that's given by this interaction.

Submitting a Scan
Running a scan will give you information about the energetic profile of a selected coordinate by running a series of component optimizations (called "scan points"). Rowan uses the wavefront propogation method to run scans, which helps ensure scan points don't get stuck at unfavorable local minimums.

To run a new scan, find your way to this screen in Rowan:

Rowan's workflow selection page

If you're currently viewing a calculation or workflow you already ran, hit the "X" icon in the top left of your screen, just below the navigation bar.

To start submitting a scan, click "New scan."

Select a Molecule
Scans in Rowan are run on molecules (or systems of molecules).

To upload a molecule, you can use any of the following input formats:

Upload a file, using the "Upload Files" button. (Rowan accepts .xyz, .gjf, .out, .mol2, and .mae chemical file formats.)
Input a SMILES string, using the "Input SMILES" button.
Paste XYZ coordinates, using the "Paste XYZ" button.
Drag and drop files anywhere on the new scan page.
For small molecules, it's often easiest to start with a SMILES string. Many 2D molecule drawing programs, including ChemDraw and MarvinJS, will let you export/copy structures as SMILES.

Editing Structures
To modify a structure you've already input, you can click the pencil icon in the top right corner of the molecule viewer to use Rowan's 3D editor.

Charge and Multiplicity
Make sure to set the charge and spin multiplicity for your selected molecule.

Level of Theory
Select the level of theory you'd like to run your scan at by choosing an appropriate method and basis set.

Rowan won't let you submit a scan with an incomplete basis set for the molecules you've input.

If any input field shows red, hover over it and read the text that will appear for information about the error.

Corrections
If the engine and method you've selected supports it, use the dropdown to select a correction (currently, Rowan only supports the D3BJ correction).

Solvent
If the engine and method you've selected supports it, click on the solvent field to select a solvent model and solvent.

Select the Scan Coordinate
With Rowan, you can scan a bond, angle, or dihedral.

You can manually select the coordinate type and input atom indices, or you can click into the scan coordinate box to select the coordinate on the 3D viewer.

Once you've selected a coordinate, you'll need to select values for:

Start: the smallest value of the selected coordinate to run
Stop: the largest value of the selected coordinate to run
Num: the number of scan points to run
For example, if you're scanning the bond C1–C2 and select start as 1, stop as 2, and num as 5, the scan will run 5 scan points at 1, 1.25, 1.5, 1.75, and 2 Å.

Adding Constraints
If you want to constrain your scan (this will constrain the optimizations at each scan point), you can add constraints. (This is optional.) You can constrain a bond length, an angle, or a dihedral angle.

Adding a constraint means the given bond length or angle won't change during the geometry optimization process.

To add a constraint, click "Add new constraint" at the bottom of the new scan page. Select the type of coordinate you'd like to constrain and input the appropriate indices. You can also select the atoms using the molecule viewer by first selecting the constraint row and then clicking on the atoms.

Be sure to input the right indices in the right order, otherwise you'll get unexpected results. (Angle A–B–C is not equivalent to angle B–A–C!)

Running Rowan's Conformer Search Workflow

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan. In this video, we're going to look at conformer searches.

First off, what is a conformer search? Well, while some molecules are very rigid and exist only in one shape, most molecules have one or more rotatable bonds and thus can exist in a variety of shapes. The point of a conformer search is to quickly figure out which of these are relevant, are going to be the ones that are low enough in energy to actually happen in the real world—either for binding to an active site, packing in a crystal lattice, or reacting in a transition state—so that we don't have to use our chemical intuition to guess. We can actually use computation to narrow this down intelligently.

It's easiest to show, not just to explain, so let's just try running a conformer search on a simple molecule and talk about what happens. We'll start by clicking the "New conformer search" button from the main page of Rowan and we'll go ahead and draw a 3D structure so we have a molecule to demo. We'll draw n-pentane which is a simple five-carbon alkane and also a laboratory solvent. This is a nice molecule because it's small, so it's relatively tractable (there aren't that many conformers), but there's also a lot of rotatable bonds. Every carbon–carbon bond here can potentially be rotated around, so there are actually a lot of possibilities of different shapes that this molecule can take on.

Now when we're running a conformer search we're faced with several questions: we can choose what solvent we want to use, what method we want to use, and what mode we want to use. So, the solvent actually dictates if we're going to try to model the effect of solvent or if we're content modeling this in the gas phase. For this example, we'll just leave it in the gas phase, although of course it might be more relevant (depending on the application) to model the effect of a solvent. The method asks us which method we want to use to score the output conformers. In this case, we'll stick with the default AIMNet2 neural-network potential, which is fast and quite reasonable for things like this.

And then the mode is the most complex, and that actually asks how we are going to generate and winnow down these conformers. We have some more details if you hover over this little info icon, and what you can see is that there's sort of a lot of things: how many conformers we're going to look for, what program we use to generate them, what level of theory, what energy cutoff. We here at Rowan have put a good amount of time into trying to choose really really good defaults for these so that the users don't have to. Basically what it boils down to is that, depending on your use case, usually rapid is fine. If you want to be very very careful that you've gotten all the conformers careful or meticulous could be better—and if you're trying to quickly search through an entire library where runtime is really, really important, then reckless is probably best. But for this use case, as with most, we'll stick with rapid (which is also the default), and we'll say "submit conformers."

So what this is doing behind the scenes while it runs is using one of the programs I mentioned earlier. This one will use RDKit to generate lots and lots of potential conformers. and then is going to go through a multi-step process of iteratively optimizing and filtering these so that we remove duplicate conformers and filter out any conformers that are too high in energy to be reasonable—and now it's finished.

What does this output mean? So, we have a list of conformers here in a little table. We have a ∆ energy, a relative energy in kcal/mol, and then we have a weight. So this essentially corresponds to what the energy is relative to the lowest energy conformer. So we can see here that conformer 1 is lowest in energy, it's this sort of slightly bent conformer. Conformer 2 is a fully linear conformer, and that's predicted to be 0.18 kcal/mol higher in energy. So that's almost the same energy, but not quite. Conformer 3 now is quite a bit higher in energy, so that's sort of doubly bent. And we can see that that's 1.2 kcal per mole, higher in energy. and then conformer 4 is this sort of syn-pentane conformer here. So there's this sort of clash between the two ethyl groups around the central carbon atom. And so that makes us, you know, 2.3 kcal per mole higher in energy.

And for those of us who struggle to do logarithms in our head, we can look over here at the weights and see that what's predicted to happen is that conformers 1 and 2 will account for the bulk of the population at room temperature. So conformer 1 will be about 53%, conformer 2 will be about 39%, conformer 3 will have maybe 7%, and the very unhappy conformer 4 will only be 1% of all molecules in solution. So that's what a conformer search looks like.

We can also do some other things. So we can overlay all of these conformers to sort of get them plotted in the same area. And while this is pretty cool—it gives you a sense of sort of the overall flexibility of the ensemble—we can also do some even more interesting things by selecting a couple of the atoms and aligning on that. So let's just see, given that these three atoms we try to align as closely as possible, like what will the overall rest of the structure look like? And we can see that, you know, some of them sort of zigzag off to the side, and others are totally straight. And the opacity here indicates sort of the energy of the conformer, so the darker conformers are lower in energy, whereas the lighter ones are slightly higher in energy.

Running Rowan's Tautomer Search Workflow

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan. In this video, I'm going to walk through tautomers: what they are, how to run a tautomer search on Rowan, and how to interpret the results.

First off, what are tautomers? So tautomers are groups of molecules that can readily interconvert under fairly normal conditions. Most commonly, this means compounds which can interconvert between each other by switching protons. These are prototropic tautomers, like ketones and enols. There are other forms of tautomerism, like the ring–chain tautomerism exhibited by some sugars, but we're not going to talk about that more in this video. That's much less relevant for most cases.

One example of a nice tautomeric molecule here is 4-pyrimidone. So you see the molecule as drawn is in one of the N–H tautomers because the proton is sitting on an N. But we can also imagine the proton sitting on this other N and shuffling this double bond around, or even sitting on this O to form sort of the O–H tautomer. And when you're faced with a molecule like this, in this case, we can sort of guess that this is the relevant tautomer because it's the one that's on the Wikipedia article. But it's not very obvious from first principles how to necessarily guess where the protons will prefer to sit. It can be pretty sensitive to the exact steric or electronic effects in a given molecule. So it's nice to be able to run a calculation to try to get an estimate for what will happen.

So let's try it out on this compound since we already sort of know the right answer. We can copy and paste the SMILES string and head over to Rowan, where we can click the "new tautomer search" button from the main page. We can input the SMILES string and we can say "4-pyrimidone", submit and there's our molecule, just like we saw it on Wikipedia, with the proton sitting on, I suppose this is N3 in the nomenclature. Now we have very little to do to run the tautomer search. The only thing we have to select is the mode, which essentially tells us how we're going to generate the conformers of each tautomer and in most cases careful is appropriate, unless you're really trying to run this on a big library. So we'll say "submit tautomers."

Let's talk about what's happening behind the scenes while this runs. The Rowan tautomer search code is going to iterate through all potential tautomeric sites: it's going to try to find the places that are reasonable to add or remove protons, and then it's going to run a conformer search and geometry optimization on each of these sites, and then compare the energy of all the different tautomers. In the end, this gives us an output like this. So we see the lowest energy tautomer is number one here, which indeed puts the proton on N3, like we saw on Wikipedia. The second highest energy tautomer is the O–H tautomer, and then the highest energy tautomer is this N1 tautomer. It's labeled as N5 here, but if we follow the proper sort of pyrimidine nomenclature, this should be nitrogen #1. And so we can see from this output that the relative energy is shown here along with the weight. So this lowest energy tautomer has a relative energy of 0 because it's the lowest, the O–H tautomer is like 1.3 kcal/mol above, so that's about a 9 to 1 ratio that's predicted. And then this N1 tautomer is very high in energy, almost 5 kcal/mol above the ground state, and is predicted to have really almost no population whatsoever in solution. So if we were trying to engineer a drug in which we wanted one of these tautomers, it'd be helpful to have these results. If we think there's a key interaction that this N–H is making, for instance, we could feel pretty confident that this is an accessible tautomer, whereas if we expected this N–H to make an interaction in a binding site, we might be pretty disappointed by the results we got back.

So let's try this on another compound just to showcase how different electronic effects can impact tautomeric populations. So we can take this molecule, and we can resubmit it. We'll resubmit as a tautomer search and now let's say we'll do 2-fluoro-4-pyrimidone, so we'll throw a fluorine in there, which we should sort of expect will probably have some sort of impact on the different stabilities of these different tautomers, although we might not be able to guess ab initio what this might have. So actually, if you want to pause the video right now and think about what effect you'd expect this to have, go for it and we can see if your intuition was right or not.

Okay, I'll go ahead and submit this, and it's gonna run right away which is lovely. Yeah and so now we can see in this case we resubmitted from this totomer sort of the N1 tautomer but it doesn't matter because Rowan will search through all the tautomers no matter the input structure, so it's not important to resubmit from any given tautomer. And there we go, and here's the answer. Did you get it right? So now the lowest energy tautomer—by a lot—is predicted to be this O–H tautomer. The tautomer which was previously favored, this N3 tautomer, is now about 4 kcal/mol higher in energy. And the N1 tautomer is now insanely unstable, so almost 8 kcal/mol above the ground state. And it's worth thinking about why this might be.

So this perhaps is a little bit of a surprising result. But I think what we can think about in trying to interpret this is that in this case, OH is not a super electron-withdrawing group. It sort of depends on exactly where you are, but in general we think of O–H or O–R substituents as somewhat electron-donating. But in these other two cases, we have this CO, this carbonyl, which we do think of as quite an electron-withdrawing group. And so my interpretation of this is that when we add this extra very electronegative atom that we're adding on here, we're actually destabilizing other electron-hungry groups on the ring. And so, as a result we destabilize anything that has a C=O double bond and stabilize anything that has a C–O single bond, just because everyone's able to get their preferred electron density a little bit more easily in this case. I'm not sure if that's the right way to think about it: there might be a more intelligent or more mathematical way to think about it, but that's how I interpret these results. Anyhow, thanks for watching!

Running Rowan's pKa Prediction Workflow

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan, and in this video we're going to talk about pKa prediction: what pKa means, how to run pKa calculations through Rowan, and how to interpret the results.

First off, what does pKa mean? So pKa allows us to quantify the acidity or basicity of different molecules and different functional groups within molecules. So basically the pKa is a single parameter which refers to how easy or hard it is to remove or add protons from a given site. This is a pretty foundational concept in organic chemistry. So a lot of intro organic chemistry classes will involve students having to look through and memorize lists and charts of pKa data for given molecules, to build up an intuition about how different substitution and different functional groups will impact the pKa of different sites. This is done because pKa is super important: it determines reactivity, it determines whether a molecule will be charged or neutral under various conditions, and pKa-related thinking is used to inform a whole lot of other sort of structure–activity relationships in organic chemistry.

If you've been around organic chemistry for a while, you might recognize this as the Evans pKa table. It's pretty famous, at least for people within a certain subculture, and it's just composed of lists and lists and lists of pKa values for different compounds in water and DMSO. This is pretty nice if the compound you care about is actually in this table, but another fact about pKa is that it's very sensitive to substitution. In fact, pKa trends are used to compare other things that are sensitive to substitution through Hammett relationships. Because pKa values are so sensitive to substitution, it's nice to be able to compute them from scratch for the molecule we care about, instead of having to dig through tables like this or the literature to find reliable reference data for the most similar compound we can find.

So let's look at what it takes to actually calculate a pKa value in Rowan. So we'll do so for pyridine, which is a really nice example compound. It's one of the most fundamental heterocycles, and the value we'll try to match for this compound here with R=H is 5.21. So let's keep that in the back of our minds, and then we'll run a pKa calculation on pyridine in Rowan. So we'll change tabs and click on the "new pKa prediction" button from the home screen and that will take us here and we can draw a 3D structure: we can say add from library, go to rings, phenyl, then we'll go to our periodic table, we can add a nitrogen to this benzene ring to make it into a protonated pyridine and then remove that proton to just give us pyridine. So we'll call this "pyridine pKa."

And now we have a bunch of choices on this settings half of the screen. And the reason we have so many choices is that there's actually a lot of different sites where we can add or remove protons, even on a molecule as simple as pyridine. So we can imagine adding a proton to every heavy atom here, so each of these five carbons plus this nitrogen. And then we can imagine removing any of these five protons. So altogether, that's 11 different sites for pKa, and that's usually more than we care about. We have two different ways to filter down to the set of questions that you actually have in Rowan. One of this is setting this min and max pKa window which essentially says that we're not going to look for pKas which are crazy low or crazy high, that might exist only under extreme conditions; we're just going to restrict ourselves to asking about pKas within the range 2 and 12 which is pretty normal for physiological or close-to-physiological conditions. If we were looking at, for instance, enolate deprotonation or enolate generation, this sort of strong base chemistry or superacid chemistry, we might want to make this window a little bit larger so that we can actually see the pKas that we care about for that. And then the other thing that we have here is we want to select the elements that we're going to protonate or deprotonate. And in this case,the default settings will be that we only protonate on nitrogen, and we only deprotonate from nitrogen, oxygen, and sulfur. So notice how carbon is on neither of these lists, and if you want to run a pKa calculation that involves deprotonating carbon, again, for studying enolate chemistry, you might want to add that to the "deprotonate elements" list.

Finally, we also have our mode setting. And in this case, at a high level, this controls the trade-off between error and efficiency. And what this usually boils down to is actually how we generate all of the conformers that we need to, for this calculation. So for each charge state that we look at, we're going to have to do a conformer search, and that can be pretty expensive for more complex molecules. And so we can tune it between reckless and careful to try to figure out how much we want to spend on each calculation for higher and more precise results. In most cases careful is appropriate, and so we'll just click "submit."

Behind the scenes what this is doing is, as I alluded to before, we're going to iterate over all the sites and compute which protonation or deprotonation sites are reasonable then we'll run a conformer search on each compound, optimize each of them, get a final sort of proton affinity, and then convert that to a pKa. And what this finally gives us now for this simple molecule is just a single site where we can protonate, and that's right here. So the value we were trying to match is 5.21, and the value we got is 5.11, so that's pretty good. And we can view the conjugate acid here, to confirm that protonation is happening as we expected, and this is exactly what we expect protonated pyridine to look like.

Okay, so that was pretty straightforward: we can see how long that calculation took in total, and that was under 10 seconds. So let's now try again on a slightly more ambitious molecule. We'll just add some extra functionality to this to tax ourselves a little bit more, so we can go to the periodic table here: we can add an oxygen, maybe we can add another oxygen, and we can add a carbon here. So now there's at least three sites that we might care about, and potentially more. We'll say "complex pyridine pKa" because I don't want to try to systematically name this compound on video, we'll leave our same settings because they seem good, and we'll say "submit pKa" again.

It's worth noting that Rowan's pKa workflow gives microscopic pKas and not macroscopic pKas. So microscopic pKas are broken down by atom, whereas macroscopic pKa reflects the propensity of the molecule as a whole to add or remove protons. We focused on microscopic pKas for now because they're more fundamental, in a sense. The microstates are the underlying unit from which we build up the macrostates, and also let us break it down by functional group, like this. In the future, we'll look into incorporating macroscopic pKas into Rowan, but we haven't yet done that.

And so, you know, now what we see is, first of all, we optimized the geometry. So we have this cool internal hydrogen bonding network—that's always interesting to see. And now we actually have three relevant sites. So we have our original nitrogen again, which is now a bit more basic, which makes sense because we've added these electron donating groups onto the ring, as well as this methyl group. And we also have one oxygen and two oxygens. What we can see, interestingly enough, is that this one is a bit more acidic than this one. So if we do deprotonate at a given site, you know, we expect it to be from there, the one that can form the pyridone-looking tautomer, as opposed to this one, which is going to be slightly less acidic. And that's a difference of about one and a half pKa units. So it's substantial, but it's not insane.

Another thing to note here is that we've colored the two different sorts of sites differently. So really, pKa is used in sort of two different ways in Rowan and in most other discussions of pKa outside the physical chemistry literature. We can refer to the pKa of adding a proton somewhere and the pKa of removing a proton from somewhere and strictly, the pKa that we're looking at here is the pKa of the conjugate acid. So really, it's this molecule that properly has a pKa of 6.79, and we should be using the term pKb to be precise. But because it's pretty obvious when we talk about the pKa of a pyridine as being 5 or 6 that we're really referring to the conjugate acid, it's most common just to talk about it in these sort of joint terms. To help disambiguate these in Rowan, we color the pKbs as blue when we're adding a proton, and the pKas where we remove a proton, we color those red. Thanks for watching!

Predicting Redox Potentials on Rowan

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan, and in this video we're going to talk about redox potentials. The redox potential of a molecule indicates how easy or difficult it is to add or remove electrons. Redox is a portmanteau of reduction and oxidation: reduction refers to adding extra electrons to a system, whereas oxidation refers to taking electrons away from a system. And we can actually quantify how easy or difficult each of these half reactions will be in volts. Those are the reduction and oxidation potentials for our molecule.

Now, these values can be measured experimentally, but prospectively, if you're considering whether or not to run a reaction or trying to understand what the trends along substrates might be, it's pretty common to look up the reduction or oxidation potentials for a given molecule in a table such as this. This is a very famous paper—there's other papers like this—and what this essentially does is record a compendium of measured redox potentials for different organic molecules. So we can see here the different oxidation potentials for various aromatic hydrocarbons: these are for alkenes, these are for phenols. And we can see that adding electron-donating groups makes these voltages lower, making the molecules easier to oxidize, whereas adding electron-withdrawing groups makes them more difficult to oxidize, leading to a larger oxidation potential. And this is very nice if the substrates we care about are actually located within this table, but if we were evaluating different substituents, different classes of compounds for which reference data did not exist, we might want to be able to compute the values from scratch for our compound rather than just guessing what the effect of these substitutions might be.

And this is where Rowan comes into play. So from the home screen of Rowan, we can click on this new redox potential prediction button and simply go here and input the structure we care about. So in this case, we can look at phenol because it's a simple molecule and we actually have the reference value on hand. So we'll go to "add fragment from library." We'll draw a ring. We'll go to the periodic table menu. We'll select an oxygen and put it here. Now this looks like a pretty good geometry for phenol. We might want this OH to actually be in-plane, but that's okay, we'll run our optimization as a part of this workflow anyway. So we'll say save, we'll say "phenyl redox potential." And now here we can choose whether we want to study the reduction, the oxidation, or both. And here we'll just study the oxidation because that's the reference data we have. Okay, and we can now select the mode. So the mode lets us choose what sort of calculation we want to run. We can tune this from reckless up to meticulous, as with all workflows in Rowan. But here we'll just leave it on rapid for the sake of this video—that's a good default for most use cases. And we'll say "submit redox."

So what's happening behind the scenes while this runs? What Rowan is going to do is first run an optimization on the input molecule, then run a more accurate single point at a different level of theory, r2SCAN-3c. And then Rowan will add or remove electrons to generate an open shell species that's reduced or oxidized, and again run an optimization and then a more accurate single point on that structure. And so in the end, we'll get a difference in energies between the neutral and the oxidized structure. And that difference in energies can then be converted to the same value you'd measure experimentally against a reference electrode. So it's not exactly just the difference of energies: we have to to adjust it linearly by adding a constant to correct for the reference electrode we care about, and in Rowan all of these values are done for now against the saturated calomel electrode (SCE), which is standard in the organic literature, and using acetonitrile as the solvent, which is also standard.

So I've just skipped ahead to where this calculation finished. And if we look at the runtime, we can see that that was only two minutes—so it's not long, there's no crazy deceptive video editing here, I just didn't want to stare at a blank screen for two minutes. And we can now see that we have the output of this redox potential calculation. And we can see the oxidation potential here is predicted to be 1.63 volts versus SCE in acetonitrile, just like we discussed. And here, if we compare it to the reference value, we can see actually, this is exactly right. We won't always get exactly the right answer here. Unfortunately, our software is not perfect, and these calculations are not perfect, but nevertheless, redox potentials, I think, are, for organic molecules, relatively easy to do a pretty good job at, versus things like pKa, which are a little bit more challenging.

So if we look here, we can do a couple interesting things in this calculation. We can change the reference electrode here to align with different experimental setups that you might have if you're trying to benchmark this relative to experimental data from your own lab. This is the neutral structure here, and we can also view the oxidized structure, which now, interestingly, is planar. See here neutral and oxidized. There's pretty minute differences here. In other cases, there's sort of larger structural changes. We can look and see that these bond lengths do change a little bit between these structures, but it's not a huge change. You know, these are pretty subtle differences. And if we want, we can even go and view the underlying calculation to see sort of what's going on here, although that's not typically super helpful. Anyhow, thanks for watching.

Running Rowan's Bond-Dissociation Energy Workflow

Transcript
This is Jonathon Vandezande, the Director of Computational Chemistry here at Rowan. Today I will be providing an overview of running a bond-dissociation energy prediction with the Rowan Scientific platform.

Bond-dissociation energies are useful for predicting metabolism and degradation. The weakest bonds tend to be metabolized and degraded first, so it is useful to have a quick method to predict the bond-dissociation energy so that the molecule can be modified to reduce possible metabolism and degradation.

To run a bond-dissociation energy prediction, first log into labs.rowansci.com and select "New BDE prediction". You can upload a molecule with one of our standard molecule inputs, or you can input it from a remote database including PubChem or Materials Project. Today, we will be working with ibuprofen and uploading it from PubChem.

You can see here the ibuprofen molecule and all of the various C–H bonds, both aromatic and aliphatic. We can add individual bonds, or we can add groups of bonds including C–H and C–X bonds. For this tutorial, we will be using all C–H bonds and running it in RAPID mode. This will take a few minutes, so we will go ahead and flip over to an already completed version of this molecule.

Here we can see the results of our molecule, which took about 25 minutes to run, which is approximately 1.5 minutes for every bond that was broken. We can see a variety of different bond types, with the lowest energy bond dissociations being those of the carbon-hydrogen bonds next to the aromatic ring. The highest energy bonds are those of the aromatic carbon-hydrogens.

Running Rowan's Spin States Workflow

Transcript
This is Jonathon Vandezande, the Director of Computational Chemistry here at Rowan.

Today I will be introducing the spin states workflow for predicting the lowest energy spin state of a molecule or system.

First, log into labs.rowansci.com and select the new spin states workflow. Here we can upload our molecule, input it via SMILES, or draw the 3D structure.

Today we will be working with a Mn(Cl)₆⁺⁴ complex. We can add the manganese first and then add the chlorine in each of the octahedral positions. We can then go ahead and save our molecule and update the name.

We should then make sure to have the correct charge and multiplicity, and go over to the tasks area to select which spin states we would like. Here we will be looking at the doublet, quartet, and sextet state of this molecule. We can then select the mode, which is consistent with the modes that you can see in multistage optimization. You can learn more about these modes in the multistage optimization workflow overview, or look at the mode info box. We will be using RAPID mode today. We will go ahead and submit this and we can let it run.

I'll jump over here to an already completed version of this where we can see our Mn(Cl)₆⁺⁴. This job took about one minute to run and was able to quickly predict our preferred multiplicity. In this case, since chlorine is a weak field ligand, we see the sextet state being the lowest in energy. We can also observe that as we go to a higher and higher multiplicity, that the manganese chloride bond slightly stretches. We can compare this to a Mn(H₂O)₆⁺² system, where water is a slightly stronger field ligand, we expect to see a slightly smaller difference between the highest and lowest spin state.

We can also look at the manganese carbonyl system where a carbonyl is a strong field ligand and suddenly the energy difference between the lowest spin state and the highest spin state completely flips where now the doublet is the favored spin state.

Running Rowan's Fukui Index Calculation Workflow

Transcript
I'm Corin, CEO and co-founder of Rowan, and in this video we're going to talk about calculating Fukui indices. Fukui indices are named after Kenichi Fukui, the 1981 Nobel laureate in chemistry, along with Roald Hoffman, and really a leader in the field of applying molecular orbital analysis techniques to predict sites of reactivity, which at a high level is what Fukui indices are all about.

Now, if we think about trying to predict where a reaction will occur on a complex molecule with many potentially reactive sites, we can imagine doing things the old-fashioned way, using a tool like Rowan or any other computational chemistry package. We could find a transition state for a reaction with each individual site. We could run optimizations of these transition states to do them at a high level of theory, and then sort of predict the difference in energy between all of the competing transition states to predict which sites will react quickly and which sites will react slowly.

Now, this is a rigorous method and one which will almost certainly work if the transition states can be found. But there's something about this that feels a little bit wrong. In many cases, a trained organic chemist can look at just a substrate—if you say this is going to react with an electrophile, they can predict where a reaction is most likely to happen without actually needing to know the structure of the electrophile. In some sense, it seems like it's a little overkill to have to run a different transition state search for each different electrophile when often what we care about is just, where is electron density stable or unstable on this molecule? You know, where are there electron-withdrawing and electron-donating groups?

And this, at a high level, is what Fukui index calculations are all about. When we're calculating Fukui indices, we're essentially adding or removing electrons to a system and then seeing where this extra positive or negative charge flows. And by looking at this, we can tell where on a molecule the positive or negative charge is going to be stabilized and predict where reactions will happen.

Let's see what this looks like in practice. So from the homepage of Rowan, we can click on "New Fukui index calculation" here, which takes us to this submission screen. And I'll quickly input a SMILES string for a simple but relatively non-trivial molecule. So we'll look at this sort of extended conjugated alkyne here. Sorry, not an alkyne: we have a double bond, a carbonyl, and then we have a diene here, and then we have a methyl group on the end. So this has potentially a lot of different sites of reaction. Let me go in here and just rotate around this dihedral to sort of align a little bit better with our chemical intuition on what this will probably look like, maybe go to a little bit of an s-trans conformation here. And obviously, you know we can imagine looking at the system that you could see 1,2-addition, 1,4-addition, or 1,6-addition if you were to add in a nucleophile and so we might actually care about where this is likely to happen or you know what the relative proclivities are going to be.

Here we can see the output of our Fukui index calculation. We have three different Fukui functions: these are called in the literature f(+) or Fukui positive, f(0), and f(-). So f(+) represents reactivity towards nucleophiles, f(0) represents reactivity towards radicals, and f(-) represents reactivity towards electrophiles. Let's sort of go through these one by one. We can see here that, you know, the exact value of the function is broken down a little bit by atom. And we can actually see the values here, but we can also see a lovely visual highlight just by which sites are more red. And we can see here that you know the most red carbon on this molecule is actually C6, so the 1,6-conjugate addition site. And so what this is telling us is that you know 1,4-conjugate addition and 1,2-conjugate addition are definitely possible, but if we're adding a nucleophile to this system we can probably expect a reaction to occur here at this carbon. If we look at f(0) which represents reactivity towards radicals again, we can see that carbon 6 is predicted to be the most likely site for radical attack. And now if we look at the negative Fukui function (reactivity towards electrophiles) here we can see that now C2, this alpha carbon is the most likely site of reactivity towards electrophiles as opposed to the other carbons which are slightly different in color, although C6 still sort of looks okay here as well, which is interesting.

Now, these values are obviously a little bit imprecise. This is just a function of where charge ends up going—and so a lot of atoms often end up having large changes in charge no matter what, like these oxygens. Carbonyl oxygens almost always have some value for the Fukui index, as do heavy atoms, like halides, so it's not a perfect metric. It needs to be sort of filtered through your own chemical intuition as to what's reasonable or not. But nevertheless, Fukui indices are a great way to quickly try to build up an intuition for reactivity, and they can be used for a lot of other downstream processes too, where the identity of the reactive partner is complex or might not even be known.

Calculating Global Electrophilicity on Rowan

Transcript
I'm Corin, CEO and co-founder of Rowan, and in this video we're going to look at global electrophilicity index calculations. Global electrophilicity index calculations are useful when you're trying to rank a bunch of electrophiles by how reactive they are. The conventional way to do this would be to actually draw out a model nucleophile, find transition states for reacting this nucleophile with each electrophile, and then rank the relative ∆∆Gs of these. Some reactions will have a high barrier, some reactions have a low barrier, and based on the transition state energies, we can actually predict the relative rates of reaction using the Arrhenius equation.

But there's also a lot of ways this process can be tedious or somewhat frustrating. Finding transition states is a little bit time consuming: it's not the simplest thing in the world to automate, and you have to run all these frequency calculations to make sure you actually found the correct transition state, and it turns out that for reactions with soft or covalent nucleophiles there's actually a shortcut we can use so we don't have to do any of this work at all and this is calculating the global electrophilicity index. The global electrophilicity index is just a function of the electronegativity and the hardness of the fragment in question and it turns out that over a wide range of covalent nucleophiles this value correlates really really well with the barrier to reaction. So if we're trying to design a warhead with a given reactivity, we can just do this based on the electrophilicity index and skip all of these tedious transition state calculations altogether.

Let's see what this looks like in practice. We can go to the "New Fukui index calculation" button here from the home page of Rowan and input a 3D structure. So let's actually just draw it out by SMILES, because that's a little bit easier in some cases, and we'll start by looking at this methyl vinyl ketone. We'll look at this because this is expected to be somewhat electrophilic, right? So we can do conjugate addition here and we'll say "Run new Fukui index calculation." And although it's not listed, this will also calculate the global electrophilicity index over here. This is because these calculations use a lot of the same sort of machinery under the hood. And so we just group them together, so you get two for the price of one. Now, if we see what this is, this gives us a global electrophilicity index of 0.952 eV.

Now, this might not be the world's most meaningful number in isolation. So I'll actually go and compute a different value, so we have something to compare this to. And we'll go "resubmit as Fukui index calculation." And now we'll modify this molecule, so we have some different substitution here. We'll make this now into an acrylamide—these are pretty common covalent inhibitors, and we'll edit this dihedral so it looks a little bit more sane, and then we'll say "submit Fukui calculation." So this will optimize and run the calculation pretty quickly.

These calculations are very fast to run, so they're suitable for high throughput screening or an iterative genetic optimization, which is one of the nice features about them. And so now if we compare: our previous value for the global electrophilicity index was 0.952, and over here, we can go to the global electrophilicity index and see that it's 0.676. So this is quite a bit lower. And this makes sense, right? We've added an amide here. This stabilizes this a lot, this makes it much less electrophilic, and as a result, the electrophilicity has gone down.

Let's model just one more effect on this, perhaps. So let's now, we'll resubmit. We'll resubmit this again as a Fukui index calculation. And we'll now just throw fluorine on here. So this we expect will increase the electrophilicity of the calculation. And we'll say "with fluorine," because I don't want to wade through that smile string again. We'll say "Submit Fukui calculation." So we can imagine this in the course of an optimization. We'll say, okay, maybe this one was too electrophilic. You know, maybe this one wasn't electrophilic enough. So now let's add a fluorine and see, you know, do we think this will be more or less electrophilic than our starting compound? This would be a little bit annoying to take care of if we didn't have this sort of lovely instant electrophilicity calculator button here. And now we can see that the global electrophilicity is predicted to be 0.782 eV, so sort of nicely between our two previous compounds. So it looks here like adding the fluorine moves us up in electrophilicity, but it still doesn't quite take away the effect of the acrylamide. So maybe this would be a nice compromise compound for some covalent inhibitor or just for a synthetic building block.

Running Rowan's Descriptors Calculation Workflow

Transcript
Hi, I'm Ari, one of the founders of Rowan, where I lead product and strategy. In today's video, I'm going to be talking about Rowan's descriptors calculation workflow. We'll go over how to submit a workflow, what the workflow does, and how you can use the results, both in Rowan and export them to use in further projects.

Now descriptors, at a very high level, are a way of generating a feature vector for your molecules so that you can run data science and machine learning workflows on your molecules. And we think that this is especially good when you're working with properties that are hard to run physics-based simulations to predict.

So to submit a descriptors calculation workflow on Rowan, we'll go ahead and click "descriptors calculation" and we'll upload the files that we're going to be looking at today. For this example, we're just going to look at this super basic set of alcohols. You can see that there's nothing fancy here, and that these structures loaded in all right.

And so we'll just go ahead and submit these six molecules, and we can submit them all at once, and they'll start running. And what's gonna happen is Rowan is going to use Mordred to generate some molecular graph and conformer-dependent features, as well as XTB to generate some per-atom descriptors.

These are small molecules and the descriptors workflow super fast, so it's already finished running. We'll go ahead and hide the sidebar, and we can view these results. So at a glance, you see that Rowan gives you this table view. You can sort by any descriptor. You can look and see what the descriptor actually calculates. And of course, you can filter.

I think we should look for hydrogen bond donors today. So I'll just type in "hydrogen bond." You can search, and we can see that there are two features related to hydrogen bonds. That's this hydrogen bond acceptor feature and this hydrogen bond donor feature. When we're working with these features, often we'll wanna take it and use it somewhere else. And so you can always download all of this data as a CSV and load it into whatever software you're using for data science or machine learning.

One cool thing though is that inside of the Rowan platform, you can run principal component analysis on a library of descriptors that you've calculated. And PCA is a statistical method that will cluster our data. So we're looking at PCA 1 and 2 and that gives us this nice XY plot. And it spreads our data out so we can see similarities and differences and make sure that whatever library we're working with covers chemical space nicely.

And so you can see that one thing that's really separating our compounds in this example is just this atom bond connectivity index. And if we want to see the actual values for each of these data points, we can click on this feature and it'll color. And by hovering over the points, we can sort of visually inspect and get a sense for, okay, what's contributing to the variance in my data right now? And if we want to look at number of hydrogen bond donors, again, we can do that too. And we'll see the data colors nicely. And, you know, with this basic example, of course, this isn't super impressive, but I think it is really cool. And if you want to work with these PCA coordinates outside of Rowan, you can download the data as a CSV right here again.

Running Rowan's ADME-Tox Workflow

Transcript
Hi, I'm Corin, CEO and co-founder of Rowan, and in this video we're going to talk about ADME/tox prediction. ADME/tox is a shorthand that's used in medicinal chemistry and drug design to refer to some of the drug-like properties that aren't directly tied to binding affinity. So A stands for absorption, D stands for distribution, M stands for metabolism, and E stands for excretion. So those pertain to how drugs get into the body, what they do in the body, and how they get out of the body. And then tox refers to toxicity—the worry that drugs will be bad. You know, will this drug cause one of a litany of different negative side effects if it's administered to a human being?

And these properties, unlike most of the other properties and workflows currently on Rowan, are not directly computable from first principles, at least not in a straightforward way in most cases. So thinking through predicting metabolism requires modeling the effect of the liver, the kidneys, all of this sort of stuff on drug molecules, and this is not the sort of thing we can just load and run a DFT calculation on. There are ways of course that DFT calculations like bond-dissociation energies can inform thinking about where and how fast metabolism will occur, but in general end-to-end metabolism or toxicity prediction from first principles just isn't very feasible because it involves something as massive and complex as the human body.

Instead, what's been done is to build empirical machine learning models to model and sort of guess what the effect of the human body will be on a given drug. Instead, what's commonly done is to build machine learning models trained on experimental data that provides a quick guess as to what a drug will do once it's in the body. This is what we do here on Rowan. So to run an ADME/tox prediction, we just come here and click "new ADMET prediction," and we load in the molecule that we care about. So in this case, we'll choose a simple molecule just to show off some of the basic features of the workflow. And of course, you can come here and at no cost just make a free account and try out your own molecules and see what you think of these predictions. So we'll draw nitrobenzene just because we expect this to be a pretty interesting result. We'll click save, we'll say "nitrobenzene," and we'll say "submit ADMET." So here we go.

On every ADME/tox page we have this warning: global models of ADME/tox are not substitutes for experimental measurements. This is really important to note because especially with properties as complex as these, it's really important to know that these predictions are useful, but they're not as good as running an experiment. And if you are actually in a drug design campaign and you need to make mission-critical decisions, you should actually pay the money and measure these properties yourself with a CRO and a vivarium and any of these things, because these are really better thought of as guesses. They're not as good as experimental data. And there's plenty of articles we link here pointing out that this is the case.

All that being said, there are a lot of ways in which these quick experimental measurements can actually be very useful in encoding some of the intuition that we as chemists have about molecules. And so I'll walk through the rest of this without making any further caveats. So the first page that we see here on the ADME/tox prediction screen is this one—we can see the physicochemical properties. This just tells you simple things like how big is this molecule and molecular weight, how greasy is it, how many hydrogen-bond donors or acceptors it has. And on this page, as with all of the ADME/tox pages, we have everything sort of highlighted here. So green means that this will probably make an effective drug based on human encoded heuristics. Yellow means you're sort of in a gray area: maybe it'll be an okay drug, maybe it won't. And then red, which we'll get to later, shows that this is a little concerning, you might want to take a closer look at this and figure out if you should make some modifications to the structure. And again, all of these are just estimates, and there's, of course, exceptions to everything here.

If you want to see exactly what the colors actually correspond to, we can hover over this info icon. So here it explains logP. So logP is the partition coefficient, which is the ratio of solubility between octanol and water. And then it shows what good values are: so a good value for logP generally is considered to be about zero to five, you can have a little deviation from that and it's fine. But then really, really greasy or really, really hydrophilic compounds are both unlikely to make great drugs because they probably won't be absorbed to get into cells the right way. Okay, so this is physicochemical properties.

Here if we go over to absorption properties, this gives us things like cell permeability, so PAMPA, Caco2 permeability, and then, you know, a variety of other things like logD, so distribution coefficient, solubility. And here, actually, this is a pretty good metric, because solubility here is predicted to be not so good. Actually, nitrobenzene generally is not miscable with water, at least as a bulk substance, so it forms little droplets in water, and so this is a correct flag that this might not be the most water-soluble compound on Earth.

If we go over here to metabolism, you know, we have here most of the CYP inhibition is predicted to be okay, but there is predicted to be inhibition of CYP1A2. So that, you know, has sort of a high predicted inhibition, which could lead to bad drug–drug interactions, and is generally something people worry about. And this molecule is predicted to be a substrate or possibly a substrate for CYP3A4, so that's something else to think about. Here we have, you know, this is predicted to get into the blood–brain barrier. This is true, I believe nitrobenzene does cross the blood–brain barrier quite quickly, so that's true and then there's some other metrics here like volume of distribution. Now we come to excretion so this is predicted to be cleared and excreted quite quickly, so that might be bad for a drug.

And now we come to toxicity. So here we can notice that we're setting off some flags so there's a lot of different toxicity warnings here for various different mechanisms of toxicity or individual targets. hERG is a pretty famous potassium ion channel, which often causes issues with basic amines. The Ames test for mutagenicity is another good one. And here we can see that nitrobenzene is predicted to cause drug-induced liver injury and skin sensitization. And, you know, this is not surprising at all because nitrobenzene and nitro-containing compounds in general are actually quite toxic. So this is an acutely toxic compound which is one of the reasons I chose it for this: I believe it is bad for the liver, it's also bad for the nervous system which doesn't make it into here, as I can recall I think it's also bad for your skin. It's really bad for most parts of your body, so if you're exposed to this compound you should definitely seek medical attention acutely. So this sort of shows that this is a legitimate concern: we've flagged a compound that's bad and it does indeed seem to be bad.

So that's an overview of the ADME/tox workflow. Another thing we can do here is we can submit another ADME/tox prediction. Maybe we'll say, okay, nitrobenzene wasn't a very good molecule, maybe we can add some steric shielding here. Maybe this will make it a better drug. So what about 2,6-dimethyl nitrobenzene? So nitrobenzene, we'll say 2,6-dimethyl nitrobenzene. You know, personally, I doubt this will have a huge effect on the predicted or actual toxicity because a nitro group is pretty bad no matter where it is. But nevertheless, we can look and sort of see, well, at least the model thinks this will cause less liver injury, but will still be bad for the skin. I don't know if that's actually true. I don't know how toxic this compound is—that'd be interesting to measure.

But one of the things we can do is now actually compare these two by selecting multiple compounds and see them side by side. So we can see here, you know, we've obviously changed the lipophilicity. So we've added more methyl groups, we've made this slightly greasier. We've changed the molecular weight, we've changed, we actually haven't changed the total polar surface area, because we've not added any polar functionality. And we've mitigated a lot of other things. So you know, the CYP profile is predicted to be different, we're predicted to be less toxic to the liver, we're predicted to still be a skin sensitizer, etc. And we can download these results as a CSV if we want to for further analysis. That's how to analyze ADME/tox properties on Rowan.

Dihedral Scans
In this tutorial, we'll use Rowan to conduct a dihedral scan on a hindered biaryl compound, locate the transition state for atropisomer interconversion, and predict the barrier to rotation.

 AIMNet2
Heads up! Since we released this tutorial, we've added support for AIMNet2, which is much faster and probably more accurate than the methods used here. We recommend using AIMNet2 for this tutorial, although we haven't re-run all the calculations yet. We have also deprecated support for running jobs with HF-3c.

Background
Atropisomerism occurs when hindered rotation around a single bond gives rise to different stereoisomers. In a recent review, Jeffrey Gustafson and co-workers discussed the increasing importance of atropisomers and atropisomerism in pharmaceutical compounds: according to their research, "∼30% of recent FDA-approved small molecules (2010–2018) possess at least one class-1 atropisomeric axis." In many cases only one atropisomer is biologically active, while the other atropisomer contributes to off-target activity or toxicity.

In a 2013 paper, Steven LaPlante and co-workers divided atropisomers into three classes based on their barrier to rotation. Atropisomers with a high barrier to interconversion (class 3) will behave as entirely separate compounds, while atropisomers with a low barrier to interconversion (class 1) will rapidly sample many different conformations. Atropisomers with middling barriers to rotation (class 2) interconvert on similar timescales to other pharmacokinetic processes: accordingly, "special caution is warranted" (LaPlante).

Understanding the barrier to atropisomer interconversion is very important when considering compounds with a potential atropisomeric axis: otherwise, atropisomerism can be "a lurking menace" (to quote one review) which can lead to numerous problems later on in drug development. Successful drugs have been developed in all three classes of LaPlante's classes, but it is important to understand which class a given molecule belongs to: class 3 atropisomers should be prepared in isomerically pure form, while class 1 atropisomers cannot be isolated and are administered as a mixture.

Different classes of atropisomers shown on a bar graph

Reproduced from Gustafson et al, Figure 1.
While it's possible to measure the rate of atropisomer interconversion in the laboratory through various methods (as described in this article), it is often faster and easier to predict the barrier to rotation using computational chemistry. Quantum chemical calculations are commonly used to generate conformational energy profiles for potentially atropisomeric compounds, and the agreement with experiment is generally excellent.

In this tutorial, we'll use Rowan to predict the barrier to rotation for a RORγt inhibitor investigated by Novartis as a potential treatment for inflammatory and autoimmune diseases like psoriasis and arthritis. In the Novartis work, high-throughput screening identified N-aryl imidazoles as a promising hit, and further optimization led to the development of compounds bearing 2,6-dichlorophenyl rings (3–5). Efforts to improve ADME properties through modification of the core (6-7) substantially reduced binding affinity, and so substitution at the 3 position of the dichlorophenyl ring was considered next.

A picture of Novartis's different compounds

Reproduced from Hoegenauer et al, Table 2.
The authors anticipated that these compounds might exhibit hindered rotation around the aryl–aryl C–N bond. To predict if the resulting compounds (8-11) would be formed as multiple separable atropisomers, the authors conducted quantum chemical calculations to determine the barrier to rotation. In this tutorial, we will demonstrate how to do this for compound 5.

Running a Dihedral Scan
To start, we need to generate a structure for compund 5. We can do this by drawing the structure in ChemDraw, highlighting it, and then clicking "Edit > Copy As > SMILES" from the menu to obtain the SMILES string corresponding to the structure we've drawn. When I do this, I get ClC1=C(N2C(C)=C(C(F)(F)F)N=C2C3=CC=C(Cl)O3)C(Cl)=CC=C1, which isn't quite canonical SMILES but will work well enough for our purposes. Here's the ChemDraw structure that gave this SMILES string:

A line drawing of compound 5

Compound 5, drawn in ChemDraw.
We can then use this SMILES string to load compound 5 into Rowan. Go to labs.rowansci.com/new/scan, click "Input Smiles," and paste in the string from ChemDraw. Your screen should look like this:

SMILES input screen

Inputting a structure to Rowan via SMILES string. We can specify the title of the job after the string.
When you click "Submit," Rowan will automatically convert the SMILES string provided into a 3D structure and display it on the screen. Take a look at the structure this generates and verify that the SMILES conversion worked properly.

Now we need to run a dihedral scan on this structure. To do this, click into "Scan Coordinate" box and configure a dihedral scan about the C5–N4–C3–C2 dihedral angle from 0º to 360º with 15 steps. (These atom numbers were chosen by clicking on atoms in the structure: you can select any four atoms to see the dihedral angle. There are several choices of atom numbers that are all equally good here.)

The other settings are straightforward: we'll leave the method to HF-3c, a good default for this sort of task, and choosing a scan means that "Optimize" is pre-selected as our task. We are ready to submit our job! At this point, your screen should look like this:

Submission screen for scan

Note that we can check the atom numbers in the molecule viewer to make sure we've specified them correctly.
After clicking "Submit Scan," you'll be redirected to the scan view; the scan will take a few hours to run.

Here's the completed scan: click through the different steps (or press the arrow keys) to visualize the different structures. We can immediately see that the barrier to rotation will be quite high: for instance, the point where the C5–N4–C3–C2 dihedral is 180º (step 8/15) has an energy about 37 kcal/mol above the lowest structure sampled. So, we can conclude based on this scan that the atropisomers will be separable compounds (LaPlante class 3) and will not interconvert after isolation or in vivo.

(You can click "View in Rowan" to open the scan in a new tab and view the individual calculations.)


Locating the Ground State
The scan we ran above gives us a quick sense of what the barrier to rotation will be, and often only a scan is needed to predict what class a given atropisomer will belong to: LaPlante recommends this approach. Sometimes, however, we want to compute an actual rotational barrier, to compare to other analogues or to experimental data. To do this, we must first locate the ground and transition states for bond rotation.

The ground state is quite simple to find. Select the lowest energy point from the scan—in this case, step 5, where the CN–N4–C3–C2 dihedral is 102.8º—and click "Resubmit" and then select "Resubmit as calculation." Select the "Optimize" and "Frequencies" tasks, leaving everything else the same. Your screen should look like this (you can rename the calculation now, if you want, or later):

Submission screen for ground state opt + freq

In my hands, this calculation finishes in a little over two hours. We can verify that the structure is indeed a true ground state by checking the frequencies tab and validating that there are no imaginary frequencies: all values are positive. Calculating the vibrational frequencies also gives us thermochemical values (viewable under the "Thermochemistry" tab), which will allow for calculation of the free energy rotational barrier.

Here's the structure: as before, you can view in a new tab by clicking "View in Rowan."


Locating the Transition State
Transition states are, in general, substantially more difficult to locate than ground states. For atropisomers with low barriers to rotation, the highest point from the scan is often a decent approximation to the transition state: unfortunately, this rotation is difficult enough that the high-energy scan points distort the rings to satisfy the dihedral constraint rather than actually getting close to the rotational transition state. (There is a lot of theory about why this occurs: see for instance this excellent paper by Jerzy Ciosłowski and Leo Radom.)

Here's what happens when you try to resubmit one of the high-energy scan points (this was step 8/15 from above). You can see that the molecule collapses to a low-energy conformation and eventually locates a transition state for methyl rotation—a common failure mode for TS calculations. (This calculation was allowed to finish for pedagogical purposes, but it was obvious after about 15 minutes that this wasn't going to succeed; the job could safely have been canceled.)


Fortunately, we have some chemical intuition about what the TS should look like: we expect the two rings to be parallel, not perpendicular, since the TS ought to connect the two atropisomers. We can thus download the ground-state structure as an .xyz file and use Avogadro or another program to manually rotate the C–N bond to make the two rings parallel, rotating the furan a bit to avoid any short interatomic distances. Then, we can re-upload the structure to Rowan, add dihedral constraints to force the two rings to remain parallel, and submit a constrained optimization.

The initial structure is pretty rough, but after about an hour the optimization converges towards something that looks more like a transition state:


This structure looks like what we might expect from a TS, and moreover qualitatively matches other dihedral rotation transition states from the literature (compare to Figure 7 here). Since it seems like we're pretty close, we can go ahead and resubmit this geometry as a transition state: remove the dihedral constraints, select the "Optimize (TS)" and "Frequencies" tasks, and click "Submit."

After a few hours, we locate the transition state. or any transition state, it's important to confirm that there is only one imaginary frequency, and that the frequency corresponds to the process we expect: here, there's a 45 cm-1 mode which corresponds to C3–N4 bond rotation, which is exactly what we've been looking for. (You can visualize this by clicking on the row under the Frequencies tab, increasing the amplitude, and rotating the structure so you're looking along the C–N bond axis.)


Computing the Barrier to Rotation
With our ground state and transition state in hand, we can now compute the barrier to rotation. The Gibbs free energy of the ground state is -2419.7661929 Hartree, and the Gibbs free energy of the transition state is -2419.6627466 Hartree, so the barrier can be computed as follows:

∆G‡ = (GTS - GGS) = (-2419.6627466 - -2419.7661929) * 627.509 (kcal/mol)/Hartree = 64.91 kcal/mol

This is really high! We can be confident that these atropisomers will not interconvert.

Correcting Single Point Energies
If we want to be even more precise, we can do a single-point energy correction at a higher level of theory. The idea behind single-point energy correction is that while electronic energies are quite sensitive to the level of theory employed, vibrational frequencies and geometries are much less sensitive. So, while we might not be able (or willing) to compute vibrational frequencies and get Gibbs free energy values at a high level of theory, we can approximate high-level Gibbs free energies by adding a low-level frequency correction to a high-level energy.

This is very easy to do in practice: resubmit both the ground and transition states and run energy calculations at the B3LYP-D3BJ/pcseg-1 level of theory (without optimization). These calculations take only a few minutes to complete: here's the ground state and the transition state. Then, add the energy from the B3LYP calculations to the "Gibbs Free Energy Corr." (under Thermochemistry) from the HF-3c calculations.

GGS ~= -2441.1257057 + 0.1842377 = -2440.9414680 Hartree

GTS ~= -2441.0419856 + 0.1856065 = -2440.8563791 Hartree

∆G‡ = (-2440.8563791 - -2440.9414680) * 627.509 = 53.39 kcal/mol

We can see that there's a substantial difference from above—unsurprising, given that HF-3c was not developed for barrier heights—but that the barrier remains very high. If we want to convert our ∆G‡ into a half-life, the math is simple, but even simpler is this free online calculator. Even at a temperature of 500 K, a barrier of 53.39 kcal/mol implies a half-life of over 450 years!

To be even more precise, we could perform a full optimization and frequency calculation at the B3LYP-D3BJ/pcseg-1 level of theory, starting from our HF-3c structures. A solvent model would help, as would additional single-point energy calculations with a triple-zeta basis set: as frequently found in computational chemistry, it's a question of how precise an answer is needed to give insight into the question at hand.

Organizing Jobs
Workflows on Rowan can be organized using a file system similar to those found in modern operating systems like the one found on your computer. The workflows are the "files" and folders can be created to organize them however you'd like.

Folders
Every Rowan user has a "Home" folder which is where workflows will end up if you don't make any additional folders. Folders have very similar functionality to folders on your computer with a few enhancements namely the ability to star and add notes to folders.

Creating Folders
To create a new folder, click the drop down of the folder name you're in and click "New folder"

A screenshot of Rowan's folder creation mechanic.
Starring Folders
If you have particularly important folders you can star them to set them apart. To star you can either hit the 3 dot menu when you are outside the folder, or hit the folder dropdown when you're inside the folder.

A screenshot of starring a folder using its three dot menu.
A screenshot of starring a folder using its dropdown menu.
After you star the folder, the star will be visible in the sidebar as well as when you enter the folder or search for the folder in the search bar.

A screenshot of a starred folder in the sidebar.
Adding Notes to Folders
You can add notes to folders that can help you remember what the workflows in that folder are for or interesting things that come up as you run workflows. As seen in the "Starring Folders" section you can add a note to a folder via the folder dropdown menu when you're inside of the folder.

After you hit add notes a text box will appear in the sidebar where you can write to your heart's content

A screenshot of the note box.
Renaming Folders
Similar to starring folders you can rename folders via the three dot or dropdown folder menus.

Moving Folders
You can move folders by clicking Move in the folder three dot menu or by hitting the move icon that shows up when you select an item in the sidebar. When you click, a modal will pop up that will allow you to navigate the file system and place the folder right where you want it. Just like the filesystem on your computer, nesting folders is valid.

A screenshot of the move icon.
A screenshot of the move modal.
Sharing Folders
Sharing workflows one by one can be tedious if there are many. Thankfully, you can share a folder which shares all the workflows in the folder as well. This can be done in the three dot or dropdown menus.

Searching for Folders
Folders show up in both "Search in Rowan" and the "Search within folder" based on their names.

Deleting Folders
You can delete folders via the three dot or dropdown menus as well as the trash icon that appears when you select items in the sidebar.

A screenshot of the trash icon.
Workflows
Starring, renaming, moving, sharing, searching, and deleting workflows works exactly the same as folders.

Adding Notes to Workflows
Notes for workflows live in the section to the right of the molecule viewer. Simply navigate to the notes section and hit edit to begin adding notes.
