"""
Run an optimization calculation on a molecule using Rowan.

See documentation at: https://docs.rowansci.com/science/quantum-chemistry/geometry-optimization
"""

from stjames import Molecule

import rowan

# rowan.api_key = ""

result = rowan.submit_basic_calculation_workflow(
    initial_molecule=Molecule.from_smiles("O"),
    method="GFN2-xTB",
    tasks=["optimize"],
    engine="xtb",
    name="Water Optimization",
)

print(result)