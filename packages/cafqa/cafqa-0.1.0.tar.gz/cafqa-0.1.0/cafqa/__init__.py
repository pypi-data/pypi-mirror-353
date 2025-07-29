"""
CAFQA: A classical simulation bootstrap for variational quantum algorithms

This package provides tools for implementing CAFQA (Clifford Ansatz For Quantum Algorithms),
a method for bootstrapping variational quantum algorithms using efficient classical simulation
of Clifford circuits.
"""

__version__ = "0.1.0"

# Import main functions from modules
from .vqe_helpers import (
    get_ref_energy,
    hartreefock,
    efficientsu2_full,
    add_ansatz,
    vqe_circuit,
    all_transpiled_vqe_circuits,
    compute_expectations,
    vqe,
    vqe_cafqa_stim,
)

from .circuit_manipulation import (
    transform_to_allowed_gates,
    qiskit_to_stim,
)

# Import vqe_experiment functions conditionally to avoid dependency issues
try:
    from .vqe_experiment import (
        molecule,
        ising_model,
        run_vqe,
        run_cafqa,
    )

    _HAS_VQE_EXPERIMENT = True
except ImportError:
    _HAS_VQE_EXPERIMENT = False

# Define what gets imported with "from cafqa import *"
__all__ = [
    # VQE helpers
    "get_ref_energy",
    "hartreefock",
    "efficientsu2_full",
    "add_ansatz",
    "vqe_circuit",
    "all_transpiled_vqe_circuits",
    "compute_expectations",
    "vqe",
    "vqe_cafqa_stim",
    # Circuit manipulation
    "transform_to_allowed_gates",
    "qiskit_to_stim",
]

# Add VQE experiment functions to __all__ only if they're available
if _HAS_VQE_EXPERIMENT:
    __all__.extend(
        [
            "molecule",
            "ising_model",
            "run_vqe",
            "run_cafqa",
        ]
    )
